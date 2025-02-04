# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : lcproxyimpl.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from typing import Union as _PyUnion

from xcofdk.fwapi.xtask import MainXTask

from xcofdk._xcofw.fw.fwssys.fwcore.logging.logif import _CreateLogImplErrorEC

from xcofdk._xcofw.fw.fwssys.fwcore.logging import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.config.fwstartupconfig import _FwStartupConfig

from threading import RLock as _PyRLock

from xcofdk._xcofw.fw.fwssys.fwcore.logging.fatalentry     import _FatalEntry
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logifbase      import _LogIFBase
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logifimpl      import _LogIFImpl
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.main.fwmain        import _FwMain
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.sync.semaphore     import _BinarySemaphore
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.atask          import _AbstractTask
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.sync.mutex         import _Mutex
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskmgr        import _TaskMgr
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskmgr        import _TaskManager
from xcofdk._xcofw.fw.fwssys.fwcore.lcmon.lcmonimpl        import _LcMonitorImpl
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcdefines           import _ELcScope
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcdefines           import _ELcCompID
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcexecstate         import _LcFailure
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcguard             import _LcGuard
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcdefines           import _ELcOperationModeID
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcproxydefines      import _ProxyInfo
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcproxydefines      import _TaskInfo
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcproxydefines      import _ELcOpModeBitFlag
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcproxydefines      import _ELcShutdownRequest
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcproxy             import _LcProxy

from xcofdk._xcofw.fw.fwssys.fwerrh.fwerrorcodes import _EFwErrorCode
from xcofdk._xcofw.fw.fwssys.fwerrh.lcfrcview    import _LcFrcView

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine

