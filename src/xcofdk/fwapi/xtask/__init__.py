# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : __init__.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


"""
Package 'xcofdk.fwapi.xtask' represents the public interface of the framework
related to task instances.
"""


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
from .xtaskerror   import XTaskError
from .xtaskerror   import XTaskException
from .xtaskprofile import XTaskProfile
from .xtask        import XTask
from .mainxtask    import MainXTask
