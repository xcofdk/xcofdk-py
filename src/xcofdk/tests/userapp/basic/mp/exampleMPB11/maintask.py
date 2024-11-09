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

from xcofdk.fwcom                   import fwutil
from xcofdk.fwcom                   import xlogif
from xcofdk.fwcom                   import ETernaryCallbackResultID
from xcofdk.fwcom                   import override
from xcofdk.fwapi.xtask             import MainXTask
from xcofdk.fwapi.xtask             import XTaskProfile
from xcofdk.fwapi.xprocess.xmputil  import XMPUtil
from xcofdk.fwapi.xprocess.xprocess import XProcess

from xcofdk.tests.userapp.st.welcome.common.commondefs       import EDetailViewID
from xcofdk.tests.userapp.st.welcome.interfaces.modelif      import EModelItemID
from xcofdk.tests.userapp.st.welcome.interfaces.modelif      import UserAppModelIF
from xcofdk.tests.userapp.st.welcome.interfaces.modelif      import MPServiceProcessResult
from xcofdk.tests.userapp.st.welcome.interfaces.modelif      import MPServiceProcess
from xcofdk.tests.userapp.st.welcome.interfaces.controllerif import UserAppControllerIF
from xcofdk.tests.userapp.st.welcome.stguiappwelcome         import STGuiAppWelcome

from xcofdk.tests.userapp.util.userAppUtil              import UserAppUtil
from xcofdk.tests.userapp.basic.mp.mputil.mpUserAppUtil import MPUserAppUtil


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


