# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : lcmontlb.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from enum import unique

from xcofdk._xcofw.fw.fwssys.fwcore.logging             import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.base.timeutil       import _StopWatch
from xcofdk._xcofw.fw.fwssys.fwcore.base.timeutil       import _PyDateTime
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.aexecutable import _AbstractExecutable
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.sync.mutex      import _Mutex
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.execprofile import _ExecutionProfile
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskbadge   import _TaskBadge
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskstate   import _TaskState
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil    import _ETaskExecutionPhaseID
from xcofdk._xcofw.fw.fwssys.fwcore.types.apobject      import _AbstractSlotsObject
from xcofdk._xcofw.fw.fwssys.fwcore.types.ebitmask       import _EBitMask
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes   import _FwIntEnum
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes   import _FwIntFlag


@unique
class _ELcCeaseTLBState(_FwIntEnum):
    eNone              = 0
    eAbortingCease     = 85490
    eRFTPrepareCeasing = 85491
    eEnterCeasing      = 85492
    ePreShutdownPhase  = 85493
    eShutdownPhase     = 85494
    eDeceased          = 85495

    @property
    def isNone(self):
        return self == _ELcCeaseTLBState.eNone

    @property
    def isPrepareCeasing(self):
        return self == _ELcCeaseTLBState.eRFTPrepareCeasing

    @property
    def isEnterCeasing(self):
        return self == _ELcCeaseTLBState.eEnterCeasing

    @property
    def isPreShutdownPhase(self):
        return self == _ELcCeaseTLBState.ePreShutdownPhase

    @property
    def isShutdownPhase(self):
        return self == _ELcCeaseTLBState.eShutdownPhase

    @property
    def isCeasing(self):
        return _ELcCeaseTLBState.eEnterCeasing.value < self.value < _ELcCeaseTLBState.eDeceased.value

    @property
    def isDeceased(self):
        return self == _ELcCeaseTLBState.eDeceased

    @property
    def isAbortingCease(self):
        return self == _ELcCeaseTLBState.eAbortingCease


@unique
class _ELcCeaseGateFlag(_FwIntFlag):
    ebfNone            = 0x0000
    ebfCeasingGate     = (0x0001 << 0)
    ebfPreShutdownGate = (0x0001 << 1)
    ebfShutdownGate    = (0x0001 << 2)

    @property
    def compactName(self) -> str:
        return self.name[3:]

    @property
    def isNone(self):
        return self==_ELcCeaseGateFlag.ebfNone

    @property
    def isCeasingGate(self):
        return self==_ELcCeaseGateFlag.ebfCeasingGate

    @property
    def isPreShutdownGate(self):
        return self==_ELcCeaseGateFlag.ebfPreShutdownGate

    @property
    def isShutdownGate(self):
        return self==_ELcCeaseGateFlag.ebfShutdownGate

    @staticmethod
    def IsNone(eLcCeaseGateBitMask_: _FwIntFlag):
        return eLcCeaseGateBitMask_==_ELcCeaseGateFlag.ebfNone

    @staticmethod
    def IsCeasingGateSet(eLcCeaseGateBitMask_: _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eLcCeaseGateBitMask_, _ELcCeaseGateFlag.ebfCeasingGate)

    @staticmethod
    def IsPreShutdownGateSet(eLcCeaseGateBitMask_: _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eLcCeaseGateBitMask_, _ELcCeaseGateFlag.ebfPreShutdownGate)

    @staticmethod
    def IsShutdownGateSet(eLcCeaseGateBitMask_: _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eLcCeaseGateBitMask_, _ELcCeaseGateFlag.ebfShutdownGate)

    @staticmethod
    def AddLcCeaseGateFlag(eLcCeaseGateBitMask_: _FwIntFlag, eLcCeaseGateBitFlag_):
        return _EBitMask.AddEnumBitFlag(eLcCeaseGateBitMask_, eLcCeaseGateBitFlag_)

    @staticmethod
    def RemoveLcCeaseGateFlag(eLcCeaseGateBitMask_: _FwIntFlag, eLcCeaseGateBitFlag_):
        return _EBitMask.RemoveEnumBitFlag(eLcCeaseGateBitMask_, eLcCeaseGateBitFlag_)

    @staticmethod
    def IsLcCeaseGateFlagSet(eLcCeaseGateBitMask_: _FwIntFlag, eLcCeaseGateBitFlag_):
        return _EBitMask.IsEnumBitFlagSet(eLcCeaseGateBitMask_, eLcCeaseGateBitFlag_)


