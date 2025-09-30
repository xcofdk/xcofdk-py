# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwtask.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from typing import Union

from _fw.fwssys.assys                        import fwsubsysshare as _ssshare
from _fw.fwssys.fwcore.logging               import logif
from _fw.fwssys.fwcore.logging               import vlogif
from _fw.fwssys.fwcore.base.fwcallable       import _FwCallable
from _fw.fwssys.fwcore.base.timeutil         import _TimeAlert
from _fw.fwssys.fwcore.base.gtimeout         import _Timeout
from _fw.fwssys.fwcore.ipc.rbl.arunnable     import _AbsRunnable
from _fw.fwssys.fwcore.ipc.sync.semaphore    import _BinarySemaphore
from _fw.fwssys.fwcore.ipc.sync.mutex        import _Mutex
from _fw.fwssys.fwcore.ipc.sync.syncresguard import _SyncResourcesGuard
from _fw.fwssys.fwcore.ipc.tsk.afwtask       import _AbsFwTask
from _fw.fwssys.fwcore.ipc.tsk.taskdefs      import _ETaskSelfCheckResultID
from _fw.fwssys.fwcore.ipc.tsk.ataskop       import _EATaskOpID
from _fw.fwssys.fwcore.ipc.tsk.ataskop       import _ATaskOpPreCheck
from _fw.fwssys.fwcore.ipc.tsk.taskbadge     import _TaskBadge
from _fw.fwssys.fwcore.ipc.tsk.fwtaskerror   import _FwTaskError
from _fw.fwssys.fwcore.ipc.tsk.fwtaskerror   import _TaskErrorExtended
from _fw.fwssys.fwcore.ipc.tsk.fwtaskprf     import _FwTaskProfile
from _fw.fwssys.fwcore.ipc.tsk.taskstate     import _TaskState
from _fw.fwssys.fwcore.ipc.tsk.taskutil      import _PyThread
from _fw.fwssys.fwcore.ipc.tsk.taskutil      import _TaskUtil
from _fw.fwssys.fwcore.ipc.tsk.taskutil      import _ETaskType
from _fw.fwssys.fwcore.ipc.tsk.taskutil      import _EFwApiBookmarkID
from _fw.fwssys.fwcore.ipc.tsk.taskutil      import _ETaskResFlag
from _fw.fwssys.fwcore.ipc.tsk.taskutil      import _ETaskApiContextID
from _fw.fwssys.fwcore.ipc.tsk.taskutil      import _ETaskXPhaseID
from _fw.fwssys.fwcore.ipc.tsk.taskxcard     import _TaskXCard
from _fw.fwssys.fwcore.lc.lcdefines          import _ELcCompID
from _fw.fwssys.fwcore.lc.ifs.iflcproxy      import _ILcProxy
from _fw.fwssys.fwcore.lc.lcmn.lcmontlb      import _LcCeaseTLB
from _fw.fwssys.fwcore.types.afwprofile      import _AbsFwProfile
from _fw.fwssys.fwcore.types.commontypes     import override
from _fw.fwssys.fwerrh.fwerrorcodes          import _EFwErrorCode
from _fw.fwssys.fwerrh.pcerrhandler          import _PcErrHandler
from _fw.fwssys.fwerrh.logs.xcoexception     import _XcoXcpRootBase

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _FwTask(_AbsFwTask):
    __slots__ = [ '__ma' , '__md' , '__tp' , '__r' , '__s' , '__bA' ]

    def __init__( self
                , fwtPrf_         : _FwTaskProfile =None
                , rbl_            : _AbsRunnable   =None
                , taskName_       : str            =None
                , rmask_          : _ETaskResFlag  =None
                , delayedStartMS_ : int            =None
                , enclHThrd_      : _PyThread      =None
                , bASEnclHThrd_   : bool =None
                , bFwMain_        : bool =False
                , args_           : list =None
                , kwargs_         : dict =None
                , tpAttrs_        : dict =None):
        self.__r  = None
        self.__s  = None
        self.__bA = None
        self.__ma = None
        self.__md = None
        self.__tp = None

        super().__init__()

        self.__md = _Mutex()
        self._tstMutex = _Mutex()

        _ts = None
        _tp = None
        _ts, _tp = self.__EvaluateCtorParams( fwtPrf_=fwtPrf_
                                            , rbl_=rbl_
                                            , taskName_=taskName_
                                            , rmask_=rmask_
                                            , delayedStartMS_=delayedStartMS_
                                            , enclHThrd_=enclHThrd_
                                            , bASEnclHThrd_=bASEnclHThrd_
                                            , args_=args_, kwargs_=kwargs_
                                            , tpAttrs_=tpAttrs_)

        if _ts is None:
            self.__CleanUpOnCtorFailure(md_=self.__md)
            return

        _utc = None
        _rbl = _tp.runnable
        _rt  = _rbl._rblType
        if bFwMain_:
            _tt = _ETaskType.eFwMainTask
        elif not _rt.isXTaskRunnable:
            _tt = _ETaskType.eFwTask
        else:
            _tt  = _ETaskType.eMainXTaskTask if _rt.isMainXTaskRunnable else _ETaskType.eXTaskTask
            _utc = _rbl._utConn

        if _utc is not None:
            _bRcTask    = _utc._taskProfile.isRcTask
            _tid, _tidx = _utc._taskProfile._bookedTaskID, _utc._taskProfile._bookedTaskIndex
        else:
            _bRcTask    = False
            _tid, _tidx = _TaskUtil.GetNextTaskID(_tp.taskRightsMask.hasUserTaskRight, bEnclSThrd_=_tp.isEnclosingStartupThread)

        _tname = None
        if not _AbsFwProfile._IsAutoGeneratedTaskNameEnabled():
            _tname = _tp.dtaskName
        if _tname is None:
            if not _tt.isXTaskTask:
                _txtID = _EFwTextID.eMisc_TNPrefix_DTask
            else:
                _txtID = _EFwTextID.eMisc_TNPrefix_CRCTask if _bRcTask else _EFwTextID.eMisc_TNPrefix_CXTask
            _tname = f'{_FwTDbEngine.GetText(_txtID)}{_tid}'

        _tp.Freeze(*(_tid, _tname))
        if not _tp.isFrozen:
            _tp = _tp if fwtPrf_ is None else None
            self.__CleanUpOnCtorFailure(md_=self.__md, fwtPrf_=_tp)
            return

        _thrdNID = None
        if _tp.isEnclosingPyThread:
            _myThrd = _tp.enclosedPyThread
            if _TaskUtil.IsNativeThreadIdSupported():
                _thrdNID = _myThrd.native_id
        else:
            _myThrd = _PyThread(group=None, target=self.__RunThread, name=_tname, args=(), kwargs={}, daemon=None)

        _bExtQueueSupport = _tp.isExternalQueueEnabled or _rbl._isSelfManagingExternalQueue
        _bIntQueueSupport = _tp.isInternalQueueEnabled or _rbl._isSelfManagingInternalQueue

        _myTB = _TaskBadge( taskName_=_tname, taskID_=_tid, threadUID_=_TaskUtil.GetPyThreadUID(_myThrd)
                          , taskType_=_tt, trMask_=_tp.taskRightsMask, threadNID_=_thrdNID, fwsID_=_rt.toFwcID
                          , bEnclHThrd_=_tp.isEnclosingPyThread, bEnclSThrd_=_tp.isEnclosingStartupThread
                          , bXQ_=_bExtQueueSupport, bIQ_=_bIntQueueSupport, bRcTask_=_bRcTask)
        if _myTB.dtaskUID is None:
            _tp = _tp if fwtPrf_ is None else None
            self.__CleanUpOnCtorFailure(md_=self.__md, fwtPrf_=_tp, tskBadge_=_myTB)
            return

        _tecbif = _FwCallable(_rbl._OnTENotification)
        if not _tecbif.isValid:
            _tp = _tp if fwtPrf_ is None else None
            self.__CleanUpOnCtorFailure(md_=self.__md, fwtPrf_=_tp, tskBadge_=_myTB, terrCIF_=_tecbif)
            return

        if _myTB.hasForeignErrorListnerTaskRight:
            _tskErr = _TaskErrorExtended(self.__md, _myTB, teCBIF_=_tecbif)
        else:
            _tskErr = _FwTaskError(self.__md, _myTB, teCBIF_=_tecbif)

        if _tskErr.taskBadge is None:
            _tp = _tp if fwtPrf_ is None else None
            self.__CleanUpOnCtorFailure(md_=self.__md, fwtPrf_=_tp, tskBadge_=_myTB, terrCIF_=_tecbif, tskError_=_tskErr)
            return

        self._dHThrd   = _myThrd
        self._utConn   = _utc
        self._tskBadge = _myTB
        self._tskError = _tskErr
        self._tskState = _ts

        self.__r  = _rbl
        self.__ma = _Mutex()
        self.__tp = _tp
        self.__bA = fwtPrf_ is None

        if _utc is not None:
            if not _utc._UpdateUTD(self):
                self.CleanUp()
                return

        _bTBR = False
        if _bTBR:
            _PcErrHandler._SetUpPcEH(self, self.__md)
            if self._isForeignErrorListener is None:
                self.CleanUp()
                return

        _rbl._RblSetTask(self)
        if _rbl._rblTask is None:
            self.CleanUp()
            return
        if self.__tp.isAutoStartEnclHThrdEnabled:
            self.__SyncStart()

    @property
    def sendOperator(self):
        return None if self._isInvalid or self.__r._isInvalid else self.__r

    @property
    def _isInvalid(self) -> bool:
        return self.__md is None

    @property
    def _isAutoStartEnclHThrdEnabled(self) -> bool:
        return False if self.__tp is None else self.__tp.isAutoStartEnclHThrdEnabled

    @property
    def _dxUnit(self):
        return self.__r

    @property
    def _daprofile(self) -> _AbsFwProfile:
        return None if self._isInvalid else self._dtaskProfile

    @property
    def _xcard(self) -> _TaskXCard:
        return None if self.__r is None else self.__r._xcard

    @property
    def _xrNumber(self) -> int:
        if self._isInvalid or (self.__r is None):
            return None
        elif self.taskBadge.isFwMain:
            with self.__md:
                return self._xrNum
        else:
            return self._xrNum

    def _GetTaskXPhase(self) -> _ETaskXPhaseID:
        if self._isInvalid:
            return _ETaskXPhaseID.eNA
        with self.__md:
            return self._tskXPhase

    def _GetTaskApiContext(self) -> _ETaskApiContextID:
        if self._isInvalid:
            return _ETaskApiContextID.eDontCare
        with self.__md:
            return self._tskApiCtx

    def _IncEuRNumber(self) -> int:
        if self._isInvalid or (self.__r is None):
            return -1
        elif self.taskBadge.isFwMain:
            with self.__md:
                return _AbsFwTask._IncEuRNumber(self)
        else:
            return _AbsFwTask._IncEuRNumber(self)

    def _PropagateLcProxy(self, lcProxy_ : _ILcProxy =None):
        if self._isInvalid:
            return
        with self.__md:
            if self._PcIsLcProxySet():
                self.__r._PcSetLcProxy(self._PcGetLcProxy() if lcProxy_ is None else lcProxy_)

    def _GetLcCompID(self) -> Union[_ELcCompID, None]:
        if self._isInvalid or (self.__r is None) or self.__r._isInvalid:
            return None
        return self.__r._rblType.toLcCompID

    def _StartTask(self, semStart_ : _BinarySemaphore =None, tskOpPCheck_ : _ATaskOpPreCheck =None, curTask_ : _AbsFwTask =None) -> bool:
        if self._isInvalid:
            return False
        if not self._PcIsLcOperable():
            return False

        with self.__ma:
            if self.isEnclosingPyThread:
                if semStart_ is not None:
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00196)
                    return False
            elif not isinstance(semStart_, _BinarySemaphore):
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00197)
                return False

            _oppc = tskOpPCheck_
            if _oppc is None:
                _oppc = _ATaskOpPreCheck(_EATaskOpID.eStart, self._tskState, self._dHThrd, self.isEnclosingPyThread, bReportErr_=True)
            else:
                _oppc.Update(taskOpID_=_EATaskOpID.eStart, bReportErr_=True)
            if _oppc.isNotApplicable or _oppc.isIgnorable:
                _bIgnorable = _oppc.isIgnorable
                if tskOpPCheck_ is None:
                    _oppc.CleanUp()

                if _bIgnorable:
                    if semStart_ is not None:
                        semStart_.Give()
                return _bIgnorable

            elif tskOpPCheck_ is None:
                _oppc.CleanUp()

            if not self.isEnclosingPyThread:
                with self._tstMutex:
                    self.__s = semStart_
                    self._CheckSetTaskState(_TaskState._EState.ePendingRun)

        res     = True
        _prvBid = None

        if self.taskBadge.isDrivingXTask:
            _prvBid = None if curTask_ is None else curTask_.fwApiBookmarkID

        if self.isEnclosingPyThread:
            if _prvBid is not None:
                curTask_._SetFwApiBookmark(_EFwApiBookmarkID.eXTaskApiBeginActionStart)

            self.__SyncStart()

            if _prvBid is not None:
                curTask_._SetFwApiBookmark(_prvBid)

            if self._isInvalid or (self.__r is None):
                res = False
        else:
            if _prvBid is not None:
                curTask_._SetFwApiBookmark(_EFwApiBookmarkID.eXTaskApiBeginActionStart)

            self._SetTaskXPhase(_ETaskXPhaseID.eFwHandling)
            try:
                _TaskUtil._StartHThread(self.dHThrd)
            except Exception as _xcp:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00983)

            if _prvBid is not None:
                curTask_._SetFwApiBookmark(_prvBid)

            with self.__md:
                _tuid          = self.taskBadge.threadUID
                _tnid          = self.taskBadge.threadNID
                _bNIDSupported = _TaskUtil.IsNativeThreadIdSupported()

                if (_tuid is None) or ((_tnid is None) and _bNIDSupported):
                    if _tuid is None:
                        _tuid = _TaskUtil.GetPyThreadUID(self.dHThrd)
                    if (_tnid is None) and _bNIDSupported:
                        _tnid = self.dHThrd.native_id
                    self.taskBadge._UpdateRuntimeIDs(threadUID_=_tuid, threadNID_=_tnid)

        if res and not (self.isDone or self.isCanceled):
            _rt = self.__r._rblType
            if _rt.isMainXTaskRunnable:
                if not self._PcHasLcAnyFailureState():
                    self._PcSetLcOperationalState(_rt.toLcCompID, True, self)
        return True

    def _StopTask(self, bCancel_ =False, semStop_ : _BinarySemaphore =None, tskOpPCheck_ : _ATaskOpPreCheck =None, curTask_ : _AbsFwTask =None) -> bool:
        if self._isInvalid:
            return False

        with self.__ma:
            if self.isEnclosingPyThread:
                if semStop_ is not None:
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00199)
                    return False
            elif (semStop_ is not None) and not isinstance(semStop_, _BinarySemaphore):
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00200)
                return False
            elif self.__startStopSem is not None:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00201)
                return False

            _oppc = tskOpPCheck_
            _opid = _EATaskOpID.eCancel if bCancel_ else _EATaskOpID.eStop
            if _oppc is None:
                _oppc = _ATaskOpPreCheck(_opid, self._tskState, self._dHThrd, self.isEnclosingPyThread, bReportErr_=True)
            else:
                _oppc.Update(taskOpID_=_opid, bReportErr_=True)
            if _oppc.isNotApplicable or _oppc.isIgnorable:
                _bIgnorable = _oppc.isIgnorable
                if tskOpPCheck_ is None:
                    _oppc.CleanUp()

                if _bIgnorable:
                    if semStop_ is not None:
                        semStop_.Give()
                return _bIgnorable

            if _oppc.isSynchronous:
                if semStop_ is not None:
                    semStop_.Give()
                    semStop_ = None

            if tskOpPCheck_ is None:
                _oppc.CleanUp()

            _prvBid = None
            if self.taskBadge.isDrivingXTask:
                _prvBid = None if curTask_ is None else curTask_.fwApiBookmarkID

        with self.__md:
            if _prvBid is not None:
                curTask_._SetFwApiBookmark(_EFwApiBookmarkID.eXTaskApiBeginActionStop)

        with self._tstMutex:
            self._CheckSetTaskState(_TaskState._EState.ePendingCancelRequest if bCancel_ else _TaskState._EState.ePendingStopRequest)

            self.__s = semStop_
            self.__r._RblSetStopSyncSem(semStop_)
            self.__s = None

        with self.__md:
            if _prvBid is not None:
                curTask_._SetFwApiBookmark(_prvBid)
        return True

    def _JoinTask(self, timeout_ : _Timeout =None, tskOpPCheck_ : _ATaskOpPreCheck =None, curTask_ : _AbsFwTask =None) -> bool:
        if self._isInvalid or (self.dHThrd is None):
            return False
        if timeout_ is not None:
            if not _Timeout.IsTimeout(timeout_, bThrowx_=True):
                return False
            elif timeout_.isInfiniteTimeout:
                timeout_ = None

        _tn  = self.dtaskName
        _lpf = self.__logPrefix

        if (self._lcDynTLB is not None) and self._lcDynTLB.isCoordinatedShutdownRunning:
            return False

        with self.__ma:
            _oppc = tskOpPCheck_
            if _oppc is None:
                _oppc = _ATaskOpPreCheck(_EATaskOpID.eJoin, self._tskState, self._dHThrd, self.isEnclosingPyThread, bReportErr_=True)
            else:
                _oppc.Update(taskOpID_=_EATaskOpID.eJoin, bReportErr_=True)

            if _oppc.isNotApplicable or _oppc.isIgnorable:
                _bIgnorable = _oppc.isIgnorable
                if tskOpPCheck_ is None:
                    _oppc.CleanUp()
                return _bIgnorable

            elif tskOpPCheck_ is None:
                _oppc.CleanUp()
        _prvBid = None
        if self.taskBadge.isDrivingXTask:
            _prvBid = None if curTask_ is None else curTask_.fwApiBookmarkID

        res          = False
        _xcpKB       = None
        _xcpCaught   = None
        _bCSDRunning = False
        try:
            if _prvBid is not None:
                curTask_._SetFwApiBookmark(_EFwApiBookmarkID.eXTaskApiBeginActionJoin)

            if self.isEnclosingPyThread:
                _MIN_WAIT_TIMESPAN_MS = 10

                _talert = None if timeout_ is None else _TimeAlert(timeout_.toNSec)
                if _talert is not None:
                    _talert.CheckAlert()

                while True:
                    res = self._isInvalid or self.isTerminated
                    if res:
                        break

                    if (self._lcDynTLB is not None) and self._lcDynTLB.isCoordinatedShutdownRunning:
                        _bCSDRunning = True
                        break

                    _TaskUtil.SleepMS(_MIN_WAIT_TIMESPAN_MS)
                    if (_talert is not None) and _talert.CheckAlert():
                        break
                    continue

            else:
                _timeoutMS      = 0 if timeout_ is None else timeout_.toMSec
                _timeoutStepMS  = _TaskXCard._GetLcMonitorCyclicRunPauseTimespanMS()
                _timeoutTotalMS = 0
                if _timeoutStepMS is None:
                    _timeoutStepMS = 100
                if (_timeoutMS > 0) and (_timeoutMS < _timeoutStepMS):
                    _timeoutStepMS = _timeoutMS
                _timeoutStepSEC = float(_timeoutStepMS/1000)

                while True:
                    if self.dHThrd is None:
                        break

                    _TaskUtil.JoinPyThread(self.dHThrd, timeoutSEC_=_timeoutStepSEC)
                    _timeoutTotalMS += _timeoutStepMS
                    if (_timeoutMS > 0) and (_timeoutTotalMS >= _timeoutMS):
                        break
                    if self._isInvalid or self.isTerminated:
                        res = True
                        break
                    if (self._lcDynTLB is not None) and self._lcDynTLB.isCoordinatedShutdownRunning:
                        _bCSDRunning = True
                        break
                    continue

        except _XcoXcpRootBase as _xcp:
            pass
        except KeyboardInterrupt:
            _tn  = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwTask_TID_002).format(_tn)
            _msg = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_KeyboardInterrupt).format(_lpf, _tn)
            _ssshare._BookKBI(_msg)
        except BaseException as _xcp:
            _xcpCaught = _xcp

        finally:
            if _prvBid is not None:
                curTask_._SetFwApiBookmark(_prvBid)
            if _xcpCaught is not None:
                logif._LogUnhandledXcoBaseXcpEC(_EFwErrorCode.FE_00019, _xcpCaught)
        if not res:
            if _bCSDRunning:
                pass
            elif timeout_ is not None:
                vlogif._LogOEC(False, _EFwErrorCode.VUE_00018)
            else:
                vlogif._LogOEC(False, _EFwErrorCode.VUE_00019)
        return res

    @override
    def _PcSelfCheck(self) -> _ETaskSelfCheckResultID:
        return self.__r._PcSelfCheck()

    @staticmethod
    def _CreateTask( fwtPrf_         : _FwTaskProfile =None
                   , rbl_            : _AbsRunnable   =None
                   , taskName_       : str            =None
                   , rmask_          : _ETaskResFlag  =None
                   , enclHThrd_      : _PyThread      =None
                   , bASEnclHThrd_   : bool           =None
                   , delayedStartMS_ : int            =None
                   , args_           : list =None
                   , kwargs_         : dict =None
                   , tpAttrs_        : dict =None ):
        if fwtPrf_ is not None:
            if (not fwtPrf_.isValid) or (fwtPrf_.isEnclosingPyThread and (fwtPrf_.enclosedPyThread is None)):
                vlogif._LogOEC(False, _EFwErrorCode.VUE_00013)
                return None
        elif tpAttrs_ is not None:
            if _FwTaskProfile._ATTR_KEY_ENCLOSED_PYTHREAD in tpAttrs_:
                vlogif._LogOEC(False, _EFwErrorCode.VUE_00014)
                return None

        res = _FwTask( fwtPrf_=fwtPrf_
                     , rbl_=rbl_
                     , taskName_=taskName_
                     , rmask_=rmask_
                     , delayedStartMS_=delayedStartMS_
                     , enclHThrd_=enclHThrd_
                     , bASEnclHThrd_=bASEnclHThrd_
                     , args_=args_
                     , kwargs_=kwargs_
                     , tpAttrs_=tpAttrs_)
        if res.taskBadge is None:
            res.CleanUp()
            res = None
        return res

    @property
    def _dtaskProfile(self):
        return self.__tp

    def _CleanUp(self):
        if self._isInvalid:
            return

        if self.__r is not None:
            self.__r._RblSetTask(None)

        if self.__bA:
            if self.__tp is not None:
                self.__tp.CleanUp()

        _tid        = self.dtaskUID
        _bEnclHThrd = self.isEnclosingPyThread

        super()._CleanUp()

        if self.__ma is not None:
            self.__ma.CleanUp()
            self.__ma = None

        self.__md.CleanUp()
        self.__md = None

        if _bEnclHThrd:
            _srg = _SyncResourcesGuard._GetInstance()
            if _srg is not None:
                _srg.ReleaseAcquiredSyncResources(_tid)

        self.__r  = None
        self.__s  = None
        self.__bA = None
        self.__tp = None

    def _CheckSetTaskState(self, newState_ : _TaskState._EState) -> _TaskState._EState:
        res = self.dtaskStateID

        if res is None:
            return None

        with self._tstMutex:
            if newState_.isFailed:
                if not (res.isFailedByXCmdReturn or newState_.isFailedByXCmdReturn):
                    if self.__r._isReturnedXCmdAbort:
                        _tstate = _TaskState._EState.eFailedByXCmdReturn
                        newState_ = _tstate

            if newState_ != res:
                _utc   = self._utConn
                _lcCID = self._GetLcCompID()

                if _utc is not None:
                    if newState_.isFailedByXCmdReturn:
                        self.__r._CheckNotifyLcFailure()
                res = _AbsFwTask._SetGetTaskState(self, newState_)

                if res != newState_:
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00202)
                elif _utc is not None:
                    _utc._UpdateUTD(self)

                    if newState_.isTerminated:
                        if newState_.isFailed:
                            pass
                        elif self.__r._rblType.isMainXTaskRunnable:
                            if not self._PcHasLcCompAnyFailureState(_lcCID, self):
                                self._PcSetLcOperationalState(_lcCID, False, self)
            return res

    def _CreateCeaseTLB(self, bEnding_ =False) -> _LcCeaseTLB:
        if self._isInvalid or (self.__r is None):
            res = None
        else:
            res = self.__r._CreateCeaseTLB(bEnding_=bEnding_)
        return res

    @property
    def __logPrefix(self):
        res  = _FwTDbEngine.GetText(_EFwTextID.eMisc_LogPrefix_Task)
        res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_010).format(self.dtaskName)
        return res

    @property
    def __logPrefixCtr(self):
        res  = _FwTDbEngine.GetText(_EFwTextID.eMisc_LogPrefix_Task)
        res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_010).format(self.dtaskName)
        res += _FwTDbEngine.GetText(_EFwTextID.eMisc_LogPrefix_ExecCounter).format(self.xrNumber)
        return res

    @property
    def __startStopSem(self):
        if self._isInvalid:
            return None
        with self._tstMutex:
            return self.__s

    def __SyncStart(self):
        if not self.dHThrd.is_alive():
            vlogif._LogOEC(False, _EFwErrorCode.VUE_00020)
            return
        if not _TaskUtil.IsCurPyThread(self.dHThrd):
            vlogif._LogOEC(False, _EFwErrorCode.VUE_00021)
            return

        self._CheckSetTaskState(_TaskState._EState.eRunning)

        _AbsFwTask.CreateLcTLB(self)

        self._SetTaskXPhase(_ETaskXPhaseID.eFwHandling)

        self.__r._Run(None)

        if self.taskBadge is None:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00206)
            return

        if self.isAborting:
            _nts = _TaskState._EState.eFailed
        else:
            _nts = _TaskState._EState.eCanceled if self.isCanceling else _TaskState._EState.eDone
        self._CheckSetTaskState(_nts)

    def __RunThread(self):
        if not self.isStarted:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00203)
            return
        if self.isEnclosingPyThread:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00204)
            return

        with self.__md:
            _tuid          = self.taskBadge.threadUID
            _tnid          = self.taskBadge.threadNID
            _bNIDSupported = _TaskUtil.IsNativeThreadIdSupported()

            if (_tuid is None) or ((_tnid is None) and _bNIDSupported):
                if _tuid is None:
                    _tuid = _TaskUtil.GetPyThreadUID(self.dHThrd)
                if (_tnid is None) and _bNIDSupported:
                    _tnid = self.dHThrd.native_id
                self.taskBadge._UpdateRuntimeIDs(threadUID_=_tuid, threadNID_=_tnid)

            self._CheckSetTaskState(_TaskState._EState.eRunning)

            _AbsFwTask.CreateLcTLB(self)

            with self._tstMutex:
                _semSS = self.__s
                self.__s = None

        self.__r._Run(_semSS)

        if self.taskBadge is None:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00205)
            return

        if self.isAborting:
            _nts = _TaskState._EState.eFailed
        else:
            _nts = _TaskState._EState.eCanceled if self.isCanceling else _TaskState._EState.eDone
        self._CheckSetTaskState(_nts)

        _srg = _SyncResourcesGuard._GetInstance()
        if _srg is not None:
            _srg.ReleaseAcquiredSyncResources(self.dtaskUID)

    def __EvaluateCtorParams( self
                            , fwtPrf_         : _FwTaskProfile =None
                            , rbl_            : _AbsRunnable   =None
                            , taskName_       : str            =None
                            , rmask_          : _ETaskResFlag  =None
                            , delayedStartMS_ : int            =None
                            , enclHThrd_      : _PyThread      =None
                            , bASEnclHThrd_   : bool =None
                            , args_           : list =None
                            , kwargs_         : dict =None
                            , tpAttrs_        : dict =None ):
        _ts    = None
        _myTpy = fwtPrf_
        _valid = True

        if _myTpy is None:
            _myTpy = _FwTaskProfile( rbl_=rbl_
                                   , taskName_=taskName_
                                   , rmask_=rmask_
                                   , delayedStartMS_=delayedStartMS_
                                   , enclHThrd_=enclHThrd_
                                   , bASEnclHThrd_=bASEnclHThrd_
                                   , args_=args_
                                   , kwargs_=kwargs_
                                   , tpAttrs_=tpAttrs_ )

        if not isinstance(_myTpy, _FwTaskProfile):
            _valid = False
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00207)
        elif not (_myTpy.isValid and _myTpy.runnable is not None):
            _valid = False
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00208)
        elif _myTpy.isEnclosingPyThread and not _myTpy.enclosedPyThread.is_alive():
            _valid = False
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00209)

        if not _valid:
            if (_myTpy is not None) and fwtPrf_ is None:
                _myTpy.CleanUp()
            _ts, _myTpy = None, None
        else:
            _ts = _TaskState(self, _TaskState._EState.eInitialized, mtx_=self._tstMutex)
        return _ts, _myTpy

    def __CleanUpOnCtorFailure( self
                              , tskError_ =None
                              , terrCIF_  =None
                              , tskBadge_ =None
                              , fwtPrf_   =None
                              , ma_       =None
                              , md_       =None):
        if tskError_ is not None: tskError_.CleanUp()
        if terrCIF_  is not None: terrCIF_.CleanUp()
        if tskBadge_ is not None: tskBadge_.CleanUp()
        if fwtPrf_   is not None: fwtPrf_.CleanUp()
        if ma_       is not None: ma_.CleanUp()
        if md_       is not None: md_.CleanUp()

        self.__r  = None
        self.__s  = None
        self.__bA = None
        self.__ma = None
        self.__md = None
        self.__tp = None

        super()._CleanUp()
        self.CleanUp()
