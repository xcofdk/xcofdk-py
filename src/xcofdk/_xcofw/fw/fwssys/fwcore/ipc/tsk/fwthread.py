# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwthread.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from xcofdk.fwapi.xtask import XTask

from xcofdk._xcofw.fw.fwssys.fwcore.logging               import logif
from xcofdk._xcofw.fw.fwssys.fwcore.logging               import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logdefines    import _EErrorImpact
from xcofdk._xcofw.fw.fwssys.fwcore.logging.errorentry    import _ErrorEntry
from xcofdk._xcofw.fw.fwssys.fwcore.logging.fatalentry    import _FatalEntry
from xcofdk._xcofw.fw.fwssys.fwcore.logging.xcoexception  import _XcoExceptionRoot
from xcofdk._xcofw.fw.fwssys.fwcore.logging.xcoexception  import _XcoBaseException
from xcofdk._xcofw.fw.fwssys.fwcore.base.callableif       import _CallableIF
from xcofdk._xcofw.fw.fwssys.fwcore.base.timeutil         import  _TimeAlert
from xcofdk._xcofw.fw.fwssys.fwcore.base.gtimeout         import _Timeout
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.err.euerrhandler  import _EuErrorHandler
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.err.euerrhandler  import _EErrorHandlerCallbackID
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.sync.mutex        import _Mutex
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.sync.semaphore    import _BinarySemaphore
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.sync.syncresguard import _SyncResourcesGuard
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcdefines          import _ELcCompID
from xcofdk._xcofw.fw.fwssys.fwcore.lcmon.lcmontlb        import _ELcCeaseTLBState
from xcofdk._xcofw.fw.fwssys.fwcore.lcmon.lcmontlb        import _LcCeaseTLB
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject         import _AbstractSlotsObject
from xcofdk._xcofw.fw.fwssys.fwcore.types.aprofile        import _AbstractProfile
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes     import _CommonDefines
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes     import _ETernaryOpResult

from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.ataskop       import _EATaskOperationID
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.ataskop       import _ATaskOperationPreCheck
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.atask         import _AbstractTask
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.execprofile   import _ExecutionProfile
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.fwthreaddefs  import _EXTaskApiFuncTag
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.fwthreaddefs  import _XTaskApiGuide
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.threadprofile import _ThreadProfile
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskbadge     import _TaskBadge
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskerror     import _TaskError
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskerror     import _TaskErrorExtended
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskstate     import _TaskState
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil      import _TaskUtil
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil      import _ETaskType
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil      import _PyThread
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil      import _EFwApiBookmarkID
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil      import _ETaskExecutionPhaseID
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil      import _EProcessingFeasibilityID

from xcofdk._xcofw.fw.fwssys.fwcore.apiimpl.xtask.xtaskconn import _XTaskConnector

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine



