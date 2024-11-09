# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : syncresbase.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from enum      import Enum
from enum      import unique
from threading import RLock            as _PyRLock
from threading import Semaphore        as _PySemaphore
from threading import BoundedSemaphore as _PyBoundedSemaphore

from xcofdk._xcofw.fw.fwssys.fwcore.logging               import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.base.listutil         import _ListUtil
from xcofdk._xcofw.fw.fwssys.fwcore.base.gtimeout         import _Timeout
from xcofdk._xcofw.fw.fwssys.fwcore.base.util             import _Util
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.sync.syncresguard import _SyncResourcesGuard
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk               import taskmgr
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject         import _AbstractSlotsObject


class _SyncResourceBase(_AbstractSlotsObject):

    @unique
    class _ESyncResType(Enum):
        eMutex            = 0
        eSemaphore        = 1
        eBoundedSemaphore = 2

    __slots__ = [ '__eType' , '__ctr' , '__apiLck' , '__resLck' ]

    __SRGUARD_ENABLED = True

    __lstPendingGuard = []

    def __init__(self, eSyncResType_ : _ESyncResType, initialCount_ : int =0):
        super().__init__()
        self.__ctr    = None
        self.__eType  = None
        self.__apiLck = None
        self.__resLck = None

        if not _Util.IsInstance(initialCount_, int, bThrowx_=True):
            return
        elif not _Util.IsInstance(eSyncResType_, _SyncResourceBase._ESyncResType, bThrowx_=True):
            return
        elif eSyncResType_==_SyncResourceBase._ESyncResType.eMutex:
            if not _Util.CheckRange(initialCount_, 0, 1, bThrowx_=True):
                return
        elif eSyncResType_ == _SyncResourceBase._ESyncResType.eBoundedSemaphore:
            if not _Util.CheckMinRange(initialCount_, 1, bThrowx_=True):
                return

        if eSyncResType_==_SyncResourceBase._ESyncResType.eMutex:
            self.__resLck = _PyRLock()
        elif eSyncResType_==_SyncResourceBase._ESyncResType.eSemaphore:
            self.__resLck = _PySemaphore(initialCount_)
        elif eSyncResType_ == _SyncResourceBase._ESyncResType.eBoundedSemaphore:
            self.__resLck = _PyBoundedSemaphore(initialCount_)
        else:
            vlogif._LogOEC(True, -1246)
            return
        self.__ctr    = initialCount_
        self.__eType  = eSyncResType_
        self.__apiLck = _PyRLock()

    def __eq__(self, other_):
        return id(self) == id(other_)

    @property
    def isMutex(self):
        return self.__eType == _SyncResourceBase._ESyncResType.eMutex

    @property
    def isSemaphore(self):
        return self.__eType == _SyncResourceBase._ESyncResType.eSemaphore

    @property
    def isBinarySemaphore(self):
        return self.isBoundedSemaphore and (self._initialCount == 1)

    @property
    def isBoundedSemaphore(self):
        return self.__eType == _SyncResourceBase._ESyncResType.eBoundedSemaphore

    @property
    def initialCount(self):
        res = None if not self._isValid else self._initialCount
        return res

    @property
    def counter(self):
        if not self._isValid:
            res = None
        else:
            with self.__apiLck:
                res = self.__ctr
        return res

    def Take(self, syncPeer_ =None):
        if not self._isValid:
            return False
        res = self._Take()
        if self.isMutex:
            pass
        elif not res:
            pass
        elif _SyncResourceBase._IsSyncResGuardEnabled():
            self.__NotifySyncResGuard(adding_=True, syncPeer_=syncPeer_)
        return res

    def TakeWait(self, timeout_ : _Timeout):
        if not self._isValid:
            return False
        res = self._TakeWait(timeout_)
        if self.isMutex:
            pass
        elif not res:
            pass
        elif _SyncResourceBase._IsSyncResGuardEnabled():
            self.__NotifySyncResGuard(adding_=True)
        return res

    def TakeNowait(self):
        if not self._isValid:
            return False
        res = self._TakeNowait()
        if self.isMutex:
            pass
        elif not res:
            pass
        elif _SyncResourceBase._IsSyncResGuardEnabled():
            self.__NotifySyncResGuard(adding_=True)
        return res

    def Give(self):
        if not self._isValid:
            return False
        retVal = self._Give()
        res = (retVal is not None) and retVal
        if self.isMutex:
            return res
        if (retVal is not None) and (not retVal):
            return False
        if _SyncResourceBase._IsSyncResGuardEnabled():
            self.__NotifySyncResGuard(adding_=False)
        return res

    @property
    def _isValid(self):
        return self.__eType is not None

    @property
    def _initialCount(self):
        return 0

    @property
    def _counter(self):
        return self.__ctr

    @_counter.setter
    def _counter(self, val_):
        self.__ctr = val_

    @property
    def _apiLock(self):
        return self.__apiLck

    @_apiLock.setter
    def _apiLock(self, val_):
        self.__apiLck = val_

    @property
    def _resLock(self):
        return self.__resLck

    @_resLock.setter
    def _resLock(self, val_):
        self.__resLck = val_

    def _IncCounter(self):
        self.__ctr += 1

    def _DecCounter(self):
        self.__ctr -= 1

    @staticmethod
    def _IsSyncResGuardEnabled():
        return _SyncResourceBase.__SRGUARD_ENABLED

    @staticmethod
    def _SetSyncResGuardConfig(synResGuardEnabled_ : bool):
        _SyncResourceBase.__SRGUARD_ENABLED = synResGuardEnabled_

    @staticmethod
    def _ProcessResourcesPendingGuard():
        if _SyncResourceBase.__lstPendingGuard is None:
            pass
        elif len(_SyncResourceBase.__lstPendingGuard) == 0:
            pass
        else:
            _srg = _SyncResourcesGuard._GetInstance()
            if _srg is None:
                pass
            else:
                _curTsk = taskmgr._TaskMgr()._GetCurTask(bAutoEncloseMissingThread_=False)
                _tid = None if _curTsk is None else _curTsk.taskID
                if _tid is None:
                    pass
                else:
                    _sr = None
                    for _sr in _SyncResourceBase.__lstPendingGuard:
                        _srg.GuardSyncResource(_sr, _tid)
                    _SyncResourceBase.__lstPendingGuard.clear()

    def _ToString(self):
        pass

    def _CleanUp(self):
        if not self._isValid:
            pass
        else:
            self.__eType = None

            _myLck = self.__apiLck
            with _myLck:
                self.__ctr    = None
                self.__apiLck = None
                self.__resLck = None

    def _TryRelease(self, maxTryNum_ : int =1):
        if self is None: pass
        return 0

    def __NotifySyncResGuard(self, adding_ =True, syncPeer_=None):
        if not self._isValid:
            pass
        elif not _SyncResourceBase._IsSyncResGuardEnabled():
            pass
        elif (syncPeer_ is not None) and not isinstance(syncPeer_, _SyncResourceBase):
            vlogif._LogOEC(True, -1247)
        else:
            _srg  = _SyncResourcesGuard._GetInstance()
            _tid  = None
            _tmgr = taskmgr._TaskMgr()

            if _srg is None:
                _bPending = True
            elif _tmgr is None:
                _bPending = True
            else:
                _curTsk = _tmgr._GetCurTask(bAutoEncloseMissingThread_=False)
                _tid = None if _curTsk is None else _curTsk.taskID
                _bPending = _tid is None

            if _bPending:
                if not adding_:
                    _idx = _ListUtil.GetIndex(_SyncResourceBase.__lstPendingGuard, self)
                    if _idx < 0:
                        pass
                    else:
                        _SyncResourceBase.__lstPendingGuard.pop(_idx)
                elif self not in _SyncResourceBase.__lstPendingGuard:
                    _SyncResourceBase.__lstPendingGuard.append(self)

            else:
                if adding_:
                    _srg.GuardSyncResource(self, _tid, syncPeer_=syncPeer_)
                else:
                    _srg.DisregardSyncResource(self, _tid)
