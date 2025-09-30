# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : timeutil.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

import sys
import time
from datetime import datetime  as _PyDateTime
from datetime import timedelta as _PyTimeDelta

from _fw.fwssys.fwcore.logging           import vlogif
from _fw.fwssys.fwcore.base.util         import _Util
from _fw.fwssys.fwcore.types.aobject     import _AbsSlotsObject
from _fw.fwssys.fwcore.types.commontypes import _FwEnum
from _fw.fwssys.fwcore.types.commontypes import _CommonDefines
from _fw.fwssys.fwerrh.fwerrorcodes      import _EFwErrorCode

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _TimeUtil:
    SEC_PER_HOUR   = 60*60
    SEC_PER_DAY    = 24*SEC_PER_HOUR
    USEC_PER_SEC   = 10**6
    USEC_PER_MSEC  = 10**3
    MSEC_PER_SEC   = 10**3

    TICKS_PER_SECOND  = 10**9
    TICKS_PER_MSECOND = 10**6
    TICKS_PER_USECOND = 10**3
    TICKS_PER_NSECOND = 1

    @staticmethod
    def GetCurTicksMS():
        return int(time.time_ns() // _TimeUtil.TICKS_PER_MSECOND)

    @staticmethod
    def GetCurTicksUS():
        return int(time.time_ns() // _TimeUtil.TICKS_PER_USECOND)

    @staticmethod
    def GetCurTicksNS():
        return int(time.time_ns() // _TimeUtil.TICKS_PER_NSECOND)

    @staticmethod
    def GetCurTicksSEC():
        return float(time.time_ns() / _TimeUtil.TICKS_PER_SECOND)

    @staticmethod
    def GetTicksMS(timespanMS_):
        return 0 if timespanMS_ < 0 else int(timespanMS_ * _TimeUtil.TICKS_PER_MSECOND)

    @staticmethod
    def GetTicksUS(timespanUS_):
        return 0 if timespanUS_ < 0 else int(timespanUS_ * _TimeUtil.TICKS_PER_USECOND)

    @staticmethod
    def GetTicksNS(timespanNS_):
        return 0 if timespanNS_ < 0 else int(timespanNS_ * _TimeUtil.TICKS_PER_NSECOND)

    @staticmethod
    def GetTicksSEC(timespanSec_):
        return 0.0 if timespanSec_ < 0.0 else int(timespanSec_ * _TimeUtil.TICKS_PER_SECOND)

    @staticmethod
    def GetTimestamp(bMS_ =True) -> str:
        if _PyDateTime.__name__ not in sys.modules:
            return _FwTDbEngine.GetText(_EFwTextID.eTimeUtil_GetTimeStamp_FmrStr_01)

        tstamp_ = _PyDateTime.now().isoformat(timespec='milliseconds')
        return tstamp_[tstamp_.index('T')+1:]

    @staticmethod
    def GetHash(*args_):
        res = 0
        for aa in args_:
            res = hash(str(res)+str(aa))
        res = hash(str(res)+str(_TimeUtil.GetCurTicksNS())+str(_TimeUtil.GetCurTicksSEC()))
        return res

class _TimeAlert:
    def __init__(self, alertTimespanNS_):
        _Util.IsInstance(alertTimespanNS_, int)
        _Util.CheckMinRange(alertTimespanNS_, 1)

        self.__ticks = None
        self.__alertTimespanNS = alertTimespanNS_

    def CheckAlert(self):
        if self.__ticks is None:
            self.__ticks = _TimeUtil.GetCurTicksNS()
            return False

        _curTicks = _TimeUtil.GetCurTicksNS()
        _diff = int(_curTicks - self.__ticks)
        res = _diff >= self.__alertTimespanNS
        if res:
            self.__ticks = _curTicks
        return res

class _TimeParts(_AbsSlotsObject):
    __slots__ = [ '__bTD' , '__dd' , '__hh' , '__mm' , '__ss' , '__ms' ]

    def __init__(self, timeDelta_ : _PyTimeDelta =None, dateTime_ : _PyDateTime =None):
        super().__init__()
        self.__dd  = None
        self.__hh  = None
        self.__mm  = None
        self.__ss  = None
        self.__ms  = None
        self.__bTD = None

        if timeDelta_ is None:
            if dateTime_ is None:
                dateTime_ = _PyDateTime.now()
            elif not isinstance(dateTime_, _PyDateTime):
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00041)
                self.CleanUp()
                return

            self.__dd  = 0
            self.__hh  = dateTime_.hour
            self.__mm  = dateTime_.minute
            self.__ss  = dateTime_.second
            self.__ms = dateTime_.microsecond // 1000
            self.__bTD = False
            return

        if not isinstance(timeDelta_, _PyTimeDelta):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00042)
            self.CleanUp()
            return

        _td = timeDelta_

        _dd = _td.days
        _ms = _td.microseconds // 1000

        _tt  = _td.seconds
        _ss  = _tt % 60
        _tt -= _ss

        _mm = _tt // 60
        _hh = _mm // 60
        _mm = _mm % 60

        self.__dd  = _dd
        self.__hh  = _hh
        self.__mm  = _mm
        self.__ss  = _ss
        self.__ms  = _ms
        self.__bTD = True

    def __str__(self):
        return self._ToString()

    @property
    def isValid(self):
        return self.__bTD is not None

    @property
    def isDateTime(self):
        return self.isValid and not self.__bTD

    @property
    def isTimeDelta(self):
        return self.isValid and self.__bTD

    @property
    def tpDD(self):
        return self.__dd

    @property
    def tpHH(self):
        return self.__hh

    @property
    def tpMM(self):
        return self.__mm

    @property
    def tpSS(self):
        return self.__ss

    @property
    def tpMS(self):
        return self.__ms

    def _ToString(self):
        if not self.isValid:
            return None

        if self.__dd > 0:
            res = _FwTDbEngine.GetText(_EFwTextID.eTimeParts_ToString_01).format(self.__dd, self.__hh, self.__mm, self.__ss, self.__ms)
        else:
            res = _FwTDbEngine.GetText(_EFwTextID.eTimeParts_ToString_02).format(self.__hh, self.__mm, self.__ss, self.__ms)

            if self.isTimeDelta:
                while res.startswith('00:'):
                    res = res[3:]
                if res.startswith('0'):
                    if res[1] != _CommonDefines._CHAR_SIGN_DOT and res[1] != _CommonDefines._CHAR_SIGN_COLON:
                        res = res[1:]
        return res

    def _CleanUp(self):
        self.__dd  = None
        self.__hh  = None
        self.__mm  = None
        self.__ss  = None
        self.__ms  = None
        self.__bTD = None

class _TimeDelta(_AbsSlotsObject):
    __slots__ = [ '__td' , '__tp' ]

    def __init__( self, timeDelta_ : _PyTimeDelta =None
                , days_ =0, seconds_ =0, microseconds_ =0, milliseconds_ =0, minutes_ =0, hours_ =0, weeks_ =0):
        self.__td = None
        self.__tp = None
        super().__init__()

        _lstParams      = [ days_, seconds_, microseconds_, milliseconds_, minutes_, hours_, weeks_ ]
        _bNonZeroOffset = False
        for _ee in _lstParams:
            if not isinstance(_ee, (int, float)):
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00043)
                self.CleanUp()
                return
            _bNonZeroOffset = _bNonZeroOffset or float(_ee) != 0.0

        if timeDelta_ is not None:
            if not isinstance(timeDelta_, _PyTimeDelta):
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00044)
                self.CleanUp()
                return

        _offset = None
        if (timeDelta_ is None) or _bNonZeroOffset:
            _offset = _PyTimeDelta(days=days_, seconds=seconds_, microseconds=microseconds_, milliseconds=milliseconds_, minutes=minutes_, hours=hours_, weeks=weeks_)

        if timeDelta_ is None:
            _td = _offset
        else:
            _td = timeDelta_

            if _offset is not None:
                _td += _offset

        self.__td = _td
        self.__tp = _TimeParts(self.__td)

    def __str__(self):
        return self._ToString()

    def __add__(self, other_):
        if not self.__CheckArithOperation(other_):
            return None

        _td = other_
        if isinstance(other_, _TimeDelta):
            _td = other_.pyTimeDelta

        _td = self.__td + _td
        return _TimeDelta(timeDelta_=self.__td+_td)

    def __sub__(self, other_):
        if not self.__CheckArithOperation(other_):
            return None

        _td = other_
        if isinstance(other_, _TimeDelta):
            _td = other_.pyTimeDelta

        _td = self.__td + _td
        return _TimeDelta(timeDelta_=self.__td-_td)

    def __neg__(self):
        if not self.__CheckArithOperation(None, bIgnoreOther_=True):
            return None
        return _TimeDelta(timeDelta_=-self.__td)

    def __abs__(self):
        if not self.__CheckArithOperation(None, bIgnoreOther_=True):
            return None
        return _TimeDelta(timeDelta_=abs(self.__td))

    @property
    def isValid(self):
        return self.__td is not None

    @property
    def totalSEC(self) -> float:
        return None if not self.isValid else self.__totalMicroSec / _TimeUtil.USEC_PER_SEC

    @property
    def totalMS(self) -> int:
        return None if not self.isValid else self.__totalMicroSec // _TimeUtil.USEC_PER_MSEC

    @property
    def totalUS(self) -> int:
        return None if not self.isValid else self.__totalMicroSec

    @property
    def timeParts(self) -> _TimeParts:
        return self.__tp

    @property
    def pyTimeDelta(self) -> _PyTimeDelta:
        return self.__td

    def _ToString(self):
        return None if not self.isValid else str(self.__tp)

    def _CleanUp(self):
        if self.__tp is not None:
            self.__tp.CleanUp()
        self.__tp = None
        self.__td = None

    @property
    def __totalMicroSec(self) -> int:
        _td = self.__td
        return (_td.days * _TimeUtil.SEC_PER_DAY + _td.seconds) * _TimeUtil.USEC_PER_SEC + _td.microseconds

    def __CheckArithOperation(self, other_, bIgnoreOther_ =False):
        if not self.isValid:
            return False
        if bIgnoreOther_:
            return True

        _bPyTimeDelta = False
        _bTimeDelta   = isinstance(other_, _TimeDelta)
        if not _bTimeDelta:
            _bPyTimeDelta = isinstance(other_, _PyTimeDelta)
        elif not other_.isValid:
            _bTimeDelta = False

        res = _bTimeDelta or _bPyTimeDelta
        if not res:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00045)
        return res

