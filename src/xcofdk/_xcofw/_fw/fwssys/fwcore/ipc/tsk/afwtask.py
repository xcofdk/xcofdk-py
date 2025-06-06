# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : afwtask.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from typing import Union

from _fw.fwssys.assys.ifs                  import _IUTaskConn
from _fw.fwssys.assys.ifs.ifxunit          import _IXUnit
from _fw.fwssys.assys.ifs.iffwtask         import _IFwTask
from _fw.fwssys.fwcore.base.gtimeout       import _Timeout
from _fw.fwssys.fwcore.lc.lcdefines        import _ELcCompID
from _fw.fwssys.fwcore.lc.ifs.iflcproxy    import _ILcProxy
from _fw.fwssys.fwcore.lc.lcproxyclient    import _LcProxyClient
from _fw.fwssys.fwcore.lc.lcmn.lcmontlb    import _LcDynamicTLB
from _fw.fwssys.fwcore.lc.lcmn.lcmontlb    import _LcCeaseTLB
from _fw.fwssys.fwcore.lc.lcmn.lcmontlb    import _ELcCeaseTLBState
from _fw.fwssys.fwcore.types.afwprofile    import _AbsFwProfile
from _fw.fwssys.fwcore.ipc.sync.semaphore  import _BinarySemaphore
from _fw.fwssys.fwcore.ipc.sync.mutex      import _Mutex
from _fw.fwssys.fwcore.ipc.tsk.ataskop     import _ATaskOpPreCheck
from _fw.fwssys.fwcore.ipc.tsk.taskbadge   import _TaskBadge
from _fw.fwssys.fwcore.ipc.tsk.taskdefs    import _ETaskSelfCheckResultID
from _fw.fwssys.fwcore.ipc.tsk.fwtaskerror import _FwTaskError
from _fw.fwssys.fwcore.ipc.tsk.taskstate   import _TaskState
from _fw.fwssys.fwcore.ipc.tsk.taskutil    import _TaskUtil
from _fw.fwssys.fwcore.ipc.tsk.taskutil    import _PyThread
from _fw.fwssys.fwcore.ipc.tsk.taskutil    import _EFwApiBookmarkID
from _fw.fwssys.fwcore.ipc.tsk.taskutil    import _ETaskApiContextID
from _fw.fwssys.fwcore.ipc.tsk.taskutil    import _ETaskXPhaseID
from _fw.fwssys.fwcore.ipc.tsk.taskxcard   import _TaskXCard
from _fw.fwssys.fwcore.types.aobject       import _AbsSlotsObject
from _fw.fwssys.fwcore.types.commontypes   import override
from _fw.fwssys.fwerrh.logs.xcoexception   import _XcoXcpRootBase
from _fw.fwssys.fwerrh.pcerrhandler        import _PcErrHandler

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _AbsFwTask(_PcErrHandler, _IFwTask):
    __slots__  = [ '__mst' , '__tst' , '__tb' , '__te' , '__dht' , '__uc' , '__sr' , '__xrn' , '__abm' , '__dtlb' , '__ctlb' , '__tcid' , '__tphid' ]

    def __init__(self):
        _PcErrHandler.__init__(self)
        _IFwTask.__init__(self)
        self.__tb    = None
        self.__te    = None
        self.__uc    = None
        self.__tst   = None
        self.__mst   = None
        self.__dht   = None
        self.__ctlb  = None
        self.__dtlb  = None

        self.__sr    = _ETaskSelfCheckResultID.eScrNA
        self.__abm   = _EFwApiBookmarkID.eNA
        self.__xrn   = -1
        self.__tcid  = _ETaskApiContextID.eDontCare
        self.__tphid = _ETaskXPhaseID.eNA

    def __str__(self):
        return self.ToString()

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
    def isPendingRun(self) -> bool:
        return False if self._isInvalid else self._tskState.isPendingRun

    @property
    def isRunning(self) -> bool:
        return False if self._isInvalid else self._tskState.isRunning

    @property
    def isDone(self):
        return False if self._isInvalid else self._tskState.isDone

    @property
    def isCanceled(self):
        return False if self._isInvalid else self._tskState.isCanceled

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
    def isCanceling(self):
        return False if self._isInvalid else self._tskState.isCanceling

    @property
    def isAborting(self):
        return False if self._isInvalid else self._tskState.isAborting

    @property
    def isPendingStopRequest(self):
        return False if self._isInvalid else self._tskState.isPendingStopRequest

    @property
    def isPendingCancelRequest(self):
        return False if self._isInvalid else self._tskState.isPendingCancelRequest

    @property
    def isFailedByXCmdReturn(self):
        return False if self._isInvalid else self._tskState.isFailedByXCmdReturn

    @property
    def isValid(self):
        return not self._isInvalid

    @property
    def isFwMain(self):
        return False if self._isInvalid else self._tskBadge.isFwMain

    @property
    def isCurrentTask(self):
        return False if self._isInvalid else _TaskUtil.IsCurPyThread(self.dHThrd)

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
    def isAutoStartEnclHThrdEnabled(self) -> bool:
        return False if self._isInvalid else self._isAutoStartEnclHThrdEnabled

    @property
    def isAutoEnclosed(self):
        return False if self._isInvalid else self._tskBadge.isAutoEnclosed

    @property
    def isInLcCeaseMode(self) -> bool:
        return not self.ceaseTLBState.isNone

    @property
    def isCFwThread(self):
        return False if self._isInvalid else self._tskBadge.isCFwThread

    @property
    def isErrorHandlingAvailable(self):
        return False if self._isInvalid else not self._tskBadge.isCFwThread

    @property
    def dtaskUID(self) -> int:
        return None if self._isInvalid else self._tskBadge.dtaskUID

    @property
    def dtaskName(self) -> str:
        return None if self._isInvalid else self._tskBadge.dtaskName

    @property
    def daprofile(self) -> _AbsFwProfile:
        return None if self._isInvalid else self._daprofile

    @property
    def dtaskStateID(self) -> _TaskState._EState:
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
    def taskError(self) -> _FwTaskError:
        return self._tskError

    @property
    def dHThrd(self) -> _PyThread:
        return self._dHThrd

    @property
    def dxUnit(self) -> Union[_IXUnit, None]:
        return self._dxUnit

    @property
    def xCard(self) -> _TaskXCard:
        return self._xcard

    @property
    def xrNumber(self) -> int:
        return self._xrNumber

    @property
    def taskXPhase(self) -> _ETaskXPhaseID:
        return self._GetTaskXPhase()

    @property
    def taskApiContext(self) -> _ETaskApiContextID:
        return self._GetTaskApiContext()

    @property
    def fwApiBookmarkID(self) -> _EFwApiBookmarkID:
        return self._fwapiBM

    @property
    def ceaseTLBState(self) -> _ELcCeaseTLBState:
        if self._lcCeaseTLB is None:
            res = _ELcCeaseTLBState.eNone
        else:
            res = self._lcCeaseTLB.ceaseState
        return res

    @property
    def lcDynamicTLB(self) -> _LcDynamicTLB:
        return self._lcDynTLB

    @property
    def lcCeaseTLB(self) -> _LcCeaseTLB:
        return self._lcCeaseTLB

    @property
    def sendOperator(self):
        return None if self._isInvalid else self

    def CreateLcTLB(self) -> _LcDynamicTLB:
        _bDynTLB = self._lcDynTLB is not None
        if (not _bDynTLB) and (self.isAutoEnclosed or self.taskBadge.isCFwThread):
            self._lcDynTLB = _LcDynamicTLB._GetDummyTLB()
        elif (not _bDynTLB) and self.isRunning:
            self._lcDynTLB = _LcDynamicTLB._CreateTLB(self, self._tskBadge, self.xCard, self.taskBadge.isDrivingXTask)
            if self._lcDynTLB is not None:
                self.__UpdateDynTLB(euRNumber_=self.xrNumber, xphaseID_=self.taskXPhase, tskState_=self.dtaskStateID)
        return self._lcDynTLB

    def CreateLcCeaseTLB(self, md_: _Mutex, bEnding_: bool) -> _LcCeaseTLB:
        if (self._lcDynTLB is None) or (self._lcCeaseTLB is not None) or self.isAutoEnclosed or self.taskBadge.isCFwThread:
            pass
        else:
            self._lcCeaseTLB = self._lcDynTLB._CreateCeaseTLB(md_, bEnding_)
        return self._lcCeaseTLB

    def GetLcCompID(self) -> _ELcCompID:
        return self._GetLcCompID()

    def StartTask(self, semStart_: _BinarySemaphore =None, tskOpPCheck_ : _ATaskOpPreCheck =None, curTask_ =None) -> bool:
        return False if self._isInvalid else self._StartTask(semStart_=semStart_, tskOpPCheck_=tskOpPCheck_, curTask_=curTask_)

    def StopTask(self, bCancel_ =False, semStop_: _BinarySemaphore =None, tskOpPCheck_ : _ATaskOpPreCheck =None, curTask_ =None) -> bool:
        return False if self._isInvalid else self._StopTask(bCancel_=bCancel_, semStop_=semStop_, tskOpPCheck_=tskOpPCheck_, curTask_=curTask_)

    def JoinTask(self, timeout_: _Timeout =None, tskOpPCheck_ : _ATaskOpPreCheck =None, curTask_ =None) -> bool:
        return False if self._isInvalid else self._JoinTask(timeout_=timeout_, tskOpPCheck_=tskOpPCheck_, curTask_=curTask_)

    def SelfCheckTask(self) -> _ETaskSelfCheckResultID:
        return False if self._isInvalid else self._SelfCheckTask()

    def _SetTaskXPhase(self, xphaseID_ : _ETaskXPhaseID):
        if self._isInvalid: return
        self._tskXPhase = xphaseID_
        self.__UpdateDynTLB(xphaseID_=xphaseID_)

    def _SetTaskApiContext(self, eApiCtxID_ : _ETaskApiContextID):
        if self._isInvalid: return
        self._tskApiCtx = eApiCtxID_

    def _SetFwApiBookmark(self, eFwApiBookmarkID_ : _EFwApiBookmarkID):
        if self._isInvalid: return
        self._fwapiBM = eFwApiBookmarkID_

    def _SetGetTaskState(self, newState_ : _TaskState._EState) -> Union[_TaskState._EState, None]:
        if self._isInvalid: return None
        res = self._tskState.SetGetStateID(newState_)
        self.__UpdateDynTLB(tskState_=res)
        return res

    @override
    def _PcSetLcProxy(self, lcPxy_ : Union[_ILcProxy, _AbsSlotsObject], bForceUnset_ =False):
        _LcProxyClient._PcSetLcProxy(self, lcPxy_, bForceUnset_=bForceUnset_)
        if self._PcIsLcProxySet():
            self._PropagateLcProxy()

    @_IFwTask._isAlive.getter
    def _isAlive(self) -> bool:
        if self._dHThrd is None:
            return False
        else:
            self._tskState.GetStateID()
            return self.dHThrd.is_alive()

    @_IFwTask._xrNumber.getter
    def _xrNumber(self) -> int:
        return self._xrNum

    @override
    def _IncEuRNumber(self) -> int:
        if self._isInvalid: return -1
        self._xrNum += 1
        self.__UpdateDynTLB(euRNumber_=self._xrNum)
        return self._xrNum

    @override
    def _ProcUnhandledException(self, xcp_: _XcoXcpRootBase):
        return self._ProcUnhandledXcp(xcp_)

    @override
    def _SelfCheckTask(self) -> _ETaskSelfCheckResultID:
        if self._isInvalid:
            return _ETaskSelfCheckResultID.eScrStop
        if self._selfCheckResult._isScrNOK:
            return self._selfCheckResult

        _pscr = _LcProxyClient._PcSelfCheck(self)
        if _pscr._isScrNOK:
            self._selfCheckResult = _pscr
            return _pscr

        if not _TaskUtil.IsCurPyThread(self.dHThrd):
            return self._selfCheckResult
        if not self.isStarted:
            return self._selfCheckResult

        self._selfCheckResult = self._PcSelfCheck()
        return self._selfCheckResult

    @property
    def _tskState(self):
        return self.__tst

    @_tskState.setter
    def _tskState(self, vv_):
        self.__tst = vv_

    @property
    def _tskXPhase(self):
        return self.__tphid

    @_tskXPhase.setter
    def _tskXPhase(self, vv_):
        self.__tphid = vv_

    @property
    def _tskApiCtx(self):
        return self.__tcid

    @_tskApiCtx.setter
    def _tskApiCtx(self, vv_):
        self.__tcid = vv_

    @property
    def _tskBadge(self):
        return self.__tb

    @_tskBadge.setter
    def _tskBadge(self, vv_):
        self.__tb = vv_

    @property
    def _tskError(self):
        return self.__te

    @_tskError.setter
    def _tskError(self, vv_):
        self.__te= vv_

    @property
    def _dHThrd(self):
        return self.__dht

    @_dHThrd.setter
    def _dHThrd(self, vv_):
        self.__dht = vv_

    @property
    def _utConn(self) -> _IUTaskConn:
        return self.__uc

    @_utConn.setter
    def _utConn(self, vv_ : _IUTaskConn):
        self.__uc = vv_

    @property
    def _xrNum(self):
        return self.__xrn

    @_xrNum.setter
    def _xrNum(self, vv_):
        self.__xrn = vv_

    @property
    def _fwapiBM(self):
        return self.__abm

    @_fwapiBM.setter
    def _fwapiBM(self, vv_):
        self.__abm = vv_

    @property
    def _lcDynTLB(self):
        return self.__dtlb

    @_lcDynTLB.setter
    def _lcDynTLB(self, vv_):
        self.__dtlb = vv_

    @property
    def _lcCeaseTLB(self):
        return self.__ctlb

    @_lcCeaseTLB.setter
    def _lcCeaseTLB(self, vv_):
        self.__ctlb = vv_

    @property
    def _tstMutex(self):
        return self.__mst

    @_tstMutex.setter
    def _tstMutex(self, mtxTST_):
        self.__mst = mtxTST_

    @property
    def _selfCheckResult(self) -> _ETaskSelfCheckResultID:
        return self.__sr

    @_selfCheckResult.setter
    def _selfCheckResult(self, scr_ : _ETaskSelfCheckResultID):
        self.__sr = scr_

    def _ToString(self) -> str:
        if self._isInvalid:
            res = type(self).__name__
        else:
            res = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_AbsTask_TID_001).format(
                type(self).__name__, self._tskBadge.ToString(False, False), self.isRunning, str(self._tskState))
        return res

    def _CleanUp(self):
        if self._tskState is None:
            return

        self.__UpdateDynTLB(bCleanedUp_=True)

        _PcErrHandler._CleanUp(self)

        self._xrNum      = None
        self._utConn     = None
        self._dHThrd     = None
        self._fwapiBM    = None
        self._lcDynTLB   = None
        self._tskApiCtx  = None
        self._tskXPhase  = None
        self._lcCeaseTLB = None

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
                     , euRNumber_  : int                =None
                     , xphaseID_   : _ETaskXPhaseID     =None
                     , tskState_   : _TaskState._EState =None
                     , bCleanedUp_ : bool               =None):
        if (self._lcDynTLB is None) or self._lcDynTLB.isDummyTLB:
            return
        self._lcDynTLB._UpdateDynTLB(euRNumber_=euRNumber_, xphaseID_=xphaseID_, tskState_=tskState_, bCleanedUp_=bCleanedUp_)
