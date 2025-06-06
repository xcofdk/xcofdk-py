# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : ifmessage.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from .ifpayload   import IPayload
from .ifmsgheader import IMessageHeader


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class IMessage:
    """
    Instances of this interface class represent common API of a message.
    """

    __slots__ = []


    # ------------------------------------------------------------------------------
    # c-tor / built-in
    # ------------------------------------------------------------------------------
    def __init__(self):
        pass


    def __str__(self):
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
    def msgUniqueID(self) -> int:
        """
        Returns:
        ----------
            A positive integer number as unique ID of this message instance.
        """
        pass

    @property
    def msgHeader(self) -> IMessageHeader:
        """
        Returns:
        ----------
            Message header of this message instance.

        See:
        -----
            >>> IMessageHeader
        """
        pass

    @property
    def msgPayload(self) -> IPayload:
        """
        Returns:
        ----------
            Payload (if any) of this message instance.

        See:
        -----
            >>> IPayload
        """
        pass
    # ------------------------------------------------------------------------------
    #END API
    # ------------------------------------------------------------------------------
#END class XMessage
