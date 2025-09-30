# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : logrdagent.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from threading import RLock as _PyRLock
from typing    import Union

from _fw.fwssys.fwcore.logrd.iflogrdsrv          import _ILogRDService
from _fw.fwssys.fwcore.logrd.logrecord           import _ELRType
from _fw.fwssys.fwcore.logrd.logrecord           import _EColorCode
from _fw.fwssys.fwcore.logrd.logrecord           import _LogRecord
from _fw.fwssys.fwcore.logrd.rdsinks.consolesink import _ConsoleSink
from _fw.fwssys.fwcore.swpfm.sysinfo             import _SystemInfo
from _fwa.fwrtecfg.fwrteconfig                   import _FwRteConfig

class _LogRDAgent:
    __slots__ = [ '__a' , '__l' , '__r' , '__s' , '__bH' , '__cs' ]

    __sgltn = None
    __ES    = ''
    __DTS   = '--:--:--.---'
    __NL    = '\n'
    __TSP   = 'milliseconds'

    def __init__(self):
        self.__a  = None
        self.__l  = None
        self.__r  = None
        self.__s  = None
        self.__bH = None
        self.__cs = None

        if _LogRDAgent.__sgltn is not None:
            self._CleanUp()
            return

        _LogRDAgent.__sgltn = self

        self.__l  = _PyRLock()
        self.__r  = _FwRteConfig._GetInstance()
        self.__bH = _LogRDAgent.__ChkHL()
        self.__cs = _ConsoleSink(bHLEnabled_=self.__bH)

    def _PutLR(self, lrec_ : Union[_LogRecord, str], color_ : _EColorCode =_EColorCode.NONE, logType_: _ELRType =_ELRType.LR_FREE):
        self.__l.acquire()

        if not (isinstance(color_, _EColorCode) and color_.isColor):
            color_ = _EColorCode.NONE
        if not isinstance(lrec_, _LogRecord):
            if not isinstance(lrec_, str):
                lrec_ = _LogRDAgent.__ES if lrec_ is None else str(lrec_)
            lrec_ = _LogRecord(lrec_, color_=color_, logType_=logType_)

        _a = self.__a

        if self.__isA and not self.__r._isValid:
            self.__a = None
            if self.__cs is None:
                self.__cs = _ConsoleSink(self.__bH)

        if self.__isA:
            _a.append(lrec_)
        else:
            if self.__s is not None:
                self.__s._AddLR(lrec_)
            elif self.__cs is not None:
                self.__cs.Flush(lrec_)
            lrec_._CleanUp()
        self.__l.release()

    @staticmethod
    def _GetInstance():
        res = _LogRDAgent.__sgltn
        if res is None:
            res = _LogRDAgent()
            _LogRDAgent.__sgltn = res
        return res

    @property
    def _isValid(self):
        return self.__l is not None

    def _AActivate(self):
        if not self._isValid:
            return

        with self.__l:
            if self.__isA:
                return

            self.__a = []
            if self.__cs is not None:
                self.__cs._CleanUp()
                self.__cs = None

    def _ADeactivate(self, bCSEnabled_ : bool, bHLEnabled_ : bool =None, lrds_ : _ILogRDService =None):
        if not self._isValid:
            return

        with self.__l:
            if not self.__isA:
                return

            bHLEnabled_ = _LogRDAgent.__ChkHL(bHLEnabled_)

            _a = self.__a
            self.__a = None

            self.__s  = lrds_
            self.__bH = bHLEnabled_

            if lrds_ is not None:
               lrds_._FlushBacklog(_a, bHLEnabled_)
               _ll = [ _rr for _rr in _a if (_rr._recType is not None) and not _rr._recType.isError]
            elif bCSEnabled_:
                self.__cs = _ConsoleSink(bHLEnabled_=bHLEnabled_)
                self.__cs.Flush(_a)
            for _rr in _a:
                _rr._CleanUp()

    def _CleanUp(self):
        if id(self) == id(_LogRDAgent.__sgltn):
            _LogRDAgent.__sgltn = None
        if self.__l is None:
            return

        if self.__a is not None:
            for _rr in self.__a:
                _rr.CleanUp()
            self.__a.clear()
            self.__a = None

        self.__l  = None
        self.__r  = None
        self.__s  = None
        self.__bH = None
        self.__cs = None

    @staticmethod
    def __ChkHL(bHLEnabled_ : bool =None) -> bool:
        _bPyVerOK = _SystemInfo._IsPythonVersionCompatible(3, 9)
        if not _bPyVerOK:
            bHLEnabled_ = False
        elif bHLEnabled_ is None:
            bHLEnabled_ = not _SystemInfo._IsPlatformWindows()
        return bHLEnabled_

    @property
    def __isA(self):
        return self.__a is not None

