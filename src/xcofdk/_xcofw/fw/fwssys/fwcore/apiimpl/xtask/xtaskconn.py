# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xtaskconn.py
#
# Copyright(c) 2023-2024 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum import auto

from xcofdk._xcofw.fw.fwssys.fwcore.logging                    import logif
from xcofdk._xcofw.fw.fwssys.fwcore.logging                    import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.base.gtimeout              import _Timeout
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.sync.mutex             import _Mutex
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.ataskop            import _EATaskOperationID
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.ataskop            import _ATaskOperationPreCheck
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.execprofile        import _ExecutionProfile
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskbadge          import _TaskBadge
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskstate          import _TaskState
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil           import _PyThread
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.aexecutable        import _AbstractExecutable
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject              import _AbstractSlotsObject
from xcofdk._xcofw.fw.fwssys.fwcore.types.aprofile             import _AbstractProfile
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes          import _CommonDefines
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes          import unique
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes          import _FwIntEnum
from xcofdk._xcofw.fw.fwssys.fwcore.apiimpl                    import xlogifbase
from xcofdk._xcofw.fw.fwssys.fwcore.apiimpl.fwapiconnap        import _FwApiConnectorAP
from xcofdk._xcofw.fw.fwssys.fwcore.apiimpl.xtask.xtaskerrbase import _XTaskErrorBase
from xcofdk._xcofw.fw.fwssys.fwcore.apiimpl.xtask.xtaskprfext  import _XTaskProfileExt
from xcofdk._xcofw.fw.fwssys.fwcore.apiimpl.xtask.xtaskconnif  import _XTaskConnectorIF
from xcofdk._xcofw.fw.fwssys.fwmsg.apiimpl.xcomsgimpl          import _XMsgImpl
from xcofdk._xcofw.fw.fwssys.fwerrh.fwerrorcodes               import _EFwErrorCode

from xcofdk.fwapi.xtask import XTaskError
from xcofdk.fwapi.xtask import XTaskProfile

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine

@unique
class _EXTExecState(_FwIntEnum):
    eXTaskInitialized = _TaskState._EState.eInitialized.value
    eXTaskPendingRun  = auto()
    eXTaskRunning     = auto()
    eXTaskDone        = auto()
    eXTaskFailed      = auto()
    eXTaskStopping    = auto()
    eXTaskAborting    = auto()

    @property
    def isXtStarted(self):
        return self.value > _EXTExecState.eXTaskInitialized.value

    @property
    def isXtPendingRun(self):
        return self == _EXTExecState.eXTaskPendingRun

    @property
    def isXtRunning(self):
        return self == _EXTExecState.eXTaskRunning

    @property
    def isXtDone(self):
        return self == _EXTExecState.eXTaskDone

    @property
    def isXtFailed(self):
        return self == _EXTExecState.eXTaskFailed

    @property
    def isXtStopping(self):
        return self == _EXTExecState.eXTaskStopping

    @property
    def isXtAborting(self):
        return self == _EXTExecState.eXTaskAborting

    def _ToString(self, bDetached_ : bool):

        if self.value < _EXTExecState.eXTaskRunning.value:
            res = _EFwTextID.eXTaskConnector_EXUExecState_ToString_02.value
        elif self.isXtRunning:
            res = _EFwTextID.eXTaskConnector_EXUExecState_ToString_03.value
        elif self.isXtDone:
            res = _EFwTextID.eXTaskConnector_EXUExecState_ToString_04.value
        elif self.isXtFailed:
            res = _EFwTextID.eXTaskConnector_EXUExecState_ToString_05.value
        elif self.isXtStopping:
            res = _EFwTextID.eXTaskConnector_EXUExecState_ToString_06.value
        else:
            res = _EFwTextID.eXTaskConnector_EXUExecState_ToString_07.value

        res = _FwTDbEngine.GetText(_EFwTextID(res))
        if bDetached_:
            if not (self.isXtDone or self.isXtFailed):
                res += _FwTDbEngine.GetText(_EFwTextID.eXTaskConnector_EXUExecState_ToString_01)
        return res

