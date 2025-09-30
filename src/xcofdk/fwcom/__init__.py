# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : __init__.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


"""
Subpackage 'xcofdk.fwcom' provides the API of commonly used definitions and
data types available through below modules:
   - fwdefs
   - xmsgdefs
   - xmpdefs
"""


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
from .fwdefs   import CompoundTUID
from .fwdefs   import EExecutionCmdID
from .fwdefs   import override
from .fwdefs   import LcFailure
from .xmpdefs  import EProcessStartMethodID
from .xmpdefs  import EXmpPredefinedID
from .xmsgdefs import EXmsgPredefinedID
