# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xtaskerror.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from typing import Union

from xcofdk.fwapi import ITaskError
from xcofdk.fwapi import ITask
from _fw.fwssys.fwmt.api.xtaskerrimpl import _XTaskErrorImpl


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class XTaskError(ITaskError):
    """
    Instances of this class represent the high-level abstraction of the current
    error of a task, i.e. an instance of either class RCTask, or a user-defined
    class subclassing one of the abstract classes XTask or XMainTask.

    Associating a task with an instance of this class is the result of a
    multilayered, multithreaded per-task error handling by the framework,
    also referred to as error qualification.

    See:
    -----
        - class XTaskException
        - module xlogif
        - module curtask
        >>> ITask.currentError
        >>> ITaskError
    """

    __slots__ = [ '__te' ]


    # ------------------------------------------------------------------------------
    # c-tor / built-in
    # ------------------------------------------------------------------------------
    def __init__(self, te_ : _XTaskErrorImpl):
        """
        Constructor (or initializer) of this instance.

        Parameters:
        -------------
            - te_ :
              framework's internal error object this instance is made around.

        Note:
        ------
            - Instances of this class are created by the framework only.
            - They are returned whenever current error (if any) of a task is
              requested.
            - Such an instance is always either a non-fatal (i.e. user) error or
              a fatal error.
            - Except for qualified fatal errors, the validity of the information
              an instance of this class delivers is bound to the scope of its
              creation.
        """
        super().__init__()
        self.__te = te_


    def __str__(self):
        """
        Returns:
        ----------
            A nicely printable string representation of this instance.
        """
        return str(self.__te)
    # ------------------------------------------------------------------------------
    #END c-tor / built-in
    # ------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # API
    # ------------------------------------------------------------------------------
    @ITaskError.isFatalError.getter
    def isFatalError(self) -> bool:
        """
        See:
        -----
            >>> ITaskError.isFatalError
        """
        return self.__te._isFatalError


    @ITaskError.uniqueID.getter
    def uniqueID(self) -> int:
        """
        See:
        -----
            >>> ITaskError.uniqueID
        """
        return self.__te._uniqueID


    @ITaskError.message.getter
    def message(self) -> str:
        """
        See:
        -----
            >>> ITaskError.message
        """
        return self.__te._message


    @ITaskError.errorCode.getter
    def errorCode(self) -> Union[int, None]:
        """
        See:
        -----
            >>> ITaskError.errorCode
        """
        return self.__te._errorCode
    # ------------------------------------------------------------------------------
    #END API
    # ------------------------------------------------------------------------------
#END class XTaskError
