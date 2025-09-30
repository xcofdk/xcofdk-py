# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : lcproxy.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from threading import RLock as _PyRLock
from typing    import List
from typing    import Union

from xcofdk.fwapi.xmt import XMainTask

from _fw.fwssys.assys.ifs.tiftmgr             import _ITTMgr
from _fw.fwssys.fwcore.logging                import vlogif
from _fw.fwssys.fwcore.logging.logif          import _CreateLogImplErrorEC
from _fw.fwssys.fwcore.logging.alogmgr        import _AbsLogMgr
from _fw.fwssys.fwcore.logging.logmgr         import _LogMgr
from _fw.fwssys.fwcore.config.fwstartupconfig import _FwStartupConfig
from _fw.fwssys.fwcore.ipc.main.fwmain        import _FwMain
from _fw.fwssys.fwcore.ipc.sync.semaphore     import _BinarySemaphore
from _fw.fwssys.fwcore.ipc.sync.mutex         import _Mutex
from _fw.fwssys.fwcore.ipc.tsk.afwtask        import _AbsFwTask
from _fw.fwssys.fwcore.ipc.tsk.taskmgr        import _TaskMgr
from _fw.fwssys.fwcore.ipc.tsk.taskmgr        import _TaskManager
from _fw.fwssys.fwcore.lc.lcmn.lcmonimpl      import _LcMonitorImpl
from _fw.fwssys.fwcore.lc.lcdefines           import _ELcScope
from _fw.fwssys.fwcore.lc.lcdefines           import _ELcCompID
from _fw.fwssys.fwcore.lc.lcxstate            import _LcFailure
from _fw.fwssys.fwcore.lc.lcdefines           import _ELcOperationModeID
from _fw.fwssys.fwcore.lc.lcproxydefines      import _ProxyInfo
from _fw.fwssys.fwcore.lc.lcproxydefines      import _TaskInfo
from _fw.fwssys.fwcore.lc.lcproxydefines      import _ELcOpModeBitFlag
from _fw.fwssys.fwcore.lc.lcproxydefines      import _ELcSDRequest
from _fw.fwssys.fwcore.lc.ifs.iflcguard       import _ILcGuard
from _fw.fwssys.fwcore.lc.ifs.iflcproxy       import _ILcProxy
from _fw.fwssys.fwerrh.fwerrorcodes           import _EFwErrorCode
from _fw.fwssys.fwerrh.logs.errorlog          import _FatalLog
from _fw.fwssys.fwerrh.lcfrcview              import _LcFrcView

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _LcProxy(_ILcProxy):
    __slots__ = [ '__lm' , '__la' , '__s' , '__g' , '__tm' , '__m' , '__mi' , '__me' , '__mm' , '__mid' , '__mni' ]

    __bPIA = False

    def __init__( self
                , ppass_      : int
                , lcScope_    : _ELcScope
                , lcGuard_    : _ILcGuard
                , lcMon_      : _LcMonitorImpl
                , startupCfg_ : _FwStartupConfig
                , mainXT_     : XMainTask):
        self.__g   = None
        self.__m   = None
        self.__s   = None
        self.__la  = None
        self.__lm  = None
        self.__me  = None
        self.__mi  = None
        self.__mm  = None
        self.__tm  = None
        self.__mid = None
        super().__init__(ppass_)

        _errMsg     = None
        _iImplErr   = None
        _implErrMsg = None

        if _ILcProxy._sgltn is not None:
            _iImplErr = _EFwErrorCode.FE_LCSF_103
        elif not isinstance(lcScope_, _ELcScope):
            _iImplErr = _EFwErrorCode.FE_LCSF_066
        elif not isinstance(lcGuard_, _ILcGuard):
            _iImplErr = _EFwErrorCode.FE_LCSF_067
        elif not isinstance(lcMon_, _LcMonitorImpl):
            _iImplErr = _EFwErrorCode.FE_LCSF_068
        elif not (isinstance(startupCfg_, _FwStartupConfig) and startupCfg_._isValid):
            _iImplErr = _EFwErrorCode.FE_LCSF_069
        if _iImplErr is not None:
            self.CleanUpByOwnerRequest(self._myPPass)
            _LcFailure.CheckSetLcSetupFailure(_iImplErr)

            if _errMsg is not None:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00385)
            return

        _LcProxy.__bPIA = False

        _tmgr = _TaskMgr()
        if not isinstance(_tmgr, _ITTMgr):
            self.CleanUpByOwnerRequest(self._myPPass)

            if _LcFailure.IsLcErrorFree():
                _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_072)

            vlogif._LogOEC(True, _EFwErrorCode.VFE_00386)
            return

        _fwMain   = None
        _tiFwMain = None
        _fwMain, _tiFwMain = _LcProxy.__CreateFwMain(_tmgr, lcMon_, mainXT_=mainXT_)
        if _fwMain is None:
            self.CleanUpByOwnerRequest(self._myPPass)

            if _LcFailure.IsLcErrorFree():
                _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_073)
            return

        _ILcProxy._sgltn = self

        self.__g   = lcGuard_
        self.__m   = _fwMain
        self.__s   = lcScope_
        self.__la  = _PyRLock()
        self.__lm  = _PyRLock()
        self.__me  = _tiFwMain._errorImpactSyncMutex
        self.__mi  = _tiFwMain
        self.__mm  = _ELcOpModeBitFlag.DefaultMask()
        self.__tm  = _tmgr
        self.__mid = _ELcOperationModeID.eIdle
        self.__mni = lcMon_

        if not _tmgr._InjectLcProxy(self):
            _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_074)

        elif _AbsLogMgr.GetInstance() is None:
            if _LogMgr._GetInstance(self, startupCfg_) is None:
                _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_075)
                vlogif._LogOEC(False, _EFwErrorCode.VUE_00034)

        if _LcFailure.IsLcNotErrorFree():
            self.CleanUpByOwnerRequest(self._myPPass)

    def _PxyIsLcProxyModeNormal(self) -> bool:
        if self.__isInvalid:
            return False
        with self.__lm:
            return _ELcOpModeBitFlag.IsNormal(self.__mm)

    def _PxyIsLcProxyModeShutdown(self) -> bool:
        if self.__isInvalid:
            return False
        with self.__lm:
            return _ELcOpModeBitFlag.IsShutdown(self.__mm)

    def _PxyIsLcMonShutdownEnabled(self) -> bool:
        return False if self.__mni is None else self.__mni.isLcShutdownEnabled

    def _PxyGetLcProxyOperationMode(self) -> _ELcOperationModeID:
        if self.__isInvalid:
            return _ELcOperationModeID.eIdle
        with self.__lm:
            if _ELcOperationModeID.eLcCeaseMode.value < self.__mid.value < _ELcOperationModeID.eLcPreShutdown.value:
                if self.__mni.isDummyMonitor:
                    pass
                elif self.__mni.isLcShutdownEnabled:
                    self.__mid = _ELcOperationModeID.eLcCeaseMode
            return _ELcOperationModeID(self.__mid.value)

    def _PxyIsLcProxyInfoAvailable(self) -> bool:
        res = False

        if       self.__isUnavailable:       pass
        elif     self.__m is None:           pass
        elif     self.__m.taskBadge is None: pass
        elif not self.__m.isRunning:         pass
        elif     self.__mi is None:          pass
        elif not self.__mi._isResponsive:    pass
        else:
            res = True

        if not res:
            if _LcProxy.__bPIA:
                _LcProxy.__bPIA = False
        else:
            if not _LcProxy.__bPIA:
                _LcProxy.__bPIA = True
        return res

    def _PxyIsLcOperable(self) -> bool:
        if self.__isUnavailable: return False
        return self.__g.isLcOperable

    def _PxyIsLcCoreOperable(self) -> bool:
        if self.__isInvalid: return False
        return self.__g.isLcCoreOperable

    def _PxyIsMainXTaskStarted(self) -> bool:
        if self.__isInvalid: return False
        return self.__g.isMainXTaskStarted

    def _PxyIsMainXTaskStopped(self) -> bool:
        if self.__isInvalid: return False
        return self.__g.isMainXTaskStopped

    def _PxyIsMainXTaskFailed(self) -> bool:
        if self.__isInvalid: return False
        return self.__g.isMainXTaskFailed

    def _PxyIsTaskMgrAvailable(self):
        _tmgr = self._PxyGetTaskMgr()
        return (_tmgr is not None) and _tmgr.isTMgrAvailable

    def _PxyIsTaskMgrFailed(self) -> bool:
        if self.__isInvalid: return False
        return self.__g.isTaskManagerFailed

    def _PxyHasLcAnyFailureState(self) -> bool:
        if self.__isInvalid: return False
        return self.__g.hasLcAnyFailureState

    def _PxyGetCurProxyInfo(self) -> Union[_ProxyInfo, None]:
        if self.__isUnavailable:
            return None
        return self.__CreateProxyInfo(self._PxyIsLcProxyInfoAvailable())

    def _PxyGetTaskMgr(self) -> Union[_TaskManager, None]:
        return None if self.__isUnavailable else self.__tm

    def _PxyGetTTaskMgr(self) -> Union[_ITTMgr, None]:
        return None if self.__isUnavailable else self.__tm

    def _PxyGetLcFrcView(self) -> _LcFrcView:
        if self.__isInvalid: return None
        return self.__g.lcFrcView

    def _PxyHasLcCompAnyFailureState(self, lcCID_: _ELcCompID, atask_: _AbsFwTask = None) -> bool:
        if self.__isInvalid: return False
        return self.__g.HasLcCompFRC(lcCID_, atask_=atask_)

    def _PxyGetLcCompFrcView(self, lcCID_ : _ELcCompID, atask_ : _AbsFwTask =None) -> _LcFrcView:
        if self.__isInvalid: return None
        with self.__la:
            return self.__g.GetLcCompFrcView(lcCID_, atask_=atask_)

    def _PxySetLcOperationalState(self, lcCID_: _ELcCompID, bStartStopFlag_: bool, atask_ : _AbsFwTask) -> bool:
        if self.__isUnavailable:
            return False
        if not isinstance(lcCID_, _ELcCompID):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00387)
            return False
        if not isinstance(lcCID_, _ELcCompID):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00388)
            return False
        if not (isinstance(atask_, _AbsFwTask) and (atask_.taskBadge is not None)):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00389)
            return False
        return self.__g._GSetLcOperationalState(lcCID_, bStartStopFlag_, atask_=atask_)

    def _PxyNotifyLcFailure(self, eFailedCompID_ : _ELcCompID, frcError_ : _FatalLog, atask_ : _AbsFwTask =None):
        if self.__isInvalid:
            return
        if not isinstance(eFailedCompID_, _ELcCompID):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00390)
            return

        _bSkipReply = True if self.__mni.isLcShutdownEnabled else False
        _bLock      = None if _bSkipReply else True

        self.__LockAPI(_bLock)

        if not self.__g._GSetLcFailure(eFailedCompID_, frcError_, atask_=atask_, bSkipReply_=_bSkipReply):
            if _bLock is not None:
                self.__LockAPI(False)

    def _PxyFinalizeSetup(self):
        res = self.__m.FinalizeCustomSetup()
        if not res:
            vlogif._LogOEC(False, _EFwErrorCode.VUE_00035)

            if _LcFailure.IsLcErrorFree():
                _frcMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcProxy_TID_001)
                _frc    = _CreateLogImplErrorEC(_EFwErrorCode.FE_00375, _frcMsg)
                if _frc is not None:
                    self.__g._GSetLcFailure(_ELcCompID.eFwMain, frcError_=_frc, atask_=self.__m, bSkipReply_=True)
                if _LcFailure.IsLcErrorFree():
                    _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_005, errMsg_=_frcMsg)
        return res

    def _PxyProcessShutdownRequest( self, eShutdownRequest_ : _ELcSDRequest, eFailedCompID_ : _ELcCompID =None
                                  , frcError_ : _FatalLog =None, atask_ : _AbsFwTask =None, bPrvRequestReply_ =True):
        if self.__isInvalid:
            return

        _bRefresh = not bPrvRequestReply_

        if eShutdownRequest_ == _ELcSDRequest.eFailureHandling:
            if eFailedCompID_ is None:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00391)
                if not _bRefresh:
                    self.__LockAPI(False)
                return

        if _bRefresh:
            self.__LockAPI(True)

        _bCurNormal          = None
        _bCurShutdown        = None
        _bCurPreShutdown     = None
        _bCurFailureHandling = None

        _bCurNormal, _bCurPreShutdown, _bCurShutdown, _bCurFailureHandling = self.__DecodeCurOperationBitmask()
        if _bCurNormal is None:
            if _bRefresh:
                self.__LockAPI(False)
            return

        _bBadAction                    = None
        _bIgnoreAction                 = None
        _bPreShutdownDueToSetupFailure = None

        _bIgnoreAction, _bBadAction, _bPreShutdownDueToSetupFailure = self.__CheckShutdownActionRequest(
            eShutdownRequest_, _bCurNormal, _bCurPreShutdown, _bCurShutdown, _bCurFailureHandling)

        if _bIgnoreAction or _bBadAction:
            if _bRefresh:
                self.__LockAPI(False)

            if _bBadAction:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00392)
            return

        _bPrvNormal          = None
        _bPrvShutdown        = None
        _bPrvPreShutdown     = None
        _bPrvFailureHandling = None

        _bPrvNormal, _bPrvPreShutdown, _bPrvShutdown, _bPrvFailureHandling = _bCurNormal, _bCurPreShutdown, _bCurShutdown, _bCurFailureHandling

        _lstNewOpModes = [ _LcProxy.__ShutdownActionType2LcOperationModeBitFlag(eShutdownRequest_) ]

        _lcCID = None

        if _bPreShutdownDueToSetupFailure:
            pass

        elif _bPrvNormal:
            if eShutdownRequest_.isShutdown:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00393)
                return

            if eShutdownRequest_.isFailureHandling:
                _lstNewOpModes.append(_ELcOpModeBitFlag.ebfLcPreShutdown)

                _lcCID = eFailedCompID_

        else:
            if not eShutdownRequest_.isShutdown:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00394)
                return

        if self.__mni.isDummyMonitor:
            self.__m.ProcessShutdownAction(eShutdownRequest_, eFailedCompID_=_lcCID, frcError_=frcError_, atask_=atask_)

        else:
            self.__mni._SetCurrentShutdownRequest(eShutdownRequest_)

            if self.__mni.isLcMonitorAlive:
                self.__m.ProcessShutdownAction(eShutdownRequest_, eFailedCompID_=_lcCID, frcError_=frcError_, atask_=atask_)

            if not self.__mni.isLcShutdownEnabled:
                self.__mni._EnableCoordinatedShutdown(bManagedByMR_=False)

        for _ee in _lstNewOpModes:
            _eSDR = _ee._toLcShutdownRequest
            if _eSDR is not None:
                _curSDR = self.__mni.curShutdownRequest
                if (_curSDR is None) or (_curSDR !=_eSDR):
                    self.__mni._SetCurrentShutdownRequest(_eSDR)
            self.__UpdateLcOperationBitMask(_ee)

        self.__LockAPI(False)

    def _PxyJoinFwMain(self, mainXtUID_ : int =None) -> Union[List[_AbsFwTask], None]:
        if self.__isInvalid:
            return None

        _lcg       = self.__g
        _myLcState = _lcg._GGetLcState(bypassApiLock_=True)

        self.__PxyStopFwMain()

        if mainXtUID_ is not None:
            if not _lcg.isMainXTaskFailed:
                _teXT = self.__tm._GetTaskErrorByTID(mainXtUID_)

                if (_teXT is not None) and _teXT.isFatalError:
                    _fee = _teXT._currentErrorEntry
                    _lcg._GSetLcFailure(_ELcCompID.eMainXTask, _fee, atask_=None, bSkipReply_=True)

                elif _myLcState.isMainXTaskStarted:
                    _lcg._GSetLcOperationalState(_ELcCompID.eMainXTask, False, atask_=None)

        if not _myLcState.isFwMainFailed:
            teMain = self.__m.taskError

            if (teMain is not None) and teMain.isFatalError:
                _fee = teMain._currentErrorEntry
                _lcg._GSetLcFailure(_ELcCompID.eFwMain, _fee, atask_=None, bSkipReply_=True)
            elif _myLcState.isFwMainStarted:
                _lcg._GSetLcOperationalState(_ELcCompID.eFwMain, False, atask_=None)

        if not self.__m.isEnclosingStartupThread:
            self.__m.JoinTask()

        res = self.__tm._StopAllTasks(bCleanupStoppedTasks_=True, lstSkipTaskIDs_=[self.__m.dtaskUID])
        return res

    def _PxyStartFwMain(self):
        _errMsg   = None
        _iImplErr = None

        if _LcFailure.IsLcNotErrorFree():
            _iImplErr = _EFwErrorCode.FE_LCSF_076
        elif self.__isUnavailable:
            _iImplErr = _EFwErrorCode.FE_LCSF_079

        if _iImplErr is not None:
            res = False
            _LcFailure.CheckSetLcSetupFailure(_iImplErr, errMsg_=_errMsg)
            if _errMsg is not None:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00395)
        else:
            _ss = None if self.__m.isEnclosingPyThread else _BinarySemaphore(take_=True)
            res = self.__m.StartFwMain(_ss)

            if _ss is not None:
                _ss.CleanUp()

            res = res and self.__m.isRunning
            if not res:
                _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_081)
                vlogif._LogOEC(False, _EFwErrorCode.VUE_00036)
            else:
                _eOpMode = _ELcOpModeBitFlag.ebfLcNormal
                self.__UpdateLcOperationBitMask(_eOpMode)
        return res

    def _ToString(self):
        if self.__isUnavailable: return None
        res = _FwTDbEngine.GetText(_EFwTextID.eLcProxy_ToString_01)
        res = res.format(self.__m.dtaskName, self.__s.compactName, self.__g._GGetLcState(), self.__curOperationMode2Str)
        return res

    def _CleanUpByOwnerRequest(self):
        if (self.__la is None) or _ILcProxy._sgltn is None:
            return
        if id(self) != id(_ILcProxy._sgltn):
            return

        _ILcProxy._sgltn     = None
        _LcProxy.__bPIA = False

        self.__la = None

        self.__tm._InjectLcProxy(None)
        self.__tm = None

        if self.__mi is not None:
            self.__mi.CleanUp()
        if self.__m is not None:
            self.__m.CleanUp()
        if self.__me is not None:
            self.__me.CleanUp()

        self.__g   = None
        self.__m   = None
        self.__s   = None
        self.__lm  = None
        self.__me  = None
        self.__mi  = None
        self.__mm  = None
        self.__mid = None
        self.__mni = None

    @property
    def __isInvalid(self):
        return self.__la is None

    @property
    def __isUnavailable(self):
        return (self.__la is None) or self._PxyIsLcProxyModeShutdown()

    @property
    def __curOperationMode2Str(self):
        _bCurNormal          = None
        _bCurShutdown        = None
        _bCurPreShutdown     = None
        _bCurFailureHandling = None
        _bCurNormal, _bCurPreShutdown, _bCurShutdown, _bCurFailureHandling = self.__DecodeCurOperationBitmask()
        return 'LC operation mode: (bLcNormal, bLcPreShutdown, bLcShutdown, bLcFailureHandling)=({}, {}, {}, {})'.format(
                _bCurNormal, _bCurPreShutdown, _bCurShutdown, _bCurFailureHandling)

    @staticmethod
    def __ShutdownActionType2LcOperationModeBitFlag(eShutdownRequest_ : _ELcSDRequest) -> _ELcOpModeBitFlag:
        if eShutdownRequest_ == _ELcSDRequest.ePreShutdown:
            res = _ELcOpModeBitFlag.ebfLcPreShutdown
        elif eShutdownRequest_ == _ELcSDRequest.eShutdown:
            res = _ELcOpModeBitFlag.ebfLcShutdown
        else: 
            res = _ELcOpModeBitFlag.ebfLcFailureHandling
        return res

    @staticmethod
    def __CreateFwMain(tmgr_ : _ITTMgr, lcMon_ : _LcMonitorImpl, mainXT_ : XMainTask =None):
        _tiFwMain = None
        _fwMain   = _FwMain(lcMon_)

        _bFwOK = isinstance(tmgr_, _ITTMgr)
        _bFwOK = _bFwOK and _LcFailure.IsLcErrorFree()
        _bFwOK = _bFwOK and (vlogif._GetFirstFatalError() is None)  

        _myTB = _fwMain.taskBadge if _bFwOK else None

        _bFwOK = _bFwOK and _myTB is not None
        _bFwOK = _bFwOK and _myTB.isFwMain
        _bFwOK = _bFwOK and _myTB.isFwTask

        if not _bFwOK:
            if _LcFailure.IsLcErrorFree():
                _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_082)
            if _myTB is None:
                vlogif._LogOEC(False, _EFwErrorCode.VUE_00037)
            else:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00396)
        else:
            _bFwOK = _bFwOK and _myTB.hasDieXcpTargetTaskRight
            _bFwOK = _bFwOK and _myTB.hasErrorObserverTaskRight
            _bFwOK = _bFwOK and _myTB.hasDieExceptionDelegateTargetTaskRight
            if not _bFwOK:
                _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_084)
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00398)
            else:
                _bFwOK = tmgr_._AddTaskEntry(_fwMain, bRemoveAutoEnclTE_=True)
                if not _bFwOK:
                    _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_085)
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00399)
            if _bFwOK:
                _mm = _Mutex()
                _tiFwMain = _TaskInfo(_fwMain, _mm)
                _bFwOK = not _tiFwMain._isInvalid
                if not _bFwOK:
                    _tiFwMain.CleanUp()
                    _mm.CleanUp()

                    _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_086)
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00400)

        if not _bFwOK:
            if _LcFailure.IsLcErrorFree():
                _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_087)

            if _fwMain is not None:
                if vlogif._GetFirstFatalError() is None:  
                    _fwMain.CleanUp()
                _fwMain, _tiFwMain = None, None
        return _fwMain, _tiFwMain

    def __PxyStopFwMain(self):
        if self.__isInvalid:
            return
        self.__tm._InjectLcProxy(None)
        if self.__m.isRunning:
            _semStop = None if self.__m.isEnclosingPyThread else _BinarySemaphore(take_=True)
            self.__m.StopFwMain(semStop_=_semStop)
            if _semStop is not None:
                _semStop.CleanUp()

    @staticmethod
    def __CheckShutdownActionRequest( eShutdownRequest_ : _ELcSDRequest
                                     , bCurNormal_      : bool, bCurPreShutdown_     : bool
                                     , bCurShutdown_    : bool, bCurFailureHandling_ : bool):
        _bBadAction    = False
        _bIgnoreAction = False

        _bPreShutdownDueToSetupFailure = (not bCurNormal_) and eShutdownRequest_.isPreShutdown

        if bCurNormal_ or _bPreShutdownDueToSetupFailure:
            if eShutdownRequest_ == _ELcSDRequest.eShutdown:
                _bIgnoreAction, _bBadAction = False, True
        else:
            if bCurPreShutdown_ or bCurShutdown_:
                if eShutdownRequest_==_ELcSDRequest.eFailureHandling:
                    _bIgnoreAction, _bBadAction = True, False
                elif bCurPreShutdown_:
                    if eShutdownRequest_ == _ELcSDRequest.ePreShutdown:
                        _bIgnoreAction, _bBadAction = True, False
                else:
                    if eShutdownRequest_ == _ELcSDRequest.ePreShutdown:
                        _bIgnoreAction, _bBadAction = False, True
                    else:
                        _bIgnoreAction, _bBadAction = True, False
            elif bCurFailureHandling_:
                if eShutdownRequest_ == _ELcSDRequest.eShutdown:
                    _bIgnoreAction, _bBadAction = False, True
                elif eShutdownRequest_==_ELcSDRequest.eFailureHandling:
                    _bIgnoreAction, _bBadAction = True, False
                else:
                    _bIgnoreAction, _bBadAction = True, False
            else:
                _bIgnoreAction, _bBadAction = True, True
        return _bIgnoreAction, _bBadAction, _bPreShutdownDueToSetupFailure

    def __LockAPI(self, bLock_ : bool):
        if self.__isInvalid:
            pass
        else:
            if bLock_ is None:
                pass
            elif bLock_:
                self.__la.acquire()
            else:
                self.__la.release()

    def __CreateProxyInfo(self, bPxyInfoAvail_ : bool) -> Union[_ProxyInfo, None]:
        if self.__isInvalid:
            return None

        _ctInst = self.__tm._GetCurTask(bAutoEncl_=True)

        if not bPxyInfoAvail_:
            return None

        if _ctInst is None:
            res = None
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00401)

        else:
            res = _ProxyInfo(_ctInst, self.__mi)
            if res.curTaskInfo is None:
                res.CleanUp()
                res = None
            elif self.__mni.isDummyMonitor:
                pass
            elif res.curTaskInfo.isFwMain:
                pass
            elif self.__mni.isLcShutdownEnabled:
                if not res.curTaskInfo.isInLcCeaseMode:
                    _myTskInst = res.curTaskInfo._taskInst
                    _myTskInst._CreateCeaseTLB(bEnding_=_myTskInst.isAborting)

            if res is None:
                if _LcProxy.__bPIA:
                    _LcProxy.__bPIA = False
            else:
                if not _LcProxy.__bPIA:
                    _LcProxy.__bPIA = True
        return res

    def __UpdateLcOperationBitMask(self, eOpMode_ : _ELcOpModeBitFlag):
        if self.__lm is None:
            return
        elif eOpMode_.value < _ELcOpModeBitFlag.ebfLcNormal.value:
            return

        with self.__lm:
            _bChanged = False

            mn = _ELcOpModeBitFlag.ebfLcNormal
            if eOpMode_.value > mn.value:
                if _ELcOpModeBitFlag.IsNormal(self.__mm):
                    _bChanged = True
                    self.__mm = _ELcOpModeBitFlag.RemoveBitFlag(self.__mm, mn)
                if eOpMode_ == _ELcOpModeBitFlag.ebfLcShutdown:
                    if _ELcOpModeBitFlag.IsPreShutdown(self.__mm):
                        _bChanged = True
                        self.__mm = _ELcOpModeBitFlag.RemoveBitFlag(self.__mm, _ELcOpModeBitFlag.ebfLcPreShutdown)
            if not _ELcOpModeBitFlag.IsBitFlagSet(self.__mm, eOpMode_):
                _bChanged = True
                self.__mm = _ELcOpModeBitFlag.AddBitFlag(self.__mm, eOpMode_)
            if _bChanged:
                _prvm = self.__mid
                self.__mid = eOpMode_._toLcOperationModeID

    def __DecodeCurOperationBitmask(self):
        _bNormal          = None
        _bShutdown        = None
        _bPreShutdown     = None
        _bFailureHandling = None

        if self.__lm is None:
            pass
        else:
            with self.__lm:
                _bNormal          = _ELcOpModeBitFlag.IsBitFlagSet(self.__mm, _ELcOpModeBitFlag.ebfLcNormal)
                _bShutdown        = _ELcOpModeBitFlag.IsBitFlagSet(self.__mm, _ELcOpModeBitFlag.ebfLcShutdown)
                _bPreShutdown     = _ELcOpModeBitFlag.IsBitFlagSet(self.__mm, _ELcOpModeBitFlag.ebfLcPreShutdown)
                _bFailureHandling = _ELcOpModeBitFlag.IsBitFlagSet(self.__mm, _ELcOpModeBitFlag.ebfLcFailureHandling)

                bImplErr = False
                if _bNormal:
                    if _bPreShutdown or _bShutdown or _bFailureHandling:
                        bImplErr = True
                        vlogif._LogOEC(True, _EFwErrorCode.VFE_00402)
                elif not (_bPreShutdown or _bShutdown or _bFailureHandling):
                    if self.__mm.value != _ELcOpModeBitFlag.ebfIdle.value:
                        bImplErr = True
                        vlogif._LogOEC(True, _EFwErrorCode.VFE_00403)
                elif _bPreShutdown and _bShutdown:
                    bImplErr = True
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00404)

                if bImplErr:
                    _bNormal, _bPreShutdown, _bShutdown, _bFailureHandling = None, None, None, None
        return _bNormal, _bPreShutdown, _bShutdown, _bFailureHandling