class _TlbAlarmStatus(_AbstractSlotsObject):
    __slots__ = [ '__bChangedLSA' , '__ffCtrLSA' , '__ctrLSA' , '__diffLSA' ]

    __REPORT_CYCLE = (2*1000) // 50
    __bIGNORE_VERY_FIRST_LSA_CHANGE = True

    def __init__(self):
        self.__ctrLSA      = 0
        self.__diffLSA     = 0
        self.__ffCtrLSA    = 0
        self.__bChangedLSA = False
        super().__init__()

    @property
    def isLSAlarmON(self) -> bool:
        return False if self.__diffLSA is None else self.__diffLSA > 0

    @property
    def isLSAlarmOFF(self) -> bool:
        return (self.__diffLSA is not None) and (self.__diffLSA < 1)

    @property
    def isLSAlarmChanged(self) -> bool:
        return False if self.__bChangedLSA is None else self.__bChangedLSA

    @property
    def lsAlarmCounter(self) -> int:
        return self.__ctrLSA

    @property
    def lsAlarmDiffTimeMS(self) -> int:
        return self.__diffLSA

    @property
    def lsAlarmToggleCounter(self) -> int:
        return self.__ffCtrLSA

    def _CleanUp(self):
        self.__ctrLSA      = None
        self.__diffLSA     = None
        self.__ffCtrLSA    = None
        self.__bChangedLSA = None

    def _UpdateLSA(self, ctrLSA_ : int, diffLSA_ : int):
        _bAlarmStatusChanged = False

        if ctrLSA_ != self.__ctrLSA:
            self.__ctrLSA = ctrLSA_

        if diffLSA_ != self.__diffLSA:
            _bAlarmStatusChanged =  self.__diffLSA != 0 if _TlbAlarmStatus.__bIGNORE_VERY_FIRST_LSA_CHANGE else True
            self.__diffLSA = diffLSA_

        self.__ffCtrLSA    = 0 if _bAlarmStatusChanged else self.__ffCtrLSA+1
        self.__bChangedLSA = _bAlarmStatusChanged

    def _AddLSAlaramReport(self, taskUniqueName_ : str, lsaReportStr_ : str) -> str:
        return None


