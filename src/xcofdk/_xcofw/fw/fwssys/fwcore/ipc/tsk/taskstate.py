# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : taskstate.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from enum import unique

from xcofdk._xcofw.fw.fwssys.fwcore.logging            import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.base.util          import _Util
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject      import _AbstractSlotsObject
from xcofdk._xcofw.fw.fwssys.fwcore.types.atomicint    import _AtomicInteger
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes  import _FwIntEnum
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes  import _CommonDefines
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.sync.mutex     import _Mutex
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil   import _TaskUtil



class _TaskState(_AbstractSlotsObject):
    @unique
    class _EState(_FwIntEnum):

        eInitialized            =  0
        ePendingRun             =  1
        eRunning                =  2
        eDone                   =  3
        eFailed                 =  4
        eFailedByApiExecReturn  =  5
        ePendingStopRequest     =  6
        eProcessingStopped      =  7
        eRunProgressAborted     =  8
        ePreRunAborted          =  9
        eSetupAborted           = 10
        eProcessingAborted      = 11
        eTeardownAborted        = 12
        eTimerProcessingAborted = 13

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
        def isFailed(self):
            return (self.value == _TaskState._EState.eFailed.value) or (self.value == _TaskState._EState.eFailedByApiExecReturn.value)

        @property
        def isInitialized(self):
            return self.value >= _TaskState._EState.eInitialized.value

        @property
        def isPendingStopRequest(self):
            return self.value == _TaskState._EState.ePendingStopRequest.value

        @property
        def isTerminating(self):
            return self.value >= _TaskState._EState.ePendingStopRequest.value

        @property
        def isTerminated(self):
            return self.isDone or self.isFailed

        @property
        def isStopping(self):
            return (self.value > _TaskState._EState.eFailedByApiExecReturn.value) and (self.value < _TaskState._EState.eRunProgressAborted.value)

        @property
        def isAborting(self):
            return self.value >= _TaskState._EState.eRunProgressAborted.value

        @property
        def isTransitional(self):
            return self.isPendingRun or self.isTerminating

        @property
        def _isFailedByApiExecutionReturn(self):
            return self.value == _TaskState._EState.eFailedByApiExecReturn.value

    __slots__ = [ '__aiState' , '__mtxApi' , '__taskInst' , '__bAliveMismatch' , '__bAutoCreatedMtx' ]

    def __init__(self, taskInst_, eStateID_ : _FwIntEnum, mtx_ =None):
        super().__init__()

        self.__aiState         = None
        self.__mtxApi          = None
        self.__taskInst        = None
        self.__bAliveMismatch  = None
        self.__bAutoCreatedMtx = None

        _expectedTypes = _CommonDefines._STR_EMPTY

        if len(_expectedTypes) > 0:
            _tname         = type(taskInst_).__name__
            _expectedTypes = _expectedTypes.split(_CommonDefines._CHAR_SIGN_COMMA)

            if _tname not in _expectedTypes:
                self.CleanUp()
                vlogif._LogOEC(True, -1409)
                return

        if not _Util.IsInstance(eStateID_, _TaskState._EState, bThrowx_=True):
            self.CleanUp()
        elif (mtx_ is not None) and not _Util.IsInstance(mtx_, _Mutex, bThrowx_=True):
            self.CleanUp()
        else:
            _mm = mtx_
            if mtx_ is None:
                _mm = _Mutex()

            self.__mtxApi          = _mm
            self.__aiState         = _AtomicInteger(eStateID_)
            self.__taskInst        = taskInst_
            self.__bAliveMismatch  = False
            self.__bAutoCreatedMtx = mtx_ is None

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
        with self.__mtxApi:
            _curSt, _bAlive = self.__GetState()
            return _curSt

    def SetGetStateID(self, eNewStateID_ : _FwIntEnum):
        _curSt, _bAlive = self.__SetGetState(eNewStateID_)
        return eNewStateID_ if _curSt is None else _curSt

    @property
    def _isFailedByApiExecutionReturn(self):
        if self.__isInvalid:
            return False
        with self.__mtxApi:
            _curSt, _bAlive = self.__GetState()
            return _curSt._isFailedByApiExecutionReturn

    def _ToString(self, *args_, **kwargs_):
        if self.__isInvalid:
            return _CommonDefines._STR_EMPTY
        with self.__mtxApi:
            _curSt, _bAlive = self.__GetState()
            return _curSt.compactName

    def _CleanUp(self):
        if self.__isInvalid:
            pass
        else:
            if self.__bAutoCreatedMtx:
                self.__mtxApi.CleanUp()
            self.__aiState.CleanUp()

            self.__mtxApi          = None
            self.__aiState         = None
            self.__taskInst        = None
            self.__bAliveMismatch  = None
            self.__bAutoCreatedMtx = None

    @property
    def __isInvalid(self):
        return self.__mtxApi is None

    def __GetState(self):
        _mtx = self.__mtxApi
        if _mtx is None:
            return None, None,

        with _mtx:
            if self.__mtxApi is None:
                return None, None

            _curSt, _linkedThrd = _TaskState._EState(self.__aiState.value), self.__taskInst.linkedPyThread
            _bAlive = False if _linkedThrd is None else _linkedThrd.is_alive()

            if not _bAlive:
                if not _curSt.isTerminated:
                    if self.__taskInst.isEnclosingPyThread:
                        if self.__taskInst.linkedExecutable is None:
                            _curSt = _TaskState._EState.eDone
                            self.__UpdateState(_curSt)
            self.__CheckAliveMismatch(_bAlive, _curSt)
            return _curSt, _bAlive

    def __SetGetState(self, eNewState_ : _FwIntEnum):
        if not _Util.IsInstance(eNewState_, _TaskState._EState, bThrowx_=True):
            return None, None

        _curSt, _bAlive = self.__GetState()
        if _curSt is None:
            return None, None

        if _curSt != eNewState_:
            if eNewState_ == _TaskState._EState.ePendingStopRequest:
                if _curSt.value >= _TaskState._EState.ePendingStopRequest.value:
                    eNewState_ = None

            if eNewState_ is not None:
                self.__UpdateState(eNewState_)
                _curSt = _TaskState._EState(self.__aiState.value)

        self.__CheckAliveMismatch(_bAlive, _curSt)
        return _curSt, _bAlive

    def __CheckAliveMismatch(self, alive_ : bool, eCurState_ : _FwIntEnum):
        _bExpectedAliveness = eCurState_.value >= _TaskState._EState.eRunning.value
        if not _bExpectedAliveness:
            _bExpectedAliveness = (eCurState_ == _TaskState._EState.eInitialized) and self.__taskInst.taskBadge.isEnclosingPyThread

        if not alive_:
            if eCurState_.isTerminated:
                _bExpectedAliveness = False
            elif self.__taskInst.isEnclosingPyThread:
                _bExpectedAliveness = False
        elif not _bExpectedAliveness:
            if eCurState_ == _TaskState._EState.ePendingRun:
                _bExpectedAliveness = True

        if alive_ != _bExpectedAliveness:
            if not self.__bAliveMismatch:
                self.__bAliveMismatch = True
        elif self.__bAliveMismatch:
            self.__bAliveMismatch = False

    def __UpdateState(self, eNewState_ : _FwIntEnum):
        self.__aiState.SetValue(eNewState_)

        if not _TaskUtil.IsNativeThreadIdSupported():
            pass
        elif eNewState_ != _TaskState._EState.eRunning:
            pass
        else:
            b = self.__taskInst.taskBadge
            t = self.__taskInst.linkedPyThread

            nid = None if t is None else t.native_id
            if nid is None:
                pass
            else:
                b._UpdateRuntimeIDs(threadNID_=nid)
