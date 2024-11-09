# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : lcssysdeputy.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from enum import unique

from xcofdk._xcofw.fw.fwssys.fwcore.logging                            import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.config.ssysconfig.fwssysconfigbase import _ESubSysID
from xcofdk._xcofw.fw.fwssys.fwcore.config.ssysconfig.fwssysconfigbase import _FwSSysConfigBase
from xcofdk._xcofw.fw.fwssys.fwcore.types.apobject                     import _ProtectedAbstractSlotsObject
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes                  import _FwIntEnum
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcdefines                       import _ELcScope


class _LcSSysDeputy(_ProtectedAbstractSlotsObject):

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


    @unique
    class _EDDeputyCmd(_FwIntEnum):
        eDontCare = 0
        eInject   = 1
        eReInject = 2
        eDeInject = 3
        eFinalize = 4

        @property
        def isInject(self):
            return self == _LcSSysDeputy._EDDeputyCmd.eInject

        @property
        def isReInject(self):
            return self == _LcSSysDeputy._EDDeputyCmd.eReInject

        @property
        def isDeInject(self):
            return self == _LcSSysDeputy._EDDeputyCmd.eDeInject

        @property
        def isFinalize(self):
            return self==_LcSSysDeputy._EDDeputyCmd.eFinalize

    __slots__   = [ '__eSSysID' , '__eState' , '__highestScope' ]

    def __init__(self, ppass_ : int, eSSysID_ : _ESubSysID, highestScope_ : _ELcScope):
        self.__eState       = None
        self.__eSSysID      = None
        self.__highestScope = None
        super().__init__(ppass_)

        if not isinstance(eSSysID_, _ESubSysID):
            vlogif._LogOEC(True, -1559)
            self.CleanUpByOwnerRequest(ppass_)
        if not (isinstance(highestScope_, _ELcScope) and (highestScope_!=_ELcScope.eIdle)):
            vlogif._LogOEC(True, -1560)
            self.CleanUpByOwnerRequest(ppass_)
        else:
            self.__eState       = _LcSSysDeputy._ELcSSysDeputyState.eIdle
            self.__eSSysID      = eSSysID_
            self.__highestScope = highestScope_

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
        return self.__eSSysID

    @property
    def highestScope(self) -> _ELcScope:

        return self.__highestScope

    def ProcLcScopeUpdateRequest(self, tgtScope_ : _ELcScope, srcScope_ : _ELcScope, subsysCfg_ : _FwSSysConfigBase, bForceReinject_ =False, bFinalize_ =False) -> bool:

        if self.deputyID is None:
            return False

        dc = self.__DetermineDeputyCmd(tgtScope_, srcScope_, bForceReinject_=bForceReinject_, bFinalize_=bFinalize_)
        if dc is None:
            return False
        elif dc == _LcSSysDeputy._EDDeputyCmd.eDontCare:
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
        return self.__eState

    def _ToString(self):
        if self.deputyID is None:
            return None
        res = '{}: (state, highestScope)=({}, {})'.format(type(self).__name__, self._deputyState.compactName, self.highestScope.compactName)
        return res

    def _CleanUpByOwnerRequest(self):
        self.__eState       = None
        self.__eSSysID      = None
        self.__highestScope = None

    def _ProcDeputyCmd(self, tgtScope_ : _ELcScope, deputyCmd_ : _FwIntEnum, subsysCfg_ : _FwSSysConfigBase) -> bool:
        return True

    def _SetInjected(self):
        self.__eState = _LcSSysDeputy._ELcSSysDeputyState.eInjected

    def _SetReInjected(self):
        self.__eState = _LcSSysDeputy._ELcSSysDeputyState.eReInjected

    def _SetDeInjected(self):
        self.__eState = _LcSSysDeputy._ELcSSysDeputyState.eDeInjected

    def _SetFailed(self):
        self.__eState = _LcSSysDeputy._ELcSSysDeputyState.eSSysDFailed

    def __DetermineDeputyCmd(self, tgtScope_: _ELcScope, srcScope_: _ELcScope, bForceReinject_ =False, bFinalize_ =False) -> _EDDeputyCmd:

        if not (isinstance(srcScope_, _ELcScope) and isinstance(tgtScope_, _ELcScope)):
            vlogif._LogOEC(True, -1561)
            return None

        res = _LcSSysDeputy._EDDeputyCmd.eDontCare
        if (tgtScope_.lcTransitionalOrder > self.highestScope.lcTransitionalOrder) or (tgtScope_==srcScope_):
            if bForceReinject_:
                res = _LcSSysDeputy._EDDeputyCmd.eReInject
            elif tgtScope_ == srcScope_:
                if bFinalize_:
                    res = _LcSSysDeputy._EDDeputyCmd.eFinalize
        elif tgtScope_.lcTransitionalOrder > srcScope_.lcTransitionalOrder:
            res = _LcSSysDeputy._EDDeputyCmd.eInject
        elif not self.isDeputyIdle:
            res = _LcSSysDeputy._EDDeputyCmd.eDeInject

        return res
