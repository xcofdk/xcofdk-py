# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : atask.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from typing import Union as _PyUnion

from xcofdk._xcofw.fw.fwssys.fwcore.logging.xcoexception     import _XcoExceptionRoot
from xcofdk._xcofw.fw.fwssys.fwcore.base.gtimeout            import _Timeout
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcdefines             import _ELcCompID
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcproxy               import _LcProxy
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcproxyclient         import _LcProxyClient
from xcofdk._xcofw.fw.fwssys.fwcore.lcmon.lcmontlb           import _LcDynamicTLB
from xcofdk._xcofw.fw.fwssys.fwcore.lcmon.lcmontlb           import _LcCeaseTLB
from xcofdk._xcofw.fw.fwssys.fwcore.lcmon.lcmontlb           import _ELcCeaseTLBState
from xcofdk._xcofw.fw.fwssys.fwcore.types.aprofile           import _AbstractProfile
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.aexecutable      import _AbstractExecutable
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.sync.semaphore       import _BinarySemaphore
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.sync.mutex           import _Mutex
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.ataskop          import _ATaskOperationPreCheck
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskbadge        import _TaskBadge
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.execprofile      import _ExecutionProfile
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskerror        import _TaskError
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskstate        import _TaskState
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil         import _TaskUtil
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil         import _PyThread
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil         import _EFwApiBookmarkID
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil         import _ETaskApiContextID
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil         import _ETaskExecutionPhaseID
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject            import _AbstractSlotsObject
from xcofdk._xcofw.fw.fwssys.fwerrh.euerrhandler             import _EuErrorHandler

