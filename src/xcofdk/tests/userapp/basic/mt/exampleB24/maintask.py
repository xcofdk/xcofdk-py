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
from xcofdk.fwapi.xtask import XTaskProfile

from xcofdk.tests.userapp.basic.mt.exampleB21.maintask import MainTask as _MainTask


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class MainTaskNoSerDes(_MainTask):

    __slots__ = []
    def __init__(self, taskProfile_ : XTaskProfile =None):
        super().__init__(taskProfile_=taskProfile_, guiTitle_='MTGuiAppNoSerDes', bSkipPayloadSerDes_=True)
#END class MainTaskNoSerDes
