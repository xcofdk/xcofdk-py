# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : lcguard.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum import auto
from enum import unique

from _fw.fwssys.assys.ifs.tiflcmgr          import _TILcManager
from _fw.fwssys.fwcore.logging.logif        import _CreateLogImplErrorEC
from _fw.fwssys.fwcore.logging.logif        import _LogKPI
from _fw.fwssys.fwcore.logging              import vlogif
from _fw.fwssys.fwcore.logging.logdefines   import _EErrorImpact
from _fw.fwssys.fwcore.base.timeutil        import _TimeAlert
from _fw.fwssys.fwcore.base.gtimeout        import _Timeout
from _fw.fwssys.fwcore.ipc.sync.syncresbase import _PyRLock
from _fw.fwssys.fwcore.ipc.sync.syncresbase import _PySemaphore
from _fw.fwssys.fwcore.ipc.tsk.afwtask      import _AbsFwTask
from _fw.fwssys.fwcore.ipc.tsk.taskutil     import _TaskUtil
from _fw.fwssys.fwcore.ipc.tsk.taskutil     import _PyThread
from _fw.fwssys.fwcore.lc.lcdefines         import _ELcCompID
from _fw.fwssys.fwcore.lc.lcxstate          import _LcFailure
from _fw.fwssys.fwcore.lc.lcproxydefines    import _ELcSDRequest
from _fw.fwssys.fwcore.lc.ifs.iflcguard     import _ILcGuard
from _fw.fwssys.fwcore.lc.ifs.iflcstate     import _ILcState
from _fw.fwssys.fwcore.lc.lcstate           import _LcState
from _fw.fwssys.fwcore.lc.lcmn.lcmonimpl    import _LcMonitorImpl
from _fw.fwssys.fwcore.lc.lcmn.lcsdc        import _LcSDCoordinator
from _fw.fwssys.fwcore.types.aobject        import _AbsSlotsObject
from _fw.fwssys.fwcore.types.commontypes    import _FwIntEnum
from _fw.fwssys.fwerrh.fwerrorcodes         import _EFwErrorCode
from _fw.fwssys.fwerrh.lcfrcview            import _LcFrcView
from _fw.fwssys.fwerrh.logs.errorlog        import _FatalLog

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _LcGuard(_ILcGuard):
    @unique
    class _ELcGuardState(_FwIntEnum):
        eFailed      = -1
        eInitialized = auto()
        ePendingRun  = auto()
        eRunning     = auto()
        ePendingStop = auto()
        eDone        = auto()

    class _LcMonData(_AbsSlotsObject):
        __slots__ = [ '__trsh' , '__bS' , '__aac' , '__ac' , '__csdr' ]

        def __init__(self, lcMonAACThreshold_ : int):
            super().__init__()
            self.__ac   = None
            self.__bS   = None
            self.__aac  = None
            self.__csdr = None
            self.__trsh = lcMonAACThreshold_

        @property
        def isAliveAlarmOn(self):
            res = self.aliveAlarmCounter is not None
            res = res and (self.__trsh is not None)
            res = res and (self.aliveAlarmCounter > self.__trsh)
            return res

        @property
        def isShutdownEnabled(self):
            return self.__bS

        @isShutdownEnabled.setter
        def isShutdownEnabled(self, val_):
            self.__bS = val_

        @property
        def aliveAlarmCounter(self):
            return self.__aac

        @aliveAlarmCounter.setter
        def aliveAlarmCounter(self, val_):
            self.__aac = val_

        @property
        def aliveCounter(self):
            return self.__ac

        @aliveCounter.setter
        def aliveCounter(self, val_):
            self.__ac = val_

        @property
        def curShutdownRequest(self):
            return self.__csdr

        @curShutdownRequest.setter
        def curShutdownRequest(self, val_):
            self.__csdr = val_

        def Update(self, bSDEnabled_ : bool, curSDR_ : _ELcSDRequest, aliveCtr_ : int):
            _bChanged = False
            if bSDEnabled_ != self.__bS:
                _bChanged, self.__bS = True, bSDEnabled_
            if curSDR_ != self.__csdr:
                _bChanged, self.__csdr = True, curSDR_
            if aliveCtr_ != self.__ac:
                _bChanged, self.__ac = True, aliveCtr_

            if not _bChanged:
                return

            self.__ac   = aliveCtr_
            self.__bS   = bSDEnabled_
            self.__csdr = curSDR_

        def _ToString(self):
            pass

        def _CleanUp(self):
            self.__ac   = None
            self.__bS   = None
            self.__aac  = None
            self.__csdr = None
            self.__trsh = None

    __slots__ = [ '__l' , '__h' , '__s' , '__mst' , '__st' , '__mi' , '__m' , '__md' , '__f' , '__msr' , '__a' , '__aa' ]

    __LOG_ALERT_TIMESPAN_MS                   = 3000
    __LOG_ALERT_AA_TIMESPAN_MS                = 1000 
    __DEFAULT_RUN_CYCLE_LOOP_TIMESPAN_MS      = 20   
    __LC_MON_ALIVE_ALARM_COUNTER_THRESHOLD    = 20   

    __MIN_OFFSET_RELATIVE_TO_LC_MON_CYCLE        = None
    __bSET_LC_FAILURE_UPON_LC_MON_ALIVE_ALARM    = True
    __bIGNORE_MRBL_STATE_UPON_LC_MON_ALIVE_ALARM = False

    def __init__(self, ppass_ : int, lcMgrTIF_ : _TILcManager):
        self.__a   = None
        self.__f   = None
        self.__h   = None
        self.__l   = None
        self.__m   = None
        self.__s   = None
        self.__aa  = None
        self.__mi  = None
        self.__md  = None
        self.__st  = None
        self.__msr = None
        self.__mst = None

        if _ILcGuard._sgltn is not None:
            self.CleanUpByOwnerRequest(self._myPPass)
            _errCode = _EFwErrorCode.FE_LCSF_039
            vlogif._LogOEC(True, _errCode)
            _LcFailure.CheckSetLcSetupFailure(_errCode)
            return

        super().__init__(ppass_)

        if not isinstance(lcMgrTIF_, _TILcManager):
            self.CleanUpByOwnerRequest(self._myPPass)
            _errCode = _EFwErrorCode.FE_LCSF_040
            vlogif._LogOEC(True, _errCode)
            _LcFailure.CheckSetLcSetupFailure(_errCode)
            return

        _lcs = _LcState(ppass_)

        if not (_lcs._isLcIdle and _LcFailure.IsLcErrorFree()):
            _lcs.CleanUpByOwnerRequest(ppass_)
            self.CleanUpByOwnerRequest(ppass_)
            if _LcFailure.IsLcErrorFree():
                _errCode = _EFwErrorCode.FE_LCSF_041
                vlogif._LogOEC(True, _errCode)
                _LcFailure.CheckSetLcSetupFailure(_errCode)
            return

        self.__f   = _LcGuard.__DEFAULT_RUN_CYCLE_LOOP_TIMESPAN_MS
        self.__l   = _PyRLock()
        self.__st  = _lcs
        self.__mi  = lcMgrTIF_
        self.__mst = _LcGuard._ELcGuardState.eInitialized
        self.__md  = _LcGuard._LcMonData(_LcGuard.__LC_MON_ALIVE_ALARM_COUNTER_THRESHOLD)

        _tout = _Timeout.CreateTimeoutMS(_LcGuard.__LOG_ALERT_TIMESPAN_MS)
        self.__a = _TimeAlert(_tout.toNSec)
        _tout.CleanUp()
        _tout = _Timeout.CreateTimeoutMS(_LcGuard.__LOG_ALERT_AA_TIMESPAN_MS)
        self.__aa = _TimeAlert(_tout.toNSec)
        _tout.CleanUp()

    @property
    def isLcOperable(self) -> bool:
        if self.__isInvalid: return False
        with self.__l:
            return self.__st.isLcOperable

    @property
    def isLcCoreOperable(self) -> bool:
        if self.__isInvalid: return False
        with self.__l:
            return self.__st.isLcCoreOperable

    @property
    def isLcStarted(self) -> bool:
        if self.__isInvalid: return False
        with self.__l:
            return self.__st.isLcStarted

    @property
    def isTaskManagerStarted(self) -> bool:
        if self.__isInvalid: return False
        with self.__l:
            return self.__st.isTaskManagerStarted

    @property
    def isFwMainStarted(self) -> bool:
        if self.__isInvalid: return False
        with self.__l:
            return self.__st.isFwMainStarted

    @property
    def isMainXTaskStarted(self) -> bool:
        if self.__isInvalid: return False
        with self.__l:
            return self.__st.isMainXTaskStarted

    @property
    def isLcStopped(self) -> bool:
        if self.__isInvalid: return False
        with self.__l:
            return self.__st.isLcStopped

    @property
    def isTaskManagerStopped(self) -> bool:
        if self.__isInvalid: return False
        with self.__l:
            return self.__st.isTaskManagerStopped

    @property
    def isFwMainStopped(self) -> bool:
        if self.__isInvalid: return False
        with self.__l:
            return self.__st.isFwMainStopped

    @property
    def isMainXTaskStopped(self) -> bool:
        if self.__isInvalid: return False
        with self.__l:
            return self.__st.isMainXTaskStopped

    @property
    def isLcFailed(self) -> bool:
        if self.__isInvalid: return False
        with self.__l:
            return self.__st.isLcFailed

    @property
    def isTaskManagerFailed(self) -> bool:
        if self.__isInvalid: return False
        with self.__l:
            return self.__st.isTaskManagerFailed

    @property
    def isFwCompFailed(self) -> bool:
        if self.__isInvalid: return False
        with self.__l:
            return self.__st.isFwCompFailed

    @property
    def isFwMainFailed(self) -> bool:
        if self.__isInvalid: return False
        with self.__l:
            return self.__st.isFwMainFailed

    @property
    def isXTaskFailed(self) -> bool:
        if self.__isInvalid: return False
        with self.__l:
            return self.__st.isXTaskFailed

    @property
    def isMainXTaskFailed(self) -> bool:
        if self.__isInvalid: return False
        with self.__l:
            return self.__st.isMainXTaskFailed

    @property
    def isMiscCompFailed(self) -> bool:
        if self.__isInvalid: return False
        with self.__l:
            return self.__st.isMiscCompFailed

    @property
    def hasLcAnyFailureState(self) -> bool:
        if self.__isInvalid: return False
        with self.__l:
            return self.__st.hasLcAnyFailureState

    @property
    def lcFrcView(self) -> _LcFrcView:
        if self.__isInvalid: return False
        with self.__l:
            return self.__st.lcFrcView

    def HasLcCompFRC(self, lcCID_: _ELcCompID, atask_: _AbsFwTask = None) -> bool:
        if self.__isInvalid: return False
        with self.__l:
            return self.__st.HasLcCompFRC(lcCID_, atask_=atask_)

    def GetLcCompFrcView(self, lcCID_ : _ELcCompID, atask_ : _AbsFwTask =None) -> _LcFrcView:
        if self.__isInvalid: return None
        with self.__l:
            return self.__st.GetLcCompFrcView(lcCID_, atask_=atask_)

    @property
    def _isGStarted(self):
        return False if self.__isInvalid else self.__mst.value >= _LcGuard._ELcGuardState.ePendingRun.value

    @property
    def _isGRunning(self):
        return False if self.__isInvalid else self.__mst==_LcGuard._ELcGuardState.eRunning

    @property
    def _isGStopped(self):
        return False if self.__isInvalid else self.__mst==_LcGuard._ELcGuardState.eDone

    @property
    def _isGFailed(self):
        return False if self.__isInvalid else self.__mst==_LcGuard._ELcGuardState.eFailed

    def _GGetLcState(self, bypassApiLock_=False) -> _ILcState:
        if self.__isInvalid: return None
        elif bypassApiLock_: return self.__st

        with self.__l:
            return self.__st

    def _GSetLcMonitorImpl(self, lcMonImpl_ : _LcMonitorImpl):
        if isinstance(lcMonImpl_, _LcMonitorImpl) and lcMonImpl_.isValid and not lcMonImpl_.isDummyMonitor:
            self.__m = lcMonImpl_

    def _GUpdateRunCycleLoopTimespanMS(self, rclTSMS_ : int):
        if not (isinstance(rclTSMS_, int) and rclTSMS_ > 0):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00347)
        else:
            self.__f = rclTSMS_

    def _GSetLcOperationalState(self, lcCID_: _ELcCompID, bStartStopFlag_: bool, atask_: _AbsFwTask =None) -> bool:
        if self.__isInvalid:
            return False
        if not isinstance(lcCID_, _ELcCompID):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00348)
            return False
        if not isinstance(bStartStopFlag_, bool):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00349)
            return False
        if (atask_ is not None) and not isinstance(atask_, _AbsFwTask):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00350)
            return False

        self.__l.acquire()
        _tname = _TaskUtil.GetCurPyThread().name if atask_ is None else atask_.dtaskName
        res = self.__st._SetLcState(lcCID_, bStartStopFlag_, frcError_=None, atask_=atask_)
        if not res:
            vlogif._LogOEC(False, _EFwErrorCode.VUE_00030)

        self.__l.release()
        return res

    def _GSetLcFailure(self, eFailedCompID_: _ELcCompID, frcError_: _FatalLog, atask_: _AbsFwTask =None, bSkipReply_=False, bInternalCall_ =False) -> bool:
        if self.__isInvalid:
            return False

        if not isinstance(eFailedCompID_, _ELcCompID):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00351)
            return False
        if not isinstance(frcError_, _FatalLog):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00352)
            return False
        if (atask_ is not None) and not isinstance(atask_, _AbsFwTask):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00353)
            return False

        self.__l.acquire()

        _tname = _TaskUtil.GetCurPyThread().name if atask_ is None else atask_.dtaskName
        res = self.__st._SetLcState(eFailedCompID_, None, frcError_=frcError_, atask_=atask_)

        if not res:
            _tailPart = '\t[FRC]\n\t{}'.format(str(frcError_))
            vlogif._LogOEC(False, _EFwErrorCode.VUE_00031)

        elif not bSkipReply_:
            if self.__mi._TIFPreCheckLcFailureNotification(eFailedCompID_):
                if atask_ is None:
                    atask_ = frcError_._taskInstance
                self.__mi._TIFOnLcFailure(eFailedCompID_, frcError_, atask_=atask_, bPrvRequestReply_=not bInternalCall_)

        self.__l.release()

        return res

    def _GStart(self, semStartStop_ : _PySemaphore, lcMgrSetupRunner_):
        _iImplErr = None

        if self.__h is not None:
            _iImplErr = _EFwErrorCode.FE_LCSF_042
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00354)
        elif not isinstance(semStartStop_, _PySemaphore):
            _iImplErr = _EFwErrorCode.FE_LCSF_043
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00355)

        if _iImplErr is not None:
            _LcFailure.CheckSetLcSetupFailure(_iImplErr)
            return False

        _name      = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcGuard_TID_004)
        self.__s   = semStartStop_
        self.__h   = _PyThread(group=None, target=self.__RunThrdTgt, name=_name, args=(), kwargs={}, daemon=None)
        self.__mst = _LcGuard._ELcGuardState.ePendingRun
        self.__msr = lcMgrSetupRunner_

        _TaskUtil._StartHThread(self.__h)
        return _LcFailure.IsLcErrorFree()

    def _GStop(self, semStartStop_ : _PySemaphore):
        if self.__h is None:
            return
        if not self._isGRunning:
            return
        if self.__s is not None:
            return
        self.__s   = semStartStop_
        self.__mst = _LcGuard._ELcGuardState.ePendingStop

    def _GJoin(self):
        if self.__isInvalid:
            return
        if self.__h is None:
            return
        if not self._isGStarted:
            return
        if self._isGStopped or self._isGFailed:
            return
        _TaskUtil.JoinPyThread(self.__h)

    def _ToString(self):
        if self.__isInvalid:
            return None
        with self.__l:
            return _FwTDbEngine.GetText(_EFwTextID.eLcGuard_ToString_001).format(self.__mst.compactName)

    def _CleanUpByOwnerRequest(self):
        if (self.__l is None) or (_ILcGuard._sgltn is None):
            pass
        elif id(self) != id(_ILcGuard._sgltn):
            pass
        else:
            _ILcGuard._sgltn = None

            if self.__md is not None:
                self.__md.CleanUp()

            if self.__st is not None:
                self.__st.CleanUpByOwnerRequest(self._myPPass)

            if self.__msr is not None:
                self.__msr.CleanUp()

            self.__a   = None
            self.__f   = None
            self.__h   = None
            self.__l   = None
            self.__m   = None
            self.__s   = None
            self.__aa  = None
            self.__mi  = None
            self.__md  = None
            self.__st  = None
            self.__msr = None
            self.__mst = None

    @property
    def __isInvalid(self):
        return self.__l is None

    def __RunThrdTgt(self):
        self.__mst = _LcGuard._ELcGuardState.eRunning

        if not self.__ExecuteSetupRunner():
            return

        _aliveCtr = self.__RunFull()
        if self.__s is not None:
            self.__s.release()
            self.__s = None
        self.__mst = _LcGuard._ELcGuardState.eDone

    def __ExecuteSetupRunner(self):
        res = False
        if self.__msr is None:
            _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_045)
        else:
            self.__msr()
            if not (self.__msr.isLcMgrSetupRunnerSucceeded and _LcFailure.IsLcErrorFree()):
                vlogif._LogOEC(False, _EFwErrorCode.VUE_00032)
                self.__mst = _LcGuard._ELcGuardState.eFailed

                if _LcFailure.IsLcErrorFree():
                    _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_046)
            else:
                res = True

        if self.__s is not None:
            self.__s.release()
            self.__s = None
        return res

    def __RunFull(self):
        _aliveCtr = 0

        while self._isGRunning:
            _aliveCtr += 1

            _lcm = self.__m
            if (_lcm is None) or _lcm.isLcMonitorIdle or (_lcm._mainTLB is None):
                pass
            elif _lcm.isLcMonitorAlive:
                self.__CheckLcMonAliveness(_aliveCtr)
            if _lcm.isLcShutdownEnabled:
                self.__ExecuteShutdownSequence()
                break
            else:
                _TaskUtil.SleepMS(self.__f)

        return _aliveCtr

    def __ExecuteShutdownSequence(self):
        _lcm = self.__m

        self.__md.aliveCounter = 0

        if _lcm.curShutdownRequest is None:
            _eSDR = _ELcSDRequest.ePreShutdown
            self.__mi._TIFOnLcShutdownRequest(_eSDR)

        _bSdcME = None

        if _lcm.isCoordinatedShutdownRunning:
            if not _lcm._isCoordinatedShutdownManagedByMR:
                _bSdcME = _LcSDCoordinator(_lcm)
                _bSdcME._ExecuteCoordinatedCeasingGate()
                if _lcm.isCoordinatedShutdownRunning:
                    _bSdcME._ExecuteCoordinatedPreShutdownGate()
            else:
                self.__MonitorShutdownCoordinationByMR(False)

        _eSDR = _ELcSDRequest.eShutdown
        self.__mi._TIFOnLcShutdownRequest(_eSDR)

        if _lcm.isCoordinatedShutdownRunning:
            if _bSdcME is not None:
                _bSdcME._ExecuteCoordinatedShutdownGate()
                _LogKPI(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcGuard_TID_003))
            else:
                self.__MonitorShutdownCoordinationByMR(True)

        _lcm._StopCoordinatedShutdown()

        self.__mi._TIFFinalizeStopFW(False)

        vlogif._LogNewline()
        vlogif._LogNewline()

        if self.__st is not None:
            if not self.__st.isLcStopped:
                self._GSetLcOperationalState(_ELcCompID.eLcMgr, False, atask_=None)

    def __CheckLcMonAliveness(self, lcGAliveCtr_ : int) -> bool:
        _lcm = self.__m

        _bSDEnabled, _curSDR, _aliveCtr = _lcm._GetAliveCounter()
        if _bSDEnabled is None:
            return True

        if not isinstance(_bSDEnabled, bool):
            _bErr = True
        elif (_curSDR is not None) and not isinstance(_curSDR, _ELcSDRequest):
            _bErr = True
        elif not isinstance(_aliveCtr, int):
            _bErr = True
        else:
            _bErr = False
        if _bErr:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00357)
            return False

        _md = self.__md

        _aliveCtrPrv    = _md.aliveCounter
        _bInitialUpdate = _md.isShutdownEnabled is None

        if _bInitialUpdate:
            _bSDEnabled      = False
            _bCeaseModeStart = False
        else:
            _bCeaseModeStart = False if _md.isShutdownEnabled == _bSDEnabled else _bSDEnabled

        _md.Update(_bSDEnabled, _curSDR, _aliveCtr)

        if _bInitialUpdate:
            _md.aliveAlarmCounter = 0
            return True
        if _bCeaseModeStart:
            _md.aliveAlarmCounter = 0
            return False

        _bWasAAlarmOFF = not _md.isAliveAlarmOn

        if _LcGuard.__MIN_OFFSET_RELATIVE_TO_LC_MON_CYCLE is None:
            _lcmCycle = _lcm._runPhaseFrequencyMS
            if (_lcmCycle is None) or (_lcmCycle < self.__f):
                minOffset = 1
            else:
                minOffset = _lcm._runPhaseFrequencyMS // self.__f
            _LcGuard.__MIN_OFFSET_RELATIVE_TO_LC_MON_CYCLE = minOffset

        if not (_aliveCtr > (_aliveCtrPrv+_LcGuard.__MIN_OFFSET_RELATIVE_TO_LC_MON_CYCLE)):
            _md.aliveAlarmCounter += 1
        else:
            _md.aliveAlarmCounter = 0

        if not _md.isAliveAlarmOn:
            return True

        _missingMS = _lcm._mainTLB.elapsedTimeSinceLastUpdate

        _bDI = _LcGuard.__bSET_LC_FAILURE_UPON_LC_MON_ALIVE_ALARM
        if _bDI:
            if not _LcGuard.__bIGNORE_MRBL_STATE_UPON_LC_MON_ALIVE_ALARM:
                _bDI = not _lcm._mainTLB.isRunning

        if not _bDI:
            return True

        _md.aliveAlarmCounter = 0
        _frcError = _CreateLogImplErrorEC(_EFwErrorCode.FE_00376, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcGuard_TID_001).format(_missingMS))

        _lcm._EnableCoordinatedShutdown(bManagedByMR_=False)

        if _lcm._isCoordinatedShutdownManagedByMR:
            if _frcError is not None:
                _frcError._UpdateErrorImpact(_EErrorImpact.eNoImpactByOwnerCondition)
                _frcError.CleanUp()
        else:
            if _frcError is None:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00358)
            else:
                if not self._GSetLcFailure(_ELcCompID.eFwMain, _frcError, atask_=None, bInternalCall_=True):
                    _frcError._UpdateErrorImpact(_EErrorImpact.eNoImpactByOwnerCondition)
                    _frcError.CleanUp()
        return False

    def __MonitorShutdownCoordinationByMR(self, bCheckForShutdownGate_ : bool):
        _lcm, _md = self.__m, self.__md

        while True:
            _bGO = _lcm.isCoordinatedShutdownGateOpened if bCheckForShutdownGate_ else _lcm.isCoordinatedPreShutdownGateOpened
            if _bGO:
                break

            _TaskUtil.SleepMS(20)

            _aliveCtrPrv   = _md.aliveCounter
            _bWasAAlarmOff = not _md.isAliveAlarmOn

            _bSDEnabled, _curSDR, _aliveCtr = _lcm._GetAliveCounter()
            _md.Update(_bSDEnabled, _curSDR, _aliveCtr)

            if not (_aliveCtr > _aliveCtrPrv):
                _md.aliveAlarmCounter += 1
            else:
                _md.aliveAlarmCounter = 0
            continue
