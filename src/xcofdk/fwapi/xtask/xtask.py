# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xtask.py
#
# Copyright(c) 2023-2024 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from typing import Union

from xcofdk.fwcom       import xlogif
from xcofdk.fwcom       import ETernaryCallbackResultID
from xcofdk.fwapi.xtask import XTaskError
from xcofdk.fwapi.xtask import XTaskProfile
from xcofdk.fwapi.xmsg  import XMessage

from xcofdk._xcofw.fw.fwssys.fwcore.apiimpl.xtask.xtaskbase import _XTaskBase


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class XTask(_XTaskBase):
    """
    Abstract class representing application tasks to be executed by the
    framework.

    Concrete task instances can be created by sub-classing this class.
    Derived classes will have to override specific callback methods according
    to the corresponding properties (explained below) of the task profile
    passed to the constructor when a task instance is created.

    Tasks are designed to achieve light-weight parallelism (or concurrency),
    but applications may also require the ability to start and/or to communicate
    with processes, that is programs running in parallel. For this, class
    XProcess is provided as the heavy-weight counterpart of class XTask.

    Class XTask has a rich set of interface functions. For quick orientation
    and guidance on by when to use which one, the interface is arranged in
    logical, context-driven subsets each of them labeled by a comment block of
    the form:
        >>> # --------------------------------------------------------------
        >>> # title of interface subset
        >>> # --------------------------------------------------------------

    Currently available interface subsets of class XTask are as follows:
        1) constructor / initializer
        2) API to be overridden when sub-classing
        3) API start/stop
        4) API task state and properties
        5) API message handling
        6) API error handling
        7) API miscellaneous

    With regard to application code using and interfacing to the runtime
    environment of the framework class XTask is ideally suited for a general
    introduction of the basics. Sections below explain terms, definitions and
    related concepts of the framework, especially tasks.


    Host thread:
    --------------
    XCOFDK is designed to be a reliable, out-of-the-box runtime environment
    for both multithreading and multiprocessing. It is built around so-called
    threads provided by the underlying host programming language (and/or host
    operating system) with threading capability for execution of user-defined
    sequences of instructions.

    In case of XCOFDK for Python, it is implemented on top of instances of class
    'threading.Thread'. A task instance created by the framework and presented
    to an application as a (carefully assembled) executable artifact is always
    linked and associated to its underlying thread object underneath.

    As both thread and task are often used as synonyms, the term 'host thread'
    is particularly used whenever framework's design (or implementation) has
    to emphasize abovementioned association between task as an abstraction
    of its thread underneath.

    By design, framework's support of host threads is not limited to a specific
    type of thread objects only. Work is in progress to support other types of
    host threads, too, especially when it comes to make XCODFK is supporting
    third-party (GUI-) frameworks with their own, specific abstraction of both
    threading and parallelism at the latest.


    Execution frame 3-PhXF:
    -------------------------
    The so-called '3-phased execution frame' builds both conceptual and
    functional aspeccts of instances of this class reflected by below callback
    methods in the given order:
        >>> XTask.SetUpXTask()     # -> setup phase
        >>> XTask.RunXTask()       # -> run phase
        >>> XTask.TearDownXTask()  # -> teardown phase

    An exception to the abovementioned attribution of execution phases is
    whenever a task's external message queue (if any) is specified to be
    blocking. For such a task the run phase is then represented by its callback
    method below:
        >>> XTask.ProcessExternalMessage()  # -> run phase

    As a sum-up, 3-PhXF means that an application task is always an instance of
    a user-defined, derived class, e.g. 'MyTask', subclassing XTask which
    overrides the callback methods mentioned above according to the possible
    task profiles (see section 'Configuration' below) targeted by that
    user-defined class roughly shaped as follows:
        >>>
        >>> # file: my_task.py
        >>>
        >>> from xcofdk.fwcom       import override
        >>> from xcofdk.fwcom       import ETernaryCallbackResultID
        >>> from xcofdk.fwapi.xtask import XTask
        >>> from xcofdk.fwapi.xtask import XTaskProfile
        >>> from xcofdk.fwapi.xmsg  import XMessage
        >>>
        >>> class MyTask(XTask):
        >>>     def __init__(self, *args_, **kwargs_):
        >>>         super().__init__(taskProfile_=XTaskProfile())
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
        >>>
        >>>     # ...


    Configuration:
    ---------------
    The specification of 3-PhXF of a task instance is always done via
    corresponding setter properties of the task profile argument passed to
    the initializer when creating that task instance:
        >>> XTaskProfile.isSetupPhaseEnabled     = [True | False]
        >>> XTaskProfile.isTeardownPhaseEnabled  = [True | False]

        >>> # (or in case of blocking external queue)
        >>> XTaskProfile.isExternalQueueEnabled   = [True | False]
        >>> XTaskProfile.isExternalQueueBlocking  = [True | False]

    Unless the last two properties both resolve to True, the callback method
    'RunXTask()' represents the run phase which is the default configuration.
    Otherwise, the callback method 'ProcessExternalMessage()' will serve as
    run phase.

    Finally, configuration of task's (external/interal) message queues, and so
    their respective callback methods, is an essential part of the subsystem
    messaging of the framework explained in more detail in class description
    of XMessageManager.


    Asymmetric task state transition:
    -----------------------------------
    Tasks are accompanied by a corresponding state transition as they pass
    through their execution phases of 3-PhXF. Except for the transitional
    states, three task states are mostly relevant to application code
    interfacing with tasks:
        - running
        - stopped
        - failed (i.e. aborted)

    Both last states are final, and it is framework's responsibility to ensure
    that tasks reach one of them based on the state transition history before.

    State 'stopped' means:
        task has finished its execution path upon normal termination,
        especially without causing any fatal error.
        Note, however, thinkng of a task as a job executor, the logical
        interpretation of this state in terms of 'job achievement' might be
        different, especially from application's viewpoint. Such a logical
        interpretation is considered by the framework application-specific with
        it is best designed and implemented by derived class(es) sub-classing
        this class.

    State 'failed' means:
        task has aborted its execution by intention, or submitted a fatal error
        by intention, or crashed (i.e. caused an unexpected exception).

    State 'running' means:
        task is still within its setup or run phase.
        But, tasks within their teardown phase (if configured), are rather in
        their transitional state 'stopping'.

    Teardown phase (if configured) serves as an opportunity for local cleanup
    purposes of free-of-fatal-error tasks. Therefore, the framework considers
    this execution phase rather a 'pure transitional' phase (possibly towards
    true ternimation of the underlying host thread if the task is an
    asynchronous one, see below). Accordingly, limited functionality in terms
    of available framework API is granted to tasks in this phase.

    This is what makes state transition of tasks 'asymmetric' with regard to
    their 3-PhXF on one hand, and from interfacing point of view on the other
    hand (see also RTE modes below).

    Finally, note that while tasks provide interface funcitons to start, stop
    or join them, there is no correspondent one to 'abort' them.
    Aborting a task is considered by the framework a critical, reserved
    operation. It is only possible either from within that task's 3-PhXF by
    the task itself and by intention, or by the framework because of some fatal
    error caused by them.


    Currently running task:
    -------------------------
    In this documentation the term 'running' is used in two different contexts
    when application tasks are of concern:
        1) 'task state running' (as described above),
        2) 'currently running task' meaning more precisely the instance of XTask
           whose associated host thread is currently executed (by the scheduler
           of the host OS) within any one of execution phases of its 3-PhXF
           regardless its current task state.

    Unless otherwise needed, and also for more readability, reader's awareness
    of the given context will be assumed.


    Task types:
    ------------
    There are two types of tasks with respect to their execution:
        - synchronous, meaning task is executed within the execution context
          of currently running host thread,
        - asynchronous, meaning task is executed within the execution context
          of a new, to be created host thread.

    The corresponding setter property of the task profile to specifiy the
    execution type is:
        >>> XTaskProfile.isSynchronousTask = [True | False]


    RTE modes:
    -------------
    From interfacing point of view of an application using the runtime
    environment (RTE for short) of XCOFDK, instaaces of class XTask (as well as
    of class XProcess) are key components provided by the framework to the
    application as active services.

    Unless otherwise oranized or configured by the application, availability of
    the public API of the framework is granted to task instances as long as RTE
    is in normal, unrestricted operational mode.

    However, there are two limited operational modes tasks (or processes)
    provided to the application should be aware of:
        - task-limited RTE mode:
          affecting individual tasks or services.
          It is currently the case whenever a task instance is within its
          teardown phase (if configured).

          Whenever this mode is given, an active service won't be able to
          perform message exchange anymore, except for sending messages.

        - LC-limited RTE mode:
          affecting all active tasks or services.
          It basically takes place as sson as the coordinated shutdown sequence
          of the framework takes place.

          In this mode neither the messaging subsystem nor any of the operations
          to create, start, stop or join tasks (or process) will be available.


    Note:
    ------
        - For error handling and lifecycle management refer to class description
          of XTaskError.
        - For subsystem messaging refer to class description of XMessageManager.


    See:
    -----
        - XTask.__init__()
        - xlogif.LogFatal()
        - xlogif.LogException()
        - XTaskProfile
        - XTaskError
        - XMessageManager
        - XProcess
    """

    __slots__ = []


    # --------------------------------------------------------------------------
    # 1) constructor / initializer
    # --------------------------------------------------------------------------
    def __init__(self, taskProfile_ : XTaskProfile =None):
        """
        Constructor (initializer) of instances of this class.

        Parameters:
        -------------
            - taskProfile_ :
              task profile to be used to configure the task instance to be
              created (or initialized).
              If None is passed to, a new task profile (with default values)
              will be created and used instead. Otherwise, passed in profile
              will be cloned and used as a read-only copy.

        Note:
        ------
            - A task instances is always attached to the framework after its
              successful creation.
            - As long as a task is attached to the framework, getter property
              below retrieves its associated, internal task profile instance
              which is always 'frozen':
                  XTask.xtaskProfile

              Frozen task profiles are read-only, their properties cannot be
              changed anymore.
            - Note, that the task profile argument passed to the constructor
              (if any) remains not-frozen, so it basically can still be modified
              and used to create other task instances.

        See:
        -----
            - XTask
            - XTask.isAttachedToFW
            - XTask.SetUpXTask()
            - XTask.RunXTask()
            - XTask.TearDownXTask()
            - XTask.ProcessExternalMessage()
            - XTaskProfile
            - XTaskProfile.isFrozen
        """
        super().__init__(taskProfile_)
    # --------------------------------------------------------------------------
    #END 1) constructor / initializer
    # --------------------------------------------------------------------------


    def __str__(self):
        """
        String representation of this instance.

        Returns:
        ----------
            A string object as representation of this instance.
        """
        return _XTaskBase.__str__(self)


    # --------------------------------------------------------------------------
    # 2) API to be overridden when sub-classing
    # --------------------------------------------------------------------------
    def SetUpXTask(self, *args_, **kwargs_) -> ETernaryCallbackResultID:
        """
        Callback of the setup phase of this instance if configured so.

        Configuration of the setup phase is explained in detail in description
        of this class above. This callback method will be called by the
        framework whenever this instance is started, and so to enter its 3-PhXF.

        Parameters:
        -------------
            - args_ :
              positional arguments (if any).
            - kwargs_ :
              keyword arguments (if any).

        Returns:
        ----------
            - ETernaryCallbackResultID.CONTINUE :
              to indicate that the execution of the run phase of this instance
              can take place.
            - ETernaryCallbackResultID.STOP :
              to instruct the framework to initiate the stop sequence (for
              whatever reason).
            - ETernaryCallbackResultID.ABORT :
              to indicate an unexpected, severe error. The framework will then
              immediately submit a fatal error accordingly.

        See:
        -----
            - XTask
            - XTaskProfile
            - XTask.__init__()
            - XTask.Start()
            - XTask.RunXTask()
            - section 4) API task state and properties
        """
        xlogif.LogWarning('Default impl of the setup phase, nothig to do, continue with run phase')
        return ETernaryCallbackResultID.CONTINUE


    def RunXTask(self, *args_, **kwargs_) -> ETernaryCallbackResultID:
        """
        Callback of the (cyclic) run phase of this instance if configured so.

        Configuration of the setup phase is explained in detail in description
        of this class above. This callback method will be called by the
        framework:
            - for the first time whenever this instance is started with no
              setup phase was configured, or
            - for the first time right after the setup phase provided its
              execution was successful, or (if applicable)
            - cyclically after each previously executed run phase cycle
              provided the execution of that cycle was successful.

        Finally, whether the setup phase via this callback method is cyclic
        depends on the configuration done via setter property below of the
        task profile argument passed to the constructor:
            >>> XTaskProfile.runPhaseFrequencyMS = VALUE

        The special case of 0 for run phase frequency will make the run phase
        become the so-called 'single-cycle run phase', so this callback method
        will be called only once.

        Parameters:
        -------------
            - args_ :
              positional arguments (if any).
            - kwargs_ :
              keyword arguments (if any).

        Returns:
        ----------
            - ETernaryCallbackResultID.CONTINUE :
              to indicate that the execution of this cycle of the run phase was
              successful.
              Unless configured as single-cycle run phase, cyclic execution of the
              run phase will keep going according to the specified run phase
              frequency mentioned above.
              Otherwise, teardown phase will take place if configured.
              Whenever no teardown phase was configured, the stop sequence of the
              task will be initiated by the framework.
            - ETernaryCallbackResultID.STOP :
              to indicate end of the run phase.
              Unless teardown phase is configured, the stop sequence of the task
              will be initiated by the framework. Otherwise, teardown phase will
              take place.
            - ETernaryCallbackResultID.ABORT :
              to indicate an unexpected, severe error. The framework will then
              immediately submit a fatal error accordingly.

        See:
        -----
            - XTask
            - XTaskProfile
            - XTask.__init__()
            - XTask.Start()
            - XTask.SetUpXTask()
            - XTask.TearDownXTask()
            - XTask.isFirstRunPhaseIteratoion
            - XTask.currentRunPhaseIteratoionNo
            - section 4) API task state and properties
        """
        xlogif.LogWarning('Default impl of the run phase, nothig to do, continue with teardown phase (if configured)')
        return ETernaryCallbackResultID.STOP


    def TearDownXTask(self) -> ETernaryCallbackResultID:
        """
        Callback of the teardown phase of this instance if configured so.

        Configuration of the teardown phase is explained in detail in
        description of this class above. This callback method will be called
        by the framework right after the run phase, unless it was aborted.

        Returns:
        ----------
            - ETernaryCallbackResultID.CONTINUE :
            - ETernaryCallbackResultID.STOP :
              to instruct the framework to initiate the stop sequence.
            - ETernaryCallbackResultID.ABORT :
              to indicate an unexpected, severe error. The framework will then
              immediately submit a fatal error accordingly.

        Note:
        ------
            - Teardown phase is designed to enable tasks to perfrom individual
              cleanup stuff (if any) upon their normal termination.
            - Bear in mind that a task in teardown phase is within the
              task-limited RTE mode (see description of this class above).

        See:
        -----
            - XTask
            - XTaskProfile
            - XTask.__init__()
            - XTask.RunXTask()
            - section 4) API task state and properties
        """
        xlogif.LogWarning('Default impl of the tear down phase, nothig to do.')
        return ETernaryCallbackResultID.STOP


    def ProcessExternalMessage(self, xmsg_ : XMessage) -> ETernaryCallbackResultID:
        """"
        Callback method called by the framework whenever there is a queued
        external message to be processed.

        Configuration of this callback method as run phase is explained in
        detail in description of this class above. In that case run phase will
        keep going as long as it is not stopped or aborted.

        Parameters:
        -------------
            - xmsg_ :
              external message to be processed

        Returns:
        ----------
            - ETernaryCallbackResultID.CONTINUE :
              to indicate message processing was successful, framework can keep
              going with message delivery to this task.
            - ETernaryCallbackResultID.STOP :
              to instruct the framework to stop message delivery to this task.
              In other words, it is a request to the framework to initiate the
              stop sequence of this task.
            - ETernaryCallbackResultID.ABORT :
              to indicate an unexpected, severe error. The framework will then
              immediately submit a fatal error accordingly.

        Note:
        ------
            - Unless configured as run phase via configuration property
              'XTaskProfile.isExternalQueueBlocking', processing of external
              messages takes place before next run phase cycle is executed
              (which is according to the default policy).
            - Also, a task may trigger the message processing itself at any time
              provided it is still in state running, and it is not processing
              messages already.

        See:
        -----
            - XTask.TriggerExternalQueueProcessing()
            - XTask.__init__()
            - XTask.isFirstRunPhaseIteratoion
            - XTask.currentRunPhaseIteratoionNo
            - XTaskProfile.isExternalQueueEnabled
            - XTaskProfile.isExternalQueueBlocking
            - XMessage
            - XMessageManager
            - XMessageManager.SendMessage()
            - XMessageManager.BroadcastMessage()
        """
        xlogif.LogWarning('Default impl of the callback for processing of external messages, nothig to do.')
        return ETernaryCallbackResultID.STOP
    # --------------------------------------------------------------------------
    #END 2) API to be overridden when sub-classing
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # 3) API start/stop
    # ------------------------------------------------------------------------------
    def Start(self, *args_, **kwargs_) -> bool:
        """
        Request to start this task.

        Passed in positional and/or keyword arguments (if any) will be passed
        to the 3-PhXF callbacks below:
            - SetUpXTask()
              if this instance is configured to have a setup-phase,
            - RunXTask()
              if this instance is not configured to have a setup-phase.
              Then, whenever this callback is entered, the property
              'XTask.isFirstRunPhaseIteratoion' shall be used to either process
              the arguments passed to accordingly or just ignore them.

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
              the requester will be blocked until task's 3-PhXF is finished.
            - For asynchronous tasks the operation is non-blocking, it returns
              right before task's 3-PhXF is going to take place. That is, the
              actual execution of such a task takes asynchronously place.
            - See also section 'Asymmetric task state transition' in description
              of this class above.

        See:
        -----
            - XTask
            - XTask.isStarted
            - XTask.isFirstRunPhaseIteratoion
        """
        return _XTaskBase._Start(self, *args_, **kwargs_)


    def Stop(self) -> bool:
        """
        Request to stop this task.

        Returns:
        ----------
            True if the operation succeeds, False otherwise.

        Note:
        ------
            - Requests to stop tasks which are in a transitional state of
              termination (i.e. stopping or aborting) already are ignored by
              the framework.
            - A request to stop a task is always a non-blocking, instruction to
              stop the task. It simply notifies the task about the stop request
              and returns.
            - See also section 'Asymmetric task state transition' in description
              of this class above.

        See:
        -----
            - XTask
            - XTask.isRunning
            - XTask.isDone
            - XTask.isFailed
            - XTask.isTerminating
        """
        return _XTaskBase._Stop(self, True)


    def Join(self, maxWaitTime_: Union[int, float] =None) -> bool:
        """
        Request to join this task, thus waiting for its termination.

        Parameters:
        -------------
            - maxWaitTime_ :
              if None it will wait forever. Otherwise, it will wait for the
              specified amount of time (milliseconds for int values or seconds
              for float values) before the operation returns.

        Returns:
        ----------
            True if the operation succeeds, False otherwise.

        Note:
        ------
            - Requests to join tasks which are terminated (i.e. stopped or
              aborted) already are ignored by the framework.
            - Attempts to join a task from within its own 3-PhXF is ignored by
              the framework.
            - Otherwise, the requester is blocked (for the specified wait time)
              until the task is terminated.
            - See also section 'Asymmetric task state transition' in description
              of this class above.

        See:
        -----
            XTask
        """
        return _XTaskBase._Join(self, maxWaitTime_)


    def DetachFromFW(self):
        """
        Request to detach this task from the framework.

        Note:
        ------
            - Main purpose of detaching tasks from the framework is releasing
              application or system resources used for them.
            - Detaching is always done automatically by the framework upon
              termination of tasks.
            - Detaching a task from the framework by intention and before its
              termination, is much like requesting the framework to stop the
              task (if applicable).
            - As soon as a task is detached from the framework, it won't be
              able to use all of its reqular API anymore. Its task state will
              be set in accordance to the state right after internal handling
              of request, e.g. 'stopped' or 'stopping', and not updated anymore.
            - See also section 'Asymmetric task state transition' in description
              of this class above.

        See:
        -----
            - XTask
            - XTask.Stop()
        """
        _XTaskBase._DetachFromFW(self)
    # ------------------------------------------------------------------------------
    #END 3) API start/stop
    # ------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # 4) API task state and properties
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
            - An instance of this class correctly constructed is always attached
              to the framework until it is requested to detach from framework.
            - See also section 'Asymmetric task state transition' in
              description of this class above.

        See:
        -----
            - XTask
            - XTask.__init__()
            - XTask.DetachFromFW()
        """
        return self._isAttachedToFW


    @property
    def isDetachedFromFW(self) -> bool:
        """
        Getter property for task's state of being 'detached to framework'.

        Returns:
        ----------
            True if this instance is dettached from the framework,
            False otherwise.

        Note:
        ------
            See also section 'Asymmetric task state transition' in description
            of this class above.

        See:
        -----
            - XTask
            - XTask.DetachFromFW()
        """
        return not self._isAttachedToFW


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
              the task is succeeded.
            - Note, however, the fact of being 'started' does not necessarily
              imply any specific, subsequent task state during the lifecycle
              of that task, e.g. 'running'.
            - But, for all subsequent task states, it is always considered
              'started'.
            - See also section 'Asymmetric task state transition' in description
              of this class above.

        See:
        -----
            - XTask
            - XTask.Start()
            - XTask.isRunning
        """
        return self._isStarted


    @property
    def isRunning(self) -> bool:
        """
        Getter property for task's state of being 'running'.

        Returns
        ----------
            True if this instance is currently running, False otherwise.

        Note:
        ------
            - A task is in 'running' state as soon as it enters its setup phase
              (if configured so) or its run phase.
            - A task is no longer in 'running' state once it reaches its
              transitional state 'terminating', especially when leaving its
              (cyclic) run phase.
            - Thus, tasks are particularly not nunning anymore whenever they
              enter their teadown phase (if configured).
            - Also, as soon as a submitted fatal error becomes qualified, the
              affected task instance leaves its 'runnig' state (see error
              handling described in class XTaskError).
            - See also section 'Asymmetric task state transition' in description
              of this class above.

        See:
        -----
            - XTask
            - XTaskError
            - XTask.SetUpXTask()
            - XTask.RunXTask()
            - XTask.TearDownXTask()
            - XTask.ProcessExternalMessage()
            - XTask.isTerminating
        """
        return self._isRunning


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
            See also section 'Asymmetric task state transition' in description
            of this class above.

        See:
        -----
            - XTask
            - XTask.isFailed
        """
        return self._isDone


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
            See also section 'Asymmetric task state transition' in description
            of this class above.

        See:
        -----
            - XTask
            - XTask.isDone
        """
        return self._isFailed


    @property
    def isTerminated(self) -> bool:
        """
        Getter property for task's state of being 'terminated'.

        Returns:
        ----------
            True if this instance has reached one of its final states 'done'
            or 'failed', False otherwise.

        Note:
        ------
            See also section 'Asymmetric task state transition' in description
            of this class above.

        See:
        -----
            - XTask
            - XTask.isDone
            - XTask.isFailed
        """
        return self.isDone or self.isFailed


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
            See also section 'Asymmetric task state transition' in description
            of this class above.

        See:
        -----
            - XTask
            - XTask.isRunning
            - XTask.isStopping
            - XTask.isAborting
        """
        return self.isStopping or self.isAborting


    @property
    def isStopping(self) -> bool:
        """
        Getter property for task's state of being 'stopping'.

        Returns:
        ----------
            True as soon as this instance leaves its 'running' state without
            having caused any fatal eroor, False otherwise.

        Note:
        ------
            See also section 'Asymmetric task state transition' in description
            of this class above.

        See:
        -----
            - XTask
            - XTask.isRunning
            - XTask.isAborting
        """
        return self._isStopping


    @property
    def isAborting(self) -> bool:
        """
        Getter property for task's state of being 'aborting'.

        Returns:
        ----------
            True as soon as this instance leaves its 'running' state with
            having caused a qualified fatal eroor, False otherwise.

        Note:
        ------
            See also section 'Asymmetric task state transition' in description
            of this class above.

        See:
        -----
            - XTask
            - XTask.isRunning
            - XTask.isStopping
        """
        return self._isAborting


    @property
    def xtaskUniqueID(self) -> int:
        """
        Getter property for task's unique ID.

        Returns:
        ----------
            Auto-generated unique ID of this instance if started,
            None otherwise.

        See:
        -----
            XTask.Start()
        """
        return self._executableUniqueID


    @property
    def xtaskName(self) -> str:
        """
        Getter property for task's (unique) name.

        Returns:
        ----------
            Auto-generated string object representing unique name of this
            instance if started, task's alias name otherwise.

        See:
        -----
            - XTask.Start()
            - XTask.xtaskAliasName
        """
        return self._executableName


    @property
    def xtaskAliasName(self) -> str:
        """
        Getter property for task's alias name.

        Returns:
        ----------
            Alias name assigned to the task profile of this instance.

        See:
        -----
            - XTask.__init__()
            - XTask.xtaskProfile
            - XTaskProfile.aliasName
        """
        return self._xtaskAliasName


    @property
    def xtaskProfile(self) -> XTaskProfile:
        """
        Getter property for the task profile of this instance.

        Returns:
        ----------
            If attached to framework, reference to the read-only copy of the
            task profile argument passed to the constructor when the instance
            is created, reference to that argument itself otherwise.

        See:
        -----
            - XTaskProfile
            - XTask.__init__()
        """
        return self._xtaskProfile
    # ------------------------------------------------------------------------------
    #END 4) API task state and properties
    # ------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # 5) API message handling
    # ------------------------------------------------------------------------------
    def TriggerExternalQueueProcessing(self) -> int:
        """
        Request to start processing of currently queued external message(s).

        For each currently queued external message this instance's callback
        method 'ProcessExternalMessage()' will be called accordingly.

        Returns:
        ----------
            If this task is attached to framework, then non-negative number of
            external messages processed (if any), -1 otherwise.

        Note:
        ------
            - Processing of external messages is triggered by the framework
              before executing next run phase cycle anyway.
            - Main purpose of this interface function is to enable tasks to
              process queued messages at their convenience on one hand, and to
              make tasks with single-cycle run phase are able to process
              messages delivered to them (if any) on the other hand.
            - The request will be ignored (returnning 0) if this task's external
              queue is blocking, or it is currently processing external/internal
              messages already.
            - See also both sections 'Configuration' and 'RTE modes' in
              description of this class above.

        See:
        -----
            - XTask
            - XTask.isAttachedToFW
            - XTask.ProcessExternalMessage()
        """
        return _XTaskBase._TriggerQueueProcessing(self, True)
    # ------------------------------------------------------------------------------
    #END 5) API message handling
    # ------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # 6) API error handling
    # ------------------------------------------------------------------------------
    @property
    def isErrorFree(self) -> bool:
        """
        Getter property for this task's current error state.

        Returns:
        ----------
            True if currently neither a user error nor a fatal error is
            associated with this instance, False otherwise.

        Note:
        ------
            Error handling is described in more detail in class XTaskError.

        See:
        -----
            - XTask.isFatalErrorFree
            - XTask.currentError
            - XTaskError
        """
        return self.currentError is None


    @property
    def isFatalErrorFree(self) -> bool:
        """
        Getter property for this task's current fatal error state.

        Returns:
        ----------
            True if currently no fatal eroor is associated with this instance,
            False otherwise.

        Note:
        ------
            Error handling is described in more detail in class XTaskError.

        See:
        -----
            - XTask.isErrorFree
            - XTask.currentError
            - XTaskError
        """
        curErr = self.currentError
        return (curErr is None) or not curErr.isFatalError


    @property
    def currentError(self) -> XTaskError:
        """
        Getter property for this task's current error.

        Returns:
        ----------
            An instance of class XTaskError if there is a (fatal) error
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
              current user/fatal error, submitting subsequent user/fatal errors
              for that task does not touch its current user/fatal error.
              In other words, unless current error is resolved (or cleared),
              it cannot be overwritten. This way, current error is kind of
              'very first error' of the respective phase (cycle) of 3-PhXF.
            - However, corresonding setter operatins (see below) may be used
              by a task to set or replace its current error.
            - Error handling is described in more detail in class XTaskError.

        See:
        -----
            - XTask.isErrorFree
            - XTask.isFatalErrorFree
            - XTask.ClearCurrentError()
            - XTask.SetError()
            - XTask.SetFatalError()
            - XTaskError
        """
        return self._currentError


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
            - Whether a current fatal error can be resolved or cleared by a
              task is briefly described in section 'Die mode' of class
              XTaskError which also provides a general description of
              framework's error handling.

        See:
        -----
            - XTask.currentError
            - XTaskError
        """
        return _XTaskBase._ClearCurrentError(self)


    def SetError(self, errorMsg_ : str):
        """
        Request to set or replace this task's current error to be a user error.

        If an attempt to clear current error (if any) passes, the operation will
        make current error associated to this task is set as requested.

        Parameters:
        -------------
            - errorMsg_ :
              message to be used for the user error to be associated to

        Note:
        ------
            - Request will be denied if not done out of the 3-PhXF of this task.
            - As opposed to submitting an error, setting (or replacing) current
              error of a task does not generate any (print) output.
            - Error handling is described in more detail in class XTaskError.

        See:
        -----
            - XTask.currentError
            - XTask.ClearCurrentError()
            - XTaskError
            - xlogif.LogError()
        """
        self._SetTaskError(False, errorMsg_, None)


    def SetErrorEC(self, errorMsg_ : str, errorCode_: int):
        """
        Request to set or replace this task's current error to be a user error.

        If an attempt to clear current error (if any) passes, the operation will
        make current error associated to this task is set as requested.

        Parameters:
        -------------
            - errorMsg_ :
              message to be used for the user error to be associated to
            - errorCode_ :
              error code to be used for the user error to be associated to

        Note:
        ------
            - Request will be denied if not done out of the 3-PhXF of this task.
            - As opposed to submitting an error, setting (or replacing) current
              error of a task does not generate any (print) output.
            - Error handling is described in more detail in class XTaskError.

        See:
        -----
            - XTask.currentError
            - XTask.ClearCurrentError()
            - XTaskError
            - xlogif.LogErrorEC()
        """
        self._SetTaskError(False, errorMsg_, errorCode_)


    def SetFatalError(self, errorMsg_ : str):
        """
        Request to set or replace this task's current error to be a fatal error.

        If an attempt to clear current error (if any) passes, the operation will
        make current error associated to this task is set as requested.

        Parameters:
        -------------
            - errorMsg_ :
              message to be used for the fatal error to be associated to

        Note:
        ------
            - Request will be denied if not done out of the 3-PhXF of this task.
            - As opposed to submitting an error, setting (or replacing) current
              error of a task does not generate any (print) output.
            - Error handling is described in more detail in class XTaskError.

        See:
        -----
            - XTask.currentError
            - XTask.ClearCurrentError()
            - XTaskError
            - xlogif.LogFatal()
        """
        self._SetTaskError(True, errorMsg_, None)


    def SetFatalErrorEC(self, errorMsg_ : str, errorCode_: int = None):
        """
        Request to set or replace this task's current error to be a fatal error.

        If an attempt to clear current error (if any) passes, the operation will
        make current error associated to this task is set as requested.

        Parameters:
        -------------
            - errorMsg_ :
              message to be used for the fatal error to be associated to
            - errorCode_ :
              error code to be used for the fatal error to be associated to

        Note:
        ------
            - Request will be denied if not done out of the 3-PhXF of this task.
            - As opposed to submitting an error, setting (or replacing) current
              error of a task does not generate any (print) output.
            - Error handling is described in more detail in class XTaskError.

        See:
        -----
            - XTask.currentError
            - XTask.ClearCurrentError()
            - XTaskError
            - xlogif.LogFatalEC()
        """
        self._SetTaskError(True, errorMsg_, errorCode_)
    # ------------------------------------------------------------------------------
    #END 6) API error handling
    # ------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # 7) API miscellaneous
    # ------------------------------------------------------------------------------
    @property
    def isFirstRunPhaseIteratoion(self) -> bool:
        """
        Getter property for this task's first iteration of the run phase.

        Returns:
        ----------
            True if the run phase of this instance has been entered with the
            interation of the run phase is currently running, False otherwise.

        Note:
        ------
            - The run phase of a task is given either through 'RunXTask()' or
              'ProcessExternalMessage()' in case of blocking external queue.
            - This property is especially useful whenever start argument(s)
              are passed to when the task is started.

        See:
        -----
            - XTask
            - XTask.Start()
            - XTask.RunXTask()
            - XTask.ProcessExternalMessage()
            - XTask.currentRunPhaseIteratoionNo
        """
        _curNo = self._curRunPhaseIteratoionNo
        return False if _curNo is None else _curNo == 0

    @property
    def currentRunPhaseIteratoionNo(self) -> int:
        """
        Getter property for this task's current iteration number of the run
        phase.

        Returns:
        ----------
            -1 if the run phase of this instance has not been entered yet,
            0-based current iteration number otherwise.

        Note:
        ------
            - The run phase of a task is given either through 'RunXTask()' or
              'ProcessExternalMessage()' in case of blocking external queue.
            - For task instance with single-cycle run phase the returned value
              is either -1 or 0.

        See:
        -----
            - XTask
            - XTask.Start()
            - XTask.RunXTask()
            - XTask.ProcessExternalMessage()
            - XTask.isFirstRunPhaseIteratoion
        """
        return self._curRunPhaseIteratoionNo
    # ------------------------------------------------------------------------------
    #END 7) API miscellaneous
    # ------------------------------------------------------------------------------
#END class XTask
