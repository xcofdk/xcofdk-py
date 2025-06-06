# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : semaphore.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from _fwadapter                             import rlogif
from _fw.fwssys.fwcore.base.gtimeout        import _Timeout
from _fw.fwssys.fwcore.base.util            import _Util
from _fw.fwssys.fwcore.ipc.sync.syncresbase import _SyncResourceBase

from _fw.fwssys.fwerrh.fwerrorcodes import _EFwErrorCode

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _SemaphoreBase(_SyncResourceBase):
    __slots__ = [ '__ic' ]

    __THROWX     = not rlogif._IsReleaseModeEnabled()
    __tskMgrImpl = None

    def __init__(self, initialCount_, isbounded_):
        self.__ic = None
        if isbounded_:
            super().__init__(_SyncResourceBase._ESyncResType.eBoundedSemaphore, initialCount_=initialCount_)
        else:
            super().__init__(_SyncResourceBase._ESyncResType.eSemaphore, initialCount_=initialCount_)
        if not self._isValid:
            return
        elif isbounded_ != self.isBoundedSemaphore:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00633)
            return

        self.__ic = initialCount_

    def _Take(self):
        self._resLock.acquire()
        with self._apiLock:
            self._DecCounter()
        return True

    def _TakeWait(self, timeout_ : _Timeout):
        if not _Timeout.IsTimeout(timeout_, bThrowx_=True):
            return False
        elif timeout_.toNSec == 0:
            return self._Take()
        res = self._resLock.acquire(True, timeout_.toSec)
        if not res:
            pass
        else:
            with self._apiLock:
                self._DecCounter()
        return res

    def _TakeNowait(self):
        res = self._resLock.acquire(False)
        if not res:
            pass
        else:
            with self._apiLock:
                self._DecCounter()
        return res

    def _Give(self):
        res = True
        with self._apiLock:
            if self.isBoundedSemaphore:
                if not _Util.CheckMaxRange(self._counter, self.__ic-1, bThrowx_=False):
                    rlogif._LogOEC(True, _EFwErrorCode.FE_00200)
                    return False
            self._IncCounter()
            try:
                self._resLock.release()
            except ValueError as ve:
                res = None
                rlogif._LogErrorEC(_EFwErrorCode.UE_00072, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_SemaphoreBase_TID_001).format(self, str(ve)))
        return res

    def _ToString(self):
        if not self._isValid:
            res = None
        else:
            with self._apiLock:
                _myTxt = _FwTDbEngine.GetText(_EFwTextID.eSemaphoreBase_ToString_01) if self.isBoundedSemaphore else _FwTDbEngine.GetText(_EFwTextID.eSemaphoreBase_ToString_02)
                res = _FwTDbEngine.GetText(_EFwTextID.eSemaphoreBase_ToString_03).format(type(self).__name__, _myTxt, self.__ic, self._counter)
        return res

    def _CleanUp(self):
        if self._isValid:
            with self._apiLock:
                _tryCount = self.__ic - self._counter
                if _tryCount > 0:
                    while _tryCount > 0:
                        _tryCount -= 1
                        self.Give()
                super()._CleanUp()
            self.__ic = None

    @property
    def _initialCount(self):
        return self.__ic

    def _TryRelease(self, maxTryNum_ : int =1):
        res = 0
        if not self._isValid:
            pass
        elif maxTryNum_ <= 0:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00634)
        else:
            with self._apiLock:
                while maxTryNum_ > 0:
                    if self.isBoundedSemaphore:
                        if not (self._counter < self.__ic):
                            break
                    self._IncCounter()
                    res += 1
                    maxTryNum_ -= 1

            _c = res
            while _c > 0:
                try:
                    self._resLock.release()
                    _c -= 1
                except ValueError as ve:
                    rlogif._LogErrorEC(_EFwErrorCode.UE_00073, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_SemaphoreBase_TID_002).format(_c, self, str(ve)))
                    break
        return res

class _Semaphore(_SemaphoreBase):
    def __init__(self, initialCount_ =1):
        super().__init__(initialCount_, False)

class _BoundedSemaphore(_SemaphoreBase):
    def __init__(self, initialCount_):
        super().__init__(initialCount_, True)

    @property
    def maxCount(self):
        return self.initialCount

class _BinarySemaphore(_BoundedSemaphore):
    def __init__(self, take_ =True):
        super().__init__(initialCount_=1)
        if take_:
            self.Take()
