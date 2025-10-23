# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwutil.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from typing import Union

from xcofdk.fwcom import EXmsgPredefinedID
from xcofdk.fwcom import LcFailure
from xcofdk.fwapi import ITask
from xcofdk.fwapi import ITaskError

from _fw.fwssys.fwctrl.fwapibase import _FwApiBase


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
def IsFwAvailable() -> bool:
    """
    Returns availability status of XCOFDK's runtime environment.

    Returns:
    ----------
        True if the runtime environment of XCOFDK has been started,
        False otherwise.

    See:
    -----
        fwapi.StartXcoFW()
    """
    return _FwApiBase.FwApiIsFwAvailable()


def IsLcFailureFree() -> bool:
    """
    Getter for the failure status of current life-cycle (LC) of XCOFDK's RTE.

    Returns:
    ----------
        False if the RTE of XCOFDK has encountered an LC failure, i.e. a qualified
        fatal error, True otherwise.

    See:
    -----
        >>> ITaskError
    """
    return _FwApiBase.FwApiIsLcErrorFree()


def IsTaskRunning(taskUID_ : Union[int, EXmsgPredefinedID]) -> bool:
    """
    Returns:
    ----------
        True if passed in task is in state 'running', False otherwise.

    Parameters:
    -------------
        - xtaskUID_ :
          unique task ID or the pre-defined alias ID of the task to checked for.

    Note:
    ------
        - Former name of this API function is deprecated and not available
          anymore:
              >>> IsXTaskRunning = IsTaskRunning

    See:
    -----
        >>> ITask.isRunning
        >>> ITask.taskUID
        >>> EXmsgPredefinedID.MainTask
    """
    return _FwApiBase.FwApiIsXTaskRunning(taskUID_)


def IsFTPythonVersion() -> bool:
    """
    Returns:
    ----------
        True if the running Python interpreter officially supports
        free-threaded with GIL is disabled, False otherwise.

    Note:
    ------
        - The framework considers the stable version 3.14.0 the first Python
          version officially supporting free-threaded (FT).
        - Any Python version older than 3.14.0 is considered by the framework
          to be not officially supporting free-threaded.
          This includes even the pre-releases of 3.14.0.
    """
    return _FwApiBase.FwApiIsFTPythonVersion()


def IsExperimentalFTPythonVersion() -> bool:
    """
    Returns:
    ----------
        True if the running Python interpreter supports experimental
        free-threaded with GIL is disabled, False otherwise.

    Note:
    ------
        - The framework considers Python versions 3.13 and pre-releases of the
          stable version 3.14.0 supporting experimental free-threaded (FT).
    """
    return _FwApiBase.FwApiIsExperimentalFTPythonVersion()


def GetLcFailure() -> Union[LcFailure, None]:
    """
    Returns:
    ----------
        An instance of class LcFailure if the RTE of XCOFDK has encountered an
        LC failure, None otherwise.

    See:
    -----
        >>> LcFailure
        >>> IsLcFailureFree()
    """
    return _FwApiBase.FwApiGetLcFailure()


def GetXcofdkVersion() -> str:
    """
    Getter for the version of XCOFDK installed.

    Returns:
    ----------
        Version of the installed XCOFDK.
    """
    return _FwApiBase.FwApiGetXcofdkVer()


def GetPythonVersion() -> str:
    """
    Getter for the running Python interpreter's version.

    Returns:
    ----------
        Running Python interpreter's version.
    """
    return _FwApiBase.FwApiGetPythonVer()


def GetPlatform() -> str:
    """
    Getter for the system/OS name of the underlying platform.

    Returns:
    ----------
        One of the string literals below:
            'Linux', 'Darwin', 'Java', 'Windows'
    """
    return _FwApiBase.FwApiGetPlatform()


def GetAvailableCpuCoresCount() -> int:
    """
    Getter for the number of available CPU cores.

    Returns:
    ----------
        Total number of available CPU cores on the host machine if it could be
        retrieved, 0 otherwise.
    """
    return _FwApiBase.FwApiAvailableCpuCoresCount()
