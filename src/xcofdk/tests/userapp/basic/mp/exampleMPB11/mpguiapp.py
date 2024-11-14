#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : mpguiapp.py
#
# Copyright(c) 2024 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
import os
import sys
sys.path.extend(((_xcoRootPath := os.path.normpath(os.path.join(os.path.dirname(__file__), '../../../../../..'))) not in sys.path) * [_xcoRootPath])

import xcofdk.tests.userapp.util.tkimport as _TkImportCheck

import platform        as _PyPlf
import multiprocessing as _PyMP

from xcofdk import fwapi

from xcofdk.tests.userapp.basic.mp.exampleMPB11.maintask import MainTaskMP
from xcofdk.tests.userapp.util.userAppUtil               import UserAppUtil


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
def Main(fwStartOptions_ : list):
    """
    Main script of example exampleMPB11.


    Purpose of exampleMPB11:
    -------------------------
    This example demonstrate how the framework of XCOFDK can be used by
    applications for multiprocessing. Its main task cyclically creates and
    starts a pre-defined number of instances of class 'XProcess' showing the
    result of each of them as soon as the execution is terminated.


    Program arguments:
    ----------------------
    This example has two optional command line arguments:
        1) --disable-auto-start:
        2) --enable-auto-close:
           see corresponding section in class description of STGuiAppWelcome,


    Process start method:
    ------------------------
    As explained in section 'Process start method' class description of XProcess
    the framework of XCOFDK never sets or changes the process start method of
    Python's multiprocessing package, explained in the official documentation
    pages below:
        - https://docs.python.org/3/library/multiprocessing.html#contexts-and-start-methods
        - https://docs.python.org/3/library/multiprocessing.html#multiprocessing.set_start_method

    Accordingly, this example will start child process created by the main task
    with the current start method by default.

    However, this module provides the helper function '_CheckSetProcessStartMode()'
    below) which can be used to explicitly set the desired process start method,
    provided necessary local changes to this script are made beforehand.

    See:
    -----
        - xcofdk.fwapi
        - xcofdk.fwapi.xprocess.XProcess
        - exampleMPB11.maintask.MainTask
        - xcofdk.tests.userapp.st.welcome.stguiappwelcome.STGuiAppWelcome
        - _CheckSetProcessStartMode()
    """

    # step 1: create main task
    _myMXT = MainTaskMP.CreateSingleton(None)
    if _myMXT is None:
        return 71

    # step 2: start framework
    if not fwapi.StartXcoFW(fwStartOptions_=fwStartOptions_):
        return 72

    # step 3: start main task
    _myMXT.Start()

    # step 4: wait for main task's termination
    _myMXT.Join()

    # step 5: stop framework
    fwapi.StopXcoFW()

    # step 6: make program termination is synchronized to framework's coordinated shutdown
    _bLcErrorFree = fwapi.JoinXcoFW()

    # step 7: check for LC failure (if any)
    res = 73 if not _bLcErrorFree else 0
    return res
#END Main()


def _CheckSetProcessStartMode():
    """
    Check and set the process start method to be used by the multiprocessing
    library of Python when starting child processes.

    Unless below local variables are modified, this helper function will not
    attempt to change current process start method:
        - __bCHANGE_PROCESS_START_METHOD:
          if it resolves to True, try to set process start method.
          It defaults to False.

        - __bCHANGE_BY_FORCE:
          if it resolves to True, set the associated 'force' flag of Python's
          setter function to True when called.
          It defaults to False.

        - __PROCESS_START_METHOD_NOT_FIXED:
          the desired process start method, either 'fork' or 'spawn'.
          The helper function won't try to set current start method if the
          returned value by Python's getter function equals to the desired one.
          It defaults to None.

    See:
    -----
        - Main()
        - https://docs.python.org/3/library/multiprocessing.html#contexts-and-start-methods
        - https://docs.python.org/3/library/multiprocessing.html#multiprocessing.set_start_method

    """

    __PROCESS_START_METHOD_FORK      = 'fork'
    __PROCESS_START_METHOD_SPAWN     = 'spawn'
    __PROCESS_START_METHOD_NOT_FIXED = None

    __bCHANGE_PROCESS_START_METHOD = False
    __bCHANGE_BY_FORCE             = False
    __TGT_PROCESS_START_METHOD     = __PROCESS_START_METHOD_NOT_FIXED

    __PLF = _PyPlf.system()


    res    = True
    _curSM = _PyMP.get_start_method(allow_none=True)

    if __bCHANGE_PROCESS_START_METHOD:
        if _curSM != __TGT_PROCESS_START_METHOD:
            print(f'[exampleMPB11][platform:{__PLF}] Trying to set MP process start method to: \'{__TGT_PROCESS_START_METHOD}\'')

            try:
                _PyMP.set_start_method(__TGT_PROCESS_START_METHOD, force=__bCHANGE_BY_FORCE)
            except RuntimeError as _xcp:
                res = False
                print(f'[exampleMPB11][platform:{__PLF}] Caught exception below while trying to set MP process start method to: \'{__TGT_PROCESS_START_METHOD}\'\n\t{_xcp}')
            finally:
                _curSM = _PyMP.get_start_method(allow_none=True)
                if res:
                    print(f'[exampleMPB11][platform:{__PLF}] Set MP process start method to \'{__TGT_PROCESS_START_METHOD}\'.')
        else:
            print(f'[exampleMPB11][platform:{__PLF}] Current MP process start method is set to \'{__TGT_PROCESS_START_METHOD}\', ignoring request to reset it.')
    else:
        pass

    return res, _curSM
#END _CheckSetProcessStartMode()


# ------------------------------------------------------------------------------
# Execution
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    for aa in sys.argv:
        if aa == '--help':
            _usage  = os.path.splitext(os.path.basename(sys.argv[0]))[0]
            _usage  = f'Usage:\n\t$> python3 -m {_usage} [--help] [--disable-auto-close] [--disable-auto-start] [--disable-log-timestamp] [--disable-log-highlighting] [--log-level LLEVEL]'
            _usage += '\n\t   LLEVEL : [trace | debug | info | warning | error]'
            print(_usage)
            exit(0)

    _fwStartOptions = UserAppUtil.GetFwStartOptions(loglevel_=None, bDisableLogTimestamp_=None, bDisableLogHighlighting_=None)
    if _fwStartOptions is None:
        exit(80)

    _bOK, _sm = _CheckSetProcessStartMode()
    if not _bOK:
        exit(81)
    print(f'[exampleMPB11][platform:{_PyPlf.system()}] Starting user application with current MP process start method detected as set to: \'{_sm}\'')

    _iRes = Main(_fwStartOptions)
    exit(_iRes)
