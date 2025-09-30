# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : rctask.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from enum   import IntEnum
from typing import Any
from typing import Union

from xcofdk.fwcom import CompoundTUID
from xcofdk.fwcom import override
from xcofdk.fwcom import EXmsgPredefinedID
from xcofdk.fwapi import ITaskError
from xcofdk.fwapi import IMessage
from xcofdk.fwapi import IPayload
from xcofdk.fwapi import ITask
from xcofdk.fwapi import IRCTask
from xcofdk.fwapi import IRCCommTask

from _fw.fwssys.fwctrl.fwapiconnap   import _FwApiConnectorAP
from _fw.fwssys.fwmt.api.rctaskagent import _RCTAgent
from _fw.fwssys.fwmt.api.rctaskagent import _RCMTAgent


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class RCTask(IRCTask):
    """
    Class RCTask is the common base for all task classes designed for rapid
    construction (RC).

    See:
    -----
        >>> IRCTask
        >>> RCCommTask
        >>> SyncTask
        >>> AsyncTask
        >>> SyncCommTask
        >>> AsyncCommTask
        >>> MessageDrivenTask
        >>> XFSyncTask
        >>> XFAsyncTask
        >>> XFSyncCommTask
        >>> XFAsyncCommTask
        >>> XFMessageDrivenTask
        >>> ITask.Start()
    """

    # --------------------------------------------------------------------------
    # 1) c-tor / built-in
    # --------------------------------------------------------------------------
    def __init__( self
                , runCallback_           =None
                , setupCallback_         =None
                , teardownCallback_      =None
                , procExtMsgCallback_    =None
                , phasedXFCallback_      =None
                , aliasName_             : str =None
                , bSyncTask_             =False
                , bMainTask_             =False
                , bMessagingTask_        =False
                , bBlockingExtQueue_     =False
                , bRefToCurTaskRequired_ =False
                , runCallbackFrequency_  : Union[int, float] =0
                , aenvl_                 =None):
        """
        Common constructor of a new RC task instance.

        Parameters:
        -------------
            - runCallback_ :
              callback function of the run phase
            - setupCallback_ :
              callback function of the setup phase
            - teardownCallback_ :
              callback function of the teardown phase
            - procExtMsgCallback_ :
              callback function for processing external messages
            - phasedXFCallback_ :
              a class instance or a class supporting 3-PhXF callbacks
            - aliasName_ :
              if specified, the alias name of this instance, an arbitrary
              non-empty and printable string literal without spaces which
              optionally may have a trailing '_'
            - bSyncTask_ :
              if True this instance will be configured to be a sync. task,
              async. task otherwise
            - bMainTask_ :
              if True this instance will be configured to be application's
              main task, a reqular task otherwise
            - bMessagingTask_ :
              if True this instance will be configured to have its own external
              queue enabling this task to receive external messages
            - bBlockingExtQueue_ :
              if True, the external queue will be configured to be blocking,
            - bRefToCurTaskRequired_ :
              if True a reference to this instance will be passed as first
              argument whenever specified callbacks are called by the framework
            - runCallbackFrequency_ :
              run phase frequency of this task
              (milliseconds for integer values, seconds for floating-point values)
            - aenvl_ :
              used for implementation purpsoses

        Note:
        ------
            - Note that the callback functions to be passed to the constructor
              are in fact 3-PhXF callbacks executed by the framework when the
              task is started.
            - Applications are highly recommended to use below subclasses only
              to create new RC task instances, as chances are good to improperly
              parameterize this constructor:
                >>> SyncTask
                >>> AsyncTask
                >>> SyncCommTask
                >>> AsyncCommTask
                >>> MessageDrivenTask
                >>> XFSyncTask
                >>> XFAsyncTask
                >>> XFSyncCommTask
                >>> XFAsyncCommTask
                >>> XFMessageDrivenTask

        See:
        -----
            >>> ITask.isSyncTask
            >>> ITask.aliasName
            >>> IRCTask.isMainTask
            >>> IRCTask.isMessagingTask
            >>> IRCTask.runPhaseFrequencyMS
            >>> IRCCommTask.isExternalQueueBlocking
        """
        super().__init__()

        if bMainTask_:
            self.__a = _RCMTAgent( self
                                 , aliasn_=aliasName_
                                 , cbRun_=runCallback_
                                 , cbSetup_=setupCallback_
                                 , cbTeardown_=teardownCallback_
                                 , cbProcExtMsg_=procExtMsgCallback_
                                 , cbProcIntMsg_=None
                                 , cbPhXFInst_=phasedXFCallback_
                                 , bSTask_=bSyncTask_
                                 , bMsgTask_=bMessagingTask_
                                 , bBlockingExtQ_=bBlockingExtQueue_
                                 , bGenericParam_=bRefToCurTaskRequired_
                                 , runFreq_=runCallbackFrequency_)
        else:
            self.__a = _RCTAgent( self
                                , aliasn_=aliasName_
                                , cbRun_=runCallback_
                                , cbSetup_=setupCallback_
                                , cbTeardown_=teardownCallback_
                                , cbProcExtMsg_=procExtMsgCallback_
                                , cbProcIntMsg_=None
                                , cbPhXFInst_=phasedXFCallback_
                                , bSTask_=bSyncTask_
                                , bMsgTask_=bMessagingTask_
                                , bBlockingExtQ_=bBlockingExtQueue_
                                , bGenericParam_=bRefToCurTaskRequired_
                                , runFreq_=runCallbackFrequency_)
        if isinstance(aenvl_, list):
            aenvl_.append(self.__a)
    # --------------------------------------------------------------------------
    #END 1) c-tor / built-in
    # --------------------------------------------------------------------------


    # --------------------------------------------------------------------------
    # 2) n/a
    # --------------------------------------------------------------------------
    # --------------------------------------------------------------------------
    #END 2) n/a
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # 3) start/stop
    # ------------------------------------------------------------------------------
    @override
    def Start(self, *args_, **kwargs_) -> bool:
        """
        See:
        -----
            >>> ITask.Start()
        """
        return self.__a._RcStart(*args_, **kwargs_)


    @override
    def Stop(self) -> bool:
        """
        See:
        -----
            >>> ITask.Stop()
        """
        return self.__a._RcStop()


    @override
    def Cancel(self) -> bool:
        """
        See:
        -----
            >>> ITask.Cancel()
        """
        return self.__a._RcCancel()


    @override
    def Join(self, maxWaitTime_: Union[int, float] =None) -> bool:
        """
        See:
        -----
            >>> ITask.Join()
        """
        return self.__a._RcJoin(maxWTime_=maxWaitTime_)


    @override
    def DetachFromFW(self):
        """
        See:
        -----
            >>> ITask.DetachFromFW()
        """
        self.__a._RcDetachFromFW()
    # ------------------------------------------------------------------------------
    #END 3) start/stop
    # ------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # 4) task state
    # ------------------------------------------------------------------------------
    @ITask.isAttachedToFW.getter
    def isAttachedToFW(self):
        """
        See:
        -----
            >>> ITask.isAttachedToFW
        """
        return self.__a._RcIsAttachedToFW()


    @ITask.isDetachedFromFW.getter
    def isDetachedFromFW(self):
        """
        See:
        -----
            >>> ITask.isDetachedFromFW
        """
        return self.__a._RcIsDetachedFromFW()


    @ITask.isStarted.getter
    def isStarted(self) -> bool:
        """
        See:
        -----
            >>> ITask.isStarted
        """
        return self.__a._RcIsStarted()


    @ITask.isPendingRun.getter
    def isPendingRun(self) -> bool:
        """
        See:
        -----
            >>> ITask.isPendingRun
        """
        return self.__a._RcIsPendingRun()


    @ITask.isRunning.getter
    def isRunning(self) -> bool:
        """
        See:
        -----
            >>> ITask.isRunning
        """
        return self.__a._RcIsRunning()


    @ITask.isDone.getter
    def isDone(self) -> bool:
        """
        See:
        -----
            >>> ITask.isDone
        """
        return self.__a._RcIsDone()


    @ITask.isCanceled.getter
    def isCanceled(self) -> bool:
        """
        See:
        -----
            >>> ITask.isCanceled
        """
        return self.__a._RcIsCanceled()


    @ITask.isFailed.getter
    def isFailed(self) -> bool:
        """
        See:
        -----
            >>> ITask.isFailed
        """
        return self.__a._RcIsFailed()


    @ITask.isTerminated.getter
    def isTerminated(self) -> bool:
        """
        See:
        -----
            >>> ITask.isTerminated
        """
        return self.__a._RcIsTerminated()


    @ITask.isTerminating.getter
    def isTerminating(self) -> bool:
        """
        See:
        -----
            >>> ITask.isTerminating
        """
        return self.__a._RcIsTerminating()


    @ITask.isStopping.getter
    def isStopping(self) -> bool:
        """
        See:
        -----
            >>> ITask.isStopping
        """
        return self.__a._RcIsStopping()


    @ITask.isCanceling.getter
    def isCanceling(self) -> bool:
        """
        See:
        -----
            >>> ITask.isCanceling
        """
        return self.__a._RcIsCanceling()
    # ------------------------------------------------------------------------------
    #END 4) task state
    # ------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # 5) task (unique) properties
    # ------------------------------------------------------------------------------
    @ITask.isSyncTask.getter
    def isSyncTask(self) -> bool:
        """
        See:
        -----
            >>> ITask.isSyncTask
        """
        return self.__a._RcIsSyncTask()


    @ITask.isFirstRunPhaseIteration.getter
    def isFirstRunPhaseIteration(self) -> bool:
        """
        See:
        -----
            >>> ITask.isFirstRunPhaseIteration
        """
        return self.__a._RcIsFirstRunPhaseIteration()


    @ITask.taskUID.getter
    def taskUID(self) -> int:
        """
        See:
        -----
            >>> ITask.taskUID
        """
        return self.__a._RcTaskUID()


    @ITask.taskName.getter
    def taskName(self) -> str:
        """
        See:
        -----
            >>> ITask.taskName
        """
        return self.__a._RcTaskName()


    @ITask.aliasName.getter
    def aliasName(self) -> str:
        """
        See:
        -----
            >>> ITask.aliasName
        """
        return self.__a._RcTaskAliasName()


    @ITask.taskCompoundUID.getter
    def taskCompoundUID(self) -> CompoundTUID:
        """
        See:
        -----
            >>> ITask.taskCompoundUID
        """
        return self.__a._RcTaskCompUID()


    @ITask.currentRunPhaseIterationNo.getter
    def currentRunPhaseIterationNo(self) -> int:
        """
        See:
        -----
            >>> ITask.currentRunPhaseIterationNo
        """
        return self.__a._RcCurrentRunPhaseIterationNo()
    # ------------------------------------------------------------------------------
    #END 5) task (unique) properties
    # ------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # 6) task-owned data
    # ------------------------------------------------------------------------------
    @override
    def GetTaskOwnedData(self, bDeserialize_ =True) -> Any:
        """
        See:
        -----
            >>> ITask.GetTaskOwnedData()
        """
        return self.__a._RcGetTaskData(bDeser_=bDeserialize_)


    @override
    def SetTaskOwnedData(self, taskOwnedData_ : Any, bSerialize_ =False):
        """
        See:
        -----
            >>> ITask.SetTaskOwnedData()
        """
        self.__a._RcSetTaskData(taskOwnedData_, bSer_=bSerialize_)
    # ------------------------------------------------------------------------------
    #END 6) task-owned data
    # ------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # 7) message handling
    # ------------------------------------------------------------------------------
    @override
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
            >>> RCTask.BroadcastMessage()
            >>> RCCommTask.TriggerExternalQueueProcessing()
        """
        return self.__a._RcSendMsg(rxTask_, msgLabelID_=msgLabelID_, msgClusterID_=msgClusterID_, msgPayload_=msgPayload_)


    @override
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
            >>> RCTask.SendMessage()
            >>> RCCommTask.TriggerExternalQueueProcessing()
        """
        return self.__a._RcBroadcastMsg(msgLabelID_, msgClusterID_=msgClusterID_, msgPayload_=msgPayload_)
    # ------------------------------------------------------------------------------
    #END 7) message handling
    # ------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # 8) error handling
    # ------------------------------------------------------------------------------
    @ITask.isErrorFree.getter
    def isErrorFree(self) -> bool:
        """
        See:
        -----
            >>> ITask.isErrorFree
        """
        return self.__a._RcIsErrorFree()


    @ITask.isFatalErrorFree.getter
    def isFatalErrorFree(self) -> bool:
        """
        See:
        -----
            >>> ITask.isFatalErrorFree
        """
        return self.__a._RcIsFatalErrorFree()


    @ITask.currentError.getter
    def currentError(self) -> ITaskError:
        """
        See:
        -----
            >>> ITask.currentError
        """
        return self.__a._RcCurrentError()


    @override
    def ClearCurrentError(self) -> bool:
        """
        See:
        -----
            >>> ITask.ClearCurrentError()
        """
        return self.__a._RcClearCurrentError()


    @override
    def SetError(self, errorMsg_ : str):
        """
        See:
        -----
            >>> ITask.SetError()
        """
        self.__a._RcSetError(errorMsg_)


    @override
    def SetErrorEC(self, errorMsg_ : str, errorCode_: int):
        """
        See:
        -----
            >>> ITask.SetErrorEC()
        """
        self.__a._RcSetErrorEC(errorMsg_, errorCode_)


    @override
    def SetFatalError(self, errorMsg_ : str):
        """
        See:
        -----
            >>> ITask.SetFatalError()
        """
        self.__a._RcSetFatalError(errorMsg_)


    @override
    def SetFatalErrorEC(self, errorMsg_ : str, errorCode_: int):
        """
        See:
        -----
            >>> ITask.SetFatalErrorEC()
        """
        self.__a._RcSetFatalErrorEC(errorMsg_, errorCode_)
    # ------------------------------------------------------------------------------
    #END 8) error handling
    # ------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # 9) supplementary API
    # ------------------------------------------------------------------------------
    @IRCTask.isMainTask.getter
    def isMainTask(self) -> bool:
        """
        See:
        -----
            >>> IRCTask.isMainTask
        """
        return self.__a._RcIsMainTask()


    @IRCTask.isMessagingTask.getter
    def isMessagingTask(self) -> bool:
        """
        See:
        -----
            >>> IRCTask.isMessagingTask
        """
        return self.__a._RcIsMsgTask()


    @IRCTask.runPhaseFrequencyMS.getter
    def runPhaseFrequencyMS(self) -> int:
        """
        See:
        -----
            >>> IRCTask.runPhaseFrequencyMS
        """
        return self.__a._RcRunPhaseFrequencyMS()


    @IRCTask.phasedXFInstance.getter
    def phasedXFInstance(self):
        """
        See:
        -----
            >>> IRCTask.phasedXFInstance
        """
        return self.__a._RcPhasedXFInstance()


    @override
    def SelfCheck(self) -> bool:
        """
        See:
        -----
            >>> ITask.SelfCheck()
        """
        return self.__a._RcSelfCheck()

    @override
    def SelfCheckSleep(self, sleepTime_: Union[int, float] = None) -> bool:
        """
        See:
        -----
            >>> IRCTask.SelfCheckSleep()
        """
        return self.__a._RcSelfCheckSleep(sleepTime_)

    @override
    def ToString(self) -> str:
        """
        See:
        -----
            >>> ITask.ToString()
        """
        return str(self.__a)
    # ------------------------------------------------------------------------------
    #END 9) supplementary API
    # ------------------------------------------------------------------------------
