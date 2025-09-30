# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xtask.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from enum   import IntEnum
from typing import Any
from typing import Union

from xcofdk.fwcom     import CompoundTUID
from xcofdk.fwcom     import EExecutionCmdID
from xcofdk.fwcom     import override
from xcofdk.fwcom     import EXmsgPredefinedID
from xcofdk.fwapi     import IMessage
from xcofdk.fwapi     import ITaskError
from xcofdk.fwapi     import IPayload
from xcofdk.fwapi     import ITask
from xcofdk.fwapi.xmt import ITaskProfile
from xcofdk.fwapi.xmt import IXTask
from xcofdk.fwapi.xmt import XTaskProfile

from _fw.fwssys.fwmt.api                 import xlogifbase
from _fw.fwssys.fwmt.utask.usertaskagent import _UserTaskAgent


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class XTask(IXTask):
    """
    Abstract class representing application tasks to be executed by the
    framework.

    In general, application tasks supported by the framework are desgined to
    achieve light-weight parallelism (or concurrency) with or without the
    capability for task communication via messaging.

    Concrete task instances can be created by sub-classing this class. Such a
    derived class will only have to override specific 3-PhXF callback methods
    (described below) according to its configuration specified at construction
    time.

    THe major part of this class is described in parent classes:
        >>> ITask
        >>> IXTask

    For the remaining API specific to this abstract class refer to:
        >>> XTask.__init__()
        >>> XTask.SetUpXTask()
        >>> XTask.RunXTask()
        >>> XTask.TearDownXTask()
        >>> XTask.ProcessExternalMessage()


    Deprecated API:
    ----------------
    Starting with XCOFDK-py v3.0 below API functions/properties (formerly part of
    the API of this class) are deprecated and not available anymore:
        >>> @property
        >>> def xtaskUniqueID(self) -> int:
        >>>     return self.taskUID
        >>>
        >>> @property
        >>> def xtaskName(self) -> str:
        >>>     return self.taskName
        >>>
        >>> @property
        >>> def xtaskAliasName(self) -> str:
        >>>     return self.aliasName
        >>>
        >>> @property
        >>> def isFirstRunPhaseIteratoion(self) -> bool:
        >>>     return self.isFirstRunPhaseIteration
        >>>
        >>> @property
        >>> def currentRunPhaseIteratoionNo(self) -> int:
        >>>     return self.currentRunPhaseIterationNo
    """

    # --------------------------------------------------------------------------
    # 1) c-tor / built-in
    # --------------------------------------------------------------------------
    def __init__(self, taskProfile_ : ITaskProfile =None):
        """
        Constructor (or initializer) of an instance of this class.

        Parameters:
        -------------
            - taskProfile_ :
              task profile to be used to configure this instance.
              If None is passed to, a new instance of class XTaskProfile (with
              default configuration) will be created and considered as passed
              in profile at construction time.

        Note:
        ------
            - Once successfully created:
                  - a task is considered attached to the framework,
                    unless it gets detached from the framework upon termination,
                    or if it intentially requests the framework to do so,
                  - both its alias name and compound unique ID are available.
            - As long as a task is attached to the framework, its confiuration
              profile will refer to a read-only (or frozen) copy created at
              construction time using the passed in profile instance.
            - Once detached from the framework, the task profile of a task
              instance will refer to the profile instance passed in at
              construction time (which may or may not be frozen).

        See:
        -----
            >>> ITask.isAttachedToFW
            >>> ITask.aliasName
            >>> ITask.taskCompoundUID
            >>> ITask.DetachFromFW()
            >>> XTask.SetUpXTask()
            >>> XTask.RunXTask()
            >>> XTask.TearDownXTask()
            >>> XTask.ProcessExternalMessage()
            >>> XTaskProfile
            >>> ITaskProfile
            >>> ITaskProfile.isFrozen
            >>> ITaskProfile.isSetupPhaseEnabled
            >>> ITaskProfile.isRunPhaseEnabled
            >>> ITaskProfile.isTeardownPhaseEnabled
            >>> ITaskProfile.isExternalQueueEnabled
            >>> ITaskProfile.isCyclicRunPhase
            >>> ITaskProfile.runPhaseFrequencyMS
        """
        IXTask.__init__(self)

        if taskProfile_ is None:
            taskProfile_ = XTaskProfile()
        self.__a = _UserTaskAgent(self, taskProfile_)
    # --------------------------------------------------------------------------
    #END 1) c-tor / built-in
    # --------------------------------------------------------------------------


    # --------------------------------------------------------------------------
    # 2) phasedXF callbacks
    # --------------------------------------------------------------------------
    def SetUpXTask(self, *args_, **kwargs_) -> EExecutionCmdID:
        """
        3-PhXF callback of the setup phase of this instance if configured so.

        It will be called by the framework when this instance is started via
        its start API passing positional and/or keyword arguments (if any).

        Parameters:
        -------------
            - args_ :
              positional arguments (if any).
            - kwargs_ :
              keyword arguments (if any).

        Returns:
        ----------
            - EExecutionCmdID.CONTINUE :
              to indicate that the execution of the run phase of this instance
              can take place.

            - EExecutionCmdID.STOP :
              to instruct the framework to initiate the stop sequence (for
              whatever reason).

            - EExecutionCmdID.CANCEL :
              to instruct the framework to initiate the cancel sequence (for
              whatever reason).

            - EExecutionCmdID.ABORT :
              to indicate an unexpected, severe error. The framework will then
              immediately submit a fatal error accordingly.

        Note:
        ------
            - Refer to the constructor of this class for more detail regarding
              configuration of task instances.

        See:
        -----
            >>> XTask.__init__()
            >>> XTask.RunXTask()
            >>> ITask.Start()
            >>> ITask.Stop()
            >>> ITask.Cancel()
            >>> EExecutionCmdID
        """
        xlogifbase._XLogWarning('Default impl of the setup phase, nothig to do, continue with run phase.')
        return EExecutionCmdID.CONTINUE


    def RunXTask(self, *args_, **kwargs_) -> EExecutionCmdID:
        """
        3-PhXF callback of the (cyclic) run phase of this instance if configured so.

        This callback method will be called by the framework:
            - to start the execution of this instance if configured to have
              no setup phase, or
            - to enter the run phase after the setup phase is finished
              indicating continue execution,
            - after each previously executed run phase interation
              with continue execution was indicated.
              Note that this happens only if this task is configured to have
              a cyclic run phase, i.e. with a run phase frequency larger than 0.

        Parameters:
        -------------
            - args_ :
              positional arguments (if any) passed to the start API if this
              instance is configured to have no setup phase,
            - kwargs_ :
              keyword arguments (if any) passed to the start API if this
              instance is configured to have no setup phase.

        Returns:
        ----------
            - EExecutionCmdID.CONTINUE :
              to indicate that the execution of this iteration of the run phase
              was successful.
              Unless configured as single-cycle run phase, cyclic execution of
              the run phase will keep going according to the specified run
              phase frequency.
              Otherwise, teardown phase will take place (if configured).
              Whenever no teardown phase was configured, the stop sequence of the
              task will be initiated by the framework.

            - EExecutionCmdID.STOP :
              to indicate end of the run phase.
              Unless teardown phase is configured, the stop sequence of the task
              will be initiated by the framework. Otherwise, teardown phase will
              take place.

            - EExecutionCmdID.CANCEL :
              to indicate a request to break the execution of this task.
              The framwork will then immediately initiate the cancel sequence.

            - EExecutionCmdID.ABORT :
              to indicate an unexpected, severe error. The framework will then
              immediately submit a fatal error accordingly.

        Note:
        ------
            - Refer to the constructor of this class for more detail regarding
              configuration of task instances.
            - Also, the run phase is always configured by default for all tasks,
              unless a task is configured to have a blocking external queue in
              which case the task rather represents a message-driven task.

        See:
        -----
            >>> XTask.__init__()
            >>> XTask.SetUpXTask()
            >>> XTask.TearDownXTask()
            >>> ITask.Start()
            >>> ITask.Stop()
            >>> ITask.Cancel()
            >>> XTask.ProcessExternalMessage()
            >>> ITask.isFirstRunPhaseIteration
            >>> ITask.currentRunPhaseIterationNo
            >>> ITaskProfile.isCyclicRunPhase
            >>> EExecutionCmdID
        """
        xlogifbase._XLogWarning('Default impl of the run phase, nothig to do, continue with teardown phase (if configured).')
        return EExecutionCmdID.STOP


    def TearDownXTask(self) -> EExecutionCmdID:
        """
        3-PhXF callback of the teardown phase of this instance if configured so.

        This callback method will be called by the framework right after the run
        phase is finished, unless it was canceled or aborted.

        Returns:
        ----------
            - EExecutionCmdID.CONTINUE :
            - EExecutionCmdID.STOP :
              to instruct the framework to initiate the stop sequence.

            - EExecutionCmdID.CANCEL :
              to instruct the framework to initiate the cancel sequence.

            - EExecutionCmdID.ABORT :
              to indicate an unexpected, severe error. The framework will then
              immediately submit a fatal error accordingly.

        Note:
        ------
            - Teardown phase is designed to enable tasks to perfrom individual
              cleanup stuff (if any) upon their normal termination.
            - Bear in mind that a task in teardown phase is within the
              task-limited RTE mode.

        Note:
        ------
            - Refer to the constructor of this class for more detail regarding
              configuration of task instances.

        See:
        -----
            >>> XTask.__init__()
            >>> XTask.RunXTask()
            >>> ITask.Start()
            >>> ITask.Stop()
            >>> ITask.Cancel()
            >>> EExecutionCmdID
        """
        xlogifbase._XLogWarning('Default impl of the tear down phase, nothig to do.')
        return EExecutionCmdID.STOP


    def ProcessExternalMessage(self, xmsg_ : IMessage) -> EExecutionCmdID:
        """"
        Callback method called by the framework whenever there is a queued
        external message to be processed.

        Parameters:
        -------------
            - xmsg_ :
              external message to be processed

        Returns:
        ----------
            - EExecutionCmdID.CONTINUE :
              to indicate message processing was successful, framework can keep
              going with message delivery to this task.

              Note that the term 'successuful' does not necessairly mean a
              positive result with regard to whatever application-specific
              and/or logical attribution.

            - EExecutionCmdID.STOP :
              to instruct the framework to stop both message delivery to and
              execution of this task. The stop sequence of this task will then
              take place.

            - EExecutionCmdID.CANCEL :
              to instruct the framework to cancel both message delivery to and
              execution of this task. The cancel sequence of this task will then
              take place.

            - EExecutionCmdID.ABORT :
              to indicate an unexpected, severe error. The framework will then
              immediately submit a fatal error accordingly.

        Note:
        ------
            - Unless configured as run phase, processing of queued external
              messages takes place before next run phase cycle is executed
              (which is according to the default policy).
            - Otherwise, this task represents rather a message-driven task.
              This callback will then be called as soon as and as long as (newly)
               queued messages are available.
            - Also, a task may trigger the message processing itself at any time
              provided it is still in state running, and it is not processing
              messages already.

        See:
        -----
            >>> XTask.__init__()
            >>> XTask.RunXTask()
            >>> ITask.isFirstRunPhaseIteration
            >>> ITask.currentRunPhaseIterationNo
            >>> IXTask.SendMessage()
            >>> IXTask.BroadcastMessage()
            >>> IXTask.TriggerExternalQueueProcessing()
            >>> ITaskProfile.isRunPhaseEnabled
            >>> ITaskProfile.isExternalQueueEnabled
            >>> ITaskProfile.isExternalQueueBlocking
        """
        xlogifbase._XLogWarning('Default impl of the callback for processing of external messages, nothig to do.')
        return EExecutionCmdID.STOP
    # --------------------------------------------------------------------------
    #END 2) phasedXF callbacks
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # 3) start/stop
    # ------------------------------------------------------------------------------
    @override
    def Start(self, *args_, **kwargs_) -> bool:
        """
        See:
        -----
            >>> ITask.Start()
        """
        return self.__a.Start(*args_, **kwargs_)


    @override
    def Stop(self) -> bool:
        """
        See:
        -----
            >>> ITask.Stop()
        """
        return self.__a.Stop()


    @override
    def Cancel(self) -> bool:
        """
        See:
        -----
            >>> ITask.Cancel()
        """
        return self.__a.Cancel()


    @override
    def Join(self, maxWaitTime_: Union[int, float, None] =None) -> bool:
        """
        See:
        -----
             >>> ITask.Join()
        """
        return self.__a.Join(maxWaitTime_)


    @override
    def DetachFromFW(self):
        """
        See:
        -----
            >>> ITask.DetachFromFW()
        """
        self.__a.DetachFromFW()
    # ------------------------------------------------------------------------------
    #END 3) start/stop
    # ------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # 4) task state
    # ------------------------------------------------------------------------------
    @ITask.isAttachedToFW.getter
    def isAttachedToFW(self) -> bool:
        """
        See:
        -----
            >>> ITask.isAttachedToFW
        """
        return self.__a.isAttachedToFW


    @ITask.isDetachedFromFW.getter
    def isDetachedFromFW(self) -> bool:
        """
        See:
        -----
            >>> ITask.isDetachedFromFW
        """
        return self.__a.isDetachedFromFW


    @ITask.isStarted.getter
    def isStarted(self) -> bool:
        """
        See:
        -----
            >>> ITask.isStarted
        """
        return self.__a.isStarted


    @ITask.isPendingRun.getter
    def isPendingRun(self) -> bool:
        """
        See:
        -----
            >>> ITask.isPendingRun
        """
        return self.__a.isPendingRun


    @ITask.isRunning.getter
    def isRunning(self) -> bool:
        """
        See:
        -----
            >>> ITask.isRunning
        """
        return self.__a.isRunning


    @ITask.isDone.getter
    def isDone(self) -> bool:
        """
        See:
        -----
            >>> ITask.isDone
        """
        return self.__a.isDone


    @ITask.isCanceled.getter
    def isCanceled(self) -> bool:
        """
        See:
        -----
            >>> ITask.isDone
        """
        return self.__a.isCanceled


    @ITask.isFailed.getter
    def isFailed(self) -> bool:
        """
        See:
        -----
            >>> ITask.isFailed
        """
        return self.__a.isFailed


    @ITask.isTerminated.getter
    def isTerminated(self) -> bool:
        """
        See:
        -----
            >>> ITask.isTerminated
        """
        return self.__a.isTerminated


    @ITask.isTerminating.getter
    def isTerminating(self) -> bool:
        """
        See:
        -----
            >>> ITask.isTerminating
        """
        return self.__a.isTerminating


    @ITask.isStopping.getter
    def isStopping(self) -> bool:
        """
        See:
        -----
            >>> ITask.isStopping
        """
        return self.__a.isStopping


    @ITask.isCanceling.getter
    def isCanceling(self) -> bool:
        """
        See:
        -----
            >>> ITask.isCanceling
        """
        return self.__a.isCanceling
    # ------------------------------------------------------------------------------
    #END 4) task state
    # ------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # 5) task (unique) properties
    # ------------------------------------------------------------------------------
    @ITask.isSyncTask.getter
    def isSyncTask(self) -> bool:
        """
        See:
        -----
            >>> ITask.isSyncTask
        """
        return self.__a.isSyncTask


    @ITask.isFirstRunPhaseIteration.getter
    def isFirstRunPhaseIteration(self) -> bool:
        """
        See:
            >>> ITask.isFirstRunPhaseIteration
        """
        return self.__a.isFirstRunPhaseIteration


    @ITask.taskUID.getter
    def taskUID(self) -> int:
        """
        See:
            >>> ITask.taskUID
        """
        return self.__a.taskUID


    @ITask.taskName.getter
    def taskName(self) -> str:
        """
        See:
            >>> ITask.taskName
        """
        return self.__a.taskName


    @ITask.aliasName.getter
    def aliasName(self) -> str:
        """
        See:
            >>> ITask.aliasName
        """
        return self.__a.aliasName


    @ITask.taskCompoundUID.getter
    def taskCompoundUID(self) -> CompoundTUID:
        """
        See:
            >>> ITask.taskCompoundUID
        """
        return self.__a.taskCompoundUID


    @ITask.currentRunPhaseIterationNo.getter
    def currentRunPhaseIterationNo(self) -> int:
        """
        See:
            >>> ITask.currentRunPhaseIterationNo
        """
        return self.__a.currentRunPhaseIterationNo
    # ------------------------------------------------------------------------------
    # 5) task (unique) properties
    # ------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # 6) task-owned data
    # ------------------------------------------------------------------------------
    @override
    def GetTaskOwnedData(self, bDeserialize_ =True) -> Any:
        """
        See:
            >>> ITask.GetTaskOwnedData()
        """
        return self.__a.GetTaskOwnedData(bDeserialize_=bDeserialize_)


    @override
    def SetTaskOwnedData(self, taskOwnedData_ : Any, bSerialize_ =False):
        """
        See:
            >>> ITask.SetTaskOwnedData()
        """
        self.__a.SetTaskOwnedData(taskOwnedData_, bSerialize_=bSerialize_)
    # ------------------------------------------------------------------------------
    # 6) task-owned data
    # ------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # 7) message handling
    # ------------------------------------------------------------------------------
    @override
    def SendMessage( self
                   , rxTask_       : Union[ITask, IntEnum, int]
                   , msgLabelID_   : Union[IntEnum, int]   =EXmsgPredefinedID.DontCare
                   , msgClusterID_ : Union[IntEnum, int]   =EXmsgPredefinedID.DontCare
                   , msgPayload_   : Union[IPayload, dict] =None) -> int:
        """
        See:
            >>> IXTask.SendMessage()
        """
        return self.__a.SendMessage(rxTask_, msgLabelID_=msgLabelID_, msgClusterID_=msgClusterID_, msgPayload_=msgPayload_)


    @override
    def BroadcastMessage( self
                        , msgLabelID_   : Union[IntEnum, int]
                        , msgClusterID_ : Union[IntEnum, int]   =EXmsgPredefinedID.DontCare
                        , msgPayload_   : Union[IPayload, dict] =None) -> int:
        """
        See:
            >>> IXTask.BroadcastMessage()
        """
        return self.__a.BroadcastMessage(msgLabelID_, msgClusterID_=msgClusterID_, msgPayload_=msgPayload_)


    @override
    def TriggerExternalQueueProcessing(self) -> int:
        """
        See:
            >>> IXTask.TriggerExternalQueueProcessing()
        """
        return self.__a.TriggerExternalQueueProcessing()
    # ------------------------------------------------------------------------------
    #END 7) message handling
    # ------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # 8) error handling
    # ------------------------------------------------------------------------------
    @ITask.isErrorFree.getter
    def isErrorFree(self) -> bool:
        """
        See:
            >>> ITask.isErrorFree
        """
        return self.__a.isErrorFree


    @ITask.isFatalErrorFree.getter
    def isFatalErrorFree(self) -> bool:
        """
        See:
            >>> ITask.isFatalErrorFree
        """
        return self.__a.isFatalErrorFree


    @ITask.currentError.getter
    def currentError(self) -> ITaskError:
        """
        See:
            >>> ITask.currentError
        """
        return self.__a.currentError


    @override
    def ClearCurrentError(self) -> bool:
        """
        See:
            >>> ITask.ClearCurrentError()
        """
        return self.__a.ClearCurrentError()


    @override
    def SetError(self, errorMsg_ : str):
        """
        See:
            >>> ITask.SetError()
        """
        self.__a.SetError(errorMsg_)


    @override
    def SetErrorEC(self, errorMsg_ : str, errorCode_: int):
        """
        See:
            >>> ITask.SetErrorEC()
        """
        self.__a.SetErrorEC(errorMsg_, errorCode_)


    @override
    def SetFatalError(self, errorMsg_ : str):
        """
        See:
            >>> ITask.SetFatalError()
        """
        self.__a.SetFatalError(errorMsg_)


    @override
    def SetFatalErrorEC(self, errorMsg_ : str, errorCode_: int):
        """
        See:
            >>> ITask.SetFatalErrorEC()
        """
        self.__a.SetFatalErrorEC(errorMsg_, errorCode_)
    # ------------------------------------------------------------------------------
    #END 8) error handling
    # ------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # 9) supplementary API
    # ------------------------------------------------------------------------------
    @IXTask.isMainTask.getter
    def isMainTask(self) -> bool:
        """
        See:
            >>> IXTask.isMainTask
        """
        return self.__a.isMainTask


    @IXTask.taskProfile.getter
    def taskProfile(self) -> ITaskProfile:
        """
        See:
            >>> IXTask.taskProfile
        """
        return self.__a.taskProfile


    @override
    def SelfCheck(self) -> bool:
        """
        See:
            >>> ITask.SelfCheck()
        """
        return self.__a.SelfCheck()


    @override
    def SelfCheckSleep(self, sleepTime_: Union[int, float] =None) -> bool:
        """
        See:
            >>> IXTask.SelfCheckSleep()
        """
        return self.__a.SelfCheckSleep(sleepTime_)


    @override
    def ToString(self) -> str:
        """
        See:
            >>> ITask.ToString()
        """
        return str(self.__a)
    # ------------------------------------------------------------------------------
    #END 9) supplementary API
    # ------------------------------------------------------------------------------
#END class XTask
