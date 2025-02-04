# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwapiimplshare.py
#
# Copyright(c) 2024 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from threading import RLock as _PyRLock

class _FwApiImplShare:
    __slots__ = []

    __theMXT = None
    __theLck = _PyRLock()

    def __init__(self):
        pass

    @staticmethod
    def _GetMainXTask():
        with _FwApiImplShare.__theLck:
            res = _FwApiImplShare.__theMXT
            if (res is not None) and not res._isAttachedToFW:
                res = None
                _FwApiImplShare.__theMXT = None
            return res

    @staticmethod
    def _SetMainXTaskSingleton(mainXT_):
        with _FwApiImplShare.__theLck:
            _FwApiImplShare.__theMXT = mainXT_

    @staticmethod
    def _Reset():
        _FwApiImplShare.__theLck = _PyRLock()
