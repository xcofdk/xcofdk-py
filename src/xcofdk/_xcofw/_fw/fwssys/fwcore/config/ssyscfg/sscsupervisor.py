# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : sscsupervisor.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from _fw.fwssys.fwcore.logging import vlogif

from _fw.fwssys.fwcore.config.fwcfgdefines        import _ESubSysID
from _fw.fwssys.fwcore.config.fwstartupconfig     import _FwStartupConfig
from _fw.fwssys.fwcore.config.ssyscfg.ssclogging  import _SSConfigLogging
from _fw.fwssys.fwcore.config.ssyscfg.fwssyscbase import _FwSSysConfigBase
from _fw.fwssys.fwcore.config.ssyscfg.fwssyscbase import _FwStartupPolicy
from _fw.fwssys.fwcore.config.ssyscfg.sscipc      import _SSConfigIPC

from _fw.fwssys.fwerrh.fwerrorcodes import _EFwErrorCode

class _SSConfigSupervisor(_FwSSysConfigBase):
    __slots__ = [ '__ac' ]

    __sgltn = None

    def __init__(self, ppass_ : int, suPolicy_ : _FwStartupPolicy, startupCfg_ : _FwStartupConfig):
        self.__ac = dict()

        super().__init__(ppass_, _ESubSysID.eSupervisor, suPolicy_, startupCfg_)

        if self.subsystemID is None:
            pass
        elif _SSConfigSupervisor.__sgltn is not None:
            self.CleanUpByOwnerRequest(ppass_)
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00934)
        else:
            if self.__CreateAllSSConfig(suPolicy_, startupCfg_):
                _SSConfigSupervisor.__sgltn = self

    @property
    def numSubsystems(self):
        return 0 if self.subsystemID is None else len(self.__ac)

    @property
    def subsystemConfigLogging(self):
        return self.GetSubSystemConfig(_ESubSysID.eLogging)

    @property
    def subsystemConfigIPC(self):
        return self.GetSubSystemConfig(_ESubSysID.eIPC)

    @property
    def subsystemConfigSupervisor(self):
        return self.GetSubSystemConfig(_ESubSysID.eSupervisor)

    def GetSubSystemConfig(self, eSSysID_ : _ESubSysID) -> _FwSSysConfigBase:
        res = None
        if self.subsystemID is None:
            pass
        elif not isinstance(eSSysID_, _ESubSysID):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00936)
        elif eSSysID_.isSupervisor:
            res = self
        elif eSSysID_.value in self.__ac:
            res = self.__ac[eSSysID_.value]
        return res

    def _ToString(self):
        if self.subsystemID is None:
            return None
        res  = '{}:  #SSConfig={}'.format(type(self).__name__, self.numSubsystems)
        return res

    def _CleanUpByOwnerRequest(self):
        if _SSConfigSupervisor.__sgltn is not None:
            if id(_SSConfigSupervisor.__sgltn) == id(self):
                _SSConfigSupervisor.__sgltn = None

        if self.__ac is not None:
            keys = list(self.__ac.keys())
            for _kk in keys:
                _vv = self.__ac.pop(_kk)
                if _vv is not None:
                    _vv.CleanUpByOwnerRequest(self._myPPass)
            self.__ac.clear()

            self.__ac = None
            _SSConfigSupervisor.__sgltn = None
        _FwSSysConfigBase._CleanUpByOwnerRequest(self)

    def __CreateAllSSConfig(self, suPolicy_ : _FwStartupPolicy, startupCfg_ : _FwStartupConfig):
        for _n, _m in _ESubSysID.__members__.items():
            if _m.isTLSubsystem:
                continue
            if not _m.isCoreMember:
                continue
            if _m.isSupervisor:
                continue
            if _m.isLogging:
                _ssc = _SSConfigLogging(self._myPPass, suPolicy_, startupCfg_)
            elif _m.isIPC:
                _ssc = _SSConfigIPC(self._myPPass, suPolicy_, startupCfg_)
            else:
                _ssc = None

            if (_ssc is None) or (_ssc.subsystemID is None):
                if _ssc is not None:
                    _ssc.CleanUpByOwnerRequest(self._myPPass)
                break
            self.__ac[_ssc.subsystemID.value] = _ssc

        res = self.numSubsystems == _ESubSysID.GetCoreMembersCount() - 1
        if not res:
            self.CleanUpByOwnerRequest(self._myPPass)
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00935)
        return res
