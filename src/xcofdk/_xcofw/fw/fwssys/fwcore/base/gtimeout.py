# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : gtimeout.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum      import Enum
from enum      import unique
from threading import TIMEOUT_MAX as _TIMEOUT_MAX

from xcofdk._xcofw.fw.fwssys.fwcore.logging              import logif
from xcofdk._xcofw.fw.fwssys.fwcore.logging              import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.logging.xcoexception import _XcoExceptionRoot
from xcofdk._xcofw.fw.fwssys.fwcore.logging.xcoexception import _XcoBaseException
from xcofdk._xcofw.fw.fwssys.fwcore.base.listutil        import _ListUtil
from xcofdk._xcofw.fw.fwssys.fwcore.base.strutil         import _StrUtil
from xcofdk._xcofw.fw.fwssys.fwcore.base.timeutil        import _TimeUtil
from xcofdk._xcofw.fw.fwssys.fwcore.base.util            import _Util
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject        import _AbstractSlotsObject

from xcofdk._xcofw.fw.fwssys.fwerrh.fwerrorcodes import _EFwErrorCode

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine

@unique
class _ETimeoutResolution(Enum):
    eTicksPerMSec  = 0  
    eTicksPerUSec  = 1  
    eTicksPerNSec  = 2  
    eTicksPerSec   = 3  

