# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xprocessbaseif.py
#
# Copyright(c) 2024 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from xcofdk.fwcom.xmpdefs import ChildProcessResultData

from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject import _AbstractSlotsObject


class _XProcessBaseIF(_AbstractSlotsObject):
    __slots__ = []

    def __init__(self):
        super().__init__()

    def _SetProcessExitCode(self, ec_ : int):
        pass

    def _SetProcessResult(self, procResData_ : ChildProcessResultData):
        pass
