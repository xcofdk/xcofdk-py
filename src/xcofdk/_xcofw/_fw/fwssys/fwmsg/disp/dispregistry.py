# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : dispregistry.py
#
# Copyright(c) 2024-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from collections import OrderedDict as _PyOrderedDict
from enum        import IntEnum
from typing      import Union

from _fw.fwssys.assys                    import fwsubsysshare as _ssshare
from _fw.fwssys.assys.ifs.ifdispagent    import _IDispAgent
from _fw.fwssys.fwcore.logging           import vlogif
from _fw.fwssys.fwcore.logging           import logif
from _fw.fwssys.fwcore.base.fwcallable   import _FwCallable
from _fw.fwssys.fwcore.ipc.sync.mutex    import _Mutex
from _fw.fwssys.fwcore.types.aobject     import _AbsSlotsObject
from _fw.fwssys.fwcore.types.commontypes import _CommonDefines
from _fw.fwssys.fwcore.types.commontypes import _EDepInjCmd
from _fw.fwssys.fwmsg.msg                import _EMessageCluster
from _fw.fwssys.fwmsg.msg                import _EMessageLabel
from _fw.fwssys.fwmsg.msg                import _MessageCluster
from _fw.fwssys.fwmsg.msg                import _SubsysMsgUtil
from _fw.fwssys.fwmsg.msg                import _IFwMessageHeader
from _fw.fwssys.fwmsg.disp.dispfilter    import _DispatchFilter
from _fw.fwssys.fwmsg.disp.disptarget    import _DispatchTarget
from _fw.fwssys.fwerrh.fwerrorcodes      import _EFwErrorCode
from _fwa.fwsubsyscoding                 import _FwSubsysCoding

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _MessageClusterMap:
    __slots__ = []

    __dictMsgClusters = None

    def __init__(self):
        pass

    @staticmethod
    def IsDefinedCluster(clrID_ : Union[_EMessageCluster, IntEnum, int], bIgnoreUndefined_ =False):
        if not _SubsysMsgUtil.IsValidClusterID(clrID_):
            return False
        if _MessageClusterMap.__dictMsgClusters is None:
            res = False
        else:
            res = clrID_ in _MessageClusterMap.__dictMsgClusters
        if not res:
            if not bIgnoreUndefined_:
                logif._LogErrorEC(_EFwErrorCode.UE_00123, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_MessageClusterMap_TID_001).format(_SubsysMsgUtil.StringizeID(clrID_)))
        return res

    @staticmethod
    def IsClusterMember(clrID_ : Union[_EMessageCluster, IntEnum, int], lblID_ : Union[_EMessageLabel, IntEnum, int, list], bAllowAsListOfLabels_ =False, bReportError_ =False):
        if not _MessageClusterMap.IsDefinedCluster(clrID_, bIgnoreUndefined_=not bReportError_):
            return False
        if not _SubsysMsgUtil.IsValidLabelID(lblID_, bAllowAsList_=bAllowAsListOfLabels_, grpIDCalledFor_=clrID_):
            return False

        res  = True
        _clr = _MessageClusterMap.__dictMsgClusters[clrID_]
        if isinstance(lblID_, list):
            if not bAllowAsListOfLabels_:
                res = False
                logif._LogErrorEC(_EFwErrorCode.UE_00124, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Shared_TID_004).format(_SubsysMsgUtil.StringizeID(lblID_)))
            else:
                for _ee in lblID_:
                    if not _ee in _clr.labels:
                        res = False
                        break
        elif not lblID_ in _MessageClusterMap.__dictMsgClusters[clrID_].labels:
            res = False

        if not res:
            if bReportError_:
                logif._LogErrorEC(_EFwErrorCode.UE_00125, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_MessageClusterMap_TID_005).format(_SubsysMsgUtil.StringizeID(lblID_), _SubsysMsgUtil.StringizeID(clrID_)))
        return res

    @staticmethod
    def GetCluster(clrID_ : Union[_EMessageCluster, IntEnum, int]) -> _MessageCluster:
        res = None
        if not _MessageClusterMap.IsDefinedCluster(clrID_):
            pass
        elif clrID_ in _MessageClusterMap.__dictMsgClusters:
            res = _MessageClusterMap.__dictMsgClusters[clrID_]
        return res

    @staticmethod
    def GetAllClusters(lblID_ : Union[_EMessageLabel, IntEnum, int, list], bAllowAsListOfLabels_ =False) -> Union[_MessageCluster, list]:
        if not _SubsysMsgUtil.IsValidLabelID(lblID_, bAllowAsList_=bAllowAsListOfLabels_):
            return None
        if _MessageClusterMap.__dictMsgClusters is None:
            return None

        _lst = lblID_
        if isinstance(lblID_, list):
            if not bAllowAsListOfLabels_:
                logif._LogErrorEC(_EFwErrorCode.UE_00126, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Shared_TID_004).format(_SubsysMsgUtil.StringizeID(lblID_)))
                return None
        else:
            _lst = [lblID_]

        res  = []
        _key = None
        for _kk, _vv in _MessageClusterMap.__dictMsgClusters.items():
            _key = _kk
            for _ee in _lst:
                if _ee not in _vv.labels:
                    _key = None
                    break
            if _key is not None:
                res.append(_key)

        if len(res) < 1:
            res = None
        else:
            res = [ _MessageClusterMap.__dictMsgClusters[_kk] for _kk in res ]
        return res

    @staticmethod
    def UpdateCluster(clrID_ : Union[_EMessageCluster, IntEnum, int], lblID_ : Union[_EMessageLabel, IntEnum, int, list], bAllowAsListOfLabels_ =False, bIgnoreDontCare_ =False) -> _MessageCluster:
        if not _SubsysMsgUtil.IsValidClusterID(clrID_):
            return None
        if isinstance(clrID_, _EMessageCluster) and clrID_.isCDontCare:
            if not bIgnoreDontCare_:
                logif._LogErrorEC(_EFwErrorCode.UE_00127, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_MessageClusterMap_TID_003))
            return None

        if not _SubsysMsgUtil.IsValidLabelID(lblID_, bAllowAsList_=bAllowAsListOfLabels_, grpIDCalledFor_=clrID_):
            return None
        if isinstance(lblID_, list):
            if not bAllowAsListOfLabels_:
                logif._LogErrorEC(_EFwErrorCode.UE_00128, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Shared_TID_004).format(_SubsysMsgUtil.StringizeID(lblID_)))
                return None
            else:
                for _ee in lblID_:
                    if isinstance(_ee, _EMessageLabel) and _ee.isLDontCare:
                        if not bIgnoreDontCare_:
                            logif._LogErrorEC(_EFwErrorCode.UE_00129, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_MessageClusterMap_TID_004).format(_SubsysMsgUtil.StringizeID(clrID_)))
                        return None
        elif isinstance(lblID_, _EMessageLabel) and lblID_.isLDontCare:
            if not bIgnoreDontCare_:
                logif._LogErrorEC(_EFwErrorCode.UE_00130, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_MessageClusterMap_TID_004).format(_SubsysMsgUtil.StringizeID(clrID_)))
            return None

        _bIgnore = False
        if _MessageClusterMap.IsDefinedCluster(clrID_, bIgnoreUndefined_=True):
            res = _MessageClusterMap.GetCluster(clrID_)
            if res.IsMember(lblID_):
                _bIgnore = True
            elif not res.UpdateCluster(lblID_):
                res = None
                logif._LogErrorEC(_EFwErrorCode.UE_00131, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_MessageClusterMap_TID_002).format(_SubsysMsgUtil.StringizeID(clrID_), str(lblID_)))
        else:
            res = _MessageCluster(clrID_, lblID_)
            if not res.isValid:
                res.CleanUp()
                res = None
            else:
                if _MessageClusterMap.__dictMsgClusters is None:
                    _MessageClusterMap.__dictMsgClusters = dict()
                _MessageClusterMap.__dictMsgClusters[res.clusterID] = res
        return res

    @staticmethod
    def _DepInjection(dinjCmd_ : _EDepInjCmd):
        if not dinjCmd_.isDeInject:
            return
        if _ssshare._IsSubsysMsgDisabled():
            return
        if _MessageClusterMap.__dictMsgClusters is None:
            return
        for _vv in _MessageClusterMap.__dictMsgClusters.values():
            _vv.CleanUp()
        _MessageClusterMap.__dictMsgClusters.clear()
        _MessageClusterMap.__dictMsgClusters = None

