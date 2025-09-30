# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : __init__.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


"""
Subpackage 'xcofdk.fwapi.fwctrl' represents the gateway of framework's public
interface available for applications.

It provides API functions to control the runtime enviornment (RTE) of XCOFDK:
    >>> # start the framework
    >>> StartXcoFW()
    >>>
    >>> # stop the framework
    >>> StopXcoFW()
    >>>
    >>> # wait for termination of the framework
    >>> JoinXcoFW()
    >>>
    >>> # wait for termination (of a subset) of all running tasks
    >>> JoinTasks()
    >>>
    >>> # wait for termination (of a subset) of all running child processes
    >>> JoinProcesses()
    >>>
    >>> # terminate (a subset of) all running child processes
    >>> TerminateProcesses()


Deprecated API:
----------------
Starting with XCOFDK-py v3.0 below API entities are deprecated and not available
anymore:
    - The start option '--enable-log-callstack' has been replacd by
      '--disable-log-callstack'.
"""


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from typing import List
from typing import Union

from _fw.fwssys.fwctrl.fwapibase import _FwApiBase

from .fwutil import LcFailure
from .fwutil import IsFwAvailable
from .fwutil import IsLcFailureFree
from .fwutil import GetLcFailure

from xcofdk.fwapi            import ITask
from xcofdk.fwapi.xmp        import XProcess
from xcofdk.fwapi.xmt.rctask import RCTask
from xcofdk.fwapi.xmt.rctask import RCCommTask
from xcofdk.fwapi.xmt.rctask import SyncTask
from xcofdk.fwapi.xmt.rctask import AsyncTask
from xcofdk.fwapi.xmt.rctask import SyncCommTask
from xcofdk.fwapi.xmt.rctask import AsyncCommTask
from xcofdk.fwapi.xmt.rctask import MessageDrivenTask
from xcofdk.fwapi.xmt.rctask import XFSyncTask
from xcofdk.fwapi.xmt.rctask import XFAsyncTask
from xcofdk.fwapi.xmt.rctask import XFSyncCommTask
from xcofdk.fwapi.xmt.rctask import XFAsyncCommTask
from xcofdk.fwapi.xmt.rctask import XFMessageDrivenTask
from xcofdk.fwapi.xmt.rctask import GetCurTask


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
def StartXcoFW(fwStartOptions_ : Union[str, List[str]] =None) -> bool:
    """
    Starts the runtime environment (RTE) of XCOFDK, also referred to as
    the framework.

    Parameters:
    -------------
        - fwStartOptions_ :
          None if the default for each start option shall be assumed,
          a space separated sequence of string literals or a list of string
          literals otherwise.

    Returns:
    ----------
        True if the operation succeeded, False otherwise.

    Available start options:
    ------------------------
        a) --log-level :
           followed by a case-sensistive string literal as the log level to be
           used for log requests submitted by the application, also referred
           to as user.
           It defaults to 'info'.

           Valid valuse are (in ascending order of their precedence):
               'trace' | 'debug' | 'info' | 'warning' | 'error'

           At runtime all log requests with a precedence lower than the
           specified user log level will be ignored by the framework.

        b) --fw-log-level:
           followed by a case-sensistive string literal as the log level to be
           useed for log requests submitted by the framework.
           It defaults to 'error'.

           Valid valuse are (in ascending order of their precedence):
               'info' | 'kpi' | 'warning' | 'error'

           At runtime all framework log requests with a precedence lower than
           the specified framework log level will be ignored by the framework.

        c) --disable-log-timestamp :
           defaulting to False, it disables/hides the timestamp of the output
           of submitted logs.

        d) --disable-log-highlighting :
           defaulting to False, disables color highlighting of the console
           output of submitted logs.

           Color highlighting of log output is supported for Python versions
           3.9 and higher. Useful usecase for supplying this option is whenever
           used terminal/console program of the platform, e.g. Windows Commond
           Prompt 'cmd.exe', does not support colored output to stdout/stderr.

        e) --disable-log-callstack
           defaulting to False, disables/hides the callstack of fatal errors
           (if any).

        f) --suppress-start-preamble
           defaulting to False, it suppresses the log output of framework's
           start preamble.

           Also, whenever framework log lelve is set to 'error', this start
           option will be treated as if enabled.

    Note:
    ------
        - Prior to start of the framework applications can configure and/or
          customize the RTE to change its default behavior, e.g. by enabling
          ForcedAutoStop:
              >>> from xcofdk       import fwapi
              >>> from xcofdk.fwapi import rtecfg
              >>>
              >>> rtecfg.RtePolicyEnableForcedAutoStop()
              >>>
              >>> fwapi.StartXcoFW()
              >>> #...
    """
    return _FwApiBase.FwApiStartXcoFW(startOptions_=fwStartOptions_)


