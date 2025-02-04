# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : arunnable.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from xcofdk.fwapi.xtask import XTask
from xcofdk.fwapi.xmsg  import XMessage
from xcofdk.fwapi.xmsg  import XPayload

from xcofdk._xcofw.fw.fwssys.fwcore.logging                      import logif
from xcofdk._xcofw.fw.fwssys.fwcore.logging                      import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.logging.errorentry           import _ErrorEntry
from xcofdk._xcofw.fw.fwssys.fwcore.logging.fatalentry           import _FatalEntry
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logdefines           import _EErrorImpact
from xcofdk._xcofw.fw.fwssys.fwcore.logging.xcoexception         import _XcoExceptionRoot
from xcofdk._xcofw.fw.fwssys.fwcore.logging.xcoexception         import _XcoBaseException
from xcofdk._xcofw.fw.fwssys.fwcore.apiimpl.xtask.xtaskconn      import _XTaskConnector
from xcofdk._xcofw.fw.fwssys.fwcore.base.callableif              import _CallableIF
from xcofdk._xcofw.fw.fwssys.fwcore.base.gtimeout                import _Timeout
from xcofdk._xcofw.fw.fwssys.fwcore.base.sigcheck                import _CallableSignature
from xcofdk._xcofw.fw.fwssys.fwcore.base.timeutil                import _TimeAlert
from xcofdk._xcofw.fw.fwssys.fwcore.base.util                    import _Util
from xcofdk._xcofw.fw.fwssys.fwcore.types.aprofile               import _AbstractProfile
from xcofdk._xcofw.fw.fwssys.fwcore.types.aprofile               import _AbstractSlotsObject
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes            import _CommonDefines
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes            import _ETernaryOpResult

from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcproxyclient  import _LcProxyClient

from xcofdk._xcofw.fw.fwssys.fwcore.lcmon.lcmontlb import _LcDynamicTLB
from xcofdk._xcofw.fw.fwssys.fwcore.lcmon.lcmontlb import _LcCeaseTLB
from xcofdk._xcofw.fw.fwssys.fwcore.lcmon.lcmontlb import _ELcCeaseTLBState

from xcofdk._xcofw.fw.fwssys.fwcore.ipc.sync.mutex        import _Mutex
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.sync.semaphore    import _BinarySemaphore
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.atask         import _AbstractTask
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.execprofile   import _ExecutionProfile
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk               import taskmgr
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskstate     import _TaskState
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil      import _TaskUtil
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil      import _ETaskApiContextID
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil      import _ETaskExecutionPhaseID
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil      import _EProcessingFeasibilityID
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.aexecutable   import _AbstractExecutable
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.arunnabledefs import _ERunnableType
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.arunnabledefs import _ARunnableApiGuide
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.arunnabledefs import _ERunProgressID
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.arunnabledefs import _ERunnableApiFuncTag
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.arunnabledefs import _ERunnableExecutionStepID

from xcofdk._xcofw.fw.fwssys.fwerrh.fwerrorcodes import _EFwErrorCode
from xcofdk._xcofw.fw.fwssys.fwerrh.euerrhandler import _EErrorHandlerCallbackID
from xcofdk._xcofw.fw.fwssys.fwerrh.euerrhandler import _EuErrorHandler

from xcofdk._xcofw.fw.fwssys.fwmsg.msg.messageif         import _MessageIF
from xcofdk._xcofw.fw.fwssys.fwmsg.disp.dispatchFilter   import _DispatchFilter
from xcofdk._xcofw.fw.fwssys.fwmsg.disp.dispatchagentif  import _DispatchAgentIF
from xcofdk._xcofw.fw.fwssys.fwmsg.disp.dispatchregistry import _DispatchRegistry

from xcofdk._xcofwa.fwadmindefs import _FwSubsystemCoding

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine

