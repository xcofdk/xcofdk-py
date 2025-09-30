# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : lcmontlb.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum import unique

from _fw.fwssys.fwcore.logging             import vlogif
from _fw.fwssys.fwcore.base.timeutil       import _StopWatch
from _fw.fwssys.fwcore.base.timeutil       import _PyDateTime
from _fw.fwssys.fwcore.ipc.sync.mutex      import _Mutex
from _fw.fwssys.fwcore.ipc.tsk.taskxcard   import _TaskXCard
from _fw.fwssys.fwcore.ipc.tsk.taskbadge   import _TaskBadge
from _fw.fwssys.fwcore.ipc.tsk.taskstate   import _TaskState
from _fw.fwssys.fwcore.ipc.tsk.taskutil    import _ETaskXPhaseID
from _fw.fwssys.fwcore.types.apobject      import _AbsSlotsObject
from _fw.fwssys.fwcore.types.ebitmask      import _EBitMask
from _fw.fwssys.fwcore.types.commontypes   import _FwIntEnum
from _fw.fwssys.fwcore.types.commontypes   import _FwIntFlag
from _fw.fwssys.fwerrh.fwerrorcodes        import _EFwErrorCode
from _fwa.fwsubsyscoding                   import _FwSubsysCoding

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

@unique
class _ELcCeaseTLBState(_FwIntEnum):
    eNone              = 0
    eEndingCease       = 85490
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
    def isEndingCease(self):
        return self == _ELcCeaseTLBState.eEndingCease

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

class _TlbAlarmStatus(_AbsSlotsObject):
    __slots__ = [ '__c' , '__bC' , '__d' , '__cff' ]

    __REPORT_CYCLE = (2*1000) // 50

    __bIVFLC = True

    def __init__(self):
        self.__c   = 0
        self.__d   = 0
        self.__bC  = False
        self.__cff = 0
        super().__init__()

    @property
    def isLSAlarmON(self) -> bool:
        return False if self.__d is None else self.__d > 0

    @property
    def isLSAlarmOFF(self) -> bool:
        return (self.__d is not None) and (self.__d < 1)

    @property
    def isLSAlarmChanged(self) -> bool:
        return False if self.__bC is None else self.__bC

    @property
    def lsAlarmCounter(self) -> int:
        return self.__c

    @property
    def lsAlarmDiffTimeMS(self) -> int:
        return self.__d

    @property
    def lsAlarmToggleCounter(self) -> int:
        return self.__cff

    def _CleanUp(self):
        self.__c   = None
        self.__d   = None
        self.__bC  = None
        self.__cff = None

    def _UpdateLSA(self, ctrLSA_ : int, diffLSA_ : int):
        _bC = False

        if ctrLSA_ != self.__c:
            self.__c = ctrLSA_

        if diffLSA_ != self.__d:
            _bC =  self.__d != 0 if _TlbAlarmStatus.__bIVFLC else True
            self.__d = diffLSA_

        self.__bC  = _bC
        self.__cff = 0 if _bC else self.__cff+1

class _LcStaticTLB(_AbsSlotsObject):
    __slots__ = [ '__bU' , '__tb' , '__xc' ]

    def __init__(self, tskBadg_ : _TaskBadge, xcard_ : _TaskXCard, bUTask_ : bool):
        self.__bU = None
        self.__tb = None
        self.__xc = None
        super().__init__()

        _xc = xcard_._Clone()
        _tb = tskBadg_._Clone()

        if (_tb is None) or (_xc is None):
            if _tb is not None:
                _tb.CleanUp()
            if _xc is not None:
                _xc.CleanUp()
            self.CleanUp()
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00420)
            return

        self.__bU = bUTask_
        self.__xc = _xc
        self.__tb = _tb

    def __str__(self):
        return self.ToString()

    @property
    def isValid(self):
        return not self.__isInvalid

    @property
    def isXTaskTLB(self) -> bool:
        return self.__bU

    @property
    def taskBadge(self) -> _TaskBadge:
        return self.__tb

    @property
    def xCard(self) -> _TaskXCard:
        return self.__xc

    def _ToString(self) -> str:
        if self.__isInvalid:
            return None
        return _FwTDbEngine.GetText(_EFwTextID.eLcTLB_ToString_001).format(self.taskBadge.dtaskName)

    def _CleanUp(self):
        if self.__tb is None:
            return

        self.__xc.CleanUp()
        self.__tb.CleanUp()

        self.__bU = None
        self.__tb = None
        self.__xc = None

    @property
    def __isInvalid(self):
        return self.__tb is None

