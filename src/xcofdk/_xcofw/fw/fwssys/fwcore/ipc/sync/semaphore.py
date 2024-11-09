# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : semaphore.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from xcofdk._xcofw.fwadapter                             import rlogif
from xcofdk._xcofw.fw.fwssys.fwcore.base.gtimeout        import _Timeout
from xcofdk._xcofw.fw.fwssys.fwcore.base.util            import _Util
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.sync.syncresbase import _SyncResourceBase

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine


class _SemaphoreBase(_SyncResourceBase):

    __slots__ = [ '__initialCount' ]

    __THROWX     = not rlogif._IsReleaseModeEnabled()
    __tskMgrImpl = None

    def __init__(self, initialCount_, isbounded_):
        self.__initialCount = None
        if isbounded_:
            super().__init__(_SyncResourceBase._ESyncResType.eBoundedSemaphore, initialCount_=initialCount_)
        else:
            super().__init__(_SyncResourceBase._ESyncResType.eSemaphore, initialCount_=initialCount_)
        if not self._isValid:
            return
        elif isbounded_ != self.isBoundedSemaphore:
            rlogif._LogOEC(True, -1248)
            return

        self.__initialCount = initialCount_

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
                if not _Util.CheckMaxRange(self._counter, self.__initialCount-1, bThrowx_=False):
                    rlogif._LogOEC(True, -1249)
                    return False
            self._IncCounter()
            try:
                self._resLock.release()
            except ValueError as ve:
                res = None
                rlogif._LogError(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_SemaphoreBase_TextID_001).format(self, str(ve)))
        return res

    def _ToString(self):
        if not self._isValid:
            res = None
        else:
            with self._apiLock:
                _myTxt = _FwTDbEngine.GetText(_EFwTextID.eSemaphoreBase_ToString_01) if self.isBoundedSemaphore else _FwTDbEngine.GetText(_EFwTextID.eSemaphoreBase_ToString_02)
                res = _FwTDbEngine.GetText(_EFwTextID.eSemaphoreBase_ToString_03).format(type(self).__name__, _myTxt, self.__initialCount, self._counter)
        return res

    def _CleanUp(self):
        if not self._isValid:
            pass
        else:
            with self._apiLock:
                _tryCount = self.__initialCount - self._counter
                if _tryCount <= 0:
                    pass
                else:
                    while _tryCount > 0:
                        _tryCount -= 1
                        self.Give()
                super()._CleanUp()
            self.__initialCount = None

    @property
    def _initialCount(self):
        return self.__initialCount

    def _TryRelease(self, maxTryNum_ : int =1):
        res = 0
        if not self._isValid:
            pass
        elif maxTryNum_ <= 0:
            rlogif._LogOEC(True, -1250)
        else:
            with self._apiLock:
                while maxTryNum_ > 0:
                    if self.isBoundedSemaphore:
                        if not (self._counter < self.__initialCount):
                            break
                    self._IncCounter()
                    res += 1
                    maxTryNum_ -= 1

            relTry = res
            while relTry > 0:
                try:
                    self._resLock.release()
                    relTry -= 1
                except ValueError as ve:
                    rlogif._LogError(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_SemaphoreBase_TextID_002).format(relTry, self, str(ve)))
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
