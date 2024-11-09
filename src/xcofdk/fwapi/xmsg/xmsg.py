# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xmsg.py
#
# Copyright(c) 2024 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from xcofdk.fwapi.xmsg.xmsgheader import XMessageHeader
from xcofdk.fwapi.xmsg.xpayloadif import XPayloadIF

from xcofdk._xcofw.fw.fwssys.fwmsg.apiimpl.xcomsgimpl import _XMsgImpl


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class XMessage:
    """
    Instances of this class represent message objects constructed according to
    the design patterns Adapter or Facade.

    Such an instance is passed to the respective callback methods (for
    processing of external/interal messages) of a task instance which was
    specified as destination of a send request before.

    Note:
    ------
        - Subsystem messaging is described in more detail in class description
          of XMessageManager.

    See:
    -----
        - XMessageHeader
        - XMessageManager
    """


    __slots__ = [ '__xhh' , '__xmsg' ]


    def __init__(self, xm_ : _XMsgImpl):
        """
        Constructor (initializer) of an instance of this class.

        Parameters:
        -------------
            - xm_ :
              the adaptee of this instance.

        Note:
        ------
            - Subsystem messaging is described in class description of
              XMessageManager.

        See:
        -----
            - XMessageManager.SendMessage()
            - XMessageManager.BroadcastMessage()
            - XTask.ProcessExternalMessage()
        """
        self.__xhh  = None
        self.__xmsg = None
        if isinstance(xm_, _XMsgImpl) and xm_.isValid:
            self.__xhh  = XMessageHeader(xm_.header)
            self.__xmsg = xm_


    def __str__(self):
        """
        String representation of this instance.

        Returns:
        ----------
            A string object as representation of this instance.
        """
        if self.__isInvalidMsg:
            return None
        return self.__xmsg.ToString()


    @property
    def msgUniqueID(self) -> int:
        """
        Returns:
        ----------
            a positive integer number as unique ID of this message
            instance.
        """
        return None if self.__isInvalidMsg else self.__xmsg.uniqueID


    @property
    def msgHeader(self) -> XMessageHeader:
        """
        Returns:
        ----------
            header of this message instance.

        See:
        -----
            - XMessageHeader
        """
        return None if self.__isInvalidMsg else self.__xhh


    @property
    def msgPayload(self) -> XPayloadIF:
        """
        Returns:
        ----------
            payload (if any) of this message instance.

        See:
        -----
            - XPayloadIF
            - XPayload
        """
        return None if self.__isInvalidMsg else self.__xmsg.payload


    def _Detach(self):
        """
        Detach this instance form its adaptee, so it becomes an invalid message
        object.

        Message objects passed to the respective callback methods (for
        processing of external/interal messages) of a task are always valid,
        that is never detached.

        Note:
        ------
            - This protected method is designed to be used by the subsystem of
              messaging only, it basically serves for interal, cleanup purposes.

        See:
        -----
            - XTask.ProcessExternalMessage()
        """
        if self.__xhh is not None:
            self.__xhh._Detach()
            self.__xhh  = None
            self.__xmsg = None


    @property
    def __isInvalidMsg(self) -> bool:
        return self.__xmsg is None
#END class XMessage
