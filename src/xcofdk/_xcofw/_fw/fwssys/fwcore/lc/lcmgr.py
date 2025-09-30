# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : lcmgr.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum      import IntEnum
from threading import RLock as _PyRLock
from typing    import List
from typing    import Tuple
from typing    import Union

from xcofdk.fwcom     import LcFailure
from xcofdk.fwapi     import IRCTask
from xcofdk.fwapi     import IRCCommTask
from xcofdk.fwcom     import EXmsgPredefinedID
from xcofdk.fwapi.xmt import IXTask

from _fw.fwssys.assys                         import fwsubsysshare as _ssshare
from _fw.fwssys.assys.fwsubsysshare           import _FwSubsysShare
from _fw.fwssys.assys.ifs.tiflcmgr            import _TILcManager
from _fw.fwssys.fwcore.logging                import logif
from _fw.fwssys.fwcore.logging                import vlogif
from _fw.fwssys.fwctrl.fwapiconn              import _FwApiConnector
from _fw.fwssys.fwcore.base.gtimeout          import _Timeout
from _fw.fwssys.fwcore.base.timeutil          import _KpiLogBook
from _fw.fwssys.fwcore.config.fwstartuppolicy import _FwStartupPolicy
from _fw.fwssys.fwcore.ipc.fws.afwservice     import _AbsFwService
from _fw.fwssys.fwcore.ipc.sync.syncresbase   import _PySemaphore
from _fw.fwssys.fwcore.ipc.tsk.afwtask        import _AbsFwTask
from _fw.fwssys.fwcore.ipc.tsk.taskdefs       import _EFwsID
from _fw.fwssys.fwcore.ipc.tsk.taskmgr        import _TaskMgr
from _fw.fwssys.fwcore.ipc.tsk.taskmgr        import _TTaskMgr
from _fw.fwssys.fwcore.ipc.tsk.taskutil       import _TaskUtil
from _fw.fwssys.fwcore.lc.lcdefines           import _ELcScope
from _fw.fwssys.fwcore.lc.lcdefines           import _ELcCompID
from _fw.fwssys.fwcore.lc.lcdefines           import _LcConfig
from _fw.fwssys.fwcore.lc.lcdepmgr            import _LcDepManager
from _fw.fwssys.fwcore.lc.lcxstate            import _ELcKpiID
from _fw.fwssys.fwcore.lc.lcxstate            import _ELcXState
from _fw.fwssys.fwcore.lc.lcxstate            import _LcXStateHistory
from _fw.fwssys.fwcore.lc.lcxstate            import _LcFailure
from _fw.fwssys.fwcore.lc.lcguard             import _LcGuard
from _fw.fwssys.fwcore.lc.lcproxydefines      import _ELcSDRequest
from _fw.fwssys.fwcore.lc.lcproxy             import _LcProxy
from _fw.fwssys.fwcore.lc.ifs.iflcstate       import _ILcState
from _fw.fwssys.fwcore.lc.lcmn.lcmonimpl      import _LcMonitorImpl
from _fw.fwssys.fwcore.logrd.logrdagent       import _LogRDAgent
from _fw.fwssys.fwcore.types.aobject          import _AbsSlotsObject
from _fw.fwssys.fwcore.types.commontypes      import override
from _fw.fwssys.fwerrh.fwerrorcodes           import _EFwErrorCode
from _fw.fwssys.fwerrh.logs.errorlog          import _FatalLog

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _LcManager(_FwApiConnector, _TILcManager):
    class _FwApiReturnRecord:
        __slots__ = [ '__m' , '__s' ]

        def __init__(self, mainXT_, syncSem_):
            self.__m = mainXT_
            self.__s = syncSem_

        @property
        def syncSem(self) -> _PySemaphore:
            return self.__s

        @property
        def mainXTask(self):
            return self.__m

    class _LcMgrSetupRunner(_AbsSlotsObject):
        __slots__ = [ '__mgr' , '__p' , '__m' , '__a' , '__bS' ]

        def __init__(self, lcMgr_, ppass_ : int, startOptions_ : list, mainXT_ =None):
            self.__a   = startOptions_
            self.__m   = mainXT_
            self.__p   = ppass_
            self.__bS  = False
            self.__mgr = lcMgr_
            super().__init__()

        def __call__(self, *args_, **kwargs_):
            self.__bS = self.__mgr._AsyncSetUpLcMgr(self.__p, self.__a, mainXT_=self.__m)

        def _CleanUp(self):
            self.__a   = None
            self.__m   = None
            self.__p   = None
            self.__bS  = None
            self.__mgr = None

        @property
        def isLcMgrSetupRunnerSucceeded(self):
            return self.__bS

    class _LcSDHelper(_AbsSlotsObject):
        __slots__ = [ '__bAS' , '__iJR' , '__iSR' ]

        def __init__(self):
            self.__bAS = True
            self.__iJR = 0
            self.__iSR = 0
            super().__init__()

        @property
        def _isStopRequestSubmitted(self):
            return self.__isValid and (self.__iSR != 0)

        @property
        def _isInternalStopRequestSubmitted(self):
            return self.__isValid and (self.__iSR == -1)

        @property
        def _isJoinRequestSubmitted(self):
            return self.__isValid and (self.__iJR != 0)

        @property
        def _isInternalJoinRequestSubmitted(self):
            return self.__isValid and (self.__iJR == -1)

        def _SetStopRequest(self, bInternal_ : bool =False):
            if self.__isValid and (self.__iSR == 0):
                self.__iSR = -1 if bInternal_ else 1

        def _SetJoinRequest(self, bInternal_ : bool =False):
            if self.__isValid and (self.__iJR == 0):
                self.__iJR = -1 if bInternal_ else 1

        def _CleanUp(self):
            self.__bAS = None
            self.__iJR = None
            self.__iSR = None

        @property
        def __isValid(self):
            return self.__bAS is not None

    __slots__ = [ '__la' , '__dm' , '__gi' , '__pi' , '__ts' , '__m' , '__s' , '__mi' , '__ld' , '__xh' , '__kpi' , '__sdh' , '__sup' ]

    __sgltn      = None
    __MSG_PREFIX = _FwTDbEngine.GetText(_EFwTextID.eLcManager_MsgPrefix)

    def __init__(self, ppass_ : int, suPolicy_ : _FwStartupPolicy, startOptions_ : list, mainXT_ =None):
        self.__m   = None
        self.__s   = None
        self.__dm  = None
        self.__gi  = None
        self.__la  = None
        self.__ld  = None
        self.__mi  = None
        self.__ts  = None
        self.__pi  = None
        self.__xh  = None
        self.__kpi = None
        self.__sdh = None
        self.__sup = None
        _FwApiConnector.__init__(self, ppass_)
        _TILcManager.__init__(self, ppass_)

        if _LcManager.__sgltn is not None:
            self.CleanUpByOwnerRequest(ppass_)
            _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_047)

            vlogif._LogOEC(True, _EFwErrorCode.VFE_00359)
            return

        _LcManager.__sgltn = self

        _lcKPI = _KpiLogBook._GetStartupKPI()
        _lcKPI.AddKPI(_ELcKpiID.eLcConfigStart)

        self.__la = _PyRLock()
        self.__ld = _PyRLock()
        _FwApiConnector._FwCNSetFwApiLock(self, self.__la)

        _tgtScope = _LcConfig.GetTargetScope()
        _errMsg  = None
        _lcfMsg  = None
        _errCode = None

        _eExpectedExecState = _ELcXState.ePreConfigPhase

        self.__xh = _LcFailure._GetLcXStateHistory()
        if (self.__xh is None) or not self.__xh.IsLcExecutionStateSet(_eExpectedExecState):
            self.CleanUpByOwnerRequest(ppass_)
            _lcfMsg  = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_039).format(_eExpectedExecState.compactName)
            _errMsg  = f'{_LcManager.__MSG_PREFIX}' + _lcfMsg
            _errCode = _EFwErrorCode.FE_LCSF_092

        elif (startOptions_ is not None) and not isinstance(startOptions_, list):
            self.CleanUpByOwnerRequest(ppass_)
            _lcfMsg  = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_034).format(type(startOptions_).__name__)
            _errMsg  = f'{_LcManager.__MSG_PREFIX}' + _lcfMsg
            _errCode = _EFwErrorCode.FE_LCSF_093

        elif not isinstance(_tgtScope, _ELcScope):
            self.CleanUpByOwnerRequest(ppass_)
            _lcfMsg  = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_035).format(type(_tgtScope).__name__)
            _errMsg  = f'{_LcManager.__MSG_PREFIX}' + _lcfMsg
            _errCode = _EFwErrorCode.FE_LCSF_094

        elif _tgtScope.isIdle:
            self.CleanUpByOwnerRequest(ppass_)
            _lcfMsg  = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_036).format(_tgtScope.value, _tgtScope.compactName)
            _errMsg  = f'{_LcManager.__MSG_PREFIX}' + _lcfMsg
            _errCode = _EFwErrorCode.FE_LCSF_095
        else:
            _myGuard = _LcGuard(self._myPPass, self)

            if _LcFailure.IsLcNotErrorFree():
                _myGuard.CleanUpByOwnerRequest(ppass_)
                self.CleanUpByOwnerRequest(ppass_)
            else:
                self.__gi  = _myGuard
                self.__kpi = _lcKPI
                self.__sdh = _LcManager._LcSDHelper()
                self.__sup = suPolicy_
        if (_errMsg is not None) or _LcFailure.IsLcNotErrorFree():
            if _LcFailure.IsLcErrorFree():
                if _errCode is None:
                    _errCode = _EFwErrorCode.FE_LCSF_049
                _LcFailure.CheckSetLcSetupFailure(_errCode)
            if _errMsg is not None:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00361)

    @override
    def _IsLcErrorFree(self) -> bool:
        if _LcManager.__sgltn is None:
            return _LcFailure.IsLcErrorFree()

        with self.__la:
            res = _LcFailure.IsLcErrorFree()
            if res:
                if self.__gi is not None:
                    res = not self.__gi.hasLcAnyFailureState
            return res

    @override
    def _IsLcShutdownEnabled(self) -> bool:
        if _LcManager.__sgltn is None:
            return False
        with self.__la:
            return (self.__mi is not None) and self.__mi.isLcShutdownEnabled

    @override
    def _IsXTaskRunning(self, xtUID_ : int) -> bool:
        if _LcManager.__sgltn is None:
            return False
        if isinstance(xtUID_, EXmsgPredefinedID) and xtUID_==EXmsgPredefinedID.MainTask:
            _mt = _LcManager.__GetMainXTask()
            return (_mt is not None) and _mt.isRunning

        with self.__la:
            res     = False
            _tskMgr = _TaskMgr()

            _bOK = self.__mi is not None
            _bOK = _bOK and not self.__mi.isLcShutdownEnabled
            _bOK = _bOK and (_tskMgr is not None)
            _bOK = _bOK and (self.__pi is not None) and self.__pi._PxyIsLcProxyModeNormal()
            if not _bOK:
                pass
            else:
                _ti   = _tskMgr.GetTask(xtUID_, bDoWarn_=False)
                _tb = None if _ti is None else _ti.taskBadge
                if (_tb is None) or not _tb.isDrivingXTask:
                    pass
                else:
                    res = _ti._utConn._isRunning
            return res

    @override
    def _GetLcFailure(self) -> Union[LcFailure, None]:
        if _LcManager.__sgltn is None:
            return _LcFailure._GetLcFailure()

        with self.__la:
            res = _LcFailure._GetLcFailure()
            if res is None:
                _frcv = None if (self.__gi is None) else self.__gi.lcFrcView
                if _frcv is not None:
                    res = LcFailure(str(_frcv), _frcv.errorMessage, _frcv.errorCode)
            return res

    @override
    def _GetXTask(self, xtUID_ : int =0) -> Union[IXTask, None]:
        if not self.__ts.isIPC:
            return None
        if _LcManager.__sgltn is None:
            return None
        if xtUID_ == 0:
            res, _dc = self._GetCurXTask()
            return res

        with self.__la:
            res     = None
            _tskMgr = _TaskMgr()

            _bOK = True
            _bOK = _bOK and not self.__mi.isLcShutdownEnabled
            _bOK = _bOK and (_tskMgr is not None)
            _bOK = _bOK and (self.__pi is not None) and self.__pi._PxyIsLcProxyModeNormal()
            if not _bOK:
                logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_045).format(xtUID_))
            else:
                _ti = _tskMgr.GetTask(xtUID_, bDoWarn_=False)
                _tb = None if _ti is None else _ti.taskBadge
                if (_tb is None) or not _tb.isDrivingXTask:
                    pass
                else:
                    _utc = _ti._utConn
                    _uta = None if _utc is None else _utc._utAgent
                    res  = None if _uta is None else _uta._xtInst
                if (res is None) or res.isDetachedFromFW:
                    res = None
                    logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_046).format(xtUID_))
            return res

    @override
    def _GetCurXTask(self, bRcTask_ =False) -> Tuple[Union[IXTask, None], Union[IRCTask, None]]:
        if not self.__ts.isIPC:
            return None, None
        if _LcManager.__sgltn is None:
            return None, None

        with self.__la:
            res     = None
            _rct    = None
            _tskMgr = _TTaskMgr()

            _bOK = True
            _bOK = _bOK and not self.__mi.isLcShutdownEnabled
            _bOK = _bOK and (_tskMgr is not None)
            _bOK = _bOK and (self.__pi is not None) and self.__pi._PxyIsLcProxyModeNormal()
            if not _bOK:
                logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_001))
            else:
                _ti = _tskMgr._GetCurTask(bAutoEncl_=True)
                _tb = None if _ti is None else _ti.taskBadge
                if (_tb is None) or not _tb.isDrivingXTask:
                    pass
                elif bRcTask_ and not _tb.isRcTask:
                    pass
                else:
                    _utc = _ti._utConn
                    _uta = None if _utc is None else _utc._utAgent
                    res  = None if _uta is None else _uta._xtInst
                    if res is not None:
                        _xp = _utc._taskProfile
                        _rct = None if _xp is None else _xp._rcTaskInst

                if (res is not None) and res.isDetachedFromFW:
                    res = None

            return res, _rct

    @override
    def _GetCurRcTask(self) -> Union[IRCTask, IRCCommTask, None]:
        _dc, res = self._GetCurXTask(bRcTask_=True)
        return res

    @override
    def _StopFW(self) -> bool:
        if not self.__ts.isIPC:
            return True

        with self.__la:
            if self.__mi.isLcShutdownEnabled:
                return True
            self.__StopFW()
            return True

    @override
    def _JoinFW(self) -> bool:
        res = self.__JoinFW()
        if res:
            _mainXT = self.__m
            if _mainXT is None:
                _mainXT = _LcManager.__GetMainXTask()

            if _mainXT is not None:
                _mainXT.DetachFromFW()
        return res

    @override
    def _JoinTasks(self, tasks_: Union[int, List[int], None] =None, timeout_: Union[int, float] =None) -> Tuple[int, Union[List[int], None]]:
        _numJ, _lstUnj = self.__JoinXUnits(True, xunits_=tasks_, timeout_=timeout_)
        return _numJ, _lstUnj

    @override
    def _JoinProcesses(self, procs_: Union[int, List[int], None] =None, timeout_: Union[int, float] =None) -> Tuple[int, Union[List[int], None]]:
        _numJ, _lstUnj =  self.__JoinXUnits(False, xunits_=procs_, timeout_=timeout_)
        return _numJ, _lstUnj

    @override
    def _TerminateProcesses(self, procs_: Union[int, List[int], None] =None) -> int:
        return self.__TerminateProcesses(procs_)

    @override
    def _TIFPreCheckLcFailureNotification(self, eFailedCompID_ : _ELcCompID):
        res = False
        if (self.__xh is None) or (_TaskMgr() is None):
            pass
        elif not self.__xh.hasPassedCustomSetupPhase:
            pass
        elif self.__pi._PxyIsLcProxyModeShutdown():
            pass
        else:
            res = True
        return res

    @override
    def _TIFOnLcFailure(self, eFailedCompID_: _ELcCompID, frcError_: _FatalLog, atask_: _AbsFwTask =None, bPrvRequestReply_ =True):
        if not self._TIFPreCheckLcFailureNotification(eFailedCompID_):
            return
        self.__pi._PxyProcessShutdownRequest( _ELcSDRequest.eFailureHandling
                                            , eFailedCompID_=eFailedCompID_
                                            , frcError_=frcError_
                                            , atask_=atask_
                                            , bPrvRequestReply_=bPrvRequestReply_)

    @override
    def _TIFOnLcShutdownRequest(self, eShutdownRequest_: _ELcSDRequest) -> bool:
        if (_LcManager.__sgltn is None) or (self.__pi is None):
            return False

        if eShutdownRequest_.isFailureHandling:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00362)
            return False

        _curSDR = self.__mi.curShutdownRequest

        if eShutdownRequest_.isShutdown:
            if not _curSDR.isShutdown:
                self.__pi._PxyProcessShutdownRequest(_ELcSDRequest.eShutdown, bPrvRequestReply_=False)
        else:
            if _curSDR is None:
                self.__StopFW(bInternalRequest_=True)
        return True

    @override
    def _TIFFinalizeStopFW(self, bCleanUpLcMgr_ : bool):
        if _LcManager.__sgltn is None:
            return False

        _mxt = self.__m
        if _mxt is None:
            _mxt = _LcManager.__GetMainXTask()
        if (_mxt is not None) and _mxt.isAttachedToFW:
            if _mxt.isRunning:
                _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_071).format(_mxt.taskUID)
                vlogif._LogUrgentWarning(_msg)

        _mxtUID = None if _mxt is None else _mxt.taskUID
        if self.__pi is not None:
            self.__FinalJoin(_mxtUID)

        if (self.__curLcScope is None) or (self.__curLcScope.lcTransitionalOrder < _ELcScope.eSemiIPC.value):
            _curLcScope = None if self.__curLcScope is None else self.__curLcScope.compactName
        else:
            for _ii in range((self.__curLcScope.value-1), (_ELcScope.eIdle.value-1), -1):
                self.__UpdateScope(srcScope_=self.__curLcScope, dstScope_=_ELcScope(_ii))

        if self.__gi is not None:
            if self.__gi._isGRunning:
                if self.__s is None:
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00364)
                else:
                    _bSTOP_SyNC_NEEDED = False

                    _semSS = self.__s if _bSTOP_SyNC_NEEDED else None
                    self.__gi._GStop(_semSS)
                    if _semSS is not None:
                        _semSS.acquire()

        self.__xh._AddExecutionState(_ELcXState.eStopPassed, self)

        if bCleanUpLcMgr_:
            if not self.__lcState.isLcStopped:
                if not self.__lcState.isLcFailed:
                    self.__SetLcOpState(_ELcCompID.eLcMgr, False)

            self.CleanUpByOwnerRequest(self._myPPass)

        return True

    @staticmethod
    def _CreateLcMgr(startupPolicy_ : _FwStartupPolicy, startOptions_ : list):
        if _LcManager.__sgltn is not None:
            return None

        if not _ssshare._GetRteConfig()._isFrozen:
            res = None
            _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_110, _EFwTextID.eLogMsg_LcManager_TID_027)
        else:
            res = _LcManager.__DoCreateLcMgr(startupPolicy_, startOptions_)

        if res is None:
            _LcFailure._PrintLcResult()
        return res

    @staticmethod
    def _CreateStartupPolicy(ppass_ : int) -> _FwStartupPolicy:
        res = _LcManager.__DoCreateStartupPolicy(ppass_)
        if res is None:
            _LcFailure._PrintLcResult()
        else:
            _LogRDAgent._GetInstance()._AActivate()
        return res

    def _AsyncSetUpLcMgr(self, ppass_ : int, startOptions_ : list, mainXT_ =None):
        return self.__SetUp(ppass_, startOptions_, mainXT_=mainXT_)

    def _ToString(self):
        if self.__dm is None:
            res = None
        else:
            _LC_STATE_COMPACT_OUTPUT = True
            res = _FwTDbEngine.GetText(_EFwTextID.eLcManager_ToString)
            res = res.format(self.__ts.compactName, self.__curLcScope.compactName, self.__lcState.ToString(_LC_STATE_COMPACT_OUTPUT))
        return res

    def _CleanUpByOwnerRequest(self):
        if _LcManager.__sgltn is not None:
            if id(_LcManager.__sgltn) == id(self):
                _LcManager.__sgltn = None
                _FwApiConnector._CleanUpByOwnerRequest(self)

        if self.__dm is not None:
            if self.__pi is not None:
                self.__pi.CleanUpByOwnerRequest(self._myPPass)
            self.__dm.CleanUpByOwnerRequest(self._myPPass)
        if self.__gi is not None:
            self.__gi.CleanUpByOwnerRequest(self._myPPass)
        if self.__mi is not None:
            self.__mi.CleanUpByOwnerRequest(self._myPPass)
        if self.__sup is not None:
            self.__sup.CleanUpByOwnerRequest(self._myPPass)
        if self.__kpi is not None:
            self.__kpi.CleanUp()
        if self.__sdh is not None:
            self.__sdh.CleanUp()
        if self.__xh is not None:
            self.__m   = None
            self.__s   = None
            self.__dm  = None
            self.__gi  = None
            self.__la  = None
            self.__ld  = None
            self.__mi  = None
            self.__ts  = None
            self.__pi  = None
            self.__xh  = None
            self.__kpi = None
            self.__sdh = None
            self.__sup = None
            vlogif._PrintVSummary(bPrint_=True)

    @property
    def __lcState(self) -> _ILcState:
        return None if self.__gi is None else self.__gi._GGetLcState(bypassApiLock_=True)

    @property
    def __curLcScope(self) -> _ELcScope:
        return None if self.__dm is None else self.__dm.lcScope

    @staticmethod
    def __DoCreateStartupPolicy(ppass_ : int) -> _FwStartupPolicy:
        _STARTUP_FAILURE_ERR_MSG = 'Encountered severe error while preparing for startup.'

        _dbCreateSt = _FwTDbEngine.GetCreateStatus()
        if not _dbCreateSt.isTDBIdle:
            if not _dbCreateSt.isTDBCreated:
                _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_096, errMsg_=_STARTUP_FAILURE_ERR_MSG)
                return None

        _lcKPI = _KpiLogBook._CreateStartupKPI(_ELcKpiID.eFwStartRequest)
        if not _lcKPI.isValid:
            _lcKPI.CleanUp()
            _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_097, errMsg_=_STARTUP_FAILURE_ERR_MSG)
            return None

        res = _FwStartupPolicy(ppass_)
        if not res.isValid:
            res.CleanUpByOwnerRequest(ppass_)
            res = None
            _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_098, errMsg_=_STARTUP_FAILURE_ERR_MSG)
        elif _dbCreateSt.isTDBIdle:
            _FwTDbEngine._CreateDB(res.isPackageDist)

            _dbCreateSt = _FwTDbEngine.GetCreateStatus()
            if not _dbCreateSt.isTDBCreated:
                res.CleanUpByOwnerRequest(ppass_)
                res = None
                _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_099, errMsg_=_STARTUP_FAILURE_ERR_MSG)
        if res is not None:
            _dbFirstFetchTS = None
            _dbCreateTS     = None
            _dbFirstFetchTS, _dbCreateTS = _FwTDbEngine._GetDBTimestamps()
            _lcKPI.AddKPI(_ELcKpiID.eTextDBFirstFetch, usTimeTicksKPI_=_dbFirstFetchTS)
            _lcKPI.AddKPI(_ELcKpiID.eTextDBCreate, usTimeTicksKPI_=_dbCreateTS)
        return res

    @staticmethod
    def __DoCreateLcMgr(startupPolicy_ : _FwStartupPolicy, startOptions_ : list):
        if _LcManager.__sgltn is not None:
            return None

        _lcKPI = _KpiLogBook._GetStartupKPI()

        if not (isinstance(startupPolicy_, _FwStartupPolicy) and startupPolicy_.isValid):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00365)
            return None

        if not (isinstance(_lcKPI, _KpiLogBook) and _lcKPI.isValid):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00366)
            return None

        _kpiTD = _lcKPI.GetKpiTimeDelta(_ELcKpiID.eTextDBCreate)
        if _kpiTD is not None:
            vlogif._LogKPI(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_004).format(_kpiTD.timeParts))
            _kpiTD.CleanUp()

        _ppass = startupPolicy_._myPPass

        _LcFailure._ClearInstance()

        _eExecHist = _LcFailure._GetLcXStateHistory()
        if _eExecHist is not None:
            _eExecHist.CleanUpByOwnerRequest(_eExecHist._myPPass)
            _eExecHist = None

        _eExecHist = _LcXStateHistory(_ppass)
        if not _eExecHist.IsLcExecutionStateSet(_ELcXState.ePreConfigPhase):
            _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_104, errMsg_=_EFwTextID.eLogMsg_LcManager_TID_038)
            _eExecHist.CleanUpByOwnerRequest(_ppass)
            return None
        _LcFailure._SetLcXStateHistory(_eExecHist)

        _lcmgr = _LcManager(_ppass, startupPolicy_, startOptions_)

        if not _eExecHist.isFailureFree:
            _lcmgr.CleanUpByOwnerRequest(_ppass)
            return None

        _lcMgrSetupRunner = _LcManager._LcMgrSetupRunner(_lcmgr, _ppass, startOptions_)
        _bLcGuardStarted  = _lcmgr.__StartLcGuard(_lcMgrSetupRunner)

        _bAsyncSetupOK = _bLcGuardStarted and _LcFailure.IsSetupPhasePassed()
        _bAsyncSetupOK = _bAsyncSetupOK   and _lcMgrSetupRunner.isLcMgrSetupRunnerSucceeded
        _bAsyncSetupOK = _bAsyncSetupOK   and _eExecHist.isFailureFree
        _bAsyncSetupOK = _bAsyncSetupOK   and _eExecHist.hasPassedSetupPhase
        _bAsyncSetupOK = _bAsyncSetupOK   and _eExecHist.hasReachedRuntimePhase

        _bStopFW = False

        _lcmgr.__SetUpLRD(_bAsyncSetupOK)

        if not _bAsyncSetupOK:
            _bStopFW = _bLcGuardStarted

        elif not _lcmgr.__CheckStartMainXT():
            _bStopFW = True

        res = _lcmgr.__DetermineAsyncStartupResult(_bAsyncSetupOK)
        if res is None:
            _bStopFW = True

        if _bStopFW:
            _lcmgr.__StopFW(bInternalRequest_=True)
            if not _lcmgr.__sdh._isJoinRequestSubmitted:
                _lcmgr.__JoinFW(bInternalRequest_=True)
        return res

    @staticmethod
    def __GetMainXTask():
        return _FwSubsysShare._GetMainXTask()

    @staticmethod
    def __GetLogRDService(bEnablePM_ =False):
        res = None
        if _ssshare._IsLogRDActiveServiceRequired():
            _sid = _EFwsID.eFwsLogRD
            if _AbsFwService.IsDefinedFws(_sid):
                res = _AbsFwService._GetFwsInstance(_sid)
                if (res is not None) and bEnablePM_:
                    res._EnablePM()
        return res

    def __SetLcOpState( self, lcCID_ : _ELcCompID, bStartStopFlag_ : bool, atask_ : _AbsFwTask =None) -> bool:
        if self.__gi is None:
            res = False
        else:
            res = self.__gi._GSetLcOperationalState(lcCID_, bStartStopFlag_, atask_=atask_)
        return res

    def __BoostFW(self, bReinjCurScope_: bool =False) -> bool:
        self.__kpi.AddKPI(_ELcKpiID.eLcConfigEnd)

        self.__kpi.AddKPI(_ELcKpiID.eLcBoostStart)
        self.__xh._AddExecutionState(_ELcXState.eSemiBoostPhase, self)

        res = self.__BoostSemiIPC(bReinjCurScope_=bReinjCurScope_)
        res = res and _LcFailure.IsLcErrorFree()
        res = res and self.__xh.IsLcExecutionStateSet(_ELcXState.eSemiBoostPhase)

        if res:
            self.__xh._AddExecutionState(_ELcXState.eFullBoostPhase, self)

            res = self.__BoostFullIPC()
            res = res and _LcFailure.IsLcErrorFree()
            res = res and self.__xh.IsLcExecutionStateSet(_ELcXState.eFullBoostPhase)

        if res:
            res = self.__curLcScope == self.__ts
            if not res:
                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_007).format(self.__ts.compactName, self.__curLcScope.compactName)
                _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_050, _errMsg)
            else:
                res = self.__pi._PxyStartFwMain()
                res = res and _LcFailure.IsLcErrorFree()

        if not res:
            if _LcFailure.IsLcErrorFree():
                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_008).format(self.__ts.compactName, self.__curLcScope.compactName)
                _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_051, _errMsg)
        else:
            self.__gi._GSetLcMonitorImpl(self.__mi)
            _TTaskMgr()._SetLcMonitorImpl(self.__mi)
        return res

    def __BoostSemiIPC(self, bReinjCurScope_ : bool =False) -> bool:
        _NO_SUPPORT_FOR_INTERMEDIATE_SCOPES_AT_RUNTIME = True
        if _NO_SUPPORT_FOR_INTERMEDIATE_SCOPES_AT_RUNTIME:
            if bReinjCurScope_:
                bReinjCurScope_ = False

        _eFS = _LcConfig.GetTargetScope()

        _bBadUse = False
        _bBadUse = _bBadUse or (_eFS.lcTransitionalOrder < _ELcScope.eSemiIPC.value)
        _bBadUse = _bBadUse or not self.__curLcScope.isPreIPC
        _bBadUse = _bBadUse or not self.__lcState.isLcStarted
        _bBadUse = _bBadUse or self.__lcState.hasLcAnyFailureState
        if _bBadUse:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00367)

            _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_052)
            return False

        if bReinjCurScope_:
            if not self.__UpdateScope(self.__curLcScope, self.__curLcScope, bForceReinject_=True):
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00368)
                return False

        if self.__ts.lcTransitionalOrder < _ELcScope.eSemiIPC.value:
            self.__ts = _ELcScope.eSemiIPC

        _bFinalSemiIPC = _eFS.isSemiIPC

        res = self.__UpdateScope(self.__curLcScope, self.__ts, bFinalize_=_bFinalSemiIPC)
        if res:
            res = res and self.__curLcScope.isSemiIPC
            res = res and self.__lcState.isLcStarted
            res = res and self.__lcState.isTaskManagerStarted
            if not res:
                _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_053)
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00369)
        if res:
            if _bFinalSemiIPC:
                self.__CreateLcProxy()

                res = res and _LcFailure.IsLcErrorFree()
                res = res and self.__pi is not None
                res = res and self.__lcState.isLcStarted
                res = res and self.__lcState.isTaskManagerStarted
                res = res and self.__lcState.isFwMainStarted
                if not res:
                    if _LcFailure.IsLcErrorFree():
                        _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_054)
                        vlogif._LogOEC(True, _EFwErrorCode.VFE_00370)
        return res

    def __BoostFullIPC(self) -> bool:
        _eFS = _LcConfig.GetTargetScope()

        _bBadUse = False    or _LcFailure.IsLcNotErrorFree()
        _bBadUse = _bBadUse or not self.__curLcScope.isSemiIPC
        _bBadUse = _bBadUse or not self.__lcState.isLcStarted
        _bBadUse = _bBadUse or not self.__lcState.isTaskManagerStarted
        _bBadUse = _bBadUse or self.__lcState.hasLcAnyFailureState
        if _bBadUse:
            if _LcFailure.IsLcErrorFree():
                _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_056)
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00371)
            return False

        if self.__ts != _eFS:
            self.__ts = _eFS

        res = self.__UpdateScope(self.__curLcScope, self.__ts)
        res = res and _LcFailure.IsLcErrorFree()
        res = res and self.__curLcScope.isFullIPC
        res = res and self.__lcState.isLcStarted
        res = res and self.__lcState.isTaskManagerStarted

        if not res:
            if _LcFailure.IsLcErrorFree():
                _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_057)
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00372)
            return False
        self.__CreateLcProxy()

        res = res and _LcFailure.IsLcErrorFree()
        res = res and self.__pi is not None
        res = res and self.__lcState.isLcStarted
        res = res and self.__lcState.isTaskManagerStarted
        res = res and self.__lcState.isFwMainStarted

        if not res:
            if _LcFailure.IsLcErrorFree():
                _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_058)

            if self.__pi is not None:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00373)
        return res

    def __StopFW(self, bInternalRequest_ =False, bAutoStop_ =False, bForceStop_ =False) -> bool:
        if (_LcManager.__sgltn is None) or (self.__gi is None) or (self.__mi is None):
            return _LcFailure.IsLcErrorFree()

        with self.__ld:
            if bInternalRequest_:
                if self.__sdh._isStopRequestSubmitted:
                    if self.__sdh._isInternalStopRequestSubmitted:
                        vlogif._LogOEC(True, _EFwErrorCode.VFE_00563)
                else:
                    self.__sdh._SetStopRequest(bInternal_=True)

            else:
                if self.__sdh._isStopRequestSubmitted:
                    return True

                self.__sdh._SetStopRequest()
                self.__xh._AddExecutionState(_ELcXState.eStopPhase, self)

                if bForceStop_:
                    logif._LogErrorEC(_EFwErrorCode.UE_00217, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_062))
                    _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_059)
                elif bAutoStop_:
                    if _ssshare._GetRteConfig()._isAutoStopEnabledByDefault:
                        _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_060)
                    else:
                        _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_051)
                else:
                    _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_012)
                logif._LogKPI(_msg)

                self.__mi._EnableCoordinatedShutdown()
                _LcManager.__GetLogRDService(bEnablePM_=True)
                return True

        vlogif._LogNewline()
        self.__xh._AddExecutionState(_ELcXState.eStopPhase, self)

        if self.__mi.curShutdownRequest is None:
            self.__pi._PxyProcessShutdownRequest(_ELcSDRequest.ePreShutdown, bPrvRequestReply_=False)
        return True

    def __JoinFW(self, bInternalRequest_ =False) -> bool:
        if (_LcManager.__sgltn is None) or (self.__gi is None) or (self.__mi is None):
            return _LcFailure.IsLcErrorFree()

        _bPendingSR = False

        with self.__la:
            if self.__mi._isCurrentThreadAttachedToFW:
                logif._LogErrorEC(_EFwErrorCode.UE_00103, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_010).format(_TaskUtil.GetCurPyThread().name))
                return False

            with self.__ld:
                if self.__sdh._isJoinRequestSubmitted:
                    if bInternalRequest_:
                        vlogif._LogOEC(True, _EFwErrorCode.VFE_00561)
                    else:
                        logif._LogErrorEC(_EFwErrorCode.UE_00209, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_037))
                    return False

                self.__sdh._SetJoinRequest(bInternal_=bInternalRequest_)
                if not bInternalRequest_:
                    logif._LogKPI(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_043))

                if not self.__sdh._isStopRequestSubmitted:
                    if bInternalRequest_:
                        vlogif._LogOEC(True, _EFwErrorCode.VFE_00562)
                        self.__StopFW(bInternalRequest_=True)
                    else:
                        _bPendingSR = True

        if _bPendingSR:
            self.__EnterPendingSR()

        logif._LogInfo(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_011))
        try:
            self.__xh._AddExecutionState(_ELcXState.eJoinPhase, self)
            _TaskUtil.SleepMS(200)
            self.__gi._GJoin()

            self.__xh._AddExecutionState(_ELcXState.eJoinPassed, self)
        except KeyboardInterrupt:
            _midPart = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_066)
            _msg     = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_KeyboardInterrupt).format(_LcManager.__MSG_PREFIX, _midPart)
            _ssshare._BookKBI(_msg, bVLog_=True)
        except BaseException as _xcp:
            _msg  = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_075).format(str(_xcp))
            vlogif._LogUrgentWarning(_msg)
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00965)

        if not self.__lcState.isLcStopped:
            if not self.__lcState.isLcFailed:
                self.__SetLcOpState(_ELcCompID.eLcMgr, False)

        self.CleanUpByOwnerRequest(self._myPPass)

        _LcFailure._PrintLcResult()
        return _LcFailure.IsLcErrorFree()

    def __SetUp(self, ppass_: int, startOptions_: list, mainXT_ =None):
        if _LcFailure.IsLcNotErrorFree():
            _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_059)
            return False

        if not self.__xh.IsLcExecutionStateSet(_ELcXState.ePreConfigPhase):
            _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_060)
            return False

        self.__xh._AddExecutionState(_ELcXState.eConfigPhase, self)

        _tgtScope = _LcConfig.GetTargetScope()
        _lcdm = _LcDepManager(ppass_, self.__sup, self.__gi, startOptions_)

        res = True
        res = res and _LcFailure.IsLcErrorFree()
        res = res and (_lcdm.lcScope is not None)
        res = res and _lcdm.lcScope.isPreIPC
        res = res and self.__SetLcOpState(_ELcCompID.eLcMgr, True)

        if not res:
            if _LcFailure.IsLcErrorFree():
                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_013).format(_FwTDbEngine.GetText(_EFwTextID.eMisc_Async))
                _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_102, errMsg_=_errMsg)
            _lcdm.CleanUpByOwnerRequest(ppass_)
            return False

        _rclTSMS = _lcdm.subsystemConfigSupervisor.subsystemConfigIPC.lcGuardRunCycleLoopTimespanMS
        self.__gi._GUpdateRunCycleLoopTimespanMS(_rclTSMS)

        self.__m  = mainXT_
        self.__dm = _lcdm
        self.__ts = _ELcScope(_tgtScope.value)

        if self.__ts.isPreIPC:
            self.__xh._AddExecutionState(_ELcXState.eCustomSetupPhase, self)

            self.__xh._AddExecutionState(_ELcXState.eSetupPassed, self)
            self.__xh._AddExecutionState(_ELcXState.eRuntimePhase, self)
            return True

        res = True
        res = res and self.__BoostFW()                 
        res = res and _LcFailure.IsLcErrorFree()       
        res = res and self.__dm is not None        
        res = res and self.__gi is not None       
        res = res and self.__gi.isLcCoreOperable  

        if not res:
            if _LcFailure.IsLcErrorFree():
                _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_061)

        else:
            self.__kpi.AddKPI(_ELcKpiID.eLcBoostEnd)
            self.__kpi.AddKPI(_ELcKpiID.eLcCustomSetupStart)

            self.__xh._AddExecutionState(_ELcXState.eCustomSetupPhase, self)
            res = self.__pi._PxyFinalizeSetup()
            res = res and _LcFailure.IsLcErrorFree()

            if not res:
                if _LcFailure.IsLcErrorFree():
                    _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_062)
            else:
                res = self.__UpdateScope(self.__curLcScope, self.__ts, bFinalize_=True)

        if not res:
            if _LcFailure.IsLcErrorFree():
                _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_109, errMsg_=_EFwTextID.eLogMsg_LcManager_TID_017)
        else:
            self.__kpi.AddKPI(_ELcKpiID.eLcCustomSetupEnd)
            self.__xh._AddExecutionState(_ELcXState.eSetupPassed, self)
            self.__xh._AddExecutionState(_ELcXState.eRuntimePhase, self)
            if not self.__sup.isReleaseModeEnabled:
                self.__PrintLcKPI()

            _kpiTD = self.__kpi.GetKpiTimeDelta(_ELcKpiID.eTextDBCreate)
            logif._LogKPI(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_004).format(_kpiTD.timeParts))
            _kpiTD.CleanUp()

            _kpiTD = self.__kpi.GetKpiTimeDelta(_ELcKpiID.eLcCustomSetupEnd, _ELcKpiID.eLcConfigStart)
            logif._LogKPI(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_018).format(_kpiTD.timeParts))
            _kpiTD.CleanUp()

        _vffe = vlogif._GetFirstFatalError()
        if not res:
            if _vffe is not None:
                if _LcFailure.IsLcErrorFree():
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00374)
        elif _vffe is not None:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00375)
        return res

    def __SetUpLRD(self, bSetuOK_ : bool):
        _bHL  = False if self.__dm is None else self.__dm.fwConfig.fwStartupConfig._isLogHighlightingEnabled
        _lrds = None
        if bSetuOK_:
            _lrds = _LcManager.__GetLogRDService()
        _LogRDAgent._GetInstance()._ADeactivate(_ssshare._IsLogRDConsoleSinkEnabled(), _bHL, _lrds)

    def __PrintLcKPI(self, bForce_ =False):
        if (self.__kpi is None) or not self.__kpi.isValid:
            return
        if (self.__sup is None) or not self.__sup.isValid:
            return
        if self.__sup.isPackageDist and not bForce_:
            return
        _myTxt = self.__kpi.ToString()
        if len(_myTxt) > 0:
            logif._LogKPI(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_014).format(_myTxt))

    def __UpdateScope(self, srcScope_ : _ELcScope, dstScope_ : _ELcScope, bForceReinject_ =False, bFinalize_ =False):
        if _LcFailure.IsLcNotErrorFree() and not _LcFailure.IsConfigPhasePassed():
            return True

        res= True

        if srcScope_ == dstScope_:
            if not (bForceReinject_ or bFinalize_):
                pass
            elif bForceReinject_:
                _ures = self.__dm.UpdateLcScope(dstScope_, bForceReinject_=True)
                res = _ures.isOK
            else:
                _ures = self.__dm.UpdateLcScope(dstScope_, bFinalize_=True)
                res = _ures.isOK
        else:
            _bTMgrAvailable = None
            if dstScope_.lcTransitionalOrder < srcScope_.lcTransitionalOrder:
                if srcScope_ == _ELcScope.eSemiIPC:
                    _bTMgrAvailable = False
                _nextScopeVal = srcScope_.value - 1
            else:
                _nextScopeVal = srcScope_.value + 1
                if _nextScopeVal == _ELcScope.eSemiIPC.value:
                    _bTMgrAvailable = True

            if _bTMgrAvailable is not None:
                if not _bTMgrAvailable:
                    if not self.__lcState.isTaskManagerFailed:
                        self.__SetLcOpState(_ELcCompID.eTMgr, False)

            _tgtScope = _ELcScope(_nextScopeVal)
            _ures = self.__dm.UpdateLcScope(_tgtScope)
            res = _ures.isOK
            if res and (_bTMgrAvailable is not None):
                if _bTMgrAvailable:
                    res = _TaskMgr() is not None
                    if not res:
                        vlogif._LogOEC(True, _EFwErrorCode.VFE_00376)
                    elif not self.__SetLcOpState(_ELcCompID.eTMgr, True):
                        res = False
                        vlogif._LogOEC(True, _EFwErrorCode.VFE_00377)
        if not res:
            if _LcFailure.IsLcErrorFree():
                if not _LcFailure.IsSetupPhasePassed():
                    _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_063)
        return res

    def __CreateLcProxy(self):
        _lcMon  = _LcMonitorImpl(self._myPPass, self.__xh)
        _bMonOK = _lcMon.isValid and not _lcMon.isDummyMonitor

        if not _bMonOK:
            _lcMon.CleanUpByOwnerRequest(self._myPPass)
            _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_070, errMsg_=_EFwTextID.eLogMsg_LcManager_TID_019)
            return

        self.__mi = _lcMon
        _mainXT = None
        _lcPxyImpl = _LcProxy(self._myPPass, self.__curLcScope, self.__gi, self.__mi, self.__dm.fwConfig.fwStartupConfig, _mainXT)

        if _lcPxyImpl._PxyGetTaskMgr() is None:
            _lcPxyImpl.CleanUpByOwnerRequest(self._myPPass)
            _lcPxyImpl = None

            if self.__lcState.isTaskManagerStarted:
                self.__SetLcOpState(_ELcCompID.eTMgr, False)

            if _LcFailure.IsLcErrorFree():
                _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_071, errMsg_=_EFwTextID.eLogMsg_LcManager_TID_020)

        elif not self.__SetLcOpState(_ELcCompID.eFwMain, True):
            _lcPxyImpl.CleanUpByOwnerRequest(self._myPPass)
            _lcPxyImpl = None

            if _LcFailure.IsLcErrorFree():
                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_021).format(_ELcCompID.eFwMain.compactName)
                _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_001, errMsg_=_errMsg)

        if _lcPxyImpl is None:
            self.__mi.CleanUpByOwnerRequest(self._myPPass)
            self.__mi = None
        else:
            self.__pi = _lcPxyImpl

    def __StartLcGuard(self, lcMgrSetupRunner_):
        self.__s = _PySemaphore(1)
        self.__s.acquire()

        if not self.__gi._GStart(self.__s, lcMgrSetupRunner_):
            res = False
            if _LcFailure.IsLcErrorFree():
                _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_002, errMsg_=_EFwTextID.eLogMsg_LcManager_TID_022)
        else:
            self.__s.acquire()

            if not self.__gi._isGRunning:
                res = False
                if _LcFailure.IsLcErrorFree():
                    _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_065)
            else:
                res = True
        return res

    def __EnterPendingSR(self):
        _rteCfg = _ssshare._GetRteConfig()

        _bTM_CFG_ENABLED  = _rteCfg._isTerminalModeEnabled
        _bFAS_CFG_ENABLED = _rteCfg._isForcedAutoStopEnabled
        _bAS_CFG_DISABLED = False if _bFAS_CFG_ENABLED else not _rteCfg._isAutoStopEnabled

        _ii       = 0
        _bXcp     = False
        _lcKPI    = _KpiLogBook._GetStartupKPI()
        _kpiStart = None

        while True:
            if _bXcp:
                break
            try:
                _tskMgr = _TTaskMgr()
                if _tskMgr is None:
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00564)
                    break

                _bWait      = False
                _lstXT, _dc = _tskMgr._GetXTasks(bRunningOnly_=True, bJoinableOnly_=True)
                _numXT      = len(_lstXT)
                _firstIter  = _ii == 0

                if _bTM_CFG_ENABLED or _bAS_CFG_DISABLED:
                    _bWait = True

                    if _firstIter:
                        _midPart = None
                        if _numXT > 0:
                            _lstXT = [str(ee) for ee in _lstXT]
                            _midPart = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_027).join(_lstXT)

                        if _bTM_CFG_ENABLED:
                            _kpiStart = _ELcKpiID.eTerminalModeStart

                            if _numXT > 0:
                                logif._LogKPI(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_055).format(_numXT, _midPart))
                            else:
                                logif._LogKPI(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_054))
                        else:
                            _kpiStart = _ELcKpiID.eAutoStopDisabledStart

                            if _numXT > 0:
                                logif._LogKPI(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_050).format(_midPart))
                            else:
                                logif._LogKPI(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_052))
                else:
                    _bWait = not (_bFAS_CFG_ENABLED or (_numXT<1))
                    if _bWait:
                        if _firstIter:
                            _kpiStart = _ELcKpiID.eAutoStopEnabledStart

                            _lstXT = [str(ee) for ee in _lstXT]
                            _midPart = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_027).join(_lstXT)
                            if _rteCfg._isAutoStopEnabledByDefault:
                                logif._LogKPI(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_061).format(_numXT, _midPart))
                            else:
                                logif._LogKPI(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_053).format(_numXT, _midPart))
                _ii += 1

                if _kpiStart is not None:
                    _lcKPI.AddKPI(_kpiStart)

                if _bWait:
                    _TaskUtil.SleepMS(100)
                elif not _bAS_CFG_DISABLED:
                    _kpiStart = _ELcKpiID.eAutoStopEnabledStart
                    if _lcKPI.IsAddedKPI(_kpiStart):
                        _kpiEnd = _ELcKpiID.eAutoStopEnabledEnd
                        _lcKPI.AddKPI(_ELcKpiID.eAutoStopEnabledEnd)
                        _kpiTD = self.__kpi.GetKpiTimeDelta(_kpiEnd, _kpiStart)
                        logif._LogKPI(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_056).format(_kpiTD.timeParts))
                        _kpiTD.CleanUp()

                    if _bFAS_CFG_ENABLED:
                        _bAutoStop, _bForceStop = False, True
                    else:
                        _bAutoStop, _bForceStop = True, False
                    self.__StopFW(bAutoStop_=_bAutoStop, bForceStop_=_bForceStop)
                    break

                with self.__ld:
                    if self.__sdh._isStopRequestSubmitted:
                        _kpiStart = None
                        _lstKpiID = [ _ELcKpiID.eTerminalModeStart , _ELcKpiID.eAutoStopDisabledStart , _ELcKpiID.eAutoStopEnabledStart ]
                        for ee in _lstKpiID:
                           if _lcKPI.IsAddedKPI(ee):
                                _kpiStart = ee
                                break

                        if _kpiStart is not None:
                            _kpiEnd = _ELcKpiID(_kpiStart.value+1)
                            _lcKPI.AddKPI(_kpiEnd)
                            _kpiTD = self.__kpi.GetKpiTimeDelta(_kpiEnd, _kpiStart)

                            if _bTM_CFG_ENABLED or _bAS_CFG_DISABLED:
                                if _bTM_CFG_ENABLED:
                                    logif._LogKPI(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_057).format(_kpiTD.timeParts))
                                else:
                                    logif._LogKPI(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_058).format(_kpiTD.timeParts))
                            else:
                                logif._LogKPI(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_056).format(_kpiTD.timeParts))
                            _kpiTD.CleanUp()
                        break
            except KeyboardInterrupt:
                _bXcp = True
                _midPart = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_068)
                _msg = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_KeyboardInterrupt).format(_LcManager.__MSG_PREFIX, _midPart)
                _ssshare._BookKBI(_msg, bVLog_=True)
            except BaseException as _xcp:
                _bXcp = True
                _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_076).format(str(_xcp))
                vlogif._LogUrgentWarning(_msg)
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00963)
            finally:
                if _bXcp:
                    if _bFAS_CFG_ENABLED:
                        _bAutoStop, _bForceStop = False, True
                    else:
                        _bAutoStop, _bForceStop = True, False
                    self.__StopFW(bAutoStop_=_bAutoStop, bForceStop_=_bForceStop)
        _LcManager.__GetLogRDService(bEnablePM_=True)

    def __JoinXUnits(self, bTasks_ : bool, xunits_: Union[int, List[int], None] =None, timeout_: Union[int, float] =None) -> Tuple[int, Union[List[int], None]]:
        _errRes = 0, None

        if (_LcManager.__sgltn is None) or (self.__ts is None) or (self.__mi is None):
            return _errRes
        if self.__mi.isLcShutdownEnabled:
            return _errRes
        if (not bTasks_) and _ssshare._WarnOnDisabledSubsysMP(annexID_=_EFwTextID.eMisc_Shared_Disabled_Subsys_MP):
            return _errRes

        if timeout_ is not None:
            timeout_ = _Timeout.TimespanToTimeout(timeout_)
            if timeout_ is None:
                return _errRes

        _midPart = _EFwTextID.eMisc_Tasks if bTasks_ else _EFwTextID.eMisc_Processes
        _midPart = _FwTDbEngine.GetText(_midPart)

        _xunits = [] if xunits_ is None else list(xunits_)
        if not isinstance(_xunits, list):
            logif._LogErrorEC(_EFwErrorCode.UE_00242, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_063).format(_midPart, type(_xunits).__name__))
            return _errRes

        _mxt = None
        _tmp = []

        for _id in _xunits:
            _idVal = _id.value if isinstance(_id, IntEnum) else _id
            if not (isinstance(_idVal, int) and (_idVal>0)):
                logif._LogErrorEC(_EFwErrorCode.UE_00242, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_063).format(_midPart, str(_id)))
                return _errRes

            if bTasks_ and isinstance(_id, EXmsgPredefinedID) and (_id == EXmsgPredefinedID.MainTask):
                _mxt = EXmsgPredefinedID.MainTask
            else:
                _tmp.append(_idVal)

        _xunits = _tmp
        if _mxt is not None:
            _mxt = _FwSubsysShare._GetMainXTask()
            if _mxt is not None:
                _xunits.append(_mxt.taskUID)
            _mxt = None

        _lstXU = None

        if not bTasks_:
            _pm = _AbsFwService._GetFwsInstance(_EFwsID.eFwsProcMgr)
            if (_pm is None) or not _pm.isRunning:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00960)
                return _errRes

            _lstXU = _pm._GetJoinableList(lstPIDs_=_xunits if len(_xunits) else None)
            _lstXU = _lstXU if (isinstance(_lstXU, list) and len(_lstXU)) else None
            if _lstXU is None:
                _numJ = 0 if _xunits is None else len(_xunits)
                return _numJ, None
        else:
            with self.__la:
                _cxtUID   = None
                _cxt, _dc = self._GetCurXTask(bRcTask_=False)
                if _cxt is not None:
                    _cxtUID = _cxt.taskUID
                    if _cxtUID in _xunits:
                        if len(_xunits) < 2:
                            logif._LogErrorEC(_EFwErrorCode.UE_00244, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_064).format(_cxtUID))
                            return _errRes

                        _xunits.remove(_cxtUID)
                        logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_065).format(_cxtUID))

                if len(_xunits) < 1:
                    _xunits = None

                _tskMgr = _TTaskMgr()
                if _tskMgr is None:
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00959)
                    return _errRes

                _lstXT, _lstUnj = _tskMgr._GetXTasks(bRunningOnly_=False, bJoinableOnly_=True, bUID_=False, lstUIDs_=_xunits)
                if _lstUnj is not None:
                    if not ((len(_lstUnj)==1) and (_cxtUID is not None) and (_cxtUID in _lstUnj)):
                        _midPart = [str(_id) for _id in _xunits]
                        _midPart = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_027).join(_midPart)
                        logif._LogErrorEC(_EFwErrorCode.UE_00245, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_070).format(_midPart))
                        return 0, _lstUnj

                if len(_lstXT) < 1:
                    _numJ = 0 if _xunits is None else len(_xunits)
                    return _numJ, None
                _lstXU = _lstXT

        _numXU       = len(_lstXU)
        _timeSpanMS  = 100
        _totalTimeMS = 0

        _MAX_TIME_MS = 0 if (timeout_ is None) else timeout_.toMSec

        _bXcp = False

        while True:
            if _bXcp:
                break

            try:
                _TaskUtil.SleepMS(_timeSpanMS)

                _bBreak = False
                _totalTimeMS += _timeSpanMS

                if not bTasks_:
                    _lstXU = [_xu for _xu in _lstXU if (_xu._isAttachedToFW and not _xu._isTerminated)]
                else:
                    _lstXU = [_xu for _xu in _lstXU if not (_xu.isDetachedFromFW or _xu.isTerminated)]

                if len(_lstXU) < 1:
                    _bBreak = True
                elif (_MAX_TIME_MS > 0) and (_totalTimeMS >= _MAX_TIME_MS):
                    _bBreak = True
                elif (self.__ts is None) or (self.__mi is None):
                    _bBreak = True
                elif self.__mi.isLcShutdownEnabled:
                    _bBreak = True
                else:
                    with self.__ld:
                        _bBreak = self.__sdh._isStopRequestSubmitted
                if _bBreak:
                    break
            except KeyboardInterrupt:
                _bXcp = True
                _midPart = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_069).format(_midPart)
                _msg     = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_KeyboardInterrupt).format(_LcManager.__MSG_PREFIX, _midPart)
                _ssshare._BookKBI(_msg, bVLog_=True)
            except BaseException as _xcp:
                _bXcp = True
                _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_077).format(_midPart, str(_xcp))
                vlogif._LogUrgentWarning(_msg)
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00966)

        _lstUnj = _lstXU if not bTasks_ else [ _xu.taskUID for _xu in _lstXU ]
        if len(_lstUnj) < 1:
            _lstUnj = None

        _numJ = _numXU-len(_lstXU)
        return _numJ, _lstUnj

    def __TerminateProcesses(self, procs_: Union[int, List[int], None] =None) -> int:
        if (_LcManager.__sgltn is None) or (self.__ts is None) or (self.__mi is None):
            return 0
        if self.__mi.isLcShutdownEnabled:
            return 0
        if _ssshare._WarnOnDisabledSubsysMP(annexID_=_EFwTextID.eMisc_Shared_Disabled_Subsys_MP):
            return 0

        _procs = [] if procs_ is None else list(procs_)

        for _id in _procs:
            if not (isinstance(_id, int) and (_id>0)):
                logif._LogErrorEC(_EFwErrorCode.UE_00256, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_072).format(str(_id)))
                return -1

        _pm = _AbsFwService._GetFwsInstance(_EFwsID.eFwsProcMgr)
        if (_pm is None) or not _pm.isRunning:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00971)
            return -1

        _procs = _pm._GetJoinableList(lstPIDs_=_procs if len(_procs) else None)
        if not (isinstance(_procs, list) and len(_procs)):
            return 0

        res = 0
        for _pp in _procs:
            if _pp._Terminate():
                res += 1

        if res < 1:
            return 0

        _num   = len(_procs)
        _procs = [ str(_pp._xprocessPID) for _pp in _procs ]
        _procs = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_027).join(_procs)
        logif._LogInfo(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_074).format(_num, _procs))
        return res

    def __FinalJoin(self, uidMainXT_ : int =None):
        _srt = self.__pi._PxyJoinFwMain(mainXtUID_=uidMainXT_)
        if _srt is None:
            return

        _NUM = len(_srt)
        _mxtTI = None
        for _ii in range(_NUM):
            _ti = _srt[_ii]

            if not _ti.isValid:
                _srt[_ii] = None
                continue
            if _ti.isEnclosingPyThread and _TaskUtil.IsMainPyThread(_ti.dHThrd):
                _mxtTI = _ti
                _srt[_ii] = None
                continue

            _ti.JoinTask()
            _ti.CleanUp()
            _srt[_ii] = None
        _srt.clear()

        if (_mxtTI is None) or not (_mxtTI.isValid and _mxtTI.isStarted):
            return

        _WARN_TIME_MS = 2 * _LcMonitorImpl.GetPerShutdownRequestWaitTimespanMS()
        _timeSpanMS   = 20
        _totalTimeMS  = 0

        _wng = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_044).format(_LcManager.__MSG_PREFIX, uidMainXT_)

        try:
            while True:
                if not _mxtTI.isValid:
                    break
                if _mxtTI.isTerminated:
                    break

                if (_totalTimeMS>=_WARN_TIME_MS) and ((_totalTimeMS%_WARN_TIME_MS) == 0):
                    vlogif._LogUrgentWarning(_wng)
                _TaskUtil.SleepMS(_timeSpanMS)
                _totalTimeMS += _timeSpanMS

        except KeyboardInterrupt:
            _midPart = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_067).format(uidMainXT_)
            _msg     = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_KeyboardInterrupt).format(_LcManager.__MSG_PREFIX, _midPart)
            _ssshare._BookKBI(_msg, bVLog_=True)
        except BaseException as _xcp:
            _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_078).format(uidMainXT_, str(_xcp))
            vlogif._LogUrgentWarning(_msg)
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00967)
        _mxtTI.CleanUp()

    def __CheckStartMainXT(self, bSkipAutoStartMainXT_ : bool =True) -> bool:
        if not (self.__xh.hasPassedSetupPhase and self.__xh.hasReachedRuntimePhase):
            return False

        _mainXT = self.__m
        if _mainXT is None:
            self._FwCNPublishFwApiConnector()
            return True
        if bSkipAutoStartMainXT_:
            self._FwCNPublishFwApiConnector()
            return True
        return False

    def __DetermineAsyncStartupResult(self, bAsyncStartupOK_ : bool, bSkipAutoStartMainXT_ : bool =True):
        res = None
        _mainXT = self.__m

        if not bAsyncStartupOK_:
            if self.__xh.isFailureFree:
                if self.__xh.hasPassedSetupPhase and self.__xh.hasReachedRuntimePhase:
                    if _mainXT is None:
                        _bOK = not self.__xh.hasPassedMxtStartPhase
                    else:
                        _bOK = not (bSkipAutoStartMainXT_ or self.__xh.hasPassedMxtStartPhase)
                else:
                    _bOK = False

                if not _bOK:
                    if self.__xh.hasReachedRuntimePhase:
                        self.__xh._RemoveExecutionState(_ELcXState.eRuntimePhase, self)
                    if self.__xh.hasPassedMxtStartPhase:
                        self.__xh._RemoveExecutionState(_ELcXState.eMxtStartPassed, self)
                    if self.__xh.hasPassedSetupPhase:
                        self.__xh._RemoveExecutionState(_ELcXState.eSetupPassed, self)

                    _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_040).format(self.__xh)
                    _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_003, errMsg_=_errMsg)
        else:
            _bOK = self.__xh.isFailureFree
            _bOK = _bOK and self.__xh.hasPassedSetupPhase
            _bOK = _bOK and self.__xh.hasReachedRuntimePhase
            if _bOK:
                if _mainXT is None:
                    _bOK = not self.__xh.hasPassedMxtStartPhase
                else:
                    _bOK = bSkipAutoStartMainXT_ or self.__xh.hasPassedMxtStartPhase

            if not _bOK:
                if self.__xh.hasReachedRuntimePhase:
                    self.__xh._RemoveExecutionState(_ELcXState.eRuntimePhase, self)
                if self.__xh.hasPassedMxtStartPhase:
                    self.__xh._RemoveExecutionState(_ELcXState.eMxtStartPassed, self)
                if self.__xh.hasPassedSetupPhase:
                    self.__xh._RemoveExecutionState(_ELcXState.eSetupPassed, self)
                if _LcFailure.IsLcErrorFree():
                    _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TID_041).format(self.__xh)
                    _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_107, _errMsg)
                    if self.__xh.isFailureFree:
                        _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_004, errMsg_=_errMsg)
            else:
                res = _LcManager._FwApiReturnRecord(_mainXT, None)
        return res

