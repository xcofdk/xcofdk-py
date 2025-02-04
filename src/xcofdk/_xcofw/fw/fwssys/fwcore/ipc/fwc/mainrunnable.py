# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : mainrunnable.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from xcofdk._xcofw.fw.fwssys.fwcore.logging               import logif
from xcofdk._xcofw.fw.fwssys.fwcore.logging               import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.base.gtimeout         import _Timeout
from xcofdk._xcofw.fw.fwssys.fwcore.base.util             import _Util
from xcofdk._xcofw.fw.fwssys.fwcore.base.timeutil         import _TimeAlert
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.atask         import _AbstractTask
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil      import _TaskUtil
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.execprofile   import _ExecutionProfile
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.arunnabledefs import _ERunProgressID
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.arunnable     import _AbstractRunnable
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.arunnable     import _EErrorHandlerCallbackID
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.arunnable     import _FatalEntry
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.arunnable     import _ETernaryOpResult
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.arunnablefwc  import _AbstractRunnableFWC
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.arunnabledefs import _ERunnableType
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.arunnabledefs import _EFwcID
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.arunnabledefs import _ERunnableApiID
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcdefines          import _ELcCompID
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcproxydefines     import _ELcShutdownRequest
from xcofdk._xcofw.fw.fwssys.fwcore.lcmon.lcmonimpl       import _LcMonitorImpl
from xcofdk._xcofw.fw.fwssys.fwcore.lcmon.lcmonimpl       import _TlbSummary
from xcofdk._xcofw.fw.fwssys.fwcore.lcmon.lcshutdowncoord import _LcShutdownCoordinator
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject         import _AbstractSlotsObject

from xcofdk._xcofw.fw.fwssys.fwerrh.fwerrorcodes import _EFwErrorCode

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine

from xcofdk._xcofwa.fwadmindefs import _FwSubsystemCoding

if not _FwSubsystemCoding.IsSubsystemMessagingConfigured():
    _FwDispatcher = object
else:
    from xcofdk._xcofw.fw.fwssys.fwcore.ipc.fwc.fwdispatcher import _FwDispatcher