class _DispatchRegCard(_AbsSlotsObject):
    __slots__ = [ '__f' , '__t' ]

    __bANONY_ADDR_ENABLED        = _FwSubsysCoding.IsAnonymousAddressingEnabled()
    __bSELF_BROADCASTING_ENABLED = _FwSubsysCoding.IsSelfExternalMessagingEnabled()

    def __init__( self, dispFilter_ : _DispatchFilter, agent_ : _IDispAgent, callback_ : _FwCallable =None):
        self.__f = None
        self.__t = None
        super().__init__()

        if not (isinstance(dispFilter_, _DispatchFilter) and dispFilter_.isValid):
            self.CleanUp()
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00524)
            return
        if not (isinstance(agent_, _IDispAgent) and agent_._isOperating):
            self.CleanUp()
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00525)
            return

        _bAutoDestroy = False
        if callback_ is not None:
            if not _FwCallable.IsValidCallableSpec(callback_):
                self.CleanUp()
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00526)
                return
            if not isinstance(callback_, _FwCallable):
                callback_ = _FwCallable.CreateInstance(callback_)
                if callback_ is None:
                    self.CleanUp()
                    return
                _bAutoDestroy = True

        self.__f = dispFilter_
        self.__t = _DispatchTarget(agent_=agent_, callback_=callback_, bAutoDestroy_=_bAutoDestroy)

    def __eq__(self, other_):
        if not isinstance(other_, _DispatchRegCard):
            return False
        if not (self.isValid and other_.isValid):
            return False
        return (self.__f == other_.dispatchFilter) and (self.__t == other_.dispatchTarget)

    def __ne__(self, other_):
        if not isinstance(other_, _DispatchRegCard):
            return True
        if not (self.isValid and other_.isValid):
            return True
        return (self.__f != other_.dispatchFilter) or (self.__t != other_.dispatchTarget)

    def __hash__(self):
        if not self.isValid:
            return None
        return hash(self.__f)+hash(self.__t)

    @property
    def isValid(self) -> bool:
        return self.__f is not None

    @property
    def dispatchFilter(self) -> _DispatchFilter:
        return self.__f

    @property
    def dispatchTarget(self) -> _DispatchTarget:
        return self.__t

    def IsMatchingMsg(self, msgHdr_ : _IFwMessageHeader) -> bool:
        if not self.isValid:
            return False
        if not (isinstance(msgHdr_, _IFwMessageHeader) and msgHdr_.isValid):
            return False

        res  = True
        _myf = self.__f

        if msgHdr_.isFwMsgHeader:
            if not (_myf.typeID == msgHdr_.typeID or _myf.isDontCareType):
                return False
            if not (_myf.channelID == msgHdr_.channelID or _myf.isDontCareChanel):
                return False
        if not (_myf.senderID == msgHdr_.senderID or _myf.isDontCareSender):
            return False

        _bDontCareMsgGrp    = msgHdr_.isDontCareCluster
        _bDontCareFilterGrp = _myf.isDontCareCluster

        if not (_myf.clusterID == msgHdr_.clusterID or _bDontCareFilterGrp or _bDontCareMsgGrp):
            return False

        _bDontCareMsgLbl    = msgHdr_.isDontCareLabel
        _bDontCareFilterLbl = _myf.isDontCareLabel

        if not (_myf.labelID == msgHdr_.labelID or _bDontCareFilterLbl or _bDontCareMsgLbl):
            return False
        if (not _bDontCareFilterGrp) and not _bDontCareMsgLbl:
            if not _MessageClusterMap.IsClusterMember(_myf.clusterID, msgHdr_.labelID):
                return False
        if (not _bDontCareMsgGrp) and not _bDontCareFilterLbl:
            if not _MessageClusterMap.IsClusterMember(msgHdr_.clusterID, _myf.labelID):
                return False
        if msgHdr_.isBroadcastMsg:
            return self.__IsMatchingBMsg(msgHdr_)

        _bDontCareMsgRcv = msgHdr_.isDontCareReceiver

        if not (_myf.receiverID == msgHdr_.receiverID or _myf.isDontCareReceiver or _bDontCareMsgRcv):
            return False
        if _bDontCareMsgRcv:
            if not _DispatchRegCard.__bANONY_ADDR_ENABLED:
                return False
        return True

    def _CleanUp(self):
        if not self.isValid:
            return

        self.__f.CleanUp()
        self.__t.CleanUp()

        self.__f = None
        self.__t = None

    def _ToString(self):
        return None if self.__f is None else self.__f.ToString()

    def __IsMatchingBMsg(self, msgHdr_: _IFwMessageHeader) -> bool:
        _myf = self.__f

        _bFwMsg = msgHdr_.isFwMsgHeader

        _bFwBroadcastMsg     = _bFwMsg and msgHdr_.isFwBroadcastMsg
        _bGlobalBroadcastMsg = _bFwMsg and msgHdr_.isGlobalBroadcastMsg

        if _myf.isBroadcastFilter:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00527)
            return False

        _agent = self.__t._dispatchAgent

        if _bGlobalBroadcastMsg:
            res = True
        elif _bFwBroadcastMsg:
            res = _agent._isFwAgent
        else:
            res = _agent._isXTaskAgent
        if res and (_agent._agentTaskID == msgHdr_.senderID):
            res = _DispatchRegCard.__bSELF_BROADCASTING_ENABLED
        return res

