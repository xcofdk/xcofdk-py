# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : iffwsprocmgr.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from typing import List
from typing import Union

from _fw.fwssys.assys.ifs import _IXProcConn
from _fw.fwssys.assys.ifs import _IXProcAgent

class _IFwsProcMgr:
    __slots__ = []

    def __init__(self):
        pass

    def _AddProcess(self, xprocConn_ : _IXProcConn, puid_ : int) -> bool:
        pass

    def _GetXProcesses(self, lstPIDs_ : list =None) -> Union[List[_IXProcAgent], None]:
        pass
