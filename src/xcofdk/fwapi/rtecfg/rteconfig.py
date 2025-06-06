# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : rteconfig.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from typing import List
from typing import Union

from xcofdk.fwcom.fwdefs            import ERtePolicyID
from xcofdk.fwapi.apiif.ifrteconfig import IRteConfig

from _fwa.fwrteconfig import _FwRteConfig

 
# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class RteConfig(IRteConfig):
    """
    This class reprsents current RTE configuration of the framework.

    Note:
    ------
        - Default RTE configuration is always valid.
        - Once current RTE configuration becomes invalid (as result of a
          mal-configuration) it remains invalid.
        - The framework will refuse to start with an invalid RTE configuration.
        - Once the framework is started, requests to re-configure the RTE will
          be denied.

    See:
    -----
        >>> IRteConfig
        >>> RtePolicyGetConfig()
        >>> RtePolicyConfigure()
        >>> RtePolicyEnableAutoStop()
        >>> RtePolicyEnableTerminalMode()
        >>> RtePolicyEnableForcedAutoStop()
        >>> RtePolicyDisableSubSystemMessaging()
        >>> RtePolicyDisableSubSystemMultiProcessing()
        >>> RtePolicyBypassExperimentalFreeThreadingGuard()
        >>> RtePolicyDisableExceptionTrackingOfChildProcesses()
    """

    __slots__ = [ '__i' ]

    # ------------------------------------------------------------------------------
    # c-tor / built-in
    # ------------------------------------------------------------------------------
    def __init__(self):
        """
        Constructor (or initializer) of instances of this class.
        """
        super().__init__()
        self.__i = _FwRteConfig._GetInstance()


    def __str__(self):
        """
        See:
        -----
            >>> IRteConfig.__str__()
        """
        return self.__i.__str__()
    # ------------------------------------------------------------------------------
    #END c-tor / built-in
    # ------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # API
    # ------------------------------------------------------------------------------
    @IRteConfig.isValid.getter
    def isValid(self) -> bool:
        """
        See:
        -----
            >>> IRteConfig.isValid
        """
        return self.__i.isValid


    @IRteConfig.isAutoStopEnabled.getter
    def isAutoStopEnabled(self) -> bool:
        """
        See:
        -----
            >>> IRteConfig.isAutoStopEnabled
        """
        return self.__i.isAutoStopEnabled


    @IRteConfig.isForcedAutoStopEnabled.getter
    def isForcedAutoStopEnabled(self) -> bool:
        """
        See:
        -----
            >>> IRteConfig.isForcedAutoStopEnabled
        """
        return self.__i.isForcedAutoStopEnabled


    @IRteConfig.isTerminalModeEnabled.getter
    def isTerminalModeEnabled(self) -> bool:
        """
        See:
        -----
            >>> IRteConfig.isTerminalModeEnabled
        """
        return self.__i.isTerminalModeEnabled


    @IRteConfig.isExperimentalFreeThreadingBypassed.getter
    def isExperimentalFreeThreadingBypassed(self) -> bool:
        """
        See:
        -----
            >>> IRteConfig.isExperimentalFreeThreadingBypassed
        """
        return self.__i.isExperimentalFreeThreadingBypassed


    @IRteConfig.isSubSystemMessagingDisabled.getter
    def isSubSystemMessagingDisabled(self) -> bool:
        """
        See:
        -----
            >>> IRteConfig.isSubSystemMessagingDisabled
        """
        return self.__i.isSubSystemMessagingDisabled


    @IRteConfig.isSubSystemMultiProcessingDisabled.getter
    def isSubSystemMultiProcessingDisabled(self) -> bool:
        """
        See:
        -----
            >>> IRteConfig.isSubSystemMultiProcessingDisabled
        """
        return self.__i.isSubSystemMultiProcessingDisabled


    @IRteConfig.isExceptionTrackingOfChildProcessesDisabled.getter
    def isExceptionTrackingOfChildProcessesDisabled(self) -> bool:
        """
        See:
        -----
            >>> IRteConfig.isExceptionTrackingOfChildProcessesDisabled
        """
        return self.__i.isExceptionTrackingOfChildProcessesDisabled
    # ------------------------------------------------------------------------------
    #END API
    # ------------------------------------------------------------------------------
#END class RteConfig


def RtePolicyGetConfig() -> IRteConfig:
    """
    Returns:
    ----------
        Current RTE configuration.

    See:
    -----
        >>> IRteConfig.isValid
        >>> ERtePolicyID
        >>> RtePolicyConfigure()
    """
    return RteConfig()


def RtePolicyEnableAutoStop() -> IRteConfig:
    """
    Request to enable RTE policy for AutoStop.

    Returns:
    ----------
        RTE configuration after the requested policy change.

    Note:
    ------
        - The RTE policies below are mutually exclusive:
              - AutoStop
              - ForcedAutoStop
              - TerminalMode
        - The RTE policy AutoStop is enabled by default.

    See:
    -----
        >>> IRteConfig.isValid
        >>> ERtePolicyID.eEnableAutoStop
        >>> RtePolicyConfigure()
        >>> RtePolicyEnableTerminalMode()
        >>> RtePolicyEnableForcedAutoStop()
    """
    _FwRteConfig._ConfigureRtePolicy(rtePolicy_=ERtePolicyID.eEnableAutoStop)
    return RteConfig()


