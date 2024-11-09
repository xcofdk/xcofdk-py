# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : messagedefs.py
#
# Copyright(c) 2023-2024 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from typing import Union as _PyUnion

from xcofdk.fwcom.xmsgdefs import EPreDefinedMessagingID

from xcofdk._xcofw.fw.fwssys.fwcore.logging           import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.logging           import logif
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil  import _TaskUtil
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject     import _AbstractSlotsObject
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes import _CommonDefines
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes import _FwIntEnum
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes import Enum
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes import IntEnum
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes import unique

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine


@unique
class _EMessageType(_FwIntEnum):
    eTDontCare = -100
    eTIntraProcess = -101
    eTIncoming = -102
    eTOutgoing = -103

    @property
    def isTDontCare(self):
        return self == _EMessageType.eTDontCare

    @property
    def isTIntraProcess(self):
        return self == _EMessageType.eTIntraProcess

    @property
    def isTIncoming(self):
        return self == _EMessageType.eTIncoming

    @property
    def isTOutgoing(self):
        return self == _EMessageType.eTOutgoing


@unique
class _EMessageChannel(_FwIntEnum):
    eChDontCare     = -200
    eChIntraTask    = -201
    eChInterTask    = -202
    eChInterProcess = -203
    eChInterCPU     = -204
    eChNetwork      = -205
    eChCustom       = -206

    @property
    def isChDontCare(self):
        return self == _EMessageChannel.eChDontCare

    @property
    def isChIntraTask(self):
        return self == _EMessageChannel.eChIntraTask

    @property
    def isChInterTask(self):
        return self == _EMessageChannel.eChInterTask

    @property
    def isChInterProcess(self):
        return self == _EMessageChannel.eChInterProcess

    @property
    def isChInterCPU(self):
        return self == _EMessageChannel.eChInterCPU

    @property
    def isChNetwork(self):
        return self == _EMessageChannel.eChNetwork

    @property
    def isChCustom(self):
        return self == _EMessageChannel.eChCustom


@unique
class _EMessageCluster(_FwIntEnum):
    eCDontCare          = -300
    eCFrameworkActivity = -301

    @property
    def isCDontCare(self):
        return self == _EMessageCluster.eCDontCare

    @property
    def isCFrameworkActivity(self):
        return self == _EMessageCluster.eCFrameworkActivity


@unique
class _EMessageLabel(_FwIntEnum):
    eLDontCare                 = -400
    eLTmrMgrBackLogAddTimer    = -401
    eLTmrMgrBackLogRemoveTimer = -402

    @property
    def isLDontCare(self):
        return self == _EMessageLabel.eLDontCare

    @property
    def isLTmrMgrBackLogAddTimer(self):
        return self == _EMessageLabel.eLTmrMgrBackLogAddTimer

    @property
    def isLTmrMgrBackLogRemoveTimer(self):
        return self == _EMessageLabel.eLTmrMgrBackLogRemoveTimer


@unique
class _EMessagePeer(_FwIntEnum):
    ePDontCare        = -500
    ePGlobalBroadcast = -501
    ePFwBroadcast     = -502
    ePXTaskBroadcast  = -503
    ePFwMain          = -504
    ePTmrMgr          = -505

    @property
    def isPDontCare(self):
        return self == _EMessagePeer.ePDontCare

    @property
    def isPBroadcast(self):
        return (self.value<=_EMessagePeer.ePGlobalBroadcast.value) and (self.value>= _EMessagePeer.ePXTaskBroadcast.value)

    @property
    def isPGlobalBroadcast(self):
        return self == _EMessagePeer.ePGlobalBroadcast

    @property
    def isPFwBroadcast(self):
        return self == _EMessagePeer.ePFwBroadcast

    @property
    def isPXTaskBroadcast(self):
        return self == _EMessagePeer.ePXTaskBroadcast

    @property
    def isPFwMain(self):
        return self == _EMessagePeer.ePFwMain

    @property
    def isPTimerManager(self):
        return self == _EMessagePeer.ePTmrMgr


