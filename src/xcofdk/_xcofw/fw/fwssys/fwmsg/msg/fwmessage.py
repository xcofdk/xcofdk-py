# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : message.py
#
# Copyright(c) 2023-2024 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from xcofdk.fwapi.xmsg.xpayloadif import XPayloadIF

from xcofdk._xcofw.fw.fwssys.fwcore.logging           import logif
from xcofdk._xcofw.fw.fwssys.fwcore.logging           import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.types.atomicint   import _AtomicInteger
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes import _CommonDefines
from xcofdk._xcofw.fw.fwssys.fwcore.types.serdes      import SerDes

from xcofdk._xcofw.fw.fwssys.fwmsg.msg           import _EMessagePeer
from xcofdk._xcofw.fw.fwssys.fwmsg.msg           import _EMessageType
from xcofdk._xcofw.fw.fwssys.fwmsg.msg           import _EMessageCluster
from xcofdk._xcofw.fw.fwssys.fwmsg.msg           import _EMessageLabel
from xcofdk._xcofw.fw.fwssys.fwmsg.msg           import _EMessageChannel
from xcofdk._xcofw.fw.fwssys.fwmsg.msg           import _FwMessageHeader
from xcofdk._xcofw.fw.fwssys.fwmsg.msg.fwpayload import _FwPayload
from xcofdk._xcofw.fw.fwssys.fwmsg.msg.messageif import _MessageIF

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine


