# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xmputil.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from xcofdk.fwcom.xmpdefs import EProcessStartMethodID

from _fw.fwssys.fwmp.api.xmputilimpl import _XMPUtilImpl


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class XmpUtil:
    """
    This class provides common, auxiliary functions related to the subsystem
    of multiprocessing.

    See:
    -----
        - class XProcess
        >>> XmpUtil.MapStartMethodToID()
        >>> XmpUtil.IsCurrentStartMethod()
        >>> XmpUtil.IsValidStartMethodName()
        >>> XmpUtil.GetCurrentStartMethodID()
        >>> XmpUtil.GetCurrentStartMethodName()
        >>> XmpUtil.GetDefinedStartMethdsNameList()
        >>> XmpUtil.GetSystemDefaultStartMethodID()
        >>> XmpUtil.CurrentProcessStartMethodAsString()


    Deprecated API:
    ----------------
    Starting with XCOFDK-py v3.0 former name of this class is deprecated and
    not available anymore:
        >>> XMPUtil = XmpUtil
    """


    __slots__ = []

    # ------------------------------------------------------------------------------
    # c-tor / built-in
    # ------------------------------------------------------------------------------
    def __init__(self):
        pass
    # ------------------------------------------------------------------------------
    #END c-tor / built-in
    # ------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # API
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
            True if passed in ID identifies current process start method as
            defined by Python's multiprocessing package, False otherwise.

        See:
        -----
            >>> EProcessStartMethodID
            >>> XmpUtil.GetCurrentStartMethodID()
        """
        return _XMPUtilImpl._MPIsCurrentStartMethod(startMethodID_)


    @staticmethod
    def IsCurrentStartMethodSystemDefault() -> bool:
        """
        Returns:
        ----------
            True if current process start method is system default, False
            otherwise.

        See:
        -----
            >>> EProcessStartMethodID
            >>> XmpUtil.GetCurrentStartMethodID()
            >>> XmpUtil.GetSystemDefaultStartMethodID()
        """
        return _XMPUtilImpl._MPIsCurrentStartMethod(XmpUtil.GetSystemDefaultStartMethodID())


    @staticmethod
    def IsValidStartMethodName(startMethod_ : str) -> bool:
        """
        Parameters:
        -------------
            - startMethod_ :
              case-sensitive name of the process start method to be checked.

        Returns:
        ----------
            True if passed in name can be mapped to one of the IDs defined by
            the enum class EProcessStartMethodID, False otherwise.

        See:
        -----
            >>> EProcessStartMethodID
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
            >>> EProcessStartMethodID
        """
        return _XMPUtilImpl._MPGetDefinedStartMethdsNameList()


    @staticmethod
    def GetSystemDefaultStartMethodID() -> EProcessStartMethodID:
        """
        Getter function for platform-dependent default start method as defined
        by Python's multiprocessing package, that is:
            - either fork or forkserver for linux platforms, and
            - spawn for other platforms.

        Returns:
        ----------
            EProcessStartMethodID.Fork for linux platforms,
            EProcessStartMethodID.Spawn otherwise.

        See:
        -----
            >>> EProcessStartMethodID
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
            >>> EProcessStartMethodID
            >>> XmpUtil.IsCurrentStartMethod()
            >>> XmpUtil.GetCurrentStartMethodName()
        """
        return _XMPUtilImpl._MPGetCurrentStartMethodID()


    @staticmethod
    def GetCurrentStartMethodName() -> str:
        """
        Returns:
        ----------
            if current process start method (as defined by Python's
            multiprocessing package) can be mapped to one of the IDs defined
            by the enum class EProcessStartMethodID, then that ID's respective
            name, None otherwise.

        See:
        -----
            >>> EProcessStartMethodID
            >>> XmpUtil.GetCurrentStartMethodID()
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
            if passed in name can be mapped to one of the IDs defined by
            the enum class EProcessStartMethodID, then that ID, None otherwise.

        See:
        -----
            >>> EProcessStartMethodID
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
    # ------------------------------------------------------------------------------
    #END API
    # ------------------------------------------------------------------------------
#END class XmpUtil
