# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : taskmgrimpl.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from collections import OrderedDict as _PyOrderedDict
from typing      import Union as _PyUnion

from xcofdk._xcofwa.fwadmindefs import _FwAdapterConfig
from xcofdk._xcofwa.fwadmindefs import _FwSubsystemCoding

from xcofdk._xcofw.fw.fwssys.fwcore.logging                   import logif
from xcofdk._xcofw.fw.fwssys.fwcore.logging                   import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.logging.xcoexception      import _XcoExceptionRoot
from xcofdk._xcofw.fw.fwssys.fwcore.logging.xcoexception      import _XcoBaseException
from xcofdk._xcofw.fw.fwssys.fwcore.apiimpl.xtask.xtaskconnif import _XTaskConnectorIF
from xcofdk._xcofw.fw.fwssys.fwcore.base.callableif           import _CallableIF
from xcofdk._xcofw.fw.fwssys.fwcore.base.gtimeout             import _Timeout
from xcofdk._xcofw.fw.fwssys.fwcore.base.util                 import _Util
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.arunnablefwc      import _AbstractRunnable
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.xtaskrunnable     import _XTaskRunnable
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.sync.mutex            import _Mutex
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.sync.semaphore        import _BinarySemaphore
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.atask             import _AbstractTask
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.ataskop           import _EATaskOperationID
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.ataskop           import _ATaskOperationPreCheck
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.fwtask            import _FwTask
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.fwthread          import _FwThread
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskbadge         import _TaskBadge
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskerror         import _TaskError
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskmgr           import _TaskManager
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskprofile       import _TaskProfile
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskstate         import _TaskState
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.threadprofile     import _ThreadProfile
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil          import _TaskUtil
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil          import _ETaskRightFlag
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil          import _ETaskResourceFlag
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil          import _EFwApiBookmarkID
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil          import _AutoEnclosedThreadsBag
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil          import _PyThread
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcdefines              import _ELcCompID
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcproxy                import _LcProxy
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcproxyclient          import _LcProxyClient
from xcofdk._xcofw.fw.fwssys.fwcore.lcmon.lcmonimpl           import _LcMonitorImpl
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject             import _AbstractSlotsObject
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes         import _CommonDefines
from xcofdk._xcofw.fw.fwssys.fwcore.types.aprofile            import _AbstractProfile

from xcofdk._xcofw.fw.fwssys.fwmsg.msg import _EMessagePeer

from xcofdk._xcofw.fw.fwssys.fwerrh.fwerrorcodes import _EFwErrorCode

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine

