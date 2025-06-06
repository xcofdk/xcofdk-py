# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwcfgdefines.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum import auto
from enum import unique

from _fw.fwssys.fwcore.types.commontypes import _FwIntEnum

@unique
class _ESubSysID(_FwIntEnum):
    eCore       = 100
    eLogging    = auto()
    eIPC        = auto()
    eSupervisor = auto()
    eErrH       = 200
    eTmr        = 300
    eMsg        = 400
    eMP         = 500

    @property
    def isTLSubsystem(self):
        return self.isCore or self.isErrH or self.isTmr or self.isMsg or self.isMP

    @property
    def isPublicSubsystem(self):
        return self.isMsg or self.isMP or self.isTmr

    @property
    def isCoreMember(self):
        return _ESubSysID.eCore.value < self.value < _ESubSysID.eErrH.value

    @property
    def isCore(self):
        return self == _ESubSysID.eCore

    @property
    def isSupervisor(self):
        return self == _ESubSysID.eSupervisor

    @property
    def isIPC(self):
        return self == _ESubSysID.eIPC

    @property
    def isLogging(self):
        return self == _ESubSysID.eLogging

    @property
    def isTmr(self):
        return self == _ESubSysID.eTmr

    @property
    def isErrH(self):
        return self == _ESubSysID.eErrH

    @property
    def isMsg(self):
        return self == _ESubSysID.eMsg

    @property
    def isMP(self):
        return self == _ESubSysID.eMP

    @staticmethod
    def GetCoreMembersCount():
        return _ESubSysID.eSupervisor.value - _ESubSysID.eCore.value
