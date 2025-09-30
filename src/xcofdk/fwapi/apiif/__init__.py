# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : __init__.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


"""
Subpackage 'xcofdk.fwapi.apiif' provides a collection of interface classes
inherited and implemented by other public classes.
"""


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from .ifmsgheader   import IMessageHeader
from .ifmessage     import IMessage
from .iftaskerror   import ITaskError
from .ifpayload     import IPayload
from .iftask        import EExecutionCmdID
from .iftask        import ITask
from .ifrctask      import IRCTask
from .ifrctask      import IRCCommTask
