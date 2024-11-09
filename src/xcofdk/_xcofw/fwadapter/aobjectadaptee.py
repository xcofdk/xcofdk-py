# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : aobjectadaptee.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------




class _AbstractObject:
    def __init__(self):
        pass

    def __str__(self):
        return self.ToString(self)

    def ToString(self, *args_, **kwargs_) -> str:
        return self._ToString(*args_, **kwargs_)

    def CleanUp(self):
        self._CleanUp()
