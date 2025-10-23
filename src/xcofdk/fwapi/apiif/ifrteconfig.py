# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : ifrteconfig.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from xcofdk.fwcom.fwdefs import ERtePolicyID

 
# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class IRteConfig:
    """
    This class represents common, read-only API of the current RTE configuration
    of the framework.

    See:
    -----
        >>> ERtePolicyID
    """

    __slots__ = []


    # ------------------------------------------------------------------------------
    # c-tor / built-in
    # ------------------------------------------------------------------------------
    def __init__(self):
        pass


    def __str__(self) -> str:
        """
        Returns:
        ----------
            A nicely printable string representation of this instance.
        """
        pass
    # ------------------------------------------------------------------------------
    #END c-tor / built-in
    # ------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # API
    # ------------------------------------------------------------------------------
    @property
    def isValid(self) -> bool:
        """
        Returns:
        ----------
           True if current RTE configuration is valid, False otherwise.
        """
        pass


    @property
    def isAutoStopEnabled(self) -> bool:
        """
        Returns:
        ----------
           True if the RTE policy for AutoStop is enabled, False otherwise.
        """
        pass


    @property
    def isForcedAutoStopEnabled(self) -> bool:
        """
        Returns:
        ----------
           True if the RTE policy for ForcedAutoStop is enabled, False otherwise.
        """
        pass


    @property
    def isTerminalModeEnabled(self) -> bool:
        """
        Returns:
        ----------
           True if the RTE policy for TerminalMode is enabled, False otherwise.
        """
        pass


    @property
    def isExperimentalFreeThreadingBypassed(self) -> bool:
        """
        Returns:
        ----------
           True if the RTE policy to allow running the framework with an
           experimental free-threaded (FT) Python interpreter with GIL is
           disabled, False otherwise.

        Note:
        ------
            - The framework considers Python versions 3.13 and pre-releases of
              the stable version 3.14.0 supporting experimental free-threaded
              (FT).
        """
        pass


    @property
    def isSubSystemMessagingDisabled(self) -> bool:
        """
        Returns:
        ----------
           True if the RTE policy to disable framework's subsystem for messaging
           is enabled, False otherwise.
        """
        pass


    @property
    def isSubSystemMultiProcessingDisabled(self) -> bool:
        """
        Returns:
        ----------
           True if the RTE policy to disable framework's subsystem for
           multiprocessing is enabled, False otherwise.
        """
        pass


    @property
    def isExceptionTrackingOfChildProcessesDisabled(self) -> bool:
        """
        Returns:
        ----------
           True if the RTE policy for exception tracking of child processes is
           disabled, False otherwise.
        """
        pass


    @property
    def isLogRDConsoleSinkDisabled(self) -> bool:
        """
        Returns:
        ----------
           True if the RTE policy to disable console output is set, False
           otherwise.
        """
        pass


    @property
    def isLogRDFileSinkEnabled(self) -> bool:
        """
        Returns:
        ----------
           True if the RTE policy to enable log output to a file sink is
           enabled, False otherwise.
        """
        pass


    @property
    def isLogRDTcpSinkEnabled(self) -> bool:
        """
        Returns:
        ----------
           True if the RTE policy to enable log output to a TCP connection
           sink is enabled, False otherwise.
        """
        pass
    # ------------------------------------------------------------------------------
    #END API
    # ------------------------------------------------------------------------------
#END class IRteConfig
