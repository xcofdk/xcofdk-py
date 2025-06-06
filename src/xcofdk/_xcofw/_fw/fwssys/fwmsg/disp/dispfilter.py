# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : dispfilter.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum   import auto
from enum   import IntEnum
from enum   import unique
from typing import Union

from xcofdk.fwcom import EXmsgPredefinedID

from _fw.fwssys.assys                import fwsubsysshare as _ssshare
from _fw.fwssys.fwcore.logging       import vlogif
from _fw.fwssys.fwcore.logging       import logif
from _fw.fwssys.fwcore.types.aobject import _AbsSlotsObject
from _fw.fwssys.fwmsg.msg            import _EMessagePeer
from _fw.fwssys.fwmsg.msg            import _EMessageType
from _fw.fwssys.fwmsg.msg            import _EMessageCluster
from _fw.fwssys.fwmsg.msg            import _EMessageLabel
from _fw.fwssys.fwmsg.msg            import _EMessageChannel
from _fw.fwssys.fwmsg.msg            import _SubsysMsgUtil
from _fw.fwssys.fwerrh.fwerrorcodes  import _EFwErrorCode
from _fwa.fwsubsyscoding             import _FwSubsysCoding

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

@unique
class _EDFCtorErrID(IntEnum):
    eNone                                  = 0
    eBadMsgType                            = auto()
    eBadMsgChannel                         = auto()
    eInvalidParams                         = auto()
    eBadInternalMsgFilter                  = auto()
    eBadDefaultDispatchFilter              = auto()
    eCodingMismatchBroadcastDispatchFilter = auto()

    @property
    def isError(self):
        return self != _EDFCtorErrID.eNone

    @property
    def isInvalidParams(self):
        return self == _EDFCtorErrID.eInvalidParams

    @property
    def isBadMsgType(self):
        return self == _EDFCtorErrID.eBadMsgType

    @property
    def isBadMsgChannel(self):
        return self == _EDFCtorErrID.eBadMsgChannel

    @property
    def isBadInternalMsgFilter(self):
        return self == _EDFCtorErrID.eBadInternalMsgFilter

    @property
    def isBadDefaultDispatchFilter(self):
        return self == _EDFCtorErrID.eBadDefaultDispatchFilter

    @property
    def isCodingMismatchBroadcastDispatchFilter(self):
        return self == _EDFCtorErrID.eCodingMismatchBroadcastDispatchFilter

