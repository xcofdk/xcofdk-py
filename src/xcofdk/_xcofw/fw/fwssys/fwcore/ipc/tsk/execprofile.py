# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : execprofile.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from xcofdk._xcofw.fw.fwssys.fwcore.logging       import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.base.gtimeout import _Timeout
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject import _AbstractSlotsObject


class _ExecutionProfile(_AbstractSlotsObject):

    __slots__ = [
        '__bReCalc'
      , '__uniqueName'
      , '__cyclicCeaseTimespanMS'
      , '__runPhaseMaxProcTimeMS'
      , '__runPhaseFreqMS'
      , '__bStrictTiming'
      , '__bLcFailureReportPermission'
      , '__revisedCyclicMaxProcTimespanMS'
      , '__revisedPerLcMonCycleMaxProcTimespanMS'
    ]

    __bDEFAULT_STRICT_TIMING                = False
    __bDEFAULT_LC_FAILURE_REPORT_PERMISSION = True
    __DEFAULT_CEASE_CYCLE_TIMESPAN_MS      = 20
    __DEFAULT_CYCLIC_RUN_PAUSE_TIMESPAN_MS = 200

    __PROC_TIMESPAN_DEVIATION_FACTOR        = 10
    __PROC_TIMESPAN_DEVIATION_MIN_THRESHOLD = 5

    __LC_MONITOR_CYCLIC_MAX_PROC_TIMESPAN_MS          = 20
    __LC_MONITOR_CYCLIC_RUN_PAUSE_TIMESPAN_MS         = None
    __DEFAULT_LC_MONITOR_CYCLIC_RUN_PAUSE_TIMESPAN_MS = 50

    def __init__( self
                , uniqueName_                        : str                    =None
                , runPhaseFreqMS_                    : [int, float, _Timeout] =None
                , runPhaseMaxProcTimeMS_             : [int, float, _Timeout] =None
                , cyclicCeaseTimespanMS_             : [int, float, _Timeout] =None
                , bStrictTimingEnabled_              : bool                   =None
                , bLcFailureReportPermissionEnabled_ : bool                   =None
                , bLcMonitor_                        : bool                   =None
                , xtaskProfileExt_                                            =None
                , cloneBy_                                                    =None):

        super().__init__()

        self.__bReCalc                               = None
        self.__uniqueName                            = None
        self.__bStrictTiming                         = None
        self.__runPhaseFreqMS                        = None
        self.__cyclicCeaseTimespanMS                 = None
        self.__runPhaseMaxProcTimeMS                 = None
        self.__bLcFailureReportPermission            = None
        self.__revisedCyclicMaxProcTimespanMS        = None
        self.__revisedPerLcMonCycleMaxProcTimespanMS = None

        if not (isinstance(uniqueName_, str) and len(uniqueName_)):
            uniqueName_ = type(self).__name__

        if cloneBy_ is not None:
            if not isinstance(cloneBy_, _ExecutionProfile):
                vlogif._LogOEC(True, -1307)
            elif not cloneBy_.isValid:
                vlogif._LogOEC(True, -1308)
            else:
                cloneBy_.__CheckForReCalculation()

                self.__bReCalc                               = cloneBy_.__bReCalc
                self.__uniqueName                            = str(cloneBy_.__uniqueName)
                self.__bStrictTiming                         = cloneBy_.__bStrictTiming
                self.__runPhaseFreqMS                        = cloneBy_.__runPhaseFreqMS
                self.__cyclicCeaseTimespanMS                 = cloneBy_.__cyclicCeaseTimespanMS
                self.__runPhaseMaxProcTimeMS                 = cloneBy_.__runPhaseMaxProcTimeMS
                self.__bLcFailureReportPermission            = cloneBy_.__bLcFailureReportPermission
                self.__revisedCyclicMaxProcTimespanMS        = cloneBy_.__revisedCyclicMaxProcTimespanMS
                self.__revisedPerLcMonCycleMaxProcTimespanMS = cloneBy_.__revisedPerLcMonCycleMaxProcTimespanMS
                return

        if bLcMonitor_:
            if _ExecutionProfile._GetLcMonitorCyclicRunPauseTimespanMS() is None:
                vlogif._LogOEC(True, -1309)
                return

            if runPhaseFreqMS_ is None:
                runPhaseFreqMS_ = _ExecutionProfile.__GetLcMonCyclicRunPauseTimespanMS()
            if runPhaseMaxProcTimeMS_ is None:
                runPhaseMaxProcTimeMS_ = _ExecutionProfile.__LC_MONITOR_CYCLIC_MAX_PROC_TIMESPAN_MS
            if cyclicCeaseTimespanMS_ is None:
                cyclicCeaseTimespanMS_ = _ExecutionProfile.__DEFAULT_CEASE_CYCLE_TIMESPAN_MS

        elif xtaskProfileExt_ is not None:
            _xtp = xtaskProfileExt_
            if runPhaseFreqMS_ is None:
                runPhaseFreqMS_ = _xtp.runPhaseFrequencyMS
            if runPhaseMaxProcTimeMS_ is None:
                runPhaseMaxProcTimeMS_ = _xtp.runPhaseMaxProcessingTimeMS

        _lstBoolParams = [ bStrictTimingEnabled_ , bLcFailureReportPermissionEnabled_ ]
        for _ee in _lstBoolParams:
            if _ee is not None:
                if not isinstance(_ee, bool):
                    vlogif._LogOEC(True, -1310)
                    return

        _lstMsParams = [ runPhaseFreqMS_ , runPhaseMaxProcTimeMS_, cyclicCeaseTimespanMS_ ]
        for _ee in _lstMsParams:
            if _ee is not None:
                if not isinstance(_ee, (int, float, _Timeout)):
                    vlogif._LogOEC(True, -1311)
                    return

        self.__uniqueName = uniqueName_

        if runPhaseFreqMS_ is not None:
            _tout = _Timeout.TimespanToTimeout(runPhaseFreqMS_)
            if _tout is None:
                vlogif._LogOEC(True, -1312)
                return
            self.__runPhaseFreqMS = _tout.toMSec
            _tout.CleanUp()
        else:
            self.__runPhaseFreqMS = _ExecutionProfile.__DEFAULT_CYCLIC_RUN_PAUSE_TIMESPAN_MS

        if runPhaseMaxProcTimeMS_ is not None:
            _tout = _Timeout.TimespanToTimeout(runPhaseMaxProcTimeMS_)
            if (_tout is None) or _tout.isInfiniteTimeout:
                vlogif._LogOEC(True, -1313)
                if _tout is not None:
                    _tout.CleanUp()
                return
            self.__runPhaseMaxProcTimeMS = _tout.toMSec
            _tout.CleanUp()
        else:
            self.__runPhaseMaxProcTimeMS = self.__runPhaseFreqMS

        if cyclicCeaseTimespanMS_ is not None:
            _tout = _Timeout.TimespanToTimeout(cyclicCeaseTimespanMS_)
            if (_tout is None) or _tout.isInfiniteTimeout:
                vlogif._LogOEC(True, -1314)
                if _tout is not None:
                    _tout.CleanUp()
                return
            self.__cyclicCeaseTimespanMS = _tout.toMSec
            _tout.CleanUp()
        else:
            self.__cyclicCeaseTimespanMS = _ExecutionProfile.__DEFAULT_CEASE_CYCLE_TIMESPAN_MS

        if bStrictTimingEnabled_ is not None:
            self.__bStrictTiming = bStrictTimingEnabled_
        else:
            self.__bStrictTiming = _ExecutionProfile.__bDEFAULT_STRICT_TIMING

        if bLcFailureReportPermissionEnabled_ is not None:
            self.__bLcFailureReportPermission = bLcFailureReportPermissionEnabled_
        else:
            self.__bLcFailureReportPermission = _ExecutionProfile.__bDEFAULT_LC_FAILURE_REPORT_PERMISSION

        self.__revisedCyclicMaxProcTimespanMS = _ExecutionProfile.__GetDeviatedTimespan(self.__runPhaseMaxProcTimeMS)
        self.__RecalculateRevisedAttributes()

        self.__bReCalc = _ExecutionProfile._GetLcMonitorCyclicRunPauseTimespanMS() is None

    @staticmethod
    def IsDefaultStrictTimingEnabled() -> bool:
        return _ExecutionProfile.__bDEFAULT_STRICT_TIMING

    @staticmethod
    def IsDefaultLcFailureReportPermissionEnabled() -> bool:
        return _ExecutionProfile.__bDEFAULT_LC_FAILURE_REPORT_PERMISSION

    @property
    def isValid(self):
        return self.__bReCalc is not None

    @property
    def isStrictTimingEnabled(self):
        return self.__bStrictTiming

    @isStrictTimingEnabled.setter
    def isStrictTimingEnabled(self, bEnabled_ : bool):
        if self.__isInvalid:
            return
        if isinstance(bEnabled_, bool):
            self.__bStrictTiming = bEnabled_

    @property
    def isLcFailureReportPermissionEnabled(self):
        return self.__bLcFailureReportPermission

    @isLcFailureReportPermissionEnabled.setter
    def isLcFailureReportPermissionEnabled(self, bEnabled_ : bool):
        if self.__isInvalid:
            return
        if isinstance(bEnabled_, bool):
            self.__bLcFailureReportPermission = bEnabled_

    @property
    def uniqueName(self):
        return self.__uniqueName


    @property
    def runPhaseFreqMS(self) -> int:
        return self.__runPhaseFreqMS

    @runPhaseFreqMS.setter
    def runPhaseFreqMS(self, timespanMS_ : [int, float, _Timeout]):
        if self.__isInvalid:
            return
        _tout = _Timeout.TimespanToTimeout(timespanMS_)
        if _tout is not None:
            self.__runPhaseFreqMS = _tout.toMSec
            _tout.CleanUp()

    @property
    def runPhaseMaxProcTimeMS(self) -> int:
        return self.__runPhaseMaxProcTimeMS

    @runPhaseMaxProcTimeMS.setter
    def runPhaseMaxProcTimeMS(self, timespanMS_ : [int, float, _Timeout]):
        if self.__isInvalid:
            return
        _tout = _Timeout.TimespanToTimeout(timespanMS_)
        if _tout is not None:
            self.__runPhaseMaxProcTimeMS = _tout.toMSec
            _tout.CleanUp()

    @property
    def cyclicCeaseTimespanMS(self) -> int:
        return self.__cyclicCeaseTimespanMS

    @cyclicCeaseTimespanMS.setter
    def cyclicCeaseTimespanMS(self, timespanMS_ : [int, float, _Timeout]):
        if self.__isInvalid:
            return
        _tout = _Timeout.TimespanToTimeout(timespanMS_)
        if _tout is not None:
            self.__cyclicCeaseTimespanMS = _tout.toMSec
            _tout.CleanUp()

    @property
    def _revisedCyclicMaxProcTimespanMS(self) -> int:
        return self.__revisedCyclicMaxProcTimespanMS

    @property
    def _revisedCyclicTotalProcTimespanMS(self) -> int:
        return self.__revisedCyclicMaxProcTimespanMS + self.__runPhaseFreqMS

    @property
    def _revisedPerLcMonCycleMaxProcTimespanMS(self) -> int:
        return self.__revisedPerLcMonCycleMaxProcTimespanMS

    @property
    def _revisedPerLcMonCycleTotalProcTimespanMS(self) -> int:
        return self.__revisedPerLcMonCycleMaxProcTimespanMS + self.__runPhaseFreqMS

    @staticmethod
    def _GetLcMonitorCyclicRunPauseTimespanMS():
        return _ExecutionProfile.__LC_MONITOR_CYCLIC_RUN_PAUSE_TIMESPAN_MS

    @staticmethod
    def _SetLcMonitorCyclicRunPauseTimespanMS(lcMonCyclicRunPauseTimespanMS_ : int):
        if lcMonCyclicRunPauseTimespanMS_ is not None:
            if _ExecutionProfile.__LC_MONITOR_CYCLIC_RUN_PAUSE_TIMESPAN_MS is not None:
                vlogif._LogOEC(True, -1315)
        _ExecutionProfile.__LC_MONITOR_CYCLIC_RUN_PAUSE_TIMESPAN_MS = lcMonCyclicRunPauseTimespanMS_

    def _UpdateUniqueName(self, uniqueName_ : str):
        if self.__isInvalid:
            return

        _bChanged = False
        if isinstance(uniqueName_, str) and len(uniqueName_):
            _bChanged = uniqueName_ != self.__uniqueName
            self.__uniqueName = uniqueName_
        if self.__bReCalc:
            self.__CheckForReCalculation()

    def _Clone(self, bPrint_ =False):
        if self.__isInvalid:
            return None

        res = _ExecutionProfile(cloneBy_=self)
        if not res.isValid:
            res.CleanUp()
            res = None
        return res

    def _ToString(self, *args_, **kwargs_):
        if self.__isInvalid:
            return None

        res  = '{}{} :\n'.format(type(self).__name__, '' if self.__uniqueName is None else ' [{}]'.format(self.__uniqueName))
        res += '  {:<46s} : {:<s}\n'.format('isStrictTimingEnabled'                          , str(self.isStrictTimingEnabled))
        res += '  {:<46s} : {:<s}\n'.format('isLcFailureReportPermissionEnabled'             , str(self.isLcFailureReportPermissionEnabled))
        res += '  {:<46s} : {:<s}\n'.format('runPhaseFrequencyMS'                            , str(self.runPhaseFreqMS))
        res += '  {:<46s} : {:<s}\n'.format('runPhaseMaxProcessingTimeMS'                    , str(self.runPhaseMaxProcTimeMS))
        res += '  {:<46s} : {:<s}\n'.format('cyclicCeaseTimespanMS'                          , str(self.cyclicCeaseTimespanMS))
        res += '  {:<46s} : {:<s}\n'.format('revisedCyclicMaxProcTimespanMS'                 , str(self._revisedCyclicMaxProcTimespanMS))
        res += '  {:<46s} : {:<s}\n'.format('revisedCyclicTotalProcessingTimespanMS'         , str(self._revisedCyclicTotalProcTimespanMS))
        res += '  {:<46s} : {:<s}\n'.format('revisedPerLcMonCycleMaxProcTimespanMS'          , str(self._revisedPerLcMonCycleMaxProcTimespanMS))
        res += '  {:<46s} : {:<s}\n'.format('revisedPerLcMonCycleTotalProcessingTimespanMS'  , str(self._revisedPerLcMonCycleTotalProcTimespanMS))
        res = res.rstrip()
        return res

    def _CleanUp(self):
        if self.__isInvalid:
            return

        self.__bReCalc                               = None
        self.__uniqueName                            = None
        self.__bStrictTiming                         = None
        self.__runPhaseFreqMS                        = None
        self.__cyclicCeaseTimespanMS                 = None
        self.__runPhaseMaxProcTimeMS                 = None
        self.__bLcFailureReportPermission            = None
        self.__revisedCyclicMaxProcTimespanMS        = None
        self.__revisedPerLcMonCycleMaxProcTimespanMS = None

    @property
    def __isInvalid(self):
        return self.__bReCalc is None

    @staticmethod
    def __GetLcMonCyclicRunPauseTimespanMS():
        res = _ExecutionProfile.__LC_MONITOR_CYCLIC_RUN_PAUSE_TIMESPAN_MS
        if res is None:
            res = _ExecutionProfile.__DEFAULT_LC_MONITOR_CYCLIC_RUN_PAUSE_TIMESPAN_MS
        return res

    @staticmethod
    def __GetDeviatedTimespan(timespan_ : int) -> int:
        if timespan_ <= 0:
            return 0

        res = (timespan_ * _ExecutionProfile.__PROC_TIMESPAN_DEVIATION_FACTOR) // 100
        if res < _ExecutionProfile.__PROC_TIMESPAN_DEVIATION_MIN_THRESHOLD:
            res = _ExecutionProfile.__PROC_TIMESPAN_DEVIATION_MIN_THRESHOLD
        res += timespan_
        return res

    def __CheckForReCalculation(self):
        if self.__isInvalid:
            return
        if not self.__bReCalc:
            return
        if _ExecutionProfile._GetLcMonitorCyclicRunPauseTimespanMS() is None:
            return

        self.__bReCalc = False
        if _ExecutionProfile._GetLcMonitorCyclicRunPauseTimespanMS() == _ExecutionProfile.__DEFAULT_LC_MONITOR_CYCLIC_RUN_PAUSE_TIMESPAN_MS:
            return

        self.__RecalculateRevisedAttributes()

    def __RecalculateRevisedAttributes(self):
        tmp = self.__runPhaseMaxProcTimeMS
        if tmp <= 0:
            self.__revisedPerLcMonCycleMaxProcTimespanMS = 0
        else:
            if (tmp-_ExecutionProfile.__PROC_TIMESPAN_DEVIATION_MIN_THRESHOLD) > _ExecutionProfile.__GetLcMonCyclicRunPauseTimespanMS():
                pass
            else:
                _bCC = False
                if _bCC:
                    _factor = -(-_ExecutionProfile.__GetLcMonCyclicRunPauseTimespanMS() // tmp)
                else:
                    _factor = _ExecutionProfile.__GetLcMonCyclicRunPauseTimespanMS() // tmp
                tmp = tmp * _factor
            self.__revisedPerLcMonCycleMaxProcTimespanMS = _ExecutionProfile.__GetDeviatedTimespan(tmp)