class _XTaskMirror:
    __slots__ = [ '__xt' , '__xtSt' , '__xtPrf' , '__aname' , '__xtlType' , '__cn' , '__bSync' , '__tuid' ]

    def __init__(self, xtsk_ : _AbstractExecutable, xtPrf_ : XTaskProfile, eXtrlType_ : _AbstractExecutable._AbstractExecutableTypeID, aliasName_ : str):
        self.__cn    = None
        self.__xtSt  = None
        self.__tuid  = None
        self.__bSync = None

        self.__xt      = xtsk_
        self.__aname   = aliasName_
        self.__xtPrf   = xtPrf_
        self.__xtlType = eXtrlType_

    def __str__(self):
        return self.__ToString()

    @property
    def isStarted(self) -> bool:
        return False if self.__xtSt is None else self.__xtSt.isXtStarted

    @property
    def isDone(self) -> bool:
        return False if self.__xtSt is None else self.__xtSt.isXtDone

    @property
    def isFailed(self) -> bool:
        return False if self.__xtSt is None else self.__xtSt.isXtFailed

    @property
    def isStopping(self) -> bool:
        return False if self.__xtSt is None else self.__xtSt.isXtStopping

    @property
    def isAborting(self) -> bool:
        return False if self.__xtSt is None else self.__xtSt.isXtAborting

    @property
    def isConnected(self) -> bool:
        return False if self.__cn is None else self.__cn._isXTaskConnected

    @property
    def xtaskInst(self) -> _AbstractExecutable:
        return self.__xt

    @property
    def xtaskConnector(self):
        return self.__cn

    @property
    def aliasName(self) -> str:
        return self.__aname

    @property
    def xtaskName(self) -> str:
        if self.__tuid is None:
            res = self.aliasName
        else:
            res = _EFwTextID.eMisc_Sync if self.__bSync else _EFwTextID.eMisc_Async
            res = _FwTDbEngine.GetText(res).capitalize()[0]
            res += f'{_FwTDbEngine.GetText(_EFwTextID.eMisc_TaskNamePrefix_XTaskTask)}{self.__tuid}'
        return res

    @property
    def xtaskUniqueID(self) -> int:
        return self.__tuid

    @property
    def xtaskProfile(self) -> XTaskProfile:
        return self.__xtPrf

    @property
    def _xtTypeID(self) -> _AbstractExecutable._AbstractExecutableTypeID:
        return self.__xtlType

    @property
    def _xtState(self) -> _EXTExecState:
        return self.__xtSt

    @property
    def _xtStateToString(self) -> str:
        return self.__MapXtStateToString()

    def _InitUpdate(self, connector_, bSynchronousTask_ : bool):
        self.__cn    = connector_
        self.__bSync = bSynchronousTask_

    def _TaskIDUpdate(self, tuid_ : int):
        self.__tuid = tuid_

    def _TaskStateUpdate(self, xuState_ : _EXTExecState, bDetach_ =False):
        self.__xtSt = xuState_
        if bDetach_:
            self.__cn = None

    def __ToString(self):
        res = _FwTDbEngine.GetText(_EFwTextID.eXTaskConnector_XTaskMirror_ToString_01)
        res = res.format(self.xtaskName, self.__MapXtStateToString())
        return res

    def __MapXtStateToString(self) -> str:
        if not self.isConnected:
            res = str(None) if self.__xtSt is None else self.__xtSt._ToString(True)
        else:
            res = self.__cn._xtStateToString
        return res

