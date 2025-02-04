# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xcomsghdrimpl.py
#
# Copyright(c) 2024 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum   import IntEnum
from typing import Union as _PyUnion

from xcofdk.fwcom.xmsgdefs import EPreDefinedMessagingID

from xcofdk._xcofw.fw.fwssys.fwcore.logging import vlogif

from xcofdk._xcofw.fw.fwssys.fwmsg.msg              import _EMessageType
from xcofdk._xcofw.fw.fwssys.fwmsg.msg              import _EMessageChannel
from xcofdk._xcofw.fw.fwssys.fwmsg.msg              import _EMessageCluster
from xcofdk._xcofw.fw.fwssys.fwmsg.msg              import _EMessageLabel
from xcofdk._xcofw.fw.fwssys.fwmsg.msg              import _EMessagePeer
from xcofdk._xcofw.fw.fwssys.fwmsg.msg              import _FwMessageHeader
from xcofdk._xcofw.fw.fwssys.fwmsg.msg              import _SubsysMsgUtil
from xcofdk._xcofw.fw.fwssys.fwmsg.msg.messagehdrif import _MessageHeaderIF

from xcofdk._xcofw.fw.fwssys.fwerrh.fwerrorcodes import _EFwErrorCode

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine

class _XMsgHeaderImpl(_MessageHeaderIF):

    __slots__ = [ '__fwMHdr' ]

    def __init__( self
                , clusterID_  : _PyUnion[IntEnum, int]
                , labelID_    : _PyUnion[IntEnum, int]
                , receiverID_ : _PyUnion[IntEnum, int]
                , senderID_   : int
                , bInternal_    =False
                , cloneBy_      =None):
        super().__init__()

        self.__fwMHdr = None

        if cloneBy_ is not None:
            if not (isinstance(cloneBy_, _XMsgHeaderImpl) and cloneBy_.isValid):
                self.CleanUp()
            else:
                _fwMHdr = cloneBy_.__fwMHdr.Clone()
                if _fwMHdr is None:
                    self.CleanUp()
                else:
                    self.__fwMHdr = _fwMHdr
            return

        if not isinstance(senderID_, int):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00515)
            self.CleanUp()
            return
        if isinstance(clusterID_, _EMessageCluster) or isinstance(labelID_, _EMessageLabel) or isinstance(receiverID_, _EMessagePeer):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00516)
            self.CleanUp()
            return

        _clrID = clusterID_
        _lblID = labelID_
        _sndID = senderID_
        _rcvID = receiverID_

        if isinstance(clusterID_, EPreDefinedMessagingID) and clusterID_==EPreDefinedMessagingID.DontCare:
            _clrID = _EMessageCluster.eCDontCare
        if isinstance(labelID_, EPreDefinedMessagingID) and labelID_==EPreDefinedMessagingID.DontCare:
            _lblID = _EMessageLabel.eLDontCare
        if isinstance(receiverID_, EPreDefinedMessagingID):
            if receiverID_.value > EPreDefinedMessagingID.Broadcast.value:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00517)
                self.CleanUp()
                return
            if receiverID_ == EPreDefinedMessagingID.DontCare:
                _rcvID = _EMessagePeer.ePDontCare
            else:
                _rcvID = _EMessagePeer.ePXTaskBroadcast

        _fwMHdr = _FwMessageHeader( _EMessageType.eTIntraProcess, _EMessageChannel.eChIntraTask if bInternal_ else _EMessageChannel.eChInterTask
                                  , _clrID, _lblID, _sndID, _rcvID)
        if not _fwMHdr.isValid:
            _fwMHdr.CleanUp()
            self.CleanUp()
        else:
            self.__fwMHdr = _fwMHdr

    def __eq__(self, other_):
        res = self.isValid and isinstance(other_, _XMsgHeaderImpl) and other_.isValid
        res = res and self.__fwMHdr == other_.__fwMHdr
        return res

    def __ne__(self, other_):
        return not self.__eq__(other_)

    def __hash__(self):
        if not self.isValid:
            return None
        return hash(id(self)) + hash(self.__fwMHdr)

    @property
    def isValid(self) -> bool:
        return (self.__fwMHdr is not None) and self.__fwMHdr.isValid

    @property
    def isXcoMsgHeader(self) -> bool:
        return True

    @property
    def isFwMsgHeader(self) -> bool:
        return False

    @property
    def isInternalMsg(self) -> bool:
        return False if self.__isInvalid else self.__fwMHdr.isInternalMsg

    @property
    def isBroadcastMsg(self) -> bool:
        return False if self.__isInvalid else self.__fwMHdr.isBroadcastMsg

    @property
    def isGlobalBroadcastMsg(self) -> bool:
        return False if self.__isInvalid else self.__fwMHdr.isGlobalBroadcastMsg

    @property
    def isFwBroadcastMsg(self) -> bool:
        return False if self.__isInvalid else self.__fwMHdr.isFwBroadcastMsg

    @property
    def isXTaskBroadcastMsg(self) -> bool:
        return False if self.__isInvalid else self.__fwMHdr.isXTaskBroadcastMsg

    @property
    def typeID(self) -> _EMessageType:
        return None if self.__isInvalid else self.__fwMHdr.typeID

    @property
    def channelID(self) -> _EMessageChannel:
        return None if self.__isInvalid else self.__fwMHdr.channelID

    @property
    def clusterID(self) -> _PyUnion[IntEnum, int]:
        if self.__isInvalid: return None
        return EPreDefinedMessagingID.DontCare if self.__fwMHdr.isDontCareCluster else self.__fwMHdr.clusterID

    @property
    def labelID(self) -> _PyUnion[IntEnum, int]:
        if self.__isInvalid: return None
        return EPreDefinedMessagingID.DontCare if self.__fwMHdr.isDontCareLabel else self.__fwMHdr.labelID

    @property
    def senderID(self) -> int:
        return None if self.__isInvalid else self.__fwMHdr.senderID

    @property
    def receiverID(self) -> _PyUnion[IntEnum, int]:
        return None if self.__isInvalid else self.__fwMHdr.receiverID

    def Clone(self):
        if not self.isValid:
            return None
        res = _XMsgHeaderImpl(cloneBy_=self)
        if not res.isValid:
            res.CleanUp()
            res = None
        return res

    def _ToString(self, *args_, **kwargs_):
        if self.__isInvalid:
            return None

        if len(args_) > 1:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00518)

        if len(kwargs_) > 0:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00519)

        _bValuesOnly = False

        for _ii in range(len(args_)):
            if 0 == _ii: _bValuesOnly = args_[_ii]

        res = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_025).format( _SubsysMsgUtil.StringizeID(self.clusterID), _SubsysMsgUtil.StringizeID(self.labelID)
                                                                             , _SubsysMsgUtil.StringizeID(self.senderID), _SubsysMsgUtil.StringizeID(self.receiverID), str(self.isInternalMsg))
        if not _bValuesOnly:
            res = _FwTDbEngine.GetText(_EFwTextID.eXcoMsgHeader_ToString_01).format(res)
        return res

    def _CleanUp(self):
        if self.__fwMHdr is not None:
            self.__fwMHdr.CleanUp()
            self.__fwMHdr = None
            super()._CleanUp()

    @property
    def __isInvalid(self) -> bool:
        return (self.__fwMHdr is None) or not self.__fwMHdr.isValid
