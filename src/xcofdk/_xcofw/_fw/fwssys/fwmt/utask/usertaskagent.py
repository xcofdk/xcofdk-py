# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : usertaskagent.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum   import IntEnum
from typing import Any
from typing import Union

from xcofdk.fwcom     import CompoundTUID
from xcofdk.fwcom     import EXmsgPredefinedID
from xcofdk.fwapi     import ITaskError
from xcofdk.fwapi     import IPayload
from xcofdk.fwapi     import ITask
from xcofdk.fwapi.xmt import ITaskProfile
from xcofdk.fwapi.xmt import IXTask

from _fw.fwssys.assys.ifs.ifxunit         import _IXUnit
from _fw.fwssys.assys.ifs.ifutask         import _IUserTask
from _fw.fwssys.assys.ifs.ifutagent       import _IUTAgent
from _fw.fwssys.fwcore.logging            import logif
from _fw.fwssys.fwcore.ipc.tsk.taskutil   import _TaskUtil
from _fw.fwssys.fwcore.types.commontypes  import _CommonDefines
from _fw.fwssys.fwcore.types.commontypes  import override
from _fw.fwssys.fwerrh.fwerrorcodes       import _EFwErrorCode
from _fw.fwssys.fwmsg.apiimpl.xmsgmgrimpl import _XMsgMgrImpl
from _fw.fwssys.fwmt.utask.usertask       import _UserTask

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _UserTaskAgent(_IUTAgent):
    __slots__ = [ '__ut' , '__xti' ]

    def __init__(self, xti_ : IXTask, xtPrf_ : ITaskProfile):
        self.__ut  = None
        self.__xti = xti_
        super().__init__()

        _ut = _UserTask(self, xtPrf_)
        if not _ut._isAttachedToFW:
            self.__xti = None
        else:
            self.__ut = _ut

    def __str__(self):
        return self.ToString()

    @_IUTAgent._xUnit.getter
    def _xUnit(self) -> _IXUnit:
        return self.__ut

    @_IUTAgent._xtInst.getter
    def _xtInst(self) -> IXTask:
        return self.__xti

    @property
    def _uTask(self) -> _IUserTask:
        return self.__ut

    @override
    def Start(self, *args_, **kwargs_) -> bool:
        return False if self.__isInvalid else self.__ut._Start(*args_, **kwargs_)

    @override
    def Stop(self) -> bool:
        return False if self.__isInvalid else self.__ut._Stop()

    @override
    def Cancel(self) -> bool:
        return False if self.__isInvalid else self.__ut._Stop(bCancel_=True)

    @override
    def Join(self, maxWaitTime_: Union[int, float, None] =None) -> bool:
        return False if self.__isInvalid else self.__ut._Join(timeout_=maxWaitTime_)

    @override
    def DetachFromFW(self):
        if not self.__isInvalid:
            self.__ut._DetachFromFW()

    @IXTask.isAttachedToFW.getter
    def isAttachedToFW(self) -> bool:
        return False if self.__isInvalid else self.__ut._isAttachedToFW

    @IXTask.isDetachedFromFW.getter
    def isDetachedFromFW(self) -> bool:
        return True if self.__isInvalid else not self.__ut._isAttachedToFW

    @IXTask.isStarted.getter
    def isStarted(self) -> bool:
        return False if self.__isInvalid else self.__ut._isStarted

    @IXTask.isPendingRun.getter
    def isPendingRun(self) -> bool:
        return False if self.__isInvalid else self.__ut._isPendingRun

    @IXTask.isRunning.getter
    def isRunning(self) -> bool:
        return False if self.__isInvalid else self.__ut._isRunning

    @IXTask.isDone.getter
    def isDone(self) -> bool:
        return False if self.__isInvalid else self.__ut._isDone

    @IXTask.isCanceled.getter
    def isCanceled(self) -> bool:
        return False if self.__isInvalid else self.__ut._isCanceled

    @IXTask.isFailed.getter
    def isFailed(self) -> bool:
        return False if self.__isInvalid else self.__ut._isFailed

    @IXTask.isTerminated.getter
    def isTerminated(self) -> bool:
        return False if self.__isInvalid else self.__ut._isTerminated

    @IXTask.isTerminating.getter
    def isTerminating(self) -> bool:
        return False if self.__isInvalid else self.__ut._isTerminating

    @IXTask.isStopping.getter
    def isStopping(self) -> bool:
        return False if self.__isInvalid else self.__ut._isStopping

    @IXTask.isCanceling.getter
    def isCanceling(self) -> bool:
        return False if self.__isInvalid else self.__ut._isCanceling

    @IXTask.isAborting.getter
    def isAborting(self) -> bool:
        return False if self.__isInvalid else self.__ut._isAborting

    @IXTask.isSyncTask.getter
    def isSyncTask(self) -> bool:
        return False if self.__isInvalid else self.__ut._isSyncTask

    @IXTask.isFirstRunPhaseIteration.getter
    def isFirstRunPhaseIteration(self) -> bool:
        _curNo = self.currentRunPhaseIterationNo
        return False if _curNo is None else _curNo == 0

    @IXTask.taskUID.getter
    def taskUID(self) -> int:
        return None if self.__isInvalid else self.__ut._taskUID

    @IXTask.taskName.getter
    def taskName(self) -> str:
        return None if self.__isInvalid else self.__ut._taskName

    @IXTask.aliasName.getter
    def aliasName(self) -> str:
        return None if self.__isInvalid else self.__ut._taskAliasName

    @IXTask.taskCompoundUID.getter
    def taskCompoundUID(self) -> CompoundTUID:
        return None if self.__isInvalid else self.__ut._taskCompUID

    @IXTask.currentRunPhaseIterationNo.getter
    def currentRunPhaseIterationNo(self) -> int:
        return -1 if self.__isInvalid else self.__ut._curRunPhaseIterationNo

    @override
    def GetTaskOwnedData(self, bDeserialize_ =True) -> Any:
        return None if self.__isInvalid else self.__ut._GetTaskOwnedData(bDeser_=bDeserialize_)

    @override
    def SetTaskOwnedData(self, taskOwnedData_ : Any, bSerialize_ =False):
        if not self.__isInvalid:
            self.__ut._SetTaskOwnedData(taskOwnedData_, bSer_=bSerialize_)

    @override
    def SendMessage( self
                   , rxTask_       : Union[ITask, IntEnum, int]
                   , msgLabelID_   : Union[IntEnum, int]   =EXmsgPredefinedID.DontCare
                   , msgClusterID_ : Union[IntEnum, int]   =EXmsgPredefinedID.DontCare
                   , msgPayload_   : Union[IPayload, dict] =None) -> int:
        return 0 if self.__isInvalid else _XMsgMgrImpl._SendXMsg(rxTask_, lblID_=msgLabelID_, clrID_=msgClusterID_, payload_=msgPayload_)

    @override
    def BroadcastMessage( self
                        , msgLabelID_   : Union[IntEnum, int]
                        , msgClusterID_ : Union[IntEnum, int]   =EXmsgPredefinedID.DontCare
                        , msgPayload_   : Union[IPayload, dict] =None) -> int:
        return 0 if self.__isInvalid else _XMsgMgrImpl._BroadcastXMsg(msgLabelID_, clrID_=msgClusterID_, payload_=msgPayload_)

    @override
    def TriggerExternalQueueProcessing(self) -> int:
        return -1 if self.__isInvalid else self.__ut._TriggerQueueProcessing(bExtQueue_=True)

    @IXTask.isErrorFree.getter
    def isErrorFree(self) -> bool:
        return False if self.__isInvalid else self.__ut._isErrorFree

    @IXTask.isFatalErrorFree.getter
    def isFatalErrorFree(self) -> bool:
        return False if self.__isInvalid else self.__ut._isFatalErrorFree

    @IXTask.currentError.getter
    def currentError(self) -> ITaskError:
        return None if self.__isInvalid else self.__ut._currentError

    @override
    def ClearCurrentError(self) -> bool:
        return False if self.__isInvalid else self.__ut._ClearCurrentError()

    @override
    def SetError(self, errorMsg_ : str):
        if not self.__isInvalid:
            self.__ut._SetTaskError(False, errorMsg_, None)

    @override
    def SetErrorEC(self, errorMsg_ : str, errorCode_: int):
        if not self.__isInvalid:
            self.__ut._SetTaskError(False, errorMsg_, errorCode_)

    @override
    def SetFatalError(self, errorMsg_ : str):
        if not self.__isInvalid:
            self.__ut._SetTaskError(True, errorMsg_, None)

    @override
    def SetFatalErrorEC(self, errorMsg_ : str, errorCode_: int):
        if not self.__isInvalid:
            self.__ut._SetTaskError(True, errorMsg_, errorCode_)

    @IXTask.isMainTask.getter
    def isMainTask(self) -> bool:
        _tp = self.taskProfile
        return False if _tp is None else _tp.isMainTask

    @IXTask.taskProfile.getter
    def taskProfile(self) -> ITaskProfile:
        return None if self.__isInvalid else self.__ut._taskProfile

    @override
    def SelfCheck(self) -> bool:
        return False if self.__isInvalid else self.__ut._SelfCheck()

    @override
    def SelfCheckSleep(self, sleepTime_: Union[int, float] =None) -> bool:
        if self.__isInvalid:
            return False

        if sleepTime_ is None:
            sleepTime_ = 20
        if isinstance(sleepTime_, float):
            sleepTime_ = int(1000*sleepTime_)
        if not (isinstance(sleepTime_, int) and (sleepTime_>0)):
            logif._LogErrorEC(_EFwErrorCode.UE_00257, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTaskAgent_TID_001).format(type(sleepTime_).__name__))
            return False

        res = self.SelfCheck()
        if res :
            _TaskUtil.SleepMS(sleepTime_)
            res = self.SelfCheck()
        return res

    @override
    def ToString(self) -> str:
        return _CommonDefines._STR_EMPTY if self.__isInvalid else self.__ut._ToString()

    @property
    def __isInvalid(self) -> bool:
        return self.__ut is None
