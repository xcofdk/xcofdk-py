# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : commondefs.py
#
# Copyright(c) 2024 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from enum import auto
from enum import IntEnum
from enum import unique

from xcofdk.fwcom.xmsgdefs import EPreDefinedMessagingID


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
MIN_USER_DEFINED_MESSAGING_ID = EPreDefinedMessagingID.MinUserDefinedID.value


@unique
class EMsgLabelID(IntEnum):
    eServiceTaskInfo  = MIN_USER_DEFINED_MESSAGING_ID + 1000
    eJobReply         = auto()
    eJobRequest       = auto()
    ePausePosting     = auto()
    eResumePosting    = auto()
    eBroadcastPinging = auto()
    ePauseGIL         = auto()
    eResumeGIL        = auto()
    eFibonacciRequest = auto()
    eFibonacciReply   = auto()
#END class EMsgLabelID

class EMsgClusterID(IntEnum):
    eJobProcessing = MIN_USER_DEFINED_MESSAGING_ID + 2000
#END class EMsgClusterID

@unique
class EMsgParamKeyID(IntEnum):
    eNumMsgSent            = 0
    eNumMsgReceived        = auto()
    eNumSendFailures       = auto()
    eNumOutOfOrderReceived = auto()
    eFibonacciInputList    = auto()
    eFibonacciResultList   = auto()
#END class EMsgParamKeyID
