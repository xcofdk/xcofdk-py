# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : arunnabledefs.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from enum import unique

from xcofdk._xcofw.fw.fwssys.fwcore.logging           import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil  import _ETaskExecutionPhaseID
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcdefines      import _ELcCompID
from xcofdk._xcofw.fw.fwssys.fwcore.types.ebitmask    import _EBitMask
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes import _FwEnum
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes import _FwIntEnum
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes import _FwIntFlag
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject     import _AbstractSlotsObject
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes import _CommonDefines
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes import _ETernaryOpResult

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine


@unique
class _ERunnableType(_FwIntEnum):
    eUserRbl      =2750
    eUTRbl        =2751
    eXTaskRbl     =2752
    eMainXTaskRbl =2753
    eFwRbl        =2754
    eFwMainRbl    =2755
    eFwDsprRbl    =2756
    eTmrMgrRbl    =2757

    @property
    def isUserRunnable(self):
        return not self.isFwRunnable

    @property
    def isXTaskRunnable(self):
        return (self == _ERunnableType.eXTaskRbl) or (self == _ERunnableType.eMainXTaskRbl)

    @property
    def isMainXTaskRunnable(self):
        return self == _ERunnableType.eMainXTaskRbl

    @property
    def isUnitTestRunnable(self):
        return self ==  _ERunnableType.eUTRbl

    @property
    def isFwRunnable(self):
        return self.value >= _ERunnableType.eFwRbl.value

    @property
    def isFwMainRunnable(self):
        return self ==  _ERunnableType.eFwMainRbl

    @property
    def isFwDispatcherRunnable(self):
        return self ==  _ERunnableType.eFwDsprRbl

    @property
    def isTimerManagerRunnable(self):
        return self ==  _ERunnableType.eTmrMgrRbl

    @property
    def toLcCompID(self) -> _ELcCompID:
        if self.isMainXTaskRunnable:
            res = _ELcCompID.eMainXTask
        elif self.isXTaskRunnable:
            res = _ELcCompID.eXTask
        elif self.isFwMainRunnable:
            res = _ELcCompID.eFwMain
        elif self.isFwDispatcherRunnable:
            res = _ELcCompID.eFwDspr
        elif self.isTimerManagerRunnable:
            res = _ELcCompID.eTmrMgr
        elif self.isFwRunnable:
            res = _ELcCompID.eFwComp
        else:
            res = _ELcCompID.eMiscComp
        return res


@unique
class _EFwcID(_FwIntEnum):
    eFwMain       = _ERunnableType.eFwMainRbl.value
    eFwDispatcher = _ERunnableType.eFwDsprRbl.value
    eTimerManager = _ERunnableType.eTmrMgrRbl.value

    @property
    def isFwMain(self):
        return self ==   _EFwcID.eFwMain

    @property
    def isFwDispatcher(self):
        return self ==   _EFwcID.eFwDispatcher

    @property
    def isTimerManager(self):
        return self ==   _EFwcID.eTimerManager


@unique
class _ERunProgressID(_FwIntEnum):

    eReadyToRun          = 220
    eExecuteSetupDone    = 221
    eExecuteRunDone      = 222
    eExecuteTeardownDone = 223
    eRunDone             = 224

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


@unique
class _ERunnableExecutionStepID(_FwIntEnum):

    eSetUpExecutable                                         = 3821
    eTeardownExecutable                                      = 3822
    eRunExecutable                                           = 3823
    eCustomManagedExternalQueue                              = 3824
    eAutoManagedExternalQueue                                = 3825
    eAutoManagedExternalQueue_By_RunExecutable               = 3826
    eCustomManagedInternalQueue_By_RunExecutable             = 3827
    eCustomManagedInternalQueue_By_AutoManagedExternalQueue  = 3828
    eAutoManagedInternalQueue_By_RunExecutable               = 3829
    eAutoManagedInternalQueue_By_AutoManagedExternalQueue    = 3830


