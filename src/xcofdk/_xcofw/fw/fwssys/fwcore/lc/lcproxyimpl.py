# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : lcproxyimpl.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from typing import Union as _PyUnion

from xcofdk._xcofw.fw.fwssys.fwcore.logging.logif import _CreateLogImplError

from xcofdk._xcofw.fw.fwssys.fwcore.logging import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.config.fwstartupconfig import _FwStartupConfig

from threading import RLock as _PyRLock

from xcofdk.fwapi.xtask import MainXTask

from xcofdk._xcofw.fw.fwssys.fwcore.logging.fatalentry     import _FatalEntry
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logifbase      import _LogIFBase
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logifimpl      import _LogIFImpl
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.main.fwmain        import _FwMain
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.sync.semaphore     import _BinarySemaphore
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.atask          import _AbstractTask
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.sync.mutex         import _Mutex
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskmgr        import _TaskManager
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskmgrimpl    import _TaskManagerImpl
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil       import _TaskUtil
from xcofdk._xcofw.fw.fwssys.fwcore.lcmon.lcmonimpl        import _LcMonitorImpl

from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcdefines           import _ELcScope
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcdefines           import _ELcCompID
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcdefines           import _LcFrcView
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcexecstate         import _LcFailure
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcguard             import _LcGuard
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcdefines           import _ELcOperationModeID
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcproxydefines      import _ProxyInfo
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcproxydefines      import _TaskInfo
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcproxydefines      import _ELcOpModeBitFlag
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcproxydefines      import _ELcShutdownRequest
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcproxy             import _LcProxy

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

        _errMsg     = None
        _iImplErr   = None
        _implErrMsg = None

        if _LcProxy._singleton is not None:
            _iImplErr = 701
        elif not isinstance(lcScope_, _ELcScope):
            _iImplErr = 702
        elif not isinstance(lcGuard_, _LcGuard):
            _iImplErr = 703
        elif not isinstance(lcMon_, _LcMonitorImpl):
            _iImplErr = 704
        elif not (isinstance(startupCfg_, _FwStartupConfig) and startupCfg_._isValid):
            _iImplErr = 705

        if _iImplErr is not None:
            self.CleanUpByOwnerRequest(self._myPPass)

            _implErrMsg = _FwTDbEngine.GetText(_EFwTextID.eMisc_ImplError_Param).format(_iImplErr)
            _LcFailure.CheckSetLcSetupFailure(errMsg_=_implErrMsg)

            if _errMsg is not None:
                vlogif._LogOEC(True, -1601)
            return

        _LcProxyImpl.__bPxyInfoAvailable = False

        _tmgr = _TaskManagerImpl._GetInstance()
        if _tmgr is None:
            self.CleanUpByOwnerRequest(self._myPPass)

            if _LcFailure.IsLcErrorFree():
                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eMisc_ImplError_Param).format(707)
                _LcFailure.CheckSetLcSetupFailure(errMsg_=_errMsg)

            vlogif._LogOEC(True, -1602)
            return

        _fwMain   = None
        _tiFwMain = None
        _fwMain, _tiFwMain = _LcProxyImpl.__CreateFwMain(_tmgr, lcMon_, mainXT_=mainXT_)
        if _fwMain is None:
            self.CleanUpByOwnerRequest(self._myPPass)

            if _LcFailure.IsLcErrorFree():
                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eMisc_ImplError_Param).format(708)
                _LcFailure.CheckSetLcSetupFailure(errMsg_=_errMsg)
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
            _errMsg = _FwTDbEngine.GetText(_EFwTextID.eMisc_ImplError_Param).format(709)
            _LcFailure.CheckSetLcSetupFailure(errMsg_=_errMsg)

        elif _LogIFBase.GetInstance() is None:
            if _LogIFImpl._GetInstance(lcpxy_=self, startupCfg_=startupCfg_) is None:
                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eMisc_ImplError_Param).format(710)
                _LcFailure.CheckSetLcSetupFailure(errMsg_=_errMsg)

                vlogif._LogOEC(False, -3030)

        if _LcFailure.IsLcNotErrorFree():
            self.CleanUpByOwnerRequest(self._myPPass)


    @property
    def isLcProxyAvailable(self) -> bool:
        if self.__isInvalid:
            return False
        return not self.isLcModeShutdown

    @property
    def isLcProxyInfoAvailable(self) -> bool:
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

    @property
    def isTaskManagerApiAvailable(self):
        _tmgr = self.taskManager
        return (_tmgr is not None) and _tmgr.isTaskManagerApiAvailable

    @property
    def lcScope(self) -> _PyUnion[_ELcScope, None]:
        return None if self.__isInvalid else self.__lcScope


    @property
    def taskManager(self) -> _PyUnion[_TaskManager, None]:
        return None if self.__isUnavailable else self.__tmgr

    @property
    def curProxyInfo(self) -> _PyUnion[_ProxyInfo, None]:
        if self.__isUnavailable:
            return None
        else:
            return self.__CreateProxyInfo(self.isLcProxyInfoAvailable)


    @property
    def isLcModeNormal(self) -> bool:
        if self.__isInvalid: return False
        with self.__opModeLck:
            return _ELcOpModeBitFlag.IsNormal(self.__eOpModeBitMask)

    @property
    def isLcModePreShutdown(self) -> bool:
        if self.__isInvalid: return False
        with self.__opModeLck:
            return _ELcOpModeBitFlag.IsPreShutdown(self.__eOpModeBitMask)

    @property
    def isLcModeShutdown(self) -> bool:
        if self.__isInvalid: return False
        with self.__opModeLck:
            return _ELcOpModeBitFlag.IsShutdown(self.__eOpModeBitMask)

    @property
    def isLcModeFailureHandling(self) -> bool:
        if self.__isInvalid: return False
        with self.__opModeLck:
            return _ELcOpModeBitFlag.IsFailureHandling(self.__eOpModeBitMask)

    @property
    def isLcShutdownEnabled(self) -> bool:
        return False if self.__lcMonImpl is None else self.__lcMonImpl.isLcShutdownEnabled

    @property
    def eLcOperationModeID(self) -> _ELcOperationModeID:
        if self.__isInvalid: return _ELcOperationModeID.eIdle
        with self.__opModeLck:
            if _ELcOperationModeID.eLcCeaseMode.value < self.__eOpModeID.value < _ELcOperationModeID.eLcPreShutdown.value:
                if self.__lcMonImpl.isDummyMonitor: pass
                elif self.__lcMonImpl.isLcShutdownEnabled:
                    self.__eOpModeID = _ELcOperationModeID.eLcCeaseMode
            return _ELcOperationModeID(self.__eOpModeID.value)


    def _SetLcOperationalState(self, eLcCompID_: _ELcCompID, bStartStopFlag_: bool, atask_ : _AbstractTask) -> bool:
        if self.__isUnavailable:
            return False
        if not isinstance(eLcCompID_, _ELcCompID):
            vlogif._LogOEC(True, -1603)
            return False
        if not isinstance(eLcCompID_, _ELcCompID):
            vlogif._LogOEC(True, -1604)
            return False
        if not (isinstance(atask_, _AbstractTask) and (atask_.taskBadge is not None)):
            vlogif._LogOEC(True, -1605)
            return False
        return self.__lcGuard._SetLcOperationalState(eLcCompID_, bStartStopFlag_, atask_=atask_)

    def _NotifyLcFailure(self, eFailedCompID_ : _ELcCompID, frcError_ : _FatalEntry, atask_ : _AbstractTask =None):
        if self.__isInvalid:
            return
        if not isinstance(eFailedCompID_, _ELcCompID):
            vlogif._LogOEC(True, -1606)
            return

        bVal   = None if self.__lcMonImpl.isLcShutdownEnabled else True
        bValid = bVal is None

        self.__LockAPI(bVal)

        if not self.__lcGuard._SetLcFailure(eFailedCompID_, frcError_, atask_=atask_, bSkipReply_=bValid):
            if bVal is not None:
                self.__LockAPI(False)

    @property
    def isLcOperable(self) -> bool:
        if self.__isUnavailable: return False
        return self.__lcGuard.isLcOperable

    @property
    def isLcCoreOperable(self) -> bool:
        if self.__isInvalid: return False
        return self.__lcGuard.isLcCoreOperable

    @property
    def isLcPreCoreOperable(self) -> bool:
        if self.__isInvalid: return False
        return self.__lcGuard.isLcPreCoreOperable

    @property
    def isLcStarted(self) -> bool:
        if self.__isInvalid: return False
        return self.__lcGuard.isLcStarted

    @property
    def isTaskManagerStarted(self) -> bool:
        if self.__isInvalid: return False
        return self.__lcGuard.isTaskManagerStarted

    @property
    def isFwMainStarted(self) -> bool:
        if self.__isInvalid: return False
        return self.__lcGuard.isFwMainStarted

    @property
    def isMainXTaskStarted(self) -> bool:
        if self.__isInvalid: return False
        return self.__lcGuard.isMainXTaskStarted

    @property
    def isLcStopped(self) -> bool:
        if self.__isInvalid: return False
        return self.__lcGuard.isLcStopped

    @property
    def isTaskManagerStopped(self) -> bool:
        if self.__isInvalid: return False
        return self.__lcGuard.isTaskManagerStopped

    @property
    def isFwMainStopped(self) -> bool:
        if self.__isUnavailable: return False
        return self.__lcGuard.isFwMainStopped

    @property
    def isMainXTaskStopped(self) -> bool:
        if self.__isInvalid: return False
        return self.__lcGuard.isMainXTaskStopped

    @property
    def isLcFailed(self) -> bool:
        if self.__isInvalid: return False
        return self.__lcGuard.isLcFailed

    @property
    def isTaskManagerFailed(self) -> bool:
        if self.__isInvalid: return False
        return self.__lcGuard.isTaskManagerFailed

    @property
    def isFwMainFailed(self) -> bool:
        if self.__isInvalid: return False
        return self.__lcGuard.isFwMainFailed

    @property
    def isMainXTaskFailed(self) -> bool:
        if self.__isInvalid: return False
        return self.__lcGuard.isMainXTaskFailed

    @property
    def hasLcAnyStoppedState(self) -> bool:
        if self.__isInvalid: return False
        return self.__lcGuard.hasLcAnyStoppedState

    @property
    def hasLcAnyFailureState(self) -> bool:
        if self.__isInvalid: return False
        return self.__lcGuard.hasLcAnyFailureState

    @property
    def lcFrcView(self) -> _LcFrcView:
        if self.__isInvalid: return None
        return self.__lcGuard.lcFrcView

    def HasLcCompFRC(self, eLcCompID_: _ELcCompID, atask_: _AbstractTask = None) -> bool:
        if self.__isInvalid: return False
        return self.__lcGuard.HasLcCompFRC(eLcCompID_, atask_=atask_)

    def GetLcCompFrcView(self, eLcCompID_ : _ELcCompID, atask_ : _AbstractTask =None) -> _LcFrcView:
        if self.__isInvalid: return None
        with self.__apiLck:
            return self.__lcGuard.GetLcCompFrcView(eLcCompID_, atask_=atask_)


    def _FinalizeSetup(self):

        res = self.__fwMain.FinalizeCustomSetup()
        if not res:
            vlogif._LogOEC(False, -3031)

            if _LcFailure.IsLcErrorFree():
                _frcMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcProxyImpl_TextID_001)
                _frc    = _CreateLogImplError(_frcMsg)
                if _frc is not None:
                    self.__lcGuard._SetLcFailure(_ELcCompID.eFwMain, frcError_=_frc, atask_=self.__fwMain, bSkipReply_=True)

                if _LcFailure.IsLcErrorFree():
                    _LcFailure.CheckSetLcSetupFailure(errMsg_=_frcMsg)
        return res

    def _ProcessShutdownRequest (self, eShutdownRequest_ : _ELcShutdownRequest, eFailedCompID_ : _ELcCompID =None
                               , frcError_ : _FatalEntry =None, atask_ : _AbstractTask =None, bPrvRequestReply_ =True):

        if self.__isInvalid:
            return

        bRefresh = not bPrvRequestReply_

        if eShutdownRequest_ == _ELcShutdownRequest.eFailureHandling:
            if eFailedCompID_ is None:
                vlogif._LogOEC(True, -1607)
                if not bRefresh:
                    self.__LockAPI(False)
                return

        if bRefresh:
            self.__LockAPI(True)

        _bCurNormal          = None
        _bCurShutdown        = None
        _bCurPreShutdown     = None
        _bCurFailureHandling = None

        _bCurNormal, _bCurPreShutdown, _bCurShutdown, _bCurFailureHandling = self.__DecodeCurOperationBitmask()
        if _bCurNormal is None:
            if bRefresh:
                self.__LockAPI(False)
            return

        _bBadAction                    = None
        _bIgnoreAction                 = None
        _bPreShutdownDueToSetupFailure = None

        _bIgnoreAction, _bBadAction, _bPreShutdownDueToSetupFailure = self.__CheckShutdownActionRequest(
            eShutdownRequest_, _bCurNormal, _bCurPreShutdown, _bCurShutdown, _bCurFailureHandling)

        if _bIgnoreAction or _bBadAction:
            if bRefresh:
                self.__LockAPI(False)

            if _bBadAction:
                vlogif._LogOEC(True, -1608)
            return

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
                vlogif._LogOEC(True, -1609)
                return

            if eShutdownRequest_.isFailureHandling:
                _lstNewOpModes.append(_ELcOpModeBitFlag.ebfLcPreShutdown)

                _lcCompID = eFailedCompID_

        else:
            if not eShutdownRequest_.isShutdown:
                vlogif._LogOEC(True, -1610)
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

    def _StopFwMain(self):
        if self.__isInvalid:
            return

        self.__tmgr._InjectLcProxy(None)
        if self.__fwMain.isRunning:
            _semStop = None if self.__fwMain.isEnclosingPyThread else _BinarySemaphore(take_=True)
            self.__fwMain.StopFwMain(semStop_=_semStop)
            if _semStop is not None:
                _semStop.CleanUp()

    def _JoinFwMain(self, mainXTUID_ : int =None) -> list:
        if self.__isInvalid:
            return None

        _lcg       = self.__lcGuard
        _myLcState = _lcg._GetLcState(bypassApiLock_=True)

        if mainXTUID_ is not None:
            if not _lcg.isMainXTaskFailed:
                teXU = self.__tmgr._GetTaskError(mainXTUID_)

                if (teXU is not None) and teXU.isFatalError:
                    fee = teXU._currentErrorEntry
                    _lcg._SetLcFailure(_ELcCompID.eMainXTask, fee, atask_=None, bSkipReply_=True)

                elif _myLcState.isMainXTaskStarted:
                    _lcg._SetLcOperationalState(_ELcCompID.eMainXTask, False, atask_=None)

        if not _lcg.isFwMainFailed:
            teMain = self.__fwMain.taskError

            if (teMain is not None) and teMain.isFatalError:
                fee = teMain._currentErrorEntry
                _lcg._SetLcFailure(_ELcCompID.eFwMain, fee, atask_=None, bSkipReply_=True)
            elif _myLcState.isFwMainStarted:
                _lcg._SetLcOperationalState(_ELcCompID.eFwMain, False, atask_=None)

        if self.__fwMain.isEnclosingStartupThread:
            pass
        else:
            self.__fwMain.JoinTask()

        res = self.__tmgr._StopAllTasks(bCleanupStoppedTasks_=True, lstSkipTaskIDs_=[self.__fwMain.taskID])
        return res

    def _SyncStarFwMainByAsynStartup(self):

        _errMsg   = None
        _iImplErr = None

        if _LcFailure.IsLcNotErrorFree():
            _iImplErr = 741
        elif self.__fwMain.isEnclosingPyThread:
            _iImplErr = 743
        elif self.__isUnavailable:
            _iImplErr = 744
        elif not ((self.__fwMain.linkedExecutable is None) or self.__fwMain.linkedExecutable.isRunnable):
            _iImplErr = 745

        if _iImplErr is not None:
            res     = False
            _errMsg = _FwTDbEngine.GetText(_EFwTextID.eMisc_ImplError_Param).format(_iImplErr)
            _LcFailure.CheckSetLcSetupFailure(errMsg_=_errMsg)

            if _errMsg is not None:
                vlogif._LogOEC(True, -1611)
        else:
            _ss = None if self.__fwMain.isEnclosingPyThread else _BinarySemaphore(take_=True)
            res = self.__fwMain.StartFwMain(_ss)

            if _ss is not None:
                _ss.CleanUp()

            res = res and self.__fwMain.isRunning
            if not res:
                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eMisc_ImplError_Param).format(746)
                _LcFailure.CheckSetLcSetupFailure(errMsg_=_errMsg)

                vlogif._LogOEC(False, -3032)
            else:
                eOpMode = _ELcOpModeBitFlag.ebfLcNormal
                self.__UpdateLcOperationBitMask(eOpMode)
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
        return (self.__apiLck is None) or self.isLcModeShutdown

    @property
    def __curOperationMode2Str(self):
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

        _midPart = _EFwTextID.eMisc_Async
        _midPart = _FwTDbEngine.GetText(_midPart)
        _fwMain = _FwMain(lcMon_)

        _bFwOK = _LcFailure.IsLcErrorFree()
        _bFwOK = _bFwOK and (vlogif._GetFirstFatalError() is None)  

        _myTskBadge = _fwMain.taskBadge if _bFwOK else None

        _bFwOK = _bFwOK and _myTskBadge is not None
        _bFwOK = _bFwOK and _myTskBadge.isFwMain
        _bFwOK = _bFwOK and _myTskBadge.isFwTask

        if not _bFwOK:
            if _LcFailure.IsLcErrorFree():
                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eMisc_ImplError_Param).format(731)
                _LcFailure.CheckSetLcSetupFailure(errMsg_=_errMsg)

            if _myTskBadge is None:
                vlogif._LogOEC(False, -3033)
            else:
                vlogif._LogOEC(True, -1612)

        elif _myTskBadge.isEnclosingPyThread:
            _bFwOK = False
            _errMsg = _FwTDbEngine.GetText(_EFwTextID.eMisc_ImplError_Param).format(732)
            _LcFailure.CheckSetLcSetupFailure(errMsg_=_errMsg)

            vlogif._LogOEC(True, -1613)

        else:
            _bFwOK = _bFwOK and _myTskBadge.hasDieXcpTargetTaskRight and _myTskBadge.hasErrorObserverTaskRight
            _bFwOK = _bFwOK and (_myTskBadge.hasDieExceptionDelegateTargetTaskRight or False) 
            if not _bFwOK:
                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eMisc_ImplError_Param).format(733)
                _LcFailure.CheckSetLcSetupFailure(errMsg_=_errMsg)

                vlogif._LogOEC(True, -1614)

            else:
                _bFwOK = tmgr_._AddTaskEntry(_fwMain, removeAutoEnclosedTaskEntry_=True)
                if not _bFwOK:
                    _errMsg = _FwTDbEngine.GetText(_EFwTextID.eMisc_ImplError_Param).format(734)
                    _LcFailure.CheckSetLcSetupFailure(errMsg_=_errMsg)

                    vlogif._LogOEC(True, -1615)

            if _bFwOK:
                _mm = _Mutex()
                _tiFwMain = _TaskInfo(_fwMain, _mm)
                _bFwOK = not _tiFwMain._isInvalid
                if not _bFwOK:
                    _tiFwMain.CleanUp()
                    _mm.CleanUp()

                    _errMsg = _FwTDbEngine.GetText(_EFwTextID.eMisc_ImplError_Param).format(735)
                    _LcFailure.CheckSetLcSetupFailure(errMsg_=_errMsg)

                    vlogif._LogOEC(True, -1616)

        if not _bFwOK:
            if _LcFailure.IsLcErrorFree():
                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eMisc_ImplError_Param).format(736)
                _LcFailure.CheckSetLcSetupFailure(errMsg_=_errMsg)

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

        ctInst = self.__tmgr._GetCurTask(bAutoEncloseMissingThread_=True)

        if not bPxyInfoAvail_:
            res = None

        elif ctInst is None:
            res = None
            vlogif._LogOEC(True, -1617)

        else:
            res = _ProxyInfo(ctInst, self.__tiFwMain)
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
                    _myTskInst._CreateCeaseTLB(bAborting_=_myTskInst.isAborting)

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
                prvm = self.__eOpModeID
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
                        vlogif._LogOEC(True, -1618)
                elif not (_bPreShutdown or _bShutdown or _bFailureHandling):
                    if self.__eOpModeBitMask.value != _ELcOpModeBitFlag.ebfIdle.value:
                        bImplErr = True
                        vlogif._LogOEC(True, -1619)
                elif _bPreShutdown and _bShutdown:
                    bImplErr = True
                    vlogif._LogOEC(True, -1620)

                if bImplErr:
                    _bNormal, _bPreShutdown, _bShutdown, _bFailureHandling = None, None, None, None
        return _bNormal, _bPreShutdown, _bShutdown, _bFailureHandling
