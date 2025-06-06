# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : controllerif.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class UserAppControllerIF:

    __slots__ = []

    def __init__(self):
        pass

    @property
    def isControllerRunning(self):
        pass

    def OnViewNotification(self, notifCounter_ : int, bProgressBarProceeding_ : bool =False, bOnDestroy_ =False) -> bool:
        pass

    def OnViewEncounteredException(self, errMsg_ : str, xcp_ : Exception):
        pass
#END class UserAppControllerIF
