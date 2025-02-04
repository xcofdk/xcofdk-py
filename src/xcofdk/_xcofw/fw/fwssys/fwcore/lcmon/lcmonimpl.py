# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : lcmonimpl.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum import unique

from xcofdk._xcofw.fw.fwssys.fwcore.logging.logif import _LogKPI
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logif import _LogUrgentWarning

from xcofdk._xcofw.fw.fwssys.fwcore.logging             import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.sync.mutex      import _Mutex
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.aexecutable import _AbstractExecutable
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.execprofile import _ExecutionProfile
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskbadge   import _TaskBadge
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil    import _TaskUtil
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcproxydefines   import _ELcShutdownRequest
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcexecstate      import _ELcExecutionState
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcexecstate      import _LcExecutionStateHistory
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcexecstate      import _LcFailure
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcmgrtif         import _LcManagerTrustedIF
from xcofdk._xcofw.fw.fwssys.fwcore.lcmon.lcmontlb      import _LcTLB
from xcofdk._xcofw.fw.fwssys.fwcore.lcmon.lcmontlb      import _LcDynamicTLB
from xcofdk._xcofw.fw.fwssys.fwcore.lcmon.lcmontlb      import _LcCeaseTLB
from xcofdk._xcofw.fw.fwssys.fwcore.lcmon.lcmontlb      import _LcDummyDynamicTLB
from xcofdk._xcofw.fw.fwssys.fwcore.lcmon.lcmontlb      import _ELcCeaseTLBState
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject       import _AbstractSlotsObject
from xcofdk._xcofw.fw.fwssys.fwcore.types.ebitmask      import _EBitMask
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes   import _FwIntFlag

from xcofdk._xcofw.fw.fwssys.fwerrh.fwerrorcodes import _EFwErrorCode

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine

class _LcMonGCItem:
    __slots__ = [ '__age' , '__item' ]

    def __init__(self, item_  : _AbstractSlotsObject):
        self.__age  = 0
        self.__item = item_

    def __eq__(self, rhs_):
        return self.itemID == rhs_.itemID

    @property
    def item(self):
        return self.__item

    @property
    def itemID(self):
        return id(self.__item)

    @property
    def itemAge(self):
        return self.__age

    def IncAge(self):
        self.__age += 1

class _LcMonGC:
    __slots__ = [ '__gcItems' ]
    __MAX_ITEM_AGE = 10

    def __init__(self):
        self.__gcItems = []

    def CleanUpItems(self, items_ : list):
        if self.__gcItems is None:
            return

        _allIDs = [ aa.itemID for aa in self.__gcItems ]

        lstFreshInsert = []
        for _tt in items_:
            gci = self._AddItem(_tt, _allIDs)
            if gci is not None:
                lstFreshInsert.append(gci)

        _lstDumped = []
        _lstOld = [ aa for aa in self.__gcItems if aa not in lstFreshInsert ]
        for aa in _lstOld:
            aa.IncAge()
            if aa.itemAge > _LcMonGC.__MAX_ITEM_AGE:
                _lstDumped.append(aa)
                self.__gcItems.remove(aa)

        for _dd in _lstDumped:
            _dd.item.CleanUp()
        _lstDumped.clear()

    def CleanUp(self):
        if self.__gcItems is not None:
            self.__gcItems.clear()
            self.__gcItems = None

    def _AddItem(self, item_  : _AbstractSlotsObject, allIDs_ : list) -> _LcMonGCItem:
        res = None
        if id(item_) not in allIDs_:
            res = _LcMonGCItem(item_)
            self.__gcItems.append(res)
        return res

