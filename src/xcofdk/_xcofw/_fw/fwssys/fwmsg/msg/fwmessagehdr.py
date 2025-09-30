# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwmessagehdr.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum   import auto
from enum   import IntEnum
from enum   import unique
from typing import Union

from _fw.fwssys.fwcore.logging           import vlogif
from _fw.fwssys.fwcore.logging           import logif
from _fw.fwssys.fwcore.ipc.tsk.taskmgr   import _TaskMgr
from _fw.fwssys.fwcore.types.ebitmask    import _EBitMask
from _fw.fwssys.fwcore.types.commontypes import _FwIntFlag
from _fw.fwssys.fwmsg.msg                import _EMessagePeer
from _fw.fwssys.fwmsg.msg                import _EMessageType
from _fw.fwssys.fwmsg.msg                import _EMessageCluster
from _fw.fwssys.fwmsg.msg                import _EMessageLabel
from _fw.fwssys.fwmsg.msg                import _EMessageChannel
from _fw.fwssys.fwmsg.msg                import _SubsysMsgUtil
from _fw.fwssys.fwmsg.msg                import _IFwMessageHeader
from _fw.fwssys.fwerrh.fwerrorcodes      import _EFwErrorCode
from _fwa.fwsubsyscoding                 import _FwSubsysCoding

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

@unique
class _EMsgHeaderCtorErrorID(IntEnum):
    eNone                                       = 0
    eInvalidMsgID                               = auto()
    eBadMsgType                                 = auto()
    eBadMsgChannel                              = auto()
    eBroadcastAsSender                          = auto()
    eDifferentPeersForInternalMsg               = auto()
    eFetchingTaskMgr                            = auto()
    eFetchingCurTaskBadge                       = auto()
    eFetchingSenderTaskBadge                    = auto()
    eFetchingReceiverTaskBadge                  = auto()
    eMissingSpecificLabelForUnspecifiedReceiver = auto()
    eSenderMissingExtQueueSupport               = auto()
    eSenderMissingIntQueueSupport               = auto()
    eReceiverMissingExtQueueSupport             = auto()
    eReceiverMissingForDirectAddressing         = auto()

    @property
    def isError(self):
        return self != _EMsgHeaderCtorErrorID.eNone

    @property
    def isIgnorableError(self):
        return self.isFetchingTaskMgr or self.isFetchingCurTaskBadge

    @property
    def isInvalidMsgID(self):
        return self == _EMsgHeaderCtorErrorID.eInvalidMsgID

    @property
    def isBadMsgType(self):
        return self == _EMsgHeaderCtorErrorID.eBadMsgType

    @property
    def isBadMsgChannel(self):
        return self == _EMsgHeaderCtorErrorID.eBadMsgChannel

    @property
    def isBroadcastAsSender(self):
        return self == _EMsgHeaderCtorErrorID.eBroadcastAsSender

    @property
    def isDifferentPeersForInternalMsg(self):
        return self == _EMsgHeaderCtorErrorID.eDifferentPeersForInternalMsg

    @property
    def isFetchingTaskMgr(self):
        return self == _EMsgHeaderCtorErrorID.eFetchingTaskMgr

    @property
    def isFetchingCurTaskBadge(self):
        return self == _EMsgHeaderCtorErrorID.eFetchingCurTaskBadge

    @property
    def isFetchingSenderTaskBadge(self):
        return self == _EMsgHeaderCtorErrorID.eFetchingSenderTaskBadge

    @property
    def isFetchingReceiverTaskBadge(self):
        return self == _EMsgHeaderCtorErrorID.eFetchingReceiverTaskBadge

    @property
    def isMissingSpecificLabelForUnspecifiedReceiver(self):
        return self == _EMsgHeaderCtorErrorID.eMissingSpecificLabelForUnspecifiedReceiver

    @property
    def isSenderMissingExtQueueSupport(self):
        return self == _EMsgHeaderCtorErrorID.eSenderMissingExtQueueSupport

    @property
    def isSenderMissingIntQueueSupport(self):
        return self == _EMsgHeaderCtorErrorID.eSenderMissingIntQueueSupport

    @property
    def isReceiverMissingExtQueueSupport(self):
        return self == _EMsgHeaderCtorErrorID.eReceiverMissingExtQueueSupport

    @property
    def isReceiverMissingForDirectAddressing(self):
        return self == _EMsgHeaderCtorErrorID.eReceiverMissingForDirectAddressing

