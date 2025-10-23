# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : ifrctask.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from enum   import IntEnum
from typing import Union

from .iftask      import ITask
from .ifmessage   import IMessage
from .ifpayload   import IPayload
from xcofdk.fwcom import EXmsgPredefinedID


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class IRCTask(ITask):
    """
    Instances of this interface class represent common API of task instances
    of class RCTask.

    THe major part of this class is described in its parent class:
        >>> ITask

    For the remaining API specific to this interface class refer to:
        >>> IRCTask.isMainTask
        >>> IRCTask.isMessagingTask
        >>> IRCTask.runPhaseFrequencyMS
        >>> IRCTask.phasedXFInstance
        >>> IRCTask.SelfCheckSleep
        >>> IRCTask.SendMessage()
        >>> IRCTask.BroadcastMessage()
    """

    __slots__ = []


    # ------------------------------------------------------------------------------
    # 1) c-tor / built-in
    # ------------------------------------------------------------------------------
    def __init__(self):
        super().__init__()
    # ------------------------------------------------------------------------------
    #END 1) c-tor / built-in
    # ------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # 2) n/a
    # ------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------
    #END 2) n/a
    # ------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # 3) start/stop
    # ------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------
    #END 3) start/stop
    # ------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # 4) task state
    # ------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------
    #END 4) task state
    # ------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # 5) task (unique) properties
    # ------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------
    #END 5) task (unique) properties
    # ------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # 6) task-owned data
    # ------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------
    #END 6) task-owned data
    # ------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # 7) message handling
    # ------------------------------------------------------------------------------
    def SendMessage( self
                   , rxTask_       : Union[ITask, IntEnum, int]
                   , msgLabelID_   : Union[IntEnum, int]   =EXmsgPredefinedID.DontCare
                   , msgClusterID_ : Union[IntEnum, int]   =EXmsgPredefinedID.DontCare
                   , msgPayload_   : Union[IPayload, dict] =None) -> int:
        """
        Request to submit an external message with this instance taken as
        sender.

        It constructs a message object based on the passed in parameters and
        put that object to the external queue of the receiver task.

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
            Positive integer number uniquely identifying the message object
            sent if the operation succeeded, 0 otherwise.

        Note:
        ------
            - The ability to send messages is available for all task instances
              even if they don't have an external queue themselves.
            - The request will be ignored by the framework if:
                  - this instance is not the currently running task,
                  - messaging subsystem 'xmsg' is disabled via RTE policy
                    configuration.
            - This API function is described in more detail by class XMessenger.

        See:
        -----
            - class XMessenger
            >>> ITask
            >>> IMessage
            >>> IPayload
            >>> EXmsgPredefinedID
            >>> IRCTask.BroadcastMessage()
            >>> IRCCommTask.TriggerExternalQueueProcessing()
        """
        pass


    def BroadcastMessage( self
                        , msgLabelID_   : Union[IntEnum, int]
                        , msgClusterID_ : Union[IntEnum, int]   =EXmsgPredefinedID.DontCare
                        , msgPayload_   : Union[IPayload, dict] =None) -> int:
        """
        Request to broadcast an external message with this instance taken as
        sender.

        It constructs a message object based on the passed in parameters and
        put that object to the external queue of the receiver task(s).

        It is provided for convenience only. It works exactly the
        same way as 'SendMessage()' explained above except for:
            - the receiver task to is set to the pre-defined ID 'Broadcast',
            - parameter 'msgLabelID_' is mandatory.

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
            Positive integer number uniquely identifying the message object
            sent if the operation succeeded, 0 otherwise.

        Note:
        ------
            - The ability to broadcast a messages is available for all task
              instances even if they don't have an external queue themselves.
            - The request will be ignored by the framework if:
                  - messaging subsystem 'xmsg' is disabled via RTE policy
                    configuration,
                  - this instance is not the currently running task.
            - This API function is described in more detail by class XMessenger.

        See:
        -----
            - class XMessenger
            >>> ITask
            >>> IMessage
            >>> IPayload
            >>> EXmsgPredefinedID
            >>> EXmsgPredefinedID.Broadcast
            >>> IRCTask.SendMessage()
            >>> IRCCommTask.TriggerExternalQueueProcessing()
        """
        pass
    # ------------------------------------------------------------------------------
    #END 7) message handling
    # ------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # 8) error handling
    # ------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------
    #END 8) error handling
    # ------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # 9) supplementary API
    # ------------------------------------------------------------------------------
    @property
    def isMainTask(self) -> bool:
        """
        Returns:
        ----------
            True, if this instance is the main application task instance,
            False otherwise.
        """
        pass


    @property
    def isMessagingTask(self) -> bool:
        """
        Returns:
        ----------
            True, if this instance is an instance of the derived class
            IRCCommTask, False otherwise.

        See:
        -----
            >>> IRCCommTask
        """
        pass


    @property
    def runPhaseFrequencyMS(self) -> int:
        """
        Returns:
        ----------
            A non-negatve integer value as amount of time (in milliseconds) used
            to configure the run phase frequency of this task.

        Note:
        ------
            - If 0 returned, then this task's run phase is configured to be
              non-cyclic.
        """
        pass


    @property
    def phasedXFInstance(self):
        """
        Task instances may also be created by passing a user-defined class as
        their 3-PhXF callback function, provided instances of that class can
        be created by default, that is without passing any argument to their
        constructor.

        Returns:
        ----------
            That instance of the above-mentioned user-defined class which
            has been auto-created by the framework to identify available
            3-PhXF callback method(s) to be used as callback function(s)
            when executing this task.

        See:
        -----
            - class XFSyncTask
            - class XFAsyncTask
            - class XFSyncCommTask
            - class XFAsyncCommTask
        """
        pass


    def SelfCheckSleep(self, sleepTime_: Union[int, float] =None) -> bool:
        """
        Request to perform a self-check and release the CPU if applicable.

        The processing of the reuest consists of three steps:
            1. A self-check will be performed.
               If this check does not pass, or if this instance is not the
               currently running task, next steps are skipped,
            2. release the CPU for the specified amount of time,
            3. perform an additional self-check.

        Parameters:
        -------------
            - sleepTime_ :
              if None passed, a pre-defined value (currently 20 [ms]).
              Otherwise, a positive amount of time (milliseconds for int values
              or seconds for floating-point values).

        Returns:
        ----------
            Result of the last self-check performed while above-mentioned
            processing of this request.

        See:
        -----
            >>> ITask.SelfCheck()
        """
        pass
    # ------------------------------------------------------------------------------
    #END 9) supplementary API
    # ------------------------------------------------------------------------------
