# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xprocessstate.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum import auto
from enum import unique
from multiprocessing import Process as _PyProcess

from _fw.fwssys.fwcore.logging            import vlogif
from _fw.fwssys.fwcore.base.util          import _Util
from _fw.fwssys.fwcore.types.aobject      import _AbsSlotsObject
from _fw.fwssys.fwcore.types.atomicint    import _AtomicInteger
from _fw.fwssys.fwcore.types.commontypes  import _FwIntEnum
from _fw.fwssys.fwcore.ipc.sync.mutex     import _Mutex

@unique
class _EPState(_FwIntEnum):
    ePInitialized = 30
    ePRunning     = auto()   
    ePDone        = auto()   
    ePFailed      = auto()   
    ePTermByCmd   = auto()   

    @property
    def isPStarted(self):
        return self.value > _EPState.ePInitialized.value

    @property
    def isPRunning(self):
        return self.value == _EPState.ePRunning.value

    @property
    def isPDone(self):
        return self.value == _EPState.ePDone.value

    @property
    def isPFailed(self):
        return self.value == _EPState.ePFailed.value

    @property
    def isPTerminated(self):
        return self.value > _EPState.ePRunning.value

    @property
    def isPTerminatedByCmd(self):
        return self.value == _EPState.ePTermByCmd

class _XProcessState(_AbsSlotsObject):
    __slots__ = [ '__st' , '__ma' , '__h' , '__bM' , '__bA' ]

    def __init__(self, xpState_ : _FwIntEnum =None, hostProc_ : _PyProcess =None, mtx_ =None):
        self.__h  = None
        self.__bA = None
        self.__bM = None
        self.__ma = None
        self.__st = None
        super().__init__()

        if xpState_ is None:
            xpState_ = _EPState.ePInitialized

        if not _Util.IsInstance(xpState_, _EPState, bThrowx_=True):
            self.CleanUp()
        elif (hostProc_ is not None) and not _Util.IsInstance(hostProc_, _PyProcess, bThrowx_=True):
            self.CleanUp()
        elif (mtx_ is not None) and not _Util.IsInstance(mtx_, _Mutex, bThrowx_=True):
            self.CleanUp()
        else:
            _mm = mtx_
            if mtx_ is None:
                _mm = _Mutex()

            self.__h  = hostProc_
            self.__bA = mtx_ is None
            self.__bM = False
            self.__ma = _mm
            self.__st = _AtomicInteger(xpState_)

    @property
    def isValid(self):
        return not self.__isInvalid

    def GetPStateID(self):
        if self.__isInvalid:
            return None
        with self.__ma:
            _curSt, _bAlive = self.__GetPStateID()
            return _curSt

    def SetGetPStateID(self, eNewStateID_ : _FwIntEnum):
        if self.__isInvalid:
            return None
        with self.__ma:
            _curSt, _bAlive = self.__SetGetPState(eNewStateID_)
            return _curSt

    def _UnsetHostProcess(self):
        self.__h = None

    def _CleanUp(self):
        if not self.__isInvalid:
            if self.__bA:
                self.__ma.CleanUp()
            self.__st.CleanUp()

            self.__h = None
            self.__bA = None
            self.__bM = None
            self.__ma = None
            self.__st = None

    @property
    def __isInvalid(self):
        return self.__ma is None

    def __GetPStateID(self):
        _curSt, _hostProc = _EPState(self.__st.value), self.__h
        _bAlive = False if _hostProc is None else _hostProc.is_alive()

        self.__CheckAM(_bAlive, _curSt)
        return _curSt, _bAlive

    def __SetGetPState(self, newState_ : _FwIntEnum):
        if not _Util.IsInstance(newState_, _EPState, bThrowx_=True):
            return None, None

        _curSt, _bAlive = self.__GetPStateID()
        if _curSt != newState_:
            self.__st.SetValue(newState_)
            _curSt = _EPState(self.__st.value)

        self.__CheckAM(_bAlive, _curSt)
        return _curSt, _bAlive

    def __CheckAM(self, alive_ : bool, eCurState_ : _EPState):
        _bExpectedAliveness = eCurState_.isPStarted and not eCurState_.isPTerminated
        if alive_ != _bExpectedAliveness:
            if not self.__bM:
                self.__bM = True
        elif self.__bM:
            self.__bM = False