#END class RCTask


class RCCommTask(RCTask, IRCCommTask):
    """
    Derived from class RCTask, class RCCommTask is the common base for all
    task classes designed for rapid construction with support for external
    queue is always configured for instances of this class.

    Note:
    ------
        - 'Comm' stands for 'full Communication', as instances of this class
          are enabled to receive external messages.

    See:
    -----
        >>> RCTask
        >>> IRCCommTask
        >>> SyncCommTask
        >>> AsyncCommTask
        >>> MessageDrivenTask
        >>> XFSyncCommTask
        >>> XFAsyncCommTask
        >>> XFMessageDrivenTask
    """

    # --------------------------------------------------------------------------
    # 1) c-tor / built-in
    # --------------------------------------------------------------------------
    def __init__( self
                , runCallback_           =None
                , setupCallback_         =None
                , teardownCallback_      =None
                , procExtMsgCallback_    =None
                , phasedXFCallback_      =None
                , aliasName_             : str =None
                , bSyncTask_             =False
                , bMainTask_             =False
                , bBlockingExtQueue_     =False
                , bRefToCurTaskRequired_ =False
                , runCallbackFrequency_  : Union[int, float] =0):
        """
        Common constructor of a new RCComm task instance.

        Parameters:
        -------------
            - runCallback_ :
              callback function of the run phase
            - setupCallback_ :
              callback function of the setup phase
            - teardownCallback_ :
              callback function of the teardown phase
            - procExtMsgCallback_ :
              callback function for processing external messages
            - phasedXFCallback_ :
              a class instance or a class supporting 3-PhXF callbacks
            - aliasName_ :
              if specified, the alias name of this instance, an arbitrary
              non-empty and printable string literal without spaces which
              optionally may have a trailing '_'
            - bSyncTask_ :
              if True this instance will be configured to be sync. task,
              async. task otherwise
            - bMainTask_ :
              if True this instance will be configured to be application's
              main task, a reqular task otherwise
            - bBlockingExtQueue_ :
              if True, the external queue will be configured to be blocking,
            - bRefToCurTaskRequired_ :
              if True a reference to this instance will be passed as first
              argument whenever specified callbacks are called by the framework
            - runCallbackFrequency_ :
              run phase frequency of this task
              (milliseconds for integer values, seconds for floating-point values)

        Note:
        ------
            - Note that the callback functions to be passed to the constructor
              are in fact 3-PhXF callbacks executed by the framework when the
              task is started.
            - Applications are highly recommended to use below subclasses only
              to create new RCComm task instances, as chances are good to
              improperly parameterize this constructor:
                >>> SyncCommTask
                >>> AsyncCommTask
                >>> MessageDrivenTask
                >>> XFSyncCommTask
                >>> XFAsyncCommTask
                >>> XFMessageDrivenTask

        See:
        -----
            >>> ITask.isSyncTask
            >>> ITask.aliasName
            >>> IRCTask.isMainTask
            >>> IRCTask.isMessagingTask
            >>> IRCTask.runPhaseFrequencyMS
            >>> IRCCommTask.isExternalQueueBlocking
        """
        _aenvl = []
        IRCCommTask.__init__(self)
        RCTask.__init__( self
                       , runCallback_=runCallback_
                       , setupCallback_=setupCallback_
                       , teardownCallback_=teardownCallback_
                       , procExtMsgCallback_=procExtMsgCallback_
                       , phasedXFCallback_=phasedXFCallback_
                       , aliasName_=aliasName_
                       , bSyncTask_=bSyncTask_
                       , bMainTask_=bMainTask_
                       , bMessagingTask_=True
                       , bBlockingExtQueue_=bBlockingExtQueue_
                       , bRefToCurTaskRequired_=bRefToCurTaskRequired_
                       , runCallbackFrequency_=runCallbackFrequency_
                       , aenvl_=_aenvl)
        self.__pa = _aenvl.pop(0)
        _aenvl = None
    # --------------------------------------------------------------------------
    #END 1) c-tor / built-in
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # 7) message handling
    # ------------------------------------------------------------------------------
    @IRCCommTask.isExternalQueueBlocking.getter
    def isExternalQueueBlocking(self):
        """
        See:
        -----
            >>> IRCCommTask.isExternalQueueBlocking
        """
        return self.__pa._RcIsXQueueBlocking()

    @override
    def TriggerExternalQueueProcessing(self) -> int:
        """
        See:
        -----
            >>> IRCCommTask.TriggerExternalQueueProcessing()
        """
        return self.__pa._RcTriggerExtQProc()
    # ------------------------------------------------------------------------------
    #END 7) message handling
    # ------------------------------------------------------------------------------
