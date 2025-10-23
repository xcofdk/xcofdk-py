# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : quickStartMP.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# PYTHONPATH extension
# ------------------------------------------------------------------------------
import os, sys
_xcoRP = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../../../..'))
if _xcoRP.endswith('/src') and os.path.exists(os.path.join(_xcoRP, 'xcofdk')) and _xcoRP not in sys.path: sys.path.extend([_xcoRP])
try:
    import xcofdk
except ImportError:
    exit(f"[{os.path.basename(__file__)}] Failed to import Python package 'xcofdk', missing installation.")
sys.path.extend(((_xua := os.path.normpath(os.path.join(os.path.dirname(__file__), '../../..'))) not in sys.path) * [_xua])


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from os        import getpid          # for demonstration purposes only
from threading import current_thread  # ditto
from time      import sleep           # ditto

from xcofdk       import fwapi
from xcofdk.fwcom import EExecutionCmdID
from xcofdk.fwapi import rtecfg
from xcofdk.fwapi import xlogif
from xcofdk.fwapi import XProcess
from xcofdk.fwapi import SyncTask
from xcofdk.fwapi import AsyncTask
from xcofdk.fwapi import GetCurTask

from xuserapp.util.cloptions import ECLOptionID
from xuserapp.util.cloptions import CLOptions
from xuserapp.util.cloptions import GetCmdLineOptions


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
def _WelcomeMP(procName_ : str, waitTimeSec_ : float =1.0):
    print(f'\n****[PID::{getpid()}] Process {procName_} welcomes you to MP.')
    sleep(waitTimeSec_)
    print(f'\n****[PID::{getpid()}] Finished execution of {procName_}, see you next time.')
    return f'Greeting to parent process from child process {getpid()}.'
#END _WelcomeMP()


def MainTaskTgt() -> EExecutionCmdID:
    _mainTsk = GetCurTask()

    # create a new child process with its target set to '_WelcomeMP()' defined above
    _proc  = XProcess(_WelcomeMP, aliasName_='DemoProc_')
    if not _proc.isAttachedToFW:
        return EExecutionCmdID.ABORT

    # start child process
    _msg = 'Sync.' if _mainTsk.isSyncTask else 'Async.'
    _msg = f'{_msg} {_mainTsk.aliasName} wlecomes you to MP of XCOFDK, current host thread: {current_thread().name}'
    xlogif.LogInfo(_msg)
    xlogif.LogInfo(f'Starting child process {_proc.aliasName}...')
    _proc.Start(_proc.aliasName, waitTimeSec_=3.0)

    _ii = 0
    while True:
        # child process not running anymore?
        if not _proc.isRunning:
            break

        _ii += 1
        if _ii==1 or (_ii%10)==0:
            xlogif.LogInfo(f'Waiting for child process {_proc.aliasName}::{_proc.processPID} to finish...')

        # do whatever else to do (or just go to sleep for a short while)
        sleep(0.1)

    # wait for termination of child process
    _proc.Join()

    _msg  = f'Done, child process {_proc.aliasName}::{_proc.processPID} finished execution:'
    _msg += f'\n\t{_proc}\n\tdata supplied by child process:  {_proc.processSuppliedData}'
    xlogif.LogInfo(_msg)

    return EExecutionCmdID.STOP
#END MainTaskTgt()


def Main(cmdLineOpts_ : CLOptions):
    # optional: disable subsystem xmsg
    rtecfg.RtePolicyDisableSubSystemMessaging()

    # step 1: configure framework's RTE for experimental free-threaded Python (if enabled via CmdLine)
    if cmdLineOpts_.isFreeThreadingGuardBypassed:
        rtecfg.RtePolicyBypassExperimentalFreeThreadingGuard()

    # step 2: start framework
    if not fwapi.StartXcoFW(fwStartOptions_=cmdLineOpts_.GetSuppliedFwOptions()):
        return 71

    # step 3: create (a)synchronous main task
    if cmdLineOpts_.isAsynMainTaskEnabled:
        _mtsk = AsyncTask( runCallback_=MainTaskTgt, aliasName_='MainTask', bMainTask_=True)
    else:
        _mtsk = SyncTask(runCallback_=MainTaskTgt, aliasName_='MainTask', bMainTask_=True)

    # step 4: start main task
    _mtsk.Start()

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
    _opts = [ ECLOptionID.eAsyncMainTask, ECLOptionID.eBypassFTGuard ]
    _cl   = GetCmdLineOptions(_opts, bAddCommonAppOptions_=False)
    if (_cl is None) or _cl.isHelpSupplied:
        _xc = 1 if _cl is None else 0
    else:
        _xc = Main(_cl)
    exit(_xc)
