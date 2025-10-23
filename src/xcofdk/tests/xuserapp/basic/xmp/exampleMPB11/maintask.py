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
from xcofdk.fwcom     import EExecutionCmdID
from xcofdk.fwcom     import override
from xcofdk.fwapi     import fwutil
from xcofdk.fwapi     import xlogif
from xcofdk.fwapi     import XProcess
from xcofdk.fwapi     import IRCTask
from xcofdk.fwapi     import XFSyncTask
from xcofdk.fwapi     import GetCurTask
from xcofdk.fwapi.xmp import XmpUtil

from xuserapp.util.cloptions                     import CLOptions
from xuserapp.util.userAppUtil                   import UserAppUtil
from xuserapp.st.welcome.common.commondefs       import EDetailViewID
from xuserapp.st.welcome.interfaces.modelif      import EModelItemID
from xuserapp.st.welcome.interfaces.modelif      import UserAppModelIF
from xuserapp.st.welcome.interfaces.modelif      import MPServiceProcessResult
from xuserapp.st.welcome.interfaces.modelif      import MPServiceProcess
from xuserapp.st.welcome.interfaces.controllerif import UserAppControllerIF
from xuserapp.st.welcome.stguiappwelcome         import STGuiAppWelcome


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
def _CreateMainTaskMP(cmdLineOpts_ : CLOptions, guiTitle_ : str =None) -> IRCTask:
    _aliasName        = 'MainTaskMP'
    _phasedXFCallback = XFMainTaskMP(cmdLineOpts_, guiTitle_=guiTitle_)
    res = XFSyncTask(_phasedXFCallback, aliasName_=_aliasName, bMainTask_=True)
    return res
#END _CreateMainTaskMP()


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


