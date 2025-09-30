# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : rteexception.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

import pickle as _PyPickle
from   pickle import PickleError
from   typing import Tuple
from   typing import Union

from _fw.fwssys.fwcore.types.commontypes import _CommonDefines

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _RteException(Exception):
    __MAX_XPS = None

    def __init__(self, msg_ : str =None, code_ : int =None, xcp_ : BaseException =None, maxXPS_ : int =None):
        self.__msg  = None
        self.__rsn  = None
        self.__rsnt = None
        self.__code = None

        _MAX_XPS = maxXPS_ if maxXPS_ is not None else _RteException.__MAX_XPS
        if not (isinstance(_MAX_XPS, int) and _MAX_XPS>0):
            return

        _bXcp        = isinstance(xcp_, BaseException)
        _MAX_XPS    -= 0x100
        _msgDumpSize = 0x200 if _bXcp else _MAX_XPS

        if not ((_MAX_XPS>0) and (_msgDumpSize<=_MAX_XPS)):
            return

        if isinstance(code_, int):
            self.__code = code_

        if not (isinstance(msg_, str) and len(msg_.strip())):
            self.__msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteException_TID_001)
        else:
            self.__msg = msg_.strip()
        self.__msg, _msgDumpSize = _RteException.__TrimStr(self.__msg, _msgDumpSize)

        _xcpDumpSize = _MAX_XPS - _msgDumpSize
        if _bXcp and (_xcpDumpSize>0):
            self.__rsn  = xcp_
            self.__rsnt = type(xcp_)

            _dmp    = _PyPickle.dumps(xcp_)
            _dmpLEN = len(_dmp)
            del _dmp

            if _dmpLEN > _xcpDumpSize:
                self.__rsn, _xcpDumpSize = _RteException.__TrimStr(str(xcp_), _xcpDumpSize, xcpType_=type(xcp_).__name__)

        super().__init__(type(self).__name__)

    def __str__(self):
        _code = _CommonDefines._CHAR_SIGN_DASH if self.__code is None else self.__code
        res   = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteException_TID_002).format(type(self).__name__[1:], _code, self.__msg)
        if self.__rsnt is not None:
            res += _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteException_TID_003).format(self.__rsnt.__name__, self.__rsn)
        return res

    @property
    def isCausedByException(self):
        return self.__rsnt is not None

    @property
    def message(self) -> str:
        return self.__msg

    @property
    def code(self) -> Union[int, None]:
        return self.__code

    @code.setter
    def code(self, code_ : int):
        self.__code = code_

    @property
    def reason(self) -> Union[BaseException, str, None]:
        return self.__rsn

    @property
    def reasonType(self) -> type:
        return self.__rsnt

    @staticmethod
    def _DepInjection(maxXPS_ : int):
        _RteException.__MAX_XPS = maxXPS_

    def _Serialize(self) -> Union[bytes, None]:
        try:
            res = _PyPickle.dumps(self)
        except (PickleError, Exception) as _xcp:
            res = None
        return res

    @staticmethod
    def __TrimStr(str_ : str, maxDumpSize_ : int, xcpType_ : str =None) -> Tuple[str, int]:
        _DOTS = 3 * _CommonDefines._CHAR_SIGN_DOT

        _str, _dmpLEN= str_, 0
        while True:
            try:
                _dmp    = _PyPickle.dumps(_str)
                _dmpLEN = len(_dmp)
                del _dmp
            except (_PyPickle.PickleError, Exception):
                _str    = xcpType_ + _CommonDefines._CHAR_SIGN_SPACE + _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteException_TID_016)
                _dmp    = _PyPickle.dumps(_str)
                _dmpLEN = len(_dmp)
                del _dmp

            if _dmpLEN > maxDumpSize_:
                _LEN = len(_str)
                _str = _str[0:_LEN-0x20] + _DOTS
                continue
            break
        return _str, _dmpLEN

class _RtePSException(_RteException):
    def __init__(self, msg_ : str =None, code_ : int =None, xcp_ : BaseException =None):
        super().__init__(msg_=msg_, code_=code_, xcp_=xcp_, maxXPS_=None)

class _RteTSException(_RteException):
    def __init__(self, msg_ : str =None, code_ : int =None, xcp_ : BaseException =None, maxXPS_ : int =None):
        super().__init__(msg_=msg_, code_=code_, xcp_=xcp_, maxXPS_=maxXPS_)
