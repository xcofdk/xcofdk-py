# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xmsgheader.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from enum   import IntEnum
from typing import Union

from xcofdk.fwcom import override
from xcofdk.fwcom import EXmsgPredefinedID
from xcofdk.fwapi import ITask
from xcofdk.fwapi import IMessage
from xcofdk.fwapi import IMessageHeader

from _fw.fwssys.fwmsg.msg import _IFwMessageHeader


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class XMessageHeader(IMessageHeader):
    """
    Instances of this class represent message header objects.

    Such an instance is part of the fix portion of a message object which
    carries all information the destination of a delivered message may need
    for its proper processing.

    See:
    -----
        - class XMessenger
        >>> IMessage.msgHeader
    """

    __slots__ = [ '_h' ]


    # ------------------------------------------------------------------------------
    # c-tor / built-in
    # ------------------------------------------------------------------------------
    def __init__(self, hh_ : _IFwMessageHeader):
        """
        Constructor (initializer) of an instance of this class.

        Parameters:
        -------------
            - hh_ :
              Framework's internal header object this instance refers to.

        See:
        -----
            >>> IMessage.msgHeader
        """
        self._h = None
        super().__init__()
        if isinstance(hh_, _IFwMessageHeader) and hh_.isValid:
            self._h = hh_


    @override
    def __str__(self):
        """
        See:
        -----
            >>> IMessageHeader.__str__()
        """
        if not self.__isValidHeader:
            return None
        return self._h.ToString()
    # ------------------------------------------------------------------------------
    #END c-tor / built-in
    # ------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # API
    # ------------------------------------------------------------------------------
    @IMessageHeader.isInternalMessage.getter
    def isInternalMessage(self) -> bool:
        """
        See:
        -----
            >>> IMessageHeader.isInternalMessage
            >>> IMessage.msgHeader
        """
        return self.__isValidHeader and self._h.isInternalMsg


    @IMessageHeader.isBroadcastMessage.getter
    def isBroadcastMessage(self) -> bool:
        """
        See:
        -----
            >>> IMessageHeader.isBroadcastMessage
            >>> IMessage.msgHeader
        """
        return self.__isValidHeader and self._h.isXTaskBroadcastMsg or self._h.isGlobalBroadcastMsg


    @IMessageHeader.msgLabel.getter
    def msgLabel(self) -> Union[IntEnum, int]:
        """
        See:
        -----
            >>> IMessageHeader.msgLabel
            >>> IMessage.msgHeader
        """
        return None if not self.__isValidHeader else self._h.labelID


    @IMessageHeader.msgCluster.getter
    def msgCluster(self) -> Union[IntEnum, int]:
        """
        See:
        -----
            >>> IMessageHeader.msgCluster
            >>> IMessage.msgHeader
        """
        return None if not self.__isValidHeader else self._h.clusterID


    @IMessageHeader.msgSender.getter
    def msgSender(self) -> int:
        """
        See:
        -----
            >>> IMessageHeader.msgSender
            >>> IMessage.msgHeader
            >>> ITask.taskUID
        """
        return None if not self.__isValidHeader else self._h.senderID


    @IMessageHeader.msgReceiver.getter
    def msgReceiver(self) -> int:
        """
        See:
        -----
            >>> IMessageHeader.msgReceiver
            >>> IMessage.msgHeader
            >>> ITask.taskUID
        """
        return None if not self.__isValidHeader else self._h.receiverID


    def _Detach(self):
        """
        Detach this instance from framework's internal object it refers to,
        so it becomes an invalid message object.

        Message (header) objects are always valid when delivered to their
        receiver(s).

        Note:
        ------
            - This protected method is designed to be used by the framework
              only, once a message has been processed by a receiver task.
              It basically serves for resource-efficient purposes, as a message
              object might have to be delivered to more than one receiver.
        """
        self._h = None
    # ------------------------------------------------------------------------------
    #END API
    # ------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # Impl
    # ------------------------------------------------------------------------------
    @property
    def __isValidHeader(self) -> bool:
        return (self._h is not None) and self._h.isValid
    # ------------------------------------------------------------------------------
    #END Impl
    # ------------------------------------------------------------------------------
#END class XMessageHeader
