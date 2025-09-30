# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : taskmgrimpl.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from collections import OrderedDict as _PyOrderedDict
from typing      import List
from typing      import Tuple
from typing      import Union

from xcofdk.fwcom     import EExecutionCmdID
from xcofdk.fwapi.xmt import IXTask

from _fw.fwssys.assys                      import fwsubsysshare as _ssshare
from _fw.fwssys.assys.ifs                  import _IUTaskConn
from _fw.fwssys.assys.ifs.ifutagent        import _IUTAgent
from _fw.fwssys.assys.ifs.iftmgrimpl       import _ITMgrImpl
from _fw.fwssys.assys.ifs.tiftmgr          import _ITTMgr
from _fw.fwssys.fwcore.logging             import logif
from _fw.fwssys.fwcore.logging             import vlogif
from _fw.fwssys.fwcore.base.fwcallable     import _FwCallable
from _fw.fwssys.fwcore.base.gtimeout       import _Timeout
from _fw.fwssys.fwcore.base.util           import _Util
from _fw.fwssys.fwcore.ipc.fws.afwservice  import _AbsRunnable
from _fw.fwssys.fwcore.ipc.sync.mutex      import _Mutex
from _fw.fwssys.fwcore.ipc.sync.semaphore  import _BinarySemaphore
from _fw.fwssys.fwcore.ipc.tsk.afwtask     import _AbsFwTask
from _fw.fwssys.fwcore.ipc.tsk.ataskop     import _EATaskOpID
from _fw.fwssys.fwcore.ipc.tsk.ataskop     import _ATaskOpPreCheck
from _fw.fwssys.fwcore.ipc.tsk.fwtask      import _FwTask
from _fw.fwssys.fwcore.ipc.tsk.taskdefs    import _ETaskSelfCheckResultID
from _fw.fwssys.fwcore.ipc.tsk.fwthread    import _FwThread
from _fw.fwssys.fwcore.ipc.tsk.taskbadge   import _TaskBadge
from _fw.fwssys.fwcore.ipc.tsk.fwtaskerror import _FwTaskError
from _fw.fwssys.fwcore.ipc.tsk.taskmgr     import _TaskManager
from _fw.fwssys.fwcore.ipc.tsk.fwtaskprf   import _FwTaskProfile
from _fw.fwssys.fwcore.ipc.tsk.taskstate   import _TaskState
from _fw.fwssys.fwcore.ipc.tsk.fwthreadprf import _FwThreadProfile
from _fw.fwssys.fwcore.ipc.tsk.taskutil    import _TaskUtil
from _fw.fwssys.fwcore.ipc.tsk.taskutil    import _ETaskRightFlag
from _fw.fwssys.fwcore.ipc.tsk.taskutil    import _ETaskResFlag
from _fw.fwssys.fwcore.ipc.tsk.taskutil    import _EFwApiBookmarkID
from _fw.fwssys.fwcore.ipc.tsk.taskutil    import _AutoEnclosedThreadsBag
from _fw.fwssys.fwcore.ipc.tsk.taskutil    import _PyThread
from _fw.fwssys.fwcore.lc.lcdefines        import _ELcCompID
from _fw.fwssys.fwcore.lc.ifs.iflcproxy    import _ILcProxy
from _fw.fwssys.fwcore.lc.lcproxyclient    import _LcProxyClient
from _fw.fwssys.fwcore.lc.lcmn.lcmonimpl   import _LcMonitorImpl
from _fw.fwssys.fwcore.types.aobject       import _AbsSlotsObject
from _fw.fwssys.fwcore.types.commontypes   import override
from _fw.fwssys.fwcore.types.commontypes   import _CommonDefines
from _fw.fwssys.fwcore.types.commontypes   import _EDepInjCmd
from _fw.fwssys.fwcore.types.afwprofile    import _AbsFwProfile
from _fw.fwssys.fwmsg.msg                  import _EMessagePeer
from _fw.fwssys.fwmt.utask.usertaskrbl     import _UserTaskRbl
from _fw.fwssys.fwerrh.fwerrorcodes        import _EFwErrorCode
from _fw.fwssys.fwerrh.logs.xcoexception   import _XcoXcpRootBase
from _fw.fwssys.fwerrh.logs.xcoexception   import _XcoBaseException

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _TaskEntry(_AbsSlotsObject):
    __slots__ = ['__ti']

    def __init__(self, taskInst_: _AbsFwTask):
        super().__init__()
        self.__ti = None

        if not _Util.IsInstance(taskInst_, _AbsFwTask):
            self.CleanUp()
        else:
            self.__ti = taskInst_

    @property
    def teTaskID(self) -> int:
        res = self.teTaskBadge
        return None if res is None else res.dtaskUID

    @property
    def teTaskName(self) -> str:
        res = self.teTaskBadge
        return None if res is None else res.dtaskName

    @property
    def teTaskUniqueName(self) -> str:
        res = self.teTaskBadge
        return None if res is None else res.dtaskName

    @property
    def teTaskBadge(self) -> _TaskBadge:
        return None if self.__ti is None else self.__ti.taskBadge

    @property
    def teTaskError(self) -> _FwTaskError:
        return None if self.__ti is None else self.__ti.taskError

    @property
    def teTaskInst(self) -> _AbsFwTask:
        return self.__ti

    @property
    def teIsAutoEnclosedEntry(self) -> bool:
        return False if self.__ti is None else self.__ti.isAutoEnclosed

    @property
    def teIsJoinableEntry(self) -> bool:
        if (self.__ti is None) or (self.__ti.taskBadge is None):
            return False
        return _ATaskOpPreCheck.IsJoinableHostThread(self.__ti.dHThrd)

    @property
    def teIsXTaskEntry(self) -> bool:
        _tb = None if self.__ti is None else self.__ti.taskBadge
        return False if _tb is None else _tb.isDrivingXTask

    @property
    def teUTAgent(self) -> _IUTAgent:
        _ti = self.teTaskInst
        _tb = None if _ti is None else _ti.taskBadge
        if (_tb is None) or (not _tb.isDrivingXTask):
            res = None
        else:
            _utc = _ti._utConn
            res = None if _utc is None else _utc._utAgent
        return res

    def _CleanUp(self):
        self.__ti = None

    def _ToString(self, bPrintNID_=False, bPrintUID_=False):
        if self.__ti is None:
            return None

        if bPrintUID_:
            _tuid = self.teTaskBadge.threadUID
            if bPrintNID_ and _TaskUtil.IsNativeThreadIdSupported():
                res = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_TaskMgr_TID_012).format(
                    self.teTaskID, self.teTaskBadge.threadNID, _tuid, self.teTaskName, self.teTaskInst.isEnclosingPyThread, self.teTaskInst.isAlive, self.teTaskInst.dtaskStateID.compactName.lower())
            else:
                res = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_TaskMgr_TID_013).format(
                    self.teTaskID, _tuid, self.teTaskName, self.teTaskInst.isEnclosingPyThread, self.teTaskInst.isAlive, self.teTaskInst.dtaskStateID.compactName.lower())
        else:
            if bPrintNID_ and _TaskUtil.IsNativeThreadIdSupported():
                res = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_TaskMgr_TID_014).format(
                    self.teTaskID, self.teTaskBadge.threadNID, self.teTaskName, self.teTaskInst.isEnclosingPyThread, self.teTaskInst.isAlive, self.teTaskInst.dtaskStateID.compactName.lower())
            else:
                res = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_TaskMgr_TID_015).format(
                    self.teTaskID, self.teTaskName, self.teTaskInst.isEnclosingPyThread, self.teTaskInst.isAlive, self.teTaskInst.dtaskStateID.compactName.lower())
        return res