#END class RCCommTask


class SyncTask(RCTask):
    """
    Derived from class RCTask, this RC task class is designed to create
    synchronous task instances by passing one or more callback functions.

    See:
    -----
        >>> RCTask
        >>> AsyncTask
        >>> XFSyncTask
        >>> SyncCommTask
    """

    __slots__ = []

    def __init__( self
                , runCallback_
                , setupCallback_         =None
                , teardownCallback_      =None
                , aliasName_             : str =None
                , bMainTask_             =False
                , bRefToCurTaskRequired_ =False
                , runCallbackFrequency_  : Union[int, float] =0):
        """
        Constructor of this class.

        Parameters:
        -------------
            - runCallback_ :
              mandatory callback function of the run phase
            - setupCallback_ :
              callback function of the setup phase
            - teardownCallback_ :
              callback function of the teardown phase
            - aliasName_ :
              if specified, the alias name of this instance, an arbitrary
              non-empty and printable string literal without spaces which
              optionally may have a trailing '_'
            - bMainTask_ :
              if True this instance will be configured to be application's
              main task, a reqular task otherwise
            - bRefToCurTaskRequired_ :
              if True a reference to this instance will be passed as first
              argument whenever specified callbacks are called by the framework
            - runCallbackFrequency_ :
              run phase frequency of this task
              (milliseconds for integer values, seconds for floating-point values)

        Note:
        ------
            - Note that the callback functions to be passed to the constructor
              are in fact 3-PhXF callbacks executed by the framework when the
              task is started.

        See:
        -----
            >>> ITask.isSyncTask
            >>> ITask.aliasName
            >>> IRCTask.isMainTask
            >>> IRCTask.runPhaseFrequencyMS
        """
        super().__init__( runCallback_=runCallback_
                        , setupCallback_=setupCallback_
                        , teardownCallback_=teardownCallback_
                        , procExtMsgCallback_=None
                        , phasedXFCallback_=None
                        , aliasName_=aliasName_
                        , bSyncTask_=True
                        , bMainTask_=bMainTask_
                        , bMessagingTask_=False
                        , bBlockingExtQueue_=False
                        , bRefToCurTaskRequired_=bRefToCurTaskRequired_
                        , runCallbackFrequency_=runCallbackFrequency_)
