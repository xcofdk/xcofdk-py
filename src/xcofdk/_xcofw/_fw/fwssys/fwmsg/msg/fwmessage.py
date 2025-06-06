# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwmessage.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from xcofdk.fwapi import IPayload

from _fw.fwssys.assys                    import fwsubsysshare as _ssshare
from _fw.fwssys.fwcore.logging           import logif
from _fw.fwssys.fwcore.logging           import vlogif
from _fw.fwssys.fwcore.types.atomicint   import _AtomicInteger
from _fw.fwssys.fwcore.types.commontypes import _CommonDefines
from _fw.fwssys.fwcore.types.serdes      import SerDes
from _fw.fwssys.fwmsg.msg                import _EMessagePeer
from _fw.fwssys.fwmsg.msg                import _EMessageType
from _fw.fwssys.fwmsg.msg                import _EMessageCluster
from _fw.fwssys.fwmsg.msg                import _EMessageLabel
from _fw.fwssys.fwmsg.msg                import _EMessageChannel
from _fw.fwssys.fwmsg.msg                import _IFwMessage
from _fw.fwssys.fwmsg.msg                import _FwMessageHeader
from _fw.fwssys.fwmsg.msg.fwpayload      import _FwPayload
from _fw.fwssys.fwerrh.fwerrorcodes      import _EFwErrorCode

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _FwMessage(_IFwMessage):
    class __MessageCreator:
        def __init__(self):
            pass

    __MSG_CREATOR  = __MessageCreator()
    __nextUniqueNr = None

    __slots__ = [ '__h' , '__u' , '__p' ]

    def __init__(self, msgCreator_, senderID_, receiverID_, labelID_, clusterID_, channelID_, typeID_):
        super().__init__()
        self.__h = None
        self.__p = None
        self.__u = None

        if not msgCreator_ == _FwMessage.__MSG_CREATOR:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00530)
            return

        header = _FwMessageHeader(typeID_, channelID_, clusterID_, labelID_, senderID_, receiverID_)
        if not header.isValid:
            self.CleanUp()
        else:
            self.__h = header
            self.__u = _FwMessage._GetNextUniqueNr(bFwMsg_=True)

    @staticmethod
    def CreateMessage(senderID_ : _EMessagePeer, receiverID_ =_EMessagePeer.ePDontCare, labelID_ =_EMessageLabel.eLDontCare, clusterID_ =_EMessageCluster.eCDontCare):
        if _ssshare._IsSubsysMsgDisabled():
            return None
        res = _FwMessage(_FwMessage.__MSG_CREATOR, senderID_, receiverID_, labelID_, clusterID_, _EMessageChannel.eChInterTask, _EMessageType.eTIntraProcess)
        if res.header is None:
            res.CleanUp()
            res = None
        return res

    @staticmethod
    def SerializeFwMsg(msgObj_) -> bytes:
        if not (isinstance(msgObj_, _FwMessage) and msgObj_.isValid):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00532)
            return None

        if msgObj_.header.channelID != _EMessageChannel.eChIntraTask:
            if msgObj_.header.channelID != _EMessageChannel.eChInterTask:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00533)
        return SerDes.SerializeObject(msgObj_)

    @staticmethod
    def DeserializeFwMsg(bytes_ : bytes):
        if not isinstance(bytes_, bytes):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00534)
            return None

        res = SerDes.DeserializeData(bytes_)
        if not (isinstance(res, _FwMessage) and res.isValid):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00535)
            return None

        if res.header.channelID != _EMessageChannel.eChIntraTask:
            if res.header.channelID != _EMessageChannel.eChInterTask:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00536)
        return res

    @property
    def isValid(self):
        return (self.__h is not None) and self.__h.isValid

    @property
    def uniqueID(self):
        return self.__u

    @property
    def header(self):
        return self.__h

    @property
    def payload(self) -> _FwPayload:
        return self.__p

    def AttachPayload(self, payld_ : _FwPayload ):
        if not self.isValid:
            return None

        res = self.__p
        if payld_ is not None:
            if not (isinstance(payld_, _FwPayload) and payld_.isValidPayload):
                _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwMessage_TID_002).format(IPayload.__name__, type(payld_).__name__)
                if not isinstance(payld_, _FwPayload):
                    logif._LogBadUseEC(_EFwErrorCode.FE_00462, _msg)
                else:
                    logif._LogErrorEC(_EFwErrorCode.UE_00134, _msg)
            else:
                self.__p = payld_
        return res

    def _ToString(self):
        if self.__h is None:
            return _CommonDefines._STR_EMPTY
        _tmp = 0 if self.__p is None else self.__p.numParameters
        return _FwTDbEngine.GetText(_EFwTextID.eFwMessage_ToString_01).format(self.uniqueID, self.__h.ToString(True), _tmp)

    def _CleanUp(self):
        if self.__h is None:
            return

        self.__h.CleanUp()
        self.__h = None

        if self.__p is not None:
            self.__p.CleanUp()
            self.__p = None
        super()._CleanUp()

    @staticmethod
    def _GetNextUniqueNr(bFwMsg_ =False):
        if _FwMessage.__nextUniqueNr is None:
            _FwMessage.__nextUniqueNr = _AtomicInteger(value_=0)

        res = _FwMessage.__nextUniqueNr.Increment()
        if bFwMsg_:
            res *= -1
        return res
