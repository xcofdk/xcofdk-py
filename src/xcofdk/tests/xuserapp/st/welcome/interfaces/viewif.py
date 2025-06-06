# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : viewif.py
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
class UserAppViewIF:

    __slots__ = []

    def __init__(self):
        pass

    @property
    def isActive(self) -> bool:
        return False

    def StartView(self) -> bool:
        return False

    def UpdateView(self, updateCounter_ : int =None) -> bool:
        return False
#END class UserAppViewIF
