# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : ifmsgheader.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from enum   import IntEnum
from typing import Union

from xcofdk.fwcom import EXmsgPredefinedID


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class IMessageHeader:
    """
    Instances of this interface class represent common API of a message header.
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
    def isInternalMessage(self) -> bool:
        """
        Returns:
        ----------
            True if this instance is an internal message, False otherwise.
        """
        pass


    @property
    def isBroadcastMessage(self) -> bool:
        """
        Returns:
        ----------
            True if this instance is a bradcast message, False otherwise.
        """
        pass


    @property
    def msgLabel(self) -> Union[IntEnum, int]:
        """
        Returns:
        ----------
            A pre-/uer-defined enum or integer value as message label ID.

        See:
        -----
            >>> IMessageHeader.msgCluster
            >>> EXmsgPredefinedID
            >>> EXmsgPredefinedID.MinUserDefinedID
        """
        pass


    @property
    def msgCluster(self) -> Union[IntEnum, int]:
        """
        Returns:
        ----------
            A pre-/uer-defined enum or integer value as message cluster ID.

        See:
        -----
            >>> IMessageHeader.msgLabel
            >>> EXmsgPredefinedID
            >>> EXmsgPredefinedID.MinUserDefinedID
        """
        pass


    @property
    def msgSender(self) -> int:
        """
        Returns:
        ----------
            The unique task ID of the sender.

        See:
        -----
            >>> IMessageHeader.msgReceiver
        """
        pass


    @property
    def msgReceiver(self) -> int:
        """
        Returns:
        ----------
            The unique task ID of the receiver.

        See:
        -----
            >>> IMessageHeader.msgSender
        """
        pass
    # ------------------------------------------------------------------------------
    #END API
    # ------------------------------------------------------------------------------
#END class IMessageHeader