class _AbstractRunnable(_DispatchAgentIF, _EuErrorHandler, _AbstractExecutable):

    class _RunnableExecutionPlan(_AbstractSlotsObject):

        __slots__ = [ '__dictSteps' ]

        def __init__(self, dictSteps_ : dict):
            self.__dictSteps = dictSteps_
            super().__init__()

        @property
        def isIncludingSetUpExecutable(self):
            return self._IsIncludingExecStep(_ERunnableExecutionStepID.eSetUpExecutable)

        @property
        def isIncludingTeardownExecutable(self):
            return self._IsIncludingExecStep(_ERunnableExecutionStepID.eTeardownExecutable)

        @property
        def isIncludingRunExecutable(self):
            return self._IsIncludingExecStep(_ERunnableExecutionStepID.eRunExecutable)

        @property
        def isIncludingCustomManagedExternalQueue(self):
            return self._IsIncludingExecStep(_ERunnableExecutionStepID.eCustomManagedExternalQueue)

        @property
        def isIncludingAutoManagedExternalQueue(self):
            return self._IsIncludingExecStep(_ERunnableExecutionStepID.eAutoManagedExternalQueue)

        @property
        def isIncludingAutoManagedExternalQueue_By_RunExecutable(self):
            return self._IsIncludingExecStep(_ERunnableExecutionStepID.eAutoManagedExternalQueue_By_RunExecutable)

        @property
        def isIncludingCustomManagedInternalQueue_By_RunExecutable(self):
            return self._IsIncludingExecStep(_ERunnableExecutionStepID.eCustomManagedInternalQueue_By_RunExecutable)

        @property
        def isIncludingCustomManagedInternalQueue_By_AutoManagedExternalQueue(self):
            return self._IsIncludingExecStep(_ERunnableExecutionStepID.eCustomManagedInternalQueue_By_AutoManagedExternalQueue)

        @property
        def isIncludingAutoManagedInternalQueue_By_RunExecutable(self):
            return self._IsIncludingExecStep(_ERunnableExecutionStepID.eAutoManagedInternalQueue_By_RunExecutable)

        @property
        def isIncludingAutoManagedInternalQueue_By_AutoManagedExternalQueue(self):
            return self._IsIncludingExecStep(_ERunnableExecutionStepID.eAutoManagedInternalQueue_By_AutoManagedExternalQueue)

        def _IsIncludingExecStep(self, eExecStepID_ : _ERunnableExecutionStepID) -> bool:
            res = False
            if self.__dictSteps is None:
                pass
            elif not isinstance(eExecStepID_, _ERunnableExecutionStepID):
                pass
            elif not eExecStepID_ in self.__dictSteps:
                pass
            else:
                res = self.__dictSteps[eExecStepID_]
            return res

        def _ToString(self, *args_, **kwargs_):
            if self.__dictSteps is None:
                return None

            res = _CommonDefines._STR_EMPTY
            if logif._IsReleaseModeEnabled():
                return res

            for _kk, _vv in self.__dictSteps.items():
                if _vv:
                    res += '\t{}\n'.format(_kk.compactName)
            return res

        def _CleanUp(self):
            if self.__dictSteps is not None:
                self.__dictSteps.clear()
                self.__dictSteps = None

    class _RunnableExecutorTable(_AbstractSlotsObject):

        __slots__ = [ '__dictExecutors' ]

        def __init__(self, dictExecutors_ : dict):
            self.__dictExecutors = dictExecutors_
            super().__init__()

        def _GetApiExecutor(self, eFuncID_ : _ERunnableApiFuncTag):
            res = None
            if self.__dictExecutors is None:
                pass
            elif not isinstance(eFuncID_, _ERunnableApiFuncTag):
                pass
            elif eFuncID_ not in self.__dictExecutors:
                pass
            else:
                res = self.__dictExecutors[eFuncID_]
            return res

        def _CleanUp(self):
            if self.__dictExecutors is not None:
                for _vv in self.__dictExecutors.values():
                    _vv.CleanUp()
                self.__dictExecutors.clear()
                self.__dictExecutors = None

    class _ARBackLogEntry(_AbstractSlotsObject):
        __slots__  = [ '__msg' , '__bXMsg' , '__msgUID' , '__msgDump' , '__pldDump' , '__bCPL' , '__cdesCB' , '__callback' ]

        _FwDispInst = None

        def __init__(self, bXMsg_ : bool, msgUID_ : int, msgDump_ : bytes, pldDump_ =None, bCustomPL_ =None, customDesCallback_ =None, callback_ : _CallableIF =None):
            super().__init__()
            self.__msg      = None
            self.__bCPL     = bCustomPL_
            self.__bXMsg    = bXMsg_
            self.__msgUID   = msgUID_
            self.__cdesCB   = customDesCallback_
            self.__msgDump  = msgDump_
            self.__pldDump  = pldDump_
            self.__callback = callback_

        @property
        def _message(self) -> _MessageIF:
            if _AbstractRunnable._ARBackLogEntry._FwDispInst is None:
                return None
            if self.__msgUID is None:
                return None
            if self.__msg is not None:
                return self.__msg

            self.__msg = _AbstractRunnable._ARBackLogEntry._FwDispInst._DeserializeMsg(self.__bXMsg, self.__msgUID, self.__msgDump, pldDump_=self.__pldDump, bCustomPL_=self.__bCPL, customDesCallback_=self.__cdesCB)
            return self.__msg

        @property
        def _msgUID(self):
            return self.__msgUID

        @property
        def _sortKey(self):
            return abs(self.__msgUID)

        @property
        def _callback(self):
            return self.__callback

        def _ToString(self, *args_, **kwargs_):
            pass

        def _CleanUp(self):
            if self.__msgDump is None:
                return

            _bSerDes = False
            if self.__msg is not None:
                _msgPld = self.__msg.AttachPayload(None)
                if _msgPld is not None:
                    _bSerDes = _msgPld.isMarshalingRequired
                    if _bSerDes:
                        if isinstance(_msgPld, XPayload):
                            _msgPld.DetachContainer()
                self.__msg.CleanUp()

            if self.__pldDump is not None:
                if self.__bCPL and _bSerDes:
                    del self.__pldDump
                self.__pldDump = None
            del self.__msgDump

            self.__msg      = None
            self.__bCPL     = None
            self.__bXMsg    = None
            self.__msgUID   = None
            self.__cdesCB   = None
            self.__msgDump  = None
            self.__callback = None

    @classmethod
    def GetMandatoryCustomApiMethodNamesList(cls_):
        return cls_._GetMandatoryCustomApiMethodNamesList()

    __slots__ = [ '__iqueue'      , '__xqueue'   , '__mtxData'     , '__ag'
                , '__semStop'     , '__eRblType' , '__xtaskConn'   , '__rblName'
                , '__tskPrf'      , '__runLogAlert' , '__execPlan' , '__executors'
                , '__execPrf'  , '__xtlType'     , '__cbReg'       , '__drivingTask'
                ]

    __FwDispRbl = None
    __XML_RUNNER_XCP_MSG_DuplicateWriter = _FwTDbEngine.GetText(_EFwTextID.eMisc_XML_RUNNER_XCP_MSG_DuplicateWriter)

    def __init__( self
                , eRblType_     : _ERunnableType       =None
                , xtaskConn_    : _XTaskConnector      =None
                , excludedRblM_ : _ERunnableApiFuncTag =None
                , runLogAlert_  : _TimeAlert           =None
                , execProfile_  : _ExecutionProfile    =None):
        self.__ag          = None
        self.__cbReg       = None
        self.__iqueue      = None
        self.__xqueue      = None
        self.__tskPrf      = None
        self.__mtxData     = None
        self.__rblName     = None
        self.__semStop     = None
        self.__execPrf     = None
        self.__xtlType     = None
        self.__eRblType    = None
        self.__execPlan    = None
        self.__executors   = None
        self.__xtaskConn   = None
        self.__drivingTask = None
        self.__runLogAlert = None

        if eRblType_ is None:
            eRblType_ = _ERunnableType.eUserRbl

        _AbstractExecutable.__init__(self)
        _EuErrorHandler.__init__(self)
        _DispatchAgentIF.__init__(self)

        _bErr = False
        if not isinstance(eRblType_, _ERunnableType):
            _bErr = True
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00091)
        elif (runLogAlert_ is not None) and not isinstance(runLogAlert_, _TimeAlert):
            _bErr = True
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00092)
        elif (execProfile_ is not None) and not (isinstance(execProfile_, _ExecutionProfile) and execProfile_.isValid):
            _bErr = True
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00093)
        else:
            _bMainXT = None
            _bMainRbl = None
            if isinstance(eRblType_, _ERunnableType):
                if eRblType_.isFwMainRunnable:
                    _bMainRbl = True
                elif not eRblType_.isXTaskRunnable:
                    _bMainRbl = False
                else:
                    _bMainRbl = False
                    if eRblType_.isMainXTaskRunnable:
                        _bMainXT = True
                    else:
                        _bMainXT = False
            xtlType = _AbstractExecutable._CalcExecutableTypeID(bMainXT_=_bMainXT, bMainRbl_=_bMainRbl)
            if xtlType is None:
                _bErr = True
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00094)
            else:
                self.__xtlType = xtlType
                if execProfile_ is None:
                    execProfile_ = _ExecutionProfile()
                else:
                    execProfile_ = execProfile_._Clone()

                _xtc = xtaskConn_
                if eRblType_.isXTaskRunnable or (_xtc is not None):
                    if not (eRblType_.isXTaskRunnable and isinstance(_xtc, _XTaskConnector)):
                        _bErr = True
                        vlogif._LogOEC(True, _EFwErrorCode.VFE_00095)
                    else:
                        _xt = xtaskConn_._connectedXTask
                        if not (isinstance(_xt, XTask) and _xt.isXtask):
                            _bErr = True
                            vlogif._LogOEC(True, _EFwErrorCode.VFE_00096)
                        elif not _xt.isAttachedToFW:
                            _bErr = True
                            vlogif._LogOEC(True, _EFwErrorCode.VFE_00097)

        if not _bErr:
            if not _FwSubsystemCoding.IsSubsystemMessagingConfigured():
                if excludedRblM_ is None:
                    excludedRblM_ = _ERunnableApiFuncTag.DefaultApiMask()
                excludedRblM_ = _ERunnableApiFuncTag.AddApiFuncTag(excludedRblM_, _ERunnableApiFuncTag.eRFTProcessExternalMsg)
                excludedRblM_ = _ERunnableApiFuncTag.AddApiFuncTag(excludedRblM_, _ERunnableApiFuncTag.eRFTProcessInternalMsg)
                excludedRblM_ = _ERunnableApiFuncTag.AddApiFuncTag(excludedRblM_, _ERunnableApiFuncTag.eRFTProcessExternalQueue)
                excludedRblM_ = _ERunnableApiFuncTag.AddApiFuncTag(excludedRblM_, _ERunnableApiFuncTag.eRFTProcessInternalQueue)

        if not _bErr:
            if (excludedRblM_ is not None) and not isinstance(excludedRblM_, _ERunnableApiFuncTag):
                _bErr = True
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00098)

        if not _bErr:
            self.__ag = _ARunnableApiGuide(self, excludedRblM_)
            if self.__ag.eApiMask is None:
                _bErr = True
            else:
                if eRblType_.isFwMainRunnable:
                    _bErr =         not self.__ag.isProvidingRunCeaseIteration
                    _bErr = _bErr or not self.__ag.isProvidingPrepareCeasing
                    _bErr = _bErr or not self.__ag.isProvidingProcFwcErrorHandlerCallback
                    if _bErr:
                        vlogif._LogOEC(True, _EFwErrorCode.VFE_00099)

                if not _bErr:
                    if not self.__CheckMutuallyExclusiveAPI():
                        _bErr = True
                    else:
                        self.__CreateExecPlan()
                        if self.__execPlan is None:
                            _bErr = True
                        else:
                            self.__CreateExecutorTable(eRblType_.isXTaskRunnable)
                            if self.__executors is None:
                                _bErr = True

        if _bErr:
            if self.__executors is not None:
                self.__executors.CleanUp()
                self.__executors = None
            if self.__execPlan is not None:
                self.__execPlan.CleanUp()
                self.__execPlan = None
            if self.__ag.eApiMask is not None:
                self.__ag.CleanUp()
                self.__ag = None

            _EuErrorHandler._CleanUp(self)
            self.CleanUp()
        else:
            self.__mtxData     = _Mutex()
            self.__execPrf     = execProfile_
            self.__eRblType    = eRblType_
            self.__xtaskConn   = xtaskConn_
            self.__runLogAlert = runLogAlert_

            if eRblType_.isFwDispatcherRunnable:
                _AbstractRunnable.__FwDispRbl = self
                _AbstractRunnable._ARBackLogEntry._FwDispInst = self

    def __eq__(self, other_):
        return (other_ is not None) and (id(self) == id(other_))

    def _ToString(self, *args_, **kwargs_):
        if self._isInvalid:
            return type(self).__name__

        if self.taskBadge is not None:
            res = self.taskBadge.ToString()
        elif self.__taskProfile is not None:
            res = self.__taskProfile.taskName
        else:
            res = None

        if res is None:
            res = type(self).__name__

        _bXTK = False
        _ii = res.find(_FwTDbEngine.GetText(_EFwTextID.eMisc_TaskNamePrefix_Task))
        if _ii < 0:
            _ii = res.find(_FwTDbEngine.GetText(_EFwTextID.eMisc_TaskNamePrefix_XTask))
            _bXTK = _ii == 0
        if _ii != 0:
            res = _FwTDbEngine.GetText(_EFwTextID.eMisc_TaskNamePrefix_Runnable) + res
        else:
            if not _bXTK:
                res = res.replace(_FwTDbEngine.GetText(_EFwTextID.eMisc_TaskNamePrefix_Task), _FwTDbEngine.GetText(_EFwTextID.eMisc_TaskNamePrefix_Runnable), 1)
            else:
                res = res.replace(_FwTDbEngine.GetText(_EFwTextID.eMisc_TaskNamePrefix_XTask), _FwTDbEngine.GetText(_EFwTextID.eMisc_TaskNamePrefix_XRunnable), 1)
        return res

    def _CleanUp(self):
        if self._isInvalid:
            return

        _myMtx    = self.__mtxData
        _bFlagSet = self._isInLcCeaseMode

        _EuErrorHandler._CleanUp(self)

        with _myMtx:
            if self.__cbReg is not None:
                self.__cbReg.CleanUp()
                self.__cbReg = None
            if self.__execPrf is not None:
                self.__execPrf.CleanUp()
                self.__execPrf = None
            if self.__executors is not None:
                self.__executors.CleanUp()
                self.__executors = None
            if self.__execPlan is not None:
                self.__execPlan.CleanUp()
                self.__execPlan = None
            if self.__ag is not None:
                self.__ag.CleanUp()
                self.__ag = None
            if self.__xtaskConn is not None:
                self.__xtaskConn._DisconnectXTask()
                self.__xtaskConn.CleanUp()

            self.__iqueue      = None
            self.__xqueue      = None
            self.__tskPrf      = None
            self.__mtxData     = None
            self.__rblName     = None
            self.__semStop     = None
            self.__xtlType     = None
            self.__eRblType    = None
            self.__xtaskConn   = None
            self.__drivingTask = None
            self.__runLogAlert = None

        if not _bFlagSet:
            _myMtx.CleanUp()

    @property
    def isProvidingRunExecutable(self):
        return False if self.__ag is None else self.__ag.isProvidingRunExecutable

    @property
    def isProvidingSetUpRunnable(self):
        return False if self.__ag is None else self.__ag.isProvidingSetUpRunnable

    @property
    def isProvidingTearDownRunnable(self):
        return False if self.__ag is None else self.__ag.isProvidingTearDownRunnable

    @property
    def isProvidingOnTimeoutExpired(self):
        return False if self.__ag is None else self.__ag.isProvidingOnTimeoutExpired

    @property
    def isProvidingOnRunProgressNotification(self):
        return False if self.__ag is None else self.__ag.isProvidingOnRunProgressNotification

    @property
    def isProvidingProcFwcTENotification(self):
        return False if self.__ag is None else self.__ag.isProvidingProcFwcTENotification

    @property
    def isProvidingProcFwcErrorHandlerCallback(self):
        return False if self.__ag is None else self.__ag.isProvidingProcFwcErrorHandlerCallback

    @property
    def isProvidingRunCeaseIteration(self):
        return False if self.__ag is None else self.__ag.isProvidingRunCeaseIteration

    @property
    def isProvidingPrepareCeasing(self):
        return False if self.__ag is None else self.__ag.isProvidingPrepareCeasing

    @property
    def isProvidingInternalQueue(self):
        return self.isProvidingProcessInternalQueue or  self.isProvidingProcessInternalMsg

    @property
    def isProvidingProcessInternalQueue(self):
        return False if self.__ag is None else self.__ag.isProvidingProcessInternalQueue

    @property
    def isProvidingProcessInternalMsg(self):
        return False if self.__ag is None else self.__ag.isProvidingProcessInternalMsg

    @property
    def isProvidingCustomManagedInternalQueue(self):
        return self.isProvidingProcessInternalQueue

    @property
    def isProvidingAutoManagedInternalQueue(self):
        return self.isProvidingProcessInternalMsg

    @property
    def isProvidingExternalQueue(self):
        return self.isProvidingProcessExternalQueue or self.isProvidingProcessExternalMsg

    @property
    def isProvidingProcessExternalQueue(self):
        return False if self.__ag is None else self.__ag.isProvidingProcessExternalQueue

    @property
    def isProvidingProcessExternalMsg(self):
        return False if self.__ag is None else self.__ag.isProvidingProcessExternalMsg

    @property
    def isProvidingCustomManagedExternalQueue(self):
        return self.isProvidingProcessExternalQueue

    @property
    def isProvidingAutoManagedExternalQueue(self):
        return self.isProvidingProcessExternalMsg

    @property
    def _eRunnableApiMask(self) -> _ERunnableApiFuncTag:
        return None if self.__ag is None else self.__ag.eApiMask

    @property
    def _eExcludedRunnableApiMask(self) -> _ERunnableApiFuncTag:
        return None if self.__ag is None else self.__ag.eExcludedApiMask
    @property
    def _apiGuideToString(self):
        _bNOT_COMPACT = False
        return None if self.__ag is None else self.__ag.ToString(_bNOT_COMPACT)

    @property
    def _isAttachedToFW(self) -> bool:
        return (self.__eRblType is not None) and (self.__taskProfile is not None)

    @property
    def _isStarted(self) -> bool:
        res =  self.__drivingTask is not None
        res = res and self.__drivingTask.isStarted
        return res

    @property
    def _isRunning(self) -> bool:
        res =  self.__drivingTask is not None
        res = res and self.__drivingTask.isRunning
        return res

    @property
    def _isDone(self):
        res =  self.__drivingTask is not None
        res = res and self.__drivingTask.isDone
        return res

    @property
    def _isFailed(self) -> bool:
        res =  self.__drivingTask is not None
        res = res and self.__drivingTask.isFailed
        return res

    @property
    def _isStopping(self):
        res =  self.__drivingTask is not None
        res = res and self.__drivingTask.isStopping
        return res

    @property
    def _isAborting(self):
        res =  self.__drivingTask is not None
        res = res and self.__drivingTask.isAborting
        return res

    @property
    def _isTerminated(self) -> bool:
        res =  self.__drivingTask is not None
        res = res and self.__drivingTask.isTerminated
        return res

    @property
    def _isTerminating(self) -> bool:
        res =  self.__drivingTask is not None
        res = res and self.__drivingTask.isTerminating
        return res

    @property
    def _executableName(self) -> str:
        return self._runnableName

    @property
    def _executableUniqueID(self) -> int:
        return self.__taskID

    def _Start(self):
        return self.__StartRunnable()

    def _Stop(self, cleanupDriver_ =True):
        self.__StopRunnable(cleanupDriver_=cleanupDriver_)

    def _Join(self, timeout_: _Timeout =None):
        self.__JoinRunnable(timeout_=timeout_)

    def _ProcErrorHandlerCallback( self
                                 , eCallbackID_           : _EErrorHandlerCallbackID
                                 , curFatalError_         : _FatalEntry               =None
                                 , lstForeignFatalErrors_ : list                     =None) -> _ETernaryOpResult:
        if self.isProvidingProcFwcErrorHandlerCallback:
            res = self.__ag.procFwcErrorHandlerCallback(eCallbackID_=eCallbackID_, curFatalError_=curFatalError_, lstForeignFatalErrors_=lstForeignFatalErrors_)
        else:
            res = self.__ProcErrHdlrCallback(eCallbackID_, curFatalError_=curFatalError_)
        return res

    def _PcClientName(self) -> str:
        return self._runnableName

    def _PcIsMonitoringLcModeChange(self) -> bool:
        _tskSID = None if self.__drivingTask is None else self.__drivingTask.taskStateID
        return False if _tskSID is None else (_tskSID.isRunning or _tskSID.isStopping)

    def _PcSetLcProxy(self, lcPxy_, bForceUnset_ =False):
        if not self._PcIsLcProxySet():
            _LcProxyClient._PcSetLcProxy(self, lcPxy_, bForceUnset_=bForceUnset_)
            if self._PcIsLcProxySet():
                if self.__xtaskConn is not None:
                    self.__xtaskConn._PcSetLcProxy(self, bForceUnset_=bForceUnset_)

    def _PcOnLcCeaseModeDetected(self) -> _ETernaryOpResult:
        if self._isInvalid:
            return _ETernaryOpResult.Abort()

        res = _ETernaryOpResult.Abort() if self._isAborting else _ETernaryOpResult.Stop()

        if not self._isInLcCeaseMode:
            self._CreateCeaseTLB(bEnding_=res.isAbort)
        else:
            self._UpdateCeaseTLB(res.isAbort)
        return res

    def _PcOnLcFailureDetected(self) -> _ETernaryOpResult:
        if self._isInvalid:
            return _ETernaryOpResult.Abort()

        res = _ETernaryOpResult.Abort() if self._isAborting else _ETernaryOpResult.Stop()

        if not res.isAbort:
            _bOwnLcFailureSet = False

            _ePF = self._GetProcessingFeasibility()
            if not _ePF.isFeasible:
                if not (_ePF.isInCeaseMode or _ePF.isOwnLcCompFailureSet):
                    res = _ETernaryOpResult.Abort()

                elif _ePF.isInCeaseMode:
                    pass

                else:
                    _bOwnLcFailureSet = True

            if not res.isAbort:
                if not _bOwnLcFailureSet:
                    if self._PcHasLcAnyFailureState():
                        _bOwnLcFailureSet = self._PcHasLcCompAnyFailureState(self._eRunnableType.toLcCompID, atask_=self.__drivingTask)

                if _bOwnLcFailureSet:
                    res = _ETernaryOpResult.Abort()

        if not self._isInLcCeaseMode:
            self._CreateCeaseTLB(bEnding_=res.isAbort)
        else:
            self._UpdateCeaseTLB(res.isAbort)
        return res

    def _PcOnLcPreShutdownDetected(self) -> _ETernaryOpResult:
        if self._isInvalid:
            return _ETernaryOpResult.Abort()

        res = _ETernaryOpResult.Abort() if self._isAborting else _ETernaryOpResult.Stop()

        if not res.isAbort:
            _bOwnLcFailureSet = False

            _ePF = self._GetProcessingFeasibility()
            if not _ePF.isFeasible:
                if not (_ePF.isInCeaseMode or _ePF.isOwnLcCompFailureSet):
                    res = _ETernaryOpResult.Abort()

                elif _ePF.isInCeaseMode:
                    pass

                else:
                    _bOwnLcFailureSet = True

            if not res.isAbort:
                if not _bOwnLcFailureSet:
                    if self._PcHasLcAnyFailureState():
                        _bOwnLcFailureSet = self._PcHasLcCompAnyFailureState(self._eRunnableType.toLcCompID, atask_=self.__drivingTask)

                if _bOwnLcFailureSet:
                    res = _ETernaryOpResult.Abort()

        if not self._isInLcCeaseMode:
            self._CreateCeaseTLB(bEnding_=res.isAbort)
        else:
            self._UpdateCeaseTLB(res.isAbort)
        return res

    def _PcOnLcShutdownDetected(self) -> _ETernaryOpResult:
        if self._isInvalid:
            return _ETernaryOpResult.Abort()

        res = _ETernaryOpResult.Abort() if self._isAborting else _ETernaryOpResult.Stop()

        if not self._isInLcCeaseMode:
            self._CreateCeaseTLB(bEnding_=True)
        else:
            self._UpdateCeaseTLB(self.isAborting)
        return res

    @property
    def _isOperating(self) -> bool:
        return not (self._isInvalid or self._isInLcCeaseMode or self._isTerminated or self._isTerminating)

    @property
    def _isFwAgent(self) -> bool:
        return False if self._isInvalid else self._eRunnableType.isFwRunnable

    @property
    def _isXTaskAgent(self) -> bool:
        return False if self._isInvalid else self._eRunnableType.isXTaskRunnable

    @property
    def _agentTaskID(self) -> int:
        return self.__taskID

    @property
    def _agentName(self) -> str:
        return self._runnableName

    def _PushMessage(self, msg_: _MessageIF, msgDump_: bytes, pldDump_=None, bCustomPL_=None, customDesCallback_=None, callback_: _CallableIF =None) -> _ETernaryOpResult:

        if self._isInvalid or self._isInLcCeaseMode or not (self.isRunning or (self.isStopping and self._GetTaskApiContext().isTeardown)):
            return _ETernaryOpResult.Abort()

        _bl = _AbstractRunnable._ARBackLogEntry(msg_.isXcoMsg, msg_.uniqueID, msgDump_, pldDump_=pldDump_, bCustomPL_=bCustomPL_, customDesCallback_=customDesCallback_, callback_=callback_)
        if not self.__xqueue.PushNowait(_bl):
            _bl.CleanUp()
            if self.isRunning:
                if self.__xqueue.qsize == self.__xqueue.capacity:
                    logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_AbstractRunnable_TextID_002).format(self._executableUniqueID, self.__xqueue.qsize, msg_.uniqueID))
            res = _ETernaryOpResult.NOK()
        else:
            res = _ETernaryOpResult.OK()
        return res

    @property
    def isAborting(self):
        return self._isAborting

    @property
    def euRNumber(self) -> int:
        return self._euRNumber

    @property
    def taskBadge(self):
        res = self.__drivingTask
        if res is not None:
            res = res.taskBadge
        return res

    @property
    def taskError(self):
        res = self.__drivingTask
        if res is not None:
            res = res.taskError
        return res

    def OnTimeoutExpired(self, timer_, *args_, **kwargs_) -> _ETernaryOpResult:

        if not self.isRunning:
            return _ETernaryOpResult.Stop()
        if not self.__ag.isProvidingOnTimeoutExpired:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00100)
            return _ETernaryOpResult.Abort()

        _xtor = self.__executors._GetApiExecutor(_ERunnableApiFuncTag.eRFTOnTimeoutExpired)
        _xtor.SetExecutorParams(param1_=timer_, args_=args_, kwargs_=kwargs_)
        _xres = self.__EvaluateExecResult(executor_=_xtor, bCheckBefore_=False, eAbortState_=_TaskState._EState.eTimerProcessingAborted)

        return _xres

    @property
    def _isInvalid(self):
        return self.__eRblType is None

    @property
    def _isStartable(self):
        if self.__drivingTask is None:
            res = not self.__tskPrf is None
        else:
            res  = True
            res &= self.__drivingTask.isInitialized
            res &= not self.__drivingTask.isStarted
        return res

    @property
    def _isAlive(self):
        res =  self.__drivingTask is not None
        res = res and self.__drivingTask.isAlive
        return res

    @property
    def _isInLcCeaseMode(self):
        return not self._eLcCeaseState.isNone

    @property
    def _isSelfManagingInternalQueue(self):
        return False

    @property
    def _isSelfManagingExternalQueue(self):
        return False

    @property
    def _hasExecutionApiFunctionReturnedAbort(self):
        return (self.__ag is not None) and (self.__ag._eExecutionApiFunctionReturn is not None) and self.__ag._eExecutionApiFunctionReturn.isAbort

    @property
    def _eRunnableType(self) -> _ERunnableType:
        return self.__eRblType

    @property
    def _drivingTask(self):
        return self.__drivingTask

    @property
    def _drivingTaskName(self):
        res = self.taskBadge
        if res is not None:
            res = res.taskName
        return res

    @property
    def _runnableName(self):
        if self.__eRblType is None:
            return type(self).__name__
        if self.__rblName is None:
            self.__UpdateRunnableName()
        return self.__rblName

    @property
    def _executionProfile(self) -> _ExecutionProfile:
        return self.__execPrf

    @property
    def _xtaskConnector(self) -> _XTaskConnector:
        return self.__xtaskConn

    @property
    def _xtaskInst(self) -> XTask:
        return None if self.__xtaskConn is None else self.__xtaskConn._connectedXTask

    @property
    def _iqueue(self):
        return self.__iqueue

    @property
    def _xqueue(self):
        return self.__xqueue

    @property
    def _euRNumber(self) -> int:
        return 0 if self.__drivingTask is None else self.__drivingTask.euRNumber

    @property
    def _eLcCeaseState(self) -> _ELcCeaseTLBState:
        if self.__drivingTask is None:
            res = _ELcCeaseTLBState.eNone
        else:
            res = self.__drivingTask.eLcCeaseTLBState
        return res

    @property
    def _lcDynamicTLB(self) -> _LcDynamicTLB:
        if self.__drivingTask is None:
            res = None
        else:
            res = self.__drivingTask.lcDynamicTLB
        return res

    @property
    def _lcCeaseTLB(self) -> _LcCeaseTLB:
        if self.__drivingTask is None:
            res = None
        else:
            res = self.__drivingTask.lcCeaseTLB
        return res

    @staticmethod
    def _GetMandatoryCustomApiMethodNamesList():
        return None

    def _IncEuRNumber(self):
        if self.__drivingTask is None: return
        self.__drivingTask._IncEuRNumber()

        if self.__xtaskConn is None: return
        self.__xtaskConn._IncEuRNumber()

    def _GetTaskXPhase(self) -> _ETaskExecutionPhaseID:
        if self.__drivingTask is None:
            return _ETaskExecutionPhaseID.eNone
        return self.__drivingTask.eTaskXPhase

    def _GetTaskApiContext(self) -> _ETaskApiContextID:
        if self.__drivingTask is None:
            return _ETaskApiContextID.eDontCare
        return self.__drivingTask.eTaskApiContext

    def _GetDataMutex(self):
        return self.__mtxData

    def _GetMyExecutableTypeID(self):
        return self.__xtlType

    def _SetDrivingTaskXPhase(self, eXPhaseID_ : _ETaskExecutionPhaseID):
        if self.__drivingTask is None:
            return
        self.__drivingTask._SetTaskXPhase(eXPhaseID_)

    def _SetDrivingTaskAContext(self, eACtxID_ : _ETaskApiContextID):
        if self.__drivingTask is None:
            return
        self.__drivingTask._SetTaskApiContext(eACtxID_)

    def _SetDrivingTask(self, myTask_ : _AbstractTask):
        if myTask_ is None:
            self.__drivingTask = None
            return

        if self.__drivingTask is not None:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00101)
            return
        if self.__tskPrf is None:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00102)
            return
        if id(myTask_.taskProfile) != id(self.__tskPrf):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00103)
            return
        if (myTask_.taskError is None) or myTask_.taskError.isFatalError or myTask_.taskError.isNoImpactFatalErrorDueToFrcLinkage:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00104)
            return

        self.__drivingTask = myTask_

        _EuErrorHandler._SetUpEuEH(self, self.__mtxData)
        if self._isForeignErrorListener is None:
            self.__drivingTask = None
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00105)

        else:
            self.__UpdateRunnableName()
            self.__execPrf._UpdateUniqueName(self._runnableName)

    def _SetTaskProfile(self, tskProfile_ : _AbstractProfile):
        if tskProfile_ is None:
            self.__iqueue = None
            self.__xqueue = None
            self.__tskPrf = None
            return

        if not tskProfile_.isValid:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00106)
            return
        if self.__tskPrf is not None:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00107)
            return
        if self.__drivingTask is not None:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00108)
            return

        _intQueue = None
        _extQueue = None
        if _FwSubsystemCoding.IsSubsystemMessagingConfigured():
            _intQueue  = tskProfile_.internalQueue
            _extQueue  = tskProfile_.externalQueue
            _bIntQueue = _intQueue is not None
            _bExtQueue = _extQueue is not None

            if _bIntQueue != self.isProvidingInternalQueue or _bExtQueue != self.isProvidingExternalQueue:
                _bNOT_COMPACT = False
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00109)
                return

            if not self.__eRblType.isFwDispatcherRunnable:
                if _bExtQueue:
                    self.__cbReg = _DispatchRegistry(bTaskRegistry_=False)

        self.__iqueue      = _intQueue
        self.__xqueue      = _extQueue
        self.__tskPrf = tskProfile_

        self.__UpdateRunnableName()
        self.__execPrf._UpdateUniqueName(self._runnableName)

    def _SetStopSyncSem(self, semStop_ : _BinarySemaphore):
        if self._isInvalid:
            return
        with self.__drivingTask._tstMutex:
            self.__semStop = semStop_

    def _SetTaskState(self, eNewState_ : _TaskState._EState) -> _TaskState._EState:
        res = None

        if (self.__drivingTask is None) or (self.__drivingTask.taskBadge is None):
            pass
        elif not _Util.IsInstance(eNewState_, _TaskState._EState, bThrowx_=True):
            pass
        elif eNewState_.value <= _TaskState._EState.ePendingStopRequest.value:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00110)
        else:
            if eNewState_.isTerminating:
                if not self.isTerminating:
                    if not self._eRunnableType.isFwDispatcherRunnable:
                        self.__DeregDefaultDispatchFilter()

            _bAborting = eNewState_.isAborting

            res = self.__drivingTask._CheckSetTaskState(eNewState_)
        return res

    def _CreateCeaseTLB(self, bEnding_ =False) -> _LcCeaseTLB:
        if self.__drivingTask is None:
            res = None
        else:
            res =_AbstractTask.CreateLcCeaseTLB(self.__drivingTask, self.__mtxData, bEnding_)
        return res

    def _UpdateCeaseTLB(self, bEnding_ : bool):
        _ctlb = self._lcCeaseTLB
        if _ctlb is not None:
            _ctlb.UpdateCeaseState(bEnding_)

    def _OnTENotification(self, errEntry_: _ErrorEntry) -> bool:

        if self._isInvalid:
            return False
        if self._isInLcCeaseMode:
            return False

        _ePF = self._GetProcessingFeasibility(errEntry_=errEntry_)
        if not _ePF.isFeasible:
            return False

        res = self._AddEuError(errEntry_)
        if not res:
            pass
        elif not self.taskBadge.hasFwTaskRight:
            pass
        elif self.isProvidingProcFwcTENotification:
            self.__ag.procFwcTENotification(errEntry_=errEntry_)
        return res

    def _GetProcessingFeasibility(self, errEntry_: _ErrorEntry =None) -> _EProcessingFeasibilityID:

        res = _EProcessingFeasibilityID.eFeasible

        if self._isInvalid:
            res = _EProcessingFeasibilityID.eUnfeasible
        elif self._PcIsLcProxyModeShutdown():
            res = _EProcessingFeasibilityID.eLcProxyUnavailable
        elif not self._PcIsLcCoreOperable():
            res = _EProcessingFeasibilityID.eLcCoreInoperable
        elif self._isAborting:
            res = _EProcessingFeasibilityID.eAborting
        elif self._isInLcCeaseMode:
            if not self._eRunnableType.isFwMainRunnable:
                res = _EProcessingFeasibilityID.eInCeaseMode
            elif not self._eLcCeaseState.isCeasing:
                res = _EProcessingFeasibilityID.eInCeaseMode

        _frcv = None
        if res.isFeasible:
            if self._PcHasLcAnyFailureState():
                _frcv = self._PcGetLcCompFrcView(self._eRunnableType.toLcCompID, atask_=self.__drivingTask)
                if _frcv is not None:
                    res = _EProcessingFeasibilityID.eOwnLcCompFailureSet

            if res.isFeasible:
                if (errEntry_ is not None) and errEntry_.hasNoErrorImpact:
                    res = _EProcessingFeasibilityID.eUnfeasible

        if not res.isFeasible:
            if errEntry_ is not None:
                _bOwnErr   = errEntry_.IsMyTaskError(self.__taskID)

                _teKind   = _FwTDbEngine.GetText(_EFwTextID.eMisc_TE) if _bOwnErr else _FwTDbEngine.GetText(_EFwTextID.eMisc_FTE)
                _tailPart = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Shared_TextID_003).format(_teKind, errEntry_.uniqueID, errEntry_.eErrorImpact.compactName, errEntry_.shortMessage)

                if _bOwnErr:
                    errEntry_._UpdateErrorImpact(_EErrorImpact.eNoImpactByOwnerCondition)
            else:
                _tailPart = _CommonDefines._CHAR_SIGN_DOT

        if _frcv is not None:
            _frcv.CleanUp()
        return res

    def _SendMessage(self, msg_ : _MessageIF) -> bool:
        if not _FwSubsystemCoding.IsSubsystemMessagingConfigured():
            return False
        if (msg_ is None) or not msg_.isValid:
            return False
        if self._isInvalid or self._isInLcCeaseMode or self.isAborting or not self.isStarted:
            return False

        _hdr = msg_.header

        if not (_hdr.typeID.isTIntraProcess and (_hdr.channelID.isChInterTask or _hdr.channelID.isChIntraTask)):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00111)
            return False

        if _hdr.isInternalMsg:
            if not self.isRunning:
                return False
            if not _FwSubsystemCoding.IsInternalQueueSupportEnabled():
                return False
            if not self.isProvidingInternalQueue:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00112)
                return False
            if self.__iqueue.isFull:
                logif._LogErrorEC(_EFwErrorCode.UE_00067, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_AbstractRunnable_TextID_001).format(self._executableUniqueID, self.__iqueue.qsize))
                return False
            return self.__iqueue.PushNowait(msg_)

        _actx = self._GetTaskApiContext()
        if not (self.isRunning or (self.isStopping and _actx.isTeardown)):
            return False

        if not self.isProvidingExternalQueue:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00113)
            return False

        return _AbstractRunnable.__FwDispRbl._DispatchMessage(msg_)

    def _TriggerQueueProc(self, bExtQueue_ : bool) -> int:

        if not _FwSubsystemCoding.IsSubsystemMessagingConfigured():
            return -1
        if self._isInvalid or self._isInLcCeaseMode:
            return -1
        if not bExtQueue_:
            if not self.isProvidingInternalQueue:
                return -1
        if not self.isProvidingExternalQueue:
            return -1

        _actx = self._GetTaskApiContext()

        if not self.isRunning:
            _bIgnore = self.isStopping and _actx.isTeardown
            if _bIgnore:
                _midPart = _FwTDbEngine.GetText(_EFwTextID.eMisc_QueueType_External) if bExtQueue_ else _FwTDbEngine.GetText(_EFwTextID.eMisc_QueueType_Internal)
                logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_AbstractRunnable_TextID_006).format(self._executableUniqueID, _midPart))
            return 0 if _bIgnore else -1

        if _actx.isDontCare:
            _midPart = _FwTDbEngine.GetText(_EFwTextID.eMisc_QueueType_External) if bExtQueue_ else _FwTDbEngine.GetText(_EFwTextID.eMisc_QueueType_Internal)
            logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_AbstractRunnable_TextID_003).format(self._executableUniqueID, _midPart))
            return 0
        if _actx.isProcessingQueue:
            _midPart = _FwTDbEngine.GetText(_EFwTextID.eMisc_QueueType_External) if bExtQueue_ else _FwTDbEngine.GetText(_EFwTextID.eMisc_QueueType_Internal)
            logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_AbstractRunnable_TextID_004).format(self._executableUniqueID, _midPart))
            return 0

        if not bExtQueue_:
            _iqSize = self.__iqueue.qsize
            self.__ExecuteAutoManagedIntQueue()
            return max(0, _iqSize - self.__iqueue.qsize)

        self._SetDrivingTaskAContext(_ETaskApiContextID.eProcExtQueue if bExtQueue_ else _ETaskApiContextID.eProcIntQueue)

        _blNum = self.__xqueue.qsize
        if _blNum < 1:
            self._SetDrivingTaskAContext(_actx)
            return 0

        _ii, _lstBL = _blNum, []
        while _ii > 0:
            _bl = self.__xqueue.PopNowait()
            if _bl is None:
                break
            _lstBL.append(_bl)
            _ii -= 1

        _blNum = len(_lstBL)
        if _blNum < 1:
            self._SetDrivingTaskAContext(_actx)
            return 0

        _lstBL = sorted(_lstBL, key=lambda _bl: _bl._sortKey)

        res   = 0
        _xres = _ETernaryOpResult.Continue()
        _xtor = self.__executors._GetApiExecutor(_ERunnableApiFuncTag.eRFTProcessExternalMsg)

        _eXPh = self._GetTaskXPhase()

        for _bl in _lstBL:
            _xres = _ETernaryOpResult.MapExecutionState2TernaryOpResult(self)

            if not _xres.isContinue:
                break

            _msg = _bl._message
            if _msg is None:
                continue

            _msg2 = _msg
            if _msg.isXcoMsg:
                _msg2 = XMessage(_msg)

            _xtor.SetExecutorParams(param1_=_msg2, param2_=_bl._callback)
            _xres = self.__EvaluateExecResult(executor_=_xtor, bCheckBefore_=False)

            res += 1

            if _msg.isXcoMsg:
                _msg2._Detach()

        for _bl in _lstBL:
            _bl.CleanUp()

        self._SetDrivingTaskAContext(_actx)

        self._SetDrivingTaskXPhase(_eXPh)

        return res

    def _Run(self, semStart_, *args_, **kwargs_):
        _caughtXcp = False

        try:
            self._SetDrivingTaskXPhase(_ETaskExecutionPhaseID.eFwHandling)

            self.__ExecutePreRun(semStart_)
            if self.isRunning:
                self.__NotifyRunProgress(_ERunProgressID.eReadyToRun)
                if self.isRunning:
                    self._SetDrivingTaskAContext(_ETaskApiContextID.eSetup)
                    self.__ExecuteSetup(*args_, **kwargs_)
                    self._SetDrivingTaskAContext(_ETaskApiContextID.eDontCare)
                    if self.isRunning:
                        self.__NotifyRunProgress(_ERunProgressID.eExecuteSetupDone)

                        if self.isRunning:
                            self._SetDrivingTaskAContext(_ETaskApiContextID.eRun)
                            self.__ExecuteRun()
                            self._SetDrivingTaskAContext(_ETaskApiContextID.eDontCare)

                            if not self._isAborting:
                                if self.isRunning:
                                    self.__NotifyRunProgress(_ERunProgressID.eExecuteRunDone)

                                if not self._isInLcCeaseMode:
                                    if not self._lcDynamicTLB.isLcShutdownEnabled:
                                        if self.__execPlan.isIncludingTeardownExecutable:
                                            self._SetDrivingTaskAContext(_ETaskApiContextID.eTeardown)
                                            self.__ExecuteTeardown()
                                            self._SetDrivingTaskAContext(_ETaskApiContextID.eDontCare)
                                            self.__NotifyRunProgress(_ERunProgressID.eExecuteTeardownDone)

                if not self._isAborting:
                    self.__NotifyRunProgress(_ERunProgressID.eRunDone)

        except _XcoExceptionRoot as xcp:
            _caughtXcp = True
            self.__HandleException(xcp, bCaughtByApiExecutor_=False)

        except BaseException as xcp:
            _caughtXcp = True
            xcp = _XcoBaseException(xcp, tb_=logif._GetFormattedTraceback())
            self.__HandleException(xcp, bCaughtByApiExecutor_=False)

        finally:
            if self._isInvalid:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00114)
                return

            if not self._isTerminating:
                if _caughtXcp:
                    st = _TaskState._EState.eProcessingAborted
                else:
                    st = _TaskState._EState.eProcessingStopped

                self._SetTaskState(st)

            _semStop = None
            with self.__drivingTask._tstMutex:
                if self.__semStop is not None:
                    _semStop = self.__semStop
                    self.__semStop = None

            if _semStop is not None:
                _semStop.Give()

            if self._isTerminated:
                if self._eRunnableType.isXTaskRunnable:
                    if self.__execPlan.isIncludingTeardownExecutable:
                        self._PcGetTaskMgr()._DetachTask(self.__drivingTask)

            self.__PreProcessCeaseMode()

            self.__ProcessCeaseMode()

    def _ExecuteTeardown(self) -> _ETernaryOpResult:
        return self.__ExecuteTeardown()

    def _CheckNotifyLcFailure(self):
        if self._isInvalid:
            return

        _eMyLcCompID = self._eRunnableType.toLcCompID

        if self._PcHasLcCompAnyFailureState(_eMyLcCompID, self.__drivingTask):
            return False

        res    = False
        _frc   = None
        _myMtx = None

        _curEE = self.taskError
        if _curEE is not None:
            _curEE = _curEE._currentErrorEntry

        if _curEE is None:
            pass 
        elif _curEE.isFatalError:
            _frc = _curEE
            _myMtx = None if _frc is None else _frc._LockInstance()
            if _frc is not None:
                if _frc.isInvalid or not _frc.isPendingResolution:
                    if _myMtx is not None:
                        _myMtx.Give()
                    _frc, _myMtx = None, None

        if _frc is None:
            if self.isAborting:
                _bFlagSet = self._hasExecutionApiFunctionReturnedAbort
                if _bFlagSet:
                    _txtID = _EFwTextID.eLogMsg_Shared_TextID_002
                    _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Shared_TextID_002).format(self.__logPrefixCtr)
                else:
                    _midPart = _FwTDbEngine.GetText(_EFwTextID.eMisc_XTask) if self.isXTaskRunnable else _FwTDbEngine.GetText(_EFwTextID.eMisc_Runnable)
                    _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Shared_TextID_001).format(self.__logPrefixCtr, _midPart)

                _bFwRbl  = self._eRunnableType.isFwRunnable
                _errCode = _EFwErrorCode.FE_00022 if _bFwRbl else _EFwErrorCode.FE_00923
                _frc     = logif._CreateLogFatalEC(_bFwRbl, _errCode, _errMsg, bDueToExecApiAboort_=_bFlagSet)
                _myMtx   = None if _frc is None else _frc._LockInstance()

        if _frc is not None:
            _frcClone = _frc.Clone()
            if _frcClone is None:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00115)
            else:
                res = True

                self._PcNotifyLcFailure(_eMyLcCompID, _frcClone, atask_=self.__drivingTask)

                _frc._UpdateErrorImpact(_EErrorImpact.eNoImpactByFrcLinkage)

            if _myMtx is not None:
                _myMtx.Give()
        return res

    @property
    def __isErrorFree(self):
        res = True
        if self.taskError is not None:
            res = self.taskError.isErrorFree
        return res

    @property
    def __taskID(self):
        res = self.taskBadge
        if res is not None:
            res = res.taskID
        return res

    @property
    def __taskProfile(self):
        if self.__tskPrf is not None:
            res = self.__tskPrf
        else:
            res = self.__drivingTask
            if res is not None:
                res = res.taskProfile
        return res

    @property
    def __logPrefix(self):
        res  = _FwTDbEngine.GetText(_EFwTextID.eMisc_LogPrefix_Runnable)
        res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_010).format(self._runnableName)
        return res

    @property
    def __logPrefixCtr(self):
        res  = _FwTDbEngine.GetText(_EFwTextID.eMisc_LogPrefix_Runnable)
        res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_010).format(self._runnableName)
        res += _FwTDbEngine.GetText(_EFwTextID.eMisc_LogPrefix_ExecCounter).format(self._euRNumber)
        return res

    def __UpdateRunnableName(self) -> str:
        res  = self._drivingTaskName

        if res is None:
            _tskPrf = self.__taskProfile
            if _tskPrf is not None:
                res = _tskPrf.taskName
        if res is None:
            res = type(self).__name__
        else:
            _bXTK = False
            _ii = res.find(_FwTDbEngine.GetText(_EFwTextID.eMisc_TaskNamePrefix_Task))
            if _ii < 0:
                _ii = res.find(_FwTDbEngine.GetText(_EFwTextID.eMisc_TaskNamePrefix_XTask))
                _bXTK = _ii==0
            if _ii != 0:
                res = _FwTDbEngine.GetText(_EFwTextID.eMisc_TaskNamePrefix_Runnable) + res
            else:
                if not _bXTK:
                    res = res.replace(_FwTDbEngine.GetText(_EFwTextID.eMisc_TaskNamePrefix_Task),
                        _FwTDbEngine.GetText(_EFwTextID.eMisc_TaskNamePrefix_Runnable), 1)
                else:
                    res = res.replace(_FwTDbEngine.GetText(_EFwTextID.eMisc_TaskNamePrefix_XTask),
                        _FwTDbEngine.GetText(_EFwTextID.eMisc_TaskNamePrefix_XRunnable), 1)

        self.__rblName = res
        return self.__rblName

    def __RegDefaultDispatchFilter(self) -> bool:

        if not _FwSubsystemCoding.IsSubsystemMessagingConfigured():
            return False
        if self._eRunnableType.isFwDispatcherRunnable:
            return False
        if not self.isProvidingExternalQueue:
            return False

        _fwDisp = _AbstractRunnable.__FwDispRbl
        if (_fwDisp is None) or not _fwDisp.isRunning:
            return False

        _dispFilter = _DispatchFilter._CreateDefaultDispatchFilter(receiverID_=self._executableUniqueID)
        if _dispFilter is None:
            return False

        res = self.__ForwardDispatchFilterRequest(_dispFilter, callback_=None, bAdd_=True)
        if not res:
            logif._LogFatalEC(_EFwErrorCode.FE_00037, '{} Failed to register default dispatch filter.'.format(self.__logPrefix))
        return res

    def __DeregDefaultDispatchFilter(self) -> bool:

        if not _FwSubsystemCoding.IsSubsystemMessagingConfigured():
            return False
        if self._eRunnableType.isFwDispatcherRunnable:
            return False
        if not self.isProvidingExternalQueue:
            return False

        _fwDisp = _AbstractRunnable.__FwDispRbl
        if (_fwDisp is None) or not _fwDisp.isRunning:
            return False

        _dispFilter = _DispatchFilter._CreateDefaultDispatchFilter(receiverID_=self._executableUniqueID)
        if _dispFilter is None:
            return False

        res = self.__ForwardDispatchFilterRequest(_dispFilter, callback_=None, bAdd_=False)
        return res

    def __ForwardDispatchFilterRequest(self, dispFilter_  : _DispatchFilter, callback_ : _CallableIF =None, bAdd_ =True) -> bool:
        if not _FwSubsystemCoding.IsSubsystemMessagingConfigured():
            return False
        if self._isInvalid or self._isInLcCeaseMode:
            return False
        if self.__eRblType.isFwDispatcherRunnable:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00116)
            return False
        if not (isinstance(dispFilter_, _DispatchFilter) and dispFilter_.isValid):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00117)
            return False

        if dispFilter_.isCustomMessageFilter:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00118)
            return False

        if dispFilter_.isInternalMessageFilter:
            if not self.isProvidingInternalQueue:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00119)
                return False
            if callback_ is not None:
                if not _CallableSignature.IsSignatureMatchingProcessInternalMessageCallback(callback_):
                    return False

        else:
            if not self.isProvidingExternalQueue:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00120)
                return False
            if callback_ is not None:
                if not _CallableSignature.IsSignatureMatchingProcessExternalMessageCallback(callback_):
                    return False

        if dispFilter_.isInternalMessageFilter:
            if bAdd_:
                res = self.__cbReg._InsertDispatchFilter(dispFilter_, self, callback_=callback_)
            else:
                res = self.__cbReg._EraseDispatchFilter(dispFilter_, self, callback_=callback_)
                dispFilter_.CleanUp()
        else:
            if bAdd_:
                res = _AbstractRunnable.__FwDispRbl._RegisterAgentDispatchFilter(dispFilter_, self, callback_=callback_)
            else:
                res = _AbstractRunnable.__FwDispRbl._DeregisterAgentDispatchFilter(dispFilter_, self, callback_=callback_)
                dispFilter_.CleanUp()
        return res

    def __StartRunnable(self):
        if not self._isStartable:
            vlogif._LogOEC(False, _EFwErrorCode.VUE_00007)
            return None
        elif (self.__drivingTask is None) and (self.__tskPrf is None):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00121)
            return None

        if self.__drivingTask is not None:
            res = taskmgr._TaskMgr().StartTask(self.__drivingTask.taskID)
        else:
            res = taskmgr._TaskMgr().CreateTask(taskPrf_=self.__tskPrf, bStart_=True)
        return res is not None

    def __StopRunnable(self, cleanupDriver_ =True):
        if self.__drivingTask is None:
            pass 
        else:
            taskmgr._TaskMgr().StopTask(self.__taskID, removeTask_=cleanupDriver_)

    def __JoinRunnable(self, timeout_ : _Timeout =None):
        if self.__drivingTask is None:
            pass
        elif self.__drivingTask.isEnclosingStartupThread:
            vlogif._LogOEC(False, _EFwErrorCode.VUE_00008)
        else:
            taskmgr._TaskMgr().JoinTask(self.__taskID, timeout_=timeout_)

    def __NotifyRunProgress(self, eRunProgressID_ : _ERunProgressID) -> _ETernaryOpResult:
        if self._isInLcCeaseMode:
            _xres = _ETernaryOpResult.Abort() if self.isAborting else _ETernaryOpResult.Stop()
        elif not self.isProvidingOnRunProgressNotification:
            _xres = _ETernaryOpResult.OK()
        else:
            _bWasRunning = self.isRunning
            _xtor = self.__executors._GetApiExecutor(_ERunnableApiFuncTag.eRFTOnRunProgressNotification)
            _xtor.SetExecutorParams(param1_=eRunProgressID_)

            _bSkipErrorProc = eRunProgressID_.value > _ERunProgressID.eExecuteRunDone
            _xres           = self.__EvaluateExecResult(executor_=_xtor, bCheckBefore_=None, eAbortState_=_TaskState._EState.eRunProgressAborted, bSkipErrorProc_=_bSkipErrorProc)

        return _xres

    def __ExecutePreRun(self, semStart_ : _BinarySemaphore) -> _ETernaryOpResult:

        _bCheckOK = True
        _drvTask = self.__drivingTask
        _bEnclPyThread = False if _drvTask is None else _drvTask.isEnclosingPyThread

        if _drvTask is None:
            _bCheckOK = False
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00122)

        elif id(_drvTask.linkedExecutable) != id(self):
            _bCheckOK = False
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00123)

        elif (self.taskError is None) or self.taskError.isFatalError or self.taskError.isNoImpactFatalErrorDueToFrcLinkage:
            _bCheckOK = False
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00124)

        elif _bEnclPyThread and (semStart_ is not None):
            _bCheckOK = False
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00125)

        elif not (_bEnclPyThread or isinstance(semStart_, _BinarySemaphore)):
            _bCheckOK = False
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00126)

        if not _bCheckOK:
            pass 
        else:
            if not _FwSubsystemCoding.IsSubsystemMessagingConfigured():
                pass
            elif _AbstractRunnable.__FwDispRbl is None:
                pass
            elif self._eRunnableType.isFwRunnable:
                pass
            elif not self.isProvidingExternalQueue:
                pass
            else:
                if not self._eRunnableType.isFwDispatcherRunnable:
                    _bCheckOK = self.__RegDefaultDispatchFilter()

        if not _bCheckOK:
            pass 
        else:
            if not self.__isErrorFree:
                self.taskError.ClearError()

        _xres = self.__EvaluateExecResult(execRes_=_bCheckOK, bCheckBefore_=True, eAbortState_=_TaskState._EState.ePreRunAborted)

        if semStart_ is not None:
            semStart_.Give()

        return _xres

    def __ExecuteSetup(self, *args_, **kwargs_):
        _xres = _ETernaryOpResult.Continue()

        if self.__execPlan.isIncludingSetUpExecutable:
            _xtor = self.__executors._GetApiExecutor(_ERunnableApiFuncTag.eRFTSetUpExecutable)
            _xtor.SetExecutorParams(args_=args_, kwargs_=kwargs_)
            _xres = self.__EvaluateExecResult(executor_=_xtor, bCheckBefore_=False, eAbortState_=_TaskState._EState.eSetupAborted)

        return _xres

    def __ExecuteTeardown(self):
        _xres = _ETernaryOpResult.Continue()

        if self.__execPlan.isIncludingTeardownExecutable:
            _xtor = self.__executors._GetApiExecutor(_ERunnableApiFuncTag.eRFTTearDownExecutable)
            _xres = self.__EvaluateExecResult(executor_=_xtor, bCheckBefore_=False, eAbortState_=_TaskState._EState.eTeardownAborted)
        return _xres

    def __ExecuteRun(self) -> _ETernaryOpResult:

        if self.__execPlan.isIncludingCustomManagedExternalQueue:
            return self.__ExecuteCustomManagedExtQueue()

        if self.__execPlan.isIncludingAutoManagedExternalQueue:
            return self.__ExecuteAutoManagedExtQueue(bCombinedManaged_=False)

        _bIncludingRunExecutable                               = self.__execPlan.isIncludingRunExecutable
        _bIncludingCustomManagedInternalQueue_By_RunExecutable = self.__execPlan.isIncludingCustomManagedInternalQueue_By_RunExecutable
        _bIncludingAutoManagedExternalQueue_By_RunExecutable   = self.__execPlan.isIncludingAutoManagedExternalQueue_By_RunExecutable
        _bIncludingAutoManagedInternalQueue_By_RunExecutable   = self.__execPlan.isIncludingAutoManagedInternalQueue_By_RunExecutable

        _xres       = _ETernaryOpResult.Continue()
        _runCycleMS = self.__execPrf.runPhaseFreqMS

        while True:
            if not _xres.isContinue:
                break

            try:
                if self._isInvalid is None:
                    return _ETernaryOpResult.Abort()

                self._IncEuRNumber()

                while True:
                    _ret = None if self._isAborting else self.isRunning
                    _xres = self.__EvaluateExecResult(execRes_=_ret, bCheckBefore_=None, bSkipErrorProc_=True)
                    if not _xres.isContinue:
                        break

                    if self.__cbReg is not None:
                        self.__cbReg._DropInvalidTargets()

                    if _bIncludingCustomManagedInternalQueue_By_RunExecutable:
                        _xres = self.__ExecuteCustomManagedIntQueue()

                        if not _xres.isContinue:
                            break

                    if _bIncludingAutoManagedInternalQueue_By_RunExecutable:
                        _xres = self.__ExecuteAutoManagedIntQueue()

                        if not _xres.isContinue:
                            break

                    if _bIncludingAutoManagedExternalQueue_By_RunExecutable:
                        _xres = self.__ExecuteAutoManagedExtQueue(bCombinedManaged_=True)

                        if not _xres.isContinue:
                            break

                    if not _bIncludingRunExecutable:
                        break

                    _xtor = self.__executors._GetApiExecutor(_ERunnableApiFuncTag.eRFTRunExecutable)
                    _xres = self.__EvaluateExecResult(executor_=_xtor, bCheckBefore_=True)
                    if not _xres.isContinue:
                        break

                    elif not self.isRunning:
                        _xres = self.__EvaluateExecResult(execRes_=None if self._isAborting else False, bCheckBefore_=None)

                    break

            except _XcoExceptionRoot as xcp:
                _xres = self.__HandleException(xcp, bCaughtByApiExecutor_=False)

            except BaseException as xcp:
                xcp   = _XcoBaseException(xcp, tb_=logif._GetFormattedTraceback())
                _xres = self.__HandleException(xcp, bCaughtByApiExecutor_=False)

            finally:
                if not _xres.isContinue:
                    break

                elif _runCycleMS == 0:
                    _xres = _ETernaryOpResult.Stop()
                    if self.isRunning:
                        self._SetTaskState(_TaskState._EState.eProcessingStopped)
                    break

                _TaskUtil.SleepMS(_runCycleMS)

            continue

        return _xres

    def __ExecuteCustomManagedExtQueue(self):
        _xres = _ETernaryOpResult.Abort()

        _actx = self._GetTaskApiContext()
        self._SetDrivingTaskAContext(_ETaskApiContextID.eProcExtQueue)

        _xtor = self.__executors._GetApiExecutor(_ERunnableApiFuncTag.eRFTProcessExternalQueue)
        self._SetDrivingTaskXPhase(_ETaskExecutionPhaseID.eRblProcExtQueue)
        _xres = self.__EvaluateExecResult(executor_=_xtor, bCheckBefore_=False)
        self._SetDrivingTaskXPhase(_ETaskExecutionPhaseID.eFwHandling)

        self._SetDrivingTaskAContext(_actx)

        return _xres

    def __ExecuteAutoManagedExtQueue(self, bCombinedManaged_ : bool =False) -> _ETernaryOpResult:

        if (not bCombinedManaged_) and self.__xqueue.isBlockingOnQueueSize:
            while True:
                _xres = self.__ExecuteAutoManagedExtQueueBlocking()
                if not _xres.isContinue:
                    break
            return _xres

        _actx = self._GetTaskApiContext()
        self._SetDrivingTaskAContext(_ETaskApiContextID.eProcExtQueue)

        _blNum = self.__xqueue.qsize
        if _blNum < 1:
            self._SetDrivingTaskAContext(_actx)
            return _ETernaryOpResult.Continue()

        _ii, _lstBL = _blNum, []
        while _ii > 0:
            _bl = self.__xqueue.PopNowait()
            if _bl is None:
                break
            _lstBL.append(_bl)
            _ii -= 1

        _blNum = len(_lstBL)
        if _blNum < 1:
            self._SetDrivingTaskAContext(_actx)
            return _ETernaryOpResult.Continue()

        _lstBL = sorted(_lstBL, key=lambda _bl: _bl._sortKey)

        _bIncludingAutoManagedInternalQueue_By_AutoManagedExternalQueue   = self.__execPlan.isIncludingAutoManagedInternalQueue_By_AutoManagedExternalQueue
        _bIncludingCustomManagedInternalQueue_By_AutoManagedExternalQueue = self.__execPlan.isIncludingCustomManagedInternalQueue_By_AutoManagedExternalQueue

        _xres = _ETernaryOpResult.Continue()
        _xtor = self.__executors._GetApiExecutor(_ERunnableApiFuncTag.eRFTProcessExternalMsg)

        for _bl in _lstBL:
            if not bCombinedManaged_:
                self._IncEuRNumber()

            if _bIncludingCustomManagedInternalQueue_By_AutoManagedExternalQueue:
                _xres = self.__ExecuteCustomManagedIntQueue()

            elif _bIncludingAutoManagedInternalQueue_By_AutoManagedExternalQueue:
                _xres = self.__ExecuteAutoManagedIntQueue()

            else:
                _xres = _ETernaryOpResult.MapExecutionState2TernaryOpResult(self)

            if not _xres.isContinue:
                break

            _msg = _bl._message
            if _msg is None:
                continue

            _msg2 = _msg
            if _msg.isXcoMsg:
                _msg2 = XMessage(_msg)

            _xtor.SetExecutorParams(param1_=_msg2, param2_=_bl._callback)
            _xres = self.__EvaluateExecResult(executor_=_xtor, bCheckBefore_=False)

            if _msg.isXcoMsg:
                _msg2._Detach()

        for _bl in _lstBL:
            _bl.CleanUp()

        self._SetDrivingTaskAContext(_actx)
        return _xres

    def __ExecuteAutoManagedExtQueueBlocking(self) -> _ETernaryOpResult:

        _actx = self._GetTaskApiContext()
        self._SetDrivingTaskAContext(_ETaskApiContextID.eProcExtQueue)

        _runCycleMS = self.__execPrf.runPhaseFreqMS

        _bl = None
        while True:
            _xres = _ETernaryOpResult.MapExecutionState2TernaryOpResult(self)
            if not _xres.isContinue:
                self._SetDrivingTaskAContext(_actx)
                return _xres

            if _bl is not None:
                break
            _bl = self.__xqueue.PopBlockingQueue(sleepTimeMS_=_runCycleMS)

        _lstBL = [_bl]
        _blNum = self.__xqueue.qsize
        _ii    = _blNum
        while _ii > 0:
            _bl = self.__xqueue.PopNowait()
            if _bl is None:
                break
            _lstBL.append(_bl)
            _ii -= 1

        _lstBL = sorted(_lstBL, key=lambda _bl: _bl._sortKey)

        _bIncludingAutoManagedInternalQueue_By_AutoManagedExternalQueue   = self.__execPlan.isIncludingAutoManagedInternalQueue_By_AutoManagedExternalQueue
        _bIncludingCustomManagedInternalQueue_By_AutoManagedExternalQueue = self.__execPlan.isIncludingCustomManagedInternalQueue_By_AutoManagedExternalQueue

        _xres = _ETernaryOpResult.Continue()
        _xtor = self.__executors._GetApiExecutor(_ERunnableApiFuncTag.eRFTProcessExternalMsg)

        for _bl in _lstBL:
            self._IncEuRNumber()

            if _bIncludingCustomManagedInternalQueue_By_AutoManagedExternalQueue:
                _xres = self.__ExecuteCustomManagedIntQueue()

            elif _bIncludingAutoManagedInternalQueue_By_AutoManagedExternalQueue:
                _xres = self.__ExecuteAutoManagedIntQueue()

            else:
                _xres = _ETernaryOpResult.MapExecutionState2TernaryOpResult(self)

            if not _xres.isContinue:
                break

            _msg = _bl._message

            if _msg is None:
                continue

            _msg2 = _msg
            if _msg.isXcoMsg:
                _msg2 = XMessage(_msg)

            _xtor.SetExecutorParams(param1_=_msg2, param2_=_bl._callback)
            _xres = self.__EvaluateExecResult(executor_=_xtor, bCheckBefore_=False)

            if _msg.isXcoMsg:
                _msg2._Detach()

        for _bl in _lstBL:
            _bl.CleanUp()

        self._SetDrivingTaskAContext(_actx)

        return _xres

    def __ExecuteCustomManagedIntQueue(self) -> _ETernaryOpResult:
        _actx = self._GetTaskApiContext()
        self._SetDrivingTaskAContext(_ETaskApiContextID.eProcIntQueue)

        _xtor = self.__executors._GetApiExecutor(_ERunnableApiFuncTag.eRFTProcessInternalQueue)
        _xres = self.__EvaluateExecResult(executor_=_xtor, bCheckBefore_=False)

        self._SetDrivingTaskAContext(_actx)

        return _xres

    def __ExecuteAutoManagedIntQueue(self) -> _ETernaryOpResult:
        _actx = self._GetTaskApiContext()
        self._SetDrivingTaskAContext(_ETaskApiContextID.eProcIntQueue)

        _lstBL = []
        _blNum = self.__iqueue.qsize
        _ii    = _blNum
        while _ii > 0:
            _bl = self.__iqueue.PopNowait()
            if _bl is None:
                break
            _lstBL.append(_bl)
            _ii -= 1

        _blNum = len(_lstBL)
        if _blNum < 1:
            self._SetDrivingTaskAContext(_actx)
            return _ETernaryOpResult.Continue()

        _xres = _ETernaryOpResult.MapExecutionState2TernaryOpResult(self)
        _xtor = self.__executors._GetApiExecutor(_ERunnableApiFuncTag.eRFTProcessInternalMsg)

        for _bl in _lstBL:
            if not _xres.isContinue:
                break

            _msg = _bl._message
            _msg2 = _msg
            if _msg.isXcoMsg:
                _msg2 = XMessage(_msg)

            _xtor.SetExecutorParams(param1_=_msg2, param2_=_bl._callback)
            _xres = self.__EvaluateExecResult(executor_=_xtor, bCheckBefore_=False)

            if _msg.isXcoMsg:
                _msg2._Detach()
            _msg.CleanUp()

        self._SetDrivingTaskAContext(_actx)
        return _xres

    def __EvaluateExecResult( self
                            , executor_                                   =None
                            , execRes_        : [bool, _ETernaryOpResult] =None
                            , bCheckBefore_   : bool                      =None
                            , eAbortState_    : _TaskState._EState        =None
                            , bSkipErrorProc_ : bool                      =False) -> _ETernaryOpResult:
        _bDoCheckAfter  = False
        _bDoCheckBefore = False

        if bCheckBefore_ is not None:
            _bDoCheckBefore = bCheckBefore_
            _bDoCheckAfter  = not _bDoCheckBefore

        res = _ETernaryOpResult.Continue()

        if _bDoCheckBefore and self._PcIsMonitoringLcModeChange():
            _eNewOpModeID = self._PcCheckLcOperationModeChange()
            if (_eNewOpModeID is not None) and not _eNewOpModeID.isLcNormal:
                if _eNewOpModeID.isLcCeaseMode:
                    res = self._PcOnLcCeaseModeDetected()
                elif _eNewOpModeID.isLcFailureHandling:
                    res = self._PcOnLcFailureDetected()
                elif _eNewOpModeID.isLcPreShutdown:
                    res = self._PcOnLcPreShutdownDetected()
                elif _eNewOpModeID.isLcShutdown:
                    res = self._PcOnLcShutdownDetected()

        if not res.isContinue:
            pass
        else:
            if executor_ is None:
                res = _ETernaryOpResult.ConvertFrom(execRes_)
            else:
                res = executor_.Execute()

            if res.isContinue and _bDoCheckAfter and self._PcIsMonitoringLcModeChange():
                _eNewOpModeID = self._PcCheckLcOperationModeChange()
                if (_eNewOpModeID is not None) and not _eNewOpModeID.isLcNormal:
                    if _eNewOpModeID.isLcCeaseMode:
                        res = self._PcOnLcCeaseModeDetected()
                    elif _eNewOpModeID.isLcFailureHandling:
                        res = self._PcOnLcFailureDetected()
                    elif _eNewOpModeID.isLcPreShutdown:
                        res = self._PcOnLcPreShutdownDetected()
                    elif _eNewOpModeID.isLcShutdown:
                        res = self._PcOnLcShutdownDetected()

        if not res.isContinue:
            pass
        elif self._isAborting or self._isInLcCeaseMode:
            pass
        elif bSkipErrorProc_:
            pass
        else:
            res = self._ProcEuErrors()

        if not res.isContinue:
            if not self._isTerminating:
                if eAbortState_ is None:
                    eAbortState_ = _TaskState._EState.eProcessingAborted

                if res.isAbort:
                    self._SetTaskState(eAbortState_)
                else:
                    self._SetTaskState(_TaskState._EState.eProcessingStopped)
        return res

    def __HandleException(self, xcp_ : _XcoExceptionRoot, bCaughtByApiExecutor_ =True) -> _ETernaryOpResult:

        if self._isInvalid:
            return _ETernaryOpResult.Abort()

        with self.__mtxData:

            _xcoXcp = None if xcp_.isXTaskException else xcp_
            _xbx    = None if (_xcoXcp is None) or not isinstance(_xcoXcp, _XcoBaseException) else _xcoXcp

            if _xbx is not None:
                if _xbx.eExceptionType.isBaseExceptionAtrributeError:
                    _xmlrMsg = _AbstractRunnable.__XML_RUNNER_XCP_MSG_DuplicateWriter

                    if _xbx.shortMessage == _xmlrMsg:
                        return _ETernaryOpResult.MapExecutionState2TernaryOpResult(self)

            if self._isAborting:
                pass
            elif _xbx is not None:
                self._ProcUnhandledXcp(_xbx)

            self._SetDrivingTaskXPhase(_ETaskExecutionPhaseID.eFwHandling)

            if not (self._isAborting or self._isInLcCeaseMode):
                if not bCaughtByApiExecutor_:
                    _eProcRes = self._ProcEuErrors()

                    if not _eProcRes.isContinue:
                        _tstate = _TaskState._EState.eProcessingStopped if _eProcRes.isStop else _TaskState._EState.eProcessingAborted
                        self._SetTaskState(_tstate)

            if not self.isRunning:
                res = _ETernaryOpResult.Abort() if self._isAborting else _ETernaryOpResult.Stop()
            else:
                res = _ETernaryOpResult.Continue()
            return res

    def __CheckMutuallyExclusiveAPI(self) -> bool:
        res = True

        _bNOT_COMPACT = False
        _tname        = type(self).__name__

        _bProvidingRunExecutable        = self.__ag.isProvidingRunExecutable
        _bProvidingProcessInternalMsg   = self.__ag.isProvidingProcessInternalMsg
        _bProvidingProcessExternalMsg   = self.__ag.isProvidingProcessExternalMsg
        _bProvidingProcessInternalQueue = self.__ag.isProvidingProcessInternalQueue
        _bProvidingProcessExternalQueue = self.__ag.isProvidingProcessExternalQueue

        if _bProvidingProcessInternalMsg and _bProvidingProcessInternalQueue:
            res = False
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00127)

        elif _bProvidingProcessExternalMsg and _bProvidingProcessExternalQueue:
            res = False
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00128)

        elif _bProvidingRunExecutable and _bProvidingProcessExternalQueue:
            res = False
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00129)

        elif not (_bProvidingRunExecutable or _bProvidingProcessExternalQueue or _bProvidingProcessExternalMsg):
            res = False
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00130)
        return res

    def __CreateExecPlan(self):
        _tname = type(self).__name__

        _dsid = dict()
        for name, member in _ERunnableExecutionStepID.__members__.items():
            _dsid[member] = False

        if self.isProvidingSetUpRunnable:
            _sid = _ERunnableExecutionStepID.eSetUpExecutable
            _dsid[_sid] = True

        if self.isProvidingTearDownRunnable:
            _sid = _ERunnableExecutionStepID.eTeardownExecutable
            _dsid[_sid] = True

        if self.isProvidingCustomManagedExternalQueue:
            _sid = _ERunnableExecutionStepID.eCustomManagedExternalQueue
            _dsid[_sid] = True

        else:
            _sid = _ERunnableExecutionStepID.eRunExecutable
            _dsid[_sid] = True

            if self.isProvidingAutoManagedExternalQueue:
                if not self.isProvidingRunExecutable:
                    _sid = _ERunnableExecutionStepID.eAutoManagedExternalQueue
                    _dsid[_sid] = True
                else:
                    _sid = _ERunnableExecutionStepID.eAutoManagedExternalQueue_By_RunExecutable
                    _dsid[_sid] = True

        if self.isProvidingCustomManagedInternalQueue:
            if not self.isProvidingRunExecutable:
                _sid = _ERunnableExecutionStepID.eCustomManagedInternalQueue_By_AutoManagedExternalQueue
                _dsid[_sid] = True
            else:
                _sid = _ERunnableExecutionStepID.eCustomManagedInternalQueue_By_RunExecutable
                _dsid[_sid] = True

        elif self.isProvidingAutoManagedInternalQueue:
            if not self.isProvidingRunExecutable:
                _sid = _ERunnableExecutionStepID.eAutoManagedInternalQueue_By_AutoManagedExternalQueue
                _dsid[_sid] = True
            else:
                _sid = _ERunnableExecutionStepID.eAutoManagedInternalQueue_By_RunExecutable
                _dsid[_sid] = True

        self.__execPlan = _AbstractRunnable._RunnableExecutionPlan(_dsid)

    def __CreateExecutorTable(self, bXTaskRbl_ : bool):

        _dictExecutors = dict()
        for name, member in _ERunnableApiFuncTag.__members__.items():
            if not member.isRunnableExecutionAPI:
                continue
            if not self.__ag._IsProvidingApiFunction(eApiFuncTag_=member):
                continue
            _dictExecutors[member] = _RunnableApiExecutor(bXTaskRbl_, self.__ag, member, self.__HandleException)

        self.__executors = _AbstractRunnable._RunnableExecutorTable(_dictExecutors)

    def __ProcErrHdlrCallback( self
                             , eCallbackID_           : _EErrorHandlerCallbackID
                             , curFatalError_         : _FatalEntry               =None) -> _ETernaryOpResult:

        if curFatalError_ is None:
            _tailPart = _CommonDefines._CHAR_SIGN_DOT
        else:
            _tailPart = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_023).format(curFatalError_.uniqueID, curFatalError_.shortMessage)

        if eCallbackID_.isFwMainSpecificCallbackID:
            return _ETernaryOpResult.Abort() if self._isAborting else _ETernaryOpResult.Continue()

        _ePF = self._GetProcessingFeasibility(errEntry_=curFatalError_)
        if not _ePF.isFeasible:
            if _ePF.isUnfeasible:
                res = _ETernaryOpResult.Abort() if self._isAborting else _ETernaryOpResult.Continue()
            else:
                res = _ETernaryOpResult.Abort()
            return res

        if not self._executionProfile.isLcFailureReportPermissionEnabled:
            vlogif._LogOEC(False, _EFwErrorCode.VUE_00009)
        else:
            _myFE          = curFatalError_
            _eMyLcCompID = self._eRunnableType.toLcCompID
            self._PcNotifyLcFailure(_eMyLcCompID, _myFE, atask_=self.__drivingTask)

        res = _ETernaryOpResult.Abort()
        return res

    def __PreProcessCeaseMode(self):
        if self._isInvalid:
            return

        if self._eRunnableType.isFwMainRunnable:
            _dtlb = self._lcDynamicTLB
            _lcMon = None if _dtlb is None else _dtlb._lcMonitor

            if _lcMon is None:
                pass 
            else:
                _bAborting = self.isAborting
                if not _lcMon.isLcShutdownEnabled:
                    _lcMon._EnableCoordinatedShutdown(bManagedByMR_=not _bAborting)

                if not self._isInLcCeaseMode:
                    self._CreateCeaseTLB(bEnding_=_bAborting)

        _bCreateCTLB = self._lcDynamicTLB.isLcShutdownEnabled

        if self._CheckNotifyLcFailure():
            _bCreateCTLB = True

        if not self._isInLcCeaseMode:
            if _bCreateCTLB:
                self._CreateCeaseTLB(bEnding_=self.isAborting)

    def __ProcessCeaseMode(self):
        if self._isInvalid:
            return

        if self._eRunnableType.isFwMainRunnable:
            pass

        elif not self._isInLcCeaseMode:
            if self._lcDynamicTLB.isLcShutdownEnabled:
                self._CreateCeaseTLB(bEnding_=self.isAborting)
            else:
                return

        _eCurCS = self._eLcCeaseState

        if _eCurCS.isPrepareCeasing:
            self.__PrepareDefaultCeasing()

            _eCurCS = self._eLcCeaseState

        if _eCurCS.isEnterCeasing:
            self.__EnterDefaultCeasing()

            _eCurCS = self._eLcCeaseState

        if _eCurCS.isEndingCease:
            self.__ProcessLeavingCease()

            _eCurCS = self._eLcCeaseState

        if not _eCurCS.isDeceased:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00131)

    def __PrepareDefaultCeasing(self):
        if not self._isInLcCeaseMode:
            return

        _eCurCS = self._eLcCeaseState
        if not _eCurCS.isPrepareCeasing:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00132)
            self._lcCeaseTLB.UpdateCeaseState(True)
            return

        _bCustomPrepare = self.__ag.isProvidingPrepareCeasing
        _bCustomPrepare = _bCustomPrepare and (self._lcCeaseTLB._lcMonitor._isCoordinatedShutdownManagedByMR or not self._eRunnableType.isFwMainRunnable)

        if _bCustomPrepare:
            self.__ag.prepareCeasing()
        else:
            while True:
                _ctlb = self._lcCeaseTLB
                if _ctlb is None:
                    return

                _ctlb.IncrementCeaseAliveCounter()
                _TaskUtil.SleepMS(20)

                _ctlb = self._lcCeaseTLB
                if _ctlb is None:
                    return

                if not _ctlb.isCoordinatedShutdownRunning:
                    self._lcCeaseTLB.UpdateCeaseState(True)
                    break

                if _ctlb._isCeasingGateOpened:
                    break

            self._lcCeaseTLB.HopToNextCeaseState(bEnding_=self._isAborting)

    def __EnterDefaultCeasing(self):
        if not self._isInLcCeaseMode:
            return

        _eCurCS = self._eLcCeaseState
        if not _eCurCS.isEnterCeasing:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00133)
            self._lcCeaseTLB.UpdateCeaseState(True)
            return

        self._lcCeaseTLB.HopToNextCeaseState(bEnding_=self._isAborting)

        _bRCIter = self.__ag.isProvidingRunCeaseIteration

        _bPreShutdownPassed = False
        while True:
            if not self._lcCeaseTLB.isCeasing:
                break

            self._lcCeaseTLB.IncrementCeaseAliveCounter()

            _TaskUtil.SleepMS(self._executionProfile.cyclicCeaseTimespanMS)

            if self._isInvalid:
                break

            if _bRCIter:
                self.__ag.runCeaseIteration()

            if not self._lcCeaseTLB.isCeasing:
                self._lcCeaseTLB.UpdateCeaseState(True)
                break

            if not _bPreShutdownPassed:
                if self._lcCeaseTLB._isPreShutdownGateOpened:
                    _bPreShutdownPassed = True

                    self.__ExecuteTeardown()

                    self._lcCeaseTLB.HopToNextCeaseState(bEnding_=self._isAborting)
                    continue

            if self._lcCeaseTLB._isShutdownGateOpened:
                break

        if self._lcCeaseTLB is not None:
            self._lcCeaseTLB.HopToNextCeaseState(bEnding_=self._isAborting)

    def __ProcessLeavingCease(self):
        if not self._isInLcCeaseMode:
            return

        _eCurCS = self._eLcCeaseState
        if not self._lcCeaseTLB.isEndingCease:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00134)

            if self._lcCeaseTLB.isDeceased:
                return

            self._lcCeaseTLB.UpdateCeaseState(True)

        while True:
            if (not self._lcCeaseTLB.isCoordinatedShutdownRunning) or self._lcCeaseTLB.isCoordinatedShutdownGateOpened:
                break

            self._lcCeaseTLB.IncrementCeaseAliveCounter()

            _TaskUtil.SleepMS(self._executionProfile.cyclicCeaseTimespanMS)

            if self._isInvalid:
                break

            _eCSR = self._lcCeaseTLB.eCurrentShutdownRequest
            if (_eCSR is None) or _eCSR.isShutdown:
                break

            continue

        if self._lcCeaseTLB is not None:
            self._lcCeaseTLB.HopToNextCeaseState(bEnding_=True)

