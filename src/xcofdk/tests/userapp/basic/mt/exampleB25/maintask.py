# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : maintask.py
#
# Copyright(c) 2024 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from typing import Union

from xcofdk.fwcom       import xlogif
from xcofdk.fwapi.xtask import XTaskProfile

from xcofdk.tests.userapp.basic.mt.exampleB21.maintask import MainTask as _MainTask


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class MainTaskCustomPayload(_MainTask):

    __slots__ = []
    def __init__(self, taskProfile_ : XTaskProfile =None):
        super().__init__(taskProfile_=taskProfile_, guiTitle_='MTGuiAppCoustomPayload', bCustomPayLoad_=True)


    # --------------------------------------------------------------------------
    # own (protected) interface
    # --------------------------------------------------------------------------
    @staticmethod
    def _CreateSingleton(taskProfile_ : Union[XTaskProfile, None]):
        res = MainTaskCustomPayload(taskProfile_=taskProfile_)
        if res.isDetachedFromFW:
            res = None
            xlogif.LogError('Failed to create main task.')
        return res
    # --------------------------------------------------------------------------
    #END own (protected) interface
    # --------------------------------------------------------------------------
#END class MainTaskCustomPayload
