# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : iflogrdd.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from typing import List

from _fw.fwssys.fwcore.logrd.logrecord import _LogRecord

class _ILogRDService:
    __slots__ = []

    def __init__(self):
        pass

    def _AddLR(self, logRec_ : _LogRecord):
        pass

    def _FlushBacklog(self, backlog_ : List[_LogRecord], bHLEnabled_ : bool):
        pass

    def _EnablePM(self):
        pass
