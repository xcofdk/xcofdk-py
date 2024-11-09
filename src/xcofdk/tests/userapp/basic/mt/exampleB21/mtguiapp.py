#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : mtguiapp.py
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

from xcofdk import fwapi

from xcofdk.tests.userapp.basic.mt.exampleB21.maintask import MainTask
from xcofdk.tests.userapp.util.userAppUtil             import UserAppUtil


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
def Main(fwStartOptions_ : list):
    # step 1: create main task
    _myMXT = MainTask.CreateSingleton(None)
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


# ------------------------------------------------------------------------------
# Execution
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    _fwStartOptions = UserAppUtil.GetFwStartOptions(loglevel_=None, bDisableLogTimestamp_=None, bDisableLogHighlighting_=None)
    if _fwStartOptions is None:
        exit(80)

    _iRes = Main(_fwStartOptions)
    exit(_iRes)
