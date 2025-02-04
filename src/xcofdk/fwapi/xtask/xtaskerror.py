# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xtaskerror.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from xcofdk._xcofw.fw.fwssys.fwcore.apiimpl.xtask.xtaskerrbase import _XTaskErrorBase
from xcofdk._xcofw.fw.fwssys.fwcore.logging.xcoexception       import _XTaskExceptionBase


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class XTaskError:
    """
    Instances of this class represent the high-level abstraction of the current
    error of a task, i.e. an instance of class XTask.

    Associating a task with an instance of this class is the result of a
    multilayered, multithreaded per-task error handling of the framework
    described below.


    Error handling:
    ----------------
    Following subsections are supposed to just give a brief presentation of
    related terms and concepts only, especially to avoid annoying repeat of
    the same matter over and over. An in-depth discussion is out of the scope
    of a source code documentation and would require a dedicated documentation.


    LC management:
    ------------------
    Unless otherwise stated, the terms error handling and lifecycle management
    (LcMgmt for short) of the framework are often used interchangeably.
    Their core responsibility and features are:
        - detect unhandled fatal errors, i.e. exceptions,
        - submit fatal errors as soon as detected,
        - allow tasks (or processes) to submit their own (fatal) errors,
        - per-task (and per-process) tracking of submitted (fatal) errors,
        - qualify submitted fatal errors,
        - identify the very first qualified fatal error as the root LC failure,
        - initiate framework's shutdown if LC failure(s) reported.

    However, LcMgmt also includes active, internal services of the framework,
    designed to ensure its stability and responsiveness regardless of the
    particular error handling mechansisms used.


    Undetected errors:
    ---------------------
    As the naming implies, those errors are actually present in the program
    code, but not detected yet (mostly because of missing proper test runs
    of the program). Worst case, they cause severe error condition(s) first
    when the programm runs in a production environment.

    Note that the LcMgmt enables an application to present a well-defined,
    controlled behavior at any time even in case of undetected fatal errors.


    Non-fatal errors:
    ------------------
    These are errors expected to happen at any time, usually because of
    wrong/bad user input. In general, they are detected by performing a
    pre-check of user input via evaluation of the formal parameters of the
    (interface) function used.

    Good news about non-fatal errors is, that neither stability nor reliability
    of the program is suffered from them. Morover, the program can keep going
    with its normal execution as its code has been able to apply existing,
    appropriate countermeasures according to application requirements.


    User errors:
    -------------
    Non-fatal errors may also be referred to as user errors.


    Submitting non-fatal errors:
    ------------------------------
    Non-fatal, i.e. user, errors can be submitted by the application using
    below interface fuctions:
        - xlogif.LogError()
        - xlogif.LogErrocEC()

    Note that the framework may also submit non-fatal errors on its own (using
    its internal API). Such a non-fatal error is considered by the framework a
    user error caused by application code when using respective public API of
    the framework.

    For example, attemps to create a new task instance may result in a
    by-framework-submitted non-fatal error as the framework is exactly behaving
    as expected. Moreover, its runtime environment (RTE) is still working as
    expected, too.

    But, from point of view of the application that non-fatal error submitted
    by the framework would normally be reason enough to submit an application-
    caused fatal error to indicate an unexpected LC failure as it wouldn't make
    sense to continue the execution without that task instace is correctly
    constructed.


    Fatal errors:
    -------------
    They are basically unexpected errors, usually as a result of a raised
    exception (or to put it in C++ or Java, thrown exception) or some otherwise
    detected bad/improper program conditions. Worst case, program code is not
    prepared for them at all, either the application crashes, or the program is
    not stable and/or reliable anymore.

    Best case is whenever the program detects such an error before the
    application crashes. The detecting piece of code submits that error as a
    fatal one hoping for its proper handling somewhere in the upper layer(s).

    Bad news about fatal errors is that their tracking and handling inevitably
    increases both complexity and programming effort of applications.

    LcMgmt of framework's RTE is designed to make the aforementioned best case
    can take place with the topmost goal of reducing the programming effort of
    the application as much as possible and without information loss on one
    hand, while keeping the RTE stable and reliable on the other hand.


    Submitting fatal errors:
    -------------------------
    Fatal erros can be submitted by the application using below interface
    fuctions with the last two ones are designed for submitting raised
    exceptions:
        - xlogif.LogFatal()
        - xlogif.LogFatalEC()
        - xlogif.LogException()
        - xlogif.LogExceptionEC()

    Again, framework may also submit fatal errors using its own internal API,
    especially whenever detecting (or catching) unhandled exceptions.

    Once a fatal error is submitted, LcMgmt is in charge of tracking and
    handling of that fatal error.


    Qualified fatal errors:
    -----------------------
    Submitted errors may change their type or even become resolved, as they
    pass through a multilayered application software. For example, an error
    classified by a specific layer as non-fatal may later be considered a
    fatal error by another (upper) layer, and vice versa.

    The public API of the framework provides the needed interface functions to
    enable application code to hanlde the above-mentioned dynamic nature of
    classification. Among others, class XTaskException is provided as a means
    of notifying the application about submitted fatal errors. In other words,
    this way the application is given the opportunity (if configured so) to
    handle the notified fatal error on its own, maybe even resolving or
    clearing it at the end.

    Once such a fatal error has passed all possible layers without being
    resolved, it is considered 'qualified' and approved. Qualified fatal errors
    are reported accordingly, they also cause that LcMgmt initiates RTE's
    shutdown sequence.


    Die mode:
    -----------
    A special start option of the framework is the so-called 'die-mode' which
    is enabled by default, Its runtime meaning is:
        as soon as a fatal error detected or submitted, it has to be treated
        by the framework as qualified. Affected task might be notified about
        that fatal error, but it won't be allowed to resolve or to clear it.
        As a consequence framework's shutdown sequence described below will
        immediately take place.

    Die mode is simply one possible policy with regard to the impact of
    qualified fatal errors. It is a strict policy, most useful especially in
    early development phases.

    But, it doesn't have to be this way. Like any other runtime policy of the
    framework, the default policy of handling qualified fatal errors can be
    customized or bypassed provided that the specific version of the framework
    running supports the respective API and/or configuration.


    Coordinated shutdown sequence:
    ------------------------------------
    Whenever the shutdown of framework's RTE takes place, it always means a
    'coordinated' shutdown sequence (CSDS for short). Its executional procedure
    strictly follows its related policy given for the lifecycle at hand.

    The default policy is briefly described as follows:
        - put the RTE in its LC-limited mode (see section 'RTE modes' in XTask),
        - request all running tasks (and child process) to stop (or terminate)
          in their reverse order of start,
        - stop RTE, so controll is given back to the host thread waiting for
          framework's termination.

    Again, the default policy of CSDS can be customized or bypassed, too,
    provided that the specific version of the framework running supports
    the respective API and/or configuration.


    See:
    -----
        - XTask
        - XTaskException
        - fwapi.StartXcoFW()
        - fwapi.JoinXcoFW()
    """

    __slots__ = [ '__xte' ]


    def __init__(self, xtaskError_ : _XTaskErrorBase):
        """
        Constructor (or initializer) of this instance.

        Parameters:
        -------------
            - xtaskError_ :
              framework internal error object this instance is made around.

        Note:
        ------
            - Instances of this class are created by the framework only.
            - They are returned whenever current error (if any) of a task is
              requested.
            - Such an instance is always either a non-fatal (i.e. user) error or
              a fatal error.
            - Except for qualified fatal errors, the validity of the information
              an instance of this class delivers is bound to the scope of its
              creation.
            - More detail available in class description of XTaskError.

        See:
        -----
            - XTaskError
            - XTask.currentError
            - curxtask.GetCurrentXTaskError()
        """
        self.__xte = xtaskError_


    def __str__(self):
        """
        String representation of this instance.

        Returns:
        ----------
            A string object as representation of this instance.
        """
        return _XTaskErrorBase.__str__(self.__xte)


    @property
    def isFatalError(self) -> bool:
        """
        Getter property.

        Returns:
        ----------
            True if this instance is a fatal error, False otherwise,
            i.e. a non-fatal (or user) error.

        Note:
        ------
            - A fatal error at this level of abstraction is always a
              qualified one.
            - More detail available in class description of XTaskError.

        See:
        -----
            XTaskError
        """
        return self.__xte._isFatalError


    @property
    def uniqueID(self) -> int:
        """
        Getter property.

        Returns:
        ----------
            An integer value as unique ID of this instance.
        """
        return self.__xte._uniqueID

    @property
    def message(self) -> str:
        """
        Getter property.

        Returns:
        ----------
            A string object giving short description of the error cause as the
            respective, underlying error object was submitted.
        """
        return self.__xte._message


    @property
    def errorCode(self) -> int:
        """
        Getter property.

        Returns:
        ----------
            None if not available, otherwise an integer value as the error code
            assigned when the respective, underlying error object was submitted.

        Note:
        ------
            The error code (if any) of error messages submitted are always
            positive integer values, unless they were submitted by the
            framework.

        See:
        -----
            - xlogif.LogErrorEC()
            - xlogif.LogFatalEC()
            - xlogif.LogExceptionEC()
        """
        return self.__xte._errorCode
