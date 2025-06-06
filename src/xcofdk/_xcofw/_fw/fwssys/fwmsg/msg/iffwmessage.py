# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : iffwmessage.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from xcofdk.fwapi import IPayload

from _fw.fwssys.fwcore.types.aobject import _AbsSlotsObject

from .iffwmessagehdr import _IFwMessageHeader

class _IFwMessage(_AbsSlotsObject):
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
    def header(self) -> _IFwMessageHeader:
        pass

    @property
    def payload(self) -> IPayload:
        pass

    def AttachPayload(self, payld_: IPayload):
        pass

    def Clone(self):
        pass

    def _ToString(self, *args_, **kwargs_) -> str:
        pass

    def _CleanUp(self):
        pass