class _StopWatch(_AbsSlotsObject):
    __slots__ = [ '__st' , '__sp' , '__td' ]

    def __init__(self, usTimeTicksStart_ : int =None, usTimeTicksStop_ : int=None):
        super().__init__()
        self.__sp = None
        self.__st = None
        self.__td = None

        if usTimeTicksStop_ is not None:
            if not isinstance(usTimeTicksStop_, int):
                self.CleanUp()
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00046)
                return

        if usTimeTicksStart_ is not None:
            if not isinstance(usTimeTicksStart_, int):
                self.CleanUp()
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00047)
                return
        else:
            usTimeTicksStart_ = _TimeUtil.GetCurTicksUS()
        self.__st = usTimeTicksStart_

        if usTimeTicksStop_ is not None:
            if self.__Stop(usTimeTicksStop_, False) is None:
                self.CleanUp()

    @property
    def isValid(self):
        return not self.__isInvalid

    @property
    def startTimeTicksUS(self) -> int:
        return self.__st

    @property
    def stopTimeTicksUS(self) -> int:
        return self.__sp

    @property
    def timeDelta(self) -> _TimeDelta:
        return self.__td

    def Stop(self, usTimeTicksStop_ : int =None) -> _TimeDelta:
        return self.__Stop(usTimeTicksStop_, False)

    def StopRelative(self, usTimeTicksStop_ : int =None) -> _TimeDelta:
        return self.__Stop(usTimeTicksStop_, True)

    def Restart(self, usTimeTicksStart_ : int =None, usTimeTicksStop_ : int=None) -> bool:
        if self.__isInvalid:
            return False
        if usTimeTicksStop_ is not None:
            if not isinstance(usTimeTicksStop_, int):
                self.CleanUp()
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00048)
                return False

        if usTimeTicksStart_ is not None:
            if not isinstance(usTimeTicksStart_, int):
                self.CleanUp()
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00049)
                return False
        else:
            usTimeTicksStart_ = _TimeUtil.GetCurTicksUS()

        if self.__td is not None:
            self.__td.CleanUp()
        self.__sp = None
        self.__st = usTimeTicksStart_
        self.__td = None

        if usTimeTicksStop_ is not None:
            self.__Stop(usTimeTicksStop_, False)
            res = self.__td is not None
        else:
            res = True
        return res

    def _ToString(self):
        if self.__isInvalid:
            return None

        res = _FwTDbEngine.GetText(_EFwTextID.eStopWatch_ToString_01).format(self.__st)
        if self.__sp is not None:
            res += _FwTDbEngine.GetText(_EFwTextID.eStopWatch_ToString_02).format(self.__sp, self.__td)
        return res

    def _CleanUp(self):
        if self.__isInvalid:
            return
        if self.__td is not None:
            self.__td.CleanUp()
        self.__sp = None
        self.__st = None
        self.__td = None

    @property
    def __isInvalid(self):
        return self.__st is None

    def __Stop(self, usTimeTicksStop_ : int, bRelative_ : bool) -> _TimeDelta:
        if self.__isInvalid:
            return None
        if usTimeTicksStop_ is not None:
            if not isinstance(usTimeTicksStop_, int):
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00050)
                return None
        else:
            usTimeTicksStop_ = _TimeUtil.GetCurTicksUS()

        if bRelative_:
            _usTimeTicksRef = self.__st if self.__sp is None else self.__sp
        else:
            _usTimeTicksRef = self.__st

        if usTimeTicksStop_ < _usTimeTicksRef:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00051)
            return None

        if self.__td is not None:
            self.__td.CleanUp()
        self.__sp = usTimeTicksStop_
        self.__td = _TimeDelta(microseconds_=usTimeTicksStop_ - _usTimeTicksRef)
        return self.__td

