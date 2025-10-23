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
from xcofdk.fwcom.fwdefs            import ELineEnding
from xcofdk.fwapi.apiif.ifrteconfig import IRteConfig

from _fw.fwssys.fwcore.types.commontypes import _CommonDefines
from _fwa.fwrtecfg.fwrteconfig           import _FwRteConfig

 
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
        >>> RtePolicyEnableLogRDTcpSink()
        >>> RtePolicyEnableLogRDFileSink()
        >>> RtePolicyEnableForcedAutoStop()
        >>> RtePolicyDisableLogRDConsoleSink()
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
        return self.__i._isValid


    @IRteConfig.isAutoStopEnabled.getter
    def isAutoStopEnabled(self) -> bool:
        """
        See:
        -----
            >>> IRteConfig.isAutoStopEnabled
            >>> RtePolicyEnableAutoStop()
        """
        return self.__i._isAutoStopEnabled


    @IRteConfig.isForcedAutoStopEnabled.getter
    def isForcedAutoStopEnabled(self) -> bool:
        """
        See:
        -----
            >>> IRteConfig.isForcedAutoStopEnabled
            >>> RtePolicyEnableForcedAutoStop()
        """
        return self.__i._isForcedAutoStopEnabled


    @IRteConfig.isTerminalModeEnabled.getter
    def isTerminalModeEnabled(self) -> bool:
        """
        See:
        -----
            >>> IRteConfig.isTerminalModeEnabled
            >>> RtePolicyEnableTerminalMode()
        """
        return self.__i._isTerminalModeEnabled


    @IRteConfig.isExperimentalFreeThreadingBypassed.getter
    def isExperimentalFreeThreadingBypassed(self) -> bool:
        """
        See:
        -----
            >>> IRteConfig.isExperimentalFreeThreadingBypassed
            >>> RtePolicyBypassExperimentalFreeThreadingGuard()
        """
        return self.__i._isExperimentalFreeThreadingBypassed


    @IRteConfig.isSubSystemMessagingDisabled.getter
    def isSubSystemMessagingDisabled(self) -> bool:
        """
        See:
        -----
            >>> IRteConfig.isSubSystemMessagingDisabled
            >>> RtePolicyDisableSubSystemMessaging()
        """
        return self.__i._isSubSystemMessagingDisabled


    @IRteConfig.isSubSystemMultiProcessingDisabled.getter
    def isSubSystemMultiProcessingDisabled(self) -> bool:
        """
        See:
        -----
            >>> IRteConfig.isSubSystemMultiProcessingDisabled
            >>> RtePolicyDisableSubSystemMultiProcessing()
        """
        return self.__i._isSubSystemMultiProcessingDisabled


    @IRteConfig.isExceptionTrackingOfChildProcessesDisabled.getter
    def isExceptionTrackingOfChildProcessesDisabled(self) -> bool:
        """
        See:
        -----
            >>> IRteConfig.isExceptionTrackingOfChildProcessesDisabled
            >>> RtePolicyDisableExceptionTrackingOfChildProcesses()
        """
        return self.__i._isExceptionTrackingOfChildProcessesDisabled


    @IRteConfig.isLogRDConsoleSinkDisabled.getter
    def isLogRDConsoleSinkDisabled(self) -> bool:
        """
        See:
        -----
            >>> IRteConfig.isLogRDConsoleSinkDisabled
            >>> RtePolicyDisableLogRDConsoleSink()
        """
        return self.__i._isLogRDConsoleSinkDisabled


    @IRteConfig.isLogRDFileSinkEnabled.getter
    def isLogRDFileSinkEnabled(self) -> bool:
        """
        See:
        -----
            >>> IRteConfig.isLogRDFileSinkEnabled
            >>> RtePolicyEnableLogRDFileSink()
        """
        return self.__i._isLogRDFileSinkEnabled


    @IRteConfig.isLogRDTcpSinkEnabled.getter
    def isLogRDTcpSinkEnabled(self) -> bool:
        """
        See:
        -----
            >>> IRteConfig.isLogRDTcpSinkEnabled
            >>> RtePolicyEnableLogRDTcpSink()
        """
        return self.__i._isLogRDTcpSinkEnabled
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
    _FwRteConfig._ConfigureRtePolicy(ERtePolicyID.eEnableAutoStop)
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
    _FwRteConfig._ConfigureRtePolicy(ERtePolicyID.eEnableForcedAutoStop)
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
    _FwRteConfig._ConfigureRtePolicy(ERtePolicyID.eEnableTerminalMode)
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
    _FwRteConfig._ConfigureRtePolicy(ERtePolicyID.eDisableSubSystemMessaging)
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
    _FwRteConfig._ConfigureRtePolicy(ERtePolicyID.eDisableSubSystemMultiProcessing)
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
    _FwRteConfig._ConfigureRtePolicy(ERtePolicyID.eDisableExceptionTrackingOfChildProcesses)
    return RteConfig()


