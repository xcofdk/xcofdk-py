# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xprocessstate.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from enum import unique
from multiprocessing import Process as _PyProcess

from xcofdk._xcofw.fw.fwssys.fwcore.logging            import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.base.util          import _Util
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject      import _AbstractSlotsObject
from xcofdk._xcofw.fw.fwssys.fwcore.types.atomicint    import _AtomicInteger
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes  import _FwIntEnum
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.sync.mutex     import _Mutex


class _XProcessState(_AbstractSlotsObject):
    @unique
    class _EPState(_FwIntEnum):

        ePInitialized = 10
        ePPendingRun  = 11
        ePRunning     = 12
        ePDone        = 13
        ePFailed      = 14

        @property
        def isPStarted(self):
            return self.value >= _XProcessState._EPState.ePPendingRun.value

        @property
        def isPPendingRun(self):
            return self.value == _XProcessState._EPState.ePPendingRun.value

        @property
        def isPRunning(self):
            return self.value == _XProcessState._EPState.ePRunning.value

        @property
        def isPDone(self):
            return self.value == _XProcessState._EPState.ePDone.value

        @property
        def isPFailed(self):
            return self.value == _XProcessState._EPState.ePFailed.value

        @property
        def isPTerminated(self):
            return self.value >= _XProcessState._EPState.ePDone.value

        @property
        def isPInitialized(self):
            return self.value >= _XProcessState._EPState.ePInitialized.value

    __slots__ = [ '__aiState' , '__mtxApi' , '__hproc' , '__bAliveMismatch' , '__bAutoCreatedMtx' ]

    def __init__(self, xpState_ : _FwIntEnum =None, hostProc_ : _PyProcess =None, mtx_ =None):
        self.__mtxApi          = None
        self.__aiState         = None
        self.__hproc           = None
        self.__bAliveMismatch  = None
        self.__bAutoCreatedMtx = None
        super().__init__()

        if xpState_ is None:
            xpState_ = _XProcessState._EPState.ePInitialized

        if not _Util.IsInstance(xpState_, _XProcessState._EPState, bThrowx_=True):
            self.CleanUp()
        elif (hostProc_ is not None) and not _Util.IsInstance(hostProc_, _PyProcess, bThrowx_=True):
            self.CleanUp()
        elif (mtx_ is not None) and not _Util.IsInstance(mtx_, _Mutex, bThrowx_=True):
            self.CleanUp()
        else:
            _mm = mtx_
            if mtx_ is None:
                _mm = _Mutex()

            self.__hproc           = hostProc_
            self.__mtxApi          = _mm
            self.__aiState         = _AtomicInteger(xpState_)
            self.__bAliveMismatch  = False
            self.__bAutoCreatedMtx = mtx_ is None

    @property
    def isValid(self):
        return not self.__isInvalid

    @property
    def isPStarted(self):
        if self.__isInvalid:
            return False
        with self.__mtxApi:
            _curSt, _bAlive = self.__GetState()
            return _curSt.isPStarted

    @property
    def isPPendingRun(self):
        if self.__isInvalid:
            return False
        with self.__mtxApi:
            _curSt, _bAlive = self.__GetState()
            return _curSt.isPPendingRun

    @property
    def isPRunning(self):
        if self.__isInvalid:
            return False
        with self.__mtxApi:
            _curSt, _bAlive = self.__GetState()
            return _curSt.isPRunning

    @property
    def isPDone(self):
        if self.__isInvalid:
            return False
        with self.__mtxApi:
            _curSt, _bAlive = self.__GetState()
            return _curSt.isPDone

    @property
    def isPFailed(self):
        if self.__isInvalid:
            return False
        with self.__mtxApi:
            _curSt, _bAlive = self.__GetState()
            return _curSt.isPFailed

    @property
    def isPTerminated(self):
        if self.__isInvalid:
            return False
        with self.__mtxApi:
            _curSt, _bAlive = self.__GetState()
            return _curSt.isPTerminated

    @property
    def isPInitialized(self):
        if self.__isInvalid:
            return False
        with self.__mtxApi:
            _curSt, _bAlive = self.__GetState()
            return _curSt.isPInitialized

    def GetStateID(self):
        if self.__isInvalid:
            return None
        with self.__mtxApi:
            _curSt, _bAlive = self.__GetState()
            return _curSt

    def SetGetStateID(self, eNewStateID_ : _FwIntEnum):
        if self.__isInvalid:
            return None
        with self.__mtxApi:
            _curSt, _bAlive = self.__SetGetState(eNewStateID_)
            return _curSt

    def _CleanUp(self):
        if self.__isInvalid:
            pass
        else:
            if self.__bAutoCreatedMtx:
                self.__mtxApi.CleanUp()
            self.__aiState.CleanUp()

            self.__hproc           = None
            self.__mtxApi          = None
            self.__aiState         = None
            self.__bAliveMismatch  = None
            self.__bAutoCreatedMtx = None

    @property
    def __isInvalid(self):
        return self.__mtxApi is None

    def __GetState(self):

        _curSt, _hostProc = _XProcessState._EPState(self.__aiState.value), self.__hproc
        _bAlive = False if _hostProc is None else _hostProc.is_alive()

        self.__CheckAliveMismatch(_bAlive, _curSt)
        return _curSt, _bAlive

    def __SetGetState(self, eNewState_ : _FwIntEnum):
        if not _Util.IsInstance(eNewState_, _XProcessState._EPState, bThrowx_=True):
            return None, None

        _curSt, _bAlive = self.__GetState()
        if _curSt != eNewState_:
            self.__aiState.SetValue(eNewState_)
            _curSt = _XProcessState._EPState(self.__aiState.value)

        self.__CheckAliveMismatch(_bAlive, _curSt)
        return _curSt, _bAlive

    def __CheckAliveMismatch(self, alive_ : bool, eCurState_ : _FwIntEnum):
        _bExpectedAliveness = eCurState_.isPStarted and not eCurState_.isPTerminated

        _hprocName = '-' if self.__hproc is None else self.__hproc.name
        if alive_ != _bExpectedAliveness:
            if not self.__bAliveMismatch:
                self.__bAliveMismatch = True
        elif self.__bAliveMismatch:
            self.__bAliveMismatch = False