class _LcStaticTLB(_AbstractSlotsObject):

    __slots__ = ['__tskBadge' , '__execPrf' , '__bXuTsk' , '__bMainXuTsk']

    def __init__(self, tskBadg_ : _TaskBadge, execPrf_ : _ExecutionProfile, linkedXtbl_ : _AbstractExecutable):
        self.__bXuTsk     = None
        self.__execPrf    = None
        self.__tskBadge   = None
        self.__bMainXuTsk = None
        super().__init__()

        _xprf       = execPrf_._Clone()
        _myTskBadge = tskBadg_._Clone()

        if (_myTskBadge is None) or (_xprf is None):
            if _myTskBadge is not None:
                _myTskBadge.CleanUp()
            if _xprf is not None:
                _xprf.CleanUp()

            self.CleanUp()
            vlogif._LogOEC(True, -1514)
            return

        self.__execPrf    = _xprf
        self.__tskBadge   = _myTskBadge
        self.__bXuTsk     = linkedXtbl_.isXtask or linkedXtbl_.isXTaskRunnable
        self.__bMainXuTsk = linkedXtbl_.isMainXtask or linkedXtbl_.isMainXTaskRunnable

    def __str__(self):
        return self.ToString()

    @property
    def isValid(self):
        return not self.__isInvalid

    @property
    def isXTaskTask(self) -> bool:
        return self.__bXuTsk

    @property
    def isMainXTaskTask(self) -> bool:
        return self.__bMainXuTsk

    @property
    def taskBadge(self) -> _TaskBadge:
        return self.__tskBadge

    @property
    def executionProfile(self) -> _ExecutionProfile:
        return self.__execPrf

    def _ToString(self, *args_, **kwargs_) -> str:
        if self.__isInvalid:
            return None
        return '[LcSTLB][{}]'.format(self.taskBadge.taskUniqueName)

    def _CleanUp(self):
        if self.__tskBadge is None:
            return

        self.__execPrf.CleanUp()
        self.__tskBadge.CleanUp()

        self.__bXuTsk     = None
        self.__execPrf    = None
        self.__tskBadge   = None
        self.__bMainXuTsk = None

    @property
    def __isInvalid(self):
        return self.__tskBadge is None


class _LcDynamicTLB(_AbstractSlotsObject):

    __slots__ = [ '__tlbStat' , '__euRNum' , '__exexPh' , '__tskSt' , '__bCleanedUp' , '__utime' ]
    __theLcmImpl = None
    _dummyTLB    = None

    def __init__(self, lcStatTLB_ : _LcStaticTLB):
        super().__init__()
        self.__tskSt      = None
        self.__utime      = _PyDateTime.now()
        self.__euRNum     = None
        self.__exexPh     = None
        self.__tlbStat    = lcStatTLB_
        self.__bCleanedUp = False

    def __str__(self):
        return self.ToString()

    @property
    def isValid(self):
        return not self.__isInvalid

    @property
    def isDummyTLB(self):
        return id(self) == id(_LcDynamicTLB._dummyTLB)

    @property
    def isLcShutdownEnabled(self) -> bool:
        if self.__isInvalid or self.isDummyTLB: return False
        return _LcDynamicTLB.__theLcmImpl.isLcShutdownEnabled

    @property
    def isCoordinatedShutdownRunning(self) -> bool:
        return False if self.__isInvalid else _LcDynamicTLB.__theLcmImpl.isCoordinatedShutdownRunning

    @property
    def isCleanedUp(self):
        return True if self.__isInvalid else self.__bCleanedUp

    @property
    def isRunning(self):
        return False if (self.__isInvalid or self.__tskSt is None) else self.__tskSt.isRunning

    @property
    def isTerminated(self):
        return True if (self.__isInvalid  or self.__tskSt is None) else self.__tskSt.isTerminated

    @property
    def lcStaticTLB(self) -> _LcStaticTLB:
        return self.__tlbStat

    @property
    def euRNumber(self) -> int:
        return self.__euRNum

    @property
    def eTaskState(self) -> _TaskState._EState:
        return self.__tskSt

    @property
    def eTaskExecPhase(self) -> _ETaskExecutionPhaseID:
        return self.__exexPh

    @property
    def updateTime(self) -> _PyDateTime:
        return self.__utime

    @property
    def _lcMonitor(self):
        res = _LcDynamicTLB.__theLcmImpl
        if res.isDummyMonitor or not res.isValid:
            res = None
        return res

    def _UpdateDynTLB( self
                     , euRNumber_  : int                    =None
                     , execPhase_  : _ETaskExecutionPhaseID =None
                     , tskState_   : _TaskState._EState      =None
                     , bCleanedUp_ : bool                   =None):
        if self.isCleanedUp:
            pass
        elif self.isLcShutdownEnabled:
            pass
        else:
            if tskState_ is not None:
                self.__tskSt = tskState_
            if euRNumber_ is not None:
                self.__euRNum = euRNumber_
            if execPhase_ is not None:
                self.__exexPh = execPhase_
            if bCleanedUp_ is not None:
                self.__bCleanedUp = bCleanedUp_
            self.__utime = _PyDateTime.now()

    def _CreateCeaseTLB(self, mtxData_: _Mutex, bAborting_: bool):
        if self.isCleanedUp:
            res = None
        else:
            _lcm = _LcDynamicTLB.__theLcmImpl
            if _lcm is None:
                res = None
            elif _lcm.isDummyMonitor:
                res = None
            else:
                res = _lcm._CreateCeaseTLB(self.__tlbStat.taskBadge.taskID, mtxData_, bAborting_)
        return res

    @staticmethod
    def _GetDummyTLB():
        return _LcDynamicTLB._dummyTLB

    @staticmethod
    def _CreateTLB(tskInst_, tskBadg_ : _TaskBadge, execPrf_ : _ExecutionProfile, linkedXtbl_ : _AbstractExecutable):
        _lcm = _LcDynamicTLB.__theLcmImpl
        if _lcm is None:
            res = None
        elif _lcm.isDummyMonitor:
            res = _LcDynamicTLB._dummyTLB
        else:
            res = _lcm._CreateTLB(tskInst_, tskBadg_, execPrf_, linkedXtbl_)
            if res is not None:
                res = res.lcDynamicTLB
        return res

    @staticmethod
    def _SetLcMonitorImpl(lcMonImpl_):
        _LcDynamicTLB.__theLcmImpl = lcMonImpl_

    def _ToString(self, *args_, **kwargs_) -> str:
        if self.__isInvalid:
            return None
        return '[LcDTLB][{}] taskState={}'.format(self.__tlbStat.taskBadge.taskUniqueName, str(self.__tskSt))

    def _CleanUp(self):
        if self.__tlbStat is None:
            return

        self.__tskSt      = None
        self.__utime      = None
        self.__euRNum     = None
        self.__exexPh     = None
        self.__tlbStat    = None
        self.__bCleanedUp = None

    @property
    def __isInvalid(self):
        return (_LcDynamicTLB.__theLcmImpl is None) or (self.__tlbStat is None)


