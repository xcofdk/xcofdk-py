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

from xcofdk.tests.userapp.st.welcome.common.commondefs import EGuiConfig

from xcofdk.tests.userapp.st.welcome.common.commondefs       import EDetailViewID
from xcofdk.tests.userapp.st.welcome.interfaces.modelif      import EModelItemID
from xcofdk.tests.userapp.st.welcome.interfaces.modelif      import TaskInfo
from xcofdk.tests.userapp.st.welcome.interfaces.modelif      import ServiceTaskGilSpec
from xcofdk.tests.userapp.st.welcome.interfaces.modelif      import UserAppModelIF
from xcofdk.tests.userapp.st.welcome.interfaces.controllerif import UserAppControllerIF
from xcofdk.tests.userapp.st.welcome.stguiappwelcome         import STGuiAppWelcome

from xcofdk.tests.userapp.basic.mt.mtmisc.commondefs     import EPreDefinedMessagingID
from xcofdk.tests.userapp.basic.mt.mtmisc.commondefs     import EMsgLabelID
from xcofdk.tests.userapp.basic.mt.mtmisc.commondefs     import EMsgParamKeyID
from xcofdk.tests.userapp.basic.mt.mtmisc.servicetaskGIL import ServiceTaskGIL


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


class MainTaskGIL(MainXTask, UserAppControllerIF):

    __slots__ = [ '__gui'       ,  '__mdl'         , '__bAutoStart'     , '__bAutoClose'
                , '__ctrSnd'    , '__ctrRcv'       , '__lstSrv'         , '__lstSrvNR'
                , '__taskInfo'  , '__srvTaskCount' , '__dictSrvInfo'    , '__curSrvView'
                , '__guiTitle'  , '__cntErrSnd'    , '__bGilPaused'     , '__ctrOutOfOrder'
                , '__startTime' , '__fiboInput'    , '__bDeficientFreq' , '__dictLastRcvUID'
                ]

    __FIBO_INPUT_MIN = 19
    __FIBO_INPUT_MAX = 24

    __MAX_NUM_ASYNC_SERVICE_TASKS = 12

    __GIL_SPEC_TABLE = {
        19 : ServiceTaskGilSpec(fiboInput_=19, fiboCpuTimeMS_=1.463, runPhaseFreqMS_=25, deficientRunPhaseFreqMS_=15)     # 11x  1.463  = 16.903 [ms]
      , 20 : ServiceTaskGilSpec(fiboInput_=20, fiboCpuTimeMS_=2.343, runPhaseFreqMS_=40, deficientRunPhaseFreqMS_=20)     # 11x  2.343  = 25.773 [ms]
      , 21 : ServiceTaskGilSpec(fiboInput_=21, fiboCpuTimeMS_=4.584, runPhaseFreqMS_=65, deficientRunPhaseFreqMS_=45)     # 11x  4.584  = 50.424 [ms]
      , 22 : ServiceTaskGilSpec(fiboInput_=22, fiboCpuTimeMS_=7.889, runPhaseFreqMS_=100, deficientRunPhaseFreqMS_=75)    # 11x  7.889  = 86.779 [ms]
      , 23 : ServiceTaskGilSpec(fiboInput_=23, fiboCpuTimeMS_=11.393, runPhaseFreqMS_=140, deficientRunPhaseFreqMS_=120)  # 11x 11.393  =125.323 [ms]
      , 24 : ServiceTaskGilSpec(fiboInput_=24, fiboCpuTimeMS_=16.964, runPhaseFreqMS_=200, deficientRunPhaseFreqMS_=180)  # 11x 16.964  =186.604 [ms]
    }


    def __init__ ( self, taskProfile_ : XTaskProfile =None, guiTitle_ : str =None):
        self.__gui              = None
        self.__mdl              = None
        self.__lstSrv           = []
        self.__lstSrvNR         = []
        self.__taskInfo         = None
        self.__fiboInput        = 19
        self.__startTime        = None
        self.__bAutoStart       = True
        self.__bAutoClose       = False
        self.__bGilPaused       = False
        self.__curSrvView       = None
        self.__bDeficientFreq   = False
        self.__dictLastRcvUID   = None

        self.__ctrSnd        = 0
        self.__ctrRcv        = 0
        self.__cntErrSnd     = 0
        self.__ctrOutOfOrder = 0

        self.__dictSrvInfo   = dict()
        self.__srvTaskCount  = MainTaskGIL.__MAX_NUM_ASYNC_SERVICE_TASKS

        if isinstance(guiTitle_, str):
            self.__guiTitle = guiTitle_
        else:
            self.__guiTitle = 'MTGuiAppGIL'

        self.__ScanCmdLineArgs()

        if taskProfile_ is None:
            taskProfile_ = MainTaskGIL.__GetMyTaskProfile()

        UserAppControllerIF.__init__(self)
        MainXTask.__init__(self, taskProfile_=taskProfile_)


    # --------------------------------------------------------------------------
    # own (protected) interface
    # --------------------------------------------------------------------------
    @staticmethod
    def _CreateSingleton(taskProfile_ : Union[XTaskProfile, None]):
        res = MainTaskGIL(taskProfile_=taskProfile_)
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
        self.__startTime = UserAppUtil.GetCurrentTime()

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
                                    , detailViewID_=EDetailViewID.eGil | EDetailViewID.eMainTaskGil | EDetailViewID.eServiceTaskGil
                                    , numServices_=self.__srvTaskCount)

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
        self.__ctrRcv += 1
        #xlogif.LogDebug('[mtGuiAppMain] Received xco-message, msgUID: {}'.format(xmsg_.msgUniqueID))

        # check for out-of-order message?
        lastRcvUID = self.__dictLastRcvUID[xmsg_.msgHeader.msgSender]
        if lastRcvUID is None:
            pass
        elif xmsg_.msgUniqueID <= lastRcvUID:
            self.__ctrOutOfOrder += 1
            xlogif.LogWarning('[mtGuiAppMain][#outOfOrder={}] Received out-of-order message {}, last received one was {}.'.format(self.__ctrOutOfOrder, xmsg_.msgUniqueID, lastRcvUID))

        # store last msg UID received from this sender
        self.__dictLastRcvUID[xmsg_.msgHeader.msgSender] = xmsg_.msgUniqueID

        # message not a service task info?
        if xmsg_.msgHeader.msgLabel != EMsgLabelID.eServiceTaskInfo:
            # don't care, just ignore the message
            return ETernaryCallbackResultID.CONTINUE

        payload   = xmsg_.msgPayload
        msgSender = xmsg_.msgHeader.msgSender

        paramCntErrSnd  = payload.GetParameter(EMsgParamKeyID.eNumSendFailures)
        paramOutOfOrder = payload.GetParameter(EMsgParamKeyID.eNumOutOfOrderReceived)

        srvinfo = self.__dictSrvInfo[msgSender]

        # lock the model if current service view is the one this message is received from
        bBLock = msgSender == self.__lstSrv[self.__curSrvView].xtaskUniqueID
        if bBLock:
            self.__mdl.Lock()

        # update affected service task info of the model
        deltaTime = UserAppUtil.DeltaTime2Str(self.__startTime, bIncludeHours_=True)
        srvinfo.UpdateTaskInfo( deltaTime
                              , sendFailuresCount_=paramCntErrSnd
                              , outOfOrderCnt_=paramOutOfOrder)

        # update own task info of the model
        cntTotalSendErr    = sum( [srvinfo.failuresCountSent       for srvinfo in self.__dictSrvInfo.values()] )
        cntTotalOutOfOrder = sum( [srvinfo.outOfOrderReceivedCount for srvinfo in self.__dictSrvInfo.values()] )
        self.__taskInfo.UpdateTaskInfo( deltaTime
                                      , serviceTasksTotalSendFailuresCount_=cntTotalSendErr
                                      , serviceTasksOutOfOrderReceivedTotalCount_=cntTotalOutOfOrder)

        # unlock the model if it was locked before
        if bBLock:
            self.__mdl.Unlock()

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
            if self.__mdl.serviceTaskGilSpec.isGilPaused:
                if not self.__bGilPaused:
                    res =self.__PostMessage(msgLabelID_=EMsgLabelID.ePauseGIL)
                    self.__bGilPaused = True
            elif self.__bGilPaused:
                self.__bGilPaused = False
                res = self.__PostMessage(msgLabelID_=EMsgLabelID.eResumeGIL)
            else:
                res = self.__PostMessage()

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
            # we're fine, update the model
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
        #NOTE:
        #  - The property 'XTaskProfile.runPhaseFrequencyMS' doesn't matter
        #    as the run-phase of this main task is a single-cycle one.
        #  - see: EHAnalysisMainTask.RunXTask()
        #

        res = XTaskProfile.CreateSynchronousTaskProfile(aliasName_='MainTaskGIL', bPrivilegedTask_=True)

        if res is not None:
            res.isSetupPhaseEnabled         = True
            res.isTeardownPhaseEnabled      = True
            res.isExternalQueueEnabled      = True
            res.runPhaseMaxProcessingTimeMS = 80
        return res

    def __ScanCmdLineArgs(self):
        _FIBO_INPUT_MIN = MainTaskGIL.__FIBO_INPUT_MIN
        _FIBO_INPUT_MAX = MainTaskGIL.__FIBO_INPUT_MAX

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
            elif aa == '--force-deficient-frequency':
                self.__bDeficientFreq = True
            elif aa == '--fibonacci-input':
                if ii >= NUM_ARGS:
                    xlogif.LogWarning(f'[mtGuiAppMain] Missing value for cmdline spec of option \'--fibonacci-input\', fall back to minimum value of {_FIBO_INPUT_MIN}.')
                else:
                    fibo  = sys.argv[ii]
                    ii   += 1
                    try:
                        fibo = int(fibo)
                        if (fibo<_FIBO_INPUT_MIN) or (fibo>_FIBO_INPUT_MAX):
                            xlogif.LogWarning(f'[mtGuiAppMain] Specified input number for Fibonacci calculation is out of range of [{_FIBO_INPUT_MIN}..{_FIBO_INPUT_MAX}], fall back to default value of {_FIBO_INPUT_MIN}.')
                        else:
                            self.__fiboInput = fibo
                    except Exception as xcp:
                        xlogif.LogWarning(f'[mtGuiAppMain] Got exception below for invalid cmdline spec of input number for Fibonacci calculation, fall back to default value of {_FIBO_INPUT_MIN}\n\t{xcp}')
            else:
                pass
        #END while...

        if not self.__bAutoStart:
            self.__bAutoClose =False

        # update gil spec for the selected fibonacci input
        MainTaskGIL.__GIL_SPEC_TABLE[self.__fiboInput].isDeficientFrequencyForced = self.__bDeficientFreq

    def __CreateStartServiceTasks(self) -> int:
        self.__dictLastRcvUID = dict()

        # get gil spec for the selected fibonacci input
        _fiboInputGilSpec = MainTaskGIL.__GIL_SPEC_TABLE[self.__fiboInput]

        for ii in range(self.__srvTaskCount):
            # just to make sure we continue in an error-free state
            self.ClearCurrentError()

            srv = ServiceTaskGIL(ii+1, _fiboInputGilSpec)

            # failed to create task?
            if not srv.isAttachedToFW:
                break

            # failed to start service task?
            if not srv.Start():
                break

            self.__lstSrv.append(srv)
            self.__dictLastRcvUID[srv.xtaskUniqueID] = None

            # create model item for service task info
            srvinfo = TaskInfo( srv.xtaskProfile.aliasName
                              , srv.xtaskUniqueID
                              , UserAppUtil.GetTimestamp()
                              , bAsync_=not srv.xtaskProfile.isSynchronousTask
                              , bMainTask_=False
                              , serviceTaskNo_=ii+1)

            # add model item created above into the internal table
            self.__dictSrvInfo[srv.xtaskUniqueID] = srvinfo

            # wait for a short while before creating/starting next service task
            UserAppUtil.SleepMS(20)
        #END for...

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

        if msgLabelID_ is None:
            msgLabelID_ = EPreDefinedMessagingID.DontCare

        _numSent, _numNotRunnig = 0, 0
        for ii in range(len(self.__lstSrv)):
            _srv = self.__lstSrv[ii]
            if not _srv.isRunning:
                _numNotRunnig += 1
                if _srv.xtaskUniqueID not in self.__lstSrvNR:
                    self.__lstSrvNR.append(_srv.xtaskUniqueID)
                    xlogif.LogWarning(f'[mtGuiAppMain] Service task {_srv.xtaskUniqueID} is not running anymore, ignoring request to post message to.')
                continue

            # send message
            _uid = XMessageManager.SendMessage(_srv, msgLabelID_=msgLabelID_)

            # send attempt failed?
            if _uid < 1:
                # increment number of failures
                self.__cntErrSnd += 1

                self.ClearCurrentError()
                xlogif.LogWarning(f'[mtGuiAppMain][#sendErrors={self.__cntErrSnd}] Failed to send xco message to service task {_srv.xtaskUniqueID}.')
            else:
                _numSent      += 1
                self.__ctrSnd += 1
                #xlogif.LogInfo(f'[mtGuiAppMain] Sent xco message {_uid} to service task {_srv.xtaskUniqueID}.')
        #END for ii...

        res = (_numSent > 0) and (_numSent == len(self.__lstSrv) - _numNotRunnig)
        return res

    def __CreateUserAppModel(self):
        items = dict()

        # version/system info
        items[EModelItemID.eNumCpuCores]   = fwutil.GetAvailableCpuCoresCount()
        items[EModelItemID.eHostPlatfrom]  = fwutil.GetPlatform()
        items[EModelItemID.eXcofdkVersion] = fwutil.GetXcofdkVersion()
        items[EModelItemID.ePythonVersion] = fwutil.GetPythonVersion()

        # main task info
        tinfo = TaskInfo( self.xtaskProfile.aliasName
                        , self.xtaskUniqueID
                        , UserAppUtil.GetTimestamp()
                        , bAsync_=not self.xtaskProfile.isSynchronousTask
                        , bMainTask_=True)
        tinfo.UpdateTaskInfo( UserAppUtil.DeltaTime2Str(self.__startTime, bIncludeHours_=True)
                            , msgCountSent_=self.__ctrSnd
                            , msgCountReceived_=self.__ctrRcv
                            , sendFailuresCount_=self.__cntErrSnd)
        items[EModelItemID.eMainTaskInfo] = tinfo

        # current service task info
        self.__curSrvView = 0
        srv = self.__lstSrv[self.__curSrvView]
        srvinfo = self.__dictSrvInfo[srv.xtaskUniqueID]
        items[EModelItemID.eServiceTaskInfo] = srvinfo

        # get gil spec for the selected fibonacci input
        _fiboInputGilSpec = MainTaskGIL.__GIL_SPEC_TABLE[self.__fiboInput]

        # set gil spec associated with the selected fibonacci input
        items[EModelItemID.eServiceTaskGilSpec] = _fiboInputGilSpec

        self.__mdl      = _UserAppModelImpl(items_=items)
        self.__taskInfo = tinfo

    def __UpdateUserAppModel(self, updateCounter_ : int):
        self.__mdl.Lock()

        cntSrvTaskTotalSendErr    = sum([srvinfo.failuresCountSent       for srvinfo in self.__dictSrvInfo.values()])
        cntSrvTaskTotalOutOfOrder = sum([srvinfo.outOfOrderReceivedCount for srvinfo in self.__dictSrvInfo.values()])

        # main task info
        self.__taskInfo.UpdateTaskInfo( UserAppUtil.DeltaTime2Str(self.__startTime, bIncludeHours_=True)
                                      , msgCountSent_=self.__ctrSnd
                                      , msgCountReceived_=self.__ctrRcv
                                      , sendFailuresCount_=self.__cntErrSnd
                                      , outOfOrderCnt_=self.__ctrOutOfOrder
                                      , serviceTasksTotalSendFailuresCount_=cntSrvTaskTotalSendErr
                                      , serviceTasksOutOfOrderReceivedTotalCount_=cntSrvTaskTotalOutOfOrder)

        # time to switch current service task view
        if (updateCounter_%EGuiConfig.eServiceViewSwitchFrequency.value) == 0:
            self.__curSrvView += 1
            if self.__curSrvView >= len(self.__lstSrv):
                self.__curSrvView = 0

            srv     = self.__lstSrv[self.__curSrvView]
            srvinfo = self.__dictSrvInfo[srv.xtaskUniqueID]
            self.__mdl.SetItem(EModelItemID.eServiceTaskInfo, srvinfo)

        self.__mdl.Unlock()
    # --------------------------------------------------------------------------
    #END Impl
    # --------------------------------------------------------------------------
#END class MainTaskGIL