class _SubsysMsgUtil:
    __slots__ = []

    def __init__(self):
        pass

    @staticmethod
    def IsValidClusterID(anID_ : _PyUnion[_EMessageCluster, IntEnum, int, list], bAllowAsList_ =False) -> bool:
        res      = True
        _myMsg   = None
        _MIN_VAL = EPreDefinedMessagingID.MinUserDefinedID.value

        if isinstance(anID_, list):
            if not bAllowAsList_:
                res = False
                _myMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Shared_TextID_004).format(_SubsysMsgUtil.StringizeID(anID_))
            elif len(anID_) < 1:
                res = False
            else:
                for _ee in anID_:
                    if not isinstance(_ee, (_EMessageCluster, IntEnum, int)):
                        res = False
                    elif not isinstance(_ee, _EMessageCluster):
                        if isinstance(_ee, IntEnum):
                            res = _ee.value >= _MIN_VAL
                        else:
                            res = _ee >= _MIN_VAL
                    if not res:
                        break
        elif not isinstance(anID_, (_EMessageCluster, IntEnum, int)):
            res = False
        elif not isinstance(anID_, _EMessageCluster):
            if isinstance(anID_, IntEnum):
                res = anID_.value >= _MIN_VAL
            else:
                res = anID_ >= _MIN_VAL

        if not res:
            if _myMsg is None:
                _myMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_SubsysMsgUtil_TextID_003).format(_SubsysMsgUtil.StringizeID(anID_))
            logif._LogError(_myMsg)
        return res

    @staticmethod
    def IsValidLabelID(anID_ : _PyUnion[_EMessageLabel, IntEnum, int, list], bAllowAsList_ =False, grpIDCalledFor_ =None) -> bool:
        res      = True
        _myMsg   = None
        _MIN_VAL = EPreDefinedMessagingID.MinUserDefinedID.value

        if isinstance(anID_, list):
            if not bAllowAsList_:
                res = False
                _myMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Shared_TextID_004).format(_SubsysMsgUtil.StringizeID(anID_))
            elif len(anID_) < 1:
                res = False
            else:
                for _ee in anID_:
                    if not isinstance(_ee, (_EMessageLabel, IntEnum, int)):
                        res = False
                    elif not isinstance(_ee, _EMessageLabel):
                        if isinstance(_ee, IntEnum):
                            res = _ee.value >= _MIN_VAL
                        else:
                            res = _ee >= _MIN_VAL
                    if not res:
                        break
        elif not isinstance(anID_, (_EMessageLabel, IntEnum, int)):
            res = False
        elif not isinstance(anID_, _EMessageLabel):
            if isinstance(anID_, IntEnum):
                res = anID_.value >= _MIN_VAL
            else:
                res = anID_ >= _MIN_VAL

        if not res:
            if _myMsg is None:
                _midPart = _CommonDefines._STR_EMPTY if grpIDCalledFor_ is None else _FwTDbEngine.GetText(_EFwTextID.eLogMsg_SubsysMsgUtil_TextID_001).format(_SubsysMsgUtil.StringizeID(grpIDCalledFor_))
                _myMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_SubsysMsgUtil_TextID_002).format(_midPart, _SubsysMsgUtil.StringizeID(anID_))
            logif._LogError(_myMsg)
        return res

    @staticmethod
    def IsValidPeerID(anID_ : _PyUnion[_EMessagePeer, IntEnum, int, list], bAllowAsList_ =False, bSender_ =False) -> bool:
        res    = True
        _myMsg = None
        if isinstance(anID_, list):
            if not bAllowAsList_:
                res = False
                _myMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Shared_TextID_004).format(_SubsysMsgUtil.StringizeID(anID_))
            elif len(anID_) < 1:
                res = False
            else:
                for _ee in anID_:
                    if not _SubsysMsgUtil.IsValidTaskID(_ee, bSender_=bSender_):
                        res = False
                        break
        else:
            res = _SubsysMsgUtil.IsValidTaskID(anID_, bSender_=bSender_)

        if not res:
            if _myMsg is None:
                _myMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_SubsysMsgUtil_TextID_004).format(_SubsysMsgUtil.StringizeID(anID_))
            logif._LogError(_myMsg)
        return res

    @staticmethod
    def IsValidTaskID(anID_ : _PyUnion[_EMessagePeer, IntEnum, int], bSender_ =False, bDoTypeCheck_ =True) -> bool:
        _bMsgPeerID = isinstance(anID_, _EMessagePeer)

        if bDoTypeCheck_ and not (_bMsgPeerID or isinstance(anID_, (IntEnum, int))):
            return False
        if _bMsgPeerID:
            return not (bSender_ and anID_.isPBroadcast)

        _idVal = anID_.value if isinstance(anID_, IntEnum) else anID_
        return _TaskUtil.IsValidUserTaskID(_idVal) or _TaskUtil.IsValidFwTaskID(_idVal)

    @staticmethod
    def StringizeID(someID_: _PyUnion[IntEnum, Enum, int, object]) -> str:
        if isinstance(someID_, (IntEnum, Enum)):
            res = f'{someID_.name}'
        else:
            res = str(someID_)
        return res