class _LcDynamicTLB(_AbsSlotsObject):
    __slots__ = [ '__st' , '__bC' , '__ut' , '__tst' , '__xph' , '__xrn' ]
    
    __sgltn = None
    _dtlb   = None

    def __init__(self, lcStatTLB_ : _LcStaticTLB):
        super().__init__()
        self.__bC  = False
        self.__st  = None
        self.__ut  = _PyDateTime.now()
        self.__tst = lcStatTLB_
        self.__xph = None
        self.__xrn = None

    def __str__(self):
        return self.ToString()

    @property
    def isValid(self):
        return not self.__isInvalid

    @property
    def isDummyTLB(self):
        return id(self) == id(_LcDynamicTLB._dtlb)

    @property
    def isLcShutdownEnabled(self) -> bool:
        if self.__isInvalid or self.isDummyTLB: return False
        return _LcDynamicTLB.__sgltn.isLcShutdownEnabled

    @property
    def isCoordinatedShutdownRunning(self) -> bool:
        return False if self.__isInvalid else _LcDynamicTLB.__sgltn.isCoordinatedShutdownRunning

    @property
    def isCleanedUp(self):
        return True if self.__isInvalid else self.__bC

    @property
    def isRunning(self):
        return False if (self.__isInvalid or self.__st is None) else self.__st.isRunning

    @property
    def isTerminated(self):
        return True if (self.__isInvalid  or self.__st is None) else self.__st.isTerminated

    @property
    def lcStaticTLB(self) -> _LcStaticTLB:
        return self.__tst

    @property
    def xrNumber(self) -> int:
        return self.__xrn

    @property
    def taskState(self) -> _TaskState._EState:
        return self.__st

    @property
    def taskXPhase(self) -> _ETaskXPhaseID:
        return self.__xph

    @property
    def updateTime(self) -> _PyDateTime:
        return self.__ut

    @property
    def _lcMonitor(self):
        res = _LcDynamicTLB.__sgltn
        if res.isDummyMonitor or not res.isValid:
            res = None
        return res

    def _UpdateDynTLB( self
                     , euRNumber_  : int                =None
                     , xphaseID_   : _ETaskXPhaseID     =None
                     , tskState_   : _TaskState._EState =None
                     , bCleanedUp_ : bool               =None):
        if self.isCleanedUp or self.isLcShutdownEnabled:
            pass
        else:
            if tskState_ is not None:
                self.__st = tskState_
            if euRNumber_ is not None:
                self.__xrn = euRNumber_
            if xphaseID_ is not None:
                self.__xph = xphaseID_
            if bCleanedUp_ is not None:
                self.__bC = bCleanedUp_
            self.__ut = _PyDateTime.now()

    def _CreateCeaseTLB(self, md_: _Mutex, bEnding_: bool):
        if self.isCleanedUp:
            res = None
        else:
            _lcm = _LcDynamicTLB.__sgltn
            if _lcm is None:
                res = None
            elif _lcm.isDummyMonitor:
                res = None
            else:
                res = _lcm._CreateCeaseTLB(self.__tst.taskBadge.dtaskUID, md_, bEnding_)
        return res

    @staticmethod
    def _GetDummyTLB():
        return _LcDynamicTLB._dtlb

    @staticmethod
    def _CreateTLB(tskInst_, tskBadg_ : _TaskBadge, xcard_ : _TaskXCard, bUTask_ : bool):
        _lcm = _LcDynamicTLB.__sgltn
        if _lcm is None:
            res = None
        elif _lcm.isDummyMonitor:
            res = _LcDynamicTLB._dtlb
        else:
            res = _lcm._CreateTLB(tskInst_, tskBadg_, xcard_, bUTask_)
            if res is not None:
                res = res.lcDynamicTLB
        return res

    @staticmethod
    def _SetLcMonitorImpl(lcMonImpl_):
        _LcDynamicTLB.__sgltn = lcMonImpl_

    def _ToString(self) -> str:
        if self.__isInvalid:
            return None
        return _FwTDbEngine.GetText(_EFwTextID.eLcTLB_ToString_002).format(self.__tst.taskBadge.dtaskName, str(self.__st))

    def _CleanUp(self):
        if self.__tst is None:
            return

        self.__bC  = None
        self.__st  = None
        self.__ut  = None
        self.__tst = None
        self.__xrn = None
        self.__xph = None

    @property
    def __isInvalid(self):
        return (_LcDynamicTLB.__sgltn is None) or (self.__tst is None)

