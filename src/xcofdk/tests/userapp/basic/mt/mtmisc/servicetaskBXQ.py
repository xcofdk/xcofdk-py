# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : servicetaskBXQ.py
#
# Copyright(c) 2024 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from xcofdk.fwcom          import xlogif
from xcofdk.fwcom          import ETernaryCallbackResultID
from xcofdk.fwcom          import override
from xcofdk.fwcom.xmsgdefs import EPreDefinedMessagingID

from xcofdk.fwapi.xtask        import XTask
from xcofdk.fwapi.xtask        import XTaskProfile
from xcofdk.fwapi.xmsg         import XMessage
from xcofdk.fwapi.xmsg.xmsgmgr import XMessageManager

from xcofdk.tests.userapp.basic.mt.mtmisc.commondefs import EMsgLabelID
from xcofdk.tests.userapp.basic.mt.mtmisc.commondefs import EMsgParamKeyID


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class ServiceTaskBXQ(XTask):

    __slots__ = [ '__ctrSnd'     , '__ctrRcv'        , '__ctrErrSnd'
                , '__mainTaskID' , '__lastRcvUID'    , '__bPostingPaused'
                , '__bBroadcast' , '__ctrOutOfOrder'
                ]

    def __init__(self, index_ : int, taskProfile_ : XTaskProfile =None, bBroadcast_ =False):
        self.__ctrSnd         = 0
        self.__ctrRcv         = 0
        self.__ctrErrSnd      = 0
        self.__ctrOutOfOrder  = 0

        self.__bBroadcast     = bBroadcast_
        self.__mainTaskID     = None
        self.__lastRcvUID     = None
        self.__bPostingPaused = False

        if taskProfile_ is None:
            taskProfile_ = ServiceTaskBXQ.__GetMyTaskProfile(index_)

        super().__init__(taskProfile_=taskProfile_)

        # received messages are expected to be always broadcasts?
        if bBroadcast_:
            # use anonymous addressing to send messages to the main task
            self.__mainTaskID = EPreDefinedMessagingID.MainTask


    # --------------------------------------------------------------------------
    # override of interface inherited from UserAppControllerIF
    # --------------------------------------------------------------------------
    @override
    def ProcessExternalMessage(self, xmsg_ : XMessage) -> ETernaryCallbackResultID:
        #xlogif.LogDebug('[mtGuiAppService] Received xco-message {}.'.format(xmsg_.msgUniqueID))

        # check for out-of-order message
        if self.__lastRcvUID is None:
            pass
        elif xmsg_.msgUniqueID <= self.__lastRcvUID:
            self.__ctrOutOfOrder += 1
            xlogif.LogWarning('[mtGuiAppServiceBXQ][#outOfOrder={}] Received out-of-order message {}, last received one was {}.'.format(self.__ctrOutOfOrder, xmsg_.msgUniqueID, self.__lastRcvUID))
        self.__lastRcvUID = xmsg_.msgUniqueID

        if self.__bBroadcast and not xmsg_.msgHeader.isBroadcastMessage:
            xlogif.LogWarning('[mtGuiAppServiceBXQ] Received unexpected, non-broadcast message {}.'.format(xmsg_.msgUniqueID))
            return ETernaryCallbackResultID.CONTINUE

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
        elif self.xtaskProfile.isExternalQueueBlocking:
            # send out a message as reply for the one we just received
            res = self.__PostMessage()

        return ETernaryCallbackResultID.FromBool(res)
    # --------------------------------------------------------------------------
    #END override of interface inherited from UserAppControllerIF
    # --------------------------------------------------------------------------


    # --------------------------------------------------------------------------
    # Impl / protected API
    # --------------------------------------------------------------------------
    @staticmethod
    def __GetMyTaskProfile(index_ : int) -> XTaskProfile:
        _aliasName = 'ServiceTask_BXQ{:02d}'.format(index_)
        res = XTaskProfile.CreateAsynchronousTaskProfile(aliasName_=_aliasName, runPhaseFreqMS_=20)

        if res is not None:
            res.isExternalQueueEnabled      = True
            res.isExternalQueueBlocking     = True
            res.runPhaseMaxProcessingTimeMS = 30
        return res

    def __PostMessage(self) -> bool:
        # not running anymore?
        if not self.isRunning:
            return False

        self.__ctrSnd += 1

        payload = { EMsgParamKeyID.eNumMsgSent            : self.__ctrSnd
                  , EMsgParamKeyID.eNumMsgReceived        : self.__ctrRcv
                  , EMsgParamKeyID.eNumSendFailures       : self.__ctrErrSnd
                  , EMsgParamKeyID.eNumOutOfOrderReceived : self.__ctrOutOfOrder
                  }
        xmsgUID = XMessageManager.SendMessage(self.__mainTaskID, msgLabelID_=EMsgLabelID.eServiceTaskInfo, msgPayload_=payload)

        res = xmsgUID > 0

        # failed to send message?
        if not res:
            # something went wrong, decrement sent counter
            self.__ctrErrSnd -= 1

            self.ClearCurrentError()
            xlogif.LogWarning(f'[mtGuiAppServiceBXQ][#sendErrors={self.__ctrErrSnd}] Failed to send xco message to xtask {self.__mainTaskID}.')
        else:
            # xlogif.LogDebug('[mtGuiAppService] Sent xco-message {}.'.format(xmsgUID))
            pass
        return res
    # --------------------------------------------------------------------------
    #END Impl / protected API
    # --------------------------------------------------------------------------
#END class ServiceTaskBXQ
