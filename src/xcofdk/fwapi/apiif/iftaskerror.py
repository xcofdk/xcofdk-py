# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : ifxtaskerror.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from typing import Union


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class ITaskError:
    """
    Instances of this interface class represent common API of qualified task
    error instances submitted by either by the application or by the framework
    and associated to the affected task instance managed and monitored by the
    framework.

    Note:
    ------
        - Except for qualified fatal errors, the validity of the information
          an instance of this class delivers is bound to the scope of its
          creation.

        See:
        -----
            - class XTaskError
            - module xlogif
            >>> ITaskError.isFatalError
            >>> ITaskError.uniqueID
            >>> ITaskError.message
            >>> ITaskError.errorCode
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
    @property
    def isFatalError(self) -> bool:
        """
        Returns:
        ----------
            True if this instance is a fatal error, False otherwise,
            i.e. a non-fatal error, also called user error.

        Note:
        ------
            - A fatal error at this level of abstraction is always a
              qualified one.

        See:
        -----
            XTaskError
        """
        pass


    @property
    def uniqueID(self) -> int:
        """
        Returns:
        ----------
            A positive integer value as unique ID of this instance.
        """
        pass


    @property
    def message(self) -> str:
        """
        Returns:
        ----------
            A string object giving (short) description of the error cause when
            the respective, underlying error object was submitted.
        """
        pass


    @property
    def errorCode(self) -> Union[int, None]:
        """
        Returns:
        ----------
            None if not available, otherwise an integer value as the error code
            assigned when the respective, underlying error object was submitted.

        Note:
        ------
            The error code (if any) of submitted task errors are always
            positive integer values, unless they were submitted by the
            framework.

        See:
        -----
            - xlogif.LogErrorEC()
            - xlogif.LogFatalEC()
            - xlogif.LogExceptionEC()
        """
        pass
    # ------------------------------------------------------------------------------
    #END API
    # ------------------------------------------------------------------------------
#END class ITaskError