class _TlbSummary:
    __slots__ = [ '__ctr' , '__numTsk' , '__numXuTsk' , '__numRunningTsk' , '__numRunningXuTsk' , '__lsaReport' ]

    def __init__(self):
        self.__ctr             = 0
        self.__numTsk          = 0
        self.__numXuTsk        = 0
        self.__numRunningTsk   = 0
        self.__numRunningXuTsk = 0

        self.__lsaReport = None

    def __eq__(self, rhs_):
        return not self.__ne__(rhs_)

    def __ne__(self, rhs_):
        return self.__numTsk          != rhs_.__numTsk        \
            or self.__numXuTsk        != rhs_.__numXuTsk      \
            or self.__numRunningTsk   != rhs_.__numRunningTsk \
            or self.__numRunningXuTsk != rhs_.__numRunningXuTsk

    @property
    def unchangedCounter(self) -> int:
        return self.__ctr

    @property
    def numTasks(self) -> int:
        return self.__numTsk

    @numTasks.setter
    def numTasks(self, val_):
        self.__numTsk = val_

    @property
    def numFwTasks(self) -> int:
        return self.__numTsk - self.__numXuTsk

    @property
    def numXTasks(self) -> int:
        return self.__numXuTsk

    @numXTasks.setter
    def numXTasks(self, val_):
        self.__numXuTsk = val_

    @property
    def numRunningTasks(self) -> int:
        return self.__numRunningTsk

    @numRunningTasks.setter
    def numRunningTasks(self, val_):
        self.__numRunningTsk = val_

    @property
    def numRunningFwTasks(self) -> int:
        return self.__numRunningTsk - self.__numRunningXuTsk

    @property
    def numRunningXTasks(self) -> int:
        return self.__numRunningXuTsk

    @numRunningXTasks.setter
    def numRunningXTasks(self, val_):
        self.__numRunningXuTsk = val_

    @property
    def lifeSignAlarmReport(self):
        return self.__lsaReport

    @lifeSignAlarmReport.setter
    def lifeSignAlarmReport(self, val_):
        self.__lsaReport = val_

    def _Update(self, rhs_):
        _bChanged = self != rhs_
        if _bChanged:
            self.__ctr            = 0
            self.__numTsk          = rhs_.__numTsk
            self.__numXuTsk        = rhs_.__numXuTsk
            self.__numRunningTsk   = rhs_.__numRunningTsk
            self.__numRunningXuTsk = rhs_.__numRunningXuTsk
        else:
            self.__ctr += 1

