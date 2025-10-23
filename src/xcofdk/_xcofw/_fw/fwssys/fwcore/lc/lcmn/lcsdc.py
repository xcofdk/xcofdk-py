# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : lcsdc.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from _fw.fwssys.fwcore.logging            import vlogif
from _fw.fwssys.fwcore.base.gtimeout      import _Timeout
from _fw.fwssys.fwcore.ipc.tsk.taskutil   import _TaskUtil
from _fw.fwssys.fwcore.lc.lcmn.lcmontlb   import _ELcCeaseGateFlag
from _fw.fwssys.fwcore.lc.lcmn.lcmontlb   import _ELcCeaseTLBState
from _fw.fwssys.fwcore.lc.lcmn.lcmonimpl  import _LcMonitorImpl
from _fw.fwssys.fwerrh.fwerrorcodes       import _EFwErrorCode

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _LcSDCoordinator:
    __slots__ = [ '__m' , '__bM' , '__act' , '__axt' ]

    def __init__(self, lcMon_ : _LcMonitorImpl):
        self.__m   = lcMon_
        self.__bM  = lcMon_._isCoordinatedShutdownManagedByMR
        self.__act = None
        self.__axt = None

    def _ExecuteCoordinatedCeasingGate(self):
        _lcm        = self.__m
        _lstFwCTLBs = None
        _lstXuCTLBs = None

        _lstFwCTLBs, _lstXuCTLBs = _lcm._GetCeaseTLBLists(_ELcCeaseTLBState.eRFTPrepareCeasing, bRSorted_=True)
        self.__act = _lstFwCTLBs
        self.__axt = _lstXuCTLBs

        if _lcm.isCoordinatedShutdownRunning:
            self.__CoordinateCeasingGateXT(_ELcCeaseGateFlag.ebfCeasingGate)
        if _lcm.isCoordinatedShutdownRunning:
            self.__CoordinateCeasingGateFW(_ELcCeaseGateFlag.ebfCeasingGate)
        _lcm._OpenCoordinatedGate(_LcMonitorImpl._ELcMonStateFlag.ebfCeasingGate)

    def _ExecuteCoordinatedPreShutdownGate(self):
        _lcm = self.__m

        _curSDR = _lcm.curShutdownRequest
        if (_curSDR is not None) and _curSDR.isShutdown:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00421)
            _lcm._StopCoordinatedShutdown(bDueToUnexpectedError_=True)
            return

        _SINGLE_WAIT_TIMESPAN_MS = _LcMonitorImpl.GetPerSingleStepWaitTimespanMS()
        _MAX_WAIT_NUM            = _LcMonitorImpl.GetPerShutdownRequestWaitTimespanMS() // _SINGLE_WAIT_TIMESPAN_MS

        _numWait = 0
        _curSDR = None

        while True:
            _numWait += 1

            if not _lcm.isCoordinatedShutdownRunning:
                break

            _curSDR = _lcm.curShutdownRequest
            if (_curSDR is not None) and _curSDR.isPreShutdown:
                break

            if self.__bM:
                _lcm._mainTLB.lcCeaseTLB.IncrementCeaseAliveCounter()
            _TaskUtil.SleepMS(_SINGLE_WAIT_TIMESPAN_MS)

            if _numWait >= _MAX_WAIT_NUM:
                break
            continue

        if (_curSDR is None) or not _curSDR.isPreShutdown:
            if vlogif._IsReleaseModeEnabled():
                vlogif._XLogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcSDC_TID_001))
        if _lcm.isCoordinatedShutdownRunning:
            self.__CoordinateCeasingGateXT(_ELcCeaseGateFlag.ebfPreShutdownGate)
        if _lcm.isCoordinatedShutdownRunning:
            self.__CoordinateCeasingGateFW(_ELcCeaseGateFlag.ebfPreShutdownGate)
        _lcm._OpenCoordinatedGate(_LcMonitorImpl._ELcMonStateFlag.ebfPreShutdownGate)

    def _ExecuteCoordinatedShutdownGate(self):
        _lcm = self.__m
        _SINGLE_WAIT_TIMESPAN_MS = _LcMonitorImpl.GetPerSingleStepWaitTimespanMS()
        _MAX_WAIT_NUM            = _LcMonitorImpl.GetPerShutdownRequestWaitTimespanMS() // _SINGLE_WAIT_TIMESPAN_MS

        _numWait, _curSDR = 0, None

        while True:
            _numWait += 1

            if not _lcm.isCoordinatedShutdownRunning:
                break

            _curSDR = _lcm.curShutdownRequest
            if (_curSDR is not None) and _curSDR.isShutdown:
                break

            if self.__bM:
                if (_lcm._mainTLB is not None) and (_lcm._mainTLB.lcCeaseTLB is not None):
                    _lcm._mainTLB.lcCeaseTLB.IncrementCeaseAliveCounter()
            _TaskUtil.SleepMS(_SINGLE_WAIT_TIMESPAN_MS)

            if _numWait >= _MAX_WAIT_NUM:
                break
            continue

        if (_curSDR is None) or not _curSDR.isShutdown:
            if vlogif._IsReleaseModeEnabled():
                vlogif._XLogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcSDC_TID_002))
        if _lcm.isCoordinatedShutdownRunning:
            self.__CoordinateCeasingGateXT(_ELcCeaseGateFlag.ebfShutdownGate)
        if _lcm.isCoordinatedShutdownRunning:
            self.__CoordinateCeasingGateFW(_ELcCeaseGateFlag.ebfShutdownGate)
        _lcm._OpenCoordinatedGate(_LcMonitorImpl._ELcMonStateFlag.ebfShutdownGate)

    @property
    def __logPrefix(self):
        return '[LcSDC][MRbl]' if self.__bM else '[LcSDC][LcG]'

    def __CoordinateCeasingGateXT(self, eCeaseFlag_ : _ELcCeaseGateFlag):
        _lstCTLBs = self.__axt
        if _lstCTLBs is None:
            return

        _ii = 0
        _NUM = 0 if _lstCTLBs is None else len(_lstCTLBs)

        _SINGLE_WAIT_TIMESPAN_MS = _LcMonitorImpl.GetPerSingleStepWaitTimespanMS()
        _OPEN_GATE_TIMESPAN_MS   = _LcMonitorImpl.GetPerShutdownPhaseWaitTimespanMS() // _NUM

        if _OPEN_GATE_TIMESPAN_MS < _SINGLE_WAIT_TIMESPAN_MS:
            _OPEN_GATE_TIMESPAN_MS = _SINGLE_WAIT_TIMESPAN_MS
        elif _OPEN_GATE_TIMESPAN_MS > _LcMonitorImpl.GetPerShutdownPhaseWaitTimespanMS():
            _OPEN_GATE_TIMESPAN_MS = _LcMonitorImpl.GetPerOpenGateWaitTimespanMS()

        _perGateOpenTimeout = _Timeout.TimespanToTimeout(_OPEN_GATE_TIMESPAN_MS)

        _lcm = self.__m
        while _lcm.isCoordinatedShutdownRunning:
            if _ii < _NUM:
                _ctlb = _lstCTLBs[_ii]
                _ii += 1

                if eCeaseFlag_.isCeasingGate:
                    _ctlb._OpenCeasingGate(timeout_=_perGateOpenTimeout)
                elif eCeaseFlag_.isPreShutdownGate:
                    _ctlb._OpenPreShutdownGate(timeout_=_perGateOpenTimeout)
                else:
                    _ctlb._OpenShutdownGate(timeout_=_perGateOpenTimeout)

                if self.__bM:
                    _lcm._mainTLB.lcCeaseTLB.IncrementCeaseAliveCounter()

                _TaskUtil.SleepMS(_SINGLE_WAIT_TIMESPAN_MS)
                continue

            break
        _perGateOpenTimeout.CleanUp()

    def __CoordinateCeasingGateFW(self, eCeaseFlag_ : _ELcCeaseGateFlag):
        _lstCTLBs = self.__act
        if _lstCTLBs is None:
            _bIgnore = True
        else:
            if self.__bM:
                _lstCTLBs = [_ctlb for _ctlb in _lstCTLBs if not _ctlb.lcStaticTLB.taskBadge.isFwMain]
            _bIgnore = len(_lstCTLBs) < 1

        if _bIgnore:
            return

        _ii   = 0
        _NUM = 0 if _lstCTLBs is None else len(_lstCTLBs)

        _SINGLE_WAIT_TIMESPAN_MS = _LcMonitorImpl.GetPerSingleStepWaitTimespanMS()
        _OPEN_GATE_TIMESPAN_MS   = _LcMonitorImpl.GetPerShutdownPhaseWaitTimespanMS() // _NUM

        if _OPEN_GATE_TIMESPAN_MS < _SINGLE_WAIT_TIMESPAN_MS:
            _OPEN_GATE_TIMESPAN_MS = _SINGLE_WAIT_TIMESPAN_MS
        elif _OPEN_GATE_TIMESPAN_MS > _LcMonitorImpl.GetPerShutdownPhaseFwcWaitTimespanMS():
            _OPEN_GATE_TIMESPAN_MS = _LcMonitorImpl.GetPerOpenGateWaitTimespanMS()

        _perGateOpenTimeout = _Timeout.TimespanToTimeout(_OPEN_GATE_TIMESPAN_MS)

        _lcm = self.__m
        while _lcm.isCoordinatedShutdownRunning:
            if _ii < _NUM:
                _ctlb = _lstCTLBs[_ii]
                _ii += 1

                if eCeaseFlag_.isCeasingGate:
                    _ctlb._OpenCeasingGate(timeout_=_perGateOpenTimeout)
                elif eCeaseFlag_.isPreShutdownGate:
                    _ctlb._OpenPreShutdownGate(timeout_=_perGateOpenTimeout)
                else:
                    _ctlb._OpenShutdownGate(timeout_=_perGateOpenTimeout)

                if self.__bM:
                    _lcm._mainTLB.lcCeaseTLB.IncrementCeaseAliveCounter()

                _TaskUtil.SleepMS(_SINGLE_WAIT_TIMESPAN_MS)
                continue

            break

        _perGateOpenTimeout.CleanUp()
