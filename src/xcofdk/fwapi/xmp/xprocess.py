# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xprocess.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from typing import Any
from typing import Union

from .xprocessxcp        import PTException
from .xprocessxcp        import PTWrappedException
from xcofdk.fwcom        import EXmpPredefinedID
from xcofdk.fwcom.fwdefs import ERtePolicyID

from _fw.fwssys.fwmp.api.xprocagent import _XProcessAgent


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class XProcess:
    """
    This class represents the heavy-weight counterpart of class XTask for
    concurrancy or multitasking.

    Instances of this class are child processes, basically constructed by
    passing a callable object. Later, they can be started for parallel execution
    with the launching task continues its own exection as usual.

    For quick orientation and guidance on by when to use which one, the
    interface is arranged in subsets each of them labeled in accordance to the
    given logical context by a comment block of the form:
        >>> # --------------------------------------------------------------
        >>> # SecNo) title of interface subset
        >>> # --------------------------------------------------------------

    Currently available interface subsets of class XProcess are as follows:
        1) c-tor / built-in
        2) API basic process properties
        3) API start, stop etc.
        4) API process state

    Note:
    ------
        Any request to the API of this class will be (noiselessly) discarded,
        if the subsystem of multiprocessing, i.e. 'xmp', is disabled via
        framework's RTE configuration.

    See:
    -----
        - RtePolicyDisableSubSystemMultiProcessing()
        >>> ERtePolicyID.eDisableSubSystemMultiProcessing


    Deprecated API:
    ----------------
    Starting with XCOFDK-py v3.0 below API functions/properties (formerly part of
    the API of this class) are deprecated and not available anymore:
        >>> @property
        >>> def xprocessPID(self):
        >>>     return self.processPID
        >>>
        >>> @property
        >>> def xprocessName(self):
        >>>     return self.processName
        >>>
        >>> @property
        >>> def xprocessExitCode(self):
        >>>     return self.processExitCode
        >>>
        >>> @property
        >>> def xprocessResult(self):
        >>>     return self.processSuppliedData
    """


    # --------------------------------------------------------------------------
    # 1) c-tor / built-in
    # --------------------------------------------------------------------------
    def __init__( self, target_, aliasName_ : str =None, name_ : str =None, maxSuppliedDataSize_ : int =None):
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
              callable object to be executed by the associated host process
              when this instance is started.

              Its signature may optionally carry postional and/or keywork
              arguments, with the general form depicted below:
                  >>> def MyProcessCBTgt(*args, **kwargs):
                  >>>     #...
            - aliasName_ :
              if specified an arbitrary, non-empty and printable string literal
              without spaces which optionally may have a trailing '_',
              otherwise 'Prc_' will be auto-assigned.

              Finally, if the alias name has a trailing '_', the framework will
              turn it to a unique alias name by appending the unique instance
              number of the instance to be created.
            - name_ :
              name of the host process to be created and associated with.
              If not supplied, that is set to None, it will be auto-generated,
              see:
                  https://docs.python.org/3/library/multiprocessing.html#multiprocessing.Process.name
            - maxSuppliedDataSize_ :
              default value used as maximum length of a byte stream representing
              the serialization of a data object (if any) returned by 'target_'.

              If specified, it must be a value larger than or equeal to 4.

              Otherwise, it defaults to EXmpPredefinedID.DefaultSuppliedDataMaxSize
              (currently set to 10240, i.e. 10 KB) which is large enough for a
              byte stream occupying a list of up to 1022 integer values equal to
              the built-in constant 'sys.maxsize' (i.e. 9223372036854775807).

        Note:
        ------
            - An attempt to create an instance of this class before the
              framework is started will be ignored with a user error is
              submitted accordingly.
            - Unless requested to do so, the framework never terminates a
              running child process.
            - Instances of this class represent ordinary child processes allowed
              to create and start their own child processes when started.
            - This way they represent so-called 'non-daemonic' processes.
              As such, child processes are responsible for termination of
              child processes they have started themselves to avoid the issue
              of orphaned processes upon termination of the parent process.

        See:
        -----
            >>> XProcess.isAttachedToFW
            >>> XProcess.processName
            >>> XProcess.processSuppliedData
            >>> XProcess.DetachFromFW()
            >>> XProcess.Start()
            >>> EXmpPredefinedID.DefaultSuppliedDataMaxSize
        """
        self.__a = _XProcessAgent(target_, aliasn_=aliasName_, name_=name_, maxSDSize_=maxSuppliedDataSize_)


    def __str__(self):
        """
        Returns:
        ----------
            A nicely printable string representation of this instance.
        """
        return str(self.__a)
    # --------------------------------------------------------------------------
    #END 1) c-tor / built-in
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # 2) API basic process properties
    # ------------------------------------------------------------------------------
    @property
    def isAttachedToFW(self):
        """
        Returns:
        ----------
            True if this instance is (still) attached to the framework,
            False otherwise.

        Note:
        ------
            - An instance of this class correctly constructed is always attached
              to the framework until it is requested to be detached from the
              framework.

        See:
        -----
            >>> XProcess.isDetachedFromFW
            >>> XProcess.__init__()
            >>> XProcess.DetachFromFW()
        """
        return self.__a._isAttachedToFW


    @property
    def isDetachedFromFW(self):
        """
        Returns:
        ----------
            True if this instance is (no longer) attached to the framework,
            False otherwise.

        Note:
        ------
            - An instance of this class correctly constructed is always attached
              to the framework until it is requested to be detached from the
              framework.

        See:
        -----
            >>> XProcess.isAttachedToFW
            >>> XProcess.__init__()
            >>> XProcess.DetachFromFW()
        """
        return not self.__a._isAttachedToFW


    @property
    def aliasName(self) -> str:
        """
        Returns:
        ----------
            (Auto-generted) alias name of this instance.

        See:
        -----
            >>> XProcess.__init__()
        """
        return self.__a._xprocessAliasName


    @property
    def processPID(self) -> int:
        """
        Returns:
        ----------
            PID of the associated host process of this instance if started,
            None otherwise.

        See:
        -----
            >>> XProcess.Start()
        """
        return self.__a._xprocessPID


    @property
    def processName(self) -> str:
        """
        Returns:
        ----------
            (Auto-generted) name of this instance.

        See:
        -----
            >>> XProcess.__init__()
        """
        return self.__a._xprocessName


    @property
    def processExitCode(self) -> int:
        """
        Getter property for exit code of this instance.

        Returns:
        ----------
            - None if not started or not terminated yet,
            - 0 upon successful termination,
            - an integer value otherwise.

        Note:
        ------
            The exit code value of a failed child process indicates an error
            code:
                - Unless terminated due to the 'SystemExit' exception caught
                  by the child process (or otherwise issued termination
                  signal), the exit code is always a positive integer value.
                - Otherwise, it is the negation of the integer value of a
                  signal, e.g. 'SIGTERM', which caused the termination.

        See:
        -----
            >>> XProcess.isDone
            >>> XProcess.isFailed
            >>> XProcess.isTerminated
            >>> XProcess.processException
            >>> XProcess.processExitCodeAsStr
            >>> XProcess.__init__()
            >>> XProcess.Start()
            >>> XProcess.Terminate()
        """
        return self.__a._xprocessExitCode


    @property
    def processExitCodeAsStr(self) -> Union[str, None]:
        """
        Returns:
        ----------
            The exit code (if available) of this child process as a string object,
            None otherwise.

        See:
        -----
            >>> XProcess.processExitCode
        """
        return self.__a._xprocessExitCodeAsStr


    @property
    def processSuppliedData(self) -> Any:
        """
        Getter property for the application-specific result of execution.

        Returns:
        ----------
            The (application-specific) data (if any) supplied by the child
            process through the returned value of the target callback function
            passed to the constructor of this instance.

        Note:
        ------
            - Child processes may supply a byte stream as the result of their
              execution, too.
            - If so, this property will return that byte stream as is.

        See:
        -----
            >>> XProcess.__init__()
            >>> XProcess.Start()
        """
        return self.__a._xprocessSuppliedData


    @property
    def processException(self) -> Union[PTException, PTWrappedException, None]:
        """
        Returns:
        ----------
            - None if exception tracking of child processes is disabled via
              RTE configuration,
            - None if this instance is not started,
            - None if this instance is terminated upon successful termination,
            - None if no exception was raised while execution of the target
              callback function passed to the constructor of this instance,
            - that raised exception otherwise.

        See:
        -----
            - RtePolicyDisableExceptionTrackingOfChildProcesses()
            >>> PTException
            >>> PTWrappedException
            >>> XProcess.isDone
            >>> XProcess.isFailed
            >>> XProcess.isTerminated
            >>> XProcess.__init__()
            >>> XProcess.Start()
            >>> ERtePolicyID.eDisableExceptionTrackingOfChildProcesses
        """
        return self.__a._xprocessException
    # ------------------------------------------------------------------------------
    #END 2) API basic process properties
    # ------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # 3) API start, stop etc.
    # ------------------------------------------------------------------------------
    def Start(self, *args_, **kwargs_) -> bool:
        """
        Request to start this instance.

        It starts the host process associated to this instance making the
        callable target passed to the constructor is called.

        Parameters:
        -------------
            - args_ :
              positional arguments (if any) to be passed to the callable target
              when started.
            - kwargs_ :
              keyword arguments (if any) to be passed to the callable target
              when started.

        Returns:
        ----------
            False if this instance is detached from the framework, or if it has
            been started already, or if the start of the associated host process
            failed, True otherwise.

        Note:
        ------
            - This operation is not available to applications in limited RTE
              modes.

        See:
        -----
            >>> XProcess.isAttachedToFW
            >>> XProcess.isStarted
            >>> XProcess.isTerminated
            >>> XProcess.__init__()
            >>> XProcess.DetachFromFW()
        """
        return self.__a._Start(*args_, **kwargs_)


    def Join(self, maxWaitTime_: Union[int, float, None] =None) -> bool:
        """
        Request to join this innstance, thus synchronously waiting for its
        termination.

        Parameters:
        -------------
            - maxWaitTime_ :
              if None it will wait forever. Otherwise, it will wait for the
              specified amount of time (milliseconds for integer values or
              seconds for floating-point values) before the operation returns.

        Returns:
        ----------
            True if the operation succeeds, False otherwise.

        Note:
        ------
            - This operation is not available to applications in limited RTE
              modes.
            - Requests to join a child process which is detached from the
              framework or not started yet or terminated already will be ignored.

        See:
        -----
            >>> XProcess.isAttachedToFW
            >>> XProcess.isStarted
            >>> XProcess.isTerminated
        """
        return self.__a._Join(maxWTime_=maxWaitTime_)


    def Terminate(self):
        """
        Request to terminate this innstance.

        The framework will ask the associated host process to terminate.
        Also, it will wait for a short, pre-defined max. amount of time as long
        as the host process is not terminated.

        Finally, this instance is detached from the framwork with its process
        state is updated to the last available one before return.

        Note:
        ------
            - This operation is available to applications even in limited RTE
              modes.
            - Unless requested to do so, the framework never terminates child
              processes.
            - Requests to terminate a child process which is detached from the
              framework or not started yet or terminated already will be ignored.

        See:
        -----
            >>> XProcess.isAttachedToFW
            >>> XProcess.isStarted
            >>> XProcess.isTerminated
            >>> XProcess.isTerminatedByCmd
            >>> XProcess.DetachFromFW()
        """
        self.__a._Terminate()


    def DetachFromFW(self):
        """
        Request to detach this instance from the framework.

        Note:
        ------
            - This operation is available to applications even in limited RTE
              modes.
            - Main purpose of detaching child processes from the framework is
              releasing application or system resources used for them.
            - Detaching is always done automatically by the framework upon
              termination of child processes.
            - Detaching a child process from the framework by intention and
              before its termination, is much like immediately releasing all
              resources used for it.
            - As soon as a child process is detached from the framework, it
              won't be able to use all of its reqular API anymore. Its execution
              state will be set in accordance to the state right after internal
              handling of the request, e.g. 'done' or 'running', and not updated
              anymore.

        See:
        -----
            >>> XProcess.isAttachedToFW
        """
        self.__a._DetachFromFW()
    # ------------------------------------------------------------------------------
    #END 3) API start, stop etc.
    # ------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # 4) API process state
    # ------------------------------------------------------------------------------
    @property
    def isStarted(self) -> bool:
        """
        Returns:
        ----------
            True if this instance has been started, False otherwise.

        Note:
        ------
            - A child process is considered 'started', as soon as a request to
              start it is succeeded.
            - However, the fact of being 'started' does not necessarily imply
              any specific, subsequent state during the lifecycle of that child
              process, e.g. 'running'.
            - But, for all subsequent process states, it is always considered
              'started'.

        See:
        -----
            >>> XProcess.isRunning
            >>> XProcess.Start()
        """
        return self.__a._isStarted


    @property
    def isRunning(self) -> bool:
        """
        Returns:
        ----------
            - False if this instance is not started yet,
            - False if the associated host process is not alive anymore or
              terminated already by providing an exit code,
            - False if this instance has been requested to terminate,
            - True otherwise.

        Note:
        ------
            - A child process is considered 'running', as soon as a request to
              start it is succeeded.

        See:
        -----
            >>> XProcess.isTerminated
            >>> XProcess.isTerminatedByCmd
            >>> XProcess.Start()
            >>> XProcess.Terminate()
        """
        return self.__a._isRunning


    @property
    def isDone(self) -> bool:
        """
        Returns:
        ----------
            True if this instance has finished its execution upon normal
            termination indicated by an exit code of 0, False otherwise.

        See:
        -----
            >>> XProcess.isFailed
            >>> XProcess.isTerminated
            >>> XProcess.processExitCode
        """
        return self.__a._isDone


    @property
    def isFailed(self) -> bool:
        """
        Returns:
        ----------
            True if this instance has finished its execution upon abnormal
            termination indicated by an exit code other than 0, False otherwise.

        See:
        -----
            >>> XProcess.isDone
            >>> XProcess.isTerminated
            >>> XProcess.processExitCode
        """
        return self.__a._isFailed


    @property
    def isTerminated(self) -> bool:
        """
        As long as a child process is in stste 'running', this property will
        resolve to False.

        Returns:
        ----------
            - False if this instance is not started yet,
            - False as long as this instance is in state 'running',
            - True otherwise.

        See:
        -----
            >>> XProcess.isStarted
            >>> XProcess.isDone
            >>> XProcess.isFailed
            >>> XProcess.isRunning
            >>> XProcess.isTerminatedByCmd
            >>> XProcess.processExitCode
            >>> XProcess.Terminate()
        """
        return self.__a._isTerminated


    @property
    def isTerminatedByCmd(self) -> bool:
        """
        Returns:
        ----------
            - False if this instance is not started yet,
            - False as long as this instance is in state 'running',
            - False if this instance is terminated already with or without
              having a request to terminate it by intention,
            - True after a request to terminate this instance by intention with
              the framework was not able to establish the exit code and/or the
              aliveness of the associated host process.

        See:
        -----
            >>> XProcess.isStarted
            >>> XProcess.isRunning
            >>> XProcess.isTerminated
            >>> XProcess.processExitCode
            >>> XProcess.Terminate()
        """
        return self.__a._isTerminatedByCmd
    # ------------------------------------------------------------------------------
    #END 4) API process state
    # ------------------------------------------------------------------------------
#END class XProcess
