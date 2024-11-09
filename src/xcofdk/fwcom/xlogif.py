# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xlogif.py
#
# Copyright(c) 2023-2024 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


"""
Module 'xcofdk.fwcom.xlogif' represents framework's subsystem 'logging'.

It mainly provides API functions for usual logging out of the currently running
application tasks, i.e. instances of class XTask, or processes, i.e. instances
of class XProcess.

In addition, its respective API functions can be used whenever errors detected
by application code, i.e. tasks or processes, have to be submitted (see class
description of XTaskEror).


Logging vs. submitting:
-------------------------
Both terms refer to a request for a certain action to be performed by the
framework, so they each do submitt a request to action.

While the final result of a loggin request is simply some sort of
'formatted-flushing' of a given message to an output stream (e.g. stdout/stderr,
a file or a serial/network port), a request to submit an error perforrms a lot
more in addition, namely triggering framework's error handling at the same time
which is both multilayered and multithreading.

API functions for 'ordinary' logging are:
    >>> LogTrace()
    >>> LogDebug()
    >>> LogInfo()
    >>> LogWarning()

And API functions for 'submitting' errors are:
    >>> LogError()
    >>> LogErrorEC()
    >>> LogFatal()
    >>> LogFatalEC()
    >>> LogException()
    >>> LogExceptionEC()


Log level:
-----------
Log level is commonly a static or dynamic configuration item used for
classification of log entries based on their precedence (or severity)
with tracees are assigned the lowest precedence, while fatal errors are
assigned the highest precedence.

The framework of XCOFDK follows the static approach, meaning the log level is
determined when starting the framework, and it remains unchanged for the whole
lifecycle of its RTE.


Note:
------
    - Pre-defined log levels are described in package description of
      'xcofdk.fwapi'.
    - Error handling is described in class description of XTaskError.

See:
-----
    - XTask
    - XProcess
    - XTaskError
    - XTaskException
    - fwapi.StartXcoFW()
"""


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from xcofdk._xcofw.fw.fwssys.fwcore.apiimpl import xlogifbase


# ------------------------------------------------------------------------------
# Interface - xtask logging API
# ------------------------------------------------------------------------------
def IsDieModeEnabled() -> bool:
    """
    Returns:
    ----------
        True if framework's RTE has been started with 'die-mode' enabled,
        False otherwise.

    Note:
    ------
        - Die mode is enabled by default.
        - More detail available in class description of XTaskError.

    See:
    -----
        XTaskError
    """
    return xlogifbase._XIsDieModeEnabled()


def LogTrace(xlogMsg_ : str):
    """
    Logging of a trace message.

    Parameters:
    -------------
        - xlogMsg_ :
          trace message to be logged.
    """
    xlogifbase._XLogTrace(xlogMsg_)


def LogDebug(xlogMsg_ : str):
    """
    Logging of a debug message.

    Parameters:
        - xlogMsg_ :
          debug message to be logged.
    """
    xlogifbase._XLogDebug(xlogMsg_)


def LogInfo(xlogMsg_ : str):
    """
    Logging of an info message.

    Parameters:
        - xlogMsg_ :
          info message to be logged.
    """
    xlogifbase._XLogInfo(xlogMsg_)


def LogWarning(xlogMsg_ : str):
    """
    Logging of a warning message.

    Parameters:
        - xlogMsg_ :
          warning message to be logged.
    """
    xlogifbase._XLogWarning(xlogMsg_)


def LogError(xlogMsg_ : str):
    """
    Submitts a user error message.

    Parameters:
        - xlogMsg_ :
          user error message to be submitted.

    Note:
    ------
        Error handling is described in class description of XTaskError.

    See:
    -----
        XTaskError
    """
    xlogifbase._XLogError(xlogMsg_)


def LogErrorEC(xlogMsg_ : str, xlogErrorCode_ : int =None):
    """
    Submitts a user error message with a given error code.

    Parameters:
        - xlogMsg_ :
          user error message to be submitted.
        - xlogErrorCode_ :
          error code of the user error message to be submitted.

    Note:
    ------
        Error handling is described in class description of XTaskError.

    See:
    -----
        XTaskError
    """
    xlogifbase._XLogErrorEC(xlogMsg_, xlogErrorCode_)


def LogFatal(xlogMsg_ : str):
    """
    Submitts a fatal error message.

    Parameters:
        - xlogMsg_ :
          fatal error message to be submitted.

    Note:
    ------
        Error handling is described in class description of XTaskError.

    See:
    -----
        XTaskError
    """
    xlogifbase._XLogFatal(xlogMsg_)


def LogFatalEC(xlogMsg_ : str, xlogErrorCode_ : int =None):
    """
    Submitts a fatal error message with a given error code.

    Parameters:
        - xlogMsg_ :
          fatal error message to be submitted.
        - xlogErrorCode_ :
          error code of the fatal error message to be submitted.

    Note:
    ------
        Error handling is described in class description of XTaskError.

    See:
    -----
        XTaskError
    """
    xlogifbase._XLogFatalEC(xlogMsg_, xlogErrorCode_)


def LogException(xlogMsg_ : str, xlogXcp_ : Exception):
    """
    Submitts a fatal error message due to the raised exception passed in.

    Parameters:
        - xlogMsg_ :
          fatal error message to be submitted.
        - xlogXcp_ :
          caught exception object the fatal error is going to be submitted for

    Note:
    ------
        Error handling is described in class description of XTaskError.

    See:
    -----
        XTaskError
    """
    xlogifbase._XLogException(xlogMsg_, xlogXcp_)


def LogExceptionEC(xlogMsg_ : str, xlogXcp_ : Exception, xlogErrorCode_ : int):
    """
    Submitts a fatal error message due to the raised exception passed in.

    Parameters:
        - xlogMsg_ :
          fatal error message to be submitted.
        - xlogXcp_ :
          caught exception object
        - xlogErrorCode_ :
          error code of the fatal error message to be submitted.

    Note:
    ------
        Error handling is described in class description of XTaskError.

    See:
    -----
        XTaskError
    """
    xlogifbase._XLogExceptionEC(xlogMsg_, xlogErrorCode_, xlogXcp_)
