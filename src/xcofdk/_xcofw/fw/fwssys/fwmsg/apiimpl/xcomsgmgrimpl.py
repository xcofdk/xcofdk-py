# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xcomsgmgrimpl.py
#
# Copyright(c) 2024 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from threading import RLock as _PyRLock
from typing    import Union as _PyUnion

from xcofdk.fwcom.xmsgdefs import IntEnum
from xcofdk.fwcom.xmsgdefs import EPreDefinedMessagingID

from xcofdk.fwapi.xtask.xtask     import XTask
from xcofdk.fwapi.xmsg.xpayloadif import XPayloadIF
from xcofdk.fwapi.xmsg            import XPayload

from xcofdk._xcofw.fw.fwssys.fwcore.logging                 import logif
from xcofdk._xcofw.fw.fwssys.fwcore.apiimpl.fwapiconnap     import _FwApiConnectorAP
from xcofdk._xcofw.fw.fwssys.fwcore.apiimpl.fwapiimplshare  import _FwApiImplShare
from xcofdk._xcofw.fw.fwssys.fwcore.apiimpl.xtask.xtaskbase import _XTaskBase
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil        import _TaskUtil
from xcofdk._xcofw.fw.fwssys.fwcore.types.serdes            import SerDes

from xcofdk._xcofw.fw.fwssys.fwmsg.apiimpl.xcomsghdrimpl    import _XMsgHeaderImpl
from xcofdk._xcofw.fw.fwssys.fwmsg.apiimpl.xcomsgimpl       import _XMsgImpl
from xcofdk._xcofw.fw.fwssys.fwmsg.msg                      import _SubsysMsgUtil
from xcofdk._xcofw.fw.fwssys.fwmsg.msg.fwmessage            import _FwMessage
from xcofdk._xcofw.fw.fwssys.fwmsg.disp.dispatchregistry    import _MessageClusterMap

from xcofdk._xcofw.fw.fwssys.fwerrh.fwerrorcodes import _EFwErrorCode

from xcofdk._xcofwa.fwadmindefs import _FwSubsystemCoding

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine

