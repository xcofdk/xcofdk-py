# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : maintask.py
#
# Copyright(c) 2024 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
import sys
from   typing import Union

from xcofdk.fwcom              import fwutil
from xcofdk.fwcom              import xlogif
from xcofdk.fwcom              import ETernaryCallbackResultID
from xcofdk.fwcom              import override
from xcofdk.fwapi.xtask        import MainXTask
from xcofdk.fwapi.xtask        import XTaskProfile
from xcofdk.fwapi.xmsg         import XMessage
from xcofdk.fwapi.xmsg.xmsgmgr import XMessageManager

from xcofdk.tests.userapp.util.userAppUtil import UserAppUtil

from xcofdk.tests.userapp.st.welcome.common.commondefs       import EDetailViewID
from xcofdk.tests.userapp.st.welcome.interfaces.modelif      import EModelItemID
from xcofdk.tests.userapp.st.welcome.interfaces.modelif      import ServiceTaskGilSpec
from xcofdk.tests.userapp.st.welcome.interfaces.modelif      import UserAppModelIF
from xcofdk.tests.userapp.st.welcome.interfaces.controllerif import UserAppControllerIF
from xcofdk.tests.userapp.st.welcome.stguiappwelcome         import STGuiAppWelcome

from xcofdk.tests.userapp.basic.mt.mtmisc.commondefs      import EPreDefinedMessagingID
from xcofdk.tests.userapp.basic.mt.mtmisc.commondefs      import EMsgLabelID
from xcofdk.tests.userapp.basic.mt.mtmisc.commondefs      import EMsgParamKeyID
from xcofdk.tests.userapp.basic.mt.mtmisc.servicetaskGIL2 import ServiceTaskGIL2


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class _UserAppModelImpl(UserAppModelIF):

    __slots__ = [ '__items' ]

    def __init__(self, items_ : dict, bThreadSafe_ =False):
        #NOTE:
        #  Thread safety of model needed only if accessed by multiple tasks.
        #

        super().__init__(bThreadSafe_=bThreadSafe_)
        self.__items = items_

    @override
    def _GetItemsMap(self) -> dict:
        return self.__items
#END class _UserAppModelImpl