@unique
class _ERunnableApiID(_FwEnum):

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
class _ERunnableApiFuncTag(_FwIntFlag):

    eNone = 0x0000
    eRFTRunExecutable             = (0x0001 <<  _ERunnableApiID.eRunExecutable.value)
    eRFTSetUpExecutable           = (0x0001 <<  _ERunnableApiID.eSetUpExecutable.value)
    eRFTTearDownExecutable        = (0x0001 <<  _ERunnableApiID.eTearDownExecutable.value)
    eRFTProcessInternalMsg        = (0x0001 <<  _ERunnableApiID.eProcessInternalMsg.value)
    eRFTProcessExternalMsg        = (0x0001 <<  _ERunnableApiID.eProcessExternalMsg.value)
    eRFTProcessInternalQueue      = (0x0001 <<  _ERunnableApiID.eProcessInternalQueue.value)
    eRFTProcessExternalQueue      = (0x0001 <<  _ERunnableApiID.eProcessExternalQueue.value)
    eRFTOnTimeoutExpired          = (0x0001 <<  _ERunnableApiID.eOnTimeoutExpired.value)
    eRFTOnRunProgressNotification = (0x0001 <<  _ERunnableApiID.eOnRunProgressNotification.value)
    eRFTPrepareCeasing              = (0x0001 << _ERunnableApiID.ePrepareCeasing.value)
    eRFTRunCeaseIteration           = (0x0001 << _ERunnableApiID.eRunCeaseIteration.value)
    eRFTProcFwcTENotification       = (0x0001 << _ERunnableApiID.eProcFwcTENotification.value)
    eRFTProcFwcErrorHandlerCallback = (0x0001 << _ERunnableApiID.eProcFwcErrorHandlerCallback.value)

    @property
    def isRunnableExecutionAPI(self):
        return (self != _ERunnableApiFuncTag.eNone) and (self.value < _ERunnableApiFuncTag.eRFTPrepareCeasing.value)

    @property
    def functionName(self):
        return _ERunnableApiID(self.rightMostBitPosition).functionName

    def MapToTaskExecutionPhaseID(self, bXTask_ =False) -> _ETaskExecutionPhaseID:
        if self == _ERunnableApiFuncTag.eRFTRunExecutable:
            res = _ETaskExecutionPhaseID.eXTaskRun if bXTask_ else _ETaskExecutionPhaseID.eRblRun

        elif self == _ERunnableApiFuncTag.eRFTSetUpExecutable:
            res = _ETaskExecutionPhaseID.eXTaskSetup if bXTask_ else _ETaskExecutionPhaseID.eRblSetup

        elif self == _ERunnableApiFuncTag.eRFTTearDownExecutable:
            res = _ETaskExecutionPhaseID.eXTaskTeardown if bXTask_ else _ETaskExecutionPhaseID.eRblTeardown

        elif self == _ERunnableApiFuncTag.eRFTOnTimeoutExpired:
            res = _ETaskExecutionPhaseID.eRblMisc

        elif self == _ERunnableApiFuncTag.eRFTProcessExternalMsg:
            res = _ETaskExecutionPhaseID.eXTaskProcExtMsg if bXTask_ else _ETaskExecutionPhaseID.eRblProcExtMsg

        elif self == _ERunnableApiFuncTag.eRFTProcessInternalMsg:
            res = _ETaskExecutionPhaseID.eXTaskProcIntMsg if bXTask_ else _ETaskExecutionPhaseID.eRblProcIntMsg

        elif self == _ERunnableApiFuncTag.eRFTProcessExternalQueue:
            res = _ETaskExecutionPhaseID.eRblProcExtQueue

        elif self == _ERunnableApiFuncTag.eRFTProcessInternalQueue:
            res = _ETaskExecutionPhaseID.eRblProcIntQueue

        elif self == _ERunnableApiFuncTag.eRFTOnRunProgressNotification:
            res = _ETaskExecutionPhaseID.eRblMisc

        else:
            res = _ETaskExecutionPhaseID.eNone
        return res

    @staticmethod
    def IsNone(eApiMask_: _FwIntFlag):
        return eApiMask_==_ERunnableApiFuncTag.eNone

    @staticmethod
    def IsEnabledRunExecutable(eApiMask_: _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eApiMask_, _ERunnableApiFuncTag.eRFTRunExecutable)

    @staticmethod
    def IsEnabledSetUpExecutable(eApiMask_: _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eApiMask_, _ERunnableApiFuncTag.eRFTSetUpExecutable)

    @staticmethod
    def IsEnabledTearDownExecutable(eApiMask_: _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eApiMask_, _ERunnableApiFuncTag.eRFTTearDownExecutable)

    @staticmethod
    def IsEnabledOnTimeoutExpired(eApiMask_: _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eApiMask_, _ERunnableApiFuncTag.eRFTOnTimeoutExpired)

    @staticmethod
    def IsEnabledProcessExternalMsg(eApiMask_: _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eApiMask_, _ERunnableApiFuncTag.eRFTProcessExternalMsg)

    @staticmethod
    def IsEnabledProcessInternalMsg(eApiMask_: _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eApiMask_, _ERunnableApiFuncTag.eRFTProcessInternalMsg)

    @staticmethod
    def IsEnabledProcessExternalQueue(eApiMask_: _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eApiMask_, _ERunnableApiFuncTag.eRFTProcessExternalQueue)

    @staticmethod
    def IsEnabledProcessInternalQueue(eApiMask_: _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eApiMask_, _ERunnableApiFuncTag.eRFTProcessInternalQueue)

    @staticmethod
    def IsEnabledOnRunProgressNotification(eApiMask_: _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eApiMask_, _ERunnableApiFuncTag.eRFTOnRunProgressNotification)

    @staticmethod
    def IsEnabledProcFwcTENotification(eApiMask_: _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eApiMask_, _ERunnableApiFuncTag.eRFTProcFwcTENotification)

    @staticmethod
    def IsEnabledProcFwcErrorHandlerCallback(eApiMask_: _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eApiMask_, _ERunnableApiFuncTag.eRFTProcFwcErrorHandlerCallback)

    @staticmethod
    def IsEnabledPrepareCeasing(eApiMask_: _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eApiMask_, _ERunnableApiFuncTag.eRFTPrepareCeasing)

    @staticmethod
    def IsEnabledRunCeaseIteration(eApiMask_: _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eApiMask_, _ERunnableApiFuncTag.eRFTRunCeaseIteration)

    @staticmethod
    def IsEnabledApiFunction(eApiMask_: _FwIntFlag, eApiFuncTag_: _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eApiMask_, eApiFuncTag_)

    @staticmethod
    def DefaultApiMask():
        return _ERunnableApiFuncTag.eNone

    @staticmethod
    def AddApiFuncTag(eApiMask_: _FwIntFlag, eApiFuncTag_ : _FwIntFlag):
        return _EBitMask.AddEnumBitFlag(eApiMask_, eApiFuncTag_)

    @staticmethod
    def RemoveApiFuncTag(eApiMask_: _FwIntFlag, eApiFuncTag_ : _FwIntFlag):
        return _EBitMask.RemoveEnumBitFlag(eApiMask_, eApiFuncTag_)


