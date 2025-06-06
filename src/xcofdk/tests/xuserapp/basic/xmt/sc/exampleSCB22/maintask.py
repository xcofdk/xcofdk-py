# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : maintask.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from typing import Union

from xcofdk.fwapi     import xlogif
from xcofdk.fwapi.xmt import XTaskProfile

from xuserapp.util.cloptions                     import CLOptions
from xuserapp.basic.xmt.sc.exampleSCB21.maintask import MainTask as _MainTask


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class MainTaskBroadcast(_MainTask):

    __slots__ = []
    def __init__(self, cmdLineOpts_ : CLOptions, taskProfile_ : XTaskProfile =None):
        super().__init__(cmdLineOpts_, taskProfile_=taskProfile_, guiTitle_='XMTGuiAppBroadcast', bBroadcast_=True)


    # --------------------------------------------------------------------------
    # own (protected) interface
    # --------------------------------------------------------------------------
    @staticmethod
    def _CreateSingleton(taskProfile_ : Union[XTaskProfile, None], cmdLineOpts_ : CLOptions):
        res = MainTaskBroadcast(cmdLineOpts_, taskProfile_=taskProfile_)
        if res.isDetachedFromFW:
            res = None
            xlogif.LogError('Failed to create main task.')
        return res
    # --------------------------------------------------------------------------
    #END own (protected) interface
    # --------------------------------------------------------------------------
#END class MainTaskBroadcast
