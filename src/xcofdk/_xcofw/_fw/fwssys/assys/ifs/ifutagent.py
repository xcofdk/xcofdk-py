# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : ifutagent.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from typing import Any

from xcofdk.fwapi.xmt import IXTask

from _fw.fwssys.assys.ifs.ifxunit import _IXUnit
from _fw.fwssys.assys.ifs.ifutask import _IUserTask

class _IUTAgent(IXTask):
    __slots__ = []

    def __init__(self):
        super().__init__()

    @property
    def _xUnit(self) -> _IXUnit:
        pass

    @property
    def _xtInst(self) -> IXTask:
        pass

    @property
    def _uTask(self) -> _IUserTask:
        pass

    @_uTask.setter
    def _uTask(self) -> _IUserTask:
        pass
