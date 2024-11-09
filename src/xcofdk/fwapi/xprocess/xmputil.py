# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xmputil.py
#
# Copyright(c) 2024 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from xcofdk.fwcom.xmpdefs import EProcessStartMethodID

from xcofdk._xcofw.fw.fwssys.fwmp.apiimpl.xmputilimpl import _XMPUtilImpl


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class XMPUtil:
    """
    This class provides common, auxiliary functions related to the subsystem
    of multiprocessing.

    Note:
    ------
        - For an introduction of framework's subsystem of multiprocessing refer
          to class description of XProcess.
        - For details regarding process start method refer to section 'Process
          start method' of the abovementioned class description.

    See:
    -----
        - XProcess
    """


    __slots__ = []

    def __init__(self):
        pass


    # ------------------------------------------------------------------------------
    # Interface - MP read-only access to process start method
    # ------------------------------------------------------------------------------
    @staticmethod
    def IsCurrentStartMethod(startMethodID_ : EProcessStartMethodID) -> bool:
        """
        Parameters:
        -------------
            - startMethodID_ :
              ID of the process start method to be checked.

        Returns:
        ----------
            True if passed in ID identifying current process start method as
            defined by Python's multiprocessing package, False otherwise.

        See:
        -----
            - EProcessStartMethodID
            - XMPUtil.GetCurrentStartMethodID()
        """
        return _XMPUtilImpl._MPIsCurrentStartMethod(startMethodID_)


    @staticmethod
    def IsValidStartMethodName(startMethod_ : str) -> bool:
        """
        Parameters:
        -------------
            - startMethod_ :
              case-sensitive name of the process start method to be checked.

        Returns:
        ----------
            True if passed in name can be mapped to one the IDs defined
            by the enum class EProcessStartMethodID, False otherwise.

        See:
        -----
            - EProcessStartMethodID
        """
        return _XMPUtilImpl._MPIsValidStartMethodName(startMethod_)


    @staticmethod
    def GetDefinedStartMethdsNameList() -> list:
        """
        Returns:
        ----------
            non-empty list of string literals (defined by Python's
            multiprocessing package as available process start methods) for
            which a corresponding ID is provided by the enum class
            EProcessStartMethodID.

        See:
        -----
            - EProcessStartMethodID
        """
        return _XMPUtilImpl._MPGetDefinedStartMethdsNameList()


    @staticmethod
    def GetSystemDefaultStartMethodID() -> EProcessStartMethodID:
        """
        Getter function for platform-dependent default start method as defined
        by Python's multiprocessing package, that is:
            - fork for linux platforms, and
            - spawn for other platforms.

        Returns:
        ----------
            EProcessStartMethodID.Fork for linux platforms,
            EProcessStartMethodID.Spawn otherwise.

        See:
        -----
            - EProcessStartMethodID
        """
        return _XMPUtilImpl._MPGetSystemDefaultStartMethodID()


    @staticmethod
    def GetCurrentStartMethodID() -> EProcessStartMethodID:
        """
        Returns:
        ----------
            if current process start method (as defined by Python's
            multiprocessing package) can be mapped to one the IDs defined by
            enum class EProcessStartMethodID, then that ID, None otherwise.

        See:
        -----
            - EProcessStartMethodID
            - XMPUtil.IsCurrentStartMethod()
            - XMPUtil.GetCurrentStartMethodName()
        """
        return _XMPUtilImpl._MPGetCurrentStartMethodID()


    @staticmethod
    def GetCurrentStartMethodName() -> str:
        """
        Returns:
        ----------
            if current process start method (as defined by Python's
            multiprocessing package) can be mapped to one the IDs defined by
            enum class EProcessStartMethodID, then that ID's respective name,
            None otherwise.

        See:
        -----
            - EProcessStartMethodID
            - XMPUtil.GetCurrentStartMethodID()
        """
        return _XMPUtilImpl._MPGetCurrentStartMethodName()


    @staticmethod
    def MapStartMethodToID(startMethod_ : str) -> EProcessStartMethodID:
        """
        Parameters:
        -------------
            - startMethod_ :
              case-sensitive name of the process start method to be mapped.

        Returns:
        ----------
            if passed in name can be mapped to one the IDs defined by the enum
            class EProcessStartMethodID, then that ID, None otherwise.

        See:
        -----
            - EProcessStartMethodID
        """
        return _XMPUtilImpl._MPMapStartMethodToID(startMethod_)


    @staticmethod
    def CurrentProcessStartMethodAsString() -> str:
        """
        Returns:
        ----------
            formatted string object representing current process start method
            (as defined by Python's multiprocessing package) detected by the
            framework, alongside a few more related information.
        """
        return _XMPUtilImpl._MPCurrentStartMethodAsString()
#END class XMPUtil
