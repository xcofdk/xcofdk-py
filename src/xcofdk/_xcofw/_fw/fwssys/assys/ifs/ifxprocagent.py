# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : ifxprocagent.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from typing import Any

from _fw.fwssys.fwcore.types.aobject import _AbsSlotsObject
from _fw.fwssys.fwmp.xprocessstate   import _EPState

class _IXProcAgent(_AbsSlotsObject):
    __slots__ = []

    def __init__(self):
        super().__init__()

    @property
    def _isAttachedToFW(self) -> bool:
        pass

    @property
    def _isStarted(self) -> bool:
        pass

    @property
    def _isTerminated(self) -> bool:
        pass

    @property
    def _xprocessPID(self) -> int:
        pass

    @property
    def _xprocessName(self) -> str:
        pass

    @property
    def _xprocessAliasName(self):
        pass

    def _OnPTerminated(self, tst_ : _EPState, xc_ : int, sd_ : Any):
        pass