class MainTaskMP(MainXTask, UserAppControllerIF):

    __slots__ = [ '__gui'            , '__mdl'          , '__lstSrv'   , '__guiTitle'
                , '__bAutoStart'     , '__bAutoClose'   , '__ctrMpRun' , '__startTime'
                , '__srvProcCount'   , '__bMPPaused'    , '__mpNumErr' , '__lstProcResult'
                , '__ctrFiboTrigger' , '__bAllProcDone'
                ]

    __SRV_PROC_SPEC_TABLE = {
        35 : MPServiceProcessResult(fiboInput_=35, fiboCpuTimeSEC_=2.9)
      , 36 : MPServiceProcessResult(fiboInput_=36, fiboCpuTimeSEC_=4.7)
      , 37 : MPServiceProcessResult(fiboInput_=37, fiboCpuTimeSEC_=7.5)
      , 38 : MPServiceProcessResult(fiboInput_=38, fiboCpuTimeSEC_=12.0)
    }

    __FIBO_BASE_INPUT           = 35
    __MAX_NUM_SERVICE_PROCESSES = 3

    def __init__ ( self, taskProfile_ : XTaskProfile =None, guiTitle_ : str =None):
        self.__gui            = None
        self.__mdl            = None
        self.__lstSrv         = []
        self.__ctrMpRun       = 0
        self.__mpNumErr       = 0
        self.__startTime      = None
        self.__bMPPaused      = False
        self.__bAutoStart     = True
        self.__bAutoClose     = False
        self.__bAllProcDone   = False
        self.__srvProcCount   = MainTaskMP.__MAX_NUM_SERVICE_PROCESSES
        self.__lstProcResult  = []
        self.__ctrFiboTrigger = 0

        if not (0 < MainTaskMP.__MAX_NUM_SERVICE_PROCESSES < 3):
            MainTaskMP.__MAX_NUM_SERVICE_PROCESSES = 3
        if not (34 < MainTaskMP.__FIBO_BASE_INPUT < 39):
            MainTaskMP.__MAX_NUM_SERVICE_PROCESSES = 35

        _fiboBaseIn = MainTaskMP.__FIBO_BASE_INPUT
        for ii in range(self.__srvProcCount):
            self.__lstProcResult.append(MainTaskMP.__SRV_PROC_SPEC_TABLE[_fiboBaseIn+ii])

        if isinstance(guiTitle_, str):
            self.__guiTitle = guiTitle_
        else:
            self.__guiTitle = 'MPGuiApp'

        self.__ScanCmdLineArgs()

        if taskProfile_ is None:
            taskProfile_ = MainTaskMP.__GetMyTaskProfile()

        UserAppControllerIF.__init__(self)
        MainXTask.__init__(self, taskProfile_=taskProfile_)


    # --------------------------------------------------------------------------
    # own (protected) interface
    # --------------------------------------------------------------------------
    @staticmethod
    def _CreateSingleton(taskProfile_ : Union[XTaskProfile, None]):
        res = MainTaskMP(taskProfile_=taskProfile_)
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
        self.__CreateUserAppModel()

        # create gui, but caution:
        #  - creating and releasing/destroying Tk's root window should always happen in the same task/thread  !!
        #
        self.__gui = STGuiAppWelcome( title_=self.__guiTitle
                                    , bAutoStart_=self.__bAutoStart
                                    , bAutoClose_=self.__bAutoClose
                                    , controllerif_=self
                                    , modelif_=self.__mdl
                                    , detailViewID_=EDetailViewID.eFibonacciResultMP
                                    , numServices_=self.__srvProcCount)

        xlogif.LogInfo(f'Finished setup.')
        return ETernaryCallbackResultID.CONTINUE

    @override
    def RunXTask(self) -> ETernaryCallbackResultID:
        xlogif.LogInfo(f'Starting run-phase of the main task {self.xtaskUniqueID}...')

        if not self.__gui.StartView():
            res = ETernaryCallbackResultID.ABORT
        else:
            res = ETernaryCallbackResultID.STOP

        xlogif.LogInfo(f'GUI view returned, activity state: {self.__gui.isActive}')

        # release referece to gui/Tk's root window
        self.__gui = None

        xlogif.LogInfo(f'Finished run-phase of the main task {self.xtaskUniqueID}.')
        return res

    @override
    def TearDownXTask(self) -> ETernaryCallbackResultID:
        self.__DetachServices(bLogInfo_=True)
        return ETernaryCallbackResultID.STOP
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
            # stop own task, i.e. the main task
            self.Stop()

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
                _DIVISOR = self.__srvProcCount * 20

                # time to trigger new fibo request (ca. 2s to 6s)?
                if (self.__ctrFiboTrigger%_DIVISOR) == 0:
                    self.__ctrFiboTrigger = 0

                    # create new service processes next time we get notified by the view
                    self.__DetachServices()

        # update services' state/result (every 100 [ms])
        else:
            self.__CheckUpdateProcResults()

        res = res and self.isRunning
        return res

    @override
    def OnViewEncounteredException(self, errMsg_ : str, xcp_ : Exception):
        self.__DetachServices()

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
        res = XTaskProfile.CreateSynchronousTaskProfile(aliasName_='MainTaskMP', bPrivilegedTask_=True)

        if res is not None:
            res.isSetupPhaseEnabled         = True
            res.isTeardownPhaseEnabled      = True
            res.runPhaseMaxProcessingTimeMS = 80
        return res

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
        for ss in self.__lstSrv:
            if not ss.isTerminated:
                res = False
                break
        return res

    def __ScanCmdLineArgs(self):
        ii, NUM_ARGS = 1, len(sys.argv)
        while ii < NUM_ARGS:
            aa = sys.argv[ii]
            ii += 1

            if aa.startswith('#'):
                break

            if aa == '--disable-auto-start':
                self.__bAutoStart = False
            elif aa == '--enable-auto-close':
                self.__bAutoClose = True
            else:
                pass
        # END while...

        if not self.__bAutoStart:
            self.__bAutoClose = False

    def __StartServices(self):
        self.__bAllProcDone = False

        _fiboBaseInput = MainTaskMP.__FIBO_BASE_INPUT

        for ii in range(self.__srvProcCount):
            # just to make sure we continue in an error-free state
            self.ClearCurrentError()

            _fiboIn  = _fiboBaseInput + ii
            _srvName = 'ServiceProc{:02d}'.format(ii+1)
            _srv     = XProcess(MPUserAppUtil.Fibonacci, name_=_srvName, args_=(_fiboIn,))

            # failed to create process?
            if not _srv.isAttachedToFW:

                # framework missed to report any error (even though this is quite unlikely to happen)?
                if self.isErrorFree:
                    # report an error just to make sure
                    xlogif.LogError(f'Failed to create next process: index={ii}')
                break

            # failed to start service process?
            if not _srv.Start():
                break

            self.__lstSrv.append(_srv)
            UserAppUtil.SleepMS(10)

        res = len(self.__lstSrv) == self.__srvProcCount
        if not res:
            xlogif.LogError(f'Failed to start service process {len(self.__lstSrv) + 1}.')
        else:
            xlogif.LogDebug(f'Started {len(self.__lstSrv)} serivce processes.')
            self.__ctrMpRun += 1
            _lstProcNames = [ f'{ss.xprocessPID}::{ss.xprocessName}' for ss in self.__lstSrv ]
            self.__UpdateUserAppModel(lstProcNames_=_lstProcNames)
        return res

    def __DetachServices(self, bLogInfo_ =False):
        for ss in self.__lstSrv:
            if not ss.isAttachedToFW:
                continue

            if not ss.isTerminated:
                #xlogif.LogDebug(f'Joining service process {ss.xprocessPID}...')
                ss.Join()
                if bLogInfo_:
                    xlogif.LogInfo(f'Joined service process {ss.xprocessPID}.')

            ss.DetachFromFW()
            continue
        #END for ss...

        self.__bAllProcDone = False
        self.__lstSrv.clear()
        self.__UpdateUserAppModel(bReset_=True)

    def __CheckUpdateProcResults(self):
        if self.__bAllProcDone:
            return

        # make execution status of each service process is updated
        for ss in self.__lstSrv:
            if ss.isRunning:
                pass

        # update all process results
        self.__UpdateUserAppModel()

    def __CreateUserAppModel(self):
        items = dict()

        # version/system info
        items[EModelItemID.eNumCpuCores]   = fwutil.GetAvailableCpuCoresCount()
        items[EModelItemID.eHostPlatfrom]  = fwutil.GetPlatform()
        items[EModelItemID.eXcofdkVersion] = fwutil.GetXcofdkVersion()
        items[EModelItemID.ePythonVersion] = fwutil.GetPythonVersion()

        # service process
        items[EModelItemID.eMPServiceProcess] = MPServiceProcess()

        # service processes result list
        items[EModelItemID.eMPServiceProcessResult] = self.__lstProcResult

        self.__mdl = _UserAppModelImpl(items_=items)

        self.__mdl.serviceProcess.mpStartMethod = XMPUtil.GetCurrentStartMethodName()

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

        _lstProcRes = self.__lstProcResult

        # reset process results only?
        if bReset_:
            self.__mdl.serviceProcess.processElapsedTimeTotalSEC = None

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

                ss           = self.__lstSrv[ii]
                _fiboResult  = None
                _bTerminated = ss.isTerminated

                if _bTerminated:
                    _procRes    = ss.xprocessResult
                    _fiboResult = None if _procRes is None else _procRes.resultData
                    _bErr       = not (ss.isDone and isinstance(_fiboResult, int) and (ss.xprocessExitCode==0))

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

            if _numFrozen == len(_lstProcRes):
                _lstProcRes = sorted(_lstProcRes, key=lambda pp: pp.fibonacciInput, reverse=True)
                self.__mdl.serviceProcess.processElapsedTimeTotalSEC = _lstProcRes[0].processElapsedTimeSEC

        self.__mdl.Unlock()
    # --------------------------------------------------------------------------
    #END Impl
    # --------------------------------------------------------------------------
#END class MainTaskMP
