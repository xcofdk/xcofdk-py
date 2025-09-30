# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwthread.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from xcofdk.fwcom import EExecutionCmdID

from _fw.fwssys.assys                        import fwsubsysshare as _ssshare
from _fw.fwssys.assys.ifs.ifutaskconn        import _IUTaskConn
from _fw.fwssys.assys.ifs.ifutagent          import _IUTAgent
from _fw.fwssys.fwcore.logging               import logif
from _fw.fwssys.fwcore.logging               import vlogif
from _fw.fwssys.fwcore.logging.logdefines    import _EErrorImpact
from _fw.fwssys.fwcore.base.fwcallable       import _FwCallable
from _fw.fwssys.fwcore.base.timeutil         import _TimeAlert
from _fw.fwssys.fwcore.base.gtimeout         import _Timeout
from _fw.fwssys.fwcore.base.strutil          import _StrUtil
from _fw.fwssys.fwcore.ipc.sync.mutex        import _Mutex
from _fw.fwssys.fwcore.ipc.sync.semaphore    import _BinarySemaphore
from _fw.fwssys.fwcore.ipc.sync.syncresguard import _SyncResourcesGuard
from _fw.fwssys.fwcore.ipc.fws.afwservice    import _AbsFwService
from _fw.fwssys.fwcore.ipc.tsk.ataskop       import _EATaskOpID
from _fw.fwssys.fwcore.ipc.tsk.ataskop       import _ATaskOpPreCheck
from _fw.fwssys.fwcore.ipc.tsk.afwtask       import _AbsFwTask
from _fw.fwssys.fwcore.ipc.tsk.taskdefs      import _EFwsID
from _fw.fwssys.fwcore.ipc.tsk.taskdefs      import _ETaskSelfCheckResultID
from _fw.fwssys.fwcore.ipc.tsk.taskdefs      import _EUTaskApiFuncTag
from _fw.fwssys.fwcore.ipc.tsk.taskdefs      import _UTaskApiGuide
from _fw.fwssys.fwcore.ipc.tsk.fwthreadprf   import _FwThreadProfile
from _fw.fwssys.fwcore.ipc.tsk.taskbadge     import _TaskBadge
from _fw.fwssys.fwcore.ipc.tsk.fwtaskerror   import _FwTaskError
from _fw.fwssys.fwcore.ipc.tsk.fwtaskerror   import _TaskErrorExtended
from _fw.fwssys.fwcore.ipc.tsk.taskstate     import _TaskState
from _fw.fwssys.fwcore.ipc.tsk.taskutil      import _TaskUtil
from _fw.fwssys.fwcore.ipc.tsk.taskutil      import _ETaskType
from _fw.fwssys.fwcore.ipc.tsk.taskutil      import _PyThread
from _fw.fwssys.fwcore.ipc.tsk.taskutil      import _EFwApiBookmarkID
from _fw.fwssys.fwcore.ipc.tsk.taskutil      import _ETaskApiContextID
from _fw.fwssys.fwcore.ipc.tsk.taskutil      import _ETaskXPhaseID
from _fw.fwssys.fwcore.ipc.tsk.taskutil      import _EProcessingFeasibilityID
from _fw.fwssys.fwcore.ipc.tsk.taskxcard     import _TaskXCard
from _fw.fwssys.fwcore.lc.lcdefines          import _ELcCompID
from _fw.fwssys.fwcore.lc.lcdefines          import _ELcOperationModeID
from _fw.fwssys.fwcore.lc.ifs.iflcproxy      import _ILcProxy
from _fw.fwssys.fwcore.lc.lcmn.lcmontlb      import _ELcCeaseTLBState
from _fw.fwssys.fwcore.lc.lcmn.lcmontlb      import _LcCeaseTLB
from _fw.fwssys.fwcore.types.aobject         import _AbsSlotsObject
from _fw.fwssys.fwcore.types.afwprofile      import _AbsFwProfile
from _fw.fwssys.fwcore.types.commontypes     import override
from _fw.fwssys.fwcore.types.commontypes     import _CommonDefines
from _fw.fwssys.fwcore.types.commontypes     import _EExecutionCmdID
from _fw.fwssys.fwerrh.fwerrorcodes          import _EFwErrorCode
from _fw.fwssys.fwerrh.pcerrhandler          import _PcErrHandler
from _fw.fwssys.fwerrh.pcerrhandler          import _EPcErrHandlerCBID
from _fw.fwssys.fwerrh.logs.errorlog         import _ErrorLog
from _fw.fwssys.fwerrh.logs.errorlog         import _FatalLog
from _fw.fwssys.fwmsg.msg                    import _IFwMessage
from _fw.fwssys.fwerrh.logs.xcoexception     import _IsXTXcp
from _fw.fwssys.fwerrh.logs.xcoexception     import _XcoXcpRootBase
from _fw.fwssys.fwerrh.logs.xcoexception     import _XcoBaseException
from _fwa.fwsubsyscoding                     import _FwSubsysCoding

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _FwThread(_AbsFwTask):
    class _UTRefs(_AbsSlotsObject):
        __slots__ = [ '__a' , '__c' ]

        def __init__(self, utConn_ : _IUTaskConn):
            super().__init__()
            self.__a = utConn_._utAgent
            self.__c = utConn_

        @property
        def _utAgent(self) -> _IUTAgent:
            return self.__a

        @property
        def _utaskConn(self) -> _IUTaskConn:
            return self.__c

        def _ToString(self) -> str:
            return _CommonDefines._STR_EMPTY

        def _CleanUp(self):
            if self.__c is not None:
                self.__c._DisconnectUTask()
                self.__c.CleanUp()

            self.__a = None
            self.__c = None

    class _XTaskExecutorTable(_AbsSlotsObject):
        __slots__ = [ '__dx' ]

        def __init__(self, dictExecutors_ : dict):
            self.__dx = dictExecutors_
            super().__init__()

        def _GetApiExecutor(self, fid_ : _EUTaskApiFuncTag):
            res = None
            if self.__dx is None:
                pass
            elif not isinstance(fid_, _EUTaskApiFuncTag):
                pass
            elif not fid_ in self.__dx:
                pass
            else:
                res = self.__dx[fid_]
            return res

        def _CleanUp(self):
            if self.__dx is not None:
                for _vv in self.__dx.values():
                    _vv.CleanUp()
                self.__dx.clear()
                self.__dx = None

    __slots__ = [ '__md' , '__ma' , '__tp' , '__s' , '__xc' , '__ag' , '__bA' , '__utr' , '__xtors' ]

    __FwDispRbl = None
    __XR_XCP_DW = _FwTDbEngine.GetText(_EFwTextID.eMisc_XML_RUNNER_XCP_MSG_DuplicateWriter)

    def __init__( self
                , fwthrdPrf_    : _FwThreadProfile =None
                , utaskConn_    : _IUTaskConn      =None
                , taskName_     : str              =None
                , enclHThrd_    : _PyThread        =None
                , bAEnclHThrd_  : bool             =None
                , bASEnclHThrd_ : bool             =None
                , thrdTgtCIF_   : _FwCallable      =None
                , bFwMain_      : bool =False
                , args_         : list =None
                , kwargs_       : dict =None
                , tpAttrs_      : dict =None
                , txCard_       : _TaskXCard =None):
        self.__s     = None
        self.__ag    = None
        self.__bA    = None
        self.__ma    = None
        self.__md    = None
        self.__xc    = None
        self.__tp    = None
        self.__utr   = None
        self.__xtors = None

        super().__init__()

        self.__md = _Mutex()
        self._tstMutex = _Mutex()

        _ts = None
        _tp = None
        _ts, _tp = self.__EvaluateCtorParams( fwthrdPrf_=fwthrdPrf_
                                            , utaskConn_=utaskConn_
                                            , taskName_=taskName_
                                            , enclHThrd_=enclHThrd_
                                            , bASEnclHThrd_=bASEnclHThrd_
                                            , thrdTgtCIF_=thrdTgtCIF_
                                            , args_=args_
                                            , kwargs_=kwargs_
                                            , tpAttrs_=tpAttrs_)
        if _ts is None:
            self.__CleanUpOnCtorFailure(md_=self.__md)
            return

        if (txCard_ is not None) and not (isinstance(txCard_, _TaskXCard) and txCard_.isValid):
            self.__CleanUpOnCtorFailure(md_=self.__md)
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00210)
            return

        _utc = _tp.utConn
        if _utc is not None:
            _utr = _FwThread._UTRefs(_utc)

            if not ((_utc._xCard is not None) and _utc._xCard.isValid):
                self.__CleanUpOnCtorFailure(md_=self.__md)
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00211)
                return

            txCard_ = _utc._xCard

            _tid, _tidx = _utc._taskProfile._bookedTaskID, _utc._taskProfile._bookedTaskIndex
        else:
            _utr = None
            _tid, _tidx = _TaskUtil.GetNextTaskID(_tp.taskRightsMask.hasUserTaskRight, bEnclSThrd_=_tp.isEnclosingStartupThread, bAEnclHThrd_=bAEnclHThrd_)

        _bRCT = False
        if thrdTgtCIF_ is not None:
            _tt = _ETaskType.eCFwThread
        elif bFwMain_:
            _tt = _ETaskType.eFwMainThread
        elif _utc is None:
            _tt = _ETaskType.eFwThread
        else:
            _utp  = _utc._taskProfile
            _tt   = _ETaskType.eMainXTaskThread if _utp.isMainTask else _ETaskType.eXTaskThread
            _bRCT = _utp.isRcTask

        _tname = None
        if not _AbsFwProfile._IsAutoGeneratedTaskNameEnabled():
            _tname = _tp.dtaskName
        if _tname is None:
            if not _tt.isXTaskThread:
                _txtID = _EFwTextID.eMisc_TNPrefix_DThread
            else:
                _txtID = _EFwTextID.eMisc_TNPrefix_RCTask if _bRCT else _EFwTextID.eMisc_TNPrefix_XTask
            _tname = f'{_FwTDbEngine.GetText(_txtID)}{_tid}'

        _tp.Freeze(*(_tid, _tname))
        if not _tp.isFrozen:
            _tp = _tp if fwthrdPrf_ is None else None
            self.__CleanUpOnCtorFailure(md_=self.__md, fwthrdPrf_=_tp)
            return

        _bAutoStart = not bAEnclHThrd_
        _bAutoStart = _bAutoStart and _tp.isEnclosingPyThread
        if _bAutoStart:
            _bAutoStart = bASEnclHThrd_ if bASEnclHThrd_ is not None else _tp.isAutoStartEnclHThrdEnabled
            if _bAutoStart:
                if not _TaskUtil.IsCurPyThread(fwthrdPrf_.enclosedPyThread):
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00212)

                    _tp = _tp if fwthrdPrf_ is None else None
                    self.__CleanUpOnCtorFailure( md_=self.__md, fwthrdPrf_=_tp, utr_=_utr)
                    return

        _thrdNID    = None
        _bEnclHThrd = _tp.isEnclosingPyThread

        if _bEnclHThrd:
            _myThrd = _tp.enclosedPyThread
            if _TaskUtil.IsNativeThreadIdSupported():
                _thrdNID = _myThrd.native_id
        else:
            _myThrd = _PyThread(group=None, target=self.__RunThrdTgt, name=_tname, args=(), kwargs={}, daemon=None)

        _myTB = _TaskBadge( taskName_=_tname, taskID_=_tid, threadUID_=_TaskUtil.GetPyThreadUID(_myThrd)
                          , taskType_=_tt, trMask_=_tp.taskRightsMask, threadNID_=_thrdNID
                          , bEnclHThrd_=_bEnclHThrd, bEnclSThrd_=_tp.isEnclosingStartupThread
                          , bAEnclHThrd_=bAEnclHThrd_, bRcTask_=_bRCT)
        if _myTB.dtaskUID is None:
            _tp = _tp if fwthrdPrf_ is None else None
            self.__CleanUpOnCtorFailure(md_=self.__md, fwthrdPrf_=_tp, utr_=_utr, tskBadge_=_myTB)
            return

        if _tt.isCFwThread:
            _tecbif = None
        else:
            _tecbif = _FwCallable(self._OnTENotification)
            if not _tecbif.isValid:
                _tp = _tp if fwthrdPrf_ is None else None
                self.__CleanUpOnCtorFailure(md_=self.__md, fwthrdPrf_=_tp, utr_=_utr, tskBadge_=_myTB, terrCIF_=_tecbif)
                return

        if _myTB.hasForeignErrorListnerTaskRight:
            _tskErr = _TaskErrorExtended(self.__md, _myTB, teCBIF_=_tecbif)
        else:
            _tskErr = _FwTaskError(self.__md, _myTB, teCBIF_=_tecbif)

        if _tskErr.taskBadge is None:
            _tp = _tp if fwthrdPrf_ is None else None
            self.__CleanUpOnCtorFailure(md_=self.__md, fwthrdPrf_=_tp, utr_=_utr, tskBadge_=_myTB, terrCIF_=_tecbif, tskError_=_tskErr)
            return

        if txCard_ is None:
            if not bAEnclHThrd_:
                _runPhaseFrequencyMS = 0 if _bEnclHThrd else None
                txCard_ = _TaskXCard(runPhaseFreqMS_=_runPhaseFrequencyMS)
        else:
            txCard_ = txCard_._Clone(bPrint_=True)

        if (txCard_ is not None) and not _myTB.isDrivingXTask:
            txCard_._SetStartArgs(*tuple(_tp.args), **_tp.kwargs)

        self._utConn   = _utc
        self._dHThrd   = _myThrd
        self._tskBadge = _myTB
        self._tskError = _tskErr
        self._tskState = _ts

        self.__ma  = _Mutex()
        self.__xc  = txCard_
        self.__tp  = _tp
        self.__bA  = fwthrdPrf_ is None
        self.__utr = _utr

        if _utr is not None:
            _ag = _UTaskApiGuide(self, _FwThread.__GetExcludedXTaskApiMask(_utr._utAgent))
            if _ag.apiMask is None:
                _ag.CleanUp()

                _tp = _tp if fwthrdPrf_ is None else None
                self.__CleanUpOnCtorFailure(md_=self.__md, fwthrdPrf_=_tp, utr_=_utr, tskBadge_=_myTB, terrCIF_=_tecbif, tskError_=_tskErr)
                return
            else:
                self.__ag = _ag

                self.__CreateExecutorTable()
                if self.__xtors is None:
                    _tp = _tp if fwthrdPrf_ is None else None
                    self.__CleanUpOnCtorFailure(md_=self.__md, fwthrdPrf_=_tp, utr_=_utr, tskBadge_=_myTB, terrCIF_=_tecbif, tskError_=_tskErr)
                    return

        if _utc is not None:
            if not _utc._UpdateUTD(self):
                self.CleanUp()
                return

        _PcErrHandler._SetUpPcEH(self, self.__md)
        if self._isForeignErrorListener is None:
            self.CleanUp()
            return

        if bAEnclHThrd_:
            self._CheckSetTaskState(_TaskState._EState.eRunning)
            self._SetTaskXPhase(_ETaskXPhaseID.eDummyRunningAutoEnclThread)

        if not bAEnclHThrd_:
            if _bAutoStart:
                self.__SyncStart()

    @property
    def _isInvalid(self):
        return self.__md is None

    @property
    def _isAutoStartEnclHThrdEnabled(self) -> bool:
        return False if self.__tp is None else self.__tp.isAutoStartEnclHThrdEnabled

    @property
    def _dxUnit(self):
        return None if self.__utr is None else self.__utr._utAgent._xUnit

    @property
    def _daprofile(self) -> _AbsFwProfile:
       return None if self._isInvalid else self.__dthreadProfile

    @property
    def _xcard(self) -> _TaskXCard:
        return self.__xc

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

    def _PropagateLcProxy(self, lcProxy_ : _ILcProxy =None):
        if self.dHThrd is not None:
            with self.__md:
                if self._PcIsLcProxySet():
                    if self._utConn is not None:
                        self._utConn._PcSetLcProxy(self if lcProxy_ is None else lcProxy_)

    def _GetLcCompID(self) -> _ELcCompID:
        if self._isInvalid:
            res = _ELcCompID.eMiscComp
        elif not self.taskBadge.isXTaskThread:
            res = _ELcCompID.eUThrd if self.isAutoEnclosed else _ELcCompID.eFwThrd
        elif self.taskBadge.isMainXTaskThread:
            res = _ELcCompID.eMainXTask
        else:
            res = _ELcCompID.eXTask
        return res

    def _StartTask(self, semStart_: _BinarySemaphore =None, tskOpPCheck_ : _ATaskOpPreCheck =None, curTask_ : _AbsFwTask =None) -> bool:
        if self.dHThrd is None:
            return False
        if not self._PcIsLcOperable():
            return False

        with self.__ma:
            if self.isEnclosingPyThread:
                if semStart_ is not None:
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00213)
                    return False
            elif not isinstance(semStart_, _BinarySemaphore):
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00214)
                return False

            _oppc = tskOpPCheck_
            if _oppc is None:
                _oppc = _ATaskOpPreCheck(_EATaskOpID.eStart, self._tskState, self._dHThrd, self.isEnclosingPyThread, bReportErr_=True)
            else:
                _oppc.Update(taskOpID_=_EATaskOpID.eStart, bReportErr_=True)

            if _oppc.isNotApplicable or _oppc.isIgnorable:
                _bIgnorable = _oppc.isIgnorable
                if _bIgnorable:
                    if semStart_ is not None:
                        semStart_.Give()
                if tskOpPCheck_ is None:
                    _oppc.CleanUp()
                return _bIgnorable

            elif tskOpPCheck_ is None:
                _oppc.CleanUp()

            if not self.isEnclosingPyThread:
                with self._tstMutex:
                    self.__s = semStart_
                    self._CheckSetTaskState(_TaskState._EState.ePendingRun)

        res     = True
        _lcCID  = self._GetLcCompID()
        _prvBid = None

        if self.taskBadge.isDrivingXTask:
            _prvBid = None if curTask_ is None else curTask_.fwApiBookmarkID

        if self.isEnclosingPyThread:
            if _lcCID.isMainXtask:
                if not self._PcIsMainXTaskStarted():
                    self._PcSetLcOperationalState(_lcCID, True, self)

            if _prvBid is not None:
                curTask_._SetFwApiBookmark(_EFwApiBookmarkID.eXTaskApiBeginActionStart)

            self.__SyncStart()

            if _prvBid is not None:
                curTask_._SetFwApiBookmark(_prvBid)

            if self._isInvalid or self._PcIsLcProxyModeShutdown():
                res = False
            elif _lcCID.isMainXtask:
                if not (self.isFailed or self._PcIsMainXTaskFailed()):
                    if not self._PcIsMainXTaskStopped():
                        self._PcSetLcOperationalState(_lcCID, False, self)

        else:
            if _prvBid is not None:
                curTask_._SetFwApiBookmark(_EFwApiBookmarkID.eXTaskApiBeginActionStart)

            self._SetTaskXPhase(_ETaskXPhaseID.eFwHandling)
            _TaskUtil._StartHThread(self.dHThrd)

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

            if _lcCID.isMainXtask:
                if not (self.isFailed or self._PcIsMainXTaskFailed()):
                    if self.isDone:
                        if not self._PcIsMainXTaskStopped():
                            self._PcSetLcOperationalState(_lcCID, False, self)
                    elif not self._PcIsMainXTaskStarted():
                        self._PcSetLcOperationalState(_lcCID, True, self)
        return res

    def _StopTask(self, bCancel_ =False, semStop_: _BinarySemaphore =None, tskOpPCheck_ : _ATaskOpPreCheck =None, curTask_ : _AbsFwTask =None) -> bool:
        if self.dHThrd is None:
            return False

        with self.__ma:
            if self.isEnclosingPyThread:
                if semStop_ is not None:
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00216)
                    return False
            elif (semStop_ is not None) and not isinstance(semStop_, _BinarySemaphore):
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00217)
                return False
            elif self.__startStopSem is not None:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00218)
                return False

            _oppc = tskOpPCheck_
            _opid = _EATaskOpID.eCancel if bCancel_ else _EATaskOpID.eStop
            if _oppc is None:
                _oppc = _ATaskOpPreCheck(_opid, self._tskState, self._dHThrd, self.isEnclosingPyThread, bReportErr_=True)
            else:
                _oppc.Update(taskOpID_=_opid, bReportErr_=True)
            if _oppc.isNotApplicable or _oppc.isIgnorable:
                _bIgnorable = _oppc.isIgnorable
                if _bIgnorable:
                    if semStop_ is not None:
                        semStop_.Give()
                if tskOpPCheck_ is None:
                    _oppc.CleanUp()
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

            with self.__md:
                if _prvBid is not None:
                    curTask_._SetFwApiBookmark(_prvBid)
        return True

    def _JoinTask(self, timeout_: _Timeout =None, tskOpPCheck_ : _ATaskOpPreCheck =None, curTask_ : _AbsFwTask =None) -> bool:
        if self._isInvalid or (self.dHThrd is None):
            return False
        if timeout_ is not None:
            if not _Timeout.IsTimeout(timeout_, bThrowx_=True):
                return False
            if timeout_.isInfiniteTimeout:
                timeout_ = None

        _midPart = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_001)
        _midPart = _midPart.format(_FwTDbEngine.GetText(_EFwTextID.eMisc_Task), str(self.dtaskName))
        _myLogPrefix = self.__logPrefix

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
            _midPart = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwTask_TID_002).format(_midPart)
            _msg     = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_KeyboardInterrupt).format(_myLogPrefix, _midPart)
            _ssshare._BookKBI(_msg)
        except BaseException as _xcp:
            _xcpCaught = _xcp

        finally:
            if _prvBid is not None:
                curTask_._SetFwApiBookmark(_prvBid)
            if _xcpCaught is not None:
                logif._LogUnhandledXcoBaseXcpEC(_EFwErrorCode.FE_00020, _xcpCaught)

        if not res:
            if _bCSDRunning:
                pass
            elif timeout_ is not None:
                vlogif._LogOEC(False, _EFwErrorCode.VUE_00022)
            else:
                vlogif._LogOEC(False, _EFwErrorCode.VUE_00023)
        return res

    @override
    def _ProcErrorHandlerCallback(self, cbID_ : _EPcErrHandlerCBID, curFE_ : _FatalLog =None, lstFFE_ : list =None) -> _EExecutionCmdID:
        _tailPart = '.' if curFE_ is None else ': [{}] - {}'.format(curFE_.uniqueID, curFE_.shortMessage)

        if cbID_.isFwMainSpecificCallbackID:
            return _EExecutionCmdID.Abort() if self.isAborting else _EExecutionCmdID.Continue()

        _ePF = self.__GetProcessingFeasibility(errLog_=curFE_)
        if not _ePF.isFeasible:
            if _ePF.isUnfeasible:
                res = _EExecutionCmdID.Abort() if self.isAborting else _EExecutionCmdID.Continue()
            else:
                res = _EExecutionCmdID.Abort()
            return res

        if not self.xCard.isLcFailureReportPermissionEnabled:
            vlogif._LogOEC(False, _EFwErrorCode.VUE_00024)
        else:
            _frc   = curFE_
            _myMtx = curFE_._LockInstance()

            if _frc.isInvalid or not _frc.isPendingResolution:
                pass
            else:
                _frcClone = _frc.Clone()
                if _frcClone is None:
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00219)
                else:
                    _myCID = self._GetLcCompID()
                    self._PcNotifyLcFailure(_myCID, _frcClone, atask_=self)

                    _frc._UpdateErrorImpact(_EErrorImpact.eNoImpactByFrcLinkage)

            if not _myMtx is None:
                _myMtx.Give()

        res = _EExecutionCmdID.Abort()
        return res

    @override
    def _PcIsMonitoringLcModeChange(self) -> bool:
        _tskSID = self.dtaskStateID
        return False if _tskSID is None else (_tskSID.isRunning or _tskSID.isStopping)

    @override
    def _PcClientName(self) -> str:
        return self.dtaskName

    @override
    def _PcSelfCheck(self) -> _ETaskSelfCheckResultID:
        return self.__EvaluateSelfCheck()

    @override
    def _PcOnLcCeaseModeDetected(self) -> _EExecutionCmdID:
        if self._isInvalid:
            return _EExecutionCmdID.Abort()

        res = _EExecutionCmdID.Abort() if self.isAborting else _EExecutionCmdID.Stop()

        if self.__isCeaseCapable:
            if not self._isInLcCeaseMode:
                self._CreateCeaseTLB(bEnding_=res.isAbort)
            else:
                self.__UpdateCeaseTLB(res.isAbort)
        return res

    @override
    def _PcOnLcFailureDetected(self) -> _EExecutionCmdID:
        if self._isInvalid:
            return _EExecutionCmdID.Abort()

        res = _EExecutionCmdID.Abort() if self.isAborting else _EExecutionCmdID.Stop()

        if not res.isAbort:
            _bOwnLcFailureSet = False

            _ePF = self.__GetProcessingFeasibility()
            if not _ePF.isFeasible:
                if not (_ePF.isInCeaseMode or _ePF.isOwnLcCompFailureSet):
                    res = _EExecutionCmdID.Abort()

                elif _ePF.isInCeaseMode:
                    pass

                else:
                    _bOwnLcFailureSet = True

            if not res.isAbort:
                if not _bOwnLcFailureSet:
                    if self._PcHasLcAnyFailureState():
                        _bOwnLcFailureSet = self._PcHasLcCompAnyFailureState(self._GetLcCompID(), atask_=self)

                if _bOwnLcFailureSet:
                    res = _EExecutionCmdID.Abort()

        if self.__isCeaseCapable:
            if not self.__isInLcCeaseMode:
                self._CreateCeaseTLB(bEnding_=res.isAbort)
            else:
                self.__UpdateCeaseTLB(res.isAbort)
        return res

    @override
    def _PcOnLcPreShutdownDetected(self) -> _EExecutionCmdID:
        if self._isInvalid:
            return _EExecutionCmdID.Abort()

        res = _EExecutionCmdID.Abort() if self.isAborting else _EExecutionCmdID.Stop()

        if not res.isAbort:
            _bOwnLcFailureSet = False

            _ePF = self.__GetProcessingFeasibility()
            if not _ePF.isFeasible:
                if not (_ePF.isInCeaseMode or _ePF.isOwnLcCompFailureSet):
                    res = _EExecutionCmdID.Abort()

                elif _ePF.isInCeaseMode:
                    pass

                else:
                    _bOwnLcFailureSet = True

            if not res.isAbort:
                if not _bOwnLcFailureSet:
                    if self._PcHasLcAnyFailureState():
                        _bOwnLcFailureSet = self._PcHasLcCompAnyFailureState(self._GetLcCompID(), atask_=self)

                if _bOwnLcFailureSet:
                    res = _EExecutionCmdID.Abort()

        if self.__isCeaseCapable:
            if not self.__isInLcCeaseMode:
                self._CreateCeaseTLB(bEnding_=res.isAbort)
            else:
                self.__UpdateCeaseTLB(res.isAbort)
        return res

    @override
    def _PcOnLcShutdownDetected(self) -> _EExecutionCmdID:
        if self._isInvalid:
            return _EExecutionCmdID.Abort()

        res = _EExecutionCmdID.Abort() if self.isAborting else _EExecutionCmdID.Stop()

        if self.__isCeaseCapable:
            if not self.__isInLcCeaseMode:
                self._CreateCeaseTLB(bEnding_=True)
            else:
                self.__UpdateCeaseTLB(True)
        return res

    @staticmethod
    def _CreateThread( fwthrdPrf_    : _FwThreadProfile =None
                     , utaskConn_    : _IUTaskConn      =None
                     , taskName_     : str              =None
                     , enclHThrd_    : _PyThread        =None
                     , bAEnclHThrd_  : bool             =None
                     , bASEnclHThrd_ : bool             =None
                     , thrdTgtCIF_   : _FwCallable      =None
                     , args_         : list =None
                     , kwargs_       : dict =None
                     , tpAttrs_      : dict =None):
        res = _FwThread( fwthrdPrf_=fwthrdPrf_
                       , utaskConn_=utaskConn_
                       , taskName_=taskName_
                       , enclHThrd_=enclHThrd_
                       , bAEnclHThrd_=bAEnclHThrd_
                       , bASEnclHThrd_=bASEnclHThrd_
                       , thrdTgtCIF_=thrdTgtCIF_
                       , args_=args_
                       , kwargs_=kwargs_
                       , tpAttrs_=tpAttrs_)
        if res.taskBadge is None:
            res.CleanUp()
            res = None
        return res

    @property
    def _isInLcCeaseMode(self):
        return self.__isInLcCeaseMode

    def _CleanUp(self):
        if self._isInvalid:
            return

        _tname = self.__logPrefix

        super()._CleanUp()

        if self.__xtors is not None:
            self.__xtors.CleanUp()
            self.__xtors = None

        if self.__ag is not None:
            self.__ag.CleanUp()

        if self.__xc is not None:
            self.__xc.CleanUp()

        if self.__utr is not None:
            self.__utr.CleanUp()

        if self.__bA:
            if self.__tp is not None:
                _thrdTgt = self.__tp.threadTarget
                if _thrdTgt is not None:
                    _thrdTgt.CleanUp()
                self.__tp.CleanUp()

        self.__s   = None
        self.__ag  = None
        self.__bA  = None
        self.__tp  = None
        self.__xc  = None
        self.__utr = None

        if self.__ma is not None:
            self.__ma.CleanUp()
            self.__ma = None
        self.__md.CleanUp()
        self.__md = None

    def _OnTENotification(self, errLog_: _ErrorLog) -> bool:
        if self._isInvalid:
            return False
        if self._isInLcCeaseMode:
            return False
        if self.isAborting:
            return False
        res = self._AddError(errLog_)
        return res

    def _CreateCeaseTLB(self, bEnding_ =False) -> _LcCeaseTLB:
        if self._isInvalid or not self.__isCeaseCapable:
            res = None
        else:
            res = _AbsFwTask.CreateLcCeaseTLB(self, self.__md, bEnding_)
        return res

    def _CheckSetTaskState(self, newState_ : _TaskState._EState) -> _TaskState._EState:
        res = self.dtaskStateID

        if res is None:
            return None

        with self._tstMutex:
            if newState_.isFailed:
                if not (res.isFailedByXCmdReturn or newState_.isFailedByXCmdReturn):
                    if self.__isReturnedXCmdAbort:
                        _tstate = _TaskState._EState.eFailedByXCmdReturn
                        newState_ = _tstate
            if newState_ != res:
                _utc   = None if self.__utr is None else self.__utr._utaskConn
                _lcCID = self._GetLcCompID()

                if _utc is not None:
                    if newState_.isFailedByXCmdReturn:
                        self._CheckNotifyLcFailure()
                res = _AbsFwTask._SetGetTaskState(self, newState_)

                if res != newState_:
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00220)
                elif _utc is not None:
                    _utc._UpdateUTD(self)
                    if newState_.isTerminated:
                        if newState_.isFailed:
                            pass
                        elif _lcCID.isMainXtask:
                            if not self._PcIsMainXTaskStopped():
                                self._PcSetLcOperationalState(_lcCID, False, self)
            return res

    def _CheckNotifyLcFailure(self) -> bool:
        if self._isInvalid:
            return False

        _myCID = self._GetLcCompID()

        if self._PcHasLcCompAnyFailureState(_myCID, self):
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
                _bXCmdAbort = self.__isReturnedXCmdAbort
                if _bXCmdAbort:
                    _xfph = _StrUtil.DeCapialize(self._GetTaskApiContext().compactName)
                    _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Shared_TID_002).format(self.__logPrefixCtr, _xfph)
                else:
                    _midPart = _FwTDbEngine.GetText(_EFwTextID.eMisc_Task) if self.taskBadge.isDrivingXTask else _FwTDbEngine.GetText(_EFwTextID.eMisc_Thread)
                    _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Shared_TID_001).format(self.__logPrefixCtr, _midPart)

                _bFwThrd  = self.taskBadge.isFwThread
                _errCode  = _EFwErrorCode.FE_00023 if _bFwThrd else _EFwErrorCode.FE_00924
                _frc      = logif._CreateLogFatalEC(_bFwThrd, _errCode, _errMsg, bDueToExecCmdAbort_=_bXCmdAbort)
                _myMtx    = None if _frc is None else _frc._LockInstance()

        if _frc is not None:
            _frcClone = _frc.Clone()
            if _frcClone is None:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00221)
            else:
                res = True
                self._PcNotifyLcFailure(_myCID, _frcClone, atask_=self)
                _frc._UpdateErrorImpact(_EErrorImpact.eNoImpactByFrcLinkage)

            if _myMtx is not None:
                _myMtx.Give()
        return res

    def _SendMessage(self, msg_: _IFwMessage) -> bool:
        if _ssshare._WarnOnDisabledSubsysMsg():
            return False
        if _FwSubsysCoding.IsSenderExternalQueueSupportMandatory():
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00948)
            return False

        _fwDisp = _FwThread.__FwDispRbl
        if _fwDisp is None:
            _fwDisp = _AbsFwService._GetFwsInstance(_EFwsID.eFwsDisp)
            if _fwDisp is None:
                return False
            _FwThread.__FwDispRbl = _fwDisp

        if (msg_ is None) or not msg_.isValid:
            return False
        if self._isInvalid or self._isInLcCeaseMode or self.isAborting or not self.isStarted:
            return False

        _hdr = msg_.header
        if not (_hdr.typeID.isTIntraProcess and (_hdr.channelID.isChInterTask or _hdr.channelID.isChIntraTask)):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00949)
            return False
        if _hdr.isInternalMsg:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00950)
            return False

        _actx = self._GetTaskApiContext()
        if not (self.isRunning or (self.isStopping and _actx.isTeardown)):
            return False

        return _fwDisp._DispatchMessage(msg_)

    @property
    def __isCeaseCapable(self):
        return (self.lcDynamicTLB is not None) and not self.lcDynamicTLB.isDummyTLB

    @property
    def __isInLcCeaseMode(self):
        return not self.__lcCeaseState.isNone

    @property
    def __isReturnedXCmdAbort(self):
        return (self.__ag is not None) and (self.__ag._xcmdReturn is not None) and self.__ag._xcmdReturn.isAbort

    @property
    def __logPrefix(self):
        res  = _FwTDbEngine.GetText(_EFwTextID.eMisc_LogPrefix_Thread)
        res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_010).format(self.dtaskName)
        return res

    @property
    def __logPrefixCtr(self):
        res  = _FwTDbEngine.GetText(_EFwTextID.eMisc_LogPrefix_Thread)
        res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_010).format(self.dtaskName)
        res += _FwTDbEngine.GetText(_EFwTextID.eMisc_LogPrefix_ExecCounter).format(self.xrNumber)
        return res

    @property
    def __startStopSem(self):
        if self._isInvalid:
            return None
        with self._tstMutex:
            return self.__s

    @property
    def __dthreadProfile(self):
        return self.__tp

    @property
    def __lcCeaseState(self) -> _ELcCeaseTLBState:
        if self._isInvalid:
            res = _ELcCeaseTLBState.eNone
        else:
            res = self.ceaseTLBState
        return res

    @staticmethod
    def __GetExcludedXTaskApiMask(uta_ : _IUTAgent) -> _EUTaskApiFuncTag:
        res  = _EUTaskApiFuncTag.DefaultApiMask()
        _utp = uta_.taskProfile

        if not _utp.isSetupPhaseEnabled:
            res = _EUTaskApiFuncTag.AddApiFuncTag(eApiMask_=res, apiFTag_=_EUTaskApiFuncTag.eXFTSetUpXTask)

        if not _utp.isTeardownPhaseEnabled:
            res = _EUTaskApiFuncTag.AddApiFuncTag(eApiMask_=res, apiFTag_=_EUTaskApiFuncTag.eXFTTearDownXTask)
        return res

    def __UpdateCeaseTLB(self, bEnding_ : bool):
        _ctlb = self._lcCeaseTLB
        if _ctlb is not None:
            _ctlb.UpdateCeaseState(bEnding_)

    def __RunThrdTgt(self):
        _bError = False
        if not self.isStarted:
            _bError = True
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00222)
        elif self.isEnclosingPyThread:
            _bError = True
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00223)
        elif self.__startStopSem is None:
            _bError = True
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00224)

        if _bError:
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

        _bXT = self.taskBadge.isDrivingXTask

        _myArgs    = None
        _myKwargs  = None
        _myThrdTgt = None

        if not _bXT:
            _tp = self.__dthreadProfile
            _myArgs, _myKwargs = _tp.args, _tp.kwargs
            _myThrdTgt = _tp.threadTarget
        else:
            _AbsFwTask.CreateLcTLB(self)

        with self._tstMutex:
            _semSS = self.__s
            self.__s = None

        _semSS.Give()

        if not _bXT:
            self._SetTaskXPhase(_ETaskXPhaseID.eRunningNonDrivingXTaskASyncThread)
            _myThrdTgt(*_myArgs, **_myKwargs)

            if not self.isTerminated:
                if self.isAborting:
                    _nts = _TaskState._EState.eFailed
                else:
                    _nts = _TaskState._EState.eCanceled if self.isCanceling else _TaskState._EState.eDone
                self._CheckSetTaskState(_nts)
        else:
            self._SetTaskXPhase(_ETaskXPhaseID.eFwHandling)
            self.__ExecuteXTask()

        _srg = _SyncResourcesGuard._GetInstance()
        if _srg is not None:
            _srg.ReleaseAcquiredSyncResources(self.dtaskUID)

    def __SyncStart(self):
        self._CheckSetTaskState(_TaskState._EState.eRunning)

        if not self.taskBadge.isDrivingXTask:
            self._SetTaskXPhase(_ETaskXPhaseID.eRunningNonDrivingXTaskSyncThread)

        else:
            _AbsFwTask.CreateLcTLB(self)

            self._SetTaskXPhase(_ETaskXPhaseID.eFwHandling)
            self.__ExecuteXTask()

    def __ExecuteXTask(self):
        _caughtXcp = True

        try:
            self._SetTaskApiContext(_ETaskApiContextID.eSetup)
            self.__ExecuteSetupXTask()
            self._SetTaskApiContext(_ETaskApiContextID.eDontCare)

            if self.isRunning:
                self._SetTaskApiContext(_ETaskApiContextID.eRun)

                self.__ExecuteRunXTask()
                self._SetTaskApiContext(_ETaskApiContextID.eDontCare)

                if not self.isAborting:
                    if not self.__isInLcCeaseMode:
                        if not (self.__isCeaseCapable and self.lcDynamicTLB.isLcShutdownEnabled):
                            if self.__ag.isProvidingTearDownXTask:
                                self._SetTaskApiContext(_ETaskApiContextID.eTeardown)
                                self.__ExecuteTeardownXTask()
                                self._SetTaskApiContext(_ETaskApiContextID.eDontCare)

        except _XcoXcpRootBase as _xcp:
            _caughtXcp = True
            self.__HandleException(_xcp, bCaughtByApiExecutor_=False)
        except BaseException as _xcp:
            _caughtXcp = True
            _xcp = _XcoBaseException(_xcp, tb_=logif._GetFormattedTraceback())
            self.__HandleException(_xcp, bCaughtByApiExecutor_=False)

        finally:
            if self._isInvalid:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00225)
            else:
                if not self.isTerminating:
                    if _caughtXcp:
                        _st = _TaskState._EState.eProcessingAborted
                    else:
                        _st = _TaskState._EState.eProcessingStopped
                    self._CheckSetTaskState(_st)

                _semStop = None
                with self._tstMutex:
                    if self.__s is not None:
                        _semStop = self.__s
                        self.__s = None

                if _semStop is not None:
                    _semStop.Give()

                if self.isTerminated:
                    if self.taskBadge.isDrivingXTask:
                        if self.__ag.isProvidingTearDownXTask:
                            self._PcGetTTaskMgr()._DetachTask(self)

                self.__PreProcessCeaseMode()

                self.__ProcessCeaseMode()

                if self._isInvalid:
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00226)
                else:
                    if self.isAborting:
                        _nts = _TaskState._EState.eFailed
                    else:
                        _nts = _TaskState._EState.eCanceled if self.isCanceling else _TaskState._EState.eDone
                    self._CheckSetTaskState(_nts)

    def __ExecuteSetupXTask(self):
        _xres = _EExecutionCmdID.Continue()

        if self.__ag.isProvidingSetUpXTask:
            _xtor = self.__xtors._GetApiExecutor(_EUTaskApiFuncTag.eXFTSetUpXTask)
            _xres = self.__EvaluateExecResult(executor_=_xtor, bCheckBefore_=False, abortState_=_TaskState._EState.eSetupAborted)
        return _xres

    def __ExecuteTeardownXTask(self):
        _xres = _EExecutionCmdID.Continue()

        if self.__ag.isProvidingTearDownXTask:
            self.__ClearCurUserError()

            _xtor = self.__xtors._GetApiExecutor(_EUTaskApiFuncTag.eXFTTearDownXTask)
            _xres = self.__EvaluateExecResult(executor_=_xtor, bCheckBefore_=False, abortState_=_TaskState._EState.eTeardownAborted)
        return _xres

    def __ExecuteRunXTask(self):
        _MM_FMT_STR = None

        _utc        = None if self.__utr is None else self.__utr._utaskConn
        _xres       = _EExecutionCmdID.Continue()
        _runCycleMS = self.xCard.runPhaseFreqMS

        _bBreak = False
        while True:
            if _bBreak:
                break

            if not _xres.isContinue:
                break

            try:
                if self._isInvalid is None:
                    return _EExecutionCmdID.Abort()

                self._IncEuRNumber()
                if _utc is not None:
                    _utc._IncEuRNumber()
                self.__ClearCurUserError()

                _xtor = self.__xtors._GetApiExecutor(_EUTaskApiFuncTag.eXFTRunXTask)
                _xres = self.__EvaluateExecResult(executor_=_xtor, bCheckBefore_=True)

                if not _xres.isContinue:
                    break
                elif not self.isRunning:
                    _xres = self.__EvaluateExecResult(xres_=None if self.isAborting else False, bCheckBefore_=None)

            except _XcoXcpRootBase as _xcp:
                _xres = self.__HandleException(_xcp, bCaughtByApiExecutor_=False)
            except BaseException as _xcp:
                _xcp  = _XcoBaseException(_xcp, tb_=logif._GetFormattedTraceback())
                _xres = self.__HandleException(_xcp, bCaughtByApiExecutor_=False)

            finally:
                if not _xres.isContinue:
                    _bBreak = True
                elif _runCycleMS == 0:
                    _xres = _EExecutionCmdID.Stop()
                    if self.isRunning:
                        self._CheckSetTaskState(_TaskState._EState.eProcessingStopped)
                    _bBreak = True
                else:
                    _TaskUtil.SleepMS(_runCycleMS)

        return _xres

    def __EvaluateExecResult( self
                            , executor_                          =None
                            , xres_         : _EExecutionCmdID   =None
                            , bCheckBefore_ : bool               =None
                            , abortState_   : _TaskState._EState =None
                            , bSkipErrProc_ : bool               =False) -> _EExecutionCmdID:
        if not ((executor_ is None) or isinstance(executor_, _XTaskApiExecutor)):
            self.__ag._SetGetReturnedExecCmd(None, bApplyConvertBefore_=False)
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00227)
            return _EExecutionCmdID.Abort()
        if not ((xres_ is None) or isinstance(xres_, (_EExecutionCmdID, bool))):
            self.__ag._SetGetReturnedExecCmd(None, bApplyConvertBefore_=False)
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00228)
            return _EExecutionCmdID.Abort()

        _bDoCheckAfter  = False
        _bDoCheckBefore = False

        if bCheckBefore_ is not None:
            _bDoCheckBefore = bCheckBefore_
            _bDoCheckAfter  = not _bDoCheckBefore

        res = _EExecutionCmdID.Continue()

        self.__ag._SetGetReturnedExecCmd(xres_, bApplyConvertBefore_=False)

        if _bDoCheckBefore and self._PcIsMonitoringLcModeChange():
            _newMode = self._PcCheckLcOperationModeChange()
            if (_newMode is not None) and not _newMode.isLcNormal:
                if _newMode.isLcCeaseMode:
                    res = self._PcOnLcCeaseModeDetected()
                elif _newMode.isLcFailureHandling:
                    res = self._PcOnLcFailureDetected()
                elif _newMode.isLcPreShutdown:
                    res = self._PcOnLcPreShutdownDetected()
                elif _newMode.isLcShutdown:
                    res = self._PcOnLcShutdownDetected()
        if not res.isContinue:
            pass
        else:
            if executor_ is None:
                res = _EExecutionCmdID.ConvertFrom(xres_)
                if res.isStop and self.isCanceling:
                    res = _EExecutionCmdID.Cancel()
            else:
                res = executor_.Execute()

            if not res.isContinue:
                pass
            elif _bDoCheckAfter and self._PcIsMonitoringLcModeChange():
                _newMode = self._PcCheckLcOperationModeChange()
                if (_newMode is not None) and not _newMode.isLcNormal:
                    if _newMode.isLcCeaseMode:
                        res = self._PcOnLcCeaseModeDetected()
                    elif _newMode.isLcFailureHandling:
                        res = self._PcOnLcFailureDetected()
                    elif _newMode.isLcPreShutdown:
                        res = self._PcOnLcPreShutdownDetected()
                    elif _newMode.isLcShutdown:
                        res = self._PcOnLcShutdownDetected()

        if not res.isContinue:
            pass
        elif self.isAborting or self._isInLcCeaseMode:
            pass
        elif bSkipErrProc_:
            pass
        else:
            res = self._ProcErrors()

        if self._selfCheckResult._isScrNOK:
            pass
        elif not res.isContinue:
            _nst = None

            if res.isAbort:
                if not self.isAborting:
                    if abortState_ is None:
                        abortState_ = _TaskState._EState.eProcessingAborted
                    _nst = abortState_
            else:
                if self.isRunning or self.isPendingStopRequest or self.isPendingCancelRequest:
                    _bCancel = res.isCancel
                    _nst = _TaskState._EState.eProcessingCanceled if _bCancel else _TaskState._EState.eProcessingStopped
            if _nst is not None:
                self._CheckSetTaskState(_nst)
        return res

    def __EvaluateSelfCheck(self) -> _ETaskSelfCheckResultID:
        if self._isInvalid:
            return _ETaskSelfCheckResultID.eScrStop

        res = self._selfCheckResult
        if res._isScrNOK or not self.isStarted:
            return res

        if self._isInLcCeaseMode:
            return _ETaskSelfCheckResultID.eScrStop

        if not self.isRunning:
            if self.isAborting or self.isFailed:
                res = _ETaskSelfCheckResultID.eScrAbort
            elif not self._GetTaskApiContext().isTeardown:
                res = _ETaskSelfCheckResultID.eScrStop
            return res

        _ret = _EExecutionCmdID.Continue()

        _newMode = self._PcCheckLcOperationModeChange()
        if (_newMode is not None) and not _newMode.isLcNormal:
            if _newMode.isLcCeaseMode:
                _ret = self._PcOnLcCeaseModeDetected()
            elif _newMode.isLcFailureHandling:
                _ret = self._PcOnLcFailureDetected()
            elif _newMode.isLcPreShutdown:
                _ret = self._PcOnLcPreShutdownDetected()
            elif _newMode.isLcShutdown:
                _ret = self._PcOnLcShutdownDetected()

        if _ret.isContinue and self._isInLcCeaseMode:
            _ret = _EExecutionCmdID.Stop()
        if not _ret.isContinue:
            res = _ETaskSelfCheckResultID.eScrAbort if _ret.isAbort else _ETaskSelfCheckResultID.eScrStop
            self._CheckSetTaskState(_TaskState._EState.eProcessingStopped)
        else:
            res = _ETaskSelfCheckResultID.eScrOK

        if _ret.isContinue != self.isRunning:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00974)
        return res

    def __HandleException(self, xcp_ : _XcoXcpRootBase, bCaughtByApiExecutor_ =True) -> _EExecutionCmdID:
        if self._isInvalid:
            return _EExecutionCmdID.Abort()

        with self.__md:
            _xcoXcp = None if _IsXTXcp(xcp_) else xcp_
            _xbx    = None if (_xcoXcp is None) or not isinstance(_xcoXcp, _XcoBaseException) else _xcoXcp

            if _xbx is not None:
                if xcp_.xcpType.isBaseExceptionAtrributeError:
                    _xmlrMsg = _FwThread.__XR_XCP_DW

                    if xcp_.shortMessage == _xmlrMsg:
                        return _EExecutionCmdID.MapExecState2ExecCmdID(self)
            if self.isAborting:
                pass
            elif _xbx is not None:
                self._ProcUnhandledXcp(_xbx)

            self._SetTaskXPhase(_ETaskXPhaseID.eFwHandling)

            if not self.isAborting:
                if not bCaughtByApiExecutor_:
                    _procRes = self._ProcErrors()

                    if not _procRes.isContinue:
                        if _procRes.isAbort:
                            _nst = _TaskState._EState.eProcessingAborted
                        else:
                            if _procRes.isStop and self.isCanceling:
                                _procRes = _EExecutionCmdID.Cancel()

                            _nst = _TaskState._EState.eProcessingCanceled if _procRes.isCancel else _TaskState._EState.eProcessingStopped
                        self._CheckSetTaskState(_nst)

            if not self.isRunning:
                if self.isAborting:
                    res = _EExecutionCmdID.Abort()
                else:
                    res = _EExecutionCmdID.Cancel() if self.isCanceling else _EExecutionCmdID.Stop()

            else:
                res = _EExecutionCmdID.Continue()
            return res

    def __GetProcessingFeasibility(self, errLog_: _ErrorLog =None) -> _EProcessingFeasibilityID:
        res = _EProcessingFeasibilityID.eFeasible

        if self._isInvalid:
            res = _EProcessingFeasibilityID.eUnfeasible
        elif self._PcIsLcProxyModeShutdown():
            res = _EProcessingFeasibilityID.eLcProxyUnavailable
        elif not self._PcIsLcCoreOperable():
            res = _EProcessingFeasibilityID.eLcCoreInoperable
        elif self.isAborting:
            res = _EProcessingFeasibilityID.eAborting
        elif self.__isInLcCeaseMode:
            res = _EProcessingFeasibilityID.eInCeaseMode

        _frcv = None
        if res.isFeasible:
            if self._PcHasLcAnyFailureState():
                _frcv = self._PcGetLcCompFrcView(self._GetLcCompID(), atask_=self)
                if _frcv is not None:
                    res = _EProcessingFeasibilityID.eOwnLcCompFailureSet

            if res.isFeasible:
                if (errLog_ is not None) and errLog_.hasNoErrorImpact:
                    res = _EProcessingFeasibilityID.eUnfeasible

        if not res.isFeasible:
            if errLog_ is not None:
                if errLog_.IsMyTaskError(self.dtaskUID):
                    errLog_._UpdateErrorImpact(_EErrorImpact.eNoImpactByOwnerCondition)
        if _frcv is not None:
            _frcv.CleanUp()
        return res

    def __CreateExecutorTable(self):
        _dictExecutors = dict()
        for _n, _m in _EUTaskApiFuncTag.__members__.items():
            if not _m.isXTaskExecutionAPI:
                continue
            if not self.__ag._IsProvidingApiFunction(apiFTag_=_m):
                continue
            _dictExecutors[_m] = _XTaskApiExecutor(self.__ag, _m, self.__HandleException)

        self.__xtors = _FwThread._XTaskExecutorTable(_dictExecutors)

    def __ClearCurUserError(self):
        _tskErr = self.taskError
        if (_tskErr is not None) and _tskErr.isUserError:
            _tskErr.ClearError()

    def __EvaluateCtorParams( self
                            , fwthrdPrf_    : _FwThreadProfile =None
                            , utaskConn_    : _IUTaskConn      =None
                            , taskName_     : str              =None
                            , enclHThrd_    : _PyThread        =None
                            , bASEnclHThrd_ : bool             =None
                            , thrdTgtCIF_   : _FwCallable      =None
                            , args_         : list =None
                            , kwargs_       : dict =None
                            , tpAttrs_      : dict =None):
        _ts    = None
        _mytp  = fwthrdPrf_
        _valid = True

        if _mytp is None:
            _mytp = _FwThreadProfile( utaskConn_=utaskConn_
                                    , taskName_=taskName_
                                    , enclHThrd_=enclHThrd_
                                    , bASEnclHThrd_=bASEnclHThrd_
                                    , thrdTgtCIF_=thrdTgtCIF_
                                    , args_=args_
                                    , kwargs_=kwargs_
                                    , tpAttrs_=tpAttrs_)
        if not isinstance(_mytp, _FwThreadProfile):
            _valid = False
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00229)
        elif not (_mytp.isValid and _mytp.taskRightsMask is not None):
            _valid = False
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00230)
        elif _mytp.isEnclosingPyThread and not _mytp.enclosedPyThread.is_alive():
            _valid = False
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00231)

        if not _valid:
            if (_mytp is not None) and fwthrdPrf_ is None:
                _mytp.CleanUp()
            _ts, _mytp = None, None
        else:
            _ts = _TaskState(self, _TaskState._EState.eInitialized, mtx_=self._tstMutex)
        return _ts, _mytp

    def __CleanUpOnCtorFailure( self
                              , tskError_  =None
                              , terrCIF_   =None
                              , tskBadge_  =None
                              , utr_       =None
                              , fwthrdPrf_ =None
                              , ma_        =None
                              , md_        =None):
        if tskError_  is not None: tskError_.CleanUp()
        if terrCIF_   is not None: terrCIF_.CleanUp()
        if tskBadge_  is not None: tskBadge_.CleanUp()
        if utr_       is not None: utr_.CleanUp()
        if fwthrdPrf_ is not None: fwthrdPrf_.CleanUp()
        if ma_        is not None: ma_.CleanUp()
        if md_        is not None: md_.CleanUp()

        self.__s   = None
        self.__bA  = None
        self.__ma  = None
        self.__md  = None
        self.__tp  = None
        self.__utr = None

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
                    self._CreateCeaseTLB(bEnding_=self.isAborting)

    def __ProcessCeaseMode(self):
        if self._isInvalid:
            return

        if not self.__isInLcCeaseMode:
            return

        _eCurCS = self.__lcCeaseState
        if _eCurCS.isPrepareCeasing:
            self.__PrepareDefaultCeasing()
            _eCurCS = self.__lcCeaseState
        if _eCurCS.isEnterCeasing:
            self.__EnterDefaultCeasing()
            _eCurCS = self.__lcCeaseState
        if _eCurCS.isEndingCease:
            self.__ProcessLeavingCease()
            _eCurCS = self.__lcCeaseState

        if not _eCurCS.isDeceased:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00232)

    def __PrepareDefaultCeasing(self):
        if not self.__isInLcCeaseMode:
            return

        _eCurCS = self.__lcCeaseState
        if not _eCurCS.isPrepareCeasing:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00233)
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

        self._lcCeaseTLB.HopToNextCeaseState(bEnding_=self.isAborting)

    def __EnterDefaultCeasing(self):
        if not self.__isInLcCeaseMode:
            return

        _eCurCS = self.__lcCeaseState
        if not _eCurCS.isEnterCeasing:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00234)
            self._lcCeaseTLB.UpdateCeaseState(True)
            return

        self._lcCeaseTLB.HopToNextCeaseState(bEnding_=self.isAborting)

        _bPreShutdownPassed = False
        while True:
            if not self._lcCeaseTLB.isCeasing:
                break

            self._lcCeaseTLB.IncrementCeaseAliveCounter()

            _TaskUtil.SleepMS(self.xCard.cyclicCeaseTimespanMS)

            if self._isInvalid:
                break
            if not self._lcCeaseTLB.isCeasing:
                self._lcCeaseTLB.UpdateCeaseState(True)
                break
            if not _bPreShutdownPassed:
                if self._lcCeaseTLB._isPreShutdownGateOpened:
                    _bPreShutdownPassed = True

                    if not self._PcHasLcAnyFailureState():
                        self.__ExecuteTeardownXTask()

                    self._lcCeaseTLB.HopToNextCeaseState(bEnding_=self.isAborting)
                    continue

            if self._lcCeaseTLB._isShutdownGateOpened:
                break
        if self._lcCeaseTLB is not None:
            self._lcCeaseTLB.HopToNextCeaseState(bEnding_=self.isAborting)

    def __ProcessLeavingCease(self):
        if not self.__isInLcCeaseMode:
            return

        _eCurCS = self.__lcCeaseState
        if not self._lcCeaseTLB.isEndingCease:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00235)
            if self._lcCeaseTLB.isDeceased:
                return
            self._lcCeaseTLB.UpdateCeaseState(True)

        while True:
            if (not self._lcCeaseTLB.isCoordinatedShutdownRunning) or self._lcCeaseTLB.isCoordinatedShutdownGateOpened:
                break

            self._lcCeaseTLB.IncrementCeaseAliveCounter()

            _TaskUtil.SleepMS(self.xCard.cyclicCeaseTimespanMS)
            if self._isInvalid:
                break

            _eCSR = self._lcCeaseTLB.curShutdownRequest
            if (_eCSR is None) or _eCSR.isShutdown:
                break
            continue

        if self._lcCeaseTLB is not None:
            self._lcCeaseTLB.HopToNextCeaseState(bEnding_=True)

