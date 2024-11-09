# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : curxtask.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


"""
Module 'xcofdk.fwcom.curxtask' provides API functions related to the
application task, i.e. the instance of class XTask, currently executed.

It is designed to facilitate error handling by the application code wherever
direct access to the task instance currently executed is not available.

Note:
------
    - Tasks (and processes) should always be considered critical active
      components of an application.
    - Even though this module enables program code to conveniently access
      task instances for specific operations, it remains the responsibilty
      of the application to arrange for a well-organized access shape in terms
      of public API of the framework allowed to use.
    - Error handling is described in class description of XTaskError.

See:
-----
    - XTask
    - XTaskError
"""


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from xcofdk.fwapi.xtask import XTaskError

from xcofdk._xcofw.fw.fwssys.fwcore.apiimpl import xlogifbase


# ------------------------------------------------------------------------------
# Interface - helper API functions referring to currently running xtask
# ------------------------------------------------------------------------------
def IsCurrentXTaskErrorFree() -> bool:
    """
    Returns:
    ----------
        True if currently executed host thread is bound to an instance of class
        XTask with that task is free of any error, False otherwise.

    Note:
    ------
        Error handling is described in class description of XTaskError.

    See:
    -----
        - XTask.isErrorFree
        - XTask.isFatalErrorFree
        - XTask.currentError
        - XTaskError
    """
    return xlogifbase._XIsErrorFree()


def IsCurrentXTaskFatalErrorFree() -> bool:
    """
    Returns:
    ----------
        True if currently executed host thread is bound to an instance of class
        XTask with that task is free of any qualified fatal error, False
        otherwise.

    Note:
    ------
        Error handling is described in class description of XTaskError.

    See:
    -----
        - XTask.isErrorFree
        - XTask.isFatalErrorFree
        - XTask.currentError
        - XTaskError
    """
    return xlogifbase._XIsFatalErrorFree()


def GetCurrentXTaskError() -> XTaskError:
    """
    Retrieve current error (if any) of currently executed task.

    Returns:
    ----------
        - None if currently executed host thread is either not bound to an
          instance of class XTask or if bound that task is free of any error.
        - An instance of class XTaskError representing that task's current
          error otherwise.

    Note:
    ------
        Error handling is described in class description of XTaskError.

    See:
    -----
        - XTask.currentError
        - XTaskError
    """
    return xlogifbase._XGetCurrentError()


def ClearCurrentXTaskError() -> bool:
    """
    Request to clear current error (if any) of currently executed task.

    Returns:
    ----------
        False if currently executed host thread is either not bound to an
        instance of class XTask or if bound that task's current error could
        not be cleared, True otherwise.

    Note:
    ------
        Error handling is described in class description of XTaskError.

    See:
    -----
        - XTask.currentError
        - XTask.ClearCurrentError()
        - XTaskError
    """
    return xlogifbase._XClearCurrentError()


def SetCurrentXTaskError(errorMsg_ : str):
    """
    Request to set or replace currently executed task's current error to be
    a user error.

    If an attempt to clear current error (if any) passes, the operation will
    make current error associated to the currently executed task is set as
    requested.

    Parameters:
    -------------
        - errorMsg_ :
          message to be used for the user error to be associated to

    Note:
    ------
        - Request will be denied if currently executed host thread is ot bound
          to an instance of class XTask.
        - Error handling is described in more detail in class XTaskError.

    See:
    -----
        - XTask.currentError
        - XTask.SetError()
        - XTask.ClearCurrentError()
        - XTaskError
    """
    xlogifbase._XSetError(errorMsg_)


def SetCurrentXTaskErrorEC(errorMsg_ : str, errorCode_ : int =None):
    """
    Request to set or replace currently executed task's current error to be
    a user error.

    If an attempt to clear current error (if any) passes, the operation will
    make current error associated to the currently executed task is set as
    requested.

    Parameters:
    -------------
        - errorMsg_ :
          message to be used for the user error to be associated to
        - errorCode_ :
          error code to be used for the user error to be associated to

    Note:
    ------
        - Request will be denied if currently executed host thread is ot bound
          to an instance of class XTask.
        - Error handling is described in more detail in class XTaskError.

    See:
    -----
        - XTask.currentError
        - XTask.SetErrorEC()
        - XTask.ClearCurrentError()
        - XTaskError
    """
    xlogifbase._XSetErrorEC(errorMsg_, errorCode_)


def SetCurrentXTaskFatalError(errorMsg_ : str):
    """
    Request to set or replace currently executed task's current error to be
    a fatal error.

    If an attempt to clear current error (if any) passes, the operation will
    make current error associated to the currently executed task is set as
    requested.

    Parameters:
    -------------
        - errorMsg_ :
          message to be used for the fatal error to be associated to

    Note:
    ------
        - Request will be denied if currently executed host thread is ot bound
          to an instance of class XTask.
        - Error handling is described in more detail in class XTaskError.

    See:
    -----
        - XTask.currentError
        - XTask.SetFatalError()
        - XTask.ClearCurrentError()
        - XTaskError
    """
    xlogifbase._XSetFatalError(errorMsg_)


def SetCurrentXTaskFatalErrorEC(errorMsg_ : str, errorCode_ : int =None):
    """
    Request to set or replace currently executed task's current error to be
    a fatal error.

    If an attempt to clear current error (if any) passes, the operation will
    make current error associated to the currently executed task is set as
    requested.

    Parameters:
    -------------
        - errorMsg_ :
          message to be used for the fatal error to be associated to
        - errorCode_ :
          error code to be used for the fatal error to be associated to

    Note:
    ------
        - Request will be denied if currently executed host thread is ot bound
          to an instance of class XTask.
        - Error handling is described in more detail in class XTaskError.

    See:
    -----
        - XTask.currentError
        - XTask.SetFatalErrorEC()
        - XTask.ClearCurrentError()
        - XTaskError
    """
    xlogifbase._XSetFatalErrorEC(errorMsg_, errorCode_)
