# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : scquickStart.py
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
from math      import pi             # for demonstration purposes only
from math      import pow            # ditto
from threading import current_thread # ditto

from xcofdk           import fwapi
from xcofdk.fwapi     import rtecfg
from xcofdk.fwcom     import EExecutionCmdID
from xcofdk.fwcom     import override
from xcofdk.fwapi     import xlogif
from xcofdk.fwapi.xmt import XTask
from xcofdk.fwapi.xmt import XMainTask
from xcofdk.fwapi.xmt import XTaskProfile

from xuserapp.util.cloptions import ECLOptionID
from xuserapp.util.cloptions import CLOptions
from xuserapp.util.cloptions import GetCmdLineOptions


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class MainTask(XMainTask):
    def __init__(self, bSyncTask_ =True):
        if bSyncTask_:
            _tp = XTaskProfile.CreateSyncTaskProfile(aliasName_='MainTask')
        else:
            _tp = XTaskProfile.CreateAsyncTaskProfile(aliasName_='MainTask')
        super().__init__(taskProfile_=_tp)

    @override
    def RunXTask(self) -> EExecutionCmdID:
        _msg  = 'sync.' if self.taskProfile.isSyncTask else 'async.'
        _msg  = f'Welcome to XCOFDK by {_msg} {self.aliasName}:'
        _msg += f'\n\tcurrent host thread : {current_thread().name}'
        xlogif.LogInfo(_msg)

        _msg = GeomTask.CreateStartGeomPool()
        xlogif.LogInfo(f'Done, result:{_msg}')

        xlogif.LogInfo(f'Going to stop the run-phase of {self.aliasName}...')
        return EExecutionCmdID.STOP
#END class MainTask


class StarterTask(XTask):
    def __init__(self, bSyncTask_ =False):
        if bSyncTask_:
            _tp = XTaskProfile.CreateSyncTaskProfile(aliasName_='StarterTask')
        else:
            _tp = XTaskProfile.CreateAsyncTaskProfile(aliasName_='StarterTask')
        super().__init__(taskProfile_=_tp)

    @override
    def RunXTask(self) -> EExecutionCmdID:
        _msg  = 'sync.' if self.taskProfile.isSyncTask else 'async.'
        _msg  = f'Welcome to XCOFDK by {_msg} {self.aliasName}:'
        _msg += f'\n\tcurrent host thread : {current_thread().name}'
        xlogif.LogInfo(_msg)

        _msg = GeomTask.CreateStartGeomPool()
        xlogif.LogInfo(f'Done, result:{_msg}')

        xlogif.LogInfo(f'Going to stop the run-phase of {self.aliasName}...')
        return EExecutionCmdID.STOP
#END class StarterTask


class GeomTask(XTask):
    def __init__(self):
        self.geomCalc = 0
        _tp = XTaskProfile.CreateAsyncTaskProfile(aliasName_=f'GeomTask_')
        super().__init__(taskProfile_=_tp)

    @override
    def RunXTask(self, radius_ : float, bCalcArea_ =False) -> EExecutionCmdID:
        self.geomCalc = pi*pow(radius_, 2) if bCalcArea_ else 2*pi*radius_
        return EExecutionCmdID.STOP

    @staticmethod
    def CreateStartGeomPool(count_ : int =5) -> str:
        xlogif.LogInfo(f'Starting {count_} async. tasks for geometric calculation...')

        _pool = [ GeomTask() for ii in range(count_) ]
        for ii in range(count_):
            _tsk = _pool[ii]
            _tsk.Start(1.7+ii, bCalcArea_=ii%2)

        res, _FMT = '', '\n\t[{}] circle radius : {:<.2f}  ,  {:>12s} : {:<.4f}'
        for ii in range(count_):
            _tsk = _pool[ii]
            _tsk.Join()
            res += _FMT.format(_tsk.aliasName, 1.7+ii, 'enclosedArea' if ii%2 else 'perimeter', _tsk.geomCalc)
        return res
#END class GeomTask


def Main(cmdLineOpts_ : CLOptions):
    """
    Entry point of a Python program demonstrating typical use of the framework
    of XCOFDK by multithreaded applications. Representing a quite simple
    example:
        - it creates application's main task with synchronous execution type,
          which is executed by the framework from within program's entry point
          'Main()', that is synchronously to program's 'MainThread',
        - the main task, on the other hand, creates a few asynchronous tasks
          each performing some geometric calculation for the passed arguments
          when started.

    Parameters:
    -------------
        - cmdLineOpts_ :
          an object representing submitted cmdline options

    Returns:
    ----------
        - a positive integer value indicating the encountered error (if any),
          0 otherwise.
    """

    # step 1: configure framework's RTE for experimental free-threaded Python (if enabled via CmdLine)
    if cmdLineOpts_.isFreeThreadingGuardBypassed:
        rtecfg.RtePolicyBypassExperimentalFreeThreadingGuard()

    # step 2: start framework
    if not fwapi.StartXcoFW(fwStartOptions_=cmdLineOpts_.GetSuppliedFwOptions()):
        return 71

    # step 3: create application's starter task
    _bMainTsk = cmdLineOpts_.isMainStarterTaskEnabled
    _bSyncTsk = cmdLineOpts_.isSyncStarterTaskEnabled
    _myTsk = MainTask(bSyncTask_=_bSyncTsk) if _bMainTsk else StarterTask(bSyncTask_=_bSyncTsk)

    # step 4: start application's starter task
    _myTsk.Start()

    # step 5: wait for framework's coordinated shutdown
    _bLcErrorFree = fwapi.JoinXcoFW()

    # done: check for LC failure (if any)
    res = 72 if not _bLcErrorFree else 0
    return res
#END Main()


# ------------------------------------------------------------------------------
# Execution
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    _opts = [ ECLOptionID.eSyncStarterTask, ECLOptionID.eNoMainStarterTask ]
    _cl   = GetCmdLineOptions(_opts)
    if (_cl is None) or _cl.isHelpSupplied:
        _xc = 1 if _cl is None else 0
    else:
        _xc = Main(_cl)
    exit(_xc)
