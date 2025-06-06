# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwssyscbase.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from _fw.fwssys.fwcore.logging import vlogif

from _fw.fwssys.fwcore.config.fwcfgdefines    import _ESubSysID
from _fw.fwssys.fwcore.config.fwstartupconfig import _FwStartupConfig
from _fw.fwssys.fwcore.config.fwstartuppolicy import _FwStartupPolicy
from _fw.fwssys.fwcore.types.apobject         import _ProtAbsSlotsObject
from _fw.fwssys.fwerrh.fwerrorcodes           import _EFwErrorCode

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _FwSSysConfigBase(_ProtAbsSlotsObject):
    __slots__  = [ '__sp' , '__sc' , '__sid' ]

    def __init__(self, ppass_ : int, eSSysID_ : _ESubSysID, suPolicy_ : _FwStartupPolicy, startupCfg_ : _FwStartupConfig):
        self.__sc  = None
        self.__sp  = None
        self.__sid = None
        super().__init__(ppass_)
        if not (isinstance(eSSysID_, _ESubSysID) and suPolicy_.isValid and startupCfg_._isValid):
            self.CleanUpByOwnerRequest(ppass_)
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00056)
        else:
            self.__sc = startupCfg_
            self.__sp = suPolicy_
            self.__sid = eSSysID_

    @property
    def isValid(self):
        return self.__sid is not None

    @property
    def subsystemID(self) -> _ESubSysID:
        return self.__sid

    @property
    def fwStartupPolicy(self) -> _FwStartupPolicy:
        return self.__sp

    @property
    def fwStartupConfig(self) -> _FwStartupConfig:
        return self.__sc

    def _ToString(self):
        if not self.isValid:
            return None
        res = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_006).format(type(self).__name__)
        return res

    def _CleanUpByOwnerRequest(self):
        self.__sc  = None
        self.__sp  = None
        self.__sid = None
