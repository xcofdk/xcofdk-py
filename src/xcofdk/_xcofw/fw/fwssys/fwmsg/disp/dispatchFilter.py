# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : dispatchFilter.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum   import auto
from enum   import IntEnum
from enum   import unique
from typing import Union as _PyUnion

from xcofdk.fwcom.xmsgdefs import EPreDefinedMessagingID

from xcofdk._xcofwa.fwadmindefs import _FwSubsystemCoding

from xcofdk._xcofw.fw.fwssys.fwcore.logging       import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.logging       import logif
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject import _AbstractSlotsObject

from xcofdk._xcofw.fw.fwssys.fwmsg.msg import _EMessagePeer
from xcofdk._xcofw.fw.fwssys.fwmsg.msg import _EMessageType
from xcofdk._xcofw.fw.fwssys.fwmsg.msg import _EMessageCluster
from xcofdk._xcofw.fw.fwssys.fwmsg.msg import _EMessageLabel
from xcofdk._xcofw.fw.fwssys.fwmsg.msg import _EMessageChannel
from xcofdk._xcofw.fw.fwssys.fwmsg.msg import _SubsysMsgUtil

from xcofdk._xcofw.fw.fwssys.fwerrh.fwerrorcodes import _EFwErrorCode

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine

@unique
class _EDispFilterCtorErrorID(IntEnum):
    eNone                                  = 0
    eBadMsgType                            = auto()
    eBadMsgChannel                         = auto()
    eInvalidParams                         = auto()
    eBadInternalMsgFilter                  = auto()
    eBadDefaultDispatchFilter              = auto()
    eCodingMismatchBroadcastDispatchFilter = auto()

    @property
    def isError(self):
        return self != _EDispFilterCtorErrorID.eNone

    @property
    def isInvalidParams(self):
        return self == _EDispFilterCtorErrorID.eInvalidParams

    @property
    def isBadMsgType(self):
        return self == _EDispFilterCtorErrorID.eBadMsgType

    @property
    def isBadMsgChannel(self):
        return self == _EDispFilterCtorErrorID.eBadMsgChannel

    @property
    def isBadInternalMsgFilter(self):
        return self == _EDispFilterCtorErrorID.eBadInternalMsgFilter

    @property
    def isBadDefaultDispatchFilter(self):
        return self == _EDispFilterCtorErrorID.eBadDefaultDispatchFilter

    @property
    def isCodingMismatchBroadcastDispatchFilter(self):
        return self == _EDispFilterCtorErrorID.eCodingMismatchBroadcastDispatchFilter

