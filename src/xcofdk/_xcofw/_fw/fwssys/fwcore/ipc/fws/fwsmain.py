# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwsmain.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from _fw.fwssys.fwcore.logging             import logif
from _fw.fwssys.fwcore.logging             import vlogif
from _fw.fwssys.fwcore.ipc.tsk.afwtask     import _AbsFwTask
from _fw.fwssys.fwcore.ipc.tsk.taskutil    import _TaskUtil
from _fw.fwssys.fwcore.ipc.fws.fwsmainbase import _FwsMainBase
from _fw.fwssys.fwcore.ipc.rbl.arbldefs    import _ERunProgressID
from _fw.fwssys.fwcore.ipc.rbl.arunnable   import _AbsRunnable
from _fw.fwssys.fwcore.ipc.rbl.arunnable   import _EPcErrHandlerCBID
from _fw.fwssys.fwcore.ipc.rbl.arunnable   import _EExecutionCmdID
from _fw.fwssys.fwcore.lc.lcdefines        import _ELcCompID
from _fw.fwssys.fwcore.lc.lcproxydefines   import _ELcSDRequest
from _fw.fwssys.fwcore.lc.lcmn.lcmonimpl   import _LcMonitorImpl
from _fw.fwssys.fwcore.lc.lcmn.lcmonimpl   import _TlbSummary
from _fw.fwssys.fwcore.lc.lcmn.lcsdc       import _LcSDCoordinator
from _fw.fwssys.fwcore.types.commontypes   import override
from _fw.fwssys.fwcore.types.aobject       import _AbsSlotsObject
from _fw.fwssys.fwcore.types.commontypes   import _CommonDefines
from _fw.fwssys.fwerrh.fwerrorcodes        import _EFwErrorCode
from _fw.fwssys.fwerrh.logs.errorlog       import _FatalLog

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _FwsMain(_FwsMainBase):
    __slots__ = [ '__p' , '__s' , '__bM' , '__mi' ]

    def __init__(self, lcMon_ : _LcMonitorImpl):
        _AbsSlotsObject.__init__(self)

        self.__s  = None
        self.__p  = None
        self.__bM = None
        self.__mi = None

        if not (isinstance(lcMon_, _LcMonitorImpl) and lcMon_.isValid and not lcMon_.isDummyMonitor):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00066)
            return

        super().__init__()
        if self._isInvalid:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00069)
            return

        self.__s  = _TlbSummary()
        self.__p  = []
        self.__bM = True
        self.__mi = lcMon_

    @override
    def _ToString(self, bVerbose_ =False, annex_ : str =None):
        return _FwsMainBase._ToString(self, bVerbose_, annex_)

    @override
    def _CleanUp(self):
        self.__CleanUpPFFEList()

        _FwsMainBase._CleanUp(self)
        self.__s  = None
        self.__p  = None
        self.__bM = None
        self.__mi = None

    def ProcessShutdownAction(self, eShutdownAction_: _ELcSDRequest, eFailedCompID_: _ELcCompID =None, frcError_: _FatalLog =None, atask_: _AbsFwTask =None):
        if self._isInvalid:
            return

        if not eShutdownAction_.isShutdown:
            self.__EnableCoordinatedShutdown()
            if eFailedCompID_ is None:
                self._ProcErrors(bCheckForFEOnly_=True)
                self.__ProcFFErrors(bIgnoreFeasibility_=True)
        _bAborting = _EExecutionCmdID.MapExecState2ExecCmdID(self).isAbort

        if not self._isInLcCeaseMode:
            self._CreateCeaseTLB(bEnding_=_bAborting)
        else:
            self._UpdateCeaseTLB(_bAborting)

    @property
    def _lcMonitorImpl(self) -> _LcMonitorImpl:
        return self.__mi

    def _GetStoredFFEsList(self) -> list:
        return self.__p

    def _CheckSFFEsPS(self):
        _lstPFFE = self.__p

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
            self.__p = _lstPFFE

    def _RunExecutable(self):
        if (self.__mi is None) or self.__mi.isLcShutdownEnabled:
            return False

        if self.__mi.isLcMonitorIdle:
            self.__mi._ActivateLcMonitorAlivenessByMR(self._xcard.runPhaseFreqMS)

        _opr = self.__ProcFFErrors()
        if not _opr.isContinue:
            res = None if _opr.isAbort else False
        else:
            res = self.isRunning
            if res:
                self.__mi._Update(tlbSum_=self.__s)
                _lsaReportStr = self.__s.lifeSignAlarmReport
                if _lsaReportStr is not None:
                    logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwsMain_TID_001).format(_lsaReportStr))
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

    def _OnRunProgressNotification(self, eRunProgressID_ : _ERunProgressID):
        _RUN_PROGRESS_NOTIF_RESULT__OK    = True
        _RUN_PROGRESS_NOTIF_RESULT__NOK   = not _RUN_PROGRESS_NOTIF_RESULT__OK
        _RUN_PROGRESS_NOTIF_RESULT__ABORT = None

        if not self._PcIsLcOperable():
            return _RUN_PROGRESS_NOTIF_RESULT__ABORT

        if not isinstance(eRunProgressID_, _ERunProgressID):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00072)
            return _RUN_PROGRESS_NOTIF_RESULT__ABORT

        _rpID = _ERunProgressID(eRunProgressID_.value)

        res = _RUN_PROGRESS_NOTIF_RESULT__OK

        if _rpID.isReadyToRun:
            if self.__mi.isLcMonitorIdle:
                self.__mi._ActivateLcMonitorAlivenessByMR(self._xcard.runPhaseFreqMS)

            while not self._PcIsLcProxyModeNormal():
                _TaskUtil.SleepMS(20)
                if self.__mi.isLcShutdownEnabled:
                    break

            if self.__mi.isLcShutdownEnabled:
                res = _RUN_PROGRESS_NOTIF_RESULT__NOK
            elif not self._StartFWCs():
                res = _RUN_PROGRESS_NOTIF_RESULT__ABORT

        return res

    def _ProcFwcErrorHandlerCallback( self
                                    , cbID_   : _EPcErrHandlerCBID
                                    , curFE_  : _FatalLog =None
                                    , lstFFE_ : list      =None) -> _EExecutionCmdID:
        res = self.__CheckProcessingFeasiblity(cbID_=cbID_, curFE_=curFE_)
        if not res.isContinue:
            return res

        if not cbID_.isProcessObservedForeignFatalErrors:
            _wmsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwsMain_TID_008)
            self.__NotifyLcFailure(_ELcCompID.eFwMain, curFE_, self._rblTask)
            res = _EExecutionCmdID.MapExecState2ExecCmdID(self)
        else:
            res = self.__ProcFFErrors(lstFFErrors_=lstFFE_, bOnErrHdlrCallback_=True)

        return res

    def _PrepareCeasing(self):
        if (self.__mi is None) or not self.__mi.isValid:
            return
        if not self._isInLcCeaseMode:
            return

        if self.__mi.isLcShutdownEnabled and self.__mi._isCoordinatedShutdownManagedByMR:
            self.__ExecuteShutdownSequence()
        _AbsRunnable._ExecuteTeardown(self)

        if self._lcCeaseTLB is not None:
            self._lcCeaseTLB.UpdateCeaseState(True)

    def _RunCeaseIteration(self):
        pass

    @property
    def __isCoordinatingShutdown(self):
        if self._isInvalid:
            return False
        with self._md:
            return (self.__bM is not None) and self.__bM

    def __CheckDeactivateCoordinatedShutdownByMR(self):
        if self._isInvalid:
            return
        if self.__bM is None:
            return

        with self._md:
            if self.__mi.isLcShutdownEnabled:
                pass
            elif self.__bM:
                self.__bM = False

    def __EnableCoordinatedShutdown(self):
        if (self.__mi is None) or not self.__mi.isValid:
            return
        elif self.__mi.isLcShutdownEnabled:
            return

        if not self.__mi.isLcMonitorAlive:
            _bByMR = False
            self.__bM = False
        elif not self.__isCoordinatingShutdown:
            _bByMR = False
        else:
            _bByMR = True

        self.__mi._EnableCoordinatedShutdown(bManagedByMR_=_bByMR)

        if not self.__mi._isCoordinatedShutdownManagedByMR:
            if self.__isCoordinatingShutdown:
                with self._md:
                    self.__bM = False

    def __NotifyLcFailure(self, eFailedCompID_ : _ELcCompID, frcError_ : _FatalLog, atask_ : _AbsFwTask):
        self._PcNotifyLcFailure(eFailedCompID_, frcError_, atask_=atask_)
        if not self.__mi.isLcShutdownEnabled:
            self.__EnableCoordinatedShutdown()

    def __CheckProcessingFeasiblity(self, cbID_ : _EPcErrHandlerCBID =None, curFE_ : _FatalLog =None) -> _EExecutionCmdID:
        if self._isInvalid:
            return _EExecutionCmdID.Abort()

        _bFE   = curFE_ is not None
        _bEHCB = cbID_ is not None

        if _bFE and not _bEHCB:
            _wmsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwsMain_TID_002).format(str(curFE_))
            _frc = logif._CreateLogImplErrorEC(_EFwErrorCode.FE_00026, _wmsg)
            self.__NotifyLcFailure(_ELcCompID.eFwMain, _frc, self._rblTask)
            return _EExecutionCmdID.MapExecState2ExecCmdID(self)

        if _bEHCB:
            if not (cbID_.isAbortTaskDueToUnexpectedCall or cbID_.isFwMainSpecificCallbackID):
                _wmsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwsMain_TID_003).format(cbID_.compactName)
                _frc = logif._CreateLogImplErrorEC(_EFwErrorCode.FE_00027, _wmsg)
                self.__NotifyLcFailure(_ELcCompID.eFwMain, _frc, self._rblTask)
                return _EExecutionCmdID.MapExecState2ExecCmdID(self)

        _ePF = self._GetProcessingFeasibility(errLog_=curFE_)
        if not _ePF.isFeasible:
            res = _EExecutionCmdID.MapExecState2ExecCmdID(self)
            return res

        _bStopInstantly        = False
        _bHasLcAnyFailureState = self._PcHasLcAnyFailureState()

        if _bHasLcAnyFailureState:
            _frcv = self._PcGetLcFrcView()
            _frcPart = _CommonDefines._STR_NONE if _frcv is None else _frcv.asCompactString
            if _frcv is not None:
                _frcv.CleanUp()
        elif not self.__mi.isLcMonitorAlive:
            _bStopInstantly = True

        if _bStopInstantly:
            _bAborting = self.isAborting or self._isInLcCeaseMode
            self.__CheckDeactivateCoordinatedShutdownByMR()
            res = _EExecutionCmdID.Abort() if _bAborting else _EExecutionCmdID.Stop()
        elif _bHasLcAnyFailureState:
            res = _EExecutionCmdID.Stop()
        else:
            res = _EExecutionCmdID.Continue()

        return res

    def __ProcFFErrors(self, lstFFErrors_ : list =None, bOnErrHdlrCallback_ =False, bIgnoreFeasibility_ =False) -> _EExecutionCmdID:
        if not bIgnoreFeasibility_:
            res = self.__CheckProcessingFeasiblity()
            if not res.isContinue:
                return _EExecutionCmdID.MapExecState2ExecCmdID(self)

        if self.__p is None:
            _wmsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwsMain_TID_005)
            _frc = logif._CreateLogImplErrorEC(_EFwErrorCode.FE_00028, _wmsg)
            self.__CheckDeactivateCoordinatedShutdownByMR()
            self.__NotifyLcFailure(_ELcCompID.eFwMain, _frc, self._rblTask)
            return _EExecutionCmdID.MapExecState2ExecCmdID(self)

        if bOnErrHdlrCallback_:
            _NUM = len(self.__p)

            if _NUM > 0:
                _wmsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwsMain_TID_006).format(_NUM)
                _frc = logif._CreateLogImplErrorEC(_EFwErrorCode.FE_00029, _wmsg)
                self.__CheckDeactivateCoordinatedShutdownByMR()
                self.__NotifyLcFailure(_ELcCompID.eFwMain, _frc, self._rblTask)
                return _EExecutionCmdID.MapExecState2ExecCmdID(self)

            if lstFFErrors_ is not None:
                self.__p += lstFFErrors_

            return _EExecutionCmdID.MapExecState2ExecCmdID(self)

        self._CheckSFFEsPS()

        _NUM = len(self.__p)

        if _NUM > 0:
            _lstCandid = self.__CheckStoredFFEsOnLcFailureCandidacy()

            if _lstCandid is not None:
                for _myFE in _lstCandid:
                    if not _myFE.isInvalid:
                        _wmsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwsMain_TID_004).format(_myFE.uniqueID, _myFE.shortMessage)
                        _atsk = _myFE._taskInstance
                        if (_atsk is None) or not _atsk.isValid:
                            _cid = _ELcCompID.eMiscComp
                            _atsk = self._rblTask
                        else:
                            _cid = _atsk.GetLcCompID()
                        self.__NotifyLcFailure(_cid, _myFE, _atsk)
                    _myFE._ForceCleanUp()
                _lstCandid.clear()

        return _EExecutionCmdID.MapExecState2ExecCmdID(self)

    def __CheckStoredFFEsOnLcFailureCandidacy(self) -> list:
        _bDM        = logif._IsFwDieModeEnabled()
        _lstPFFE    = self.__p
        _lstCleanup = []

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

            if _bDM:
                _fec = _myFE.Clone()
                if _fec is not None:
                    res.append(_fec)

                _lstPFFE[_ii] = None
                _lstCleanup.append(_myFE)
                if _myMtx is not None: _myMtx.Give()
                continue

            _bTaskMissedToResolveFE = _ti.taskXPhase != _myFE.taskXPhase  
            if not _bTaskMissedToResolveFE:
                _bTaskMissedToResolveFE = _ti.xrNumber != _myFE.xrNumber        
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
        self.__p = _lstPFFE

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
        if self.__p is None:
            return

        with self._md:
            for _ee in self.__p:
                _ee._ForceCleanUp()
            self.__p.clear()
            self.__p = None

    def __ExecuteShutdownSequence(self):
        _sdCoord = _LcSDCoordinator(self.__mi)
        _sdCoord._ExecuteCoordinatedCeasingGate()

        if self.__mi.isCoordinatedShutdownRunning:
            _sdCoord._ExecuteCoordinatedPreShutdownGate()
        if self.__mi.isCoordinatedShutdownRunning:
            _sdCoord._ExecuteCoordinatedShutdownGate()
        if self.__mi is not None:
            self.__mi._StopCoordinatedShutdown()
        logif._LogKPI(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwsMain_TID_007))

    def __StartCoordinatedShutdown(self):
        _sdCoord = _LcSDCoordinator(self.__mi)
        _sdCoord._ExecuteCoordinatedCeasingGate()
