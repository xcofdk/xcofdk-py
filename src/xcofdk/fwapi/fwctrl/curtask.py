# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : curtask.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


"""
Module 'xcofdk.fwapi.fwctrl.curtask' provides API functions related to the
application task, i.e. an instance of either classes RCTask or XTask, currently
executed by the framework.

It is designed to facilitate error handling by the application code wherever
direct access to the ccurrent task is not available.

This documentation refers to the term 'current running application task' as an
instance of eitehr classes RCTask or XTask with the associated host thread is
the one currently being executed. But, be aware that there might be no
application task avialable right now, if the execution context or scope at hand
is outside the 3-PhXF of any possible application task instance.

Note:
------
    - Tasks (and processes) should always be considered critical active
      components of an application.
    - Even though this module enables program code to conveniently access
      task instances for specific operations, it remains the responsibilty
      of the application to arrange for a well-organized access shape in terms
      of public API of the framework allowed to use.

See:
-----
    >>> ITask
    >>> IRCTask
    >>> ITaskError


Deprecated API:
----------------
Starting with XCOFDK-py v3.0 below API entities (formerly part of
the API of this module) are deprecated and not available anymore:
    >>> IsCurrentXTaskErrorFree      = IsCurTaskErrorFree
    >>> IsCurrentXTaskFatalErrorFree = IsCurTaskFatalErrorFree
    >>> GetCurrentXTaskError         = GetCurTaskError
    >>> SetCurrentXTaskError         = SetCurTaskError
    >>> ClearCurrentXTaskError       = ClearCurTaskError
    >>> SetCurrentXTaskErrorEC       = SetCurTaskErrorEC
    >>> SetCurrentXTaskFatalError    = SetCurTaskFatalError
    >>> SetCurrentXTaskFatalErrorEC  = SetCurTaskFatalErrorEC
"""


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from xcofdk.fwapi import ITask
from xcofdk.fwapi import IRCTask
from xcofdk.fwapi import ITaskError

from _fw.fwssys.fwmt.api import xlogifbase


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
def IsCurTaskErrorFree() -> bool:
    """
    Returns:
    ----------
        True if current task error as returned by the API function
        'GetCurTaskError()' resloves to None, False otherwise.

    See:
    -----
        >>> ITaskError
        >>> ITask.isErrorFree
        >>> ITask.isFatalErrorFree
        >>> ITask.currentError
        >>> GetCurTaskError()
    """
    return xlogifbase._XIsErrorFree()


def IsCurTaskFatalErrorFree() -> bool:
    """
    Returns:
    ----------
        False if current task error as returned by the API function
        'GetCurTaskError()' resloves to a qualified fatal error, True otherwise.

    See:
    -----
        >>> ITaskError
        >>> ITask.isErrorFree
        >>> ITask.isFatalErrorFree
        >>> ITask.currentError
        >>> GetCurTaskError()
    """
    return xlogifbase._XIsFatalErrorFree()


def GetCurTaskError() -> ITaskError:
    """
    Retrieve current error (if any) of current application task.

    Returns:
    ----------
        - None if currently executed host thread is not bound to an instance
          of either classes RCTask or XTask,
        - None if such an instance is bound to currently executed host thread,
          but that task is free of any error,
        - current task error otherwise.

    See:
    -----
        >>> ITaskError
        >>> ITask.currentError
    """
    return xlogifbase._XGetCurrentError()


def ClearCurTaskError() -> bool:
    """
    Request to clear current error (if any) of current application task.

    Returns:
    ----------
        False if current task error (if any) of current application task could
        not be cleared, True otherwise.

    See:
    -----
        >>> ITaskError
        >>> GetCurTaskError()
        >>> ITask.ClearCurrentError()
    """
    return xlogifbase._XClearCurrentError()


def SetCurTaskError(errorMsg_ : str):
    """
    Request to set or replace current application task's current error to be a
    user error.

    The request will be processed as follows:
        a) clear current task error (if any) as returned by the API function
           'GetCurTaskError()',
        b) if a) passed, then try to set current error of current application
           task as requested.

    Parameters:
    -------------
        - errorMsg_ :
          user error message to be set.

    See:
    -----
        >>> ITaskError
        >>> ITask.currentError
        >>> ITask.SetError()
        >>> ITask.ClearCurrentError()
        >>> GetCurTaskError()
    """
    xlogifbase._XSetError(errorMsg_)


def SetCurTaskErrorEC(errorMsg_ : str, errorCode_ : int =None):
    """
    Request to set or replace current application task's current error to be a
    user error.

    The request will be processed as follows:
        a) clear current task error (if any) as returned by the API function
           'GetCurTaskError()',
        b) if a) passed, then try to set current error of current application
           task as requested.

    Parameters:
    -------------
        - errorMsg_ :
          user error message to be set,
        - errorCode_ :
          error code to be set.

    See:
    -----
        >>> ITaskError
        >>> ITask.currentError
        >>> ITask.SetErrorEC()
        >>> ITask.ClearCurrentError()
        >>> GetCurTaskError()
    """
    xlogifbase._XSetErrorEC(errorMsg_, errorCode_)


def SetCurTaskFatalError(errorMsg_ : str):
    """
    Request to set or replace current application task's current error to be a
    fatal error.

    The request will be processed as follows:
        a) clear current task error (if any) as returned by the API function
           'GetCurTaskError()',
        b) if a) passed, then try to set current error of current application
           task as requested.

    Parameters:
    -------------
        - errorMsg_ :
          fatal error message to be set.

    See:
    -----
        >>> ITaskError
        >>> ITask.currentError
        >>> ITask.SetFatalError()
        >>> ITask.ClearCurrentError()
        >>> GetCurTaskError()
    """
    xlogifbase._XSetFatalError(errorMsg_)


def SetCurTaskFatalErrorEC(errorMsg_ : str, errorCode_ : int =None):
    """
    Request to set or replace current application task's current error to be a
    fatal error.

    The request will be processed as follows:
        a) clear current task error (if any) as returned by the API function
           'GetCurTaskError()',
        b) if a) passed, then try to set current error of current application
           task as requested.

    Parameters:
    -------------
        - errorMsg_ :
          fatal error message to be set,
        - errorCode_ :
          error code to be set.

    See:
    -----
        >>> ITaskError
        >>> ITask.currentError
        >>> ITask.SetFatalErrorEC()
        >>> ITask.ClearCurrentError()
        >>> GetCurTaskError()
    """
    xlogifbase._XSetFatalErrorEC(errorMsg_, errorCode_)
