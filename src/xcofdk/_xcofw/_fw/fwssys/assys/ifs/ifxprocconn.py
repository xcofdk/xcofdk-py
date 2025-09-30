# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : ifxprocconn.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from _fw.fwssys.assys.ifs               import _IXProcAgent
from _fw.fwssys.fwcore.lc.lcproxyclient import _LcProxyClient
from _fw.fwssys.fwmp.xprocessstate      import _EPState

class _IXProcConn(_LcProxyClient):
    __slots__ = []

    def __init__(self):
        super().__init__()

    @property
    def _xprocessAgent(self) -> _IXProcAgent:
        pass

    def _ConfirmPUID(self):
        pass

    def _CleanUp(self):
        super()._CleanUp()
