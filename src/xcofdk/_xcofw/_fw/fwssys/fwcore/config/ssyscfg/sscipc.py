# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : sscipc.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum import auto
from enum import unique

from _fw.fwssys.fwcore.logging           import vlogif
from _fw.fwssys.fwcore.base.strutil      import _StrUtil
from _fw.fwssys.fwcore.types.commontypes import _FwIntEnum

from _fw.fwssys.fwcore.config.fwcfgdefines        import _ESubSysID
from _fw.fwssys.fwcore.config.ssyscfg.fwssyscbase import _FwSSysConfigBase
from _fw.fwssys.fwcore.config.ssyscfg.fwssyscbase import _FwStartupPolicy
from _fw.fwssys.fwcore.config.ssyscfg.fwssyscbase import _FwStartupConfig

class _SSConfigIPC(_FwSSysConfigBase):
    @unique
    class _EIpcConfigEntityID(_FwIntEnum):
        eAbsFwService__CleanFwsTable         = 100
        eMessageClusterMap__CleanMap         = auto()
        eAbsFwService__DefineFwsTable        = auto()
        eSyncResourcesGuard__Singleton       = auto()
        eTaskID__Defines                     = auto()
        eExecutionProfile__LcMonitorRunCycle = auto()
        eAutoEnclosedThreadsBag              = auto()
        eStartupThread__Singleton            = auto()
        eTaskManager__Singleton              = auto()
        eXTaskConn__PRFC                     = auto()
        eXProcConn__PMI                      = auto()
        eFwApi__ConnAccessLock               = auto()
        eFwApiImplShare__AccessLock          = auto()
        eLcFailure__LcResultSilentMode       = auto()

    __slots__ = [ '__bmv1' , '__imv1' , '__imv2' , '__imv3' ]

    def __init__(self, ppass_ : int, suPolicy_ : _FwStartupPolicy, startupCfg_ : _FwStartupConfig):
        self.__bmv1 = True
        self.__imv1 = 50
        self.__imv2 = 20
        self.__imv3 = 100
        super().__init__(ppass_, _ESubSysID.eIPC, suPolicy_, startupCfg_)

        if not self.isValid:
            self.CleanUpByOwnerRequest(ppass_)

    @property
    def isSilentFwLogLevel(self) -> bool:
        return self.fwStartupConfig._isSilentFwLogLevel

    @property
    def isSyncResourceGuardEnabled(self):
        return self.__bmv1

    @property
    def lcMonCyclicRunPauseTimespanMS(self):
        return self.__imv1

    @property
    def lcGuardRunCycleLoopTimespanMS(self):
        return self.__imv2

    @property
    def fwApiConnectorOnDisconnectTimespanMS(self):
        return self.__imv3

    def _ToString(self):
        if self.subsystemID is None:
            res = None
        else:
            res  = '{}:\n'.format(type(self).__name__)
            res += '  {:<38s} : {:<s}\n'.format('isSyncResourceGuardEnabled'           , str(self.isSyncResourceGuardEnabled))
            res += '  {:<38s} : {:<s}\n'.format('lcMonCyclicRunPauseTimespanMS'        , str(self.lcMonCyclicRunPauseTimespanMS))
            res += '  {:<38s} : {:<s}\n'.format('lcGuardRunCycleLoopTimespanMS'        , str(self.lcGuardRunCycleLoopTimespanMS))
            res += '  {:<38s} : {:<s}\n'.format('fwApiConnectorOnDisconnectTimespanMS' , str(self.fwApiConnectorOnDisconnectTimespanMS))
        return res

    def _CleanUpByOwnerRequest(self):
        self.__bmv1 = None
        self.__imv1 = None
        self.__imv2 = None
        self.__imv3 = None
        super()._CleanUpByOwnerRequest()
