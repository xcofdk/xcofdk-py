# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : maintask.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from xcofdk.fwcom import EXmsgPredefinedID
from xcofdk.fwcom import EExecutionCmdID
from xcofdk.fwcom import override
from xcofdk.fwapi import IMessage
from xcofdk.fwapi import fwutil
from xcofdk.fwapi import xlogif
from xcofdk.fwapi import IRCCommTask
from xcofdk.fwapi import XFSyncCommTask
from xcofdk.fwapi import GetCurTask

from xuserapp.util.cloptions                     import CLOptions
from xuserapp.util.userAppUtil                   import UserAppUtil
from xuserapp.st.welcome.common.commondefs       import EDetailViewID
from xuserapp.st.welcome.interfaces.modelif      import EModelItemID
from xuserapp.st.welcome.interfaces.modelif      import ServiceTaskGilSpec
from xuserapp.st.welcome.interfaces.modelif      import UserAppModelIF
from xuserapp.st.welcome.interfaces.controllerif import UserAppControllerIF
from xuserapp.st.welcome.stguiappwelcome         import STGuiAppWelcome

from xuserapp.basic.xmt.xmtmisc.commondefs        import EMsgLabelID
from xuserapp.basic.xmt.xmtmisc.commondefs        import EMsgParamKeyID
from xuserapp.basic.xmt.rc.rcmisc.servicetaskGIL2 import CreateServiceTaskGIL2


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
def _CreateMainTaskGIL2(cmdLineOpts_ : CLOptions) -> IRCCommTask:
    _phasedXFCallback = XFMainTaskGIL2(cmdLineOpts_, guiTitle_='XMTGuiAppGIL2')
    res = XFSyncCommTask(_phasedXFCallback, aliasName_='MainTask', bMainTask_=True)
    return res
#END _CreateMainTaskGIL2()


class _UserAppModelImpl(UserAppModelIF):

    __slots__ = [ '__items' ]

    def __init__(self, items_ : dict, bThreadSafe_ =False):
        #[NOTE]
        #  Thread safety of model needed only if accessed by multiple tasks.
        #

        super().__init__(bThreadSafe_=bThreadSafe_)
        self.__items = items_

    @override
    def _GetItemsMap(self) -> dict:
        return self.__items
#END class _UserAppModelImpl


