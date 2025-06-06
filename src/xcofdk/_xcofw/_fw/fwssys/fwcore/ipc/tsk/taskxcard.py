# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : taskxcard.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from typing import Union

from _fw.fwssys.fwcore.logging           import vlogif
from _fw.fwssys.fwcore.base.gtimeout     import _Timeout
from _fw.fwssys.fwcore.types.aobject     import _AbsSlotsObject
from _fw.fwssys.fwcore.types.commontypes import _EDepInjCmd
from _fw.fwssys.fwerrh.fwerrorcodes      import _EFwErrorCode

class _TaskXCard(_AbsSlotsObject):
    __slots__ = [ '__a' , '__k' , '__bR' , '__un' , '__cf' , '__mp' , '__rf' , '__bS' , '__bP' , '__rmp' , '__rmp2' ]

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
                , uniqueName_     : str                            =None
                , runPhaseFreqMS_ : Union[int, float, _Timeout] =None
                , runPhaseMPTMS_  : Union[int, float, _Timeout] =None
                , cceaseFreqMS_   : Union[int, float, _Timeout] =None
                , bStrictTiming_  : bool                           =None
                , bFRPermission_  : bool                           =None
                , bLcMonitor_     : bool                           =None
                , xtPrfExt_       =None
                , cloneBy_        =None):
        super().__init__()
        self.__a    = None
        self.__k    = None
        self.__bR   = None
        self.__un   = None
        self.__bS   = None
        self.__rf   = None
        self.__cf   = None
        self.__mp   = None
        self.__bP   = None
        self.__rmp  = None
        self.__rmp2 = None

        if not (isinstance(uniqueName_, str) and len(uniqueName_)):
            uniqueName_ = type(self).__name__

        if cloneBy_ is not None:
            if not isinstance(cloneBy_, _TaskXCard):
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00187)
            elif not cloneBy_.isValid:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00188)
            else:
                cloneBy_.__CheckForReCalculation()

                self.__a    = cloneBy_.__a
                self.__k    = cloneBy_.__k
                self.__bP   = cloneBy_.__bP
                self.__bR   = cloneBy_.__bR
                self.__bS   = cloneBy_.__bS
                self.__cf   = cloneBy_.__cf
                self.__rf   = cloneBy_.__rf
                self.__mp   = cloneBy_.__mp
                self.__un   = str(cloneBy_.__un)
                self.__rmp  = cloneBy_.__rmp
                self.__rmp2 = cloneBy_.__rmp2
                return

        if bLcMonitor_:
            if _TaskXCard._GetLcMonitorCyclicRunPauseTimespanMS() is None:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00189)
                return

            if runPhaseFreqMS_ is None:
                runPhaseFreqMS_ = _TaskXCard.__GetLcMonCyclicRunPauseTimespanMS()
            if runPhaseMPTMS_ is None:
                runPhaseMPTMS_ = _TaskXCard.__LC_MONITOR_CYCLIC_MAX_PROC_TIMESPAN_MS
            if cceaseFreqMS_ is None:
                cceaseFreqMS_ = _TaskXCard.__DEFAULT_CEASE_CYCLE_TIMESPAN_MS

        elif xtPrfExt_ is not None:
            _xtp = xtPrfExt_
            if runPhaseFreqMS_ is None:
                runPhaseFreqMS_ = _xtp.runPhaseFrequencyMS
            if runPhaseMPTMS_ is None:
                runPhaseMPTMS_ = _xtp.runPhaseMaxProcessingTimeMS

        _lstBoolParams = [ bStrictTiming_ , bFRPermission_ ]
        for _ee in _lstBoolParams:
            if _ee is not None:
                if not isinstance(_ee, bool):
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00190)
                    return

        _lstMsParams = [ runPhaseFreqMS_ , runPhaseMPTMS_, cceaseFreqMS_ ]
        for _ee in _lstMsParams:
            if _ee is not None:
                if not isinstance(_ee, (int, float, _Timeout)):
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00191)
                    return

        self.__un = uniqueName_

        if runPhaseFreqMS_ is not None:
            _tout = _Timeout.TimespanToTimeout(runPhaseFreqMS_)
            if _tout is None:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00192)
                return
            self.__rf = _tout.toMSec
            _tout.CleanUp()
        else:
            self.__rf = _TaskXCard.__DEFAULT_CYCLIC_RUN_PAUSE_TIMESPAN_MS

        if runPhaseMPTMS_ is not None:
            _tout = _Timeout.TimespanToTimeout(runPhaseMPTMS_)
            if (_tout is None) or _tout.isInfiniteTimeout:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00193)
                if _tout is not None:
                    _tout.CleanUp()
                return
            self.__mp = _tout.toMSec
            _tout.CleanUp()
        else:
            self.__mp = self.__rf

        if cceaseFreqMS_ is not None:
            _tout = _Timeout.TimespanToTimeout(cceaseFreqMS_)
            if (_tout is None) or _tout.isInfiniteTimeout:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00194)
                if _tout is not None:
                    _tout.CleanUp()
                return
            self.__cf = _tout.toMSec
            _tout.CleanUp()
        else:
            self.__cf = _TaskXCard.__DEFAULT_CEASE_CYCLE_TIMESPAN_MS

        if bStrictTiming_ is not None:
            self.__bS = bStrictTiming_
        else:
            self.__bS = _TaskXCard.__bDEFAULT_STRICT_TIMING

        if bFRPermission_ is not None:
            self.__bP = bFRPermission_
        else:
            self.__bP = _TaskXCard.__bDEFAULT_LC_FAILURE_REPORT_PERMISSION

        self.__rmp = _TaskXCard.__GetDeviatedTimespan(self.__mp)
        self.__RecalculateRevisedAttributes()

        self.__bR = _TaskXCard._GetLcMonitorCyclicRunPauseTimespanMS() is None

    @staticmethod
    def IsDefaultStrictTimingEnabled() -> bool:
        return _TaskXCard.__bDEFAULT_STRICT_TIMING

    @staticmethod
    def IsDefaultLcFailureReportPermissionEnabled() -> bool:
        return _TaskXCard.__bDEFAULT_LC_FAILURE_REPORT_PERMISSION

    @property
    def isValid(self):
        return self.__bR is not None

    @property
    def isStrictTimingEnabled(self):
        return self.__bS

    @isStrictTimingEnabled.setter
    def isStrictTimingEnabled(self, bEnabled_ : bool):
        if self.__isInvalid:
            return
        if isinstance(bEnabled_, bool):
            self.__bS = bEnabled_

    @property
    def isLcFailureReportPermissionEnabled(self):
        return self.__bP

    @isLcFailureReportPermissionEnabled.setter
    def isLcFailureReportPermissionEnabled(self, bEnabled_ : bool):
        if self.__isInvalid:
            return
        if isinstance(bEnabled_, bool):
            self.__bP = bEnabled_

    @property
    def args(self):
        if self.__a is None:
            self.__a = ()
        return self.__a

    @property
    def kwargs(self):
        if self.__k is None:
            self.__k = {}
        return self.__k

    @property
    def uniqueName(self):
        return self.__un

    @property
    def runPhaseFreqMS(self) -> int:
        return self.__rf

    @runPhaseFreqMS.setter
    def runPhaseFreqMS(self, timespanMS_ : Union[int, float, _Timeout]):
        if self.__isInvalid:
            return
        _tout = _Timeout.TimespanToTimeout(timespanMS_)
        if _tout is not None:
            self.__rf = _tout.toMSec
            _tout.CleanUp()

    @property
    def runPhaseMaxProcTimeMS(self) -> int:
        return self.__mp

    @runPhaseMaxProcTimeMS.setter
    def runPhaseMaxProcTimeMS(self, timespanMS_ : Union[int, float, _Timeout]):
        if self.__isInvalid:
            return
        _tout = _Timeout.TimespanToTimeout(timespanMS_)
        if _tout is not None:
            self.__mp = _tout.toMSec
            _tout.CleanUp()

    @property
    def cyclicCeaseTimespanMS(self) -> int:
        return self.__cf

    @cyclicCeaseTimespanMS.setter
    def cyclicCeaseTimespanMS(self, timespanMS_ : Union[int, float, _Timeout]):
        if self.__isInvalid:
            return
        _tout = _Timeout.TimespanToTimeout(timespanMS_)
        if _tout is not None:
            self.__cf = _tout.toMSec
            _tout.CleanUp()

    @property
    def _revisedCyclicMaxProcTimespanMS(self) -> int:
        return self.__rmp

    @property
    def _revisedCyclicTotalProcTimespanMS(self) -> int:
        return self.__rmp + self.__rf

    @property
    def _revisedPerLcMonCycleMaxProcTimespanMS(self) -> int:
        return self.__rmp2

    @property
    def _revisedPerLcMonCycleTotalProcTimespanMS(self) -> int:
        return self.__rmp2 + self.__rf

    def _SetStartArgs(self, *args_, **kwargs_):
        if not isinstance(args_, tuple):
            args_ = ()
        if not isinstance(kwargs_, dict):
            kwargs_ = {}
        self.__a   = tuple(args_)
        self.__k = kwargs_.copy()

    @staticmethod
    def _GetLcMonitorCyclicRunPauseTimespanMS():
        return _TaskXCard.__LC_MONITOR_CYCLIC_RUN_PAUSE_TIMESPAN_MS

    @staticmethod
    def _ClsDepInjection(dinjCmd_ : _EDepInjCmd, runPauseTimespanMS_ : int =None):
        res = True
        _ts = None
        if dinjCmd_.isDeInject:
            pass
        else:
            if _TaskXCard.__LC_MONITOR_CYCLIC_RUN_PAUSE_TIMESPAN_MS is not None:
                res = False
            else:
                _ts = None if not (isinstance(runPauseTimespanMS_, int) and runPauseTimespanMS_>0) else runPauseTimespanMS_
                res = _ts is not None
        _TaskXCard.__LC_MONITOR_CYCLIC_RUN_PAUSE_TIMESPAN_MS = _ts
        return res

    def _UpdateUniqueName(self, uniqueName_ : str):
        if self.__isInvalid:
            return

        _bChanged = False
        if isinstance(uniqueName_, str) and len(uniqueName_):
            _bChanged = uniqueName_ != self.__un
            self.__un = uniqueName_
        if self.__bR:
            self.__CheckForReCalculation()

    def _Clone(self, bPrint_ =False):
        if self.__isInvalid:
            return None

        res = _TaskXCard(cloneBy_=self)
        if not res.isValid:
            res.CleanUp()
            res = None
        return res

    def _ToString(self):
        if self.__isInvalid:
            return None

        res  = '{}{} :\n'.format(type(self).__name__, '' if self.__un is None else ' [{}]'.format(self.__un))
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
        self.__a    = None
        self.__k    = None
        self.__bR   = None
        self.__un   = None
        self.__bS   = None
        self.__rf   = None
        self.__cf   = None
        self.__mp   = None
        self.__bP   = None
        self.__rmp  = None
        self.__rmp2 = None

    @property
    def __isInvalid(self):
        return self.__bR is None

    @staticmethod
    def __GetLcMonCyclicRunPauseTimespanMS():
        res = _TaskXCard.__LC_MONITOR_CYCLIC_RUN_PAUSE_TIMESPAN_MS
        if res is None:
            res = _TaskXCard.__DEFAULT_LC_MONITOR_CYCLIC_RUN_PAUSE_TIMESPAN_MS
        return res

    @staticmethod
    def __GetDeviatedTimespan(timespan_ : int) -> int:
        if timespan_ <= 0:
            return 0

        res = (timespan_ * _TaskXCard.__PROC_TIMESPAN_DEVIATION_FACTOR) // 100
        if res < _TaskXCard.__PROC_TIMESPAN_DEVIATION_MIN_THRESHOLD:
            res = _TaskXCard.__PROC_TIMESPAN_DEVIATION_MIN_THRESHOLD
        res += timespan_
        return res

    def __CheckForReCalculation(self):
        if self.__isInvalid:
            return
        if not self.__bR:
            return
        if _TaskXCard._GetLcMonitorCyclicRunPauseTimespanMS() is None:
            return

        self.__bR = False
        if _TaskXCard._GetLcMonitorCyclicRunPauseTimespanMS() == _TaskXCard.__DEFAULT_LC_MONITOR_CYCLIC_RUN_PAUSE_TIMESPAN_MS:
            return
        self.__RecalculateRevisedAttributes()

    def __RecalculateRevisedAttributes(self):
        _tmp = self.__mp
        if _tmp <= 0:
            self.__rmp2 = 0
        else:
            if (_tmp-_TaskXCard.__PROC_TIMESPAN_DEVIATION_MIN_THRESHOLD) > _TaskXCard.__GetLcMonCyclicRunPauseTimespanMS():
                pass
            else:
                _bCC = False
                if _bCC:
                    _factor = -(-_TaskXCard.__GetLcMonCyclicRunPauseTimespanMS() // _tmp)
                else:
                    _factor = _TaskXCard.__GetLcMonCyclicRunPauseTimespanMS() // _tmp
                _tmp = _tmp * _factor
            self.__rmp2 = _TaskXCard.__GetDeviatedTimespan(_tmp)
