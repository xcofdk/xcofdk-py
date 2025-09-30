# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : usertaskconn.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from typing import Union

from xcofdk.fwapi                import ITaskError
from xcofdk.fwapi.xmt.xtaskerror import XTaskError

from _fw.fwssys.assys.ifs                import _IUTaskConn
from _fw.fwssys.assys.ifs.ifutagent      import _IUTAgent
from _fw.fwssys.fwcore.logging           import logif
from _fw.fwssys.fwcore.logging           import vlogif
from _fw.fwssys.fwcore.base.gtimeout     import _Timeout
from _fw.fwssys.fwcore.ipc.sync.mutex    import _Mutex
from _fw.fwssys.fwcore.ipc.tsk.ataskop   import _EATaskOpID
from _fw.fwssys.fwcore.ipc.tsk.ataskop   import _ATaskOpPreCheck
from _fw.fwssys.fwcore.ipc.tsk.afwtask   import _AbsFwTask
from _fw.fwssys.fwcore.ipc.tsk.taskbadge import _TaskBadge
from _fw.fwssys.fwcore.ipc.tsk.taskdefs  import _ETaskSelfCheckResultID
from _fw.fwssys.fwcore.ipc.tsk.taskstate import _TaskState
from _fw.fwssys.fwcore.ipc.tsk.taskutil  import _PyThread
from _fw.fwssys.fwcore.ipc.tsk.taskxcard import _TaskXCard
from _fw.fwssys.fwcore.lc.lcproxyclient  import _LcProxyClient
from _fw.fwssys.fwcore.types.aobject     import _AbsSlotsObject
from _fw.fwssys.fwcore.types.afwprofile  import _AbsFwProfile
from _fw.fwssys.fwcore.types.commontypes import override
from _fw.fwssys.fwcore.types.commontypes import _CommonDefines
from _fw.fwssys.fwcore.types.commontypes import _EDepInjCmd
from _fw.fwssys.fwmt.xtaskprfext         import _XTaskPrfExt
from _fw.fwssys.fwctrl.fwapiconnap       import _FwApiConnectorAP
from _fw.fwssys.fwmsg.apiimpl.xmsgimpl   import _XMsgImpl
from _fw.fwssys.fwmt.api                 import xlogifbase
from _fw.fwssys.fwmt.api.xtaskerrimpl    import _XTaskErrorImpl
from _fw.fwssys.fwmt.utask.usertaskdefs  import _EUTaskXState
from _fw.fwssys.fwmt.utask.usertaskdefs  import _UTaskMirror
from _fw.fwssys.fwerrh.fwerrorcodes      import _EFwErrorCode
from _fwa.fwsubsyscoding                 import _FwSubsysCoding

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _UserTaskConn(_LcProxyClient, _IUTaskConn):
    class __UTConnData(_AbsSlotsObject):
        __slots__ = [ '__ma' , '__st' , '__xst' , '__tp' , '__tid' , '__tn' , '__bM' , '__sndOp' , '__dht' ]

        def __init__( self, ma_ : _Mutex):
            super().__init__()
            self.__bM    = None
            self.__ma    = None
            self.__st    = None
            self.__tn    = None
            self.__tp    = None
            self.__dht   = None
            self.__tid   = None
            self.__xst   = None
            self.__sndOp = None

            if not isinstance(ma_, _Mutex):
                self.CleanUp()
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00007)
            else:
                self.__ma = ma_

        @property
        def isMsgXTask(self):
            return self.__bM

        @property
        def dtaskUID(self) -> int:
            return self.__tid

        @property
        def dtaskName(self) -> str:
            return self.__tn

        @property
        def utaskXState(self) -> _EUTaskXState:
            return self.__xst

        @property
        def dtaskPyThread(self) -> _PyThread:
            if self.__isInvalid:
                return None
            with self.__ma:
                return self.__dht

        @property
        def _dtaskState(self) -> _TaskState:
            if self.__isInvalid:
                return None
            with self.__ma:
                return self.__st

        @property
        def _msgOperator(self):
            return None if self.__isInvalid else self.__sndOp

        def _SetData(self, tskBadge_ : _TaskBadge, fwtPrf_ : _AbsFwProfile, dhThrd_ : _PyThread, sndOperator_):
            if self.__isInvalid:
                return
            if self.__tid is not None:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00947)
                return
            if not (isinstance(tskBadge_, _TaskBadge) and tskBadge_.isValid):
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00007)
                return
            if not isinstance(dhThrd_, _PyThread):
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00008)
                return
            if not (isinstance(fwtPrf_, _AbsFwProfile) and fwtPrf_.isValid and fwtPrf_.isFrozen):
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00009)
                return
            if not fwtPrf_.isDrivingXTaskTaskProfile:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00010)
                return
            if sndOperator_ is None:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00946)
                return

            with self.__ma:
                self.__bM    = tskBadge_.isXTaskTask
                self.__tn    = tskBadge_.dtaskName
                self.__tp    = fwtPrf_
                self.__dht   = dhThrd_
                self.__sndOp = sndOperator_
                self.__tid   = tskBadge_.dtaskUID

        def _UpdateState(self, tskState_ : _TaskState):
            if self.__isInvalid:
                return False
            elif self.__tid is None:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00012)
                return False
            elif not isinstance(tskState_, _TaskState):
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00013)
                return False
            with self.__ma:
                self.__st  = tskState_
                self.__xst = self._TaskState2UtXState()
                return True

        def _TaskState2UtXState(self) -> _EUTaskXState:
            if self.__isInvalid:
                return None

            _stateID = None if self.__st is None else self.__st.GetStateID()
            if _stateID is None:
                return _EUTaskXState.eUTInitialized

            _curVal = _stateID.value
            if _curVal >= _TaskState._EState.eRunProgressAborted.value:
                _curVal = _EUTaskXState.eUTAborting.value
            elif _curVal >= _TaskState._EState.ePendingStopRequest.value:
                if (_curVal > _TaskState._EState.ePendingStopRequest.value) and (_curVal < _TaskState._EState.eProcessingStopped.value):
                    _curVal = _EUTaskXState.eUTCanceling.value
                else:
                    _curVal = _EUTaskXState.eUTStopping.value
            elif _curVal >= _TaskState._EState.eFailed.value:
                _curVal = _EUTaskXState.eUTFailed.value
            res = _EUTaskXState(_curVal)
            return res

        def _ToString(self):
            pass

        def _CleanUp(self):
            if self.__isInvalid:
                return

            if self.__tp is not None:
                self.__tp.CleanUp()
            self.__bM    = None
            self.__ma    = None
            self.__st    = None
            self.__tn    = None
            self.__tp    = None
            self.__dht   = None
            self.__tid   = None
            self.__xst   = None
            self.__sndOp = None

        @property
        def __isInvalid(self):
            return self.__ma is None

    __slots__ = [ '__utm' , '__xc' , '__xd' , '__ma' , '__md' , '__xp' , '__xrn' ]

    __prfc = None

    def __init__(self, utm_ : _UTaskMirror, xtPrf_ : _XTaskPrfExt):
        self.__xd  = None
        self.__ma  = None
        self.__xp  = None
        self.__md  = None
        self.__xc  = None
        self.__xrn = None
        self.__utm = None

        _LcProxyClient.__init__(self)
        _IUTaskConn.__init__(self)

        if not isinstance(utm_, _UTaskMirror):
            self.CleanUp()
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00014)
        elif not (isinstance(xtPrf_, _XTaskPrfExt) and xtPrf_.isValid):
            self.CleanUp()
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00017)
        else:
            _xc = _TaskXCard(xtPrfExt_=xtPrf_)
            if not _xc.isValid:
                self.CleanUp()
            else:
                xtPrf_._Freeze()

                self.__ma  = _Mutex()
                self.__md  = _Mutex()
                self.__xc  = _xc
                self.__xp  = xtPrf_
                self.__utm = utm_

    @override
    def _PcSelfCheck(self) -> _ETaskSelfCheckResultID:
        if self.__isInvalid:
            return _ETaskSelfCheckResultID.eScrStop

        _mscr = self.__utm._mrSelfCheckResult
        if _mscr._isScrNOK:
            return _mscr

        _pscr = _LcProxyClient._PcSelfCheck(self)
        if _pscr._isScrNOK:
            self.__utm._mrSelfCheckResult = _pscr
            return _pscr

        if self.__isUtDisconnected or self.__isFwUnavailable or self._PcIsTaskMgrFailed():
            res = _ETaskSelfCheckResultID.eScrStop
            self.__utm._mrSelfCheckResult = res
            return res

        _tmgr = self._PcGetTaskMgr()
        if not self._PcGetTaskMgr().IsCurTask(self.__utaskUID):
            res = self.__utm._mrSelfCheckResult
        else:
            res = _tmgr.SelfCheckTask(self.__utaskUID)
            self.__utm._mrSelfCheckResult = res
        return res

    @_IUTaskConn._isUTConnected.getter
    def _isUTConnected(self) -> bool:
        return self.__isUtConnected

    @_IUTaskConn._taskUID.getter
    def _taskUID(self) -> Union[int, None]:
        if self.__isInvalid:
            return None
        if self.__isUtDisconnected:
            return None
        return self.__utm.mrUTaskUID

    @_IUTaskConn._taskProfile.getter
    def _taskProfile(self) -> _XTaskPrfExt:
        return self.__xp

    @_IUTaskConn._xCard.getter
    def _xCard(self) -> _TaskXCard:
        return self.__xc

    @_IUTaskConn._utAgent.getter
    def _utAgent(self) -> Union[_IUTAgent, None]:
        if self.__isInvalid:
            return None
        if self.__isUtDisconnected:
            return None
        return self.__utm.mrUTAgent

    @override
    def _IncEuRNumber(self):
        if self.__xrn is None:
            return
        self.__xrn += 1

    @override
    def _UpdateUTD( self, atask_ : _AbsFwTask):
        if self.__isInvalid or self.__isFwUnavailable:
            return False
        if not atask_.isValid:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00945)
            return False

        with self.__md:
            if self.__isFwTaskDisconnected:
                self.__xd = _UserTaskConn.__UTConnData(ma_=self.__md)

            if self.__xd.dtaskUID is None:
                self.__xd._SetData(atask_.taskBadge, atask_.daprofile, atask_.dHThrd, atask_.sendOperator)
                if self.__xd.dtaskUID is None:
                    self.__xd.CleanUp()
                    self.__xd = None
                    return False

                self.__xrn = -1
                if self.__isUtConnected:
                    self.__utm._MrUpdateTaskID(atask_.taskBadge.dtaskUID, atask_.taskBadge.dtaskName)

            _xtSt         = self.__xd.utaskXState
            _bWasXtFailed = False if _xtSt is None else _xtSt.isUtFailed or _xtSt.isUtAborting

            _atSt = atask_._tskState
            res   = self.__xd._UpdateState(_atSt)
            if not res:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00033)
            elif self.__utm is None:
                if not (_atSt.isTerminated or _atSt.isTerminating or _atSt.isFailedByXCmdReturn):
                    print(f'>>> _atSt: {_atSt}')
                    res = res
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00034)
            else:
                _xtSt = self.__xd.utaskXState
                _bA, _bT = _atSt.isAborting, _atSt.isTerminated

                if _bA or _bT:
                    if _bA or _atSt.isFailed:
                        if not _bWasXtFailed:
                            _bT, _xtSt = True, _EUTaskXState.eUTFailed
                            logif._LogInfo(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTaskConn_TID_024).format(self.__GetFormattedUTLabel().capitalize()))
                if _bT:
                    self.__DisconnectUTMirror(_xtSt)
                else:
                    self.__utm._MrUpdateTaskState(_xtSt)
            return res

    @override
    def _DisconnectUTask(self, bDetachApiRequest_ =False):
        if self.__isInvalid:
            return
        with self.__md:
            if self.__utm is not None:
                if self.__isFwTaskDisconnected or not self._PcIsLcProxyModeNormal():
                    _xtSt = self.__utm._mrUTaskXState
                else:
                    if self._isRunning:
                        if bDetachApiRequest_:
                            if self._PcIsTaskMgrAvailable():
                                _oppc  = self.__PreCheckTaskOperation(_EATaskOpID.eStop)
                                _bStop = not (_oppc.isNotApplicable or _oppc.isIgnorable)

                                _oppc.CleanUp()
                                if _bStop:
                                    self._PcGetTaskMgr().StopUTask(self, bCancel_=False, bCleanupDriver_=False)
                    _xtSt = self.__xd.utaskXState

                if _xtSt is not None:
                    self.__DisconnectUTMirror(_xtSt)

    @property
    def _isStarted(self) -> bool:
        if self.__isFwTaskDisconnected:
            return False
        with self.__md:
            _xtSt = self.__xd.utaskXState
            return False if _xtSt is None else _xtSt.isUtStarted

    @property
    def _isPendingRun(self) -> bool:
        if self.__isFwTaskDisconnected:
            return False
        with self.__md:
            _xtSt = self.__xd.utaskXState
            return False if _xtSt is None else _xtSt.isUtPendingRun

    @property
    def _isRunning(self) -> bool:
        if self.__isFwTaskDisconnected:
            return False
        with self.__md:
            _xtSt = self.__xd.utaskXState
            return False if _xtSt is None else _xtSt.isUtRunning

    @property
    def _isDone(self) -> bool:
        if self.__isFwTaskDisconnected:
            return False
        with self.__md:
            _xtSt = self.__xd.utaskXState
            return False if _xtSt is None else _xtSt.isUtDone

    @property
    def _isCanceled(self) -> bool:
        if self.__isFwTaskDisconnected:
            return False
        with self.__md:
            _xtSt = self.__xd.utaskXState
            return False if _xtSt is None else _xtSt.isUtCanceled

    @property
    def _isFailed(self) -> bool:
        if self.__isFwTaskDisconnected:
            return False
        with self.__md:
            _xtSt = self.__xd.utaskXState
            return False if _xtSt is None else _xtSt.isUtFailed

    @property
    def _isStopping(self) -> bool:
        if self.__isFwTaskDisconnected:
            return False
        with self.__md:
            _xtSt = self.__xd.utaskXState
            return False if _xtSt is None else _xtSt.isUtStopping

    @property
    def _isCanceling(self) -> bool:
        if self.__isFwTaskDisconnected:
            return False
        with self.__md:
            _xtSt = self.__xd.utaskXState
            return False if _xtSt is None else _xtSt.isUtCanceling

    @property
    def _isAborting(self) -> bool:
        if self.__isFwTaskDisconnected:
            return False
        with self.__md:
            _xtSt = self.__xd.utaskXState
            return False if _xtSt is None else _xtSt.isUtAborting

    @property
    def _currentError(self) -> ITaskError:
        return self.__GetCurrentError()

    @property
    def _xrNumber(self) -> int:
        if self.__xrn is None:
            return -1
        return self.__xrn

    @property
    def _utXStateToString(self) -> str:
        if self.__isInvalid:
            return None
        with self.__md:
            _xtSt = None if self.__isFwTaskDisconnected else self.__xd.utaskXState
            return None if _xtSt is None else _xtSt._ToString(self.__utm is None)

    def _StartUTask(self, *args_, **kwargs_) -> bool:
        if self.__isInvalid:
            return False
        if self.__isUtDisconnected:
            return False

        _midPart = self.__GetFormattedUTLabel()

        if self.__isFwUnavailable:
            logif._XLogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTaskConn_TID_001).format(_midPart))
            return False

        elif self._isStarted:
            logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTaskConn_TID_004).format(_midPart.capitalize()))
            return False

        elif self.__isLcProxyUnavailable:
            return False

        elif not self._PcIsLcProxyModeNormal():
            logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTaskConn_TID_003).format(_midPart))
            return False

        elif not self._PcIsTaskMgrAvailable():
            logif._XLogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTaskConn_TID_001).format(_midPart))
            return False

        self.__xc._SetStartArgs(*args_, **kwargs_)

        _bSyncTask = self.__xp.isSyncTask
        if not _bSyncTask:
            self.__ma.Take()

        if _bSyncTask:
            res = self._PcGetTaskMgr().StartUTask(self)
        else:
            res = self._PcGetTaskMgr().StartUTask(self)
            self.__ma.Give()

        _bErrorFree = self._currentError is None

        if self.__isInvalid:
            logif._LogErrorEC(_EFwErrorCode.UE_00010, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTaskConn_TID_008).format(_midPart))
        elif not res:
            if _bErrorFree:
                logif._LogErrorEC(_EFwErrorCode.UE_00011, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTaskConn_TID_008).format(_midPart))
        elif self._isFailed:
            res = False
            if _bErrorFree:
                logif._LogErrorEC(_EFwErrorCode.UE_00012, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTaskConn_TID_009).format(_midPart))
        return res

    def _StopUTask(self, bCancel_ =False, bCleanupDriver_ =True) -> bool:
        if self.__isInvalid:
            return False
        if self.__isUtDisconnected:
            return False

        _midPart = self.__GetFormattedUTLabel()

        if self.__isFwUnavailable:
            logif._XLogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTaskConn_TID_016).format(_midPart))
            return False

        elif self.__isFwTaskDisconnected:
            logif._LogErrorEC(_EFwErrorCode.UE_00013, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTaskConn_TID_019).format(_midPart))
            return False

        elif self.__isLcProxyUnavailable:
            return False

        elif not self._PcIsLcProxyModeNormal():
            logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTaskConn_TID_018).format(_midPart))
            return False

        elif not self._PcIsTaskMgrAvailable():
            logif._XLogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTaskConn_TID_016).format(_midPart))
            return False

        self.__ma.Take()
        _oppc = self.__PreCheckTaskOperation(_EATaskOpID.eCancel if bCancel_ else _EATaskOpID.eStop)
        if _oppc.isNotApplicable or _oppc.isIgnorable:
            self.__ma.Give()
            res = _oppc.isIgnorable
        else:
            if _oppc.isSynchronous:
                self.__ma.Give()
            res = self._PcGetTaskMgr().StopUTask(self, bCancel_=bCancel_, bCleanupDriver_=bCleanupDriver_)

            if not self.__isInvalid: self.__ma.Give()
        _oppc.CleanUp()
        return res

    def _JoinUTask(self, timeout_ : Union[int, float] =None) -> bool:
        if self.__isInvalid:
            return False
        if self.__isUtDisconnected:
            return False

        _midPart = self.__GetFormattedUTLabel()

        if self.__isFwUnavailable:
            logif._XLogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTaskConn_TID_021).format(_midPart))
            return False

        elif self.__isFwTaskDisconnected:
            logif._LogErrorEC(_EFwErrorCode.UE_00014, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTaskConn_TID_007).format(_midPart))
            return False

        elif self.__isLcProxyUnavailable:
            return False

        elif not self._PcIsLcProxyModeNormal():
            logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTaskConn_TID_022).format(_midPart))
            return False

        elif not self._PcIsTaskMgrAvailable():
            logif._XLogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTaskConn_TID_021).format(_midPart))
            return False

        elif self._PcIsLcMonShutdownEnabled():
            logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTaskConn_TID_023).format(_midPart))
            return False

        _tout = timeout_
        if timeout_ is not None:
            if not isinstance(timeout_, (int, float)):
                if not isinstance(timeout_, _Timeout):
                    logif._LogErrorEC(_EFwErrorCode.UE_00015, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTaskConn_TID_002).format(type(timeout_).__name__, _midPart))
                    return False
            elif (isinstance(timeout_, int) and timeout_ < 0) or (isinstance(timeout_, float) and timeout_ < 0.0):
                logif._LogErrorEC(_EFwErrorCode.UE_00016, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTaskConn_TID_012).format(str(timeout_), _midPart))
                return False

            if not isinstance(timeout_, _Timeout):
                if isinstance(timeout_, int):
                    _tout = _Timeout.CreateTimeoutMS(timeout_)
                else:
                    _tout = _Timeout.CreateTimeoutSec(timeout_)

        self.__ma.Take()
        _oppc = self.__PreCheckTaskOperation(_EATaskOpID.eJoin)
        if _oppc.isNotApplicable or _oppc.isIgnorable:
            self.__ma.Give()
            res = _oppc.isIgnorable
        else:
            if _oppc.isSynchronous:
                self.__ma.Give()
            res = self._PcGetTaskMgr().JoinUTask(self, timeout_=_tout)

            if not self.__isInvalid: self.__ma.Give()
        _oppc.CleanUp()

        if _tout is not None:
            if isinstance(timeout_, _Timeout):
                _tout.CleanUp()
        return res

    def _ClearCurrentError(self) -> bool:
        res = False
        if self.__isUtDisconnected:
            pass
        elif self.__isFwUnavailable:
            pass
        elif self.__isLcProxyUnavailable:
            pass
        elif not self._PcIsLcProxyModeNormal():
            pass
        elif not self._PcIsTaskMgrAvailable():
            pass
        elif not self._PcGetTaskMgr().IsCurTask(self.__utaskUID):
            logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTaskConn_TID_029).format(self.__utaskUID))
        else:
            _tskErr      = self._PcGetTaskMgr().GetTaskError(self.__utaskUID)
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
                    res = _tskErr.ClearError() and _tskErr.isErrorFree
                    if not res:
                        vlogif._LogOEC(True, _EFwErrorCode.VFE_00023)
                else:
                    res = True
        return res

    def _SetTaskError(self, bFatal_ : bool, errMsg_: str, errCode_: int =None):
        if self.__isUtDisconnected:
            pass
        elif self.__isFwUnavailable:
            pass
        elif self.__isLcProxyUnavailable:
            pass
        elif not self._PcIsLcProxyModeNormal():
            pass
        elif not self._PcIsTaskMgrAvailable():
            pass
        elif not self._PcGetTaskMgr().IsCurTask(self.__utaskUID):
            _msgID = _EFwTextID.eLogMsg_UserTaskConn_TID_033 if bFatal_ else _EFwTextID.eLogMsg_UserTaskConn_TID_032
            logif._LogWarning(_FwTDbEngine.GetText(_msgID).format(self.__utaskUID))
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
        if self.__isUtDisconnected:
            return False
        if not self._PcIsLcProxyModeNormal():
            return False

        _midPart = self.__GetFormattedUTLabel()

        if self.__isFwTaskDisconnected:
            logif._LogErrorEC(_EFwErrorCode.UE_00178, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTaskConn_TID_030).format(_midPart))
            return False

        _msgOp = None
        with self.__md:
            _xdata = self.__xd
            if _xdata is None:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00024)
                return False
            if (_xdata.utaskXState is None) or _xdata.utaskXState.isUtAborting:
                return False

            _bMsgXT = _xdata.isMsgXTask
            if not _bMsgXT:
                if xmsg_.isInternalMsg:
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00942)
                    return False
                if _FwSubsysCoding.IsSenderExternalQueueSupportMandatory():
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00943)
                    return False
            _msgOp = _xdata._msgOperator

        return _msgOp._SendMessage(xmsg_)

    def _TriggerQueueProcessing(self, bExtQueue_ : bool) -> int:
        if self.__isUtDisconnected:
            return False
        if not self._PcIsLcProxyModeNormal():
            return False

        _midPart = self.__GetFormattedUTLabel()

        if self.__isFwTaskDisconnected:
            logif._XLogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTaskConn_TID_031).format(_midPart))
            return -1

        _msgOp = None
        with self.__md:
            _xdata = self.__xd
            if _xdata is None:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00024)
                return -1
            if not _xdata.isMsgXTask:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00027)
                return -1
            if (_xdata.utaskXState is None) or not (_xdata.utaskXState.isUtRunning or _xdata.utaskXState.isUtStopping):
                return -1
            _msgOp = _xdata._msgOperator

        return _msgOp._TriggerQueueProc(bExtQueue_)

    def _CPrf(self, enclHThrd_ : _PyThread =None, profileAttrs_ : dict =None):
        _prfc = _UserTaskConn.__prfc
        if _prfc is None:
            res = None
        else:
            res = _prfc._CreateXTaskProfile(self, enclHThrd_=enclHThrd_, profileAttrs_=profileAttrs_)
        return res

    def _ToString(self):
        if self.__isInvalid:
            return type(self).__name__

        res = self.__logPrefix
        _ut = self._utAgent
        if _ut is None:
            pass
        else:
            res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_008).format(_ut)
        return res

    def _CleanUp(self):
        if self.__isInvalid:
            return

        _n = self.__logPrefix

        self._DisconnectUTask()

        _LcProxyClient._CleanUp(self)
        if self.__xd is not None:
            self.__xd.CleanUp()
        self.__md.CleanUp()
        self.__ma.CleanUp()
        self.__xc.CleanUp()

        self.__ma  = None
        self.__md  = None
        self.__xd  = None
        self.__xp  = None
        self.__xc  = None
        self.__utm = None
        self.__xrn = None

    @staticmethod
    def _ClsDepInjection(dinjCmd_ : _EDepInjCmd, ak_, prfc_):
        return _UserTaskConn._SetPRFC(ak_, prfc_)

    @staticmethod
    def _SetPRFC(ak_, prfc_):
        _ak = hash(str(_UserTaskConn.__init__))
        res = ak_ == _ak
        if not res:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00035)
        else:
            if (prfc_ is not None) and (_UserTaskConn.__prfc is not None):
                pass
            elif (prfc_ is None) and (_UserTaskConn.__prfc is None):
                pass
            else:
                _UserTaskConn.__prfc = prfc_
        return res

    @property
    def __isInvalid(self):
        return self.__md is None

    @property
    def __isMainUTConnector(self) -> bool:
        return self.__isUtConnected and self.__xp.isMainTask

    @property
    def __isUtConnected(self):
        if self.__isInvalid:
            return False
        with self.__md:
            return self.__utm is not None

    @property
    def __isUtDisconnected(self):
        if self.__isInvalid:
            return False
        with self.__md:
            return self.__utm is None

    @property
    def __isFwAvailable(self):
        return _FwApiConnectorAP._APIsFwApiConnected()

    @property
    def __isFwUnavailable(self):
        return not self.__isFwAvailable

    @property
    def __isLcProxyUnavailable(self):
        if not self._PcIsLcProxySet():
            _prfc = _UserTaskConn.__prfc
            if _prfc is not None:
                _pxy = _prfc._GetLcProxy()
                if (_pxy is not None) and _pxy._PxyIsLcProxyModeNormal():
                    self._PcSetLcProxy(_pxy)
        res = self._PcIsLcProxyModeShutdown()
        return res

    @property
    def __isFwTaskConnected(self) -> bool:
        return self.__xd is not None

    @property
    def __isFwTaskDisconnected(self) -> bool:
        return self.__xd is None

    @property
    def __utaskName(self):
        if self.__isInvalid:
            res = _CommonDefines._STR_EMPTY
        elif self.__isUtConnected:
            res = self.__utm.mrUTaskName
        elif self.__isFwTaskDisconnected:
            res = _CommonDefines._STR_EMPTY
        else:
            res = self.__xd.dtaskName
        return res

    @property
    def __utaskUID(self):
        if self.__isInvalid:
            res = None
        elif self.__isUtConnected:
            res = self.__utm.mrUTaskUID
        elif self.__isFwTaskDisconnected:
            res = None
        else:
            res = self.__xd.dtaskUID
        return res

    @property
    def __logPrefixStateUpdate(self):
        res     = _FwTDbEngine.GetText(_EFwTextID.eUserTaskConn_LogPrefix) + _FwTDbEngine.GetText(_EFwTextID.eUserTaskConn_LogPrefix_StateUpdate)
        _xtname = self.__utaskName
        if (_xtname is not None) and (len(_xtname) > 0):
            res += f'[{_xtname}] '
        return res

    @property
    def __logPrefix(self):
        res     = _FwTDbEngine.GetText(_EFwTextID.eUserTaskConn_LogPrefix)
        _xtname = self.__utaskName
        if (_xtname is not None) and (len(_xtname) > 0):
            res += f'[{_xtname}] '
        return res

    def __GetFormattedUTLabel(self) -> str:
        if self.__isInvalid:
            return _CommonDefines._STR_EMPTY

        res  = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_007).format(_FwTDbEngine.GetText(_EFwTextID.eMisc_Main)) if self.__isMainUTConnector else _CommonDefines._STR_EMPTY
        res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_001).format(_FwTDbEngine.GetText(_EFwTextID.eMisc_Task), self.__utaskName)
        return res

    def __GetCurrentError(self) -> ITaskError:
        if self.__isUtDisconnected:
            return None
        if self.__isFwUnavailable:
            return None
        if self.__isLcProxyUnavailable:
            return None
        if not self._PcIsTaskMgrAvailable():
            return None

        res          = None
        _tskErr      = self._PcGetTaskMgr().GetTaskError(self.__utaskUID)
        _myLogPrefix = self.__logPrefix

        if _tskErr is None:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00036)
        elif _tskErr.taskBadge.isDrivingXTask:
            _curEE = _tskErr._currentErrorEntry
            if _curEE is not None:
                _bFatal = _curEE.isFatalError or _curEE.hasNoImpactDueToFrcLinkage
                _tmp = _XTaskErrorImpl(_curEE.uniqueID, _bFatal, _bFatal and logif._IsFwDieModeEnabled(), _curEE.shortMessage, errCode_=None if _curEE.isAnonymousError else _curEE.errorCode)
                res  = XTaskError(_tmp)
        return res

    def __DisconnectUTMirror(self, xtDetachState_ : _EUTaskXState):
        if self.__isInvalid:
            return
        if self.__utm is None:
            return
        if not isinstance(xtDetachState_, _EUTaskXState):
            return

        self.__utm._MrUpdateTaskState(xtDetachState_, bDetach_=True)

        self.__utm = None

    def __PreCheckTaskOperation(self, taskOpID_ : _EATaskOpID) -> _ATaskOpPreCheck:
        return _ATaskOpPreCheck(taskOpID_, self.__xd._dtaskState, self.__xd.dtaskPyThread, self.__xp.isSyncTask, bReportErr_=True)