def RtePolicyBypassExperimentalFreeThreadingGuard() -> IRteConfig:
    """
    Request to allow running the framework with an experimental free-threaded
    Python interpreter with GIL disabled, even though this runtime condition of
    the framework is officially not supprted.

    Returns:
    ----------
        RTE configuration after the requested policy change.

    Note:
    ------
        - The framework considers Python versions 3.13 and pre-releases of the
          stable version 3.14.0 supporting experimental free-threaded (FT).

    See:
    -----
        >>> IRteConfig.isValid
        >>> ERtePolicyID.eBypassExperimentalFTGuard
        >>> RtePolicyConfigure()
    """
    _FwRteConfig._ConfigureRtePolicy(ERtePolicyID.eBypassExperimentalFTGuard)
    return RteConfig()


def RtePolicyDisableLogRDConsoleSink() -> IRteConfig:
    """
    Request to disable console output.

    Returns:
    ----------
        RTE configuration after the requested policy change.

    See:
    -----
        >>> IRteConfig.isValid
        >>> ERtePolicyID.eDisableLogRDConsoleSink
        >>> RtePolicyConfigure()
    """
    _FwRteConfig._ConfigureRtePolicy(ERtePolicyID.eDisableLogRDConsoleSink)
    return RteConfig()


def RtePolicyEnableLogRDFileSink(filePath_ : Union[str, None] =None, bFileModeAppend_ =False, fileEncoding_ : Union[str, None] =_CommonDefines._STR_ENCODING_UTF8) -> IRteConfig:
    """
    Request to enable log output to the specified file sink.

    Parameters:
    -------------
        - filePath_ :
          pathname (absolute or relative to the current working directory) of
          the file to be used for log output to:
              - if None, then the path to the current working directory will
                be assumed as specified,
              - if the path specifies an existing directory, then an
                auto-generated file name (in that directory) will be used,
                for example:
                    'xcofdk_log__14_23_38_418.txt'
                The format used for the auto-generated file name is:
                    'xcofdk_log__'<HH>_<MM>_<SS>_<MS>'.txt'
                    HH : hours
                    MM : minutes
                    SS : seconds
                    MS : milliseconds
              - the pathname as is otherwise.
        - bFileModeAppend_ :
          if True then the specified file will be opened with file open mode
          'a' (for appending if exists), otherwise it will be opened with 'w'
          (for writing).
        - fileEncoding_ :
          the encoding to be used for the specified file:
              - if None, then system or platform default will be used,
              - the specified encoding otherwise.
          It defaults to 'utf-8'.

    Returns:
    ----------
        RTE configuration after the requested policy change.

    See:
    -----
        >>> IRteConfig.isValid
        >>> ERtePolicyID.eEnableLogRDFileSink
        >>> RtePolicyConfigure()
    """
    _FwRteConfig._ConfigureRtePolicy(ERtePolicyID.eEnableLogRDFileSink, rdFileSinkPath_=filePath_, rdFileSinkEncoding_=fileEncoding_, rdFileSinkAppend_=bFileModeAppend_)
    return RteConfig()