class _FwMessageHeader(_IFwMessageHeader):
    @unique
    class _EFwMsgFlag(_FwIntFlag):
        ebfNone            = 0x0000
        ebfGlobalBroadcast = (0x0001 << 0)
        ebfFwBroadcast     = (0x0001 << 1)
        ebfXTaskBroadcast  = (0x0001 << 2)

        @property
        def compactName(self) -> str:
            return self.name[3:]

        @staticmethod
        def IsNone(eFwMsgBitMask_: _FwIntFlag):
            return eFwMsgBitMask_ == _FwMessageHeader._EFwMsgFlag.ebfNone

        @staticmethod
        def IsBroadcast(eFwMsgBitMask_: _FwIntFlag):
            _lstbf = [ _FwMessageHeader._EFwMsgFlag.ebfFwBroadcast
                     , _FwMessageHeader._EFwMsgFlag.ebfXTaskBroadcast
                     , _FwMessageHeader._EFwMsgFlag.ebfGlobalBroadcast ]
            return _EBitMask.IsAnyEnumBitFlagSet(eFwMsgBitMask_, _lstbf, bCheckTypeMatch_=False)

        @staticmethod
        def IsGlobalBroadcast(eFwMsgBitMask_: _FwIntFlag):
            return _EBitMask.IsEnumBitFlagSet(eFwMsgBitMask_, _FwMessageHeader._EFwMsgFlag.ebfGlobalBroadcast)

        @staticmethod
        def IsFwBroadcast(eFwMsgBitMask_: _FwIntFlag):
            return _EBitMask.IsEnumBitFlagSet(eFwMsgBitMask_, _FwMessageHeader._EFwMsgFlag.ebfFwBroadcast)

        @staticmethod
        def IsXTaskBroadcast(eFwMsgBitMask_: _FwIntFlag):
            return _EBitMask.IsEnumBitFlagSet(eFwMsgBitMask_, _FwMessageHeader._EFwMsgFlag.ebfXTaskBroadcast)

        @staticmethod
        def AddFwMsgBitFlag(eFwMsgBitMask_: _FwIntFlag, eFwMsgBitFlag_):
            return _EBitMask.AddEnumBitFlag(eFwMsgBitMask_, eFwMsgBitFlag_)

        @staticmethod
        def IsFwMsgBitFlagSet(eFwMsgBitMask_: _FwIntFlag, eFwMsgBitFlag_):
            return _EBitMask.IsEnumBitFlagSet(eFwMsgBitMask_, eFwMsgBitFlag_)

    __slots__ = [ '__c' , '__l' , '__s' , '__t' , '__ch' , '__r' , '__bm' ]

    def __init__( self
                , typeID_     : _EMessageType
                , channelID_  : _EMessageChannel
                , clusterID_  : Union[_EMessageCluster, IntEnum, int]
                , labelID_    : Union[_EMessageLabel, IntEnum, int]
                , senderID_   : Union[_EMessagePeer,  IntEnum, int]
                , receiverID_ : Union[_EMessagePeer,  IntEnum, int]
                , bSkipCheck_   =False):
        super().__init__()

        self.__c  = None
        self.__l  = None
        self.__r  = None
        self.__s  = None
        self.__t  = None
        self.__bm = None
        self.__ch = None

        _bm    = _FwMessageHeader._EFwMsgFlag.ebfNone
        _sndID = senderID_
        _rcvID = receiverID_

        if bSkipCheck_:
            pass
        else:
            _err = _EMsgHeaderCtorErrorID.eNone
            _err, _sndID, _rcvID, _bm = _FwMessageHeader.__VerifyHeaderParams(typeID_, channelID_, clusterID_, labelID_, senderID_, receiverID_)

            if _err.isError:
                self.CleanUp()

                if _err.isIgnorableError:
                    return

                _midPart = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_MessageHeader_TID_001).format(_err.value)

                _bFatal = False
                if _err.isBadMsgType or _err.isBadMsgChannel:
                    _bFatal = True
                    _myMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_MessageHeader_TID_002).format(_midPart, typeID_.value, channelID_.value)

                elif _err.isInvalidMsgID:
                    _myMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_MessageHeader_TID_003).format(_midPart, typeID_.value, channelID_.value
                                                                                                     , _SubsysMsgUtil.StringizeID(clusterID_), _SubsysMsgUtil.StringizeID(labelID_)
                                                                                                     , _SubsysMsgUtil.StringizeID(_sndID), _SubsysMsgUtil.StringizeID(_rcvID))
                elif _err.isBroadcastAsSender:
                    _myMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_MessageHeader_TID_004).format(_midPart, _SubsysMsgUtil.StringizeID(_sndID))
                elif _err.isDifferentPeersForInternalMsg:
                    _myMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_MessageHeader_TID_005).format(_midPart, _SubsysMsgUtil.StringizeID(_sndID), _SubsysMsgUtil.StringizeID(_rcvID))
                elif _err.isFetchingSenderTaskBadge:
                    _myMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_MessageHeader_TID_007).format(_midPart, _SubsysMsgUtil.StringizeID(_sndID))
                elif _err.isFetchingReceiverTaskBadge:
                    _myMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_MessageHeader_TID_008).format(_midPart, _SubsysMsgUtil.StringizeID(_rcvID))
                elif _err.isMissingSpecificLabelForUnspecifiedReceiver:
                    _myMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_MessageHeader_TID_009).format(_midPart, _SubsysMsgUtil.StringizeID(_rcvID))
                elif _err.isSenderMissingExtQueueSupport:
                    _myMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_MessageHeader_TID_010).format(_midPart, _SubsysMsgUtil.StringizeID(_sndID))
                elif _err.isSenderMissingIntQueueSupport:
                    _myMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_MessageHeader_TID_011).format(_midPart, _SubsysMsgUtil.StringizeID(_sndID))
                elif _err.isReceiverMissingExtQueueSupport:
                    _myMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_MessageHeader_TID_012).format(_midPart, _SubsysMsgUtil.StringizeID(_rcvID))
                elif _err.isReceiverMissingForDirectAddressing:
                    _myMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_MessageHeader_TID_006).format(_midPart, _SubsysMsgUtil.StringizeID(_rcvID))
                else:
                    _bFatal = True
                    _myMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_MessageHeader_TID_014).format(_midPart, _err.value)

                if _bFatal:
                    logif._LogFatalEC(_EFwErrorCode.FE_00050, _myMsg)
                else:
                    logif._LogErrorEC(_EFwErrorCode.UE_00135, _myMsg)
                return

        self.__c  = clusterID_
        self.__l  = labelID_
        self.__r  = _rcvID
        self.__s  = _sndID
        self.__t  = typeID_
        self.__bm = _bm
        self.__ch = channelID_

    def __eq__(self, other_):
        res = (self.__bm is not None) and isinstance(other_, _FwMessageHeader) and other_.isValid
        res = res and self.__bm == other_.__bm
        res = res and self.__t  == other_.__t
        res = res and self.__c  == other_.__c
        res = res and self.__l  == other_.__l
        res = res and self.__s  == other_.__s
        res = res and self.__ch == other_.__ch
        res = res and self.__r  == other_.__r
        return res

    def __ne__(self, other_):
        return not self.__eq__(other_)

    def __hash__(self):
        if not self.isValid:
            return None
        return hash(hash(self.__bm)+hash(self.__t)+hash(self.__c)+hash(self.__l)+hash(self.__s)+hash(self.__ch)+hash(self.__r))

    @property
    def isValid(self) -> bool:
        return self.__bm is not None

    @property
    def isXcoMsgHeader(self) -> bool:
        return False

    @property
    def isFwMsgHeader(self) -> bool:
        return True

    @property
    def isInternalMsg(self) -> bool:
        return self.isValid and self.__ch.isChIntraTask

    @property
    def isBroadcastMsg(self) -> bool:
        return self.isValid and _FwMessageHeader._EFwMsgFlag.IsBroadcast(self.__bm)

    @property
    def isGlobalBroadcastMsg(self) -> bool:
        return self.isValid and _FwMessageHeader._EFwMsgFlag.IsGlobalBroadcast(self.__bm)

    @property
    def isFwBroadcastMsg(self) -> bool:
        return self.isValid and _FwMessageHeader._EFwMsgFlag.IsFwBroadcast(self.__bm)

    @property
    def isXTaskBroadcastMsg(self) -> bool:
        return self.isValid and _FwMessageHeader._EFwMsgFlag.IsXTaskBroadcast(self.__bm)

    @property
    def typeID(self) -> _EMessageType:
        return self.__t

    @property
    def channelID(self) -> _EMessageChannel:
        return self.__ch

    @property
    def clusterID(self) -> _EMessageCluster:
        return self.__c

    @property
    def labelID(self) -> _EMessageLabel:
        return self.__l

    @property
    def senderID(self) -> _EMessagePeer:
        return self.__s

    @property
    def receiverID(self) -> _EMessagePeer:
        return self.__r

    def Clone(self):
        if not self.isValid:
            return None
        res = _FwMessageHeader(self.typeID, self.channelID, self.clusterID, self.labelID, self.senderID, self.receiverID)
        if not res.isValid:
            res.CleanUp()
            res = None
        return res

    def _ToString(self, bValuesOnly_ =False):
        res = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_024).format( self.typeID, self.channelID, _SubsysMsgUtil.StringizeID(self.clusterID), _SubsysMsgUtil.StringizeID(self.labelID)
                                                                             , _SubsysMsgUtil.StringizeID(self.senderID), _SubsysMsgUtil.StringizeID(self.receiverID))
        if not bValuesOnly_:
            res = _FwTDbEngine.GetText(_EFwTextID.eMessageHeader_ToString_01).format(res)
        return res

    def _CleanUp(self):
        self.__c  = None
        self.__l  = None
        self.__r  = None
        self.__s  = None
        self.__t  = None
        self.__bm = None
        self.__ch = None
        super()._CleanUp()

    @staticmethod
    def __VerifyHeaderParams( typeID_     : _EMessageType
                            , channelID_  : _EMessageChannel
                            , clusterID_  : Union[_EMessageCluster, IntEnum, int]
                            , labelID_    : Union[_EMessageLabel, IntEnum, int]
                            , senderID_   : Union[_EMessagePeer,  IntEnum, int]
                            , receiverID_ : Union[_EMessagePeer,  IntEnum, int] ) -> (_EMsgHeaderCtorErrorID, Union[_EMessagePeer, IntEnum, int], Union[_EMessagePeer, IntEnum, int], _FwIntFlag):
        _err            = _EMsgHeaderCtorErrorID.eNone
        _bParamsOK      = True
        _bBadUseLogDone = False

        _bm    = _FwMessageHeader._EFwMsgFlag.ebfNone
        _sndID = senderID_
        _rcvID = receiverID_

        if not (isinstance(typeID_, _EMessageType) and typeID_.isTIntraProcess):
            _bParamsOK = False
            _err = _EMsgHeaderCtorErrorID.eBadMsgType
            vlogif._LogNotSupportedEC(_EFwErrorCode.UE_00002, f'[MsgHdr] eType: {typeID_}')

        elif not (isinstance(channelID_, _EMessageChannel) and (channelID_.isChInterTask or channelID_.isChIntraTask or channelID_.isChCustom)):
            _bParamsOK = False
            _err = _EMsgHeaderCtorErrorID.eBadMsgChannel
            vlogif._LogNotSupportedEC(_EFwErrorCode.UE_00003, f'[MsgHdr] eChannel: {channelID_}')

        else:
            if _bParamsOK and not _SubsysMsgUtil.IsValidClusterID(clusterID_):                         _bParamsOK = False
            if _bParamsOK and not _SubsysMsgUtil.IsValidLabelID(labelID_, grpIDCalledFor_=clusterID_): _bParamsOK = False
            if _bParamsOK and not _SubsysMsgUtil.IsValidPeerID(senderID_, bSender_=True):              _bParamsOK = False
            if _bParamsOK and not _SubsysMsgUtil.IsValidPeerID(receiverID_):                           _bParamsOK = False

        if not _bParamsOK:
            if not _err.isError:
                _err = _EMsgHeaderCtorErrorID.eInvalidMsgID
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00542)
            return _err, _sndID, _rcvID, _bm

        _bIntMsg          = channelID_.isChIntraTask
        _bEMessageLabel   = isinstance(labelID_    , _EMessageLabel)
        _bEMessagePeerSnd = isinstance(senderID_   , _EMessagePeer)
        _bEMessagePeerRcv = isinstance(receiverID_ , _EMessagePeer)

        if _bEMessagePeerSnd and senderID_.isPBroadcast:
            _bBadUseLogDone = True
            _err = _EMsgHeaderCtorErrorID.eBroadcastAsSender
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00543)

        elif receiverID_!=senderID_ and _bIntMsg:
            _bBadUseLogDone = True
            _err = _EMsgHeaderCtorErrorID.eDifferentPeersForInternalMsg
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00544)

        if _err.isError:
            if not _bBadUseLogDone:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00545)
            return _err, _sndID, _rcvID, _bm

        _err = None

        _tmgr = _TaskMgr()
        if _tmgr is None:
            return _EMsgHeaderCtorErrorID.eFetchingTaskMgr, _sndID, _rcvID, _bm

        _tbadgeCur = _tmgr.GetCurTaskBadge()
        if (_tbadgeCur is None) or not _tbadgeCur.isValid:
            return _EMsgHeaderCtorErrorID.eFetchingCurTaskBadge, _sndID, _rcvID, _bm

        if _bEMessagePeerSnd:
            if senderID_.isPDontCare:
                _sndID     = _tbadgeCur.dtaskUID
                _tbadgeSnd = _tbadgeCur
            else:
                _tbadgeSnd = _tmgr.GetTaskBadge(senderID_, bDoWarn_=False)
                if (_tbadgeSnd is None) or not _tbadgeSnd.isValid:
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00546)
                    return _EMsgHeaderCtorErrorID.eFetchingSenderTaskBadge, _sndID, _rcvID, _bm

                _sndID = _tbadgeSnd.dtaskUID

        else:
            if isinstance(senderID_, IntEnum):
                _sndID = senderID_.value

            _tbadgeSnd = _tmgr.GetTaskBadge(_sndID, bDoWarn_=False)
            if (_tbadgeSnd is None) or not _tbadgeSnd.isValid:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00547)
                return _EMsgHeaderCtorErrorID.eFetchingSenderTaskBadge, _sndID, _rcvID, _bm

        if _bIntMsg:
            if not _tbadgeSnd.isSupportingInternalQueue:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00548)
                return _EMsgHeaderCtorErrorID.eSenderMissingIntQueueSupport, _sndID, _rcvID, _bm
            else:
                _rcvID = _sndID

        elif not _tbadgeSnd.isSupportingExternalQueue:
            if _FwSubsysCoding.IsSenderExternalQueueSupportMandatory():
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00549)
                return _EMsgHeaderCtorErrorID.eSenderMissingExtQueueSupport, _sndID, _rcvID, _bm

        _tbadgeRcv = None

        if _bIntMsg:
            _tbadgeRcv = _tbadgeSnd

        elif _bEMessagePeerRcv:
            if receiverID_.isPDontCare:
                if not _FwSubsysCoding.IsAnonymousAddressingEnabled():
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00550)
                    return _EMsgHeaderCtorErrorID.eReceiverMissingForDirectAddressing, _sndID, _rcvID, _bm

            elif receiverID_.isPBroadcast:
                if _bEMessageLabel and labelID_.isLDontCare:
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00551)
                    return _EMsgHeaderCtorErrorID.eMissingSpecificLabelForUnspecifiedReceiver, _sndID, _rcvID, _bm

                if receiverID_.isPGlobalBroadcast:
                    _bm = _FwMessageHeader._EFwMsgFlag.AddFwMsgBitFlag(_bm, _FwMessageHeader._EFwMsgFlag.ebfGlobalBroadcast)
                elif receiverID_.isPGlobalBroadcast:
                    _bm = _FwMessageHeader._EFwMsgFlag.AddFwMsgBitFlag(_bm, _FwMessageHeader._EFwMsgFlag.ebfFwBroadcast)
                else:
                    _bm = _FwMessageHeader._EFwMsgFlag.AddFwMsgBitFlag(_bm, _FwMessageHeader._EFwMsgFlag.ebfXTaskBroadcast)
            else:
                _tbadgeRcv = _tmgr.GetTaskBadge(receiverID_, bDoWarn_=False)
                if (_tbadgeRcv is None) or not _tbadgeRcv.isValid:
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00552)
                    return _EMsgHeaderCtorErrorID.eFetchingReceiverTaskBadge, _sndID, _rcvID, _bm

                _rcvID = _tbadgeRcv.dtaskUID
        else:
            if isinstance(receiverID_, IntEnum):
                _rcvID = receiverID_.value

            _tbadgeRcv = _tmgr.GetTaskBadge(_rcvID, bDoWarn_=False)
            if (_tbadgeRcv is None) or not _tbadgeRcv.isValid:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00553)
                return _EMsgHeaderCtorErrorID.eFetchingReceiverTaskBadge, _sndID, _rcvID, _bm

        if _tbadgeRcv is None:
            pass
        elif _bIntMsg:
            pass
        elif not _tbadgeRcv.isSupportingExternalQueue:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00554)
            return _EMsgHeaderCtorErrorID.eReceiverMissingExtQueueSupport, _sndID, _rcvID, _bm
        return _EMsgHeaderCtorErrorID.eNone, _sndID, _rcvID, _bm
