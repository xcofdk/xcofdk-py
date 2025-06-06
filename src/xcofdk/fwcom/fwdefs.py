# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwdefs.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
try:
    from typing import override
except ImportError:
    def override(method_):
        def DecoFunc(*args_, **kwargs_): return method_(*args_, **kwargs_)
        def _DecoFunc(*args_, **kwargs_): return method_(*args_, **kwargs_)
        return _DecoFunc if method_.__name__.startswith('_') else DecoFunc

from typing import Union

from enum        import auto
from enum        import IntEnum
from enum        import unique
from collections import namedtuple


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
CompoundTUID = namedtuple('CompoundTUID', ['uid', 'instNo'])
"""
Compound task unique ID, a tuple type with below named, immutable fields:
    - uid :
      unique task ID,
    - instNo:
      unique task instance number.
"""


@unique
class ERtePolicyID(IntEnum):
    """
    Enum class with its members each define a policy associated with a specific
    RTE configuration item.

    A request to configure the framework is an operation to be done before it
    is started. In other words, RTE configuration enables applications to change
    framework's default runtime behavior during its lifecycle.

    Currently available RTE policies are grouped acc. to their purpose:
        a) addressing control operation to start the framework:
            - eBypassExperimentalFTGuard :
              allows running the framework with an experimental free-threaded
              Python interpreter with GIL disabled, even though it is officially
              not supprted yet,

        b) addressing control operation to wait for framework's shutdown:
           Mutually exclusive policies of this group all make the otherwise
           mandatory request to stop the framework before it is joined an
           optional operation:
            - eEnableAutoStop :
              when joining the framework, the RTE will first wait for all
              currently running tasks to stop before entering the shutdown
              sequence. This RTE policy is enabled by default,
            - eEnableForcedAutoStop :
              when joining the framework, the RTE will first request all
              currently running tasks to stop before entering the shutdown
              sequence,
            - eEnableTerminalMode :
              enables terminal mode of the framework.
              When joining the framework, the RTE will wait for an explicit
              request to stop the framework before entering the shutdown
              sequence,

        c) addressing (availability of) specific subsystems:
            - eDisableSubSystemMessaging :
              disables framework's subsysteem for messaging, i.e. 'xmsg',
            - eDisableSubSystemMultiProcessing :
              disables framework's subsysteem for multiprocessing, i.e. 'xmp',

        d) addressing child processes
            - eDisableExceptionTrackingOfChildProcesses :
              disables the ability of exception tracking of child processes,
              i.e. instances of class XProcess, on target side.
              This feature of exception tracking is enabled by default.

    Note:
    ------
        - This enum class and the order of its members must not be changed or
          extended by additional enum members.

    See:
    -----
        - subpackage xcofdk.fwapi.fwctrl
        - subpackage xcofdk.fwapi.rtecfg
    """

    # a) addressing framework control operation StartXcoFW()
    eBypassExperimentalFTGuard = 0

    # b) addressing framework control operation JoinXcoFW()
    eEnableAutoStop       = auto()
    eEnableForcedAutoStop = auto()
    eEnableTerminalMode   = auto()

    # c) addressing availability of specific subsystems
    eDisableSubSystemMessaging       = auto()
    eDisableSubSystemMultiProcessing = auto()

    # d) addressing child processes
    eDisableExceptionTrackingOfChildProcesses = auto()
#END class ERtePolicyID


@unique
class EExecutionCmdID(IntEnum):
    """
    Enum class to be used as return type of 3-PhXF callback functions.

    Its defined enum members can be used by callback functions to return one of
    the possible four IDs to specify the subsequent action the respective
    callback function expects the framework to do in the given call context:
        - ABORT
          to indicate a request to abort the execution by submitting
          a fatal error,
        - CANCEL
          to indicate a request to cancel the execution, i.e. to break,
          and so leaving the execution imcomplete,
        - STOP
          to indicate a request to stop the execution leaving it as completed,
        - CONTINUE
          to indicate a request to continue the execution by the next 3-PhXF
          callback or run phase iteration, respectively.

    Note:
    ------
        - In order to avoid possible confusion no enum called FAILED is provided
          by this enum class.


    Deprecated API:
    ----------------
    Starting with XCOFDK-py v3.0 below enum class is deprecated and not
    available anymore:
        >>> # enum class 'ETernaryCallbackResultID' due to renaming
        >>> ETernaryCallbackResultID = EExecutionCmdID
    """

    ABORT    = -1
    CANCEL   = auto()
    STOP     = auto()
    CONTINUE = auto()

    @property
    def isOK(self):
        """
        Returns:
        ----------
            True, if this instance equals to CONTINUE, False otherwise.

        See:
        -----
            >>> EExecutionCmdID.isCONTINUE
        """
        return self.isCONTINUE


    @property
    def isNotOK(self):
        """
        Returns:
        ----------
            False, if this instance equals to CONTINUE, True otherwise.


        See:
        -----
            >>> EExecutionCmdID.isOK
        """
        return not self.isCONTINUE


    @property
    def isCONTINUE(self):
        """
        Returns:
        ----------
            True, if this instance equals to CONTINUE, False otherwise.

        See:
        -----
            >>> EExecutionCmdID.isOK
        """
        return self == EExecutionCmdID.CONTINUE


    @property
    def isSTOP(self):
        """
        Returns:
        ----------
            True, if this instance equals to STOP, False otherwise.

        See:
        -----
            >>> EExecutionCmdID.isCANCEL
        """
        return self == EExecutionCmdID.STOP


    @property
    def isCANCEL(self):
        """
        Returns:
        ----------
            True, if this instance equals to CANCEL, False otherwise.

        See:
        -----
            >>> EExecutionCmdID.isSTOP
        """
        return self == EExecutionCmdID.CANCEL


    @property
    def isABORT(self):
        """
        Returns:
        ----------
            True, if this instance equals to ABORT, False otherwise.

        See:
        -----
            >>> EExecutionCmdID.isSTOP
            >>> EExecutionCmdID.isCANCEL
        """
        return self == EExecutionCmdID.ABORT


    @staticmethod
    def FromBool(b_ : Union[bool, None] ):
        """
        Static method to convert a boolean value to its correspondent
        enum member of this class.

        Parameters:
        -------------
            - b_ :
              a boolean value to be converted to its correspondent enum
              member of this class.

        Returns:
        ----------
            - ABORT, if passed in argument resolves to None
              (or more generally is not of a boolean type).
            - STOP, if passed in argument resolves to False.
            - CONTINUE, otherwise.

        See:
        -----
            >>> EExecutionCmdID.isSTOP
            >>> EExecutionCmdID.isABORT
            >>> EExecutionCmdID.isCONTINUE
        """
        if not isinstance(b_, bool):
            res = EExecutionCmdID.ABORT
        else:
            res = EExecutionCmdID.CONTINUE if b_ else EExecutionCmdID.STOP
        return res
#END class EExecutionCmdID