class XFMainTaskGIL2(UserAppControllerIF):

    __slots__ = [ '__gui' , '__mdl' , '__lstSrv' , '__bGilPaused' , '__cmdLine' , '__cntErrSnd' , '__srvTaskCount' , '__guiTitle' , '__myCTsk'
                , '__ctrOutOfOrder' , '__lstFiboReply' , '__dictLastRcvUID' , '__ctrFiboTrigger' , '__fcalcStartTime' , '__curFiboReqIdx' ]

    __FIBO_BASE_INPUT   = 20
    __FIBO_REQUESTS_NUM = 10
    __FIBO_REQUEST_LIST = [40, 50, 100]

    __NUM_ASYNC_SRV = 12

    __GIL_SPEC_TABLE = {
        19 : ServiceTaskGilSpec(fiboInput_=19, fiboCpuTimeMS_=1.463, runPhaseFreqMS_=25, deficientRunPhaseFreqMS_=15)     # 11x  1.463  = 16.903 [ms]
      , 20 : ServiceTaskGilSpec(fiboInput_=20, fiboCpuTimeMS_=2.343, runPhaseFreqMS_=40, deficientRunPhaseFreqMS_=25)     # 11x  2.343  = 25.773 [ms]
      , 21 : ServiceTaskGilSpec(fiboInput_=21, fiboCpuTimeMS_=4.584, runPhaseFreqMS_=65, deficientRunPhaseFreqMS_=45)     # 11x  4.584  = 50.424 [ms]
      , 22 : ServiceTaskGilSpec(fiboInput_=22, fiboCpuTimeMS_=7.889, runPhaseFreqMS_=100, deficientRunPhaseFreqMS_=75)    # 11x  7.889  = 86.779 [ms]
      , 23 : ServiceTaskGilSpec(fiboInput_=23, fiboCpuTimeMS_=11.393, runPhaseFreqMS_=140, deficientRunPhaseFreqMS_=120)  # 11x 11.393  =125.323 [ms]
      , 24 : ServiceTaskGilSpec(fiboInput_=24, fiboCpuTimeMS_=16.964, runPhaseFreqMS_=210, deficientRunPhaseFreqMS_=180)  # 11x 16.964  =186.604 [ms]
    }


    def __init__ ( self, cmdLineOpts_ : CLOptions, guiTitle_ : str =None):
        self.__gui            = None
        self.__mdl            = None
        self.__myCTsk         = None
        self.__lstSrv         = []
        self.__cmdLine        = cmdLineOpts_
        self.__guiTitle       = guiTitle_ if isinstance(guiTitle_, str) else 'XMTGuiAppGIL2'
        self.__cntErrSnd      = 0
        self.__bGilPaused     = False
        self.__lstFiboReply   = None
        self.__srvTaskCount   = XFMainTaskGIL2.__NUM_ASYNC_SRV
        self.__curFiboReqIdx  = 0
        self.__ctrOutOfOrder  = 0
        self.__ctrFiboTrigger = 0
        self.__dictLastRcvUID = None
        self.__fcalcStartTime = None

        super().__init__()


    # --------------------------------------------------------------------------
    # phasedXF callbacks
    # --------------------------------------------------------------------------
    def SetUpTask(self) -> EExecutionCmdID:
        self.__myCTsk = GetCurTask()
        _numStarted   = self.__CreateStartServiceTasks()

        # framework encountered some LC failure?
        if not fwutil.IsLcFailureFree():
            return EExecutionCmdID.ABORT

        # mismatch regarding number of started service tasks?
        if _numStarted != self.__srvTaskCount:
            xlogif.LogError(f'[mtGuiAppMain] Setup failed with only {_numStarted} serivce tasks started.')
            return EExecutionCmdID.ABORT

        # create model
        self.__CreateUserAppModel()

        # create gui, but caution:
        #  - creating and releasing/destroying Tk's root window should always happen in the same task/thread  !!
        #
        self.__gui = STGuiAppWelcome( title_=self.__guiTitle
                                    , bAutoStart_=self.__cmdLine.isAutoStartEnabled
                                    , bAutoClose_=self.__cmdLine.isAutoCloseEnabled
                                    , controllerif_=self
                                    , modelif_=self.__mdl
                                    , detailViewID_=EDetailViewID.eFibonacciResult)

        xlogif.LogInfo(f'[mtGuiAppMain] Finished setup, {_numStarted} serivce tasks started.')
        return EExecutionCmdID.CONTINUE

    def RunTask(self) -> EExecutionCmdID:
        xlogif.LogInfo(f'[mtGuiAppMain] Starting run-phase of the main task {self.__myCTsk.taskUID}...')

        if not self.__gui.StartView():
            res = EExecutionCmdID.ABORT
        else:
            res = EExecutionCmdID.STOP

        xlogif.LogInfo(f'[mtGuiAppMain] GUI view returned, activity state: {self.__gui.isActive}')

        # release referece to gui/Tk's root window
        self.__gui = None

        if res.isSTOP:
            xlogif.LogInfo(f'[mtGuiAppMain] Finished run-phase of the main task {self.__myCTsk.taskUID}.')
        return res

    def TearDownTask(self) -> EExecutionCmdID:
        for ii in range(len(self.__lstSrv)):
            _srv = self.__lstSrv[ii]
            #xlogif.LogDebug(f'[mtGuiAppMain] Joining service task {_srv.taskUID}...')
            _srv.Join()
            xlogif.LogDebug(f'[mtGuiAppMain] Joined service task {_srv.taskUID}.')
        return EExecutionCmdID.STOP

    def ProcessExternalMessage(self, xmsg_ : IMessage) -> EExecutionCmdID:
        #xlogif.LogDebug('[mtGuiAppMain] Received xco-message, msgUID: {}'.format(xmsg_.msgUniqueID))

        lastRcvUID = self.__dictLastRcvUID[xmsg_.msgHeader.msgSender]

        # check for out-of-order message?
        if lastRcvUID is None:
            pass
        elif xmsg_.msgUniqueID <= lastRcvUID:
            self.__ctrOutOfOrder += 1
            xlogif.LogWarning('[mtGuiAppMain][#outOfOrder={}] Received out-of-order message {}, last received one was {}.'.format(
                self.__ctrOutOfOrder, xmsg_.msgUniqueID, lastRcvUID))

        # store last msg UID received from this sender
        self.__dictLastRcvUID[xmsg_.msgHeader.msgSender] = xmsg_.msgUniqueID

        # not a fibo reply message?
        if xmsg_.msgHeader.msgLabel != EMsgLabelID.eFibonacciReply:
            # don't care, just ignore the message
            return EExecutionCmdID.CONTINUE

        # not expecting any fibo reply?
        if not self.__isFiboReuested:
            xlogif.LogWarning(f'[mtGuiAppMain] Received unexpected fibonacci reply from service task {xmsg_.msgHeader.msgSender}.')
            return EExecutionCmdID.CONTINUE

        # first time receiving fibo reply?
        if not self.__isFiboReplyReceived:
            # fetch the reply out of the payload
            self.__lstFiboReply = xmsg_.msgPayload.GetParameter(EMsgParamKeyID.eFibonacciResultList)

            # set calculation time
            calcTimeMS = UserAppUtil.DeltaTime2Str(self.__fcalcStartTime, bLeftStripUnsetFields_=True) + ' [ms]'
            for ii in range(len(self.__lstFiboReply)):
                self.__lstFiboReply[ii].calculationTimeMS = calcTimeMS

            # update model's fibo reply item
            self.__mdl.SetItem(EModelItemID.eFibonacciReply, self.__lstFiboReply)

            # reset fibo request counter
            self.__ctrFiboTrigger = 0

        # fibo reply received and processed already
        else:
            pass

        return EExecutionCmdID.CONTINUE
    # --------------------------------------------------------------------------
    #END phasedXF callbacks
    # --------------------------------------------------------------------------


    # --------------------------------------------------------------------------
    # override of interface inherited from UserAppControllerIF
    # --------------------------------------------------------------------------
    @UserAppControllerIF.isControllerRunning.getter
    def isControllerRunning(self):
        return self.__myCTsk.isRunning

    @override
    def OnViewNotification(self, notifCounter_ : int, bProgressBarProceeding_ : bool =False, bOnDestroy_ =False) -> bool:
        if bProgressBarProceeding_:
            # currently no use for this flag, just ignore it
            pass

        # main task not running anymore?
        if not self.__myCTsk.isRunning:
            return False

        # is gui going to be destroyed?
        if bOnDestroy_:
            #[NOTE]
            #  a) make sure all services are stopped before the main task leaves its run-phase,
            #     i.e. its 'running' state,
            #  b) alternatively, a) could be skipped in which case service instances are
            #     recommended to perform a pre-check on the avilability of the main task
            #     before attempting to send out their next message, see impl of method below:
            #         XFServiceTaskGIL2.__PostMessage():
            #
            self.__StopServiceTasks()

            # stop own task, i.e. the main task
            self.__myCTsk.Stop()

            # done, acknowledge this notification
            return True

        res = True

        # time to post a new message to the service tasks?
        if (notifCounter_%5) == 0:
            # 'Pause' button got clicked?
            if self.__mdl.serviceTaskGilSpec.isGilPaused:
                if not self.__bGilPaused:
                    res = self.__PostMessage(msgLabelID_=EMsgLabelID.ePauseGIL)
                    self.__bGilPaused = True

            # in 'paused' state?
            elif self.__bGilPaused:
                self.__bGilPaused = False
                res = self.__PostMessage(msgLabelID_=EMsgLabelID.eResumeGIL)

            # no fibo request sent out?
            elif not self.__isFiboReuested:
                # send next fibo request
                res = self.__PostMessage(msgLabelID_=EMsgLabelID.eFibonacciRequest)

            # fibo reply received already?
            elif self.__isFiboReplyReceived:
                self.__ctrFiboTrigger += 1

                # time to trigger new fibo request?
                if (self.__ctrFiboTrigger%8) == 0:
                    self.__ctrFiboTrigger = 0

                    # make a new fibo request is sent out next time we get notified by the view
                    self.__lstFiboReply = None

            # waiting for fibo reply
            else:
                # nothing to do
                pass

        # no need to post a new message, process queued external messages (if any)
        else:
            res = self.__myCTsk.TriggerExternalQueueProcessing() > -1

            # something went wrong while processing queued external messages?
            if not res:
                # try to clear own current error
                self.__myCTsk.ClearCurrentError()

                # submit a new error message
                xlogif.LogError(f'[mtGuiAppMain][notifCounter={notifCounter_}] Failed to trigger external queue processing.')

        res = res and self.__myCTsk.isRunning
        if res:
            self.__UpdateUserAppModel(notifCounter_)
        return res

    @override
    def OnViewEncounteredException(self, errMsg_ : str, xcp_ : Exception):
        self.__StopServiceTasks()

        # main task has caused/detected a fatal error already?
        if not self.__myCTsk.isFatalErrorFree:
            # nothing to do, no need to cause addintional one
            pass
        else:
            # unexpected exception, main task will consider it an LC failure, so notify the framework accordingly
            #xlogif.LogExceptionEC(errMsg_, xcp_, 1032001)
            xlogif.LogExceptionEC(errMsg_, xcp_, 1032001)
    # --------------------------------------------------------------------------
    #END override of interface inherited from UserAppControllerIF
    # --------------------------------------------------------------------------


    # --------------------------------------------------------------------------
    # Impl
    # --------------------------------------------------------------------------
    @property
    def __myTask(self) -> IRCCommTask:
        return self.__myCTsk

    @property
    def __isFiboReuested(self):
        return self.__lstFiboReply is not None

    @property
    def __isFiboReplyReceived(self):
        return (self.__lstFiboReply is not None) and (len(self.__lstFiboReply)>0)

    def __CreateStartServiceTasks(self) -> int:
        self.__dictLastRcvUID = dict()

        # get gil spec for the base fibonacci input
        _baseFiboInputGilSpec = XFMainTaskGIL2.__GIL_SPEC_TABLE[XFMainTaskGIL2.__FIBO_BASE_INPUT]

        for ii in range(self.__srvTaskCount):
            # just to make sure we continue in an error-free state
            self.__myCTsk.ClearCurrentError()

            _srv = CreateServiceTaskGIL2(ii+1, _baseFiboInputGilSpec)

            # failed to create task?
            if not _srv.isAttachedToFW:
                return len(self.__lstSrv)

            # failed to start service task?
            if not _srv.Start():
                return len(self.__lstSrv)

            self.__lstSrv.append(_srv)
            self.__dictLastRcvUID[_srv.taskUID] = None
        #END for ii...

        return len(self.__lstSrv)

    def __GetRunningServiceTasksCount(self):
        if self.__lstSrv is None:
            return 0
        return len( [_srv for _srv in self.__lstSrv if _srv.isRunning] )

    def __StopServiceTasks(self):
        if self.__lstSrv is None:
            return

        _lst = [ _srv for _srv in self.__lstSrv if _srv.isRunning ]
        if len(_lst) < 1:
            return

        # make all running service tasks stop (their messaging)
        for _srv in _lst:
            if _srv.isRunning:
                _srv.Stop()
        xlogif.LogInfo(f'[mtGuiAppMain] Stopped {len(_lst)} service tasks.')

        # sleep for a while before leaving running state
        UserAppUtil.SleepMS(200)

    def __PostMessage(self, msgLabelID_ : EMsgLabelID =None) -> bool:
        # all service tasks stopped running?
        if self.__GetRunningServiceTasksCount() < 1:
            _errMsg = f'Unexpected runtime condition of {self.__guiTitle}, all {self.__srvTaskCount} service tasks stopped running already.'
            xlogif.LogError(_errMsg)

            # wait for a few seconds, then throw an exception
            UserAppUtil.SleepSEC(3.0)
            raise Exception(_errMsg)

        _payload = None

        if msgLabelID_ is None:
            msgLabelID_ = EXmsgPredefinedID.DontCare
        elif msgLabelID_ == EMsgLabelID.eFibonacciRequest:
            # prepare request's payload
            _lstInput = [_ee-self.__curFiboReqIdx for _ee in XFMainTaskGIL2.__FIBO_REQUEST_LIST]
            _payload  = { EMsgParamKeyID.eFibonacciInputList : _lstInput }

        # broadcast message
        _uid = self.__myCTsk.BroadcastMessage(msgLabelID_, msgPayload_=_payload)

        # send attempt successful?
        res = _uid > 0
        if not res:
            # increment number of failures
            self.__cntErrSnd += 1

            self.__myCTsk.ClearCurrentError()
            xlogif.LogError(f'[mtGuiAppMain][#sendErrors={self.__cntErrSnd}] Failed to broadcast xco message to {len(self.__lstSrv)} service task(s).')
        else:
            # xlogif.LogDebug(f'[mtGuiAppMain] Sent broadcast message to {len(self.__lstSrv)} service task(s).')

            if msgLabelID_ == EMsgLabelID.eFibonacciRequest:
                # increment current fibo request index
                self.__curFiboReqIdx += 1

                # all requests put out?
                if self.__curFiboReqIdx > XFMainTaskGIL2.__FIBO_REQUESTS_NUM:
                    # reset current fibo request index
                    self.__curFiboReqIdx = 0

                # indicate pending fibo reply from now on
                self.__lstFiboReply = []

                # set start time of fibo calculation
                self.__fcalcStartTime = UserAppUtil.GetCurrentTime()

                # reset model's fibo reply item
                self.__mdl.SetItem(EModelItemID.eFibonacciReply, [None, None, None])

        return res

    def __CreateUserAppModel(self):
        items = dict()

        # version/system info
        items[EModelItemID.eNumCpuCores]   = fwutil.GetAvailableCpuCoresCount()
        items[EModelItemID.eHostPlatfrom]  = fwutil.GetPlatform()
        items[EModelItemID.eXcofdkVersion] = fwutil.GetXcofdkVersion()
        items[EModelItemID.ePythonVersion] = UserAppUtil.GetPythonVersion()

        # get gil spec for the base fibonacci input
        _baseFiboInputGilSpec = XFMainTaskGIL2.__GIL_SPEC_TABLE[XFMainTaskGIL2.__FIBO_BASE_INPUT]

        # set gil spec associated with the base fibonacci input
        items[EModelItemID.eServiceTaskGilSpec] = _baseFiboInputGilSpec

        # fibonacci reply list
        items[EModelItemID.eFibonacciReply] = [None, None, None]

        self.__mdl = _UserAppModelImpl(items_=items)

    def __UpdateUserAppModel(self, notifCounter_ : int):
        # nothing to update
        pass
    # --------------------------------------------------------------------------
    #END Impl
    # --------------------------------------------------------------------------
#END class XFMainTaskGIL2