class _MainRunnable(_AbstractRunnableFWC):

    __slots__ = [ '__fwcDict'  , '__lcMonImpl' , '__lstPFFE'  , '__mtxData'
                , '__eRunProg' , '__bACS'      , '__bCSDbyMR' , '__tlbSum' ]

    __LOG_ALERT_TIMESPAN_MS         = 3000
    __mandatoryCustomApiMethodNames = [ _ERunnableApiID.ePrepareCeasing.functionName
                                      , _ERunnableApiID.eRunCeaseIteration.functionName
                                      , _ERunnableApiID.eProcFwcErrorHandlerCallback.functionName
                                      ]

    def __init__(self, lcMon_ : _LcMonitorImpl):
        _AbstractSlotsObject.__init__(self)

        self.__bACS      = None
        self.__tlbSum    = None
        self.__fwcDict   = None
        self.__mtxData   = None
        self.__eRunProg  = None
        self.__bCSDbyMR  = None
        self.__lcMonImpl = None

        self.__lstPFFE = None

        if not (isinstance(lcMon_, _LcMonitorImpl) and lcMon_.isValid and not lcMon_.isDummyMonitor):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00066)
            return

        if not ((_AbstractRunnableFWC.GetDefinedFwcNum() > 0) and _AbstractRunnableFWC.IsDefinedFwc(_EFwcID.eFwMain)):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00067)
            return

        mmn = _MainRunnable.GetMandatoryCustomApiMethodNamesList()
        if _Util.GetNumAttributes(self, mmn, bThrowx_=True) != len(mmn):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00068)
            return

        _toutAlert = _Timeout.CreateTimeoutMS(_MainRunnable.__LOG_ALERT_TIMESPAN_MS)
        _logAlert = _TimeAlert(_toutAlert.toNSec)
        _toutAlert.CleanUp()

        _xp = _ExecutionProfile(bLcMonitor_=True)

        _AbstractRunnableFWC.__init__(self, _ERunnableType.eFwMainRbl, excludedRblM_=None, runLogAlert_=_logAlert, execProfile_=_xp)
        _xp.CleanUp()

        _mtxDataMe = _AbstractRunnable._GetDataMutex(self)
        if (self._eRunnableType is None) or (_mtxDataMe is None):
            self.CleanUp()
        elif not self.__CreateFWCs():
            self.__CleanUpFWCs()
            self.CleanUp()

        if (self._eRunnableType != _ERunnableType.eFwMainRbl) or (_mtxDataMe is None):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00069)
            return

        self.__tlbSum    = _TlbSummary()
        self.__mtxData   = _mtxDataMe
        self.__lstPFFE   = []
        self.__bCSDbyMR  = True
        self.__lcMonImpl = lcMon_

    def _ToString(self, *args_, **kwargs_):
        return _AbstractRunnableFWC._ToString(self, *args_, **kwargs_)

    def _CleanUp(self):
        self.__CleanUpPFFEList()

        super()._CleanUp()
        self.__bACS      = None
        self.__tlbSum    = None
        self.__fwcDict   = None
        self.__mtxData   = None
        self.__lstPFFE   = None
        self.__eRunProg  = None
        self.__bCSDbyMR  = None
        self.__lcMonImpl = None

    def ProcessShutdownAction(self, eShutdownAction_: _ELcShutdownRequest, eFailedCompID_: _ELcCompID =None, frcError_: _FatalEntry =None, atask_: _AbstractTask =None):

        if self._isInvalid:
            return

        if eFailedCompID_ is not None:
            _tuname   = 'None' if atask_ is None else atask_.taskUniqueName
            _tailPart = ': eFailedCompID={} task={} [{}] - {}'.format(eFailedCompID_.compactName, _tuname, frcError_.uniqueID, frcError_.shortMessage)
        else:
            _tailPart = '.'

        if not eShutdownAction_.isShutdown:
            self.__EnableCoordinatedShutdown()

            if eFailedCompID_ is None:

                self._ProcEuErrors(bCheckForFatalErrorsOnly_=True)
                self.__ProcFFErrors(bIgnoreFeasibility_=True)

        _bAborting = _ETernaryOpResult.MapExecutionState2TernaryOpResult(self).isAbort

        if not self._isInLcCeaseMode:
            self._CreateCeaseTLB(bEnding_=_bAborting)
        else:
            self._UpdateCeaseTLB(_bAborting)

    @property
    def _lcMonitorImpl(self) -> _LcMonitorImpl:
        return self.__lcMonImpl

    @property
    def _isAwaitingCustomSetup(self):
        if self._isInvalid:
            return False
        if self.__bACS is None:
            return False
        with self.__mtxData:
            return self.__bACS

    @property
    def _isCustomSetupDone(self):
        if self._isInvalid:
            return True
        if self.__bACS is None:
            return True

        with self.__mtxData:
            if self.__bACS:
                res = False
            elif self.__fwcDict is None:
                res = True
            else:
                _keys = list(self.__fwcDict.keys())
                _keys.sort(reverse=True)
                for _kk in _keys:
                    _fwcID = _EFwcID(_kk)
                    fwc = self.__GetFwc(_fwcID)
                    res = fwc.isRunning
                    if not res:
                        break
            return res

    @property
    def _isCustomSetupFailed(self):
        if self._isInvalid:
            return False
        if self.__bACS is None:
            return False
        if self._isAwaitingCustomSetup:
            return False
        return not self._isCustomSetupDone

    def _GetStoredFFEsList(self) -> list:
        return self.__lstPFFE

    def _CheckStoredFFEsOnPendingStatus(self):
        _lstPFFE = self.__lstPFFE

        if (_lstPFFE is None) or (len(_lstPFFE) < 1):
            return

        _bChanged = False
        for _ii in range(len(_lstPFFE)):
            _myFE = _lstPFFE[_ii]
            if _myFE.isInvalid or not _myFE.isPendingResolution:
                _bChanged = True
                _lstPFFE[_ii] = None
                if not _myFE.hasNoImpactDueToFrcLinkage:
                    _myFE._ForceCleanUp()
        if _bChanged:
            _lstUpdate = [_myFE for _myFE in _lstPFFE if _myFE is not None]
            _lstPFFE.clear()
            if len(_lstUpdate) > 0:
                _lstPFFE += _lstUpdate
            self.__lstPFFE = _lstPFFE

    @staticmethod
    def _GetMandatoryCustomApiMethodNamesList():
        ret = []
        _tmp = _AbstractRunnableFWC._GetMandatoryCustomApiMethodNamesList()
        if _tmp is not None:
            ret += _tmp
        ret += _MainRunnable.__mandatoryCustomApiMethodNames
        return ret

    def _RunExecutable(self):
        if (self.__lcMonImpl is None) or self.__lcMonImpl.isLcShutdownEnabled:
            return False

        if self.__lcMonImpl.isLcMonitorIdle:
            self.__lcMonImpl._ActivateLcMonitorAlivenessByMR(self._executionProfile.runPhaseFreqMS)

        _opr = self.__ProcFFErrors()
        if not _opr.isContinue:
            res = None if _opr.isAbort else False
        else:
            res = self.isRunning
            if res:

                self.__lcMonImpl._Update(tlbSum_=self.__tlbSum)
                _lsaReportStr = self.__tlbSum.lifeSignAlarmReport
                if _lsaReportStr is not None:
                    logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_MainRunnable_TextID_001).format(_lsaReportStr))
        return res

    def _ProcessInternalMsg(self, msg_, callback_ =None):
        if callback_ is not None:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00070)
            return None
        return self.isRunning

    def _ProcessExternalMsg(self, msg_, callback_ =None):
        if callback_ is not None:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00071)
            return None
        return self.isRunning

    def _SetUpRunnable(self):
        return True

    def _TearDownRunnable(self):
        return False

    def _OnRunProgressNotification(self, eRunProgressID_ : _ERunProgressID):

        _RUN_PROGRESS_NOTIF_RESULT__OK    = True
        _RUN_PROGRESS_NOTIF_RESULT__NOK   = not _RUN_PROGRESS_NOTIF_RESULT__OK
        _RUN_PROGRESS_NOTIF_RESULT__ABORT = None

        if not self._PcIsLcOperable():
            return _RUN_PROGRESS_NOTIF_RESULT__ABORT

        if not isinstance(eRunProgressID_, _ERunProgressID):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00072)
            return _RUN_PROGRESS_NOTIF_RESULT__ABORT

        if (eRunProgressID_.value < _ERunProgressID.eReadyToRun) or (eRunProgressID_.value > _ERunProgressID.eRunDone):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00073)
            return _RUN_PROGRESS_NOTIF_RESULT__ABORT

        res = _RUN_PROGRESS_NOTIF_RESULT__OK

        self.__eRunProg = _ERunProgressID(eRunProgressID_.value)

        if eRunProgressID_.isReadyToRun:
            if self.__lcMonImpl.isLcMonitorIdle:
                self.__lcMonImpl._ActivateLcMonitorAlivenessByMR(self._executionProfile.runPhaseFreqMS)

            while not self._PcIsLcProxyModeNormal():
                _TaskUtil.SleepMS(20)
                if self.__lcMonImpl.isLcShutdownEnabled:
                    break

            if self.__lcMonImpl.isLcShutdownEnabled:
                res = _RUN_PROGRESS_NOTIF_RESULT__NOK
            elif not self.__StartFWCs():
                res = _RUN_PROGRESS_NOTIF_RESULT__ABORT

        elif eRunProgressID_.isExecuteSetupDone:
            pass

        elif eRunProgressID_.isExecuteRunDone:
            pass

        elif eRunProgressID_.isExecuteTeardownDone:
            pass

        return res

    def _ProcFwcErrorHandlerCallback( self
                                    , eCallbackID_           : _EErrorHandlerCallbackID
                                    , curFatalError_         : _FatalEntry               =None
                                    , lstForeignFatalErrors_ : list                     =None) -> _ETernaryOpResult:
        res = self.__CheckProcessingFeasiblity(eCallbackID_=eCallbackID_, curFatalError_=curFatalError_)
        if not res.isContinue:
            return res

        if not eCallbackID_.isProcessObservedForeignFatalErrors:
            self.__NotifyLcFailure(_ELcCompID.eFwMain, curFatalError_, self._drivingTask)
            res = _ETernaryOpResult.MapExecutionState2TernaryOpResult(self)
        else:
            res = self.__ProcFFErrors(lstFFErrors_=lstForeignFatalErrors_, bOnErrHdlrCallback_=True)

        return res

    def _PrepareCeasing(self):
        if (self.__lcMonImpl is None) or not self.__lcMonImpl.isValid:
            return
        if not self._isInLcCeaseMode:
            return

        if not self.__lcMonImpl.isLcShutdownEnabled:
            pass 
        elif not self.__lcMonImpl._isCoordinatedShutdownManagedByMR:
            pass 
        else:
            self.__ExecuteShutdownSequence()

        _AbstractRunnable._ExecuteTeardown(self)

        self._lcCeaseTLB.UpdateCeaseState(True)

    def _RunCeaseIteration(self):
        pass

    @property
    def __isCoordinatingShutdown(self):
        if self._isInvalid:
            return False
        with self.__mtxData:
            return (self.__bCSDbyMR is not None) and self.__bCSDbyMR

    def __CheckDeactivateCoordinatedShutdownByMR(self):

        if self._isInvalid:
            return
        if self.__bCSDbyMR is None:
            return

        with self.__mtxData:
            if self.__lcMonImpl.isLcShutdownEnabled:
                pass

            elif self.__bCSDbyMR:
                self.__bCSDbyMR = False

    def __EnableCoordinatedShutdown(self):
        if (self.__lcMonImpl is None) or not self.__lcMonImpl.isValid:
            return
        elif self.__lcMonImpl.isLcShutdownEnabled:
            return

        if not self.__lcMonImpl.isLcMonitorAlive:
            _bByMR = False
            self.__bCSDbyMR = False
        elif not self.__isCoordinatingShutdown:
            _bByMR = False
        else:
            _bByMR = True

        self.__lcMonImpl._EnableCoordinatedShutdown(bManagedByMR_=_bByMR)

        if not self.__lcMonImpl._isCoordinatedShutdownManagedByMR:
            if self.__isCoordinatingShutdown:
                with self.__mtxData:
                    self.__bCSDbyMR = False

    def __CreateFWCs(self):
        if _AbstractRunnableFWC.GetDefinedFwcNum() < 2:
            self.__bACS = True
            return True

        if not _FwSubsystemCoding.IsSubsystemMessagingConfigured():
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00074)
            return False

        res, self.__fwcDict = False, {}

        _fwcID  = _EFwcID.eFwDispatcher
        if _AbstractRunnableFWC.IsDefinedFwc(_fwcID):
            _FwDispatcher._GetInstance(bCreate_=True)
            comp = _AbstractRunnableFWC.GetFwcInstance(_fwcID)

            res = comp is not None
            res = res and _AbstractRunnableFWC.IsActiveFwc(_fwcID)
            res = res and self.__AddFwc(_fwcID, comp)
            if not res:
                if comp is not None:
                    comp.CleanUp()
                return False

        if res:
            self.__bACS = True
        return True

    def __StartFWCs(self):

        if _AbstractRunnableFWC.GetDefinedFwcNum() < 2:
            with self.__mtxData:
                self.__bACS = False
            return True

        res = False
        _keys = list(self.__fwcDict.keys())
        _keys.sort(reverse=False)
        for _kk in _keys:
            _fwcID  = _EFwcID(_kk)
            _vv = self.__fwcDict[_kk]

            res = _vv.Start()
            if not res:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00075)
                break

            res = _vv.isRunning
            if not res:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00076)
                break

        if res:
            if _FwSubsystemCoding.IsSubsystemMessagingConfigured():
                _rblDisp = self.__GetFwc(_EFwcID.eFwDispatcher)
                if _rblDisp is not None:
                    for _kk in _keys:
                        _fwcID = _EFwcID(_kk)
                        if _fwcID.isFwDispatcher:
                            continue

                        _vv = self.__fwcDict[_kk]
                        if not _vv.isProvidingExternalQueue:
                            continue

        if not res:
            for _kk in _keys:
                _vv = self.__fwcDict[_kk]
                if _vv.isRunning:
                    _fwcID = _EFwcID(_kk)
                    _vv.Stop()

        with self.__mtxData:
            self.__bACS = False
        return res

    def __CleanUpFWCs(self):
        if (self.__fwcDict is None) or len(self.__fwcDict) == 0:
            self.__fwcDict = None
            return

        _keys = list(self.__fwcDict.keys())
        _keys.sort(reverse=True)
        for _kk in _keys:
            _vv = self.__fwcDict.pop(_kk)
            _vv.CleanUp()

        self.__fwcDict.clear()
        self.__fwcDict = None

    def __GetFwc(self, eFwcID_ :  _EFwcID) -> _AbstractRunnableFWC:
        res = None
        if self.__fwcDict is None:
            pass
        elif not eFwcID_.value in self.__fwcDict:
            pass
        else:
            res = self.__fwcDict[eFwcID_.value]
        return res

    def __AddFwc(self, eFwcID_ :  _EFwcID, fwc_ : _AbstractRunnableFWC):
        if not (isinstance(eFwcID_,  _EFwcID) and isinstance(fwc_, _AbstractRunnableFWC)):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00077)
            return False
        elif eFwcID_.value in self.__fwcDict:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00078)
            return False
        self.__fwcDict[eFwcID_.value] = fwc_
        return True

    def __NotifyLcFailure(self, eFailedCompID_ : _ELcCompID, frcError_ : _FatalEntry, atask_ : _AbstractTask):
        self._PcNotifyLcFailure(eFailedCompID_, frcError_, atask_=atask_)
        if not self.__lcMonImpl.isLcShutdownEnabled:
            self.__EnableCoordinatedShutdown()

    def __CheckProcessingFeasiblity(self, eCallbackID_ : _EErrorHandlerCallbackID =None, curFatalError_ : _FatalEntry =None) -> _ETernaryOpResult:
        if self._isInvalid:
            return _ETernaryOpResult.Abort()

        _bFE   = curFatalError_ is not None
        _bEHCB = eCallbackID_ is not None

        if _bFE and not _bEHCB:
            _wmsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_MainRunnable_TextID_002).format(str(curFatalError_))
            _frc = logif._CreateLogImplErrorEC(_EFwErrorCode.FE_00026, _wmsg)
            self.__NotifyLcFailure(_ELcCompID.eFwMain, _frc, self._drivingTask)
            return _ETernaryOpResult.MapExecutionState2TernaryOpResult(self)

        if _bEHCB:
            if not (eCallbackID_.isAbortTaskDueToUnexpectedCall or eCallbackID_.isFwMainSpecificCallbackID):
                _wmsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_MainRunnable_TextID_003).format(eCallbackID_.compactName)
                _frc = logif._CreateLogImplErrorEC(_EFwErrorCode.FE_00027, _wmsg)
                self.__NotifyLcFailure(_ELcCompID.eFwMain, _frc, self._drivingTask)
                return _ETernaryOpResult.MapExecutionState2TernaryOpResult(self)

        _ePF = self._GetProcessingFeasibility(errEntry_=curFatalError_)
        if not _ePF.isFeasible:
            res = _ETernaryOpResult.MapExecutionState2TernaryOpResult(self)
            return res

        _bStopInstantly        = False
        _bHasLcAnyFailureState = self._PcHasLcAnyFailureState()

        if _bHasLcAnyFailureState:

            _frcv = self._PcGetLcFrcView()
            _frcPart = str(None) if _frcv is None else _frcv.ToString(bVerbose_=False)

            if _frcv is not None:
                _frcv.CleanUp()

        elif not self.__lcMonImpl.isLcMonitorAlive:
            _bStopInstantly = True

        if _bStopInstantly:
            _bAborting = self.isAborting or self._isInLcCeaseMode

            self.__CheckDeactivateCoordinatedShutdownByMR()
            res = _ETernaryOpResult.Abort() if _bAborting else _ETernaryOpResult.Stop()
        elif _bHasLcAnyFailureState:
            res = _ETernaryOpResult.Stop()
        else:
            res = _ETernaryOpResult.Continue()

        return res

    def __ProcFFErrors(self, lstFFErrors_ : list =None, bOnErrHdlrCallback_ =False, bIgnoreFeasibility_ =False) -> _ETernaryOpResult:

        if bOnErrHdlrCallback_:
            pass
        elif not bIgnoreFeasibility_:
            res = self.__CheckProcessingFeasiblity()
            if not res.isContinue:
                return _ETernaryOpResult.MapExecutionState2TernaryOpResult(self)

        if self.__lstPFFE is None:
            _wmsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_MainRunnable_TextID_005)
            _frc = logif._CreateLogImplErrorEC(_EFwErrorCode.FE_00028, _wmsg)
            self.__CheckDeactivateCoordinatedShutdownByMR()
            self.__NotifyLcFailure(_ELcCompID.eFwMain, _frc, self._drivingTask)
            return _ETernaryOpResult.MapExecutionState2TernaryOpResult(self)

        if bOnErrHdlrCallback_:
            _NUM = len(self.__lstPFFE)

            if _NUM > 0:
                _wmsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_MainRunnable_TextID_006).format(_NUM)
                _frc = logif._CreateLogImplErrorEC(_EFwErrorCode.FE_00029, _wmsg)
                self.__CheckDeactivateCoordinatedShutdownByMR()
                self.__NotifyLcFailure(_ELcCompID.eFwMain, _frc, self._drivingTask)
                return _ETernaryOpResult.MapExecutionState2TernaryOpResult(self)

            if lstFFErrors_ is not None:
                self.__lstPFFE += lstFFErrors_

            return _ETernaryOpResult.MapExecutionState2TernaryOpResult(self)

        self._CheckStoredFFEsOnPendingStatus()

        _NUM = len(self.__lstPFFE)

        if _NUM > 0:
            _lstCandid = self.__CheckStoredFFEsOnLcFailureCandidacy()

            if _lstCandid is not None:
                for _myFE in _lstCandid:
                    if not _myFE.isInvalid:
                        _atsk = _myFE._taskInstance
                        if (_atsk is None) or not _atsk.isValid:
                            _eCID = _ELcCompID.eMiscComp
                            _atsk = self._drivingTask
                        else:
                            _eCID = _atsk.GetLcCompID()
                        self.__NotifyLcFailure(_eCID, _myFE, _atsk)
                    _myFE._ForceCleanUp()
                _lstCandid.clear()

        return _ETernaryOpResult.MapExecutionState2TernaryOpResult(self)

    def __CheckStoredFFEsOnLcFailureCandidacy(self) -> list:
        _lstPFFE         = self.__lstPFFE
        _lstCleanup      = []
        _bDimModeEnabled = logif._IsFwDieModeEnabled()

        res  = []

        for _ii in range(len(_lstPFFE)):
            _myFE = _lstPFFE[_ii]
            _myMtx = _myFE._LockInstance()

            if _myFE.isInvalid or not _myFE.isPendingResolution:
                _lstPFFE[_ii] = None
                _lstCleanup.append(_myFE)
                if _myMtx is not None: _myMtx.Give()
                continue

            _ti = _myFE._taskInstance

            if (_ti is None) or not _ti.isValid:
                _fec = _myFE.Clone()
                if _fec is not None:
                    res.append(_fec)

                _lstPFFE[_ii] = None
                _lstCleanup.append(_myFE)
                if _myMtx is not None: _myMtx.Give()
                continue

            if _bDimModeEnabled:
                if not _ti.taskBadge.hasUnitTestTaskRight:
                    _fec = _myFE.Clone()
                    if _fec is not None:
                        res.append(_fec)

                    _lstPFFE[_ii] = None
                    _lstCleanup.append(_myFE)
                    if _myMtx is not None: _myMtx.Give()
                    continue

            _bTaskMissedToResolveFE = _ti.eTaskXPhase != _myFE.eTaskXPhase  
            if not _bTaskMissedToResolveFE:
                _bTaskMissedToResolveFE = _ti.euRNumber != _myFE.euRNumber        
                if not _bTaskMissedToResolveFE:
                    _bTaskMissedToResolveFE = not _ti.isRunning                   

            if _bTaskMissedToResolveFE:
                if not (_myFE.isInvalid or not _myFE.isPendingResolution):
                    _fec = _myFE.Clone()
                    if _fec is not None:
                        res.append(_fec)

                _lstPFFE[_ii] = None
                _lstCleanup.append(_myFE)
                if _myMtx is not None: _myMtx.Give()
                continue

            else:
                if _myMtx is not None: _myMtx.Give()
                continue

        _lstUpdate = [_myFE for _myFE in _lstPFFE if _myFE is not None]
        _lstPFFE.clear()
        if len(_lstUpdate) > 0:
            _lstPFFE += _lstUpdate
        self.__lstPFFE = _lstPFFE

        for _myFE in _lstCleanup:
            if _myFE.hasNoImpactDueToFrcLinkage:
                _myFE._ForceCleanUp()
        _lstCleanup.clear()

        if len(res) == 0:
            res = None

        return res

    def __CleanUpPFFEList(self):
        if self._isInvalid:
            return
        if self.__lstPFFE is None:
            return

        with self.__mtxData:
            for _ee in self.__lstPFFE:
                _ee._ForceCleanUp()
            self.__lstPFFE.clear()
            self.__lstPFFE = None

    def __ExecuteShutdownSequence(self):
        _sdCoord = _LcShutdownCoordinator(self.__lcMonImpl)

        _sdCoord._ExecuteCoordinatedCeasingGate()

        if self.__lcMonImpl.isCoordinatedShutdownRunning:
            _sdCoord._ExecuteCoordinatedPreShutdownGate()

        if self.__lcMonImpl.isCoordinatedShutdownRunning:
            _sdCoord._ExecuteCoordinatedShutdownGate()

        self.__lcMonImpl._StopCoordinatedShutdown()
        logif._LogKPI(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_MainRunnable_TextID_007))

    def __StartCoordinatedShutdown(self):
        _sdCoord = _LcShutdownCoordinator(self.__lcMonImpl)
        _sdCoord._ExecuteCoordinatedCeasingGate()