#END class IRCTask


class IRCCommTask(IRCTask):
    """
    Instances of this interface class represent common API of task instances
    of class RCCommTask.

    Instances of this class are capable for full communication, as they are
    always configured for external queue support.

    THe major part of this class is described in its parent classes:
        >>> ITask
        >>> IRCTask

    For the remaining API specific to this interface class refer to:
        >>> IRCCommTask.isExternalQueueBlocking
        >>> IRCCommTask.TriggerExternalQueueProcessing()
    """

    __slots__ = []

    # --------------------------------------------------------------------------
    # 1) c-tor / built-in
    # --------------------------------------------------------------------------
    def __init__(self):
        super().__init__()
    # --------------------------------------------------------------------------
    #END 1) c-tor / built-in
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # 7) message handling
    # ------------------------------------------------------------------------------
    @property
    def isExternalQueueBlocking(self):
        """
        Returns:
        ----------
            True if this task's external queue is configured to be blocking,
            False otherwise.
        """
        pass


    def TriggerExternalQueueProcessing(self) -> int:
        """
        Request to start processing of currently queued external message(s).

        For each currently queued external message this instance's 3-PhXF
        callback method for processing external messages will be called
        accordingly.

        Returns:
        ----------
            Non-negative number of external messages processed (if any),
            -1 otherwise.

        Note:
        ------
            - Processing of external messages is triggered by the framework
              before executing next run phase cycle anyway.
            - Main purpose of this interface function is to enable tasks to
              process queued messages at their convenience on one hand, and to
              make tasks with single-cycle run phase are able to process
              messages delivered to them (if any) on the other hand.
            - The request will be ignored by the framework (returnning 0) if:
                  - messaging subsystem 'xmsg' is disabled via RTE policy
                    configuration,
                  - this instance is not the currently running task,
                  - this task's external queue is blocking,
                  - it is currently processing external/internal messages
                    already.

        See:
        -----
            >>> ITask
            >>> IRCTask
            >>> IRCTask.SendMessage()
            >>> IRCTask.BroadcastMessage()
            >>> IRCCommTask.isExternalQueueBlocking
        """
        pass
    # ------------------------------------------------------------------------------
    #END 7) message handling
    # ------------------------------------------------------------------------------
#END class IRCCommTask