class XFMainTaskMP(UserAppControllerIF):

    __slots__ = [ '__gui' , '__mdl' , '__lstSrv' , '__guiTitle' , '__ctrMpRun' , '__startTime' , '__cmdLine' , '__myTsk'
                , '__bAllProcDone' , '__mpNumErr' , '__bMPPaused' , '__srvProcCnt' , '__lstProcRes' , '__ctrFiboTrigger' ]

    __SRV_PROC_SPEC_TABLE = {
        35 : MPServiceProcessResult(fiboInput_=35)
      , 36 : MPServiceProcessResult(fiboInput_=36)
      , 37 : MPServiceProcessResult(fiboInput_=37)
      , 38 : MPServiceProcessResult(fiboInput_=38)
    }

    __FIBO_BASE_INPUT           = 35
    __MAX_NUM_SERVICE_PROCESSES = 3

    def __init__ ( self, cmdLineOpts_ : CLOptions, guiTitle_ : str =None):
        self.__gui            = None
        self.__mdl            = None
        self.__myTsk          = None
        self.__lstSrv         = []
        self.__cmdLine        = cmdLineOpts_
        self.__ctrMpRun       = 0
        self.__guiTitle       = guiTitle_ if isinstance(guiTitle_, str) else 'XMPGuiApp'
        self.__mpNumErr       = 0
        self.__startTime      = None
        self.__bMPPaused      = False
        self.__lstProcRes     = []
        self.__srvProcCnt     = XFMainTaskMP.__MAX_NUM_SERVICE_PROCESSES
        self.__bAllProcDone   = False
        self.__ctrFiboTrigger = 0

        if not (0 < XFMainTaskMP.__MAX_NUM_SERVICE_PROCESSES <= 3):
            XFMainTaskMP.__MAX_NUM_SERVICE_PROCESSES = 3
        if not (34 < XFMainTaskMP.__FIBO_BASE_INPUT < 39):
            XFMainTaskMP.__MAX_NUM_SERVICE_PROCESSES = 35

        _fiboBaseIn = XFMainTaskMP.__FIBO_BASE_INPUT
        for ii in range(self.__srvProcCnt):
            self.__lstProcRes.append(XFMainTaskMP.__SRV_PROC_SPEC_TABLE[_fiboBaseIn+ii])

        super().__init__()


    # --------------------------------------------------------------------------
    # phasedXF callbacks
    # --------------------------------------------------------------------------
    def SetUpTask(self) -> EExecutionCmdID:
        self.__myTsk     = GetCurTask()
        self.__startTime = UserAppUtil.GetCurrentTime()
        self.__CreateUserAppModel()

        # create gui, but caution:
        #  - creating and releasing/destroying Tk's root window should always happen in the same task/thread  !!
        #
        self.__gui = STGuiAppWelcome( title_=self.__guiTitle
                                    , bAutoStart_=self.__cmdLine.isAutoStartEnabled
                                    , bAutoClose_=self.__cmdLine.isAutoCloseEnabled
                                    , controllerif_=self
                                    , modelif_=self.__mdl
                                    , detailViewID_=EDetailViewID.eFibonacciResultMP
                                    , numServices_=self.__srvProcCnt)

        xlogif.LogInfo(f'Finished setup.')
        return EExecutionCmdID.CONTINUE

    def RunTask(self) -> EExecutionCmdID:
        xlogif.LogInfo(f'Starting run-phase of the main task {self.__myTask.taskUID}...')

        if not self.__gui.StartView():
            res = EExecutionCmdID.ABORT
        else:
            res = EExecutionCmdID.STOP

        xlogif.LogInfo(f'GUI view returned, activity state: {self.__gui.isActive}')

        # release referece to gui/Tk's root window
        self.__gui = None

        xlogif.LogInfo(f'Finished run-phase of the main task {self.__myTask.taskUID}.')
        return res

    def TearDownTask(self) -> EExecutionCmdID:
        self.__DetachServices(bLogInfo_=True)
        return EExecutionCmdID.STOP
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
            # stop own task, i.e. the main task
            self.__myTask.Stop()

            # done, acknowledge this notification
            return True


        # update main task's duration time
        self.__UpdateUserAppModel(bDTimeOnly_=True)

        res = True

        # in 'paused' state?
        if self.__bMPPaused:
            if not self.__mdl.serviceProcess.isPaused:
                self.__bMPPaused = False

        # no fibonacci request sent out?
        elif not self.__isFiboReuested:
            # start service processes
            self.__DetachServices()
            res = self.__StartServices()

        # fibonacci reply received already?
        elif self.__isFiboRequestDone:
            self.__ctrFiboTrigger += 1

            if not self.__bAllProcDone:
                self.__CheckUpdateProcResults()
                self.__bAllProcDone = True

            if self.__mdl.serviceProcess.isPaused:
                self.__bMPPaused = True
            else:
                _DIVISOR = self.__srvProcCnt * 20

                # time to trigger new fibo request (ca. 2s to 6s)?
                if (self.__ctrFiboTrigger%_DIVISOR) == 0:
                    self.__ctrFiboTrigger = 0

                    # create new service processes next time we get notified by the view
                    self.__DetachServices()

        # update services' state/result (every 100 [ms])
        else:
            self.__CheckUpdateProcResults()

        res = res and self.__myTask.isRunning
        return res

    @override
    def OnViewEncounteredException(self, errMsg_ : str, xcp_ : Exception):
        self.__DetachServices()

        # main task has caused/detected a fatal error already?
        if not self.__myTask.isFatalErrorFree:
            # nothing to do, no need to cause addintional one
            pass
        else:
            # unexpected exception, main task will consider it an LC failure, so notify the framework accordingly
            xlogif.LogExceptionEC(errMsg_, xcp_, 3011001)
    # --------------------------------------------------------------------------
    #END override of interface inherited from UserAppControllerIF
    # --------------------------------------------------------------------------


    # --------------------------------------------------------------------------
    # Impl
    # --------------------------------------------------------------------------
    @property
    def __isFiboReuested(self):
        return len(self.__lstSrv) > 0

    @property
    def __isFiboRequestDone(self):
        if len(self.__lstSrv) < 1:
            return False
        if self.__bAllProcDone:
            return True

        res = True
        for _ss in self.__lstSrv:
            if not _ss.isTerminated:
                res = False
                break
        return res

    @property
    def __myTask(self) -> IRCTask:
        return self.__myTsk

    def __StartServices(self):
        self.__bAllProcDone = False

        _fiboBaseInput = XFMainTaskMP.__FIBO_BASE_INPUT

        for ii in range(self.__srvProcCnt):
            # just to make sure we continue in an error-free state
            self.__myTask.ClearCurrentError()

            _fiboIn  = _fiboBaseInput + ii
            _srvName = 'ServiceProc{:02d}'.format(ii+1)
            _srv     = XProcess(UserAppUtil.Fibonacci, name_=_srvName)

            # failed to create process?
            if not _srv.isAttachedToFW:

                # framework missed to report any error (even though this is quite unlikely to happen)?
                if self.__myTask.isErrorFree:
                    # report an error just to make sure
                    xlogif.LogError(f'Failed to create next process: index={ii}')
                break

            # failed to start service process?
            if not _srv.Start(_fiboIn):
                break

            self.__lstSrv.append(_srv)
            UserAppUtil.SleepMS(10)

        res = len(self.__lstSrv) == self.__srvProcCnt
        if not res:
            xlogif.LogError(f'Failed to start service process {len(self.__lstSrv) + 1}.')
        else:
            xlogif.LogDebug(f'Started {len(self.__lstSrv)} serivce processes.')
            self.__ctrMpRun += 1
            _lstProcNames = [ f'{_ss.processPID}::{_ss.processName}' for _ss in self.__lstSrv ]
            self.__UpdateUserAppModel(lstProcNames_=_lstProcNames)
        return res

    def __DetachServices(self, bLogInfo_ =False):
        for _ss in self.__lstSrv:
            if not _ss.isAttachedToFW:
                continue

            if not _ss.isTerminated:
                #xlogif.LogDebug(f'Joining service process {_ss.processPID}...')
                _ss.Join()
                if bLogInfo_:
                    xlogif.LogInfo(f'Joined service process {_ss.processPID}.')

            _ss.DetachFromFW()
            continue
        #END for _ss...

        self.__bAllProcDone = False
        self.__lstSrv.clear()
        self.__UpdateUserAppModel(bReset_=True)

    def __CheckUpdateProcResults(self):
        if self.__bAllProcDone:
            return

        # make execution status of each service process is updated
        for _ss in self.__lstSrv:
            if _ss.isRunning:
                pass

        # update all process results
        self.__UpdateUserAppModel()

    def __CreateUserAppModel(self):
        items = dict()

        # version/system info
        items[EModelItemID.eNumCpuCores]   = fwutil.GetAvailableCpuCoresCount()
        items[EModelItemID.eHostPlatfrom]  = fwutil.GetPlatform()
        items[EModelItemID.eXcofdkVersion] = fwutil.GetXcofdkVersion()
        items[EModelItemID.ePythonVersion] = UserAppUtil.GetPythonVersion()

        # service process
        items[EModelItemID.eMPServiceProcess] = MPServiceProcess()

        # service processes result list
        items[EModelItemID.eMPServiceProcessResult] = self.__lstProcRes

        self.__mdl = _UserAppModelImpl(items_=items)

        self.__mdl.serviceProcess.mpStartMethod = XmpUtil.GetCurrentStartMethodName()
        if XmpUtil.IsCurrentStartMethodSystemDefault():
            self.__mdl.serviceProcess.mpStartMethod += ' (system default)'

    def __UpdateUserAppModel(self, bReset_ =False, lstProcNames_ =None, bDTimeOnly_ =False):
        self.__mdl.Lock()

        # number of errors
        self.__mdl.serviceProcess.mpNumErrors = self.__mpNumErr

        # update duration time only?
        if bDTimeOnly_:
            self.__mdl.serviceProcess.durationTime = UserAppUtil.DeltaTime2Str(self.__startTime, bIncludeHours_=True)
            self.__mdl.Unlock()
            return

        # current run No.
        self.__mdl.serviceProcess.mpRunCount = self.__ctrMpRun

        _lstProcRes = self.__lstProcRes

        # reset process results only?
        if bReset_:
            for pr in _lstProcRes:
                pr.UpdateResult(bReset_=True)

        # update process' pid/name only?
        elif lstProcNames_ is not None:
            for ii in range(len(_lstProcRes)):
                pr = _lstProcRes[ii]
                pr.UpdateResult(procName_=lstProcNames_[ii])

        # check update result of terminated processes
        else:
            _numFrozen = 0
            for ii in range(len(_lstProcRes)):
                pr = _lstProcRes[ii]
                if pr.isFrozen:
                    _numFrozen += 1
                    continue

                _ss          = self.__lstSrv[ii]
                _fiboResult  = None
                _bTerminated = _ss.isTerminated

                if _bTerminated:
                    _fiboResult = _ss.processSuppliedData
                    _bErr       = not (_ss.isDone and isinstance(_fiboResult, int) and (_ss.processExitCode==0))

                    if _bErr:
                        _fiboResult      = 0
                        self.__mpNumErr += 1
                        self.__mdl.serviceProcess.mpNumErrors = self.__mpNumErr
                    else:
                        pass
                #END if _bTerminated:

                pr.UpdateResult(fiboResult_=_fiboResult)

                if pr.isFrozen:
                    _numFrozen += 1

        self.__mdl.Unlock()
    # --------------------------------------------------------------------------
    #END Impl
    # --------------------------------------------------------------------------
#END class XFMainTaskMP