class _LcCeaseTLB(_AbsSlotsObject):
    __slots__ = [ '__ut' , '__tst' , '__md' , '__cst' , '__cac' , '__cgf' ]

    __sgltn = None

    def __init__(self, lcStatTLB_: _LcStaticTLB, md_ : _Mutex, bEnding_ : bool):
        super().__init__()
        self.__md  = md_
        self.__ut  = _PyDateTime.now()
        self.__cac = 0
        self.__cgf = _ELcCeaseGateFlag.ebfNone
        self.__cst = _ELcCeaseTLBState.eEndingCease if bEnding_ else _ELcCeaseTLBState.eRFTPrepareCeasing
        self.__tst = lcStatTLB_

    def __str__(self):
        return self.ToString()

    @property
    def isValid(self):
        return not self.__isInvalid

    @property
    def isCeasing(self) -> bool:
        if self.__isInvalid:
            return False
        with self.__md:
            return self.__cst.isCeasing and not (self.__cst.isEndingCease or not _LcCeaseTLB.__sgltn.isCoordinatedShutdownRunning)

    @property
    def isDeceased(self) -> bool:
        if self.__isInvalid:
            return False
        with self.__md:
            return self.__cst.isDeceased

    @property
    def isEndingCease(self) -> bool:
        if self.__isInvalid:
            return False
        with self.__md:
            return self.__cst.isEndingCease

    @property
    def isLcShutdownEnabled(self) -> bool:
        return False if self.__isInvalid else _LcCeaseTLB.__sgltn.isLcShutdownEnabled

    @property
    def isCoordinatedShutdownRunning(self) -> bool:
        return False if self.__isInvalid else _LcCeaseTLB.__sgltn.isCoordinatedShutdownRunning

    @property
    def isCoordinatedShutdownGateOpened(self) -> bool:
        return False if self.__isInvalid else _LcCeaseTLB.__sgltn.isCoordinatedShutdownGateOpened

    @property
    def lcStaticTLB(self) -> _LcStaticTLB:
        return self.__tst

    @property
    def ceaseAliveCounter(self) -> int:
        if self.__isInvalid:
            res = None
        else:
            with self.__md:
                res = self.__cac
        return res

    @property
    def ceaseState(self) -> _ELcCeaseTLBState:
        if self.__isInvalid:
            res = _ELcCeaseTLBState.eNone
        else:
            with self.__md:
                res = self.__cst
        return res

    @property
    def updateTime(self) -> _PyDateTime:
        return self.__ut

    def HopToNextCeaseState(self, bEnding_ =False):
        if not  self.__isInvalid:
            with self.__md:
                if not self.__cst.isDeceased:
                    self.UpdateCeaseState(bEnding_)
                    if self.__cst.isEndingCease:
                        self.__cst = _ELcCeaseTLBState.eDeceased
                    else:
                        self.__cst = _ELcCeaseTLBState(self.__cst.value+1)

    def UpdateCeaseState(self, bEnding_ : bool):
        if not self.__isInvalid:
            with self.__md:
                self.__ut = _PyDateTime.now()
                if bEnding_:
                    self.__cst = _ELcCeaseTLBState.eEndingCease

    def IncrementCeaseAliveCounter(self) -> int:
        if self.__isInvalid:
            res = None
        else:
            with self.__md:
                self.__ut  = _PyDateTime.now()
                self.__cac += 1
                res = self.__cac
        return res

    @staticmethod
    def _SetLcMonitorImpl(lcMonImpl_):
        _LcCeaseTLB.__sgltn = lcMonImpl_

    @property
    def _isCeasingGateOpened(self):
        if self.__isInvalid:
            return True
        else:
            with self.__md:
                return _ELcCeaseGateFlag.IsCeasingGateSet(self.__cgf)

    @property
    def _isPreShutdownGateOpened(self):
        if self.__isInvalid:
            return True
        else:
            with self.__md:
                return _ELcCeaseGateFlag.IsPreShutdownGateSet(self.__cgf)

    @property
    def _isShutdownGateOpened(self):
        if self.__isInvalid:
            return True
        else:
            with self.__md:
                return _ELcCeaseGateFlag.IsShutdownGateSet(self.__cgf)

    @property
    def _lcMonitor(self):
        res = _LcCeaseTLB.__sgltn
        if res.isDummyMonitor or not res.isValid:
            res = None
        return res

    @property
    def curShutdownRequest(self):
        return None if self._lcMonitor is None else self._lcMonitor.curShutdownRequest

    def _OpenCeasingGate(self, timeout_ =None):
        if self.__isInvalid:
            return

        if timeout_ is None:
            _bLocked = self.__md.Take()
        else:
            _bLocked = self.__md.TakeWait(timeout_)
        if _bLocked:
            if not _ELcCeaseGateFlag.IsCeasingGateSet(self.__cgf):
                self.__cgf = _ELcCeaseGateFlag.AddLcCeaseGateFlag(self.__cgf, _ELcCeaseGateFlag.ebfCeasingGate)
            self.__md.Give()

    def _OpenPreShutdownGate(self, timeout_ =None):
        if self.__isInvalid:
            return

        if timeout_ is None:
            _bLocked = self.__md.Take()
        else:
            _bLocked = self.__md.TakeWait(timeout_)
        if _bLocked:
            if not _ELcCeaseGateFlag.IsPreShutdownGateSet(self.__cgf):
                self.__cgf = _ELcCeaseGateFlag.AddLcCeaseGateFlag(self.__cgf, _ELcCeaseGateFlag.ebfPreShutdownGate)
            self.__md.Give()

    def _OpenShutdownGate(self, timeout_ =None):
        if self.__isInvalid:
            return

        if timeout_ is None:
            _bLocked = self.__md.Take()
        else:
            _bLocked = self.__md.TakeWait(timeout_)
        if _bLocked:
            if not _ELcCeaseGateFlag.IsShutdownGateSet(self.__cgf):
                self.__cgf = _ELcCeaseGateFlag.AddLcCeaseGateFlag(self.__cgf, _ELcCeaseGateFlag.ebfShutdownGate)
            self.__md.Give()

    def _ToString(self):
        if self.__isInvalid:
            return None
        with self.__md:
            return _FwTDbEngine.GetText(_EFwTextID.eLcTLB_ToString_003).format(self.__tst.taskBadge.dtaskName, self.__cst.compactName)

    def _CleanUp(self):
        if self.__tst is None:
            return

        self.__md.CleanUp()

        self.__ut  = None
        self.__md  = None
        self.__cac = None
        self.__cgf = None
        self.__cst = None
        self.__tst = None

    @property
    def __isInvalid(self):
        return (_LcCeaseTLB.__sgltn is None) or (self.__tst is None)

