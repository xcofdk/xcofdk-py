# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : sysres.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

import sys
import threading

class _SystemResources:
    __slots__ = []

    def __init__(self):
        pass

    @staticmethod
    def _GetRecursionLimit() -> int:
        return sys.getrecursionlimit()

    @staticmethod
    def _SetRecursionLimit(recursionLimit_ : int) -> int:
        sys.setrecursionlimit(recursionLimit_)
        return sys.getrecursionlimit()

    @staticmethod
    def _SetThreadStackSize(size_: int):
        threading.stack_size(size_)