#END class XTaskError


class XTaskException(_XTaskExceptionBase):
    """
    Instances of this class are exceptions raised by the framework.

    As mentioned in section 'Qualified fatal errors' in class description of
    XTaskError, the purpose of this class is primarily to inform currently
    running application task, i.e. an instance of class XTask, about submitted,
    fatal errors.

    Whether such a submitted fatal error is qualified already depends basically
    on 'die-mode' configuration of framework's RTE during its lifecycle (see
    class description of XTaskError).

    If applicable, application code prepared to handle such an exception (via
    try and except clauses) is given the opportunity to be part of the
    qualification procedure of submitted fatal errors of the affected task.

    However, if not applicable, e.g. because of 'die-mode' or missing
    permissions, affected task won't be able to resolve the submitted error.
    Nevertheless, the application might use it as the right time or place to
    initiate specific actions before CSDS (see class description of XTaskError)
    takes place.

    See:
    -----
        - XTask
        - XTaskError
    """


    def __init__(self, xtaskXcp_ : _XTaskExceptionBase):
        """
        Constructor (or initializer) of this instance.

        Parameters:
        -------------
            - xtaskXcp_ :
              framework internal exception object this instance is made around.

        Note:
        ------
            - Instances of this class are created by the framework only.
            - They are raised during the qualificaiton procedure of submitted
              fatal errors.
            - More detail available in class description of XTaskError.

        See:
        -----
            - XTaskError
        """
        super().__init__(clone_=xtaskXcp_)


    def __str__(self):
        """
        String representation of this instance.

        Returns:
        ----------
            A string object as representation of this instance.
        """
        return _XTaskExceptionBase.__str__(self)


    @property
    def isDieException(self):
        """
        Getter property.

        Returns:
        ----------
            True if this instance is created due to enabled configuration of
            'die-mode', False otherwise.

        Note:
        ------
            - More detail available in class description of XTaskError.

        See:
        -----
            - XTaskError
        """
        return self._isDieException


    @property
    def uniqueID(self) -> int:
        """
        Getter property.

        Returns:
        ----------
            An integer value as unique ID of this instance.
        """
        return self._uniqueID


    @property
    def message(self) -> str:
        """
        Getter property.

        Returns:
        ----------
            A string object giving short description of the exception cause as
            the respective fatal error was submitted.
        """
        return self._message


    @property
    def errorCode(self) -> int:
        """
        Getter property.

        Returns:
        ----------
            None if not available, otherwise an integer value as the error code
            assigned when the respective fatal error was submitted.

        Note:
        ------
            The error code (if any) of fatal error messages submitted are always
            positive integer values, unless they were submitted by the framework.

        See:
        -----
            - xlogif.LogFatalEC()
            - xlogif.LogExceptionEC()
        """
        return self._errorCode


    @property
    def callstack(self) -> str:
        """
        Getter property.

        Returns:
        ----------
            None if not available, otherwise the callstack retrieved at the time
            of detection of the respective fatal error.
        """
        return self._callstack


    @property
    def traceback(self) -> str:
        """
        Getter property.

        Returns:
        ----------
            None if not available, otherwise the traceback retrieved at the time
            of detection of the respective fatal error.
        """
        return self._traceback
#END class XTaskException
