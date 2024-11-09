# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : mutex.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from xcofdk._xcofw.fwadapter                             import rlogif
from xcofdk._xcofw.fw.fwssys.fwcore.base.util            import _Util
from xcofdk._xcofw.fw.fwssys.fwcore.base.gtimeout        import _Timeout
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.sync.syncresbase import _SyncResourceBase
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil     import _TaskUtil

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine


class _Mutex(_SyncResourceBase):

    __slots__ = [ '__ownerID' ]

    def __init__(self, take_ =False):
        self.__ownerID = None
        ic = 1 if take_ else 0
        super().__init__(_SyncResourceBase._ESyncResType.eMutex, initialCount_=ic)
        if not self._isValid:
            pass
        else:
            self.__ownerID = _TaskUtil.GetInvalidTaskID()

    def __enter__(self):
        self.Take()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.Give()

    def _Take(self):
        self._resLock.acquire()
        with self._apiLock:
            self._IncCounter()
            self.__ownerID = _TaskUtil.GetCurPyThreadRuntimeID()
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
                self._IncCounter()
                self.__ownerID = _TaskUtil.GetCurPyThreadRuntimeID()
        return res

    def _TakeNowait(self):
        res = self._resLock.acquire(False)
        if not res:
            pass
        else:
            with self._apiLock:
                self._IncCounter()
                self.__ownerID = _TaskUtil.GetCurPyThreadRuntimeID()
        return res

    def _Give(self):
        _INVALID_TASK_ID = _TaskUtil.GetInvalidTaskID()

        with self._apiLock:
            if self.__ownerID == _INVALID_TASK_ID:
                return False
            if self.__ownerID != _TaskUtil.GetCurPyThreadRuntimeID():
                rlogif._LogOEC(True, -1251)
                return False
            if self._counter <= 0:
                rlogif._LogOEC(True, -1252)
                return False
            self._DecCounter()
            if self._counter == 0:
                self.__ownerID = _INVALID_TASK_ID
        res = None
        try:
            self._resLock.release()
            res = True
        except RuntimeError as re:
            rlogif._LogError(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_Mutex_TextID_001).format(self, str(re)))
        return res

    @property
    def _ownerID(self):
        if not self._isValid:
            res = None
        else:
            with self._apiLock:
                res = self.__ownerID
        return res

    def _CleanUp(self):
        if not self._isValid:
            pass
        else:
            with self._apiLock:
                if self.__ownerID == _TaskUtil.GetCurPyThreadRuntimeID():
                    _tryCount = self._counter
                    while _tryCount > 0:
                        _tryCount -= 1
                        self.Give()
                super()._CleanUp()
            self.__ownerID = None

    def _ToString(self, *args_, **kwargs_):
        if not self._isValid:
            res = None
        else:
            with self._apiLock:
                res = _FwTDbEngine.GetText(_EFwTextID.eMutex_ToString_01).format(type(self).__name__, self.__ownerID, self._counter)
        return res
