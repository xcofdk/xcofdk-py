# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwtask.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from xcofdk._xcofw.fw.fwssys.fwcore.apiimpl.xtask.xtaskconn import _XTaskConnector

from xcofdk._xcofw.fw.fwssys.fwcore.logging               import logif
from xcofdk._xcofw.fw.fwssys.fwcore.logging               import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.logging.xcoexception  import _XcoExceptionRoot
from xcofdk._xcofw.fw.fwssys.fwcore.base.timeutil         import _TimeAlert
from xcofdk._xcofw.fw.fwssys.fwcore.base.callableif       import _CallableIF
from xcofdk._xcofw.fw.fwssys.fwcore.base.gtimeout         import _Timeout
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.err.euerrhandler  import _EuErrorHandler
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.arunnable     import _AbstractRunnable
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.sync.semaphore    import _BinarySemaphore
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.sync.mutex        import _Mutex
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.sync.syncresguard import _SyncResourcesGuard
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcdefines          import _ELcCompID
from xcofdk._xcofw.fw.fwssys.fwcore.lcmon.lcmontlb        import _LcCeaseTLB
from xcofdk._xcofw.fw.fwssys.fwcore.types.aprofile        import _AbstractProfile

from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.atask       import _AbstractTask
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.execprofile import _ExecutionProfile
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.ataskop     import _EATaskOperationID
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.ataskop     import _ATaskOperationPreCheck
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskbadge   import _TaskBadge
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskerror   import _TaskError
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskerror   import _TaskErrorExtended
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskprofile import _TaskProfile
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskstate   import _TaskState
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil    import _PyThread
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil    import _TaskUtil
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil    import _ETaskType
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil    import _EFwApiBookmarkID
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil    import _ETaskResourceFlag
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil    import _ETaskExecutionPhaseID

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine



