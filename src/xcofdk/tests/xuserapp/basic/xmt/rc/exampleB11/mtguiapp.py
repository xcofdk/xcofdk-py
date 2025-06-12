#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : mtguiapp.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# PYTHONPATH extension
# ------------------------------------------------------------------------------
import os, sys
_xcoRP = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../../../../../..'))
if _xcoRP.endswith('/src') and os.path.exists(os.path.join(_xcoRP, 'xcofdk')) and _xcoRP not in sys.path: sys.path.extend([_xcoRP])
try:
    import xcofdk
except ImportError:
    exit(f"[{os.path.basename(__file__)}] Failed to import Python package 'xcofdk', missing installation.")
sys.path.extend(((_xua := os.path.normpath(os.path.join(os.path.dirname(__file__), '../../../../..'))) not in sys.path) * [_xua])


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
import xuserapp.util.tkimport as _TkImportCheck

from xcofdk       import fwapi
from xcofdk.fwapi import rtecfg

from xuserapp.util.cloptions                   import ECLOptionID
from xuserapp.util.cloptions                   import CLOptions
from xuserapp.util.cloptions                   import GetCmdLineOptions
from xuserapp.basic.xmt.rc.exampleB11.maintask import _CreateMainTask


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
def Main(cmdLineOpts_ : CLOptions):
    """
    Main script of example exampleB11.


    Purpose of exampleB11:
    -------------------------
    Main objective of this example is to:
        a) demonstrate rapid construction (RC) approach to create application
           tasks.

        b) demonstrate how the framework of XCOFDK can be used by mutlithreaded
           applications.

           The example uses one single application task, namely its main task,
           only. However, that task is executed by framework's multithreaded
           runtime environment, so the resulted program is in fact a
           multithreaded application.

        c) serve as the multithreaded version of its singlethreaded counterpart
           presented via class 'STGuiAppWelcome'.

           So, a performance comparison between both versions of the same GUI
           applications provides direct conclusions with regard to the
           performance of the framework, too.

        d) demonstrate how to use pre-start confguration of framework's RTE.
           It also shows how waiting for running tasks is managed in an
           automated manner, especially by making an explicit, otherwise
           mandatory request to stop the framework an optional operation now,
           except for RTE policy TerminalMode (if enabled).

    See:
    -----
        - xcofdk.fwapi
        - xcofdk.fwapi.rtecfg
        - exampleB11.maintask.MainTask
        - xcofdk.tests.xuserapp.st.welcome.stguiappwelcome.STGuiAppWelcome
    """

    # step 1: configure framework's RTE for free-threaded Python (if enabled via CmdLine)
    if cmdLineOpts_.isFreeThreadingGuardBypassed:
        rtecfg.RtePolicyBypassExperimentalFreeThreadingGuard()

    # step 2: create main task
    _myMT = _CreateMainTask(cmdLineOpts_)
    if not _myMT.isAttachedToFW:
        return 71

    # step 3: start framework
    if not fwapi.StartXcoFW(fwStartOptions_=cmdLineOpts_.GetSuppliedFwOptions()):
        return  72

    # step 4: start main task
    _myMT.Start('sample positional argument', kwArg_='sample keyword argument')

    # step 5: wait for framework's coordinated shutdown
    _bLcErrorFree = fwapi.JoinXcoFW()

    # done: check for LC failure (if any)
    res = 73 if not _bLcErrorFree else 0
    return res
#END Main()


# ------------------------------------------------------------------------------
# Execution
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    _opts = [ ECLOptionID.eAsyncMainTask ]
    _cl   = GetCmdLineOptions(_opts)
    if (_cl is None) or _cl.isHelpSupplied:
        _xc = 1 if _cl is None else 0
    else:
        _xc = Main(_cl)
    exit(_xc)
