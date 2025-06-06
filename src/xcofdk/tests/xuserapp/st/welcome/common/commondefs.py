# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : commondefs.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from enum import unique
from enum import IntEnum
from enum import IntFlag


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class EGuiConfig(IntEnum):
    # root window
    eControllerNotificationFrequencyMS  = 100

    # progress bar
    eProgressBarStepSize                = 100
    eProgressBarUpdateFrequencyMS       = 50
    eProgressBarAutoRestartFrequency    = 30
    eProgressBarInitialUpdateWaitTimeMS = 1

    # service view
    eServiceViewSwitchFrequency         = 40
#END class EGuiConfig


@unique
class EDetailViewID(IntFlag):
    eNone = 0x0000

    # simple views
    eMainTask           = (0x0001 << 0)
    eServiceTask        = (0x0001 << 1)

    # messaging views
    eMainTaskMsgInfo    = (0x0001 << 2)
    eServiceTaskMsgInfo = (0x0001 << 3)

    # gil views
    eGil                = (0x0001 << 4)
    eMainTaskGil        = (0x0001 << 5)
    eServiceTaskGil     = (0x0001 << 6)
    eFibonacciResult    = (0x0001 << 7)
    eFibonacciResultMP  = (0x0001 << 8)
#END class EDetailViewID


