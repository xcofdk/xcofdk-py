# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : tcpsink.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from typing import Union

from _fw.fwssys.fwcore.logrd.logrecord           import _LogRecord
from _fw.fwssys.fwcore.logrd.rdsinks.logsinkbase import _LogSinkBase
from _fw.fwssys.fwcore.ipc.net.tcpsocket         import _TCPSocket
from _fw.fwssys.fwcore.types.commontypes         import override

class _TCPSink(_LogSinkBase):
    __slots__ = [ '__s' , '__t' ]

    def __init__(self, terminator_ : Union[str, None] =None):
        super().__init__()
        self.__s = None
        self.__t = terminator_

    @_LogSinkBase.isActiveSink.getter
    def isActiveSink(self) -> bool:
        if not self.isValidSink:
            return False
        return False if (self.__s is None) else self.__s._isConnected

    @override
    def _FlushLR(self, logRec_ : _LogRecord) -> bool:
        if not self.isActiveSink:
            return False
        res = self.__s._Send(logRec_._recToStr, terminator_=self.__t)
        if not res:
            self.__s._Close()
            self.__s = None
        return res

    @override
    def _CleanUp(self):
        if not self.isValidSink:
            return
        if self.__s is not None:
            self.__s._CleanUp()
            self.__s = None
            self.__t = None
        super()._CleanUp()

    @property
    def _ip(self) -> Union[str, None]:
        return None if not self.isActiveSink else self.__s._ip

    @property
    def _port(self) -> Union[int, None]:
        return None if not self.isActiveSink else self.__s._port

    @property
    def _peerIP(self) -> Union[str, None]:
        return None if not self.isActiveSink else self.__s._peerIP

    @property
    def _peerPort(self)-> Union[int, None]:
        return None if not self.isActiveSink else self.__s._peerPort

    def _SetSocket(self, socket_ : _TCPSocket):
        if self.__s is not None:
            self.__s._CleanUp()
        self.__s = socket_
