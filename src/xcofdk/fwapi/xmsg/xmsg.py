# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xmsg.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from xcofdk.fwcom                 import override
from xcofdk.fwapi                 import IMessage
from xcofdk.fwapi                 import IPayload
from xcofdk.fwapi                 import IMessageHeader
from xcofdk.fwapi.xmsg.xmsgheader import XMessageHeader

from _fw.fwssys.assys     import fwsubsysshare as _ssshare
from _fw.fwssys.fwmsg.msg import _IFwMessage


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class XMessage(IMessage):
    """
    Instances of this class represent message objects constructed by the
    framework when a message has to be derlivered to its receiver(s).

    Such an instance the result of a send request and is passed to the
    respective 3-PhXF callback methods (for processing messages) of the
    destination task instance(s).

    Note:
    ------
        - Subsystem messaging is described in more detail in class description
          of XMessenger.

    See:
    -----
        >>> XMessageHeader
        >>> IMessage
        >>> IPayload
    """


    __slots__ = [ '__xhh' , '__xmsg' ]


    def __init__(self, xm_ : _IFwMessage):
        """
        Constructor (initializer) of an instance of this class.

        Parameters:
        -------------
            - xm_ :
              the adaptee of this instance.

        Note:
        ------
            - Subsystem messaging is described in class description of
              XMessenger.

        See:
        -----
            - XMessenger.SendMessage()
            - XMessenger.BroadcastMessage()
            - XTask.ProcessExternalMessage()
        """
        self.__xhh  = None
        self.__xmsg = None
        super().__init__()
        if _ssshare._IsSubsysMsgDisabled():
            return
        if isinstance(xm_, _IFwMessage) and xm_.isValid:
            self.__xhh  = XMessageHeader(xm_.header)
            self.__xmsg = xm_


    @override
    def __str__(self):
        """
        See:
        -----
            >>> IMessage.__str__()
        """
        if self.__isInvalidMsg:
            return None
        return self.__xmsg.ToString()


    @IMessage.msgUniqueID.getter
    def msgUniqueID(self) -> int:
        """
        See:
        -----
            >>> IMessage.msgUniqueID
        """
        return None if self.__isInvalidMsg else self.__xmsg.uniqueID


    @IMessage.msgHeader.getter
    def msgHeader(self) -> IMessageHeader:
        """
        See:
        -----
            >>> IMessage.msgHeader
        """
        return None if self.__isInvalidMsg else self.__xhh


    @IMessage.msgPayload.getter
    def msgPayload(self) -> IPayload:
        """
        See:
        -----
            >>> IMessage.msgPayload
        """
        return None if self.__isInvalidMsg else self.__xmsg.payload


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
        if self.__xhh is not None:
            self.__xhh._Detach()
            self.__xhh  = None
            self.__xmsg = None


    @property
    def __isInvalidMsg(self) -> bool:
        return self.__xmsg is None
#END class XMessage
