# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : quickStart.py
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
from enum      import auto, IntEnum
from threading import current_thread  # for demonstration purposes only
from typing    import List
from datetime  import datetime

from xcofdk       import fwapi
from xcofdk.fwcom import EExecutionCmdID, EXmsgPredefinedID
from xcofdk.fwapi import rtecfg, IRCTask, IRCCommTask
from xcofdk.fwapi import SyncTask, AsyncTask, MessageDrivenTask
from xcofdk.fwapi import GetCurTask, IMessage, XProcess, xlogif

from xuserapp.util.cloptions   import ECLOptionID, CLOptions, GetCmdLineOptions
from xuserapp.util.userAppUtil import CartProdAlgo, DisableBigCartProd


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class EMsgLabel(IntEnum):
    DontCare    = EXmsgPredefinedID.MinUserDefinedID.value
    AlgoRequest = auto()
    Quit        = auto()

def AlgoServerCBTgt(myTsk_ : IRCCommTask, msg_ : IMessage) -> EExecutionCmdID:
    # very first message?
    if myTsk_.isFirstRunPhaseIteration:
        xlogif.LogInfo(f'Task {myTsk_.aliasName} received first delivered message.')

        # put an own CP-request
        CartProdAlgo(tid_=f'{myTsk_.taskUID}:{myTsk_.aliasName}')

    _lbl = msg_.msgHeader.msgLabel

    # dont-care message?
    if _lbl == EMsgLabel.DontCare:
        # ignore, wait for next message
        return EExecutionCmdID.CONTINUE

    # request to quit?
    if _lbl != EMsgLabel.AlgoRequest:
        # put last own CP-request
        CartProdAlgo(tid_=f'{myTsk_.taskUID}:{myTsk_.aliasName}')

        # framework has been started in TerminalMode?
        if rtecfg.RtePolicyGetConfig().isTerminalModeEnabled:
            # wait for running child processes to complete
            fwapi.JoinProcesses()

            # instruct the framework to stop
            fwapi.StopXcoFW()
            xlogif.LogInfo(f'Put request to stop the framework.')

        # stop the algo server
        return EExecutionCmdID.STOP

    # put a new CP-request on behalf of the sender
    CartProdAlgo(tid_=msg_.msgHeader.msgSender)

    # wait for next message
    return EExecutionCmdID.CONTINUE

def AlgoClientCBTgt(myTsk_ : IRCTask, srvUID_ : int) -> EExecutionCmdID:
    # already done 4x CP-requests?
    if myTsk_.currentRunPhaseIterationNo >= 4:
        # stop running
        return EExecutionCmdID.STOP

    # delegate next CP-request to algo-server, or do it yourself
    _bDelegate = (myTsk_.taskCompoundUID.instNo + myTsk_.currentRunPhaseIterationNo) % 2
    if _bDelegate:
        myTsk_.SendMessage(srvUID_, EMsgLabel.AlgoRequest)
    else:
        CartProdAlgo(tid_=f'{myTsk_.taskUID}:{myTsk_.aliasName}')

    # continue running
    return EExecutionCmdID.CONTINUE

def CreateStartAlgoProcesses(count_ : int) -> List[XProcess]:
    res = []
    for _ii in range(count_):
        _pp = XProcess(CartProdAlgo)
        res.append(_pp)

    xlogif.LogInfo(f'Starting {count_}x child processes...')
    for _pp in res:
        _pp.Start(bRequestByParentProc_=True)

    res = [ _pp for _pp in res if _pp.isStarted ]
    return res

def CreateStartAlgoClients(count_ : int, srvUID_ : int) -> list:
    res = [ AsyncTask( runCallback_=AlgoClientCBTgt, aliasName_='AlgoC_', bRefToCurTaskRequired_=True
                     , runCallbackFrequency_=(_ii+1)*20) for _ii in range(count_) ]
    xlogif.LogInfo(f'Starting {count_}x async. algo-client tasks...')
    for _cc in res:
        _cc.Start(srvUID_)
    return res

def StarterTaskCBTgt(srvUID_ : int, count_ : int, procPool_ : List[XProcess]) -> EExecutionCmdID:
    _curTsk = GetCurTask()

    _msg  = 'Running {} {}'.format('sync.' if _curTsk.isSyncTask else 'async.', _curTsk.aliasName)
    _msg += f', current host thread: {current_thread().name}'
    xlogif.LogInfo(_msg)

    # send first CP-request to algo-server
    _curTsk.SendMessage(srvUID_, EMsgLabel.AlgoRequest)

    # create and start child processes
    procPool_ += CreateStartAlgoProcesses(count_)

    # create and start client tasks
    _clientPool = CreateStartAlgoClients(count_, srvUID_)

    # wait for termination of client tasks
    fwapi.JoinTasks([_cc.taskUID for _cc in _clientPool])
    if not _curTsk.SelfCheck():
        xlogif.LogFatal('Encountered unexpected self-error.')

    # collect the CP-results of client tasks and store them as own (user) data
    _ud = []
    for _cc in _clientPool:
        if _cc.GetTaskOwnedData() is not None:
            _ud += _cc.GetTaskOwnedData()
    _curTsk.SetTaskOwnedData(_ud)

    # send last CP-request to algo-server
    _curTsk.SendMessage(srvUID_, EMsgLabel.AlgoRequest)

    # put request to algo-server to quit
    _curTsk.SendMessage(srvUID_, EMsgLabel.Quit)

    # done, stop the starter task
    return EExecutionCmdID.STOP

