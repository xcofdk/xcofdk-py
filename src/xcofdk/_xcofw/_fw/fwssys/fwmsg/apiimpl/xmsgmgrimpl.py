# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xmsgmgrimpl.py
#
# Copyright(c) 2024-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum      import IntEnum
from threading import RLock as _PyRLock
from typing    import Union

from xcofdk.fwcom      import EXmsgPredefinedID
from xcofdk.fwapi      import IPayload
from xcofdk.fwapi      import IRCTask
from xcofdk.fwapi.xmsg import XPayload
from xcofdk.fwapi.xmt  import IXTask

from _fw.fwssys.assys                     import fwsubsysshare as _ssshare
from _fw.fwssys.assys.fwsubsysshare       import _FwSubsysShare
from _fw.fwssys.fwcore.logging            import logif
from _fw.fwssys.fwctrl.fwapiconnap        import _FwApiConnectorAP
from _fw.fwssys.fwcore.ipc.tsk.taskutil   import _TaskUtil
from _fw.fwssys.fwmsg.apiimpl.xmsghdrimpl import _XMsgHeaderImpl
from _fw.fwssys.fwmsg.apiimpl.xmsgimpl    import _XMsgImpl
from _fw.fwssys.fwmsg.msg                 import _SubsysMsgUtil
from _fw.fwssys.fwmsg.msg.fwmessage       import _FwMessage
from _fw.fwssys.fwmsg.disp.dispregistry   import _MessageClusterMap
from _fw.fwssys.fwerrh.fwerrorcodes       import _EFwErrorCode
from _fw.fwssys.fwmt.utask.usertask       import _UserTask
from _fwa.fwsubsyscoding                  import _FwSubsysCoding

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _XMsgMgrImpl:
    __slots__ = []

    __ma = _PyRLock()

    def __init__(self):
        pass

    @staticmethod
    def _SendXMsg( rcvID_   : Union[IXTask, IntEnum, int]
                 , lblID_   : Union[IntEnum, int]   =EXmsgPredefinedID.DontCare
                 , clrID_   : Union[IntEnum, int]   =EXmsgPredefinedID.DontCare
                 , payload_ : Union[IPayload, dict] =None) -> int:
        if _ssshare._WarnOnDisabledSubsysMsg(annexID_=_EFwTextID.eMisc_Shared_Disabled_Subsys_Msg):
            return 0

        if isinstance(rcvID_, EXmsgPredefinedID) and rcvID_==EXmsgPredefinedID.Broadcast:
            return _XMsgMgrImpl._BroadcastXMsg(lblID_, clrID_, payload_)
        if isinstance(rcvID_, IRCTask):
            rcvID_ = rcvID_.taskUID

        res    = 0
        _msg   = None
        _sndXT = None
        _msg, _sndXT = _XMsgMgrImpl.__ProcSendRequest(lblID_, clrID_, rcvID_, payload_=payload_, bInternal_=False, bBroadcast_=False)
        if _msg is None:
            pass
        else:
            res = _msg.uniqueID
            _bSent = _UserTask._SendXMsg(_sndXT, _msg)
            if not _bSent:
                res = 0
                if (_bSent is not None) and _sndXT.isRunning and (_sndXT.currentError is None):
                    logif._LogErrorEC(_EFwErrorCode.UE_00192, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TID_034).format(_msg.header))
            _msg.CleanUp()
        return res

    @staticmethod
    def _BroadcastXMsg( lblID_   : Union[IntEnum, int]
                      , clrID_   : Union[IntEnum, int]   =EXmsgPredefinedID.DontCare
                      , payload_ : Union[IPayload, dict] =None) -> int:
        if _ssshare._WarnOnDisabledSubsysMsg(annexID_=_EFwTextID.eMisc_Shared_Disabled_Subsys_Msg):
            return 0

        res    = 0
        _msg   = None
        _sndXT = None
        _msg, _sndXT = _XMsgMgrImpl.__ProcSendRequest(lblID_, clrID_, 0, payload_=payload_, bInternal_=False, bBroadcast_=True)
        if _msg is None:
            pass
        else:
            res = _msg.uniqueID
            _bSent = _UserTask._SendXMsg(_sndXT, _msg)
            if not _bSent:
                res = 0
                if (_bSent is not None) and _sndXT.isRunning and (_sndXT.currentError is None):
                    logif._LogErrorEC(_EFwErrorCode.UE_00193, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TID_035).format(_msg.header))
            _msg.CleanUp()
        return res

    @staticmethod
    def __GetNextUniqueNr():
        return _FwMessage._GetNextUniqueNr()

    @staticmethod
    def __ProcSendRequest( lblID_      : Union[IntEnum, int]    =EXmsgPredefinedID.DontCare
                         , clrID_      : Union[IntEnum, int]    =EXmsgPredefinedID.DontCare
                         , rcvID_      : Union[IXTask, IntEnum, int] =0
                         , payload_    : Union[IPayload, dict]  =None
                         , bInternal_                              =False
                         , bBroadcast_                             =False):
        _failedTuple = None, None

        _bLRTE = False
        _bLRTE = _bLRTE or not _FwApiConnectorAP._APIsFwApiConnected()
        _bLRTE = _bLRTE or not _FwApiConnectorAP._APIsLcErrorFree()
        _bLRTE = _bLRTE or _FwApiConnectorAP._APIsLcShutdownEnabled()
        if _bLRTE:
            return _failedTuple

        if bInternal_ and (not _FwSubsysCoding.IsInternalQueueSupportEnabled()):
            return _failedTuple

        _midPart = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TID_013)

        _rcvXT = None
        _sndXT = _FwApiConnectorAP._APGetCurXTask()
        if _sndXT is None:
            logif._LogErrorEC(_EFwErrorCode.UE_00194, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TID_014).format(_midPart))
            return _failedTuple
        elif not _sndXT.taskProfile.isExternalQueueEnabled:
            if _FwSubsysCoding.IsSenderExternalQueueSupportMandatory():
                logif._LogErrorEC(_EFwErrorCode.UE_00236, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TID_002).format(_midPart))
                return _failedTuple

        _sndID = _sndXT.taskUID
        _rcvID = rcvID_

        _bPreDefRcv   = isinstance(_rcvID, EXmsgPredefinedID)
        _bDontCareRcv = _bPreDefRcv and _rcvID == EXmsgPredefinedID.DontCare
        _bDontCareLbl = isinstance(lblID_, EXmsgPredefinedID) and lblID_ == EXmsgPredefinedID.DontCare
        _bDontCareClr = isinstance(clrID_, EXmsgPredefinedID) and clrID_ == EXmsgPredefinedID.DontCare

        if _bDontCareRcv:
            if not _FwSubsysCoding.IsAnonymousAddressingEnabled():
                logif._LogErrorEC(_EFwErrorCode.UE_00195, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TID_028).format(_midPart, _SubsysMsgUtil.StringizeID(_rcvID)))
                return _failedTuple

            if _bDontCareLbl and _bDontCareClr:
                logif._LogErrorEC(_EFwErrorCode.UE_00196, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TID_029).format(_midPart, _SubsysMsgUtil.StringizeID(lblID_), _SubsysMsgUtil.StringizeID(clrID_), EXmsgPredefinedID.MinUserDefinedID.value))
                return _failedTuple

        if not (bInternal_ or bBroadcast_):
            if isinstance(_rcvID, IntEnum):
                if _bPreDefRcv and (_rcvID == EXmsgPredefinedID.MainTask):
                    _rcvID = _FwSubsysShare._GetMainXTask()
                    if _rcvID is None:
                        logif._LogErrorEC(_EFwErrorCode.UE_00197, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TID_032).format(_midPart))
                        return _failedTuple
                else:
                    _rcvID = _rcvID.value

        _bIntRcv   = isinstance(_rcvID, int)
        _bXTaskRcv = isinstance(_rcvID, IXTask)

        if _bXTaskRcv:
            if _rcvID.isDetachedFromFW or (_rcvID.taskUID is None):
                logif._LogErrorEC(_EFwErrorCode.UE_00198, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TID_019).format(_midPart, rcvID_))
                return _failedTuple
            _rcvXT = _rcvID
            _rcvID = _rcvID.taskUID
        elif not _bIntRcv:
            logif._LogErrorEC(_EFwErrorCode.UE_00199, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TID_016).format(_midPart, type(rcvID_).__name__))
            return _failedTuple
        elif _rcvID == 0:
            _rcvID = _sndID

        if (_rcvID==_sndID) and not (bInternal_ or bBroadcast_):
            if not _FwSubsysCoding.IsSelfExternalMessagingEnabled():
                logif._LogErrorEC(_EFwErrorCode.UE_00200, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TID_031).format(_midPart, _sndID))
                return _failedTuple

        if bInternal_:
            if not _sndXT.taskProfile.isInternalQueueEnabled:
                logif._LogErrorEC(_EFwErrorCode.UE_00201, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TID_015).format(_midPart, _sndID))
                return _failedTuple
            _rcvID = _sndID
            _rcvXT = _sndXT

        elif bBroadcast_:
            _rcvID = EXmsgPredefinedID.Broadcast

        else:
            if _bDontCareRcv:
                pass

            else:
                if _bXTaskRcv:
                    pass
                else:
                    if not _TaskUtil.IsValidUserTaskID(_rcvID):
                        logif._LogErrorEC(_EFwErrorCode.UE_00202, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TID_017).format(_midPart, rcvID_))
                        return _failedTuple
                    _rcvXT = _FwApiConnectorAP._APGetXTask(_rcvID)

                if _rcvXT is None:
                    logif._LogErrorEC(_EFwErrorCode.UE_00203, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TID_018).format(_midPart, rcvID_))
                    return _failedTuple
                if not (_rcvXT.isRunning or _rcvXT.isStopping or _rcvXT.isCanceling):
                    logif._LogErrorEC(_EFwErrorCode.UE_00205, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TID_020).format(_midPart, rcvID_))
                    return _failedTuple
                if not _rcvXT.taskProfile.isExternalQueueEnabled:
                    logif._LogErrorEC(_EFwErrorCode.UE_00206, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TID_021).format(_midPart, rcvID_))
                    return _failedTuple

                _rcvID = _rcvXT.taskUID

        _arg1 = _SubsysMsgUtil.StringizeID(lblID_)
        _arg2 = _SubsysMsgUtil.StringizeID(clrID_)
        _arg3 = _SubsysMsgUtil.StringizeID(_sndID)
        _arg4 = _SubsysMsgUtil.StringizeID(_rcvID)
        if not _XMsgMgrImpl.__CheckSendRequest(lblID_, clrID_, _bDontCareLbl, _bDontCareClr, bBroadcast_=bBroadcast_):
            if bBroadcast_:
                logif._LogErrorEC(_EFwErrorCode.UE_00207, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TID_027).format(_midPart, _arg1, _arg2, _arg3, _arg4, EXmsgPredefinedID.MinUserDefinedID.value))
            else:
                logif._LogErrorEC(_EFwErrorCode.UE_00208, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TID_022).format(_midPart, _arg1, _arg2, _arg3, _arg4, EXmsgPredefinedID.MinUserDefinedID.value))
            return _failedTuple

        _pld = payload_
        if _pld is not None:
            if not isinstance(_pld, (XPayload, dict)):
                if not isinstance(_pld, IPayload):
                    logif._LogErrorEC(_EFwErrorCode.UE_00155, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TID_023).format(_midPart, IPayload.__name__, dict.__name__, type(payload_).__name__, _arg1, _arg2, _arg3, _arg4, EXmsgPredefinedID.MinUserDefinedID.value))
                    return _failedTuple

                if _pld.isCustomMarshalingRequired:
                    if not _FwSubsysCoding.IsCustomPayloadSerDesEnabled():
                        logif._LogErrorEC(_EFwErrorCode.UE_00156, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TID_033).format(_midPart))
                        return _failedTuple

                _bCustomPLD = True
            elif isinstance(_pld, XPayload):
                if not _pld.isValidPayload:
                    logif._LogErrorEC(_EFwErrorCode.UE_00157, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TID_026).format(_midPart, _arg1, _arg2, _arg3, _arg4, EXmsgPredefinedID.MinUserDefinedID.value))
                    return _failedTuple
                if _pld.numParameters < 1:
                    _pld = None
                    logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TID_024).format(_midPart, _arg1, _arg2, _arg3, _arg4, EXmsgPredefinedID.MinUserDefinedID.value))
            elif len(_pld) < 1:
                _pld = None
                logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TID_024).format(_midPart, _arg1, _arg2, _arg3, _arg4, EXmsgPredefinedID.MinUserDefinedID.value))
            else:
                _pld = XPayload(containerInitializer_=payload_)
                if not (_pld.isValidPayload and _pld.numParameters==len(payload_)):
                    _pld.DetachContainer()
                    logif._LogErrorEC(_EFwErrorCode.UE_00158, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoMsgMgrImpl_TID_030).format(_midPart, XPayload.__name__, len(payload_), _arg1, _arg2, _arg3, _arg4, EXmsgPredefinedID.MinUserDefinedID.value))
                    return _failedTuple

        _hdr = _XMsgHeaderImpl(clrID_, lblID_, _rcvID, _sndID, bInternal_=bInternal_)
        if not _hdr.isValid:
            if (_pld is not None) and not isinstance(payload_, IPayload):
                _pld.DetachContainer()
            _hdr.CleanUp()
            return _failedTuple
        res = _XMsgImpl(uid_=_XMsgMgrImpl.__GetNextUniqueNr(), header_=_hdr, payld_=_pld)
        if not res.isValid:
            if (_pld is not None) and not isinstance(payload_, IPayload):
                _pld.DetachContainer()
            _hdr.CleanUp()
            res.CleanUp()
            return _failedTuple
        return res, _sndXT

    @staticmethod
    def __CheckSendRequest( lblID_  : Union[IntEnum, int], clrID_  : Union[IntEnum, int], bDontCareLbl_, bDontCareClr_, bBroadcast_ =False):
        _MIN_VAL = EXmsgPredefinedID.MinUserDefinedID.value

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
            with _XMsgMgrImpl.__ma:
                if not _MessageClusterMap.IsClusterMember(_valGrp, _valLbl):
                    if _FwSubsysCoding.IsAutoCreateClusterEnabled():
                        if not _MessageClusterMap.UpdateCluster(_valGrp, _valLbl):
                            return False
        return True

