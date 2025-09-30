# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : arbldefs.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum import auto
from enum import unique

from _fw.fwssys.fwcore.logging           import vlogif
from _fw.fwssys.fwcore.ipc.tsk.taskutil  import _ETaskXPhaseID
from _fw.fwssys.fwcore.types.ebitmask    import _EBitMask
from _fw.fwssys.fwcore.types.commontypes import _FwEnum
from _fw.fwssys.fwcore.types.commontypes import _FwIntEnum
from _fw.fwssys.fwcore.types.commontypes import _FwIntFlag
from _fw.fwssys.fwcore.types.aobject     import _AbsSlotsObject
from _fw.fwssys.fwcore.types.commontypes import _CommonDefines
from _fw.fwssys.fwcore.types.commontypes import _EExecutionCmdID
from _fw.fwssys.fwerrh.fwerrorcodes      import _EFwErrorCode

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

@unique
class _ERunProgressID(_FwIntEnum):
    eReadyToRun          = 220
    eExecuteSetupDone    = auto()
    eExecuteRunDone      = auto()
    eExecuteTeardownDone = auto()
    eRunDone             = auto()

    @property
    def isReadyToRun(self):
        return self == _ERunProgressID.eReadyToRun

    @property
    def isExecuteSetupDone(self):
        return self == _ERunProgressID.eExecuteSetupDone

    @property
    def isExecuteRunDone(self):
        return self == _ERunProgressID.eExecuteRunDone

    @property
    def isExecuteTeardownDone(self):
        return self == _ERunProgressID.eExecuteTeardownDone

    @property
    def isRunDone(self):
        return self == _ERunProgressID.eRunDone

    @property
    def isPostRunPhase(self):
        return self.value > _ERunProgressID.eExecuteRunDone.value

@unique
class _ERblExecStepID(_FwIntEnum):
    eSetUpExecutable                                         = 3821
    eTeardownExecutable                                      = auto()
    eRunExecutable                                           = auto()
    eCustomManagedExternalQueue                              = auto()
    eAutoManagedExternalQueue                                = auto()
    eAutoManagedExternalQueue_By_RunExecutable               = auto()
    eCustomManagedInternalQueue_By_RunExecutable             = auto()
    eCustomManagedInternalQueue_By_AutoManagedExternalQueue  = auto()
    eAutoManagedInternalQueue_By_RunExecutable               = auto()
    eAutoManagedInternalQueue_By_AutoManagedExternalQueue    = auto()

@unique
class _ERblApiID(_FwEnum):
    eRunExecutable                  = 0
    eSetUpExecutable                = 1
    eTearDownExecutable             = 2
    eProcessInternalMsg             = 3
    eProcessExternalMsg             = 4
    eProcessInternalQueue           = 5
    eProcessExternalQueue           = 6
    eOnTimeoutExpired               = 7
    eOnRunProgressNotification      = 8
    ePrepareCeasing                 =  9
    eRunCeaseIteration              = 10
    eProcFwcTENotification          = 11
    eProcFwcErrorHandlerCallback    = 12

    @property
    def functionName(self):
        return _CommonDefines._CHAR_SIGN_UNDERSCORE + self.compactName

