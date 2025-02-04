# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xprocess.py
#
# Copyright(c) 2024 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from typing import Union

from xcofdk.fwcom.xmpdefs import ChildProcessResultData

from xcofdk._xcofw.fw.fwssys.fwmp.apiimpl.xprocessbase import _XProcessBase


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class XProcess(_XProcessBase):
    """
    This class represents the heavy-weight counterpart of class XTask.

    Instances of this class are child processes, basically constructed by
    passing a callable object. Later, they can be started for parallel execution
    with the launching task continues its own exection as usual.

    For quick orientation and guidance on by when to use what, the interface is
    arranged in logical, context-driven subsets each labeled by a comment block
    of the form:
        >>> # --------------------------------------------------------------
        >>> # title of interface subset
        >>> # --------------------------------------------------------------

    Currently available interface subsets of class XProcess are as follows:
        1) constructor / initializer
        2) API basic process properties
        3) API start/stop
        4) API process state

    Sections below explain terms, definitions and related concepts of the
    framework dealing with parallel processes.


    Multiprocessing (MP):
    -----------------------
    refers to framwork's subsystem and capability to create and start new,
    processes on one hand, while enabling applications to communicate with
    other processes (probably already existing and running) on the other hand.

    In general, with regard to its logical and/or technical purpose, a process
    may be:
        - an instance of this class created and started from within
          a running instance of the framework using Python's standard library
          'multiprocessing' (and its relted class 'Process').

          Such a process is either a forked or a spawned child process (see
          start methods below), often as a preferred option for parallel
          execution of a so-called CPU-bound piece of code.

        - an arbitrary process (or program) running either on the host machine
          or on a remotely connected machine over network. Note that such a
          process is assumed to be any possible single- or multithreaded
          application. It especially can be another running instance of XCOFDK,
          or a spawned child process using Python's library 'subprocess'.

          In this case framework's focus is rather shifted to its interface for
          process communication which is part of the subsystem messaging, too.
          That is, a process which is a messaging endpoint needs to be provided
          by a unique identifier only, but not necessarily represented as a
          process object (of some specific class, e.g. XProcess).


    Interface of MP:
    -----------------
    as indicated above, MP-related interface of the framework is given by:
        - process communication:
          covered by the subsystem of messaging explained in class description
          of XMessageManager,

        - child processes:
          are provided as instances of class XProcess as well as thier
          management and error handling.

      Representing an abstraction of another type of executable artifacts (also
      refered to as 'host processes' provided by the host programming language
      or operating system) class XProcess is designed to have a similar
      look-and-feel as given for class XTask enabling applications to a uniform
      interfacing as much as possible and feasible.

      However, class XProcess as presented here is not complete yet. It is
      rather considered a kickoff version. Especially the supplementary
      interfaces related to both management and in-depth error handling are
      part of work still in progress. Same is true for restrictions related
      to limited RTE modes (see XTask).


    Process start method:
    ------------------------
    refers to the mechanism Python's MP library 'multiprocessing' uses to start
    child processes, explained in the respective section of the official
    documentation page:
        - Contexts and start methods
          https://docs.python.org/3/library/multiprocessing.html#contexts-and-start-methods

    Process start methods supported by Python's MP are:
        - spawn
        - fork
        - forkserver

    with the related getter and setter functions of the library are:
        - multiprocessing.get_start_method()
        - multiprocessing.set_start_method()

    It is important to notice that the process start method shall be set only
    once by program's main module (named '__main__') as pointed out in the
    official documentaton, see:
        - https://docs.python.org/3/library/multiprocessing.html#multiprocessing.set_start_method

    Hence, framework considers setting of the desired process start method as
    an issue solely to be done by applications, it never changes its current
    value returned by the abovementioned getter function. Moreover, as soon as
    a change of the process start method is detected, (subsequent) requests to
    create new instances of class XProcess will be refused by the framework for
    the rest of the life-cycle at hand.

    Finally, with regard to a child process created and started via interface of
    MP (expained above) of the framework (acting as its parent process, then),
    awareness of three important aspects of child processes is necessary:
        - threading
        - termination
        - performance


    Threading of child processes:
    --------------------------------
    unless intended for parallel execution of a (CPU-bound) piece of code, they
    also may be arranged as ordinary multithreaded programs. Hence, It is
    application's responsibility to ensure that such a threaded child process in
    connection with the chosen process start method (see above) does not end up
    in potential deadlocks.

    This is especially true for forked child processes classified as 'unsafe
    for multithreading' as they inherit all ressources (including lock objects)
    of the parent process by making use of (OS-dependent) function 'os.fork()'
    for the implementation of their instantiation and start, see:
        - https://docs.python.org/3/library/os.html#os.fork


    Termination of child processes:
    --------------------------------
    if not terminated yet, attempts to terminate running child processes (from
    within the parent process) become a critical issue, especially if a child
    process is performing some long-term computation right now, or even worse
    if it is stuck in some deadlock(s).

    As the framework is commited to both reliability and responsiveness at any
    time, this issue is of utmost importance, especially if requested to do so
    by the application, or when shutting down (see sections 'LC management' and
    'Coordinated shutdown sequence' of class description of XTaskError).

    Therefore, regardless of the mechanism picked out by the framework to
    initate the termination of a running/stuck child process, the general
    approach follows the pattern of either request-reply (as for tasks) or
    fire-and-forget.

    All in all, the process of both stopping and shuting down a child process
    is equippped with the so-called 'provision for non-daemonic' child
    processes meaning:
        a) child processes, i.e. instances of class XProcess, are not
           daemonic, hence they are not auto-terminated upon termination of
           the parent process,

        b) they are rather ordinary processes allowed to have their own child
           processes,

        c) their termination (if necessary) by the framework is done on the
           aforementioned managed basis limited to child process started by
           the framework only,

        d) they are responsible for termination of their own child processes
           (if any) to avoid the issue of orphaned children.


    Performance of child processes:
    ----------------------------------
    measured as the cost of the consumed CPU time for execution, performance of
    child processes is out of the functional socpe of the framework, too. Its
    related interface (and implementation) is primarily responsible for creation
    and tracking of their execution state in a way it doesn't have a worsening
    impact on the performance and responsiveness of the parent process, that is
    the framework itself.


    Note:
    ------
        - Both design and implementation of this class is not completed yet,
          see section 'Interface of MP' above.
        - Framework's runtime envioronment, especially its task model, is
          described in class description of XTask.
        - Framework's messaging subsystem is described in class description of
          XMessageManager.
        - For more detail regarding the standard library 'multiprocessing'
          refer to the official documentation page below:
            https://docs.python.org/3/library/multiprocessing.html
        - For more detail regarding the standard library 'subprocess'
          refer to the official documentation page below:
            https://docs.python.org/3/library/subprocess.html

    See:
    -----
        - XMPUtil
        - XTask
        - XMessageManager
        - XTaskError
    """


    __slots__ = []


    # --------------------------------------------------------------------------
    # 1) constructor / initializer
    # --------------------------------------------------------------------------
    def __init__( self, target_, name_ : str =None, args_ : tuple =None, kwargs_ : dict =None, maxResultByteSize_ : int =None):
        """
        Constructor (initializer) of instances of this class.

        When created, an instance of this class is considered attached to the
        framework. Unless detached from the framework later, it is always
        associated with its underlying host process object, see Python's class
        'multiprocessing.Process':
            - https://docs.python.org/3/library/multiprocessing.html#multiprocessing.Process

        Parameters:
        -------------
            - target_ :
              callable object to be invoked when this instance is started.

              Its signature must take an instance of class 'ChildProcessResultData'
              as its first formal parameter, optionally followd by postional
              and/or keywork arguments, with the general form depicted below:
                  >>> def MyProcessTarget(procResData_ : ChildProcessResultData, *args, **kwargs):
                  >>>     pass
            - name_ :
              name of the process to be created.
              If not supplied, that is set to None, it will be auto-generated,
              see:
                  https://docs.python.org/3/library/multiprocessing.html#multiprocessing.Process.name
            - args_ :
              positional arguments (if any) to be passed to the callable target
              when started.
            - kwargs_ :
              keyword arguments (if any) to be passed to the callable target
              when started.
            - maxResultByteSize_ :
              maximum length of the byte stream representing the serialization
              of a data object (if any) assigned to the abovementioned instance
              of class 'ChildProcessResultData' as user-defined result data.

              If specified, it must be a value larger than or equeal to 4.
              Otherwise, it defaults to 1024 which is large enough for a byte
              stream occupying a list of up to 100 integer values equal to the
              built-in constant 'sys.maxsize' (i.e. 9223372036854775807).

              For more detail refer to the respecitve setter property of class
              ChildProcessResultData.

        Note:
        ------
            - Abovementioned instance of class 'ChildProcessResultData' passed
              to the callable target when started is designed to enable child
              processes to supply their specific execution result, i.e. exit
              code and/or data. Once terminated, that result is provided to
              applications via corresponding getter property.
            - Instances of this class represent ordinary (child) processes
              allowed to create and start their own child processes when
              started, see 'non-daemonic provision' explained in section
              'Termination of child  processes' of class description of
              XProcess above.
            - More detail available in abovementioned class description.

        See:
        -----
            - XProcess.isAttachedToFW
            - XProcess.xprocessResult
            - XProcess.xprocessName
            - XProcess.DetachFromFW()
            - XProcess.Start()
            - ChildProcessResultData.resultData
            - EXPMPreDefinedID.DefaultUserDefinedResultDataMaxSize
        """
        super().__init__(target_, name_=name_, args_=args_, kwargs_=kwargs_, maxDataSize_=maxResultByteSize_)
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
        return _XProcessBase.__str__(self)


    # ------------------------------------------------------------------------------
    # 2) API basic process properties
    # ------------------------------------------------------------------------------
    @property
    def isAttachedToFW(self):
        """
        Getter property for process' state of being 'attached to framework'.

        Returns:
        ----------
            True if this instance is (still) attached to the framework, False
            otherwise.

        Note:
        ------
            - An instance of this class correctly constructed is always attached
              to the framework until it is requested to detach from framework.

        See:
        -----
            - XProcess.__init__()
            - XProcess.DetachFromFW()
        """
        return self._isAttachedToFW


    @property
    def xprocessPID(self) -> int:
        """
        Getter property for PID of this instance.

        Returns:
        ----------
            PID of the associated host process of this instance if started,
            None otherwise.

        See:
        -----
            XProcess.Start()
        """
        return self._xprocessPID


    @property
    def xprocessName(self) -> str:
        """
        Getter property for the name of this instance.

        Returns:
        ----------
            (auto-generted) name of this instance.

        See:
        -----
            XProcess.__init__()
        """
        return self._xprocessName


    @property
    def xprocessResult(self) -> ChildProcessResultData:
        """
        Getter property for the application specific result of execution.

        Returns:
        ----------
            an object representing the application specific result of the
            execution of this instance.

        See:
        -----
            - XProcess.__init__()
            - XProcess.Start()
            - ChildProcessResultData.exitCode
            - ChildProcessResultData.resultData
        """
        return self._xprocessResult


    @property
    def xprocessExitCode(self) -> int:
        """
        Getter property for exit code of this instance.

        Returns:
        ----------
            if terminated 0 upon successful termination, a positive integer
            value otherwise. If not terminated yet, None is returned.

        Note:
        ------
            - Exit code values supplied by the callable target of a child
              process are expected to be of the range [0..80].
            - Values larger than 80 are reserved exit codes interally used by
              the framework.

        See:
        -----
            - XProcess.isTerminated
            - XProcess.__init__()
            - XProcess.Start()
            - ChildProcessResultData.exitCode
        """
        return self._xprocessExitCode
    # ------------------------------------------------------------------------------
    #END 2) API basic process properties
    # ------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # 3) API start/stop
    # ------------------------------------------------------------------------------
    def Start(self) -> bool:
        """
        Request to start this instance.

        It starts the host process associated to this instance making the
        callable target passed to the constructor is called.

        Returns:
        ----------
            False if this instance is detached from the framework, or if it has
            been started already, or if the start of the associated host process
            failed, True otherwise.

        Note:
        ------
            - This operation is not available to applications in limited RTE
              modes, refer to the respective section in class description of
              XTask.

        See:
        -----
            - XProcess.isAttachedToFW
            - XProcess.isStarted
            - XProcess.isTerminated
            - XProcess.__init__()
            - XProcess.DetachFromFW()
            - XTask
        """
        return _XProcessBase._Start(self)


    def Join(self, maxWaitTime_: Union[int, float] =None):
        """
        Request to join this innstance, thus waiting for its termination.

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
            - This operation is not available to applications in limited RTE
              modes, refer to the respective section in class description of
              XTask.
            - The optional parameter 'maxWaitTime_' above is not supported yet.
            - Requests to join a child process which is not started yet or
              terminated already are ignored by the framework.

        See:
        -----
            - XProcess.isAttachedToFW
            - XProcess.isStarted
            - XProcess.isTerminated
        """
        _XProcessBase._Join(self)


    def DetachFromFW(self):
        """
        Request to detach this instance from the framework.

        Note:
        ------
            - This operation is not available to applications in limited RTE
              modes, refer to the respective section in class description of
              XTask.
            - Main purpose of detaching child processes from the framework is
              releasing application or system resources used for them.
            - Detaching is always done automatically by the framework upon
              termination of child processes.
            - Detaching a child process from the framework by intention and
              before its termination, is much like requesting the framework to
              stop it (if applicable).
            - As soon as a child process is detached from the framework, it
              won't be able to use all of its reqular API anymore. Its execution
              state will be set in accordance to the state right after internal
              handling of request, e.g. 'stopped' or 'stopping', and not updated
              anymore.

        See:
        -----
            - XProcess.isAttachedToFW
        """
        _XProcessBase._DetachFromFW(self)
    # ------------------------------------------------------------------------------
    #END 3) API start/stop
    # ------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # 4) API process state
    # ------------------------------------------------------------------------------
    @property
    def isStarted(self) -> bool:
        """
        Getter property for the state of being 'started'.

        Returns:
        ----------
            True if this instance has been started, False otherwise.

        Note:
        ------
            - A child process is considered 'started', as soon as a request to
              start it is succeeded.
            - Note, however, the fact of being 'started' does not necessarily
              imply any specific, subsequent state during the lifecycle
              of that child process, e.g. 'running'.
            - But, for all subsequent process states, it is always considered
              'started'.

        See:
        -----
            - XProcess.isRunning
            - XProcess.Start()
        """
        return self._isStarted


    @property
    def isRunning(self) -> bool:
        """
        Getter property for the state of being 'running'.

        Returns:
        ----------
            True if this instance is currently running, False otherwise.

        Note:
        ------
            - A child process is considered 'running', as soon as a request to
              start it is succeeded.
            - However, work is in progress to have this state is set right
              before the callable taget passed to the constructor is called
              first. As a matter of backward compatibility, this will be
              announced accordingly.

        See:
        -----
            - XProcess.isTerminated
            - XProcess.Start()
        """
        return self._isRunning


    @property
    def isDone(self) -> bool:
        """
        Getter property for the state of being 'done'.

        Returns:
        ----------
            True if this instance has finished its execution upon normal
            termination indicated by an exit code of 0, False otherwise.

        See:
        -----
            - XProcess.isFailed
            - XProcess.isTerminated
            - XProcess.xprocessExitCode
        """
        return self._isDone


    @property
    def isFailed(self) -> bool:
        """
        Getter property for the state of being 'failed'.

        Returns:
        ----------
            True if this instance has finished its execution upon anormal
            termination indicated by an exit code other than 0, False otherwise.

        See:
        -----
            - XProcess.isDone
            - XProcess.isTerminated
            - XProcess.xprocessExitCode
        """
        return self._isFailed


    @property
    def isTerminated(self) -> bool:
        """
        Getter property for the state of being either 'done' or 'failed'.

        As long as a child process is in stste 'running', this property will
        resolve to False.

        Returns:
        ----------
            True if this instance has finished its execution, False otherwise.

        See:
        -----
            - XProcess.isDone
            - XProcess.isFailed
            - XProcess.isRunning
            - XProcess.xprocessExitCode
        """
        return self._isTerminated
    # ------------------------------------------------------------------------------
    #END 4) API process state
    # ------------------------------------------------------------------------------
#END class XProcess