class _DispatchFilter(_AbstractSlotsObject):

    __slots__ = [ '__clrID' , '__lblID' , '__sndID' , '__rcvID' , '__chlID' , '__typID' , '__bDefault' ]

    def __init__( self
                , typeID_         : _EMessageType
                , channelID_      : _EMessageChannel
                , clusterID_      : _PyUnion[_EMessageCluster, IntEnum, int]
                , labelID_        : _PyUnion[_EMessageLabel, IntEnum, int]
                , senderID_       : _PyUnion[_EMessagePeer,  IntEnum, int]
                , receiverID_     : _PyUnion[_EMessagePeer,  IntEnum, int]
                , bDefaultFilter_   =False):
        super().__init__()

        self.__typID    = None
        self.__clrID    = None
        self.__lblID    = None
        self.__sndID    = None
        self.__chlID    = None
        self.__rcvID    = None
        self.__bDefault = None

        _err = _DispatchFilter.__VerifyFilterParams(typeID_, channelID_, clusterID_, labelID_, senderID_, receiverID_, bDefaultFilter_=bDefaultFilter_)

        if _err.isError:
            self.CleanUp()

            _myMsg   = None
            _midPart = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_DispatchFilter_TextID_001).format(_err.value)

            _bFatal = False
            if _err.isBadMsgType or _err.isBadMsgChannel:
                _bFatal = True
                _myMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_DispatchFilter_TextID_002).format(_midPart, typeID_.value, channelID_.value)

            elif _err.isInvalidParams:
                _myMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_DispatchFilter_TextID_003).format(_midPart, typeID_.value, channelID_.value
                                                                                                 , _SubsysMsgUtil.StringizeID(clusterID_), _SubsysMsgUtil.StringizeID(labelID_)
                                                                                                 , _SubsysMsgUtil.StringizeID(senderID_), _SubsysMsgUtil.StringizeID(receiverID_))
            elif _err.isBadInternalMsgFilter:
                _bFatal = True
                _myMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_DispatchFilter_TextID_004).format( _midPart, channelID_.value
                                                                                                  , _SubsysMsgUtil.StringizeID(senderID_), _SubsysMsgUtil.StringizeID(receiverID_))
            elif _err.isBadDefaultDispatchFilter:
                _myMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_DispatchFilter_TextID_005).format( _midPart
                                                                                                  , _SubsysMsgUtil.StringizeID(clusterID_), _SubsysMsgUtil.StringizeID(labelID_)
                                                                                                  , _SubsysMsgUtil.StringizeID(senderID_), _SubsysMsgUtil.StringizeID(receiverID_))
            elif _err.isCodingMismatchBroadcastDispatchFilter:
                _myMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_DispatchFilter_TextID_006).format( _midPart
                                                                                                  , _SubsysMsgUtil.StringizeID(clusterID_), _SubsysMsgUtil.StringizeID(labelID_)
                                                                                                  , _SubsysMsgUtil.StringizeID(senderID_), _SubsysMsgUtil.StringizeID(receiverID_))
            else:
                _bFatal = True
                _myMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_DispatchFilter_TextID_007).format(_midPart, _err.value)

            if _bFatal:
                logif._LogFatalEC(_EFwErrorCode.FE_00031, _myMsg)
            else:
                logif._LogErrorEC(_EFwErrorCode.UE_00120, _myMsg)
            return

        self.__typID    = typeID_
        self.__clrID    = clusterID_
        self.__lblID    = labelID_
        self.__sndID    = senderID_
        self.__chlID    = channelID_
        self.__rcvID    = receiverID_
        self.__bDefault = bDefaultFilter_

    def __eq__(self, other_):
        res = (self.__typID is not None) and isinstance(other_, _DispatchFilter) and other_.isValid
        res = res and self.__typID    == other_.__typID
        res = res and self.__clrID    == other_.__clrID
        res = res and self.__lblID    == other_.__lblID
        res = res and self.__sndID    == other_.__sndID
        res = res and self.__chlID    == other_.__chlID
        res = res and self.__rcvID    == other_.__rcvID
        res = res and self.__bDefault == other_.__bDefault
        return res

    def __ne__(self, other_):
        return not self.__eq__(other_)

    def __hash__(self):
        if not self.isValid:
            return None
        return hash(hash(self.__typID)+hash(self.__clrID)+hash(self.__lblID)+hash(self.__sndID)+hash(self.__chlID)+hash(self.__rcvID)+hash(self.__bDefault))

    @staticmethod
    def CreateDispatchFilter( typeID_     : _EMessageType                            =_EMessageType.eTIntraProcess
                            , channelID_  : _EMessageChannel                         =_EMessageChannel.eChInterTask
                            , clusterID_  : _PyUnion[_EMessageCluster, IntEnum, int] =_EMessageCluster.eCDontCare
                            , labelID_    : _PyUnion[_EMessageLabel, IntEnum, int]   =_EMessageLabel.eLDontCare
                            , senderID_   : _PyUnion[_EMessagePeer,  IntEnum, int]   =_EMessagePeer.ePDontCare
                            , receiverID_ : _PyUnion[_EMessagePeer,  IntEnum, int]   =_EMessagePeer.ePDontCare):

        res = _DispatchFilter(typeID_=typeID_, channelID_=channelID_, clusterID_=clusterID_, labelID_=labelID_, senderID_=senderID_, receiverID_=receiverID_, bDefaultFilter_=False)
        if not res.isValid:
            res = None
        return res

    @property
    def isValid(self) -> bool:
        return self.__typID is not None

    @property
    def isDefaultDispatchFilter(self) -> bool:
        return self.isValid and self.__bDefault

    @property
    def isDontCareType(self) -> bool:
        return self.isValid and self.__typID.isTDontCare

    @property
    def isDontCareChanel(self) -> bool:
        return self.isValid and self.__chlID.isChDontCare

    @property
    def isDontCareCluster(self) -> bool:
        if not self.isValid:
            return False
        res = isinstance(self.__clrID, _EMessageCluster) and self.__clrID.isCDontCare
        res = res or isinstance(self.__clrID, EPreDefinedMessagingID) and self.__clrID==EPreDefinedMessagingID.DontCare
        return res

    @property
    def isDontCareLabel(self) -> bool:
        if not self.isValid:
            return False
        res = isinstance(self.__lblID, _EMessageLabel) and self.__lblID.isLDontCare
        res = res or isinstance(self.__lblID, EPreDefinedMessagingID) and self.__lblID==EPreDefinedMessagingID.DontCare
        return res

    @property
    def isDontCareSender(self) -> bool:
        if not self.isValid:
            return False
        res = isinstance(self.__sndID, _EMessagePeer) and self.__sndID.isPDontCare
        res = res or isinstance(self.__sndID, EPreDefinedMessagingID) and self.__sndID==EPreDefinedMessagingID.DontCare
        return res

    @property
    def isDontCareReceiver(self) -> bool:
        if not self.isValid:
            return False
        res = isinstance(self.__rcvID, _EMessagePeer) and self.__rcvID.isPDontCare
        res = res or isinstance(self.__rcvID, EPreDefinedMessagingID) and self.__rcvID==EPreDefinedMessagingID.DontCare
        return res

    @property
    def isInternalMessageFilter(self) -> bool:
        return self.isValid and self.__chlID.isChIntraTask

    @property
    def isExternalMessageFilter(self) -> bool:
        return self.isValid and self.__chlID.isChInterTask

    @property
    def isCustomMessageFilter(self) -> bool:
        return self.isValid and self.__chlID.isChCustom

    @property
    def isBroadcastFilter(self) -> bool:
        return self.isValid and isinstance(self.__rcvID, _EMessagePeer) and self.__rcvID.isPBroadcast

    @property
    def isGlobalBroadcastFilter(self) -> bool:
        return self.isValid and isinstance(self.__rcvID, _EMessagePeer) and self.__rcvID.isPGlobalBroadcast

    @property
    def isFwBroadcastFilter(self) -> bool:
        return self.isValid and isinstance(self.__rcvID, _EMessagePeer) and self.__rcvID.isPFwBroadcast

    @property
    def isXTaskBroadcastFilter(self) -> bool:
        return self.isValid and isinstance(self.__rcvID, _EMessagePeer) and self.__rcvID.isPXTaskBroadcast

    @property
    def typeID(self) -> _EMessageType:
        return self.__typID

    @property
    def channelID(self) -> _EMessageChannel:
        return self.__chlID

    @property
    def clusterID(self) -> _PyUnion[_EMessageCluster, IntEnum, int]:
        return self.__clrID

    @property
    def labelID(self) -> _PyUnion[_EMessageLabel, IntEnum, int]:
        return self.__lblID

    @property
    def senderID(self) -> _PyUnion[_EMessagePeer, IntEnum, int]:
        return self.__sndID

    @property
    def receiverID(self) -> _PyUnion[_EMessagePeer, IntEnum, int]:
        return self.__rcvID

    def Clone(self):
        if not self.isValid:
            return None
        res = _DispatchFilter(self.typeID, self.channelID, self.clusterID, self.labelID, self.senderID, self.receiverID)
        if not res.isValid:
            res = None
        return res

    @staticmethod
    def _CreateDefaultDispatchFilter( typeID_     : _EMessageType                            =_EMessageType.eTIntraProcess
                                    , channelID_  : _EMessageChannel                         =_EMessageChannel.eChInterTask
                                    , clusterID_  : _PyUnion[_EMessageCluster, IntEnum, int] =_EMessageCluster.eCDontCare
                                    , labelID_    : _PyUnion[_EMessageLabel, IntEnum, int]   =_EMessageLabel.eLDontCare
                                    , senderID_   : _PyUnion[_EMessagePeer,  IntEnum, int]   =_EMessagePeer.ePDontCare
                                    , receiverID_ : _PyUnion[_EMessagePeer,  IntEnum, int]   =_EMessagePeer.ePDontCare):
        res = _DispatchFilter(typeID_=typeID_, channelID_=channelID_, clusterID_=clusterID_, labelID_=labelID_, senderID_=senderID_, receiverID_=receiverID_, bDefaultFilter_=True)
        if not res.isValid:
            res = None
        return res

    def _ToString(self, *args_, **kwargs_):
        if len(args_) > 1:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00520)

        if len(kwargs_) > 0:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00521)

        _bValuesOnly = False

        for _ii in range(len(args_)):
            if 0 == _ii: _bValuesOnly = args_[_ii]

        res = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_026).format( _SubsysMsgUtil.StringizeID(self.clusterID), _SubsysMsgUtil.StringizeID(self.labelID)
                                                                             , _SubsysMsgUtil.StringizeID(self.senderID), _SubsysMsgUtil.StringizeID(self.receiverID))

        if not _bValuesOnly:
            res = _FwTDbEngine.GetText(_EFwTextID.eMessageFilter_ToString_01).format(res)
        return res

    def _CleanUp(self):
        self.__typID    = None
        self.__clrID    = None
        self.__lblID    = None
        self.__sndID    = None
        self.__chlID    = None
        self.__rcvID    = None
        self.__bDefault = None

    @staticmethod
    def __VerifyFilterParams( typeID_         : _EMessageType
                            , channelID_      : _EMessageChannel
                            , clusterID_      : _PyUnion[_EMessageCluster, IntEnum, int]
                            , labelID_        : _PyUnion[_EMessageLabel, IntEnum, int]
                            , senderID_       : _PyUnion[_EMessagePeer,  IntEnum, int]
                            , receiverID_     : _PyUnion[_EMessagePeer,  IntEnum, int]
                            , bDefaultFilter_   =False):

        _err       = _EDispFilterCtorErrorID.eNone
        _bParamsOK = True

        if not (isinstance(typeID_, _EMessageType) and typeID_.isTIntraProcess):
            _bParamsOK = False
            _err = _EDispFilterCtorErrorID.eBadMsgType
            vlogif._LogNotSupportedEC(_EFwErrorCode.UE_00148, f'[DispFltr] eType: {typeID_}')

        elif not (isinstance(channelID_, _EMessageChannel) and (channelID_.isChInterTask or channelID_.isChIntraTask or channelID_.isChCustom)):
            _bParamsOK = False
            _err = _EDispFilterCtorErrorID.eBadMsgChannel
            vlogif._LogNotSupportedEC(_EFwErrorCode.UE_00149, f'[DispFltr] eChannel: {channelID_}')

        elif channelID_.isChIntraTask and receiverID_ != senderID_:
            _bParamsOK = False
            _err = _EDispFilterCtorErrorID.eBadInternalMsgFilter
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00522)

        else:
            if _bParamsOK and not _SubsysMsgUtil.IsValidClusterID(clusterID_):                           _bParamsOK = False
            if _bParamsOK and not _SubsysMsgUtil.IsValidLabelID(labelID_, grpIDCalledFor_=clusterID_): _bParamsOK = False
            if _bParamsOK and not _SubsysMsgUtil.IsValidPeerID(senderID_, bSender_=True):            _bParamsOK = False
            if _bParamsOK and not _SubsysMsgUtil.IsValidPeerID(receiverID_):                         _bParamsOK = False

        if not _bParamsOK:
            if not _err.isError:
                _err = _EDispFilterCtorErrorID.eInvalidParams
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00523)
            return _err

        _bMsgPeerRcv = isinstance(receiverID_, _EMessagePeer)

        if _bMsgPeerRcv and receiverID_.isPBroadcast:

            if not _FwSubsystemCoding.IsNegativeDispatchFiltersEnabled():
                _err = _EDispFilterCtorErrorID.eCodingMismatchBroadcastDispatchFilter
                vlogif._LogOEC(False, _EFwErrorCode.VUE_00039)
        elif bDefaultFilter_:
            _bIntRcv      = (not _bMsgPeerRcv) and isinstance(receiverID_, int)
            _bDontcareGrp = isinstance(clusterID_,  _EMessageCluster) and clusterID_.isCDontCare
            _bDontcareLbl = isinstance(labelID_,  _EMessageLabel) and labelID_.isLDontCare
            _bDontcareSnd = isinstance(senderID_, _EMessagePeer)  and senderID_.isPDontCare

            if not (_bDontcareGrp and _bDontcareLbl and _bDontcareSnd and _bIntRcv):
                _err = _EDispFilterCtorErrorID.eBadDefaultDispatchFilter
                vlogif._LogOEC(False, _EFwErrorCode.VUE_00040)

        return _err
