# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwutil.py
#
# Copyright(c) 2024 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from xcofdk._xcofw.fw.fwssys.fwcore.apiimpl.fwapibase import _FwApiBase


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
        True if the RTE of XCOFDK has encountered an LC failure, i.e. a qualified
        fatal error, False otherwise.

    Note:
    ------
        Error handling is described in class description of XTaskError.

    See:
    -----
        XTaskError
    """
    return _FwApiBase.FwApiIsLcErrorFree()


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
    Getter for running Python interpreter's version.

    Returns:
    ----------
        Running Python interpreter's version if the framework is available,
        None otherwise.
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
