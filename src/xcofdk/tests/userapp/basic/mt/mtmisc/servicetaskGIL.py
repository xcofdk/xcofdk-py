# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : servicetaskGIL.py
#
# Copyright(c) 2024 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from xcofdk.fwcom              import xlogif
from xcofdk.fwcom              import ETernaryCallbackResultID
from xcofdk.fwcom              import override
from xcofdk.fwapi.xtask        import XTask
from xcofdk.fwapi.xtask        import XTaskProfile
from xcofdk.fwapi.xmsg         import XMessage
from xcofdk.fwapi.xmsg.xmsgmgr import XMessageManager

from xcofdk.tests.userapp.util.userAppUtil import UserAppUtil

from xcofdk.tests.userapp.st.welcome.interfaces.modelif import ServiceTaskGilSpec

from xcofdk.tests.userapp.basic.mt.mtmisc.commondefs import EMsgLabelID
from xcofdk.tests.userapp.basic.mt.mtmisc.commondefs import EMsgParamKeyID


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class ServiceTaskGIL(XTask):

    __slots__ = [ '__ctrRun'        , '__ctrSnd'     , '__ctrRcv'
                , '__mainTaskID'    , '__ctrErrSnd'  , '__bGilPaused'
                , '__ctrOutOfOrder' , '__lastRcvUID' , '__fiboInput'
                ]

    __myFiboCache     = { 0:0, 1:1 }

    def __init__(self, index_ : int, gilSpec_ : ServiceTaskGilSpec):
        self.__ctrRun        = 0
        self.__ctrSnd        = 0
        self.__ctrRcv        = 0
        self.__ctrErrSnd     = 0
        self.__ctrOutOfOrder = 0

        self.__mainTaskID = None
        self.__lastRcvUID = None
        self.__bGilPaused = False
        self.__fiboInput  = gilSpec_.fibonacciInput

        _runPhaseFreqMS = gilSpec_.deficientRunPhaseFrequencyMS if gilSpec_.isDeficientFrequencyForced else gilSpec_.runPhaseFrequencyMS
        _xtaskPrf = ServiceTaskGIL.__GetMyTaskProfile(index_, runPhaseFreqMS_=_runPhaseFreqMS)

        super().__init__(taskProfile_=_xtaskPrf)


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
        if self.__bGilPaused:
            return ETernaryCallbackResultID.CONTINUE

        # perform fibo calculation
        UserAppUtil.Fibonacci(self.__fiboInput)

        # we have done some non-trivail execution, so check if we're still running?
        if not self.isRunning:
           return ETernaryCallbackResultID.STOP

        _bDoSend = False
        if (self.xtaskProfile.runPhaseFrequencyMS*self.__ctrRun) >= 500:
            self.__ctrRun = 0

            # send next message in a frequency of 500ms
            _bDoSend = True

        res = True
        if _bDoSend:
            res = self.__PostMessage()
        return ETernaryCallbackResultID.FromBool(res)

    @override
    def ProcessExternalMessage(self, xmsg_ : XMessage) -> ETernaryCallbackResultID:
        #xlogif.LogDebug('[mtGuiAppService] Received xco-message {}.'.format(xmsg_.msgUniqueID))

        if self.__lastRcvUID is None:
            pass
        else:
            if xmsg_.msgUniqueID <= self.__lastRcvUID:
                self.__ctrOutOfOrder += 1
                xlogif.LogWarning('[mtGuiAppService][#outOfOrder={}] Received out-of-order message {}, last received one was {}.'.format(self.__ctrOutOfOrder, xmsg_.msgUniqueID, self.__lastRcvUID))

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

        return ETernaryCallbackResultID.FromBool(res)
    # --------------------------------------------------------------------------
    #END override of interface inherited from UserAppControllerIF
    # --------------------------------------------------------------------------


    # --------------------------------------------------------------------------
    # Impl / protected API
    # --------------------------------------------------------------------------
    @staticmethod
    def __GetMyTaskProfile(index_ : int, runPhaseFreqMS_ : int =None) -> XTaskProfile:
        _aliasName = 'ServiceTaskGIL_{:02d}'.format(index_)
        res = XTaskProfile.CreateAsynchronousTaskProfile(aliasName_=_aliasName, runPhaseFreqMS_=runPhaseFreqMS_)

        if res is not None:
            res.isExternalQueueEnabled = True
        return res

    def __PostMessage(self) -> bool:
        self.__ctrSnd += 1

        _payload = { EMsgParamKeyID.eNumSendFailures       : self.__ctrErrSnd
                   , EMsgParamKeyID.eNumOutOfOrderReceived : self.__ctrOutOfOrder
                   }

        _xmsgUID = XMessageManager.SendMessage(self.__mainTaskID, msgLabelID_=EMsgLabelID.eServiceTaskInfo, msgPayload_=_payload)

        res = _xmsgUID > 0

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
#END class ServiceTaskGIL