#END class SyncTask


class XFSyncTask(RCTask):
    """
    Derived from class RCTask, this RC task class is designed to create
    synchronous task instances by passing a class instance or a class
    supporting 3-PhXF callbacks.

    See:
    -----
        >>> RCTask
        >>> SyncTask
        >>> XFAsyncCommTask
    """

    __slots__ = []

    def __init__( self
                , phasedXFCallback_
                , aliasName_             : str =None
                , bMainTask_             =False
                , bRefToCurTaskRequired_ =False
                , runCallbackFrequency_  : Union[int, float] =0):
        """
        Constructor of this class.

        Parameters:
        -------------
            - phasedXFCallback_ :
              mandatory class (instance) supporting 3-PhXF callbacks
            - aliasName_ :
              if specified, the alias name of this instance, an arbitrary
              non-empty and printable string literal without spaces which
              optionally may have a trailing '_'
            - bMainTask_ :
              if True this instance will be configured to be application's
              main task, a reqular task otherwise
            - bRefToCurTaskRequired_ :
              if True a reference to this instance will be passed as first
              argument whenever specified callbacks are called by the framework
            - runCallbackFrequency_ :
              run phase frequency of this task
              (milliseconds for integer values, seconds for floating-point values)

        See:
        -----
            >>> ITask.isSyncTask
            >>> ITask.aliasName
            >>> IRCTask.isMainTask
            >>> IRCTask.runPhaseFrequencyMS
        """
        super().__init__( runCallback_=None
                        , setupCallback_=None
                        , teardownCallback_=None
                        , procExtMsgCallback_=None
                        , phasedXFCallback_=phasedXFCallback_
                        , aliasName_=aliasName_
                        , bSyncTask_=True
                        , bMainTask_=bMainTask_
                        , bMessagingTask_=False
                        , bBlockingExtQueue_=False
                        , bRefToCurTaskRequired_=bRefToCurTaskRequired_
                        , runCallbackFrequency_=runCallbackFrequency_)