class _LcMonitorImpl(_LcManagerTrustedIF):

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
        def IsCoordinatedCeasingGate(eLcMonBitMask_: _FwIntFlag):
            _eLcMonBitFlag = _LcMonitorImpl._ELcMonStateFlag.ebfCeasingGate
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

    __slots__ = [ '__mtxData'  , '__mtxApi'    , '__tblTLB'     , '__mainTLB'
                , '__eBitMask' , '__curSDR'    , '__bCSDbyMRbl' , '__cycleTS'
                , '__gc'       , '__eExecHist' ]

    __theLcMon = None

    __PER_OPEN_GATE_WAIT_TIMESPAN_MS          = 200
    __PER_SINGLE_STEP_WAIT_TIMESPAN_MS        = 20
    __PER_SHUTDOWN_PHASE_WAIT_TIMESPAN_MS     = 10 * 1000
    __PER_SHUTDOWN_REQUEST_WAIT_TIMESPAN_MS   = 1 * 1000
    __PER_SHUTDOWN_PHASE_FWC_WAIT_TIMESPAN_MS = 1 * 1000

    def __init__(self, ppass_ : int, eLcExceHist_ : _LcExecutionStateHistory):
        self.__gc         = None
        self.__curSDR     = None
        self.__mtxApi     = None
        self.__tblTLB     = None
        self.__mainTLB    = None
        self.__mtxData    = None
        self.__cycleTS    = None
        self.__eBitMask   = None
        self.__eExecHist  = None
        self.__bCSDbyMRbl = None
        super().__init__(ppass_)

        if _LcMonitorImpl.__theLcMon is not None:
            self.CleanUpByOwnerRequest(ppass_)
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00414)
            return
        if not (isinstance(eLcExceHist_, _LcExecutionStateHistory) and eLcExceHist_.isValid):
            self.CleanUpByOwnerRequest(ppass_)
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00415)
            return

        _LcMonitorImpl.__theLcMon = self

        self.__gc       = _LcMonGC()
        self.__mtxApi   = _Mutex()
        self.__mtxData  = _Mutex()

        self.__tblTLB     = dict()
        self.__eBitMask   = _LcMonitorImpl._ELcMonStateFlag.ebfIdle
        self.__eExecHist  = eLcExceHist_
        self.__bCSDbyMRbl = False

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
        with self.__mtxApi:
            return _LcMonitorImpl._ELcMonStateFlag.IsIdle(self.__eBitMask)

    @property
    def isLcMonitorAlive(self) -> bool:
        if self.__isInvalid: return False
        with self.__mtxApi:
            return _LcMonitorImpl._ELcMonStateFlag.IsAlive(self.__eBitMask)

    @property
    def isLcShutdownEnabled(self) -> bool:
        if self.__isInvalid: return False
        with self.__mtxApi:
            return _LcMonitorImpl._ELcMonStateFlag.IsCoordinatedShutdownMode(self.__eBitMask)

    @property
    def isCoordinatedShutdownRunning(self) -> bool:
        if self.__isInvalid: return False
        with self.__mtxApi:
            return _LcMonitorImpl._ELcMonStateFlag.IsCoordinatedShutdownRunning(self.__eBitMask)

    @property
    def isCoordinatedCeasingGateOpened(self) -> bool:
        if self.__isInvalid: return False
        with self.__mtxApi:
            return _LcMonitorImpl._ELcMonStateFlag.IsCoordinatedCeasingGate(self.__eBitMask)

    @property
    def isCoordinatedPreShutdownGateOpened(self) -> bool:
        if self.__isInvalid: return False
        with self.__mtxApi:
            return _LcMonitorImpl._ELcMonStateFlag.IsCoordinatedPreShutdownGate(self.__eBitMask)

    @property
    def isCoordinatedShutdownGateOpened(self) -> bool:
        if self.__isInvalid: return False
        with self.__mtxApi:
            return _LcMonitorImpl._ELcMonStateFlag.IsCoordinatedShutdownGate(self.__eBitMask)

    @property
    def eCurrentShutdownRequest(self) -> _ELcShutdownRequest:
        if self.__isInvalid: return None
        with self.__mtxApi:
            return self.__curSDR

    @property
    def _isCoordinatedShutdownManagedByMR(self) -> bool:
        if self.__isInvalid: return False
        with self.__mtxApi:
            return self.__bCSDbyMRbl

    @property
    def _isCurrentThreadAttachedToFW(self):
        res    = False
        _curTLB = self._GetCurrentTLB()

        if (_curTLB is not None) and _curTLB.isValid:
            _ctlb = _curTLB.lcCeaseTLB
            if (_ctlb is not None) and _ctlb.isValid:
                eCState = _ctlb.eCeaseState
                if not eCState.isNone:
                    if not eCState.isDeceased:
                        res = True

            else:
                _dtlb = _curTLB.lcDynamicTLB
                if (_dtlb is not None) and _dtlb.isValid:
                    _tstate = _dtlb.eTaskState
                    if not (_tstate.isDone or _tstate.isFailed):
                        res = True

        return res

    @property
    def _runPhaseFrequencyMS(self):
        return self.__cycleTS

    @property
    def _mainTLB(self) -> _LcTLB:
        if self.__isInvalid: return None
        with self.__mtxApi:
            return self.__mainTLB

    def _ActivateLcMonitorAlivenessByMR(self, runPhaseFreqMS_ : int):
        self.__cycleTS = runPhaseFreqMS_
        self.__SetLcMonitorAliveness(True)

    def _SetCurrentShutdownRequest(self, eShutdownRequest_ : _ELcShutdownRequest):
        if self.__isInvalid:
            return
        with self.__mtxApi:
            if (self.__curSDR is None) or self.__curSDR != eShutdownRequest_:
                self.__curSDR = eShutdownRequest_

    def _StopCoordinatedShutdown(self, bDueToUnexpectedError_ =False):
        if self.__isInvalid:
            return
        with self.__mtxApi:
            _bm = _LcMonitorImpl._ELcMonStateFlag.ebfCoordSDRunning
            if _LcMonitorImpl._ELcMonStateFlag.IsLcMonBitFlagSet(self.__eBitMask, _bm):
                self.__eBitMask = _LcMonitorImpl._ELcMonStateFlag.RemoveLcMonBitFlag(self.__eBitMask, _bm)

                if not bDueToUnexpectedError_:
                    self.__eExecHist._AddExecutionState(_ELcExecutionState.eShutdownPassed, self)

    def _OpenCoordinatedGate(self, bfLcMonState_):
        if self.__isInvalid:
            return
        if not isinstance(bfLcMonState_, _LcMonitorImpl._ELcMonStateFlag):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00416)
            return
        if bfLcMonState_.value < _LcMonitorImpl._ELcMonStateFlag.ebfCeasingGate:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00417)
            return
        with self.__mtxApi:
            if not _LcMonitorImpl._ELcMonStateFlag.IsLcMonBitFlagSet(self.__eBitMask, bfLcMonState_):
                self.__eBitMask = _LcMonitorImpl._ELcMonStateFlag.AddLcMonBitFlag(self.__eBitMask, bfLcMonState_)

    def _EnableCoordinatedShutdown(self, bManagedByMR_ : bool =None):

        if self.__isInvalid:
            return

        with self.__mtxApi:
            if self.isLcShutdownEnabled:
                pass 
            else:
                _bAlive = self.isLcMonitorAlive
                if bManagedByMR_ is None:
                    bManagedByMR_ = _bAlive

                if not _bAlive:
                    if bManagedByMR_:
                        bManagedByMR_ = False

                self.__bCSDbyMRbl = bManagedByMR_
                self.__EnableCoordinatedShutdownMode()
                self.__EnableCoordinatedShutdownRunning()

                if _bAlive and not bManagedByMR_:
                    self.__SetLcMonitorAliveness(False)

                self.__eExecHist._AddExecutionState(_ELcExecutionState.eShutdownPhase, self)

                if _LcFailure.IsLcNotErrorFree():
                    _errMsg = _LcFailure._GetCurrentLcFRC()
                    if _errMsg is None:
                        _errMsg = _LcFailure._GetCurrentLcState()
                    else:
                        _errMsg = _errMsg.ToString(bVerbose_=False)
                    _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcMonitorImpl_TextID_002).format(_errMsg)
                    _LogUrgentWarning(_errMsg)
                else:
                    _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcMonitorImpl_TextID_001)
                    _LogKPI(_errMsg)

    def _GetAliveCounter(self):
        if self.__isInvalid:
            return None, None, None

        with self.__mtxApi:
            if self.__mainTLB is None:
                return None, None, None

            _curSDR     = self.__curSDR
            _bSDEnabled = self.isLcShutdownEnabled
            if _bSDEnabled and (self.__mainTLB.lcCeaseTLB is not None):
                _aCtr = self.__mainTLB.ceaseAliveCounter
            else:
                _aCtr = self.__mainTLB.aliveCounter
            return _bSDEnabled, _curSDR, _aCtr

    def _Update(self, tlbSum_ : _TlbSummary =None):
        if self.__isInvalid:
            return

        if _LcMonitorImpl._ELcMonStateFlag.IsCoordinatedShutdownMode(self.__eBitMask):
            return

        _lsaReportStr = ''
        _curSum = None if tlbSum_ is None else _TlbSummary()
        with self.__mtxData:

            _lstRemoved       = []
            _lstXuTaskCleanUp = []
            for _kk in self.__tblTLB.keys():
                _tlb = self.__tblTLB[_kk]
                if not (_tlb.isValid and not _tlb.isCleanedUp):
                    _lstRemoved.append(_kk)
                    continue

                tlbStat = _tlb.lcStaticTLB
                if tlbStat.taskBadge.isFwMain:
                    continue

                _bXuTask = _tlb.lcStaticTLB.isXTaskTask

                if _tlb.isTerminatedAfterStart:
                    if _bXuTask:
                        _ti = _tlb._taskInstance
                        if (_ti is not None) and _ti.isValid:
                            _lstXuTaskCleanUp.append(_ti)
                    continue

                _lsaReportStr = _tlb._UpdateTLB(False, lsaReportStr_=_lsaReportStr)

                if _curSum is None:
                    pass
                else:
                    _curSum.numTasks = 1 + _curSum.numTasks
                    if _bXuTask:
                        _curSum.numXTasks = 1 + _curSum.numXTasks

                    if _tlb.lcDynamicTLB.isRunning:
                        _curSum.numRunningTasks = 1 + _curSum.numRunningTasks
                        if _bXuTask:
                            _curSum.numRunningXTasks = 1 + _curSum.numRunningXTasks

            if (_lsaReportStr is not None) and (len(_lsaReportStr) < 1):
                _lsaReportStr = None

            if tlbSum_ is not None:
                if _curSum is not None:
                    tlbSum_._Update(_curSum)
                tlbSum_.lifeSignAlarmReport = _lsaReportStr

            for _kk in _lstRemoved:
                _tlb = self.__tblTLB.pop(_kk)
                _tlb.CleanUp()

            if len(_lstXuTaskCleanUp) > 0:
                self.__gc.CleanUpItems(_lstXuTaskCleanUp)

    def _GetCeaseTLBLists(self, eCeaseState_ : _ELcCeaseTLBState, bReverseStartTimeSorted_ =True):
        if self.__isInvalid:
            return None, None

        _SINGLE_WAIT_TIMESPAN_MS = _LcMonitorImpl.GetPerSingleStepWaitTimespanMS()
        _TOTAL_WAIT_TIMESPAN_MS  = _LcMonitorImpl.GetPerShutdownPhaseTotalWaitTimespanMS()
        _MAX_WAIT_NUM            = _TOTAL_WAIT_TIMESPAN_MS // _SINGLE_WAIT_TIMESPAN_MS

        _bByMR = self._isCoordinatedShutdownManagedByMR

        _numWait    = 0
        _tidFW      = []
        _tidXU      = []
        _tidIgnore  = []
        _tunWaiting = []
        _tidWaiting = []

        _bContinue = True
        while _bContinue:
            _bContinue = self.isCoordinatedShutdownRunning
            if not _bContinue:
                break

            with self.__mtxData:
                for _kk in self.__tblTLB.keys():
                    _tlb = self.__tblTLB[_kk]
                    if (not _tlb.isValid) or _tlb.isCleanedUp or _tlb.isTerminated:
                        continue

                    _ctlb   = _tlb.lcCeaseTLB
                    _tid    = _tlb.lcStaticTLB.taskBadge.taskID
                    _tuname = _tlb.lcStaticTLB.taskBadge.taskUniqueName
                    if (_tid in _tidFW) or (_tid in _tidXU) or (_tid in _tidIgnore):
                        continue

                    if (_ctlb is None) or (not _ctlb.isValid) or _ctlb.isDeceased or _ctlb.isEndingCease:
                        if _ctlb is not None:
                            _tidIgnore.append(_tid)
                            if _tuname in _tunWaiting:
                                _tunWaiting.remove(_tuname)
                                _tidWaiting.remove(_tid)
                        elif _tuname not in _tunWaiting:
                            _tunWaiting.append(_tuname)
                            _tidWaiting.append(_tid)
                        continue

                    if _tuname in _tunWaiting:
                        _tunWaiting.remove(_tuname)
                        _tidWaiting.remove(_tid)

                    if _ctlb.eCeaseState != eCeaseState_:
                        continue

                    if _tlb.lcStaticTLB.isXTaskTask:
                        _tidXU.append(_tid)
                    else:
                        _tidFW.append(_tid)

            if not _bContinue:
                pass
            elif len(_tunWaiting) > 0:
                if _numWait >= _MAX_WAIT_NUM:
                    _wngMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcMonitorImpl_TextID_003).format(len(_tunWaiting))
                    if not vlogif._IsReleaseModeEnabled():
                        pass 
                    else:
                        vlogif._XLogWarning(_wngMsg)
                    for _tid in _tidWaiting:
                        if _tid in self.__tblTLB:
                            _vv = self.__tblTLB[_tid]
                            if _vv.lcCeaseTLB is not None:
                                _vv.lcCeaseTLB.UpdateCeaseState(True)
                    break

                if ((_numWait * _SINGLE_WAIT_TIMESPAN_MS) % 1000) == 0:
                    _wngMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcMonitorImpl_TextID_004).format(len(_tunWaiting))
                    if not vlogif._IsReleaseModeEnabled():
                        pass 
                    else:
                        vlogif._XLogWarning(_wngMsg)

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
            with self.__mtxData:
                _lstFwTLBs = []
                _lstXuTLBs = []

                for _tid in _tidXU:
                    _lstXuTLBs.append(self.__tblTLB[_tid])
                if len(_lstXuTLBs) == 0:
                    _lstXuTLBs = None
                elif bReverseStartTimeSorted_:
                    _lstXuTLBs = sorted(_lstXuTLBs, key=lambda t: t.stopWatch.startTimeTicksUS, reverse=True)

                for _tid in _tidFW:
                    _lstFwTLBs.append(self.__tblTLB[_tid])
                if len(_lstFwTLBs) == 0:
                    _lstFwTLBs = None
                elif bReverseStartTimeSorted_:
                    _lstFwTLBs = sorted(_lstFwTLBs, key=lambda t: t.stopWatch.startTimeTicksUS, reverse=True)

                if _lstFwTLBs is not None:
                    _lstFwCTLBs = [_tt.lcCeaseTLB for _tt in _lstFwTLBs]
                if _lstXuTLBs is not None:
                    _lstXuCTLBs = [_tt.lcCeaseTLB for _tt in _lstXuTLBs]

        return _lstFwCTLBs, _lstXuCTLBs

    def _CreateTLB(self, tskInst_, tskBadg_ : _TaskBadge, execPrf_ : _ExecutionProfile, linkedXtbl_ : _AbstractExecutable) -> _LcTLB:
        if self.__isInvalid:
            return None

        if (tskInst_ is None) or not tskInst_.isValid:
            return None
        if (tskBadg_ is None) or (tskBadg_.taskID is None):
            return None
        if (execPrf_ is None) or not execPrf_.isValid:
            return None
        if linkedXtbl_ is None:
            return None

        with self.__mtxData:
            _tid = tskBadg_.taskID
            if _tid in self.__tblTLB:
                res = self.__tblTLB[_tid]
            else:
                res = _LcTLB(tskInst_, tskBadg_, execPrf_, linkedXtbl_)
                if not res.isValid:
                    res.CleanUp()
                    res = None
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00418)
                else:
                    self.__tblTLB[_tid] = res
                    if res.lcStaticTLB.taskBadge.isFwMain:
                        self.__mainTLB = res
        return res

    def _CreateCeaseTLB(self, tskID_ : int, mtxData_: _Mutex, bEnding_: bool) -> _LcCeaseTLB:
        if self.__isInvalid:
            return None

        if not isinstance(tskID_, int):
            return None
        if not isinstance(mtxData_, _Mutex):
            return None

        with self.__mtxData:
            if tskID_ not in self.__tblTLB:
                res = None
            else:
                _tlb = self.__tblTLB[tskID_]
                if not _tlb.isValid:
                    res = None
                else:
                    res = _LcCeaseTLB(_tlb.lcStaticTLB, mtxData_, bEnding_)
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
        _cthrdUID = _TaskUtil.GetPyThreadUniqueID(_TaskUtil.GetCurPyThread())

        with self.__mtxApi:
            for _vv in self.__tblTLB.values():
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
        if self.__mtxData is None:
            return

        if _LcMonitorImpl.__theLcMon is not None:
            if id(_LcMonitorImpl.__theLcMon) == id(self):
                _LcMonitorImpl.__theLcMon = None
                _LcCeaseTLB._SetLcMonitorImpl(None)
                _LcDynamicTLB._SetLcMonitorImpl(None)
                _LcDummyDynamicTLB._CleanUpDummyTLB()

        self.__gc.CleanUp()
        self.__gc = None

        for _vv in self.__tblTLB.values():
            if _vv.isValid:
                _vv.CleanUp()
        self.__tblTLB.clear()

        self.__mtxApi.CleanUp()
        self.__mtxData.CleanUp()

        self.__curSDR     = None
        self.__mtxApi     = None
        self.__tblTLB     = None
        self.__mainTLB    = None
        self.__mtxData    = None
        self.__cycleTS    = None
        self.__eBitMask   = None
        self.__eExecHist  = None
        self.__bCSDbyMRbl = None

    @property
    def __isInvalid(self):
        return self.__mtxData is None

    def __SetLcMonitorAliveness(self, bAlive_ : bool):
        if self.__isInvalid:
            return
        with self.__mtxApi:
            _bm = _LcMonitorImpl._ELcMonStateFlag.ebfAlive
            _bSet = _LcMonitorImpl._ELcMonStateFlag.IsLcMonBitFlagSet(self.__eBitMask, _bm)
            if _bSet != bAlive_:
                if not bAlive_:
                    self.__eBitMask = _LcMonitorImpl._ELcMonStateFlag.RemoveLcMonBitFlag(self.__eBitMask, _bm)
                else:
                    self.__eBitMask = _LcMonitorImpl._ELcMonStateFlag.AddLcMonBitFlag(self.__eBitMask, _bm)

    def __EnableCoordinatedShutdownMode(self):
        if self.__isInvalid:
            return
        with self.__mtxApi:
            _bm = _LcMonitorImpl._ELcMonStateFlag.ebfCoordSDMode
            if not _LcMonitorImpl._ELcMonStateFlag.IsLcMonBitFlagSet(self.__eBitMask, _bm):
                self.__eBitMask = _LcMonitorImpl._ELcMonStateFlag.AddLcMonBitFlag(self.__eBitMask, _bm)

    def __EnableCoordinatedShutdownRunning(self):
        if self.__isInvalid:
            return
        with self.__mtxApi:
            _bm = _LcMonitorImpl._ELcMonStateFlag.ebfCoordSDRunning
            if not _LcMonitorImpl._ELcMonStateFlag.IsLcMonBitFlagSet(self.__eBitMask, _bm):
                self.__eBitMask = _LcMonitorImpl._ELcMonStateFlag.AddLcMonBitFlag(self.__eBitMask, _bm)
