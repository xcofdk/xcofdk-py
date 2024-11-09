# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwrteseed.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from os import getpid as _PyGetPID


class _FwRteSeed:

    __slots__ = [ '__bMaster' , '__seed' ]

    __FW_RTE_SEED    = None
    __bFW_RTE_MASTER = None

    def __new__(cls, *args_, **kwargs_):
        if _FwRteSeed.__FW_RTE_SEED is None:
            _FwRteSeed.__FW_RTE_SEED = _PyGetPID()
        if _FwRteSeed.__bFW_RTE_MASTER is None:
            _FwRteSeed.__bFW_RTE_MASTER = False
        return super().__new__(cls)
    def __init__(self):

        self.__seed    = int(_FwRteSeed.__FW_RTE_SEED)
        self.__bMaster = _FwRteSeed.__bFW_RTE_MASTER

    def __str__(self):
        return f'FwRteSeed: seed={self.seed} , bMaster={self.isMasterSeed}'


    @staticmethod
    def IsRteSeedInitialized():
        return _FwRteSeed.__FW_RTE_SEED is not None

    @staticmethod
    def CheckCreateInitialInstance():
        if _FwRteSeed.__bFW_RTE_MASTER is None:
            _FwRteSeed.__bFW_RTE_MASTER = True
        return _FwRteSeed()

    @property
    def isMasterSeed(self):
        return self.__bMaster

    @property
    def seed(self):
        return self.__seed

    def CloneAndUpdate(self):
        _seed    = self.seed
        _bMaster = self.isMasterSeed

        res = _FwRteSeed()
        res.__seed    = _seed
        res.__bMaster = _bMaster

        _new = _FwRteSeed()
        self.__seed    = _new.seed
        self.__bMaster = _new.__bMaster

        del _new
        return res