@unique
class _ERblApiFuncTag(_FwIntFlag):
    eNone = 0x0000
    eRFTRunExecutable             = (0x0001 <<  _ERblApiID.eRunExecutable.value)
    eRFTSetUpExecutable           = (0x0001 <<  _ERblApiID.eSetUpExecutable.value)
    eRFTTearDownExecutable        = (0x0001 <<  _ERblApiID.eTearDownExecutable.value)
    eRFTProcessInternalMsg        = (0x0001 <<  _ERblApiID.eProcessInternalMsg.value)
    eRFTProcessExternalMsg        = (0x0001 <<  _ERblApiID.eProcessExternalMsg.value)
    eRFTProcessInternalQueue      = (0x0001 <<  _ERblApiID.eProcessInternalQueue.value)
    eRFTProcessExternalQueue      = (0x0001 <<  _ERblApiID.eProcessExternalQueue.value)
    eRFTOnTimeoutExpired          = (0x0001 <<  _ERblApiID.eOnTimeoutExpired.value)
    eRFTOnRunProgressNotification = (0x0001 <<  _ERblApiID.eOnRunProgressNotification.value)
    eRFTPrepareCeasing              = (0x0001 << _ERblApiID.ePrepareCeasing.value)
    eRFTRunCeaseIteration           = (0x0001 << _ERblApiID.eRunCeaseIteration.value)
    eRFTProcFwcTENotification       = (0x0001 << _ERblApiID.eProcFwcTENotification.value)
    eRFTProcFwcErrorHandlerCallback = (0x0001 << _ERblApiID.eProcFwcErrorHandlerCallback.value)

    @property
    def isRunnableExecutionAPI(self):
        return (self != _ERblApiFuncTag.eNone) and (self.value < _ERblApiFuncTag.eRFTPrepareCeasing.value)

    @property
    def functionName(self):
        return _ERblApiID(self.rightMostBitPosition).functionName

    def MapToTaskExecutionPhaseID(self, bUTask_ =False) -> _ETaskXPhaseID:
        if self == _ERblApiFuncTag.eRFTRunExecutable:
            res = _ETaskXPhaseID.eXTaskRun if bUTask_ else _ETaskXPhaseID.eRblRun

        elif self == _ERblApiFuncTag.eRFTSetUpExecutable:
            res = _ETaskXPhaseID.eXTaskSetup if bUTask_ else _ETaskXPhaseID.eRblSetup

        elif self == _ERblApiFuncTag.eRFTTearDownExecutable:
            res = _ETaskXPhaseID.eXTaskTeardown if bUTask_ else _ETaskXPhaseID.eRblTeardown

        elif self == _ERblApiFuncTag.eRFTOnTimeoutExpired:
            res = _ETaskXPhaseID.eRblMisc

        elif self == _ERblApiFuncTag.eRFTProcessExternalMsg:
            res = _ETaskXPhaseID.eXTaskProcExtMsg if bUTask_ else _ETaskXPhaseID.eRblProcExtMsg

        elif self == _ERblApiFuncTag.eRFTProcessInternalMsg:
            res = _ETaskXPhaseID.eXTaskProcIntMsg if bUTask_ else _ETaskXPhaseID.eRblProcIntMsg

        elif self == _ERblApiFuncTag.eRFTProcessExternalQueue:
            res = _ETaskXPhaseID.eRblProcExtQueue

        elif self == _ERblApiFuncTag.eRFTProcessInternalQueue:
            res = _ETaskXPhaseID.eRblProcIntQueue

        elif self == _ERblApiFuncTag.eRFTOnRunProgressNotification:
            res = _ETaskXPhaseID.eRblMisc

        else:
            res = _ETaskXPhaseID.eNA
        return res

    @staticmethod
    def IsNone(eApiMask_: _FwIntFlag):
        return eApiMask_==_ERblApiFuncTag.eNone

    @staticmethod
    def IsEnabledRunExecutable(eApiMask_: _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eApiMask_, _ERblApiFuncTag.eRFTRunExecutable)

    @staticmethod
    def IsEnabledSetUpExecutable(eApiMask_: _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eApiMask_, _ERblApiFuncTag.eRFTSetUpExecutable)

    @staticmethod
    def IsEnabledTearDownExecutable(eApiMask_: _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eApiMask_, _ERblApiFuncTag.eRFTTearDownExecutable)

    @staticmethod
    def IsEnabledOnTimeoutExpired(eApiMask_: _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eApiMask_, _ERblApiFuncTag.eRFTOnTimeoutExpired)

    @staticmethod
    def IsEnabledProcessExternalMsg(eApiMask_: _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eApiMask_, _ERblApiFuncTag.eRFTProcessExternalMsg)

    @staticmethod
    def IsEnabledProcessInternalMsg(eApiMask_: _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eApiMask_, _ERblApiFuncTag.eRFTProcessInternalMsg)

    @staticmethod
    def IsEnabledProcessExternalQueue(eApiMask_: _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eApiMask_, _ERblApiFuncTag.eRFTProcessExternalQueue)

    @staticmethod
    def IsEnabledProcessInternalQueue(eApiMask_: _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eApiMask_, _ERblApiFuncTag.eRFTProcessInternalQueue)

    @staticmethod
    def IsEnabledOnRunProgressNotification(eApiMask_: _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eApiMask_, _ERblApiFuncTag.eRFTOnRunProgressNotification)

    @staticmethod
    def IsEnabledProcFwcTENotification(eApiMask_: _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eApiMask_, _ERblApiFuncTag.eRFTProcFwcTENotification)

    @staticmethod
    def IsEnabledProcFwcErrorHandlerCallback(eApiMask_: _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eApiMask_, _ERblApiFuncTag.eRFTProcFwcErrorHandlerCallback)

    @staticmethod
    def IsEnabledPrepareCeasing(eApiMask_: _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eApiMask_, _ERblApiFuncTag.eRFTPrepareCeasing)

    @staticmethod
    def IsEnabledRunCeaseIteration(eApiMask_: _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eApiMask_, _ERblApiFuncTag.eRFTRunCeaseIteration)

    @staticmethod
    def IsEnabledApiFunction(eApiMask_: _FwIntFlag, apiFTag_: _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eApiMask_, apiFTag_)

    @staticmethod
    def DefaultApiMask():
        return _ERblApiFuncTag.eNone

    @staticmethod
    def AddApiFuncTag(eApiMask_: _FwIntFlag, apiFTag_ : _FwIntFlag):
        return _EBitMask.AddEnumBitFlag(eApiMask_, apiFTag_)

    @staticmethod
    def RemoveApiFuncTag(eApiMask_: _FwIntFlag, apiFTag_ : _FwIntFlag):
        return _EBitMask.RemoveEnumBitFlag(eApiMask_, apiFTag_)

