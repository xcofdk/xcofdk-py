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
from typing import Union

from xcofdk.fwcom     import EExecutionCmdID
from xcofdk.fwcom     import override
from xcofdk.fwapi     import fwutil
from xcofdk.fwapi     import xlogif
from xcofdk.fwapi.xmt import XMainTask
from xcofdk.fwapi.xmt import XTaskProfile

from xuserapp.util.cloptions                     import CLOptions
from xuserapp.util.userAppUtil                   import UserAppUtil
from xuserapp.st.welcome.common.commondefs       import EDetailViewID
from xuserapp.st.welcome.interfaces.modelif      import EModelItemID
from xuserapp.st.welcome.interfaces.modelif      import TaskInfo
from xuserapp.st.welcome.interfaces.modelif      import UserAppModelIF
from xuserapp.st.welcome.interfaces.controllerif import UserAppControllerIF
from xuserapp.st.welcome.stguiappwelcome         import STGuiAppWelcome


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
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


class MainTask(XMainTask, UserAppControllerIF):
    """
    Main task of example exampleSCB11.


    Common shape of main tasks:
    --------------------------------
    For all basic examples the main task is a derived class with multiple
    inheritance subclassing both classes:
        - UserAppControllerIF:
          to make the main task is the controller instance of the application
          (see section 'MVC design' in class description of class
          STGuiAppWelcome).

        - XMainTask:
          to make the main task is the singleton instance of class XMainTask
          provided by the framework of XCOFDK.

          Based on the basic example at hand, the derived class will have to
          override one or more 3-PhXF callback methods of class XTask.

    The general shape of such a main task class is depicted below:
        >>>
        >>> # file: my_maintask.py
        >>>
        >>> from xcofdk.fwcom     import override
        >>> from xcofdk.fwcom     import EExecutionCmdID
        >>> from xcofdk.fwapi     import IMessage
        >>> from xcofdk.fwapi.xmt import XMainTask
        >>> from xcofdk.fwapi.xmt import XTaskProfile
        >>>
        >>> from xuserapp.st.welcome.interfaces.controllerif import UserAppControllerIF
        >>>
        >>> class MyMainTask(XMainTask, UserAppControllerIF):
        >>>     def __init__(self, *args_, **kwargs_):
        >>>         UserAppControllerIF.__init__(self)
        >>>         XMainTask.__init__(self, taskProfile_=XTaskProfile())
        >>>         # ...
        >>>
        >>>     @override
        >>>     def SetUpXTask(self, *args_, **kwargs_) -> EExecutionCmdID:
        >>>         pass
        >>>
        >>>     @override
        >>>     def RunXTask(self, *args_, **kwargs_) -> EExecutionCmdID:
        >>>         pass
        >>>
        >>>     @override
        >>>     def TearDownXTask(self) -> EExecutionCmdID:
        >>>         pass
        >>>
        >>>     @override
        >>>     def ProcessExternalMessage(self, xmsg_ : IMessage) -> EExecutionCmdID:
        >>>         pass
        >>>     # ...


    Functional responsibility of main tasks:
    ------------------------------------------
    Given a basic example, the main task is generally responsible to:
        - create application's GUI, that is an instance of class
          STGuiAppWelcome,
        - create additional service instance (if any), that is instances of
          class XTask and/or XProcess,
        - start the GUI and its services (if any) upon start of the main task,
        - provide application-specific behavior,
        - process its external messages (if configured so),
        - perform cleanup stuff upon shutdown.

    The implementation code of the examples is perperly organized to reflect
    Note that the respective code of the abovementioned action items is more or
    less mapped to the corresponding callback method of the execution frame of
    the given main task.


    See:
    -----
        - exampleSCB11/mtguiapp.py
        - xcofdk.tests.xuserapp.st.welcome.stguiappwelcome.STGuiAppWelcome
        - xcofdk.tests.xuserapp.st.welcome.interfaces.controllerif.UserAppControllerIF
        - xcofdk.fwapi.xmt.XMainTask
        - xcofdk.fwapi.ITaskProfile
        - xcofdk.fwapi.IMessage
    """


    __slots__ = [ '__gui' , '__mdl' , '__startTime' , '__taskInfo' , '__cmdLine' ]

    def __init__(self, cmdLineOpts_ : CLOptions, taskProfile_ : XTaskProfile =None):
        self.__gui        = None
        self.__mdl        = None
        self.__cmdLine    = cmdLineOpts_
        self.__taskInfo   = None
        self.__startTime  = None
        self.__bAutoStart = True
        self.__bAutoClose = False

        if taskProfile_ is None:
            taskProfile_ = MainTask.__GetMyTaskProfile(cmdLineOpts_.isAsynMainTaskEnabled)

        UserAppControllerIF.__init__(self)
        XMainTask.__init__(self, taskProfile_=taskProfile_)


    # --------------------------------------------------------------------------
    # own (protected) interface
    # --------------------------------------------------------------------------
    @staticmethod
    def _CreateSingleton(taskProfile_ : Union[XTaskProfile, None], cmdLineOpts_ : CLOptions):
        res = MainTask(cmdLineOpts_, taskProfile_)
        if res.isDetachedFromFW:
            res = None
            xlogif.LogError('Failed to create main task.')
        return res
    # --------------------------------------------------------------------------
    #END own (protected) interface
    # --------------------------------------------------------------------------


    # --------------------------------------------------------------------------
    # override of interface inherited from XMainTask
    # --------------------------------------------------------------------------
    @override
    def RunXTask(self, posArg_ : str, kwArg_='default keyword argument') -> EExecutionCmdID:
        xlogif.LogInfo(f'Starting run-phase of the main task {self.taskUID} called with arguments below:\n\tposArg_ : {posArg_}\n\tkwArg_  : {kwArg_}')

        self.__CreateUserAppModel(UserAppUtil.GetTimestamp())

        # create gui, but caution:
        #  - creating and releasing/destroying Tk's root window should always happen
        #    in the same task/thread  !!
        #
        self.__gui = STGuiAppWelcome( title_='XMTGuiAppWelcome'
                                    , bAutoStart_=self.__cmdLine.isAutoStartEnabled
                                    , bAutoClose_=self.__cmdLine.isAutoCloseEnabled
                                    , controllerif_=self
                                    , modelif_=self.__mdl
                                    , detailViewID_=EDetailViewID.eMainTask
                                    , bRCExample_=False)

        self.__startTime = UserAppUtil.GetCurrentTime()
        self.__gui.StartView()
        xlogif.LogInfo(f'Finished run-phase of the main task {self.taskUID}.')

        # release referece to gui/Tk's root window
        self.__gui = None

        return EExecutionCmdID.STOP
    # --------------------------------------------------------------------------
    #END override of interface inherited from XMainTask
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

        if not self.isRunning:
            return False

        if (notifCounter_%5) == 0:
            self.__UpdateUserAppModel()
        return True

    @override
    def OnViewEncounteredException(self, errMsg_ : str, xcp_ : Exception):
        # main task has caused/detected a fatal error already?
        if not self.isFatalErrorFree:
            # nothing to do, no need to cause addintional one
            pass
        else:
            # unexpected exception, main task will consider it an LC failure, so notify the framework accordingly
            xlogif.LogExceptionEC(errMsg_, xcp_, 1011001)
    # --------------------------------------------------------------------------
    #END override of interface inherited from UserAppControllerIF
    # --------------------------------------------------------------------------


    # --------------------------------------------------------------------------
    # Impl
    # --------------------------------------------------------------------------
    @staticmethod
    def __GetMyTaskProfile(bAsync_ : bool) -> XTaskProfile:
        #[NOTE]
        #  - The property 'XTaskProfile.runPhaseFrequencyMS' doesn't matter
        #    as the run-phase of this main task is effectively a single-cycle one.
        #  - see: MainTask.RunXTask()
        #

        _aliasName = 'MainTask'
        if bAsync_:
            res = XTaskProfile.CreateAsyncTaskProfile(aliasName_=_aliasName, bPrivilegedTask_=True)
        else:
            res = XTaskProfile.CreateSyncTaskProfile(aliasName_=_aliasName, bPrivilegedTask_=True)

        if res is not None:
            res.runPhaseMaxProcessingTimeMS = 70
        return res

    def __CreateUserAppModel(self, mainTaskStartTime_ : str):
        items = dict()

        # version/system info
        items[EModelItemID.eNumCpuCores]   = fwutil.GetAvailableCpuCoresCount()
        items[EModelItemID.eHostPlatfrom]  = fwutil.GetPlatform()
        items[EModelItemID.eXcofdkVersion] = fwutil.GetXcofdkVersion()
        items[EModelItemID.ePythonVersion] = UserAppUtil.GetPythonVersion()

        # main task info
        tinfo = TaskInfo( self.taskProfile.aliasName
                        , self.taskUID
                        , mainTaskStartTime_
                        , bAsync_=not self.taskProfile.isSyncTask
                        , bMainTask_=True)
        tinfo.UpdateTaskInfo(UserAppUtil.DeltaTime2Str(UserAppUtil.GetCurrentTime(), bIncludeHours_=True))
        items[EModelItemID.eMainTaskInfo] = tinfo

        self.__mdl      = _UserAppModelImpl(items_=items)
        self.__taskInfo = tinfo

    def __UpdateUserAppModel(self):
        # main task info
        self.__mdl.Lock()
        self.__taskInfo.UpdateTaskInfo(UserAppUtil.DeltaTime2Str(self.__startTime, bIncludeHours_=True))
        self.__mdl.Unlock()
    # --------------------------------------------------------------------------
    #END Impl
    # --------------------------------------------------------------------------
#END class MainTask
