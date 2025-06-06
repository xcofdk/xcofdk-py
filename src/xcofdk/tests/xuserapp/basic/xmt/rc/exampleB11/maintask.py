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
from xcofdk.fwcom import EExecutionCmdID
from xcofdk.fwcom import override
from xcofdk.fwapi import fwutil
from xcofdk.fwapi import xlogif
from xcofdk.fwapi import IRCTask
from xcofdk.fwapi import XFSyncTask
from xcofdk.fwapi import XFAsyncTask
from xcofdk.fwapi import GetCurTask

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
def _CreateMainTask(cmdLineOpts_ : CLOptions) -> IRCTask:
    _aliasName        = 'MainTask'
    _phasedXFCallback = XFMainTask(cmdLineOpts_)
    if cmdLineOpts_.isAsynMainTaskEnabled:
        res = XFAsyncTask(_phasedXFCallback, aliasName_=_aliasName, bMainTask_=True)
    else:
        res = XFSyncTask(_phasedXFCallback, aliasName_=_aliasName, bMainTask_=True)
    return res
#END _CreateMainTask()


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


class XFMainTask(UserAppControllerIF):
    """
    Main task of example exampleB11.


    Common shape of main tasks:
    --------------------------------
    For all basic GUI examples the main task is derived from interface class
    UserAppControllerIF to make the main task is the controller instance of
    the application (see section 'MVC design' in class description of class
    STGuiAppWelcome).

    The general shape of such a main task class is depicted below:
        >>>
        >>> # file: maintask.py
        >>>
        >>> from xcofdk.fwcom import override
        >>> from xcofdk.fwcom import EExecutionCmdID
        >>> from xcofdk.fwapi import IMessage
        >>> from xcofdk.fwapi import IRCTask
        >>> from xcofdk.fwapi import XFSyncTask
        >>> from xcofdk.fwapi import XFAsyncTask
        >>> from xcofdk.fwapi import GetCurTask
        >>>
        >>> from xuserapp.st.welcome.interfaces.controllerif import UserAppControllerIF
        >>>
        >>> class MyMainTask(UserAppControllerIF):
        >>>     def __init__(self, *args_, **kwargs_):
        >>>         UserAppControllerIF.__init__(self)
        >>>         # ...
        >>>
        >>>     def SetUpTask(self, *args_, **kwargs_) -> EExecutionCmdID:
        >>>         pass
        >>>
        >>>     def RunTask(self, *args_, **kwargs_) -> EExecutionCmdID:
        >>>         pass
        >>>
        >>>     def TearDownTask(self) -> EExecutionCmdID:
        >>>         pass
        >>>
        >>>     def ProcessExternalMessage(self, xmsg_ : IMessage) -> EExecutionCmdID:
        >>>         pass
        >>>     # ...

    Functional responsibility of main tasks:
    ------------------------------------------
    Given a basic example, the main task is generally responsible to:
        - create application's GUI, that is an instance of class
          STGuiAppWelcome,
        - create additional service instances (if any), that is instances of
          class RCTask and/or RCCommTask,
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
        - exampleB11/mtguiapp.py
        - xcofdk.tests.xuserapp.st.welcome.stguiappwelcome.STGuiAppWelcome
        - xcofdk.tests.xuserapp.st.welcome.interfaces.controllerif.UserAppControllerIF
        - xcofdk.fwapi.xmt.rctask.RCTask
        - xcofdk.fwapi.xmt.rctask.RCCommTask
        - xcofdk.fwapi.xmsg.IMessage
    """


    __slots__ = [ '__gui' , '__mdl' , '__startTime' , '__taskInfo' , '__cmdLine' , '__myTsk' ]

    def __init__(self, cmdLineOpts_ : CLOptions):
        self.__gui        = None
        self.__mdl        = None
        self.__myTsk      = None
        self.__cmdLine    = cmdLineOpts_
        self.__taskInfo   = None
        self.__startTime  = None

        UserAppControllerIF.__init__(self)


    # --------------------------------------------------------------------------
    # phasedXF callbacks
    # --------------------------------------------------------------------------
    def RunTask(self, posArg_ : str, kwArg_='default keyword argument') -> EExecutionCmdID:
        self.__myTsk = GetCurTask()

        _msg = 'Starting run-phase of {} called with arguments below:\n\tposArg_ : {}\n\tkwArg_  : {}'
        xlogif.LogInfo(_msg.format(self.__myTask.aliasName, posArg_, kwArg_))

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
                                    , detailViewID_=EDetailViewID.eMainTask)

        self.__startTime = UserAppUtil.GetCurrentTime()
        self.__gui.StartView()
        xlogif.LogInfo(f'Finished run-phase of the main task {self.__myTask.taskUID}.')

        # release referece to gui/Tk's root window
        self.__gui = None

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

        if not self.__myTask.isRunning:
            return False

        if (notifCounter_%5) == 0:
            self.__UpdateUserAppModel()
        return True

    @override
    def OnViewEncounteredException(self, errMsg_ : str, xcp_ : Exception):
        # main task has caused/detected a fatal error already?
        if not self.__myTask.isFatalErrorFree:
            # nothing to do, no need to cause addintional one
            pass
        else:
            # unexpected exception, main task will consider it an LC failure, so notify the framework accordingly
            xlogif.LogExceptionEC(errMsg_, xcp_, 2011001)
    # --------------------------------------------------------------------------
    #END override of interface inherited from UserAppControllerIF
    # --------------------------------------------------------------------------


    # --------------------------------------------------------------------------
    # Impl
    # --------------------------------------------------------------------------
    @property
    def __myTask(self) -> IRCTask:
        return self.__myTsk

    def __CreateUserAppModel(self, mainTaskStartTime_ : str):
        items = dict()

        # version/system info
        items[EModelItemID.eNumCpuCores]   = fwutil.GetAvailableCpuCoresCount()
        items[EModelItemID.eHostPlatfrom]  = fwutil.GetPlatform()
        items[EModelItemID.eXcofdkVersion] = fwutil.GetXcofdkVersion()
        items[EModelItemID.ePythonVersion] = UserAppUtil.GetPythonVersion()

        # main task info
        tinfo = TaskInfo( self.__myTask.aliasName
                        , self.__myTask.taskUID
                        , mainTaskStartTime_
                        , bAsync_=not self.__myTask.isSyncTask
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
#END class XFMainTask
