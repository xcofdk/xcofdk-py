# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : lcmonimpl.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum import unique

from _fw.fwssys.fwcore.logging.logif     import _LogKPI
from _fw.fwssys.fwcore.logging.logif     import _LogWarning
from _fw.fwssys.fwcore.logging.logif     import _LogUrgentWarning
from _fw.fwssys.fwcore.logging           import vlogif
from _fw.fwssys.fwcore.ipc.sync.mutex    import _Mutex
from _fw.fwssys.fwcore.ipc.tsk.taskxcard import _TaskXCard
from _fw.fwssys.fwcore.ipc.tsk.taskbadge import _TaskBadge
from _fw.fwssys.fwcore.ipc.tsk.taskutil  import _TaskUtil
from _fw.fwssys.fwcore.lc.lcproxydefines import _ELcSDRequest
from _fw.fwssys.fwcore.lc.lcxstate       import _ELcXState
from _fw.fwssys.fwcore.lc.lcxstate       import _LcXStateDriver
from _fw.fwssys.fwcore.lc.lcxstate       import _LcXStateHistory
from _fw.fwssys.fwcore.lc.lcxstate       import _LcFailure
from _fw.fwssys.fwcore.lc.lcmn.lcmontlb  import _LcTLB
from _fw.fwssys.fwcore.lc.lcmn.lcmontlb  import _LcDynamicTLB
from _fw.fwssys.fwcore.lc.lcmn.lcmontlb  import _LcCeaseTLB
from _fw.fwssys.fwcore.lc.lcmn.lcmontlb  import _LcDummyDynamicTLB
from _fw.fwssys.fwcore.lc.lcmn.lcmontlb  import _ELcCeaseTLBState
from _fw.fwssys.fwcore.types.aobject     import _AbsSlotsObject
from _fw.fwssys.fwcore.types.ebitmask    import _EBitMask
from _fw.fwssys.fwcore.types.commontypes import _FwIntFlag
from _fw.fwssys.fwerrh.fwerrorcodes      import _EFwErrorCode

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _LcMonGCItem:
    __slots__ = [ '__a' , '__i' ]

    def __init__(self, item_  : _AbsSlotsObject):
        self.__a  = 0
        self.__i = item_

    def __eq__(self, rhs_):
        return self.itemID == rhs_.itemID

    @property
    def item(self):
        return self.__i

    @property
    def itemID(self):
        return id(self.__i)

    @property
    def itemAge(self):
        return self.__a

    def IncAge(self):
        self.__a += 1

class _LcMonGC:
    __slots__ = [ '__ai' ]

    __MAX_ITEM_AGE = 10

    def __init__(self):
        self.__ai = []

    def CleanUpItems(self, items_ : list):
        if self.__ai is None:
            return

        _allIDs = [ aa.itemID for aa in self.__ai ]

        lstFreshInsert = []
        for _tt in items_:
            gci = self._AddItem(_tt, _allIDs)
            if gci is not None:
                lstFreshInsert.append(gci)

        _lstDumped = []
        _lstOld = [ aa for aa in self.__ai if aa not in lstFreshInsert ]
        for aa in _lstOld:
            aa.IncAge()
            if aa.itemAge > _LcMonGC.__MAX_ITEM_AGE:
                _lstDumped.append(aa)
                self.__ai.remove(aa)

        for _dd in _lstDumped:
            _dd.item.CleanUp()
        _lstDumped.clear()

    def CleanUp(self):
        if self.__ai is not None:
            self.__ai.clear()
            self.__ai = None

    def _AddItem(self, item_  : _AbsSlotsObject, allIDs_ : list) -> _LcMonGCItem:
        res = None
        if id(item_) not in allIDs_:
            res = _LcMonGCItem(item_)
            self.__ai.append(res)
        return res

