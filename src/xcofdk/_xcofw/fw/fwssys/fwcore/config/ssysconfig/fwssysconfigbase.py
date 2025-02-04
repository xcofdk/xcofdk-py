# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwssysconfigbase.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from xcofdk._xcofw.fw.fwssys.fwcore.logging import vlogif

from xcofdk._xcofw.fw.fwssys.fwcore.config.fwcfgdefines    import _ESubSysID
from xcofdk._xcofw.fw.fwssys.fwcore.config.fwstartupconfig import _FwStartupConfig
from xcofdk._xcofw.fw.fwssys.fwcore.config.fwstartuppolicy import _FwStartupPolicy
from xcofdk._xcofw.fw.fwssys.fwcore.types.apobject         import _ProtectedAbstractSlotsObject
from xcofdk._xcofw.fw.fwssys.fwerrh.fwerrorcodes           import _EFwErrorCode

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine

class _FwSSysConfigBase(_ProtectedAbstractSlotsObject):

    __slots__  = [ '__eSSysID' , '__fwSUP' , '__fwSCfg' ]

    def __init__(self, ppass_ : int, eSSysID_ : _ESubSysID, suPolicy_ : _FwStartupPolicy, startupCfg_ : _FwStartupConfig):
        self.__fwSUP   = None
        self.__fwSCfg  = None
        self.__eSSysID = None
        super().__init__(ppass_)
        if not (isinstance(eSSysID_, _ESubSysID) and suPolicy_.isValid and startupCfg_._isValid):
            self.CleanUpByOwnerRequest(ppass_)
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00056)
        else:
            self.__fwSUP   = suPolicy_
            self.__fwSCfg  = startupCfg_
            self.__eSSysID = eSSysID_

    @property
    def isValid(self):
        return self.__eSSysID is not None

    @property
    def subsystemID(self) -> _ESubSysID:
        return self.__eSSysID

    @property
    def fwStartupPolicy(self) -> _FwStartupPolicy:
        return self.__fwSUP

    @property
    def fwStartupConfig(self) -> _FwStartupConfig:
        return self.__fwSCfg

    def _ToString(self):
        if not self.isValid:
            return None
        res = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_006).format(type(self).__name__)
        return res

    def _CleanUpByOwnerRequest(self):
        self.__fwSUP   = None
        self.__fwSCfg  = None
        self.__eSSysID = None
