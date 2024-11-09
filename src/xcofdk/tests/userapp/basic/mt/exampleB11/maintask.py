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

from xcofdk.fwcom        import fwutil
from xcofdk.fwcom        import xlogif
from xcofdk.fwcom        import ETernaryCallbackResultID
from xcofdk.fwcom        import override
from xcofdk.fwapi.xtask  import MainXTask
from xcofdk.fwapi.xtask  import XTaskProfile

from xcofdk.tests.userapp.util.userAppUtil import UserAppUtil

from xcofdk.tests.userapp.st.welcome.common.commondefs       import EDetailViewID
from xcofdk.tests.userapp.st.welcome.interfaces.modelif      import EModelItemID
from xcofdk.tests.userapp.st.welcome.interfaces.modelif      import TaskInfo
from xcofdk.tests.userapp.st.welcome.interfaces.modelif      import UserAppModelIF
from xcofdk.tests.userapp.st.welcome.interfaces.controllerif import UserAppControllerIF
from xcofdk.tests.userapp.st.welcome.stguiappwelcome         import STGuiAppWelcome


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
    """
    Main task of example exampleB11.


    Common shape of main tasks:
    --------------------------------
    For all basic examples the main task is a derived class with multiple
    inheritance subclassing both classes:
        - UserAppControllerIF:
          to make the main task is the controller instance of the application
          (see section 'MVC design' in class description of 'STGuiAppWelcome').

        - MainXTask:
          to make the main task is the singleton instance of class 'MainXTask'
          provided by the framework of XCOFDK.

          Based on the basic example at hand, the derived class will have to
          override one or more callback methods of class 'XTask' (see section
          'Execution frame 3-PhXF' in class description of 'XTask').

    The general shape of such a main task class is depicted below:
        >>>
        >>> # file: my_maintask.py
        >>>
        >>> from xcofdk.fwcom       import override
        >>> from xcofdk.fwcom       import ETernaryCallbackResultID
        >>> from xcofdk.fwapi.xtask import MainXTask
        >>> from xcofdk.fwapi.xtask import XTaskProfile
        >>> from xcofdk.fwapi.xmsg  import XMessage
        >>>
        >>> from xcofdk.tests.userapp.st.welcome.interfaces.controllerif import UserAppControllerIF
        >>>
        >>> class MyMainTask(MainXTask, UserAppControllerIF):
        >>>     def __init__(self, *args_, **kwargs_):
        >>>         UserAppControllerIF.__init__(self)
        >>>         MainXTask.__init__(self, taskProfile_=XTaskProfile())
        >>>         # ...
        >>>
        >>>     @override
        >>>     def SetUpXTask(self, *args_, **kwargs_) -> ETernaryCallbackResultID:
        >>>         pass
        >>>
        >>>     @override
        >>>     def RunXTask(self, *args_, **kwargs_) -> ETernaryCallbackResultID:
        >>>         pass
        >>>
        >>>     @override
        >>>     def TearDownXTask(self) -> ETernaryCallbackResultID:
        >>>         pass
        >>>
        >>>     @override
        >>>     def ProcessExternalMessage(self, xmsg_ : XMessage) -> ETernaryCallbackResultID:
        >>>         pass
        >>>     # ...

    The abovementioned multiple inheriance of main tasks in depicted as a simple
    class diagram in comment block placed right at the bottom of this docstring.

    Functional responsibility of main tasks:
    ------------------------------------------
    Given a basic example, the main task is generally responsible to:
        - create application's GUI, that is an instance of class
          'STGuiAppWelcome',
        - create additional service instance (if any), that is instances of
          class 'XTask' and/or 'XProcess',
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
        - exampleB11.mtguiapp.py
        - xcofdk.tests.userapp.st.welcome.stguiappwelcome.STGuiAppWelcome
        - xcofdk.tests.userapp.st.welcome.interfaces.controllerif.UserAppControllerIF
        - xcofdk.fwapi.xtask.MainXTask
        - xcofdk.fwapi.xtask.XTaskProfile
        - xcofdk.fwapi.xmsg.XMessage
    """
    # -------------------------------------------------------------------------
    # Class diagram of the main task common for all basic examples of XCOFDK:
    #
    #            ┌─────────────┐   ┌───────────────────────┐
    #            │  MainXTask  │   │  UserAppControllerIF  │
    #            └───────────┬─┘   └─┬─────────────────────┘
    #                        │       │
    #                        │       │
    #     ┌─────────┐    ┌───▽───────▽──┐    ┌──────────────────┐
    #     │  XTask  ├───◇│   MainTask   │◆───┤  STGuiAppWelcome │
    #     └─────────┘    └──────────────┘    └──────────────────┘
    #
    # Note that the left-hand side aggreation has a multipliciy N >= 0, that is
    # the main task may or may not have additional task instances as members,
    # while the multiplicity of the right-hand side composition is 1, that is
    # the main task always has a main GUI window.
    #
    # -------------------------------------------------------------------------


    __slots__ = [ '__gui' , '__mdl' , '__startTime' , '__taskInfo' , '__bAutoStart' , '__bAutoClose' ]

    def __init__(self, taskProfile_ : XTaskProfile =None):
        self.__gui        = None
        self.__mdl        = None
        self.__taskInfo   = None
        self.__startTime  = None
        self.__bAutoStart = True
        self.__bAutoClose = False

        _bAsync = self.__ScanCmdLineArgs()

        if taskProfile_ is None:
            taskProfile_ = MainTask.__GetMyTaskProfile(_bAsync)

        UserAppControllerIF.__init__(self)
        MainXTask.__init__(self, taskProfile_=taskProfile_)


    # --------------------------------------------------------------------------
    # own (protected) interface
    # --------------------------------------------------------------------------
    @staticmethod
    def _CreateSingleton(taskProfile_ : Union[XTaskProfile, None]):
        res = MainTask(taskProfile_)
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
    def RunXTask(self) -> ETernaryCallbackResultID:
        xlogif.LogInfo(f'Starting run-phase of the main task {self.xtaskUniqueID}...')

        self.__CreateUserAppModel(UserAppUtil.GetTimestamp())

        # create gui, but caution:
        #  - creating and releasing/destroying Tk's root window should always happen
        #    in the same task/thread  !!
        #
        self.__gui = STGuiAppWelcome( title_='MTGuiAppWelcome', bAutoStart_=self.__bAutoStart, bAutoClose_=self.__bAutoClose
                                    , controllerif_=self, modelif_=self.__mdl, detailViewID_=EDetailViewID.eMainTask)

        self.__startTime = UserAppUtil.GetCurrentTime()
        self.__gui.StartView()
        xlogif.LogInfo(f'Finished run-phase of the main task {self.xtaskUniqueID}.')

        # release referece to gui/Tk's root window
        self.__gui = None

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
            # unexpected exception, main task will consider it a LC failure, so notify the framework accordingly
            xlogif.LogException(errMsg_, xcp_)
    # --------------------------------------------------------------------------
    #END override of interface inherited from UserAppControllerIF
    # --------------------------------------------------------------------------


    # --------------------------------------------------------------------------
    # Impl
    # --------------------------------------------------------------------------
    @staticmethod
    def __GetMyTaskProfile(bAsync_ : bool) -> XTaskProfile:
        #NOTE:
        #  - The property 'XTaskProfile.runPhaseFrequencyMS' doesn't matter
        #    as the run-phase of this main task is a single-cycle one.
        #  - see: MainTask.RunXTask()
        #

        _aliasName = 'MainTask'
        if bAsync_:
            res = XTaskProfile.CreateAsynchronousTaskProfile(aliasName_=_aliasName, bPrivilegedTask_=True)
        else:
            res = XTaskProfile.CreateSynchronousTaskProfile(aliasName_=_aliasName, bPrivilegedTask_=True)

        if res is not None:
            res.runPhaseMaxProcessingTimeMS = 70
        return res

    def __ScanCmdLineArgs(self):
        _bAsync = False
        if len(sys.argv) > 1:
            for aa in sys.argv[1:]:
                if aa.startswith('#'):
                    break
                if aa == '--enable-async-execution':
                    _bAsync = True
                elif aa == '--disable-auto-start':
                    self.__bAutoStart = False
                elif aa == '--enable-auto-close':
                    self.__bAutoClose = True

        if not self.__bAutoStart:
            self.__bAutoClose =False
        return _bAsync

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