class _MessageCluster(_AbstractSlotsObject):

    __slots__ = [ '__clrID' , '__labels' ]

    def __init__(self, clrID_ : _PyUnion[_EMessageCluster, IntEnum, int], lblID_ : _PyUnion[_EMessageLabel, IntEnum, int, list] =None):
        self.__clrID  = None
        self.__labels = None
        super().__init__()

        if not _SubsysMsgUtil.IsValidClusterID(clrID_):
            vlogif._LogOEC(True, -1631)
            return

        _lbls = lblID_
        if _lbls is None:
            vlogif._LogOEC(True, -1632)
            return
        if isinstance(_lbls, list):
            if len(_lbls) < 1:
                vlogif._LogOEC(True, -1633)
                return
        else:
            _lbls = [_lbls]

        for _ee in _lbls:
            if not _SubsysMsgUtil.IsValidLabelID(lblID_, bAllowAsList_=True, grpIDCalledFor_=clrID_):
                vlogif._LogOEC(True, -1634)
                return
            elif isinstance(lblID_, _EMessageLabel):
                if lblID_.isLDontCare:
                    vlogif._LogOEC(True, -1635)
                    return

        self.__clrID  = clrID_
        self.__labels = _lbls

    @property
    def isValid(self):
        return self.__clrID is not None

    @property
    def clusterID(self):
        return self.__clrID

    @property
    def clusterName(self):
        return _SubsysMsgUtil.StringizeID(self.__clrID)

    @property
    def labels(self):
        return self.__labels

    def IsMember(self, lblID_ : _PyUnion[_EMessageLabel, IntEnum, int, list]):
        if not (self.isValid and self.__labels is not None):
            return False
        if not _SubsysMsgUtil.IsValidLabelID(lblID_, bAllowAsList_=True, grpIDCalledFor_=self.__clrID):
            return False

        res = True
        if isinstance(lblID_, list):
            for _ee in lblID_:
                if _ee not in self.__labels:
                    res = False
                    break
        else:
            res = lblID_ in self.__labels
        return res

    def UpdateCluster(self, lblID_: _PyUnion[_EMessageLabel, IntEnum, int, list]):
        if not self.isValid:
            return False
        if not _SubsysMsgUtil.IsValidLabelID(lblID_, bAllowAsList_=True, grpIDCalledFor_=self.__clrID):
            return False

        if self.__labels is None:
            self.__labels = []

        if isinstance(lblID_, list):
            for _ee in lblID_:
                if isinstance(_ee, _EMessageLabel) and _ee.isLDontCare:
                    return False
                if _ee not in self.__labels:
                    self.__labels.append(_ee)
        elif isinstance(lblID_, _EMessageLabel) and lblID_.isLDontCare:
            return False
        if lblID_ not in self.__labels:
            self.__labels.append(lblID_)
        return True

    def _ToString(self, *args_, **kwargs_):
        if self.__clrID is None:
            return None
        return _FwTDbEngine.GetText(_EFwTextID.eMessageCluster_ToString_01).format(type(self).__name__, self.clusterName, str(self.__labels))

    def _CleanUp(self):
        if self.__labels is not None:
            self.__labels.clear()
        self.__clrID  = None
        self.__labels = None