class _KpiLogBook(_AbsSlotsObject):
    __slots__ = [ '__lb' , '__sid' ]

    __SUP_KPI = None

    def __init__(self, eStartKPI_ : _FwEnum, usTimeTicksStart_: int = None):
        self.__lb  = None
        self.__sid = None
        super().__init__()

        self.__lb = dict()

        startTime_ = self.AddKPI(eStartKPI_, usTimeTicksStart_)
        if startTime_ is None:
            self.CleanUp()
        else:
            self.__sid = eStartKPI_

    @property
    def isValid(self):
        return not self.__isInvalid

    @property
    def startKPI(self):
        return None if self.__isInvalid else self.__sid

    def IsAddedKPI(self, eKPI_ : _FwEnum) -> bool:
        return False if self.__isInvalid else isinstance(eKPI_, _FwEnum) and (eKPI_ in self.__lb)

    def AddKPI(self, eKPI_ : _FwEnum, usTimeTicksKPI_ : int =None, bForceOverwrite_ =False) -> int:
        if self.__isInvalid:
            return None

        if not isinstance(eKPI_, _FwEnum):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00052)
            return None
        if (eKPI_ in self.__lb) and not bForceOverwrite_:
            return self.__lb[eKPI_]
        if usTimeTicksKPI_ is not None:
            if not isinstance(usTimeTicksKPI_, int):
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00053)
                return None
            res = usTimeTicksKPI_
        else:
            res = _TimeUtil.GetCurTicksUS()

        self.__lb[eKPI_] = res
        return res

    def GetKpiTimeDelta(self, rhsKPI_: _FwEnum, lhsKPI_: _FwEnum =None) -> _TimeDelta:
        if self.__isInvalid:
            return None

        if not (isinstance(rhsKPI_, _FwEnum) and (rhsKPI_ in self.__lb)):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00054)
            return None
        if lhsKPI_ is not None:
            if not (isinstance(lhsKPI_, _FwEnum) and (lhsKPI_ in self.__lb)):
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00055)
                return None
        else:
            lhsKPI_ = self.startKPI

        _rhsTime = self.__lb[rhsKPI_]
        _lhsTime = self.__lb[lhsKPI_]

        if _lhsTime > _rhsTime:
            _lhsTime, _rhsTime = _rhsTime, _lhsTime
        _sw = _StopWatch(_lhsTime, _rhsTime)
        if not _sw.isValid:
            return None

        res = _TimeDelta(timeDelta_=_sw.timeDelta.pyTimeDelta)
        _sw.CleanUp()
        return res

    @staticmethod
    def _GetStartupKPI():
        return _KpiLogBook.__SUP_KPI

    @staticmethod
    def _CreateStartupKPI(eStartKPI_ : _FwEnum):
        res = _KpiLogBook.__SUP_KPI
        if res is None:
            res = _KpiLogBook(eStartKPI_)
            if not res.isValid:
                res.CleanUp()
                res = None
            else:
                _KpiLogBook.__SUP_KPI = res
        return res

    def _ToString(self):
        if self.__isInvalid:
            return _CommonDefines._STR_EMPTY

        _fmtStr = f'{_CommonDefines._STR_TIME_UNIT_MS}{_CommonDefines._CHAR_SIGN_LF}{_CommonDefines._CHAR_SIGN_TAB}'
        _fmtStr = _FwTDbEngine.GetText(_EFwTextID.eKpiLogBook_ToString_01) + _fmtStr

        _sortedLB = dict(sorted(self.__lb.items(), key=lambda t: t[1], reverse=False))
        _keys     = list(_sortedLB.keys())

        res = _CommonDefines._CHAR_SIGN_TAB
        for _ii in range(len(_keys)):
            if _ii == 0:
                continue

            _kk, _pkk = _keys[_ii], _keys[_ii-1]
            _vv, _pvv = _sortedLB[_kk], _sortedLB[_pkk]
            _sw  = _StopWatch(_pvv, _vv)
            res += _fmtStr.format(_pkk.compactName, _kk.compactName, _sw.timeDelta.totalMS)
            _sw.CleanUp()
        return res.rstrip()

    def _CleanUp(self):
        if self.__isInvalid:
            return

        self.__lb.clear()
        self.__lb  = None
        self.__sid = None

    @property
    def __isInvalid(self):
        return self.__lb is None
