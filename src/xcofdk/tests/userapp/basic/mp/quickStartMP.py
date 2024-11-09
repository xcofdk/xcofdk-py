# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : quickStartMP.py
#
# Copyright(c) 2023-2024 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
import os
import sys
sys.path.extend(((_xcoRootPath := os.path.normpath(os.path.join(os.path.dirname(__file__), '../../../../..'))) not in sys.path) * [_xcoRootPath])

# for demonstration purposes only
from os   import getpid as _PyGetPID
from time import sleep  as _PySleep

from xcofdk                import fwapi
from xcofdk.fwcom          import ETernaryCallbackResultID
from xcofdk.fwcom          import xlogif
from xcofdk.fwcom          import override
from xcofdk.fwcom.xmpdefs  import ChildProcessResultData
from xcofdk.fwapi.xtask    import XTask
from xcofdk.fwapi.xtask    import MainXTask
from xcofdk.fwapi.xtask    import XTaskProfile
from xcofdk.fwapi.xprocess import XProcess


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
def _WelcomeMP(procResData_ : ChildProcessResultData, procName_ : str):
    print(f'\n****[PID::{_PyGetPID()}] Process {procName_} welcomes you to MP.')
    _PySleep(3)
    print(f'\n****[PID::{_PyGetPID()}] Finished execution of {procName_}, see you next time.')
    procResData_.exitCode   = 0
    procResData_.resultData = f'Greeting to parent process from child process {_PyGetPID()}.'
#END _WelcomeMP()


class AppMainTask(MainXTask):
    def __init__(self, bSynchronousTask_ =True):
        if bSynchronousTask_:
            _tp = XTaskProfile.CreateSynchronousTaskProfile(aliasName_='appMainTask')
        else:
            _tp = XTaskProfile.CreateAsynchronousTaskProfile(aliasName_='appMainTask')
        MainXTask.__init__(self, taskProfile_=_tp)

    @override
    def RunXTask(self) -> ETernaryCallbackResultID:
        # create a new child process with its target set to '_WelcomeMP()' defined above
        _pname = 'demoProc'
        _proc  = XProcess(_WelcomeMP, name_=_pname, args_=(_pname,))
        if not _proc.isAttachedToFW:
            return ETernaryCallbackResultID.ABORT

        # start child process
        xlogif.LogInfo(f'Task {self.xtaskAliasName} starting child process {_proc.xprocessName}...')
        _proc.Start()

        _ii = 0
        while True:
            # child process not running anymore?
            if not _proc.isRunning:
                break

            _ii += 1
            if _ii==1 or (_ii%10)==0:
                xlogif.LogInfo(f'Waiting for child process {_proc.xprocessName}::{_proc.xprocessPID} to finish...')

            # do whatever else to do (or just go to sleep for a short while)
            _PySleep(0.1)

        # wait for termination of child process
        _proc.Join()

        _msg  = f'Done, child process {_proc.xprocessName}::{_proc.xprocessPID} finished execution:'
        _msg += f'\n\tresult data received from child:  {_proc.xprocessResult.resultData}'
        xlogif.LogInfo(_msg)

        return ETernaryCallbackResultID.STOP
#END class AppMainTask


class AppTask(XTask):
    def __init__(self, bSynchronousTask_ =False):
        if bSynchronousTask_:
            _tp = XTaskProfile.CreateSynchronousTaskProfile(aliasName_='appTask')
        else:
            _tp = XTaskProfile.CreateAsynchronousTaskProfile(aliasName_='appTask')
        XTask.__init__(self, taskProfile_=_tp)

    @override
    def RunXTask(self) -> ETernaryCallbackResultID:
        # create a new child process
        _pname = 'demoProc'
        _proc  = XProcess(_WelcomeMP, name_=_pname, args_=(_pname,))
        if not _proc.isAttachedToFW:
            return ETernaryCallbackResultID.ABORT

        # start child process
        xlogif.LogInfo(f'Task {self.xtaskAliasName} starting child process {_proc.xprocessName}...')
        _proc.Start()

        _ii = 0
        while True:
            # child process not running anymore?
            if not _proc.isRunning:
                break

            _ii += 1
            if _ii==1 or (_ii%10)==0:
                xlogif.LogInfo(f'Waiting for child process {_proc.xprocessName}::{_proc.xprocessPID} to finish...')

            # do whatever else to do (or just go to sleep for a short while)
            _PySleep(0.1)

        # wait for termination of child process
        _proc.Join()

        _msg  = f'Done, child process {_proc.xprocessName}::{_proc.xprocessPID} finished execution:'
        _msg += f'\n\tresult data received from child:  {_proc.xprocessResult.resultData}'
        xlogif.LogInfo(_msg)

        return ETernaryCallbackResultID.STOP
#END class AppTask


def Main(bSyncTask_ =False, bUseMainTask_ =True, fwStartOptions_ : list =None):
    # step 1: start framework
    if not fwapi.StartXcoFW(fwStartOptions_=fwStartOptions_):
        return 71

    # step 2: create and start application's starting task
    _myTsk = AppMainTask(bSynchronousTask_=bSyncTask_) if bUseMainTask_ else AppTask(bSynchronousTask_=bSyncTask_)
    _myTsk.Start()

    # step 3: wait for starting task's termination
    _myTsk.Join()

    # step 4: stop framework
    fwapi.StopXcoFW()

    # step 5: wait for framework's coordinated shutdown
    _bLcErrorFree = fwapi.JoinXcoFW()

    # step 6: check for LC failure (if any)
    res = 72 if not _bLcErrorFree else 0
    return res
#END Main()


def _ScanCmdLine():
    _lstFW_START_OPTIONS    = [ '--disable-log-timestamp' , '--disable-log-highlighting' ]
    _lstQUICK_START_OPTIONS = [ '--use-sync-task', '--no-main-task' ]

    _bSync, _bMain, _lstOptions = False, True, []
    for aa in sys.argv:
        if aa in _lstFW_START_OPTIONS:
            _lstOptions.append(aa)
            continue
        if aa in _lstQUICK_START_OPTIONS:
            if _lstQUICK_START_OPTIONS.index(aa) == 0:
                _bSync = True
            else:
                _bMain = False
            continue
    return _bSync, _bMain, _lstOptions
#END _ScanCmdLine()


# ------------------------------------------------------------------------------
# Execution
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    _bSyncTask, _bUseMainTask, _lstStartOptions = _ScanCmdLine()
    exit(Main(bSyncTask_=_bSyncTask, bUseMainTask_=_bUseMainTask, fwStartOptions_=_lstStartOptions))
