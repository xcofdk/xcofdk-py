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
        _dt = datetime.now()
        return _dt.strftime("%H:%M:%S.") + "{:>03d}".format(_dt.microsecond // 1000)

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
    def SampleFibonacci():
        """
        Prints out sample time of CPU consumption to calculate
        'UserAppUtil.Fibonacci(N)' with N<=50 when running as standlone script
        with no use of cache and for Python 3.12:

            Fibonacci(0):            0  00:00:00.000.008 [hr]
            Fibonacci(1):            1  00:00:00.000.003 [hr]
            Fibonacci(2):            1  00:00:00.000.002 [hr]
            Fibonacci(3):            2  00:00:00.000.002 [hr]
            Fibonacci(4):            3  00:00:00.000.002 [hr]
            Fibonacci(5):            5  00:00:00.000.002 [hr]
            Fibonacci(6):            8  00:00:00.000.003 [hr]
            Fibonacci(7):           13  00:00:00.000.005 [hr]
            Fibonacci(8):           21  00:00:00.000.007 [hr]
            Fibonacci(9):           34  00:00:00.000.011 [hr]
            Fibonacci(10):          55  00:00:00.000.079 [hr]
            Fibonacci(11):          89  00:00:00.000.051 [hr]
            Fibonacci(12):         144  00:00:00.000.079 [hr]
            Fibonacci(13):         233  00:00:00.000.070 [hr]
            Fibonacci(14):         377  00:00:00.000.155 [hr]
            Fibonacci(15):         610  00:00:00.000.190 [hr]
            Fibonacci(16):         987  00:00:00.000.292 [hr]
            Fibonacci(17):        1597  00:00:00.000.480 [hr]
            Fibonacci(18):        2584  00:00:00.001.818 [hr]
            Fibonacci(19):        4181  00:00:00.001.463 [hr]
            Fibonacci(20):        6765  00:00:00.002.343 [hr]
            Fibonacci(21):       10946  00:00:00.004.584 [hr]
            Fibonacci(22):       17711  00:00:00.007.889 [hr]
            Fibonacci(23):       28657  00:00:00.011.393 [hr]
            Fibonacci(24):       46368  00:00:00.016.964 [hr]
            Fibonacci(25):       75025  00:00:00.029.015 [hr]
            Fibonacci(26):      121393  00:00:00.043.515 [hr]
            Fibonacci(27):      196418  00:00:00.063.963 [hr]
            Fibonacci(28):      317811  00:00:00.105.532 [hr]
            Fibonacci(29):      514229  00:00:00.164.576 [hr]
            Fibonacci(30):      832040  00:00:00.271.604 [hr]
            Fibonacci(31):     1346269  00:00:00.424.861 [hr]
            Fibonacci(32):     2178309  00:00:00.689.491 [hr]
            Fibonacci(33):     3524578  00:00:01.109.348 [hr]
            Fibonacci(34):     5702887  00:00:01.785.914 [hr]
            Fibonacci(35):     9227465  00:00:02.883.205 [hr]
            Fibonacci(36):    14930352  00:00:04.638.776 [hr]
            Fibonacci(37):    24157817  00:00:07.469.615 [hr]
            Fibonacci(38):    39088169  00:00:12.015.411 [hr]
            Fibonacci(39):    63245986  00:00:19.465.279 [hr]
            Fibonacci(40):   102334155  00:00:32.087.946 [hr]
            Fibonacci(41):   165580141  00:00:52.016.172 [hr]
            Fibonacci(42):   267914296  00:01:23.806.934 [hr]
            Fibonacci(43):   433494437  00:02:17.115.432 [hr]
            Fibonacci(44):   701408733  00:03:38.564.663 [hr]
            Fibonacci(45):  1134903170  00:06:00.546.468 [hr]
            Fibonacci(46):  1836311903  00:09:33.907.614 [hr]
            Fibonacci(47):  2971215073  00:16:17.001.775 [hr]
            Fibonacci(48):  4807526976  00:25:46.447.269 [hr]
            Fibonacci(49):  7778742049  00:41:30.306.381 [hr]
            Fibonacci(50): 12586269025  01:06:08.101.126 [hr]
        """

        _MAX_N = 40
        for nn in range(_MAX_N+1):
            start = UserAppUtil.GetCurrentTime()
            print('Fibonacci({}): {:>9d}  {} [sec]'.format(nn, UserAppUtil.Fibonacci(nn), UserAppUtil.DeltaTime2Str(start, bIncludeUSec_=True)))

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


# ------------------------------------------------------------------------------
# Execution
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    UserAppUtil.SampleFibonacci()
