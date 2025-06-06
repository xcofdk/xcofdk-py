# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : servicetaskGIL.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from xcofdk.fwcom import EExecutionCmdID
from xcofdk.fwapi import IMessage
from xcofdk.fwapi import fwutil
from xcofdk.fwapi import xlogif
from xcofdk.fwapi import IRCCommTask
from xcofdk.fwapi import XFAsyncCommTask
from xcofdk.fwapi import GetCurTask

from xuserapp.util.userAppUtil              import UserAppUtil
from xuserapp.st.welcome.interfaces.modelif import ServiceTaskGilSpec

from xuserapp.basic.xmt.xmtmisc.commondefs import EMsgLabelID
from xuserapp.basic.xmt.xmtmisc.commondefs import EMsgParamKeyID


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
def CreateServiceTaskGIL(srvTaskNo_ : int, gilSpec_ : ServiceTaskGilSpec) -> IRCCommTask:
    _aliasName        = 'ServiceTaskGIL_{:02d}'.format(srvTaskNo_)
    _phasedXFCallback = XFServiceTaskGIL(gilSpec_)
    _runPhaseFreqMS   = gilSpec_.deficientRunPhaseFrequencyMS if gilSpec_.isDeficientFrequencyForced else gilSpec_.runPhaseFrequencyMS
    res = XFAsyncCommTask(_phasedXFCallback, aliasName_=_aliasName, runCallbackFrequency_=_runPhaseFreqMS)
    return res
#END CreateServiceTaskGIL()


class XFServiceTaskGIL:

    __slots__ = [ '__ctrRun' , '__ctrSnd' , '__ctrRcv' , '__mainTaskID' , '__ctrErrSnd'
                , '__bGilPaused' , '__ctrOutOfOrder' , '__lastRcvUID' , '__fiboInput', '__myCTsk' ]

    __myFiboCache = { 0:0, 1:1 }

    def __init__(self, gilSpec_ : ServiceTaskGilSpec):
        self.__ctrRun        = 0
        self.__ctrSnd        = 0
        self.__ctrRcv        = 0
        self.__ctrErrSnd     = 0
        self.__ctrOutOfOrder = 0

        self.__myCTsk     = None
        self.__mainTaskID = None
        self.__lastRcvUID = None
        self.__bGilPaused = False
        self.__fiboInput  = gilSpec_.fibonacciInput


    # --------------------------------------------------------------------------
    # phasedXF callbacks
    # --------------------------------------------------------------------------
    def RunTask(self) -> EExecutionCmdID:
        #xlogif.LogDebug(f'[mtGuiAppService] Executing run-phase of service xtask {self.taskProfile.aliasName}...')
        if self.__myCTsk is None:
            self.__myCTsk = GetCurTask()
        self.__ctrRun += 1

        # main task's (unique task) ID not known yet?
        if self.__mainTaskID is None:
            return EExecutionCmdID.CONTINUE

        # posting paused?
        if self.__bGilPaused:
            return EExecutionCmdID.CONTINUE

        # perform fibo calculation
        UserAppUtil.Fibonacci(self.__fiboInput)

        # we have done some non-trivail execution, so check if we're still running?
        if not self.__myTask.isRunning:
           return EExecutionCmdID.STOP

        _bDoSend = False
        if (self.__myTask.runPhaseFrequencyMS*self.__ctrRun) >= 500:
            self.__ctrRun = 0

            # send next message in a frequency of 500ms
            _bDoSend = True

        res = True
        if _bDoSend:
            res = self.__PostMessage()
        return EExecutionCmdID.FromBool(res)

    def ProcessExternalMessage(self, xmsg_ : IMessage) -> EExecutionCmdID:
        if self.__lastRcvUID is None:
            pass
        else:
            if xmsg_.msgUniqueID <= self.__lastRcvUID:
                self.__ctrOutOfOrder += 1
                xlogif.LogWarning('[mtGuiAppService][#outOfOrder={}] Received out-of-order message {}, last received one was {}.'.format(
                    self.__ctrOutOfOrder, xmsg_.msgUniqueID, self.__lastRcvUID))

        self.__lastRcvUID = xmsg_.msgUniqueID

        # increment number of messages received from main task
        self.__ctrRcv += 1

        # main task's (unique task) ID not set yet?
        if self.__mainTaskID is None:
            # use unique task ID of the main task
            self.__mainTaskID = xmsg_.msgHeader.msgSender

        res = True

        # instruction to pause fibonacci calculation?
        if xmsg_.msgHeader.msgLabel == EMsgLabelID.ePauseGIL:
            self.__bGilPaused = True

            # try to send a last message so the receiver is up-to-date with regard to the count of both received and sent messages
            res = self.__PostMessage()

        # instruction to resume fibonacci calculation?
        elif xmsg_.msgHeader.msgLabel == EMsgLabelID.eResumeGIL:
            self.__bGilPaused = False

        # ignore whatever else
        else:
            pass

        return EExecutionCmdID.FromBool(res)
    # --------------------------------------------------------------------------
    #END phasedXF callbacks
    # --------------------------------------------------------------------------


    # --------------------------------------------------------------------------
    # Impl / protected API
    # --------------------------------------------------------------------------
    @property
    def __myTask(self) -> IRCCommTask:
        return self.__myCTsk

    def __PostMessage(self) -> bool:
        # not running anymore?
        if not self.__myTask.isRunning:
            return False

        #[NOTE]
        #  - optional:
        #      turn on flag below to pre-check the availability of the main task before trying to send next message to.
        #      This is basically useful to avoid annoying user errors reported by the framework.
        #  - by application design, the main task stops all its services before leaving its run-phase,
        #  - so, a pre-check is not really necessary, as the main task is expected to be available and running
        #    as long as its services are still running.
        #
        _bPreCheckForMainTaskAvailability = False
        if _bPreCheckForMainTaskAvailability:
            if not fwutil.IsTaskRunning(self.__mainTaskID):
                return False

        self.__ctrSnd += 1

        _payload = { EMsgParamKeyID.eNumSendFailures       : self.__ctrErrSnd
                   , EMsgParamKeyID.eNumOutOfOrderReceived : self.__ctrOutOfOrder
                   }

        # clear current error (if any)
        self.__myTask.ClearCurrentError()

        _xmsgUID = self.__myTask.SendMessage(self.__mainTaskID, msgLabelID_=EMsgLabelID.eServiceTaskInfo, msgPayload_=_payload)

        res = _xmsgUID > 0

        # failed to send message?
        if not res:
            # something went wrong, decrement sent counter
            self.__ctrSnd    -= 1
            self.__ctrErrSnd += 1

            #[NOTE] 'self.currentError' is always set upon send failure  !!
            #
            xlogif.LogWarning(f'[mtGuiAppService][#sendErrors={self.__ctrErrSnd}] Failed to send xco message to xtask {self.__mainTaskID}.')
        else:
            #xlogif.LogDebug('[mtGuiAppService] Sent xco-message {}.'.format(msgUID))
            pass
        return res
    # --------------------------------------------------------------------------
    #END Impl / protected API
    # --------------------------------------------------------------------------
#END class XFServiceTaskGIL
