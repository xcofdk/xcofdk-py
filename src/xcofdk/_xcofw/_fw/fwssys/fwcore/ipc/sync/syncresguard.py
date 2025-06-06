# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : syncresguard.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from threading import RLock as _PyRLock

from _fw.fwssys.fwcore.logging           import vlogif
from _fw.fwssys.fwcore.types.aobject     import _AbsSlotsObject
from _fw.fwssys.fwcore.types.commontypes import _EDepInjCmd
from _fw.fwssys.fwerrh.fwerrorcodes      import _EFwErrorCode

class _SyncResourcesGuard(_AbsSlotsObject):
    class _TaskEntry(_AbsSlotsObject):
        __slots__ = [ '__n' , '__tid' ]

        def __init__(self, taskID_, lock_):
            super().__init__()
            self.__n   = 1 if lock_ else 0
            self.__tid = taskID_

        def __eq__(self, other_):
            return self.dtaskUID == other_.dtaskUID

        @property
        def dtaskUID(self):
            return self.__tid

        @property
        def numLocks(self):
            return self.__n

        def IncNumLocks(self):
            self.__n += 1
            return self.__n

        def DecNumLocks(self):
            self.__n -= 1
            return self.__n

        def _ToString(self):
            pass

        def _CleanUp(self):
            if self.dtaskUID is not None:
                self.__n   = None
                self.__tid = None

    class _SResEntry(_AbsSlotsObject):
        __slots__ = [ '__n' , '__at' , '__sr' ]

        def __init__(self, sres_):
            super().__init__()
            self.__n  = 0
            self.__at = []
            self.__sr = sres_

        def __eq__(self, other_):
            return id(self.__sr) == id(other_.__sr)

        @property
        def sres(self):
            return self.__sr

        @property
        def tasks(self):
            return self.__at

        @property
        def numTasks(self):
            return 0 if self.__sr is None else len(self.__at)

        @property
        def numLocks(self):
            return self.__n

        def DecNumLocks(self, decVal_):
            if self.__sr is None:
                pass
            elif decVal_ > self.__n:
                pass
            else:
                self.__n -= decVal_

        def UpdateTask(self, taskID_ : int, adding_ : bool):
            if self.__sr is None:
                return None

            _te = None
            if len(self.__at) <= 0:
                if not adding_:
                    pass
                else:
                    _te = _SyncResourcesGuard._TaskEntry(taskID_, True)
                    self.__at.append(_te)
            else:
                _lstTE = [ _te for _te in self.__at if _te.dtaskUID == taskID_ ]
                _LEN = len(_lstTE)
                if _LEN > 1:
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00174)
                _te = None if _LEN == 0 else _lstTE[0]
                if _te is None:
                    if not adding_:
                        _te = self.__at[0]
                    else:
                        _te = _SyncResourcesGuard._TaskEntry(taskID_, False)
                        self.__at.append(_te)
                if not adding_:
                    if _te.DecNumLocks() <= 0:
                        self.__at.remove(_te)
                        _te.CleanUp()
                        _te = None
                else:
                    _te.IncNumLocks()
            if _te is not None:
                self.__n += 1 if adding_ else -1
            return _te

        def _ToString(self):
            pass

        def _CleanUp(self):
            if self.__sr is not None:
                for _te in self.__at:
                    _te.CleanUp()
                self.__at.clear()
                self.__n  = None
                self.__at = None
                self.__sr = None

    __slots__ = [ '__ar' , '__rl' ]

    __sgltn = None

    def __init__(self):
        self.__ar = None
        self.__rl = None
        super().__init__()

        if _SyncResourcesGuard.__sgltn is not None:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00175)
            self.CleanUp()
        else:
            self.__ar = []
            self.__rl = _PyRLock()
            _SyncResourcesGuard.__sgltn = self

    @property
    def numResources(self):
        return 0 if self.__rl is None else len(self.__ar)

    def GuardSyncResource(self, sres_, taskID_ : int, syncPeer_ =None):
        self.__UpdateSyncRes(sres_, taskID_, True, syncPeer_=syncPeer_)

    def DisregardSyncResource(self, sres_, taskID_ : int):
        self.__UpdateSyncRes(sres_, taskID_, False)

    def ReleaseAcquiredSyncResources(self, taskID_ : int):
        if self.__rl is None:
            return

        self.__rl.acquire()
        _lstTbr = []
        for _re in self.__ar:
            if not _re.sres._isValid:
                continue

            _lstTE = [_te for _te in _re.tasks if _te.dtaskUID==taskID_]
            _LEN = len(_lstTE)
            if _LEN > 1:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00176)
            _te = None if _LEN==0 else _lstTE[0]
            if _te is not None:
                numRel = _re.sres._TryRelease(maxTryNum_=_te.numLocks)
                _re.DecNumLocks(_te.numLocks)
                _re.tasks.remove(_te)
                _te.CleanUp()
            if _re.numTasks <= 0:
                _lstTbr.append(_re)
        for _re in _lstTbr:
            self.__ar.remove(_re)
            _re.CleanUp()
        self.__rl.release()

    @staticmethod
    def _GetInstance():
        return _SyncResourcesGuard.__sgltn

    @staticmethod
    def _CreateInstance():
        _SyncResourcesGuard.__sgltn = _SyncResourcesGuard()
        return _SyncResourcesGuard.__sgltn

    @staticmethod
    def _ClsDepInjection(dinjCmd_ : _EDepInjCmd):
        if dinjCmd_.isDeInject:
            res = True
            _srg = _SyncResourcesGuard._GetInstance()
            if _srg is not None:
                _srg.CleanUp()
        else:
            _srg = _SyncResourcesGuard._CreateInstance()
            res = _srg is not None
            if not res:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00956)
        return res

    def _ToString(self):
        pass

    def _CleanUp(self):
        if self.__rl is None:
            return

        _SyncResourcesGuard.__sgltn = None
        self.__rl.acquire()
        for _rr in self.__ar:
            _rr.CleanUp()
        self.__ar.clear()
        self.__rl.release()
        self.__ar = None
        self.__rl = None

    def __UpdateSyncRes(self, sres_, taskID_ : int, adding_ : bool, syncPeer_ =None):
        if (self.__rl is None) or (sres_ is None) or not sres_._isValid:
            return

        self.__rl.acquire()

        _teAd = None
        _lstRes = [ _re for _re in self.__ar if id(_re.sres) == id(sres_) ]
        if len(_lstRes) > 1:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00177)
        _re = None if len(_lstRes) == 0 else _lstRes[0]
        if _re is None:
            if not adding_:
                pass
            else:
                _re = _SyncResourcesGuard._SResEntry(sres_)
                self.__ar.append(_re)
        if _re is None:
            pass
        else:
            _te = _re.UpdateTask(taskID_, adding_)
            if (syncPeer_ is not None) and adding_:
                _teAd = _te
            if _re.numTasks <= 0:
                self.__ar.remove(_re)
                _re.CleanUp()

        if _teAd is None:
            pass
        else:
            _lstRes = [_re for _re in self.__ar if id(_re.sres)==id(syncPeer_)]
            if len(_lstRes) > 1:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00178)

            _pr = None if len(_lstRes)==0 else _lstRes[0]

            if _pr is None:
                pass
            else:
                _pt = _pr.UpdateTask(taskID_, True)

        self.__rl.release()
