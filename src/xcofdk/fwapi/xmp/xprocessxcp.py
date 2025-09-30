# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xprocessxcp.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from inspect import isclass
from typing  import Union

from xcofdk.fwcom.fwdefs import ERtePolicyID


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class PTException(Exception):
    """
    Instances of this class are exceptions raised during execution of the target
    callback function of a child process, i.e. of an instance of class XProcess.

    Whenever such an exception is raised on target side, the framework will
    provide a reference to the transferred copy of that exception via respective
    property of the affected instance of class XProcess.

    An exception using an instance of this class may appear in two ways:
        - as an abnormal condition encountered on target side and described by a
          (short) message and an error code, or
        - caused by another exception raised on target side.

    Note:
    ------
        - This feature of child processes is available only if the related RTE
          policy for exception tracking of child processes is not disabled.
        - Also, if the byte stream size of an instance of this class exceeds the
          max. size of supplied data specified for the affected child process,
          then a so-called 'wrapped' (and compact) version (which is small
          enough to be transferred) will be used instead.

    See:
    -----
        - class XProcess
        - RtePolicyDisableExceptionTrackingOfChildProcesses()
        >>> PTWrappedException
        >>> ERtePolicyID.eDisableExceptionTrackingOfChildProcesses
    """


    # --------------------------------------------------------------------------
    # c-tor / built-in
    # --------------------------------------------------------------------------
    def __init__(self, xcp_):
        """
        Constructor of new instances of this class.

        Parameters:
        -------------
            - xcp_ :
              Framework's internal exception object this instance refers to.
        """
        self.__xcp = xcp_
        super().__init__(type(self).__name__)


    def __str__(self):
        """
        Returns:
        ----------
            A nicely printable string representation of this instance.
        """
        return str(self.__xcp)
    # --------------------------------------------------------------------------
    #END c-tor / built-in
    # --------------------------------------------------------------------------


    # --------------------------------------------------------------------------
    # API
    # --------------------------------------------------------------------------
    @property
    def isWrappedException(self) -> bool:
        """
        Returns:
        ----------
            True if this instance represents the wrapped version of another
            non-wrapped instance of this class, False otherwise.

        Note:
        ------
            - A wrapped exception is always an instance of class
              PTWrappedException derived from class PTException.

        See:
        -----
            >>> PTException.__init__()
            >>> PTWrappedException
        """
        return isinstance(self, PTWrappedException)


    @property
    def message(self) -> str:
        """
        Returns:
        ----------
            Short description of this instance.

        See:
        -----
            >>> PTException.code
            >>> PTException.reason
        """
        return self.__xcp.message


    @property
    def code(self) -> int:
        """
        Returns:
        ----------
            A positive integer value as the error code of this instance.

        See:
        -----
            >>> PTException.message
            >>> PTException.reason
        """
        return self.__xcp.code


    @property
    def reason(self) -> Union[BaseException, None]:
        """
        Returns:
        ----------
            - None if the creation of this instance is not because of an
              exception raised on target side,
            - an exception object representing the root cause otherwise.

        See:
        -----
            >>> PTException.message
            >>> PTException.code
        """
        return self.__xcp.reason
    # --------------------------------------------------------------------------
    #END API
    # --------------------------------------------------------------------------
#END class PTException


class PTWrappedException(PTException):
    """
    Derived from class PTException, instances of this class represent exceptions
    raised on target side, too.

    A wrapped exception always represent the compact version of a non-wrapped
    instance of class PTException.

    Note:
    ------
        - This feature of child processes is available only if the related RTE
          policy for exception tracking of child processes is not disabled.

    See:
    -----
        - class XProcess
        - RtePolicyDisableExceptionTrackingOfChildProcesses()
        >>> PTException
        >>> ERtePolicyID.eDisableExceptionTrackingOfChildProcesses
    """


    # --------------------------------------------------------------------------
    # c-tor / built-in
    # --------------------------------------------------------------------------
    def __init__(self, xcp_):
        """
        Constructor of new instances of this class.

        Parameters:
        -------------
            - xcp_ :
              Framework's internal exception object this instance refers to.
        """
        self.__xcp = xcp_
        super().__init__(xcp_)


    def __str__(self):
        """
        Returns:
        ----------
            A nicely printable string representation of this instance.
        """
        return str(self.__xcp)
    # --------------------------------------------------------------------------
    #END c-tor / built-in
    # --------------------------------------------------------------------------


    # --------------------------------------------------------------------------
    # API
    # --------------------------------------------------------------------------
    @PTException.message.getter
    def message(self) -> str:
        """
        Returns:
        ----------
            Short description of this instance.

        See:
        -----
            >>> PTWrappedException.code
            >>> PTWrappedException.reason
        """
        return self.__xcp.message


    @PTException.code.getter
    def code(self) -> int:
        """
        Returns:
        ----------
            A positive integer value as the error code of this instance.

        See:
        -----
            >>> PTWrappedException.message
            >>> PTWrappedException.reason
        """
        return self.__xcp.code


    @PTException.reason.getter
    def reason(self) -> str:
        """
        Returns:
        ----------
            - A compact string representation of a non-wrapped instance of class
              PTException this instance is wrapping it.

              It may or may not include callstack and/or traceback of the root
              cause of the exception raised on target side.

        See:
        -----
            >>> PTException.reason
            >>> PTWrappedException.message
            >>> PTWrappedException.code
        """
        return self.__xcp.reason


    @property
    def reasonType(self) -> type:
        """
        Returns:
        ----------
            Type information of the root cause of the exception raised on
            target side.

        See:
        -----
            >>> PTWrappedException.IsReasonType()
        """
        return self.__xcp.reasonType


    def IsReasonType(self, cls_ : type) -> bool:
        """
        Returns:
        ----------
            True if the type argument passed to passes a check for the exact
            matching to the reason type of this instance, False otherwise.

        See:
        -----
            >>> PTWrappedException.reasonType
        """
        return isclass(cls_) and self.reasonType == cls_
    # --------------------------------------------------------------------------
    #END API
    # --------------------------------------------------------------------------
#END class PTWrappedException