class _FwThread(_AbstractTask):

    class _LinkedXTaskRefs(_AbstractSlotsObject):
        __slots__ = [ '__xtask' , '__xtaskConn' ]

        def __init__(self, xtsk_ : XTask, xtaskConn_ : _XTaskConnector):
            super().__init__()
            self.__xtask     = xtsk_
            self.__xtaskConn = xtaskConn_

        @property
        def xtaskInst(self):
            return self.__xtask

        @property
        def xtaskConn(self):
            return self.__xtaskConn

        def _ToString(self, *args_, **kwargs_) -> str:
            pass

        def _CleanUp(self):
            if self.__xtaskConn is not None:
                self.__xtaskConn._DisconnectXTask()
                self.__xtaskConn.CleanUp()

            self.__xtask     = None
            self.__xtaskConn = None


    class _XTaskExecutorTable(_AbstractSlotsObject):

        __slots__ = [ '__dictExecutors' ]

        def __init__(self, dictExecutors_ : dict):
            self.__dictExecutors = dictExecutors_
            super().__init__()

        def _GetApiExecutor(self, eFuncID_ : _EXTaskApiFuncTag):
            res = None
            if self.__dictExecutors is None:
                pass
            elif not isinstance(eFuncID_, _EXTaskApiFuncTag):
                pass
            elif not eFuncID_ in self.__dictExecutors:
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

    __slots__ = [ '__mtxApi' , '__mtxData' , '__thrdProfile' , '__semSS' , '__execPrf'
                , '__ag'     , '__bAutocreatedTP' , '__LinkedXTaskRefs' , '__executors'
                ]

    __XML_RUNNER_XCP_MSG_DuplicateWriter               = _FwTDbEngine.GetText(_EFwTextID.eMisc_XML_RUNNER_XCP_MSG_DuplicateWriter)
    __bPRINT_WNG_UPON_TENOTIF_OF_AUTO_ENCLOSED_THREADS = True

    def __init__( self
                , thrdProfile_                : _ThreadProfile    =None
                , xtaskConn_                  : _XTaskConnector   =None
                , taskName_                   : str               =None
                , enclosedPyThread_           : _PyThread         =None
                , bAutoEnclosedPyThrd_        : bool              =None
                , bAutoStartEnclosedPyThread_ : bool              =None
                , threadTargetCallableIF_     : _CallableIF       =None
                , bFwMain_                    : bool              =False
                , args_                       : list              =None
                , kwargs_                     : dict              =None
                , threadProfileAttrs_         : dict              =None
                , execProfile_                : _ExecutionProfile =None):

        self.__ag                = None
        self.__semSS             = None
        self.__mtxApi            = None
        self.__mtxData           = None
        self.__execPrf           = None
        self.__executors         = None
        self.__thrdProfile       = None
        self.__bAutocreatedTP    = None
        self.__LinkedXTaskRefs = None

        super().__init__()

        self.__mtxData = _Mutex()
        self._tstMutex = _Mutex()

        _ts = None
        _tp = None
        _ts, _tp = self.__EvaluateCtorParams( thrdProfile_=thrdProfile_
                                            , xtaskConn_=xtaskConn_
                                            , taskName_=taskName_
                                            , enclosedPyThread_=enclosedPyThread_
                                            , bAutoStartEnclosedPyThread_=bAutoStartEnclosedPyThread_
                                            , threadTargetCallableIF_=threadTargetCallableIF_
                                            , args_=args_
                                            , kwargs_=kwargs_
                                            , threadProfileAttrs_=threadProfileAttrs_)
        if _ts is None:
            self.__CleanUpOnCtorFailure(mtxData_=self.__mtxData)
            return

        if (execProfile_ is not None) and not (isinstance(execProfile_, _ExecutionProfile) and execProfile_.isValid):
            self.__CleanUpOnCtorFailure(mtxData_=self.__mtxData)
            vlogif._LogOEC(True, -1258)
            return

        _xtc = _tp.xtaskConnector
        if _xtc is not None:
            if (_xtc.executionProfile is None) or not _xtc.executionProfile.isValid:
                self.__CleanUpOnCtorFailure(mtxData_=self.__mtxData)
                vlogif._LogOEC(True, -1259)
                return

            execProfile_ = _xtc.executionProfile

        _tid   = _TaskUtil.GetNextTaskID(_tp.taskRightsMask.hasUserTaskRight, _tp.isEnclosingStartupThread, bAutoEnclosedPyThrd_=bAutoEnclosedPyThrd_)
        _tname = None

        _bUSE_AUTO_GENERATED_TASK_NAMES_ONLY = True
        if not _bUSE_AUTO_GENERATED_TASK_NAMES_ONLY:
            _tname = _tp.taskName
        if _tname is None:
            _txtID = _EFwTextID.eMisc_TaskNamePrefix_Thread if _xtc is None else _EFwTextID.eMisc_TaskNamePrefix_XThread
            _tname = f'{_FwTDbEngine.GetText(_txtID)}{_tid}'

        _tp.Freeze(*(_tid, _tname))
        if not _tp.isFrozen:
            _tp = _tp if thrdProfile_ is None else None
            self.__CleanUpOnCtorFailure(mtxData_=self.__mtxData, thrdProfile_=_tp)
            return

        if _xtc is None:
            _linkedXUR = None
        else:
            _linkedXUR = _FwThread._LinkedXTaskRefs(_xtc._connectedXTask, _xtc)

        _bAutoStart = not bAutoEnclosedPyThrd_
        _bAutoStart = _bAutoStart and _tp.isEnclosingPyThread
        if _bAutoStart:
            _bAutoStart = bAutoStartEnclosedPyThread_ if bAutoStartEnclosedPyThread_ is not None else _tp.isAutoStartEnclosedPyThreadEnabled
            if _bAutoStart:
                if not _TaskUtil.IsCurPyThread(thrdProfile_.enclosedPyThread):
                    vlogif._LogOEC(True, -1260)

                    _tp = _tp if thrdProfile_ is None else None
                    self.__CleanUpOnCtorFailure( mtxData_=self.__mtxData, thrdProfile_=_tp, linkedXTaskRefs_=_linkedXUR)
                    return

        _thrdNID       = None
        _bEnclPyThread = _tp.isEnclosingPyThread

        if _bEnclPyThread:
            _myThrd = _tp.enclosedPyThread
            if _TaskUtil.IsNativeThreadIdSupported():
                _thrdNID = _myThrd.native_id
        else:
            _myThrd = _PyThread(group=None, target=self.__RunThrdTgtCallback, name=_tname, args=(), kwargs={}, daemon=None)

        if bFwMain_:
            _tt = _ETaskType.eFwMainThread
        elif _linkedXUR is None:
            _tt = _ETaskType.eFwThread
        else:
            _tt = _ETaskType.eMainXTaskThread if _linkedXUR.xtaskInst.xtaskProfile.isMainTask else _ETaskType.eXTaskThread

        _myTskBadge = _TaskBadge( taskName_=_tname, taskID_=_tid, threadUID_=_TaskUtil.GetPyThreadUniqueID(_myThrd)
                                , taskType_=_tt, trMask_=_tp.taskRightsMask, threadNID_=_thrdNID
                                , bEnclosingPyThrd_=_bEnclPyThread, bEnclosingStartupThrd_=_tp.isEnclosingStartupThread
                                , bAutoEnclosedPyThrd_=bAutoEnclosedPyThrd_)
        if _myTskBadge.taskID is None:
            _tp = _tp if thrdProfile_ is None else None
            self.__CleanUpOnCtorFailure( mtxData_=self.__mtxData, thrdProfile_=_tp
                                       , linkedXTaskRefs_=_linkedXUR, tskBadge_=_myTskBadge)
            return

        _bFEL = _myTskBadge.hasForeignErrorListnerTaskRight

        _ALWAYS_PROVIDE_TE_CALLBACK = True
        _bProvideTECallback         = True

        if not _ALWAYS_PROVIDE_TE_CALLBACK:
            if (not _bFEL) and _bEnclPyThread:
                _bProvideTECallback = False

        if not _bProvideTECallback:
            _tecbif = None
        else:
            _tecbif = _CallableIF(self._OnTENotification)
            if not _tecbif.isValid:
                _tp = _tp if thrdProfile_ is None else None
                self.__CleanUpOnCtorFailure( mtxData_=self.__mtxData, thrdProfile_=_tp
                                           , linkedXTaskRefs_=_linkedXUR, tskBadge_=_myTskBadge, terrCallableIF_=_tecbif)
                return

        if _bFEL:
            _tskErr = _TaskErrorExtended(self.__mtxData, _myTskBadge, taskErrorCallableIF_=_tecbif)
        else:
            _tskErr = _TaskError(self.__mtxData, _myTskBadge, taskErrorCallableIF_=_tecbif)

        if _tskErr.taskBadge is None:
            _tp = _tp if thrdProfile_ is None else None
            self.__CleanUpOnCtorFailure( mtxData_=self.__mtxData, thrdProfile_=_tp, linkedXTaskRefs_=_linkedXUR
                                       , tskBadge_=_myTskBadge, terrCallableIF_=_tecbif, tskError_=_tskErr)
            return

        if execProfile_ is None:
            if bAutoEnclosedPyThrd_:
                pass
            else:
                _runPhaseFrequencyMS = 0 if _bEnclPyThread else None
                execProfile_ = _ExecutionProfile(runPhaseFreqMS_=_runPhaseFrequencyMS)
        else:
            execProfile_ = execProfile_._Clone(bPrint_=True)

        self._execConn     = _xtc
        self._tskBadge     = _myTskBadge
        self._tskError     = _tskErr
        self._tskState     = _ts
        self._linkedPyThrd = _myThrd

        self.__mtxApi            = _Mutex()
        self.__execPrf           = execProfile_
        self.__thrdProfile       = _tp
        self.__bAutocreatedTP    = thrdProfile_ is None
        self.__LinkedXTaskRefs = _linkedXUR

        if _linkedXUR is not None:
            _ag = _XTaskApiGuide(self, _FwThread.__GetExcludedXTaskApiMask(_linkedXUR.xtaskInst))
            if _ag.eApiMask is None:
                _ag.CleanUp()

                _tp = _tp if thrdProfile_ is None else None
                self.__CleanUpOnCtorFailure(mtxData_=self.__mtxData, thrdProfile_=_tp, linkedXTaskRefs_=_linkedXUR
                    , tskBadge_=_myTskBadge, terrCallableIF_=_tecbif, tskError_=_tskErr)
                return
            else:
                self.__ag = _ag

                self.__CreateExecutorTable()
                if self.__executors is None:
                    _tp = _tp if thrdProfile_ is None else None
                    self.__CleanUpOnCtorFailure(mtxData_=self.__mtxData, thrdProfile_=_tp, linkedXTaskRefs_=_linkedXUR
                        , tskBadge_=_myTskBadge, terrCallableIF_=_tecbif, tskError_=_tskErr)
                    return

        if _xtc is not None:
            if not _xtc._UpdateXD(_ts, tskBadge_=_myTskBadge, tskProfile_=_tp, linkedPyThrd_=_myThrd):
                self.CleanUp()
                return

        _EuErrorHandler._SetUpEuEH(self, self.__mtxData)
        if self._isForeignErrorListener is None:
            self.CleanUp()
            return

        if bAutoEnclosedPyThrd_:
            self._CheckSetTaskState(_TaskState._EState.eRunning)
            self._SetTaskExecPhase(_ETaskExecutionPhaseID.eDummyRunningAutoEnclosedThread)

        if not bAutoEnclosedPyThrd_:
            if _bAutoStart:
                self.__StartPyThread()

    @property
    def threadProfile(self):
        return self.__thrdProfile

    @property
    def _isInvalid(self):
        return self.__mtxData is None

    @property
    def _isAutoStartEnclosedPyThreadEnabled(self) -> bool:
        return False if self.__thrdProfile is None else self.__thrdProfile.isAutoStartEnclosedPyThreadEnabled

    @property
    def _linkedExecutable(self):
        return None if self.__LinkedXTaskRefs is None else self.__LinkedXTaskRefs.xtaskInst

    @property
    def _xtaskConnector(self) -> _XTaskConnector:
        return None if self.__LinkedXTaskRefs is None else self.__LinkedXTaskRefs.xtaskConn

    @property
    def _abstractTaskProfile(self) -> _AbstractProfile:
        return self.threadProfile

    @property
    def _executionProfile(self) -> _ExecutionProfile:
        return self.__execPrf

    @property
    def _eTaskExecPhase(self) -> _ETaskExecutionPhaseID:
        if self._isInvalid:
            return _ETaskExecutionPhaseID.eNone
        with self.__mtxData:
            return self._tskEPhase

    def _PropagateLcProxy(self):
        if self.linkedPyThread is None:
            pass
        else:
            with self.__mtxData:
                if self._lcProxy is not None:
                    if self._execConn is not None:
                        self._execConn._SetLcProxy(self._lcProxy)

    def _GetLcCompID(self) -> _ELcCompID:
        if self._isInvalid:
            res = _ELcCompID.eMiscComp
        elif not self.taskBadge.isXTaskThread:
            res = _ELcCompID.eFwThrd
        elif self.taskBadge.isMainXTaskThread:
            res = _ELcCompID.eMainXTask
        else:
            res = _ELcCompID.eXTask
        return res

    def _StartTask(self, semStart_: _BinarySemaphore =None, tskOpPreCheck_ : _ATaskOperationPreCheck =None, curTask_ : _AbstractTask =None) -> bool:
        if self.linkedPyThread is None:
            return False
        if not self._lcProxy.isLcOperable:
            return False

        with self.__mtxApi:
            if self.isEnclosingPyThread:
                if semStart_ is not None:
                    vlogif._LogOEC(True, -1261)
                    return False
            elif not isinstance(semStart_, _BinarySemaphore):
                vlogif._LogOEC(True, -1262)
                return False

            _oppc = tskOpPreCheck_
            if _oppc is None:
                _oppc = _ATaskOperationPreCheck( _EATaskOperationID.eStart, self._tskState
                                              , self._linkedPyThrd, self.isEnclosingPyThread, reportErr_=True)
            else:
                _oppc.Update(eTaskOpID_=_EATaskOperationID.eStart, reportErr_=True)

            if _oppc.isNotApplicable or _oppc.isIgnorable:
                _bIgnorable = _oppc.isIgnorable
                if _bIgnorable:
                    if semStart_ is not None:
                        semStart_.Give()
                if tskOpPreCheck_ is None:
                    _oppc.CleanUp()
                return _bIgnorable

            elif tskOpPreCheck_ is None:
                _oppc.CleanUp()

            if not self.isEnclosingPyThread:
                with self._tstMutex:
                    self.__semSS = semStart_
                    self._CheckSetTaskState(_TaskState._EState.ePendingRun)

        res       = True
        _prvBid   = None
        _lcCompID = self._GetLcCompID()

        if self.isDrivingXTask:
            _prvBid = None if curTask_ is None else curTask_.eFwApiBookmarkID

        if self.isEnclosingPyThread:
            if _lcCompID.isMainXtask:
                if not self._lcProxy.isMainXTaskStarted:
                    self._lcProxy._SetLcOperationalState(_lcCompID, True, atask_=self)

            if _prvBid is not None:
                curTask_._SetFwApiBookmark(_EFwApiBookmarkID.eXTaskApiBeginActionStart)

            self.__StartPyThread()

            if _prvBid is not None:
                curTask_._SetFwApiBookmark(_prvBid)

            if self._isInvalid or (self._lcProxy is None):
                res = False
            elif _lcCompID.isMainXtask:
                if not (self.isFailed or self._lcProxy.isMainXTaskFailed):
                    if not self._lcProxy.isMainXTaskStopped:
                        self._lcProxy._SetLcOperationalState(_lcCompID, False, atask_=self)
        else:
            if _prvBid is not None:
                curTask_._SetFwApiBookmark(_EFwApiBookmarkID.eXTaskApiBeginActionStart)

            self._SetTaskExecPhase(_ETaskExecutionPhaseID.eFwHandling)
            self.linkedPyThread.start()

            if _prvBid is not None:
                curTask_._SetFwApiBookmark(_prvBid)

            with self.__mtxData:
                _tuid          = self.taskBadge.threadUID
                _tnid          = self.taskBadge.threadNID
                _bNIDSupported = _TaskUtil.IsNativeThreadIdSupported()

                if (_tuid is None) or ((_tnid is None) and _bNIDSupported):
                    if _tuid is None:
                        _tuid = _TaskUtil.GetPyThreadUniqueID(self.linkedPyThread)
                    if (_tnid is None) and _bNIDSupported:
                        _tnid = self.linkedPyThread.native_id
                    self.taskBadge._UpdateRuntimeIDs(threadUID_=_tuid, threadNID_=_tnid)

            if _lcCompID.isMainXtask:
                if not (self.isFailed or self._lcProxy.isMainXTaskFailed):
                    if self.isDone:
                        if not self._lcProxy.isMainXTaskStopped:
                            self._lcProxy._SetLcOperationalState(_lcCompID, False, atask_=self)
                    elif not self._lcProxy.isMainXTaskStarted:
                        self._lcProxy._SetLcOperationalState(_lcCompID, True, atask_=self)
        return res

    def _RestartTask(self, semStart_ : _BinarySemaphore =None, tskOpPreCheck_ : _ATaskOperationPreCheck =None, curTask_ : _AbstractTask =None) -> bool:
        if self.linkedPyThread is None:
            return False
        vlogif._LogOEC(True, -1263)
        return False

    def _StopTask(self, semStop_: _BinarySemaphore =None, tskOpPreCheck_ : _ATaskOperationPreCheck =None, curTask_ : _AbstractTask =None) -> bool:
        if self.linkedPyThread is None:
            return False

        with self.__mtxApi:
            if self.isEnclosingPyThread:
                if semStop_ is not None:
                    vlogif._LogOEC(True, -1264)
                    return False
            elif (semStop_ is not None) and not isinstance(semStop_, _BinarySemaphore):
                vlogif._LogOEC(True, -1265)
                return False
            elif self.__startStopSem is not None:
                vlogif._LogOEC(True, -1266)
                return False

            _oppc = tskOpPreCheck_
            if _oppc is None:
                _oppc = _ATaskOperationPreCheck( _EATaskOperationID.eStop, self._tskState
                                              , self._linkedPyThrd, self.isEnclosingPyThread, reportErr_=True)
            else:
                _oppc.Update(eTaskOpID_=_EATaskOperationID.eStop, reportErr_=True)
            if _oppc.isNotApplicable or _oppc.isIgnorable:
                _bIgnorable = _oppc.isIgnorable
                if _bIgnorable:
                    if semStop_ is not None:
                        semStop_.Give()
                if tskOpPreCheck_ is None:
                    _oppc.CleanUp()
                return _bIgnorable

            if _oppc.isSynchronous:
                if semStop_ is not None:
                    semStop_.Give()
                    semStop_ = None

            if tskOpPreCheck_ is None:
                _oppc.CleanUp()

            _prvBid = None
            if self.isDrivingXTask:
                _prvBid = None if curTask_ is None else curTask_.eFwApiBookmarkID

            with self.__mtxData:
                if _prvBid is not None:
                    curTask_._SetFwApiBookmark(_EFwApiBookmarkID.eXTaskApiBeginActionStop)

            with self._tstMutex:
                self.__semSS = semStop_
                self._CheckSetTaskState(_TaskState._EState.ePendingStopRequest)

            with self.__mtxData:
                if _prvBid is not None:
                    curTask_._SetFwApiBookmark(_prvBid)
        return True

    def _JoinTask(self, timeout_: _Timeout =None, tskOpPreCheck_ : _ATaskOperationPreCheck =None, curTask_ : _AbstractTask =None) -> bool:

        if self._isInvalid or (self.linkedPyThread is None):
            return False
        if timeout_ is not None:
            if not _Timeout.IsTimeout(timeout_, bThrowx_=True):
                return False
            elif timeout_.isInfiniteTimeout:
                timeout_ = None

        _midPart     = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_001)
        _myLogPrefix = self.__logPrefix

        if self.linkedExecutable is None:
            _midPart = _midPart.format(_FwTDbEngine.GetText(_EFwTextID.eMisc_Task), str(self.taskUniqueName))
        else:
            _midPart = _midPart.format(_FwTDbEngine.GetText(_EFwTextID.eMisc_XTask), str(self.taskUniqueName))

        if (self._lcDynTLB is not None) and self._lcDynTLB.isCoordinatedShutdownRunning:
            return False

        with self.__mtxApi:
            _oppc = tskOpPreCheck_
            if _oppc is None:
                _oppc = _ATaskOperationPreCheck( _EATaskOperationID.eJoin, self._tskState
                                               , self._linkedPyThrd, self.isEnclosingPyThread, reportErr_=True)
            else:
                _oppc.Update(eTaskOpID_=_EATaskOperationID.eJoin, reportErr_=True)

            if _oppc.isNotApplicable or _oppc.isIgnorable:
                _bIgnorable = _oppc.isIgnorable
                if tskOpPreCheck_ is None:
                    _oppc.CleanUp()
                return _bIgnorable

            elif tskOpPreCheck_ is None:
                _oppc.CleanUp()

        res                    = False
        _prvBid                = None
        _xcpCaught             = None
        _bCoordShutdownRunning = False

        if self.isDrivingXTask:
            _prvBid = None if curTask_ is None else curTask_.eFwApiBookmarkID

        try:
            if _prvBid is not None:
                curTask_._SetFwApiBookmark(_EFwApiBookmarkID.eXTaskApiBeginActionJoin)

            if self.isEnclosingPyThread or _TaskUtil.IsMainPyThread(self.linkedPyThread):
                _MIN_WAIT_TIMESPAN_MS = 10

                talert = None if timeout_ is None else _TimeAlert(timeout_.toNSec)
                if talert is not None:
                    talert.CheckAlert()

                while True:
                    res = self._isInvalid or (self.isDone or self.isFailed)
                    if res:
                        break

                    if (self._lcDynTLB is not None) and self._lcDynTLB.isCoordinatedShutdownRunning:
                        _bCoordShutdownRunning = True
                        break

                    _TaskUtil.SleepMS(_MIN_WAIT_TIMESPAN_MS)
                    if (talert is not None) and talert.CheckAlert():
                        break
                    continue

            else:
                _timeoutMS              = 0 if timeout_ is None else timeout_.toMSec
                _totalJoinTimespanMS    = 0
                _stepwiseJoinTimespanMS = _ExecutionProfile._GetLcMonitorCyclicRunPauseTimespanMS()
                if _stepwiseJoinTimespanMS is None:
                    _stepwiseJoinTimespanMS = 100
                if (_timeoutMS > 0) and (_timeoutMS < _stepwiseJoinTimespanMS):
                    _stepwiseJoinTimespanMS = _timeoutMS
                _stepwiseJoinTimespanSEC = float(_stepwiseJoinTimespanMS/1000)

                while True:
                    self.linkedPyThread.join(_stepwiseJoinTimespanSEC)
                    _totalJoinTimespanMS += _stepwiseJoinTimespanMS
                    if (_timeoutMS > 0) and (_totalJoinTimespanMS >= _timeoutMS):
                        break
                    if self._isInvalid or (self.isDone or self.isFailed):
                        res = True
                        break
                    if (self._lcDynTLB is not None) and self._lcDynTLB.isCoordinatedShutdownRunning:
                        _bCoordShutdownRunning = True
                        break
                    continue

        except _XcoExceptionRoot as xcp:
            pass
        except KeyboardInterrupt:
            pass
        except BaseException as xcp:
            _xcpCaught = xcp

        finally:
            if _prvBid is not None:
                curTask_._SetFwApiBookmark(_prvBid)

            if _xcpCaught is not None:
                logif._LogUnhandledXcoBaseXcp(_xcpCaught)

        if not res:
            if _bCoordShutdownRunning:
                pass
            elif timeout_ is not None:
                vlogif._LogOEC(False, -3006)
            else:
                vlogif._LogOEC(False, -3007)
        return res


    def _ProcErrorHandlerCallback( self
                                 , eCallbackID_           : _EErrorHandlerCallbackID
                                 , curFatalError_         : _FatalEntry               =None
                                 , lstForeignFatalErrors_ : list                     =None) -> _ETernaryOpResult:

        _tailPart = '.' if curFatalError_ is None else ': [{}] - {}'.format(curFatalError_.uniqueID, curFatalError_.shortMessage)

        if eCallbackID_.isFwMainSpecificCallbackID:
            return _ETernaryOpResult.Abort() if self.isAborting else _ETernaryOpResult.Continue()

        _ePF = self.__GetProcessingFeasiblity(errEntry_=curFatalError_)
        if not _ePF.isFeasible:
            if _ePF.isUnfeasible:
                res = _ETernaryOpResult.Abort() if self.isAborting else _ETernaryOpResult.Continue()
            else:
                res = _ETernaryOpResult.Abort()
            return res

        if not self.executionProfile.isLcFailureReportPermissionEnabled:
            vlogif._LogOEC(False, -3008)
        else:
            _frc   = curFatalError_
            _myMtx = curFatalError_._LockInstance()

            if _frc.isInvalid or not _frc.isPendingResolution:
                pass
            else:
                _frcClone = _frc.Clone()
                if _frcClone is None:
                    vlogif._LogOEC(True, -1267)
                else:
                    _eMyLcCompID = self._GetLcCompID()
                    self._lcProxy._NotifyLcFailure(_eMyLcCompID, _frcClone, atask_=self)

                    _frc._UpdateErrorImpact(_EErrorImpact.eNoImpactByFrcLinkage)

            if not _myMtx is None:
                _myMtx.Give()

        res = _ETernaryOpResult.Abort()
        return res


    @property
    def _isLcProxyClientMonitoringLcModeChange(self) -> bool:
        return self._isMonitoringLcModeChange

    @property
    def _lcProxyClientName(self) -> str:
        return self.taskUniqueName

    def _OnLcCeaseModeDetected(self) -> _ETernaryOpResult:
        if self._isInvalid:
            return _ETernaryOpResult.Abort()

        res = _ETernaryOpResult.Abort() if self.isAborting else _ETernaryOpResult.Stop()

        if self.__isCeaseCapable:
            if not self._isInLcCeaseMode:
                self._CreateCeaseTLB(bAborting_=res.isAbort)
            else:
                self.__UpdateCeaseTLB(res.isAbort)
        return res

    def _OnLcFailureDetected(self) -> _ETernaryOpResult:
        if self._isInvalid:
            return _ETernaryOpResult.Abort()

        res = _ETernaryOpResult.Abort() if self.isAborting else _ETernaryOpResult.Stop()

        if not res.isAbort:
            _bOwnLcFailureSet = False

            _ePF = _EProcessingFeasibilityID.eInCeaseMode if self._isInLcCeaseMode else self.__GetProcessingFeasiblity()
            if not _ePF.isFeasible:
                if not (_ePF.isInCeaseMode or _ePF.isOwnLcCompFailureSet):
                    res = _ETernaryOpResult.Abort()
                elif _ePF.isInCeaseMode:
                    pass
                else:
                    _bOwnLcFailureSet = True

            if not res.isAbort:
                if not _bOwnLcFailureSet:
                    if self._lcProxy.hasLcAnyFailureState:
                        _bOwnLcFailureSet = self._lcProxy.HasLcCompFRC(self._GetLcCompID(), atask_=self)

                if _bOwnLcFailureSet:
                    res = _ETernaryOpResult.Abort()

        if self.__isCeaseCapable:
            if not self.__isInLcCeaseMode:
                self._CreateCeaseTLB(bAborting_=res.isAbort)
            else:
                self.__UpdateCeaseTLB(res.isAbort)
        return res

    def _OnLcPreShutdownDetected(self) -> _ETernaryOpResult:
        if self._isInvalid:
            return _ETernaryOpResult.Abort()

        res = _ETernaryOpResult.Abort() if self.isAborting else _ETernaryOpResult.Stop()

        if not res.isAbort:
            _bOwnLcFailureSet = False

            _ePF = _EProcessingFeasibilityID.eInCeaseMode if self._isInLcCeaseMode else self.__GetProcessingFeasiblity()
            if not _ePF.isFeasible:
                if not (_ePF.isInCeaseMode or _ePF.isOwnLcCompFailureSet):
                    res = _ETernaryOpResult.Abort()

                elif _ePF.isInCeaseMode:
                    pass
                else:
                    _bOwnLcFailureSet = True

            if not res.isAbort:
                if not _bOwnLcFailureSet:
                    if self._lcProxy.hasLcAnyFailureState:
                        _bOwnLcFailureSet = self._lcProxy.HasLcCompFRC(self._GetLcCompID(), atask_=self)

                if _bOwnLcFailureSet:
                    res = _ETernaryOpResult.Abort()

        if self.__isCeaseCapable:
            if not self.__isInLcCeaseMode:
                self._CreateCeaseTLB(bAborting_=res.isAbort)
            else:
                self.__UpdateCeaseTLB(res.isAbort)
        return res

    def _OnLcShutdownDetected(self) -> _ETernaryOpResult:
        if self._isInvalid:
            return _ETernaryOpResult.Abort()

        res = _ETernaryOpResult.Abort() if self.isAborting else _ETernaryOpResult.Stop()

        if self.__isCeaseCapable:
            if not self.__isInLcCeaseMode:
                self._CreateCeaseTLB(bAborting_=True)
            else:
                self.__UpdateCeaseTLB(True)
        return res


    @property
    def _isInLcCeaseMode(self):
        return self.__isInLcCeaseMode

    @property
    def _isMonitoringLcModeChange(self) -> bool:
        _tskSID = self.taskStateID
        return False if _tskSID is None else (_tskSID.isRunning or _tskSID.isStopping)

    @staticmethod
    def _CreateThread( thrdProfile_                : _ThreadProfile  =None
                     , xtaskConn_                  : _XTaskConnector =None
                     , taskName_                   : str             =None
                     , enclosedPyThread_           : _PyThread       =None
                     , bAutoEnclosedPyThrd_        : bool            =None
                     , bAutoStartEnclosedPyThread_ : bool            =None
                     , threadTargetCallableIF_     : _CallableIF     =None
                     , args_                       : list            =None
                     , kwargs_                     : dict            =None
                     , threadProfileAttrs_         : dict            =None):
        res = _FwThread( thrdProfile_=thrdProfile_
                       , xtaskConn_=xtaskConn_
                       , taskName_=taskName_
                       , enclosedPyThread_=enclosedPyThread_
                       , bAutoEnclosedPyThrd_=bAutoEnclosedPyThrd_
                       , bAutoStartEnclosedPyThread_=bAutoStartEnclosedPyThread_
                       , threadTargetCallableIF_=threadTargetCallableIF_
                       , args_=args_
                       , kwargs_=kwargs_
                       , threadProfileAttrs_=threadProfileAttrs_)
        if res.taskBadge is None:
            res.CleanUp()
            res = None
        return res

    def _ToString(self, *args_, **kwargs_):
        return _AbstractTask._ToString(self)

    def _CleanUp(self):

        if self._isInvalid:
            return

        super()._CleanUp()

        if self.__executors is not None:
            self.__executors.CleanUp()
            self.__executors = None

        if self.__ag is not None:
            self.__ag.CleanUp()

        if self.__execPrf is not None:
            self.__execPrf.CleanUp()

        if self.__LinkedXTaskRefs is not None:
            self.__LinkedXTaskRefs.CleanUp()

        if self.__bAutocreatedTP:
            if self.__thrdProfile is not None:
                _thrdTgt = self.__thrdProfile.threadTarget
                if _thrdTgt is not None:
                    _thrdTgt.CleanUp()
                self.__thrdProfile.CleanUp()

        self.__ag                = None
        self.__semSS             = None
        self.__execPrf           = None
        self.__thrdProfile       = None
        self.__bAutocreatedTP    = None
        self.__LinkedXTaskRefs = None

        if self.__mtxApi is not None:
            self.__mtxApi.CleanUp()
            self.__mtxApi = None

        self.__mtxData.CleanUp()
        self.__mtxData = None

    def _OnTENotification(self, errEntry_: _ErrorEntry) -> bool:
        if self._isInvalid:
            return False
        if self._isInLcCeaseMode:
            return False

        _bOwnErr  = errEntry_.IsMyTaskError(self.taskID)
        _teKind   = _FwTDbEngine.GetText(_EFwTextID.eMisc_TE) if _bOwnErr else _FwTDbEngine.GetText(_EFwTextID.eMisc_FTE)
        _tailPart = '{}[{}:{}]:\n\t{}'.format(_teKind, errEntry_.uniqueID, errEntry_.eErrorImpact.compactName, errEntry_.shortMessage)

        if not self.isRunning:
            return False

        if self.taskBadge.isAutoEnclosed:
            if _FwThread.__bPRINT_WNG_UPON_TENOTIF_OF_AUTO_ENCLOSED_THREADS:
                if errEntry_.isFatalError:
                    _wngMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwThread_TextID_002).format(self.taskName, errEntry_.uniqueID, errEntry_.shortMessage)
                else:
                    _wngMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwThread_TextID_001).format(self.taskName, errEntry_.uniqueID, errEntry_.shortMessage)
                logif._LogWarning(_wngMsg)

            errEntry_._UpdateErrorImpact(eErrImpact_=_EErrorImpact.eNoImpactByAutoEnclosedThreadOwnership)
            return True

        res = self._AddEuError(errEntry_)
        return res

    def _CreateCeaseTLB(self, bAborting_ =False) -> _LcCeaseTLB:
        if self._isInvalid or not self.__isCeaseCapable:
            res = None
        else:
            res = _AbstractTask.CreateLcCeaseTLB(self, self.__mtxData, bAborting_)
        return res

    def _CheckSetTaskState(self, eNewState_ : _TaskState._EState) -> _TaskState._EState:
        res = self.taskStateID

        if res is None:
            return None

        with self._tstMutex:
            if eNewState_.isFailed:
                if not (res._isFailedByApiExecutionReturn or eNewState_._isFailedByApiExecutionReturn):
                    if self.__hasExecutionApiFunctionReturnedAbort:
                        _tstate = _TaskState._EState.eFailedByApiExecReturn
                        eNewState_ = _tstate

            if eNewState_ == res:
                pass
            else:
                _xtc      = None if self.__LinkedXTaskRefs is None else self.__LinkedXTaskRefs.xtaskConn
                _lcCompID = self._GetLcCompID()

                if _xtc is None:
                    pass
                else:
                    if eNewState_._isFailedByApiExecutionReturn:
                        self._CheckNotifyLcFailure()
                res = _AbstractTask._SetGetTaskState(self, eNewState_)

                if res != eNewState_:
                    vlogif._LogOEC(True, -1268)

                elif _xtc is None:
                    pass
                else:
                    _xtc._UpdateXD(self._tskState)

                    if eNewState_.isTerminated:
                        if eNewState_.isFailed:
                            pass
                        elif _lcCompID.isMainXtask:
                            if not self._lcProxy.isMainXTaskStopped:
                                self._lcProxy._SetLcOperationalState(_lcCompID, False, atask_=self)
            return res

    def _CheckNotifyLcFailure(self) -> bool:
        if self._isInvalid:
            return False

        _eMyLcCompID = self._GetLcCompID()

        if self._lcProxy.HasLcCompFRC(_eMyLcCompID, self):
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
                _bFlagSet = self.__hasExecutionApiFunctionReturnedAbort
                if _bFlagSet:
                    _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Shared_TextID_002).format(self.__logPrefixCtr)
                else:
                    _midPart = _FwTDbEngine.GetText(_EFwTextID.eMisc_XTask) if self.isDrivingXTask else _FwTDbEngine.GetText(_EFwTextID.eMisc_Thread)
                    _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Shared_TextID_001).format(self.__logPrefixCtr, _midPart)

                _frc = logif._CreateLogFatal(_errMsg, bDueToExecApiAboort_=_bFlagSet)
                _myMtx = None if _frc is None else _frc._LockInstance()

        if _frc is not None:
            _frcClone = _frc.Clone()
            if _frcClone is None:
                vlogif._LogOEC(True, -1269)
            else:
                res = True
                self._lcProxy._NotifyLcFailure(_eMyLcCompID, _frcClone, atask_=self)

                _frc._UpdateErrorImpact(_EErrorImpact.eNoImpactByFrcLinkage)

            if _myMtx is not None:
                _myMtx.Give()
        return res


    @property
    def __isCeaseCapable(self):
        return (self.lcDynamicTLB is not None) and not self.lcDynamicTLB.isDummyTLB

    @property
    def __isInLcCeaseMode(self):
        return not self.__eLcCeaseState.isNone

    @property
    def __hasExecutionApiFunctionReturnedAbort(self):
        return (self.__ag is not None) and (self.__ag._eExecutionApiFunctionReturn is not None) and self.__ag._eExecutionApiFunctionReturn.isAbort

    @property
    def __logPrefix(self):
        res  = _FwTDbEngine.GetText(_EFwTextID.eMisc_LogPrefix_Thread)
        res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_010).format(self.taskUniqueName)
        return res

    @property
    def __logPrefixCtr(self):
        res  = _FwTDbEngine.GetText(_EFwTextID.eMisc_LogPrefix_Thread)
        res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_010).format(self.taskUniqueName)
        res += _FwTDbEngine.GetText(_EFwTextID.eMisc_LogPrefix_ExecCounter).format(self.euRNumber)
        return res

    @property
    def __startStopSem(self):
        if self._isInvalid:
            return None
        with self._tstMutex:
            return self.__semSS

    @property
    def __eLcCeaseState(self) -> _ELcCeaseTLBState:
        if self._isInvalid:
            res = _ELcCeaseTLBState.eNone
        else:
            res = self.eLcCeaseTLBState
        return res

    @staticmethod
    def __GetExcludedXTaskApiMask(xtsk_ : XTask) -> _EXTaskApiFuncTag:
        res = _EXTaskApiFuncTag.DefaultApiMask()

        if not xtsk_.xtaskProfile.isSetupPhaseEnabled:
            res = _EXTaskApiFuncTag.AddApiFuncTag(eApiMask_=res, eApiFuncTag_=_EXTaskApiFuncTag.eXFTSetUpXTask)

        if not xtsk_.xtaskProfile.isTeardownPhaseEnabled:
            res = _EXTaskApiFuncTag.AddApiFuncTag(eApiMask_=res, eApiFuncTag_= _EXTaskApiFuncTag.eXFTTearDownXTask)
        return res

    def __UpdateCeaseTLB(self, bAborting_ : bool):
        _ctlb = self._lcCeaseTLB
        if _ctlb is None:
            pass
        else:
            _ctlb.UpdateCeaseState(bAborting_)

    def __RunThrdTgtCallback(self):
        _bError = False
        if not self.isStarted:
            _bError = True
            vlogif._LogOEC(True, -1270)
        elif self.isEnclosingPyThread:
            _bError = True
            vlogif._LogOEC(True, -1271)
        elif self.__startStopSem is None:
            _bError = True
            vlogif._LogOEC(True, -1272)

        if _bError:
            pass
        else:
            with self.__mtxData:
                _tuid          = self.taskBadge.threadUID
                _tnid          = self.taskBadge.threadNID
                _bNIDSupported = _TaskUtil.IsNativeThreadIdSupported()

                if (_tuid is None) or ((_tnid is None) and _bNIDSupported):
                    if _tuid is None:
                        _tuid = _TaskUtil.GetPyThreadUniqueID(self.linkedPyThread)
                    if (_tnid is None) and _bNIDSupported:
                        _tnid = self.linkedPyThread.native_id
                    self.taskBadge._UpdateRuntimeIDs(threadUID_=_tuid, threadNID_=_tnid)

            self._CheckSetTaskState(_TaskState._EState.eRunning)

            _myArgs    = None
            _myKwargs  = None
            _myThrdTgt = None
            _bDrivingXtbl = self.isDrivingExecutable
            if not _bDrivingXtbl:
                _myArgs, _myKwargs = self.threadProfile.args, self.threadProfile.kwargs
                _myThrdTgt = self.threadProfile.threadTarget
            else:
                _AbstractTask.CreateLcTLB(self)

            with self._tstMutex:
                _semSS = self.__semSS
                self.__semSS = None

            _semSS.Give()

            if not _bDrivingXtbl:
                self._SetTaskExecPhase(_ETaskExecutionPhaseID.eRunningNonDrivingExecutableASyncThread)
                _myThrdTgt(*_myArgs, **_myKwargs)

                if not (self.isDone or self.isFailed):
                    if self.isAborting:
                        self._CheckSetTaskState(_TaskState._EState.eFailed)
                    else:
                        self._CheckSetTaskState(_TaskState._EState.eDone)
            else:
                self._SetTaskExecPhase(_ETaskExecutionPhaseID.eFwHandling)
                self.__ExecuteXTask()

            _srg = _SyncResourcesGuard._GetInstance()
            if _srg is not None:
                _srg.ReleaseAcquiredSyncResources(self.taskID)

    def __StartPyThread(self):

        self._CheckSetTaskState(_TaskState._EState.eRunning)

        if not self.isDrivingExecutable:
            self._SetTaskExecPhase(_ETaskExecutionPhaseID.eRunningNonDrivingExecutableSyncThread)
        else:
            _AbstractTask.CreateLcTLB(self)

            self._SetTaskExecPhase( _ETaskExecutionPhaseID.eFwHandling)
            self.__ExecuteXTask()

    def __ExecuteXTask(self):


        _caughtXcp = True

        try:
            self.__ExecuteSetupXTask()

            if self.isRunning:
                self.__ExecuteRunXTask()
                if not self.isAborting:
                    if not self.__isInLcCeaseMode:
                        if not (self.__isCeaseCapable and self.lcDynamicTLB.isLcShutdownEnabled):
                            if self.__ag.isProvidingTearDownXTask:
                                self.__ExecuteTeardownXTask()

        except _XcoExceptionRoot as xcp:
            _caughtXcp = True
            self.__HandleException(xcp, bCaughtByApiExecutor_=False)

        except BaseException as xcp:
            _caughtXcp = True
            xcp = _XcoBaseException(xcp, tb_=logif._GetFormattedTraceback())
            self.__HandleException(xcp, bCaughtByApiExecutor_=False)


        finally:
            if self._isInvalid:
                vlogif._LogOEC(True, -1273)
                return

            if not self.isTerminating:
                if _caughtXcp:
                    st = _TaskState._EState.eProcessingAborted
                else:
                    st = _TaskState._EState.eProcessingStopped
                self._CheckSetTaskState(st)

            _semStop = None
            with self._tstMutex:
                if self.__semSS is not None:
                    _semStop = self.__semSS
                    self.__semSS = None

            if _semStop is not None:
                _semStop.Give()

            self.__PreProcessCeaseMode()

            self.__ProcessCeaseMode()

            if self._isInvalid:
                vlogif._LogOEC(True, -1274)
            else:
                if self.isAborting:
                    self._CheckSetTaskState(_TaskState._EState.eFailed)
                else:
                    self._CheckSetTaskState(_TaskState._EState.eDone)

    def __ExecuteSetupXTask(self):
        _xres = _ETernaryOpResult.Continue()

        if not self.__ag.isProvidingSetUpXTask:
            pass
        else:
            _xtor = self.__executors._GetApiExecutor(_EXTaskApiFuncTag.eXFTSetUpXTask)
            _xres = self.__EvaluateExecResult(executor_=_xtor, bCheckBefore_=False, eAbortState_=_TaskState._EState.eSetupAborted)
        return _xres

    def __ExecuteTeardownXTask(self):
        _xres = _ETernaryOpResult.Continue()

        if not self.__ag.isProvidingTearDownXTask:
            pass
        else:
            _xtor = self.__executors._GetApiExecutor(_EXTaskApiFuncTag.eXFTTearDownXTask)
            _xres = self.__EvaluateExecResult(executor_=_xtor, bCheckBefore_=False, eAbortState_=_TaskState._EState.eTeardownAborted)
        return _xres

    def __ExecuteRunXTask(self):

        _MM_FMT_STR = None

        _xres       = _ETernaryOpResult.Continue()
        _runCycleMS = self.executionProfile.runPhaseFreqMS

        while True:
            if not _xres.isContinue:
                break

            try:
                if self._isInvalid is None:
                    return _ETernaryOpResult.Abort()
                self._IncEuRNumber()

                _xtor = self.__executors._GetApiExecutor(_EXTaskApiFuncTag.eXFTRunXTask)
                _xres = self.__EvaluateExecResult(executor_=_xtor, bCheckBefore_=True)
                if not _xres.isContinue:
                    break

                elif not self.isRunning:
                    _xres = self.__EvaluateExecResult(executor_=_xtor, execRes_=None if self.isAborting else False, bCheckBefore_=None)

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
                        self._CheckSetTaskState(_TaskState._EState.eProcessingStopped)
                    break

                _TaskUtil.SleepMS(_runCycleMS)

            continue

        return _xres

    def __EvaluateExecResult( self
                            , executor_
                            , execRes_      : _ETernaryOpResult  =None
                            , bCheckBefore_ : bool               =None
                            , eAbortState_  : _TaskState._EState =None) -> _ETernaryOpResult:
        if not isinstance(executor_, _XTaskApiExecutor):
            self.__ag._SetGetExecutionApiFunctionReturn(None, bApplyConvertBefore_=False)
            vlogif._LogOEC(True, -1275)
            return _ETernaryOpResult.Abort()
        if not ((execRes_ is None) or isinstance(execRes_, _ETernaryOpResult)):
            self.__ag._SetGetExecutionApiFunctionReturn(None, bApplyConvertBefore_=False)
            vlogif._LogOEC(True, -1276)
            return _ETernaryOpResult.Abort()

        _bDoCheckAfter  = False
        _bDoCheckBefore = False

        if bCheckBefore_ is not None:
            _bDoCheckBefore = bCheckBefore_
            _bDoCheckAfter  = not _bDoCheckBefore

        res = _ETernaryOpResult.Continue()

        self.__ag._SetGetExecutionApiFunctionReturn(execRes_, bApplyConvertBefore_=False)

        if _bDoCheckBefore and self._isMonitoringLcModeChange:
            eNewLcOpModeID = self._CheckLcOperationModeChange()
            if (eNewLcOpModeID is not None) and not eNewLcOpModeID.isLcNormal:
                if eNewLcOpModeID.isLcCeaseMode:
                    res = self._OnLcCeaseModeDetected()
                elif eNewLcOpModeID.isLcFailureHandling:
                    res = self._OnLcFailureDetected()
                elif eNewLcOpModeID.isLcPreShutdown:
                    res = self._OnLcPreShutdownDetected()
                elif eNewLcOpModeID.isLcShutdown:
                    res = self._OnLcShutdownDetected()

        if res.isContinue:
            if execRes_ is not None:
                res = _ETernaryOpResult.ConvertFrom(execRes_)
            else:
                res = executor_.Execute()

            if res.isContinue:
                if _bDoCheckAfter and self._isMonitoringLcModeChange:
                    eNewLcOpModeID = self._CheckLcOperationModeChange()
                    if (eNewLcOpModeID is not None) and not eNewLcOpModeID.isLcNormal:
                        if eNewLcOpModeID.isLcCeaseMode:
                            res = self._OnLcCeaseModeDetected()
                        elif eNewLcOpModeID.isLcFailureHandling:
                            res = self._OnLcFailureDetected()
                        elif eNewLcOpModeID.isLcPreShutdown:
                            res = self._OnLcPreShutdownDetected()
                        elif eNewLcOpModeID.isLcShutdown:
                            res = self._OnLcShutdownDetected()

        if not res.isContinue:
            pass
        elif not self.isAborting:
            res = self._ProcEuErrors()

        if not res.isContinue:
            if not self.isTerminating:
                if eAbortState_ is None:
                    eAbortState_ = _TaskState._EState.eProcessingAborted

                if res.isAbort:
                    self._CheckSetTaskState(eAbortState_)
                else:
                    self._CheckSetTaskState(_TaskState._EState.eProcessingStopped)
        return res

    def __HandleException(self, xcp_ : _XcoExceptionRoot, bCaughtByApiExecutor_ =True) -> _ETernaryOpResult:

        if self._isInvalid:
            return _ETernaryOpResult.Abort()

        with self.__mtxData:

            xcoXcp     = None if xcp_.isXTaskException else xcp_
            xbx = None if (xcoXcp is None) or not isinstance(xcoXcp, _XcoBaseException) else xcoXcp

            if xbx is not None:
                if xcp_.eExceptionType.isBaseExceptionAtrributeError:
                    _xmlrMsg = _FwThread.__XML_RUNNER_XCP_MSG_DuplicateWriter

                    if xcp_.shortMessage == _xmlrMsg:
                        return _ETernaryOpResult.MapExecutionState2TernaryOpResult(self)

            if self.isAborting:
                pass
            elif xbx is not None:
                self._ProcUnhandledXcp(xbx)

            self._SetTaskExecPhase(_ETaskExecutionPhaseID.eFwHandling)

            if not self.isAborting:
                if not bCaughtByApiExecutor_:
                    eProcRes = self._ProcEuErrors()

                    if not eProcRes.isContinue:
                        nst = _TaskState._EState.eProcessingStopped if eProcRes.isStop else _TaskState._EState.eProcessingAborted
                        self._CheckSetTaskState(nst)

            if not self.isRunning:
                res = _ETernaryOpResult.Abort() if self.isAborting else _ETernaryOpResult.Stop()

            else:
                res = _ETernaryOpResult.Continue()
            return res

    def __GetProcessingFeasiblity(self, errEntry_: _ErrorEntry =None) -> _EProcessingFeasibilityID:

        res = _EProcessingFeasibilityID.eFeasible

        if self._isInvalid:
            res = _EProcessingFeasibilityID.eUnfeasible
        elif not self._lcProxy.isLcProxyAvailable:
            res = _EProcessingFeasibilityID.eLcProxyUnavailable
        elif not self._lcProxy.isLcCoreOperable:
            res = _EProcessingFeasibilityID.eLcCoreInoperable
        elif self.isAborting:
            res = _EProcessingFeasibilityID.eAborting

        _frcv = None
        if res.isFeasible:
            if self._lcProxy.hasLcAnyFailureState:
                _frcv = self._lcProxy.GetLcCompFrcView(self._GetLcCompID(), atask_=self)
                if _frcv is not None:
                    res = _EProcessingFeasibilityID.eOwnLcCompFailureSet

            if res.isFeasible:
                if (errEntry_ is not None) and errEntry_.hasNoErrorImpact:
                    res = _EProcessingFeasibilityID.eUnfeasible

        if not res.isFeasible:
            if errEntry_ is not None:
                _bOwnErr   = errEntry_.IsMyTaskError(self.taskID)

                _teKind   = _FwTDbEngine.GetText(_EFwTextID.eMisc_TE) if _bOwnErr else _FwTDbEngine.GetText(_EFwTextID.eMisc_FTE)
                _tailPart = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Shared_TextID_003).format(_teKind, errEntry_.uniqueID, errEntry_.eErrorImpact.compactName, errEntry_.shortMessage)

                if _bOwnErr:
                    errEntry_._UpdateErrorImpact(_EErrorImpact.eNoImpactByOwnerCondition)
            else:
                _tailPart = _CommonDefines._CHAR_SIGN_DOT

            _midPart = res.compactName
            if res.isOwnLcCompFailureSet:
                _midPart += _CommonDefines._CHAR_SIGN_COLON + _frcv.ToString(bVerbose_=False)

        if _frcv is not None:
            _frcv.CleanUp()
        return res

    def __CreateExecutorTable(self):

        _dictExecutors = dict()
        for name, member in _EXTaskApiFuncTag.__members__.items():
            if not member.isXTaskExecutionAPI:
                continue
            if not self.__ag._IsProvidingApiFunction(eApiFuncTag_=member):
                continue
            _dictExecutors[member] = _XTaskApiExecutor(self.__ag, member, self.__HandleException)

        self.__executors = _FwThread._XTaskExecutorTable(_dictExecutors)

    def __EvaluateCtorParams( self
                            , thrdProfile_                : _ThreadProfile  =None
                            , xtaskConn_                  : _XTaskConnector =None
                            , taskName_                   : str             =None
                            , enclosedPyThread_           : _PyThread       =None
                            , bAutoStartEnclosedPyThread_ : bool            =None
                            , threadTargetCallableIF_     : _CallableIF     =None
                            , args_                       : list            =None
                            , kwargs_                     : dict            =None
                            , threadProfileAttrs_         : dict            =None):
        _ts    = None
        _mytp  = thrdProfile_
        _valid = True

        if _mytp is None:
            _mytp = _ThreadProfile( xtaskConn_=xtaskConn_
                                , taskName_=taskName_
                                , enclosedPyThread_=enclosedPyThread_
                                , bAutoStartEnclosedPyThread_=bAutoStartEnclosedPyThread_
                                , threadTargetCallableIF_=threadTargetCallableIF_
                                , args_=args_
                                , kwargs_=kwargs_
                                , threadProfileAttrs_=threadProfileAttrs_)
        if not isinstance(_mytp, _ThreadProfile):
            _valid = False
            vlogif._LogOEC(True, -1277)
        elif not (_mytp.isValid and _mytp.taskRightsMask is not None):
            _valid = False
            vlogif._LogOEC(True, -1278)
        elif _mytp.isEnclosingPyThread and not _mytp.enclosedPyThread.is_alive():
            _valid = False
            vlogif._LogOEC(True, -1279)

        if not _valid:
            if (_mytp is not None) and thrdProfile_ is None:
                _mytp.CleanUp()
            _ts, _mytp = None, None
        else:
            _ts = _TaskState(self, _TaskState._EState.eInitialized, mtx_=self._tstMutex)
        return _ts, _mytp

    def __CleanUpOnCtorFailure (self
                              , tskError_          =None
                              , terrCallableIF_    =None
                              , tskBadge_          =None
                              , linkedXTaskRefs_ =None
                              , thrdProfile_       =None
                              , mtxApi_            =None
                              , mtxData_           =None):
        if tskError_          is not None: tskError_.CleanUp()
        if terrCallableIF_    is not None: terrCallableIF_.CleanUp()
        if tskBadge_          is not None: tskBadge_.CleanUp()
        if linkedXTaskRefs_ is not None: linkedXTaskRefs_.CleanUp()
        if thrdProfile_       is not None: thrdProfile_.CleanUp()
        if mtxApi_            is not None: mtxApi_.CleanUp()
        if mtxData_           is not None: mtxData_.CleanUp()

        self.__semSS             = None
        self.__mtxApi            = None
        self.__mtxData           = None
        self.__thrdProfile       = None
        self.__bAutocreatedTP    = None
        self.__LinkedXTaskRefs = None

        super()._CleanUp()
        self.CleanUp()

    def __PreProcessCeaseMode(self):
        if self._isInvalid:
            return

        _bCreateCeaseTLB = self.lcDynamicTLB.isLcShutdownEnabled

        if self._CheckNotifyLcFailure():
            _bCreateCeaseTLB = True

        if not self.__isInLcCeaseMode:
            if self.__isCeaseCapable:
                if _bCreateCeaseTLB:
                    self._CreateCeaseTLB(bAborting_=self.isAborting)

    def __ProcessCeaseMode(self):
        if self._isInvalid:
            return

        if not self.__isInLcCeaseMode:
            return

        _eCurCS = self.__eLcCeaseState

        _midPart = 'aborting ' if _eCurCS.isDeceased else ''

        if _eCurCS.isPrepareCeasing:
            self.__PrepareDefaultCeasing()

            _eCurCS = self.__eLcCeaseState

        if _eCurCS.isEnterCeasing:
            self.__EnterDefaultCeasing()

            _eCurCS = self.__eLcCeaseState

        if _eCurCS.isAbortingCease:
            self.__ProcessLeavingCease()

            _eCurCS = self.__eLcCeaseState

        if not _eCurCS.isDeceased:
            vlogif._LogOEC(True, -1280)

    def __PrepareDefaultCeasing(self):
        if not self.__isInLcCeaseMode:
            return

        _eCurCS = self.__eLcCeaseState
        if not _eCurCS.isPrepareCeasing:
            vlogif._LogOEC(True, -1281)
            self._lcCeaseTLB.UpdateCeaseState(True)
            return

        if self._lcCeaseTLB.isLcShutdownEnabled:
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

        self._lcCeaseTLB.HopToNextCeaseState(bAborting_=self.isAborting)

    def __EnterDefaultCeasing(self):
        if not self.__isInLcCeaseMode:
            return

        _eCurCS = self.__eLcCeaseState
        if not _eCurCS.isEnterCeasing:
            vlogif._LogOEC(True, -1282)
            self._lcCeaseTLB.UpdateCeaseState(True)
            return

        self._lcCeaseTLB.HopToNextCeaseState(bAborting_=self.isAborting)

        _bPreShutdownPassed = False
        while True:
            if not self._lcCeaseTLB.isCeasing:
                break

            self._lcCeaseTLB.IncrementCeaseAliveCounter()

            _TaskUtil.SleepMS(self.executionProfile.cyclicCeaseTimespanMS)

            if self._isInvalid:
                break

            if not self._lcCeaseTLB.isCeasing:
                self._lcCeaseTLB.UpdateCeaseState(True)
                break

            if not _bPreShutdownPassed:
                if self._lcCeaseTLB._isPreShutdownGateOpened:
                    _bPreShutdownPassed = True

                    self.__ExecuteTeardownXTask()

                    self._lcCeaseTLB.HopToNextCeaseState(bAborting_=self.isAborting)
                    continue

            if self._lcCeaseTLB._isShutdownGateOpened:
                break

        if self._lcCeaseTLB is not None:
            self._lcCeaseTLB.HopToNextCeaseState(bAborting_=self.isAborting)

    def __ProcessLeavingCease(self):
        if not self.__isInLcCeaseMode:
            return

        _eCurCS = self.__eLcCeaseState
        if not self._lcCeaseTLB.isAbortingCease:
            vlogif._LogOEC(True, -1283)

            if self._lcCeaseTLB.isDeceased:
                return

            self._lcCeaseTLB.UpdateCeaseState(True)

        while True:
            if (not self._lcCeaseTLB.isCoordinatedShutdownRunning) or self._lcCeaseTLB.isCoordinatedShutdownGateOpened:
                break

            self._lcCeaseTLB.IncrementCeaseAliveCounter()

            _TaskUtil.SleepMS(self.executionProfile.cyclicCeaseTimespanMS)

            if self._isInvalid:
                break

            _eCSR = self._lcCeaseTLB.eCurrentShutdownRequest
            if (_eCSR is None) or _eCSR.isShutdown:
                break
            continue

        if self._lcCeaseTLB is not None:
            self._lcCeaseTLB.HopToNextCeaseState(bAborting_=True)