def RtePolicyEnableForcedAutoStop() -> IRteConfig:
    """
    Request to enable RTE policy for ForcedAutoStop.

    Returns:
    ----------
        RTE configuration after the requested policy change.

    Note:
    ------
        - The RTE policies below are mutually exclusive:
              - AutoStop
              - ForcedAutoStop
              - TerminalMode
        - The RTE policy AutoStop is enabled by default.

    See:
    -----
        >>> IRteConfig.isValid
        >>> ERtePolicyID.eEnableForcedAutoStop
        >>> RtePolicyConfigure()
        >>> RtePolicyEnableAutoStop()
        >>> RtePolicyEnableTerminalMode()
    """
    _FwRteConfig._ConfigureRtePolicy(rtePolicy_=ERtePolicyID.eEnableForcedAutoStop)
    return RteConfig()


def RtePolicyEnableTerminalMode() -> IRteConfig:
    """
    Request to enable RTE policy for TerminalMode.

    Returns:
    ----------
        RTE configuration after the requested policy change.

    Note:
    ------
        - The RTE policies below are mutually exclusive:
              - AutoStop
              - ForcedAutoStop
              - TerminalMode
        - The RTE policy AutoStop is enabled by default.

    See:
    -----
        >>> IRteConfig.isValid
        >>> ERtePolicyID.eEnableTerminalMode
        >>> RtePolicyConfigure()
        >>> RtePolicyEnableAutoStop()
        >>> RtePolicyEnableForcedAutoStop()
    """
    _FwRteConfig._ConfigureRtePolicy(rtePolicy_=ERtePolicyID.eEnableTerminalMode)
    return RteConfig()


def RtePolicyDisableSubSystemMessaging() -> IRteConfig:
    """
    Request to disable framework's subsystem for messaging, i.e. 'xmsg'.

    Returns:
    ----------
        RTE configuration after the requested policy change.

    See:
    -----
        >>> IRteConfig.isValid
        >>> ERtePolicyID.eDisableSubSystemMessaging
        >>> RtePolicyConfigure()
    """
    _FwRteConfig._ConfigureRtePolicy(rtePolicy_=ERtePolicyID.eDisableSubSystemMessaging)
    return RteConfig()


def RtePolicyDisableSubSystemMultiProcessing() -> IRteConfig:
    """
    Request to disable framework's subsystem for multiprocessing, i.e. 'xmp'.

    Returns:
    ----------
        RTE configuration after the requested policy change.

    See:
    -----
        >>> IRteConfig.isValid
        >>> ERtePolicyID.eDisableSubSystemMultiProcessing
        >>> RtePolicyConfigure()
    """
    _FwRteConfig._ConfigureRtePolicy(rtePolicy_=ERtePolicyID.eDisableSubSystemMultiProcessing)
    return RteConfig()


def RtePolicyDisableExceptionTrackingOfChildProcesses() -> IRteConfig:
    """
    Request to disable the ability of the framework for exception tracking of
    child processes, i.e. instances of class XProcess, on target side.

    Returns:
    ----------
        RTE configuration after the requested policy change.

    Note:
    ------
        Exception tracking of child processes is enabled by default.

    See:
    -----
        >>> IRteConfig.isValid
        >>> ERtePolicyID.eDisableExceptionTrackingOfChildProcesses
        >>> RtePolicyConfigure()
    """
    _FwRteConfig._ConfigureRtePolicy(rtePolicy_=ERtePolicyID.eDisableExceptionTrackingOfChildProcesses)
    return RteConfig()


def RtePolicyBypassExperimentalFreeThreadingGuard() -> IRteConfig:
    """
    Request to allow running the framework with an experimental free-threaded
    Python interpreter with GIL disabled, even though this runtime condition of
    the framework is officially not supprted yet.

    Returns:
    ----------
        RTE configuration after the requested policy change.

    See:
    -----
        >>> IRteConfig.isValid
        >>> ERtePolicyID.eBypassExperimentalFTGuard
        >>> RtePolicyConfigure()
    """
    _FwRteConfig._ConfigureRtePolicy(rtePolicy_=ERtePolicyID.eBypassExperimentalFTGuard)
    return RteConfig()


def RtePolicyConfigure(fwRtePolicy_ : Union[ERtePolicyID, List[ERtePolicyID]]) -> IRteConfig:
    """
    Request to change current RTE configuration prior to start of the framework.

    As long as current RTE configuration is valid, this function will try to
    change the configuration for the specified policies one by one in their
    given order.

    Parameters:
    -------------
        - fwRtePolicy_ :
          A single or a list of RTE policy IDs

    Returns:
    ----------
        RTE configuration after the requested policy change(s).

        Note that the current RTE configuration will remain invalid, as soon as
        a mal-configuration (if any) is detected.
        If happend so, then a subsequent request to start the framework will be
        denied.

    Note:
    ------
        - Once the framework is started, requests to re-configure the RTE will
          be denied.
        - The RTE policies below are mutually exclusive:
              - AutoStop
              - ForcedAutoStop
              - TerminalMode
        - The RTE policy AutoStop is enabled by default.

    See:
    -----
        >>> IRteConfig.isValid
        >>> ERtePolicyID
        >>> RtePolicyGetConfig()
    """
    _FwRteConfig._ConfigureRtePolicy(rtePolicy_=fwRtePolicy_)
    return RteConfig()