class _AbstractTask(_EuErrorHandler):

    __slots__  = [ '__mtxTST'   , '__tskState'  , '__tskBadge' , '__tskError' , '__linkedPyThrd'
                 , '__execConn' , '__euRNum'    , '__fwapiBM'  , '__lcDynTLB' , '__lcCeaseTLB'
                 , '__tskACtx'  , '__tskXPhase'
                 ]

    def __init__(self):
        super().__init__()
        self.__euRNum       = 0
        self.__mtxTST       = None
        self.__fwapiBM      = _EFwApiBookmarkID.eNone
        self.__tskACtx      = _ETaskApiContextID.eDontCare
        self.__tskError     = None
        self.__tskState     = None
        self.__execConn     = None
        self.__lcDynTLB     = None
        self.__tskBadge     = None
        self.__tskXPhase    = _ETaskExecutionPhaseID.eNone
        self.__lcCeaseTLB   = None
        self.__linkedPyThrd = None

    def __str__(self):
        return self.ToString()

    @property
    def _tskState(self):
        return self.__tskState

    @_tskState.setter
    def _tskState(self, val_):
        self.__tskState = val_

    @property
    def _tskXPhase(self):
        return self.__tskXPhase

    @_tskXPhase.setter
    def _tskXPhase(self, val_):
        self.__tskXPhase = val_

    @property
    def _tskApiCtx(self):
        return self.__tskACtx

    @_tskApiCtx.setter
    def _tskApiCtx(self, val_):
        self.__tskACtx = val_

    @property
    def _tskBadge(self):
        return self.__tskBadge

    @_tskBadge.setter
    def _tskBadge(self, val_):
        self.__tskBadge = val_

    @property
    def _tskError(self):
        return self.__tskError

    @_tskError.setter
    def _tskError(self, val_):
        self.__tskError= val_

    @property
    def _linkedPyThrd(self):
        return self.__linkedPyThrd

    @_linkedPyThrd.setter
    def _linkedPyThrd(self, val_):
        self.__linkedPyThrd = val_

    @property
    def _execConn(self):
        return self.__execConn

    @_execConn.setter
    def _execConn(self, val_):
        self.__execConn = val_

    @property
    def _euRNum(self):
        return self.__euRNum

    @_euRNum.setter
    def _euRNum(self, val_):
        self.__euRNum = val_

    @property
    def _fwapiBM(self):
        return self.__fwapiBM

    @_fwapiBM.setter
    def _fwapiBM(self, val_):
        self.__fwapiBM = val_

    @property
    def _lcDynTLB(self):
        return self.__lcDynTLB

    @_lcDynTLB.setter
    def _lcDynTLB(self, val_):
        self.__lcDynTLB = val_

    @property
    def _lcCeaseTLB(self):
        return self.__lcCeaseTLB

    @_lcCeaseTLB.setter
    def _lcCeaseTLB(self, val_):
        self.__lcCeaseTLB = val_

    @property
    def _tstMutex(self):
        return self.__mtxTST

    @_tstMutex.setter
    def _tstMutex(self, mtxTST_):
        self.__mtxTST = mtxTST_

    @property
    def isValid(self):
        return not self._isInvalid

    @property
    def isFwThread(self):
        return False if self._isInvalid else self._tskBadge.isFwThread

    @property
    def isFwTask(self):
        return False if self._isInvalid else self._tskBadge.isFwTask

    @property
    def isFwMain(self):
        return False if self._isInvalid else self._tskBadge.isFwMain

    @property
    def isCurrentTask(self):
        return False if self._isInvalid else _TaskUtil.IsCurPyThread(self.linkedPyThread)

    @property
    def isAlive(self) -> bool:
        return self._isAlive

    @property
    def isInitialized(self):
        return False if self._isInvalid else self._tskState.isInitialized

    @property
    def isStarted(self):
        return False if self._isInvalid else self._tskState.isStarted

    @property
    def isRunning(self) -> bool:
        return False if self._isInvalid else self._tskState.isRunning

    @property
    def isDone(self):
        return False if self._isInvalid else self._tskState.isDone

    @property
    def isFailed(self):
        return False if self._isInvalid else self._tskState.isFailed

    @property
    def isTerminating(self):
        return False if self._isInvalid else self._tskState.isTerminating

    @property
    def isTerminated(self):
        return False if self._isInvalid else self._tskState.isTerminated

    @property
    def isStopping(self):
        return False if self._isInvalid else self._tskState.isStopping

    @property
    def isAborting(self):
        return False if self._isInvalid else self._tskState.isAborting

    @property
    def isPendingStopRequest(self):
        return False if self._isInvalid else self._tskState.isPendingStopRequest

    @property
    def isStateTransitional(self):
        return False if self._isInvalid else self._tskState.isTransitional

    @property
    def isErrorFree(self):
        return False if self._isInvalid else self._tskError.isErrorFree

    @property
    def isEnclosingPyThread(self) -> bool:
        return False if self._isInvalid else self._tskBadge.isEnclosingPyThread

    @property
    def isEnclosingStartupThread(self) -> bool:
        return False if self._isInvalid else self._tskBadge.isEnclosingStartupThread

    @property
    def isAutoStartEnclosedPyThreadEnabled(self) -> bool:
        return False if self._isInvalid else self._isAutoStartEnclosedPyThreadEnabled

    @property
    def isAutoEnclosed(self):
        return False if self._isInvalid else self._tskBadge.isAutoEnclosed

    @property
    def isDrivingExecutable(self):
        return False if self._isInvalid else self._tskBadge.isDrivingExecutable

    @property
    def isDrivingXTask(self):
        return False if self._isInvalid else self._tskBadge.isDrivingXTask

    @property
    def isInLcCeaseMode(self) -> bool:
        return not self.eLcCeaseTLBState.isNone

    @property
    def taskID(self) -> int:
        return None if self._isInvalid else self._tskBadge.taskID

    @property
    def taskName(self) -> str:
        return None if self._isInvalid else self._tskBadge.taskName

    @property
    def taskUniqueName(self) -> str:
        return None if self._isInvalid else self._tskBadge.taskUniqueName

    @property
    def taskStateID(self) -> _TaskState._EState:
        return None if self._isInvalid else self._tskState.GetStateID()

    @property
    def threadUID(self) -> int:
        return None if self._isInvalid else self._tskBadge.threadUID

    @property
    def threadNID(self) -> int:
        return None if self._isInvalid else self._tskBadge.threadNID

    @property
    def taskBadge(self) -> _TaskBadge:
        return self._tskBadge

    @property
    def taskError(self) -> _TaskError:
        return self._tskError

    @property
    def linkedPyThread(self) -> _PyThread:
        return self._linkedPyThrd

    @property
    def linkedExecutable(self) -> _AbstractExecutable:
        return self._linkedExecutable

    @property
    def xtaskConnector(self):
        return self._xtaskConnector

    @property
    def abstractTaskProfile(self) -> _AbstractProfile:
        return self._abstractTaskProfile

    @property
    def executionProfile(self) -> _ExecutionProfile:
        return self._executionProfile

    @property
    def euRNumber(self) -> int:
        return self._euRNumber

    @property
    def eTaskXPhase(self) -> _ETaskExecutionPhaseID:
        return self._GetTaskXPhase()

    @property
    def eTaskApiContext(self) -> _ETaskApiContextID:
        return self._GetTaskApiContext()

    @property
    def eFwApiBookmarkID(self) -> _EFwApiBookmarkID:
        return self._fwapiBM

    @property
    def eLcCeaseTLBState(self) -> _ELcCeaseTLBState:
        if self._lcCeaseTLB is None:
            res = _ELcCeaseTLBState.eNone
        else:
            res = self._lcCeaseTLB.eCeaseState
        return res

    @property
    def lcDynamicTLB(self) -> _LcDynamicTLB:
        return self._lcDynTLB

    @property
    def lcCeaseTLB(self) -> _LcCeaseTLB:
        return self._lcCeaseTLB

    def CreateLcTLB(self) -> _LcDynamicTLB:
        if self._lcDynTLB is not None:
            pass
        elif self.isAutoEnclosed or (self.linkedExecutable is None):
            self._lcDynTLB = _LcDynamicTLB._GetDummyTLB()
        elif not self.isRunning:
            pass
        else:
            self._lcDynTLB = _LcDynamicTLB._CreateTLB(self, self._tskBadge, self._executionProfile, self._linkedExecutable)
            if self._lcDynTLB is not None:
                self.__UpdateDynTLB(euRNumber_=self.euRNumber, execPhase_=self.eTaskXPhase, tskState_=self.taskStateID)
        return self._lcDynTLB

    def CreateLcCeaseTLB(self, mtxData_: _Mutex, bEnding_: bool) -> _LcCeaseTLB:
        if self._lcDynTLB is None:
            pass
        elif self._lcCeaseTLB is not None:
            pass
        elif self.isAutoEnclosed or (self.linkedExecutable is None):
            pass
        else:
            self._lcCeaseTLB = self._lcDynTLB._CreateCeaseTLB(mtxData_, bEnding_)
        return self._lcCeaseTLB

    def GetLcCompID(self) -> _ELcCompID:
        return self._GetLcCompID()

    def StartTask(self, semStart_: _BinarySemaphore =None, tskOpPreCheck_ : _ATaskOperationPreCheck =None, curTask_ =None) -> bool:
        return False if self._isInvalid else self._StartTask(semStart_=semStart_, tskOpPreCheck_=tskOpPreCheck_, curTask_=curTask_)

    def RestartTask(self, semStart_: _BinarySemaphore =None, tskOpPreCheck_ : _ATaskOperationPreCheck =None, curTask_ =None) -> bool:
        return False if self._isInvalid else self._RestartTask(semStart_=semStart_, tskOpPreCheck_=tskOpPreCheck_, curTask_=curTask_)

    def StopTask(self, semStop_: _BinarySemaphore =None, tskOpPreCheck_ : _ATaskOperationPreCheck =None, curTask_ =None) -> bool:
        return False if self._isInvalid else self._StopTask(semStop_=semStop_, tskOpPreCheck_=tskOpPreCheck_, curTask_=curTask_)

    def JoinTask(self, timeout_: _Timeout =None, tskOpPreCheck_ : _ATaskOperationPreCheck =None, curTask_ =None) -> bool:
        return False if self._isInvalid else self._JoinTask(timeout_=timeout_, tskOpPreCheck_=tskOpPreCheck_, curTask_=curTask_)

    @property
    def _isAlive(self) -> bool:
        if self._linkedPyThrd is None:
            return False
        else:
            self._tskState.GetStateID()
            return self.linkedPyThread.is_alive()

    @property
    def _isFailedByApiExecutionReturn(self):
        return False if self._isInvalid else self._tskState._isFailedByApiExecutionReturn

    @property
    def _linkedExecutable(self) -> _AbstractExecutable:
        return None

    @property
    def _xtaskConnector(self):
        return None

    @property
    def _abstractTaskProfile(self) -> _AbstractProfile:
        return None

    @property
    def _euRNumber(self) -> int:
        return self._euRNum

    def _IncEuRNumber(self) -> int:
        if self._isInvalid: return 0
        self._euRNum += 1
        self.__UpdateDynTLB(euRNumber_=self._euRNum)
        return self._euRNum

    def _PcSetLcProxy(self, lcPxy_ : _PyUnion[_LcProxy, _AbstractSlotsObject], bForceUnset_ =False):
        _LcProxyClient._PcSetLcProxy(self, lcPxy_, bForceUnset_=bForceUnset_)
        if self._PcIsLcProxySet():
            self._PropagateLcProxy()

    def _PropagateLcProxy(self, lcProxy_=None):
        pass

    def _SetGetTaskState(self, eNewState_ : _TaskState._EState) -> _TaskState._EState:
        if self._isInvalid: return None
        res = self._tskState.SetGetStateID(eNewState_)
        self.__UpdateDynTLB(tskState_=res)
        return res

    def _SetTaskXPhase(self, eXPhaseID_ : _ETaskExecutionPhaseID):
        if self._isInvalid: return
        self._tskXPhase = eXPhaseID_
        self.__UpdateDynTLB(execPhase_=eXPhaseID_)

    def _SetTaskApiContext(self, eApiCtxID_ : _ETaskApiContextID):
        if self._isInvalid: return
        self._tskApiCtx = eApiCtxID_

    def _SetFwApiBookmark(self, eFwApiBookmarkID_ : _EFwApiBookmarkID):
        if self._isInvalid: return
        self._fwapiBM = eFwApiBookmarkID_

    def _ProcUnhandledException(self, xcp_: _XcoExceptionRoot):
        return self._ProcUnhandledXcp(xcp_)

    def _ToString(self, *args_, **kwargs_) -> str:
        if self._isInvalid:
            res = type(self).__name__
        else:
            res = '{}: (badge, running, state)=({}, {}, {})'.format(
                type(self).__name__, self._tskBadge.ToString(False, False), self.isRunning, str(self._tskState))
        return res

    def _CleanUp(self):
        if self._tskState is None:
            return

        self.__UpdateDynTLB(bCleanedUp_=True)

        super()._CleanUp()

        self._euRNum       = None
        self._fwapiBM      = None
        self._execConn     = None
        self._lcDynTLB     = None
        self._tskApiCtx    = None
        self._tskXPhase    = None
        self._lcCeaseTLB   = None
        self._linkedPyThrd = None

        if self._tskState is not None:
            self._tskState.CleanUp()
            self._tskState = None
        if self._tskError is not None:
            self._tskError.CleanUp()
            self._tskError = None
        if self._tskBadge is not None:
            self._tskBadge.CleanUp()
            self._tskBadge = None
        if self._tstMutex is not None:
            self._tstMutex.CleanUp()
            self._tstMutex = None

    def __UpdateDynTLB( self
                     , euRNumber_  : int                    =None
                     , execPhase_  : _ETaskExecutionPhaseID =None
                     , tskState_   : _TaskState._EState     =None
                     , bCleanedUp_ : bool                   =None):
        if (self._lcDynTLB is None) or self._lcDynTLB.isDummyTLB:
            pass
        else:
            self._lcDynTLB._UpdateDynTLB(euRNumber_=euRNumber_, execPhase_=execPhase_, tskState_=tskState_, bCleanedUp_=bCleanedUp_)
