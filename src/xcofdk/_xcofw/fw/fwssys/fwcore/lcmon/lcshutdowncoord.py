# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : lcshutdowncoord.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from xcofdk._xcofw.fw.fwssys.fwcore.logging           import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.base.gtimeout     import _Timeout
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil  import _TaskUtil
from xcofdk._xcofw.fw.fwssys.fwcore.lcmon.lcmontlb    import _ELcCeaseGateFlag
from xcofdk._xcofw.fw.fwssys.fwcore.lcmon.lcmontlb    import _ELcCeaseTLBState
from xcofdk._xcofw.fw.fwssys.fwcore.lcmon.lcmonimpl   import _LcMonitorImpl

from xcofdk._xcofw.fw.fwssys.fwerrh.fwerrorcodes import _EFwErrorCode

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine

class _LcShutdownCoordinator:
    __slots__ = [ '__lcMon' , '__bByMR' , '__lstFwCTLBs' , '__lstXuCTLBs' ]

    def __init__(self, lcMon_ : _LcMonitorImpl):
        self.__lcMon      = lcMon_
        self.__bByMR      = lcMon_._isCoordinatedShutdownManagedByMR
        self.__lstFwCTLBs = None
        self.__lstXuCTLBs = None

    def _ExecuteCoordinatedCeasingGate(self):
        _lcm       = self.__lcMon
        _lstFwCTLBs = None
        _lstXuCTLBs = None

        _lstFwCTLBs, _lstXuCTLBs = _lcm._GetCeaseTLBLists(_ELcCeaseTLBState.eRFTPrepareCeasing, bReverseStartTimeSorted_=True)
        self.__lstFwCTLBs = _lstFwCTLBs
        self.__lstXuCTLBs = _lstXuCTLBs

        if _lcm.isCoordinatedShutdownRunning:
            self.__CoordinateCeasingGateXU(_ELcCeaseGateFlag.ebfCeasingGate)

        if _lcm.isCoordinatedShutdownRunning:
            self.__CoordinateCeasingGateFW(_ELcCeaseGateFlag.ebfCeasingGate)

        _lcm._OpenCoordinatedGate(_LcMonitorImpl._ELcMonStateFlag.ebfCeasingGate)

    def _ExecuteCoordinatedPreShutdownGate(self):
        _lcm = self.__lcMon

        _curSDR = _lcm.eCurrentShutdownRequest
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

            _curSDR = _lcm.eCurrentShutdownRequest
            if (_curSDR is not None) and _curSDR.isPreShutdown:
                break

            if self.__bByMR:
                _lcm._mainTLB.lcCeaseTLB.IncrementCeaseAliveCounter()
            _TaskUtil.SleepMS(_SINGLE_WAIT_TIMESPAN_MS)

            if _numWait >= _MAX_WAIT_NUM:
                break
            continue

        if (_curSDR is None) or not _curSDR.isPreShutdown:
            if not vlogif._IsReleaseModeEnabled():
                pass 
            else:
                vlogif._XLogWarning('Maximum wait time for internal pre-gate expired, forcing to continue shutdown execution.')

        if _lcm.isCoordinatedShutdownRunning:
            self.__CoordinateCeasingGateXU(_ELcCeaseGateFlag.ebfPreShutdownGate)

        if _lcm.isCoordinatedShutdownRunning:
            self.__CoordinateCeasingGateFW(_ELcCeaseGateFlag.ebfPreShutdownGate)

        _lcm._OpenCoordinatedGate(_LcMonitorImpl._ELcMonStateFlag.ebfPreShutdownGate)

    def _ExecuteCoordinatedShutdownGate(self):
        _lcm = self.__lcMon

        _SINGLE_WAIT_TIMESPAN_MS = _LcMonitorImpl.GetPerSingleStepWaitTimespanMS()
        _MAX_WAIT_NUM            = _LcMonitorImpl.GetPerShutdownRequestWaitTimespanMS() // _SINGLE_WAIT_TIMESPAN_MS

        _numWait, _curSDR = 0, None

        while True:
            _numWait += 1

            if not _lcm.isCoordinatedShutdownRunning:
                break

            _curSDR = _lcm.eCurrentShutdownRequest
            if (_curSDR is not None) and _curSDR.isShutdown:
                break

            if self.__bByMR:
                _lcm._mainTLB.lcCeaseTLB.IncrementCeaseAliveCounter()
            _TaskUtil.SleepMS(_SINGLE_WAIT_TIMESPAN_MS)

            if _numWait >= _MAX_WAIT_NUM:
                break
            continue

        if (_curSDR is None) or not _curSDR.isShutdown:
            if not vlogif._IsReleaseModeEnabled():
                pass 
            else:
                vlogif._XLogWarning('Maximum wait time for internal gate expired, forcing to continue shutdown execution.')

        if _lcm.isCoordinatedShutdownRunning:
            self.__CoordinateCeasingGateXU(_ELcCeaseGateFlag.ebfShutdownGate)

        if _lcm.isCoordinatedShutdownRunning:
            self.__CoordinateCeasingGateFW(_ELcCeaseGateFlag.ebfShutdownGate)

        _lcm._OpenCoordinatedGate(_LcMonitorImpl._ELcMonStateFlag.ebfShutdownGate)

    @property
    def __logPrefix(self):
        return '[LcSDC][MRbl]' if self.__bByMR else '[LcSDC][LcG]'

    def __CoordinateCeasingGateXU(self, eCeaseFlag_ : _ELcCeaseGateFlag):
        _lstCTLBs = self.__lstXuCTLBs
        if _lstCTLBs is None:
            return

        lstTmp = None if _lstCTLBs is None else [_tt.lcStaticTLB.ToString() for _tt in _lstCTLBs]
        _ii = 0
        _NUM = 0 if _lstCTLBs is None else len(_lstCTLBs)

        _SINGLE_WAIT_TIMESPAN_MS = _LcMonitorImpl.GetPerSingleStepWaitTimespanMS()
        _OPEN_GATE_TIMESPAN_MS   = _LcMonitorImpl.GetPerShutdownPhaseWaitTimespanMS() // _NUM

        if _OPEN_GATE_TIMESPAN_MS < _SINGLE_WAIT_TIMESPAN_MS:
            _OPEN_GATE_TIMESPAN_MS = _SINGLE_WAIT_TIMESPAN_MS
        elif _OPEN_GATE_TIMESPAN_MS > _LcMonitorImpl.GetPerShutdownPhaseWaitTimespanMS():
            _OPEN_GATE_TIMESPAN_MS = _LcMonitorImpl.GetPerOpenGateWaitTimespanMS()

        _perGateOpenTimeout = _Timeout.TimespanToTimeout(_OPEN_GATE_TIMESPAN_MS)

        _lcm = self.__lcMon
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

                if self.__bByMR:
                    _lcm._mainTLB.lcCeaseTLB.IncrementCeaseAliveCounter()

                _TaskUtil.SleepMS(_SINGLE_WAIT_TIMESPAN_MS)
                continue

            break
        _perGateOpenTimeout.CleanUp()

    def __CoordinateCeasingGateFW(self, eCeaseFlag_ : _ELcCeaseGateFlag):
        _lstCTLBs = self.__lstFwCTLBs
        if _lstCTLBs is None:
            _bIgnore = True
        else:
            if self.__bByMR:
                _lstCTLBs = [_ctlb for _ctlb in _lstCTLBs if not _ctlb.lcStaticTLB.taskBadge.isFwMain]
            _bIgnore = len(_lstCTLBs) < 1

        if _bIgnore:
            return

        lstTmp = None if _lstCTLBs is None else [_tt.lcStaticTLB.ToString() for _tt in _lstCTLBs]
        _ii   = 0
        _NUM = 0 if _lstCTLBs is None else len(_lstCTLBs)

        _SINGLE_WAIT_TIMESPAN_MS = _LcMonitorImpl.GetPerSingleStepWaitTimespanMS()
        _OPEN_GATE_TIMESPAN_MS   = _LcMonitorImpl.GetPerShutdownPhaseWaitTimespanMS() // _NUM

        if _OPEN_GATE_TIMESPAN_MS < _SINGLE_WAIT_TIMESPAN_MS:
            _OPEN_GATE_TIMESPAN_MS = _SINGLE_WAIT_TIMESPAN_MS
        elif _OPEN_GATE_TIMESPAN_MS > _LcMonitorImpl.GetPerShutdownPhaseFwcWaitTimespanMS():
            _OPEN_GATE_TIMESPAN_MS = _LcMonitorImpl.GetPerOpenGateWaitTimespanMS()

        _perGateOpenTimeout = _Timeout.TimespanToTimeout(_OPEN_GATE_TIMESPAN_MS)

        _lcm = self.__lcMon
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

                if self.__bByMR:
                    _lcm._mainTLB.lcCeaseTLB.IncrementCeaseAliveCounter()

                _TaskUtil.SleepMS(_SINGLE_WAIT_TIMESPAN_MS)
                continue

            break
        _perGateOpenTimeout.CleanUp()
