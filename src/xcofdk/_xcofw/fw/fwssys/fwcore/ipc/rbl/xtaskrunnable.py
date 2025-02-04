# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xtaskrunnable.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from xcofdk.fwapi.xtask import XTask
from xcofdk.fwapi.xtask import XTaskProfile

from xcofdk._xcofw.fw.fwssys.fwcore.logging       import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.base.util     import _Util
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject import _AbstractSlotsObject

from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.arunnabledefs import _ERunnableType
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.arunnabledefs import _ERunnableApiID
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.arunnabledefs import _ERunProgressID
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.arunnabledefs import _ERunnableApiFuncTag
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.arunnable     import _AbstractRunnable

from xcofdk._xcofw.fw.fwssys.fwerrh.fwerrorcodes import _EFwErrorCode

from xcofdk._xcofw.fw.fwssys.fwcore.apiimpl.xtask.xtaskconn import _XTaskConnector

class _XTaskRunnable(_AbstractRunnable):

    __mandatoryCustomApiMethodNames = [ _ERunnableApiID.eOnRunProgressNotification.functionName ]

    __slots__ = [ '__bEnabledSetUpXtbl' , '__bEnabledTearDownXtbl' , '__bEnabledRunXtbl' , '__bEnabledProcIntMsg' , '__bEnabledProcExtMsg']

    def __init__(self, xtaskConn_ : _XTaskConnector):
        self.__bEnabledRunXtbl      = None
        self.__bEnabledSetUpXtbl    = None
        self.__bEnabledProcIntMsg   = None
        self.__bEnabledProcExtMsg   = None
        self.__bEnabledTearDownXtbl = None
        _AbstractSlotsObject.__init__(self)

        if not isinstance(xtaskConn_, _XTaskConnector):
            self.CleanUp()
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00161)
        elif xtaskConn_._connectedXTask is None:
            self.CleanUp()
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00162)
        elif not (xtaskConn_._connectedXTask.isXtask and isinstance(xtaskConn_._connectedXTask, XTask)):
            self.CleanUp()
            execStr = str(xtaskConn_._connectedXTask)
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00163)
        elif (xtaskConn_.executionProfile is None) or not xtaskConn_.executionProfile.isValid:
            self.CleanUp()
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00164)
        elif not self.__CheckAPI(xtaskConn_._connectedXTask):
            self.CleanUp()
        else:
            _em = _XTaskRunnable.__GetExcludedRunnableApiMask(xtaskConn_._connectedXTask)
            if _em is None:
                self.CleanUp()
            else:
                _AbstractRunnable.__init__( self
                                          , eRblType_= _ERunnableType.eMainXTaskRbl if xtaskConn_.xtaskProfile.isMainTask else _ERunnableType.eXTaskRbl
                                          , xtaskConn_=xtaskConn_
                                          , excludedRblM_=_em
                                          , execProfile_=xtaskConn_.executionProfile)
                if self.__isInvalid:
                    self.CleanUp()

    @staticmethod
    def _GetMandatoryCustomApiMethodNamesList():
        res = []
        _tmp = _AbstractRunnable._GetMandatoryCustomApiMethodNamesList()
        if _tmp is not None:
            res += _tmp
        res += _XTaskRunnable.__mandatoryCustomApiMethodNames
        return res

    def _CleanUp(self):
        if not self.__isInvalid:
            self.__bEnabledRunXtbl      = None
            self.__bEnabledSetUpXtbl    = None
            self.__bEnabledProcIntMsg   = None
            self.__bEnabledProcExtMsg   = None
            self.__bEnabledTearDownXtbl = None
            super()._CleanUp()

    def _RunExecutable(self, *args_, **kwargs_):
        return self.__ExecuteApiFunc(_ERunnableApiFuncTag.eRFTRunExecutable)

    def _SetUpExecutable(self, *args_, **kwargs_):
        return self.__ExecuteApiFunc(_ERunnableApiFuncTag.eRFTSetUpExecutable)

    def _TearDownExecutable(self):
        return self.__ExecuteApiFunc(_ERunnableApiFuncTag.eRFTTearDownExecutable)

    def _ProcessInternalMsg(self, msg_, callback_ =None):
        return self.__ExecuteApiFunc(_ERunnableApiFuncTag.eRFTProcessInternalMsg, msg_, callback_)

    def _ProcessExternalMsg(self, msg_, callback_ =None):
        return self.__ExecuteApiFunc(_ERunnableApiFuncTag.eRFTProcessExternalMsg, msg_, callback_)

    def _OnRunProgressNotification(self, eRunProgressID_ : _ERunProgressID):
        return True

    @staticmethod
    def __GetExcludedRunnableApiMask(xtsk_ : XTask) -> _ERunnableApiFuncTag:

        if not (isinstance(xtsk_, XTask) and isinstance(xtsk_.xtaskProfile, XTaskProfile) and xtsk_.xtaskProfile.isValid):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00165)
            return None

        res = _ERunnableApiFuncTag.DefaultApiMask()
        res = _ERunnableApiFuncTag.AddApiFuncTag(res, _ERunnableApiFuncTag.eRFTProcessInternalQueue)

        if not xtsk_.xtaskProfile.isInternalQueueEnabled:
            res = _ERunnableApiFuncTag.AddApiFuncTag(res, _ERunnableApiFuncTag.eRFTProcessInternalMsg)

        if not xtsk_.xtaskProfile.isExternalQueueEnabled:
            res = _ERunnableApiFuncTag.AddApiFuncTag(res, _ERunnableApiFuncTag.eRFTProcessExternalMsg)
            res = _ERunnableApiFuncTag.AddApiFuncTag(res, _ERunnableApiFuncTag.eRFTProcessExternalQueue)

        else:
            res = _ERunnableApiFuncTag.AddApiFuncTag(res, _ERunnableApiFuncTag.eRFTProcessExternalQueue)

            if xtsk_.xtaskProfile.isExternalQueueBlocking:
                res = _ERunnableApiFuncTag.AddApiFuncTag(res, _ERunnableApiFuncTag.eRFTRunExecutable)

        if not xtsk_.xtaskProfile.isSetupPhaseEnabled:
            res = _ERunnableApiFuncTag.AddApiFuncTag(res, _ERunnableApiFuncTag.eRFTSetUpExecutable)

        if not xtsk_.xtaskProfile.isTeardownPhaseEnabled:
            res = _ERunnableApiFuncTag.AddApiFuncTag(res, _ERunnableApiFuncTag.eRFTTearDownExecutable)
        return res

    @property
    def __isInvalid(self):
        return self._eRunnableType is None

    def __ExecuteApiFunc(self, apiFuncID_ : _ERunnableApiFuncTag, *args_):
        if self.__isInvalid:
            return None

        res     = None
        _bRun   = apiFuncID_ == _ERunnableApiFuncTag.eRFTRunExecutable
        _bSetup = (not _bRun) and (apiFuncID_ == _ERunnableApiFuncTag.eRFTSetUpExecutable)

        if not (_bRun or _bSetup):
            _len    = len(args_)
            _param1 = args_[0] if _len>0 else None
            _param2 = args_[1] if _len>1 else None
        else:
            _param1 = None
            _param2 = None

        if apiFuncID_ == _ERunnableApiFuncTag.eRFTProcessExternalMsg:
            if not self.__bEnabledProcExtMsg:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00166)
            elif not self.isRunning:
                res = False
            elif _param2 is not None:
                res = _param2(_param1)
            else:
                res = self._xtaskInst.ProcessExternalMessage(_param1)

        elif _bSetup:
            if not self.__bEnabledSetUpXtbl:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00167)
            else:
                _args   = self._executionProfile.args
                _kwargs = self._executionProfile.kwargs
                res     = False if not self.isRunning else self._xtaskInst.SetUpXTask(*_args, **_kwargs)
        elif apiFuncID_ == _ERunnableApiFuncTag.eRFTTearDownExecutable:
            if not self.__bEnabledTearDownXtbl:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00168)
            else:
                res = False if not self._isTerminating else self._xtaskInst.TearDownXTask()
        elif _bRun:
            if not self.__bEnabledRunXtbl:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00169)
            elif self.isProvidingSetUpRunnable:
                res = False if not self.isRunning else self._xtaskInst.RunXTask()
            else:
                _args   = self._executionProfile.args
                _kwargs = self._executionProfile.kwargs
                res     = False if not self.isRunning else self._xtaskInst.RunXTask(*_args, **_kwargs)
        else:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00170)
        return res

    def __CheckAPI(self, xtsk_ : XTask) -> bool:
        mmn = _XTaskRunnable.GetMandatoryCustomApiMethodNamesList()
        _numMandatoryApiMehtods = _Util.GetNumAttributes(self, mmn, bThrowx_=True)
        if _numMandatoryApiMehtods != len(mmn):
            res = False
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00171)
        else:
            res = True
            self.__bEnabledRunXtbl      = (not xtsk_.xtaskProfile.isExternalQueueEnabled) or (not xtsk_.xtaskProfile.isExternalQueueBlocking)
            self.__bEnabledSetUpXtbl    = xtsk_.xtaskProfile.isSetupPhaseEnabled
            self.__bEnabledProcIntMsg   = xtsk_.xtaskProfile.isInternalQueueEnabled
            self.__bEnabledProcExtMsg   = xtsk_.xtaskProfile.isExternalQueueEnabled
            self.__bEnabledTearDownXtbl = xtsk_.xtaskProfile.isTeardownPhaseEnabled
        return res
