# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : servicetask.py
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
from xcofdk.fwapi.xmsg         import XPayload
from xcofdk.fwapi.xmsg.xmsgmgr import XMessageManager

from xcofdk.tests.userapp.basic.mt.mtmisc.commondefs    import EMsgLabelID
from xcofdk.tests.userapp.basic.mt.mtmisc.commondefs    import EMsgParamKeyID
from xcofdk.tests.userapp.basic.mt.mtmisc.custompayload import CustomPayload


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class ServiceTask(XTask):

    __slots__ = [ '__ctrRun'         , '__ctrSnd'      , '__ctrRcv'
                , '__mainTaskID'     , '__lastRcvUID'  , '__ctrErrSnd'
                , '__bPostingPaused' , '__bBroadcast'  , '__ctrOutOfOrder'
                , '__bSkipSerDes'    , '__bCustomPLD'
                ]

    def __init__(self, index_ : int, taskProfile_ : XTaskProfile =None, bBroadcast_ =False, bSkipPayloadSerDes_ =False, bCustomPayLoad_ =False):
        self.__ctrRun         = 0
        self.__ctrSnd         = 0
        self.__ctrRcv         = 0
        self.__ctrErrSnd      = 0
        self.__ctrOutOfOrder  = 0

        self.__bBroadcast     = bBroadcast_
        self.__mainTaskID     = None
        self.__lastRcvUID     = None
        self.__bCustomPLD     = bCustomPayLoad_
        self.__bSkipSerDes    = bSkipPayloadSerDes_
        self.__bPostingPaused = False

        if taskProfile_ is None:
            taskProfile_ = ServiceTask.__GetMyTaskProfile(index_, bBroadcast_=bBroadcast_, bSkipPayloadSerDes_ =bSkipPayloadSerDes_, bCustomPayLoad_=bCustomPayLoad_)

        super().__init__(taskProfile_=taskProfile_)

        # received messages are expected to be always broadcasts?
        if bBroadcast_:
            # use anonymous addressing to send messages to the main task
            self.__mainTaskID = EPreDefinedMessagingID.MainTask


    # --------------------------------------------------------------------------
    # override of interface inherited from UserAppControllerIF
    # --------------------------------------------------------------------------
    @override
    def RunXTask(self) -> ETernaryCallbackResultID:
        #xlogif.LogDebug(f'[mtGuiAppService] Executing run-phase of service xtask {self.xtaskProfile.aliasName}...')
        self.__ctrRun += 1

        # main task's (unique task) ID not known yet?
        if self.__mainTaskID is None:
            return ETernaryCallbackResultID.CONTINUE

        # posting paused?
        if self.__bPostingPaused:
            return ETernaryCallbackResultID.CONTINUE

        # odd task ID?
        if self.xtaskUniqueID%2:
            # send next message every 100ms
            _bDoSend = (self.__ctrRun%5) == 0
        else:
            # send next message every 60ms
            _bDoSend = (self.__ctrRun%3) == 0

        res = True
        if _bDoSend:
            res = self.__PostMessage()
        return ETernaryCallbackResultID.FromBool(res)

    @override
    def ProcessExternalMessage(self, xmsg_ : XMessage) -> ETernaryCallbackResultID:
        #xlogif.LogDebug('[mtGuiAppService] Received xco-message {}.'.format(xmsg_.msgUniqueID))

        # check for out-of-order message
        if self.__lastRcvUID is None:
            pass
        elif xmsg_.msgUniqueID <= self.__lastRcvUID:
            self.__ctrOutOfOrder += 1
            xlogif.LogWarning('[mtGuiAppService][#outOfOrder={}] Received out-of-order message {}, last received one was {}.'.format(self.__ctrOutOfOrder, xmsg_.msgUniqueID, self.__lastRcvUID))
        self.__lastRcvUID = xmsg_.msgUniqueID

        if self.__bBroadcast and not xmsg_.msgHeader.isBroadcastMessage:
            xlogif.LogWarning('[mtGuiAppService] Received unexpected, non-broadcast message {}.'.format(xmsg_.msgUniqueID))
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
    def __GetMyTaskProfile(index_ : int, bBroadcast_ =False, bSkipPayloadSerDes_ =False, bCustomPayLoad_ =False) -> XTaskProfile:
        if bSkipPayloadSerDes_:
            _aliasName = 'ServiceTaskNoSD_{:02d}'.format(index_)
        elif bCustomPayLoad_:
            _aliasName = 'ServiceTaskCPL_{:02d}'.format(index_)
        elif bBroadcast_:
            _aliasName = 'ServiceTaskBC_{:02d}'.format(index_)
        else:
            _aliasName = 'ServiceTask_{:02d}'.format(index_)

        res = XTaskProfile.CreateAsynchronousTaskProfile(aliasName_=_aliasName, runPhaseFreqMS_=20)

        if res is not None:
            res.isExternalQueueEnabled      = True
            res.runPhaseMaxProcessingTimeMS = 30
        return res

    def __PostMessage(self) -> bool:
        # not running anymore?
        if not self.isRunning:
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

        xmsgUID = XMessageManager.SendMessage(self.__mainTaskID, msgLabelID_=EMsgLabelID.eServiceTaskInfo, msgPayload_=payload)

        res = xmsgUID > 0

        # failed to send message?
        if not res:
            # something went wrong, decrement sent counter
            self.__ctrErrSnd -= 1

            self.ClearCurrentError()
            xlogif.LogWarning(f'[mtGuiAppService][#sendErrors={self.__ctrErrSnd}] Failed to send xco message to xtask {self.__mainTaskID}.')
        else:
            #xlogif.LogDebug('[mtGuiAppService] Sent xco-message {}.'.format(xmsgUID))
            pass
        return res
    # --------------------------------------------------------------------------
    #END Impl / protected API
    # --------------------------------------------------------------------------
#END class ServiceTask