def RtePolicyEnableLogRDTcpSink(ipv4Addr_ : str, port_ : int, lineEnding_ : ELineEnding =ELineEnding.NOLE) -> IRteConfig:
    """
    Request to enable log output to the specified TCP connection sink.

    Parameters:
    -------------
        - ipv4Addr_ :
          the IPv4 address (specified in dotted decimal notation) of the host
          machine the application is running on,
        - port_ :
          the port number of the host machine to be used for the connection,
        - lineEnding_ :
          the line ending to be used for sending string objects via the
          specified TCP connection, it defaults to NOLE, i.e. no line ending.

    Returns:
    ----------
        RTE configuration after the requested policy change.

    Note:
    ------
        - The RTE configuration API for redirection to TCP sinks is designed and
          provided 'for development purposes only'
          (in a development/local/private environment).
        - Especially, the underlying implementation does not incorporate any
          kind of precautions in terms of secure connections.
        - Hence, this API function shall not be used in a production code or
          whenever seccure network requirements are of concern.
        - A new, separate API function for redirection via secure connections
          is part of framework's PM-backlog for future featucres and will be
          announced accordingly as soon as available.

    See:
    -----
        >>> ELineEnding
        >>> IRteConfig.isValid
        >>> ERtePolicyID.eEnableLogRDTcpSink
        >>> RtePolicyConfigure()
    """
    _FwRteConfig._ConfigureRtePolicy(ERtePolicyID.eEnableLogRDTcpSink, rdTcpSinkIpAddr_=ipv4Addr_, rdTcpSinkPort_=port_, rdTcpSinkLineEnding_=lineEnding_)
    return RteConfig()


def RtePolicyConfigure( fwRtePolicy_         : Union[ERtePolicyID, List[ERtePolicyID]]
                      , rdFileSinkPath_      : Union[str, None] =None
                      , rdFileSinkEncoding_  : Union[str, None] =_CommonDefines._STR_ENCODING_UTF8
                      , rdFileSinkAppend_    : bool             =False
                      , rdTcpSinkIpAddr_     : str              =None
                      , rdTcpSinkPort_       : int              =None
                      , rdTcpSinkLineEnding_ : ELineEnding      =ELineEnding.NOLE ) -> IRteConfig:
    """
    Request to change current RTE configuration prior to start of the framework.

    As long as current RTE configuration is valid, this function will try to
    change the configuration for the specified policies one by one in their
    given order.

    Parameters:
    -------------
        - fwRtePolicy_ :
          A single or a list of RTE policy IDs
        - rdFileSinkPath_ :
          same as 'filePath_' in RtePolicyEnableLogRDFileSink() above,
        - rdFileSinkEncoding_ :
          same as 'fileEncoding_' in RtePolicyEnableLogRDFileSink() above,
        - rdFileSinkAppend_ :
          same as 'bFileModeAppend_' in RtePolicyEnableLogRDFileSink() above,
        - rdTcpSinkIpAddr_ :
          same as 'ipv4Addr_' in RtePolicyEnableLogRDTcpSink() above,
        - rdTcpSinkPort_ :
          same as 'port_' in RtePolicyEnableLogRDTcpSink() above,
        - rdTcpSinkLineEnding_ :
          same as 'lineEnding_' in RtePolicyEnableLogRDTcpSink() above,

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
        - Current implementation uses a 'non-secure' connection for the TCP
          redirection sink.

    See:
    -----
        >>> IRteConfig.isValid
        >>> ERtePolicyID
        >>> RtePolicyGetConfig()
        >>> RtePolicyEnableLogRDFileSink()
        >>> RtePolicyEnableLogRDTcpSink()
    """
    _FwRteConfig._ConfigureRtePolicy( fwRtePolicy_
                                    , rdFileSinkPath_=rdFileSinkPath_
                                    , rdFileSinkEncoding_=rdFileSinkEncoding_
                                    , rdFileSinkAppend_=rdFileSinkAppend_
                                    , rdTcpSinkIpAddr_=rdTcpSinkIpAddr_
                                    , rdTcpSinkPort_=rdTcpSinkPort_
                                    , rdTcpSinkLineEnding_=rdTcpSinkLineEnding_)
    return RteConfig()
