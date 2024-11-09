# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xcomsgimpl.py
#
# Copyright(c) 2024 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes    import _CommonDefines
from xcofdk._xcofw.fw.fwssys.fwmsg.apiimpl.xcomsghdrimpl import _XMsgHeaderImpl

from xcofdk._xcofw.fw.fwssys.fwmsg.msg.messageif import _MessageIF

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine

from xcofdk.fwapi.xmsg.xpayloadif import XPayloadIF
from xcofdk.fwapi.xmsg.xpayload   import XPayload


class _XMsgImpl(_MessageIF):
    __slots__ = [ '__hdr' , '__uid' , '__pld' ]

    def __init__(self, uid_ : int, header_ : _XMsgHeaderImpl, payld_ : XPayloadIF =None):
        self.__hdr = None
        self.__uid = None
        self.__pld = None
        super().__init__()

        if not (isinstance(header_, _XMsgHeaderImpl) and header_.isValid):
            self.CleanUp()
        elif (payld_ is not None) and not (isinstance(payld_, XPayloadIF) and payld_.isValidPayload):
            self.CleanUp()
        else:
            self.__hdr = header_
            self.__uid = uid_
            self.__pld = payld_


    @property
    def isValid(self) -> bool:
        return (self.__hdr is not None) and self.__hdr.isValid


    @property
    def uniqueID(self) -> int:
        return self.__uid

    @property
    def header(self) -> _XMsgHeaderImpl:
        return self.__hdr

    @property
    def payload(self) -> XPayloadIF:
        return self.__pld

    def AttachPayload(self, payld_ : XPayloadIF ):
        if not self.isValid:
            return None

        res = self.__pld
        if payld_ is not None:
            if not (isinstance(payld_, XPayloadIF) and payld_.isValidPayload):
                _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgImpl_TextID_001).format(self.uniqueID)
            else:
                self.__pld = payld_
        return res

    def _ToString(self, *args_, **kwargs_) -> str:
        if not self.isValid:
            return _CommonDefines._STR_EMPTY

        _tmp = 0 if self.__pld is None else self.__pld.numParameters
        res = _FwTDbEngine.GetText(_EFwTextID.eXcoMsgImpl_ToString_01).format(self.uniqueID, self.__hdr.ToString(True), _tmp)
        return res

    def _CleanUp(self):
        if self.__hdr is None:
            return

        if self.__pld is not None:
            if self.__pld.isMarshalingRequired:
                if isinstance(self.__pld, XPayload):
                    _cont = self.__pld.DetachContainer()
                    if isinstance(_cont, dict):
                        _cont.clear()
            self.__pld = None

        self.__hdr.CleanUp()
        self.__hdr = None
        self.__uid = None
        super()._CleanUp()
