# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : __init__.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


"""
Package 'xcofdk.fwapi.xmsg' provides framework's public API for the subsystem
'xmsg' for messaging.


Deprecated API:
----------------
Starting with XCOFDK-py v3.0 below API entities (formerly part of
the API of this package) are deprecated and not available anymore:
    >>> # renaming
    >>> XPayloadIF = IPayload
"""


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from .xmsg       import IMessage
from .xmsg       import XMessage
from .xpayload   import IPayload
from .xpayload   import XPayload
from .xmsgheader import IMessageHeader