class _Timeout(_AbstractSlotsObject):

    __TIMEOUT_MAX_TICKS = _TIMEOUT_MAX * _TimeUtil.TICKS_PER_SECOND

    @staticmethod
    def TimespanToTimeout(timeSpan_ : [int, float]):

        if isinstance(timeSpan_, _Timeout):
            if timeSpan_.__remainingTicksNS is None:
                res = None
                logif._LogErrorEC(_EFwErrorCode.UE_00029, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Timeout_TextID_001).format(type(timeSpan_).__name__))
            elif timeSpan_.isInfiniteTimeout:
                res = _Timeout.CreateInfiniteTimeout()
            else:
                res = _Timeout.CreateTimeoutMS(timeSpan_.toMSec)
        elif not isinstance(timeSpan_, (int, float)):
            res = None
            logif._LogErrorEC(_EFwErrorCode.UE_00030, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Timeout_TextID_002).format(type(timeSpan_).__name__))
        else:
            if timeSpan_ < 0:
                res = None
                logif._LogErrorEC(_EFwErrorCode.UE_00031, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Timeout_TextID_003).format(type(timeSpan_).__name__))
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
        res.__timeSpan         = 0
        res.__remainingTicksNS = 0
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
            logif._LogBadUseEC(_EFwErrorCode.FE_00083, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Timeout_TextID_004).format(_Timeout.__name__, _Util.TypeName(timeout_)))
        return res

    __slots__ = [ '__timeSpan' , '__remainingTicksNS' , '__resolution' , '__cycleTimes' , '__clockTicksNSec' , '__consumedCycleTimes' ]

    def __init__(self, timeSpan_, cycleTimes_ : int =1, timeoutRes_ : _ETimeoutResolution =None, clockTicksNSec_ : int =None):

        self.__timeSpan           = None
        self.__resolution         = None
        self.__cycleTimes         = None
        self.__clockTicksNSec     = None
        self.__remainingTicksNS   = None
        self.__consumedCycleTimes = None
        super().__init__()

        self.__resolution          = None
        r1, r2, r3, r4, r5 = _Timeout.__EvaluateParams(timeSpan_, cycleTimes_, timeoutRes_, clockTicksNSec_)
        if r1 is None:
            self.CleanUp()
        else:
            self.__timeSpan           = r2
            self.__resolution         = r3
            self.__cycleTimes         = r4
            self.__clockTicksNSec     = r5
            self.__remainingTicksNS   = r1
            self.__consumedCycleTimes = 0

    def __eq__(self, other_):
        if not _Util.IsInstance(other_, [_Timeout, int, float], bThrowx_=False):
            return False
        return self.__Compare(other_) == 0

    def __ne__(self, other_):
        if not _Util.IsInstance(other_, [_Timeout, int, float], bThrowx_=False):
            return True
        return self.__Compare(other_) != 0

    def __lt__(self, other_):
        if not _Util.IsInstance(other_, [_Timeout, int, float], bThrowx_=False):
            return False
        return self.__Compare(other_) == -1

    def __le__(self, other_):
        if not _Util.IsInstance(other_, [_Timeout, int, float], bThrowx_=False):
            return False
        cmp = self.__Compare(other_)
        return cmp == -1 or cmp == 0

    def __gt__(self, other_):
        if not _Util.IsInstance(other_, [_Timeout, int, float], bThrowx_=False):
            return False
        return self.__Compare(other_) == 1

    def __ge__(self, other_):
        if not _Util.IsInstance(other_, [_Timeout, int, float], bThrowx_=False):
            return False
        cmp = self.__Compare(other_)
        return cmp == 1 or cmp == 0

    @property
    def timeSpan(self):
        return self.__timeSpan

    @property
    def resolution(self):
        return self.__resolution

    @property
    def clockTicksNS(self):
        return self.__clockTicksNSec

    @property
    def cycleTimes(self):
        return self.__cycleTimes

    @property
    def consumedCycleTimes(self):
        return self.__consumedCycleTimes 

    @property
    def remainingCycleTimes(self):
        res = 0
        if self.__cycleTimes != 0:
            res = self.__cycleTimes - self.__consumedCycleTimes
        return res

    @property
    def toMSec(self):
        return int(self.__remainingTicksNS / _TimeUtil.TICKS_PER_MSECOND)

    @property
    def toUSec(self):
        return int(self.__remainingTicksNS / _TimeUtil.TICKS_PER_USECOND)

    @property
    def toNSec(self):
        return int(self.__remainingTicksNS / _TimeUtil.TICKS_PER_NSECOND)

    @property
    def toSec(self):
        return float(float(self.__remainingTicksNS) / _TimeUtil.TICKS_PER_SECOND)

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
        return self.__remainingTicksNS > 0

    @property
    def isInfiniteTimeout(self):
        return self.__remainingTicksNS == 0

    @property
    def isCyclic(self):
        return self.__cycleTimes != 1

    @property
    def isInfiniteCyclic(self):
        return self.__cycleTimes == 0

    def IsExpired(self, clockTicksNSec_ : int =None):
        if not isinstance(clockTicksNSec_, int) or clockTicksNSec_ < 0:
            clockTicksNSec_ = _TimeUtil.GetCurTicksNS()
        if clockTicksNSec_ <= self.__clockTicksNSec:
            return True
        return (clockTicksNSec_ - self.__clockTicksNSec) >= self.toNSec

    def IsNotExpired(self, clockTicksNSec_ : int =None):
        return not _Timeout.IsExpired(self, clockTicksNSec_)

    def IncrementConsumedCycleTimes(self):
        if self.__cycleTimes == 0 or self.__consumedCycleTimes < self.__cycleTimes:
            self.__consumedCycleTimes += 1

    def ResetConsumedCycleTimes(self, consumedCycleTimes_ =0):
        if consumedCycleTimes_ < 0:
            consumedCycleTimes_ = 0
        if self.__cycleTimes != 0 and consumedCycleTimes_ > self.cycleTimes:
            consumedCycleTimes_ = self.cycleTimes
        self.__consumedCycleTimes = consumedCycleTimes_

    def UpdateClock(self, clockTicksNSec_ : int =None, bUpdateTimeSpan_ =False):
        if not isinstance(clockTicksNSec_, int) or clockTicksNSec_ < 0:
            clockTicksNSec_ = _TimeUtil.GetCurTicksNS()

        if bUpdateTimeSpan_:
            if self.resolution != _ETimeoutResolution.eTicksPerNSec:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00040)
                return 0
            else:
                self.__timeSpan -= clockTicksNSec_ - self.__clockTicksNSec
                if self.__timeSpan < 0:
                    self.__timeSpan = 0
                self.__remainingTicksNS = self.__timeSpan

        self.__clockTicksNSec = clockTicksNSec_
        return self.__clockTicksNSec

    def SetTimeSpan(self, timeSpan_, clockTicksNSec_ : int =None):
        if self.isFiniteTimeout:
            logif._LogBadUseEC(_EFwErrorCode.FE_00084, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Timeout_TextID_005))
        self.Reconfigure(timeSpan_, cycleTimes_=self.cycleTimes, timeoutRes_=self.resolution, clockTicksNSec_=clockTicksNSec_)

    def Clone(self, clockTicksNSec_ : int =None):
        if self.isInfiniteTimeout:
            return _Timeout.CreateInfiniteTimeout()
        else:
            return _Timeout.__CreateTimeout( self.timeSpan, self.cycleTimes, self.resolution, clockTicksNSec_)

    def Reconfigure(self, timeSpan_, cycleTimes_ : int =None, timeoutRes_ : _ETimeoutResolution =None, clockTicksNSec_ : int =None):
        if self.isInfiniteTimeout:
            logif._LogBadUseEC(_EFwErrorCode.FE_00085, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Timeout_TextID_006))
            return False

        if cycleTimes_ is None:
            cycleTimes_ = self.cycleTimes
        if timeoutRes_ is None:
            timeoutRes_ = self.resolution

        r1, r2, r3, r4, r5 = _Timeout.__EvaluateParams(timeSpan_, cycleTimes_, timeoutRes_, clockTicksNSec_)
        if r1 is None:
            return False

        self.__timeSpan           = r2
        self.__resolution         = r3
        self.__cycleTimes         = r4
        self.__clockTicksNSec     = r5
        self.__remainingTicksNS   = r1
        self.__consumedCycleTimes = 0
        return True

    def _ToString(self, *args_, **kwargs_):
        tres    = self.resolution
        _verbose = False

        _lstArgs = _ListUtil.UnpackArgs(*args_, minArgsNum_=1, maxArgsNum_=2, bThrowx_=True)
        if len(_lstArgs) > 0:
            tres = _lstArgs[0]
            _Util.IsInstance(tres, _ETimeoutResolution)
            if len(_lstArgs) > 1:
                _verbose = _lstArgs[1]

        if _verbose:
            if self.isInfiniteCyclic:
                res = '_Timeout: (resolution, timeSpan, cycleTimes)=({}, {}, {})'.format(tres, self.__ToString(tres), self.cycleTimes)
            else:
                res = '_Timeout: (resolution, timeSpan, cycleTimes, remainingCycleTimes)=({}, {}, {}, {})'.format(
                    tres, self.__ToString(tres), self.cycleTimes, self.remainingCycleTimes)
        else:
            res = '_Timeout: (resolution, timeSpan)=({}, {})'.format(tres, self.__ToString(tres))
        return res

    def _CleanUp(self):
        self.__timeSpan           = None
        self.__resolution         = None
        self.__cycleTimes         = None
        self.__clockTicksNSec     = None
        self.__remainingTicksNS   = None
        self.__consumedCycleTimes = None

    @staticmethod
    def __CreateTimeout(timeSpan_, cycleTimes_, timeoutRes_, clockTicksNSec_, createCyclic_ =False):
        if createCyclic_:
            if cycleTimes_ == 1:
                logif._LogErrorEC(_EFwErrorCode.UE_00032, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Timeout_TextID_007))
                return None
        elif cycleTimes_ != 1:
            logif._LogErrorEC(_EFwErrorCode.UE_00033, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Timeout_TextID_008).format(cycleTimes_))
            return None

        res = None
        try:
            res = _Timeout(timeSpan_, cycleTimes_=cycleTimes_, timeoutRes_=timeoutRes_, clockTicksNSec_=clockTicksNSec_)
        except _XcoExceptionRoot as xcp:
            logif._PrintException(xcp)
        except BaseException as xcp:
            logif._PrintException(_XcoBaseException(xcp, tb_=logif._GetFormattedTraceback()))
        finally:
            if res is None:
                pass
            elif res.__remainingTicksNS is None:
                res.CleanUp()
                res = None
        return res

    @staticmethod
    def __EvaluateParams(timeSpan_, cycleTimes_, timeoutRes_ =None, clockTicksNSec_ =None):
        _bOK, r1, r3, r4 = True, -1, timeoutRes_, clockTicksNSec_

        if r3 is None:
            r3 = _ETimeoutResolution.eTicksPerMSec
        if r4 is None:
            r4 = _TimeUtil.GetCurTicksNS()

        _bOK &= _Util.IsInstance(r3, _ETimeoutResolution, bThrowx_=True)
        _bOK &= _Util.IsInstance(r4, int, bThrowx_=True)
        _bOK &= _Util.CheckMinRange(r4, 0, bThrowx_=True)
        _bOK &= _Util.IsInstance(cycleTimes_, int, bThrowx_=True)
        _bOK &= _Util.CheckMinRange(cycleTimes_, 0, bThrowx_=True)
        if _bOK:
            r1   = _Timeout.__TimeSpanToTicks(timeSpan_, r3)
            _bOK = r1 > -1
            _bOK &= _Util.CheckMaxRange(r1, _Timeout.__TIMEOUT_MAX_TICKS, bThrowx_=True)

        if not _bOK:
            r1, timeSpan_, r3, cycleTimes_, r4 = None, None, None, None, None
        return r1, timeSpan_, r3, cycleTimes_, r4

    @staticmethod
    def __TimeSpanToTicks(timeSpan_, timeoutRes_):
        if _Timeout.GetBaseResolution() != _ETimeoutResolution.eTicksPerNSec:
            logif._LogImplErrorEC(_EFwErrorCode.FE_00570, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Timeout_TextID_009))

        if not _Util.IsInstance(timeSpan_, [int, float, str], bThrowx_=False):
            logif._LogBadUseEC(_EFwErrorCode.FE_00086, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Timeout_TextID_010).format(_Util.TypeName(timeSpan_)))
            return -1

        if isinstance(timeSpan_, str):
            try:
                base = 10 if not _StrUtil.IsHexString(timeSpan_) else 16
                timeSpan_ = int(timeSpan_, base)
            except ValueError as xcp:
                logif._LogBadUseEC(_EFwErrorCode.FE_00087, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Timeout_TextID_011).format(timeSpan_, timeoutRes_.name))
                return -1

        if not _Util.CheckMinRange(timeSpan_, 1, bThrowx_=True):
            logif._LogBadUseEC(_EFwErrorCode.FE_00088, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Timeout_TextID_012).format(timeSpan_, timeoutRes_.name))
            return -1

        if timeoutRes_ == _ETimeoutResolution.eTicksPerSec:
            ticksFactor = _TimeUtil.TICKS_PER_SECOND
        elif timeoutRes_ == _ETimeoutResolution.eTicksPerMSec:
            ticksFactor = _TimeUtil.TICKS_PER_MSECOND
        elif timeoutRes_ == _ETimeoutResolution.eTicksPerUSec:
            ticksFactor = _TimeUtil.TICKS_PER_USECOND
        elif timeoutRes_ == _ETimeoutResolution.eTicksPerNSec:
            ticksFactor = _TimeUtil.TICKS_PER_NSECOND
        else:
            logif._LogImplErrorEC(_EFwErrorCode.FE_00571, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Timeout_TextID_013).format(timeoutRes_))
            return -1
        return int(timeSpan_ * ticksFactor)

    def __Compare(self, other_):
        _Util.IsInstance(other_, [_Timeout, int, float])

        if not isinstance(other_, _Timeout):
            otherNS = other_
        else:
            otherNS = other_.toNSec

        res = 0
        if self.toNSec < otherNS:
            res = -1
        elif self.toNSec > otherNS:
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
