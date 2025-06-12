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
from xuserapp.st.welcome.common.commondefs       import EGuiConfig
from xuserapp.st.welcome.common.commondefs       import EDetailViewID
from xuserapp.st.welcome.interfaces.modelif      import EModelItemID
from xuserapp.st.welcome.interfaces.modelif      import TaskInfo
from xuserapp.st.welcome.interfaces.modelif      import ServiceTaskGilSpec
from xuserapp.st.welcome.interfaces.modelif      import UserAppModelIF
from xuserapp.st.welcome.interfaces.controllerif import UserAppControllerIF
from xuserapp.st.welcome.stguiappwelcome         import STGuiAppWelcome

from xuserapp.basic.xmt.xmtmisc.commondefs       import EMsgLabelID
from xuserapp.basic.xmt.xmtmisc.commondefs       import EMsgParamKeyID
from xuserapp.basic.xmt.rc.rcmisc.servicetaskGIL import CreateServiceTaskGIL


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
def _CreateMainTaskGIL(cmdLineOpts_ : CLOptions) -> IRCCommTask:
    _phasedXFCallback = XFMainTaskGIL(cmdLineOpts_, guiTitle_='XMTGuiAppGIL')
    res = XFSyncCommTask(_phasedXFCallback, aliasName_='MainTask', bMainTask_=True)
    return res
#END _CreateMainTaskGIL()


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


