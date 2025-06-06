# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : gtimeout.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum      import Enum
from enum      import unique
from threading import TIMEOUT_MAX as _TIMEOUT_MAX
from typing    import Union

from _fw.fwssys.fwcore.logging           import logif
from _fw.fwssys.fwcore.logging           import vlogif
from _fw.fwssys.fwcore.base.strutil      import _StrUtil
from _fw.fwssys.fwcore.base.timeutil     import _TimeUtil
from _fw.fwssys.fwcore.base.util         import _Util
from _fw.fwssys.fwcore.types.aobject     import _AbsSlotsObject
from _fw.fwssys.fwerrh.fwerrorcodes      import _EFwErrorCode
from _fw.fwssys.fwerrh.logs.xcoexception import _XcoXcpRootBase
from _fw.fwssys.fwerrh.logs.xcoexception import _XcoBaseException

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

@unique
class _ETimeoutResolution(Enum):
    eTicksPerMSec  = 0  
    eTicksPerUSec  = 1  
    eTicksPerNSec  = 2  
    eTicksPerSec   = 3  

class _Timeout(_AbsSlotsObject):
    __TIMEOUT_MAX_TICKS = _TIMEOUT_MAX * _TimeUtil.TICKS_PER_SECOND

    @staticmethod
    def TimespanToTimeout(timeSpan_ : Union[int, float]):
        if isinstance(timeSpan_, _Timeout):
            if timeSpan_.__rns is None:
                res = None
                logif._LogErrorEC(_EFwErrorCode.UE_00029, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Timeout_TID_001).format(type(timeSpan_).__name__))
            elif timeSpan_.isInfiniteTimeout:
                res = _Timeout.CreateInfiniteTimeout()
            else:
                res = _Timeout.CreateTimeoutMS(timeSpan_.toMSec)
        elif not isinstance(timeSpan_, (int, float)):
            res = None
            logif._LogErrorEC(_EFwErrorCode.UE_00030, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Timeout_TID_002).format(type(timeSpan_).__name__))
        else:
            if timeSpan_ < 0:
                res = None
                logif._LogErrorEC(_EFwErrorCode.UE_00031, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Timeout_TID_003).format(type(timeSpan_).__name__))
            elif float(timeSpan_) == 0.0:
                res = _Timeout.CreateInfiniteTimeout()
            elif isinstance(timeSpan_, float):
                res = _Timeout.CreateTimeoutSec(timeSpan_)
            else:  
                res = _Timeout.CreateTimeoutMS(timeSpan_)
        return res

    @staticmethod
    def CreateInfiniteTimeout():
        res = _Timeout.__CreateTimeout(1, 1, _ETimeoutResolution.eTicksPerNSec, None)
        if res is None:
            logif._LogImplErrorEC(_EFwErrorCode.FE_00001, None)
        res.__ts         = 0
        res.__rns = 0
        return res

    @staticmethod
    def CreateTimeout(timeSpan_, timeoutRes_ : _ETimeoutResolution =None, clockTicksNSec_ : int =None):
        return _Timeout.__CreateTimeout(timeSpan_, 1, timeoutRes_, clockTicksNSec_)

    @staticmethod
    def CreateTimeoutMS(timeSpanMS_, clockTicksNSec_ : int =None):
        return _Timeout.__CreateTimeout(timeSpanMS_, 1, _ETimeoutResolution.eTicksPerMSec, clockTicksNSec_)

    @staticmethod
    def CreateTimeoutUS(timeSpanUS_, clockTicksNSec_ : int =None):
        return _Timeout.__CreateTimeout(timeSpanUS_, 1, _ETimeoutResolution.eTicksPerUSec, clockTicksNSec_)

    @staticmethod
    def CreateTimeoutNS(timeSpanNS_, clockTicksNSec_ : int =None):
        return _Timeout.__CreateTimeout(timeSpanNS_, 1, _ETimeoutResolution.eTicksPerNSec, clockTicksNSec_)

    @staticmethod
    def CreateTimeoutSec(timeSpanSec_, clockTicksNSec_ : int =None):
        return _Timeout.__CreateTimeout(timeSpanSec_, 1, _ETimeoutResolution.eTicksPerSec, clockTicksNSec_)

    @staticmethod
    def CreateCyclicTimeout(timeSpan_, cycleTimes_ : int =0, timeoutRes_ : _ETimeoutResolution =None, clockTicksNSec_ : int =None):
        return _Timeout.__CreateTimeout(timeSpan_, cycleTimes_, timeoutRes_, clockTicksNSec_, createCyclic_=True)

    @staticmethod
    def CreateCyclicTimeoutMS(timeSpanMS_, cycleTimes_ : int =0, clockTicksNSec_ : int =None):
        return _Timeout.__CreateTimeout(timeSpanMS_, cycleTimes_, _ETimeoutResolution.eTicksPerMSec, clockTicksNSec_, createCyclic_=True)

    @staticmethod
    def CreateCyclicTimeoutUS(timeSpanUS_, cycleTimes_ : int =0, clockTicksNSec_ : int =None):
        return _Timeout.__CreateTimeout(timeSpanUS_, cycleTimes_, _ETimeoutResolution.eTicksPerUSec, clockTicksNSec_, createCyclic_=True)

    @staticmethod
    def CreateCyclicTimeoutNS(timeSpanNS_, cycleTimes_ : int =0, clockTicksNSec_ : int =None):
        return _Timeout.__CreateTimeout(timeSpanNS_, cycleTimes_, _ETimeoutResolution.eTicksPerNSec, clockTicksNSec_, createCyclic_=True)

    @staticmethod
    def CreateCyclicTimeoutSec(timeSpanSec_, cycleTimes_ : int =0, clockTicksNSec_ : int =None):
        return _Timeout.__CreateTimeout(timeSpanSec_, cycleTimes_, _ETimeoutResolution.eTicksPerSec, clockTicksNSec_, createCyclic_=True)

    @staticmethod
    def GetBaseResolution():
        return _ETimeoutResolution.eTicksPerNSec

    @staticmethod
    def IsFiniteTimeout(timeout_, bThrowx_ =True) -> bool:
        return _Timeout.IsTimeout(timeout_, bThrowx_) and timeout_.toNSec != 0

    @staticmethod
    def IsInfiniteTimeout(timeout_, bThrowx_ =True) -> bool:
        return _Timeout.IsTimeout(timeout_, bThrowx_) and timeout_.toNSec == 0

    @staticmethod
    def IsTimeout(timeout_, bThrowx_ =True) -> bool:
        res = isinstance(timeout_, _Timeout)
        if not res and bThrowx_:
            logif._LogBadUseEC(_EFwErrorCode.FE_00083, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Timeout_TID_004).format(_Timeout.__name__, _Util.TypeName(timeout_)))
        return res

    __slots__ = [ '__cc' , '__ns' , '__ts' , '__res' , '__ccc' , '__rns' ]

    def __init__(self, timeSpan_, cycleTimes_ : int =1, timeoutRes_ : _ETimeoutResolution =None, clockTicksNSec_ : int =None):
        self.__cc  = None
        self.__ns  = None
        self.__ts  = None
        self.__ccc = None
        self.__res = None
        self.__rns = None
        super().__init__()

        self.__res          = None
        _r1, _r2, _r3, _r4, _r5 = _Timeout.__EvaluateParams(timeSpan_, cycleTimes_, timeoutRes_, clockTicksNSec_)
        if _r1 is None:
            self.CleanUp()
        else:
            self.__cc  = _r4
            self.__ns  = _r5
            self.__ts  = _r2
            self.__ccc = 0
            self.__res = _r3
            self.__rns = _r1

    def __eq__(self, rhs_):
        if not _Util.IsInstance(rhs_, [_Timeout, int, float], bThrowx_=False):
            return False
        return self.__Compare(rhs_) == 0

    def __ne__(self, rhs_):
        if not _Util.IsInstance(rhs_, [_Timeout, int, float], bThrowx_=False):
            return True
        return self.__Compare(rhs_) != 0

    def __lt__(self, rhs_):
        if not _Util.IsInstance(rhs_, [_Timeout, int, float], bThrowx_=False):
            return False
        return self.__Compare(rhs_) == -1

    def __le__(self, rhs_):
        if not _Util.IsInstance(rhs_, [_Timeout, int, float], bThrowx_=False):
            return False
        _cmp = self.__Compare(rhs_)
        return _cmp == -1 or _cmp == 0

    def __gt__(self, rhs_):
        if not _Util.IsInstance(rhs_, [_Timeout, int, float], bThrowx_=False):
            return False
        return self.__Compare(rhs_) == 1

    def __ge__(self, rhs_):
        if not _Util.IsInstance(rhs_, [_Timeout, int, float], bThrowx_=False):
            return False
        _cmp = self.__Compare(rhs_)
        return _cmp == 1 or _cmp == 0

    @property
    def timeSpan(self):
        return self.__ts

    @property
    def resolution(self):
        return self.__res

    @property
    def clockTicksNS(self):
        return self.__ns

    @property
    def cycleTimes(self):
        return self.__cc

    @property
    def consumedCycleTimes(self):
        return self.__ccc 

    @property
    def remainingCycleTimes(self):
        res = 0
        if self.__cc != 0:
            res = self.__cc - self.__ccc
        return res

    @property
    def toMSec(self):
        return int(self.__rns / _TimeUtil.TICKS_PER_MSECOND)

    @property
    def toUSec(self):
        return int(self.__rns / _TimeUtil.TICKS_PER_USECOND)

    @property
    def toNSec(self):
        return int(self.__rns / _TimeUtil.TICKS_PER_NSECOND)

    @property
    def toSec(self):
        return float(float(self.__rns) / _TimeUtil.TICKS_PER_SECOND)

    @property
    def toString(self):
        return self.__ToString(self.resolution)

    @property
    def toStringMS(self):
        return self.__ToString(_ETimeoutResolution.eTicksPerMSec)

    @property
    def toStringUS(self):
        return self.__ToString(_ETimeoutResolution.eTicksPerUSec)

    @property
    def toStringNS(self):
        return self.__ToString(_ETimeoutResolution.eTicksPerNSec)

    @property
    def toStringSec(self):
        return self.__ToString(_ETimeoutResolution.eTicksPerSec)

    @property
    def isFiniteTimeout(self):
        return self.__rns > 0

    @property
    def isInfiniteTimeout(self):
        return self.__rns == 0

    @property
    def isCyclic(self):
        return self.__cc != 1

    @property
    def isInfiniteCyclic(self):
        return self.__cc == 0

    def IsExpired(self, clockTicksNSec_ : int =None):
        if not isinstance(clockTicksNSec_, int) or clockTicksNSec_ < 0:
            clockTicksNSec_ = _TimeUtil.GetCurTicksNS()
        if clockTicksNSec_ <= self.__ns:
            return True
        return (clockTicksNSec_ - self.__ns) >= self.toNSec

    def IsNotExpired(self, clockTicksNSec_ : int =None):
        return not _Timeout.IsExpired(self, clockTicksNSec_)

    def IncrementConsumedCycleTimes(self):
        if self.__cc == 0 or self.__ccc < self.__cc:
            self.__ccc += 1

    def ResetConsumedCycleTimes(self, consumedCycleTimes_ =0):
        if consumedCycleTimes_ < 0:
            consumedCycleTimes_ = 0
        if self.__cc != 0 and consumedCycleTimes_ > self.cycleTimes:
            consumedCycleTimes_ = self.cycleTimes
        self.__ccc = consumedCycleTimes_

    def UpdateClock(self, clockTicksNSec_ : int =None, bUpdateTimeSpan_ =False):
        if not isinstance(clockTicksNSec_, int) or clockTicksNSec_ < 0:
            clockTicksNSec_ = _TimeUtil.GetCurTicksNS()

        if bUpdateTimeSpan_:
            if self.resolution != _ETimeoutResolution.eTicksPerNSec:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00040)
                return 0
            else:
                self.__ts -= clockTicksNSec_ - self.__ns
                if self.__ts < 0:
                    self.__ts = 0
                self.__rns = self.__ts

        self.__ns = clockTicksNSec_
        return self.__ns

    def SetTimeSpan(self, timeSpan_, clockTicksNSec_ : int =None):
        if self.isFiniteTimeout:
            logif._LogBadUseEC(_EFwErrorCode.FE_00084, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Timeout_TID_005))
        self.Reconfigure(timeSpan_, cycleTimes_=self.cycleTimes, timeoutRes_=self.resolution, clockTicksNSec_=clockTicksNSec_)

    def Clone(self, clockTicksNSec_ : int =None):
        if self.isInfiniteTimeout:
            return _Timeout.CreateInfiniteTimeout()
        else:
            return _Timeout.__CreateTimeout( self.timeSpan, self.cycleTimes, self.resolution, clockTicksNSec_)

    def Reconfigure(self, timeSpan_, cycleTimes_ : int =None, timeoutRes_ : _ETimeoutResolution =None, clockTicksNSec_ : int =None):
        if self.isInfiniteTimeout:
            logif._LogBadUseEC(_EFwErrorCode.FE_00085, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Timeout_TID_006))
            return False

        if cycleTimes_ is None:
            cycleTimes_ = self.cycleTimes
        if timeoutRes_ is None:
            timeoutRes_ = self.resolution

        _r1, _r2, _r3, _r4, _r5 = _Timeout.__EvaluateParams(timeSpan_, cycleTimes_, timeoutRes_, clockTicksNSec_)
        if _r1 is None:
            return False

        self.__cc  = _r4
        self.__ns  = _r5
        self.__ts  = _r2
        self.__ccc = 0
        self.__res = _r3
        self.__rns = _r1
        return True

    def _ToString(self, tres_ =None, bVerbose_ =False):
        if tres_ is None:
            tres_ = self.resolution

        if bVerbose_:
            if self.isInfiniteCyclic:
                res = '_Timeout: (resolution, timeSpan, cycleTimes)=({}, {}, {})'.format(tres_, self.__ToString(tres_), self.cycleTimes)
            else:
                res = '_Timeout: (resolution, timeSpan, cycleTimes, remainingCycleTimes)=({}, {}, {}, {})'.format(
                    tres_, self.__ToString(tres_), self.cycleTimes, self.remainingCycleTimes)
        else:
            res = '_Timeout: (resolution, timeSpan)=({}, {})'.format(tres_, self.__ToString(tres_))
        return res

    def _CleanUp(self):
        self.__ts  = None
        self.__res = None
        self.__cc  = None
        self.__ns  = None
        self.__rns = None
        self.__ccc = None

    @staticmethod
    def __CreateTimeout(timeSpan_, cycleTimes_, timeoutRes_, clockTicksNSec_, createCyclic_ =False):
        if createCyclic_:
            if cycleTimes_ == 1:
                logif._LogErrorEC(_EFwErrorCode.UE_00032, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Timeout_TID_007))
                return None
        elif cycleTimes_ != 1:
            logif._LogErrorEC(_EFwErrorCode.UE_00033, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Timeout_TID_008).format(cycleTimes_))
            return None

        res = None
        try:
            res = _Timeout(timeSpan_, cycleTimes_=cycleTimes_, timeoutRes_=timeoutRes_, clockTicksNSec_=clockTicksNSec_)
        except _XcoXcpRootBase as _xcp:
            logif._PrintException(_xcp)
        except Exception as _xcp:
            logif._PrintException(_XcoBaseException(_xcp, tb_=logif._GetFormattedTraceback()))
        finally:
            if res is None:
                pass
            elif res.__rns is None:
                res.CleanUp()
                res = None
        return res

    @staticmethod
    def __EvaluateParams(timeSpan_, cycleTimes_, timeoutRes_ =None, clockTicksNSec_ =None):
        _bOK, _r1, _r3, _r4 = True, -1, timeoutRes_, clockTicksNSec_

        if _r3 is None:
            _r3 = _ETimeoutResolution.eTicksPerMSec
        if _r4 is None:
            _r4 = _TimeUtil.GetCurTicksNS()

        _bOK &= _Util.IsInstance(_r3, _ETimeoutResolution, bThrowx_=True)
        _bOK &= _Util.IsInstance(_r4, int, bThrowx_=True)
        _bOK &= _Util.CheckMinRange(_r4, 0, bThrowx_=True)
        _bOK &= _Util.IsInstance(cycleTimes_, int, bThrowx_=True)
        _bOK &= _Util.CheckMinRange(cycleTimes_, 0, bThrowx_=True)
        if _bOK:
            _r1   = _Timeout.__TimeSpanToTicks(timeSpan_, _r3)
            _bOK = _r1 > -1
            _bOK &= _Util.CheckMaxRange(_r1, _Timeout.__TIMEOUT_MAX_TICKS, bThrowx_=True)

        if not _bOK:
            _r1, timeSpan_, _r3, cycleTimes_, _r4 = None, None, None, None, None
        return _r1, timeSpan_, _r3, cycleTimes_, _r4

    @staticmethod
    def __TimeSpanToTicks(timeSpan_, timeoutRes_):
        if _Timeout.GetBaseResolution() != _ETimeoutResolution.eTicksPerNSec:
            logif._LogImplErrorEC(_EFwErrorCode.FE_00570, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Timeout_TID_009))

        if not _Util.IsInstance(timeSpan_, [int, float, str], bThrowx_=False):
            logif._LogBadUseEC(_EFwErrorCode.FE_00086, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Timeout_TID_010).format(_Util.TypeName(timeSpan_)))
            return -1

        if isinstance(timeSpan_, str):
            try:
                _base = 10 if not _StrUtil.IsHexString(timeSpan_) else 16
                timeSpan_ = int(timeSpan_, _base)
            except ValueError as _xcp:
                logif._LogBadUseEC(_EFwErrorCode.FE_00087, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Timeout_TID_011).format(timeSpan_, timeoutRes_.name))
                return -1

        if not _Util.CheckMinRange(timeSpan_, 1, bThrowx_=True):
            logif._LogBadUseEC(_EFwErrorCode.FE_00088, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Timeout_TID_012).format(timeSpan_, timeoutRes_.name))
            return -1

        if timeoutRes_ == _ETimeoutResolution.eTicksPerSec:
            _ticksFactor = _TimeUtil.TICKS_PER_SECOND
        elif timeoutRes_ == _ETimeoutResolution.eTicksPerMSec:
            _ticksFactor = _TimeUtil.TICKS_PER_MSECOND
        elif timeoutRes_ == _ETimeoutResolution.eTicksPerUSec:
            _ticksFactor = _TimeUtil.TICKS_PER_USECOND
        elif timeoutRes_ == _ETimeoutResolution.eTicksPerNSec:
            _ticksFactor = _TimeUtil.TICKS_PER_NSECOND
        else:
            logif._LogImplErrorEC(_EFwErrorCode.FE_00571, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Timeout_TID_013).format(timeoutRes_))
            return -1
        return int(timeSpan_ * _ticksFactor)

    def __Compare(self, rhs_):
        _Util.IsInstance(rhs_, [_Timeout, int, float])

        if not isinstance(rhs_, _Timeout):
            _rhsNS = rhs_
        else:
            _rhsNS = rhs_.toNSec

        res = 0
        if self.toNSec < _rhsNS:
            res = -1
        elif self.toNSec > _rhsNS:
            res = 1
        return res

    def __ToString(self, eTimeRes_):
        if eTimeRes_ is None:
            return None
        if eTimeRes_ == _ETimeoutResolution.eTicksPerMSec:
            _trStr = 'ms'
            _ts = self.toMSec
        elif eTimeRes_ == _ETimeoutResolution.eTicksPerUSec:
            _trStr = 'us'
            _ts = self.toUSec
        elif eTimeRes_ == _ETimeoutResolution.eTicksPerNSec:
            _trStr = 'ns'
            _ts = self.toNSec
        elif eTimeRes_ == _ETimeoutResolution.eTicksPerSec:
            _trStr = 's'
            _ts = self.toSec
        else:
            logif._LogImplErrorEC(_EFwErrorCode.FE_00002, None)
            return None
        return _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_013).format(_ts, _trStr)
