# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwcfgdefines.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from enum import unique

from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes import _FwIntEnum


@unique
class _ESubSysID(_FwIntEnum):
    eLogging    =0
    eIPC        =1
    eSupervisor =2

    @property
    def isSupervisor(self):
        return self == _ESubSysID.eSupervisor

    @property
    def isIPC(self):
        return self == _ESubSysID.eIPC

    @property
    def isLogging(self):
        return self == _ESubSysID.eLogging