class _TlbSummary:
    __slots__ = [ '__c' , '__rl' , '__nt' , '__nrt' , '__nxt' , '__nrxt' ]

    def __init__(self):
        self.__c    = 0
        self.__nt   = 0
        self.__rl   = None
        self.__nrt  = 0
        self.__nxt  = 0
        self.__nrxt = 0

    def __eq__(self, rhs_):
        return not self.__ne__(rhs_)

    def __ne__(self, rhs_):
        return self.__nt   != rhs_.__nt   \
            or self.__nxt  != rhs_.__nxt  \
            or self.__nrt  != rhs_.__nrt  \
            or self.__nrxt != rhs_.__nrxt

    @property
    def unchangedCounter(self) -> int:
        return self.__c

    @property
    def numTasks(self) -> int:
        return self.__nt

    @numTasks.setter
    def numTasks(self, val_):
        self.__nt = val_

    @property
    def numFwTasks(self) -> int:
        return self.__nt - self.__nxt

    @property
    def numXTasks(self) -> int:
        return self.__nxt

    @numXTasks.setter
    def numXTasks(self, val_):
        self.__nxt = val_

    @property
    def numRunningTasks(self) -> int:
        return self.__nrt

    @numRunningTasks.setter
    def numRunningTasks(self, val_):
        self.__nrt = val_

    @property
    def numRunningFwTasks(self) -> int:
        return self.__nrt - self.__nrxt

    @property
    def numRunningXTasks(self) -> int:
        return self.__nrxt

    @numRunningXTasks.setter
    def numRunningXTasks(self, val_):
        self.__nrxt = val_

    @property
    def lifeSignAlarmReport(self):
        return self.__rl

    @lifeSignAlarmReport.setter
    def lifeSignAlarmReport(self, val_):
        self.__rl = val_

    def _Update(self, rhs_):
        _bChanged = self != rhs_
        if _bChanged:
            self.__c    = 0
            self.__nt   = rhs_.__nt
            self.__nxt  = rhs_.__nxt
            self.__nrt  = rhs_.__nrt
            self.__nrxt = rhs_.__nrxt
        else:
            self.__c += 1

