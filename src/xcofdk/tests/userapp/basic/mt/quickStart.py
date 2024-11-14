# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : quickStart.py
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
from threading import current_thread as _PyCurThread

from xcofdk             import fwapi
from xcofdk.fwcom       import ETernaryCallbackResultID
from xcofdk.fwcom       import xlogif
from xcofdk.fwcom       import override
from xcofdk.fwapi.xtask import XTask
from xcofdk.fwapi.xtask import MainXTask
from xcofdk.fwapi.xtask import XTaskProfile


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class AppMainTask(MainXTask):
    def __init__(self, bSynchronousTask_ =True):
        if bSynchronousTask_:
            _tp = XTaskProfile.CreateSynchronousTaskProfile(aliasName_='appMainTask')
        else:
            _tp = XTaskProfile.CreateAsynchronousTaskProfile(aliasName_='appMainTask')
        MainXTask.__init__(self, taskProfile_=_tp)

    @override
    def RunXTask(self) -> ETernaryCallbackResultID:
        _msg  = 'sync.' if self.xtaskProfile.isSynchronousTask else 'async.'
        _msg  = f'Welcome to XCOFDK by {_msg} {self.xtaskAliasName}:'
        _msg += f'\n\tcurrent host thread : {_PyCurThread().name}'
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
        _msg  = 'sync.' if self.xtaskProfile.isSynchronousTask else 'async.'
        _msg  = f'Welcome to XCOFDK by {_msg} {self.xtaskAliasName}:'
        _msg += f'\n\tcurrent host thread : {_PyCurThread().name}'
        xlogif.LogInfo(_msg)
        return ETernaryCallbackResultID.STOP
#END class AppTask


def Main(bSyncTask_ =False, bUseMainTask_ =True, fwStartOptions_ : list =None):
    """
    Entry point of a Python program demonstrating typical use of the framework
    of XCOFDK by multithreaded applications.

    Representing a quite simple example, it creates an application task serving
    as its 'starting task' which is executed by the framework. Note that the
    applicatiion may also opt to create and start additional tasks from within
    this entry point, or at some time later from within its starting task.

    Parameters:
    -------------
        - bSyncTask_ :
          configure application's starting task to be synchronous if set to
          True, or to be asynchronous otherwise.
        - bUseMainTask_ :
          application's starting task is the main task if set to True, or a
          regular task otherwise.
        - fwStartOptions_ :
          a subset of available framework start options (if any).
          See documentation of 'xcofdk.fwapi.StartXcoFW()'

    Returns:
    ----------
        - a positive integer value indicating the encountered error (if any),
          0 otherwise.
    """

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
        if aa == '--help':
            _usage = os.path.splitext(os.path.basename(sys.argv[0]))[0]
            _usage = f'Usage:\n\t$> python3 -m {_usage} [--help] [--use-sync-task] [--no-main-task] [--disable-log-timestamp] [--disable-log-highlighting]'
            print(_usage)
            return None, None, None

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
    if _bSyncTask is None:
        exit(0)
    exit(Main(bSyncTask_=_bSyncTask, bUseMainTask_=_bUseMainTask, fwStartOptions_=_lstStartOptions))
