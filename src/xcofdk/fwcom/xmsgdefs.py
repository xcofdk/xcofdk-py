# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xmsgdefs.py
#
# Copyright(c) 2024 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from enum import IntEnum


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class EPreDefinedMessagingID(IntEnum):
    """
    Enum class providing pre-defined IDs specified for use in the context of
    task comminication via messaging.

    The IDs currently defined are as follows:
        - DontCare:
          usable wherever wildcard specification of a communication or messaging
          endpoint is applicable. When specified by this ID any possible
          receiver/sender endpoint is intended.

        - MainTask:
          unique ID referring to the singleton of class MainXTask whenever
          anonymous (or alias) addressing is applicable.

        - Broadcast:
          unique ID referring to the wildcard specification of any possible
          receiver endpoint available. This ID is part of the anonymous (or
          alias) addressing, too.

        - MinUserDefinedID:
          unique ID supposed to be used by applications as starting point to
          define their own, custom IDs. In other words, (the integer value of)
          any application specific ID must not be less than this ID.

    Note:
    ------
        - Applications should always introduce their own enum classes (if any)
          as this enum class is not designed to be changed or extended by
          additional enum members.
        - Task communication is described in class description of
          XMessageManager.

    See:
    -----
        - MainXTask
        - XMessageManager
    """

    DontCare         = 0
    MainTask         = 1
    Broadcast        = 2
    MinUserDefinedID = 5001
#END class EPreDefinedMessagingID