class _FwMessage(_MessageIF):

    class __MessageCreator:
        def __init__(self):
            pass

    __MSG_CREATOR  = __MessageCreator()
    __nextUniqueNr = None

    __slots__ = [ '__hdr' , '__uid' , '__pld' ]

    def __init__(self, msgCreator_, senderID_, receiverID_, labelID_, clusterID_, channelID_, typeID_):
        super().__init__()

        self.__hdr = None
        self.__uid = None
        self.__pld = None

        if not msgCreator_ == _FwMessage.__MSG_CREATOR:
            vlogif._LogOEC(True, -1651)
            return

        header = _FwMessageHeader(typeID_, channelID_, clusterID_, labelID_, senderID_, receiverID_)
        if not header.isValid:
            self.CleanUp()
        else:
            self.__hdr = header
            self.__uid = _FwMessage._GetNextUniqueNr(bFwMsg_=True)



    @staticmethod
    def CreateMessage(senderID_ : _EMessagePeer, receiverID_ =_EMessagePeer.ePDontCare, labelID_ =_EMessageLabel.eLDontCare, clusterID_ =_EMessageCluster.eCDontCare):
        res = _FwMessage(_FwMessage.__MSG_CREATOR, senderID_, receiverID_, labelID_, clusterID_, _EMessageChannel.eChInterTask, _EMessageType.eTIntraProcess)
        if res.header is None:
            res.CleanUp()
            res = None
        return res

    @staticmethod
    def CreateMessageMIntern(labelID_ =_EMessageLabel.eLDontCare, clusterID_ =_EMessageCluster.eCDontCare, senderID_ =_EMessagePeer.ePDontCare):
        res = _FwMessage(_FwMessage.__MSG_CREATOR, senderID_, senderID_, labelID_, clusterID_, _EMessageChannel.eChIntraTask, _EMessageType.eTIntraProcess)
        if res.header is None:
            res.CleanUp()
            res = None
        return res

    @staticmethod
    def CreateInMessageIPC(senderID_ : _EMessagePeer, receiverID_ : _EMessagePeer, labelID_ =_EMessageLabel.eLDontCare, clusterID_ =_EMessageCluster.eCDontCare):
        return _FwMessage.__CreateMessageIPC(senderID_, receiverID_, labelID_, clusterID_, _EMessageType.eTIncoming)

    @staticmethod
    def CreateOutMessageIPC(senderID_ : _EMessagePeer, receiverID_ : _EMessagePeer, labelID_ =_EMessageLabel.eLDontCare, clusterID_ =_EMessageCluster.eCDontCare):
        return  _FwMessage.__CreateMessageIPC(senderID_, receiverID_, labelID_, clusterID_, _EMessageType.eTOutgoing)

    @staticmethod
    def CreateInMessageInterCPU(senderID_ : _EMessagePeer, receiverID_ : _EMessagePeer, labelID_ =_EMessageLabel.eLDontCare, clusterID_ =_EMessageCluster.eCDontCare):
        return  _FwMessage.__CreateMessageInterCPU(senderID_, receiverID_, labelID_, clusterID_, _EMessageType.eTIncoming)

    @staticmethod
    def CreateOutMessageInterCPU(senderID_ : _EMessagePeer, receiverID_ : _EMessagePeer, labelID_ =_EMessageLabel.eLDontCare, clusterID_ =_EMessageCluster.eCDontCare):
        return  _FwMessage.__CreateMessageInterCPU(senderID_, receiverID_, labelID_, clusterID_, _EMessageType.eTOutgoing)

    @staticmethod
    def CreateInMessageNetwork(senderID_ : _EMessagePeer, receiverID_ : _EMessagePeer, labelID_ =_EMessageLabel.eLDontCare, clusterID_ =_EMessageCluster.eCDontCare):
        return  _FwMessage.__CreateMessageNetwork(senderID_, receiverID_, labelID_, clusterID_, _EMessageType.eTIncoming)

    @staticmethod
    def CreateOutMessageNetwork(senderID_ : _EMessagePeer, receiverID_ : _EMessagePeer, labelID_ =_EMessageLabel.eLDontCare, clusterID_ =_EMessageCluster.eCDontCare):
        return  _FwMessage.__CreateMessageNetwork(senderID_, receiverID_, labelID_, clusterID_, _EMessageType.eTOutgoing)

    @staticmethod
    def CreateMessageCustom(senderID_ : _EMessagePeer, receiverID_ : _EMessagePeer, labelID_ =_EMessageLabel.eLDontCare, clusterID_=_EMessageCluster.eCDontCare, typeID_=_EMessageType.eTIntraProcess):
        res = _FwMessage(_FwMessage.__MSG_CREATOR, senderID_, receiverID_, labelID_, clusterID_, channelID_=_EMessageChannel.eChCustom, typeID_=typeID_)
        if res.header is None:
            res.CleanUp()
            res = None
        return res

    @staticmethod
    def SerializeFwMsg(msgObj_) -> bytes:
        if not (isinstance(msgObj_, _FwMessage) and msgObj_.isValid):
            vlogif._LogOEC(True, -1652)
            return None

        if msgObj_.header.channelID != _EMessageChannel.eChIntraTask:
            if msgObj_.header.channelID != _EMessageChannel.eChInterTask:
                vlogif._LogOEC(True, -1653)
        return SerDes.SerializeObject(msgObj_)

    @staticmethod
    def DeserializeFwMsg(bytes_ : bytes):
        if not isinstance(bytes_, bytes):
            vlogif._LogOEC(True, -1654)
            return None

        res = SerDes.DeserializeData(bytes_)
        if not (isinstance(res, _FwMessage) and res.isValid):
            vlogif._LogOEC(True, -1655)
            return None

        if res.header.channelID != _EMessageChannel.eChIntraTask:
            if res.header.channelID != _EMessageChannel.eChInterTask:
                vlogif._LogOEC(True, -1656)
        return res


    @property
    def isValid(self):
        return (self.__hdr is not None) and self.__hdr.isValid


    @property
    def uniqueID(self):
        return self.__uid

    @property
    def header(self):
        return self.__hdr

    @property
    def payload(self) -> _FwPayload:
        return self.__pld

    def AttachPayload(self, payld_ : _FwPayload ):
        if not self.isValid:
            return None

        res = self.__pld
        if payld_ is not None:
            if not (isinstance(payld_, _FwPayload) and payld_.isValidPayload):
                _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwMessage_TextID_002).format(XPayloadIF.__name__, type(payld_).__name__)
                if not isinstance(payld_, _FwPayload):
                    logif._LogBadUse(_msg)
                else:
                    logif._LogError(_msg)
            else:
                self.__pld = payld_
        return res

    def _ToString(self, *args_, **kwargs_):
        if self.__hdr is None:
            return _CommonDefines._STR_EMPTY
        _tmp = 0 if self.__pld is None else self.__pld.numParameters
        return _FwTDbEngine.GetText(_EFwTextID.eFwMessage_ToString_01).format(self.uniqueID, self.__hdr.ToString(True), _tmp)

    def _CleanUp(self):
        if self.__hdr is None:
            return

        self.__hdr.CleanUp()
        self.__hdr = None

        if self.__pld is not None:
            self.__pld.CleanUp()
            self.__pld = None
        super()._CleanUp()


    @staticmethod
    def _GetNextUniqueNr(bFwMsg_ =False):
        if _FwMessage.__nextUniqueNr is None:
            _FwMessage.__nextUniqueNr = _AtomicInteger(value_=0)

        res = _FwMessage.__nextUniqueNr.Increment()
        if bFwMsg_:
            res *= -1
        return res


    @staticmethod
    def __CreateMessageIPC(senderID_ : _EMessagePeer, receiverID_ : _EMessagePeer, labelID_ : _EMessageLabel, clusterID_ : _EMessageCluster, typeID_ : _EMessageType):
        if typeID_ == _EMessageType.eTDontCare or typeID_ == _EMessageType.eTIntraProcess:
            vlogif._LogOEC(True, -1657)
        logif._LogNotImplemented(_FwTDbEngine.GetText(_EFwTextID.eMisc_ImplError))
        return None

    @staticmethod
    def __CreateMessageInterCPU(senderID_ : _EMessagePeer, receiverID_ : _EMessagePeer, labelID_ : _EMessageLabel, clusterID_ : _EMessageCluster, typeID_ : _EMessageType):
        if typeID_ == _EMessageType.eTDontCare or typeID_ == _EMessageType.eTIntraProcess:
            vlogif._LogOEC(True, -1658)
        logif._LogNotImplemented(_FwTDbEngine.GetText(_EFwTextID.eMisc_ImplError))
        return None

    @staticmethod
    def __CreateMessageNetwork(senderID_ : _EMessagePeer, receiverID_ : _EMessagePeer, labelID_ : _EMessageLabel, clusterID_ : _EMessageCluster, typeID_ : _EMessageType):
        if typeID_ == _EMessageType.eTDontCare or typeID_ == _EMessageType.eTIntraProcess:
            vlogif._LogOEC(True, -1659)
        logif._LogNotImplemented(_FwTDbEngine.GetText(_EFwTextID.eMisc_ImplError))
        return None