class MainTaskGIL2(MainXTask, UserAppControllerIF):

    __slots__ = [ '__gui'            , '__mdl'               , '__lstSrv'
                , '__bAutoStart'     , '__bGilPaused'        , '__bAutoClose'
                , '__cntErrSnd'      , '__srvTaskCount'      , '__guiTitle'
                , '__ctrOutOfOrder'  , '__lstFiboReply'      , '__dictLastRcvUID'
                , '__ctrFiboTrigger' , '__fiboCalcStartTime' , '__curFiboRequestIdx'
                ]

    __FIBO_BASE_INPUT   = 20
    __FIBO_REQUESTS_NUM = 10
    __FIBO_REQUEST_LIST = [40, 50, 100]

    __MAX_NUM_ASYNC_SERVICE_TASKS = 12

    __GIL_SPEC_TABLE = {
        19 : ServiceTaskGilSpec(fiboInput_=19, fiboCpuTimeMS_=1.463, runPhaseFreqMS_=25, deficientRunPhaseFreqMS_=15)     # 11x  1.463  = 16.903 [ms]
      , 20 : ServiceTaskGilSpec(fiboInput_=20, fiboCpuTimeMS_=2.343, runPhaseFreqMS_=40, deficientRunPhaseFreqMS_=25)     # 11x  2.343  = 25.773 [ms]
      , 21 : ServiceTaskGilSpec(fiboInput_=21, fiboCpuTimeMS_=4.584, runPhaseFreqMS_=65, deficientRunPhaseFreqMS_=45)     # 11x  4.584  = 50.424 [ms]
      , 22 : ServiceTaskGilSpec(fiboInput_=22, fiboCpuTimeMS_=7.889, runPhaseFreqMS_=100, deficientRunPhaseFreqMS_=75)    # 11x  7.889  = 86.779 [ms]
      , 23 : ServiceTaskGilSpec(fiboInput_=23, fiboCpuTimeMS_=11.393, runPhaseFreqMS_=140, deficientRunPhaseFreqMS_=120)  # 11x 11.393  =125.323 [ms]
      , 24 : ServiceTaskGilSpec(fiboInput_=24, fiboCpuTimeMS_=16.964, runPhaseFreqMS_=210, deficientRunPhaseFreqMS_=180)  # 11x 16.964  =186.604 [ms]
    }


    def __init__ ( self, taskProfile_ : XTaskProfile =None, guiTitle_ : str =None):
        self.__gui               = None
        self.__mdl               = None
        self.__lstSrv            = []
        self.__bAutoStart        = True
        self.__bAutoClose        = False
        self.__bGilPaused        = False
        self.__lstFiboReply      = None
        self.__ctrFiboTrigger    = 0
        self.__dictLastRcvUID    = None
        self.__curFiboRequestIdx = 0
        self.__fiboCalcStartTime = None

        self.__cntErrSnd     = 0
        self.__ctrOutOfOrder = 0

        self.__srvTaskCount  = MainTaskGIL2.__MAX_NUM_ASYNC_SERVICE_TASKS

        if isinstance(guiTitle_, str):
            self.__guiTitle = guiTitle_
        else:
            self.__guiTitle = 'MTGuiAppGIL2'

        self.__ScanCmdLineArgs()

        if taskProfile_ is None:
            taskProfile_ = MainTaskGIL2.__GetMyTaskProfile()

        UserAppControllerIF.__init__(self)
        MainXTask.__init__(self, taskProfile_=taskProfile_)


    # --------------------------------------------------------------------------
    # own (protected) interface
    # --------------------------------------------------------------------------
    @staticmethod
    def _CreateSingleton(taskProfile_ : Union[XTaskProfile, None]):
        res = MainTaskGIL2(taskProfile_=taskProfile_)
        if res.isDetachedFromFW:
            res = None
            xlogif.LogError('Failed to create main task.')
        return res
    # --------------------------------------------------------------------------
    #END own (protected) interface
    # --------------------------------------------------------------------------


    # --------------------------------------------------------------------------
    # override of interface inherited from MainXTask
    # --------------------------------------------------------------------------
    @override
    def SetUpXTask(self) -> ETernaryCallbackResultID:
        # create and start service tasks
        _numStarted = self.__CreateStartServiceTasks()

        # framework encountered some LC failure?
        if not fwutil.IsLcFailureFree():
            return ETernaryCallbackResultID.ABORT

        # mismatch regarding number of started service tasks?
        if _numStarted != self.__srvTaskCount:
            xlogif.LogError(f'[mtGuiAppMain] Setup failed with only {_numStarted} serivce tasks started.')
            return ETernaryCallbackResultID.ABORT

        # create model
        self.__CreateUserAppModel()

        # create gui, but caution:
        #  - creating and releasing/destroying Tk's root window should always happen in the same task/thread  !!
        #
        self.__gui = STGuiAppWelcome( title_=self.__guiTitle
                                    , bAutoStart_=self.__bAutoStart
                                    , bAutoClose_=self.__bAutoClose
                                    , controllerif_=self
                                    , modelif_=self.__mdl
                                    , detailViewID_=EDetailViewID.eFibonacciResult)

        xlogif.LogInfo(f'[mtGuiAppMain] Finished setup, {_numStarted} serivce tasks started.')
        return ETernaryCallbackResultID.CONTINUE

    @override
    def RunXTask(self) -> ETernaryCallbackResultID:
        xlogif.LogInfo(f'[mtGuiAppMain] Starting run-phase of the main task {self.xtaskUniqueID}...')

        if not self.__gui.StartView():
            res = ETernaryCallbackResultID.ABORT
        else:
            res = ETernaryCallbackResultID.STOP

        xlogif.LogInfo(f'[mtGuiAppMain] GUI view returned, activity state: {self.__gui.isActive}')

        # release referece to gui/Tk's root window
        self.__gui = None

        #NOTE:
        # - stopping running service tasks while still being in run-phase is
        #   necessary due to the current asymmetric state transition of tasks
        #   (see section 'Asymmetric task state transition' in class description
        #   of XTask),
        # - an appropriate remedy is in progress and will be provided accordingly.
        #
        self.__StopServiceTasks()

        if res.isSTOP:
            xlogif.LogInfo(f'[mtGuiAppMain] Finished run-phase of the main task {self.xtaskUniqueID}.')
        return res

    @override
    def TearDownXTask(self) -> ETernaryCallbackResultID:
        for ii in range(len(self.__lstSrv)):
            _srv = self.__lstSrv[ii]
            #xlogif.LogDebug(f'[mtGuiAppMain] Joining service task {_srv.xtaskUniqueID}...')
            _srv.Join()
            xlogif.LogDebug(f'[mtGuiAppMain] Joined service task {_srv.xtaskUniqueID}.')
        return ETernaryCallbackResultID.STOP

    @override
    def ProcessExternalMessage(self, xmsg_ : XMessage) -> ETernaryCallbackResultID:
        #xlogif.LogDebug('[mtGuiAppMain] Received xco-message, msgUID: {}'.format(xmsg_.msgUniqueID))

        lastRcvUID = self.__dictLastRcvUID[xmsg_.msgHeader.msgSender]

        # check for out-of-order message?
        if lastRcvUID is None:
            pass
        elif xmsg_.msgUniqueID <= lastRcvUID:
            self.__ctrOutOfOrder += 1
            xlogif.LogWarning('[mtGuiAppMain][#outOfOrder={}] Received out-of-order message {}, last received one was {}.'.format(self.__ctrOutOfOrder, xmsg_.msgUniqueID, lastRcvUID))

        # store last msg UID received from this sender
        self.__dictLastRcvUID[xmsg_.msgHeader.msgSender] = xmsg_.msgUniqueID

        # not a fibo reply message?
        if xmsg_.msgHeader.msgLabel != EMsgLabelID.eFibonacciReply:
            # don't care, just ignore the message
            return ETernaryCallbackResultID.CONTINUE

        # not expecting any fibo reply?
        if not self.__isFiboReuested:
            xlogif.LogWarning(f'[mtGuiAppMain] Received unexpected fibonacci reply from service task {xmsg_.msgHeader.msgSender}.')
            return ETernaryCallbackResultID.CONTINUE

        # first time receiving fibo reply?
        if not self.__isFiboReplyReceived:
            # fetch the reply out of the payload
            self.__lstFiboReply = xmsg_.msgPayload.GetParameter(EMsgParamKeyID.eFibonacciResultList)

            # set calculation time
            calcTimeMS = UserAppUtil.DeltaTime2Str(self.__fiboCalcStartTime, bLeftStripUnsetFields_=True) + ' [ms]'
            for ii in range(len(self.__lstFiboReply)):
                self.__lstFiboReply[ii].calculationTimeMS = calcTimeMS

            # update model's fibo reply item
            self.__mdl.SetItem(EModelItemID.eFibonacciReply, self.__lstFiboReply)

            # reset fibo request counter
            self.__ctrFiboTrigger = 0

        # fibo reply received and processed already
        else:
            pass

        return ETernaryCallbackResultID.CONTINUE
    # --------------------------------------------------------------------------
    #END override of interface inherited from MainXTask
    # --------------------------------------------------------------------------


    # --------------------------------------------------------------------------
    # override of interface inherited from UserAppControllerIF
    # --------------------------------------------------------------------------
    @UserAppControllerIF.isControllerRunning.getter
    def isControllerRunning(self):
        return self.isRunning

    @override
    def OnViewNotification(self, notifCounter_ : int, bProgressBarProceeding_ : bool =False, bOnDestroy_ =False) -> bool:
        if bProgressBarProceeding_:
            # currently no use for this flag, just ignore it
            pass

        # main task not running anymore?
        if not self.isRunning:
            return False

        # is gui going to be destroyed?
        if bOnDestroy_:
            # stop all (running) service tasks
            self.__StopServiceTasks()

            # stop own task, i.e. the main task
            self.Stop()

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
            res = self.TriggerExternalQueueProcessing() > -1

            # something went wrong while processing queued external messages?
            if not res:
                # try to clear own current error
                self.ClearCurrentError()

                # submit a new error message
                xlogif.LogError(f'[mtGuiAppMain][notifCounter={notifCounter_}] Failed to trigger external queue processing.')

        res = res and self.isRunning
        if res:
            self.__UpdateUserAppModel(notifCounter_)
        return res

    @override
    def OnViewEncounteredException(self, errMsg_ : str, xcp_ : Exception):
        self.__StopServiceTasks()

        # main task has caused/detected a fatal error already?
        if not self.isFatalErrorFree:
            # nothing to do, no need to cause addintional one
            pass
        else:
            # unexpected exception, main task will consider it a LC failure, so notify the framework accordingly
            xlogif.LogException(errMsg_, xcp_)
    # --------------------------------------------------------------------------
    #END override of interface inherited from UserAppControllerIF
    # --------------------------------------------------------------------------


    # --------------------------------------------------------------------------
    # Impl
    # --------------------------------------------------------------------------
    @staticmethod
    def __GetMyTaskProfile() -> XTaskProfile:
        res = XTaskProfile.CreateSynchronousTaskProfile(aliasName_='MainTaskGIL2', bPrivilegedTask_=True)

        if res is not None:
            res.isSetupPhaseEnabled         = True
            res.isTeardownPhaseEnabled      = True
            res.isExternalQueueEnabled      = True
            res.runPhaseMaxProcessingTimeMS = 80
        return res

    @property
    def __isFiboReuested(self):
        return self.__lstFiboReply is not None

    @property
    def __isFiboReplyReceived(self):
        return (self.__lstFiboReply is not None) and (len(self.__lstFiboReply)>0)

    def __ScanCmdLineArgs(self):
        ii, NUM_ARGS = 1, len(sys.argv)
        while ii < NUM_ARGS:
            aa  = sys.argv[ii]
            ii += 1

            if aa.startswith('#'):
                break

            if aa == '--disable-auto-start':
                self.__bAutoStart = False
            elif aa == '--enable-auto-close':
                self.__bAutoClose = True
            else:
                pass
        #END while...

        if not self.__bAutoStart:
            self.__bAutoClose =False

    def __CreateStartServiceTasks(self) -> int:
        self.__dictLastRcvUID = dict()

        # get gil spec for the base fibonacci input
        _baseFiboInputGilSpec = MainTaskGIL2.__GIL_SPEC_TABLE[MainTaskGIL2.__FIBO_BASE_INPUT]

        for ii in range(self.__srvTaskCount):
            # just to make sure we continue in an error-free state
            self.ClearCurrentError()

            srv = ServiceTaskGIL2(ii+1, _baseFiboInputGilSpec)

            # failed to create task?
            if not srv.isAttachedToFW:
                return len(self.__lstSrv)

            # failed to start service task?
            if not srv.Start():
                return len(self.__lstSrv)

            self.__lstSrv.append(srv)
            self.__dictLastRcvUID[srv.xtaskUniqueID] = None
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
            _errMsg = f'Unexpected runtime condition, all {self.__srvTaskCount} service tasks stopped running.'
            xlogif.LogError(_errMsg)

            # wait for a few seconds, then throw an exception
            UserAppUtil.SleepSEC(3.0)
            raise Exception(_errMsg)

        _payload = None

        if msgLabelID_ is None:
            msgLabelID_ = EPreDefinedMessagingID.DontCare
        elif msgLabelID_ == EMsgLabelID.eFibonacciRequest:
            # prepare request's payload
            _lstInput = [_ee-self.__curFiboRequestIdx for _ee in MainTaskGIL2.__FIBO_REQUEST_LIST]
            _payload  = { EMsgParamKeyID.eFibonacciInputList : _lstInput }

        # broadcast message
        _uid = XMessageManager.BroadcastMessage(msgLabelID_, msgPayload_=_payload)

        # send attempt successful?
        res = _uid > 0
        if not res:
            # increment number of failures
            self.__cntErrSnd += 1

            self.ClearCurrentError()
            xlogif.LogError(f'[mtGuiAppMain][#sendErrors={self.__cntErrSnd}] Failed to broadcast xco message to {len(self.__lstSrv)} service task(s).')
        else:
            # xlogif.LogDebug(f'[mtGuiAppMain] Sent broadcast message to {len(self.__lstSrv)} service task(s).')

            if msgLabelID_ == EMsgLabelID.eFibonacciRequest:
                # increment current fibo request index
                self.__curFiboRequestIdx += 1

                # all requests put out?
                if self.__curFiboRequestIdx > MainTaskGIL2.__FIBO_REQUESTS_NUM:
                    # reset current fibo request index
                    self.__curFiboRequestIdx = 0

                # indicate pending fibo reply from now on
                self.__lstFiboReply = []

                # set start time of fibo calculation
                self.__fiboCalcStartTime = UserAppUtil.GetCurrentTime()

                # reset model's fibo reply item
                self.__mdl.SetItem(EModelItemID.eFibonacciReply, [None, None, None])

        return res

    def __CreateUserAppModel(self):
        items = dict()

        # version/system info
        items[EModelItemID.eNumCpuCores]   = fwutil.GetAvailableCpuCoresCount()
        items[EModelItemID.eHostPlatfrom]  = fwutil.GetPlatform()
        items[EModelItemID.eXcofdkVersion] = fwutil.GetXcofdkVersion()
        items[EModelItemID.ePythonVersion] = fwutil.GetPythonVersion()

        # get gil spec for the base fibonacci input
        _baseFiboInputGilSpec = MainTaskGIL2.__GIL_SPEC_TABLE[MainTaskGIL2.__FIBO_BASE_INPUT]

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
#END class MainTaskGIL2