class _LcCeaseTLB(_AbstractSlotsObject):

    __slots__ = [ '__tlbStat' , '__mtxData' , '__eCState' , '__caCtr' , '__eCGBM' , '__utime' ]
    __theLcmImpl = None

    def __init__(self, lcStatTLB_: _LcStaticTLB, mtxData_ : _Mutex, bAborting_ : bool):
        super().__init__()
        self.__caCtr   = 0
        self.__eCGBM   = _ELcCeaseGateFlag.ebfNone
        self.__utime   = _PyDateTime.now()
        self.__mtxData = mtxData_
        self.__tlbStat = lcStatTLB_
        if bAborting_:
            self.__eCState = _ELcCeaseTLBState.eAbortingCease
        else:
            self.__eCState = _ELcCeaseTLBState.eRFTPrepareCeasing

    def __str__(self):
        return self.ToString()

    @property
    def isValid(self):
        return not self.__isInvalid

    @property
    def isCeasing(self) -> bool:
        if self.__isInvalid:
            return False
        with self.__mtxData:
            return self.__eCState.isCeasing and not (self.__eCState.isAbortingCease or not _LcCeaseTLB.__theLcmImpl.isCoordinatedShutdownRunning)

    @property
    def isDeceased(self) -> bool:
        if self.__isInvalid:
            return False
        with self.__mtxData:
            return self.__eCState.isDeceased

    @property
    def isAbortingCease(self) -> bool:
        if self.__isInvalid:
            return False
        with self.__mtxData:
            return self.__eCState.isAbortingCease

    @property
    def isLcShutdownEnabled(self) -> bool:
        return False if self.__isInvalid else _LcCeaseTLB.__theLcmImpl.isLcShutdownEnabled

    @property
    def isCoordinatedShutdownRunning(self) -> bool:
        return False if self.__isInvalid else _LcCeaseTLB.__theLcmImpl.isCoordinatedShutdownRunning

    @property
    def isCoordinatedShutdownGateOpened(self) -> bool:
        return False if self.__isInvalid else _LcCeaseTLB.__theLcmImpl.isCoordinatedShutdownGateOpened

    @property
    def lcStaticTLB(self) -> _LcStaticTLB:
        return self.__tlbStat

    @property
    def ceaseAliveCounter(self) -> int:
        if self.__isInvalid:
            res = None
        else:
            with self.__mtxData:
                res = self.__caCtr
        return res

    @property
    def eCeaseState(self) -> _ELcCeaseTLBState:
        if self.__isInvalid:
            res = _ELcCeaseTLBState.eNone
        else:
            with self.__mtxData:
                res = self.__eCState
        return res

    @property
    def updateTime(self) -> _PyDateTime:
        return self.__utime

    def HopToNextCeaseState(self, bAborting_ =False):
        if self.__isInvalid:
            pass
        else:
            with self.__mtxData:
                if self.__eCState.isDeceased:
                    pass
                else:
                    self.UpdateCeaseState(bAborting_)
                    if self.__eCState.isAbortingCease:
                        self.__eCState = _ELcCeaseTLBState.eDeceased
                    else:
                        self.__eCState = _ELcCeaseTLBState(self.__eCState.value+1)

    def UpdateCeaseState(self, bAborting_ : bool):
        if self.__isInvalid:
            pass
        else:
            with self.__mtxData:
                self.__utime = _PyDateTime.now()
                if bAborting_:
                    self.__eCState = _ELcCeaseTLBState.eAbortingCease

    def IncrementCeaseAliveCounter(self) -> int:
        if self.__isInvalid:
            res = None
        else:
            with self.__mtxData:
                self.__utime  = _PyDateTime.now()
                self.__caCtr += 1
                res = self.__caCtr
        return res

    @staticmethod
    def _SetLcMonitorImpl(lcMonImpl_):
        _LcCeaseTLB.__theLcmImpl = lcMonImpl_

    @property
    def _isCeasingGateOpened(self):
        if self.__isInvalid:
            return True
        else:
            with self.__mtxData:
                return _ELcCeaseGateFlag.IsCeasingGateSet(self.__eCGBM)

    @property
    def _isPreShutdownGateOpened(self):
        if self.__isInvalid:
            return True
        else:
            with self.__mtxData:
                return _ELcCeaseGateFlag.IsPreShutdownGateSet(self.__eCGBM)

    @property
    def _isShutdownGateOpened(self):
        if self.__isInvalid:
            return True
        else:
            with self.__mtxData:
                return _ELcCeaseGateFlag.IsShutdownGateSet(self.__eCGBM)

    @property
    def _lcMonitor(self):
        res = _LcCeaseTLB.__theLcmImpl
        if res.isDummyMonitor or not res.isValid:
            res = None
        return res

    @property
    def eCurrentShutdownRequest(self):
        return None if self._lcMonitor is None else self._lcMonitor.eCurrentShutdownRequest

    def _OpenCeasingGate(self, timeout_ =None):
        if self.__isInvalid:
            return

        if timeout_ is None:
            _bLocked = self.__mtxData.Take()
        else:
            _bLocked = self.__mtxData.TakeWait(timeout_)
        if _bLocked:
            if not _ELcCeaseGateFlag.IsCeasingGateSet(self.__eCGBM):
                eBM = _ELcCeaseGateFlag.ebfCeasingGate
                self.__eCGBM = _ELcCeaseGateFlag.AddLcCeaseGateFlag(self.__eCGBM, eBM)
            self.__mtxData.Give()

    def _OpenPreShutdownGate(self, timeout_ =None):
        if self.__isInvalid:
            return

        if timeout_ is None:
            _bLocked = self.__mtxData.Take()
        else:
            _bLocked = self.__mtxData.TakeWait(timeout_)
        if _bLocked:
            if not _ELcCeaseGateFlag.IsPreShutdownGateSet(self.__eCGBM):
                eBM = _ELcCeaseGateFlag.ebfPreShutdownGate
                self.__eCGBM = _ELcCeaseGateFlag.AddLcCeaseGateFlag(self.__eCGBM, eBM)
            self.__mtxData.Give()

    def _OpenShutdownGate(self, timeout_ =None):
        if self.__isInvalid:
            return

        if timeout_ is None:
            _bLocked = self.__mtxData.Take()
        else:
            _bLocked = self.__mtxData.TakeWait(timeout_)
        if _bLocked:
            if not _ELcCeaseGateFlag.IsShutdownGateSet(self.__eCGBM):
                eBM = _ELcCeaseGateFlag.ebfShutdownGate
                self.__eCGBM = _ELcCeaseGateFlag.AddLcCeaseGateFlag(self.__eCGBM, eBM)
            self.__mtxData.Give()

    def _ToString(self, *args_, **kwargs_):
        if self.__isInvalid:
            return None
        with self.__mtxData:
            return '[LcCTLB][{}] : ceaseState = {}'.format(
                self.__tlbStat.taskBadge.taskUniqueName, self.__eCState.compactName)

    def _CleanUp(self):
        if self.__tlbStat is None:
            return

        self.__mtxData.CleanUp()

        self.__caCtr   = None
        self.__eCGBM   = None
        self.__utime   = None
        self.__mtxData = None
        self.__eCState = None
        self.__tlbStat = None

    @property
    def __isInvalid(self):
        return (_LcCeaseTLB.__theLcmImpl is None) or (self.__tlbStat is None)


