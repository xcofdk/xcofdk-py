# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : __init__.py
#
# Copyright(c) 2024 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


"""
Subpackage 'xcofdk.fwcom' provides modules of two categories:
    1) public API of XCOFDK designed for convenient use by applications:
       - fwutil
       - xlogif
       - curxtask
    2) modules commonly used by both public API and protected packages (i.e.
       the internal implementation of the framework) of XCOFDK:
       - fwdefs
       - xmsgdefs
       - xmpdefs
"""


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
from .fwdefs   import ETernaryCallbackResultID
from .fwdefs   import override
from .xmpdefs  import EProcessStartMethodID
from .xmsgdefs import EPreDefinedMessagingID