class _LcTLB(_AbsSlotsObject):
    __slots__ = [ '__i' , '__sw' , '__td' , '__tc' , '__as']

    __LSAT = 2

    def __init__(self, tskInst_, tskBadg_ : _TaskBadge, xcard_ : _TaskXCard, bUTask_ : bool):
        self.__i  = None
        self.__tc = None
        self.__td = None
        self.__sw = None
        super().__init__()

        _st = _LcStaticTLB(tskBadg_, xcard_, bUTask_)
        if _st.taskBadge is None:
            self.CleanUp()
            return

        self.__i  = tskInst_
        self.__td = _LcDynamicTLB(_st)
        self.__as = _TlbAlarmStatus()
        self.__sw = _StopWatch()

    def __str__(self):
        return self.ToString()

    @property
    def isValid(self):
        return not self.__isInvalid

    @property
    def isCleanedUp(self):
        return True if self.__isInvalid else self.__td.isCleanedUp

    @property
    def isRunning(self):
        return False if self.__isInvalid else self.__td.isRunning

    @property
    def isTerminated(self):
        return True if self.__isInvalid else self.__td.isTerminated

    @property
    def isTerminatedAfterStart(self):
        return True if self.__isInvalid else (self.__td.taskState is not None) and self.__td.isTerminated

    @property
    def aliveCounter(self) -> int:
        return None if self.__isInvalid else self.__td.xrNumber

    @property
    def ceaseAliveCounter(self) -> int:
        return None if self.__tc is None else self.__tc.ceaseAliveCounter

    @property
    def lcStaticTLB(self) -> _LcStaticTLB:
        return None if self.__isInvalid else self.__td.lcStaticTLB

    @property
    def lcDynamicTLB(self) -> _LcDynamicTLB:
        return None if self.__isInvalid else self.__td

    @property
    def lcCeaseTLB(self) -> _LcCeaseTLB:
        return self.__tc

    @property
    def stopWatch(self) -> _StopWatch:
        return self.__sw

    @property
    def updateTime(self) -> _PyDateTime:
        if self.__isInvalid:
            _tlb = None
        else:
            _tlb = self.__td if self.__tc is None else self.__tc
        return None if _tlb is None else _tlb.updateTime

    @property
    def elapsedTimeSinceLastUpdate(self) -> int:
        _ut = self.updateTime
        if _ut is None:
            return None
        return (_PyDateTime.now() - _ut).microseconds // 1000

    @property
    def _taskInstance(self):
        return self.__i

    def _SetCeaseTLB(self, lcCeaseTLB_ : _LcCeaseTLB):
        self.__tc = lcCeaseTLB_

    def _UpdateTLB(self, bCeaseMode_ : bool, lsaReportStr_ : str =None) -> str:
        if self.__isInvalid:
            return None

        if bCeaseMode_:
            return lsaReportStr_

        _td = self.__td

        if _td.isCleanedUp:
            return lsaReportStr_
        if _td.isTerminated:
            return lsaReportStr_

        _tpTS = _td.lcStaticTLB.xCard._revisedPerLcMonCycleTotalProcTimespanMS
        if _tpTS < 1:
            return lsaReportStr_

        _elapsedTS = self.__sw.StopRelative(usTimeTicksStop_=None)
        _diffTS    = _elapsedTS.totalMS - _tpTS
        _lsaCtr    = self.__as.lsAlarmCounter

        if _diffTS > _LcTLB.__LSAT:
            _lsaCtr += 1
        else:
            _lsaCtr, _diffTS = 0, 0

        self.__as._UpdateLSA(_lsaCtr, _diffTS)
        return lsaReportStr_

    def _ToString(self):
        if self.__isInvalid:
            return None
        return _FwTDbEngine.GetText(_EFwTextID.eLcTLB_ToString_004).format(self.lcStaticTLB.taskBadge.dtaskName)

    def _CleanUp(self):
        if self.__sw is None:
            return

        if self.__tc is not None:
            self.__tc.CleanUp()
        if self.__td is not None:
            _st = self.__td.lcStaticTLB
            self.__td.CleanUp()
            if _st is not None:
                _st.CleanUp()
        if self.__as is not None:
            self.__as.CleanUp()
        if self.__sw is not None:
            self.__sw.CleanUp()

        self.__i  = None
        self.__as = None
        self.__sw = None
        self.__tc = None
        self.__td = None

    @property
    def __isInvalid(self):
        return self.__sw is None

class _LcDummyDynamicTLB(_LcDynamicTLB):
    __slots__ = []

    def __init__(self):
        super().__init__(None)

    @staticmethod
    def _CreateDummyTLB():
        if _LcDynamicTLB._dtlb is None:
            _LcDynamicTLB._dtlb = _LcDummyDynamicTLB()

    @staticmethod
    def _CleanUpDummyTLB():
        if _LcDynamicTLB._dtlb is not None:
            _LcDynamicTLB._dtlb.CleanUp()
            _LcDynamicTLB._dtlb = None
