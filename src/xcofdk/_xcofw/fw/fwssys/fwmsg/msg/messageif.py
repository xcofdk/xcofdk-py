# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : messageif.py
#
# Copyright(c) 2024 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject import _AbstractSlotsObject

from xcofdk._xcofw.fw.fwssys.fwmsg.msg.messagehdrif import _MessageHeaderIF

from xcofdk.fwapi.xmsg.xpayloadif import XPayloadIF


class _MessageIF(_AbstractSlotsObject):
    __slots__ = []

    def __init__(self):
        super().__init__()

    @property
    def isValid(self) -> bool:
        pass

    @property
    def isXcoMsg(self) -> bool:
        return self.isValid and self.header.isXcoMsgHeader

    @property
    def isFwMsg(self) -> bool:
        return self.isValid and self.header.isFwMsgHeader

    @property
    def isInternalMsg(self) -> bool:
        return self.isValid and self.header.isInternalMsg

    @property
    def isBroadcastMsg(self) -> bool:
        return self.isValid and self.header.isBroadcastMsg

    @property
    def uniqueID(self) -> int:
        pass

    @property
    def header(self) -> _MessageHeaderIF:
        pass

    @property
    def payload(self) -> XPayloadIF:
        pass

    def AttachPayload(self, payld_: XPayloadIF):
        pass

    def Clone(self):
        pass

    def _ToString(self, *args_, **kwargs_) -> str:
        pass

    def _CleanUp(self):
        pass
