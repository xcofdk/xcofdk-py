# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : servicetaskBXQ.py
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
from xcofdk.fwapi import XFMessageDrivenTask
from xcofdk.fwapi import GetCurTask

from xuserapp.basic.xmt.xmtmisc.commondefs import EMsgLabelID
from xuserapp.basic.xmt.xmtmisc.commondefs import EMsgParamKeyID


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
def CreateServiceTaskBXQ(srvTaskNo_ : int) -> IRCCommTask:
    _aliasName = 'ServiceTask_BXQ{:02d}'.format(srvTaskNo_)
    return XFMessageDrivenTask(XFServiceTaskBXQ, aliasName_=_aliasName, pollingFrequency_=20)
#END CreateServiceTaskBXQ()


class XFServiceTaskBXQ:

    __slots__ = [ '__ctrSnd' , '__ctrRcv' , '__ctrErrSnd' , '__mainTaskID'
                , '__lastRcvUID' , '__bPostingPaused' , '__ctrOutOfOrder' , '__myCTsk' ]

    def __init__(self):
        self.__ctrSnd         = 0
        self.__ctrRcv         = 0
        self.__ctrErrSnd      = 0
        self.__ctrOutOfOrder  = 0

        self.__myCTsk         = None
        self.__mainTaskID     = None
        self.__lastRcvUID     = None
        self.__bPostingPaused = False


    # --------------------------------------------------------------------------
    # phasedXF callbacks
    # --------------------------------------------------------------------------
    def ProcessExternalMessage(self, xmsg_ : IMessage) -> EExecutionCmdID:
        if self.__myCTsk is None:
            _myCTsk       = GetCurTask()
            self.__myCTsk = _myCTsk

            #
            _msg = "For demo-purposes only, id-check of 'self' and 'phasedXFInstance':  {} vs. {}"
            xlogif.LogInfo(_msg.format(id(self), id(_myCTsk.phasedXFInstance)))

        # check for out-of-order message
        if self.__lastRcvUID is None:
            pass
        elif xmsg_.msgUniqueID <= self.__lastRcvUID:
            self.__ctrOutOfOrder += 1
            xlogif.LogWarning('[mtGuiAppServiceBXQ][#outOfOrder={}] Received out-of-order message {}, last received one was {}.'.format(
                self.__ctrOutOfOrder, xmsg_.msgUniqueID, self.__lastRcvUID))
        self.__lastRcvUID = xmsg_.msgUniqueID

        res = True

        # increment number of messages received from main task
        self.__ctrRcv += 1

        # main task's (unique task) ID not set yet?
        if self.__mainTaskID is None:
            # use unique task ID of the main task
            self.__mainTaskID = xmsg_.msgHeader.msgSender

        # instruction to pause posting?
        if xmsg_.msgHeader.msgLabel == EMsgLabelID.ePausePosting:
            self.__bPostingPaused = True

            # try to send a last message so the receiver is up-to-date with regard to the count of both received and sent messages
            res = self.__PostMessage()

        # instruction to resume posting?
        elif xmsg_.msgHeader.msgLabel == EMsgLabelID.eResumePosting:
            self.__bPostingPaused = False

        # external queue configured to be blocking?
        elif self.__myTask.isExternalQueueBlocking:
            # send out a message as reply for the one we just received
            res = self.__PostMessage()

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

        payload = { EMsgParamKeyID.eNumMsgSent            : self.__ctrSnd
                  , EMsgParamKeyID.eNumMsgReceived        : self.__ctrRcv
                  , EMsgParamKeyID.eNumSendFailures       : self.__ctrErrSnd
                  , EMsgParamKeyID.eNumOutOfOrderReceived : self.__ctrOutOfOrder
                  }

        # clear current error (if any)
        self.__myTask.ClearCurrentError()

        msgUID = self.__myTask.SendMessage(self.__mainTaskID, msgLabelID_=EMsgLabelID.eServiceTaskInfo, msgPayload_=payload)

        res = msgUID > 0

        # failed to send message?
        if not res:
            # something went wrong, decrement sent counter
            self.__ctrSnd    -= 1
            self.__ctrErrSnd += 1

            #[NOTE] 'self.currentError' is always set upon send failure  !!
            #
            xlogif.LogWarning(f'[mtGuiAppServiceBXQ][#sendErrors={self.__ctrErrSnd}] Failed to send xco message to xtask {self.__mainTaskID}.')
        else:
            # xlogif.LogDebug('[mtGuiAppService] Sent xco-message {}.'.format(msgUID))
            pass
        return res
    # --------------------------------------------------------------------------
    #END Impl / protected API
    # --------------------------------------------------------------------------
#END class XFServiceTaskBXQ
