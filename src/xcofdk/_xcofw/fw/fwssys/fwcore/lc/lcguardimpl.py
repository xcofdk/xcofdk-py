# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : lcguardimpl.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum     import unique
from datetime import datetime as _PyDateTime

from xcofdk._xcofw.fw.fwssys.fwcore.logging.logif import _CreateLogImplErrorEC
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logif import _LogKPI
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logif import _XLogWarning

from xcofdk._xcofw.fw.fwssys.fwcore.logging               import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logdefines    import _EErrorImpact
from xcofdk._xcofw.fw.fwssys.fwcore.logging.fatalentry    import _FatalEntry
from xcofdk._xcofw.fw.fwssys.fwcore.base.timeutil         import _TimeAlert
from xcofdk._xcofw.fw.fwssys.fwcore.base.gtimeout         import _Timeout
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.sync.syncresbase  import _PyRLock
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.sync.syncresbase  import _PySemaphore
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.atask         import _AbstractTask
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil      import _TaskUtil
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil      import _PyThread
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcdefines          import _ELcCompID
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcexecstate        import _LcFailure
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcguard            import _LcGuard
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcmgrtif           import _LcManagerTrustedIF
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcproxydefines     import _ELcShutdownRequest
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcstate            import _LcState
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcstateimpl        import _LcStateImpl
from xcofdk._xcofw.fw.fwssys.fwcore.lcmon.lcmonimpl       import _LcMonitorImpl
from xcofdk._xcofw.fw.fwssys.fwcore.lcmon.lcshutdowncoord import _LcShutdownCoordinator
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject         import _AbstractSlotsObject
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes     import _FwIntEnum

from xcofdk._xcofw.fw.fwssys.fwerrh.fwerrorcodes import _EFwErrorCode
from xcofdk._xcofw.fw.fwssys.fwerrh.lcfrcview    import _LcFrcView

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine

