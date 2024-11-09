# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xmsgheader.py
#
# Copyright(c) 2024 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from typing import Union

from xcofdk.fwcom.xmsgdefs import IntEnum

from xcofdk._xcofw.fw.fwssys.fwmsg.apiimpl.xcomsghdrimpl import _XMsgHeaderImpl


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class XMessageHeader:
    """
    Instances of this class represent message header objects constructed
    according to the design patterns Adapter or Facade.

    Such an instance is part of the fix portion of a message object. It carries
    all information the destination of a delivered message may need for its
    proper processing.

    Note:
    ------
        - Subsystem messaging is described in more detail in class description
          of XMessageManager.

    See:
    -----
        - XMessage.msgHeader
        - XMessageManager
    """

    __slots__ = [ '__hdr' ]


    def __init__(self, hh_ : _XMsgHeaderImpl):
        """
        Constructor (initializer) of an instance of this class.

        Parameters:
        -------------
            - hh_ :
              the adaptee of this instance.

        Note:
        ------
            - Subsystem messaging is described in class description of
              XMessageManager.

        See:
        -----
            - XMessage.msgHeader
        """
        self.__hdr = None
        if isinstance(hh_, _XMsgHeaderImpl) and hh_.isValid:
            self.__hdr = hh_


    def __str__(self):
        """
        String representation of this instance.

        Returns:
        ----------
            A string object as representation of this instance.
        """
        if not self.__isValidHeader:
            return None
        return self.__hdr.ToString()


    @property
    def isInternalMessage(self) -> bool:
        """
        Returns:
        ----------
            True if this instance is an internal message, False otherwise.

        See:
        -----
            - XMessage.msgHeader
        """
        return self.__isValidHeader and self.__hdr.isInternalMsg


    @property
    def isBroadcastMessage(self) -> bool:
        """
        Returns:
        ----------
            True if this instance is a bradcast message, False otherwise.

        See:
        -----
            - XMessage.msgHeader
        """
        return self.__isValidHeader and self.__hdr.isXTaskBroadcastMsg or self.__hdr.isGlobalBroadcastMsg


    @property
    def msgLabel(self) -> Union[IntEnum, int]:
        """
        Returns:
        ----------
            a pre-/uer-defined enum or integer value as message label ID.

        See:
        -----
            - XMessage.msgHeader
        """
        return None if not self.__isValidHeader else self.__hdr.labelID


    @property
    def msgCluster(self) -> Union[IntEnum, int]:
        """
        Returns:
        ----------
            a pre-/uer-defined enum or integer value as message cluster ID.

        See:
        -----
            - XMessage.msgHeader
        """
        return None if not self.__isValidHeader else self.__hdr.clusterID


    @property
    def msgSender(self) -> int:
        """
        Returns:
        ----------
            the unique task ID of the sender.

        See:
        -----
            - XMessage.msgHeader
            - XTask.xtaskUniqueID
        """
        return None if not self.__isValidHeader else self.__hdr.senderID


    @property
    def msgReceiver(self) -> int:
        """
        Returns:
        ----------
            the unique task ID of the receiver.

        See:
        -----
            - XMessage.msgHeader
            - XTask.xtaskUniqueID
        """
        return None if not self.__isValidHeader else self.__hdr.receiverID


    def _Detach(self):
        """
        Detach this instance form its adaptee, so it becomes an invalid message
        object.

        Message objects, and so message header objects, passed to the respective
        callback methods (for processing of external/interal messages) of a task
        are always valid, that is never detached.

        Note:
        ------
            - This protected method is designed to be used by the subsystem of
              messaging only, it basically serves for interal, cleanup purposes.

        See:
        -----
            - XMessage._Detach()
            - XTask.ProcessExternalMessage()
        """
        self.__hdr = None


    @property
    def __isValidHeader(self) -> bool:
        return (self.__hdr is not None) and self.__hdr.isValid
#END class XMessageHeader