def CreateStartStarterTask(cmdLineOpts_ : CLOptions, srvUID_ : int, count_ : int, procPool_ : List[XProcess]):
    _bMainTsk  = cmdLineOpts_.isMainStarterTaskEnabled
    _alias     = 'MainTask' if _bMainTsk else 'StarterTask'
    if cmdLineOpts_.isSyncStarterTaskEnabled:
        res = SyncTask(runCallback_=StarterTaskCBTgt, aliasName_=_alias, bMainTask_=_bMainTsk)
    else:
        res = AsyncTask(runCallback_=StarterTaskCBTgt, aliasName_=_alias, bMainTask_=_bMainTsk)

    _msg = 'TerminalMode' if rtecfg.RtePolicyGetConfig().isTerminalModeEnabled else 'AutoStop mode'
    _msg = f'Welcome to XCOFDK in {_msg} of RTE.'
    xlogif.LogInfo(_msg)

    # start (a)sync. starter task and wait until all child processes have been started
    res.Start(srvUID_, count_, procPool_)
    while res.isRunning:
        if len(procPool_):
            break
    return res

def Main(cmdLineOpts_ : CLOptions):
    _startTime = datetime.now()

    # step 1: configure framework's RTE for terminal mode and/or
    #         experimental free-threaded Python (if enabled via CmdLine)
    if cmdLineOpts_.isSmallCartProdEnabled:
        DisableBigCartProd()
        rtecfg.RtePolicyEnableTerminalMode()
    if cmdLineOpts_.isFreeThreadingGuardBypassed:
        rtecfg.RtePolicyBypassExperimentalFreeThreadingGuard()

    # step 2: start framework
    if not fwapi.StartXcoFW(fwStartOptions_=cmdLineOpts_.GetSuppliedFwOptions()):
        return 71

    # step 3: create and start appplication's algo-server task
    _algoSrv = MessageDrivenTask(AlgoServerCBTgt, aliasName_='AlgoSrv', bRefToCurTaskRequired_=True, pollingFrequency_=20)
    _algoSrv.Start()

    # step 4: create and start appplication's starter task
    #         (which will create and start both child processes and client tasks, too)
    _count, _procPool = 5, []
    _starterTsk = CreateStartStarterTask(cmdLineOpts_, _algoSrv.taskUID, _count, _procPool)

    # step 5: if not in terminal mode, wait for running child processes to complete
    if not rtecfg.RtePolicyGetConfig().isTerminalModeEnabled:
        fwapi.JoinProcesses()

    # step 6: wait for framework's coordinated shutdown
    _bLcErrorFree = fwapi.JoinXcoFW()

    # step 7: collect and print out results of CP requests executed
    if _bLcErrorFree:
        _procPoolRes = [_pp.processSuppliedData for _pp in _procPool if _pp.processSuppliedData is not None]
        _cp  = _procPoolRes + _starterTsk.GetTaskOwnedData() + _algoSrv.GetTaskOwnedData()
        _cp.sort(key=lambda _ee: _ee.cartProdTimestamp)
        _cpLEN = len(_cp)
        _cp = '\n\t'.join( [str(_ee) for _ee in _cp] )

        _msg1 = 'small' if cmdLineOpts_.isSmallCartProdEnabled else 'big'
        _msg2 = f'Got total of {_cpLEN}x {_msg1} CartProdAlgo executions:\n\t{_cp}'
        xlogif.LogInfo(_msg2)
        xlogif.LogInfo(f'Done, elapsed time for {_msg1} CartProdAlgo: ' + str(datetime.now()-_startTime))

    # done: check for LC failure (if any)
    res = 72 if not _bLcErrorFree else 0
    return res


# ------------------------------------------------------------------------------
# Execution
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    _opts = [ ECLOptionID.eSyncStarterTask, ECLOptionID.eNoMainStarterTask, ECLOptionID.eSmallCartProd, ECLOptionID.eBypassFTGuard ]
    _cl   = GetCmdLineOptions(_opts, bAddCommonAppOptions_=False)
    if (_cl is None) or _cl.isHelpSupplied:
        exit(1 if _cl is None else 0)
    exit(Main(_cl))
