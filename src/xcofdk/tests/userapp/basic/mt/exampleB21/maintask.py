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
from xcofdk.fwapi.xmsg         import XPayload
from xcofdk.fwapi.xmsg.xmsgmgr import XMessageManager

from xcofdk.tests.userapp.util.userAppUtil import UserAppUtil

from xcofdk.tests.userapp.st.welcome.common.commondefs       import EGuiConfig
from xcofdk.tests.userapp.st.welcome.common.commondefs       import EDetailViewID
from xcofdk.tests.userapp.st.welcome.interfaces.modelif      import EModelItemID
from xcofdk.tests.userapp.st.welcome.interfaces.modelif      import TaskInfo
from xcofdk.tests.userapp.st.welcome.interfaces.modelif      import UserAppModelIF
from xcofdk.tests.userapp.st.welcome.interfaces.controllerif import UserAppControllerIF
from xcofdk.tests.userapp.st.welcome.stguiappwelcome         import STGuiAppWelcome

from xcofdk.tests.userapp.basic.mt.mtmisc.commondefs     import EPreDefinedMessagingID
from xcofdk.tests.userapp.basic.mt.mtmisc.commondefs     import EMsgLabelID
from xcofdk.tests.userapp.basic.mt.mtmisc.commondefs     import EMsgClusterID
from xcofdk.tests.userapp.basic.mt.mtmisc.commondefs     import EMsgParamKeyID
from xcofdk.tests.userapp.basic.mt.mtmisc.custompayload  import CustomPayload
from xcofdk.tests.userapp.basic.mt.mtmisc.servicetask    import ServiceTask
from xcofdk.tests.userapp.basic.mt.mtmisc.servicetaskBXQ import ServiceTaskBXQ


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


