# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : sscsupervisor.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from xcofdk._xcofw.fw.fwssys.fwcore.logging import vlogif

from xcofdk._xcofw.fw.fwssys.fwcore.config.fwcfgdefines                import _ESubSysID
from xcofdk._xcofw.fw.fwssys.fwcore.config.fwstartupconfig             import _FwStartupConfig
from xcofdk._xcofw.fw.fwssys.fwcore.config.ssysconfig.ssclogging       import _SSConfigLogging
from xcofdk._xcofw.fw.fwssys.fwcore.config.ssysconfig.fwssysconfigbase import _FwSSysConfigBase
from xcofdk._xcofw.fw.fwssys.fwcore.config.ssysconfig.fwssysconfigbase import _FwStartupPolicy
from xcofdk._xcofw.fw.fwssys.fwcore.config.ssysconfig.sscipc           import _SSConfigIPC

from xcofdk._xcofw.fw.fwssys.fwerrh.fwerrorcodes import _EFwErrorCode

class _SSConfigSupervisor(_FwSSysConfigBase):

    __slots__ = [ '__allSSCfg' ]
    __theSSCSupv = None

    def __init__(self, ppass_ : int, suPolicy_ : _FwStartupPolicy, startupCfg_ : _FwStartupConfig):
        self.__allSSCfg = dict()

        super().__init__(ppass_, _ESubSysID.eSupervisor, suPolicy_, startupCfg_)

        if self.subsystemID is None:
            pass
        elif _SSConfigSupervisor.__theSSCSupv is not None:
            self.CleanUpByOwnerRequest(ppass_)
            vlogif._XLogFatalEC(_EFwErrorCode.FE_00898, 'CFG: Violation against singeleton of SSConfig {}.'.format(_ESubSysID.eSupervisor.compactName))
        else:
            if self.__CreateAllSSConfig(suPolicy_, startupCfg_):
                _SSConfigSupervisor.__theSSCSupv = self

    @property
    def numSubsystems(self):
        return 0 if self.subsystemID is None else len(self.__allSSCfg)

    @property
    def subsystemConfigLogging(self):
        return self.GetSubSystemConfig(_ESubSysID.eLogging)

    @property
    def subsystemConfigIPC(self):
        return self.GetSubSystemConfig(_ESubSysID.eIPC)

    @property
    def subsystemConfigSupervisor(self):
        return self.GetSubSystemConfig(_ESubSysID.eSupervisor)

    def GetSubSystemConfig(self, eSubSysID_ : _ESubSysID) -> _FwSSysConfigBase:
        res = None
        if self.subsystemID is None:
            pass
        elif not isinstance(eSubSysID_, _ESubSysID):
            vlogif._XLogFatalEC(_EFwErrorCode.FE_00899, 'CFG: Bad subsystem ID object: {}'.format(type(eSubSysID_).__name__))
        elif eSubSysID_.isSupervisor:
            res = self
        elif not eSubSysID_.value in self.__allSSCfg:
            pass 
        else:
            res = self.__allSSCfg[eSubSysID_.value]
        return res

    def _ToString(self):
        if self.subsystemID is None:
            return None
        res  = '{}:  #SSConfig={}'.format(type(self).__name__, self.numSubsystems)
        return res

    def _CleanUpByOwnerRequest(self):
        if _SSConfigSupervisor.__theSSCSupv is not None:
            if id(_SSConfigSupervisor.__theSSCSupv) == id(self):
                _SSConfigSupervisor.__theSSCSupv = None

        if self.__allSSCfg is not None:
            keys = list(self.__allSSCfg.keys())
            for _kk in keys:
                _vv = self.__allSSCfg.pop(_kk)
                if _vv is not None:
                    _vv.CleanUpByOwnerRequest(self._myPPass)
            self.__allSSCfg.clear()

            self.__allSSCfg = None
            _SSConfigSupervisor.__theSSCSupv = None
        _FwSSysConfigBase._CleanUpByOwnerRequest(self)

    def __CreateAllSSConfig(self, suPolicy_ : _FwStartupPolicy, startupCfg_ : _FwStartupConfig):
        for name, member in _ESubSysID.__members__.items():
            if member.isSupervisor:
                break
            if member.isLogging:
                sscfg = _SSConfigLogging(self._myPPass, suPolicy_, startupCfg_)
            elif member.isIPC:
                sscfg = _SSConfigIPC(self._myPPass, suPolicy_, startupCfg_)
            else:
                sscfg = None

            if (sscfg is None) or (sscfg.subsystemID is None):
                if sscfg is not None:
                    sscfg.CleanUpByOwnerRequest(self._myPPass)
                break
            self.__allSSCfg[sscfg.subsystemID.value] = sscfg

        res = self.numSubsystems == _ESubSysID.eSupervisor.value
        if not res:
            self.CleanUpByOwnerRequest(self._myPPass)
            vlogif._XLogFatalEC(_EFwErrorCode.FE_00900, '[LC] At least one subsystem config still missing.')
        return res
