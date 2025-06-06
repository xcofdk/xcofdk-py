# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : taskstate.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum import auto
from enum import unique

from _fw.fwssys.fwcore.logging            import vlogif
from _fw.fwssys.fwcore.base.util          import _Util
from _fw.fwssys.fwcore.types.aobject      import _AbsSlotsObject
from _fw.fwssys.fwcore.types.atomicint    import _AtomicInteger
from _fw.fwssys.fwcore.types.commontypes  import _FwIntEnum
from _fw.fwssys.fwcore.types.commontypes  import _CommonDefines
from _fw.fwssys.fwcore.ipc.sync.mutex     import _Mutex
from _fw.fwssys.fwcore.ipc.tsk.taskutil   import _TaskUtil

from _fw.fwssys.fwerrh.fwerrorcodes import _EFwErrorCode

class _TaskState(_AbsSlotsObject):
    @unique
    class _EState(_FwIntEnum):
        eInitialized            = 0
        ePendingRun             = auto()  
        eRunning                = auto()  
        eDone                   = auto()  
        eCanceled               = auto()  
        eFailed                 = auto()  
        eFailedByXCmdReturn     = auto()  
        ePendingStopRequest     = auto()  
        ePendingCancelRequest   = auto()  
        eProcessingCanceled     = auto()  
        eProcessingStopped      = auto()  
        eRunProgressAborted     = auto()  
        ePreRunAborted          = auto()  
        eSetupAborted           = auto()  
        eProcessingAborted      = auto()  
        eTeardownAborted        = auto()  
        eTimerProcessingAborted = auto()  

        @property
        def isStarted(self):
            return self.value >= _TaskState._EState.ePendingRun.value

        @property
        def isPendingRun(self):
            return self.value == _TaskState._EState.ePendingRun.value

        @property
        def isRunning(self):
            return self.value == _TaskState._EState.eRunning.value

        @property
        def isDone(self):
            return self.value == _TaskState._EState.eDone.value

        @property
        def isCanceled(self):
            return self.value == _TaskState._EState.eCanceled.value

        @property
        def isFailed(self):
            return (self.value == _TaskState._EState.eFailed.value) or (self.value == _TaskState._EState.eFailedByXCmdReturn.value)

        @property
        def isInitialized(self):
            return self.value >= _TaskState._EState.eInitialized.value

        @property
        def isPendingStopRequest(self):
            return self.value == _TaskState._EState.ePendingStopRequest.value

        @property
        def isPendingCancelRequest(self):
            return self.value == _TaskState._EState.ePendingCancelRequest.value

        @property
        def isTerminating(self):
            return self.value >= _TaskState._EState.ePendingStopRequest.value

        @property
        def isTerminated(self):
            return self.eRunning.value < self.value < self.eFailedByXCmdReturn.value

        @property
        def isStopping(self):
            return (self.value > _TaskState._EState.eFailedByXCmdReturn.value) and (self.value < _TaskState._EState.eRunProgressAborted.value)

        @property
        def isCanceling(self):
            return (self.value > _TaskState._EState.ePendingStopRequest.value) and (self.value < _TaskState._EState.eProcessingStopped.value)

        @property
        def isAborting(self):
            return self.value >= _TaskState._EState.eRunProgressAborted.value

        @property
        def isTransitional(self):
            return self.isPendingRun or self.isTerminating

        @property
        def isFailedByXCmdReturn(self):
            return self.value == _TaskState._EState.eFailedByXCmdReturn.value

    __slots__ = [ '__t' , '__ai' , '__ma' , '__bM' , '__bA' ]

    def __init__(self, taskInst_, eStateID_ : _FwIntEnum, mtx_ =None):
        self.__t  = None
        self.__ai = None
        self.__bA = None
        self.__bM = None
        self.__ma = None
        super().__init__()

        if not _Util.IsInstance(eStateID_, _TaskState._EState, bThrowx_=True):
            self.CleanUp()
        elif (mtx_ is not None) and not _Util.IsInstance(mtx_, _Mutex, bThrowx_=True):
            self.CleanUp()
        else:
            _mm = mtx_
            if mtx_ is None:
                _mm = _Mutex()

            self.__t  = taskInst_
            self.__ai = _AtomicInteger(eStateID_)
            self.__ma = _mm
            self.__bA = mtx_ is None
            self.__bM = False

    @property
    def isValid(self):
        return not self.__isInvalid

    @property
    def isStarted(self):
        _curSt, _bAlive = self.__GetState()
        return False if _curSt is None else _curSt.isStarted

    @property
    def isPendingRun(self):
        _curSt, _bAlive = self.__GetState()
        return False if _curSt is None else _curSt.isPendingRun

    @property
    def isRunning(self):
        _curSt, _bAlive = self.__GetState()
        return False if _curSt is None else _curSt.isRunning

    @property
    def isDone(self):
        _curSt, _bAlive = self.__GetState()
        return False if _curSt is None else _curSt.isDone

    @property
    def isCanceled(self):
        _curSt, _bAlive = self.__GetState()
        return False if _curSt is None else _curSt.isCanceled

    @property
    def isFailed(self):
        _curSt, _bAlive = self.__GetState()
        return False if _curSt is None else _curSt.isFailed

    @property
    def isInitialized(self):
        _curSt, _bAlive = self.__GetState()
        return False if _curSt is None else _curSt.isInitialized

    @property
    def isPendingStopRequest(self):
        _curSt, _bAlive = self.__GetState()
        return False if _curSt is None else _curSt.isPendingStopRequest

    @property
    def isPendingCancelRequest(self):
        _curSt, _bAlive = self.__GetState()
        return False if _curSt is None else _curSt.isPendingCancelRequest

    @property
    def isTerminating(self):
        _curSt, _bAlive = self.__GetState()
        return False if _curSt is None else _curSt.isTerminating

    @property
    def isTerminated(self):
        _curSt, _bAlive = self.__GetState()
        return False if _curSt is None else _curSt.isTerminated

    @property
    def isStopping(self):
        _curSt, _bAlive = self.__GetState()
        return False if _curSt is None else _curSt.isStopping

    @property
    def isCanceling(self):
        _curSt, _bAlive = self.__GetState()
        return False if _curSt is None else _curSt.isCanceling

    @property
    def isAborting(self):
        _curSt, _bAlive = self.__GetState()
        return False if _curSt is None else _curSt.isAborting

    @property
    def isTransitional(self):
        _curSt, _bAlive = self.__GetState()
        return False if _curSt is None else _curSt.isTransitional

    def GetStateID(self):
        if self.__isInvalid:
            return None
        with self.__ma:
            _curSt, _bAlive = self.__GetState()
            return _curSt

    def SetGetStateID(self, eNewStateID_ : _FwIntEnum):
        _curSt, _bAlive = self.__SetGetState(eNewStateID_)
        return eNewStateID_ if _curSt is None else _curSt

    @property
    def isFailedByXCmdReturn(self):
        if self.__isInvalid:
            return False
        with self.__ma:
            _curSt, _bAlive = self.__GetState()
            return _curSt.isFailedByXCmdReturn

    def _ToString(self):
        if self.__isInvalid:
            return _CommonDefines._STR_EMPTY
        with self.__ma:
            _curSt, _bAlive = self.__GetState()
            return _curSt.compactName

    def _CleanUp(self):
        if self.__isInvalid:
            return
        if self.__bA:
            self.__ma.CleanUp()
        self.__ai.CleanUp()

        self.__t = None
        self.__ai = None
        self.__bA = None
        self.__bM = None
        self.__ma = None

    @property
    def __isInvalid(self):
        return self.__ma is None

    def __GetState(self):
        _mtx = self.__ma
        if _mtx is None:
            return None, None,

        with _mtx:
            if self.__ma is None:
                return None, None

            _curSt, _linkedThrd = _TaskState._EState(self.__ai.value), self.__t.dHThrd
            _bAlive = False if _linkedThrd is None else _linkedThrd.is_alive()

            if not _bAlive:
                if not _curSt.isTerminated:
                    if self.__t.isEnclosingPyThread:
                        if self.__t.dxUnit is None:
                            _curSt = _TaskState._EState.eDone
                            self.__UpdateState(_curSt)
            self.__CheckAliveMismatch(_bAlive, _curSt)
            return _curSt, _bAlive

    def __SetGetState(self, newState_ : _FwIntEnum):
        if not _Util.IsInstance(newState_, _TaskState._EState, bThrowx_=True):
            return None, None

        _curSt, _bAlive = self.__GetState()
        if _curSt is None:
            return None, None

        if _curSt != newState_:
            if (newState_ == _TaskState._EState.ePendingStopRequest) or (newState_ == _TaskState._EState.ePendingCancelRequest):
                if _curSt.value >= _TaskState._EState.ePendingStopRequest.value:
                    newState_ = None

            if newState_ is not None:
                self.__UpdateState(newState_)
                _curSt = _TaskState._EState(self.__ai.value)

        self.__CheckAliveMismatch(_bAlive, _curSt)
        return _curSt, _bAlive

    def __CheckAliveMismatch(self, alive_ : bool, eCurState_ : _FwIntEnum):
        _bExpectedAliveness = eCurState_.value >= _TaskState._EState.eRunning.value
        if not _bExpectedAliveness:
            _bExpectedAliveness = (eCurState_ == _TaskState._EState.eInitialized) and self.__t.taskBadge.isEnclosingPyThread

        if not alive_:
            if eCurState_.isTerminated:
                _bExpectedAliveness = False
            elif self.__t.isEnclosingPyThread:
                _bExpectedAliveness = False
        elif not _bExpectedAliveness:
            if eCurState_ == _TaskState._EState.ePendingRun:
                _bExpectedAliveness = True

        if alive_ != _bExpectedAliveness:
            if not self.__bM:
                self.__bM = True
        elif self.__bM:
            self.__bM = False

    def __UpdateState(self, newState_ : _FwIntEnum):
        self.__ai.SetValue(newState_)

        if not _TaskUtil.IsNativeThreadIdSupported():
            pass
        elif newState_ != _TaskState._EState.eRunning:
            pass
        else:
            _b = self.__t.taskBadge
            _t = self.__t.dHThrd

            _nid = None if _t is None else _t.native_id
            if _nid is not None:
                _b._UpdateRuntimeIDs(threadNID_=_nid)
