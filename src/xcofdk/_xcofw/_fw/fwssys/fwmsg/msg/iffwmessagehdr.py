# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : iffwmessagehdr.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum   import IntEnum
from typing import Union

from xcofdk.fwcom import EXmsgPredefinedID

from _fw.fwssys.fwcore.types.aobject import _AbsSlotsObject

from _fw.fwssys.fwmsg.msg import _EMessageType
from _fw.fwssys.fwmsg.msg import _EMessageChannel
from _fw.fwssys.fwmsg.msg import _EMessageCluster
from _fw.fwssys.fwmsg.msg import _EMessageLabel
from _fw.fwssys.fwmsg.msg import _EMessagePeer

class _IFwMessageHeader(_AbsSlotsObject):
    __slots__ = []

    def __init__( self):
        super().__init__()

    @property
    def isValid(self) -> bool:
        pass

    @property
    def isXcoMsgHeader(self) -> bool:
        pass

    @property
    def isFwMsgHeader(self) -> bool:
        pass

    @property
    def isInternalMsg(self) -> bool:
        pass

    @property
    def isBroadcastMsg(self) -> bool:
        pass

    @property
    def isGlobalBroadcastMsg(self) -> bool:
        pass

    @property
    def isFwBroadcastMsg(self) -> bool:
        pass

    @property
    def isXTaskBroadcastMsg(self) -> bool:
        pass

    @property
    def isDontCareCluster(self) -> bool:
        if not self.isValid: return False
        _tmp = self.clusterID
        res = isinstance(_tmp, _EMessageCluster) and _tmp.isCDontCare
        res = res or isinstance(_tmp, EXmsgPredefinedID) and _tmp==EXmsgPredefinedID.DontCare
        return res

    @property
    def isDontCareLabel(self) -> bool:
        if not self.isValid: return False
        _tmp = self.labelID
        res = isinstance(_tmp, _EMessageLabel) and _tmp.isLDontCare
        res = res or isinstance(_tmp, EXmsgPredefinedID) and _tmp==EXmsgPredefinedID.DontCare
        return res

    @property
    def isDontCareReceiver(self) -> bool:
        if not self.isValid: return False
        _tmp = self.receiverID
        res = isinstance(_tmp, _EMessagePeer) and _tmp.isPDontCare
        res = res or isinstance(_tmp, EXmsgPredefinedID) and _tmp==EXmsgPredefinedID.DontCare
        return res

    @property
    def typeID(self) -> _EMessageType:
        pass

    @property
    def channelID(self) -> _EMessageChannel:
        pass

    @property
    def clusterID(self) -> Union[IntEnum, int]:
        pass

    @property
    def labelID(self) -> Union[IntEnum, int]:
        pass

    @property
    def senderID(self) -> int:
        pass

    @property
    def receiverID(self) -> Union[IntEnum, int]:
        pass

    def Clone(self):
        pass

    def _ToString(self, *args_, **kwargs_) -> str:
        pass

    def _CleanUp(self):
        pass