class _FwTask(_AbstractTask):

    __bERROR_HANDLING_ENABLED = False

    __slots__ = [ '__mtxApi' , '__mtxData' , '__tskProfile' , '__rbl' , '__semSS' , '__bAutocreatedTP' ]

    def __init__( self
                , taskPrf_                    : _TaskProfile       =None
                , runnable_                   : _AbstractRunnable  =None
                , taskName_                   : str                =None
                , resourcesMask_              : _ETaskResourceFlag =None
                , delayedStartTimeSpanMS_     : int                =None
                , enclosedPyThread_           : _PyThread          =None
                , bAutoStartEnclosedPyThread_ : bool               =None
                , bFwMain_                    : bool               =False
                , args_                       : list               =None
                , kwargs_                     : dict               =None
                , taskProfileAttrs_           : dict               =None):

        self.__rbl            = None
        self.__semSS          = None
        self.__mtxApi         = None
        self.__mtxData        = None
        self.__tskProfile     = None
        self.__bAutocreatedTP = None

        super().__init__()

        self.__mtxData = _Mutex()
        self._tstMutex = _Mutex()

        _ts = None
        _tp = None
        _ts, _tp = self.__EvaluateCtorParams( taskPrf_=taskPrf_
                                            , runnable_=runnable_
                                            , taskName_=taskName_
                                            , resourcesMask_=resourcesMask_
                                            , delayedStartTimeSpanMS_=delayedStartTimeSpanMS_
                                            , enclosedPyThread_=enclosedPyThread_
                                            , bAutoStartEnclosedPyThread_=bAutoStartEnclosedPyThread_
                                            , args_=args_, kwargs_=kwargs_
                                            , taskProfileAttrs_=taskProfileAttrs_)

        if _ts is None:
            self.__CleanUpOnCtorFailure(mtxData_=self.__mtxData)
            return

        _rbl = _tp.runnable
        if bFwMain_:
            _tt = _ETaskType.eFwMainTask
        elif not _rbl.isXTaskRunnable:
            _tt = _ETaskType.eFwTask
        else:
            _tt = _ETaskType.eMainXTaskTask if _rbl.isMainXTaskRunnable else _ETaskType.eXTaskTask

        _tid   = _TaskUtil.GetNextTaskID(_tp.taskRightsMask.hasUserTaskRight, _tp.isEnclosingStartupThread)
        _tname = None

        _bUSE_AUTO_GENERATED_TASK_NAMES_ONLY = True
        if not _bUSE_AUTO_GENERATED_TASK_NAMES_ONLY:
            _tname = _tp.taskName
        if _tname is None:
            _txtID = _EFwTextID.eMisc_TaskNamePrefix_XTask if _tt.isXTaskTask else _EFwTextID.eMisc_TaskNamePrefix_Task
            _tname = f'{_FwTDbEngine.GetText(_txtID)}{_tid}'

        _tp.Freeze(*(_tid, _tname))
        if not _tp.isFrozen:
            _tp = _tp if taskPrf_ is None else None
            self.__CleanUpOnCtorFailure(mtxData_=self.__mtxData, tskProfile_=_tp)
            return

        _thrdNID = None
        if _tp.isEnclosingPyThread:
            _myThrd = _tp.enclosedPyThread
            if _TaskUtil.IsNativeThreadIdSupported():
                _thrdNID = _myThrd.native_id
        else:
            _myThrd = _PyThread(group=None, target=self._RunThread, name=_tname, args=(), kwargs={}, daemon=None)

        _bExtQueueSupport = _tp.isExternalQueueEnabled or _rbl._isSelfManagingExternalQueue
        _bIntQueueSupport = _tp.isInternalQueueEnabled or _rbl._isSelfManagingInternalQueue

        _myTskBadge = _TaskBadge( taskName_=_tname, taskID_=_tid, threadUID_=_TaskUtil.GetPyThreadUniqueID(_myThrd)
                                , taskType_=_tt, trMask_=_tp.taskRightsMask, threadNID_=_thrdNID
                                , bEnclosingPyThrd_=_tp.isEnclosingPyThread, bEnclosingStartupThrd_=_tp.isEnclosingStartupThread
                                , bExtQueueSupport_=_bExtQueueSupport, bIntQueueSupport_=_bIntQueueSupport)
        if _myTskBadge.taskID is None:
            _tp = _tp if taskPrf_ is None else None
            self.__CleanUpOnCtorFailure(mtxData_=self.__mtxData, tskProfile_=_tp, tskBadge_=_myTskBadge)
            return

        _tecbif = _CallableIF(_rbl._OnTENotification)
        if not _tecbif.isValid:
            _tp = _tp if taskPrf_ is None else None
            self.__CleanUpOnCtorFailure(mtxData_=self.__mtxData, tskProfile_=_tp, tskBadge_=_myTskBadge, terrCallableIF_=_tecbif)
            return

        _bFEL = _myTskBadge.hasForeignErrorListnerTaskRight

        if _bFEL:
            _tskErr = _TaskErrorExtended(self.__mtxData, _myTskBadge, taskErrorCallableIF_=_tecbif)
        else:
            _tskErr = _TaskError(self.__mtxData, _myTskBadge, taskErrorCallableIF_=_tecbif)

        if _tskErr.taskBadge is None:
            _tp = _tp if taskPrf_ is None else None
            self.__CleanUpOnCtorFailure( mtxData_=self.__mtxData, tskProfile_=_tp, tskBadge_=_myTskBadge
                                       , terrCallableIF_=_tecbif, tskError_=_tskErr)
            return

        _xtc = _rbl._xtaskConnector if _rbl._eRunnableType.isXTaskRunnable else None

        self._execConn     = _xtc
        self._tskBadge     = _myTskBadge
        self._tskError     = _tskErr
        self._tskState     = _ts
        self._linkedPyThrd = _myThrd

        self.__rbl            = _rbl
        self.__mtxApi         = _Mutex()
        self.__tskProfile     = _tp
        self.__bAutocreatedTP = taskPrf_ is None

        if _xtc is not None:
            if not _xtc._UpdateXD(_ts, tskBadge_=_myTskBadge, tskProfile_=_tp, linkedPyThrd_=_myThrd):
                self.CleanUp()
                return

        if _FwTask.__bERROR_HANDLING_ENABLED:
            _EuErrorHandler._SetUpEuEH(self, self.__mtxData)
            if self._isForeignErrorListener is None:
                self.CleanUp()
                return

        _rbl._SetDrivingTask(self)
        if _rbl._drivingTask is None:
            self.CleanUp()
            return
        if self.__tskProfile.isAutoStartEnclosedPyThreadEnabled:
            self.__StartPyThread()

    @property
    def hasTimerResource(self):
        return None if self.__tskProfile is None else self.__tskProfile.hasTimerResource

    @property
    def taskProfile(self):
        return self.__tskProfile

    @staticmethod
    def _CreateTask( taskPrf_                 : _TaskProfile       =None
                    , runnable_               : _AbstractRunnable  =None
                    , taskName_               : str                =None
                    , resourcesMask_          : _ETaskResourceFlag =None
                    , delayedStartTimeSpanMS_ : int                =None
                    , args_                   : list               =None
                    , kwargs_                 : dict               =None
                    , taskProfileAttrs_       : dict               =None ):

        if taskPrf_ is not None:
            if (not taskPrf_.isValid) or taskPrf_.isEnclosingPyThread:
                vlogif._LogOEC(False, -3009)
                return None
        elif taskProfileAttrs_ is not None:
            if _TaskProfile._ATTR_KEY_ENCLOSED_PYTHREAD in taskProfileAttrs_:
                vlogif._LogOEC(False, -3010)
                return None

        res = _FwTask( taskPrf_=taskPrf_
                     , runnable_=runnable_
                     , taskName_=taskName_
                     , resourcesMask_=resourcesMask_
                     , delayedStartTimeSpanMS_=delayedStartTimeSpanMS_
                     , enclosedPyThread_=None
                     , bAutoStartEnclosedPyThread_=None
                     , args_=args_
                     , kwargs_=kwargs_
                     , taskProfileAttrs_=taskProfileAttrs_)
        if res.taskBadge is None:
            res.CleanUp()
            res = None
        return res

    @staticmethod
    def _CreateEnclosingTask( taskPrf_                    : _TaskProfile       =None
                            , runnable_                   : _AbstractRunnable  =None
                            , resourcesMask_              : _ETaskResourceFlag =None
                            , enclosedPyThread_           : _PyThread          =None
                            , bAutoStartEnclosedPyThread_ : bool               =None
                            , args_                       : list               =None
                            , kwargs_                     : dict               =None
                            , taskProfileAttrs_           : dict               =None ):

        if taskPrf_ is not None:
            if not (taskPrf_.isValid and taskPrf_.isEnclosingPyThread):
                vlogif._LogOEC(False, -3011)
                return None
        elif taskProfileAttrs_ is not None:
            if enclosedPyThread_ is None:
                if not _AbstractProfile._ATTR_KEY_ENCLOSED_PYTHREAD in taskProfileAttrs_:
                    vlogif._LogOEC(False, -3012)
                    return None

        res = _FwTask( taskPrf_=taskPrf_
                     , runnable_=runnable_
                     , taskName_=None
                     , resourcesMask_=resourcesMask_
                     , delayedStartTimeSpanMS_=None
                     , enclosedPyThread_=enclosedPyThread_
                     , bAutoStartEnclosedPyThread_=bAutoStartEnclosedPyThread_
                     , args_=args_
                     , kwargs_=kwargs_
                     , taskProfileAttrs_=taskProfileAttrs_)
        if res.taskBadge is None:
            res.CleanUp()
            res = None
        return res


    @property
    def _isInvalid(self) -> bool:
        return self.__mtxData is None

    @property
    def _isAutoStartEnclosedPyThreadEnabled(self) -> bool:
        return False if self.__tskProfile is None else self.__tskProfile.isAutoStartEnclosedPyThreadEnabled

    @property
    def _linkedExecutable(self):
        return self.__rbl

    @property
    def _xtaskConnector(self) -> _XTaskConnector:
        return None if self.__rbl is None else self.__rbl._xtaskConnector

    @property
    def _abstractTaskProfile(self) -> _AbstractProfile:
        return self.taskProfile

    @property
    def _executionProfile(self) -> _ExecutionProfile:
        return None if self.__rbl is None else self.__rbl.executionProfile

    @property
    def _euRNumber(self) -> int:
        if self._isInvalid or (self.__rbl is None):
            return None
        elif self.isFwMain:
            with self.__mtxData:
                return self._euRNum
        else:
            return self._euRNum

    @property
    def _eTaskExecPhase(self) -> _ETaskExecutionPhaseID:
        if self._isInvalid:
            return _ETaskExecutionPhaseID.eNone
        with self.__mtxData:
            return self._tskEPhase

    def _IncEuRNumber(self) -> int:
        if self._isInvalid or (self.__rbl is None):
            return 0
        elif self.isFwMain:
            with self.__mtxData:
                return _AbstractTask._IncEuRNumber(self)
        else:
            return _AbstractTask._IncEuRNumber(self)

    def _PropagateLcProxy(self):
        if self._isInvalid:
            return
        with self.__mtxData:
            if self._lcProxy is not None:
                self.__rbl._SetLcProxy(self._lcProxy)

    def _GetLcCompID(self) -> _ELcCompID:
        if self._isInvalid or (self.__rbl is None) or self.__rbl._isInvalid:
            return None
        return self.__rbl._eRunnableType.toLcCompID

    def _StartTask(self, semStart_ : _BinarySemaphore =None, tskOpPreCheck_ : _ATaskOperationPreCheck =None, curTask_ : _AbstractTask =None) -> bool:
        if self._isInvalid:
            return False
        if not self._lcProxy.isLcOperable:
            return False

        with self.__mtxApi:
            if self.isEnclosingPyThread:
                if semStart_ is not None:
                    vlogif._LogOEC(True, -1293)
                    return False
            elif not isinstance(semStart_, _BinarySemaphore):
                vlogif._LogOEC(True, -1294)
                return False

            _oppc = tskOpPreCheck_
            if _oppc is None:
                _oppc = _ATaskOperationPreCheck( _EATaskOperationID.eStart, self._tskState
                                              , self._linkedPyThrd, self.isEnclosingPyThread, reportErr_=True)
            else:
                _oppc.Update(eTaskOpID_=_EATaskOperationID.eStart, reportErr_=True)
            if _oppc.isNotApplicable or _oppc.isIgnorable:
                _bIgnorable = _oppc.isIgnorable
                if tskOpPreCheck_ is None:
                    _oppc.CleanUp()

                if _bIgnorable:
                    if semStart_ is not None:
                        semStart_.Give()
                return _bIgnorable

            elif tskOpPreCheck_ is None:
                _oppc.CleanUp()

            if not self.isEnclosingPyThread:
                with self._tstMutex:
                    self.__semSS = semStart_
                    self._CheckSetTaskState(_TaskState._EState.ePendingRun)

        res     = True
        _prvBid = None

        if self.isDrivingXTask:
            _prvBid = None if curTask_ is None else curTask_.eFwApiBookmarkID

        if self.isEnclosingPyThread:
            if _prvBid is not None:
                curTask_._SetFwApiBookmark(_EFwApiBookmarkID.eXTaskApiBeginActionStart)

            self.__StartPyThread()

            if _prvBid is not None:
                curTask_._SetFwApiBookmark(_prvBid)

            if self._isInvalid or (self.__rbl is None):
                res = False
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

        if not res:
            pass
        elif not self.isDone:
            if self.__rbl.isMainXTaskRunnable:
                if not self._lcProxy.hasLcAnyFailureState:
                    _lcCompID = self.__rbl._eRunnableType.toLcCompID
                    self._lcProxy._SetLcOperationalState(_lcCompID, True, atask_=self)
        return True

    def _RestartTask(self, semStart_ : _BinarySemaphore =None, tskOpPreCheck_ : _ATaskOperationPreCheck =None, curTask_ : _AbstractTask =None) -> bool:
        if self._isInvalid:
            return False
        vlogif._LogOEC(True, -1295)
        return False

    def _StopTask(self, semStop_ : _BinarySemaphore =None, tskOpPreCheck_ : _ATaskOperationPreCheck =None, curTask_ : _AbstractTask =None) -> bool:
        if self._isInvalid:
            return False

        with self.__mtxApi:
            if self.isEnclosingPyThread:
                if semStop_ is not None:
                    vlogif._LogOEC(True, -1296)
                    return False
            elif (semStop_ is not None) and not isinstance(semStop_, _BinarySemaphore):
                vlogif._LogOEC(True, -1297)
                return False
            elif self.__startStopSem is not None:
                vlogif._LogOEC(True, -1298)
                return False

            _oppc = tskOpPreCheck_
            if _oppc is None:
                _oppc = _ATaskOperationPreCheck( _EATaskOperationID.eStop, self._tskState
                                              , self._linkedPyThrd, self.isEnclosingPyThread, reportErr_=True)
            else:
                _oppc.Update(eTaskOpID_=_EATaskOperationID.eStop, reportErr_=True)
            if _oppc.isNotApplicable or _oppc.isIgnorable:
                _bIgnorable = _oppc.isIgnorable
                if tskOpPreCheck_ is None:
                    _oppc.CleanUp()

                if _bIgnorable:
                    if semStop_ is not None:
                        semStop_.Give()
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
            self.__rbl._SetStopSyncSem(semStop_)

            self._CheckSetTaskState(_TaskState._EState.ePendingStopRequest)
            self.__semSS = None

        with self.__mtxData:
            if _prvBid is not None:
                curTask_._SetFwApiBookmark(_prvBid)
        return True

    def _JoinTask(self, timeout_ : _Timeout =None, tskOpPreCheck_ : _ATaskOperationPreCheck =None, curTask_ : _AbstractTask =None) -> bool:
        if self._isInvalid or (self.linkedPyThread is None):
            return False
        if timeout_ is not None:
            if not _Timeout.IsTimeout(timeout_, bThrowx_=True):
                return False
            elif timeout_.isInfiniteTimeout:
                timeout_ = None

        _myLogPrefix = self.__logPrefix
        if (self.__rbl is None) or self.__rbl._isInvalid or not self.__rbl.isXTaskRunnable:
            _midPart = 'task ' + self.taskUniqueName
        else:
            _midPart = 'xtask ' + self.__rbl._xtaskInst.xtaskName

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

        if self.__resourceTimer is not None:
            try:
                self.__resourceTimer.Stop()
            except (BaseException, RuntimeError) as xcp:
                vlogif._LogOEC(False, -3013)

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
                vlogif._LogOEC(False, -3014)
            else:
                vlogif._LogOEC(False, -3015)
        return res


    def _ToString(self, *args_, **kwargs_):
        return _AbstractTask._ToString(self)

    def _CleanUp(self):

        if self._isInvalid:
            return

        if self.__rbl is not None:
            self.__rbl._SetDrivingTask(None)

        if self.__resourceTimer is not None:
            self.__resourceTimer.CleanUp()
        if self.__bAutocreatedTP:
            if self.__tskProfile is not None:
                self.__tskProfile.CleanUp()

        _tid           = self.taskID
        _bEnclPyThread = self.isEnclosingPyThread

        super()._CleanUp()

        if self.__mtxApi is not None:
            self.__mtxApi.CleanUp()
            self.__mtxApi = None

        self.__mtxData.CleanUp()
        self.__mtxData = None

        if _bEnclPyThread:
            _srg = _SyncResourcesGuard._GetInstance()
            if _srg is not None:
                _srg.ReleaseAcquiredSyncResources(_tid)

        self.__rbl            = None
        self.__semSS          = None
        self.__tskProfile     = None
        self.__bAutocreatedTP = None

    def _CheckSetTaskState(self, eNewState_ : _TaskState._EState) -> _TaskState._EState:

        res = self.taskStateID

        if res is None:
            return None

        with self._tstMutex:
            if eNewState_.isFailed:
                if not (res._isFailedByApiExecutionReturn or eNewState_._isFailedByApiExecutionReturn):
                    if self.__rbl._hasExecutionApiFunctionReturnedAbort:
                        _tstate = _TaskState._EState.eFailedByApiExecReturn
                        eNewState_ = _tstate

            if eNewState_ == res:
                pass
            else:
                _xtc      = self._execConn
                _lcCompID = self._GetLcCompID()

                if _xtc is None:
                    pass
                else:
                    if eNewState_._isFailedByApiExecutionReturn:
                        self.__rbl._CheckNotifyLcFailure()

                res = _AbstractTask._SetGetTaskState(self, eNewState_)

                if res != eNewState_:
                    vlogif._LogOEC(True, -1299)

                elif _xtc is None:
                    pass
                else:
                    _xtc._UpdateXD(self._tskState)

                    if eNewState_.isTerminated:
                        if eNewState_.isFailed:
                            pass
                        elif self.__rbl.isMainXTaskRunnable:
                            if not self._lcProxy.HasLcCompFRC(_lcCompID, self):
                                self._lcProxy._SetLcOperationalState(_lcCompID, False, atask_=self)
            return res

    def _CreateCeaseTLB(self, bAborting_ =False) -> _LcCeaseTLB:
        if self._isInvalid or (self.__rbl is None):
            res = None
        else:
            res = self.__rbl._CreateCeaseTLB(bAborting_=bAborting_)
        return res

    def _RunThread(self):
        if not self.isStarted:
            vlogif._LogOEC(True, -1300)
            return
        if self.isEnclosingPyThread:
            vlogif._LogOEC(True, -1301)
            return

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

            _AbstractTask.CreateLcTLB(self)

            with self._tstMutex:
                _semSS = self.__semSS
                self.__semSS = None

        self.__rbl._Run(_semSS, *self.taskProfile.args, **self.taskProfile.kwargs)

        if self.taskBadge is None:
            vlogif._LogOEC(True, -1302)
            return

        if self.isAborting:
            self._CheckSetTaskState(_TaskState._EState.eFailed)
        else:
            self._CheckSetTaskState(_TaskState._EState.eDone)

        _srg = _SyncResourcesGuard._GetInstance()
        if _srg is not None:
            _srg.ReleaseAcquiredSyncResources(self.taskID)


    @property
    def __logPrefix(self):
        res  = _FwTDbEngine.GetText(_EFwTextID.eMisc_LogPrefix_Task)
        res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_010).format(self.taskUniqueName)
        return res

    @property
    def __logPrefixCtr(self):
        res  = _FwTDbEngine.GetText(_EFwTextID.eMisc_LogPrefix_Task)
        res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_010).format(self.taskUniqueName)
        res += _FwTDbEngine.GetText(_EFwTextID.eMisc_LogPrefix_ExecCounter).format(self.euRNumber)
        return res

    @property
    def __resourceTimer(self):
        return None if self.__tskProfile is None else self.__tskProfile.timerResource

    @property
    def __startStopSem(self):
        if self._isInvalid:
            return None
        with self._tstMutex:
            return self.__semSS

    def __StartPyThread(self):

        if not self.linkedPyThread.is_alive():
            vlogif._LogOEC(False, -3016)
            return
        elif not _TaskUtil.IsCurPyThread(self.linkedPyThread):
            vlogif._LogOEC(False, -3017)
            return

        self._CheckSetTaskState(_TaskState._EState.eRunning)

        _AbstractTask.CreateLcTLB(self)

        self._SetTaskExecPhase(_ETaskExecutionPhaseID.eFwHandling)

        self.__rbl._Run(None, *self.taskProfile.args, **self.taskProfile.kwargs)

        if self.taskBadge is None:
            vlogif._LogOEC(True, -1303)
            return

        if self.isAborting:
            self._CheckSetTaskState(_TaskState._EState.eFailed)
        else:
            self._CheckSetTaskState(_TaskState._EState.eDone)

    def __EvaluateCtorParams( self
                            , taskPrf_                    : _TaskProfile       =None
                            , runnable_                   : _AbstractRunnable  =None
                            , taskName_                   : str                =None
                            , resourcesMask_              : _ETaskResourceFlag =None
                            , delayedStartTimeSpanMS_     : int                =None
                            , enclosedPyThread_           : _PyThread          =None
                            , bAutoStartEnclosedPyThread_ : bool               =None
                            , args_                       : list               =None
                            , kwargs_                     : dict               =None
                            , taskProfileAttrs_           : dict               =None ):
        _ts    = None
        _myTpy = taskPrf_
        _valid = True

        if _myTpy is None:
            _myTpy = _TaskProfile( runnable_=runnable_
                                 , taskName_=taskName_
                                 , resourcesMask_=resourcesMask_
                                 , delayedStartTimeSpanMS_=delayedStartTimeSpanMS_
                                 , enclosedPyThread_=enclosedPyThread_
                                 , bAutoStartEnclosedPyThread_=bAutoStartEnclosedPyThread_
                                 , args_=args_
                                 , kwargs_=kwargs_
                                 , taskProfileAttrs_=taskProfileAttrs_ )

        if not isinstance(_myTpy, _TaskProfile):
            _valid = False
            vlogif._LogOEC(True, -1304)
        elif not (_myTpy.isValid and _myTpy.runnable is not None):
            _valid = False
            vlogif._LogOEC(True, -1305)
        elif _myTpy.isEnclosingPyThread and not _myTpy.enclosedPyThread.is_alive():
            _valid = False
            vlogif._LogOEC(True, -1306)

        if not _valid:
            if (_myTpy is not None) and taskPrf_ is None:
                _myTpy.CleanUp()
            _ts, _myTpy = None, None
        else:
            _ts = _TaskState(self, _TaskState._EState.eInitialized, mtx_=self._tstMutex)
        return _ts, _myTpy

    def __CleanUpOnCtorFailure (self
                              , tskError_          =None
                              , terrCallableIF_    =None
                              , tskBadge_          =None
                              , tskProfile_        =None
                              , mtxApi_            =None
                              , mtxData_           =None):
        if tskError_          is not None: tskError_.CleanUp()
        if terrCallableIF_    is not None: terrCallableIF_.CleanUp()
        if tskBadge_          is not None: tskBadge_.CleanUp()
        if tskProfile_        is not None: tskProfile_.CleanUp()
        if mtxApi_            is not None: mtxApi_.CleanUp()
        if mtxData_           is not None: mtxData_.CleanUp()

        self.__rbl            = None
        self.__semSS          = None
        self.__mtxApi         = None
        self.__mtxData        = None
        self.__tskProfile     = None
        self.__bAutocreatedTP = None

        super()._CleanUp()
        self.CleanUp()
