# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : userAppUtil.py
#
# Copyright(c) 2024 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
import os
import sys
sys.path.extend(((_xcoRootPath := os.path.normpath(os.path.join(os.path.dirname(__file__), '../../../..'))) not in sys.path) * [_xcoRootPath])

from typing   import Union
from datetime import datetime
from datetime import timedelta
from time     import sleep


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class UserAppUtil:

    __slots__ = []

    __FW_START_OPTION_LOGLEVEL       = '--log-level'
    __CMD_LINE_DUAL_OPTIONS_LIST     = [ __FW_START_OPTION_LOGLEVEL , '--service-tasks-count' , '--fibonacci-input 20' ]
    __FW_START_OPTION_DISABLE_LOG_TS = '--disable-log-timestamp'
    __FW_START_OPTION_DISABLE_LOG_HL = '--disable-log-highlighting'


    def __init__(self):
        pass

    @staticmethod
    def GetFwStartOptions(loglevel_ : str =None, bDisableLogTimestamp_ : bool =None, bDisableLogHighlighting_ : bool =None) -> list:
        """
        Return a list of string literals which can be used as framework's start
        options to be passed to corresponding API function.
        """
        return UserAppUtil.__GetFwStartOptions(loglevel_=loglevel_, bDisableLogTimestamp_=bDisableLogTimestamp_, bDisableLogHighlighting_=bDisableLogHighlighting_)

    @staticmethod
    def SleepMS(timespanMS_ : int):
        if not (isinstance(timespanMS_, int) and timespanMS_>0):
            timespanMS_ = 1
        return sleep(float(timespanMS_/1000))

    @staticmethod
    def SleepSEC(timespanSEC_ : float):
        if not (isinstance(timespanSEC_, float) and timespanSEC_>0.0):
            timespanSEC_ = 0.001
        return sleep(float(timespanSEC_))

    @staticmethod
    def GetCurrentTime() -> datetime:
        return datetime.now()

    @staticmethod
    def GetTimestamp() -> str:
        dt = datetime.now()
        secfrac = "{:>03d}".format(dt.microsecond // 1000)
        return dt.strftime("%H:%M:%S.") + secfrac

    @staticmethod
    def DeltaTime2Str(dtime_ : Union[timedelta, datetime], bIncludeHours_ =False, bIncludeUSec_ =False, bLeftStripUnsetFields_ =False) -> str:
        if not isinstance(dtime_, (timedelta, datetime)):
            return None

        dt = dtime_
        if not isinstance(dtime_, timedelta):
            dt = datetime.now() - dtime_

        dd = dt.days
        #ms = ((dt.microseconds+500) // 1000)
        ms  = dt.microseconds // 1000

        tt  = dt.seconds
        ss  = tt % 60
        tt -= ss

        mm = tt // 60
        hh = mm // 60
        mm = mm % 60

        if dd > 0:
            res = '{0:02d}, {1:02d}:{2:02d}:{3:02d}.{4:03d}'.format(dd, hh, mm, ss, ms)
        elif (hh > 0) or bIncludeHours_:
            res = '{0:02d}:{1:02d}:{2:02d}.{3:03d}'.format( hh, mm, ss, ms)
        else:
            res = '{0:02d}:{1:02d}.{2:03d}'.format(mm, ss, ms)

        if bIncludeUSec_:
            res += '.{:03d}'.format(dt.microseconds%1000)

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

    # --------------------------------------------------------------------------
    # Impl
    # --------------------------------------------------------------------------
    @staticmethod
    def __GetFwStartOptions(loglevel_ : str =None, bDisableLogTimestamp_ : bool =None, bDisableLogHighlighting_ : bool =None) -> list:
        #NOTE:
        # a) currently available start options:
        #      --log-level
        #      --disable-log-timestamp
        #      --disable-log-highlighting
        #
        # b) valid values for loglevel:
        #    trace | debug | info | warning | error
        #

        _LOG_LEVEL_CHOICES_LIST = 'trace debug info warning error'.split()

        res = UserAppUtil.__CheckGetCmdLineOptions(_LOG_LEVEL_CHOICES_LIST)
        if res is None:
            return None

        # option '--log-level' not specified via cmdline?
        if not UserAppUtil.__FW_START_OPTION_LOGLEVEL in res:
            if loglevel_ is not None:
                if not (isinstance(loglevel_, str) and loglevel_ in _LOG_LEVEL_CHOICES_LIST):
                    _tmp = ' | '.join(_LOG_LEVEL_CHOICES_LIST)
                    print('[UserAppUtil] Unknown/invalid loglevel \'{}\' passed in as start option, see below for defined values:\n\t'.format(str(loglevel_), _tmp))
                    return None

                res.append(UserAppUtil.__FW_START_OPTION_LOGLEVEL)
                res.append(loglevel_)
        else:
            # ignore passed in loglevel, cmdline options do have precedence
            pass

        # option '--disable-log-timestamp' not specified via cmdline?
        if not UserAppUtil.__FW_START_OPTION_DISABLE_LOG_TS in res:
            if isinstance(bDisableLogTimestamp_, bool):
                res.append(UserAppUtil.__FW_START_OPTION_DISABLE_LOG_TS)
        else:
            # ignore passed in flag, cmdline options do have precedence
            pass

        # option '--disable-log-highlighting' not specified via cmdline?
        if not UserAppUtil.__FW_START_OPTION_DISABLE_LOG_HL in res:
            if isinstance(bDisableLogHighlighting_, bool):
                res.append(UserAppUtil.__FW_START_OPTION_DISABLE_LOG_HL)
        else:
            # ignore passed in flag, cmdline options do have precedence
            pass

        if len(res) < 1:
            print('[UserAppUtil] No framework start options detected via cmdline arguments or requested by passed in parameters, defautls will be applied.\n')
        else:
            print('[UserAppUtil] Resulting list of framework start options detected via cmdline arguments or requested by passed in parameters:\n\t{}'.format(' '.join(res)))
        return res

    @staticmethod
    def __CheckGetCmdLineOptions(lstValidLoglevelValues_ : list) -> list:
        res = []

        _NARGS = len(sys.argv)
        if _NARGS < 1:
            return res

        _ii = 0
        while True:
            _ii += 1
            if _ii >= _NARGS:
                break

            _aa = sys.argv[_ii]
            if _aa.startswith('#'):
                break

            # dual option?
            if _aa in UserAppUtil.__CMD_LINE_DUAL_OPTIONS_LIST:
                _aa  = sys.argv[_ii]
                _bLL = _aa == UserAppUtil.__FW_START_OPTION_LOGLEVEL
                if _bLL:
                    res.append(_aa)

                _ii += 1
                if _ii >= _NARGS:
                    print('[UserAppUtil] Missing value specification after cmdline option \'{}\'.'.format(_aa))
                    return None

                if not _bLL:
                    continue

                _loglevel = sys.argv[_ii]
                if _loglevel not in lstValidLoglevelValues_:
                    _tmp = ' | '.join(lstValidLoglevelValues_)
                    print('[UserAppUtil] Unknown/invalid loglevel \'{}\' specified via cmdline, see below for defined values:\n\t{}'.format(str(_loglevel), _tmp))
                    return None

                res.append(_loglevel)
                continue

            # option '--disable-log-timestamp'
            if _aa == UserAppUtil.__FW_START_OPTION_DISABLE_LOG_TS:
                res.append(_aa)
                continue

            # option '--disable-log-highlighting'
            if _aa == UserAppUtil.__FW_START_OPTION_DISABLE_LOG_HL:
                res.append(_aa)
                continue
        return res
    # --------------------------------------------------------------------------
    #END Impl
    # --------------------------------------------------------------------------
#END class UserAppUtil


# ------------------------------------------------------------------------------
# Execution
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    UserAppUtil.SampleFibonacci()
