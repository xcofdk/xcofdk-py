# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : tcpsocket.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

import socket
import ipaddress
from   collections import namedtuple
from   socket      import socket as _PySocket
from   typing      import Union

from _fw.fwssys.fwcore.types.commontypes import _CommonDefines

_IpAddress = namedtuple('_IpAddress', ['ip', 'port'])

class _TCPSocket:
    __slots__ = [ '__s' , '__hp' , '__rp' ]

    __NOLE = _CommonDefines._STR_EMPTY
    __CRLF = _CommonDefines._CHAR_SIGN_LF + _CommonDefines._CHAR_SIGN_CR

    def __init__(self, pySock_ : Union[_PySocket, None], rpeer_ : _IpAddress =None):
        self.__s  = None if not isinstance(pySock_, _PySocket) else pySock_
        self.__hp = None
        self.__rp = None

        if self.__s is not None:
            _h, _p    = pySock_.getsockname()
            self.__hp = _IpAddress(_h, _p)
            self.__rp = rpeer_

    def __str__(self):
        return self._ToString()

    @property
    def _isValid(self):
        return not self.__isInvalid

    @property
    def _isHostSocket(self):
        return isinstance(self, _TCPHostSocket)

    @property
    def _isListenerSocket(self):
        return isinstance(self, _TCPListenerSocket)

    @property
    def _isConnected(self):
        return self._isValid and (self.__rp is not None)

    @property
    def _isBlocking(self):
        return False if self.__isInvalid else (self.__s.getblocking() != 0)

    @property
    def _isNonBlocking(self):
        return False if self.__isInvalid else (self.__s.getblocking() == 0)

    @property
    def _isInfiniteBlocking(self):
        return False if self.__isInvalid else (self.__s.gettimeout() is None)

    @property
    def _isTimeoutBlocking(self):
        return False if self.__isInvalid else (self.__s.gettimeout() > 0)

    @property
    def _ip(self) -> Union[str, None]:
        return None if (self.__hp is None) else self.__hp.ip

    @property
    def _port(self)-> Union[int, None]:
        return None if (self.__hp is None) else self.__hp.port

    @property
    def _peerIP(self) -> Union[str, None]:
        return None if (self.__rp is None) else self.__rp.ip

    @property
    def _peerPort(self)-> Union[int, None]:
        return None if (self.__rp is None) else self.__rp.port

    @property
    def _timeout(self) -> Union[float, None]:
        return None if self.__isInvalid else self.__s.gettimeout()

    @property
    def _socket(self) -> Union[_PySocket, None]:
        return self.__s

    def _Send(self, msg_ : str, terminator_ : Union[str, None] =None) -> bool:
        if not isinstance(msg_, str):
            return False
        if not self._isConnected:
            return False

        if not isinstance(terminator_, str):
            terminator_ = _TCPSocket.__NOLE
        if len(terminator_):
            if not msg_.endswith(terminator_):
                if terminator_ == _TCPSocket.__CRLF:
                    if msg_.endswith(_CommonDefines._CHAR_SIGN_LF) or msg_.endswith(_CommonDefines._CHAR_SIGN_CR):
                        msg_ = msg_[:len(msg_)-1]
                msg_ += terminator_
        try:
            _num = self.__s.send(msg_.encode(_CommonDefines._STR_ENCODING_UTF8))
        except (BrokenPipeError, Exception) as _xcp:
            _num = 0
        return _num > 0

    def _Close(self, bShutdown_ =True):
        if not self._isConnected:
           return

        if bShutdown_:
            try:
                self.__s.shutdown(socket.SHUT_RDWR)
            except (OSError, Exception) as _xcp:
                pass
        self.__s.close()

    def _CleanUp(self):
        if self.__isInvalid:
            return
        self._Close()
        self.__s  = None
        self.__hp = None
        self.__rp = None

    def _ToString(self) -> str:
        if self.__isInvalid:
            return _CommonDefines._STR_EMPTY
        res = f'host={self._ip}:{self._port}'
        if self._isConnected:
            res += f'  remote={self._peerIP}:{self._peerPort}'
        return res

    @property
    def __isInvalid(self):
        return self.__s is None

class _TCPHostSocket(_TCPSocket):
    __slots__ = []

    def __init__(self, ip_ : str, port_ : int, timeout_ : float =None, xenvl_ =None):
        _pys = None
        try:
            _ip4Addr = ipaddress.IPv4Address(ip_)
            _saddr   = (ip_, port_)
            _pys     = _PySocket(socket.AF_INET, socket.SOCK_STREAM)
            _pys.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            _pys.bind(_saddr)
            if timeout_ is not None:
                _pys.settimeout(timeout_)
        except (ValueError, Exception) as _xcp:
            _pys = None
            if isinstance(xenvl_, list):
                xenvl_.append(_xcp)

        super().__init__(_pys)

    @property
    def _hostSocket(self) -> Union[_PySocket, None]:
        return self._socket

    def _CleanUp(self):
        super()._CleanUp()

class _TCPListenerSocket(_TCPHostSocket):
    __slots__ = []

    _DEFAULT_LISTENER_TIMEOUT = 0.05

    def __init__(self, ip_ : str, port_ : int, timeout_ : float =None, xenvl_ =None):
        super().__init__(ip_=ip_, port_=port_, timeout_=timeout_, xenvl_=xenvl_)

    @staticmethod
    def _CheckListenerParams(ip_ : str, port_ : int, timeout_ : float =None) -> Union[Exception, None]:
        _MAX_PORT = 65535
        if not (isinstance(port_, int) and (0<port_<=_MAX_PORT)):
            res = ValueError(f'Invalid port number {port_}, expecting positive integer number <= {_MAX_PORT}.')
            return res

        _xenvl = []
        _ls = _TCPListenerSocket(ip_=ip_, port_=port_, timeout_=timeout_, xenvl_=_xenvl)
        if _ls._isValid:
            _ls._CleanUp()
        return _xenvl[0] if len(_xenvl) else None

    def _Listen(self, backlog_ =1) -> Union[_TCPSocket, None]:
        if not self._isValid:
            return None

        _hs = self._hostSocket
        _hs.listen(backlog_)

        _ps, _paddr = None, None

        try:
            _ps, _paddr = _hs.accept()
        except TimeoutError as _xcp:
            pass
        except Exception as _xcp:
            pass

        res = None if _ps is None else _TCPSocket(_ps, _IpAddress(_paddr[0], _paddr[1]))
        return res

    def _CleanUp(self):
        super()._CleanUp()

