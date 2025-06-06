# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xmsghdrimpl.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum   import IntEnum
from typing import Union

from xcofdk.fwcom import EXmsgPredefinedID

from _fw.fwssys.fwcore.logging import vlogif

from _fw.fwssys.fwmsg.msg           import _EMessageType
from _fw.fwssys.fwmsg.msg           import _EMessageChannel
from _fw.fwssys.fwmsg.msg           import _EMessageCluster
from _fw.fwssys.fwmsg.msg           import _EMessageLabel
from _fw.fwssys.fwmsg.msg           import _EMessagePeer
from _fw.fwssys.fwmsg.msg           import _SubsysMsgUtil
from _fw.fwssys.fwmsg.msg           import _IFwMessageHeader
from _fw.fwssys.fwmsg.msg           import _FwMessageHeader
from _fw.fwssys.fwerrh.fwerrorcodes import _EFwErrorCode

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _XMsgHeaderImpl(_IFwMessageHeader):
    __slots__ = [ '__h' ]

    def __init__( self
                , clusterID_  : Union[IntEnum, int]
                , labelID_    : Union[IntEnum, int]
                , receiverID_ : Union[IntEnum, int]
                , senderID_   : int
                , bInternal_    =False
                , cloneBy_      =None):
        super().__init__()

        self.__h = None

        if cloneBy_ is not None:
            if not (isinstance(cloneBy_, _XMsgHeaderImpl) and cloneBy_.isValid):
                self.CleanUp()
            else:
                _fwMHdr = cloneBy_.__h.Clone()
                if _fwMHdr is None:
                    self.CleanUp()
                else:
                    self.__h = _fwMHdr
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

        if isinstance(clusterID_, EXmsgPredefinedID) and clusterID_==EXmsgPredefinedID.DontCare:
            _clrID = _EMessageCluster.eCDontCare
        if isinstance(labelID_, EXmsgPredefinedID) and labelID_==EXmsgPredefinedID.DontCare:
            _lblID = _EMessageLabel.eLDontCare
        if isinstance(receiverID_, EXmsgPredefinedID):
            if receiverID_.value > EXmsgPredefinedID.Broadcast.value:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00517)
                self.CleanUp()
                return
            if receiverID_ == EXmsgPredefinedID.DontCare:
                _rcvID = _EMessagePeer.ePDontCare
            else:
                _rcvID = _EMessagePeer.ePXTaskBroadcast

        _fwMHdr = _FwMessageHeader( _EMessageType.eTIntraProcess, _EMessageChannel.eChIntraTask if bInternal_ else _EMessageChannel.eChInterTask
                                  , _clrID, _lblID, _sndID, _rcvID)
        if not _fwMHdr.isValid:
            _fwMHdr.CleanUp()
            self.CleanUp()
        else:
            self.__h = _fwMHdr

    def __eq__(self, other_):
        res = self.isValid and isinstance(other_, _XMsgHeaderImpl) and other_.isValid
        res = res and self.__h == other_.__h
        return res

    def __ne__(self, other_):
        return not self.__eq__(other_)

    def __hash__(self):
        if not self.isValid:
            return None
        return hash(id(self)) + hash(self.__h)

    @property
    def isValid(self) -> bool:
        return (self.__h is not None) and self.__h.isValid

    @property
    def isXcoMsgHeader(self) -> bool:
        return True

    @property
    def isFwMsgHeader(self) -> bool:
        return False

    @property
    def isInternalMsg(self) -> bool:
        return False if self.__isInvalid else self.__h.isInternalMsg

    @property
    def isBroadcastMsg(self) -> bool:
        return False if self.__isInvalid else self.__h.isBroadcastMsg

    @property
    def isGlobalBroadcastMsg(self) -> bool:
        return False if self.__isInvalid else self.__h.isGlobalBroadcastMsg

    @property
    def isFwBroadcastMsg(self) -> bool:
        return False if self.__isInvalid else self.__h.isFwBroadcastMsg

    @property
    def isXTaskBroadcastMsg(self) -> bool:
        return False if self.__isInvalid else self.__h.isXTaskBroadcastMsg

    @property
    def typeID(self) -> _EMessageType:
        return None if self.__isInvalid else self.__h.typeID

    @property
    def channelID(self) -> _EMessageChannel:
        return None if self.__isInvalid else self.__h.channelID

    @property
    def clusterID(self) -> Union[IntEnum, int]:
        if self.__isInvalid: return None
        return EXmsgPredefinedID.DontCare if self.__h.isDontCareCluster else self.__h.clusterID

    @property
    def labelID(self) -> Union[IntEnum, int]:
        if self.__isInvalid: return None
        return EXmsgPredefinedID.DontCare if self.__h.isDontCareLabel else self.__h.labelID

    @property
    def senderID(self) -> int:
        return None if self.__isInvalid else self.__h.senderID

    @property
    def receiverID(self) -> Union[IntEnum, int]:
        return None if self.__isInvalid else self.__h.receiverID

    def Clone(self):
        if not self.isValid:
            return None
        res = _XMsgHeaderImpl(cloneBy_=self)
        if not res.isValid:
            res.CleanUp()
            res = None
        return res

    def _ToString(self, bValuesOnly_ =False):
        if self.__isInvalid:
            return None

        res = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_025).format( _SubsysMsgUtil.StringizeID(self.clusterID), _SubsysMsgUtil.StringizeID(self.labelID)
                                                                             , _SubsysMsgUtil.StringizeID(self.senderID), _SubsysMsgUtil.StringizeID(self.receiverID), str(self.isInternalMsg))
        if not bValuesOnly_:
            res = _FwTDbEngine.GetText(_EFwTextID.eXcoMsgHeader_ToString_01).format(res)
        return res

    def _CleanUp(self):
        if self.__h is not None:
            self.__h.CleanUp()
            self.__h = None
            super()._CleanUp()

    @property
    def __isInvalid(self) -> bool:
        return (self.__h is None) or not self.__h.isValid