class _DispatchRegistry(_AbsSlotsObject):
    __slots__ = [ '__bT' , '__ma' , '__t' ]

    def __init__(self, bTaskRegistry_ : bool =False):
        super().__init__()
        self.__t  = None
        self.__bT = bTaskRegistry_
        self.__ma = _Mutex()

    @property
    def _isTaskRegistry(self):
        return self.__isValid and self.__bT

    @property
    def _isCallbackRegistry(self):
        return self.__isValid and not self.__bT

    @property
    def _regSize(self):
        if self.__isInvalid:
            return 0
        with self.__ma:
            return 0 if self.__t is None else len(self.__t)

    def _InsertDispatchFilter( self
                          , dispFilter_ : _DispatchFilter
                          , dispAgent_  : _IDispAgent
                          , callback_   : _FwCallable =None) -> bool:
        if self.__isInvalid:
            return False

        _drc = _DispatchRegCard(dispFilter_, dispAgent_, callback_)
        if not _drc.isValid:
            _drc.CleanUp()
            return False

        return self.__AddRegCard(_drc)

    def _EraseDispatchFilter( self
                           , dispFilter_ : _DispatchFilter
                           , dispAgent_  : _IDispAgent
                           , callback_   : _FwCallable =None) -> bool:
        if self.__isInvalid:
            return False

        _drc = _DispatchRegCard(dispFilter_, dispAgent_, callback_)
        if not _drc.isValid:
            _drc.CleanUp()
            return False

        return self.__RemoveRegCard(_drc)

    def _GetAllDispatchTargets(self, msgHdr_ : _IFwMessageHeader) -> list:
        if self.__isInvalid:
            return None
        with self.__ma:
            if self.__t is None:
                return None

            _atgt  = None
            _cbtgt = None

            _lstAgent    = []
            _lstCallback = []
            for _vv in self.__t.values():
                _dt = _vv.dispatchTarget
                if _dt.isValid and _vv.IsMatchingMsg(msgHdr_):
                    if _dt._isCallbackDispatch:
                        if _dt not in _lstCallback:
                            _lstCallback.append(_dt)
                    elif _dt not in _lstAgent:
                        _lstAgent.append(_dt)
            if len(_lstCallback) < 1:
                res = _lstAgent
            elif len(_lstAgent) < 1:
                res = _lstCallback
            else:
                res = []
                for _atgt in _lstAgent:
                    _bIgnore = False
                    for _cbtgt in _lstCallback:
                        if _atgt._IsSameAgent(_cbtgt, bSkipPreCheck_=True):
                            _bIgnore = True
                            break
                    if not _bIgnore:
                        res.append(_atgt)
                res.extend(_lstCallback)

            if len(res) < 1:
                res = None
            return res

    def _DropInvalidTargets(self):
        if self.__isInvalid:
            return
        with self.__ma:
            if self.__t is None:
                return
            _lst = [ _kk for _kk, _vv in self.__t.items() if not _vv.dispatchTarget.isValid ]
            for _kk in _lst:
                _vv = self.__t[_kk]
                self.__t[_kk] = None
                del self.__t[_kk]
                _vv.CleanUp()
            if len(self.__t) < 1:
                self.__t = None

    def _ToString(self):
        if self.__isInvalid:
            return None
        return _CommonDefines._STR_EMPTY

    def _CleanUp(self):
        if self.__isInvalid:
            return

        with self.__ma:
            if self.__t is not None:
                for _vv in self.__t.values():
                    _vv.CleanUp()
                self.__t.clear()
                self.__t = None

        self.__ma.CleanUp()
        self.__ma = None
        self.__bT = None

    @property
    def __isValid(self):
        return self.__ma is not None

    @property
    def __isInvalid(self):
        return self.__ma is None

    def __AddRegCard(self, drc_ : _DispatchRegCard) -> bool:
        _hval = hash(drc_)

        with self.__ma:
            if self.__t is None:
                self.__t = _PyOrderedDict()

            elif _hval in self.__t.keys():
                drc_.CleanUp()
                drc_ = None

            if drc_ is not None:
                self.__t[_hval] = drc_
                if _FwSubsysCoding.IsAutoCreateClusterEnabled():
                    _MessageClusterMap.UpdateCluster(drc_.dispatchFilter.clusterID, drc_.dispatchFilter.labelID, bAllowAsListOfLabels_=False, bIgnoreDontCare_=True)
            return True

    def __RemoveRegCard(self, drc_ : _DispatchRegCard) -> bool:
        _hval = hash(drc_)

        with self.__ma:
            if self.__t is None:
                return False
            if _hval not in self.__t.keys():
                return False

            _drc = self.__t.pop(_hval)
            if len(self.__t) < 1:
                self.__t = None
            _drc.CleanUp()

            drc_.CleanUp()
            return True