class _TaskMgrImpl(_TaskManager, _LcProxyClient, _ITMgrImpl, _ITTMgr):
    __slots__ = [ '__m' , '__s' , '__bF' , '__md' , '__ma' , '__tn' , '__tt' , '__tu' ]

    def __init__(self):
        self.__m  = None
        self.__s  = None
        self.__ma = None
        self.__md = None
        self.__bF = None
        self.__tn = None
        self.__tt = None
        self.__tu = None

        _TaskManager.__init__(self)
        _LcProxyClient.__init__(self)
        _ITMgrImpl.__init__(self)
        _ITTMgr.__init__(self)

        if _TaskManager._theTMgrImpl is not None:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00265)
            self.CleanUp()
        else:
            self.__s  = _BinarySemaphore()
            self.__bF = False
            self.__ma = _Mutex()
            self.__md = _Mutex()
            self.__tn = _PyOrderedDict()
            self.__tt = _PyOrderedDict()
            self.__tu = _PyOrderedDict()

            if self.__EncloseCurThread(bAEnclosed_=True, bSkipCheck_=True) is None:
                logif._XLogFatalEC(_EFwErrorCode.FE_00925, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_TaskMgr_TID_001))
                self.CleanUp()
            else:
                _TaskManager._theTMgrImpl = self

    def _PcClientName(self) -> str:
        return _FwTDbEngine.GetText(_EFwTextID.eELcCompID_TMgr)

    def _ToString(self):
        if self.__isInvalid:
            return None
        return _CommonDefines._STR_EMPTY

    def _CleanUp(self):
        if self.__isInvalid:
            return

        _TaskManager._theTMgrImpl = None
        self.__StopAllTasks(bCleanupStoppedTasks_=False, lstSkipTaskIDs_=None, bSkipStartupThrd_=False)

        for _vv in self.__tt.values():
            _vv.CleanUp()

        self.__tn.clear()
        self.__tu.clear()
        self.__tt.clear()
        self.__s.CleanUp()
        self.__md.CleanUp()
        self.__ma.CleanUp()

        self.__m  = None
        self.__s  = None
        self.__ma = None
        self.__md = None
        self.__bF = None
        self.__tn = None
        self.__tt = None
        self.__tu = None

        _LcProxyClient._CleanUp(self)

    @property
    def _isTMgrAvailable(self):
        return self.__isApiAvailable

    @override
    def _IsCurTask(self, taskID_ : int):
        if not isinstance(taskID_, int):
            return False
        if self.__isInvalidOrFailed:
            return False
        _bg, _ti = self.__GetCurTaskBadge()
        res = (_bg is not None) and _bg.dtaskUID == taskID_
        return res

    @override
    def _CreateTask( self
                   , fwtPrf_         : _FwTaskProfile   =None
                   , rbl_            : _AbsRunnable     =None
                   , taskName_       : str              =None
                   , enclHThrd_      : _PyThread        =None
                   , rmask_          : _ETaskResFlag    =None
                   , delayedStartMS_ : int              =None
                   , args_           : list             =None
                   , kwargs_         : dict             =None
                   , tpAttrs_        : dict             =None
                   , bStart_         : bool             =False
                   , tskOpPCheck_    : _ATaskOpPreCheck =None ) -> Union[int, None]:
        res = None
        if not self.__isApiNotAvailable:
            _ept = enclHThrd_
            if (_ept is None) and (tpAttrs_ is not None):
                if _AbsFwProfile._ATTR_KEY_ENCLOSED_PYTHREAD in tpAttrs_:
                    _ept = tpAttrs_[_AbsFwProfile._ATTR_KEY_ENCLOSED_PYTHREAD]
            if not self.__PrecheckExecutableRequest(tskID_=None, aprofile_=fwtPrf_, enclPyThrd_=_ept):
                return None

            _tp = self.__CheckCreateTaskRequest( fwtPrf_=fwtPrf_
                                               , rbl_=rbl_
                                               , taskName_=taskName_
                                               , rmask_=rmask_
                                               , delayedStartMS_=delayedStartMS_
                                               , enclHThrd_=enclHThrd_
                                               , args_=args_
                                               , kwargs_=kwargs_
                                               , tpAttrs_=tpAttrs_)
            if _tp is not None:
                res = self.__CreateStartProfiledTask(_tp, bStart_, tskOpPCheck_=tskOpPCheck_)
                if res is None:
                    if fwtPrf_ is None:
                        _tp.CleanUp()
                else:
                    res = res.dtaskUID
        return res

    @override
    def _CreateThread( self
                     , fwthrdPrf_   : _FwThreadProfile =None
                     , utConn_      : _IUTaskConn      =None
                     , taskName_    : str              =None
                     , enclHThrd_   : _PyThread        =None
                     , bStart_      : bool             =None
                     , thrdTgtCIF_  : _FwCallable      =None
                     , args_        : list             =None
                     , kwargs_      : dict             =None
                     , tpAttrs_     : dict             =None
                     , tskOpPCheck_ : _ATaskOpPreCheck =None ) -> Union[int, None]:
        res = None
        if not self.__isApiNotAvailable:
            _ept = enclHThrd_
            if (_ept is None) and (tpAttrs_ is not None):
                if _AbsFwProfile._ATTR_KEY_ENCLOSED_PYTHREAD in tpAttrs_:
                    _ept = tpAttrs_[_AbsFwProfile._ATTR_KEY_ENCLOSED_PYTHREAD]
            if not self.__PrecheckExecutableRequest(tskID_=None, aprofile_=fwthrdPrf_, enclPyThrd_=_ept):
                return None

            res = self.__CreateStartThread( fwthrdPrf_=fwthrdPrf_
                                          , utConn_=utConn_
                                          , taskName_=taskName_
                                          , enclHThrd_=enclHThrd_
                                          , bStart_=bStart_
                                          , thrdTgtCIF_=thrdTgtCIF_
                                          , args_=args_
                                          , kwargs_=kwargs_
                                          , tpAttrs_=tpAttrs_
                                          , tskOpPCheck_=tskOpPCheck_)
            if res is not None:
                res = res.dtaskUID
        return res

    @override
    def _GetCurTaskBadge(self):
        if self.__isApiNotAvailable:
            return None
        _bg, _ti = self.__GetCurTaskBadge()
        return _bg

    @override
    def _GetTaskError(self, taskID_ =None):
        if self.__isApiNotAvailable:
            return None

        res = None
        if taskID_ is None:
            _bg, _ti = self.__GetCurTaskBadge()
            if _ti is not None:
                res = _ti.taskError
        else:
            _ti = self._GetTask(taskID_, bDoWarn_=False)
            if _ti is not None:
                res = _ti.taskError
        return res

    @override
    def _GetTask(self, taskID_ : Union[int, _EMessagePeer], bDoWarn_ =True):
        if self.__isApiNotAvailable:
            return None
        if not isinstance(taskID_, (int, _EMessagePeer)):
            return None
        res = self.__GetTableEntry(taskID_=taskID_, bDoWarn_=bDoWarn_)
        if res is not None:
            res = res.teTaskInst
        return res

    @override
    def _GetTaskID(self, taskName_):
        if self.__isApiNotAvailable:
            return None
        with self.__md:
            res = None
            if taskName_ in self.__tn:
                _te = self.__tn[taskName_]
                res = _te.teTaskID
            return res

    @override
    def _GetTaskBadge(self, taskID_ : Union[int, _EMessagePeer], bDoWarn_ =True):
        if self.__isApiNotAvailable:
            return None
        if not isinstance(taskID_, (int, _EMessagePeer)):
            return None
        res = self.__GetTableEntry(taskID_=taskID_, bDoWarn_=bDoWarn_)
        if res is not None:
            res = res.teTaskBadge
        return res

    @override
    def _StartTask(self, taskID_, tskOpPCheck_ : _ATaskOpPreCheck =None, bSkipPrecheck_ =False) -> bool:
        if self.__isApiNotAvailable:
            return False

        self.__ma.Take()
        if not bSkipPrecheck_:
            if not self.__PrecheckExecutableRequest(tskID_=taskID_, aprofile_=None, enclPyThrd_=None):
                self.__ma.Give()
                return False

        _te = self.__GetTableEntry(taskID_=taskID_)
        if _te is None:
            self.__ma.Give()
            return False
        return self.__StartTaskInstance(_te.teTaskInst, tskOpPCheck_, cleanupOnFailure_=False)

    @override
    def _StopTask(self, taskID_, bCancel_ =False, removeTask_=True, tskOpPCheck_ : _ATaskOpPreCheck =None) -> bool:
        if self.__isApiNotAvailable:
            return False
        else:
            _tid = self.__StopTaskByID(taskID_, bCancel_=bCancel_, removeTask_=removeTask_, tskOpPCheck_=tskOpPCheck_)
            return _tid is not None

    @override
    def _JoinTask(self, taskID_, timeout_ : _Timeout =None, tskOpPCheck_ : _ATaskOpPreCheck =None, curTask_ : _AbsFwTask =None) -> bool:
        if self.__isApiNotAvailable:
            return False

        with self.__ma:
            _te = self.__GetTableEntry(taskID_=taskID_)
            if _te is None:
                return False

            _ti = _te.teTaskInst
            _oppc = _TaskMgrImpl.__GetTaskOpPreCheck(_ti, _EATaskOpID.eJoin, tskOpPCheck_=tskOpPCheck_)
            if _oppc.isNotApplicable or _oppc.isIgnorable:
                res = _oppc.isIgnorable
                if tskOpPCheck_ is None:
                    _oppc.CleanUp()
                return res

        res = _ti.JoinTask(timeout_, tskOpPCheck_=_oppc, curTask_=curTask_)
        if tskOpPCheck_ is None:
            _oppc.CleanUp()
        return res

    @override
    def _SelfCheckTask(self, taskID_ : int) -> _ETaskSelfCheckResultID:
        if self.__isInvalidOrFailed or not self._PcIsLcProxySet():
            res = _ETaskSelfCheckResultID.eScrStop
        else:
            _te = self.__GetTableEntry(taskID_=taskID_, bDoWarn_=False)
            _ti = None if _te is None else _te.teTaskInst
            if _ti is None:
                res = _ETaskSelfCheckResultID.eScrStop
            else:
                res = _ti._SelfCheckTask()
        return res

    @override
    def _StartUTask(self, utConn_ : _IUTaskConn, tskOpPCheck_ : _ATaskOpPreCheck =None) -> bool:
        if self.__isApiNotAvailable:
            return False
        _bUTC = isinstance(utConn_, _IUTaskConn)
        if not (_bUTC and utConn_._isUTConnected):
            if not _bUTC:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00266)
            else:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00267)
            return False

        res     = False
        _atsk   = None
        _xbXcp  = None
        _curTsk = None

        try:
            _curTsk = self.__BookmarkCurTask(_EFwApiBookmarkID.eXTaskApiRequestStart)

            _tid       = utConn_._taskUID
            _xtp       = utConn_._taskProfile
            _enclHThrd = None

            if _tid is None:
                if _xtp.isSyncTask:
                    _enclHThrd = _TaskUtil.GetCurPyThread()

            if not self.__PrecheckExecutableRequest(tskID_=_tid, aprofile_=None, enclPyThrd_=_enclHThrd):
                return False

            if _tid is not None:
                res = self._StartTask(_tid, tskOpPCheck_=tskOpPCheck_, bSkipPrecheck_=True)
            else:
                enclThrd = None
                if _xtp.isSyncTask:
                    enclThrd = _TaskUtil.GetCurPyThread()
                _tp = _TaskMgrImpl.__CreateXTaskProfile(utConn_, enclHThrd_=enclThrd, profileAttrs_=None)
                if _tp is None:
                    pass
                elif _tp.isTaskProfile:
                    _atsk = self.__CreateStartProfiledTask(_tp, True, tskOpPCheck_=tskOpPCheck_)
                else:
                    _atsk = self.__CreateStartThread(fwthrdPrf_=_tp, bStart_=True, tskOpPCheck_=tskOpPCheck_)
                res = (_atsk is not None) and _atsk.isStarted and not (_atsk.isFailed or _atsk.isAborting)

        except _XcoXcpRootBase as _xcp:
            if self.__CheckForReraiseXcoException(_xcp):
                raise _xcp

        except BaseException as _xcp:
            _xbXcp = _XcoBaseException(_xcp, tb_=logif._GetFormattedTraceback())
        finally:
            if _xbXcp is not None:
                self.__HandleXcoBaseException(_xbXcp, curTask_=_curTsk)

        if _curTsk is not None:
            self.__BookmarkCurTask(_EFwApiBookmarkID.eNA, curTask_=_curTsk)

        return res

    @override
    def _StopUTask(self, utConn_ : _IUTaskConn, bCancel_ =False, bCleanupDriver_ =True, tskOpPCheck_ : _ATaskOpPreCheck =None) -> bool:
        if self.__isApiNotAvailable:
            return False
        _bUTC = isinstance(utConn_, _IUTaskConn)
        if not (_bUTC and utConn_._isUTConnected):
            if not _bUTC:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00271)
            else:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00272)
            return False

        _tid    = None
        _xtUID  = None
        _xbXcp  = None
        _curTsk = None
        try:
            _curTsk = self.__BookmarkCurTask(_EFwApiBookmarkID.eXTaskApiRequestStop)

            _bTD   = utConn_._taskProfile.isTeardownPhaseEnabled
            _xtUID = utConn_._taskUID

            if _xtUID is not None:
                if _bTD:
                    bCleanupDriver_ = False
                _tid = self.__StopTaskByID(_xtUID, bCancel_=bCancel_, removeTask_=bCleanupDriver_, tskOpPCheck_=tskOpPCheck_, curTask_=_curTsk)

        except _XcoXcpRootBase as _xcp:
            if self.__CheckForReraiseXcoException(_xcp):
                raise _xcp

        except BaseException as _xcp:
            _xbXcp = _XcoBaseException(_xcp, tb_=logif._GetFormattedTraceback())

        finally:
            if _xbXcp is not None:
                self.__HandleXcoBaseException(_xbXcp, curTask_=_curTsk)

        if _curTsk is not None:
            self.__BookmarkCurTask(_EFwApiBookmarkID.eNA, curTask_=_curTsk)

        return (_xtUID is None) or (_tid is not None)

    @override
    def _JoinUTask(self, utConn_ : _IUTaskConn, timeout_ : _Timeout =None, tskOpPCheck_ : _ATaskOpPreCheck =None) -> bool:
        if self.__isApiNotAvailable:
            return False
        _bUTC = isinstance(utConn_, _IUTaskConn)
        if not (_bUTC and utConn_._isUTConnected):
            if not _bUTC:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00273)
            return False

        res     = False
        _xbXcp  = None
        _curTsk = None
        try:
            _curTsk = self.__BookmarkCurTask(_EFwApiBookmarkID.eXTaskApiRequestJoin)
            _xtUID  = utConn_._taskUID

            if _xtUID is None:
                res = True
            else:
                res = self._JoinTask(_xtUID, timeout_=timeout_, tskOpPCheck_=tskOpPCheck_, curTask_=_curTsk)

        except _XcoXcpRootBase as _xcp:
            if self.__CheckForReraiseXcoException(_xcp):
                raise _xcp

        except BaseException as _xcp:
            _xbXcp = _XcoBaseException(_xcp, tb_=logif._GetFormattedTraceback())

        finally:
            if _xbXcp is not None:
                self.__HandleXcoBaseException(_xbXcp, curTask_=_curTsk)

        if _curTsk is not None:
            self.__BookmarkCurTask(_EFwApiBookmarkID.eNA, curTask_=_curTsk)

        return res

    @override
    def _ProcUnhandledXcp(self, xcp_: _XcoXcpRootBase):
        if self.__isApiNotAvailable:
            return False
        else:
            _te = self.__GetCurTableEntry(bDoWarn_=True)
            if (_te is None) or _te.teIsAutoEnclosedEntry:
                return False
            else:
                return _te.teTaskInst._ProcUnhandledException(xcp_)

    @override
    def _GetCurTask(self, bAutoEncl_ =False) -> Union[_AbsFwTask, None]:
        if self.__isInvalid:
            return None
        else:
            _bg, res = self.__GetCurTaskBadge(bAutoEncl_=bAutoEncl_)
            return res

    @override
    def _GetXTasks(self, bRunningOnly_ =True, bJoinableOnly_ =True, bUID_ =True, lstUIDs_ : list =None) -> Tuple[List[Union[int, IXTask]], Union[List[int], None]]:
        _lstXT, _lstUnj = self.__GetXTasks(bRunningOnly_=bRunningOnly_, bJoinableOnly_=bJoinableOnly_, bUID_=bUID_, lstUIDs_=lstUIDs_)
        return _lstXT, _lstUnj

    @override
    def _GetProxyInfoReplacementData(self):
        if self.__isInvalid:
            return None, None

        with self.__md:
            _curHT = _TaskUtil.GetCurPyThread()
            _tuid  = _TaskUtil.GetPyThreadUID(_curHT)

            _tname    = None
            _bXTask = False
            _te       = None if _tuid not in self.__tu else self.__tu[_tuid]
            if _te is None:
                _tname, _bXTask = _curHT.name, False
            else:
                _tname, _bXTask = _te.teTaskName, _te.teIsXTaskEntry

            return _tname, _bXTask

    @override
    def _GetTaskErrorByTID(self, taskID_ : int) -> Union[_FwTaskError, None]:
        if self.__isInvalid:
            return None
        elif not isinstance(taskID_, int):
            return None
        res = self.__GetTableEntry(taskID_=taskID_)
        if res is not None:
            res = res.teTaskInst
        if res is not None:
            res = res.taskError
        return res

    @override
    def _SetLcMonitorImpl(self, lcMonImpl_ : _LcMonitorImpl):
        if isinstance(lcMonImpl_, _LcMonitorImpl) and lcMonImpl_.isValid and not lcMonImpl_.isDummyMonitor:
            self.__m = lcMonImpl_

    @override
    def _InjectLcProxy(self, lcProxy_ : _ILcProxy):
        if self.__isInvalid:
            return False

        self._PcSetLcProxy(lcProxy_, bForceUnset_=True)
        if self._PcIsLcProxySet():
            with self.__md:
                _ii = 0
                for _kk, _te in self.__tt.items():
                    if isinstance(_te.teTaskInst, _LcProxyClient):
                        if not _te.teTaskInst._PcIsLcProxySet():
                            _ii += 1
                            _te.teTaskInst._PcSetLcProxy(self)
        return True

    @override
    def _StopAllTasks(self, bCleanupStoppedTasks_ =True, lstSkipTaskIDs_ =None) -> list:
        if self.__isInvalid:
            res = None
        else:
            res = self.__StopAllTasks(bCleanupStoppedTasks_=bCleanupStoppedTasks_, lstSkipTaskIDs_=lstSkipTaskIDs_)
        return res

    @override
    def _AddTaskEntry(self, taskInst_ : _AbsFwTask, bRemoveAutoEnclTE_ =True) -> Union[int, None]:
        if self.__isInvalid:
            return None
        elif not isinstance(taskInst_, _AbsFwTask):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00274)
            return None

        self.__ma.Take()
        if taskInst_.isEnclosingPyThread:
            if bRemoveAutoEnclTE_:
                _te = self.__GetTableEntry(hthrd_=taskInst_.dHThrd, bDoWarn_=False)
                if _te is not None:
                    if _te.teIsAutoEnclosedEntry:
                        _aet = _te.teTaskInst
                        if not self.__RemoveFromTable(_aet):
                            self.__ma.Give()
                            return None
                        else:
                            _aet.CleanUp()

        res = None
        if self.__AddToTable(taskInst_):
            res = taskInst_.dtaskUID
        self.__ma.Give()
        return res

    @override
    def _DetachTask(self, taskInst_ : _AbsFwTask, cleanup_ =True):
       if self.__isInvalid:
           return
       elif not isinstance(taskInst_, _AbsFwTask):
           vlogif._LogOEC(True, _EFwErrorCode.VFE_00275)
           return

       self.__ma.Take()
       _te = self.__GetTableEntry(hthrd_=taskInst_.dHThrd, bDoWarn_=False)
       if _te is None:
           pass
       elif not self.__RemoveFromTable(_te.teTaskInst):
           _ttn, _tn, _tb, _tid = type(taskInst_).__name__, taskInst_.dtaskName, _te.teTaskBadge, taskInst_.dtaskUID
           vlogif._LogOEC(False, _EFwErrorCode.VUE_00026)
       elif cleanup_:
           self.__CleanUpTaskInstance(taskInst_)
       self.__ma.Give()

    @staticmethod
    def _ClsDepInjection(dinjCmd_ : _EDepInjCmd):
        if dinjCmd_.isDeInject:
            _inst = _TaskManager._theTMgrImpl
            if _inst is not None:
                _inst.CleanUp()
            res = _TaskManager._theTMgrImpl is None
        else:
            _inst = _TaskMgrImpl()
            res = (_inst.__bF is not None) and (_TaskManager._theTMgrImpl is not None)
            if not res:
                _inst.CleanUp()
        return res

    @staticmethod
    def _CreateXTaskProfile(utConn_ : _IUTaskConn, enclHThrd_ : _PyThread =None, profileAttrs_ : dict =None):
        return _TaskMgrImpl.__CreateXTaskProfile(utConn_, enclHThrd_=enclHThrd_, profileAttrs_=profileAttrs_)

    @staticmethod
    def _GetLcProxy() -> _ILcProxy:
        res = None
        if _TaskManager._theTMgrImpl is None:
            pass
        elif _TaskManager._theTMgrImpl.__isInvalid:
            pass
        else:
            res = _TaskManager._theTMgrImpl._PcGetLcProxy()
        return res

    @property
    def __isInvalid(self):
        return self.__tt is None

    @property
    def __isInvalidOrFailed(self):
        return True if self.__tt is None else self.__bF

    @property
    def __isApiAvailable(self):
        if self.__isInvalidOrFailed:
            return False
        return self._PcIsLcProxyModeNormal()

    @property
    def __isApiNotAvailable(self):
        if self.__isInvalidOrFailed:
            return True
        return not self._PcIsLcProxyModeNormal()

    @staticmethod
    def __CreateXTaskProfile(utConn_ : _IUTaskConn, enclHThrd_ : _PyThread =None, profileAttrs_ : dict =None):
        if not isinstance(utConn_, _IUTaskConn):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00276)
            return None

        _uta = utConn_._utAgent
        if _uta is None:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00277)
            return None

        _TRM_KEY = _FwThreadProfile._ATTR_KEY_TASK_RIGHTS

        if profileAttrs_ is None:
            profileAttrs_ = dict()
        _trm = profileAttrs_[_TRM_KEY] if _TRM_KEY in profileAttrs_ else _ETaskRightFlag.UserTaskRightDefaultMask()

        if not isinstance(_trm, _ETaskRightFlag):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00278)
            return None

        if not _trm.hasUserTaskRight:
            _trm = _ETaskRightFlag.AddUserTaskRightFlag(_trm, _ETaskRightFlag.eUTTask)
        if not _trm.hasXTaskTaskRight:
            _trm = _ETaskRightFlag.AddXTaskTaskRight(_trm)

        res  = None
        _xtp = utConn_._taskProfile
        profileAttrs_[_TRM_KEY] = _trm

        try:
            if _xtp.isInternalQueueEnabled or _xtp.isExternalQueueEnabled:
                _rr = _UserTaskRbl(utConn_)
                if _rr._rblType is None:
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00279)
                else:
                    res = _FwTaskProfile(rbl_=_rr, enclHThrd_=enclHThrd_, tpAttrs_=profileAttrs_)
            else:
                res = _FwThreadProfile(utaskConn_=utConn_, enclHThrd_=enclHThrd_, tpAttrs_=profileAttrs_)
        except (_XcoXcpRootBase, BaseException) as _xcp:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00280)

        if res is not None:
            if not (res.isValid and res.isDrivingXTaskTaskProfile):
                logif._LogImplErrorEC(_EFwErrorCode.FE_00689, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_TaskMgr_TID_010).format(_uta))
                res.CleanUp()
                res = None

        if res is None:
            logif._LogErrorEC(_EFwErrorCode.UE_00092, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_TaskMgr_TID_002).format(_uta))
        return res

    @staticmethod
    def __GetTaskOpPreCheck(taskInst_ : _AbsFwTask, taskOpID_ : _EATaskOpID, tskOpPCheck_: _ATaskOpPreCheck = None) -> _ATaskOpPreCheck:
        res = tskOpPCheck_
        if res is None:
            res = _ATaskOpPreCheck(taskOpID_, taskInst_._tskState, taskInst_._dHThrd, taskInst_.isEnclosingPyThread, bReportErr_=True)
        else:
            res.Update(bReportErr_=True)
        return res

    def __BookmarkCurTask(self, eFwApiBookmarkID_ : _EFwApiBookmarkID, curTask_ : _AbsFwTask =None) -> _AbsFwTask:
        res = curTask_
        if res is None:
            res = self._GetCurTask(bAutoEncl_=True)
        if res is not None:
            res._SetFwApiBookmark(eFwApiBookmarkID_)
        return res

    def __CheckForReraiseXcoException(self, xcp_: _XcoXcpRootBase, bForceReraise_ =True) -> bool:
        return self is not None

    def __HandleXcoBaseException(self, xcp_: _XcoBaseException, bCausedByTMgr_ =None, curTask_ : _AbsFwTask =None):
        if self._PcIsTaskMgrFailed():
            return
        if not xcp_.isXcoBaseException:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00281)
            return

        _bDoLogSysXcp     = False
        _bRootCauseFWS    = False
        _bRootCauseTMgr   = False
        _bRootCauseClient = False

        _bCTV  = (curTask_ is not None) and curTask_.isValid
        _bCTAE = _bCTV and curTask_.isAutoEnclosed

        _bCTNT = _bCTV and not curTask_.isTerminated

        if bCausedByTMgr_ is not None:
            if bCausedByTMgr_:
                _bRootCauseFWS, _bRootCauseTMgr = True, True

        if not _bRootCauseFWS:
            if not _bCTNT:
                _bRootCauseFWS, _bRootCauseTMgr = True, True

            elif _bCTAE:
                _bDoLogSysXcp = True

            else:
                _fwApiBmID = curTask_.fwApiBookmarkID
                if _fwApiBmID.isXTaskApiRequest:
                    _bRootCauseFWS, _bRootCauseTMgr = True, True
                elif _fwApiBmID.isXTaskApiBeginAction:
                    if curTask_.taskXPhase.isXTaskExecution:
                        _bDoLogSysXcp, _bRootCauseClient = True, True
                    else:
                        _bDoLogSysXcp, _bRootCauseFWS = True, True
                else:
                    _bRootCauseFWS = True

        if _bDoLogSysXcp:
            logif._LogSysExceptionEC(_EFwErrorCode.FE_00016, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_TaskMgr_TID_003), xcp_._enclosedException, xcp_.traceback)
            return

        if not self.__bF:
            self.__bF = _bRootCauseTMgr

        if not (_bRootCauseFWS or _bRootCauseTMgr or _bRootCauseClient):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00282)
            return

        _bCreateFE = _bCTAE or not (_bCTNT and curTask_.isRunning)

        if _bRootCauseClient:
            _cc = _ELcCompID.eXTask
        elif _bRootCauseTMgr:
            _cc = _ELcCompID.eTMgr
        else:
            _cc = _ELcCompID.eFwSrv

        _frc = None

        if _bCreateFE:
            _bFwTsk  = not _cc.isXtask
            _errCode = _EFwErrorCode.FE_00024 if _bFwTsk else _EFwErrorCode.FE_00926
            _frc     = logif._CreateLogFatalEC(_bFwTsk, _errCode, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_TaskMgr_TID_009).format(str(xcp_)))
        else:
            logif._LogUnhandledXcoBaseXcpEC(_EFwErrorCode.FE_00021, xcp_)

            _te = curTask_.taskError
            if (_te is not None) and _te.isFatalError:
                _frc = _te._currentErrorEntry

        if _frc is not None:
            self._PcNotifyLcFailure(_cc, _frc, atask_=curTask_)

    def __GetCurTaskBadge(self, bAutoEncl_ =False):
        _te = None
        with self.__md:
            _curHT = _TaskUtil.GetCurPyThread()

            _te = self.__GetTableEntry(hthrd_=_curHT, bDoWarn_=True)
            if _te is None:
                if not bAutoEncl_:
                    pass
                else:
                    _tuid = _TaskUtil.GetPyThreadUID(_curHT)

                    if not _AutoEnclosedThreadsBag.IsProcessingCurPyThread(curPyThrd_=_curHT):
                        _AutoEnclosedThreadsBag._AddPyThread(_curHT)
                        _fthrd = self.__EncloseCurThread(bAEnclosed_=True, bSkipCheck_=True)
                        _AutoEnclosedThreadsBag._RemovePyThread(_curHT)

                        if _fthrd is None:
                            _errMsg = 'TMgr failed to auto-enclose current thread {}:{}.'.format(_curHT.name, _tuid)
                            vlogif._LogOEC(True, _EFwErrorCode.VFE_00283)

                            if not self._PcIsTaskMgrFailed():
                                _myFE = logif._CreateLogImplErrorEC(_EFwErrorCode.FE_00030, _errMsg)
                                self._PcNotifyLcFailure(_ELcCompID.eTMgr, _myFE)
                        else:
                            _te = self.__GetTableEntry(taskID_=_fthrd.dtaskUID)

        res    = None
        _tinst = None
        if (_te is None) or (_te.teTaskBadge is None):
            pass
        else:
            res, _tinst = _te.teTaskBadge, _te.teTaskInst

            if _tinst.isAutoEnclosed:
                pass
            elif not _tinst.isEnclosingPyThread:
                pass
            elif (self.__m is None) or not self.__m.isLcShutdownEnabled:
                pass
            elif (_tinst.lcDynamicTLB is None) or _tinst.lcDynamicTLB.isDummyTLB:
                pass
            elif _tinst.isInLcCeaseMode:
                pass
            elif _tinst.isRunning:
                _AbsFwTask._SetGetTaskState(_tinst, _TaskState._EState.ePendingStopRequest)
                if not _tinst.isPendingStopRequest:
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00284)

        return res, _tinst

    def __GetCurTableEntry(self, bDoWarn_ =False):
        return self.__GetTableEntry(hthrd_=_TaskUtil.GetCurPyThread(), bDoWarn_=bDoWarn_)

    def __GetTableEntry(self, taskID_ : Union[_EMessagePeer, int] =None, hthrd_ : _PyThread =None, bDoWarn_=True) -> Union[_TaskEntry, None]:
        res = None
        _bMsgPeer = False if _ssshare._IsSubsysMsgDisabled() else isinstance(taskID_, _EMessagePeer)

        if not (_bMsgPeer or isinstance(taskID_, int) or isinstance(hthrd_, _PyThread)):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00285)
        elif _bMsgPeer and _ssshare._IsSubsysMsgDisabled():
            pass
        else:
            with self.__md:
                if taskID_ is not None:
                    if _bMsgPeer:
                        if not (taskID_.isPFwMain or taskID_.isPTimerManager):
                            pass
                        else:
                            for _kk, _te in self.__tt.items():
                                _tb = _te.teTaskBadge
                                if (_tb is None) or not _tb.isValid:
                                    continue
                                if not _tb.isFwTask:
                                    continue
                                if _tb.isXTaskTask:
                                    continue

                                _sid = _tb.fwSID
                                if _sid is None:
                                    continue
                                if not _sid.isFwsMain:
                                    continue
                                if _sid.isFwsMain and taskID_.isPFwMain:
                                    res = _te
                                    break
                                continue
                    elif taskID_ not in self.__tt:
                        if bDoWarn_:
                            vlogif._LogOEC(False, _EFwErrorCode.VUE_00027)
                    else:
                        res = self.__tt[taskID_]
                else:
                    _tuid = _TaskUtil.GetPyThreadUID(hthrd_)
                    if _tuid in self.__tu:
                        res = self.__tu[_tuid]
        return res

    def __AddToTable(self, taskInst_ : _AbsFwTask):
        if not isinstance(taskInst_, _AbsFwTask):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00286)
            return False

        with self.__md:
            _tid = taskInst_.dtaskUID
            if _tid in self.__tt:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00287)
                return False

            _te = _TaskEntry(taskInst_)
            self.__tt[_tid] = _te

            _tuid = taskInst_.threadUID
            self.__tu[_tuid] = _te

            _tname = taskInst_.dtaskName
            if _tname not in self.__tn:
                self.__tn[_tname] = _te

            if self._PcIsLcProxyModeNormal():
                if isinstance(taskInst_, _LcProxyClient):
                    taskInst_._PcSetLcProxy(self)

            self.__RemoveCleanedUpEntries()
            return True

    def __RemoveFromTable(self, taskInst_ : _AbsFwTask):
        if not isinstance(taskInst_, _AbsFwTask):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00288)
            return False
        elif not taskInst_.isValid:
            return False

        with self.__md:
            _tid   = taskInst_.dtaskUID
            _tuid  = taskInst_.threadUID
            _tname = taskInst_.dtaskName

            if _tid not in self.__tt:
                return False
            elif _tuid not in self.__tu:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00289)
                return False

            _teByName     = None
            _allTEsByName = [ self.__tn[_kk] for _kk in self.__tn if _tname in self.__tn ]
            for _te in _allTEsByName:
                if _te.teTaskID == taskInst_.dtaskUID:
                    _teByName = _te
                    break
            if _teByName is not None:
                self.__tn[_tname] = None
                _AbsSlotsObject.Delete(self.__tn, _tname)

            self.__tu[_tuid] = None
            _AbsSlotsObject.Delete(self.__tu, _tuid)

            _te = self.__tt[_tid]
            self.__tt[_tid] = None
            _AbsSlotsObject.Delete(self.__tt, _tid)
            _te.CleanUp()
            return True

    def __RemoveCleanedUpEntries(self):
        _rm = [ _kk for _kk, _te in self.__tt.items() if not _te.teTaskInst.isValid ]
        for _kk in _rm:
            self.__tt.pop(_kk)
        _rm = [ _kk for _kk, _te in self.__tu.items() if not _te.teTaskInst.isValid ]
        for _kk in _rm:
            self.__tu.pop(_kk)
        _rm = [ _kk for _kk, _te in self.__tn.items() if not _te.teTaskInst.isValid ]
        for _kk in _rm:
            self.__tn.pop(_kk)

    def __RemoveDetachedEntries(self):
        with self.__md:
            if len(self.__tt):
                _rm = []
                for _kk in self.__tt.keys():
                    _te = self.__tt[_kk]

                    if not _te.teIsXTaskEntry:
                        continue

                    _utc = _te.teTaskInst._utConn
                    if not _utc._isUTConnected:
                        _rm.append(_kk)
                for _kk in _rm:
                    self.__tt.pop(_kk)

            if len(self.__tu):
                _rm = []
                for _kk in self.__tu.keys():
                    _te = self.__tu[_kk]

                    if not _te.teIsXTaskEntry:
                        continue

                    _utc = _te.teTaskInst._utConn
                    if not _utc._isUTConnected:
                        _rm.append(_kk)
                for _kk in _rm:
                    self.__tu.pop(_kk)

            if len(self.__tn):
                _rm = []
                for _kk in self.__tn.keys():
                    _te = self.__tn[_kk]

                    if not _te.teIsXTaskEntry:
                        continue

                    _utc = _te.teTaskInst._utConn
                    if not _utc._isUTConnected:
                        _rm.append(_kk)
                for _kk in _rm:
                    self.__tn.pop(_kk)

    def __StartTaskInstance(self, taskInst_ : _AbsFwTask, tskOpPCheck_ : _ATaskOpPreCheck, cleanupOnFailure_ =False) -> bool:
        _oppc = _TaskMgrImpl.__GetTaskOpPreCheck(taskInst_, _EATaskOpID.eStart, tskOpPCheck_=tskOpPCheck_)
        if _oppc.isNotApplicable or _oppc.isIgnorable:
            if cleanupOnFailure_:
                res = False
                self.__RemoveFromTable(taskInst_)
                taskInst_.CleanUp()
            else:
                res = _oppc.isIgnorable

            if tskOpPCheck_ is None:
                _oppc.CleanUp()

            self.__ma.Give()
            return res

        _semSS = None if taskInst_.isEnclosingPyThread else self.__s

        res     = False
        _xbXcp  = None
        _curTsk = None

        try:
            _curTblE = self.__GetCurTableEntry()
            if _curTblE is not None:
                _curTsk = _curTblE.teTaskInst

            if not _oppc.isASynchronous:
                self.__ma.Give()
            res = taskInst_.StartTask(semStart_=_semSS, tskOpPCheck_=tskOpPCheck_, curTask_=_curTsk)

        except _XcoXcpRootBase as _xcp:
            if self.__CheckForReraiseXcoException(_xcp):
                if _oppc.isASynchronous:
                    self.__ma.Give()

                raise _xcp

        except BaseException as _xcp:
            _xbXcp = _XcoBaseException(_xcp, tb_=logif._GetFormattedTraceback())

        finally:
            if _semSS is not None:
                _semSS.Take()

            if _oppc.isASynchronous:
                self.__ma.Give()

            if tskOpPCheck_ is None:
                _oppc.CleanUp()

            _bTaskGone = not taskInst_.isValid
            if _bTaskGone:
                res = False
            elif _xbXcp is not None:
                res = False

            if not res:
                if cleanupOnFailure_:
                    if not _bTaskGone:
                        self.__RemoveFromTable(taskInst_)
                        taskInst_.CleanUp()

                if _xbXcp is not None:
                    if _oppc.isASynchronous:
                        self.__ma.Give()

                    self.__HandleXcoBaseException(_xbXcp, curTask_=_curTsk)
        return res

    def __StopTaskByID(self, taskID_ : int, bCancel_ =False, removeTask_ =True, tskOpPCheck_ : _ATaskOpPreCheck =None, curTask_ : _AbsFwTask =None):
        if not _Util.IsInstance(taskID_, int, bThrowx_=True):
            return None

        self.__ma.Take()

        _te = self.__GetTableEntry(taskID_=taskID_)
        if _te is None:
            self.__ma.Give()
            return None

        _tinst = _te.teTaskInst
        if _tinst.isAutoEnclosed:
            if not _tinst.dtaskStateID.isDone:
                _AbsFwTask._SetGetTaskState(_tinst, _TaskState._EState.eDone)
            if removeTask_:
                self.__RemoveFromTable(_tinst)
                self.__CleanUpTaskInstance(_tinst)

            self.__ma.Give()
            return taskID_

        _oppc = _TaskMgrImpl.__GetTaskOpPreCheck(_tinst, _EATaskOpID.eCancel if bCancel_ else _EATaskOpID.eStop, tskOpPCheck_=tskOpPCheck_)
        if _oppc.isNotApplicable or _oppc.isIgnorable:
            _bIgnorable = _oppc.isIgnorable
            if tskOpPCheck_ is None:
                _oppc.CleanUp()

            if _bIgnorable:
                if removeTask_:
                    self.__RemoveFromTable(_tinst)
                    self.__CleanUpTaskInstance(_tinst)
            self.__ma.Give()
            return taskID_ if _bIgnorable else None

        _semSS= None
        _bASync = _oppc.isASynchronous
        if _bASync:
            if not _tinst.isEnclosingPyThread:
                if _tinst.dxUnit is not None:
                    _semSS = self.__s

        if not _bASync:
            self.__ma.Give()

        _bStopOK = _tinst.StopTask(bCancel_=bCancel_, semStop_=_semSS, tskOpPCheck_=_oppc, curTask_=curTask_)
        if not _bStopOK:
            vlogif._LogOEC(False, _EFwErrorCode.VUE_00028)

        if tskOpPCheck_ is None:
            _oppc.CleanUp()

        if _bASync:
            self.__ma.Give()

        if _bStopOK:
            if _semSS is not None:
                _semSS.Take()

            if removeTask_:
                self.__RemoveFromTable(_tinst)
                self.__CleanUpTaskInstance(_tinst)

        return taskID_ if _bStopOK else None

    def __StopAllTasks(self, bCleanupStoppedTasks_ =True, lstSkipTaskIDs_= None, bSkipStartupThrd_=True) -> list:
        if self.__isInvalid:
            return None
        if (lstSkipTaskIDs_ is not None) and not isinstance(lstSkipTaskIDs_, list):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00290)
            return None

        res = []

        if (lstSkipTaskIDs_ is not None) and len(lstSkipTaskIDs_) == 0:
            lstSkipTaskIDs_ = None

        _lstRemoveTIDs, _lstStopTIDs = [], []

        with self.__md:
            _tblSize = len(self.__tt)
            if _tblSize == 0:
                return None

            _lstSkip = None
            if lstSkipTaskIDs_ is not None:
                _lstSkip = [ _tid for _tid in lstSkipTaskIDs_ if _tid in self.__tt ]

            for _kk in self.__tt.keys():
                _te = self.__tt[_kk]

                if _te.teTaskBadge is None:
                    continue
                if _te.teTaskInst.isEnclosingStartupThread and bSkipStartupThrd_:
                    continue
                if (_lstSkip is not None) and _te.teTaskID in _lstSkip:
                    continue
                if not _te.teTaskInst.isRunning:
                    if bCleanupStoppedTasks_: _lstRemoveTIDs.append(_kk)
                    continue

                if _te.teIsAutoEnclosedEntry:
                    _bCalledByCleanup = not bSkipStartupThrd_
                    if _bCalledByCleanup: _lstRemoveTIDs.append(_kk)

                _lstStopTIDs.append(_te.teTaskID)

        if len(_lstStopTIDs) > 0:
            for _tid in _lstStopTIDs:
                _tid = self.__StopTaskByID(_tid, removeTask_=False)
                if _tid is not None:
                    if bCleanupStoppedTasks_: _lstRemoveTIDs.append(_tid)

        if len(_lstRemoveTIDs) > 0:
            with self.__ma:
                with self.__md:
                    _lstRemoveTIDs.sort(reverse=True)
                    for _kk in _lstRemoveTIDs:
                        _te = self.__tt[_kk]
                        _ti = _te.teTaskInst
                        _ttn, _tn, _tid = type(_ti).__name__, _ti.dtaskName, _ti.dtaskUID
                        self.__RemoveFromTable(_ti)

                        if not _ti.taskBadge.isFwMain:
                            if not self.__CleanUpTaskInstance(_ti, bIgnoreCeaseMode_=True):
                                res.append(_ti)

        _tblSizeLeft = len(self.__tt)
        if len(res) < 1:
            res = None
        return res

    def __GetXTasks(self, bRunningOnly_ =True, bJoinableOnly_ =True, bUID_ =True, lstUIDs_ : list =None) -> Tuple[List[Union[int, IXTask]], Union[List[int], None]]:
        res, _lstUnj = [], None

        if self.__isInvalid:
            return res, _lstUnj

        with self.__md:
            _tblSize = len(self.__tt)
            if _tblSize == 0:
                return res, _lstUnj

            _lstAvbl = []
            for _kk in self.__tt.keys():
                _te = self.__tt[_kk]

                if (lstUIDs_ is not None) and (_kk in lstUIDs_):
                    _lstAvbl.append(_kk)

                if _te.teTaskBadge is None:
                    continue
                if not _te.teIsXTaskEntry:
                    continue
                if bRunningOnly_:
                    if not _te.teTaskInst.isRunning:
                        continue
                elif (not _te.teTaskInst.isStarted) or _te.teTaskInst.isTerminated:
                    continue
                if (lstUIDs_ is not None) and _kk not in lstUIDs_:
                    continue
                if bJoinableOnly_ and not _te.teIsJoinableEntry:
                    if _lstUnj is None:
                        _lstUnj = []
                    _lstUnj.append(_kk)
                    continue

                _xt = _kk
                if not bUID_:
                    _uta = _te.teUTAgent
                    _xt  = None if _uta is None else _uta._xtInst
                if _xt is not None:
                    res.append(_xt)

            if bJoinableOnly_ and (lstUIDs_ is not None):
                if len(_lstAvbl) != len(lstUIDs_):
                    _lstUAvbl = [ _kk for _kk in lstUIDs_ if _kk not in _lstAvbl]
                    _lstUAvbl = [str(_kk) for _kk in _lstUAvbl]
                    _lstUAvbl = _CommonDefines._CHAR_SIGN_SPACE.join(_lstUAvbl)
                    _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_TaskMgr_TID_016).format(_lstUAvbl)
                    logif._LogWarning(_msg)
        return res, _lstUnj

    def __CleanUpTaskInstance(self, tskInst_ : _AbsFwTask, bIgnoreCeaseMode_ =False):
        if not tskInst_.isValid:
            return self is not None
        if not tskInst_.ceaseTLBState.isNone:
            if not bIgnoreCeaseMode_:
                return False

        if tskInst_.isStarted and not tskInst_.isTerminated:
            return False

        if tskInst_.taskBadge.isFwTask:
            _axu = tskInst_.dxUnit
            tskInst_.CleanUp()
            if _axu is not None:
                _axu.CleanUp()
        else:
            _utc = tskInst_._utConn
            tskInst_.CleanUp()
            if _utc is not None:
                _utc.CleanUp()
        return True

    def __PrecheckExecutableRequest( self, tskID_ : int =None, aprofile_ : _AbsFwProfile =None, enclPyThrd_ : _PyThread =None) -> bool:
        _bParamsOK = True
        _bParamsOK = _bParamsOK and (tskID_      is None or isinstance(tskID_, int))
        _bParamsOK = _bParamsOK and (aprofile_   is None or (isinstance(aprofile_, _AbsFwProfile) and aprofile_.isValid and (aprofile_.isTaskProfile or aprofile_.isThreadProfile)))
        _bParamsOK = _bParamsOK and (enclPyThrd_ is None or isinstance(enclPyThrd_, _PyThread))
        if not _bParamsOK:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00291)
            return False

        self.__RemoveDetachedEntries()

        if tskID_ is not None:
            if not (aprofile_ is None and enclPyThrd_ is None):
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00292)
                return False

            else:
                return self.__PrecheckExecutableRequestByTaskID(tskID_)

        res = None

        if aprofile_ is None:
            if enclPyThrd_ is None:
                res = True

        elif aprofile_.isEnclosingPyThread:
            _bError        = False
            _enclPyThrdPrf = aprofile_.enclosedPyThread

            if _enclPyThrdPrf is None:
                _bError = True
            elif (enclPyThrd_ is not None) and id(_enclPyThrdPrf) != id(enclPyThrd_):
                _bError = True

            if _bError:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00293)
                res = False
            else:
                enclPyThrd_ = _enclPyThrdPrf
        elif enclPyThrd_ is not None:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00294)
            res = False
        else:
            res = True

        if res is not None:
            return res

        if enclPyThrd_ is None:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00295)
            res = False

        else:
            _curHT = _TaskUtil.GetCurPyThread()

            if id(enclPyThrd_) != id(_curHT):
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00296)
                res = False

            else:
                _curTE = self.__GetTableEntry(hthrd_=_curHT, bDoWarn_=False)

                if not ((_curTE is None) or _curTE.teIsAutoEnclosedEntry):
                    _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_TaskMgr_TID_004).format(_curHT.name, _curTE.teTaskInst.dtaskUID, _curTE.teTaskInst.dtaskName)

                    if not _curTE.teIsXTaskEntry:
                        vlogif._LogOEC(True, _EFwErrorCode.VFE_00297)
                    else:
                        logif._LogErrorEC(_EFwErrorCode.UE_00095, _errMsg)
                    res = False
                else:
                    res = True

        return res

    def __PrecheckExecutableRequestByTaskID(self, tskID_: int) -> bool:
        res = False

        with self.__ma:
            _te = self.__GetTableEntry(taskID_=tskID_, bDoWarn_=True)

            if _te is None:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00298)

            else:
                _errMsg     = None
                _tinst = _te.teTaskInst
                _curTblE   = self.__GetCurTableEntry(bDoWarn_=False)

                if _tinst.isAutoEnclosed:
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00299)

                elif _tinst.isStarted:
                    _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_TaskMgr_TID_005).format(tskID_, str(_tinst))

                elif not _tinst.isInitialized:
                    _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_TaskMgr_TID_006).format(tskID_, str(_tinst))

                if _tinst.isEnclosingPyThread:
                    if _tinst.isEnclosingPyThread and not _TaskUtil.IsCurPyThread(_tinst.dHThrd):
                        _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_TaskMgr_TID_007).format(tskID_, _tinst.dHThrd.name, _TaskUtil.GetCurPyThread().name)
                    elif (_curTblE is not None) and (not _curTblE.teIsAutoEnclosedEntry) and id(_tinst) != id(_curTblE.teTaskInst):
                        _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_TaskMgr_TID_008).format(tskID_, _tinst.dtaskName, _curTblE.teTaskInst.dtaskUID, _curTblE.teTaskInst.dtaskName)
                    else:
                        res = True
                else:
                    res = True

                if not res:
                    if _errMsg is not None:
                        if (_curTblE is not None) and not (_curTblE.teIsAutoEnclosedEntry or _curTblE.teIsXTaskEntry):
                            vlogif._LogOEC(True, _EFwErrorCode.VFE_00300)
                        else:
                            logif._LogErrorEC(_EFwErrorCode.UE_00096, _errMsg)
        return res

    def __CreateStartProfiledTask(self, fwtPrf_ : _FwTaskProfile, bStart_ : bool, tskOpPCheck_ : _ATaskOpPreCheck =None) -> Union[_FwTask, None]:
        if not (isinstance(fwtPrf_, _FwTaskProfile) and fwtPrf_.isValid):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00301)
            return None

        self.__ma.Take()

        _autoEnclTE = None
        _curTblE = self.__GetCurTableEntry(bDoWarn_=False)
        if fwtPrf_.isEnclosingPyThread:
            _autoEnclTE = _curTblE
            if _autoEnclTE is not None:
                if not _autoEnclTE.teIsAutoEnclosedEntry:
                    _autoEnclTE.CleanUp()
                    self.__ma.Give()
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00302)
                    return None

        res = None
        try:
            res = _FwTask._CreateTask(fwtPrf_=fwtPrf_)
        except _XcoXcpRootBase as _xcp:
            if self.__CheckForReraiseXcoException(_xcp):
                self.__ma.Give()

                raise _xcp

        except BaseException as _xcp:
            _xbXcp = _XcoBaseException(_xcp, tb_=logif._GetFormattedTraceback())
            self.__HandleXcoBaseException(_xbXcp, curTask_=None if _curTblE is None else _curTblE.teTaskInst)

        if res is None:
            if _autoEnclTE is not None:
                _autoEnclTE.CleanUp()
            self.__ma.Give()
            return None

        if _autoEnclTE is not None:
            _autoEnclTI = _autoEnclTE.teTaskInst
            if not self.__RemoveFromTable(_autoEnclTE.teTaskInst):
                _tid, _tname = res.dtaskUID, res.dtaskName
                self.__ma.Give()
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00303)
                _autoEnclTE.CleanUp()
                return None
            else:
                _autoEnclTI.CleanUp()

        if not self.__AddToTable(res):
            res.CleanUp()
            self.__ma.Give()
            return None

        if not res.isEnclosingPyThread:
            _bDoStart = bStart_
        else:
            _bDoStart = res.isAutoStartEnclHThrdEnabled if bStart_ is None else bStart_

        if not _bDoStart:
            self.__ma.Give()
        elif not self.__StartTaskInstance(res, tskOpPCheck_, cleanupOnFailure_=True):
            res = None
        return res

    def __CheckCreateTaskRequest( self
                                , fwtPrf_         : _FwTaskProfile =None
                                , rbl_            : _AbsRunnable   =None
                                , taskName_       : str            =None
                                , rmask_          : _ETaskResFlag  =None
                                , delayedStartMS_ : int            =None
                                , enclHThrd_      : _PyThread      =None
                                , bASEnclHThrd_   : bool =None
                                , args_           : list =None
                                , kwargs_         : dict =None
                                , tpAttrs_        : dict =None) -> Union[_FwTaskProfile, None]:
        res, _bValid, _enclHThrd = fwtPrf_, True, None

        with self.__ma:
            if res is None:
                res = _FwTaskProfile( rbl_=rbl_
                                    , taskName_=taskName_
                                    , rmask_=rmask_
                                    , delayedStartMS_=delayedStartMS_
                                    , enclHThrd_=enclHThrd_
                                    , bASEnclHThrd_=bASEnclHThrd_
                                    , args_=args_
                                    , kwargs_=kwargs_
                                    , tpAttrs_=tpAttrs_ )

            if not isinstance(res, _FwTaskProfile):
                _bValid = False
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00304)
            elif not (res.isValid and res.runnable is not None):
                _bValid = False
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00305)
            else:
                _enclHThrd = res.enclosedPyThread
                if (_enclHThrd is not None) and not _enclHThrd.is_alive():
                    _bValid = False
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00306)

            if _bValid and (_enclHThrd is not None):
                _te = self.__GetTableEntry(hthrd_=_enclHThrd, bDoWarn_=False)
                if _te is not None:
                    _bValid = False
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00307)
                elif not _TaskUtil.IsCurPyThread(_enclHThrd):
                    _bValid = False
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00308)

            if not _bValid:
                if (res is not None) and fwtPrf_ is None:
                    res.CleanUp()
        return res

    def __CreateStartThread( self
                           , fwthrdPrf_   : _FwThreadProfile =None
                           , utConn_      : _IUTaskConn      =None
                           , taskName_    : str              =None
                           , enclHThrd_   : _PyThread        =None
                           , bStart_      : bool             =None
                           , thrdTgtCIF_  : _FwCallable      =None
                           , args_        : list             =None
                           , kwargs_      : dict             =None
                           , tpAttrs_     : dict             =None
                           , tskOpPCheck_ : _ATaskOpPreCheck =None) -> Union[_FwThread, None]:
        self.__ma.Take()

        _autoEnclTE, _curTblE = None, self.__GetCurTableEntry(bDoWarn_=False)

        if fwthrdPrf_.isEnclosingPyThread:
            _autoEnclTE = _curTblE
            if _autoEnclTE is not None:
                if not _autoEnclTE.teIsAutoEnclosedEntry:
                    _autoEnclTE.CleanUp()
                    self.__ma.Give()
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00309)
                    return None

        res = None
        try:
            res = _FwThread._CreateThread( fwthrdPrf_=fwthrdPrf_
                                         , utaskConn_=utConn_
                                         , taskName_=taskName_
                                         , enclHThrd_=enclHThrd_
                                         , bASEnclHThrd_=False
                                         , thrdTgtCIF_=thrdTgtCIF_
                                         , args_=args_
                                         , kwargs_=kwargs_
                                         , tpAttrs_=tpAttrs_)
        except _XcoXcpRootBase as _xcp:
            if self.__CheckForReraiseXcoException(_xcp):
                self.__ma.Give()

                raise _xcp

        except BaseException as _xcp:
            _xbXcp = _XcoBaseException(_xcp, tb_=logif._GetFormattedTraceback())
            self.__HandleXcoBaseException(_xbXcp, curTask_=None if _curTblE is None else _curTblE.teTaskInst)

        if res is None:
            if _autoEnclTE is not None:
                _autoEnclTE.CleanUp()
            self.__ma.Give()
            return None

        if _autoEnclTE is not None:
            _autoEnclTI = _autoEnclTE.teTaskInst
            if not self.__RemoveFromTable(_autoEnclTE.teTaskInst):
                _tid, _tname = res.dtaskUID, res.dtaskName
                self.__ma.Give()
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00310)
                return None
            else:
                _autoEnclTI.CleanUp()

        if not self.__AddToTable(res):
            res.CleanUp()
            self.__ma.Give()
            return None

        if not res.isEnclosingPyThread:
            _bDoStart = bStart_
        else:
            _bDoStart = res.isAutoStartEnclHThrdEnabled if bStart_ is None else bStart_

        if not _bDoStart:
            self.__ma.Give()
        else:
            if not self.__StartTaskInstance(res, tskOpPCheck_, cleanupOnFailure_=True):
                res = None
        return res

    def __EncloseCurThread(self, bAEnclosed_ =False, bSkipCheck_ =False) -> Union[_FwThread, None]:
        self.__ma.Take()

        res    = None
        _curHT = _TaskUtil.GetCurPyThread()
        _te    = None if bSkipCheck_ else self.__GetTableEntry(hthrd_=_curHT)

        if _te is not None:
            if not isinstance(_te.teTaskInst, _FwThread):
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00311)
            else:
                res = _te.teTaskInst

            self.__ma.Give()
            return res

        _xbXcp = None
        try:
            res = _FwThread._CreateThread(enclHThrd_=_curHT, bAEnclHThrd_=bAEnclosed_, bASEnclHThrd_=False)
            if res is None:
                pass
            elif not self.__AddToTable(res):
                res.CleanUp()
                res = None

        except _XcoXcpRootBase as _xcp:
            if self.__CheckForReraiseXcoException(_xcp):
                self.__ma.Give()
                raise _xcp

        except BaseException as _xcp:
            if _TaskManager._theTMgrImpl is None:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00312)
            else:
                _xbXcp = _XcoBaseException(_xcp, tb_=logif._GetFormattedTraceback())

        finally:
            self.__ma.Give()

            if _xbXcp is not None:
                self.__HandleXcoBaseException(_xbXcp, bCausedByTMgr_=True)

        return res
