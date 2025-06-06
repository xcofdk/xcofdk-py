# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : ssdsupervisor.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from _fw.fwssys.fwcore.logging                      import vlogif
from _fw.fwssys.fwcore.logging.ssdlogging           import _SSDeputyLogging
from _fw.fwssys.fwcore.config.fwcfgdefines          import _ESubSysID
from _fw.fwssys.fwcore.config.ssyscfg.sscsupervisor import _SSConfigSupervisor
from _fw.fwssys.fwcore.ipc.ssdipc                   import _SSDeputyIPC
from _fw.fwssys.fwcore.lc.lcdefines                 import _ELcScope
from _fw.fwssys.fwcore.lc.lcssysdeputy              import _LcSSysDeputy
from _fw.fwssys.fwcore.types.commontypes            import unique
from _fw.fwssys.fwcore.types.commontypes            import _FwIntEnum

from _fw.fwssys.fwerrh.fwerrorcodes import _EFwErrorCode

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

    __slots__ = [ '__ad' , '__s' ]

    __sgltn = None

    def __init__(self, ppass_ : int, ssysCfgSupv_ : _SSConfigSupervisor):
        self.__s  = None
        self.__ad = dict()
        super().__init__(ppass_, _ESubSysID.eSupervisor, _ELcScope.eFullIPC)

        if self.deputyID is None:
            self.CleanUpByOwnerRequest(ppass_)
        elif _SSDeputySupervisor.__sgltn is not None:
            self.CleanUpByOwnerRequest(ppass_)
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00001)
        elif not isinstance(ssysCfgSupv_, _SSConfigSupervisor):
            self.CleanUpByOwnerRequest(ppass_)
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00002)
        elif not self.__CreateSSDeputies():
            self.CleanUpByOwnerRequest(ppass_)
        else:
            self.__s = ssysCfgSupv_
            _SSDeputySupervisor.__sgltn = self

    @property
    def numSubsystems(self):
        return 0 if self.deputyID is None else len(self.__ad)

    def SwitchLcScope(self, tgtScope_ : _ELcScope, srcScope_ : _ELcScope, bForceReinject_ =False, bFinalize_ =False) -> bool:
        if self.deputyID is None:
            return False

        _KEY_BASE = 11000
        if tgtScope_ == srcScope_:
            _key  = _KEY_BASE
        elif tgtScope_.lcTransitionalOrder < srcScope_.lcTransitionalOrder:
            _key = -1 * (_KEY_BASE + srcScope_.value)
        else:
            _key = _KEY_BASE + tgtScope_.value
        _lstSS = _SSDeputySupervisor.__SINGLE_STEP_TRANS_MAP_TO_SSYS[_key]

        res = True
        for _ss in _lstSS:
            if _ss.isSupervisor:
                _deputy = self
            else:
                _deputy = self.__ad[_ss.value]
            if _deputy.isDeputyFailed:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00003)
                break

            _ssc = self.__s.GetSubSystemConfig(_ss)
            if _ssc is None:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00004)
                break

            res = _deputy.ProcLcScopeUpdateRequest(tgtScope_, srcScope_, _ssc, bForceReinject_=bForceReinject_, bFinalize_=bFinalize_)
            if (not res) or _deputy.isDeputyFailed:
                res = False
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00005)
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
        if _SSDeputySupervisor.__sgltn is not None:
            if id(_SSDeputySupervisor.__sgltn) == id(self):
                _SSDeputySupervisor.__sgltn = None

        if self.__ad is not None:
            keys = list(self.__ad.keys())
            for _kk in keys:
                _vv = self.__ad.pop(_kk)
                if _vv is not None:
                    _vv.CleanUpByOwnerRequest(self._myPPass)
            self.__ad.clear()

            self.__s  = None
            self.__ad = None
            _SSDeputySupervisor.__sgltn = None
        _LcSSysDeputy._CleanUpByOwnerRequest(self)

    def __CreateSSDeputies(self):
        for _n, _m in _ESubSysID.__members__.items():
            if _m.isTLSubsystem:
                continue
            if not _m.isCoreMember:
                continue
            if _m.isSupervisor:
                continue
            if _m.isLogging:
                _ssd = _SSDeputyLogging(self._myPPass)
            elif _m.isIPC:
                _ssd = _SSDeputyIPC(self._myPPass)
            else:
                _ssd = None

            if (_ssd is None) or (_ssd.deputyID is None):
                if _ssd is not None:
                    _ssd.CleanUpByOwnerRequest(self._myPPass)
                break
            self.__ad[_ssd.deputyID.value] = _ssd

        res = self.numSubsystems == _ESubSysID.GetCoreMembersCount() - 1
        if not res:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00006)
        return res