class _LcMonitorImpl(_LcXStateDriver):
    @unique
    class _ELcMonStateFlag(_FwIntFlag):
        ebfIdle            = 0x0000
        ebfAlive           = (0x0001 << 0)
        ebfCoordSDMode     = (0x0001 << 1)
        ebfCoordSDRunning  = (0x0001 << 2)
        ebfCeasingGate     = (0x0001 << 3)
        ebfPreShutdownGate = (0x0001 << 4)
        ebfShutdownGate    = (0x0001 << 5)

        @property
        def compactName(self) -> str:
            return self.name[3:]

        @staticmethod
        def IsIdle(eLcMonBitMask_: _FwIntFlag):
            return eLcMonBitMask_ == _LcMonitorImpl._ELcMonStateFlag.ebfIdle

        @staticmethod
        def IsAlive(eLcMonBitMask_: _FwIntFlag):
            _eLcMonBitFlag = _LcMonitorImpl._ELcMonStateFlag.ebfAlive
            return _EBitMask.IsEnumBitFlagSet(eLcMonBitMask_, _eLcMonBitFlag)

        @staticmethod
        def IsCoordinatedShutdownMode(eLcMonBitMask_: _FwIntFlag):
            _eLcMonBitFlag = _LcMonitorImpl._ELcMonStateFlag.ebfCoordSDMode
            return _EBitMask.IsEnumBitFlagSet(eLcMonBitMask_, _eLcMonBitFlag)

        @staticmethod
        def IsCoordinatedShutdownRunning(eLcMonBitMask_: _FwIntFlag):
            _eLcMonBitFlag = _LcMonitorImpl._ELcMonStateFlag.ebfCoordSDRunning
            return _EBitMask.IsEnumBitFlagSet(eLcMonBitMask_, _eLcMonBitFlag)

        @staticmethod
        def IsCoordinatedPreShutdownGate(eLcMonBitMask_: _FwIntFlag):
            _eLcMonBitFlag = _LcMonitorImpl._ELcMonStateFlag.ebfPreShutdownGate
            return _EBitMask.IsEnumBitFlagSet(eLcMonBitMask_, _eLcMonBitFlag)

        @staticmethod
        def IsCoordinatedShutdownGate(eLcMonBitMask_: _FwIntFlag):
            _eLcMonBitFlag = _LcMonitorImpl._ELcMonStateFlag.ebfShutdownGate
            return _EBitMask.IsEnumBitFlagSet(eLcMonBitMask_, _eLcMonBitFlag)

        @staticmethod
        def AddLcMonBitFlag(eLcMonBitMask_: _FwIntFlag, eLcMonBitFlag_):
            return _EBitMask.AddEnumBitFlag(eLcMonBitMask_, eLcMonBitFlag_)

        @staticmethod
        def RemoveLcMonBitFlag(eLcMonBitMask_: _FwIntFlag, eLcMonBitFlag_):
            return _EBitMask.RemoveEnumBitFlag(eLcMonBitMask_, eLcMonBitFlag_)

        @staticmethod
        def IsLcMonBitFlagSet(eLcMonBitMask_: _FwIntFlag, eLcMonBitFlag_):
            return _EBitMask.IsEnumBitFlagSet(eLcMonBitMask_, eLcMonBitFlag_)

    __slots__ = [ '__gc' , '__ma' , '__md' , '__tt' , '__mt' , '__m' , '__cr' , '__bM' , '__ts' , '__xh' ]

    __theLcMon = None

    __PER_OPEN_GATE_WAIT_TIMESPAN_MS          = 200
    __PER_SINGLE_STEP_WAIT_TIMESPAN_MS        = 20
    __PER_SHUTDOWN_PHASE_WAIT_TIMESPAN_MS     = 10 * 1000
    __PER_SHUTDOWN_REQUEST_WAIT_TIMESPAN_MS   = 1 * 1000
    __PER_SHUTDOWN_PHASE_FWC_WAIT_TIMESPAN_MS = 1 * 1000

    def __init__(self, ppass_ : int, xhist_ : _LcXStateHistory):
        self.__m  = None
        self.__bM = None
        self.__cr = None
        self.__gc = None
        self.__ma = None
        self.__mt = None
        self.__md = None
        self.__ts = None
        self.__tt = None
        self.__xh = None
        super().__init__(ppass_)

        if _LcMonitorImpl.__theLcMon is not None:
            self.CleanUpByOwnerRequest(ppass_)
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00414)
            return
        if not (isinstance(xhist_, _LcXStateHistory) and xhist_.isValid):
            self.CleanUpByOwnerRequest(ppass_)
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00415)
            return

        _LcMonitorImpl.__theLcMon = self

        self.__m  = _LcMonitorImpl._ELcMonStateFlag.ebfIdle
        self.__bM = False
        self.__gc = _LcMonGC()
        self.__ma = _Mutex()
        self.__md = _Mutex()
        self.__tt = dict()
        self.__xh = xhist_

        _LcCeaseTLB._SetLcMonitorImpl(self)
        _LcDynamicTLB._SetLcMonitorImpl(self)
        _LcDummyDynamicTLB._CreateDummyTLB()

    @staticmethod
    def GetPerSingleStepWaitTimespanMS():
        return _LcMonitorImpl.__PER_SINGLE_STEP_WAIT_TIMESPAN_MS

    @staticmethod
    def GetPerOpenGateWaitTimespanMS():
        return _LcMonitorImpl.__PER_OPEN_GATE_WAIT_TIMESPAN_MS

    @staticmethod
    def GetPerShutdownRequestWaitTimespanMS():
        return _LcMonitorImpl.__PER_SHUTDOWN_REQUEST_WAIT_TIMESPAN_MS

    @staticmethod
    def GetPerShutdownPhaseWaitTimespanMS():
        return _LcMonitorImpl.__PER_SHUTDOWN_PHASE_WAIT_TIMESPAN_MS

    @staticmethod
    def GetPerShutdownPhaseFwcWaitTimespanMS():
        return _LcMonitorImpl.__PER_SHUTDOWN_PHASE_FWC_WAIT_TIMESPAN_MS

    @staticmethod
    def GetPerShutdownPhaseTotalWaitTimespanMS():
        return _LcMonitorImpl.GetPerShutdownPhaseWaitTimespanMS() + _LcMonitorImpl.GetPerShutdownPhaseFwcWaitTimespanMS()

    @property
    def isValid(self):
        return not self.__isInvalid

    @property
    def isDummyMonitor(self):
        return False

    @property
    def isLcMonitorIdle(self) -> bool:
        if self.__isInvalid: return False
        with self.__ma:
            return _LcMonitorImpl._ELcMonStateFlag.IsIdle(self.__m)

    @property
    def isLcMonitorAlive(self) -> bool:
        if self.__isInvalid: return False
        with self.__ma:
            return _LcMonitorImpl._ELcMonStateFlag.IsAlive(self.__m)

    @property
    def isLcShutdownEnabled(self) -> bool:
        if self.__isInvalid: return False
        with self.__ma:
            return _LcMonitorImpl._ELcMonStateFlag.IsCoordinatedShutdownMode(self.__m)

    @property
    def isCoordinatedShutdownRunning(self) -> bool:
        if self.__isInvalid: return False
        with self.__ma:
            return _LcMonitorImpl._ELcMonStateFlag.IsCoordinatedShutdownRunning(self.__m)

    @property
    def isCoordinatedPreShutdownGateOpened(self) -> bool:
        if self.__isInvalid: return False
        with self.__ma:
            return _LcMonitorImpl._ELcMonStateFlag.IsCoordinatedPreShutdownGate(self.__m)

    @property
    def isCoordinatedShutdownGateOpened(self) -> bool:
        if self.__isInvalid: return False
        with self.__ma:
            return _LcMonitorImpl._ELcMonStateFlag.IsCoordinatedShutdownGate(self.__m)

    @property
    def curShutdownRequest(self) -> _ELcSDRequest:
        if self.__isInvalid: return None
        with self.__ma:
            return self.__cr

    @property
    def _isCoordinatedShutdownManagedByMR(self) -> bool:
        if self.__isInvalid: return False
        with self.__ma:
            return self.__bM

    @property
    def _isCurrentThreadAttachedToFW(self):
        res    = False
        _curTLB = self._GetCurrentTLB()

        if (_curTLB is not None) and _curTLB.isValid:
            _ctlb = _curTLB.lcCeaseTLB
            if (_ctlb is not None) and _ctlb.isValid:
                _cst = _ctlb.ceaseState
                if not _cst.isNone:
                    if not _cst.isDeceased:
                        res = True

            else:
                _dtlb = _curTLB.lcDynamicTLB
                if (_dtlb is not None) and _dtlb.isValid:
                    _tstate = _dtlb.taskState
                    if not _tstate.isTerminated:
                        res = True

        return res

    @property
    def _runPhaseFrequencyMS(self):
        return self.__ts

    @property
    def _mainTLB(self) -> _LcTLB:
        if self.__isInvalid: return None
        with self.__ma:
            return self.__mt

    def _ActivateLcMonitorAlivenessByMR(self, runPhaseFreqMS_ : int):
        self.__ts = runPhaseFreqMS_
        self.__SetLcMonitorAliveness(True)

    def _SetCurrentShutdownRequest(self, eShutdownRequest_ : _ELcSDRequest):
        if self.__isInvalid:
            return
        with self.__ma:
            if (self.__cr is None) or self.__cr != eShutdownRequest_:
                self.__cr = eShutdownRequest_

    def _StopCoordinatedShutdown(self, bDueToUnexpectedError_ =False):
        if self.__isInvalid:
            return
        with self.__ma:
            _bm = _LcMonitorImpl._ELcMonStateFlag.ebfCoordSDRunning
            if _LcMonitorImpl._ELcMonStateFlag.IsLcMonBitFlagSet(self.__m, _bm):
                self.__m = _LcMonitorImpl._ELcMonStateFlag.RemoveLcMonBitFlag(self.__m, _bm)
                if not bDueToUnexpectedError_:
                    self.__xh._AddExecutionState(_ELcXState.eShutdownPassed, self)

    def _OpenCoordinatedGate(self, bfLcMonState_):
        if self.__isInvalid:
            return
        if not isinstance(bfLcMonState_, _LcMonitorImpl._ELcMonStateFlag):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00416)
            return
        if bfLcMonState_.value < _LcMonitorImpl._ELcMonStateFlag.ebfCeasingGate.value:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00417)
            return
        with self.__ma:
            if not _LcMonitorImpl._ELcMonStateFlag.IsLcMonBitFlagSet(self.__m, bfLcMonState_):
                self.__m = _LcMonitorImpl._ELcMonStateFlag.AddLcMonBitFlag(self.__m, bfLcMonState_)

    def _EnableCoordinatedShutdown(self, bManagedByMR_ : bool =None):
        if self.__isInvalid:
            return

        with self.__ma:
            if not self.isLcShutdownEnabled:
                _bAlive = self.isLcMonitorAlive
                if bManagedByMR_ is None:
                    bManagedByMR_ = _bAlive

                if not _bAlive:
                    if bManagedByMR_:
                        bManagedByMR_ = False

                self.__bM = bManagedByMR_
                self.__EnableCoordinatedShutdownMode()
                self.__EnableCoordinatedShutdownRunning()

                if _bAlive and not bManagedByMR_:
                    self.__SetLcMonitorAliveness(False)

                self.__xh._AddExecutionState(_ELcXState.eShutdownPhase, self)

                if _LcFailure.IsLcNotErrorFree():
                    _errMsg = _LcFailure._GetCurrentLcFRC()
                    if _errMsg is None:
                        _errMsg = _LcFailure._GetCurrentLcState()
                    else:
                        _errMsg = _errMsg.asCompactString
                    _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcMonitorImpl_TID_002).format(_errMsg)
                    _LogUrgentWarning(_errMsg)
                else:
                    _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcMonitorImpl_TID_001)
                    _LogKPI(_errMsg)

    def _GetAliveCounter(self):
        if self.__isInvalid:
            return None, None, None

        with self.__ma:
            if self.__mt is None:
                return None, None, None

            _curSDR     = self.__cr
            _bSDEnabled = self.isLcShutdownEnabled
            if _bSDEnabled and (self.__mt.lcCeaseTLB is not None):
                _aCtr = self.__mt.ceaseAliveCounter
            else:
                _aCtr = self.__mt.aliveCounter
            return _bSDEnabled, _curSDR, _aCtr

    def _Update(self, tlbSum_ : _TlbSummary =None):
        if self.__isInvalid:
            return

        if _LcMonitorImpl._ELcMonStateFlag.IsCoordinatedShutdownMode(self.__m):
            return

        _lsaReportStr = ''
        _curSum = None if tlbSum_ is None else _TlbSummary()
        with self.__md:
            _lstRemoved       = []
            _lstXtTaskCleanUp = []
            for _kk in self.__tt.keys():
                _tlb = self.__tt[_kk]
                if not (_tlb.isValid and not _tlb.isCleanedUp):
                    _lstRemoved.append(_kk)
                    continue

                if _tlb.lcStaticTLB.taskBadge.isFwMain:
                    continue

                _bXtTask = _tlb.lcStaticTLB.isXTaskTLB

                if _tlb.isTerminatedAfterStart:
                    if _bXtTask:
                        _ti = _tlb._taskInstance
                        if (_ti is not None) and _ti.isValid:
                            _lstXtTaskCleanUp.append(_ti)
                    continue

                _lsaReportStr = _tlb._UpdateTLB(False, lsaReportStr_=_lsaReportStr)

                if _curSum is None:
                    pass
                else:
                    _curSum.numTasks = 1 + _curSum.numTasks
                    if _bXtTask:
                        _curSum.numXTasks = 1 + _curSum.numXTasks

                    if _tlb.lcDynamicTLB.isRunning:
                        _curSum.numRunningTasks = 1 + _curSum.numRunningTasks
                        if _bXtTask:
                            _curSum.numRunningXTasks = 1 + _curSum.numRunningXTasks

            if (_lsaReportStr is not None) and (len(_lsaReportStr) < 1):
                _lsaReportStr = None

            if tlbSum_ is not None:
                if _curSum is not None:
                    tlbSum_._Update(_curSum)
                tlbSum_.lifeSignAlarmReport = _lsaReportStr

            for _kk in _lstRemoved:
                _tlb = self.__tt.pop(_kk)
                _tlb.CleanUp()

            if len(_lstXtTaskCleanUp) > 0:
                self.__gc.CleanUpItems(_lstXtTaskCleanUp)

    def _GetCeaseTLBLists(self, cstate_ : _ELcCeaseTLBState, bRSorted_ =True):
        if self.__isInvalid:
            return None, None

        _WAIT_WNG_TIMESPAN_MS    = 2 * _LcMonitorImpl.GetPerShutdownRequestWaitTimespanMS()
        _SINGLE_WAIT_TIMESPAN_MS = _LcMonitorImpl.GetPerSingleStepWaitTimespanMS()
        _TOTAL_WAIT_TIMESPAN_MS  = _LcMonitorImpl.GetPerShutdownPhaseTotalWaitTimespanMS()
        _MAX_WAIT_NUM            = _TOTAL_WAIT_TIMESPAN_MS // _SINGLE_WAIT_TIMESPAN_MS

        _bByMR = self._isCoordinatedShutdownManagedByMR

        _numWait    = 0
        _tidFW      = []
        _tidXT      = []
        _tidIgnore  = []
        _tunWaiting = []
        _tidWaiting = []

        _bContinue = True
        while _bContinue:
            _bContinue = self.isCoordinatedShutdownRunning
            if not _bContinue:
                break

            with self.__md:
                for _kk in self.__tt.keys():
                    _tlb = self.__tt[_kk]
                    if (not _tlb.isValid) or _tlb.isCleanedUp or _tlb.isTerminated:
                        continue

                    _ctlb   = _tlb.lcCeaseTLB
                    _tid    = _tlb.lcStaticTLB.taskBadge.dtaskUID
                    _tname = _tlb.lcStaticTLB.taskBadge.dtaskName
                    if (_tid in _tidFW) or (_tid in _tidXT) or (_tid in _tidIgnore):
                        continue
                    if (_ctlb is None) or (not _ctlb.isValid) or _ctlb.isDeceased or _ctlb.isEndingCease:
                        if _ctlb is not None:
                            _tidIgnore.append(_tid)
                            if _tname in _tunWaiting:
                                _tunWaiting.remove(_tname)
                                _tidWaiting.remove(_tid)
                        elif _tname not in _tunWaiting:
                            _tunWaiting.append(_tname)
                            _tidWaiting.append(_tid)
                        continue
                    if _tname in _tunWaiting:
                        _tunWaiting.remove(_tname)
                        _tidWaiting.remove(_tid)
                    if _ctlb.ceaseState != cstate_:
                        continue
                    if _tlb.lcStaticTLB.isXTaskTLB:
                        _tidXT.append(_tid)
                    else:
                        _tidFW.append(_tid)

            if not _bContinue:
                pass
            elif len(_tunWaiting) > 0:
                if _numWait >= _MAX_WAIT_NUM:
                    _wngMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcMonitorImpl_TID_003).format(len(_tunWaiting))
                    vlogif._LogUrgentWarning(_wngMsg)
                    for _tid in _tidWaiting:
                        if _tid in self.__tt:
                            _vv = self.__tt[_tid]
                            if _vv.lcCeaseTLB is not None:
                                _vv.lcCeaseTLB.UpdateCeaseState(True)
                    break

                if ((_numWait * _SINGLE_WAIT_TIMESPAN_MS) % _WAIT_WNG_TIMESPAN_MS) == 0:
                    _wngMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcMonitorImpl_TID_004).format(len(_tunWaiting))
                    if vlogif._IsReleaseModeEnabled():
                        _LogWarning(_wngMsg)

                if _bByMR:
                    self._mainTLB.lcCeaseTLB.IncrementCeaseAliveCounter()
                _TaskUtil.SleepMS(_SINGLE_WAIT_TIMESPAN_MS)

                _numWait += 1
                continue
            break

        _lstFwCTLBs = None
        _lstXuCTLBs = None
        if not _bContinue:
            pass
        else:
            with self.__md:
                _lstFwTLBs = []
                _lstXuTLBs = []

                for _tid in _tidXT:
                    _lstXuTLBs.append(self.__tt[_tid])
                if len(_lstXuTLBs) == 0:
                    _lstXuTLBs = None
                elif bRSorted_:
                    _lstXuTLBs = sorted(_lstXuTLBs, key=lambda t: t.stopWatch.startTimeTicksUS, reverse=True)

                for _tid in _tidFW:
                    _lstFwTLBs.append(self.__tt[_tid])
                if len(_lstFwTLBs) == 0:
                    _lstFwTLBs = None
                elif bRSorted_:
                    _lstFwTLBs = sorted(_lstFwTLBs, key=lambda t: t.stopWatch.startTimeTicksUS, reverse=True)

                if _lstFwTLBs is not None:
                    _lstFwCTLBs = [_tt.lcCeaseTLB for _tt in _lstFwTLBs]
                if _lstXuTLBs is not None:
                    _lstXuCTLBs = [_tt.lcCeaseTLB for _tt in _lstXuTLBs]

        return _lstFwCTLBs, _lstXuCTLBs

    def _CreateTLB(self, tskInst_, tskBadg_ : _TaskBadge, xcard_ : _TaskXCard, bUTask_ : bool) -> _LcTLB:
        if self.__isInvalid:
            return None

        if (tskInst_ is None) or not tskInst_.isValid:
            return None
        if (tskBadg_ is None) or (tskBadg_.dtaskUID is None):
            return None
        if (xcard_ is None) or not xcard_.isValid:
            return None

        with self.__md:
            _tid = tskBadg_.dtaskUID
            if _tid in self.__tt:
                res = self.__tt[_tid]
            else:
                res = _LcTLB(tskInst_, tskBadg_, xcard_, bUTask_)
                if not res.isValid:
                    res.CleanUp()
                    res = None
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00418)
                else:
                    self.__tt[_tid] = res
                    if res.lcStaticTLB.taskBadge.isFwMain:
                        self.__mt = res
        return res

    def _CreateCeaseTLB(self, tskID_ : int, md_: _Mutex, bEnding_: bool) -> _LcCeaseTLB:
        if self.__isInvalid:
            return None

        if not isinstance(tskID_, int):
            return None
        if not isinstance(md_, _Mutex):
            return None

        with self.__md:
            if tskID_ not in self.__tt:
                res = None
            else:
                _tlb = self.__tt[tskID_]
                if not _tlb.isValid:
                    res = None
                else:
                    res = _LcCeaseTLB(_tlb.lcStaticTLB, md_, bEnding_)
                    if not res.isValid:
                        res.CleanUp()
                        res = None
                        vlogif._LogOEC(True, _EFwErrorCode.VFE_00419)
                    else:
                        _tlb._SetCeaseTLB(res)
            return res

    def _GetCurrentTLB(self) -> _LcTLB:
        if self.__isInvalid:
            return None

        res       = None
        _cthrdUID = _TaskUtil.GetPyThreadUID(_TaskUtil.GetCurPyThread())

        with self.__ma:
            for _vv in self.__tt.values():
                _stlb = _vv.lcStaticTLB

                if (_stlb is None) or not _stlb.isValid:
                    continue
                if _stlb.taskBadge.threadUID == _cthrdUID:
                    res = _vv
                    break
                continue
        return res

    def _ToString(self):
        if self.__isInvalid:
            return None
        return '[LcMon] : alive={}'.format(str(self.isLcMonitorAlive))

    def _CleanUpByOwnerRequest(self):
        if self.__md is None:
            return

        if _LcMonitorImpl.__theLcMon is not None:
            if id(_LcMonitorImpl.__theLcMon) == id(self):
                _LcMonitorImpl.__theLcMon = None
                _LcCeaseTLB._SetLcMonitorImpl(None)
                _LcDynamicTLB._SetLcMonitorImpl(None)
                _LcDummyDynamicTLB._CleanUpDummyTLB()

        self.__gc.CleanUp()
        self.__gc = None

        for _vv in self.__tt.values():
            if _vv.isValid:
                _vv.CleanUp()
        self.__tt.clear()

        self.__ma.CleanUp()
        self.__md.CleanUp()

        self.__m  = None
        self.__bM = None
        self.__cr = None
        self.__ma = None
        self.__mt = None
        self.__md = None
        self.__ts = None
        self.__tt = None
        self.__xh = None

    @property
    def __isInvalid(self):
        return self.__md is None

    def __SetLcMonitorAliveness(self, bAlive_ : bool):
        if self.__isInvalid:
            return
        with self.__ma:
            _bm = _LcMonitorImpl._ELcMonStateFlag.ebfAlive
            _bSet = _LcMonitorImpl._ELcMonStateFlag.IsLcMonBitFlagSet(self.__m, _bm)
            if _bSet != bAlive_:
                if not bAlive_:
                    self.__m = _LcMonitorImpl._ELcMonStateFlag.RemoveLcMonBitFlag(self.__m, _bm)
                else:
                    self.__m = _LcMonitorImpl._ELcMonStateFlag.AddLcMonBitFlag(self.__m, _bm)

    def __EnableCoordinatedShutdownMode(self):
        if self.__isInvalid:
            return
        with self.__ma:
            _bm = _LcMonitorImpl._ELcMonStateFlag.ebfCoordSDMode
            if not _LcMonitorImpl._ELcMonStateFlag.IsLcMonBitFlagSet(self.__m, _bm):
                self.__m = _LcMonitorImpl._ELcMonStateFlag.AddLcMonBitFlag(self.__m, _bm)

    def __EnableCoordinatedShutdownRunning(self):
        if self.__isInvalid:
            return
        with self.__ma:
            _bm = _LcMonitorImpl._ELcMonStateFlag.ebfCoordSDRunning
            if not _LcMonitorImpl._ELcMonStateFlag.IsLcMonBitFlagSet(self.__m, _bm):
                self.__m = _LcMonitorImpl._ELcMonStateFlag.AddLcMonBitFlag(self.__m, _bm)
