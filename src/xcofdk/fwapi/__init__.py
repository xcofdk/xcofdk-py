# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : __init__.py
#
# Copyright(c) 2023-2024 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


"""
Subpackage 'xcofdk.fwapi' provides the main, public interface of the framework
through its subpackages:
    - xcofdk.fwapi.xtask
    - xcofdk.fwapi.xmsg
    - xcofdk.fwapi.xprocess

It also provides API functions to control the runtime enviornment (RTE) of
XCOFDK:
    - StartXcoFW()
    - StopXcoFW()
    - JoinXcoFW()

The RTE is built on top of host threads. Currently supported host threads are
instances of Python class 'threading.Thread'.

A console or GUI application can use the RTE following a common, simple pattern
depicted in code snippet below:

    >>> from xcofdk import fwapi
    >>> from xcofdk.tests.userapp.basic.mt.exampleB11.maintask import MainTask
    >>>
    >>> fwapi.StartXcoFW()
    >>>
    >>> _myMXT = MainTask.CreateSingleton(None)
    >>> _myMXT.Start()
    >>> _myMXT.Join()
    >>>
    >>> fwapi.StopXcoFW()
    >>> fwapi.JoinXcoFW()

Note:
------
    - Framework's RTE is described in class description of XTask.
    - RTE's subsystem of error handling is described in class description of
      XTaskError.
    - RTE's subsystem of mutliprocessing is described in class description of
      XProess.

See:
-----
    - XTask
    - XTaskError
    - xcofdk.fwcom.xlogif
"""


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from typing import Union

from xcofdk._xcofw.fw.fwssys.fwcore.apiimpl.fwapibase import _FwApiBase

from xcofdk.fwapi.xtask import MainXTask
from xcofdk.fwapi.xtask import XTask


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
def StartXcoFW(fwStartOptions_ : Union[list, str] =None) -> bool:
    """
    Starts the runtime environment (RTE) of XCOFDK, i.e. the framwork.

    Detailed description of RTE and its services is provided in description of
    class XTask.

    Parameters:
    -------------
        - fwStartOptions_ :
          framework start options defaulting to None in which case default start
          options will be assumed. If not None, either a list of string literals
          or a space separated sequence of string literals must be passed to.

    Returns:
    ----------
        True if the operation succeeded, False otherwise.

    Available start options:
    ------------------------
        - '--log-level' :
          case-sensistive string literal as log level to be specified right
          after this option. It will be used as the log level to be considered
          when processing application log requests. It defaults to 'info'.

          Valid valuse are (in ascending order of their precedence):
              'trace' | 'debug' | 'info' | 'warning' | 'error'

          At runtime all log requests with a precedence lower than the specified
          application log level will be ignored by the framework.

        - '--disable-log-timestamp' :
          disables/hides timestamp of user log entries, defaults to False.

        - '--disable-log-highlighting' :
          disables color highlighting of log entries, defaults to False.

          Color highlighting of log entries is supported for Python versions 3.9
          and higher. Useful usecase for supplying this option is whenever used
          terminal/console program of the platform, e.g. Windows, does not
          support colored output to stdout/stderr.

    Note:
    ------
        For an introductory presentation of the RTE provided by the framework
        of XCOFDK, its general services and features refert to the
        class description of both XTask and XTaskError.

    See:
    -----
        - XTask
        - XTaskError
        - fwutil.IsFwAvailable()
    """
    return _FwApiBase.FwApiStartXcoFW(startOptions_=fwStartOptions_)


def StopXcoFW() -> bool:
    """
    Asynchronous request to stop the RTE of XCOFDK if it is running.

    Returns:
    ----------
        True if the operation could be successfully performed, False otherwise.

    Note:
    ------
        A request to stop the framework will also initiate its coordinated
        shutdown sequence if not done already.

    See:
    -----
        fwutil.IsFwAvailable()
    """
    return _FwApiBase.FwApiStopXcoFW()


def JoinXcoFW() -> bool:
    """
    Synchronously waits for the RTE of XCOFDK to finish its execution
    (if still running).

    Returns:
    ----------
        True if the operation could be successfully performed and there has been
        no lifecycle failures, False otherwise.

    Note:
    ------
        Requests to join the RTE from within tasks started, but not terminated
        yet will be denied by the framework.

    See:
    -----
        - XTask.isStarted
        - XTask.isTerminated
        - fwutil.IsFwAvailable()
    """
    res = _FwApiBase.FwApiJoinXcoFW()
    return res
