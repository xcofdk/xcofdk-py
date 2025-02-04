# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : sscipc.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum import auto
from enum import unique

from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes import _FwIntEnum

from xcofdk._xcofw.fw.fwssys.fwcore.config.fwcfgdefines                import _ESubSysID
from xcofdk._xcofw.fw.fwssys.fwcore.config.ssysconfig.fwssysconfigbase import _FwSSysConfigBase
from xcofdk._xcofw.fw.fwssys.fwcore.config.ssysconfig.fwssysconfigbase import _FwStartupPolicy
from xcofdk._xcofw.fw.fwssys.fwcore.config.ssysconfig.fwssysconfigbase import _FwStartupConfig

class _SSConfigIPC(_FwSSysConfigBase):

    @unique
    class _EIpcConfigEntityID(_FwIntEnum):

        eAbstractRunnableFWC__CleanFwcTable  = 100
        eMessageClusterMap__CleanMap         = auto()
        eAbstractRunnableFWC__DefineFwcTable = auto()
        eSyncResourcesGuard__Singleton       = auto()
        eTaskID__Defines                     = auto()
        eExecutionProfile__LcMonitorRunCycle = auto()
        eAutoEnclosedThreadsBag              = auto()
        eStartupThread__Singleton            = auto()
        eTaskManager__Singleton              = auto()
        eXTaskConn__PRFC                     = auto()
        eFwApi__ConnAccessLock               = auto()
        eFwApiImplShare__AccessLock          = auto()

    __slots__ = [ '__bmv1' , '__imv3' , '__imv1' , '__imv2']

    def __init__(self, ppass_ : int, suPolicy_ : _FwStartupPolicy, startupCfg_ : _FwStartupConfig):
        self.__bmv1 = True
        self.__imv1 = 50
        self.__imv2 = 20
        self.__imv3 = 100
        super().__init__(ppass_, _ESubSysID.eIPC, suPolicy_, startupCfg_)

        if not self.isValid:
            self.CleanUpByOwnerRequest(ppass_)

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