class _TaskManagerImpl(_TaskManager, _LcProxyClient):

    class __TaskEntry(_AbstractSlotsObject):

        __slots__ = [ '__taskInst' ]

        def __init__(self, taskInst_ : _AbstractTask):
            super().__init__()
            self.__taskInst = None

            if not _Util.IsInstance(taskInst_, _AbstractTask):
                self.CleanUp()
            else:
                self.__taskInst = taskInst_

        @property
        def teTaskID(self) -> int:
            res = self.teTaskBadge
            return None if res is None else res.taskID

        @property
        def teTaskName(self) -> str:
            res = self.teTaskBadge
            return None if res is None else res.taskName

        @property
        def teTaskUniqueName(self) -> str:
            res = self.teTaskBadge
            return None if res is None else res.taskUniqueName

        @property
        def teTaskBadge(self) -> _TaskBadge:
            return None if self.__taskInst is None else self.__taskInst.taskBadge

        @property
        def teTaskError(self) -> _TaskError:
            return None if self.__taskInst is None else self.__taskInst.taskError

        @property
        def teTaskInst(self) -> _AbstractTask:
            return self.__taskInst

        @property
        def teIsAutoEnclosedEntry(self) -> bool:
            return False if self.__taskInst is None else self.__taskInst.isAutoEnclosed

        @property
        def teIsXTaskEntry(self) -> bool:
            res = False
            if self.__taskInst is None:
                pass
            else:
                linkedXtbl = self.__taskInst.linkedExecutable
                if linkedXtbl is None:
                    pass
                else:
                    res = linkedXtbl.isXtask or linkedXtbl.isXTaskRunnable
            return res

        def _CleanUp(self):
            self.__taskInst = None
    
        def _ToString(self, *args_, **kwargs_):
            if self.__taskInst is None:
                return None

            if len(args_) > 2:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00263)
    
            if len(kwargs_) > 0:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00264)
    
            printNID = False
            printUID = False
    
            for _ii in range(len(args_)):
                if 0 == _ii: printNID = args_[_ii]
                if 1 == _ii: printUID = args_[_ii]

            if printUID:
                _tuid = self.teTaskBadge.threadUID
                if printNID and _TaskUtil.IsNativeThreadIdSupported():
                    res = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_TaskManager_TextID_012).format(
                        self.teTaskID, self.teTaskBadge.threadNID, _tuid, self.teTaskName, self.teTaskInst.isEnclosingPyThread, self.teTaskInst.isAlive, self.teTaskInst.taskStateID.compactName.lower())
                else:
                    res = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_TaskManager_TextID_013).format(
                        self.teTaskID, _tuid, self.teTaskName, self.teTaskInst.isEnclosingPyThread, self.teTaskInst.isAlive, self.teTaskInst.taskStateID.compactName.lower())
            else:
                if printNID and _TaskUtil.IsNativeThreadIdSupported():
                    res = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_TaskManager_TextID_014).format(
                        self.teTaskID, self.teTaskBadge.threadNID, self.teTaskName, self.teTaskInst.isEnclosingPyThread, self.teTaskInst.isAlive, self.teTaskInst.taskStateID.compactName.lower())
                else:
                    res = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_TaskManager_TextID_015).format(
                        self.teTaskID, self.teTaskName, self.teTaskInst.isEnclosingPyThread, self.teTaskInst.isAlive, self.teTaskInst.taskStateID.compactName.lower())
            return res

    __slots__ = [ '__mtxApi' , '__mtxData' , '__tidtable' , '__tuidtable' , '__tnametable' , '__semSS' , '__lcMon' , '__bFailed' ]

    def __init__(self):
        self.__lcMon      = None
        self.__semSS      = None
        self.__mtxApi     = None
        self.__mtxData    = None
        self.__bFailed    = None
        self.__tidtable   = None
        self.__tuidtable  = None
        self.__tnametable = None

        _TaskManager.__init__(self)
        _LcProxyClient.__init__(self)

        if _TaskManager._theTMgrImpl is not None:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00265)
            self.CleanUp()
        else:
            self.__bFailed    = False
            self.__tidtable   = _PyOrderedDict()
            self.__tuidtable  = _PyOrderedDict()
            self.__tnametable = _PyOrderedDict()

            self.__semSS   = _BinarySemaphore()
            self.__mtxApi  = _Mutex()
            self.__mtxData = _Mutex()

            if self.__EncloseCurThread(bAutoEnclosed_=True, bSkipTableEntryCheck_=True) is None:
                logif._XLogFatalEC(_EFwErrorCode.FE_00925, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_TaskManager_TextID_001))
                self.CleanUp()
            else:
                _TaskManager._theTMgrImpl = self

    def _PcClientName(self) -> str:
        return _FwTDbEngine.GetText(_EFwTextID.eELcCompID_TMgr)

    def _ToString(self, *args_, **kwargs_):
        if self.__isTMgrInvalid:
            return None
        with self.__mtxData:
            res = 'TMgr: #tasks={}'.format(len(self.__tidtable))
            return res

    def _CleanUp(self):
        if self.__isTMgrInvalid:
            return

        _TaskManager._theTMgrImpl = None

        self.__StopAllTasks(bCleanupStoppedTasks_=False, lstSkipTaskIDs_=None, bSkipStartupThrd_=False)

        for _vv in self.__tidtable.values():
            _vv.CleanUp()

        self.__lcMon   = None
        self.__bFailed = None

        self.__tnametable.clear()
        self.__tnametable = None

        self.__tuidtable.clear()
        self.__tuidtable = None

        self.__tidtable.clear()
        self.__tidtable = None

        self.__semSS.CleanUp()
        self.__semSS = None

        self.__mtxData.CleanUp()
        self.__mtxData = None

        self.__mtxApi.CleanUp()
        self.__mtxApi = None

        _LcProxyClient._CleanUp(self)

    @property
    def _isTMgrApiFullyAvailable(self):
        return self.__isMyApiFullyAvailable

    def _IsCurTask(self, taskID_ : int):
        if not isinstance(taskID_, int):
            return False
        if self.__isMyApiNotFullyAvailable:
            return False
        _bg, _ti = self.__GetCurTaskBadge()
        res = (_bg is not None) and _bg.taskID == taskID_
        return res

    def _CreateTask( self
                   , taskPrf_                : _TaskProfile            =None
                   , runnable_               : _AbstractRunnable       =None
                   , taskName_               : str                     =None
                   , enclosedPyThread_       : _PyThread               =None
                   , resourcesMask_          : _ETaskResourceFlag      =None
                   , delayedStartTimeSpanMS_ : int                     =None
                   , args_                   : list                    =None
                   , kwargs_                 : dict                    =None
                   , taskProfileAttrs_       : dict                    =None
                   , bStart_                 : bool                    =False
                   , tskOpPreCheck_          : _ATaskOperationPreCheck =None  ) -> _PyUnion[int, None]:
        res = None
        if not self.__isMyApiNotFullyAvailable:
            ept = enclosedPyThread_
            if (ept is None) and (taskProfileAttrs_ is not None):
                if _AbstractProfile._ATTR_KEY_ENCLOSED_PYTHREAD in taskProfileAttrs_:
                    ept = taskProfileAttrs_[_AbstractProfile._ATTR_KEY_ENCLOSED_PYTHREAD]
            if not self.__PrecheckExecutableRequest(tskID_=None, aprofile_=taskPrf_, enclPyThrd_=ept):
                return None

            _tp = self.__CheckCreateTaskRequest( taskPrf_=taskPrf_
                                               , runnable_=runnable_
                                               , taskName_=taskName_
                                               , resourcesMask_=resourcesMask_
                                               , delayedStartTimeSpanMS_=delayedStartTimeSpanMS_
                                               , enclosedPyThread_=enclosedPyThread_
                                               , args_=args_
                                               , kwargs_=kwargs_
                                               , taskProfileAttrs_=taskProfileAttrs_)
            if _tp is not None:
                res = self.__CreateStartProfiledTask(_tp, bStart_, tskOpPreCheck_=tskOpPreCheck_)
                if res is None:
                    if taskPrf_ is None:
                        _tp.CleanUp()
                else:
                    res = res.taskID
        return res

    def _CreateThread( self
                     , thrdProfile_            : _ThreadProfile          =None
                     , xtConn_                 : _XTaskConnectorIF       =None
                     , taskName_               : str                     =None
                     , enclosedPyThread_       : _PyThread               =None
                     , bStart_                 : bool                    =None
                     , threadTargetCallableIF_ : _CallableIF             =None
                     , args_                   : list                    =None
                     , kwargs_                 : dict                    =None
                     , threadProfileAttrs_     : dict                    =None
                     , tskOpPreCheck_          : _ATaskOperationPreCheck =None ) -> _PyUnion[int, None]:
        res = None
        if not self.__isMyApiNotFullyAvailable:
            ept = enclosedPyThread_
            if (ept is None) and (threadProfileAttrs_ is not None):
                if _AbstractProfile._ATTR_KEY_ENCLOSED_PYTHREAD in threadProfileAttrs_:
                    ept = threadProfileAttrs_[_AbstractProfile._ATTR_KEY_ENCLOSED_PYTHREAD]
            if not self.__PrecheckExecutableRequest(tskID_=None, aprofile_=thrdProfile_, enclPyThrd_=ept):
                return None

            res = self.__CreateStartThread( thrdProfile_=thrdProfile_
                                          , xtConn_=xtConn_
                                          , taskName_=taskName_
                                          , enclosedPyThread_=enclosedPyThread_
                                          , bStart_=bStart_
                                          , threadTargetCallableIF_=threadTargetCallableIF_
                                          , args_=args_
                                          , kwargs_=kwargs_
                                          , threadProfileAttrs_=threadProfileAttrs_
                                          , tskOpPreCheck_=tskOpPreCheck_)
            if res is not None:
                res = res.taskID
        return res

    def _GetCurTaskBadge(self):
        if self.__isMyApiNotFullyAvailable:
            return None
        _bg, _ti = self.__GetCurTaskBadge()
        return _bg

    def _GetTaskError(self, taskID_ =None):
        if self.__isMyApiNotFullyAvailable:
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

    def _GetTask(self, taskID_ : _PyUnion[int, _EMessagePeer], bDoWarn_ =True):
        if self.__isMyApiNotFullyAvailable:
            return None
        if not isinstance(taskID_, (int, _EMessagePeer)):
            return None
        res = self.__GetTableEntry(taskID_=taskID_, bDoWarn_=bDoWarn_)
        if res is not None:
            res = res.teTaskInst
        return res

    def _GetTaskID(self, taskName_):
        if self.__isMyApiNotFullyAvailable:
            return None
        with self.__mtxData:
            res = None
            if taskName_ in self.__tnametable:
                _te = self.__tnametable[taskName_]
                res = _te.teTaskID
            return res

    def _GetTaskBadge(self, taskID_ : _PyUnion[int, _EMessagePeer], bDoWarn_ =True):
        if self.__isMyApiNotFullyAvailable:
            return None
        if not isinstance(taskID_, (int, _EMessagePeer)):
            return None
        res = self.__GetTableEntry(taskID_=taskID_, bDoWarn_=bDoWarn_)
        if res is not None:
            res = res.teTaskBadge
        return res

    def _StartTask(self, taskID_, tskOpPreCheck_ : _ATaskOperationPreCheck =None, bSkipPrecheck_ =False) -> bool:
        if self.__isMyApiNotFullyAvailable:
            return False

        self.__mtxApi.Take()
        if not bSkipPrecheck_:
            if not self.__PrecheckExecutableRequest(tskID_=taskID_, aprofile_=None, enclPyThrd_=None):
                self.__mtxApi.Give()
                return False

        _te = self.__GetTableEntry(taskID_=taskID_)
        if _te is None:
            self.__mtxApi.Give()
            return False
        return self.__StartTaskInstance(_te.teTaskInst, tskOpPreCheck_, cleanupOnFailure_=False)

    def _StopTask(self, taskID_, removeTask_=True, tskOpPreCheck_ : _ATaskOperationPreCheck =None) -> bool:
        if self.__isMyApiNotFullyAvailable:
            return False
        else:
            _tid = self.__StopTaskByID(taskID_, removeTask_=removeTask_, tskOpPreCheck_=tskOpPreCheck_)
            return _tid is not None

    def _JoinTask(self, taskID_, timeout_ : _Timeout =None, tskOpPreCheck_ : _ATaskOperationPreCheck =None, curTask_ : _AbstractTask =None) -> bool:
        if self.__isMyApiNotFullyAvailable:
            return False

        with self.__mtxApi:
            _te = self.__GetTableEntry(taskID_=taskID_)
            if _te is None:
                return False

            _ti = _te.teTaskInst
            _oppc = _TaskManagerImpl.__GetTaskOpPreCheck(_ti, _EATaskOperationID.eJoin, tskOpPreCheck_=tskOpPreCheck_)
            if _oppc.isNotApplicable or _oppc.isIgnorable:
                res = _oppc.isIgnorable
                if tskOpPreCheck_ is None:
                    _oppc.CleanUp()
                return res

        res = _ti.JoinTask(timeout_, tskOpPreCheck_=_oppc, curTask_=curTask_)
        if tskOpPreCheck_ is None:
            _oppc.CleanUp()
        return res

    def _StartXTask(self, xtConn_ : _XTaskConnectorIF, tskOpPreCheck_ : _ATaskOperationPreCheck =None) -> bool:
        if self.__isMyApiNotFullyAvailable:
            return False
        elif not (isinstance(xtConn_, _XTaskConnectorIF) and xtConn_._isXTaskConnected):
            if not isinstance(xtConn_, _XTaskConnectorIF):
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00266)
            else:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00267)
            return False
        elif xtConn_._isStarted:
            return xtConn_._isPendingRun or xtConn_._isRunning or xtConn_._isDone
        elif not xtConn_._connectedXTask.isXtask:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00268)
            return False

        res       = False
        _atsk     = None
        _curTsk   = None
        _mySysXcp = None

        try:
            _curTsk = self.__BookmarkCurTask(_EFwApiBookmarkID.eXTaskApiRequestStart)

            _tid        = xtConn_._connectedXTask.executableUniqueID
            _xtp        = xtConn_.xtaskProfile
            _enclPyThrd = None

            if _tid is None:
                if _xtp.isSynchronousTask:
                    _enclPyThrd = _TaskUtil.GetCurPyThread()

            if not self.__PrecheckExecutableRequest(tskID_=_tid, aprofile_=None, enclPyThrd_=_enclPyThrd):
                return False

            if _tid is not None:
                res = self._StartTask(_tid, tskOpPreCheck_=tskOpPreCheck_, bSkipPrecheck_=True)
            else:
                enclThrd = None
                if _xtp.isSynchronousTask:
                    enclThrd = _TaskUtil.GetCurPyThread()
                _tp = _TaskManagerImpl.__CreateXTaskProfile(xtConn_, enclosedPyThread_=enclThrd, profileAttrs_=None)
                if _tp is None:
                    pass
                elif _tp.isTaskProfile:
                    _atsk = self.__CreateStartProfiledTask(_tp, True, tskOpPreCheck_=tskOpPreCheck_)
                else:
                    _atsk = self.__CreateStartThread(thrdProfile_=_tp, bStart_=True, tskOpPreCheck_=tskOpPreCheck_)
                res = (_atsk is not None) and _atsk.isStarted and not (_atsk.isFailed or _atsk.isAborting)

        except _XcoExceptionRoot as xcp:
            if self.__CheckForReraiseXcoException(xcp):
                raise xcp

        except BaseException as xcp:
            _mySysXcp = _XcoBaseException(xcp, tb_=logif._GetFormattedTraceback())
        finally:
            if _mySysXcp is not None:
                self.__HandleXcoBaseException(_mySysXcp, curTask_=_curTsk)

        if _curTsk is not None:
            self.__BookmarkCurTask(_EFwApiBookmarkID.eNone, curTask_=_curTsk)

        return res

    def _StopXTask(self, xtConn_ : _XTaskConnectorIF, cleanupDriver_ =True, tskOpPreCheck_ : _ATaskOperationPreCheck =None) -> bool:
        if self.__isMyApiNotFullyAvailable:
            return False
        elif not (isinstance(xtConn_, _XTaskConnectorIF) and xtConn_._isXTaskConnected):
            if not isinstance(xtConn_, _XTaskConnectorIF):
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00271)
            else:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00272)
            return False

        _tid      = None
        _xtUID    = None
        _curTsk   = None
        _mySysXcp = None
        try:
            _curTsk = self.__BookmarkCurTask(_EFwApiBookmarkID.eXTaskApiRequestStop)

            _bTD   = xtConn_.xtaskProfile.isTeardownPhaseEnabled
            _cxt   = xtConn_._connectedXTask
            _xtUID = None if _cxt is None else _cxt.xtaskUniqueID

            if _xtUID is not None:
                if _bTD:
                    cleanupDriver_ = False
                _tid = self.__StopTaskByID(_xtUID, removeTask_=cleanupDriver_, tskOpPreCheck_=tskOpPreCheck_, curTask_=_curTsk)

        except _XcoExceptionRoot as xcp:
            if self.__CheckForReraiseXcoException(xcp):
                raise xcp

        except BaseException as xcp:
            _mySysXcp = _XcoBaseException(xcp, tb_=logif._GetFormattedTraceback())

        finally:
            if _mySysXcp is not None:
                self.__HandleXcoBaseException(_mySysXcp, curTask_=_curTsk)

        if _curTsk is not None:
            self.__BookmarkCurTask(_EFwApiBookmarkID.eNone, curTask_=_curTsk)

        return (_xtUID is None) or (_tid is not None)

    def _JoinXTask(self, xtConn_ : _XTaskConnectorIF, timeout_ : _Timeout =None, tskOpPreCheck_ : _ATaskOperationPreCheck =None) -> bool:
        if self.__isMyApiNotFullyAvailable:
            return False
        elif not (isinstance(xtConn_, _XTaskConnectorIF) and xtConn_._isXTaskConnected):
            if not isinstance(xtConn_, _XTaskConnectorIF):
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00273)
            return False

        res       = False
        _curTsk   = None
        _mySysXcp = None
        try:
            _curTsk = self.__BookmarkCurTask(_EFwApiBookmarkID.eXTaskApiRequestJoin)

            _cxt   = xtConn_._connectedXTask
            _xtUID = None if _cxt is None else _cxt.xtaskUniqueID

            if _xtUID is None:
                res = True
            else:
                res = self._JoinTask(_xtUID, timeout_=timeout_, tskOpPreCheck_=tskOpPreCheck_, curTask_=_curTsk)

        except _XcoExceptionRoot as xcp:
            if self.__CheckForReraiseXcoException(xcp):
                raise xcp

        except BaseException as xcp:
            _mySysXcp = _XcoBaseException(xcp, tb_=logif._GetFormattedTraceback())

        finally:
            if _mySysXcp is not None:
                self.__HandleXcoBaseException(_mySysXcp, curTask_=_curTsk)

        if _curTsk is not None:
            self.__BookmarkCurTask(_EFwApiBookmarkID.eNone, curTask_=_curTsk)

        return res

    def _ProcUnhandledXcp(self, xcp_: _XcoExceptionRoot):
        if self.__isMyApiNotFullyAvailable:
            return False
        else:
            _te = self.__GetCurTableEntry(bDoWarn_=True)
            if (_te is None) or _te.teIsAutoEnclosedEntry:
                return False
            else:
                return _te.teTaskInst._ProcUnhandledException(xcp_)

    @staticmethod
    def _CreateXTaskProfile(xtConn_ : _XTaskConnectorIF, enclosedPyThread_ : _PyThread =None, profileAttrs_ : dict =None):
        return _TaskManagerImpl.__CreateXTaskProfile(xtConn_, enclosedPyThread_=enclosedPyThread_, profileAttrs_=profileAttrs_)

    @staticmethod
    def _GetLcProxy() -> _LcProxy:
        res = None
        if _TaskManager._theTMgrImpl is None:
            pass
        elif _TaskManager._theTMgrImpl.__isTMgrInvalid:
            pass
        else:
            res = _TaskManager._theTMgrImpl._PcGetLcProxy()
        return res

    def _GetCurTask(self, bAutoEncloseMissingThread_ =True) -> _AbstractTask:
        if self.__isTMgrInvalid:
            return None
        else:
            _bg, res = self.__GetCurTaskBadge(bAutoEncloseMissingThread_=bAutoEncloseMissingThread_)
            return res

    def _GetProxyInfoReplacementData(self):

        if self.__isTMgrInvalid:
            return None, None

        with self.__mtxData:
            _curPyThrd = _TaskUtil.GetCurPyThread()
            _tuid      = _TaskUtil.GetPyThreadUniqueID(_curPyThrd)

            _tname    = None
            _bXTask = False
            _te       = None if _tuid not in self.__tuidtable else self.__tuidtable[_tuid]
            if _te is None:
                _tname, _bXTask = _curPyThrd.name, False
            else:
                _tname, _bXTask = _te.teTaskName, _te.teIsXTaskEntry

            return _tname, _bXTask

    def _GetTaskErrorByTID(self, taskID_ : int) -> _AbstractTask:
        if self.__isTMgrInvalid:
            return None
        elif not isinstance(taskID_, int):
            return None
        res = self.__GetTableEntry(taskID_=taskID_)
        if res is not None:
            res = res.teTaskInst
        if res is not None:
            res = res.taskError
        return res

    def _SetLcMonitorImpl(self, lcMonImpl_: _LcMonitorImpl):
        if isinstance(lcMonImpl_, _LcMonitorImpl) and lcMonImpl_.isValid and not lcMonImpl_.isDummyMonitor:
            self.__lcMon = lcMonImpl_

    def _InjectLcProxy(self, lcProxy_ : _LcProxy):

        if self.__isTMgrInvalid:
            return False

        self._PcSetLcProxy(lcProxy_, bForceUnset_=True)

        if self._PcIsLcProxySet():
            with self.__mtxData:
                _ii = 0
                for _kk, _te in self.__tidtable.items():
                    if isinstance(_te.teTaskInst, _LcProxyClient):
                        if not _te.teTaskInst._PcIsLcProxySet():
                            _ii += 1
                            _te.teTaskInst._PcSetLcProxy(self)
        return True

    def _StopAllTasks(self, bCleanupStoppedTasks_ =True, lstSkipTaskIDs_ =None) -> list:
        if self.__isTMgrInvalid:
            res = None
        else:
            res = self.__StopAllTasks(bCleanupStoppedTasks_=bCleanupStoppedTasks_, lstSkipTaskIDs_=lstSkipTaskIDs_)
        return res

    def _AddTaskEntry(self, taskInst_ : _AbstractTask, removeAutoEnclosedTaskEntry_ =True):

        if self.__isTMgrInvalid:
            return None
        elif not isinstance(taskInst_, _AbstractTask):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00274)
            return None

        self.__mtxApi.Take()

        if taskInst_.isEnclosingPyThread:
            if removeAutoEnclosedTaskEntry_:
                _te = self.__GetTableEntry(pythread_=taskInst_.linkedPyThread, bDoWarn_=False)
                if _te is not None:
                    if _te.teIsAutoEnclosedEntry:
                        _aet = _te.teTaskInst
                        if not self.__RemoveFromTable(_aet):
                            self.__mtxApi.Give()
                            return None
                        else:
                            _aet.CleanUp()

        res = None
        if self.__AddToTable(taskInst_):
            res = taskInst_.taskID
        self.__mtxApi.Give()
        return res

    def _DetachTask(self, taskInst_ : _AbstractTask, cleanup_ =True):

       if self.__isTMgrInvalid:
           return
       elif not isinstance(taskInst_, _AbstractTask):
           vlogif._LogOEC(True, _EFwErrorCode.VFE_00275)
           return

       self.__mtxApi.Take()

       _te = self.__GetTableEntry(pythread_=taskInst_.linkedPyThread, bDoWarn_=False)
       if _te is None:
           pass
       elif not self.__RemoveFromTable(_te.teTaskInst):
           _ttn, _tn, _tid = type(taskInst_).__name__, taskInst_.taskName, taskInst_.taskID
           vlogif._LogOEC(False, _EFwErrorCode.VUE_00026)
       elif cleanup_:
           self.__CleanUpTaskInstance(taskInst_)
       self.__mtxApi.Give()

    @property
    def __isTMgrInvalid(self):
        return self.__tidtable is None

    @property
    def __isTMgrFailed(self):
        return False if self.__isTMgrInvalid else self.__bFailed

    @property
    def __isTMgrInvalidOrFailed(self):
        return True if self.__tidtable is None else self.__bFailed

    @property
    def __isMyApiNotFullyAvailable(self):
        if self.__isTMgrInvalidOrFailed:
            return True
        return not self._PcIsLcProxyModeNormal()

    @property
    def __isMyApiFullyAvailable(self):
        if self.__isTMgrInvalidOrFailed:
            return False
        return self._PcIsLcProxyModeNormal()

    @staticmethod
    def __CreateXTaskProfile(xtConn_ : _XTaskConnectorIF, enclosedPyThread_ : _PyThread =None, profileAttrs_ : dict =None):
        if not isinstance(xtConn_, _XTaskConnectorIF):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00276)
            return None
        elif not (xtConn_._isXTaskConnected and (xtConn_._connectedXTask is not None)):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00277)
            return None

        _TRM_KEY = _ThreadProfile._ATTR_KEY_TASK_RIGHTS

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

        _xtp = xtConn_.xtaskProfile
        if _xtp.isUnitTest:
            if not _trm.hasUnitTestTaskRight:
                _trm = _ETaskRightFlag.AddUnitTestTaskRight(_trm)

        profileAttrs_[_TRM_KEY] = _trm

        res = None

        try:
            if _xtp.isInternalQueueEnabled or _xtp.isExternalQueueEnabled:
                _rr = _XTaskRunnable(xtConn_)
                if _rr._eRunnableType is None:
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00279)
                else:
                    res = _TaskProfile(runnable_=_rr, enclosedPyThread_=enclosedPyThread_, taskProfileAttrs_=profileAttrs_)
            else:
                res = _ThreadProfile(xtaskConn_=xtConn_, enclosedPyThread_=enclosedPyThread_, threadProfileAttrs_=profileAttrs_)
        except (_XcoExceptionRoot, BaseException) as xcp:
            if _FwAdapterConfig._IsLogIFUTSwitchModeEnabled() or not logif._IsReleaseModeEnabled():
                raise xcp
            else:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00280)

        if res is not None:
            if not (res.isValid and res.isDrivingXTaskTaskProfile):
                logif._LogImplErrorEC(_EFwErrorCode.FE_00689, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_TaskManager_TextID_010).format(xtConn_._connectedXTask))
                res.CleanUp()
                res = None

        if res is None:
            logif._LogErrorEC(_EFwErrorCode.UE_00092, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_TaskManager_TextID_002).format(xtConn_._connectedXTask))
        return res

    @staticmethod
    def __GetTaskOpPreCheck(taskInst_ : _AbstractTask, eTaskOpID_ : _EATaskOperationID, tskOpPreCheck_: _ATaskOperationPreCheck = None) -> _ATaskOperationPreCheck:
        res = tskOpPreCheck_
        if res is None:
            res = _ATaskOperationPreCheck( eTaskOpID_, taskInst_._tskState
                                         , taskInst_._linkedPyThrd, taskInst_.isEnclosingPyThread, reportErr_=True)
        else:
            res.Update(reportErr_=True)
        return res

    def __BookmarkCurTask(self, eFwApiBookmarkID_ : _EFwApiBookmarkID, curTask_ : _AbstractTask =None) -> _AbstractTask:
        res = curTask_
        if res is None:
            res = self._GetCurTask()
        if res is not None:
            res._SetFwApiBookmark(eFwApiBookmarkID_)
        return res

    def __CheckForReraiseXcoException(self, xcp_: _XcoExceptionRoot, bForceReraise_ =True) -> bool:
        return self is not None

    def __HandleXcoBaseException(self, xcp_: _XcoBaseException, bCausedByTMgr_ =None, curTask_ : _AbstractTask =None):

        if self._PcIsTaskMgrFailed():
            return
        if not xcp_.isXcoBaseException:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00281)
            return

        _bDoLogSysXcp     = False
        _bRootCauseFWC    = False
        _bRootCauseTMgr   = False
        _bRootCauseClient = False

        _bCurTaskValid         = (curTask_ is not None) and curTask_.isValid
        _bCurTaskAutoEnclosed  = _bCurTaskValid and curTask_.isAutoEnclosed

        _bCurTaskNotTerminated = _bCurTaskValid and not curTask_.isTerminated

        if bCausedByTMgr_ is not None:
            if bCausedByTMgr_:
                _bRootCauseFWC, _bRootCauseTMgr = True, True

        if not _bRootCauseFWC:
            if not _bCurTaskNotTerminated:
                _bRootCauseFWC, _bRootCauseTMgr = True, True

            elif _bCurTaskAutoEnclosed:

                _fwApiBmID = curTask_.eFwApiBookmarkID
                if _fwApiBmID.isXTaskApiRequest:
                    _bRootCauseFWC, _bRootCauseTMgr = True, True
                elif _fwApiBmID.isXTaskApiBeginAction:
                    if curTask_.eTaskXPhase.isXTaskExecution:
                        _bRootCauseClient = True
                    else:
                        _bRootCauseFWC = True
                else:
                    _bRootCauseFWC = True

            else:
                _fwApiBmID = curTask_.eFwApiBookmarkID
                if _fwApiBmID.isXTaskApiRequest:
                    _bRootCauseFWC, _bRootCauseTMgr = True, True
                elif _fwApiBmID.isXTaskApiBeginAction:
                    if curTask_.eTaskXPhase.isXTaskExecution:
                        _bDoLogSysXcp, _bRootCauseClient = True, True
                    else:
                        _bDoLogSysXcp, _bRootCauseFWC = True, True
                else:
                    _bRootCauseFWC = True

        if _bDoLogSysXcp:
            logif._LogSysExceptionEC(_EFwErrorCode.FE_00016, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_TaskManager_TextID_003), xcp_._enclosedException, xcp_.traceback)
            return

        if not self.__bFailed:
            self.__bFailed = _bRootCauseTMgr

        if not (_bRootCauseFWC or _bRootCauseTMgr or _bRootCauseClient):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00282)
            return

        _bCreateFE = _bCurTaskAutoEnclosed or not (_bCurTaskNotTerminated and curTask_.isRunning)

        if _bRootCauseClient:
            _cc = _ELcCompID.eXTask
        elif _bRootCauseTMgr:
            _cc = _ELcCompID.eTMgr
        else:
            _cc = _ELcCompID.eFwComp

        _frc = None

        if _bCreateFE:
            _bFwTsk  = not _cc.isXtask
            _errCode = _EFwErrorCode.FE_00024 if _bFwTsk else _EFwErrorCode.FE_00926
            _frc     = logif._CreateLogFatalEC(_bFwTsk, _errCode, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_TaskManager_TextID_009).format(str(xcp_)))
        else:
            logif._LogUnhandledXcoBaseXcpEC(_EFwErrorCode.FE_00021, xcp_)

            _te = curTask_.taskError
            if (_te is None) or not _te.isFatalError:
                pass 
            else:
                _frc = _te._currentErrorEntry

        if _frc is not None:
            self._PcNotifyLcFailure(_cc, _frc, atask_=curTask_)

    def __PrintTaskTable(self, tabPrefixed_=False, printNavtiveID_=False, printIdent_=False):
        with self.__mtxData:
            _ttStr  = _CommonDefines._STR_EMPTY
            _prefix = _CommonDefines._CHAR_SIGN_SPACE * 4 if tabPrefixed_ else _CommonDefines._STR_EMPTY

            _ii = 0
            for _kk in self.__tidtable.keys():
                _vv = self.__tidtable[_kk]
                _ii += 1
                _ttStr += _FwTDbEngine.GetText(_EFwTextID.eLogMsg_TaskManager_TextID_011).format(_prefix, _ii) + _vv.ToString(printNavtiveID_, printIdent_) + _CommonDefines._CHAR_SIGN_NEWLINE
            vlogif._LogFree(_ttStr)

    def __GetCurTaskBadge(self, bAutoEncloseMissingThread_ =False):

        _te = None
        with self.__mtxData:
            _curPyThrd = _TaskUtil.GetCurPyThread()

            _te = self.__GetTableEntry(pythread_=_curPyThrd, bDoWarn_=True)
            if _te is None:
                if not bAutoEncloseMissingThread_:
                    pass
                else:
                    _tuid = _TaskUtil.GetPyThreadUniqueID(_curPyThrd)

                    if _AutoEnclosedThreadsBag.IsProcessingCurPyThread(curPyThrd_=_curPyThrd):
                        pass 
                    else:
                        _AutoEnclosedThreadsBag._AddPyThread(_curPyThrd)
                        _fthrd = self.__EncloseCurThread(bAutoEnclosed_=True, bSkipTableEntryCheck_=True)
                        _AutoEnclosedThreadsBag._RemovePyThread(_curPyThrd)

                        if _fthrd is None:
                            _errMsg = 'TMgr failed to auto-enclose current thread {}:{}.'.format(_curPyThrd.name, _tuid)
                            vlogif._LogOEC(True, _EFwErrorCode.VFE_00283)

                            if not self._PcIsTaskMgrFailed():
                                _myFE = logif._CreateLogImplErrorEC(_EFwErrorCode.FE_00030, _errMsg)
                                self._PcNotifyLcFailure(_ELcCompID.eTMgr, _myFE)
                        else:
                            _te = self.__GetTableEntry(taskID_=_fthrd.taskID)

        res = None
        _tinst = None
        if (_te is None) or (_te.teTaskBadge is None):
            pass
        else:
            res, _tinst = _te.teTaskBadge, _te.teTaskInst

            if _tinst.isAutoEnclosed:
                pass
            elif not _tinst.isEnclosingPyThread:
                pass
            elif (self.__lcMon is None) or not self.__lcMon.isLcShutdownEnabled:
                pass
            elif (_tinst.lcDynamicTLB is None) or _tinst.lcDynamicTLB.isDummyTLB:
                pass
            elif _tinst.isInLcCeaseMode:
                pass
            else:
                if _tinst.isRunning:
                    _AbstractTask._SetGetTaskState(_tinst, _TaskState._EState.ePendingStopRequest)
                    if not _tinst.isPendingStopRequest:
                        vlogif._LogOEC(True, _EFwErrorCode.VFE_00284)

        return res, _tinst

    def __GetCurTableEntry(self, bDoWarn_ =False):
        return self.__GetTableEntry(pythread_=_TaskUtil.GetCurPyThread(), bDoWarn_=bDoWarn_)

    def __GetTableEntry(self, taskID_ : _PyUnion[_EMessagePeer, int] =None, pythread_ : _PyThread =None, bDoWarn_=True):

        res = None
        _bEMessagePeer = isinstance(taskID_, _EMessagePeer)

        if not (_bEMessagePeer or isinstance(taskID_, int) or isinstance(pythread_, _PyThread)):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00285)
        elif _bEMessagePeer and not _FwSubsystemCoding.IsSubsystemMessagingConfigured():
            pass
        else:
            with self.__mtxData:
                if taskID_ is not None:
                    if _bEMessagePeer:
                        if not (taskID_.isPFwMain or taskID_.isPTimerManager):
                            pass
                        else:
                            for _kk, te in self.__tidtable.items():
                                _tbadge = te.teTaskBadge
                                if (_tbadge is None) or not _tbadge.isValid:
                                    continue
                                if not _tbadge.isFwTask:
                                    continue
                                if _tbadge.isXTaskTask:
                                    continue

                                _rbl = te.teTaskInst._linkedExecutable
                                if not (_rbl._eRunnableType.isFwMainRunnable or _rbl._eRunnableType.isTimerManagerRunnable):
                                    continue
                                if _rbl._eRunnableType.isFwMainRunnable and taskID_.isPFwMain:
                                    res = te
                                    break
                                if _rbl._eRunnableType.isTimerManagerRunnable and taskID_.isPTimerManager:
                                    res = te
                                    break
                                continue
                    elif taskID_ not in self.__tidtable:
                        if bDoWarn_:
                            vlogif._LogOEC(False, _EFwErrorCode.VUE_00027)
                    else:
                        res = self.__tidtable[taskID_]
                else:
                    _tuid = _TaskUtil.GetPyThreadUniqueID(pythread_)
                    if _tuid not in self.__tuidtable:
                        pass
                    else:
                        res = self.__tuidtable[_tuid]
        return res

    def __AddToTable(self, taskInst_ : _AbstractTask):

        if not isinstance(taskInst_, _AbstractTask):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00286)
            return False

        with self.__mtxData:
            _tid = taskInst_.taskID
            if _tid in self.__tidtable:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00287)
                return False

            _te = _TaskManagerImpl.__TaskEntry(taskInst_)
            self.__tidtable[_tid] = _te

            _tuid = taskInst_.threadUID
            self.__tuidtable[_tuid] = _te

            _tname = taskInst_.taskName
            if _tname in self.__tnametable:
                _teOther = self.__tnametable[_tname]
            else:
                self.__tnametable[_tname] = _te

            if self._PcIsLcProxyModeNormal():
                if isinstance(taskInst_, _LcProxyClient):
                    taskInst_._PcSetLcProxy(self)

            self.__RemoveCleanedUpEntries()
            return True

    def __RemoveFromTable(self, taskInst_ : _AbstractTask):

        if not isinstance(taskInst_, _AbstractTask):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00288)
            return False
        elif not taskInst_.isValid:
            return False

        with self.__mtxData:
            _tid   = taskInst_.taskID
            _tuid  = taskInst_.threadUID
            _tname = taskInst_.taskName

            if _tid not in self.__tidtable:
                return False
            elif _tuid not in self.__tuidtable:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00289)
                return False

            _teByName     = None
            _allTEsByName = [ self.__tnametable[_kk] for _kk in self.__tnametable if _tname in self.__tnametable ]
            for _te in _allTEsByName:
                if _te.teTaskID == taskInst_.taskID:
                    _teByName = _te
                    break
            if _teByName is not None:
                self.__tnametable[_tname] = None
                _AbstractSlotsObject.Delete(self.__tnametable, _tname)

            self.__tuidtable[_tuid] = None
            _AbstractSlotsObject.Delete(self.__tuidtable, _tuid)

            _te = self.__tidtable[_tid]
            self.__tidtable[_tid] = None
            _AbstractSlotsObject.Delete(self.__tidtable, _tid)
            _te.CleanUp()
            return True

    def __RemoveCleanedUpEntries(self):

        _rm = [ _kk for _kk, _te in self.__tidtable.items() if not _te.teTaskInst.isValid ]
        for _kk in _rm:
            self.__tidtable.pop(_kk)
        _rm = [ _kk for _kk, _te in self.__tuidtable.items() if not _te.teTaskInst.isValid ]
        for _kk in _rm:
            self.__tuidtable.pop(_kk)
        _rm = [ _kk for _kk, _te in self.__tnametable.items() if not _te.teTaskInst.isValid ]
        for _kk in _rm:
            self.__tnametable.pop(_kk)

    def __StartTaskInstance(self, taskInst_ : _AbstractTask, tskOpPreCheck_ : _ATaskOperationPreCheck, cleanupOnFailure_ =False) -> bool:

        _oppc = _TaskManagerImpl.__GetTaskOpPreCheck(taskInst_, _EATaskOperationID.eStart, tskOpPreCheck_=tskOpPreCheck_)
        if _oppc.isNotApplicable or _oppc.isIgnorable:
            if cleanupOnFailure_:
                res = False
                self.__RemoveFromTable(taskInst_)
                taskInst_.CleanUp()
            else:
                res = _oppc.isIgnorable

            if tskOpPreCheck_ is None:
                _oppc.CleanUp()

            self.__mtxApi.Give()
            return res

        _semSS = None if taskInst_.isEnclosingPyThread else self.__semSS

        res       = False
        _curTsk   = None
        _mySysXcp = None

        try:
            _curTblE = self.__GetCurTableEntry()
            if _curTblE is not None:
                _curTsk = _curTblE.teTaskInst

            if not _oppc.isASynchronous:
                self.__mtxApi.Give()

            res = taskInst_.StartTask(semStart_=_semSS, tskOpPreCheck_=tskOpPreCheck_, curTask_=_curTsk)

        except _XcoExceptionRoot as xcp:
            if self.__CheckForReraiseXcoException(xcp):
                if _oppc.isASynchronous:
                    self.__mtxApi.Give()

                raise xcp

        except BaseException as xcp:
            _mySysXcp = _XcoBaseException(xcp, tb_=logif._GetFormattedTraceback())

        finally:
            if _semSS is not None:
                _semSS.Take()

            if _oppc.isASynchronous:
                self.__mtxApi.Give()

            if tskOpPreCheck_ is None:
                _oppc.CleanUp()

            _bTaskGone = not taskInst_.isValid
            if _bTaskGone:
                res = False
            elif _mySysXcp is not None:
                res = False

            if not res:
                if cleanupOnFailure_:
                    if not _bTaskGone:
                        self.__RemoveFromTable(taskInst_)
                        taskInst_.CleanUp()

                if _mySysXcp is not None:
                    if _oppc.isASynchronous:
                        self.__mtxApi.Give()

                    self.__HandleXcoBaseException(_mySysXcp, curTask_=_curTsk)
        return res

    def __StopTaskByID(self, taskID_ : int, removeTask_ =True, tskOpPreCheck_ : _ATaskOperationPreCheck =None, curTask_ : _AbstractTask =None):
        if not _Util.IsInstance(taskID_, int, bThrowx_=True):
            return None

        self.__mtxApi.Take()

        _te = self.__GetTableEntry(taskID_=taskID_)
        if _te is None:
            self.__mtxApi.Give()
            return None

        _tinst = _te.teTaskInst
        if _tinst.isAutoEnclosed:
            if _tinst.taskStateID.isDone:
                pass 
            else:
                _AbstractTask._SetGetTaskState(_tinst, _TaskState._EState.eDone)

            if removeTask_:
                self.__RemoveFromTable(_tinst)
                self.__CleanUpTaskInstance(_tinst)

            self.__mtxApi.Give()
            return taskID_

        _oppc = _TaskManagerImpl.__GetTaskOpPreCheck(_tinst, _EATaskOperationID.eStop, tskOpPreCheck_=tskOpPreCheck_)
        if _oppc.isNotApplicable or _oppc.isIgnorable:
            _bIgnorable = _oppc.isIgnorable
            if tskOpPreCheck_ is None:
                _oppc.CleanUp()

            if _bIgnorable:
                if removeTask_:
                    self.__RemoveFromTable(_tinst)
                    self.__CleanUpTaskInstance(_tinst)
            self.__mtxApi.Give()
            return taskID_ if _bIgnorable else None

        _semSS= None
        _bASynchronous = _oppc.isASynchronous
        if _bASynchronous:
            if not _tinst.isEnclosingPyThread:
                if _tinst.linkedExecutable is not None:
                    _semSS = self.__semSS

        if not _bASynchronous:
            self.__mtxApi.Give()

        _bStopOK = _tinst.StopTask(semStop_=_semSS, tskOpPreCheck_=_oppc, curTask_=curTask_)
        if not _bStopOK:
            vlogif._LogOEC(False, _EFwErrorCode.VUE_00028)

        if tskOpPreCheck_ is None:
            _oppc.CleanUp()

        if _bASynchronous:
            self.__mtxApi.Give()

        if _bStopOK:
            if _semSS is not None:
                _semSS.Take()

            if removeTask_:
                self.__RemoveFromTable(_tinst)
                self.__CleanUpTaskInstance(_tinst)

        return taskID_ if _bStopOK else None

    def __StopAllTasks(self, bCleanupStoppedTasks_ =True, lstSkipTaskIDs_= None, bSkipStartupThrd_=True) -> list:

        if self.__isTMgrInvalid:
            return None
        if (lstSkipTaskIDs_ is not None) and not isinstance(lstSkipTaskIDs_, list):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00290)
            return None

        res = []

        if (lstSkipTaskIDs_ is not None) and len(lstSkipTaskIDs_) == 0:
            lstSkipTaskIDs_ = None

        _lstRemoveTIDs, _lstStopTIDs = [], []

        with self.__mtxData:
            _tblSize = len(self.__tidtable)
            if _tblSize == 0:
                return None

            _lstSkip = None
            if lstSkipTaskIDs_ is not None:
                _lstSkip = [ _tid for _tid in lstSkipTaskIDs_ if _tid in self.__tidtable ]

            _numTaskToBeStopped = _tblSize if _lstSkip is None else (_tblSize-len(_lstSkip))

            for _kk in self.__tidtable.keys():
                _te = self.__tidtable[_kk]

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

        _numStopped = 0
        _numRemoved = 0

        if len(_lstStopTIDs) > 0:
            for _tid in _lstStopTIDs:
                _tid = self.__StopTaskByID(_tid, removeTask_=False)
                if _tid is not None:
                    _numStopped += 1
                    if bCleanupStoppedTasks_: _lstRemoveTIDs.append(_tid)

        if len(_lstRemoveTIDs) > 0:
            with self.__mtxApi:
                with self.__mtxData:
                    for _kk in _lstRemoveTIDs:
                        _te = self.__tidtable[_kk]
                        _ti = _te.teTaskInst
                        _ttn, _tn, _tid = type(_ti).__name__, _ti.taskName, _ti.taskID
                        self.__RemoveFromTable(_ti)
                        _numRemoved += 1

                        if _ti.taskBadge.isFwMain:
                            pass 
                        else:
                            if not self.__CleanUpTaskInstance(_ti, bIgnoreCeaseMode_=True):
                                res.append(_ti)

        _tblSizeLeft = len(self.__tidtable)
        if len(res) > 0:
            pass 
        else:
            res = None
        return res

    def __CleanUpTaskInstance(self, tskInst_ : _AbstractTask, bIgnoreCeaseMode_ =False):

        if not tskInst_.isValid:
            return self is not None
        if not tskInst_.eLcCeaseTLBState.isNone:
            if not bIgnoreCeaseMode_:
                return False

        if tskInst_.isStarted and not (tskInst_.isDone or tskInst_.isFailed):
            return False

        if tskInst_.isFwTask:
            linkedXtbl = tskInst_.linkedExecutable
            tskInst_.CleanUp()
            if linkedXtbl is not None:
                linkedXtbl.CleanUp()
        else:
            _xtc = tskInst_._xtaskConnector
            tskInst_.CleanUp()
            if _xtc is not None:
                _xtc.CleanUp()
        return True

    def __PrecheckExecutableRequest( self, tskID_ : int =None, aprofile_ : _AbstractProfile =None, enclPyThrd_ : _PyThread =None) -> bool:
        _bParamsOK = True
        _bParamsOK = _bParamsOK and (tskID_      is None or isinstance(tskID_, int))
        _bParamsOK = _bParamsOK and (aprofile_   is None or (isinstance(aprofile_, _AbstractProfile) and aprofile_.isValid and (aprofile_.isTaskProfile or aprofile_.isThreadProfile)))
        _bParamsOK = _bParamsOK and (enclPyThrd_ is None or isinstance(enclPyThrd_, _PyThread))
        if not _bParamsOK:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00291)
            return False

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
            _curPyThrd = _TaskUtil.GetCurPyThread()

            if id(enclPyThrd_) != id(_curPyThrd):
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00296)
                res = False

            else:
                _curTblE = self.__GetTableEntry(pythread_=_curPyThrd, bDoWarn_=False)

                if not ((_curTblE is None) or _curTblE.teIsAutoEnclosedEntry):
                    _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_TaskManager_TextID_004).format(_curPyThrd.name, _curTblE.teTaskInst.taskID, _curTblE.teTaskInst.taskName)

                    if not _curTblE.teIsXTaskEntry:
                        vlogif._LogOEC(True, _EFwErrorCode.VFE_00297)
                    else:
                        logif._LogErrorEC(_EFwErrorCode.UE_00095, _errMsg)
                    res = False
                else:
                    res = True

        return res

    def __PrecheckExecutableRequestByTaskID(self, tskID_: int) -> bool:
        res = False

        with self.__mtxApi:
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
                    _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_TaskManager_TextID_005).format(tskID_, str(_tinst))

                elif not _tinst.isInitialized:
                    _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_TaskManager_TextID_006).format(tskID_, str(_tinst))

                if _tinst.isEnclosingPyThread:
                    if _tinst.isEnclosingPyThread and not _TaskUtil.IsCurPyThread(_tinst.linkedPyThread):
                        _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_TaskManager_TextID_007).format(tskID_, _tinst.linkedPyThread.name, _TaskUtil.GetCurPyThread().name)

                    elif (_curTblE is not None) and (not _curTblE.teIsAutoEnclosedEntry) and id(_tinst) != id(_curTblE.teTaskInst):
                        _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_TaskManager_TextID_008).format(tskID_, _tinst.taskName, _curTblE.teTaskInst.taskID, _curTblE.teTaskInst.taskName)

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

    def __CreateStartProfiledTask(self, taskPrf_ : _TaskProfile, bStart_ : bool, tskOpPreCheck_ : _ATaskOperationPreCheck =None) -> _PyUnion[_FwTask, None]:
        if not (isinstance(taskPrf_, _TaskProfile) and taskPrf_.isValid):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00301)
            return None

        self.__mtxApi.Take()

        _autoEnclTE = None
        _curTblE = self.__GetCurTableEntry(bDoWarn_=False)
        if taskPrf_.isEnclosingPyThread:
            _autoEnclTE = _curTblE
            if _autoEnclTE is not None:
                if not _autoEnclTE.teIsAutoEnclosedEntry:
                    _autoEnclTE.CleanUp()
                    self.__mtxApi.Give()
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00302)
                    return None

        res = None
        try:
            if taskPrf_.isEnclosingPyThread:
                res = _FwTask._CreateEnclosingTask(taskPrf_=taskPrf_, bAutoStartEnclosedPyThread_=False)
            else:
                res = _FwTask._CreateTask(taskPrf_=taskPrf_)
        except _XcoExceptionRoot as xcp:
            if self.__CheckForReraiseXcoException(xcp):
                self.__mtxApi.Give()

                raise xcp

        except BaseException as xcp:
            _mySysXcp = _XcoBaseException(xcp, tb_=logif._GetFormattedTraceback())
            self.__HandleXcoBaseException(_mySysXcp, curTask_=None if _curTblE is None else _curTblE.teTaskInst)

        if res is None:
            if _autoEnclTE is not None:
                _autoEnclTE.CleanUp()
            self.__mtxApi.Give()
            return None

        if _autoEnclTE is not None:
            _autoEnclTaskInst = _autoEnclTE.teTaskInst
            if not self.__RemoveFromTable(_autoEnclTE.teTaskInst):
                _tid, _tname = res.taskID, res.taskName
                self.__mtxApi.Give()
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00303)
                _autoEnclTE.CleanUp()
                return None
            else:
                _autoEnclTaskInst.CleanUp()

        if not self.__AddToTable(res):
            res.CleanUp()
            self.__mtxApi.Give()
            return None

        if not res.isEnclosingPyThread:
            _bDoStart = bStart_
        else:
            _bDoStart = res.isAutoStartEnclosedPyThreadEnabled if bStart_ is None else bStart_

        if not _bDoStart:
            self.__mtxApi.Give()
        elif not self.__StartTaskInstance(res, tskOpPreCheck_, cleanupOnFailure_=True):
            res = None
        return res

    def __CheckCreateTaskRequest( self
                                , taskPrf_                    : _TaskProfile       =None
                                , runnable_                   : _AbstractRunnable  =None
                                , taskName_                   : str                =None
                                , resourcesMask_              : _ETaskResourceFlag =None
                                , delayedStartTimeSpanMS_     : int                =None
                                , enclosedPyThread_           : _PyThread          =None
                                , bAutoStartEnclosedPyThread_ : bool               =None
                                , args_                       : list               =None
                                , kwargs_                     : dict               =None
                                , taskProfileAttrs_           : dict               =None) -> _PyUnion[_TaskProfile, None]:
        res, _bValid, _enclPyThrd = taskPrf_, True, None

        with self.__mtxApi:
            if res is None:
                res = _TaskProfile( runnable_=runnable_
                                 , taskName_=taskName_
                                 , resourcesMask_=resourcesMask_
                                 , delayedStartTimeSpanMS_=delayedStartTimeSpanMS_
                                 , enclosedPyThread_=enclosedPyThread_
                                 , bAutoStartEnclosedPyThread_=bAutoStartEnclosedPyThread_
                                 , args_=args_
                                 , kwargs_=kwargs_
                                 , taskProfileAttrs_=taskProfileAttrs_ )

            if not isinstance(res, _TaskProfile):
                _bValid = False
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00304)
            elif not (res.isValid and res.runnable is not None):
                _bValid = False
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00305)
            else:
                _enclPyThrd = res.enclosedPyThread
                if (_enclPyThrd is not None) and not _enclPyThrd.is_alive():
                    _bValid = False
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00306)

            if not _bValid:
                pass
            elif _enclPyThrd is None:
                pass
            else:
                _te = self.__GetTableEntry(pythread_=_enclPyThrd, bDoWarn_=False)
                if _te is not None:
                    _bValid = False
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00307)
                elif not _TaskUtil.IsCurPyThread(_enclPyThrd):
                    _bValid = False
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00308)

            if not _bValid:
                if (res is not None) and taskPrf_ is None:
                    res.CleanUp()
        return res

    def __CreateStartThread( self
                           , thrdProfile_            : _ThreadProfile          =None
                           , xtConn_                 : _XTaskConnectorIF       =None
                           , taskName_               : str                     =None
                           , enclosedPyThread_       : _PyThread               =None
                           , bStart_                 : bool                    =None
                           , threadTargetCallableIF_ : _CallableIF             =None
                           , args_                   : list                    =None
                           , kwargs_                 : dict                    =None
                           , threadProfileAttrs_     : dict                    =None
                           , tskOpPreCheck_          : _ATaskOperationPreCheck =None) -> _PyUnion[_FwThread, None]:
        self.__mtxApi.Take()

        _autoEnclTE, _curTblE = None, self.__GetCurTableEntry(bDoWarn_=False)

        if thrdProfile_.isEnclosingPyThread:
            _autoEnclTE = _curTblE
            if _autoEnclTE is not None:
                if not _autoEnclTE.teIsAutoEnclosedEntry:
                    _autoEnclTE.CleanUp()
                    self.__mtxApi.Give()
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00309)
                    return None

        res = None
        try:
            res = _FwThread._CreateThread( thrdProfile_=thrdProfile_
                                         , xtaskConn_=xtConn_
                                         , taskName_=taskName_
                                         , enclosedPyThread_=enclosedPyThread_
                                         , bAutoStartEnclosedPyThread_=False
                                         , threadTargetCallableIF_=threadTargetCallableIF_
                                         , args_=args_
                                         , kwargs_=kwargs_
                                         , threadProfileAttrs_=threadProfileAttrs_)
        except _XcoExceptionRoot as xcp:
            if self.__CheckForReraiseXcoException(xcp):
                self.__mtxApi.Give()

                raise xcp

        except BaseException as xcp:
            _mySysXcp = _XcoBaseException(xcp, tb_=logif._GetFormattedTraceback())
            self.__HandleXcoBaseException(_mySysXcp, curTask_=None if _curTblE is None else _curTblE.teTaskInst)

        if res is None:
            if _autoEnclTE is not None:
                _autoEnclTE.CleanUp()
            self.__mtxApi.Give()
            return None

        if _autoEnclTE is not None:
            _autoEnclTaskInst = _autoEnclTE.teTaskInst
            if not self.__RemoveFromTable(_autoEnclTE.teTaskInst):
                _tid, _tname = res.taskID, res.taskName
                self.__mtxApi.Give()
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00310)
                return None
            else:
                _autoEnclTaskInst.CleanUp()

        if not self.__AddToTable(res):
            res.CleanUp()
            self.__mtxApi.Give()
            return None

        if not res.isEnclosingPyThread:
            _bDoStart = bStart_
        else:
            _bDoStart = res.isAutoStartEnclosedPyThreadEnabled if bStart_ is None else bStart_

        if not _bDoStart:
            self.__mtxApi.Give()
        else:
            if not self.__StartTaskInstance(res, tskOpPreCheck_, cleanupOnFailure_=True):
                res = None
        return res

    def __EncloseCurThread(self, bAutoEnclosed_ =False, bSkipTableEntryCheck_ =False) -> _FwThread:
        self.__mtxApi.Take()

        res     = None
        _curPyThrd = _TaskUtil.GetCurPyThread()
        _te     = None if bSkipTableEntryCheck_ else self.__GetTableEntry(pythread_=_curPyThrd)

        if _te is not None:
            if not isinstance(_te.teTaskInst, _FwThread):
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00311)
            else:
                res = _te.teTaskInst

            self.__mtxApi.Give()
            return res

        _mySysXcp = None
        try:
            res = _FwThread._CreateThread(enclosedPyThread_=_curPyThrd, bAutoEnclosedPyThrd_=bAutoEnclosed_, bAutoStartEnclosedPyThread_=False)
            if res is None:
                pass
            elif not self.__AddToTable(res):
                res.CleanUp()
                res = None

        except _XcoExceptionRoot as xcp:
            if self.__CheckForReraiseXcoException(xcp):
                raise xcp

        except BaseException as xcp:
            if _TaskManager._theTMgrImpl is None:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00312)
            else:
                _mySysXcp = _XcoBaseException(xcp, tb_=logif._GetFormattedTraceback())

        finally:
            self.__mtxApi.Give()

            if _mySysXcp is not None:
                self.__HandleXcoBaseException(_mySysXcp, bCausedByTMgr_=True)
        return res
