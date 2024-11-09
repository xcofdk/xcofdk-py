# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xtaskrunnable.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from xcofdk.fwapi.xtask import XTask

from xcofdk._xcofw.fw.fwssys.fwcore.logging       import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.base.util     import _Util
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject import _AbstractSlotsObject

from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.arunnabledefs import _ERunnableType
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.arunnabledefs import _ERunnableApiID
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.arunnabledefs import _ERunProgressID
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.arunnabledefs import _ERunnableApiFuncTag
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.arunnable     import _AbstractRunnable

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
            vlogif._LogOEC(True, -1217)
        elif xtaskConn_._connectedXTask is None:
            self.CleanUp()
            vlogif._LogOEC(True, -1218)
        elif not (xtaskConn_._connectedXTask.isXtask and isinstance(xtaskConn_._connectedXTask, XTask)):
            self.CleanUp()
            execStr = str(xtaskConn_._connectedXTask)
            vlogif._LogOEC(True, -1219)
        elif (xtaskConn_.executionProfile is None) or not xtaskConn_.executionProfile.isValid:
            self.CleanUp()
            vlogif._LogOEC(True, -1220)
        elif not self.__CheckAPI(xtaskConn_._connectedXTask):
            self.CleanUp()
        else:
            _em = _XTaskRunnable.__GetExcludedRunnableApiMask(xtaskConn_._connectedXTask)

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
        tmp = _AbstractRunnable._GetMandatoryCustomApiMethodNamesList()
        if tmp is not None:
            res += tmp
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

    def _RunExecutable(self):
        return self.__ExecuteApiFunc(_ERunnableApiFuncTag.eRFTRunExecutable)

    def _SetUpExecutable(self):
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

    def __ExecuteApiFunc(self, apiFuncID_ : _ERunnableApiFuncTag, param1_ =None, param2_ =None):

        res = None
        if self.__isInvalid:
            pass
        else:
            if apiFuncID_==_ERunnableApiFuncTag.eRFTProcessExternalMsg:
                if not self.__bEnabledProcExtMsg:
                    vlogif._LogOEC(True, -1221)
                elif not self.isRunning:
                    res = False
                elif param2_ is not None:
                    res = param2_(param1_)
                else:
                    res = self._xtaskInst.ProcessExternalMessage(param1_)
            elif apiFuncID_==_ERunnableApiFuncTag.eRFTProcessInternalMsg:
                if not self.__bEnabledProcIntMsg:
                    vlogif._LogOEC(True, -1222)
                elif not self.isRunning:
                    res = False
                elif param2_ is not None:
                    res = param2_(param1_)
                else:
                    res = self._xtaskInst.ProcessInternalMessage(param1_)

            elif apiFuncID_ == _ERunnableApiFuncTag.eRFTSetUpExecutable:
                if not self.__bEnabledSetUpXtbl:
                    vlogif._LogOEC(True, -1223)
                else:
                    res = False if not self.isRunning else self._xtaskInst.SetUpXTask()
            elif apiFuncID_ == _ERunnableApiFuncTag.eRFTTearDownExecutable:
                if not self.__bEnabledTearDownXtbl:
                    vlogif._LogOEC(True, -1224)
                else:
                    res = False if not self._isTerminating else self._xtaskInst.TearDownXTask()
            elif apiFuncID_ == _ERunnableApiFuncTag.eRFTRunExecutable:
                if not self.__bEnabledRunXtbl:
                    vlogif._LogOEC(True, -1225)
                else:
                    res = False if not self.isRunning else self._xtaskInst.RunXTask()
            else:
                vlogif._LogOEC(True, -1226)
        return res

    def __CheckAPI(self, xtsk_ : XTask) -> bool:
        mmn = _XTaskRunnable.GetMandatoryCustomApiMethodNamesList()
        _numMandatoryApiMehtods = _Util.GetNumAttributes(self, mmn, bThrowx_=True)
        if _numMandatoryApiMehtods != len(mmn):
            res = False
            vlogif._LogOEC(True, -1227)
        else:
            res = True
            self.__bEnabledRunXtbl      = (not xtsk_.xtaskProfile.isExternalQueueEnabled) or (not xtsk_.xtaskProfile.isExternalQueueBlocking)
            self.__bEnabledSetUpXtbl    = xtsk_.xtaskProfile.isSetupPhaseEnabled
            self.__bEnabledProcIntMsg   = xtsk_.xtaskProfile.isInternalQueueEnabled
            self.__bEnabledProcExtMsg   = xtsk_.xtaskProfile.isExternalQueueEnabled
            self.__bEnabledTearDownXtbl = xtsk_.xtaskProfile.isTeardownPhaseEnabled
        return res
