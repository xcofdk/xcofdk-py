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

from xuserapp.util.cloptions                     import ECLOptionID
from xuserapp.util.cloptions                     import CLOptions
from xuserapp.util.cloptions                     import GetCmdLineOptions
from xuserapp.basic.xmt.sc.exampleSCB25.maintask import MainTaskCustomPayload


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
def Main(cmdLineOpts_ : CLOptions):
    # optional: disable subsystem xmp
    rtecfg.RtePolicyDisableSubSystemMultiProcessing()

    # step 1: configure framework's RTE for experimental free-threaded Python (if enabled via CmdLine)
    if cmdLineOpts_.isFreeThreadingGuardBypassed:
        rtecfg.RtePolicyBypassExperimentalFreeThreadingGuard()

    # step 2: create main task
    _myMXT = MainTaskCustomPayload.CreateSingleton(None, cmdLineOpts_)
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


# ------------------------------------------------------------------------------
# Execution
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    _opts = [ECLOptionID.eAsyncMainTask, ECLOptionID.eServiceTasksCount]
    _cl = GetCmdLineOptions(_opts)
    if (_cl is None) or _cl.isHelpSupplied:
        _xc = 1 if _cl is None else 0
    else:
        _xc = Main(_cl)
    exit(_xc)
