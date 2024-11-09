# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xtaskdefs.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes import unique
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes import _FwEnum

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine


@unique
class _EXTaskApiID(_FwEnum):

    eRunXTask               = 0
    eSetUpXTask             = 1
    eTearDownXTask          = 2
    eProcessInternalMessage = 3
    eProcessExternalMessage = 4

    @property
    def functionName(self):
        return _FwTDbEngine.GetText(_EFwTextID(self.value+_EFwTextID.eEXTaskApiID_RunXTask.value))
