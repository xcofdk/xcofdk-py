# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xmsgimpl.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from xcofdk.fwapi               import IPayload
from xcofdk.fwapi.xmsg.xpayload import XPayload

from _fw.fwssys.fwcore.types.commontypes  import _CommonDefines
from _fw.fwssys.fwmsg.msg                 import _IFwMessage
from _fw.fwssys.fwmsg.apiimpl.xmsghdrimpl import _XMsgHeaderImpl

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _XMsgImpl(_IFwMessage):
    __slots__ = [ '__h' , '__u' , '__p' ]

    def __init__(self, uid_ : int, header_ : _XMsgHeaderImpl, payld_ : IPayload =None):
        self.__h = None
        self.__p = None
        self.__u = None
        super().__init__()

        if not (isinstance(header_, _XMsgHeaderImpl) and header_.isValid):
            self.CleanUp()
        elif (payld_ is not None) and not (isinstance(payld_, IPayload) and payld_.isValidPayload):
            self.CleanUp()
        else:
            self.__h = header_
            self.__p = payld_
            self.__u = uid_

    @property
    def isValid(self) -> bool:
        return (self.__h is not None) and self.__h.isValid

    @property
    def uniqueID(self) -> int:
        return self.__u

    @property
    def header(self) -> _XMsgHeaderImpl:
        return self.__h

    @property
    def payload(self) -> IPayload:
        return self.__p

    def AttachPayload(self, payld_ : IPayload ):
        if not self.isValid:
            return None

        res = self.__p
        if payld_ is not None:
            if not (isinstance(payld_, IPayload) and payld_.isValidPayload):
                _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgImpl_TID_001).format(self.uniqueID)
            else:
                self.__p = payld_
        return res

    def _ToString(self) -> str:
        if not self.isValid:
            return _CommonDefines._STR_EMPTY

        _tmp = 0 if self.__p is None else self.__p.numParameters
        res = _FwTDbEngine.GetText(_EFwTextID.eXcoMsgImpl_ToString_01).format(self.uniqueID, self.__h.ToString(True), _tmp)
        return res

    def _CleanUp(self):
        if self.__h is None:
            return

        if self.__p is not None:
            if self.__p.isMarshalingRequired:
                if isinstance(self.__p, XPayload):
                    _cont = self.__p.DetachContainer()
                    if isinstance(_cont, dict):
                        _cont.clear()
            self.__p = None

        self.__h.CleanUp()
        self.__h = None
        self.__u = None
        super()._CleanUp()