class _XTaskApiExecutor(_AbstractSlotsObject):

    __slots__ = [ '__er' , '__apiG' , '__apiF' , '__eFID' , '__fwthrd' , '__teph' , '__xcpH' ]

    def __init__(self, apiGuide_  : _XTaskApiGuide, eFuncID_ : _EXTaskApiFuncTag, xcpHdlr_):
        super().__init__()
        self.__er     = None
        self.__apiF   = None
        self.__apiG   = apiGuide_
        self.__eFID   = eFuncID_
        self.__xcpH   = xcpHdlr_
        self.__teph   = None
        self.__fwthrd = None

        if not isinstance(eFuncID_, _EXTaskApiFuncTag):
            vlogif._LogOEC(True, -1284)
            self.CleanUp()
        elif xcpHdlr_ is None:
            vlogif._LogOEC(True, -1285)
            self.CleanUp()
        elif not isinstance(apiGuide_, _XTaskApiGuide):
            vlogif._LogOEC(True, -1286)
            self.CleanUp()
        elif not isinstance(apiGuide_._fwThread, _FwThread):
            vlogif._LogOEC(True, -1287)
            self.CleanUp()
        elif not eFuncID_.isXTaskExecutionAPI:
            vlogif._LogOEC(True, -1288)
            self.CleanUp()
        elif self.__SetApiFunc() is None:
            self.CleanUp()
        else:
            _tskExecPhaseID = eFuncID_.MapToTaskExecutionPhaseID()
            if _tskExecPhaseID.isNone:
                vlogif._LogOEC(True, -1289)
                self.CleanUp()
            else:
                self.__teph   = _tskExecPhaseID
                self.__fwthrd = apiGuide_._fwThread

    @property
    def executionResult(self) -> _ETernaryOpResult:
        return self.__er

    @property
    def eApiFunctID(self) -> _EXTaskApiFuncTag:
        return self.__eFID

    def Execute(self) -> _ETernaryOpResult:
        if self.__isInvalid:
            return _ETernaryOpResult.Abort()
        if self.__apiF is None:
            if self.__er is not None:
                self.__er = _ETernaryOpResult.Abort()
            vlogif._LogOEC(True, -1290)
            return _ETernaryOpResult.Abort()

        ret = None

        try:
            self.__fwthrd._SetTaskExecPhase(self.__eTaskExecPhase)

            ret = self.__apiF()
            ret = self.__apiG._SetGetExecutionApiFunctionReturn(ret)

            self.__fwthrd._SetTaskExecPhase(_ETaskExecutionPhaseID.eFwHandling)

            if ret.isAbort:
                self.__fwthrd._CheckSetTaskState(_TaskState._EState.eProcessingAborted)

                self.__fwthrd._CheckNotifyLcFailure()

        except _XcoExceptionRoot as xcp:
            ret = self.__xcpH(xcp_=xcp, bCaughtByApiExecutor_=True)

        except BaseException as xcp:
            xcp = _XcoBaseException(xcp, tb_=logif._GetFormattedTraceback())
            ret = self.__xcpH(xcp_=xcp, bCaughtByApiExecutor_=True)

        finally:
            _xres = _ETernaryOpResult.ConvertFrom(ret)
            self.__er = _xres

        return self.__er

    def _ToString(self, *args_, **kwargs_):
        if self.__isInvalid:
            return None
        return _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_002).format(type(self).__name__, self.__fwthrd.taskUniqueName, self.__eFID.functionName)

    def _CleanUp(self):
        self.__er     = None
        self.__apiF   = None
        self.__apiG   = None
        self.__eFID   = None
        self.__xcpH   = None
        self.__teph   = None
        self.__fwthrd = None

    @property
    def __isInvalid(self):
        return (self.__apiG is None) or (self.__eFID is None)

    @property
    def __logPrefix(self):
        if self.__isInvalid:
            return None

        res = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_003)
        return res.format(self.__fwthrd.taskUniqueName, self.__eFID.functionName)

    @property
    def __eTaskExecPhase(self) -> _ETaskExecutionPhaseID:
        return self.__teph

    def __SetApiFunc(self):
        if self.__isInvalid:
            return None

        res             = None
        _bUnexpectedErr = False

        if self.__eFID == _EXTaskApiFuncTag.eXFTRunXTask:
            res = self.__apiG.runXTask

        elif self.__eFID == _EXTaskApiFuncTag.eXFTSetUpXTask:
            res = self.__apiG.setUpXTask

        elif self.__eFID == _EXTaskApiFuncTag.eXFTTearDownXTask:
            res = self.__apiG.tearDownXTask

        else:
            _bUnexpectedErr = True
            vlogif._LogOEC(True, -1291)

        if res is None:
            if not _bUnexpectedErr:
                vlogif._LogOEC(True, -1292)
        else:
            self.__apiF = res
        return res