class _LcProxyImpl(_LcProxy):

    __slots__ = [ '__apiLck'    , '__opModeLck' , '__lcScope'   , '__lcGuard'
                , '__tmgr'      , '__fwMain'    , '__tiFwMain'  , '__lcMonImpl'
                , '__eOpModeID' , '__mtxErrImp' , '__eOpModeBitMask' ]

    __bPxyInfoAvailable = False

    def __init__(self
                 , ppass_      : int
                 , lcScope_    : _ELcScope
                 , lcGuard_    : _LcGuard
                 , lcMon_      : _LcMonitorImpl
                 , startupCfg_ : _FwStartupConfig
                 , mainXT_     : MainXTask):
        self.__tmgr           = None
        self.__fwMain         = None
        self.__apiLck         = None
        self.__lcScope        = None
        self.__lcGuard        = None
        self.__tiFwMain       = None
        self.__mtxErrImp      = None
        self.__opModeLck      = None
        self.__eOpModeID      = None
        self.__eOpModeBitMask = None
        super().__init__(ppass_)

        _errMsg   = None
        _iImplErr = None

        if _LcProxy._singleton is not None:
            _iImplErr = _EFwErrorCode.FE_LCSF_103
        elif not isinstance(lcScope_, _ELcScope):
            _iImplErr = _EFwErrorCode.FE_LCSF_066
        elif not isinstance(lcGuard_, _LcGuard):
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

        _LcProxyImpl.__bPxyInfoAvailable = False

        _tmgr = _TaskMgr()
        if _tmgr is None:
            self.CleanUpByOwnerRequest(self._myPPass)

            if _LcFailure.IsLcErrorFree():
                _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_072)

            vlogif._LogOEC(True, _EFwErrorCode.VFE_00386)
            return

        _fwMain   = None
        _tiFwMain = None
        _fwMain, _tiFwMain = _LcProxyImpl.__CreateFwMain(_tmgr, lcMon_, mainXT_=mainXT_)
        if _fwMain is None:
            self.CleanUpByOwnerRequest(self._myPPass)

            if _LcFailure.IsLcErrorFree():
                _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_073)
            return

        _LcProxy._singleton = self

        self.__tmgr           = _tmgr
        self.__fwMain         = _fwMain
        self.__lcScope        = lcScope_
        self.__lcGuard        = lcGuard_
        self.__apiLck         = _PyRLock()
        self.__tiFwMain       = _tiFwMain
        self.__mtxErrImp      = _tiFwMain._errorImpactSyncMutex
        self.__lcMonImpl      = lcMon_
        self.__opModeLck      = _PyRLock()
        self.__eOpModeID      = _ELcOperationModeID.eIdle
        self.__eOpModeBitMask = _ELcOpModeBitFlag.DefaultMask()

        if not _tmgr._InjectLcProxy(self):
            _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_074)

        elif _LogIFBase.GetInstance() is None:
            if _LogIFImpl._GetInstance(lcpxy_=self, startupCfg_=startupCfg_) is None:
                _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_075)
                vlogif._LogOEC(False, _EFwErrorCode.VUE_00034)

        if _LcFailure.IsLcNotErrorFree():
            self.CleanUpByOwnerRequest(self._myPPass)

    def _PxyIsLcProxyModeNormal(self) -> bool:
        if self.__isInvalid:
            return False
        with self.__opModeLck:
            return _ELcOpModeBitFlag.IsNormal(self.__eOpModeBitMask)

    def _PxyIsLcProxyModeShutdown(self) -> bool:
        if self.__isInvalid:
            return False
        with self.__opModeLck:
            return _ELcOpModeBitFlag.IsShutdown(self.__eOpModeBitMask)

    def _PxyIsLcMonShutdownEnabled(self) -> bool:
        return False if self.__lcMonImpl is None else self.__lcMonImpl.isLcShutdownEnabled

    def _PxyGetLcProxyOperationMode(self) -> _ELcOperationModeID:
        if self.__isInvalid:
            return _ELcOperationModeID.eIdle
        with self.__opModeLck:
            if _ELcOperationModeID.eLcCeaseMode.value < self.__eOpModeID.value < _ELcOperationModeID.eLcPreShutdown.value:
                if self.__lcMonImpl.isDummyMonitor:
                    pass
                elif self.__lcMonImpl.isLcShutdownEnabled:
                    self.__eOpModeID = _ELcOperationModeID.eLcCeaseMode
            return _ELcOperationModeID(self.__eOpModeID.value)

    def _PxyIsLcProxyInfoAvailable(self) -> bool:
        res = False

        if       self.__isUnavailable:            pass
        elif     self.__fwMain is None:           pass
        elif     self.__fwMain.taskBadge is None: pass
        elif not self.__fwMain.isRunning:         pass
        elif     self.__tiFwMain is None:         pass
        elif not self.__tiFwMain._isResponsive:   pass
        else:
            res = True

        if not res:
            if _LcProxyImpl.__bPxyInfoAvailable:
                _LcProxyImpl.__bPxyInfoAvailable = False
        else:
            if not _LcProxyImpl.__bPxyInfoAvailable:
                _LcProxyImpl.__bPxyInfoAvailable = True
        return res

    def _PxyIsLcOperable(self) -> bool:
        if self.__isUnavailable: return False
        return self.__lcGuard.isLcOperable

    def _PxyIsLcCoreOperable(self) -> bool:
        if self.__isInvalid: return False
        return self.__lcGuard.isLcCoreOperable

    def _PxyIsMainXTaskStarted(self) -> bool:
        if self.__isInvalid: return False
        return self.__lcGuard.isMainXTaskStarted

    def _PxyIsMainXTaskStopped(self) -> bool:
        if self.__isInvalid: return False
        return self.__lcGuard.isMainXTaskStopped

    def _PxyIsMainXTaskFailed(self) -> bool:
        if self.__isInvalid: return False
        return self.__lcGuard.isMainXTaskFailed

    def _PxyIsTaskMgrApiAvailable(self):
        _tmgr = self._PxyGetTaskMgr()
        return (_tmgr is not None) and _tmgr.isTMgrApiFullyAvailable

    def _PxyIsTaskMgrFailed(self) -> bool:
        if self.__isInvalid: return False
        return self.__lcGuard.isTaskManagerFailed

    def _PxyHasLcAnyFailureState(self) -> bool:
        if self.__isInvalid: return False
        return self.__lcGuard.hasLcAnyFailureState

    def _PxyGetCurProxyInfo(self) -> _PyUnion[_ProxyInfo, None]:
        if self.__isUnavailable:
            return None
        return self.__CreateProxyInfo(self._PxyIsLcProxyInfoAvailable())

    def _PxyGetTaskMgr(self) -> _PyUnion[_TaskManager, None]:
        return None if self.__isUnavailable else self.__tmgr

    def _PxyGetLcFrcView(self) -> _LcFrcView:
        if self.__isInvalid: return None
        return self.__lcGuard.lcFrcView

    def _PxyHasLcCompAnyFailureState(self, eLcCompID_: _ELcCompID, atask_: _AbstractTask = None) -> bool:
        if self.__isInvalid: return False
        return self.__lcGuard.HasLcCompFRC(eLcCompID_, atask_=atask_)

    def _PxyGetLcCompFrcView(self, eLcCompID_ : _ELcCompID, atask_ : _AbstractTask =None) -> _LcFrcView:
        if self.__isInvalid: return None
        with self.__apiLck:
            return self.__lcGuard.GetLcCompFrcView(eLcCompID_, atask_=atask_)

    def _PxySetLcOperationalState(self, eLcCompID_: _ELcCompID, bStartStopFlag_: bool, atask_ : _AbstractTask) -> bool:
        if self.__isUnavailable:
            return False
        if not isinstance(eLcCompID_, _ELcCompID):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00387)
            return False
        if not isinstance(eLcCompID_, _ELcCompID):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00388)
            return False
        if not (isinstance(atask_, _AbstractTask) and (atask_.taskBadge is not None)):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00389)
            return False
        return self.__lcGuard._SetLcOperationalState(eLcCompID_, bStartStopFlag_, atask_=atask_)

    def _PxyNotifyLcFailure(self, eFailedCompID_ : _ELcCompID, frcError_ : _FatalEntry, atask_ : _AbstractTask =None):
        if self.__isInvalid:
            return
        if not isinstance(eFailedCompID_, _ELcCompID):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00390)
            return

        _bSkipReply = True if self.__lcMonImpl.isLcShutdownEnabled else False
        _bLock      = None if _bSkipReply else True

        self.__LockAPI(_bLock)

        if self._PxyIsLcProxyModeShutdown():
            pass 

        if not self.__lcGuard._SetLcFailure(eFailedCompID_, frcError_, atask_=atask_, bSkipReply_=_bSkipReply):
            if _bLock is not None:
                self.__LockAPI(False)

    def _PxyFinalizeSetup(self):
        res = self.__fwMain.FinalizeCustomSetup()
        if not res:
            vlogif._LogOEC(False, _EFwErrorCode.VUE_00035)

            if _LcFailure.IsLcErrorFree():
                _frcMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcProxyImpl_TextID_001)
                _frc    = _CreateLogImplErrorEC(_EFwErrorCode.FE_00375, _frcMsg)
                if _frc is not None:
                    self.__lcGuard._SetLcFailure(_ELcCompID.eFwMain, frcError_=_frc, atask_=self.__fwMain, bSkipReply_=True)

                if _LcFailure.IsLcErrorFree():
                    _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_005, errMsg_=_frcMsg)
        return res

    def _PxyProcessShutdownRequest( self, eShutdownRequest_ : _ELcShutdownRequest, eFailedCompID_ : _ELcCompID =None
                                  , frcError_ : _FatalEntry =None, atask_ : _AbstractTask =None, bPrvRequestReply_ =True):
        if self.__isInvalid:
            return

        _bRefresh = not bPrvRequestReply_

        if eShutdownRequest_ == _ELcShutdownRequest.eFailureHandling:
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

        if not self.__fwMain.isCurrentTask:
            _curTskInst = self.__tmgr._GetCurTask(bAutoEncloseMissingThread_=False)

        _bPrvNormal          = None
        _bPrvShutdown        = None
        _bPrvPreShutdown     = None
        _bPrvFailureHandling = None

        _bPrvNormal, _bPrvPreShutdown, _bPrvShutdown, _bPrvFailureHandling = _bCurNormal, _bCurPreShutdown, _bCurShutdown, _bCurFailureHandling

        _lstNewOpModes = [ _LcProxyImpl.__ShutdownActionType2LcOperationModeBitFlag(eShutdownRequest_) ]

        _lcCompID = None

        if _bPreShutdownDueToSetupFailure:
            pass
        elif _bPrvNormal:
            if eShutdownRequest_.isShutdown:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00393)
                return

            if eShutdownRequest_.isFailureHandling:
                _lstNewOpModes.append(_ELcOpModeBitFlag.ebfLcPreShutdown)

                _lcCompID = eFailedCompID_
        else:
            if not eShutdownRequest_.isShutdown:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00394)
                return

        if self.__lcMonImpl.isDummyMonitor:
            self.__fwMain.ProcessShutdownAction(eShutdownRequest_, eFailedCompID_=_lcCompID, frcError_=frcError_, atask_=atask_)
        else:
            self.__lcMonImpl._SetCurrentShutdownRequest(eShutdownRequest_)

            if self.__lcMonImpl.isLcMonitorAlive:
                self.__fwMain.ProcessShutdownAction(eShutdownRequest_, eFailedCompID_=_lcCompID, frcError_=frcError_, atask_=atask_)

            if not self.__lcMonImpl.isLcShutdownEnabled:
                self.__lcMonImpl._EnableCoordinatedShutdown(bManagedByMR_=False)

        for _ee in _lstNewOpModes:
            _eSDR = _ee._toLcShutdownRequest
            if _eSDR is not None:
                _curSDR = self.__lcMonImpl.eCurrentShutdownRequest
                if (_curSDR is None) or (_curSDR !=_eSDR):
                    self.__lcMonImpl._SetCurrentShutdownRequest(_eSDR)
            self.__UpdateLcOperationBitMask(_ee)

        self.__LockAPI(False)

    def _PxyStopFwMain(self):
        if self.__isInvalid:
            return

        self.__tmgr._InjectLcProxy(None)

        if self.__fwMain.isRunning:
            _semStop = None if self.__fwMain.isEnclosingPyThread else _BinarySemaphore(take_=True)
            self.__fwMain.StopFwMain(semStop_=_semStop)
            if _semStop is not None:
                _semStop.CleanUp()

    def _PxyJoinFwMain(self, mainXTUID_ : int =None) -> list:
        if self.__isInvalid:
            return None

        _lcg       = self.__lcGuard
        _myLcState = _lcg._GetLcState(bypassApiLock_=True)

        if mainXTUID_ is not None:
            if not _lcg.isMainXTaskFailed:
                _teXT = self.__tmgr._GetTaskErrorByTID(mainXTUID_)

                if (_teXT is not None) and _teXT.isFatalError:
                    _fee = _teXT._currentErrorEntry
                    _lcg._SetLcFailure(_ELcCompID.eMainXTask, _fee, atask_=None, bSkipReply_=True)

                elif _myLcState.isMainXTaskStarted:
                    _lcg._SetLcOperationalState(_ELcCompID.eMainXTask, False, atask_=None)

        if not _myLcState.isFwMainFailed:
            teMain = self.__fwMain.taskError

            if (teMain is not None) and teMain.isFatalError:
                _fee = teMain._currentErrorEntry
                _lcg._SetLcFailure(_ELcCompID.eFwMain, _fee, atask_=None, bSkipReply_=True)

            elif _myLcState.isFwMainStarted:
                _lcg._SetLcOperationalState(_ELcCompID.eFwMain, False, atask_=None)

        if self.__fwMain.isEnclosingStartupThread:
            pass 
        else:
            self.__fwMain.JoinTask()

        res = self.__tmgr._StopAllTasks(bCleanupStoppedTasks_=True, lstSkipTaskIDs_=[self.__fwMain.taskID])
        return res

    def _PxySyncStarFwMainByAsynStartup(self):
        _iImplErr = None

        if _LcFailure.IsLcNotErrorFree():
            _iImplErr = _EFwErrorCode.FE_LCSF_076
        elif self.__fwMain.isEnclosingPyThread:
            _iImplErr = _EFwErrorCode.FE_LCSF_078
        elif self.__isUnavailable:
            _iImplErr = _EFwErrorCode.FE_LCSF_079
        elif not ((self.__fwMain.linkedExecutable is None) or self.__fwMain.linkedExecutable.isRunnable):
            _iImplErr = _EFwErrorCode.FE_LCSF_080

        if _iImplErr is not None:
            res = False
            _LcFailure.CheckSetLcSetupFailure(_iImplErr)
        else:

            _ss = None if self.__fwMain.isEnclosingPyThread else _BinarySemaphore(take_=True)
            res = self.__fwMain.StartFwMain(_ss)

            if _ss is not None:
                _ss.CleanUp()

            res = res and self.__fwMain.isRunning
            if not res:
                _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_081)

                vlogif._LogOEC(False, _EFwErrorCode.VUE_00036)
            else:
                self.__UpdateLcOperationBitMask(_ELcOpModeBitFlag.ebfLcNormal)
        return res

    def _ToString(self, *args_, **kwargs_):
        if self.__isUnavailable: return None
        res = _FwTDbEngine.GetText(_EFwTextID.eLcProxyImpl_ToString_01)
        res = res.format(self.__fwMain.taskUniqueName, self.__lcScope.compactName, self.__lcGuard._GetLcState(), self.__curOperationMode2Str)
        return res

    def _CleanUpByOwnerRequest(self):
        if (self.__apiLck is None) or _LcProxy._singleton is None:
            pass
        elif id(self) != id(_LcProxy._singleton):
            pass
        else:
            _LcProxyImpl.__bPxyInfoAvailable = False

            _LcProxy._singleton = None

            self.__apiLck = None

            self.__tmgr._InjectLcProxy(None)
            self.__tmgr = None

            if self.__tiFwMain is not None:
                self.__tiFwMain.CleanUp()
            if self.__fwMain is not None:
                self.__fwMain.CleanUp()
            if self.__mtxErrImp is not None:
                self.__mtxErrImp.CleanUp()

            self.__fwMain         = None
            self.__lcScope        = None
            self.__lcGuard        = None
            self.__tiFwMain       = None
            self.__mtxErrImp      = None
            self.__lcMonImpl      = None
            self.__opModeLck      = None
            self.__eOpModeID      = None
            self.__eOpModeBitMask = None

    @property
    def __isInvalid(self):
        return self.__apiLck is None

    @property
    def __isUnavailable(self):
        return (self.__apiLck is None) or self._PxyIsLcProxyModeShutdown()

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
    def __ShutdownActionType2LcOperationModeBitFlag(eShutdownRequest_ : _ELcShutdownRequest) -> _ELcOpModeBitFlag:
        if eShutdownRequest_ == _ELcShutdownRequest.ePreShutdown:
            res = _ELcOpModeBitFlag.ebfLcPreShutdown
        elif eShutdownRequest_ == _ELcShutdownRequest.eShutdown:
            res = _ELcOpModeBitFlag.ebfLcShutdown
        else: 
            res = _ELcOpModeBitFlag.ebfLcFailureHandling
        return res

    @staticmethod
    def __CreateFwMain(tmgr_, lcMon_ : _LcMonitorImpl, mainXT_ : MainXTask =None):

        _tiFwMain = None
        _fwMain   = _FwMain(lcMon_)

        _bFwOK = _LcFailure.IsLcErrorFree()
        _bFwOK = _bFwOK and (vlogif._GetFirstFatalError() is None)  

        _myTskBadge = _fwMain.taskBadge if _bFwOK else None

        _bFwOK = _bFwOK and _myTskBadge is not None
        _bFwOK = _bFwOK and _myTskBadge.isFwMain
        _bFwOK = _bFwOK and _myTskBadge.isFwTask

        if not _bFwOK:
            if _LcFailure.IsLcErrorFree():
                _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_082)

            if _myTskBadge is None:
                vlogif._LogOEC(False, _EFwErrorCode.VUE_00037)
            else:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00396)

        elif _myTskBadge.isEnclosingPyThread:
            _bFwOK = False
            _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_083)
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00397)

        else:

            _bFwOK = _bFwOK and _myTskBadge.hasDieXcpTargetTaskRight
            _bFwOK = _bFwOK and _myTskBadge.hasErrorObserverTaskRight
            _bFwOK = _bFwOK and _myTskBadge.hasDieExceptionDelegateTargetTaskRight
            if not _bFwOK:
                _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_084)
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00398)
            else:
                _bFwOK = tmgr_._AddTaskEntry(_fwMain, removeAutoEnclosedTaskEntry_=True)
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

    @staticmethod
    def __CheckShutdownActionRequest( eShutdownRequest_ : _ELcShutdownRequest
                                     , bCurNormal_      : bool, bCurPreShutdown_     : bool
                                     , bCurShutdown_    : bool, bCurFailureHandling_ : bool):
        _bBadAction    = False
        _bIgnoreAction = False

        _bPreShutdownDueToSetupFailure = (not bCurNormal_) and eShutdownRequest_.isPreShutdown

        if bCurNormal_ or _bPreShutdownDueToSetupFailure:
            if eShutdownRequest_ == _ELcShutdownRequest.eShutdown:
                _bIgnoreAction, _bBadAction = False, True
        else:
            if bCurPreShutdown_ or bCurShutdown_:
                if eShutdownRequest_==_ELcShutdownRequest.eFailureHandling:
                    _bIgnoreAction, _bBadAction = True, False
                elif bCurPreShutdown_:
                    if eShutdownRequest_ == _ELcShutdownRequest.ePreShutdown:
                        _bIgnoreAction, _bBadAction = True, False
                else:
                    if eShutdownRequest_ == _ELcShutdownRequest.ePreShutdown:
                        _bIgnoreAction, _bBadAction = False, True
                    else:
                        _bIgnoreAction, _bBadAction = True, False

            elif bCurFailureHandling_:
                if eShutdownRequest_ == _ELcShutdownRequest.eShutdown:
                    _bIgnoreAction, _bBadAction = False, True
                elif eShutdownRequest_==_ELcShutdownRequest.eFailureHandling:
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
                self.__apiLck.acquire()
            else:
                self.__apiLck.release()

    def __CreateProxyInfo(self, bPxyInfoAvail_ : bool) -> _ProxyInfo:

        if self.__isInvalid:
            return None

        _ctInst = self.__tmgr._GetCurTask(bAutoEncloseMissingThread_=True)

        if not bPxyInfoAvail_:
            return None

        if _ctInst is None:
            res = None
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00401)

        else:
            res = _ProxyInfo(_ctInst, self.__tiFwMain, bIgnoreCeaseMode_=True)
            if res.curTaskInfo is None:
                res.CleanUp()
                res = None
            elif self.__lcMonImpl.isDummyMonitor:
                pass
            elif res.curTaskInfo.isFwMain:
                pass
            elif self.__lcMonImpl.isLcShutdownEnabled:
                if not res.curTaskInfo.isInLcCeaseMode:
                    _myTskInst = res.curTaskInfo._taskInst
                    _myTskInst._CreateCeaseTLB(bEnding_=_myTskInst.isAborting)

            if res is None:
                if _LcProxyImpl.__bPxyInfoAvailable:
                    _LcProxyImpl.__bPxyInfoAvailable = False
            else:
                if not _LcProxyImpl.__bPxyInfoAvailable:
                    _LcProxyImpl.__bPxyInfoAvailable = True
        return res

    def __UpdateLcOperationBitMask(self, eOpMode_ : _ELcOpModeBitFlag):

        if self.__opModeLck is None:
            return
        elif eOpMode_.value < _ELcOpModeBitFlag.ebfLcNormal.value:
            return

        with self.__opModeLck:
            _bChanged = False

            mn = _ELcOpModeBitFlag.ebfLcNormal
            if eOpMode_.value > mn.value:
                if _ELcOpModeBitFlag.IsNormal(self.__eOpModeBitMask):
                    _bChanged = True
                    self.__eOpModeBitMask = _ELcOpModeBitFlag.RemoveBitFlag(self.__eOpModeBitMask, mn)

                if eOpMode_ == _ELcOpModeBitFlag.ebfLcShutdown:
                    if _ELcOpModeBitFlag.IsPreShutdown(self.__eOpModeBitMask):
                        _bChanged = True
                        self.__eOpModeBitMask = _ELcOpModeBitFlag.RemoveBitFlag(self.__eOpModeBitMask, _ELcOpModeBitFlag.ebfLcPreShutdown)

            if not _ELcOpModeBitFlag.IsBitFlagSet(self.__eOpModeBitMask, eOpMode_):
                _bChanged = True
                self.__eOpModeBitMask = _ELcOpModeBitFlag.AddBitFlag(self.__eOpModeBitMask, eOpMode_)

            if _bChanged:
                self.__eOpModeID = eOpMode_._toLcOperationModeID

    def __DecodeCurOperationBitmask(self):
        _bNormal          = None
        _bShutdown        = None
        _bPreShutdown     = None
        _bFailureHandling = None

        if self.__opModeLck is None:
            pass
        else:
            with self.__opModeLck:
                _bNormal          = _ELcOpModeBitFlag.IsBitFlagSet(self.__eOpModeBitMask, _ELcOpModeBitFlag.ebfLcNormal)
                _bShutdown        = _ELcOpModeBitFlag.IsBitFlagSet(self.__eOpModeBitMask, _ELcOpModeBitFlag.ebfLcShutdown)
                _bPreShutdown     = _ELcOpModeBitFlag.IsBitFlagSet(self.__eOpModeBitMask, _ELcOpModeBitFlag.ebfLcPreShutdown)
                _bFailureHandling = _ELcOpModeBitFlag.IsBitFlagSet(self.__eOpModeBitMask, _ELcOpModeBitFlag.ebfLcFailureHandling)

                bImplErr = False
                if _bNormal:
                    if _bPreShutdown or _bShutdown or _bFailureHandling:
                        bImplErr = True
                        vlogif._LogOEC(True, _EFwErrorCode.VFE_00402)
                elif not (_bPreShutdown or _bShutdown or _bFailureHandling):
                    if self.__eOpModeBitMask.value != _ELcOpModeBitFlag.ebfIdle.value:
                        bImplErr = True
                        vlogif._LogOEC(True, _EFwErrorCode.VFE_00403)
                elif _bPreShutdown and _bShutdown:
                    bImplErr = True
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00404)

                if bImplErr:
                    _bNormal, _bPreShutdown, _bShutdown, _bFailureHandling = None, None, None, None
        return _bNormal, _bPreShutdown, _bShutdown, _bFailureHandling