class _DispatchFilter(_AbsSlotsObject):
    __slots__ = [ '__c' , '__l' , '__s' , '__r' , '__ch' , '__t' , '__bD' ]

    def __init__( self
                , typeID_         : _EMessageType
                , channelID_      : _EMessageChannel
                , clusterID_      : Union[_EMessageCluster, IntEnum, int]
                , labelID_        : Union[_EMessageLabel, IntEnum, int]
                , senderID_       : Union[_EMessagePeer,  IntEnum, int]
                , receiverID_     : Union[_EMessagePeer,  IntEnum, int]
                , bDefaultFilter_   =False):
        super().__init__()

        self.__c  = None
        self.__l  = None
        self.__r  = None
        self.__s  = None
        self.__t  = None
        self.__bD = None
        self.__ch = None

        if _ssshare._IsSubsysMsgDisabled():
            return

        _err = _DispatchFilter.__VerifyFilterParams(typeID_, channelID_, clusterID_, labelID_, senderID_, receiverID_, bDefaultFilter_=bDefaultFilter_)

        if _err.isError:
            self.CleanUp()

            _myMsg   = None
            _midPart = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_DispatchFilter_TID_001).format(_err.value)

            _bFatal = False
            if _err.isBadMsgType or _err.isBadMsgChannel:
                _bFatal = True
                _myMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_DispatchFilter_TID_002).format(_midPart, typeID_.value, channelID_.value)

            elif _err.isInvalidParams:
                _myMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_DispatchFilter_TID_003).format(_midPart, typeID_.value, channelID_.value
                                                                                                 , _SubsysMsgUtil.StringizeID(clusterID_), _SubsysMsgUtil.StringizeID(labelID_)
                                                                                                 , _SubsysMsgUtil.StringizeID(senderID_), _SubsysMsgUtil.StringizeID(receiverID_))
            elif _err.isBadInternalMsgFilter:
                _bFatal = True
                _myMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_DispatchFilter_TID_004).format( _midPart, channelID_.value
                                                                                                  , _SubsysMsgUtil.StringizeID(senderID_), _SubsysMsgUtil.StringizeID(receiverID_))
            elif _err.isBadDefaultDispatchFilter:
                _myMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_DispatchFilter_TID_005).format( _midPart
                                                                                                  , _SubsysMsgUtil.StringizeID(clusterID_), _SubsysMsgUtil.StringizeID(labelID_)
                                                                                                  , _SubsysMsgUtil.StringizeID(senderID_), _SubsysMsgUtil.StringizeID(receiverID_))
            elif _err.isCodingMismatchBroadcastDispatchFilter:
                _myMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_DispatchFilter_TID_006).format( _midPart
                                                                                                  , _SubsysMsgUtil.StringizeID(clusterID_), _SubsysMsgUtil.StringizeID(labelID_)
                                                                                                  , _SubsysMsgUtil.StringizeID(senderID_), _SubsysMsgUtil.StringizeID(receiverID_))
            else:
                _bFatal = True
                _myMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_DispatchFilter_TID_007).format(_midPart, _err.value)

            if _bFatal:
                logif._LogFatalEC(_EFwErrorCode.FE_00031, _myMsg)
            else:
                logif._LogErrorEC(_EFwErrorCode.UE_00120, _myMsg)
            return

        self.__t  = typeID_
        self.__c  = clusterID_
        self.__l  = labelID_
        self.__s  = senderID_
        self.__ch = channelID_
        self.__r  = receiverID_
        self.__bD = bDefaultFilter_

    def __eq__(self, other_):
        res = (self.__t is not None) and isinstance(other_, _DispatchFilter) and other_.isValid
        res = res and self.__t  == other_.__t
        res = res and self.__c  == other_.__c
        res = res and self.__l  == other_.__l
        res = res and self.__s  == other_.__s
        res = res and self.__ch == other_.__ch
        res = res and self.__r  == other_.__r
        res = res and self.__bD == other_.__bD
        return res

    def __ne__(self, other_):
        return not self.__eq__(other_)

    def __hash__(self):
        if not self.isValid:
            return None
        return hash(hash(self.__t)+hash(self.__c)+hash(self.__l)+hash(self.__s)+hash(self.__ch)+hash(self.__r)+hash(self.__bD))

    @staticmethod
    def CreateDispatchFilter( typeID_     : _EMessageType                            =None
                            , channelID_  : _EMessageChannel                         =None
                            , clusterID_  : Union[_EMessageCluster, IntEnum, int] =None
                            , labelID_    : Union[_EMessageLabel, IntEnum, int]   =None
                            , senderID_   : Union[_EMessagePeer,  IntEnum, int]   =None
                            , receiverID_ : Union[_EMessagePeer,  IntEnum, int]   =None):
        if _ssshare._IsSubsysMsgDisabled():
            return None

        if typeID_ is None:
            typeID_ = _EMessageType.eTIntraProcess
        if channelID_ is None:
            channelID_ = _EMessageChannel.eChInterTask
        if clusterID_ is None:
            clusterID_ = _EMessageCluster.eCDontCare
        if labelID_ is None:
            labelID_ = _EMessageLabel.eLDontCare
        if senderID_ is None:
            senderID_ = _EMessagePeer.ePDontCare
        if receiverID_ is None:
            receiverID_ = _EMessagePeer.ePDontCare

        res = _DispatchFilter(typeID_=typeID_, channelID_=channelID_, clusterID_=clusterID_, labelID_=labelID_, senderID_=senderID_, receiverID_=receiverID_, bDefaultFilter_=False)
        if not res.isValid:
            res = None
        return res

    @property
    def isValid(self) -> bool:
        return self.__t is not None

    @property
    def isDefaultDispatchFilter(self) -> bool:
        return self.isValid and self.__bD

    @property
    def isDontCareType(self) -> bool:
        return self.isValid and self.__t.isTDontCare

    @property
    def isDontCareChanel(self) -> bool:
        return self.isValid and self.__ch.isChDontCare

    @property
    def isDontCareCluster(self) -> bool:
        if not self.isValid:
            return False
        res = isinstance(self.__c, _EMessageCluster) and self.__c.isCDontCare
        res = res or isinstance(self.__c, EXmsgPredefinedID) and self.__c==EXmsgPredefinedID.DontCare
        return res

    @property
    def isDontCareLabel(self) -> bool:
        if not self.isValid:
            return False
        res = isinstance(self.__l, _EMessageLabel) and self.__l.isLDontCare
        res = res or isinstance(self.__l, EXmsgPredefinedID) and self.__l==EXmsgPredefinedID.DontCare
        return res

    @property
    def isDontCareSender(self) -> bool:
        if not self.isValid:
            return False
        res = isinstance(self.__s, _EMessagePeer) and self.__s.isPDontCare
        res = res or isinstance(self.__s, EXmsgPredefinedID) and self.__s==EXmsgPredefinedID.DontCare
        return res

    @property
    def isDontCareReceiver(self) -> bool:
        if not self.isValid:
            return False
        res = isinstance(self.__r, _EMessagePeer) and self.__r.isPDontCare
        res = res or isinstance(self.__r, EXmsgPredefinedID) and self.__r==EXmsgPredefinedID.DontCare
        return res

    @property
    def isInternalMessageFilter(self) -> bool:
        return self.isValid and self.__ch.isChIntraTask

    @property
    def isExternalMessageFilter(self) -> bool:
        return self.isValid and self.__ch.isChInterTask

    @property
    def isCustomMessageFilter(self) -> bool:
        return self.isValid and self.__ch.isChCustom

    @property
    def isBroadcastFilter(self) -> bool:
        return self.isValid and isinstance(self.__r, _EMessagePeer) and self.__r.isPBroadcast

    @property
    def isGlobalBroadcastFilter(self) -> bool:
        return self.isValid and isinstance(self.__r, _EMessagePeer) and self.__r.isPGlobalBroadcast

    @property
    def isFwBroadcastFilter(self) -> bool:
        return self.isValid and isinstance(self.__r, _EMessagePeer) and self.__r.isPFwBroadcast

    @property
    def isXTaskBroadcastFilter(self) -> bool:
        return self.isValid and isinstance(self.__r, _EMessagePeer) and self.__r.isPXTaskBroadcast

    @property
    def typeID(self) -> _EMessageType:
        return self.__t

    @property
    def channelID(self) -> _EMessageChannel:
        return self.__ch

    @property
    def clusterID(self) -> Union[_EMessageCluster, IntEnum, int]:
        return self.__c

    @property
    def labelID(self) -> Union[_EMessageLabel, IntEnum, int]:
        return self.__l

    @property
    def senderID(self) -> Union[_EMessagePeer, IntEnum, int]:
        return self.__s

    @property
    def receiverID(self) -> Union[_EMessagePeer, IntEnum, int]:
        return self.__r

    def Clone(self):
        if not self.isValid:
            return None
        res = _DispatchFilter(self.typeID, self.channelID, self.clusterID, self.labelID, self.senderID, self.receiverID)
        if not res.isValid:
            res = None
        return res

    @staticmethod
    def _CreateDefaultDispatchFilter( typeID_     : _EMessageType                            =None
                                    , channelID_  : _EMessageChannel                         =None
                                    , clusterID_  : Union[_EMessageCluster, IntEnum, int] =None
                                    , labelID_    : Union[_EMessageLabel, IntEnum, int]   =None
                                    , senderID_   : Union[_EMessagePeer,  IntEnum, int]   =None
                                    , receiverID_ : Union[_EMessagePeer,  IntEnum, int]   =None):
        if _ssshare._IsSubsysMsgDisabled():
            return None

        if typeID_ is None:
            typeID_ = _EMessageType.eTIntraProcess
        if channelID_ is None:
            channelID_ = _EMessageChannel.eChInterTask
        if clusterID_ is None:
            clusterID_ = _EMessageCluster.eCDontCare
        if labelID_ is None:
            labelID_ = _EMessageLabel.eLDontCare
        if senderID_ is None:
            senderID_ = _EMessagePeer.ePDontCare
        if receiverID_ is None:
            receiverID_ = _EMessagePeer.ePDontCare

        res = _DispatchFilter(typeID_=typeID_, channelID_=channelID_, clusterID_=clusterID_, labelID_=labelID_, senderID_=senderID_, receiverID_=receiverID_, bDefaultFilter_=True)
        if not res.isValid:
            res = None
        return res

    def _ToString(self, bValuesOnly_ =False):
        res = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_026).format( _SubsysMsgUtil.StringizeID(self.clusterID), _SubsysMsgUtil.StringizeID(self.labelID)
                                                                             , _SubsysMsgUtil.StringizeID(self.senderID), _SubsysMsgUtil.StringizeID(self.receiverID))

        if not bValuesOnly_:
            res = _FwTDbEngine.GetText(_EFwTextID.eMessageFilter_ToString_01).format(res)
        return res

    def _CleanUp(self):
        self.__c  = None
        self.__l  = None
        self.__r  = None
        self.__s  = None
        self.__t  = None
        self.__bD = None
        self.__ch = None

    @staticmethod
    def __VerifyFilterParams( typeID_         : _EMessageType
                            , channelID_      : _EMessageChannel
                            , clusterID_      : Union[_EMessageCluster, IntEnum, int]
                            , labelID_        : Union[_EMessageLabel, IntEnum, int]
                            , senderID_       : Union[_EMessagePeer,  IntEnum, int]
                            , receiverID_     : Union[_EMessagePeer,  IntEnum, int]
                            , bDefaultFilter_   =False):
        _err       = _EDFCtorErrID.eNone
        _bParamsOK = True

        if not (isinstance(typeID_, _EMessageType) and typeID_.isTIntraProcess):
            _bParamsOK = False
            _err = _EDFCtorErrID.eBadMsgType
            vlogif._LogNotSupportedEC(_EFwErrorCode.UE_00148, f'[DispFltr] eType: {typeID_}')

        elif not (isinstance(channelID_, _EMessageChannel) and (channelID_.isChInterTask or channelID_.isChIntraTask or channelID_.isChCustom)):
            _bParamsOK = False
            _err = _EDFCtorErrID.eBadMsgChannel
            vlogif._LogNotSupportedEC(_EFwErrorCode.UE_00149, f'[DispFltr] eChannel: {channelID_}')

        elif channelID_.isChIntraTask and receiverID_ != senderID_:
            _bParamsOK = False
            _err = _EDFCtorErrID.eBadInternalMsgFilter
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00522)

        else:
            if _bParamsOK and not _SubsysMsgUtil.IsValidClusterID(clusterID_):                           _bParamsOK = False
            if _bParamsOK and not _SubsysMsgUtil.IsValidLabelID(labelID_, grpIDCalledFor_=clusterID_): _bParamsOK = False
            if _bParamsOK and not _SubsysMsgUtil.IsValidPeerID(senderID_, bSender_=True):            _bParamsOK = False
            if _bParamsOK and not _SubsysMsgUtil.IsValidPeerID(receiverID_):                         _bParamsOK = False

        if not _bParamsOK:
            if not _err.isError:
                _err = _EDFCtorErrID.eInvalidParams
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00523)
            return _err

        _bMsgPeerRcv = isinstance(receiverID_, _EMessagePeer)

        if _bMsgPeerRcv and receiverID_.isPBroadcast:
            if not _FwSubsysCoding.IsNegativeDispatchFiltersEnabled():
                _err = _EDFCtorErrID.eCodingMismatchBroadcastDispatchFilter
                vlogif._LogOEC(False, _EFwErrorCode.VUE_00039)
        elif bDefaultFilter_:
            _bIntRcv      = (not _bMsgPeerRcv) and isinstance(receiverID_, int)
            _bDontcareGrp = isinstance(clusterID_,  _EMessageCluster) and clusterID_.isCDontCare
            _bDontcareLbl = isinstance(labelID_,  _EMessageLabel) and labelID_.isLDontCare
            _bDontcareSnd = isinstance(senderID_, _EMessagePeer)  and senderID_.isPDontCare

            if not (_bDontcareGrp and _bDontcareLbl and _bDontcareSnd and _bIntRcv):
                _err = _EDFCtorErrID.eBadDefaultDispatchFilter
                vlogif._LogOEC(False, _EFwErrorCode.VUE_00040)
        return _err