#END class XFSyncTask


class AsyncTask(RCTask):
    """
    Derived from class RCTask, this RC task class is designed to create
    asynchronous task instances by passing one or more callback functions.

    See:
    -----
        >>> RCTask
        >>> SyncTask
        >>> XFAsyncTask
        >>> AsyncCommTask
    """

    __slots__ = []

    def __init__( self
                , runCallback_
                , setupCallback_         =None
                , teardownCallback_      =None
                , aliasName_             : str =None
                , bMainTask_             =False
                , bRefToCurTaskRequired_ =False
                , runCallbackFrequency_  : Union[int, float] =0):
        """
        Constructor of this class.

        Parameters:
        -------------
            - runCallback_ :
              mandatory callback function of the run phase
            - setupCallback_ :
              callback function of the setup phase
            - teardownCallback_ :
              callback function of the teardown phase
            - aliasName_ :
              if specified, the alias name of this instance, an arbitrary
              non-empty and printable string literal without spaces which
              optionally may have a trailing '_'
            - bMainTask_ :
              if True this instance will be configured to be application's
              main task, a reqular task otherwise
            - bRefToCurTaskRequired_ :
              if True a reference to this instance will be passed as first
              argument whenever specified callbacks are called by the framework
            - runCallbackFrequency_ :
              run phase frequency of this task
              (milliseconds for integer values, seconds for floating-point values)

        Note:
        ------
            - Note that the callback functions to be passed to the constructor
              are in fact 3-PhXF callbacks executed by the framework when the
              task is started.

        See:
        -----
            >>> ITask.isSyncTask
            >>> ITask.aliasName
            >>> IRCTask.isMainTask
            >>> IRCTask.runPhaseFrequencyMS
        """
        super().__init__( runCallback_=runCallback_
                        , setupCallback_=setupCallback_
                        , teardownCallback_=teardownCallback_
                        , procExtMsgCallback_=None
                        , phasedXFCallback_=None
                        , aliasName_=aliasName_
                        , bSyncTask_=False
                        , bMainTask_=bMainTask_
                        , bMessagingTask_=False
                        , bBlockingExtQueue_=False
                        , bRefToCurTaskRequired_=bRefToCurTaskRequired_
                        , runCallbackFrequency_=runCallbackFrequency_)
#END class AsyncTask


