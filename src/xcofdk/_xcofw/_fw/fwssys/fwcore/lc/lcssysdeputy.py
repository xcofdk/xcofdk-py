# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : lcssysdeputy.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum import unique

from _fw.fwssys.fwcore.logging                    import vlogif
from _fw.fwssys.fwcore.config.ssyscfg.fwssyscbase import _ESubSysID
from _fw.fwssys.fwcore.config.ssyscfg.fwssyscbase import _FwSSysConfigBase
from _fw.fwssys.fwcore.lc.lcdefines               import _ELcScope
from _fw.fwssys.fwcore.types.apobject             import _ProtAbsSlotsObject
from _fw.fwssys.fwcore.types.commontypes          import _FwIntEnum
from _fw.fwssys.fwcore.types.commontypes          import _EDepInjCmd

from _fw.fwssys.fwerrh.fwerrorcodes import _EFwErrorCode

class _LcSSysDeputy(_ProtAbsSlotsObject):
    @unique
    class _ELcSSysDeputyState(_FwIntEnum):
        eSSysDFailed = -1
        eIdle        = 0
        eInjected    = 1
        eReInjected  = 2
        eDeInjected  = 3

        @property
        def isIdle(self):
            return self == _LcSSysDeputy._ELcSSysDeputyState.eIdle

        @property
        def isInjected(self):
            return self == _LcSSysDeputy._ELcSSysDeputyState.eInjected

        @property
        def isReInjected(self):
            return self == _LcSSysDeputy._ELcSSysDeputyState.eReInjected

        @property
        def isDeInjected(self):
            return self == _LcSSysDeputy._ELcSSysDeputyState.eDeInjected

        @property
        def isSSysDFailed(self):
            return self == _LcSSysDeputy._ELcSSysDeputyState.eSSysDFailed

    __slots__ = [ '__sid' , '__st' , '__hs' ]

    def __init__(self, ppass_ : int, eSSysID_ : _ESubSysID, highestScope_ : _ELcScope):
        self.__hs  = None
        self.__st  = None
        self.__sid = None
        super().__init__(ppass_)

        if not isinstance(eSSysID_, _ESubSysID):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00405)
            self.CleanUpByOwnerRequest(ppass_)
        if not (isinstance(highestScope_, _ELcScope) and (highestScope_!=_ELcScope.eIdle)):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00406)
            self.CleanUpByOwnerRequest(ppass_)
        else:
            self.__hs  = highestScope_
            self.__st  = _LcSSysDeputy._ELcSSysDeputyState.eIdle
            self.__sid = eSSysID_

    @property
    def isDeputyIdle(self):
        return False if self._deputyState is None else self._deputyState.isIdle

    @property
    def isDeputyInjected(self):
        return False if self._deputyState is None else self._deputyState.isInjected

    @property
    def isDeputyReInjected(self):
        return False if self._deputyState is None else self._deputyState.isReInjected

    @property
    def isDeputyDeInjected(self):
        return False if self._deputyState is None else self._deputyState.isDeInjected

    @property
    def isDeputyFailed(self):
        return False if self._deputyState is None else self._deputyState.isSSysDFailed

    @property
    def deputyID(self) -> _ESubSysID:
        return self.__sid

    @property
    def highestScope(self) -> _ELcScope:
        return self.__hs

    def ProcLcScopeUpdateRequest(self, tgtScope_ : _ELcScope, srcScope_ : _ELcScope, subsysCfg_ : _FwSSysConfigBase, bForceReinject_ =False, bFinalize_ =False) -> bool:
        if self.deputyID is None:
            return False

        dc = self.__DetermineDeputyCmd(tgtScope_, srcScope_, bForceReinject_=bForceReinject_, bFinalize_=bFinalize_)
        if dc is None:
            return False
        elif dc == _EDepInjCmd.eDontCare:
            return True

        res = self._ProcDeputyCmd(tgtScope_, dc, subsysCfg_)
        if not res:
            self._SetFailed()
        else:
            if dc.isInject:
                self._SetInjected()
            elif dc.isReInject:
                self._SetReInjected()
            elif dc.isDeInject:
                self._SetDeInjected()
        return res

    @property
    def _deputyState(self) -> _ELcSSysDeputyState:
        return self.__st

    def _ToString(self):
        if self.deputyID is None:
            return None
        res = '{}: (state, highestScope)=({}, {})'.format(type(self).__name__, self._deputyState.compactName, self.highestScope.compactName)
        return res

    def _CleanUpByOwnerRequest(self):
        self.__hs  = None
        self.__st  = None
        self.__sid = None

    def _ProcDeputyCmd(self, tgtScope_ : _ELcScope, dinjCmd_ : _EDepInjCmd, subsysCfg_ : _FwSSysConfigBase) -> bool:
        return True

    def _SetInjected(self):
        self.__st = _LcSSysDeputy._ELcSSysDeputyState.eInjected

    def _SetReInjected(self):
        self.__st = _LcSSysDeputy._ELcSSysDeputyState.eReInjected

    def _SetDeInjected(self):
        self.__st = _LcSSysDeputy._ELcSSysDeputyState.eDeInjected

    def _SetFailed(self):
        self.__st = _LcSSysDeputy._ELcSSysDeputyState.eSSysDFailed

    def __DetermineDeputyCmd(self, tgtScope_: _ELcScope, srcScope_: _ELcScope, bForceReinject_ =False, bFinalize_ =False) -> _EDepInjCmd:
        if not (isinstance(srcScope_, _ELcScope) and isinstance(tgtScope_, _ELcScope)):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00407)
            return None

        res = _EDepInjCmd.eDontCare
        if (tgtScope_.lcTransitionalOrder > self.highestScope.lcTransitionalOrder) or (tgtScope_==srcScope_):
            if bForceReinject_:
                res = _EDepInjCmd.eReInject
            elif tgtScope_ == srcScope_:
                if bFinalize_:
                    res = _EDepInjCmd.eFinalize
        elif tgtScope_.lcTransitionalOrder > srcScope_.lcTransitionalOrder:
            res = _EDepInjCmd.eInject
        elif not self.isDeputyIdle:
            res = _EDepInjCmd.eDeInject
        return res