class _LcGuardImpl(_LcGuard):

    @unique
    class _ELcGuardState(_FwIntEnum):
        eFailed      =-1
        eInitialized =0
        ePendingRun  =1
        eRunning     =2
        ePendingStop =3
        eDone        =4

    class _LcMonData(_AbstractSlotsObject):

        __slots__ = [ '__lcMonAliveAlarmCounterThreshold' , '__bShutdownEnabled' , '__aliveAlarmCounter' , '__aliveCounter' , '__curShutdownRequest' ]

        def __init__(self, lcMonAliveAlarmCounterThreshold_ : int):
            super().__init__()
            self.__aliveCounter       = None
            self.__bShutdownEnabled   = None
            self.__aliveAlarmCounter  = None
            self.__curShutdownRequest = None

            self.__lcMonAliveAlarmCounterThreshold = lcMonAliveAlarmCounterThreshold_

        @property
        def isAliveAlarmOn(self):
            res = self.aliveAlarmCounter is not None
            res = res and (self.__lcMonAliveAlarmCounterThreshold is not None)
            res = res and (self.aliveAlarmCounter > self.__lcMonAliveAlarmCounterThreshold)
            return res

        @property
        def isShutdownEnabled(self):
            return self.__bShutdownEnabled

        @isShutdownEnabled.setter
        def isShutdownEnabled(self, val_):
            self.__bShutdownEnabled = val_

        @property
        def aliveAlarmCounter(self):
            return self.__aliveAlarmCounter

        @aliveAlarmCounter.setter
        def aliveAlarmCounter(self, val_):
            self.__aliveAlarmCounter = val_

        @property
        def aliveCounter(self):
            return self.__aliveCounter

        @aliveCounter.setter
        def aliveCounter(self, val_):
            self.__aliveCounter = val_

        @property
        def curShutdownRequest(self):
            return self.__curShutdownRequest

        @curShutdownRequest.setter
        def curShutdownRequest(self, val_):
            self.__curShutdownRequest = val_

        def Update(self, bSDEnabled_ : bool, curSDR_ : _ELcShutdownRequest, aliveCtr_ : int):
            _bChanged = False
            if bSDEnabled_ != self.__bShutdownEnabled:
                _bChanged, self.__bShutdownEnabled    = True, bSDEnabled_
            if curSDR_ != self.__curShutdownRequest:
                _bChanged, self.__curShutdownRequest  = True, curSDR_
            if aliveCtr_ != self.__aliveCounter:
                _bChanged, self.__aliveCounter        = True, aliveCtr_

            if not _bChanged:
                return

            self.__aliveCounter       = aliveCtr_
            self.__bShutdownEnabled   = bSDEnabled_
            self.__curShutdownRequest = curSDR_

        def _ToString(self, *args_, **kwargs_):
            pass

        def _CleanUp(self):
            self.__aliveCounter       = None
            self.__aliveAlarmCounter  = None
            self.__bShutdownEnabled   = None
            self.__curShutdownRequest = None
            self.__lcMonAliveAlarmCounterThreshold = None

    __slots__ = [
                  '__apiLck'     , '__pythrd'     , '__semSS'            , '__myState'    , '__lcState'
                , '__lcMgrTIF'   , '__lcMon'      , '__lcMonData'        , '__rclTSMS'    , '__logAlert'
                , '__logAlertAA' , '__maxETAlert' , '__lcMgrSetupRunner'
                ]

    __LOG_ALERT_TIMESPAN_MS                   = 3000
    __LOG_ALERT_AA_TIMESPAN_MS                = 1000 
    __DEFAULT_RUN_CYCLE_LOOP_TIMESPAN_MS      = 20   
    __LC_MON_ALIVE_ALARM_COUNTER_THRESHOLD    = 20   

    __MIN_OFFSET_RELATIVE_TO_LC_MON_CYCLE        = None
    __bSET_LC_FAILURE_UPON_LC_MON_ALIVE_ALARM    = True
    __bIGNORE_MRBL_STATE_UPON_LC_MON_ALIVE_ALARM = False

    def __init__(self, ppass_ : int, lcMgrTIF_ : _LcManagerTrustedIF):
        self.__lcMon            = None
        self.__semSS            = None
        self.__pythrd           = None
        self.__apiLck           = None
        self.__myState          = None
        self.__lcState          = None
        self.__rclTSMS          = None
        self.__lcMgrTIF         = None
        self.__logAlert         = None
        self.__lcMonData        = None
        self.__maxETAlert       = None
        self.__logAlertAA       = None
        self.__lcMgrSetupRunner = None

        if _LcGuard._singleton is not None:
            self.CleanUpByOwnerRequest(self._myPPass)
            _errCode = _EFwErrorCode.FE_LCSF_039
            vlogif._LogOEC(True, _errCode)
            _LcFailure.CheckSetLcSetupFailure(_errCode)
            return

        super().__init__(ppass_)

        if not isinstance(lcMgrTIF_, _LcManagerTrustedIF):
            self.CleanUpByOwnerRequest(self._myPPass)
            _errCode = _EFwErrorCode.FE_LCSF_040
            vlogif._LogOEC(True, _errCode)
            _LcFailure.CheckSetLcSetupFailure(_errCode)
            return

        _lcs = _LcStateImpl(ppass_)

        if not (_lcs._isLcIdle and _LcFailure.IsLcErrorFree()):
            _lcs.CleanUpByOwnerRequest(ppass_)
            self.CleanUpByOwnerRequest(ppass_)
            if _LcFailure.IsLcErrorFree():
                _errCode = _EFwErrorCode.FE_LCSF_041
                vlogif._LogOEC(True, _errCode)
                _LcFailure.CheckSetLcSetupFailure(_errCode)
            return

        self.__apiLck        = _PyRLock()
        self.__myState       = _LcGuardImpl._ELcGuardState.eInitialized
        self.__lcState       = _lcs
        self.__rclTSMS       = _LcGuardImpl.__DEFAULT_RUN_CYCLE_LOOP_TIMESPAN_MS
        self.__lcMgrTIF      = lcMgrTIF_
        self.__lcMonData     = _LcGuardImpl._LcMonData(_LcGuardImpl.__LC_MON_ALIVE_ALARM_COUNTER_THRESHOLD)

        _tout = _Timeout.CreateTimeoutMS(_LcGuardImpl.__LOG_ALERT_TIMESPAN_MS)
        self.__logAlert = _TimeAlert(_tout.toNSec)
        _tout.CleanUp()
        _tout = _Timeout.CreateTimeoutMS(_LcGuardImpl.__LOG_ALERT_AA_TIMESPAN_MS)
        self.__logAlertAA = _TimeAlert(_tout.toNSec)
        _tout.CleanUp()

    @property
    def isLcOperable(self) -> bool:
        if self.__isInvalid: return False
        with self.__apiLck:
            return self.__lcState.isLcOperable

    @property
    def isLcCoreOperable(self) -> bool:
        if self.__isInvalid: return False
        with self.__apiLck:
            return self.__lcState.isLcCoreOperable

    @property
    def isLcStarted(self) -> bool:
        if self.__isInvalid: return False
        with self.__apiLck:
            return self.__lcState.isLcStarted

    @property
    def isTaskManagerStarted(self) -> bool:
        if self.__isInvalid: return False
        with self.__apiLck:
            return self.__lcState.isTaskManagerStarted

    @property
    def isFwMainStarted(self) -> bool:
        if self.__isInvalid: return False
        with self.__apiLck:
            return self.__lcState.isFwMainStarted

    @property
    def isMainXTaskStarted(self) -> bool:
        if self.__isInvalid: return False
        with self.__apiLck:
            return self.__lcState.isMainXTaskStarted

    @property
    def isLcStopped(self) -> bool:
        if self.__isInvalid: return False
        with self.__apiLck:
            return self.__lcState.isLcStopped

    @property
    def isTaskManagerStopped(self) -> bool:
        if self.__isInvalid: return False
        with self.__apiLck:
            return self.__lcState.isTaskManagerStopped

    @property
    def isFwMainStopped(self) -> bool:
        if self.__isInvalid: return False
        with self.__apiLck:
            return self.__lcState.isFwMainStopped

    @property
    def isMainXTaskStopped(self) -> bool:
        if self.__isInvalid: return False
        with self.__apiLck:
            return self.__lcState.isMainXTaskStopped

    @property
    def isLcFailed(self) -> bool:
        if self.__isInvalid: return False
        with self.__apiLck:
            return self.__lcState.isLcFailed

    @property
    def isTaskManagerFailed(self) -> bool:
        if self.__isInvalid: return False
        with self.__apiLck:
            return self.__lcState.isTaskManagerFailed

    @property
    def isFwCompFailed(self) -> bool:
        if self.__isInvalid: return False
        with self.__apiLck:
            return self.__lcState.isFwCompFailed

    @property
    def isFwMainFailed(self) -> bool:
        if self.__isInvalid: return False
        with self.__apiLck:
            return self.__lcState.isFwMainFailed

    @property
    def isXTaskFailed(self) -> bool:
        if self.__isInvalid: return False
        with self.__apiLck:
            return self.__lcState.isXTaskFailed

    @property
    def isMainXTaskFailed(self) -> bool:
        if self.__isInvalid: return False
        with self.__apiLck:
            return self.__lcState.isMainXTaskFailed

    @property
    def isMiscCompFailed(self) -> bool:
        if self.__isInvalid: return False
        with self.__apiLck:
            return self.__lcState.isMiscCompFailed

    @property
    def hasLcAnyFailureState(self) -> bool:
        if self.__isInvalid: return False
        with self.__apiLck:
            return self.__lcState.hasLcAnyFailureState

    @property
    def lcFrcView(self) -> _LcFrcView:
        if self.__isInvalid: return False
        with self.__apiLck:
            return self.__lcState.lcFrcView

    def HasLcCompFRC(self, eLcCompID_: _ELcCompID, atask_: _AbstractTask = None) -> bool:
        if self.__isInvalid: return False
        with self.__apiLck:
            return self.__lcState.HasLcCompFRC(eLcCompID_, atask_=atask_)

    def GetLcCompFrcView(self, eLcCompID_ : _ELcCompID, atask_ : _AbstractTask =None) -> _LcFrcView:
        if self.__isInvalid: return None
        with self.__apiLck:
            return self.__lcState.GetLcCompFrcView(eLcCompID_, atask_=atask_)

    @property
    def _isCurrentThread(self):
        return False if not self._isStarted else _TaskUtil.IsCurPyThread(self.__pythrd)

    @property
    def _isStarted(self):
        return False if self.__isInvalid else self.__myState.value >= _LcGuardImpl._ELcGuardState.ePendingRun.value

    @property
    def _isPendingRun(self):
        return False if self.__isInvalid else self.__myState==_LcGuardImpl._ELcGuardState.ePendingRun

    @property
    def _isRunning(self):
        return False if self.__isInvalid else self.__myState==_LcGuardImpl._ELcGuardState.eRunning

    @property
    def _isPendingStop(self):
        return False if self.__isInvalid else self.__myState==_LcGuardImpl._ELcGuardState.ePendingStop

    @property
    def _isStopped(self):
        return self._isDone

    @property
    def _isDone(self):
        return False if self.__isInvalid else self.__myState==_LcGuardImpl._ELcGuardState.eDone

    @property
    def _isFailed(self):
        return False if self.__isInvalid else self.__myState==_LcGuardImpl._ELcGuardState.eFailed

    def _GetLcState(self, bypassApiLock_=False) -> _LcState:
        if self.__isInvalid: return None
        elif bypassApiLock_: return self.__lcState

        with self.__apiLck:
            return self.__lcState

    def _SetLcMonitorImpl(self, lcMonImpl_ : _LcMonitorImpl):
        if isinstance(lcMonImpl_, _LcMonitorImpl) and lcMonImpl_.isValid and not lcMonImpl_.isDummyMonitor:
            self.__lcMon = lcMonImpl_

    def _UpdateRunCycleLoopTimespanMS(self, rclTSMS_ : int):
        if not (isinstance(rclTSMS_, int) and rclTSMS_ > 0):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00347)
        else:
            self.__rclTSMS = rclTSMS_

    def _SetLcOperationalState(self, eLcCompID_: _ELcCompID, bStartStopFlag_: bool, atask_: _AbstractTask =None) -> bool:
        if self.__isInvalid:
            return False
        if not isinstance(eLcCompID_, _ELcCompID):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00348)
            return False
        if not isinstance(bStartStopFlag_, bool):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00349)
            return False
        if (atask_ is not None) and not isinstance(atask_, _AbstractTask):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00350)
            return False

        self.__apiLck.acquire()
        tuname = _TaskUtil.GetCurPyThread().name if atask_ is None else atask_.taskUniqueName

        res = self.__lcState._SetLcState(eLcCompID_, bStartStopFlag_, frcError_=None, atask_=atask_)
        if not res:
            vlogif._LogOEC(False, _EFwErrorCode.VUE_00030)

        self.__apiLck.release()
        return res

    def _SetLcFailure(self, eFailedCompID_: _ELcCompID, frcError_: _FatalEntry, atask_: _AbstractTask =None, bSkipReply_=False, bInternalCall_ =False) -> bool:
        if self.__isInvalid:
            return False

        if not isinstance(eFailedCompID_, _ELcCompID):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00351)
            return False
        if not isinstance(frcError_, _FatalEntry):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00352)
            return False
        if (atask_ is not None) and not isinstance(atask_, _AbstractTask):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00353)
            return False

        self.__apiLck.acquire()

        tuname = _TaskUtil.GetCurPyThread().name if atask_ is None else atask_.taskUniqueName

        res = self.__lcState._SetLcState(eFailedCompID_, None, frcError_=frcError_, atask_=atask_)

        if not res:
            _tailPart = '\t[FRC]\n\t{}'.format(str(frcError_))
            vlogif._LogOEC(False, _EFwErrorCode.VUE_00031)

        elif not bSkipReply_:
            if self.__lcMgrTIF._TIFPreCheckLcFailureNotification(eFailedCompID_):
                if atask_ is None:
                    atask_ = frcError_._taskInstance
                self.__lcMgrTIF._TIFOnLcFailure(eFailedCompID_, frcError_, atask_=atask_, bPrvRequestReply_=not bInternalCall_)

        self.__apiLck.release()

        return res

    def _Start(self, semStartStop_ : _PySemaphore, lcMgrSetupRunner_):
        _iImplErr = None

        if self.__pythrd is not None:
            _iImplErr = _EFwErrorCode.FE_LCSF_042
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00354)
        elif not isinstance(semStartStop_, _PySemaphore):
            _iImplErr = _EFwErrorCode.FE_LCSF_043
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00355)
        elif lcMgrSetupRunner_ is None:
            _iImplErr = _EFwErrorCode.FE_LCSF_044
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00356)

        if _iImplErr is not None:
            _LcFailure.CheckSetLcSetupFailure(_iImplErr)
            return False

        self.__semSS            = semStartStop_
        self.__pythrd           = _PyThread(group=None, target=self.__RunThrdTgtCallback, args=(), kwargs={}, daemon=None)
        self.__myState          = _LcGuardImpl._ELcGuardState.ePendingRun
        self.__lcMgrSetupRunner = lcMgrSetupRunner_

        self.__pythrd.start()
        return _LcFailure.IsLcErrorFree()

    def _Stop(self, semStartStop_ : _PySemaphore):
        if self.__pythrd is None:
            return
        if not self._isRunning:
            return
        if self.__semSS is not None:
            return
        self.__semSS   = semStartStop_
        self.__myState = _LcGuardImpl._ELcGuardState.ePendingStop

    def _Join(self):
        if self.__isInvalid:
            return
        if self.__pythrd is None:
            return
        if not self._isStarted:
            return
        if self._isStopped or self._isFailed:
            return
        self.__pythrd.join(timeout=None)

    def _ToString(self, *args_, **kwargs_):
        if self.__isInvalid:
            return None
        with self.__apiLck:
            return '[LcG] : state={}'.format(self.__myState.compactName)

    def _CleanUpByOwnerRequest(self):
        if (self.__apiLck is None) or (_LcGuard._singleton is None):
            pass
        elif id(self) != id(_LcGuard._singleton):
            pass
        else:
            _LcGuard._singleton = None

            if self.__lcMonData is not None:
                self.__lcMonData.CleanUp()

            if self.__lcState is not None:
                self.__lcState.CleanUpByOwnerRequest(self._myPPass)

            if self.__lcMgrSetupRunner is not None:
                self.__lcMgrSetupRunner.CleanUp()

            self.__lcMon            = None
            self.__semSS            = None
            self.__pythrd           = None
            self.__apiLck           = None
            self.__myState          = None
            self.__lcState          = None
            self.__rclTSMS          = None
            self.__logAlert         = None
            self.__lcMgrTIF         = None
            self.__logAlertAA       = None
            self.__lcMonData        = None
            self.__maxETAlert       = None
            self.__lcMgrSetupRunner = None

    @property
    def __isInvalid(self):
        return self.__apiLck is None

    def __RunThrdTgtCallback(self):
        self.__myState = _LcGuardImpl._ELcGuardState.eRunning

        if not self.__ExecuteSetupRunner():
            return

        _aliveCtr = self.__RunFull()
        if self.__semSS is not None:
            self.__semSS.release()
            self.__semSS = None
        self.__myState = _LcGuardImpl._ELcGuardState.eDone

    def __ExecuteSetupRunner(self):
        res = False
        if self.__lcMgrSetupRunner is None:
            _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_045)
        else:
            self.__lcMgrSetupRunner()
            if not (self.__lcMgrSetupRunner.isLcMgrSetupRunnerSucceeded and _LcFailure.IsLcErrorFree()):
                vlogif._LogOEC(False, _EFwErrorCode.VUE_00032)
                self.__myState = _LcGuardImpl._ELcGuardState.eFailed

                if _LcFailure.IsLcErrorFree():
                    _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_046)
            else:
                res = True

        if self.__semSS is not None:
            self.__semSS.release()
            self.__semSS = None
        return res

    def __RunFull(self):
        _aliveCtr = 0
        _bSkipMaxExecTimeCheck = self.__maxETAlert is None

        while self._isRunning:
            _aliveCtr += 1

            _lcm = self.__lcMon
            if (_lcm is None) or _lcm.isLcMonitorIdle or (_lcm._mainTLB is None):
                pass
            elif _lcm.isLcMonitorAlive:
                if self.__CheckLcMonAliveness(_aliveCtr):
                    if _bSkipMaxExecTimeCheck:
                        pass
                    elif self.__maxETAlert.CheckAlert():
                        _XLogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcGuardImpl_TextID_002))

                        _lcm._EnableCoordinatedShutdown()

            if _lcm.isLcShutdownEnabled:
                self.__ExecuteShutdownSequence()
                break
            else:
                _TaskUtil.SleepMS(self.__rclTSMS)

        return _aliveCtr

    def __ExecuteShutdownSequence(self):
        _lcm = self.__lcMon

        self.__lcMonData.aliveCounter = 0

        if _lcm.eCurrentShutdownRequest is None:
            _eSDR = _ELcShutdownRequest.ePreShutdown
            self.__lcMgrTIF._TIFOnLcShutdownRequest(_eSDR)

        _bSdcME = None

        if _lcm.isCoordinatedShutdownRunning:
            if not _lcm._isCoordinatedShutdownManagedByMR:
                _bSdcME = _LcShutdownCoordinator(_lcm)
                _bSdcME._ExecuteCoordinatedCeasingGate()

                if _lcm.isCoordinatedShutdownRunning:
                    _bSdcME._ExecuteCoordinatedPreShutdownGate()
            else:
                self.__MonitorShutdownCoordinationByMR(False)

        _eSDR = _ELcShutdownRequest.eShutdown
        self.__lcMgrTIF._TIFOnLcShutdownRequest(_eSDR)

        if _lcm.isCoordinatedShutdownRunning:
            if _bSdcME is not None:
                _bSdcME._ExecuteCoordinatedShutdownGate()

                _LogKPI(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcGuardImpl_TextID_003))
            else:
                self.__MonitorShutdownCoordinationByMR(True)

        _lcm._StopCoordinatedShutdown()

        self.__lcMgrTIF._TIFFinalizeStopFW(False)

        vlogif._LogNewline()
        vlogif._LogNewline()

        if self.__lcState is not None:
            if not self.__lcState.isLcStopped:
                self._SetLcOperationalState(_ELcCompID.eLcMgr, False, atask_=None)

    def __CheckLcMonAliveness(self, lcGAliveCtr_ : int) -> bool:
        _lcm = self.__lcMon

        _bSDEnabled, _curSDR, _aliveCtr = _lcm._GetAliveCounter()
        if _bSDEnabled is None:
            return True

        if not isinstance(_bSDEnabled, bool):
            _bErr = True
        elif (_curSDR is not None) and not isinstance(_curSDR, _ELcShutdownRequest):
            _bErr = True
        elif not isinstance(_aliveCtr, int):
            _bErr = True
        else:
            _bErr = False
        if _bErr:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00357)
            return False

        _md = self.__lcMonData

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

        if _LcGuardImpl.__MIN_OFFSET_RELATIVE_TO_LC_MON_CYCLE is None:
            _lcmCycle = _lcm._runPhaseFrequencyMS
            if (_lcmCycle is None) or (_lcmCycle < self.__rclTSMS):
                minOffset = 1
            else:
                minOffset = _lcm._runPhaseFrequencyMS // self.__rclTSMS
            _LcGuardImpl.__MIN_OFFSET_RELATIVE_TO_LC_MON_CYCLE = minOffset

        if not (_aliveCtr > (_aliveCtrPrv+_LcGuardImpl.__MIN_OFFSET_RELATIVE_TO_LC_MON_CYCLE)):
            _md.aliveAlarmCounter += 1
        else:
            _md.aliveAlarmCounter = 0

        if not _md.isAliveAlarmOn:
            return True

        _missingMS = _lcm._mainTLB.elapsedTimeSinceLastUpdate

        _bDI = _LcGuardImpl.__bSET_LC_FAILURE_UPON_LC_MON_ALIVE_ALARM
        if _bDI:
            if not _LcGuardImpl.__bIGNORE_MRBL_STATE_UPON_LC_MON_ALIVE_ALARM:
                _bDI = not _lcm._mainTLB.isRunning

        if not _bDI:
            return True

        _md.aliveAlarmCounter = 0

        _frcError = _CreateLogImplErrorEC(_EFwErrorCode.FE_00376, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcGuardImpl_TextID_001).format(_missingMS))

        _lcm._EnableCoordinatedShutdown(bManagedByMR_=False)

        if _lcm._isCoordinatedShutdownManagedByMR:
            if _frcError is not None:
                _frcError._UpdateErrorImpact(_EErrorImpact.eNoImpactByOwnerCondition)
                _frcError.CleanUp()
        else:
            if _frcError is None:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00358)
            else:
                if not self._SetLcFailure(_ELcCompID.eFwMain, _frcError, atask_=None, bInternalCall_=True):
                    _frcError._UpdateErrorImpact(_EErrorImpact.eNoImpactByOwnerCondition)
                    _frcError.CleanUp()
        return False

    def __MonitorShutdownCoordinationByMR(self, bCheckForShutdownGate_ : bool):
        _lcm, _md = self.__lcMon, self.__lcMonData

        while True:
            _bGO = _lcm.isCoordinatedShutdownGateOpened if bCheckForShutdownGate_ else _lcm.isCoordinatedPreShutdownGateOpened
            if _bGO:
                break

            _TaskUtil.SleepMS(20)

            _aliveCtrPrv = _md.aliveCounter

            _bSDEnabled, _curSDR, _aliveCtr = _lcm._GetAliveCounter()
            _md.Update(_bSDEnabled, _curSDR, _aliveCtr)

            if not (_aliveCtr > _aliveCtrPrv):
                _md.aliveAlarmCounter += 1
            else:
                _md.aliveAlarmCounter = 0
            continue
