# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : mutex.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from _fwadapter                             import rlogif
from _fw.fwssys.fwcore.base.gtimeout        import _Timeout
from _fw.fwssys.fwcore.ipc.sync.syncresbase import _SyncResourceBase
from _fw.fwssys.fwcore.ipc.tsk.taskutil     import _TaskUtil

from _fw.fwssys.fwerrh.fwerrorcodes import _EFwErrorCode

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _Mutex(_SyncResourceBase):
    __slots__ = [ '__h' ]

    __INVALID_TID = _TaskUtil.GetInvalidTaskID()

    def __init__(self, take_ =False):
        self.__h = None
        super().__init__(_SyncResourceBase._ESyncResType.eMutex, initialCount_=1 if take_ else 0)
        if self._isValid:
            self.__h = _TaskUtil.GetInvalidTaskID()

    def __enter__(self):
        self.Take()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.Give()

    def _Take(self):
        self._resLock.acquire()

        _ll = self._apiLock
        if _ll is not None:
            with _ll:
                self._IncCounter()
                self.__h = _TaskUtil.GetCurPyThreadRuntimeID()
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
            _ll = self._apiLock
            if _ll is not None:
                with _ll:
                    self._IncCounter()
                    self.__h = _TaskUtil.GetCurPyThreadRuntimeID()
        return res

    def _TakeNowait(self):
        res = self._resLock.acquire(False)
        if not res:
            pass
        else:
            _ll = self._apiLock
            if _ll is not None:
                with _ll:
                    self._IncCounter()
                    self.__h = _TaskUtil.GetCurPyThreadRuntimeID()
        return res

    def _Give(self):
        _ll = self._apiLock
        if _ll is not None:
            with _ll:
                if self.__h == _Mutex.__INVALID_TID:
                    return False
                if self.__h != _TaskUtil.GetCurPyThreadRuntimeID():
                    rlogif._LogOEC(True, _EFwErrorCode.FE_00199)
                    return False
                if self._counter <= 0:
                    rlogif._LogOEC(True, _EFwErrorCode.FE_00632)
                    return False
                self._DecCounter()
                if self._counter == 0:
                    self.__h = _Mutex.__INVALID_TID
        res = None
        try:
            self._resLock.release()
            res = True
        except RuntimeError as re:
            rlogif._LogErrorEC(_EFwErrorCode.UE_00071, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Mutex_TID_001).format(self, str(re)))
        return res

    def _CleanUp(self):
        if self._isValid:
            _ll = self._apiLock
            if _ll is not None:
                with _ll:
                    if self.__h == _TaskUtil.GetCurPyThreadRuntimeID():
                        _c = self._counter
                        while _c > 0:
                            _c -= 1
                            self.Give()
                    super()._CleanUp()
            self.__h = None

    def _ToString(self):
        if not self._isValid:
            res = None
        else:
            _ll = self._apiLock
            if _ll is not None:
                with _ll:
                    res = _FwTDbEngine.GetText(_EFwTextID.eMutex_ToString_01).format(type(self).__name__, self.__h, self._counter)
        return res
