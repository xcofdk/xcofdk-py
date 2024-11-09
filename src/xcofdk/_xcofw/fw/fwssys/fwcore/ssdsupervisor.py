# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : ssdsupervisor.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from xcofdk._xcofw.fw.fwssys.fwcore.logging                         import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.logging.ssdlogging              import _SSDeputyLogging
from xcofdk._xcofw.fw.fwssys.fwcore.config.fwcfgdefines             import _ESubSysID
from xcofdk._xcofw.fw.fwssys.fwcore.config.ssysconfig.sscsupervisor import _SSConfigSupervisor
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcdefines                    import _ELcScope
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcssysdeputy                 import _LcSSysDeputy
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes               import unique
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes               import _FwIntEnum
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.ssdipc                      import _SSDeputyIPC


class _SSDeputySupervisor(_LcSSysDeputy):

    @unique
    class _ESingleScopeTransID(_FwIntEnum):
        ePreIPC_2_Idle     =-11001
        eSemiIPC_2_PreIPC  =-11002
        eFullIPC_2_SemiIPC =-11003

        eReEnter           =11000

        eIdle_2_PreIPC     =11001
        ePreIPC_2_SemiIPC  =11002
        eSemiIPC_2_FullIPC =11003

    __SINGLE_STEP_TRANS_MAP_TO_SSYS = {
        _ESingleScopeTransID.eIdle_2_PreIPC.value     : [_ESubSysID.eLogging , _ESubSysID.eIPC, _ESubSysID.eSupervisor]
      , _ESingleScopeTransID.ePreIPC_2_SemiIPC.value  : [_ESubSysID.eIPC     , _ESubSysID.eSupervisor]
      , _ESingleScopeTransID.eSemiIPC_2_FullIPC.value : [_ESubSysID.eIPC     , _ESubSysID.eSupervisor]

      , _ESingleScopeTransID.eReEnter.value           : [_ESubSysID.eLogging , _ESubSysID.eIPC , _ESubSysID.eSupervisor]

      , _ESingleScopeTransID.ePreIPC_2_Idle.value     : [_ESubSysID.eLogging , _ESubSysID.eSupervisor]
      , _ESingleScopeTransID.eSemiIPC_2_PreIPC.value  : [_ESubSysID.eIPC     , _ESubSysID.eSupervisor]
      , _ESingleScopeTransID.eFullIPC_2_SemiIPC.value : [_ESubSysID.eIPC     , _ESubSysID.eSupervisor]
    }

    __slots__ = [ '__allSSD' , '__sscfgSupv' ]
    __theSSDSupv = None

    def __init__(self, ppass_ : int, ssysCfgSupv_ : _SSConfigSupervisor):
        self.__allSSD    = dict()
        self.__sscfgSupv = None
        super().__init__(ppass_, _ESubSysID.eSupervisor, _ELcScope.eFullIPC)

        if self.deputyID is None:
            self.CleanUpByOwnerRequest(ppass_)
        elif _SSDeputySupervisor.__theSSDSupv is not None:
            self.CleanUpByOwnerRequest(ppass_)
            vlogif._LogOEC(True, -1001)
        elif not isinstance(ssysCfgSupv_, _SSConfigSupervisor):
            self.CleanUpByOwnerRequest(ppass_)
            vlogif._LogOEC(True, -1002)
        elif not self.__CreateSSDeputies():
            self.CleanUpByOwnerRequest(ppass_)
        else:
            self.__sscfgSupv =ssysCfgSupv_
            _SSDeputySupervisor.__theSSDSupv = self

    @property
    def numSubsystems(self):
        return 0 if self.deputyID is None else len(self.__allSSD)

    def SwitchLcScope(self, tgtScope_ : _ELcScope, srcScope_ : _ELcScope, bForceReinject_ =False, bFinalize_ =False) -> bool:
        if self.deputyID is None:
            return False

        _KEY_BASE = 11000
        if tgtScope_ == srcScope_:
            key  = _KEY_BASE
        elif tgtScope_.lcTransitionalOrder < srcScope_.lcTransitionalOrder:
            key  = _KEY_BASE + srcScope_.value
            key *= -1
        else:
            key = _KEY_BASE + tgtScope_.value
        lstSS = _SSDeputySupervisor.__SINGLE_STEP_TRANS_MAP_TO_SSYS[key]

        res = True
        for _ss in lstSS:
            if _ss.isSupervisor:
                deputy = self
            else:
                deputy = self.__allSSD[_ss.value]
            if deputy.isDeputyFailed:
                vlogif._LogOEC(True, -1003)
                break

            ssc = self.__sscfgSupv.GetSubSystemConfig(_ss)
            if ssc is None:
                vlogif._LogOEC(True, -1004)
                break

            res = deputy.ProcLcScopeUpdateRequest(tgtScope_, srcScope_, ssc, bForceReinject_=bForceReinject_, bFinalize_=bFinalize_)
            if (not res) or deputy.isDeputyFailed:
                res = False
                vlogif._LogOEC(True, -1005)
            if not res:
                break
        return res

    def _ToString(self):
        if self.deputyID is None:
            return None
        res = '{}: (state, highestScope)=({}, {})'.format(type(self).__name__, self._deputyState.compactName, self.highestScope.compactName)
        res += ', #SSDs={}'.format(self.numSubsystems)
        return res

    def _CleanUpByOwnerRequest(self):
        if _SSDeputySupervisor.__theSSDSupv is not None:
            if id(_SSDeputySupervisor.__theSSDSupv) == id(self):
                _SSDeputySupervisor.__theSSDSupv = None

        if self.__allSSD is not None:
            keys = list(self.__allSSD.keys())
            for _kk in keys:
                _vv = self.__allSSD.pop(_kk)
                if _vv is not None:
                    _vv.CleanUpByOwnerRequest(self._myPPass)
            self.__allSSD.clear()

            self.__allSSD    = None
            self.__sscfgSupv = None
            _SSDeputySupervisor.__theSSDSupv = None
        _LcSSysDeputy._CleanUpByOwnerRequest(self)

    def __CreateSSDeputies(self):
        for name, member in _ESubSysID.__members__.items():
            if member.isSupervisor:
                break
            if member.isLogging:
                ssd = _SSDeputyLogging(self._myPPass)
            elif member.isIPC:
                ssd = _SSDeputyIPC(self._myPPass)
            else:
                ssd = None

            if (ssd is None) or (ssd.deputyID is None):
                if ssd is not None:
                    ssd.CleanUpByOwnerRequest(self._myPPass)
                break
            self.__allSSD[ssd.deputyID.value] = ssd

        res = self.numSubsystems == _ESubSysID.eSupervisor.value
        if not res:
            vlogif._LogOEC(True, -1006)
        return res
