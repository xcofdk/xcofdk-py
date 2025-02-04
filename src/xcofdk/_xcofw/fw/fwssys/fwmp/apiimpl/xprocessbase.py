# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xprocessbase.py
#
# Copyright(c) 2024 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from xcofdk.fwcom         import override
from xcofdk.fwcom.xmpdefs import ChildProcessResultData

from xcofdk._xcofw.fw.fwssys.fwmp.xprocessconn           import _XProcessConnector
from xcofdk._xcofw.fw.fwssys.fwmp.apiimpl.xprocessbaseif import _XProcessBaseIF

class _XProcessBase(_XProcessBaseIF):
    __slots__ = [ '__xpc' , '__pid' , '__pname' , '__pec' , '__pres' ]

    def __init__(self, target_, name_ : str =None, args_ : tuple =None, kwargs_ : dict =None, maxDataSize_ : int =None):
        super().__init__()
        self.__pec   = None
        self.__pid   = None
        self.__xpc   = None
        self.__pres  = None
        self.__pname = None

        _xpc = _XProcessConnector(self, target_, name_=name_, args_=args_, kwargs_=kwargs_, maxDataSize_=maxDataSize_)
        if not _xpc.isValid:
            _xpc.CleanUp()
            self.CleanUp()
            return

        self.__xpc   = _xpc
        self.__pname = self.__xpc._processName

    def __str__(self) -> str:
        return self.ToString()

    @property
    def _isAttachedToFW(self):
        return not self.__isDetachedFromFW

    @property
    def _isStarted(self) -> bool:
        return False if self.__isDetachedFromFW else self.__xpc._GetCurProcessState().isPStarted

    @property
    def _isRunning(self) -> bool:
        return False if self.__isDetachedFromFW else self.__xpc._GetCurProcessState().isPRunning

    @property
    def _isDone(self) -> bool:
        return False if self.__isDetachedFromFW else self.__xpc._GetCurProcessState().isPDone

    @property
    def _isFailed(self) -> bool:
        return False if self.__isDetachedFromFW else self.__xpc._GetCurProcessState().isPFailed

    @property
    def _isTerminated(self) -> bool:
        return False if self.__isDetachedFromFW else self.__xpc._GetCurProcessState().isPTerminated

    @property
    def _xprocessPID(self) -> int:
        return self.__pid

    @property
    def _xprocessName(self) -> str:
        return self.__pname

    @property
    def _xprocessResult(self) -> ChildProcessResultData:
        res = self.__pres
        if res is None:
            res = None if self.__isDetachedFromFW else self.__xpc._processResult
            self.__pres = res
        return res

    @property
    def _xprocessExitCode(self) -> int:
        return self.__pec

    @override
    def _SetProcessExitCode(self, ec_ : int):
        self.__pec = ec_

    @override
    def _SetProcessResult(self, procResData_ : ChildProcessResultData):
        self.__pres = procResData_

    def _Start(self) -> bool:
        if self.__isDetachedFromFW:
            return False
        res = self.__xpc._StartProcess()
        if res:
            self.__pec = self.__xpc._processExitCode
            self.__pid = self.__xpc._processPID
        return res

    def _Stop(self):
        pass

    def _Join(self):
        if self.__isDetachedFromFW:
            return
        self.__xpc._JoinProcess()
        self.__pec = self.__xpc._processExitCode

    def _DetachFromFW(self):
        if self.__isDetachedFromFW:
            return
        _ec, _procRes = self.__xpc._DetachFromFW()

        self.__xpc = None

    def _CleanUp(self):
        if self.__isInvalid:
            return

        self.__pec   = None
        self.__pid   = None
        self.__xpc   = None
        self.__pres  = None
        self.__pname = None

    def _ToString(self, *args_, **kwargs_):
        if self.__isInvalid:
            return ''
        return ''

    @property
    def __isInvalid(self):
        return self.__pname is None

    @property
    def __isDetachedFromFW(self):
        return (self.__pname is None) or (self.__xpc is None)
