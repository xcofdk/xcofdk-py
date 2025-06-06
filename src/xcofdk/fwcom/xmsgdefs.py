# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xmsgdefs.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from enum import unique
from enum import IntEnum


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
@unique
class EXmsgPredefinedID(IntEnum):
    """
    Enum class providing pre-defined IDs specified for use in the context of
    task comminication via messaging.

    The IDs currently defined are as follows:
        - DontCare:
          usable wherever wildcard specification of a communication or messaging
          endpoint is applicable. When specified by this ID any possible
          receiver/sender endpoint is intended.

        - MainTask:
          unique ID referring to application's main task, i.e. the singleton
          instance of either classes RCTask or XMainTask, whenever anonymous
          (or alias) addressing is applicable.

        - Broadcast:
          unique ID referring to the wildcard specification of any possible
          receiver endpoint available. This ID is part of the anonymous (or
          alias) addressing, too.

        - MinUserDefinedID:
          unique ID supposed to be used by applications as starting point to
          define their own, custom IDs. In other words, (the integer value of)
          any application-specific ID must not be less than this ID.

    Note:
    ------
        - Applications are recommended to always introduce their own enum
          classes (if any) as this enum class must not be changed or extended
          by additional enum members.

    See:
    -----
        - class XMessenger


    Deprecated API:
    ----------------
    Starting with XCOFDK-py v3.0 below enum class is deprecated and not
    available anymore:
        >>> # enum class 'EPreDefinedMessagingID' due to renaming
        >>> EPreDefinedMessagingID = EXmsgPredefinedID
    """

    DontCare         = 0
    MainTask         = 1
    Broadcast        = 2
    MinUserDefinedID = 5001
#END class EXmsgPredefinedID
