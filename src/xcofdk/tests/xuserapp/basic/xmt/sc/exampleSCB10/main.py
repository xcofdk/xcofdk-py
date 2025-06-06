# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : main.py
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
from xcofdk import fwapi

from xuserapp.basic.xmt.sc.exampleSCB10.maintask import MyMainTask


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
def _GetStartOptions() -> str:
    """
    Return a string which can be passed to framework's API in step 2 of
    function 'Main()' below.
    """

    res   = ''
    #res  = '--log-level info '
    res  += '--fw-log-level info '
    #res += '--disable-log-callstack'
    #res += '--disable-log-timestamp'
    #res += '--disable-log-highlighting'
    return res
#END _GetStartOptions()


def Main():
    # step 1: create main task
    _myMXT = MyMainTask.CreateSingleton(None)
    if _myMXT is None:
        return 71

    # step 2: start framework
    if not fwapi.StartXcoFW(fwStartOptions_=_GetStartOptions()):
        return  72

    # step 3: start main task
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
    for aa in sys.argv:
        if aa == '--help':
            _usage = os.path.splitext(os.path.basename(sys.argv[0]))[0]
            _usage = f'Usage:\n\t$> python3 -m {_usage} [--help]'
            print(_usage)
            exit(0)
    exit(Main())
