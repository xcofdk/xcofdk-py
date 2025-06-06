# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : servicetaskGIL2.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from xcofdk.fwcom      import EExecutionCmdID
from xcofdk.fwcom      import override
from xcofdk.fwcom      import EXmsgPredefinedID
from xcofdk.fwapi      import IMessage
from xcofdk.fwapi      import fwutil
from xcofdk.fwapi      import xlogif
from xcofdk.fwapi.xmt  import XTask
from xcofdk.fwapi.xmt  import XTaskProfile

from xuserapp.st.welcome.interfaces.modelif import FibonacciReply
from xuserapp.st.welcome.interfaces.modelif import ServiceTaskGilSpec

from xuserapp.basic.xmt.xmtmisc.commondefs import EMsgLabelID
from xuserapp.basic.xmt.xmtmisc.commondefs import EMsgParamKeyID


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class ServiceTaskGIL2(XTask):

    __slots__ = [ '__ctrRun'         , '__ctrSnd'        , '__ctrRcv'
                , '__ctrErrSnd'      , '__bGilPaused'    , '__ctrOutOfOrder'
                , '__lastRcvUID'     , '__fiboBaseInput' , '__fiboCurInput'
                , '__lstFiboRequest' , '__fiboCache'
                ]

    #[NOTE] Fibonacci(100) >= sys.maxsize // 2
    #
    __MAX_FIBO_INPUT = 100

    def __init__(self, index_ : int, gilSpec_ : ServiceTaskGilSpec):
        self.__ctrRun        = 0
        self.__ctrSnd        = 0
        self.__ctrRcv        = 0
        self.__ctrErrSnd     = 0
        self.__ctrOutOfOrder = 0

        self.__lastRcvUID = None
        self.__bGilPaused = False

        self.__fiboCache      = { 0:0, 1:1 }
        self.__fiboCurInput   = 0
        self.__fiboBaseInput  = gilSpec_.fibonacciInput
        self.__lstFiboRequest = None

        _runPhaseFreqMS = gilSpec_.deficientRunPhaseFrequencyMS if gilSpec_.isDeficientFrequencyForced else gilSpec_.runPhaseFrequencyMS
        _xtaskPrf = ServiceTaskGIL2.__GetMyTaskProfile(index_, runPhaseFreqMS_=_runPhaseFreqMS)

        super().__init__(taskProfile_=_xtaskPrf)


    # --------------------------------------------------------------------------
    # override of interface inherited from UserAppControllerIF
    # --------------------------------------------------------------------------
    @override
    def RunXTask(self) -> EExecutionCmdID:
        #xlogif.LogDebug(f'[mtGuiAppService] Executing run-phase of service xtask {self.taskProfile.aliasName}...')
        self.__ctrRun += 1

        # posting paused?
        if self.__bGilPaused:
            return EExecutionCmdID.CONTINUE

        bMaxFiboResultAvailable = self.__IsFibonacciResultAvailable(ServiceTaskGIL2.__MAX_FIBO_INPUT)

        # max fibo result available?
        if bMaxFiboResultAvailable:
            # resart fibo calculation next time
            self.__fiboCurInput = 0

            bPendingRequest = self.__lstFiboRequest is not None

            # no request to be serviced?
            if not bPendingRequest:
                pass

            # pending request can be serviced now
            else:
                lstResult = []
                for _ee in self.__lstFiboRequest:
                    resultItem = FibonacciReply(sender_=self.taskUID, fiboInput_=_ee, fiboResult=self.__fiboCache[_ee])
                    lstResult.append(resultItem)
                payload = { EMsgParamKeyID.eFibonacciResultList : lstResult}

                # clear current request
                self.__lstFiboRequest = None

                # reset fibo cache
                self.__ResetFiboCache()

                # send the reply to the main task
                res = self.__PostMessage(msgLabelID_=EMsgLabelID.eFibonacciReply, msgPayload_=payload)
                return EExecutionCmdID.FromBool(res)

        # reset fibo cache?
        _bResetFiboCache = self.__fiboCurInput == 0

        # continue with the calculatiion of fibo results for as many numbers as given by 'self.__fiboBaseInput'
        self.__fiboCurInput += self.__fiboBaseInput

        # perform fibo calculation
        self.__CalcFibo(self.__fiboCurInput, bResetCache_=_bResetFiboCache)

        # we have done some non-trivail execution, so check if we're still running?
        if not self.isRunning:
           return EExecutionCmdID.STOP

        _bDoSend = False
        if (self.taskProfile.runPhaseFrequencyMS*self.__ctrRun) >= 500:
            self.__ctrRun = 0

            # send next message in a frequency of 500ms
            _bDoSend = True

        res = True
        if _bDoSend:
            res = self.__PostMessage()
        return EExecutionCmdID.FromBool(res)

    @override
    def ProcessExternalMessage(self, xmsg_ : IMessage) -> EExecutionCmdID:
        #xlogif.LogDebug('[mtGuiAppService] Received xco-message {}.'.format(xmsg_.msgUniqueID))

        if self.__lastRcvUID is None:
            pass
        elif xmsg_.msgUniqueID <= self.__lastRcvUID:
            self.__ctrOutOfOrder += 1
            xlogif.LogWarning('[mtGuiAppService][#outOfOrder={}] Received out-of-order message {}, last received one was {}.'.format(
                self.__ctrOutOfOrder, xmsg_.msgUniqueID, self.__lastRcvUID))
        self.__lastRcvUID = xmsg_.msgUniqueID

        # increment number of messages received from main task
        self.__ctrRcv += 1

        res = True

        # instruction to pause fibonacci calculation?
        if xmsg_.msgHeader.msgLabel == EMsgLabelID.ePauseGIL:
            self.__bGilPaused = True

            # try to send a last message so the receiver is up-to-date with regard to the count of both received and sent messages
            res = self.__PostMessage()

        # instruction to resume fibonacci calculation?
        elif xmsg_.msgHeader.msgLabel == EMsgLabelID.eResumeGIL:
            self.__bGilPaused = False

        # new request for fibonacci results?
        elif xmsg_.msgHeader.msgLabel == EMsgLabelID.eFibonacciRequest:
            self.__lstFiboRequest = list(xmsg_.msgPayload.GetParameter(EMsgParamKeyID.eFibonacciInputList))

            # make we restart the fibo calculation
            self.__fiboCurInput = 0
            self.__ResetFiboCache()

        # ignore whatever else
        else:
            pass

        return EExecutionCmdID.FromBool(res)
    # --------------------------------------------------------------------------
    #END override of interface inherited from UserAppControllerIF
    # --------------------------------------------------------------------------


    # --------------------------------------------------------------------------
    # Impl / protected API
    # --------------------------------------------------------------------------
    @staticmethod
    def __GetMyTaskProfile(index_ : int, runPhaseFreqMS_ : int =None) -> XTaskProfile:
        _aliasName = 'ServiceTaskGIL2_{:02d}'.format(index_)
        res = XTaskProfile.CreateAsyncTaskProfile(aliasName_=_aliasName, runPhaseFreqMS_=runPhaseFreqMS_)

        if res is not None:
            res.isExternalQueueEnabled = True
        return res

    def __IsFibonacciResultAvailable(self, in_ : int):
        return in_ in self.__fiboCache

    def __PostMessage(self, msgLabelID_ : EMsgLabelID =None, msgPayload_ =None) -> bool:
        # not running anymore?
        if not self.isRunning:
            return False

        _mainTaskID = EXmsgPredefinedID.MainTask

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
            if not fwutil.IsTaskRunning(_mainTaskID):
                return False

        self.__ctrSnd += 1

        if msgLabelID_ is not None:
            pass
        else:
            msgLabelID_ = EMsgLabelID.eServiceTaskInfo
            msgPayload_ = { EMsgParamKeyID.eNumSendFailures       : self.__ctrErrSnd
                          , EMsgParamKeyID.eNumOutOfOrderReceived : self.__ctrOutOfOrder
                          }

        # clear current error (if any)
        self.ClearCurrentError()

        _xmsgUID = self.SendMessage(rxTask_=_mainTaskID, msgLabelID_=msgLabelID_, msgPayload_=msgPayload_)

        res = _xmsgUID > 0

        # failed to send message?
        if not res:
            # something went wrong, decrement sent counter
            self.__ctrSnd    -= 1
            self.__ctrErrSnd += 1

            #[NOTE] 'self.currentError' is always set upon send failure  !!
            #
            xlogif.LogWarning(f'[mtGuiAppService][#sendErrors={self.__ctrErrSnd}] Failed to send xco message to main task.')
        else:
            #xlogif.LogDebug('[mtGuiAppService] Sent xco-message {}.'.format(msgUID))
            pass

        return res

    def __ResetFiboCache(self):
        self.__fiboCache.clear()
        self.__fiboCache.update({0: 0, 1: 1})

    def __CalcFibo(self, in_: int, bResetCache_ =False):
        if bResetCache_:
            self.__ResetFiboCache()

        if not (isinstance(in_, int) and in_>-1):
            in_ = 0

        if in_ in self.__fiboCache:
            res = self.__fiboCache[in_]
        else:
            _in2  = in_ - 2
            _res2 = self.__CalcFibo(_in2)
            if _in2 not in self.__fiboCache:
                self.__fiboCache[_in2] = _res2

            _in1 = in_ - 1
            _res1 = self.__CalcFibo(_in1)
            if _in1 not in self.__fiboCache:
                self.__fiboCache[_in1] = _res1

            res = _res1 + _res2
            self.__fiboCache[in_] = res
        return res
    # --------------------------------------------------------------------------
    #END Impl / protected API
    # --------------------------------------------------------------------------
#END class ServiceTaskGIL2
