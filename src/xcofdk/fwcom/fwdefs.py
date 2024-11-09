# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwdefs.py
#
# Copyright(c) 2024 Farzad Safa (farzad.safa@xcofdk.de)
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

from enum import auto
from enum import IntEnum
from enum import unique


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
@unique
class ETernaryCallbackResultID(IntEnum):
    """
    Enum class to be used as return type of specific user/application callback
    functions.

    It is mainly used by the respective callback functions related to the
    '3-phased execution frame' (3-PhXF for short).

    Its defined enum members can be used by callback functions to return one of
    the possible three IDs as the action a callback function expects the
    framework to do in the given call context:
        - ABORT
          to indicate request to abort
        - STOP
          to indicate request to stop
        - CONTINUE
          to indicate request to continue

    Note:
    ------
        - As far as the framework is concerned saying 'a user/application
          callback is aborted' is the same as saying 'that callback is failed'
          and vice versa.
        - A user/application callback wishing 'just to abort' with no fatal
          error is automatically submitted must rather return STOP.
        - In order to avoid possible confusion no enum called FAILED is provided
          by this enum class.
        - 3-PhXF is described in class description of XTask.
        - Returned value of callback functions related to 3-PhXF are essential
          parts of the error handling mechanism of the framework (see class
          description of XTaskError).

    See:
    -----
        - XTask
        - XTaskError
    """

    ABORT    = -1
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
            ETernaryCallbackResultID.isCONTINUE
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
            ETernaryCallbackResultID.isOK
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
            ETernaryCallbackResultID.isOK
        """
        return self == ETernaryCallbackResultID.CONTINUE

    @property
    def isSTOP(self):
        """
        Returns:
        ----------
            True, if this instance equals to STOP, False otherwise.
        """
        return self == ETernaryCallbackResultID.STOP

    @property
    def isABORT(self):
        """
        Returns:
        ----------
            True, if this instance equals to ABORT, False otherwise.
        """
        return self == ETernaryCallbackResultID.ABORT

    @staticmethod
    def FromBool(res_ : bool ):
        """
        Static method to convert a boolean value to its correspondent
        enum member of this class.

        Parameters:
        -------------
            - res_ :
              a boolean value to be converted to its correspondent enum member
              of this class.

        Returns:
        ----------
            - ABORT, if passed in argument resolves to None
              (or more generally is not of a boolean type).
            - STOP, if passed in argument resolves to False.
            - CONTINUE, otherwise.
        """
        if not isinstance(res_, bool):
            return ETernaryCallbackResultID.ABORT
        return ETernaryCallbackResultID.CONTINUE if res_ else ETernaryCallbackResultID.STOP
#END class ETernaryCallbackResultID
