#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : mpguiapp.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# PYTHONPATH extension
# ------------------------------------------------------------------------------
import os, sys
_xcoRP = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../../../../..'))
if _xcoRP.endswith('/src') and os.path.exists(os.path.join(_xcoRP, 'xcofdk')) and _xcoRP not in sys.path: sys.path.extend([_xcoRP])
try:
    import xcofdk
except ImportError:
    exit(f"[{os.path.basename(__file__)}] Failed to import Python package 'xcofdk', missing installation.")
sys.path.extend(((_xua := os.path.normpath(os.path.join(os.path.dirname(__file__), '../../../..'))) not in sys.path) * [_xua])


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
import xuserapp.util.tkimport as _TkImportCheck

import platform        as _PyPlf
import multiprocessing as _PyMP

from xcofdk       import fwapi
from xcofdk.fwapi import rtecfg

from xuserapp.util.cloptions                  import CLOptions
from xuserapp.util.cloptions                  import GetCmdLineOptions
from xuserapp.basic.xmp.exampleMPB11.maintask import _CreateMainTaskMP


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
def Main(cmdLineOpts_ : CLOptions):
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
        - xcofdk.fwapi.xmp.XProcess
        - exampleMPB11.maintask.MainTask
        - xcofdk.tests.xuserapp.st.welcome.stguiappwelcome.STGuiAppWelcome
        - _CheckSetProcessStartMode()
    """

    # optional: disable subsystem xmsg
    rtecfg.RtePolicyDisableSubSystemMessaging()

    # step 1: configure framework's RTE for experimental free-threaded Python (if enabled via CmdLine)
    if cmdLineOpts_.isFreeThreadingGuardBypassed:
        rtecfg.RtePolicyBypassExperimentalFreeThreadingGuard()

    # step 2: create main task
    _myMXT = _CreateMainTaskMP(cmdLineOpts_)
    if _myMXT is None:
        return 71

    # step 3: start framework
    if not fwapi.StartXcoFW(fwStartOptions_=cmdLineOpts_.GetSuppliedFwOptions()):
        return 72

    # step 4: start main task
    _myMXT.Start()

    # step 5: wait for framework's coordinated shutdown
    _bLcErrorFree = fwapi.JoinXcoFW()

    # done: check for LC failure (if any)
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

    __PROCESS_START_METHOD_FORK       = 'fork'
    __PROCESS_START_METHOD_SPAWN      = 'spawn'
    __PROCESS_START_METHOD_FORKSERVER = 'forkserver'
    __PROCESS_START_METHOD_NOT_FIXED  = None

    __bCHANGE_PROCESS_START_METHOD = False
    __bCHANGE_BY_FORCE             = False
    __TGT_PROCESS_START_METHOD     = __PROCESS_START_METHOD_NOT_FIXED

    __PLF = _PyPlf.system()


    res    = True
    _curSM = _PyMP.get_start_method(allow_none=True)
    print(f'[exampleMPB11][platform:{__PLF}] Current MP process start method: \'{_curSM}\'')

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

    return res, _curSM
#END _CheckSetProcessStartMode()


# ------------------------------------------------------------------------------
# Execution
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    _cl = GetCmdLineOptions()
    if (_cl is None) or _cl.isHelpSupplied:
        exit(1 if _cl is None else 0)

    _bOK, _sm = _CheckSetProcessStartMode()
    if not _bOK:
        _xc = 80
    else:
        print(f'[exampleMPB11][platform:{_PyPlf.system()}] Starting user application with current MP process start method detected as set to: \'{_sm}\'')
        _xc = Main(_cl)
    exit(_xc)
