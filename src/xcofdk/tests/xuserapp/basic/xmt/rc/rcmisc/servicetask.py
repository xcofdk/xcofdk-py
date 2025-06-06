# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : servicetask.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from xcofdk.fwcom      import EExecutionCmdID
from xcofdk.fwcom      import EXmsgPredefinedID
from xcofdk.fwapi      import IMessage
from xcofdk.fwapi      import fwutil
from xcofdk.fwapi      import xlogif
from xcofdk.fwapi      import IRCCommTask
from xcofdk.fwapi      import XFAsyncCommTask
from xcofdk.fwapi      import GetCurTask
from xcofdk.fwapi.xmsg import XPayload

from xuserapp.basic.xmt.xmtmisc.commondefs    import EMsgLabelID
from xuserapp.basic.xmt.xmtmisc.commondefs    import EMsgParamKeyID
from xuserapp.basic.xmt.xmtmisc.custompayload import CustomPayload


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
def CreateServiceTask( srvTaskNo_          : int
                     , bBroadcast_         =False
                     , bSkipPayloadSerDes_ =False
                     , bCustomPayLoad_     =False) -> IRCCommTask:
    if bSkipPayloadSerDes_:
        _aliasName = 'ServiceTaskNoSD_{:02d}'.format(srvTaskNo_)
    elif bCustomPayLoad_:
        _aliasName = 'ServiceTaskCPL_{:02d}'.format(srvTaskNo_)
    elif bBroadcast_:
        _aliasName = 'ServiceTaskBC_{:02d}'.format(srvTaskNo_)
    else:
        _aliasName = 'ServiceTask_{:02d}'.format(srvTaskNo_)

    _phasedXFCallback = XFServiceTask( bBroadcast_=bBroadcast_
                                     , bSkipPayloadSerDes_=bSkipPayloadSerDes_
                                     , bCustomPayLoad_=bCustomPayLoad_)

    res = XFAsyncCommTask(_phasedXFCallback, aliasName_=_aliasName, runCallbackFrequency_=20)
    return res
#END CreateServiceTask()


class XFServiceTask:

    __slots__ = [ '__ctrRun' , '__ctrSnd' , '__ctrRcv' , '__mainTaskID' , '__lastRcvUID' , '__ctrErrSnd' , '__myCTsk'
                , '__bPostingPaused' , '__bBroadcast' , '__ctrOutOfOrder' , '__bSkipSerDes' , '__bCustomPLD' ]

    def __init__(self, bBroadcast_ =False, bSkipPayloadSerDes_ =False, bCustomPayLoad_ =False):
        self.__ctrRun         = 0
        self.__ctrSnd         = 0
        self.__ctrRcv         = 0
        self.__ctrErrSnd      = 0
        self.__ctrOutOfOrder  = 0

        self.__myCTsk         = None
        self.__bBroadcast     = bBroadcast_
        self.__mainTaskID     = None
        self.__lastRcvUID     = None
        self.__bCustomPLD     = bCustomPayLoad_
        self.__bSkipSerDes    = bSkipPayloadSerDes_
        self.__bPostingPaused = False

        # received messages are expected to be always broadcasts?
        if bBroadcast_:
            # use anonymous addressing to send messages to the main task
            self.__mainTaskID = EXmsgPredefinedID.MainTask


    # --------------------------------------------------------------------------
    # phasedXF callbacks
    # --------------------------------------------------------------------------
    def RunTask(self) -> EExecutionCmdID:
        if self.__myCTsk is None:
            self.__myCTsk = GetCurTask()

        if not self.__myTask.isRunning:
            return EExecutionCmdID.CANCEL if self.__myTask.isCanceling else EExecutionCmdID.STOP

        #xlogif.LogDebug(f'[mtGuiAppService] Executing run-phase of service xtask {self.taskProfile.aliasName}...')
        self.__ctrRun += 1

        # main task's (unique task) ID not known yet?
        if self.__mainTaskID is None:
            return EExecutionCmdID.CONTINUE

        # posting paused?
        if self.__bPostingPaused:
            return EExecutionCmdID.CONTINUE

        # odd task ID?
        if self.__myTask.taskUID%2:
            # send next message every 100ms
            _bDoSend = (self.__ctrRun%5) == 0
        else:
            # send next message every 60ms
            _bDoSend = (self.__ctrRun%3) == 0

        res = True
        if _bDoSend:
            res = self.__PostMessage()
        return EExecutionCmdID.FromBool(res)

    def ProcessExternalMessage(self, xmsg_ : IMessage) -> EExecutionCmdID:
        if not self.__myTask.isRunning:
            return EExecutionCmdID.CANCEL if self.__myTask.isCanceling else EExecutionCmdID.STOP

        # check for out-of-order message
        if self.__lastRcvUID is None:
            pass
        elif xmsg_.msgUniqueID <= self.__lastRcvUID:
            self.__ctrOutOfOrder += 1
            xlogif.LogWarning('[mtGuiAppService][#outOfOrder={}] Received out-of-order message {}, last received one was {}.'.format(
                self.__ctrOutOfOrder, xmsg_.msgUniqueID, self.__lastRcvUID))
        self.__lastRcvUID = xmsg_.msgUniqueID

        if self.__bBroadcast and not xmsg_.msgHeader.isBroadcastMessage:
            xlogif.LogWarning('[mtGuiAppService] Received unexpected, non-broadcast message {}.'.format(xmsg_.msgUniqueID))
            return EExecutionCmdID.CONTINUE

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

        if self.__bCustomPLD:
            payload = CustomPayload(self.__ctrRcv, self.__ctrSnd, self.__ctrErrSnd, self.__ctrOutOfOrder, bSkipSer_=False)
        else:
            payload = { EMsgParamKeyID.eNumMsgSent            : self.__ctrSnd
                      , EMsgParamKeyID.eNumMsgReceived        : self.__ctrRcv
                      , EMsgParamKeyID.eNumSendFailures       : self.__ctrErrSnd
                      , EMsgParamKeyID.eNumOutOfOrderReceived : self.__ctrOutOfOrder
                      }

            if self.__bSkipSerDes:
                payload = XPayload(containerInitializer_=payload, bBypassSerDes_=True)

        # clear current error (if any)
        self.__myTask.ClearCurrentError()

        msgUID = self.__myTask.SendMessage(self.__mainTaskID, msgLabelID_=EMsgLabelID.eServiceTaskInfo, msgPayload_=payload)
        res = msgUID > 0

        # failed to send message?
        if not res:
            # main task still running?
            if fwutil.IsTaskRunning(self.__mainTaskID):
                # something went wrong, decrement sent counter
                self.__ctrSnd    -= 1
                self.__ctrErrSnd += 1
        else:
            #xlogif.LogDebug('[mtGuiAppService] Sent xco-message {}.'.format(msgUID))
            pass
        return res
    # --------------------------------------------------------------------------
    #END Impl / protected API
    # --------------------------------------------------------------------------
#END class XFServiceTask