class XFAsyncTask(RCTask):
    """
    Derived from class RCTask, this RC task class is designed to create
    asynchronous task instances by passing a class instance or a class
    supporting 3-PhXF callbacks.

    See:
    -----
        >>> RCTask
        >>> AsyncTask
        >>> XFSyncTask
        >>> XFAsyncCommTask
    """

    __slots__ = []

    def __init__( self
                , phasedXFCallback_
                , aliasName_             : str =None
                , bMainTask_             =False
                , bRefToCurTaskRequired_ =False
                , runCallbackFrequency_  : Union[int, float] =0):
        """
        Constructor of this class.

        Parameters:
        -------------
            - phasedXFCallback_ :
              mandatory class (instance) supporting 3-PhXF callbacks
            - aliasName_ :
              if specified, the alias name of this instance, an arbitrary
              non-empty and printable string literal without spaces which
              optionally may have a trailing '_'
            - bMainTask_ :
              if True this instance will be configured to be application's
              main task, a reqular task otherwise
            - bRefToCurTaskRequired_ :
              if True a reference to this instance will be passed as first
              argument whenever specified callbacks are called by the framework
            - runCallbackFrequency_ :
              run phase frequency of this task
              (milliseconds for integer values, seconds for floating-point values)

        See:
        -----
            >>> ITask.isSyncTask
            >>> ITask.aliasName
            >>> IRCTask.isMainTask
            >>> IRCTask.runPhaseFrequencyMS
        """
        super().__init__( runCallback_=None
                        , setupCallback_=None
                        , teardownCallback_=None
                        , procExtMsgCallback_=None
                        , phasedXFCallback_=phasedXFCallback_
                        , aliasName_=aliasName_
                        , bSyncTask_=False
                        , bMainTask_=bMainTask_
                        , bMessagingTask_=False
                        , bBlockingExtQueue_=False
                        , bRefToCurTaskRequired_=bRefToCurTaskRequired_
                        , runCallbackFrequency_=runCallbackFrequency_)
#END class XFAsyncTask


class SyncCommTask(RCCommTask):
    """
    Derived from class RCCommTask, this class is designed to create synchronous
    task instances with full support for external queue by passing one or more
    callback functions.

    See:
    -----
        >>> RCCommTask
        >>> SyncTask
        >>> AsyncCommTask
        >>> XFSyncCommTask
    """

    __slots__ = []

    def __init__( self
                , runCallback_
                , procExtMsgCallback_
                , setupCallback_         =None
                , teardownCallback_      =None
                , aliasName_             : str =None
                , bMainTask_             =False
                , bRefToCurTaskRequired_ =False
                , runCallbackFrequency_  : Union[int, float] =0):
        """
        Constructor of this class.

        Parameters:
        -------------
            - runCallback_ :
              mandatory callback function of the run phase
            - procExtMsgCallback_ :
              mandatory callback function for processing external messages
            - setupCallback_ :
              callback function of the setup phase
            - teardownCallback_ :
              callback function of the teardown phase
            - aliasName_ :
              if specified, the alias name of this instance, an arbitrary
              non-empty and printable string literal without spaces which
              optionally may have a trailing '_'
            - bMainTask_ :
              if True this instance will be configured to be application's
              main task, a reqular task otherwise
            - bRefToCurTaskRequired_ :
              if True a reference to this instance will be passed as first
              argument whenever specified callbacks are called by the framework
            - runCallbackFrequency_ :
              run phase frequency of this task
              (milliseconds for integer values, seconds for floating-point values)

        Note:
        ------
            - Note that the callback functions to be passed to the constructor
              are in fact 3-PhXF callbacks executed by the framework when the
              task is started.

        See:
        -----
            >>> ITask.isSyncTask
            >>> ITask.aliasName
            >>> IRCTask.isMainTask
            >>> IRCTask.isMessagingTask
            >>> IRCTask.runPhaseFrequencyMS
        """
        super().__init__( runCallback_=runCallback_
                        , setupCallback_=setupCallback_
                        , teardownCallback_=teardownCallback_
                        , procExtMsgCallback_=procExtMsgCallback_
                        , phasedXFCallback_=None
                        , aliasName_=aliasName_
                        , bSyncTask_=True
                        , bMainTask_=bMainTask_
                        , bBlockingExtQueue_=False
                        , bRefToCurTaskRequired_=bRefToCurTaskRequired_
                        , runCallbackFrequency_=runCallbackFrequency_)
#END class SyncCommTask


class XFSyncCommTask(RCCommTask):
    """
    Derived from class RCCommTask, this class is designed to create synchronous
    task instances with full support for external queue by passing a class
    instance or a class supporting 3-PhXF callbacks.

    See:
    -----
        >>> RCCommTask
        >>> SyncCommTask
        >>> XFAsyncCommTask
    """

    __slots__ = []

    def __init__( self
                , phasedXFCallback_
                , aliasName_             : str =None
                , bMainTask_             =False
                , bRefToCurTaskRequired_ =False
                , runCallbackFrequency_  : Union[int, float] =0):
        """
        Constructor of this class.

        Parameters:
        -------------
            - phasedXFCallback_ :
              mandatory class (instance) supporting 3-PhXF callbacks
            - aliasName_ :
              if specified, the alias name of this instance, an arbitrary
              non-empty and printable string literal without spaces which
              optionally may have a trailing '_'
            - bMainTask_ :
              if True this instance will be configured to be application's
              main task, a reqular task otherwise
            - bRefToCurTaskRequired_ :
              if True a reference to this instance will be passed as first
              argument whenever specified callbacks are called by the framework
            - runCallbackFrequency_ :
              run phase frequency of this task
              (milliseconds for integer values, seconds for floating-point values)

        See:
        -----
            >>> ITask.isSyncTask
            >>> ITask.aliasName
            >>> IRCTask.isMainTask
            >>> IRCTask.isMessagingTask
            >>> IRCTask.runPhaseFrequencyMS
            >>> IRCCommTask.isExternalQueueBlocking
            >>> IRCCommTask.TriggerExternalQueueProcessing()
        """
        super().__init__( runCallback_=None
                        , setupCallback_=None
                        , teardownCallback_=None
                        , procExtMsgCallback_=None
                        , phasedXFCallback_=phasedXFCallback_
                        , aliasName_=aliasName_
                        , bSyncTask_=True
                        , bMainTask_=bMainTask_
                        , bBlockingExtQueue_=False
                        , bRefToCurTaskRequired_=bRefToCurTaskRequired_
                        , runCallbackFrequency_=runCallbackFrequency_)
