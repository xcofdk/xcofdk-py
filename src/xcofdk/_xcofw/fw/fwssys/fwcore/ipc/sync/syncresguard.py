# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : syncresguard.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from threading import RLock as _PyRLock

from xcofdk._xcofw.fw.fwssys.fwcore.logging       import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject import _AbstractSlotsObject

from xcofdk._xcofw.fw.fwssys.fwerrh.fwerrorcodes import _EFwErrorCode

class _SyncResourcesGuard(_AbstractSlotsObject):

    class _TaskEntry(_AbstractSlotsObject):
        __slots__ = [ '__taskID' , '__numLocks' ]

        def __init__(self, taskID_, lock_):
            super().__init__()
            self.__taskID   = taskID_
            self.__numLocks = 1 if lock_ else 0

        def __eq__(self, other_):
            return self.taskID == other_.taskID

        @property
        def taskID(self):
            return self.__taskID

        @property
        def numLocks(self):
            return self.__numLocks

        def IncNumLocks(self):
            self.__numLocks += 1
            return self.__numLocks

        def DecNumLocks(self):
            self.__numLocks -= 1
            return self.__numLocks

        def _ToString(self, *args_, **kwargs_):
            if self is None: pass
            return None

        def _CleanUp(self):
            if self.taskID is not None:
                self.__taskID   = None
                self.__numLocks = None

    class _SResEntry(_AbstractSlotsObject):
        __slots__ = [ '__sres' , '__tasks' , '__numLocks' ]

        def __init__(self, sres_):
            super().__init__()
            self.__sres     = sres_
            self.__tasks    = []
            self.__numLocks = 0

        def __eq__(self, other_):
            return id(self.__sres) == id(other_.__sres)

        @property
        def sres(self):
            return self.__sres

        @property
        def tasks(self):
            return self.__tasks

        @property
        def numTasks(self):
            return 0 if self.__sres is None else len(self.__tasks)

        @property
        def numLocks(self):
            return self.__numLocks

        def DecNumLocks(self, decVal_):
            if self.__sres is None:
                pass
            elif decVal_ > self.__numLocks:
                pass
            else:
                self.__numLocks -= decVal_

        def UpdateTask(self, taskID_ : int, adding_ : bool):
            if self.__sres is None:
                return None

            _te = None
            if len(self.__tasks) <= 0:
                if not adding_:
                    pass
                else:
                    _te = _SyncResourcesGuard._TaskEntry(taskID_, True)
                    self.__tasks.append(_te)
            else:
                _lstTE = [ _te for _te in self.__tasks if _te.taskID == taskID_ ]
                _LGHT = len(_lstTE)
                if _LGHT > 1:
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00174)
                _te = None if _LGHT == 0 else _lstTE[0]
                if _te is None:
                    if not adding_:
                        _te = self.__tasks[0]
                    else:
                        _te = _SyncResourcesGuard._TaskEntry(taskID_, False)
                        self.__tasks.append(_te)
                if not adding_:
                    if _te.DecNumLocks() <= 0:
                        self.__tasks.remove(_te)
                        _te.CleanUp()
                        _te = None
                else:
                    _te.IncNumLocks()
            if _te is not None:
                self.__numLocks += 1 if adding_ else -1
            return _te

        def _ToString(self, *args_, **kwargs_):
            if self is None: pass
            return None

        def _CleanUp(self):
            if self.__sres is not None:
                for _te in self.__tasks:
                    _te.CleanUp()
                self.__tasks.clear()
                self.__sres     = None
                self.__tasks    = None
                self.__numLocks = None

    __slots__ = [ '__rlock', '__allRes' ]

    __singleton = None

    def __init__(self):
        self.__rlock  = None
        self.__allRes = None
        super().__init__()

        if _SyncResourcesGuard.__singleton is not None:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00175)
            self.CleanUp()
        else:
            self.__rlock  = _PyRLock()
            self.__allRes = []
            _SyncResourcesGuard.__singleton = self

    @property
    def numResources(self):
        return 0 if self.__rlock is None else len(self.__allRes)

    def GuardSyncResource(self, sres_, taskID_ : int, syncPeer_ =None):
        self.__UpdateSyncRes(sres_, taskID_, True, syncPeer_=syncPeer_)

    def DisregardSyncResource(self, sres_, taskID_ : int):
        self.__UpdateSyncRes(sres_, taskID_, False)

    def ReleaseAcquiredSyncResources(self, taskID_ : int):

        if self.__rlock is None:
            return

        self.__rlock.acquire()
        _lstTbr = []
        for _re in self.__allRes:
            if not _re.sres._isValid:
                continue

            _lstTE = [_te for _te in _re.tasks if _te.taskID==taskID_]
            _LGHT = len(_lstTE)
            if _LGHT > 1:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00176)
            _te = None if _LGHT==0 else _lstTE[0]
            if _te is not None:
                numRel = _re.sres._TryRelease(maxTryNum_=_te.numLocks)
                _re.DecNumLocks(_te.numLocks)
                _re.tasks.remove(_te)
                _te.CleanUp()
            if _re.numTasks <= 0:
                _lstTbr.append(_re)
        for _re in _lstTbr:
            self.__allRes.remove(_re)
            _re.CleanUp()
        self.__rlock.release()

    @staticmethod
    def _GetInstance():
        return _SyncResourcesGuard.__singleton

    @staticmethod
    def _CreateInstance():
        _SyncResourcesGuard.__singleton = _SyncResourcesGuard()
        return _SyncResourcesGuard.__singleton

    def _ToString(self, *args_, **kwargs_):
        if self is None: pass
        return None

    def _CleanUp(self):
        if self.__rlock is None:
            return

        _SyncResourcesGuard.__singleton = None
        self.__rlock.acquire()
        for _rr in self.__allRes:
            _rr.CleanUp()
        self.__allRes.clear()
        self.__allRes = None
        self.__rlock.release()
        self.__rlock = None

    def __UpdateSyncRes(self, sres_, taskID_ : int, adding_ : bool, syncPeer_ =None):
        if (self.__rlock is None) or (sres_ is None) or not sres_._isValid:
            return

        self.__rlock.acquire()

        _teAd = None
        _lstRes = [ _re for _re in self.__allRes if id(_re.sres) == id(sres_) ]
        if len(_lstRes) > 1:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00177)
        _re = None if len(_lstRes) == 0 else _lstRes[0]
        if _re is None:
            if not adding_:
                pass
            else:
                _re = _SyncResourcesGuard._SResEntry(sres_)
                self.__allRes.append(_re)
        if _re is None:
            pass
        else:
            _te = _re.UpdateTask(taskID_, adding_)
            if (syncPeer_ is not None) and adding_:
                _teAd = _te
            if _re.numTasks <= 0:
                self.__allRes.remove(_re)
                _re.CleanUp()

        if _teAd is None:
            pass
        else:
            _lstRes = [_re for _re in self.__allRes if id(_re.sres)==id(syncPeer_)]
            if len(_lstRes) > 1:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00178)

            _pr = None if len(_lstRes)==0 else _lstRes[0]

            if _pr is None:
                pass
            else:
                _pt = _pr.UpdateTask(taskID_, True)

        self.__rlock.release()