class XFMainTaskGIL(UserAppControllerIF):

    __slots__ = [ '__gui' , '__mdl' , '__cmdLine' , '__ctrSnd' , '__ctrRcv' , '__lstSrv' , '__lstSrvNR' , '__taskInfo'
                , '__srvTaskCount' , '__dictSrvInfo' , '__curSrvView' , '__guiTitle' , '__cntErrSnd' , '__dictLastRcvUID'
                , '__bGilPaused' , '__ctrOutOfOrder' , '__startTime' , '__fiboInput' , '__myCTsk' ]

    __NUM_ASYNC_SRV = 12

    __GIL_SPEC_TABLE = {
        19 : ServiceTaskGilSpec(fiboInput_=19, fiboCpuTimeMS_=1.463, runPhaseFreqMS_=25, deficientRunPhaseFreqMS_=15)     # 11x  1.463  = 16.903 [ms]
      , 20 : ServiceTaskGilSpec(fiboInput_=20, fiboCpuTimeMS_=2.343, runPhaseFreqMS_=40, deficientRunPhaseFreqMS_=20)     # 11x  2.343  = 25.773 [ms]
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
        self.__guiTitle       = guiTitle_ if isinstance(guiTitle_, str) else 'XMTGuiAppGIL'
        self.__lstSrvNR       = []
        self.__fiboInput      = cmdLineOpts_.fibonacciInput
        self.__taskInfo       = None
        self.__startTime      = None
        self.__bGilPaused     = False
        self.__curSrvView     = None
        self.__dictLastRcvUID = None

        self.__ctrSnd        = 0
        self.__ctrRcv        = 0
        self.__cntErrSnd     = 0
        self.__ctrOutOfOrder = 0

        self.__dictSrvInfo   = dict()
        self.__srvTaskCount  = XFMainTaskGIL.__NUM_ASYNC_SRV

        # update gil spec for the selected fibonacci input
        XFMainTaskGIL.__GIL_SPEC_TABLE[self.__fiboInput].isDeficientFrequencyForced = cmdLineOpts_.isForceDeficientFrequencyEnabled

        super().__init__()


    # --------------------------------------------------------------------------
    # phasedXF callbacks
    # --------------------------------------------------------------------------
    def SetUpTask(self) -> EExecutionCmdID:
        self.__myCTsk    = GetCurTask()
        self.__startTime = UserAppUtil.GetCurrentTime()

        # create and start service tasks
        _numStarted = self.__CreateStartServiceTasks()

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
                                    , detailViewID_=EDetailViewID.eGil | EDetailViewID.eMainTaskGil | EDetailViewID.eServiceTaskGil
                                    , numServices_=self.__srvTaskCount)

        xlogif.LogInfo(f'[mtGuiAppMain] Finished setup, {_numStarted} serivce tasks started.')
        return EExecutionCmdID.CONTINUE

    def RunTask(self) -> EExecutionCmdID:
        xlogif.LogInfo(f'[mtGuiAppMain] Starting run-phase of the main task {self.__myTask.taskUID}...')

        if not self.__gui.StartView():
            res = EExecutionCmdID.ABORT
        else:
            res = EExecutionCmdID.STOP

        xlogif.LogInfo(f'[mtGuiAppMain] GUI view returned, activity state: {self.__gui.isActive}')

        # release referece to gui/Tk's root window
        self.__gui = None

        if res.isSTOP:
            xlogif.LogInfo(f'[mtGuiAppMain] Finished run-phase of the main task {self.__myTask.taskUID}.')
        return res

    def TearDownTask(self) -> EExecutionCmdID:
        for ii in range(len(self.__lstSrv)):
            _srv = self.__lstSrv[ii]
            #xlogif.LogDebug(f'[mtGuiAppMain] Joining service task {_srv.taskUID}...')
            _srv.Join()
            xlogif.LogDebug(f'[mtGuiAppMain] Joined service task {_srv.taskUID}.')
        return EExecutionCmdID.STOP

    def ProcessExternalMessage(self, xmsg_ : IMessage) -> EExecutionCmdID:
        self.__ctrRcv += 1
        #xlogif.LogDebug('[mtGuiAppMain] Received xco-message, msgUID: {}'.format(xmsg_.msgUniqueID))

        # check for out-of-order message?
        lastRcvUID = self.__dictLastRcvUID[xmsg_.msgHeader.msgSender]
        if lastRcvUID is None:
            pass
        elif xmsg_.msgUniqueID <= lastRcvUID:
            self.__ctrOutOfOrder += 1
            xlogif.LogWarning('[mtGuiAppMain][#outOfOrder={}] Received out-of-order message {}, last received one was {}.'.format(
                self.__ctrOutOfOrder, xmsg_.msgUniqueID, lastRcvUID))

        # store last msg UID received from this sender
        self.__dictLastRcvUID[xmsg_.msgHeader.msgSender] = xmsg_.msgUniqueID

        # message not a service task info?
        if xmsg_.msgHeader.msgLabel != EMsgLabelID.eServiceTaskInfo:
            # don't care, just ignore the message
            return EExecutionCmdID.CONTINUE

        payload   = xmsg_.msgPayload
        msgSender = xmsg_.msgHeader.msgSender

        paramCntErrSnd  = payload.GetParameter(EMsgParamKeyID.eNumSendFailures)
        paramOutOfOrder = payload.GetParameter(EMsgParamKeyID.eNumOutOfOrderReceived)

        srvinfo = self.__dictSrvInfo[msgSender]

        # lock the model if current service view is the one this message is received from
        bBLock = msgSender == self.__lstSrv[self.__curSrvView].taskUID
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
        return EExecutionCmdID.CONTINUE
    # --------------------------------------------------------------------------
    #END phasedXF callbacks
    # --------------------------------------------------------------------------


    # --------------------------------------------------------------------------
    # override of interface inherited from UserAppControllerIF
    # --------------------------------------------------------------------------
    @UserAppControllerIF.isControllerRunning.getter
    def isControllerRunning(self):
        return self.__myTask.isRunning

    @override
    def OnViewNotification(self, notifCounter_ : int, bProgressBarProceeding_ : bool =False, bOnDestroy_ =False) -> bool:
        if bProgressBarProceeding_:
            # currently no use for this flag, just ignore it
            pass

        # main task not running anymore?
        if not self.__myTask.isRunning:
            return False

        # is gui going to be destroyed?
        if bOnDestroy_:
            #[NOTE]
            #  a) make sure all services are stopped before the main task leaves its run-phase,
            #     i.e. its 'running' state,
            #  b) alternatively, a) could be skipped in which case service instances are
            #     recommended to perform a pre-check on the avilability of the main task
            #     before attempting to send out their next message, see impl of method below:
            #         XFServiceTaskGIL.__PostMessage():
            #
            self.__StopServiceTasks()

            # stop own task, i.e. the main task
            self.__myTask.Stop()

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
            res = self.__myTask.TriggerExternalQueueProcessing() > -1

            # something went wrong while processing queued external messages?
            if not res:
                # try to clear own current error
                self.__myTask.ClearCurrentError()

                # submit a new error message
                xlogif.LogError(f'[mtGuiAppMain][notifCounter={notifCounter_}] Failed to trigger external queue processing.')

        res = res and self.__myTask.isRunning
        if res:
            # we're fine, update the model
            self.__UpdateUserAppModel(notifCounter_)
        return res

    @override
    def OnViewEncounteredException(self, errMsg_ : str, xcp_ : Exception):
        self.__StopServiceTasks()

        # main task has caused/detected a fatal error already?
        if not self.__myTask.isFatalErrorFree:
            # nothing to do, no need to cause addintional one
            pass
        else:
            # unexpected exception, main task will consider it an LC failure, so notify the framework accordingly
            xlogif.LogExceptionEC(errMsg_, xcp_, 1031001)
    # --------------------------------------------------------------------------
    #END override of interface inherited from UserAppControllerIF
    # --------------------------------------------------------------------------


    # --------------------------------------------------------------------------
    # Impl
    # --------------------------------------------------------------------------
    @property
    def __myTask(self) -> IRCCommTask:
        return self.__myCTsk

    def __CreateStartServiceTasks(self) -> int:
        self.__dictLastRcvUID = dict()

        # get gil spec for the selected fibonacci input
        _fiboInputGilSpec = XFMainTaskGIL.__GIL_SPEC_TABLE[self.__fiboInput]

        for ii in range(self.__srvTaskCount):
            # just to make sure we continue in an error-free state
            self.__myTask.ClearCurrentError()

            _srv = CreateServiceTaskGIL(ii+1, _fiboInputGilSpec)

            # failed to create task?
            if not _srv.isAttachedToFW:
                break

            # failed to start service task?
            if not _srv.Start():
                break

            self.__lstSrv.append(_srv)
            self.__dictLastRcvUID[_srv.taskUID] = None

            # create model item for service task info
            srvinfo = TaskInfo( _srv.aliasName
                              , _srv.taskUID
                              , UserAppUtil.GetTimestamp()
                              , bAsync_=not _srv.isSyncTask
                              , bMainTask_=False
                              , serviceTaskNo_=ii+1)

            # add model item created above into the internal table
            self.__dictSrvInfo[_srv.taskUID] = srvinfo

            # wait for a short while before creating/starting next service task
            #UserAppUtil.SleepMS(20)
            self.__myTask.SelfCheckSleep(20)
            if not self.__myTask.isRunning:
                break
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
            _errMsg = f'Unexpected runtime condition of {self.__guiTitle}, all {self.__srvTaskCount} service tasks stopped running already.'
            xlogif.LogError(_errMsg)

            # wait for a few seconds, then throw an exception
            UserAppUtil.SleepSEC(3.0)
            raise Exception(_errMsg)

        if msgLabelID_ is None:
            msgLabelID_ = EXmsgPredefinedID.DontCare

        _numSent, _numNotRunnig = 0, 0
        for ii in range(len(self.__lstSrv)):
            _srv = self.__lstSrv[ii]
            if not _srv.isRunning:
                _numNotRunnig += 1
                if _srv.taskUID not in self.__lstSrvNR:
                    self.__lstSrvNR.append(_srv.taskUID)
                    xlogif.LogWarning(f'[mtGuiAppMain] Service task {_srv.taskUID} is not running anymore, ignoring request to post message to.')
                continue

            # send message
            _uid = self.__myTask.SendMessage(_srv, msgLabelID_=msgLabelID_)

            # send attempt failed?
            if _uid < 1:
                # increment number of failures
                self.__cntErrSnd += 1

                self.__myTask.ClearCurrentError()
                xlogif.LogWarning(f'[mtGuiAppMain][#sendErrors={self.__cntErrSnd}] Failed to send xco message to service task {_srv.taskUID}.')
            else:
                _numSent      += 1
                self.__ctrSnd += 1
                #xlogif.LogInfo(f'[mtGuiAppMain] Sent xco message {_uid} to service task {_srv.taskUID}.')
        #END for ii...

        res = (_numSent > 0) and (_numSent == len(self.__lstSrv) - _numNotRunnig)
        return res

    def __CreateUserAppModel(self):
        items = dict()

        # version/system info
        items[EModelItemID.eNumCpuCores]   = fwutil.GetAvailableCpuCoresCount()
        items[EModelItemID.eHostPlatfrom]  = fwutil.GetPlatform()
        items[EModelItemID.eXcofdkVersion] = fwutil.GetXcofdkVersion()
        items[EModelItemID.ePythonVersion] = UserAppUtil.GetPythonVersion()

        # main task info
        tinfo = TaskInfo( self.__myTask.aliasName
                        , self.__myTask.taskUID
                        , UserAppUtil.GetTimestamp()
                        , bAsync_=not self.__myTask.isSyncTask
                        , bMainTask_=True)
        tinfo.UpdateTaskInfo( UserAppUtil.DeltaTime2Str(self.__startTime, bIncludeHours_=True)
                            , msgCountSent_=self.__ctrSnd
                            , msgCountReceived_=self.__ctrRcv
                            , sendFailuresCount_=self.__cntErrSnd)
        items[EModelItemID.eMainTaskInfo] = tinfo

        # current service task info
        self.__curSrvView = 0
        _srv = self.__lstSrv[self.__curSrvView]
        srvinfo = self.__dictSrvInfo[_srv.taskUID]
        items[EModelItemID.eServiceTaskInfo] = srvinfo

        # get gil spec for the selected fibonacci input
        _fiboInputGilSpec = XFMainTaskGIL.__GIL_SPEC_TABLE[self.__fiboInput]

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

            _srv     = self.__lstSrv[self.__curSrvView]
            srvinfo = self.__dictSrvInfo[_srv.taskUID]
            self.__mdl.SetItem(EModelItemID.eServiceTaskInfo, srvinfo)

        self.__mdl.Unlock()
    # --------------------------------------------------------------------------
    #END Impl
    # --------------------------------------------------------------------------
#END class XFMainTaskGIL
