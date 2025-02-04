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
from math      import pi             as _PI
from math      import pow            as _POW
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
        super().__init__(taskProfile_=_tp)

    @override
    def RunXTask(self) -> ETernaryCallbackResultID:
        _msg  = 'sync.' if self.xtaskProfile.isSynchronousTask else 'async.'
        _msg  = f'Welcome to XCOFDK by {_msg} {self.xtaskAliasName}:'
        _msg += f'\n\tcurrent host thread : {_PyCurThread().name}'
        xlogif.LogInfo(_msg)

        xlogif.LogInfo('Starting a few async. tasks for geometric calculation...')
        _msg = GeomTask.CreateStartGeomPool()
        xlogif.LogInfo(f'Done, result:{_msg}')

        xlogif.LogInfo(f'Going to stop the run-phase of {self.xtaskAliasName}...')
        return ETernaryCallbackResultID.STOP
#END class AppMainTask


class AppTask(XTask):
    def __init__(self, bSynchronousTask_ =False):
        if bSynchronousTask_:
            _tp = XTaskProfile.CreateSynchronousTaskProfile(aliasName_='appTask')
        else:
            _tp = XTaskProfile.CreateAsynchronousTaskProfile(aliasName_='appTask')
        super().__init__(taskProfile_=_tp)

    @override
    def RunXTask(self) -> ETernaryCallbackResultID:
        _msg  = 'sync.' if self.xtaskProfile.isSynchronousTask else 'async.'
        _msg  = f'Welcome to XCOFDK by {_msg} {self.xtaskAliasName}:'
        _msg += f'\n\tcurrent host thread : {_PyCurThread().name}'
        xlogif.LogInfo(_msg)

        xlogif.LogInfo('Starting a few async. tasks for geometric calculation...')
        _msg = GeomTask.CreateStartGeomPool()
        xlogif.LogInfo(f'Done, result:{_msg}')

        xlogif.LogInfo(f'Going to stop the run-phase of {self.xtaskAliasName}...')
        return ETernaryCallbackResultID.STOP
#END class AppTask


class GeomTask(XTask):
    def __init__(self, index_ : int):
        self.geomCalc = 0
        _tp = XTaskProfile.CreateAsynchronousTaskProfile(aliasName_=f'geomTask_{index_}')
        super().__init__(taskProfile_=_tp)

    @override
    def RunXTask(self, radius_ : float, bCalcArea_ =False) -> ETernaryCallbackResultID:
        self.geomCalc = _PI*_POW(radius_, 2) if bCalcArea_ else 2*_PI*radius_
        return ETernaryCallbackResultID.STOP

    @staticmethod
    def CreateStartGeomPool(size_ : int =5) -> str:
        _pool = [ GeomTask(ii) for ii in range(size_) ]
        for ii in range(size_):
            _tsk = _pool[ii]
            _tsk.Start(1.7+ii, bCalcArea_=ii%2)

        res, _FMT = '', '\n\t[{}] circle radius : {:<.2f}  ,  {:>12s} : {:<.4f}'
        for ii in range(size_):
            _tsk = _pool[ii]
            _tsk.Join()
            res += _FMT.format(_tsk.xtaskAliasName, 1.7+ii, 'enclosedArea' if ii%2 else 'perimeter', _tsk.geomCalc)
        return res
#END class GeomTask


def Main(bSyncTask_ =False, bUseMainTask_ =True, fwStartOptions_ : list =None):
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
    _lstFW_START_OPTIONS    = [ '--disable-log-timestamp' , '--disable-log-highlighting' , '--enable-log-callstack' ]
    _lstQUICK_START_OPTIONS = [ '--use-sync-task', '--no-main-task' ]

    _bSync, _bMain, _lstOptions = False, True, []
    for aa in sys.argv:
        if aa == '--help':
            _usage = os.path.splitext(os.path.basename(sys.argv[0]))[0]
            _usage = f'Usage:\n\t$> python3 -m {_usage} [--help] [--use-sync-task] [--no-main-task] [--disable-log-timestamp] [--disable-log-highlighting] [--enable-log-callstack]'
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