#END class XFSyncCommTask


class AsyncCommTask(RCCommTask):
    """
    Derived from class RCCommTask, this class is designed to create asynchronous
    task instances with full support for external queue by passing one or more
    callback functions.

    See:
    -----
        >>> RCCommTask
        >>> SyncCommTask
        >>> XFAsyncCommTask
    """

    __slots__ = []

    def __init__( self
                , runCallback_
                , procExtMsgCallback_
                , setupCallback_         =None
                , teardownCallback_      =None
                , aliasName_             : str =None
                , bMainTask_             =False
                , bRefToCurTaskRequired_ =False
                , runCallbackFrequency_  : Union[int, float] =0):
        """
        Constructor of this class.

        Parameters:
        -------------
            - runCallback_ :
              mandatory callback function of the run phase
            - procExtMsgCallback_ :
              mandatory callback function for processing external messages
            - setupCallback_ :
              callback function of the setup phase
            - teardownCallback_ :
              callback function of the teardown phase
            - aliasName_ :
              if specified, the alias name of this instance, an arbitrary
              non-empty and printable string literal without spaces which
              optionally may have a trailing '_'
            - bMainTask_ :
              if True this instance will be configured to be application's
              main task, a reqular task otherwise
            - bRefToCurTaskRequired_ :
              if True a reference to this instance will be passed as first
              argument whenever specified callbacks are called by the framework
            - runCallbackFrequency_ :
              run phase frequency of this task
              (milliseconds for integer values, seconds for floating-point values)

        Note:
        ------
            - Note that the callback functions to be passed to the constructor
              are in fact 3-PhXF callbacks executed by the framework when the
              task is started.

        See:
        -----
            >>> ITask.isSyncTask
            >>> ITask.aliasName
            >>> IRCTask.isMainTask
            >>> IRCTask.isMessagingTask
            >>> IRCTask.runPhaseFrequencyMS
            >>> IRCCommTask.isExternalQueueBlocking
            >>> IRCCommTask.TriggerExternalQueueProcessing()
        """
        super().__init__( runCallback_=runCallback_
                        , setupCallback_=setupCallback_
                        , teardownCallback_=teardownCallback_
                        , procExtMsgCallback_=procExtMsgCallback_
                        , phasedXFCallback_=None
                        , aliasName_=aliasName_
                        , bSyncTask_=False
                        , bMainTask_=bMainTask_
                        , bBlockingExtQueue_=False
                        , bRefToCurTaskRequired_=bRefToCurTaskRequired_
                        , runCallbackFrequency_=runCallbackFrequency_)
#END class AsyncCommTask


class XFAsyncCommTask(RCCommTask):
    """
    Derived from class RCCommTask, this class is designed to create asynchronous
    task instances with full support for external queue by passing a class
    instance or a class supporting 3-PhXF callbacks.

    See:
    -----
        >>> RCCommTask
        >>> AsyncCommTask
        >>> XFSyncCommTask
    """

    __slots__ = []

    def __init__( self
                , phasedXFCallback_
                , aliasName_             : str =None
                , bMainTask_             =False
                , bRefToCurTaskRequired_ =False
                , runCallbackFrequency_  : Union[int, float] =0):
        """
        Constructor of this class.

        Parameters:
        -------------
            - phasedXFCallback_ :
              mandatory class (instance) supporting 3-PhXF callbacks
            - aliasName_ :
              if specified, the alias name of this instance, an arbitrary
              non-empty and printable string literal without spaces which
              optionally may have a trailing '_'
            - bMainTask_ :
              if True this instance will be configured to be application's
              main task, a reqular task otherwise
            - bRefToCurTaskRequired_ :
              if True a reference to this instance will be passed as first
              argument whenever specified callbacks are called by the framework
            - runCallbackFrequency_ :
              run phase frequency of this task
              (milliseconds for integer values, seconds for floating-point values)

        See:
        -----
            >>> ITask.isSyncTask
            >>> ITask.aliasName
            >>> IRCTask.isMainTask
            >>> IRCTask.isMessagingTask
            >>> IRCTask.runPhaseFrequencyMS
            >>> IRCCommTask.isExternalQueueBlocking
            >>> IRCCommTask.TriggerExternalQueueProcessing()
        """
        super().__init__( runCallback_=None
                        , setupCallback_=None
                        , teardownCallback_=None
                        , procExtMsgCallback_=None
                        , phasedXFCallback_=phasedXFCallback_
                        , aliasName_=aliasName_
                        , bSyncTask_=False
                        , bMainTask_=bMainTask_
                        , bBlockingExtQueue_=False
                        , bRefToCurTaskRequired_=bRefToCurTaskRequired_
                        , runCallbackFrequency_=runCallbackFrequency_)