class _ARunnableApiGuide(_AbstractSlotsObject):
    __slots__ = [
        '__rbl'
      , '__eApiMask'
      , '__eExclApiMask'
      , '__eExecApiFuncRet'

      , '__runExecutable'
      , '__setUpRunnable'
      , '__procExternalMsg'
      , '__procInternalMsg'
      , '__onTimeoutExpired'
      , '__tearDownRunnable'
      , '__procExternalQueue'
      , '__procInternalQueue'
      , '__onRunProgressNotification'

      , '__getRunLoopCycleTimeout'

      , '__prepareCeasing'
      , '__runCeaseIteration'
      , '__procFwcTENotification'
      , '__procFwcErrorHandlerCallback'
    ]

    def __init__(self, rbl_, excludedRblM_ : _ERunnableApiFuncTag):

        self.__rbl             = rbl_
        self.__eApiMask        = None
        self.__eExclApiMask    = None
        self.__eExecApiFuncRet = None

        self.__runExecutable               = None
        self.__setUpRunnable               = None
        self.__procExternalMsg             = None
        self.__procInternalMsg             = None
        self.__onTimeoutExpired            = None
        self.__tearDownRunnable            = None
        self.__procExternalQueue           = None
        self.__procInternalQueue           = None
        self.__onRunProgressNotification   = None

        self.__getRunLoopCycleTimeout      = None

        self.__prepareCeasing              = None
        self.__runCeaseIteration           = None
        self.__procFwcTENotification       = None
        self.__procFwcErrorHandlerCallback = None

        super().__init__()

        _exclApiFuncs = None
        if excludedRblM_ is not None:
            if not isinstance(excludedRblM_, _ERunnableApiFuncTag):
                vlogif._LogOEC(True, -1228)
                self.CleanUp()
                return

            _exclApiFuncs = _EBitMask.GetIntegerBitFlagsList(excludedRblM_)
            if _exclApiFuncs is None:
                vlogif._LogOEC(True, -1229)
                self.CleanUp()
                return
            if len(_exclApiFuncs) == 0:
                _exclApiFuncs = None

        self.__eApiMask     = _ERunnableApiFuncTag.DefaultApiMask()
        self.__eExclApiMask = excludedRblM_

        for name, member in _ERunnableApiFuncTag.__members__.items():
            if member == _ERunnableApiFuncTag.eNone:
                continue
            if _EBitMask.IsEnumBitFlagSet(self.__eApiMask, member):
                continue
            if _exclApiFuncs is not None:
                if member.value in _exclApiFuncs:
                    continue

            _apiFunc = getattr(rbl_, member.functionName, None)
            if _apiFunc is None:
                continue

            self.__eApiMask = _ERunnableApiFuncTag.AddApiFuncTag(self.__eApiMask, member)

            if   member == _ERunnableApiFuncTag.eRFTRunExecutable:             self.runExecutable             = _apiFunc
            elif member == _ERunnableApiFuncTag.eRFTSetUpExecutable:             self.setUpRunnable             = _apiFunc
            elif member == _ERunnableApiFuncTag.eRFTProcessExternalMsg:        self.procExternalMsg           = _apiFunc
            elif member == _ERunnableApiFuncTag.eRFTProcessInternalMsg:        self.procInternalMsg           = _apiFunc
            elif member == _ERunnableApiFuncTag.eRFTOnTimeoutExpired:          self.onTimeoutExpired          = _apiFunc
            elif member == _ERunnableApiFuncTag.eRFTTearDownExecutable:          self.tearDownRunnable          = _apiFunc
            elif member == _ERunnableApiFuncTag.eRFTProcessExternalQueue:      self.procExternalQueue         = _apiFunc
            elif member == _ERunnableApiFuncTag.eRFTProcessInternalQueue:      self.procInternalQueue         = _apiFunc
            elif member == _ERunnableApiFuncTag.eRFTOnRunProgressNotification: self.onRunProgressNotification = _apiFunc

            elif member == _ERunnableApiFuncTag.eRFTPrepareCeasing:              self.prepareCeasing              = _apiFunc
            elif member == _ERunnableApiFuncTag.eRFTRunCeaseIteration:           self.runCeaseIteration           = _apiFunc
            elif member == _ERunnableApiFuncTag.eRFTProcFwcTENotification:       self.procFwcTENotification       = _apiFunc
            elif member == _ERunnableApiFuncTag.eRFTProcFwcErrorHandlerCallback: self.procFwcErrorHandlerCallback = _apiFunc

            else:
                vlogif._LogOEC(True, -1230)
                self.__eApiMask     = None
                self.__eExclApiMask = None
                self.CleanUp()
                return

    @property
    def runExecutable(self):
        return self.__runExecutable

    @runExecutable.setter
    def runExecutable(self, val_):
        self.__runExecutable = val_

    @property
    def setUpRunnable(self):
        return self.__setUpRunnable

    @setUpRunnable.setter
    def setUpRunnable(self, val_):
        self.__setUpRunnable = val_

    @property
    def procExternalMsg(self):
        return self.__procExternalMsg

    @procExternalMsg.setter
    def procExternalMsg(self, val_):
        self.__procExternalMsg = val_

    @property
    def procInternalMsg(self):
        return self.__procInternalMsg

    @procInternalMsg.setter
    def procInternalMsg(self, val_):
        self.__procInternalMsg = val_

    @property
    def onTimeoutExpired(self):
        return self.__onTimeoutExpired

    @onTimeoutExpired.setter
    def onTimeoutExpired(self, val_):
        self.__onTimeoutExpired = val_

    @property
    def tearDownRunnable(self):
        return self.__tearDownRunnable

    @tearDownRunnable.setter
    def tearDownRunnable(self, val_):
        self.__tearDownRunnable = val_

    @property
    def procExternalQueue(self):
        return self.__procExternalQueue

    @procExternalQueue.setter
    def procExternalQueue(self, val_):
        self.__procExternalQueue = val_

    @property
    def procInternalQueue(self):
        return self.__procInternalQueue

    @procInternalQueue.setter
    def procInternalQueue(self, val_):
        self.__procInternalQueue = val_

    @property
    def onRunProgressNotification(self):
        return self.__onRunProgressNotification

    @onRunProgressNotification.setter
    def onRunProgressNotification(self, val_):
        self.__onRunProgressNotification = val_

    @property
    def getRunLoopCycleTimeout(self):
        return self.__getRunLoopCycleTimeout

    @getRunLoopCycleTimeout.setter
    def getRunLoopCycleTimeout(self, val_):
        self.__getRunLoopCycleTimeout = val_

    @property
    def prepareCeasing(self):
        return self.__prepareCeasing

    @prepareCeasing.setter
    def prepareCeasing(self, val_):
        self.__prepareCeasing= val_

    @property
    def runCeaseIteration(self):
        return self.__runCeaseIteration

    @runCeaseIteration.setter
    def runCeaseIteration(self, val_):
        self.__runCeaseIteration = val_

    @property
    def procFwcTENotification(self):
        return self.__procFwcTENotification

    @procFwcTENotification.setter
    def procFwcTENotification(self, val_):
        self.__procFwcTENotification = val_

    @property
    def procFwcErrorHandlerCallback(self):
        return self.__procFwcErrorHandlerCallback

    @procFwcErrorHandlerCallback.setter
    def procFwcErrorHandlerCallback(self, val_):
        self.__procFwcErrorHandlerCallback = val_

    @property
    def eApiMask(self) -> _ERunnableApiFuncTag:
        return self.__eApiMask

    @property
    def eExcludedApiMask(self) -> _ERunnableApiFuncTag:
        return self.__eExclApiMask

    @property
    def isProvidingRunExecutable(self):
        return False if self.__eApiMask is None else _ERunnableApiFuncTag.IsEnabledRunExecutable(self.__eApiMask)

    @property
    def isProvidingSetUpRunnable(self):
        return False if self.__eApiMask is None else _ERunnableApiFuncTag.IsEnabledSetUpExecutable(self.__eApiMask)

    @property
    def isProvidingTearDownRunnable(self):
        return False if self.__eApiMask is None else _ERunnableApiFuncTag.IsEnabledTearDownExecutable(self.__eApiMask)

    @property
    def isProvidingOnTimeoutExpired(self):
        return False if self.__eApiMask is None else _ERunnableApiFuncTag.IsEnabledOnTimeoutExpired(self.__eApiMask)

    @property
    def isProvidingProcessExternalMsg(self):
        return False if self.__eApiMask is None else _ERunnableApiFuncTag.IsEnabledProcessExternalMsg(self.__eApiMask)

    @property
    def isProvidingProcessInternalMsg(self):
        return False if self.__eApiMask is None else _ERunnableApiFuncTag.IsEnabledProcessInternalMsg(self.__eApiMask)

    @property
    def isProvidingProcessExternalQueue(self):
        return False if self.__eApiMask is None else _ERunnableApiFuncTag.IsEnabledProcessExternalQueue(self.__eApiMask)

    @property
    def isProvidingProcessInternalQueue(self):
        return False if self.__eApiMask is None else _ERunnableApiFuncTag.IsEnabledProcessInternalQueue(self.__eApiMask)

    @property
    def isProvidingOnRunProgressNotification(self):
        return False if self.__eApiMask is None else _ERunnableApiFuncTag.IsEnabledOnRunProgressNotification(self.__eApiMask)

    @property
    def isProvidingRunCeaseIteration(self):
        return False if self.__eApiMask is None else _ERunnableApiFuncTag.IsEnabledRunCeaseIteration(self.__eApiMask)

    @property
    def isProvidingPrepareCeasing(self):
        return False if self.__eApiMask is None else _ERunnableApiFuncTag.IsEnabledPrepareCeasing(self.__eApiMask)

    @property
    def isProvidingProcFwcTENotification(self):
        return False if self.__eApiMask is None else _ERunnableApiFuncTag.IsEnabledProcFwcTENotification(self.__eApiMask)

    @property
    def isProvidingProcFwcErrorHandlerCallback(self):
        return False if self.__eApiMask is None else _ERunnableApiFuncTag.IsEnabledProcFwcErrorHandlerCallback(self.__eApiMask)

    @property
    def _runnable(self):
        return self.__rbl

    @property
    def _eExecutionApiFunctionReturn(self) -> _ETernaryOpResult:
        return self.__eExecApiFuncRet

    def _IsProvidingApiFunction(self, eApiFuncTag_ : _ERunnableApiFuncTag):
        return False if self.__eApiMask is None else _ERunnableApiFuncTag.IsEnabledApiFunction(self.__eApiMask, eApiFuncTag_)

    def _ToString(self, *args_, **kwargs_):
        if self.__eApiMask is None:
            return None

        _bCompact = True
        for _ii in range(len(args_)):
            if 0 == _ii: _bCompact = args_[_ii]

        _myTxt = _ARunnableApiGuide.__ApiMask2String(self.__eApiMask)
        res = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_ApiGuide_ApiMask)
        res = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_004).format(type(self).__name__, res, _myTxt)
        if not _bCompact:
            if self.__eExclApiMask is not None:
                _myTxt = _ARunnableApiGuide.__ApiMask2String(self.__eExclApiMask, bExcluded_=True)
                res   += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_NewlineTab) + _myTxt
        return res

    def _CleanUp(self):
        self.__rbl          = None
        self.__eApiMask     = None
        self.__eExclApiMask = None

        self.runExecutable             = None
        self.setUpRunnable             = None
        self.procExternalMsg           = None
        self.procInternalMsg           = None
        self.onTimeoutExpired          = None
        self.tearDownRunnable          = None
        self.procExternalQueue         = None
        self.procInternalQueue         = None
        self.onRunProgressNotification = None

        self.getRunLoopCycleTimeout = None

        self.prepareCeasing              = None
        self.runCeaseIteration           = None
        self.procFwcTENotification       = None
        self.procFwcErrorHandlerCallback = None

    def _SetGetExecutionApiFunctionReturn(self, execRet_ : _ETernaryOpResult, bApplyConvertBefore_ =True) -> _ETernaryOpResult:
        if not bApplyConvertBefore_:
            res = execRet_
        else:
            res = _ETernaryOpResult.ConvertFrom(execRet_)
        self.__eExecApiFuncRet = res
        return res

    @staticmethod
    def __ApiMask2String(rblApiMask_ : _ERunnableApiFuncTag, bExcluded_ =False):
        res = _EFwTextID.eMisc_Shared_ApiGuide_ExcludedApiMask if bExcluded_ else _EFwTextID.eMisc_Shared_ApiGuide_ApiMask
        res = _FwTDbEngine.GetText(res)
        res = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_005).format(res, hex(rblApiMask_))

        _myTxt = _CommonDefines._STR_EMPTY
        for name, member in _ERunnableApiFuncTag.__members__.items():
            if member == _ERunnableApiFuncTag.eNone:
                continue
            if not _EBitMask.IsEnumBitFlagSet(rblApiMask_, member):
                continue
            _myTxt += _CommonDefines._CHAR_SIGN_TAB + member.functionName + _CommonDefines._CHAR_SIGN_NEWLINE

        if len(_myTxt) > 0:
            _myTxt = _myTxt.rstrip()
            res   += _CommonDefines._CHAR_SIGN_NEWLINE + _myTxt
        return res


@unique
class _ERunnableExecutionContextID(_FwIntEnum):
    eDontCare     = 400
    eRun          = 433
    eProcIntQueue = 435
    eProcExtQueue = 437

    @property
    def isDontCare(self):
        return self == _ERunnableExecutionContextID.eDontCare

    @property
    def isRun(self):
        return self == _ERunnableExecutionContextID.eRun

    @property
    def isProcessingQueue(self):
        return self.value > _ERunnableExecutionContextID.eRun.value
