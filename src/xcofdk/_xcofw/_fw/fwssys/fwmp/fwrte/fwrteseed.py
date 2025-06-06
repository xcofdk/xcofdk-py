# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwrteseed.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from os import getpid as _PyGetPID

from _fw.fwssys.fwcore.types.commontypes import _CommonDefines

class _FwRteSeed:
    __slots__ = [ '__bM' , '__s' ]

    __FW_RTE_SEED    = None
    __bFW_RTE_MASTER = None

    def __new__(cls, *args_, **kwargs_):
        if _FwRteSeed.__FW_RTE_SEED is None:
            _FwRteSeed.__FW_RTE_SEED = _PyGetPID()
        if _FwRteSeed.__bFW_RTE_MASTER is None:
            _FwRteSeed.__bFW_RTE_MASTER = False
        return super().__new__(cls)

    def __init__(self):
        self.__s  = int(_FwRteSeed.__FW_RTE_SEED)
        self.__bM = _FwRteSeed.__bFW_RTE_MASTER

    def __str__(self):
        return _CommonDefines._STR_EMPTY

    @staticmethod
    def CheckCreateMasterSeed():
        if _FwRteSeed.__bFW_RTE_MASTER is None:
            _FwRteSeed.__bFW_RTE_MASTER = True
        return _FwRteSeed()

    @property
    def seed(self):
        return self.__s

    def CloneAndUpdateChild(self):
        _seed  = self.__s
        _bMstr = self.__bM

        res = _FwRteSeed()
        res.__s  = _seed
        res.__bM = _bMstr

        self.__s  = _PyGetPID()
        self.__bM = False

        return res

    @staticmethod
    def _Reset():
        _FwRteSeed.__bFW_RTE_MASTER = None
        _FwRteSeed.__bFW_RTE_MASTER = None