class MainTask(MainXTask, UserAppControllerIF):

    __slots__ = [ '__gui'         , '__mdl'           , '__bAutoStart'  , '__bAutoClose'
                , '__ctrSnd'      , '__ctrRcv'        , '__lstSrv'      , '__lstSrvNR'
                , '__taskInfo'    , '__srvTaskCount'  , '__dictSrvInfo' , '__curSrvView'
                , '__bSkipSerDes' , '__guiTitle'      , '__cntErrSnd'   , '__bPostingPaused'
                , '__bBroadcast'  , '__ctrOutOfOrder' , '__bCustomPLD'  , '__bBlockingSrvTsk'
                , '__startTime'   , '__dictLastRcvUID'
                ]

    __MAX_NUM_ASYNC_SERVICE_TASKS = 12

    def __init__ ( self
                 , taskProfile_       : XTaskProfile =None
                 , guiTitle_          : str          =None
                 , bBroadcast_                       =False
                 , bBlockingSrvTask_                 =False
                 , bSkipPayloadSerDes_               =False
                 , bCustomPayLoad_                   =False):
        self.__gui             = None
        self.__mdl             = None
        self.__lstSrv          = []
        self.__lstSrvNR        = []
        self.__taskInfo        = None
        self.__startTime       = None
        self.__bAutoStart      = True
        self.__bAutoClose      = False
        self.__bBroadcast      = bBroadcast_
        self.__curSrvView      = None
        self.__bCustomPLD      = bCustomPayLoad_
        self.__bSkipSerDes     = bSkipPayloadSerDes_
        self.__dictSrvInfo     = dict()
        self.__bPostingPaused  = False
        self.__dictLastRcvUID  = None
        self.__bBlockingSrvTsk = bBlockingSrvTask_

        self.__ctrSnd        = 0
        self.__ctrRcv        = 0
        self.__cntErrSnd     = 0
        self.__ctrOutOfOrder = 0

        if isinstance(guiTitle_, str):
            self.__guiTitle = guiTitle_
        elif bCustomPayLoad_:
            self.__guiTitle = 'MTGuiAppCoustomPayload'
        elif bBroadcast_:
            self.__guiTitle = 'MTGuiAppBroadcast'
        elif bBlockingSrvTask_:
            self.__guiTitle = 'MTGuiAppCoustomPayload'
        elif bSkipPayloadSerDes_:
            self.__guiTitle = 'MTGuiAppNoSerDes'
        else:
            self.__guiTitle = 'MTGuiAppMessaging'

        _bAsync = self.__ScanCmdLineArgs()
        if taskProfile_ is None:
            taskProfile_ = self.__GetMyTaskProfile(_bAsync)

        UserAppControllerIF.__init__(self)
        MainXTask.__init__(self, taskProfile_=taskProfile_)


    # --------------------------------------------------------------------------
    # own (protected) interface
    # --------------------------------------------------------------------------
    @staticmethod
    def _CreateSingleton(taskProfile_ : Union[XTaskProfile, None]):
        res = MainTask(taskProfile_=taskProfile_)
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
        self.__CreateUserAppModel(UserAppUtil.GetTimestamp())

        # create gui, but caution:
        #  - creating and releasing/destroying Tk's root window should always happen in the same task/thread  !!
        #
        self.__gui = STGuiAppWelcome( title_=self.__guiTitle
                                    , bAutoStart_=self.__bAutoStart
                                    , bAutoClose_=self.__bAutoClose
                                    , controllerif_=self
                                    , modelif_=self.__mdl
                                    , detailViewID_=EDetailViewID.eMainTaskMsgInfo | EDetailViewID.eServiceTaskMsgInfo
                                    , numServices_=self.__srvTaskCount
                                    , bBroadcast_=self.__bBroadcast
                                    , bBlockingSrvTsk_=self.__bBlockingSrvTsk)

        xlogif.LogInfo(f'[mtGuiAppMain] Finished setup, {_numStarted} serivce tasks started.')
        return ETernaryCallbackResultID.CONTINUE

    @override
    def RunXTask(self) -> ETernaryCallbackResultID:
        xlogif.LogInfo(f'[mtGuiAppMain] Starting run-phase of the main task {self.xtaskUniqueID}...')

        # start gui
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

        # message expected to carry custom payload?
        if self.__bCustomPLD:
            # unexpected payload type?
            if not isinstance(payload, CustomPayload):
                xlogif.LogWarning('[mtGuiAppMain] Message {} refers to an unexpected payload object type: {}.'.format(xmsg_.msgUniqueID, type(payload).__name__))
                return ETernaryCallbackResultID.CONTINUE

            paramSnt        = payload.countSent
            paramRcv        = payload.countReceived
            paramCntErrSnd  = payload.countFailure
            paramOutOfOrder = payload.countOutOfOrder

        # ordinary payload
        else:
            paramSnt        = payload.GetParameter(EMsgParamKeyID.eNumMsgSent)
            paramRcv        = payload.GetParameter(EMsgParamKeyID.eNumMsgReceived)
            paramCntErrSnd  = payload.GetParameter(EMsgParamKeyID.eNumSendFailures)
            paramOutOfOrder = payload.GetParameter(EMsgParamKeyID.eNumOutOfOrderReceived)

        # lock the model if current service view is the one this message is received from
        bBLock = msgSender == self.__lstSrv[self.__curSrvView].xtaskUniqueID
        if bBLock:
            self.__mdl.Lock()

        # update affected service task info of the model
        srvinfo   = self.__dictSrvInfo[msgSender]
        deltaTime = UserAppUtil.DeltaTime2Str(self.__startTime, bIncludeHours_=True)
        srvinfo.UpdateTaskInfo( deltaTime
                              , msgCountSent_=paramSnt
                              , msgCountReceived_=paramRcv
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

        # just to be very brave, make allocated resources for the payload get released (if applicable)
        if payload is not None:
            if isinstance(payload, XPayload):
                if not payload.isMarshalingRequired:
                    cont = payload.DetachContainer()
                    if cont is not None:
                        cont.clear()

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

            # indicate that the main task is going to stop running
            self.Stop()

            # done, acknowledge this notification
            return True


        # time to post a new message to the service tasks?
        if (notifCounter_%5) == 0:
            if self.__mdl.isPostingPaused:
                if not self.__bPostingPaused:
                    res = self.__PostMessage(msgLabelID_=EMsgLabelID.ePausePosting)
                    self.__bPostingPaused = True
                else:
                    res = True
            elif self.__bPostingPaused:
                self.__bPostingPaused = False
                res = self.__PostMessage(msgLabelID_=EMsgLabelID.eResumePosting)
            else:
                bJobReq = (notifCounter_ % 20) == 0

                labelID   = EMsgLabelID.eJobRequest      if bJobReq else None
                clusterID = EMsgClusterID.eJobProcessing if bJobReq else None

                res = self.__PostMessage(msgLabelID_=labelID, msgClusterID_=clusterID)

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
    def __ScanCmdLineArgs(self):
        _MAX_NUM_SRV_TASKS = MainTask.__MAX_NUM_ASYNC_SERVICE_TASKS

        _bAsync, _srvTaskCount = False, MainTask.__MAX_NUM_ASYNC_SERVICE_TASKS

        ii, NUM_ARGS = 1, len(sys.argv)
        while ii < NUM_ARGS:
            aa  = sys.argv[ii]
            ii += 1

            if aa.startswith('#'):
                break
            if aa == '--enable-async-execution':
                _bAsync = True
            elif aa == '--disable-auto-start':
                self.__bAutoStart = False
            elif aa == '--enable-auto-close':
                self.__bAutoClose = True
            elif aa == '--service-tasks-count':
                if ii >= NUM_ARGS:
                    xlogif.LogWarning(f'[mtGuiAppMain] Missing value for cmdline spec of option \'--service-tasks-count\', fall back to default value of {self.__srvTaskCount}.')
                else:
                    _vv  = sys.argv[ii]
                    ii += 1
                    try:
                        cnt = int(_vv)
                        if (cnt<1) or (cnt>_MAX_NUM_SRV_TASKS):
                            xlogif.LogWarning(f'[mtGuiAppMain] Specified number of service tasks out of range of [1..{_MAX_NUM_SRV_TASKS}], fall back to default value of {self.__srvTaskCount}.')
                        else:
                            _srvTaskCount = cnt
                    except Exception as xcp:
                        xlogif.LogWarning(f'[mtGuiAppMain] Got exception below for invalid cmdline spec of number of service tasks, fall back to default value of {self.__srvTaskCount}\n\t{xcp}')
                    finally:
                        pass
            else:
                pass
        #END while...

        # auto-start of the progress bar not requested?
        if not self.__bAutoStart:
            # do not auto-close the gui
            self.__bAutoClose = False

        self.__srvTaskCount = _srvTaskCount
        return _bAsync

    def __GetMyTaskProfile(self, bAsync_ : bool) -> XTaskProfile:
        #NOTE:
        #  - The property 'XTaskProfile.runPhaseFrequencyMS' doesn't matter
        #    as the run-phase of this main task is a single-cycle one.
        #  - see: MainTask.RunXTask()
        #

        if self.__bCustomPLD:
            _aliasName = 'MainTaskCPL'
        elif self.__bBroadcast:
            _aliasName = 'MainTaskBC'
        elif self.__bSkipSerDes:
            _aliasName = 'MainTaskNoSD'
        elif self.__bBlockingSrvTsk:
            _aliasName = 'MainTaskBXQ'
        else:
            _aliasName = 'MainTask'

        if bAsync_:
            res = XTaskProfile.CreateAsynchronousTaskProfile(aliasName_=_aliasName, bPrivilegedTask_=True)
        else:
            res = XTaskProfile.CreateSynchronousTaskProfile(aliasName_=_aliasName, bPrivilegedTask_=True)

        if res is not None:
            res.isSetupPhaseEnabled         = True
            res.isTeardownPhaseEnabled      = True
            res.isExternalQueueEnabled      = True
            res.runPhaseMaxProcessingTimeMS = 80
        return res

    def __CreateStartServiceTasks(self) -> int:
        self.__dictLastRcvUID = dict()

        for ii in range(self.__srvTaskCount):
            if not fwutil.IsLcFailureFree():
                break

            # just to make sure we continue in an error-free state
            self.ClearCurrentError()

            if self.__bBlockingSrvTsk:
                srv = ServiceTaskBXQ(ii+1, bBroadcast_=self.__bBroadcast)
            else:
                srv = ServiceTask(ii+1, bBroadcast_=self.__bBroadcast, bSkipPayloadSerDes_=self.__bSkipSerDes, bCustomPayLoad_=self.__bCustomPLD)

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

    def __PostMessage(self, srvTask_ : ServiceTask =None, msgLabelID_ : EMsgLabelID =None, msgClusterID_ : EMsgClusterID =None) -> bool:
        # all service tasks stopped running?
        if self.__GetRunningServiceTasksCount() < 1:
            _errMsg = f'Unexpected runtime condition, all {self.__srvTaskCount} service tasks stopped running.'
            xlogif.LogError(_errMsg)

            # wait for a few seconds, then throw an exception
            UserAppUtil.SleepSEC(3.0)
            raise Exception(_errMsg)

        _lst = self.__lstSrv if srvTask_ is None else [srvTask_]

        # broadcast posting?
        #
        if self.__bBroadcast:
            if msgLabelID_ is None:
                msgLabelID_ = EMsgLabelID.eBroadcastPinging

            # broadcast message
            _uid = XMessageManager.BroadcastMessage(msgLabelID_)

            # send attempt successful?
            res = _uid > 0
            if not res:
                # increment number of failures
                self.__cntErrSnd += 1

                self.ClearCurrentError()
                xlogif.LogError(f'[mtGuiAppMain][#sendErrors={self.__cntErrSnd}] Failed to broadcast xco message to {len(_lst)} service task(s).')
            else:
                self.__ctrSnd += 1
                #xlogif.LogInfo(f'[mtGuiAppMain] Sent broadcast message to {len(_lst)} service task(s).')
            return res
        #END if self.__bBroadcast:


        # direct addressing
        #
        _numSent, _numNotRunnig = 0, 0
        for ii in range(len(_lst)):
            _srv = _lst[ii]
            if not _srv.isRunning:
                _numNotRunnig += 1
                if _srv.xtaskUniqueID not in self.__lstSrvNR:
                    self.__lstSrvNR.append(_srv.xtaskUniqueID)
                    xlogif.LogWarning(f'[mtGuiAppMain] Service task {_srv.xtaskUniqueID} is not running anymore, ignoring request to post message to.')
                continue

            if msgLabelID_ is None:
                msgLabelID_ = EPreDefinedMessagingID.DontCare
            if msgClusterID_ is None:
                msgClusterID_ = EPreDefinedMessagingID.DontCare

            # send message
            _uid = XMessageManager.SendMessage(_srv, msgLabelID_=msgLabelID_, msgClusterID_=msgClusterID_)

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

        res = (_numSent > 0) and (_numSent == len(_lst) - _numNotRunnig)
        return res

    def __CreateUserAppModel(self, mainTaskStartTime_ : str):
        items = dict()

        # version/system info
        items[EModelItemID.eNumCpuCores]   = fwutil.GetAvailableCpuCoresCount()
        items[EModelItemID.eHostPlatfrom]  = fwutil.GetPlatform()
        items[EModelItemID.eXcofdkVersion] = fwutil.GetXcofdkVersion()
        items[EModelItemID.ePythonVersion] = fwutil.GetPythonVersion()

        # main task info
        tinfo = TaskInfo( self.xtaskProfile.aliasName
                        , self.xtaskUniqueID
                        , mainTaskStartTime_
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

        self.__mdl      = _UserAppModelImpl(items_=items)
        self.__taskInfo = tinfo

    def __UpdateUserAppModel(self, updateCounter_ : int):
        self.__mdl.Lock()

        cntSrvTaskTotalSnt        = sum([srvinfo.messageCountSent        for srvinfo in self.__dictSrvInfo.values()])
        cntSrvTaskTotalRcv        = sum([srvinfo.messageCountReceived    for srvinfo in self.__dictSrvInfo.values()])
        cntSrvTaskTotalSendErr    = sum([srvinfo.failuresCountSent       for srvinfo in self.__dictSrvInfo.values()])
        cntSrvTaskTotalOutOfOrder = sum([srvinfo.outOfOrderReceivedCount for srvinfo in self.__dictSrvInfo.values()])

        # main task info
        self.__taskInfo.UpdateTaskInfo( UserAppUtil.DeltaTime2Str(self.__startTime, bIncludeHours_=True)
                                      , msgCountSent_=self.__ctrSnd
                                      , msgCountReceived_=self.__ctrRcv
                                      , sendFailuresCount_=self.__cntErrSnd
                                      , outOfOrderCnt_=self.__ctrOutOfOrder
                                      , serviceTasksTotalSentCount_=cntSrvTaskTotalSnt
                                      , serviceTasksTotalReceivedCount_=cntSrvTaskTotalRcv
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
#END class MainTask
