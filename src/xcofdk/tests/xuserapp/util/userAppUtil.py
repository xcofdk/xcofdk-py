# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : userAppUtil.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# PYTHONPATH extension
# ------------------------------------------------------------------------------
import os, sys
_xcoRP = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../../..'))
if _xcoRP.endswith('/src') and os.path.exists(os.path.join(_xcoRP, 'xcofdk')) and _xcoRP not in sys.path: sys.path.extend([_xcoRP])
try:
    import xcofdk
except ImportError:
    exit(f"[{os.path.basename(__file__)}] Failed to import Python package 'xcofdk', missing installation.")


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
try:
    from sys import _is_gil_enabled
    def _PyIsGilEnabled(): return _is_gil_enabled()
except (ImportError, Exception):
    def _PyIsGilEnabled(): return True

import itertools
import random
from   datetime import datetime
from   datetime import timedelta
from   os       import getpid
from   time     import sleep
from   typing   import Union

from xcofdk.fwapi import fwutil
from xcofdk.fwapi import GetCurTask


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class CartProdResult:
    __slots__ = [ '__ts', '__cp' ]

    def __init__(self, res_: str):
        self.__ts = datetime.now()
        self.__cp = res_

    def __str__(self):
        return self.__ToString()

    @property
    def cartProdResult(self) -> str:
        return self.__cp

    @property
    def cartProdTimestamp(self) -> datetime:
        return self.__ts

    def __ToString(self):
        _ts = self.__ts.strftime("%H:%M:%S.") + "{:>03d}".format(self.__ts.microsecond // 1000)
        return f'[{_ts}]{self.__cp}'
#END class CartProdResult


class UserAppUtil:
    __slots__ = []

    def __init__(self):
        pass

    _bBigCartProdAlgo = True

    # --------------------------------------------------------------------------
    # API
    # --------------------------------------------------------------------------
    @staticmethod
    def IsExperimentalFTPythonVersion() -> bool:
        return fwutil.IsExperimentalFTPythonVersion()

    @staticmethod
    def GetPythonVersion() -> str:
        res = fwutil.GetPythonVersion()
        if (sys.version_info.minor >= 13) and not _PyIsGilEnabled():
            res += '-FT'
        return res

    @staticmethod
    def SleepMS(timespanMS_ : int):
        if not (isinstance(timespanMS_, int) and timespanMS_>0):
            timespanMS_ = 1
        sleep(float(timespanMS_/1000))

    @staticmethod
    def SleepSEC(timespanSEC_ : float):
        if not (isinstance(timespanSEC_, float) and timespanSEC_>0.0):
            timespanSEC_ = 0.001
        sleep(float(timespanSEC_))

    @staticmethod
    def GetCurrentTime() -> datetime:
        return datetime.now()

    @staticmethod
    def GetTimestamp() -> str:
        tstamp_ = datetime.now().isoformat(timespec='milliseconds')
        return tstamp_[tstamp_.index('T')+1:]

    @staticmethod
    def DeltaTime2Str(dtime_ : Union[timedelta, datetime], bIncludeHours_ =False, bIncludeUSec_ =False, bLeftStripUnsetFields_ =False) -> Union[str, None]:
        if not isinstance(dtime_, (timedelta, datetime)):
            return None

        _dt = dtime_
        if not isinstance(dtime_, timedelta):
            _dt = datetime.now() - dtime_

        _dd = _dt.days
        #_ms = ((_dt.microseconds+500) // 1000)
        _ms  = _dt.microseconds // 1000

        _tt  = _dt.seconds
        _ss  = _tt % 60
        _tt -= _ss

        _mm = _tt // 60
        _hh = _mm // 60
        _mm = _mm % 60

        if _dd > 0:
            res = '{0:02d}, {1:02d}:{2:02d}:{3:02d}.{4:03d}'.format(_dd, _hh, _mm, _ss, _ms)
        elif (_hh > 0) or bIncludeHours_:
            res = '{0:02d}:{1:02d}:{2:02d}.{3:03d}'.format( _hh, _mm, _ss, _ms)
        else:
            res = '{0:02d}:{1:02d}.{2:03d}'.format(_mm, _ss, _ms)

        if bIncludeUSec_:
            res += '.{:03d}'.format(_dt.microseconds%1000)

        if bLeftStripUnsetFields_:
            while True:
                pos = res.find('00:')
                if pos != 0:
                    break

                res = res[3:]
                if res.startswith('.'):
                    res = f'0{res}'
                    break
                if res.startswith('00.'):
                    res = res[1:]
                    break
                if res.startswith('0') and not res.startswith('0.'):
                    res = res[1:]
                    break
        return res

    @staticmethod
    def Fibonacci(in_: int):
        if not (isinstance(in_, int) and in_>=0):
            res = 0
        elif in_ < 2:
            res = in_
        else:
            res = UserAppUtil.Fibonacci(in_-1) + UserAppUtil.Fibonacci(in_-2)
        return res

    @staticmethod
    def FibonacciCpuTimeUS(in_: int) -> float:
        _dt = datetime.now()
        UserAppUtil.Fibonacci(in_)
        _dt = datetime.now() - _dt
        return _dt.total_seconds()*(10**6)

    @staticmethod
    def CreateDigitSet(repeatSize_: int = 5) -> str:
        _MIN_VAL, _MAX_VAL = 10 ** repeatSize_, ((10 ** (repeatSize_ + 1)) - 1)

        res = str(random.randint(_MIN_VAL, _MAX_VAL))
        res = list(''.join(res.split()))
        for _ii in range(10):
            random.shuffle(res)
        return ''.join(res)

    @staticmethod
    def CartProdAlgo(tid_: Union[int, str] = None, bRequestByParentProc_=False) -> CartProdResult:
        _bBig = UserAppUtil._bBigCartProdAlgo

        if _bBig:
            _REPEAT_SIZE = 7 if bRequestByParentProc_ else 6
        else:
            _REPEAT_SIZE = 6 if bRequestByParentProc_ else 5

        _FMT1   = '{:>7}' if _bBig else '{:>6}'
        _ds     = UserAppUtil.CreateDigitSet(_REPEAT_SIZE)
        _prods  = [_pp for _pp in itertools.product(_ds, repeat=_REPEAT_SIZE)]
        _prods2 = _prods[len(_prods) - 5:]
        _prods2 = [_FMT1.format(''.join(_pp)) for _pp in _prods2]
        _prods2 = ' , '.join(_prods2)
        _reqtor = '' if not bRequestByParentProc_ else f'[PID:{getpid()}]'
        _curTsk = None if bRequestByParentProc_ else GetCurTask()

        if (_curTsk is not None) and (tid_ is None):
            tid_ = _curTsk.taskUID
        if (len(_reqtor) < 1) and (tid_ is not None):
            _reqtor = f'[TID:{tid_}]'

        _ds   = f"'{_ds}'"
        _FMT2 = "{:<20}  digitSet={:<10} size={:<7}  tail:  {}"
        res = CartProdResult(_FMT2.format(_reqtor, _ds, len(_prods), _prods2))

        if _curTsk is not None:
            if _curTsk.GetTaskOwnedData() is None:
                _curTsk.SetTaskOwnedData([])
            _curTsk.GetTaskOwnedData().append(res)
        return res
    # --------------------------------------------------------------------------
    #END API
    # --------------------------------------------------------------------------
#END class UserAppUtil


def DisableBigCartProd():
    UserAppUtil._bBigCartProdAlgo = False

def CreateDigitSet(repeatSize_: int =5) -> str:
    return UserAppUtil.CreateDigitSet(repeatSize_=repeatSize_)

def CartProdAlgo(tid_: Union[int, str] =None, bRequestByParentProc_ =False) -> CartProdResult:
    return UserAppUtil.CartProdAlgo(tid_=tid_, bRequestByParentProc_=bRequestByParentProc_)