class _XTaskConnector(_XTaskConnectorIF):

    class __XConnData(_AbstractSlotsObject):
        __slots__ = [ '__mtxApi' , '__tskState' , '__xtState' , '__tskPrf' , '__linkedPyThrd' , '__tid' , '__tname' , '__bXtTsk' ]

        def __init__( self, mtxApi_ : _Mutex):
            super().__init__()
            self.__tid          = None
            self.__tname        = None
            self.__bXtTsk       = None
            self.__mtxApi       = None
            self.__tskPrf       = None
            self.__xtState      = None
            self.__tskState     = None
            self.__linkedPyThrd = None

            if not isinstance(mtxApi_, _Mutex):
                self.CleanUp()
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00007)
            else:
                self.__mtxApi = mtxApi_

        @property
        def isXTaskTask(self):
            return self.__bXtTsk

        @property
        def taskID(self) -> int:
            return self.__tid

        @property
        def taskName(self) -> str:
            return self.__tname

        @property
        def xtaskState(self) -> _EXTExecState:
            return self.__xtState

        @property
        def taskProfile(self) -> _AbstractProfile:
            if self.__isInvalid:
                return None
            with self.__mtxApi:
                return self.__tskPrf

        @property
        def linkedPyThread(self) -> _PyThread:
            if self.__isInvalid:
                return None
            with self.__mtxApi:
                return self.__linkedPyThrd

        @property
        def _taskState(self) -> _TaskState:
            if self.__isInvalid:
                return None
            with self.__mtxApi:
                return self.__tskState

        def _SetData(self, tskBadge_ : _TaskBadge, tskProfile_ : _AbstractProfile, linkedPyThrd_ : _PyThread):
            if self.__isInvalid:
                return
            if not (isinstance(tskBadge_, _TaskBadge) and tskBadge_.isValid):
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00007)
                return
            if not isinstance(linkedPyThrd_, _PyThread):
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00008)
                return
            if not (isinstance(tskProfile_, _AbstractProfile) and tskProfile_.isValid and tskProfile_.isFrozen):
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00009)
                return
            if not tskProfile_.isDrivingXTaskTaskProfile:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00010)
                return
            if self.__tskPrf is not None:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00011)
                return

            with self.__mtxApi:
                self.__tid          = tskBadge_.taskID
                self.__tname        = tskBadge_.taskName
                self.__bXtTsk       = tskBadge_.isXTaskTask
                self.__tskPrf       = tskProfile_
                self.__linkedPyThrd = linkedPyThrd_

        def _UpdateState(self, tskState_ : _TaskState):
            if self.__isInvalid:
                return False
            elif self.__tskPrf is None:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00012)
                return False
            elif not isinstance(tskState_, _TaskState):
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00013)
                return False
            with self.__mtxApi:
                self.__tskState = tskState_
                self.__xtState = self._TaskState2XUExecState()
                return True

        def _TaskState2XUExecState(self) -> _EXTExecState:
            if self.__isInvalid:
                return None

            res       = _EXTExecState.eXTaskInitialized
            _curTskSt = None if self.__tskState is None else self.__tskState.GetStateID()

            if _curTskSt is not None:
                _curTskStVal = _curTskSt.value
                if _curTskStVal >= _TaskState._EState.eRunProgressAborted.value:
                    _curTskStVal = _EXTExecState.eXTaskAborting.value
                elif _curTskStVal >= _TaskState._EState.ePendingStopRequest.value:
                    _curTskStVal = _EXTExecState.eXTaskStopping.value
                elif _curTskStVal >= _TaskState._EState.eFailed.value:
                    _curTskStVal = _EXTExecState.eXTaskFailed.value
                res = _EXTExecState(_curTskStVal)
            return res

        def _ToString(self, *args_, **kwargs_):
            pass

        def _CleanUp(self):
            if self.__isInvalid:
                return

            if self.__tskPrf is not None:
                self.__tskPrf.CleanUp()
            self.__tid          = None
            self.__tname        = None
            self.__mtxApi       = None
            self.__bXtTsk       = None
            self.__tskPrf       = None
            self.__xtState      = None
            self.__tskState     = None
            self.__linkedPyThrd = None

        @property
        def __isInvalid(self):
            return self.__mtxApi is None

    __slots__ = [ '__xtm' , '__xdata' , '__mtxApi' , '__mtxData' , '__xtPrf' , '__execPrf' , '__euNum' ]
    __prfCreator = None

    def __init__(self, xtm_ : _XTaskMirror, xtPrf_ : _XTaskProfileExt):
        self.__xtm     = None
        self.__euNum   = None
        self.__xdata   = None
        self.__mtxApi  = None
        self.__xtPrf   = None
        self.__mtxData = None
        self.__execPrf = None

        super().__init__()

        if not isinstance(xtm_, _XTaskMirror):
            self.CleanUp()
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00014)
        elif not isinstance(xtm_.xtaskInst, _AbstractExecutable):
            self.CleanUp()
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00015)
        elif not xtm_.xtaskInst.isXtask:
            self.CleanUp()
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00016)
        elif not (isinstance(xtPrf_, _XTaskProfileExt) and xtPrf_.isValid):
            self.CleanUp()
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00017)
        else:
            _xp = _ExecutionProfile(xtaskProfileExt_=xtPrf_)
            if not _xp.isValid:
                self.CleanUp()
            else:
                xtPrf_._Freeze()
                xtm_._InitUpdate(self, xtPrf_.isSynchronousTask)

                self.__xtm     = xtm_
                self.__xtPrf   = xtPrf_
                self.__mtxApi  = _Mutex()
                self.__mtxData = _Mutex()
                self.__execPrf = _xp

    @property
    def xtaskProfile(self) -> _XTaskProfileExt:
        return self.__xtPrf

    @property
    def _isStarted(self) -> bool:
        if self.__isFwTaskDisconnected:
            return False
        with self.__mtxData:
            _xtSt = self.__xdata.xtaskState
            return False if _xtSt is None else _xtSt.isXtStarted

    @property
    def _isPendingRun(self) -> bool:
        if self.__isFwTaskDisconnected:
            return False
        with self.__mtxData:
            _xtSt = self.__xdata.xtaskState
            return False if _xtSt is None else _xtSt.isXtPendingRun

    @property
    def _isRunning(self) -> bool:
        if self.__isFwTaskDisconnected:
            return False
        with self.__mtxData:
            _xtSt = self.__xdata.xtaskState
            return False if _xtSt is None else _xtSt.isXtRunning

    @property
    def _isDone(self) -> bool:
        if self.__isFwTaskDisconnected:
            return False
        with self.__mtxData:
            _xtSt = self.__xdata.xtaskState
            return False if _xtSt is None else _xtSt.isXtDone

    @property
    def _isXTaskConnected(self) -> bool:
        return self.__isXtConnected

    @property
    def _connectedXTask(self) -> _AbstractExecutable:
        if self.__isInvalid:
            return None
        if self.__isXtDisconnected:
            return None
        return self.__xtm.xtaskInst

    @property
    def taskUniqueName(self) -> str:
        return None if self.__isFwTaskDisconnected else self.__xdata.taskName

    @property
    def executionProfile(self) -> _ExecutionProfile:
        return self.__execPrf

    @property
    def _isMainXTaskConnector(self) -> bool:
        return self.__isXtConnected and self.__xtPrf.isMainTask

    @property
    def _isFailed(self) -> bool:
        if self.__isFwTaskDisconnected:
            return False
        with self.__mtxData:
            _xtSt = self.__xdata.xtaskState
            return False if _xtSt is None else _xtSt.isXtFailed

    @property
    def _isStopping(self) -> bool:
        if self.__isFwTaskDisconnected:
            return False
        with self.__mtxData:
            _xtSt = self.__xdata.xtaskState
            return False if _xtSt is None else _xtSt.isXtStopping

    @property
    def _isAborting(self) -> bool:
        if self.__isFwTaskDisconnected:
            return False
        with self.__mtxData:
            _xtSt = self.__xdata.xtaskState
            return False if _xtSt is None else _xtSt.isXtAborting

    @property
    def _currentError(self) -> XTaskError:
        return self.__GetCurrentError()

    @property
    def _euRNumber(self) -> int:
        if self.__euNum is None:
            return -1
        return self.__euNum

    @property
    def _xtStateToString(self) -> str:
        if self.__isInvalid:
            return None
        with self.__mtxData:
            _xtSt = None if self.__isFwTaskDisconnected else self.__xdata.xtaskState
            return None if _xtSt is None else _xtSt._ToString(self.__xtm is None)

    def _StartXTask(self, *args_, **kwargs_) -> bool:
        if self.__isInvalid:
            return False
        if self.__isXtDisconnected:
            return False

        _midPart = self.__GetFormattedXTaskLabel()

        if self.__isFwUnavailable:
            logif._XLogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskConnector_TextID_001).format(_midPart))
            return False

        elif self.__isFwTaskConnected and self._isStarted:
            logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskConnector_TextID_004).format(_midPart.capitalize()))
            return False

        elif self.__isLcProxyUnavailable:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00018)
            return False

        elif not self._PcIsLcProxyModeNormal():
            logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskConnector_TextID_003).format(_midPart))
            return False

        elif not self._PcIsTaskMgrApiAvailable():
            logif._XLogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskConnector_TextID_001).format(_midPart))
            return False

        self.__execPrf._SetStartArgs(*args_, **kwargs_)

        _bSyncTask = self.__xtPrf.isSynchronousTask
        if not _bSyncTask:
            self.__mtxApi.Take()

        if _bSyncTask:
            _midPart2 = _FwTDbEngine.GetText(_EFwTextID.eMisc_TaskType_Sync)
            res = self._PcGetTaskMgr().StartXTask(self)
        else:
            res = self._PcGetTaskMgr().StartXTask(self)
            if res:
                _midPart2 = _FwTDbEngine.GetText(_EFwTextID.eMisc_TaskType_Async)
            self.__mtxApi.Give()

        _bErrorFree = self._currentError is None

        if self.__isInvalid:
            logif._LogErrorEC(_EFwErrorCode.UE_00010, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskConnector_TextID_008).format(_midPart))
        elif not res:
            if _bErrorFree:
                logif._LogErrorEC(_EFwErrorCode.UE_00011, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskConnector_TextID_008).format(_midPart))
        elif self._isFailed:
            res = False
            if _bErrorFree:
                logif._LogErrorEC(_EFwErrorCode.UE_00012, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskConnector_TextID_009).format(_midPart))
        return res

    def _StopXTask(self, cleanupDriver_ =True) -> bool:

        if self.__isInvalid:
            return False
        if self.__isXtDisconnected:
            return False

        _midPart = self.__GetFormattedXTaskLabel()

        if self.__isFwUnavailable:
            logif._XLogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskConnector_TextID_016).format(_midPart))
            return False

        elif self.__isFwTaskDisconnected:
            logif._LogErrorEC(_EFwErrorCode.UE_00013, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskConnector_TextID_019).format(_midPart))
            return False

        elif self.__isLcProxyUnavailable:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00020)
            return False

        elif not self._PcIsLcProxyModeNormal():
            logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskConnector_TextID_018).format(_midPart))
            return False

        elif not self._PcIsTaskMgrApiAvailable():
            logif._XLogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskConnector_TextID_016).format(_midPart))
            return False

        self.__mtxApi.Take()
        _oppc = self.__PreCheckTaskOperation(_EATaskOperationID.eStop)
        if _oppc.isNotApplicable or _oppc.isIgnorable:
            self.__mtxApi.Give()
            res = _oppc.isIgnorable
        else:
            if _oppc.isSynchronous:
                self.__mtxApi.Give()
            res = self._PcGetTaskMgr().StopXTask(self, cleanupDriver_=cleanupDriver_)

            if not self.__isInvalid: self.__mtxApi.Give()
        _oppc.CleanUp()
        return res

    def _JoinXTask(self, timeout_ : [int, float] =None) -> bool:

        if self.__isInvalid:
            return False
        if self.__isXtDisconnected:
            return False

        _midPart = self.__GetFormattedXTaskLabel()

        if self.__isFwUnavailable:
            logif._XLogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskConnector_TextID_021).format(_midPart))
            return False

        elif self.__isFwTaskDisconnected:
            logif._LogErrorEC(_EFwErrorCode.UE_00014, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskConnector_TextID_007).format(_midPart))
            return False

        elif self.__isLcProxyUnavailable:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00021)
            return False

        elif not self._PcIsLcProxyModeNormal():
            logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskConnector_TextID_022).format(_midPart))
            return False

        elif not self._PcIsTaskMgrApiAvailable():
            logif._XLogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskConnector_TextID_021).format(_midPart))
            return False

        elif self._PcIsLcMonShutdownEnabled():
            logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskConnector_TextID_023).format(_midPart))
            return False

        _tout = timeout_
        if timeout_ is not None:
            if not isinstance(timeout_, (int, float)):
                if not isinstance(timeout_, _Timeout):
                    logif._LogErrorEC(_EFwErrorCode.UE_00015, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskConnector_TextID_002).format(type(timeout_).__name__, _midPart))
                    return False
            elif (isinstance(timeout_, int) and timeout_ < 0) or (isinstance(timeout_, float) and timeout_ < 0.0):
                logif._LogErrorEC(_EFwErrorCode.UE_00016, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskConnector_TextID_012).format(str(timeout_), _midPart))
                return False

            if not isinstance(timeout_, _Timeout):
                if isinstance(timeout_, int):
                    _tout = _Timeout.CreateTimeoutMS(timeout_)
                else:
                    _tout = _Timeout.CreateTimeoutSec(timeout_)

        self.__mtxApi.Take()
        _oppc = self.__PreCheckTaskOperation(_EATaskOperationID.eJoin)
        if _oppc.isNotApplicable or _oppc.isIgnorable:
            self.__mtxApi.Give()
            res = _oppc.isIgnorable
        else:
            if _oppc.isSynchronous:
                self.__mtxApi.Give()
            res = self._PcGetTaskMgr().JoinXTask(self, timeout_=_tout)

            if not self.__isInvalid: self.__mtxApi.Give()
        _oppc.CleanUp()

        if _tout is not None:
            if isinstance(timeout_, _Timeout):
                _tout.CleanUp()
        return res

    def _DisconnectXTask(self, bDetachApiRequest_ =False):
        if self.__isInvalid:
            return
        with self.__mtxData:
            if self.__xtm is not None:
                if self.__isFwTaskDisconnected or not self._PcIsLcProxyModeNormal():
                    _xtSt = self.__xtm._xtState
                else:
                    if self._isRunning:
                        if bDetachApiRequest_:
                            if self._PcIsTaskMgrApiAvailable():
                                _bDoTryStop = False
                                _oppc       = self.__PreCheckTaskOperation(_EATaskOperationID.eStop)

                                if not (_oppc.isNotApplicable or _oppc.isIgnorable):
                                    _bDoTryStop = True
                                _oppc.CleanUp()
                                if _bDoTryStop:
                                    self._PcGetTaskMgr().StopXTask(self, cleanupDriver_=False)

                    _xtSt = self.__xdata.xtaskState

                if _xtSt is not None:
                    self.__DisconnectXTaskMirror(_xtSt, bDetachApiRequest_=bDetachApiRequest_)

    def _ClearCurrentError(self) -> bool:

        res = False
        if self.__isXtDisconnected:
            pass
        elif self.__isFwUnavailable:
            pass
        elif self.__isLcProxyUnavailable:
            pass
        elif not self._PcIsLcProxyModeNormal():
            pass
        elif not self._PcIsTaskMgrApiAvailable():
            pass
        elif not self._PcGetTaskMgr().IsCurTask(self.__xtaskUniqueID):
            logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskConnector_TextID_029).format(self.__xtaskUniqueID))
        else:
            _tskErr      = self._PcGetTaskMgr().GetTaskError(self.__xtaskUniqueID)
            _myLogPrefix = self.__logPrefix

            if _tskErr is None:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00022)
            elif _tskErr.taskBadge is None:
                pass
            elif not _tskErr.taskBadge.isDrivingXTask:
                pass
            else:
                _errUID = _tskErr.currentErrorUniqueID
                if _errUID is not None:
                    _bNoImpactFatalErrorDueToFrcLinkage = _tskErr.isNoImpactFatalErrorDueToFrcLinkage

                    res = _tskErr.ClearError() and _tskErr.isErrorFree

                    if not res:
                        vlogif._LogOEC(True, _EFwErrorCode.VFE_00023)
                else:
                    res = True
        return res

    def _SetTaskError(self, bFatal_ : bool, errMsg_: str, errCode_: int =None):

        if self.__isXtDisconnected:
            pass
        elif self.__isFwUnavailable:
            pass
        elif self.__isLcProxyUnavailable:
            pass
        elif not self._PcIsLcProxyModeNormal():
            pass
        elif not self._PcIsTaskMgrApiAvailable():
            pass
        elif not self._PcGetTaskMgr().IsCurTask(self.__xtaskUniqueID):
            _msgID = _EFwTextID.eLogMsg_XTaskConnector_TextID_033 if bFatal_ else _EFwTextID.eLogMsg_XTaskConnector_TextID_032
            logif._LogWarning(_FwTDbEngine.GetText(_msgID).format(self.__xtaskUniqueID))
        elif errCode_ is None:
            if bFatal_:
                xlogifbase._XSetFatalError(errMsg_)
            else:
                xlogifbase._XSetError(errMsg_)
        elif bFatal_:
            xlogifbase._XSetFatalErrorEC(errMsg_, errCode_)
        else:
            xlogifbase._XSetErrorEC(errMsg_, errCode_)

    def _SendXMsg(self, xmsg_: _XMsgImpl) -> bool:

        if self.__isXtDisconnected:
            return False
        if not self._PcIsLcProxyModeNormal():
            return False

        _midPart = self.__GetFormattedXTaskLabel()

        if self.__isFwTaskDisconnected:
            logif._XLogErrorEC(_EFwErrorCode.UE_00178, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskConnector_TextID_030).format(_midPart))
            return False

        _xrbl = None
        with self.__mtxData:
            _xdata = self.__xdata
            if _xdata is None:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00024)
                return False
            if not _xdata.isXTaskTask:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00025)
                return False
            if (_xdata.taskProfile is None) or (_xdata.taskProfile.runnable is None):
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00026)
                return False
            if (_xdata.xtaskState is None) or _xdata.xtaskState.isXtAborting:
                return False
            _xrbl = _xdata.taskProfile.runnable

        return _xrbl._SendMessage(xmsg_)

    def _TriggerQueueProcessing(self, bExtQueue_ : bool) -> int:

        if self.__isXtDisconnected:
            return False
        if not self._PcIsLcProxyModeNormal():
            return False

        _midPart = self.__GetFormattedXTaskLabel()

        if self.__isFwTaskDisconnected:
            logif._XLogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskConnector_TextID_031).format(_midPart))
            return -1

        _xrbl = None
        with self.__mtxData:
            _xdata = self.__xdata
            if not _xdata.isXTaskTask:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00027)
                return -1
            if (_xdata.taskProfile is None) or (_xdata.taskProfile.runnable is None):
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00028)
                return -1
            if (_xdata.xtaskState is None) or not (_xdata.xtaskState.isXtRunning or _xdata.xtaskState.isXtStopping):
                return -1
            _xrbl = _xdata.taskProfile.runnable

        return _xrbl._TriggerQueueProc(bExtQueue_)

    def _CPrf(self, enclosedPyThread_ : _PyThread =None, profileAttrs_ : dict =None):
        _prfc = _XTaskConnector.__prfCreator
        if _prfc is None:
            res = None
        else:
            res = _prfc._CreateXTaskProfile(self, enclosedPyThread_=enclosedPyThread_, profileAttrs_=profileAttrs_)
        return res

    def _UpdateXD( self, tskState_ : _TaskState, tskBadge_ : _TaskBadge =None, tskProfile_ : _AbstractProfile =None, linkedPyThrd_ : _PyThread =None):
        if self.__isInvalid or self.__isFwUnavailable:
            return False
        if (tskBadge_ is not None) and not (isinstance(tskBadge_, _TaskBadge) and tskBadge_.isValid):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00029)
            return False
        if not (isinstance(tskState_, _TaskState) and tskState_.isValid):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00030)
            return False

        with self.__mtxData:
            if self.__isFwTaskDisconnected:
                self.__xdata = _XTaskConnector.__XConnData(mtxApi_=self.__mtxData)

            if self.__xdata.taskProfile is None:
                if (tskBadge_ is None) or (tskProfile_ is None) or (linkedPyThrd_ is None):
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00031)
                    return False
                self.__xdata._SetData(tskBadge_, tskProfile_, linkedPyThrd_)
                if self.__xdata.taskProfile is None:
                    return False

                self.__euNum = -1
                if self.__isXtConnected:
                    self.__xtm._TaskIDUpdate(tskBadge_.taskID)

            elif (tskBadge_ is not None) or (tskProfile_ is not None) or (linkedPyThrd_ is not None):
                _bNOK = False
                _bNOK = _bNOK or ((tskProfile_ is not None)   and id(tskProfile_)   != id(self.__xdata.taskProfile))
                _bNOK = _bNOK or ((linkedPyThrd_ is not None) and id(linkedPyThrd_) != id(self.__xdata.linkedPyThread))
                if _bNOK:
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00032)
                    return False

            _xtSt         = self.__xdata.xtaskState
            _bWasXuFailed = False if _xtSt is None else _xtSt.isXtFailed or _xtSt.isXtAborting

            res = self.__xdata._UpdateState(tskState_)
            if not res:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00033)
            elif self.__xtm is None:
                if not tskState_.isTerminated:
                    res = res
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00034)
            else:
                _xtSt        = self.__xdata.xtaskState
                _bAborting   = tskState_.isAborting
                _bTerminated = tskState_.isTerminated

                if _bTerminated or _bAborting:
                    if _bAborting or tskState_.isFailed:
                        if not _bWasXuFailed:
                            logif._LogInfo(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskConnector_TextID_024).format(self.__GetFormattedXTaskLabel().capitalize()))

                if _bTerminated:
                    self.__DisconnectXTaskMirror(_xtSt, bDetachApiRequest_=None)
                else:
                    self.__xtm._TaskStateUpdate(_xtSt)
            return res

    def _IncEuRNumber(self):
        if self.__euNum is None:
            return
        self.__euNum += 1

    def _ToString(self, *args_, **kwargs_):
        if self.__isInvalid:
            return type(self).__name__

        res = self.__logPrefix
        if self._connectedXTask is None:
            res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_008).format(type(self).__name__)
        else:
            res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_008).format(self._connectedXTask)
        return res

    def _CleanUp(self):
        if self.__isInvalid:
            return

        _xucName = self.__logPrefix

        self._DisconnectXTask()

        super()._CleanUp()
        if self.__xdata is not None:
            self.__xdata.CleanUp()
        self.__mtxData.CleanUp()
        self.__mtxApi.CleanUp()
        self.__execPrf.CleanUp()

        self.__euNum   = None
        self.__xdata   = None
        self.__xtPrf   = None
        self.__mtxApi  = None
        self.__mtxData = None
        self.__execPrf = None

    @staticmethod
    def _SetPRFC(ak_, prfc_):

        ak = hash(str(_XTaskConnector._SetPRFC))
        res = ak_ == ak
        if not res:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00035)
        else:
            if (prfc_ is not None) and (_XTaskConnector.__prfCreator is not None):
                pass
            elif (prfc_ is None) and (_XTaskConnector.__prfCreator is None):
                pass
            else:
                _XTaskConnector.__prfCreator = prfc_
        return res

    @property
    def __isInvalid(self):
        return self.__mtxData is None

    @property
    def __isXtConnected(self):
        if self.__isInvalid:
            return False
        with self.__mtxData:
            return self.__xtm is not None

    @property
    def __isXtDisconnected(self):
        if self.__isInvalid:
            return False
        with self.__mtxData:
            return self.__xtm is None

    @property
    def __isFwAvailable(self):
        return _FwApiConnectorAP._APIsFwApiConnected()

    @property
    def __isFwUnavailable(self):
        return not self.__isFwAvailable

    @property
    def __isLcProxyUnavailable(self):
        if not self._PcIsLcProxySet():
            _prfc = _XTaskConnector.__prfCreator
            if _prfc is not None:
                _pxy = _prfc._GetLcProxy()
                if (_pxy is not None) and _pxy._PxyIsLcProxyModeNormal():
                    self._PcSetLcProxy(_pxy)
        res = self._PcIsLcProxyModeShutdown()
        return res

    @property
    def __isFwTaskConnected(self) -> bool:
        return self.__xdata is not None

    @property
    def __isFwTaskDisconnected(self) -> bool:
        return self.__xdata is None

    @property
    def __xtaskName(self):
        if self.__isInvalid:
            res = _CommonDefines._STR_EMPTY
        elif self.__isXtConnected:
            res = self.__xtm.xtaskName
        elif self.__isFwTaskDisconnected:
            res = _CommonDefines._STR_EMPTY
        else:
            res = self.__xdata.taskName
        return res

    @property
    def __xtaskUniqueID(self):
        if self.__isInvalid:
            res = None
        elif self.__isXtConnected:
            res = self.__xtm.xtaskUniqueID
        elif self.__isFwTaskDisconnected:
            res = None
        else:
            res = self.__xdata.taskID
        return res

    @property
    def __logPrefixStateUpdate(self):
        res     = _FwTDbEngine.GetText(_EFwTextID.eXTaskConnector_LogPrefix) + _FwTDbEngine.GetText(_EFwTextID.eXTaskConnector_LogPrefix_StateUpdate)
        _xtname = self.__xtaskName
        if (_xtname is not None) and (len(_xtname) > 0):
            res += f'[{_xtname}] '
        return res

    @property
    def __logPrefix(self):
        res     = _FwTDbEngine.GetText(_EFwTextID.eXTaskConnector_LogPrefix)
        _xtname = self.__xtaskName
        if (_xtname is not None) and (len(_xtname) > 0):
            res += f'[{_xtname}] '
        return res

    def __GetFormattedXTaskLabel(self) -> str:
        if self.__isInvalid:
            return _CommonDefines._STR_EMPTY

        res  = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_007).format(_FwTDbEngine.GetText(_EFwTextID.eMisc_Main)) if self._isMainXTaskConnector else _CommonDefines._STR_EMPTY
        res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_001).format(_FwTDbEngine.GetText(_EFwTextID.eMisc_XTask), self.__xtaskName)
        return res

    def __GetCurrentError(self) -> XTaskError:
        if self.__isXtDisconnected:
            return None
        if self.__isFwUnavailable:
            return None
        if self.__isLcProxyUnavailable:
            return None
        if not self._PcIsTaskMgrApiAvailable():
            return None

        res          = None
        _tskErr      = self._PcGetTaskMgr().GetTaskError(self.__xtaskUniqueID)
        _myLogPrefix = self.__logPrefix

        if _tskErr is None:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00036)
        elif _tskErr.taskBadge.isDrivingXTask:
            _curEE = _tskErr._currentErrorEntry
            if _curEE is not None:
                _bFatal = _curEE.isFatalError or _curEE.hasNoImpactDueToFrcLinkage
                _tmp  = _XTaskErrorBase(_curEE.uniqueID, _bFatal, _bFatal and logif._IsFwDieModeEnabled(), _curEE.shortMessage, errCode_=None if _curEE.isAnonymousError else _curEE.errorCode)

                res = XTaskError(xtaskError_=_tmp)
        return res

    def __DisconnectXTaskMirror(self, xtDetachState_ : _EXTExecState, bDetachApiRequest_ =False):

        if self.__isInvalid:
            return
        if self.__xtm is None:
            return
        if not isinstance(xtDetachState_, _EXTExecState):
            return

        self.__xtm._TaskStateUpdate(xtDetachState_, bDetach_=True)

        self.__xtm = None

    def __PreCheckTaskOperation(self, eTaskOpID_ : _EATaskOperationID) -> _ATaskOperationPreCheck:

        return _ATaskOperationPreCheck( eTaskOpID_, self.__xdata._taskState
                                      , self.__xdata.linkedPyThread, self.__xtPrf.isSynchronousTask, reportErr_=True)