def StopXcoFW() -> bool:
    """
    Asynchronous request to stop the RTE of the framework if it is (still)
    running.

    Returns:
    ----------
        True if the operation could be successfully performed, False otherwise.

    Note:
    ------
        - A request to stop the framework will also initiate its coordinated
          shutdown sequence if not done already.
        - Unless RTE policy of TerminalMode is enabled, an explicit request to
          stop the framework is optional.

          There are three mutually exclusive RTE configuration policies
          introduced to address different application requirements with regard
          to how framework's stop is managed:
              >>> from xcofdk       import fwapi
              >>> from xcofdk.fwapi import rtecfg
              >>>
              >>> # either enable AutoStop (optional, as this is the default)
              >>> rtecfg.RtePolicyEnableAutoStop()
              >>>
              >>> # or, enable ForcedAutoStop
              >>> rtecfg.RtePolicyEnableForcedAutoStop()
              >>>
              >>> # or, enable TerminalMode
              >>> rtecfg.RtePolicyEnableTerminalMode()
              >>>
              >>> fwapi.StartXcoFW()
              >>>
              >>> # create and start application's starter task
              >>> #...
              >>>
              >>> fwapi.JoinXcoFW()

    See:
    -----
        >>> StartXcoFW()
        >>> JoinXcoFW()
    """
    return _FwApiBase.FwApiStopXcoFW()


def JoinXcoFW() -> bool:
    """
    Request to synchronously wait for the RTE of XCOFDK to finish its execution
    (if still running).

    Returns:
    ----------
        True if the operation could be successfully performed and there have
        been no lifecycle failures, False otherwise.

    Note:
    ------
        - A request to join the RTE from within a running application task will
          be denied by the framework.

    See:
    -----
        >>> StartXcoFW()
        >>> StopXcoFW()
    """
    return _FwApiBase.FwApiJoinXcoFW()


def JoinTasks(taskUIDs_ : Union[int, List[int], None] =None, maxWaitTime_: Union[int, float, None] =None, unjoined_ : Union[List, None] =None) -> int:
    """
    Request to wait for termination (of a subset) of all application tasks
    currently running.

    Parameters:
    -------------
        - taskUIDs_ :
              - unique task ID of a single application task, or
              - a list of such unique task IDs, or
              - None, in which case all application tasks (except for current
                running application task if any) which are not terminated yet
                will be assumed.
        - maxWaitTime_ :
          wait for specified amount of time as long as there are still tasks
          not joined yet.
          If None, then the wait time is not limited.
          Otherwise, milliseconds for integer values or seconds for
          floating-point values will be taken.
        - unjoined_:
          if a list object is passed to, then the operation will put the unique
          task ID of all specified application tasks which could not be joined
          into this list object.

    Returns:
    ----------
        Number of application tasks joined.

    See:
    -----
        >>> ITask.taskUID
    """
    res, _lstUnj = _FwApiBase.FwApiJoinTasks(taskUIDs_, timeout_=maxWaitTime_)
    if isinstance(unjoined_, list):
        unjoined_.clear()
        if isinstance(_lstUnj,list) and len(_lstUnj):
            unjoined_ += _lstUnj
    return res


def JoinProcesses(procPIDs_ : Union[int, List[int], None] =None, maxWaitTime_: Union[int, float, None] =None, unjoined_ : Union[List, None] =None) -> int:
    """
    Request to wait for termination (of a subset) of all child proceesses
    currently running.

    Parameters:
    -------------
        - procPIDs_ :
              - PID of a single child process, or
              - a list of such PIDs, or
              - None, in which case all child processes which are not terminated
                yet will be assumed.
        - maxWaitTime_ :
          wait for specified amount of time as long as there are still child
          processes not joined yet.
          If None, then the wait time is not limited.
          Otherwise, milliseconds for integer values or seconds for
          floating-point values will be taken.
        - unjoined_:
          if a list object is passed to, then the operation will put the child
          process instances of all specified PIDs which could not be joined
          into this list object.

    Returns:
    ----------
        Number of child processes terminated.
    """
    res, _lstUnj = _FwApiBase.FwApiJoinProcesses(procPIDs_, timeout_=maxWaitTime_)
    if isinstance(unjoined_, list):
        unjoined_.clear()
        if isinstance(_lstUnj,list) and len(_lstUnj):
            unjoined_ += _lstUnj
    return res


def TerminateProcesses(procPIDs_ : Union[int, List[int], None] =None) -> int:
    """
    Request to terminate (a subset of) all child proceesses currently running.

    Parameters:
    -------------
        - procPIDs_ :
              - PID of a single child process, or
              - a list of such PIDs, or
              - None, in which case all child processes which are not terminated
                yet will be assumed.

    Returns:
    ----------
        Number of child processes requested to terminate.

    Note:
    ------
        - Unless requested to do so, the framework never attempts to terminate
          a child process.
    """
    return _FwApiBase.FwApiTerminateProcesses(procPIDs_)
