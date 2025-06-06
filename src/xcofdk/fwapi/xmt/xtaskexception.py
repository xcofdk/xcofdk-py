# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xtaskexception.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from _fw.fwssys.fwerrh.logs.xcoexception import _XTaskXcpBase


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class XTaskException(_XTaskXcpBase):
    """
    Instances of this class are exceptions raised by the framework.

    The purpose of this class is to inform currently running application task,
    i.e. an instance of class RCTask or XTask, about submitted fatal errors
    which need to be qualified or aproved.

    For more detail refer to the respective wiki page discussing error handling.
    """


    def __init__(self, xcp_ : Exception):
        """
        Constructor (or initializer) of this instance.

        Parameters:
        -------------
            - xcp_ :
              framework's internal exception object this instance is made around.

        Note:
        ------
            - Instances of this class are created by the framework only.
            - They are raised during the qualificaiton procedure of submitted
              fatal errors.
        """
        super().__init__(xcp_)


    def __str__(self):
        """
        Returns:
        ----------
            A nicely printable string object as representation of this instance.
        """
        return super().__str__()


    @property
    def isDieException(self):
        """
        Returns:
        ----------
            True if this instance is created due to enabled configuration of
            'die-mode', False otherwise.
        """
        return super().isDieException


    @property
    def uniqueID(self) -> int:
        """
        Returns:
        ----------
            An integer value as unique ID of this instance.
        """
        return super().uniqueID


    @property
    def message(self) -> str:
        """
        Returns:
        ----------
            A string object giving (short) description of the exception cause
            as the respective fatal error was submitted.
        """
        return super().message


    @property
    def errorCode(self) -> int:
        """
        Returns:
        ----------
            None if not available, otherwise an integer value as the error code
            assigned when the respective fatal error was submitted.

        Note:
        ------
            The error code (if any) of fatal error messages submitted are always
            positive integer values, unless they were submitted by the framework.

        See:
        -----
            - xlogif.LogFatalEC()
            - xlogif.LogExceptionEC()
        """
        return super().errorCode


    @property
    def callstack(self) -> str:
        """
        Returns:
        ----------
            None if not available, otherwise the callstack retrieved at the time
            of detection of the respective fatal error.
        """
        return super().callstack


    @property
    def traceback(self) -> str:
        """
        Returns:
        ----------
            None if not available, otherwise the traceback retrieved at the time
            of detection of the respective fatal error.
        """
        return super().traceback
#END class XTaskException
