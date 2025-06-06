# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xmsgmgr.py
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
from xcofdk.fwapi import ITask
from xcofdk.fwapi import IMessage
from xcofdk.fwapi import IPayload

from _fw.fwssys.fwmsg.apiimpl.xmsgmgrimpl import _XMsgMgrImpl


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class XMessenger:
    """
    This class represents the high-level abstraction of the messaging subsystem
    'xmsg' of the framework.

    Its interface is designed to provide a collection of common operations
    available for application tasks for communication via messages.


    Deprecated API:
    ----------------
    Starting with XCOFDK-py v3.0 below API entities (formerly part of
    the API of this class) are deprecated and not available anymore:
        >>> # renaming
        >>> XMessageManager = XMessenger
    """

    __slots__ = []

    def __init__(self):
        pass


    # ------------------------------------------------------------------------------
    # API - Messaging
    # ------------------------------------------------------------------------------
    @staticmethod
    def SendMessage( rxTask_       : Union[ITask, IntEnum, int]
                   , msgLabelID_   : Union[IntEnum, int]   =EXmsgPredefinedID.DontCare
                   , msgClusterID_ : Union[IntEnum, int]   =EXmsgPredefinedID.DontCare
                   , msgPayload_   : Union[IPayload, dict] =None) -> int:
        """
        Request to submit an external message with currently running task taken
        as sender.

        Main responsibility of this interface function is to construct a
        message object based on the passed in parameters, and to put that object
        to the external queue of the receiver task.

        In cases an immediate delivery is not possible, for example when
        receiver's queue is temporarily full, an internal, shared service
        responsible for delivery of pending messages is in charge to take over
        the remaining part of the delivery process.

        Later, framework's execution of the run phase of the receiver task is
        responsible to call the respective callback method (for processing of
        external messages) passing a message object sent by the sender.

        Parameters:
        -------------
            - rxTask_ :
                  - an instance of class ITask, or
                  - unique task ID of such a task, or
                  - a pre-defined alias ID, or
                  - a user-defined enum or an integer resolving to a unique
                    task ID.
            - msgLabelID_ :
              optional pre-/user-defined message label.
            - msgClusterID_ :
              optional pre-/user-defined message cluster.
            - msgPayload_ :
              payload (if any) to be associated to the message to be sent.

        Returns:
        ----------
            Positive integer number uniquely identifying the message sent if
            the operation succeeded, 0 otherwise.

        Note:
        ------
            - The multipurpose type annotation of the first three parameters to
              be passed to enables the senders to choose any of the addressing
              policies, i.e. direct or alias or anonymous addressing, at their
              convenient.

        See:
        -----
            >>> ITask
            >>> ITask.taskUID
            >>> IMessage
            >>> IPayload
            >>> EXmsgPredefinedID.MainTask
            >>> EXmsgPredefinedID.MinUserDefinedID
            >>> XMessenger.BroadcastMessage()
        """
        return _XMsgMgrImpl._SendXMsg(rxTask_, msgLabelID_, msgClusterID_, payload_=msgPayload_)


    @staticmethod
    def BroadcastMessage( msgLabelID_   : Union[IntEnum, int]
                        , msgClusterID_ : Union[IntEnum, int]   =EXmsgPredefinedID.DontCare
                        , msgPayload_   : Union[IPayload, dict] =None) -> int:
        """
        Request to broadcast an external message with currently running task
        taken as sender.

        This interface is provided for convenience only. It works exactly the
        same way as sending messages explained above except for:
            - the receiver task is set to the pre-defined ID 'Broadcast',
            - parameter 'msgLabelID_' is mandatory.

        The major benefits of sending a message as broadcast is:
            - firstly to have to submit one single request only when more
              than one receiver are supposed to be delivered to,
            - secondly when anonymous addressing is either the preferred or the
              only available option to specify the receiver(s).

        Parameters:
        -------------
            - msgLabelID_ :
              mandatory pre-/user-defined message label.
            - msgClusterID_ :
              optional pre-/user-defined message cluster.
            - msgPayload_ :
              payload (if any) to be associated to the message to be sent.

        Returns:
        ----------
            Positive integer number uniquely identifying sent message if the
            operation succeeded, 0 otherwise.

        See:
        -----
            >>> ITask
            >>> ITask.taskUID
            >>> IMessage
            >>> IPayload
            >>> EXmsgPredefinedID.MinUserDefinedID
            >>> XMessenger.SendMessage()
        """
        return _XMsgMgrImpl._BroadcastXMsg(msgLabelID_, msgClusterID_,payload_=msgPayload_)
    # ------------------------------------------------------------------------------
    #END API - Messaging
    # ------------------------------------------------------------------------------
##END class XMessenger
