# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : iftask.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from typing import Any
from typing import Union

from xcofdk.fwcom   import CompoundTUID
from xcofdk.fwcom   import EExecutionCmdID
from .iftaskerror   import ITaskError
from .iftaskprofile import ITaskProfile


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class ITask:
    """
    Instances of this interface class represent common API of task instances
    created by the framework and provided to applications.

    It has a rich set of API functions. For quick orientation and guidance on
    by when to use which one, the interface is arranged in subsets each of them
    labeled in accordance to the given logical context by a comment block
    of the form:
        >>> # --------------------------------------------------------------
        >>> # SecNo) title of interface subset
        >>> # --------------------------------------------------------------

    Currently available interface subsets are as follows:
         1) c-tor / built-in
         2) phasedXF callbacks
         3) start/stop
         4) task state
         5) task (unique) properties
         6) task-owned data
         7) message handling
         8) error handling
         9) supplementary API
    """

    __slots__ = []


    # ------------------------------------------------------------------------------
    # 1) c-tor / built-in
    # ------------------------------------------------------------------------------
    def __init__(self):
        """
        See:
        -----
            - class RCTask
            - class XTask
        """
        pass


    def __str__(self):
        """
        See:
        -----
            >>> ITask.ToString()
        """
        return self.ToString()
    # ------------------------------------------------------------------------------
    #END 1) c-tor / built-in
    # ------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # 2) phasedXF callbacks
    # ------------------------------------------------------------------------------
    # n/a
    # ------------------------------------------------------------------------------
    #END 2) phasedXF callbacks
    # ------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # 3) start/stop
    # ------------------------------------------------------------------------------
    def Start(self, *args_, **kwargs_) -> bool:
        """
        Request to start this task.

        Passed in positional and/or keyword arguments (if any) will be passed
        to either one of the phasedXF callbacks below:
            - setup phase if configured,
            - run phase otherwise.

        Parameters:
        -------------
            - args_ :
              positional arguments (if any).
            - kwargs_ :
              keyword arguments (if any).

        Returns:
        ----------
            True if the operation succeeds, False otherwise.

        Note:
        ------
            - A request to start a synchronous task is always a synchronous,
              i.e. blocking, operation. Note that synchronous tasks can only be
              started from within the currently running host thread. That is,
              the requester will be blocked until the execution of task's 3-PhXF
              is finished.

            - For asynchronous tasks the operation is non-blocking, it returns
              right before the execution of task's 3-PhXF is going to take place.
              That is, the actual execution of such a task is always performed
              asynchronously.

            - Right after start, a synchronous task immediately is in state
              'running'.

            - For an asynchronous task, however, it is in principle in a pending
              state (for a short while) until its execution effectively takes
              place. The duration of that pending state is out of the control of
              the framework, it basically is controlled by the (scheduling
              mechanism of the) host operating system, and possibly by the host
              programming language, e.g. Python due to the GIL (if enabled).

            - Below simplified code snippet (for debug mode) may be of some help
              for better understanding of the start operation:
                  >>>
                  >>> def StartMyTask(tsk_ : ITask) -> bool:
                  >>>     #ASSUMPTION:
                  >>>     #  - Passed in 'tsk_' is an instance of either class RCTask,
                  >>>     #    or a user-defined class subclassing one of the abstract
                  >>>     #    classes XTask or XMainTask.
                  >>>
                  >>>     # make sure interpreter's debug mode is not turned off
                  >>>     if not __debug__:
                  >>>         return False
                  >>>
                  >>>     assert tsk_.isAttachedToFW
                  >>>     assert not tsk_.isStarted
                  >>>
                  >>>     # start the task
                  >>>     if not tsk_.Start():
                  >>>         # the operation failed for whatever reason
                  >>>         return False
                  >>>
                  >>>     # now, the 'isStarted' property will always pass the assertion
                  >>>     assert tsk_.isStarted
                  >>>
                  >>>     # synchronous task?
                  >>>     if tsk_.isSyncTask:
                  >>>         # as a synchronous task, it is terminated already
                  >>>         assert tsk_.isTerminated
                  >>>
                  >>>     # asynchronous task
                  >>>     else:
                  >>>         while True:
                  >>>             # still in pending state?
                  >>>             if tsk_.isPendingRun:
                  >>>                 # if ever, this should happen for a very short time only, so stay in the loop
                  >>>                 continue
                  >>>
                  >>>             # task is not waiting for its initial CPU assignment anymore, leave the loop
                  >>>             break
                  >>>
                  >>>         # task is in either one of the states below
                  >>>         assert tsk_.isRunning or tsk_.isTerminating or tsk_.isTerminated
                  >>>
                  >>>         # wait for the task to finish its work (if still running)
                  >>>         tsk_.Join()
                  >>>
                  >>>     # now, the task is in either one of the states below
                  >>>     assert tsk_.isDone or tsk_.isCanceled or tsk_.isFailed
                  >>>
                  >>>     return True

            - Unless for the purpose of advanced, application-specific
              synchronization of quite many tasks started in a row, in practice
              the task state 'isPendingRun' should rarely be observable by
              applications or even need to be considered at all.

              But, if ever troubling, it in fact represents a typical race
              condition related to the possibly needed synchronization between
              both the caller and the callee host threads. Releasing the CPU
              by the caller for a short time is a common approach when dealing
              with start of host threads. Same approach should also resolve
              similar problems with task instances, too, as depicted below:
                  >>> from time   import sleep
                  >>> from typing import List
                  >>>
                  >>> def StartAsyncTasks(pool_ : List[ITask]):
                  >>>     for tt in pool_:
                  >>>         tt.Start()
                  >>>
                  >>>     # sleep for a proper amount of time, e.g. 20 [ms]
                  >>>     sleep(0.02)

        See:
        -----
            >>> ITask.isSyncTask
            >>> ITask.isStarted
            >>> ITask.isRunning
            >>> ITask.isPendingRun
            >>> ITask.isDone
            >>> ITask.isCanceled
            >>> ITask.isFailed
            >>> ITask.isFirstRunPhaseIteration
            >>> ITask.Stop()
            >>> ITask.Cancel()
            >>> ITask.Join()
            >>> ITask.DetachFromFW()
        """
        pass


    def Stop(self) -> bool:
        """
        Request to stop this task.

        Returns:
        ----------
            True if the operation succeeds, False otherwise.

        Note:
        ------
            - Requests to stop tasks which are in a transitional state of
              termination (i.e. stopping, canceling or aborting) already are
              ignored by the framework.
            - A request to stop a task is always a non-blocking instruction to
              stop the task. It simply notifies the task about the stop request
              and returns.
            - Detaching a task from the framework causes that task to be stopped
              by the framework as well (if still running).
            - Upon initiating the shutdown sequence, the framework always asks
              running tasks to stop their execution via this API function, but
              never via API function 'Cancel()'.

        See:
        -----
            >>> ITask.isRunning
            >>> ITask.isDone
            >>> ITask.isCanceled
            >>> ITask.isFailed
            >>> ITask.isTerminating
            >>> ITask.Start()
            >>> ITask.Cancel()
            >>> ITask.Join()
            >>> ITask.DetachFromFW()
            >>> EExecutionCmdID.STOP
        """
        pass


    def Cancel(self) -> bool:
        """
        Request to cancel this task.

        Returns:
        ----------
            True if the operation succeeds, False otherwise.

        Note:
        ------
            - Canceling a task is an API function reserved for use by
              applications only, the framework never makes any use of it.
            - Its major purpose is to provide applications with their own
              logical and/or functional attribution of the execution result of
              a task which is terminated, but not failed, i.e. having caused
              any LC failure. Such an attribution might look like below:
                  - DONE     : finished or stopped the job as expected, or
                  - CANCELED : not failed, but broken for whatever
                               application-specific reason
            - Requests to cancel tasks which are in a transitional state of
              termination (i.e. stopping, canceling or aborting) already are
              ignored by the framework.
            - A request to cancel a task is always a non-blocking instruction
              to cancel the task. It simply notifies the task about the cancel
              request and returns.

        See:
        -----
            >>> ITask.isRunning
            >>> ITask.isDone
            >>> ITask.isCanceled
            >>> ITask.isFailed
            >>> ITask.isTerminating
            >>> ITask.Start()
            >>> ITask.Stop()
            >>> ITask.Join()
            >>> ITask.DetachFromFW()
            >>> EExecutionCmdID.CANCEL
        """
        pass


    def Join(self, maxWaitTime_: Union[int, float] =None) -> bool:
        """
        Request to join this task, thus waiting for its termination.

        Parameters:
        -------------
            - maxWaitTime_ :
              if None it will wait forever. Otherwise, it will wait for the
              specified amount of time (milliseconds for int values or seconds
              for floating-point values) before the operation returns.

        Returns:
        ----------
            True if the operation succeeds, False otherwise.

        Note:
        ------
            - Requests to join tasks which are terminated (i.e. stopped,
              canceled or aborted) already are ignored by the framework.
            - Attempts to join a task from within its own 3-PhXF is ignored by
              the framework.
            - Otherwise, the requester is blocked (for the specified wait time)
              until the task is terminated.

        See:
        -----
            >>> ITask.isTerminated
            >>> ITask.Start()
            >>> ITask.Stop()
            >>> ITask.Cancel()
            >>> ITask.DetachFromFW()
        """
        pass


    def DetachFromFW(self):
        """
        Request to detach this task from the framework.

        Note:
        ------
            - The main purpose of detaching a task from the framework is to
              release the application or system resources used for that task.
            - Detaching is always done automatically by the framework upon
              termination of tasks.
            - Detaching a task from the framework by intention and before its
              termination, is much like requesting the framework to stop the
              task (if applicable).
            - As soon as a task is detached from the framework, it won't be able
              to use the full set of its reqular API anymore. Its task state
              will be set in accordance to the task state right after the
              internal handling of the request is completed, e.g. 'stopping',
              and not updated anymore.

        See:
        -----
            >>> ITask.Stop()
            >>> ITask.isDetachedFromFW
        """
        pass
    # ------------------------------------------------------------------------------
    #END 3) start/stop
    # ------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # 4) task state
    # ------------------------------------------------------------------------------
    @property
    def isAttachedToFW(self) -> bool:
        """
        Getter property for task's state of being 'attached to framework'.

        Returns:
        ----------
            True if this instance is (still) attached to the framework, False
            otherwise.

        Note:
        ------
            - Task instances correctly constructed are always attached to the
              framework until they are terminated or requested to be detached
              from the framework.
            - So, once successfully created, both alias name and compound unique
              ID of a task are promptly available even if not started yet.

        See:
        -----
            >>> ITask.isDetachedFromFW
            >>> ITask.aliasName
            >>> ITask.taskCompoundUID
            >>> ITask.DetachFromFW()
        """
        pass


    @property
    def isDetachedFromFW(self) -> bool:
        """
        Getter property for task's state of being 'detached from framework'.

        Returns:
        ----------
            True if this instance is dettached from the framework,
            False otherwise.

        Note:
        ------
            - Task instances correctly constructed are always attached to the
              framework until they are terminated or requested to be detached
              from the framework.

        See:
        -----
            >>> ITask.isAttachedToFW
            >>> ITask.DetachFromFW()
        """
        pass


    @property
    def isStarted(self) -> bool:
        """
        Getter property for task's state of being 'started'.

        Returns:
        ----------
            True if this instance has been started, False otherwise.

        Note:
        ------
            - A task is considered 'started', as soon as a request to start
              that task is succeeded. This property of a task remains unchanged
              during its lifcycle regardless of its subsequent task states.
            - However, the property of being 'started' is not a true task
              state. It simply means whether a task has been requested to start
              already.
            - Also, it is important to be aware of the difference betwewen the
              return values of below API:
                  - ITask.Start():
                    returns True if the start was succeeded,
                  - ITask.isStarted:
                    returns True if an attempt to start the task has been made
                    already regardless of the result of its start operation.
            - For more about subsequent task states after start refer to the
              API function 'ITask.Start()'.

        See:
        -----
            >>> ITask.Start()
        """
        pass


    @property
    def isPendingRun(self) -> bool:
        """
        Getter property for task's state of being 'pending for execution'.

        Returns:
        ----------
            True if this instance has been started, but still waiting for its
            very first CPU assignment (and thus be provided with its own
            execution context), False otherwise.

        Note:
        ------
            - Synchronous tasks never get into this state when started.
              Instead, they are rather immediatey in running state as soon as
              the execution of their 3-PhXF begins.
            - Detailed description of the pending state of asynchronous tasks
              is provieded in the API function 'ITask.Start()'.

        See:
        -----
            >>> ITask.Start()
            >>> ITask.isSyncTask
            >>> ITask.isRunning
        """
        pass


    @property
    def isRunning(self) -> bool:
        """
        Getter property for task's state of being 'running'.

        Returns
        ----------
            True if this instance is started, but not terminating or terminated,
            False otherwise.

        Note:
        ------
            - When started, a task is in 'running' state as soon as it enters
              its 3-PhXF, i.e. setup phase (if configured so) or run phase.
            - A task is no longer in 'running' state once it reaches its
              transitional state 'terminating', especially when leaving its
              (cyclic) run phase.
            - Thus, tasks are particularly not in the state of 'running' anymore
              whenever they enter their teadown phase (if configured).
            - Also, as soon as a (submitted) fatal error becomes qualified, the
              affected task instance leaves its 'runnig' state, too.

        See:
        -----
            >>> ITask.Start()
            >>> ITask.isPendingRun
            >>> EExecutionCmdID.CONTINUE
        """
        pass


    @property
    def isDone(self) -> bool:
        """
        Getter property for task's state of being 'done'.

        Returns:
        ----------
            True if this instance has finished its execution upon normal
            termination, False otherwise.

        Note:
        ------
            - The task state 'done' is one of the possible three final states
              assigned to a task when terminated.
            - As opposed to both final states 'canceled' and 'failed', tasks
              reach the final state 'done' at the end of the execution of their
              3-PhXF whenever they neither have caused any fatal error nor they
              have been requested to cancel.
            - Tasks requested to stop via API function 'ITask.Stop()' (or
              intentially requesting the framework to stop before full execution
              of their 3-PhXF) end up in the final state 'done', too.

        See:
        -----
            >>> ITask.isCanceled
            >>> ITask.isFailed
            >>> ITask.isTerminated
            >>> ITask.Start()
            >>> ITask.Stop()
            >>> ITask.Cancel()
            >>> EExecutionCmdID.STOP
        """
        pass


    @property
    def isCanceled(self) -> bool:
        """
        Getter property for task's state of being 'canceled'.

        Returns:
        ----------
            True if this instance has finished its execution due to a 'cancel'
            request, False otherwise.

        Note:
        ------
            - The task state 'canceled' is one of the possible three final
              states assigned to a task when terminated.
            - Tasks reach the final state 'canceled' if and only if they were
              requested to break their execution via API function
              'ITask.Cancel()', or if they intentially request the framework
              to cancel the execution.

        See:
        -----
            >>> ITask.isDone
            >>> ITask.isFailed
            >>> ITask.isTerminated
            >>> ITask.Start()
            >>> ITask.Stop()
            >>> ITask.Cancel()
            >>> EExecutionCmdID.CANCEL
        """
        pass


    @property
    def isFailed(self) -> bool:
        """
        Getter property for task's state of being 'failed', i.e. aborted.

        Returns:
        ----------
            True if this instance has finished its execution upon abnormal
            termination, False otherwise.

        Note:
        ------
            - The task state 'failed' is one of the possible three final
              states assigned to a task when terminated.
            - A task reaches the final state 'failed' if and only if the
              execution of its 3-PhXF causes a qualified fatal error, i.e. an
              LC failure, or if it intentially requests the framework to abort
              the execution.
            - In other words, as soon as this instance leaves its 'running' (or
              'stopping' or 'canceling') state due to a qualified fatal error
              caused by this instance (or intentially by returning
              EExecutionCmdID.ABORT out of its 3-PhXF), it is considered failed.
            - Whenever a task reaches this state, it will immediately be
              auto-detached from the framework.
            - Also note, that the state property 'isAboring' is deprecated now.

        See:
        -----
            >>> ITask.isDone
            >>> ITask.isCanceled
            >>> ITask.isTerminated
            >>> ITask.isDetachedFromFW
            >>> ITask.Start()
            >>> ITask.Stop()
            >>> ITask.Cancel()
            >>> ITask.DetachFromFW()
            >>> EExecutionCmdID.ABORT
        """
        pass


    @property
    def isTerminated(self) -> bool:
        """
        Getter property for task's state of being 'terminated'.

        Returns:
        ----------
            True if this instance has reached one of its final states 'done',
            'cancele' or 'failed', False otherwise.

        See:
        -----
            >>> ITask.isDone
            >>> ITask.isCanceled
            >>> ITask.isFailed
        """
        pass


    @property
    def isTerminating(self) -> bool:
        """
        Getter property for task's state of being 'terminating'.

        Returns:
        ----------
            True as soon as this instance leaves its 'running' state,
            False otherwise.

        Note:
        ------
            - A terminating task is either 'stopping' or 'aborting'.
            - The state 'canceling' is a special case of 'stopping'.
              It is assigned to a task in the course of processing of
              a cancel request.

        See:
        -----
            >>> ITask.isRunning
            >>> ITask.isStopping
            >>> ITask.isCanceling
            >>> ITask.isAborting
            >>> EExecutionCmdID.STOP
            >>> EExecutionCmdID.CANCEL
            >>> EExecutionCmdID.ABORT
        """
        pass


    @property
    def isStopping(self) -> bool:
        """
        Getter property for task's state of being 'stopping'.

        Returns:
        ----------
            True as soon as this instance leaves its 'running' state without
            having caused any fatal error (or intentially by returning either
            one of EExecutionCmdID.STOP or EExecutionCmdID.CANCEL out of its
            3-PhXF), False otherwise.

        Note:
        ------
            - Whenever a task enters its teardown phase (if configured), it is
              either in state 'canceling' if it was canceled before, or in state
              'stopping' otherwise.

        See:
        -----
            >>> ITask.isRunning
            >>> ITask.isCanceling
            >>> EExecutionCmdID.STOP
            >>> EExecutionCmdID.CANCEL
        """
        pass


    @property
    def isCanceling(self) -> bool:
        """
        Getter property for task's state of being 'canceling'.

        Returns:
        ----------
            True as soon as this instance leaves its 'running' state due to a
            'cancel' request (or intentially by returning EExecutionCmdID.CANCEL
            out of its 3-PhXF), False otherwise.

        Note:
        ------
            - Whenever a task enters its teardown phase (if configured), it is
              either in state 'canceling' if it was canceled before, or in state
              'stopping' otherwise.

        See:
        -----
            >>> ITask.isRunning
            >>> ITask.isStopping
            >>> EExecutionCmdID.STOP
            >>> EExecutionCmdID.CANCEL
        """
        pass


    @property
    def isAborting(self) -> bool:
        """
        [DEPRECATED]
          - This task state property is still present for backward compatibily
            reason only.
          - It is planned to be removed by the next change of the major
            release number from 3.x to 4.x (if ever).
        """
        return False
    # ------------------------------------------------------------------------------
    #END 4) task state
    # ------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # 5) task (unique) properties
    # ------------------------------------------------------------------------------
    @property
    def isSyncTask(self) -> bool:
        """
        Getter property for this task's execution type.

        Returns:
        ----------
            True if this instance is configured to be executed by the framework
            as a synchronous task, False otherwise.

        See:
        -----
            >>> ITaskProfile.isSyncTask
        """
        pass


    @property
    def isFirstRunPhaseIteration(self) -> bool:
        """
        Getter property for this task's first iteration of the run phase.

        Returns:
        ----------
            True if it is the initial iteration of the run phase being executed
            right now, False otherwise.

        Note:
        ------
            - This property is especially useful for tasks with no setup phase
              specified for them. Then, whenever started this property can be
              used for possible application-specific initialization purposes.
            - The run phase of a task configuered for support of blocking
              external queue is given by the corresponding 3-PhXF callback
              function for processing of external messages.

        See:
        -----
            >>> ITaskProfile.isRunPhaseEnabled
            >>> ITaskProfile.isSetupPhaseEnabled
            >>> ITaskProfile.isExternalQueueBlocking
            >>> ITask.Start()
            >>> ITask.currentRunPhaseIterationNo
        """
        pass


    @property
    def taskUID(self) -> int:
        """
        Getter property for task's unique ID.

        Returns:
        ----------
            Auto-generated unique ID of this instance if started, None
            otherwise.

        See:
        -----
            >>> ITask.isStarted
        """
        pass


    @property
    def taskName(self) -> str:
        """
        Getter property for task's unique name.

        Returns:
        ----------
            Auto-generated string object representing unique name of this
            instance if started, task's alias name otherwise.

        See:
        -----
            >>> ITask.aliasName
            >>> ITask.isStarted
        """
        pass


    @property
    def aliasName(self) -> str:
        """
        Getter property for task's alias name.

        Returns:
        ----------
            Alias name assigned to this instance.

        Note:
        ------
            - The alias name of a task is specified in either ways below:
                  a) if supplied, via respective parameter passed to the
                     constructor of either class RCTask, or a user-defined
                     class subclassing one of the abstract classes XTask or
                     XMainTask, or
                  b) if not supplied, auto-generated by the framework as shown
                     below:
                       Tsk_<INST_NO>   : for instances of class RCTask without
                                         external queue support
                       CTsk_<INST_NO>  : for instances of class RCTask with
                                         external queue support
                       XTsk_<INST_NO>  : for instances of class XTask without
                                         external queue support
                       CXTsk_<INST_NO> : for instances of class XTask with
                                         external queue support
                     with:
                       - 'INST_NO' is the unique instance number (see
                         'taskCompoundUID').
                       - 'C' stands for 'capable of full Communication',
                         something available to a task only if created with
                         support for external queue requested for.
            - Note that for a supplied alias name with a trailing '_' the
              above-mentioned 'INST_NO' will be appended to.
            - The alias name is always available for successfully constructed
              task instances.

        See:
        -----
            >>> ITaskProfile.aliasName
            >>> ITask.isAttachedToFW
            >>> ITask.taskCompoundUID
        """
        pass


    @property
    def taskCompoundUID(self) -> CompoundTUID:
        """
        Getter property for task's compound unique ID.

        Returns:
        ----------
            An auto-generated namedtuple object with below immutable fields:
                - uid    : unique ID of the task
                - instNo : unique, positive integer value representing
                           the instance number auto-assigned to this task

        Note:
        ------
            - The compound unique ID is always available for successfully
              constructed task instances.
            - The field 'uid' of the returned object equals to the property
              'ITask.uniqueID' available once the task is started.

              In other words, once a task instance is created, its unique ID
              is already reserved and available even if that task is not started
              yet, a valuable feature when it comes to share sender and/or
              receiver information for messaging purposes even before the
              communication participants are alive.

        See:
        -----
            >>> ITask.isAttachedToFW
            >>> ITask.taskUID
            >>> CompoundTUID
        """
        pass


    @property
    def currentRunPhaseIterationNo(self) -> int:
        """
        Getter property for this task's current iteration number of the run
        phase.

        Returns:
        ----------
            -1 if the run phase of this instance has not been entered yet,
            0-based current iteration number otherwise.

        Note:
        ------
            - For task instance with single-cycle run phase the returned value
              is either -1 or 0.
            - The run phase of a task configuered for support of blocking
              external queue is given by the corresponding 3-PhXF callback
              function for processing of external messages.

        See:
        -----
            >>> ITask.isFirstRunPhaseIteration
            >>> ITask.Start()
            >>> ITaskProfile.isRunPhaseEnabled
            >>> ITaskProfile.isExternalQueueBlocking
            >>> ITaskProfile.isSingleCycleRunPhase
        """
        pass
    # ------------------------------------------------------------------------------
    #END 5) task (unique) properties
    # ------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # 6) task-owned data
    # ------------------------------------------------------------------------------
    def GetTaskOwnedData(self, bDeserialize_ =True) -> Any:
        """
        Retrieve application-specific data (if any) owned by this instance.

        Parameters:
        -------------
           - bDeserialize_ :
             if False or if the data to be retrieved is not a byte stream,
             return the data as is, de-serialize it before otherwise.

        Returns:
        ----------
            None if no data is available, the data object stored last time
            otherwise.

        Note:
        ------
            - Application-specific data of a new task instance is initialized
              with None.
            - Read/write access to application-specific data of a task is
              managed by the framework in a synchronized, thread-safa manner.

        See:
        -----
            >>> ITask.SetTaskOwnedData()
        """
        pass


    def SetTaskOwnedData(self, taskOwnedData_ : Any, bSerialize_ =False):
        """
        Store or update the application-specific data owned by this instance.

        Parameters:
        -------------
           - taskOwnedData_ :
             application-specific data of this instance to be stored,
           - bSerialize_ :
             if True serialize passed in data before, if passed in data
             is not a byte stream already.

        Note:
        ------
            - Application-specific data of a new task instance is initialized
              with None.
            - Read/write access to application-specific data of a task is
              managed by the framework in a synchronized, thread-safa manner.

        See:
        -----
            >>> ITask.GetTaskOwnedData()
        """
        pass
    # ------------------------------------------------------------------------------
    #END 6) task-owned data
    # ------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # 7) message handling
    # ------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------
    #END 7) message handling
    # ------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # 8) error handling
    # ------------------------------------------------------------------------------
    @property
    def isErrorFree(self) -> bool:
        """
        Getter property for this task's current error state.

        Returns:
        ----------
            True if currently neither a user nor a fatal error is associated
            with this instance, False otherwise.

        See:
        -----
            >>> ITask.isFatalErrorFree
            >>> ITask.currentError
            >>> ITaskError
        """
        pass


    @property
    def isFatalErrorFree(self) -> bool:
        """
        Getter property for this task's current fatal error state.

        Returns:
        ----------
            True if currently no fatal error is associated with this instance,
            False otherwise.

        See:
        -----
            >>> ITask.isErrorFree
            >>> ITask.currentError
            >>> ITaskError
        """
        pass


    @property
    def currentError(self) -> ITaskError:
        """
        Getter property for this task's current error.

        Returns:
        ----------
            An instance of class ITaskError if there is a (fatal) error
            currently associated with this task, None otherwise.

        Note:
        ------
            - A task is always associated with its current error only (if any)
              which is either a user error or a fatal error.

            - A current fatal error can only be cleared by a task itself
              during the qualification process of submitted fatal errors.

            - A current user error is auto-cleared by the framework before
              entering any of the phases of 3-PhXF (in case of run phase before
              starting next run cycle). That is tasks starts their phases of
              3-PhXF always in an error-free state.

            - Fatal errors have precedence over user errors, that is submitting
              a fatal error overwrites existing current user error (if any).

            - In all other cases where a task is already associated with its
              current user/fatal error, submitting subsequent errors (of the
              same error type as the current error) for that task does not
              touch its current user/fatal error.

              In other words, unless current error is resolved (or cleared),
              it cannot be overwritten. This way, current error is kind of
              'very first error' of the respective phase (cycle) of 3-PhXF.

            - However, corresonding setter operations (see below) may be used
              by a task to set or replace its current error.

        See:
        -----
            >>> ITask.isErrorFree
            >>> ITask.isFatalErrorFree
            >>> ITask.ClearCurrentError()
            >>> ITask.SetError()
            >>> ITask.SetFatalError()
            >>> ITaskError
        """
        pass


    def ClearCurrentError(self) -> bool:
        """
        Request to clear current error (if any) of this instance.

        Returns:
        ----------
            True if the operation succeeded, False otherwise.

        Note:
        ------
            - Request will be denied if not done out of the 3-PhXF of this task.
            - Otherwise, current user error (if any) can always be cleared, and
              so considered resolved.
            - Whether a current fatal error can be resolved or cleared by a task
              is described in the respective wiki page discussing framework's
              error handling.

        See:
        -----
            >>> ITask.currentError
            >>> ITaskError
        """
        pass


    def SetError(self, errorMsg_ : str):
        """
        Request to set or replace this task's current error by a user error.

        If the attempt to clear current error (if any) passes, the operation will
        make current error of this task is set as requested.

        Parameters:
        -------------
            - errorMsg_ :
              user error message to be set as current error of this task

        Note:
        ------
            - Request will be denied if not done out of the 3-PhXF of this task.
            - As opposed to submitting an error, setting (or replacing) current
              error of a task does not generate any (print) output.

        See:
        -----
            >>> ITask.currentError
            >>> ITask.SetErrorEC()
            >>> ITask.ClearCurrentError()
            >>> ITaskError
        """
        pass


    def SetErrorEC(self, errorMsg_ : str, errorCode_: int):
        """
        Request to set or replace this task's current error by a user error.

        If the attempt to clear current error (if any) passes, the operation will
        make current error of this task is set as requested.

        Parameters:
        -------------
            - errorMsg_ :
              user error message to be set as current error of this task
            - errorCode_ :
              positive integer value used as error code to be set for
              current error of this task

        Note:
        ------
            - Request will be denied if not done out of the 3-PhXF of this task.
            - As opposed to submitting an error, setting (or replacing) current
              error of a task does not generate any (print) output.

        See:
        -----
            >>> ITask.currentError
            >>> ITask.SetError()
            >>> ITask.ClearCurrentError()
            >>> ITaskError
        """
        pass


    def SetFatalError(self, errorMsg_ : str):
        """
        Request to set or replace this task's current error by a fatal error.

        If the attempt to clear current error (if any) passes, the operation will
        make current error of this task is set as requested.

        Parameters:
        -------------
            - errorMsg_ :
              fatal error message to be set as current error of this task

        Note:
        ------
            - Request will be denied if not done out of the 3-PhXF of this task.
            - As opposed to submitting an error, setting (or replacing) current
              error of a task does not generate any (print) output.

        See:
        -----
            >>> ITask.currentError
            >>> ITask.SetFatalErrorEC()
            >>> ITask.ClearCurrentError()
            >>> ITaskError
        """
        pass


    def SetFatalErrorEC(self, errorMsg_ : str, errorCode_: int):
        """
        Request to set or replace this task's current error by a fatal error.

        If the attempt to clear current error (if any) passes, the operation will
        make current error of this task is set as requested.

        Parameters:
        -------------
            - errorMsg_ :
              fatal error message to be set as current error of this task
            - errorCode_ :
              positive integer value used as fatal error code to be set
              for current error of this task

        Note:
        ------
            - Request will be denied if not done out of the 3-PhXF of this task.
            - As opposed to submitting an error, setting (or replacing) current
              error of a task does not generate any (print) output.

        See:
        -----
            >>> ITask.currentError
            >>> ITask.SetFatalError()
            >>> ITask.ClearCurrentError()
            >>> ITaskError
        """
        pass
    # ------------------------------------------------------------------------------
    #END 8) error handling
    # ------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # 9) supplementary API
    # ------------------------------------------------------------------------------
    def SelfCheck(self) -> bool:
        """
        Request to perform a self-check of this instance.

        The major purpose of self-check is to ensure that the task state is
        always up-to-date, especially after a time-consuming operation done
        by the application.

        Returns:
        ----------
            - True if:
                  - the instance is not started yet, or
                  - this instance is being executed right now with its execution
                    can continue,
            - False otherwise.

        Note:
        ------
            - If called for a task instance which is not the currently running
              task, then the last available operation result of the requested
              task will be returned.
            - As soon as a limited RTE mode, e.g. in case of an LC failure or
              whenever framework's shutdown sequence is initiated, self-check
              will not pass with the state of the task affected by the operation
              is set to 'stopping' (if not terminated or terminating already).
            - As long as a task:
                  - is in state 'running', the execution can continue,
                  - is not in state 'canceling' or 'aborting' its execution
                    of the teardown phase (if configured) con continue.

        See:
        -----
            >>> ITask.isRunning
            >>> ITask.isCanceling
            >>> ITask.isAborting
            >>> ITaskProfile.isTeardownPhaseEnabled
        """
        pass


    def ToString(self) -> str:
        """
        Returns:
        ----------
            A nicely printable string representation of this instance.
        """
        pass
    # ------------------------------------------------------------------------------
    #END 9) supplementary API
    # ------------------------------------------------------------------------------
#END class ITask