class _XTaskApiExecutor(_AbsSlotsObject):
    __slots__ = [ '__er' , '__ag' , '__bTD' , '__af' , '__fid' , '__ht' , '__xph' , '__xh' ]

    def __init__(self, apiGuide_  : _UTaskApiGuide, fid_ : _EUTaskApiFuncTag, xcpHdlr_):
        super().__init__()
        self.__af  = None
        self.__ag  = apiGuide_
        self.__er  = None
        self.__ht  = None
        self.__xh  = xcpHdlr_
        self.__bTD = False
        self.__fid = fid_
        self.__xph = None

        if not isinstance(fid_, _EUTaskApiFuncTag):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00236)
            self.CleanUp()
        elif xcpHdlr_ is None:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00237)
            self.CleanUp()
        elif not isinstance(apiGuide_, _UTaskApiGuide):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00238)
            self.CleanUp()
        elif not isinstance(apiGuide_._fwThread, _FwThread):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00239)
            self.CleanUp()
        elif not fid_.isXTaskExecutionAPI:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00240)
            self.CleanUp()
        elif self.__SetApiFunc() is None:
            self.CleanUp()
        else:
            _txph = fid_.MapToTaskExecutionPhaseID()
            if _txph.isNA:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00241)
                self.CleanUp()
            else:
                self.__ht  = apiGuide_._fwThread
                self.__xph = _txph

    @property
    def executionResult(self) -> _EExecutionCmdID:
        return self.__er

    def Execute(self) -> _EExecutionCmdID:
        if self.__isInvalid:
            return _EExecutionCmdID.Abort()
        if self.__af is None:
            if self.__er is not None:
                self.__er = _EExecutionCmdID.Abort()
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00242)
            return _EExecutionCmdID.Abort()

        _ret = None

        try:
            self.__ht._SetTaskXPhase(self.__eTaskExecPhase)

            if self.__fid == _EUTaskApiFuncTag.eXFTTearDownXTask:
                if self.__bTD:
                    _ret = _EExecutionCmdID.Stop()
                else:
                    self.__bTD = True
                    _ret = self.__af()

            elif self.__fid == _EUTaskApiFuncTag.eXFTSetUpXTask:
                _args   = self.__ht._xcard.args
                _kwargs = self.__ht._xcard.kwargs
                _ret    = self.__af(*_args, **_kwargs)

            elif not self.__ag.isProvidingSetUpXTask:
                _args   = self.__ht._xcard.args
                _kwargs = self.__ht._xcard.kwargs
                _ret    = self.__af(*_args, **_kwargs)

            else:
                _ret = self.__af()

            if (_ret is not None) and not isinstance(_ret, (EExecutionCmdID, _EExecutionCmdID, bool)):
                logif._LogErrorEC(_EFwErrorCode.UE_00258, _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_BAD_XCMD_RETURN_TYPE).format(type(_ret).__name__))
                _ret = _EExecutionCmdID.Stop()
            self.__ht._SetTaskXPhase(_ETaskXPhaseID.eFwHandling)

            _bScrNOK = self.__ht._selfCheckResult._isScrNOK

            if _bScrNOK:
                _ret = _EExecutionCmdID.MapExecState2ExecCmdID(self)

            _ret = self.__ag._SetGetReturnedExecCmd(_ret)

            if _bScrNOK:
                pass

            elif _ret.isAbort:
                self.__ht._CheckSetTaskState(_TaskState._EState.eProcessingAborted)

                self.__ht._CheckNotifyLcFailure()

        except _XcoXcpRootBase as _xcp:
            if _IsXTXcp(_xcp):
                raise _xcp
            _ret = self.__xh(xcp_=_xcp, bCaughtByApiExecutor_=True)

        except BaseException as _xcp:
            _xcp = _XcoBaseException(_xcp, tb_=logif._GetFormattedTraceback())
            _ret  = self.__xh(xcp_=_xcp, bCaughtByApiExecutor_=True)

        finally:
            self.__er = _EExecutionCmdID.ConvertFrom(_ret)
        return self.__er

    def _ToString(self):
        if self.__isInvalid:
            return None
        return _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_002).format(type(self).__name__, self.__ht.dtaskName, self.__fid.functionName)

    def _CleanUp(self):
        self.__af  = None
        self.__ag  = None
        self.__er  = None
        self.__ht  = None
        self.__xh  = None
        self.__bTD = None
        self.__fid = None
        self.__xph = None

    @property
    def __isInvalid(self):
        return (self.__ag is None) or (self.__fid is None)

    @property
    def __logPrefix(self):
        if self.__isInvalid:
            return None

        res = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_003)
        return res.format(self.__ht.dtaskName, self.__fid.functionName)

    @property
    def __eTaskExecPhase(self) -> _ETaskXPhaseID:
        return self.__xph

    def __SetApiFunc(self):
        if self.__isInvalid:
            return None

        res             = None
        _bUnexpectedErr = False

        if self.__fid == _EUTaskApiFuncTag.eXFTRunXTask:
            res = self.__ag.runXTask

        elif self.__fid == _EUTaskApiFuncTag.eXFTSetUpXTask:
            res = self.__ag.setUpXTask

        elif self.__fid == _EUTaskApiFuncTag.eXFTTearDownXTask:
            res = self.__ag.tearDownXTask

        else:
            _bUnexpectedErr = True
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00243)

        if res is None:
            if not _bUnexpectedErr:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00244)
        else:
            self.__af = res
        return res