class _XMsgMgrImpl:

    __slots__ = []

    __FWD    = None
    __mtxApi = _PyRLock()

    def __init__(self):
        pass

    @staticmethod
    def _SerializeXcoMsg(msgObj_) -> bytes:
        if not isinstance(msgObj_, _XMsgImpl):
            return None
        return SerDes.SerializeObject(msgObj_, bTreatAsUserError_=True)

    @staticmethod
    def _DeserializeXcoMsg(bytes_ : bytes):
        if not isinstance(bytes_, bytes):
            return None

        res = SerDes.DeserializeData(bytes_, bTreatAsUserError_=True)
        if not isinstance(res, _XMsgImpl):
            logif._LogFatalEC(_EFwErrorCode.FE_00049, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TextID_025).format(str(res)))
            res = None
        return res

    @staticmethod
    def _SendXMsg( rcvID_   : _PyUnion[XTask, IntEnum, int]
                 , lblID_   : _PyUnion[IntEnum, int]        =EPreDefinedMessagingID.DontCare
                 , clrID_   : _PyUnion[IntEnum, int]        =EPreDefinedMessagingID.DontCare
                 , payload_ : _PyUnion[XPayloadIF, dict]    =None) -> int:
        if isinstance(rcvID_, EPreDefinedMessagingID) and rcvID_==EPreDefinedMessagingID.Broadcast:
            return _XMsgMgrImpl._BroadcastXMsg(lblID_, clrID_, payload_)

        res    = 0
        _msg   = None
        _sndXT = None
        _msg, _sndXT = _XMsgMgrImpl.__ProcSendRequest(lblID_, clrID_, rcvID_, payload_=payload_, bInternal_=False, bBroadcast_=False)
        if _msg is None:
            pass
        else:
            res = _msg.uniqueID
            if not _XTaskBase._SendXMsg(_sndXT, _msg):
                res = 0
                if _sndXT.currentError is None:
                    logif._XLogErrorEC(_EFwErrorCode.UE_00192, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TextID_034).format(_msg.header))
            _msg.CleanUp()
        return res

    @staticmethod
    def _BroadcastXMsg( lblID_   : _PyUnion[IntEnum, int]
                      , clrID_   : _PyUnion[IntEnum, int]     =EPreDefinedMessagingID.DontCare
                      , payload_ : _PyUnion[XPayloadIF, dict] =None) -> int:
        res    = 0
        _msg   = None
        _sndXT = None
        _msg, _sndXT = _XMsgMgrImpl.__ProcSendRequest(lblID_, clrID_, 0, payload_=payload_, bInternal_=False, bBroadcast_=True)
        if _msg is None:
            pass
        else:
            res = _msg.uniqueID
            if not _XTaskBase._SendXMsg(_sndXT, _msg):
                res = 0
                if _sndXT.currentError is None:
                    logif._XLogErrorEC(_EFwErrorCode.UE_00193, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TextID_035).format(_msg.header))
            _msg.CleanUp()

        return res

    @staticmethod
    def __GetNextUniqueNr():
        return _FwMessage._GetNextUniqueNr()

    @staticmethod
    def __ProcSendRequest( lblID_      : _PyUnion[IntEnum, int]        =EPreDefinedMessagingID.DontCare
                         , clrID_      : _PyUnion[IntEnum, int]        =EPreDefinedMessagingID.DontCare
                         , rcvID_      : _PyUnion[XTask, IntEnum, int] =0
                         , payload_    : _PyUnion[XPayloadIF, dict]  =None
                         , bInternal_                                  =False
                         , bBroadcast_                                 =False):
        _failedTuple = None, None

        if not _FwApiConnectorAP._APIsFwApiConnected():
            return _failedTuple
        if not _FwSubsystemCoding.IsSubsystemMessagingConfigured():
            return _failedTuple
        if not _FwSubsystemCoding.IsInternalQueueSupportEnabled():
            if bInternal_:
                return _failedTuple

        _midPart = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TextID_013)

        _rcvXT = None
        _sndXT = _FwApiConnectorAP._APGetCurXTask()
        if _sndXT is None:
            logif._XLogErrorEC(_EFwErrorCode.UE_00194, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TextID_014).format(_midPart))
            return _failedTuple

        _sndID = _sndXT.xtaskUniqueID
        _rcvID = rcvID_

        _bPreDefRcv   = isinstance(_rcvID, EPreDefinedMessagingID)
        _bDontCareRcv = _bPreDefRcv and _rcvID == EPreDefinedMessagingID.DontCare
        _bDontCareLbl = isinstance(lblID_, EPreDefinedMessagingID) and lblID_ == EPreDefinedMessagingID.DontCare
        _bDontCareClr = isinstance(clrID_, EPreDefinedMessagingID) and clrID_ == EPreDefinedMessagingID.DontCare

        if _bDontCareRcv:
            if not _FwSubsystemCoding.IsAnonymousAddressingEnabled():
                logif._XLogErrorEC(_EFwErrorCode.UE_00195, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TextID_028).format(_midPart, _SubsysMsgUtil.StringizeID(_rcvID)))
                return _failedTuple

            if _bDontCareLbl and _bDontCareClr:
                logif._XLogErrorEC(_EFwErrorCode.UE_00196, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TextID_029).format(_midPart, _SubsysMsgUtil.StringizeID(lblID_), _SubsysMsgUtil.StringizeID(clrID_), EPreDefinedMessagingID.MinUserDefinedID.value))
                return _failedTuple

        if not (bInternal_ or bBroadcast_):
            if isinstance(_rcvID, IntEnum):
                if _bPreDefRcv and (_rcvID == EPreDefinedMessagingID.MainTask):
                    _rcvID = _FwApiImplShare._GetMainXTask()
                    if _rcvID is None:
                        logif._XLogErrorEC(_EFwErrorCode.UE_00197, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TextID_032).format(_midPart))
                        return _failedTuple
                else:
                    _rcvID = _rcvID.value

        _bIntRcv   = isinstance(_rcvID, int)
        _bXTaskRcv = isinstance(_rcvID, XTask)

        if _bXTaskRcv:
            if _rcvID.isDetachedFromFW or (_rcvID.xtaskUniqueID is None):
                logif._XLogErrorEC(_EFwErrorCode.UE_00198, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TextID_019).format(_midPart, rcvID_))
                return _failedTuple
            _rcvXT = _rcvID
            _rcvID = _rcvID.xtaskUniqueID
        elif not _bIntRcv:
            logif._XLogErrorEC(_EFwErrorCode.UE_00199, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TextID_016).format(_midPart, type(rcvID_).__name__))
            return _failedTuple
        elif _rcvID == 0:
            _rcvID = _sndID

        if (_rcvID==_sndID) and not (bInternal_ or bBroadcast_):
            if not _FwSubsystemCoding.IsSelfExternalMessagingEnabled():
                logif._XLogErrorEC(_EFwErrorCode.UE_00200, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TextID_031).format(_midPart, _sndID))
                return _failedTuple

        if bInternal_:
            if not _sndXT.xtaskProfile.isInternalQueueEnabled:
                logif._XLogErrorEC(_EFwErrorCode.UE_00201, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TextID_015).format(_midPart, _sndID))
                return _failedTuple
            _rcvID = _sndID
            _rcvXT = _sndXT

        elif bBroadcast_:
            _rcvID = EPreDefinedMessagingID.Broadcast

        else:
            if _bDontCareRcv:
                pass

            else:
                if _bXTaskRcv:
                    pass
                else:
                    if not _TaskUtil.IsValidUserTaskID(_rcvID):
                        logif._XLogErrorEC(_EFwErrorCode.UE_00202, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TextID_017).format(_midPart, rcvID_))
                        return _failedTuple
                    _rcvXT = _FwApiConnectorAP._APGetXTask(_rcvID)

                if _rcvXT is None:
                    logif._XLogErrorEC(_EFwErrorCode.UE_00203, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TextID_018).format(_midPart, rcvID_))
                    return _failedTuple
                if _rcvXT.isDetachedFromFW:
                    logif._XLogErrorEC(_EFwErrorCode.UE_00204, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TextID_019).format(_midPart, rcvID_))
                    return _failedTuple
                if not (_rcvXT.isRunning or _rcvXT.isStopping):
                    logif._XLogErrorEC(_EFwErrorCode.UE_00205, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TextID_020).format(_midPart, rcvID_))
                    return _failedTuple
                if not _rcvXT.xtaskProfile.isExternalQueueEnabled:
                    logif._XLogErrorEC(_EFwErrorCode.UE_00206, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TextID_021).format(_midPart, rcvID_))
                    return _failedTuple

                _rcvID = _rcvXT.xtaskUniqueID

        _arg1 = _SubsysMsgUtil.StringizeID(lblID_)
        _arg2 = _SubsysMsgUtil.StringizeID(clrID_)
        _arg3 = _SubsysMsgUtil.StringizeID(_sndID)
        _arg4 = _SubsysMsgUtil.StringizeID(_rcvID)
        if not _XMsgMgrImpl.__CheckSendRequest(lblID_, clrID_, _bDontCareLbl, _bDontCareClr, bBroadcast_=bBroadcast_):
            if bBroadcast_:
                logif._XLogErrorEC(_EFwErrorCode.UE_00207, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TextID_027).format(_midPart, _arg1, _arg2, _arg3, _arg4, EPreDefinedMessagingID.MinUserDefinedID.value))
            else:
                logif._XLogErrorEC(_EFwErrorCode.UE_00208, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TextID_022).format(_midPart, _arg1, _arg2, _arg3, _arg4, EPreDefinedMessagingID.MinUserDefinedID.value))
            return _failedTuple

        _pld = payload_
        if _pld is not None:
            if not isinstance(_pld, (XPayload, dict)):
                if not isinstance(_pld, XPayloadIF):
                    logif._XLogErrorEC(_EFwErrorCode.UE_00155, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TextID_023).format(_midPart, XPayloadIF.__name__, dict.__name__, type(payload_).__name__, _arg1, _arg2, _arg3, _arg4, EPreDefinedMessagingID.MinUserDefinedID.value))
                    return _failedTuple

                if _pld.isCustomMarshalingRequired:
                    if not _FwSubsystemCoding.IsCustomPayloadSerDesEnabled():
                        logif._XLogErrorEC(_EFwErrorCode.UE_00156, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TextID_033).format(_midPart))
                        return _failedTuple

                _bCustomPLD = True
            elif isinstance(_pld, XPayload):
                if not _pld.isValidPayload:
                    logif._XLogErrorEC(_EFwErrorCode.UE_00157, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TextID_026).format(_midPart, _arg1, _arg2, _arg3, _arg4, EPreDefinedMessagingID.MinUserDefinedID.value))
                    return _failedTuple
                if _pld.numParameters < 1:
                    _pld = None
                    logif._XLogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TextID_024).format(_midPart, _arg1, _arg2, _arg3, _arg4, EPreDefinedMessagingID.MinUserDefinedID.value))
            elif len(_pld) < 1:
                _pld = None
                logif._XLogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TextID_024).format(_midPart, _arg1, _arg2, _arg3, _arg4, EPreDefinedMessagingID.MinUserDefinedID.value))
            else:
                _pld = XPayload(containerInitializer_=payload_)
                if not (_pld.isValidPayload and _pld.numParameters==len(payload_)):
                    _pld.DetachContainer()
                    logif._XLogErrorEC(_EFwErrorCode.UE_00158, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TextID_030).format(_midPart, XPayload.__name__, len(payload_), _arg1, _arg2, _arg3, _arg4, EPreDefinedMessagingID.MinUserDefinedID.value))
                    return _failedTuple

        _hdr = _XMsgHeaderImpl(clrID_, lblID_, _rcvID, _sndID, bInternal_=bInternal_)
        if not _hdr.isValid:
            if (_pld is not None) and not isinstance(payload_, XPayloadIF):
                _pld.DetachContainer()
            _hdr.CleanUp()
            return _failedTuple
        res = _XMsgImpl(uid_=_XMsgMgrImpl.__GetNextUniqueNr(), header_=_hdr, payld_=_pld)
        if not res.isValid:
            if (_pld is not None) and not isinstance(payload_, XPayloadIF):
                _pld.DetachContainer()
            _hdr.CleanUp()
            res.CleanUp()
            return _failedTuple
        return res, _sndXT

    @staticmethod
    def __CheckSendRequest( lblID_  : _PyUnion[IntEnum, int], clrID_  : _PyUnion[IntEnum, int], bDontCareLbl_, bDontCareClr_, bBroadcast_ =False):
        _MIN_VAL = EPreDefinedMessagingID.MinUserDefinedID.value

        if bDontCareLbl_:
            if bBroadcast_:
                return False
            elif bDontCareClr_:
                return True

        _valLbl = lblID_
        _valGrp = clrID_

        _bInt  = isinstance(lblID_, int)
        _bEnum = isinstance(lblID_, IntEnum)
        if not (_bEnum or _bInt):
            return False
        elif not _bEnum:
            if lblID_ < _MIN_VAL:
                return False
        elif not bDontCareLbl_:
            _valLbl = lblID_.value
            if _valLbl < _MIN_VAL:
                return False

        _bInt  = isinstance(clrID_, int)
        _bEnum = isinstance(clrID_, IntEnum)
        if not (_bEnum or _bInt):
            return False
        elif not _bEnum:
            if clrID_ < _MIN_VAL:
                return False
        elif not bDontCareClr_:
            _valGrp = clrID_.value
            if _valGrp < _MIN_VAL:
                return False

        if not (bDontCareLbl_ or bDontCareClr_):
            with _XMsgMgrImpl.__mtxApi:
                if not _MessageClusterMap.IsClusterMember(_valGrp, _valLbl):
                    if _FwSubsystemCoding.IsAutoCreateClusterEnabled():
                        if not _MessageClusterMap.UpdateCluster(_valGrp, _valLbl):
                            return False
        return True