class _LcTLB(_AbstractSlotsObject):



    __slots__ = [ '__sw' , '__tskInst' , '__tlbDyn' , '__tlbCease' , '__tlbAS']

    __LIFE_SIGN_ALARM_THRESHOLD = 2

    def __init__(self, tskInst_, tskBadg_ : _TaskBadge, execPrf_ : _ExecutionProfile, linkedXtbl_ : _AbstractExecutable):
        self.__sw       = None
        self.__tlbDyn   = None
        self.__tskInst  = None
        self.__tlbCease = None
        super().__init__()

        _st = _LcStaticTLB(tskBadg_, execPrf_, linkedXtbl_)
        if _st.taskBadge is None:
            self.CleanUp()
            return

        self.__sw      = _StopWatch()
        self.__tlbAS   = _TlbAlarmStatus()
        self.__tlbDyn  = _LcDynamicTLB(_st)
        self.__tskInst = tskInst_

    def __str__(self):
        return self.ToString()

    @property
    def isValid(self):
        return not self.__isInvalid

    @property
    def isCleanedUp(self):
        return True if self.__isInvalid else self.__tlbDyn.isCleanedUp

    @property
    def isRunning(self):
        return False if self.__isInvalid else self.__tlbDyn.isRunning

    @property
    def isTerminated(self):
        return True if self.__isInvalid else self.__tlbDyn.isTerminated

    @property
    def isTerminatedAfterStart(self):
        return True if self.__isInvalid else (self.__tlbDyn.eTaskState is not None) and self.__tlbDyn.isTerminated

    @property
    def aliveCounter(self) -> int:
        return None if self.__isInvalid else self.__tlbDyn.euRNumber

    @property
    def ceaseAliveCounter(self) -> int:
        return None if self.__tlbCease is None else self.__tlbCease.ceaseAliveCounter

    @property
    def lcStaticTLB(self) -> _LcStaticTLB:
        return None if self.__isInvalid else self.__tlbDyn.lcStaticTLB

    @property
    def lcDynamicTLB(self) -> _LcDynamicTLB:
        return None if self.__isInvalid else self.__tlbDyn

    @property
    def lcCeaseTLB(self) -> _LcCeaseTLB:
        return self.__tlbCease

    @property
    def stopWatch(self) -> _StopWatch:
        return self.__sw

    @property
    def updateTime(self) -> _PyDateTime:
        if self.__isInvalid:
            _tlb = None
        else:
            _tlb = self.__tlbDyn if self.__tlbCease is None else self.__tlbCease
        return None if _tlb is None else _tlb.updateTime

    @property
    def elapsedTimeSinceLastUpdate(self) -> int:
        ut = self.updateTime
        if ut is None:
            return None
        return (_PyDateTime.now() - ut).microseconds // 1000

    @property
    def tlbAlarmStatus(self) -> _TlbAlarmStatus:
        return None if self.__isInvalid else self.__tlbAS

    @property
    def _taskInstance(self):
        return self.__tskInst

    def _SetCeaseTLB(self, lcCeaseTLB_ : _LcCeaseTLB):
        self.__tlbCease = lcCeaseTLB_

    def _UpdateTLB(self, bCeaseMode_ : bool, lsaReportStr_ : str =None) -> str:

        if self.__isInvalid:
            return None

        if bCeaseMode_:
            return lsaReportStr_


        _td = self.__tlbDyn

        if _td.isCleanedUp:
            return lsaReportStr_
        if _td.isTerminated:
            return lsaReportStr_

        _tpTS = _td.lcStaticTLB.executionProfile._revisedPerLcMonCycleTotalProcTimespanMS
        if _tpTS < 1:
            return lsaReportStr_

        _elapsedTS = self.__sw.StopRelative(usTimeTicksStop_=None)
        _diffTS    = _elapsedTS.totalMS - _tpTS
        _lsaCtr    = self.__tlbAS.lsAlarmCounter

        if _diffTS > _LcTLB.__LIFE_SIGN_ALARM_THRESHOLD:
            _lsaCtr += 1
        else:
            _lsaCtr, _diffTS = 0, 0

        self.__tlbAS._UpdateLSA(_lsaCtr, _diffTS)
        if lsaReportStr_ is None:
            pass
        else:
            lsaReportStr_ = self.__tlbAS._AddLSAlaramReport(self.lcStaticTLB.taskBadge.taskUniqueName, lsaReportStr_)
        return lsaReportStr_

    def _ToString(self, *args_, **kwargs_):
        if self.__isInvalid:
            return None
        return '[LcTLB][{}]'.format(self.lcStaticTLB.taskBadge.taskUniqueName)

    def _CleanUp(self):
        if self.__sw is None:
            return

        if self.__tlbCease is not None:
            self.__tlbCease.CleanUp()

        if self.__tlbDyn is not None:
            _st = self.__tlbDyn.lcStaticTLB
            self.__tlbDyn.CleanUp()
            if _st is not None:
                _st.CleanUp()

        if self.__tlbAS is not None:
            self.__tlbAS.CleanUp()
        if self.__sw is not None:
            self.__sw.CleanUp()

        self.__sw       = None
        self.__tlbAS    = None
        self.__tlbDyn   = None
        self.__tskInst  = None
        self.__tlbCease = None

    @property
    def __isInvalid(self):
        return self.__sw is None


class _LcDummyDynamicTLB(_LcDynamicTLB):
    __slots__ = []

    def __init__(self):
        super().__init__(None)

    @staticmethod
    def _CreateDummyTLB():
        if _LcDynamicTLB._dummyTLB is None:
            _LcDynamicTLB._dummyTLB = _LcDummyDynamicTLB()

    @staticmethod
    def _CleanUpDummyTLB():
        if _LcDynamicTLB._dummyTLB is not None:
            _LcDynamicTLB._dummyTLB.CleanUp()
            _LcDynamicTLB._dummyTLB = None