#END class XFAsyncCommTask


class MessageDrivenTask(RCCommTask):
    """
    Derived from class RCCommTask, this class is designed to create asynchronous
    task instances with full support for blocking external queue by passing one
    or more callback functions.

    See:
    -----
        >>> RCCommTask
        >>> XFMessageDrivenTask
    """

    __slots__ = []

    def __init__( self
                , procExtMsgCallback_
                , setupCallback_         =None
                , teardownCallback_      =None
                , aliasName_             : str =None
                , bMainTask_             =False
                , bRefToCurTaskRequired_ =False
                , pollingFrequency_      =100):
        """
        Constructor of this class.

        Parameters:
        -------------
            - procExtMsgCallback_ :
              mandatory callback function for processing external messages
            - setupCallback_ :
              callback function of the setup phase
            - teardownCallback_ :
              callback function of the teardown phase
            - aliasName_ :
              if specified, the alias name of this instance, an arbitrary
              non-empty and printable string literal without spaces which
              optionally may have a trailing '_'
            - bMainTask_ :
              if True this instance will be configured to be application's
              main task, a reqular task otherwise
            - bRefToCurTaskRequired_ :
              if True a reference to this instance will be passed as first
              argument whenever specified callbacks are called by the framework
            - pollingFrequency_ :
              frequency at which to check for new messages delivered
              (milliseconds for integer values, seconds for floating-point values)

        Note:
        ------
            - From technical point of view there is actually no need for polling
              a blocking queue.
            - But, the polling frequency to be specified is mandatory to make
              the task remains responsive, especially whenever the framework
              has to initiate its coordinated shutdown sequence.

        See:
        -----
            >>> ITask.isSyncTask
            >>> ITask.aliasName
            >>> IRCTask.isMainTask
            >>> IRCTask.isMessagingTask
            >>> IRCTask.runPhaseFrequencyMS
            >>> IRCCommTask.isExternalQueueBlocking
        """
        super().__init__( runCallback_=None
                        , setupCallback_=setupCallback_
                        , teardownCallback_=teardownCallback_
                        , procExtMsgCallback_=procExtMsgCallback_
                        , phasedXFCallback_=None
                        , aliasName_=aliasName_
                        , bSyncTask_=False
                        , bMainTask_=bMainTask_
                        , bBlockingExtQueue_=True
                        , bRefToCurTaskRequired_=bRefToCurTaskRequired_
                        , runCallbackFrequency_=pollingFrequency_)
#END class MessageDrivenTask


class XFMessageDrivenTask(RCCommTask):
    """
    Derived from class RCCommTask, this class is designed to create asynchronous
    task instances with full support for blocking external queue by passing a
    class instance or a class supporting 3-PhXF callbacks.

    See:
    -----
        >>> RCCommTask
        >>> MessageDrivenTask
    """

    __slots__ = []

    def __init__( self
                , phasedXFCallback_
                , aliasName_             : str =None
                , bMainTask_             =False
                , bRefToCurTaskRequired_ =False
                , pollingFrequency_      =100):
        """
        Constructor of this class.

        Parameters:
        -------------
            - procExtMsgCallback_ :
              mandatory class (instance) supporting 3-PhXF callbacks
            - aliasName_ :
              if specified, the alias name of this instance, an arbitrary
              non-empty and printable string literal without spaces which
              optionally may have a trailing '_'
            - bMainTask_ :
              if True this instance will be configured to be application's
              main task, a reqular task otherwise
            - bRefToCurTaskRequired_ :
              if True a reference to this instance will be passed as first
              argument whenever specified callbacks are called by the framework
            - pollingFrequency_ :
              frequency at which to check for new messages delivered
              (milliseconds for integer values, seconds for floating-point values)

        Note:
        ------
            - From technical point of view there is actually no need for polling
              a blocking queue.
            - But, the polling frequency to be specified is mandatory to make
              the task remains responsive, especially whenever the framework
              has to initiate its coordinated shutdown sequence.

        See:
        -----
            >>> ITask.isSyncTask
            >>> ITask.aliasName
            >>> IRCTask.isMainTask
            >>> IRCTask.isMessagingTask
            >>> IRCTask.runPhaseFrequencyMS
            >>> IRCCommTask.isExternalQueueBlocking
        """
        super().__init__( runCallback_=None
                        , setupCallback_=None
                        , teardownCallback_=None
                        , procExtMsgCallback_=None
                        , phasedXFCallback_=phasedXFCallback_
                        , aliasName_=aliasName_
                        , bSyncTask_=False
                        , bMainTask_=bMainTask_
                        , bBlockingExtQueue_=True
                        , bRefToCurTaskRequired_=bRefToCurTaskRequired_
                        , runCallbackFrequency_=pollingFrequency_)
#END class XFMessageDrivenTask


def GetCurTask() -> Union[IRCTask, IRCCommTask, None]:
    """
    This function enables application code to get access to the application
    task currently executed by framework.

     Returns:
     ----------
        - None if:
              - the framework or the currently executed task is affected by
                the limited RTE mode, or
              - not called from within the 3-PhXF of the currently executed
                instance of class RCTask or RCCommTask,
        - currently executed instance of class RCTask or RCCommTask otherwise.
          Note that the task state of the returned task is 'running' unless
          the call was made out of the teardown phase.

    See:
    ------
        >>> IRCTask.isRunning
    """
    return _FwApiConnectorAP._APGetCurRcTask()