class _RunnableApiExecutor(_AbstractSlotsObject):

    __slots__ = [ '__er'   , '__apiG' , '__apiF' , '__eFID' , '__rbl' , '__xt'
                , '__txph' , '__xcpH' , '__par1' , '__par2' , '__args' , '__kwargs' ]

    def __init__(self, bXTaskRbl_ : bool, apiGuide_  : _ARunnableApiGuide, eFuncID_ : _ERunnableApiFuncTag, xcpHdlr_):
        super().__init__()
        self.__er     = None
        self.__xt     = None
        self.__rbl    = None
        self.__apiF   = None
        self.__apiG   = apiGuide_
        self.__eFID   = eFuncID_
        self.__xcpH   = xcpHdlr_
        self.__txph   = None
        self.__par1   = None
        self.__par2   = None
        self.__args   = None
        self.__kwargs = None

        if not isinstance(eFuncID_, _ERunnableApiFuncTag):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00135)
            self.CleanUp()
        elif xcpHdlr_ is None:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00136)
            self.CleanUp()
        elif not isinstance(apiGuide_, _ARunnableApiGuide):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00137)
            self.CleanUp()
        elif not isinstance(apiGuide_._runnable, _AbstractRunnable):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00138)
            self.CleanUp()
        elif eFuncID_.value < _ERunnableApiFuncTag.eRFTRunExecutable.value or eFuncID_.value > _ERunnableApiFuncTag.eRFTOnRunProgressNotification.value:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00139)
            self.CleanUp()
        elif self.__SetApiFunc() is None:
            self.CleanUp()
        else:
            _txph = eFuncID_.MapToTaskExecutionPhaseID(bXTask_=bXTaskRbl_)
            if _txph.isNone:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00140)
                self.CleanUp()
            else:
                self.__xt   = apiGuide_._runnable._xtaskInst
                self.__rbl  = apiGuide_._runnable
                self.__txph = _txph

    @property
    def apiGuide(self) -> _ARunnableApiGuide:
        return self.__apiG

    @property
    def executionResult(self) -> _ETernaryOpResult:
        return self.__er

    @property
    def eApiFunctID(self) -> _ERunnableApiFuncTag:
        return self.__eFID

    def SetExecutorParams(self, param1_ =None, param2_ =None, args_ =None, kwargs_ =None):
        if self.__eFID is not None:
            self.__par1   = param1_
            self.__par2   = param2_
            self.__args   = args_
            self.__kwargs = kwargs_

    def Execute(self) -> _ETernaryOpResult:

        if self.__eFID is None:
            return self.__er

        self.__er = _ETernaryOpResult.Abort()

        if self.__apiF is None:
            return self.__er

        _ret = None
        try:
            self.__runnable._SetDrivingTaskXPhase(self.__txph)

            if self.__eFID == _ERunnableApiFuncTag.eRFTSetUpExecutable:
                if (self.__args is None) or (self.__kwargs is None):
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00141)
                elif not self.__isXTaskRunnable:
                    _ret = self.__apiF(*self.__args, **self.__kwargs)
                else:
                    _ret = self.__xtask.SetUpXTask()

            elif self.__eFID == _ERunnableApiFuncTag.eRFTOnTimeoutExpired:
                if (self.__par1 is None) or (self.__args is None) or (self.__kwargs is None):
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00142)
                else:
                    _ret = self.__apiF(self.__par1, *self.__args, **self.__kwargs)

            else:
                _bProcIntMsg = self.__eFID == _ERunnableApiFuncTag.eRFTProcessInternalMsg

                if _bProcIntMsg or self.__eFID == _ERunnableApiFuncTag.eRFTProcessExternalMsg:
                    if self.__par1 is None:
                        vlogif._LogOEC(True, _EFwErrorCode.VFE_00143)
                    elif (self.__par2 is not None) and not (isinstance(self.__par2, _CallableIF) and self.__par2.isValid):
                        vlogif._LogOEC(True, _EFwErrorCode.VFE_00144)
                    elif not self.__isXTaskRunnable:
                        _ret = self.__apiF(self.__par1, self.__par2)
                    else:
                        if _bProcIntMsg:
                            _ret = self.__xtask.ProcessInternalMessage(self.__par1, self.__par2)
                        else:
                            _ret = self.__xtask.ProcessExternalMessage(self.__par1, self.__par2)

                elif self.__eFID == _ERunnableApiFuncTag.eRFTOnRunProgressNotification:
                    if self.__par1 is None:
                        vlogif._LogOEC(True, _EFwErrorCode.VFE_00145)
                    else:
                        _ret = self.__apiF(self.__par1)

                elif (self.__eFID == _ERunnableApiFuncTag.eRFTRunExecutable) or (self.__eFID == _ERunnableApiFuncTag.eRFTTearDownExecutable):
                    if not self.__isXTaskRunnable:
                        _ret = self.__apiF()
                    elif self.__eFID == _ERunnableApiFuncTag.eRFTTearDownExecutable:
                        _ret = self.__xtask.TearDownXTask()
                    else:
                        _ret = self.__xtask.RunXTask()

                else:
                    _ret = self.__apiF()

            self.__runnable._SetDrivingTaskXPhase(_ETaskExecutionPhaseID.eFwHandling)

            _ret = self.__apiG._SetGetExecutionApiFunctionReturn(_ret)

            if _ret.isAbort:
                self.__runnable._SetTaskState(_TaskState._EState.eProcessingAborted)

                self.__runnable._CheckNotifyLcFailure()

        except _XcoExceptionRoot as xcp:
            _ret = self.__xcpH(xcp, bCaughtByApiExecutor_=True)

        except BaseException as xcp:
            xcp = _XcoBaseException(xcp, tb_=logif._GetFormattedTraceback())
            _ret = self.__xcpH(xcp, bCaughtByApiExecutor_=True)

        finally:
            _xres = _ETernaryOpResult.ConvertFrom(_ret)
            self.__er = _xres

        self.__par1   = None
        self.__args   = None
        self.__kwargs = None

        return self.__er

    def _ToString(self, *args_, **kwargs_):
        if self.__eFID is None:
            return None
        return _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_002).format(type(self).__name__, self.__runnable._runnableName, self.__eFID.functionName)

    def _CleanUp(self):
        self.__er     = None
        self.__xt     = None
        self.__rbl    = None
        self.__apiF   = None
        self.__apiG   = None
        self.__eFID   = None
        self.__xcpH   = None
        self.__txph   = None
        self.__par1   = None
        self.__par2   = None
        self.__args   = None
        self.__kwargs = None

    @property
    def __isXTaskRunnable(self):
        return self.__xt is not None

    @property
    def __logPrefix(self):
        res = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_003)
        return res.format(self.__runnable._runnableName, self.__eFID.functionName)

    @property
    def __runnable(self):
        return self.__rbl

    @property
    def __xtask(self):
        return self.__xt

    def __SetApiFunc(self):
        if (self.__apiG is None) or (self.__eFID is None):
            return None

        res            = None
        _bUnexpectedErr = False

        if self.__eFID == _ERunnableApiFuncTag.eRFTRunExecutable:
            res = self.__apiG.runExecutable

        elif self.__eFID == _ERunnableApiFuncTag.eRFTSetUpExecutable:
            res = self.__apiG.setUpRunnable

        elif self.__eFID == _ERunnableApiFuncTag.eRFTProcessExternalMsg:
            res = self.__apiG.procExternalMsg

        elif self.__eFID == _ERunnableApiFuncTag.eRFTProcessInternalMsg:
            res = self.__apiG.procInternalMsg

        elif self.__eFID == _ERunnableApiFuncTag.eRFTOnTimeoutExpired:
            res = self.__apiG.onTimeoutExpired

        elif self.__eFID == _ERunnableApiFuncTag.eRFTTearDownExecutable:
            res = self.__apiG.tearDownRunnable

        elif self.__eFID == _ERunnableApiFuncTag.eRFTProcessExternalQueue:
            res = self.__apiG.procExternalQueue

        elif self.__eFID == _ERunnableApiFuncTag.eRFTProcessInternalQueue:
            res = self.__apiG.procInternalQueue

        elif self.__eFID == _ERunnableApiFuncTag.eRFTOnRunProgressNotification:
            res = self.__apiG.onRunProgressNotification

        else:
            _bUnexpectedErr = True
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00146)

        if res is None:
            if not _bUnexpectedErr:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00147)
        else:
            self.__apiF = res
        return res