class _ARblApiGuide(_AbsSlotsObject):
    __slots__ = [ '__r' , '__m' , '__xm' , '__xcr' , '__gt' , '__cp' , '__cri', '__nt' , '__nrp' , '__ncte' , '__nccb' , '__phxr' , '__phxs' , '__phxt' , '__phxxm' , '__phxim' , '__phxxq' , '__phxiq' ]

    def __init__(self, rbl_, rblXM_ : _ERblApiFuncTag):
        self.__r     = rbl_
        self.__m     = None
        self.__gt    = None
        self.__cp    = None
        self.__nt    = None
        self.__xm    = None
        self.__cri   = None
        self.__nrp   = None
        self.__xcr   = None
        self.__ncte  = None
        self.__nccb  = None
        self.__phxr  = None
        self.__phxs  = None
        self.__phxt  = None
        self.__phxxm = None
        self.__phxim = None
        self.__phxxq = None
        self.__phxiq = None

        super().__init__()

        _xf = None
        if rblXM_ is not None:
            if not isinstance(rblXM_, _ERblApiFuncTag):
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00148)
                self.CleanUp()
                return

            _xf = _EBitMask.GetIntegerBitFlagsList(rblXM_)
            if _xf is None:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00149)
                self.CleanUp()
                return
            if len(_xf) == 0:
                _xf = None

        self.__m = _ERblApiFuncTag.DefaultApiMask()
        self.__xm = rblXM_

        for _n, _m in _ERblApiFuncTag.__members__.items():
            if _m == _ERblApiFuncTag.eNone:
                continue
            if _EBitMask.IsEnumBitFlagSet(self.__m, _m):
                continue
            if _xf is not None:
                if _m.value in _xf:
                    continue

            _f = getattr(rbl_, _m.functionName, None)
            if _f is None:
                continue

            self.__m = _ERblApiFuncTag.AddApiFuncTag(self.__m, _m)

            if   _m == _ERblApiFuncTag.eRFTRunExecutable:             self.runExecutable             = _f
            elif _m == _ERblApiFuncTag.eRFTSetUpExecutable:           self.setUpRunnable             = _f
            elif _m == _ERblApiFuncTag.eRFTProcessExternalMsg:        self.procExternalMsg           = _f
            elif _m == _ERblApiFuncTag.eRFTProcessInternalMsg:        self.procInternalMsg           = _f
            elif _m == _ERblApiFuncTag.eRFTOnTimeoutExpired:          self.onTimeoutExpired          = _f
            elif _m == _ERblApiFuncTag.eRFTTearDownExecutable:        self.tearDownRunnable          = _f
            elif _m == _ERblApiFuncTag.eRFTProcessExternalQueue:      self.procExternalQueue         = _f
            elif _m == _ERblApiFuncTag.eRFTProcessInternalQueue:      self.procInternalQueue         = _f
            elif _m == _ERblApiFuncTag.eRFTOnRunProgressNotification: self.onRunProgressNotification = _f

            elif _m == _ERblApiFuncTag.eRFTPrepareCeasing:              self.prepareCeasing              = _f
            elif _m == _ERblApiFuncTag.eRFTRunCeaseIteration:           self.runCeaseIteration           = _f
            elif _m == _ERblApiFuncTag.eRFTProcFwcTENotification:       self.procFwcTENotification       = _f
            elif _m == _ERblApiFuncTag.eRFTProcFwcErrorHandlerCallback: self.procFwcErrorHandlerCallback = _f

            else:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00150)
                self.__m  = None
                self.__xm = None
                self.CleanUp()
                return

    @property
    def runExecutable(self):
        return self.__phxr

    @runExecutable.setter
    def runExecutable(self, vv_):
        self.__phxr = vv_

    @property
    def setUpRunnable(self):
        return self.__phxs

    @setUpRunnable.setter
    def setUpRunnable(self, vv_):
        self.__phxs = vv_

    @property
    def procExternalMsg(self):
        return self.__phxxm

    @procExternalMsg.setter
    def procExternalMsg(self, vv_):
        self.__phxxm = vv_

    @property
    def procInternalMsg(self):
        return self.__phxim

    @procInternalMsg.setter
    def procInternalMsg(self, vv_):
        self.__phxim = vv_

    @property
    def onTimeoutExpired(self):
        return self.__nt

    @onTimeoutExpired.setter
    def onTimeoutExpired(self, vv_):
        self.__nt = vv_

    @property
    def tearDownRunnable(self):
        return self.__phxt

    @tearDownRunnable.setter
    def tearDownRunnable(self, vv_):
        self.__phxt = vv_

    @property
    def procExternalQueue(self):
        return self.__phxxq

    @procExternalQueue.setter
    def procExternalQueue(self, vv_):
        self.__phxxq = vv_

    @property
    def procInternalQueue(self):
        return self.__phxiq

    @procInternalQueue.setter
    def procInternalQueue(self, vv_):
        self.__phxiq = vv_

    @property
    def onRunProgressNotification(self):
        return self.__nrp

    @onRunProgressNotification.setter
    def onRunProgressNotification(self, vv_):
        self.__nrp = vv_

    @property
    def getRunLoopCycleTimeout(self):
        return self.__gt

    @getRunLoopCycleTimeout.setter
    def getRunLoopCycleTimeout(self, vv_):
        self.__gt = vv_

    @property
    def prepareCeasing(self):
        return self.__cp

    @prepareCeasing.setter
    def prepareCeasing(self, vv_):
        self.__cp= vv_

    @property
    def runCeaseIteration(self):
        return self.__cri

    @runCeaseIteration.setter
    def runCeaseIteration(self, vv_):
        self.__cri = vv_

    @property
    def procFwcTENotification(self):
        return self.__ncte

    @procFwcTENotification.setter
    def procFwcTENotification(self, vv_):
        self.__ncte = vv_

    @property
    def procFwcErrorHandlerCallback(self):
        return self.__nccb

    @procFwcErrorHandlerCallback.setter
    def procFwcErrorHandlerCallback(self, vv_):
        self.__nccb = vv_

    @property
    def apiMask(self) -> _ERblApiFuncTag:
        return self.__m

    @property
    def exclApiMask(self) -> _ERblApiFuncTag:
        return self.__xm

    @property
    def isProvidingRunExecutable(self):
        return False if self.__m is None else _ERblApiFuncTag.IsEnabledRunExecutable(self.__m)

    @property
    def isProvidingSetUpRunnable(self):
        return False if self.__m is None else _ERblApiFuncTag.IsEnabledSetUpExecutable(self.__m)

    @property
    def isProvidingTearDownRunnable(self):
        return False if self.__m is None else _ERblApiFuncTag.IsEnabledTearDownExecutable(self.__m)

    @property
    def isProvidingOnTimeoutExpired(self):
        return False if self.__m is None else _ERblApiFuncTag.IsEnabledOnTimeoutExpired(self.__m)

    @property
    def isProvidingProcessExternalMsg(self):
        return False if self.__m is None else _ERblApiFuncTag.IsEnabledProcessExternalMsg(self.__m)

    @property
    def isProvidingProcessInternalMsg(self):
        return False if self.__m is None else _ERblApiFuncTag.IsEnabledProcessInternalMsg(self.__m)

    @property
    def isProvidingProcessExternalQueue(self):
        return False if self.__m is None else _ERblApiFuncTag.IsEnabledProcessExternalQueue(self.__m)

    @property
    def isProvidingProcessInternalQueue(self):
        return False if self.__m is None else _ERblApiFuncTag.IsEnabledProcessInternalQueue(self.__m)

    @property
    def isProvidingOnRunProgressNotification(self):
        return False if self.__m is None else _ERblApiFuncTag.IsEnabledOnRunProgressNotification(self.__m)

    @property
    def isProvidingRunCeaseIteration(self):
        return False if self.__m is None else _ERblApiFuncTag.IsEnabledRunCeaseIteration(self.__m)

    @property
    def isProvidingPrepareCeasing(self):
        return False if self.__m is None else _ERblApiFuncTag.IsEnabledPrepareCeasing(self.__m)

    @property
    def isProvidingProcFwcTENotification(self):
        return False if self.__m is None else _ERblApiFuncTag.IsEnabledProcFwcTENotification(self.__m)

    @property
    def isProvidingProcFwcErrorHandlerCallback(self):
        return False if self.__m is None else _ERblApiFuncTag.IsEnabledProcFwcErrorHandlerCallback(self.__m)

    @property
    def _xcmdReturn(self) -> _EExecutionCmdID:
        return self.__xcr

    @property
    def _runnable(self):
        return self.__r

    def _IsProvidingApiFunction(self, apiFTag_ : _ERblApiFuncTag):
        return False if self.__m is None else _ERblApiFuncTag.IsEnabledApiFunction(self.__m, apiFTag_)

    def _ToString(self, bCompact_ =True):
        if self.__m is None:
            return None

        _myTxt = _ARblApiGuide.__ApiMask2String(self.__m)
        res = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_ApiGuide_ApiMask)
        res = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_004).format(type(self).__name__, res, _myTxt)
        if not bCompact_:
            if self.__xm is not None:
                _myTxt = _ARblApiGuide.__ApiMask2String(self.__xm, bExcluded_=True)
                res   += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_NewlineTab) + _myTxt
        return res

    def _CleanUp(self):
        self.__r     = None
        self.__m     = None
        self.__gt    = None
        self.__cp    = None
        self.__nt    = None
        self.__xm    = None
        self.__cri   = None
        self.__nrp   = None
        self.__xcr   = None
        self.__ncte  = None
        self.__nccb  = None
        self.__phxr  = None
        self.__phxs  = None
        self.__phxt  = None
        self.__phxxm = None
        self.__phxim = None
        self.__phxxq = None
        self.__phxiq = None

    def _SetGetReturnedExecCmd(self, xcmd_ : _EExecutionCmdID, bApplyConvertBefore_ =True) -> _EExecutionCmdID:
        if not bApplyConvertBefore_:
            res = xcmd_
        else:
            res = _EExecutionCmdID.ConvertFrom(xcmd_)
        self.__xcr = res
        return res

    @staticmethod
    def __ApiMask2String(rblApiMask_ : _ERblApiFuncTag, bExcluded_ =False):
        res = _EFwTextID.eMisc_Shared_ApiGuide_ExcludedApiMask if bExcluded_ else _EFwTextID.eMisc_Shared_ApiGuide_ApiMask
        res = _FwTDbEngine.GetText(res)
        res = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_005).format(res, hex(rblApiMask_))

        _myTxt = _CommonDefines._STR_EMPTY
        for _n, _m in _ERblApiFuncTag.__members__.items():
            if _m == _ERblApiFuncTag.eNone:
                continue
            if not _EBitMask.IsEnumBitFlagSet(rblApiMask_, _m):
                continue
            _myTxt += _CommonDefines._CHAR_SIGN_TAB + _m.functionName + _CommonDefines._CHAR_SIGN_LF

        if len(_myTxt) > 0:
            _myTxt = _myTxt.rstrip()
            res   += _CommonDefines._CHAR_SIGN_LF + _myTxt
        return res
