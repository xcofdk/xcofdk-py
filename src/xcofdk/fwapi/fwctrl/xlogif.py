# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xlogif.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from _fw.fwssys.fwmt.api import xlogifbase

from xcofdk.fwapi import ITaskError


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
def LogTrace(logMsg_ : str):
    """
    Logging of a trace message.

    Parameters:
    -------------
        - logMsg_ :
          trace message to be logged.
    """
    xlogifbase._XLogTrace(logMsg_)


def LogDebug(logMsg_ : str):
    """
    Logging of a debug message.

    Parameters:
        - logMsg_ :
          debug message to be logged.
    """
    xlogifbase._XLogDebug(logMsg_)


def LogInfo(logMsg_ : str):
    """
    Logging of an info message.

    Parameters:
        - logMsg_ :
          info message to be logged.
    """
    xlogifbase._XLogInfo(logMsg_)


def LogWarning(logMsg_ : str):
    """
    Logging of a warning message.

    Parameters:
        - logMsg_ :
          warning message to be logged.
    """
    xlogifbase._XLogWarning(logMsg_)


def LogError(logMsg_ : str):
    """
    Submitts a user error message.

    Parameters:
        - logMsg_ :
          user error message to be submitted.

    See:
    -----
        >>> ITaskError
    """
    xlogifbase._XLogError(logMsg_)


def LogErrorEC(logMsg_ : str, errorCode_ : int):
    """
    Submitts a user error message with a given error code.

    Parameters:
        - logMsg_ :
          user error message to be submitted.
        - errorCode_ :
          positive integer value as error code of the user error message to be
          submitted.

    See:
    -----
        >>> ITaskError
    """
    xlogifbase._XLogErrorEC(logMsg_, errorCode_)


def LogFatal(logMsg_ : str):
    """
    Submitts a fatal error message.

    Parameters:
        - logMsg_ :
          fatal error message to be submitted.

    See:
    -----
        >>> ITaskError
    """
    xlogifbase._XLogFatal(logMsg_)


def LogFatalEC(logMsg_ : str, errorCode_ : int):
    """
    Submitts a fatal error message with a given error code.

    Parameters:
        - logMsg_ :
          fatal error message to be submitted.
        - errorCode_ :
          positive integer value as error code of the fatal error message to be
          submitted.

   See:
    -----
        >>> ITaskError
    """
    xlogifbase._XLogFatalEC(logMsg_, errorCode_)


def LogException(logMsg_ : str, logXcp_ : Exception):
    """
    Submitts a fatal error message due to the raised exception passed in.

    Parameters:
        - logMsg_ :
          fatal error message to be submitted.
        - logXcp_ :
          caught exception object the fatal error is going to be submitted for

    See:
    -----
        >>> ITaskError
    """
    xlogifbase._XLogException(logMsg_, logXcp_)


def LogExceptionEC(logMsg_ : str, logXcp_ : Exception, errorCode_ : int):
    """
    Submitts a fatal error message due to the raised exception passed in.

    Parameters:
        - logMsg_ :
          fatal error message to be submitted.
        - logXcp_ :
          caught exception object
        - errorCode_ :
          positive integer value as error code of the fatal error message to be
          submitted.

    See:
    -----
        >>> ITaskError
    """
    xlogifbase._XLogExceptionEC(logMsg_, errorCode_, logXcp_)
