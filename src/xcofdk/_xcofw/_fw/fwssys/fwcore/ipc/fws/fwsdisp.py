# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwsdisp.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from xcofdk.fwapi import IPayload

from _fw.fwssys.assys                     import fwsubsysshare as _ssshare
from _fw.fwssys.assys.ifs.ifdispagent     import _IDispAgent
from _fw.fwssys.fwcore.logging            import logif
from _fw.fwssys.fwcore.logging            import vlogif
from _fw.fwssys.fwcore.base.fwcallable    import _FwCallable
from _fw.fwssys.fwcore.base.timeutil      import _TimeAlert
from _fw.fwssys.fwcore.base.gtimeout      import _Timeout
from _fw.fwssys.fwcore.ipc.fws.afwservice import _AbsFwService
from _fw.fwssys.fwcore.ipc.sync.mutex     import _Mutex
from _fw.fwssys.fwcore.ipc.tsk.taskdefs   import _ERblType
from _fw.fwssys.fwcore.ipc.tsk.taskxcard  import _TaskXCard
from _fw.fwssys.fwcore.ipc.tsk.fwtaskprf  import _FwTaskProfile
from _fw.fwssys.fwcore.ipc.tsk.taskutil   import _ETaskRightFlag
from _fw.fwssys.fwcore.types.aobject      import _AbsSlotsObject
from _fw.fwssys.fwcore.types.serdes       import SerDes
from _fw.fwssys.fwmsg.msg                 import _IFwMessage
from _fw.fwssys.fwmsg.msg                 import _FwMessage
from _fw.fwssys.fwmsg.disp.fwqueue        import _FwQueue
from _fw.fwssys.fwmsg.disp.dispfilter     import _DispatchFilter
from _fw.fwssys.fwmsg.disp.dispregistry   import _DispatchRegistry
from _fw.fwssys.fwerrh.fwerrorcodes       import _EFwErrorCode
from _fwa.fwsubsyscoding                  import _FwSubsysCoding

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _FwsDispatcher(_AbsFwService):
    class _DeliveryRetryMap(_AbsSlotsObject):
        __slots__ = [ '__mr' , '__map' ]

        def __init__(self, maxRetry_ : int, map_ : dict =None):
            self.__mr = maxRetry_
            self.__map = map_
            super().__init__()

        def IsThresholdReached(self, agentTID_ : int):
            if agentTID_ is None:
                return False
            elif self.__map is None:
                return False
            elif agentTID_ not in self.__map:
                return False
            else:
                return self.__map[agentTID_] >= self.__mr

        def GetRetryCount(self, agentTID_ : int):
            if agentTID_ is None:
                return None
            elif self.__map is None:
                return 0
            elif agentTID_ not in self.__map:
                return 0
            else:
                return self.__map[agentTID_]

        def UpdateMap(self, agentTID_ : int, bWarn_ =True):
            if agentTID_ is None:
                res = False
            else:
                if self.__map is None:
                    self.__map = { agentTID_ : 1}
                elif agentTID_ not in self.__map:
                    self.__map[agentTID_] = 1
                else:
                    self.__map[agentTID_] += 1

                _newVal = self.__map[agentTID_]
                if bWarn_ and (_newVal == self.__mr):
                    logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwsDispatcher_TID_012).format(self.__mr, agentTID_))
                res = _newVal >= self.__mr
            return res

        def UpdateMapByList(self, lstTasks_: list):
            if self.__map is None:
                return None

            _keys = list(self.__map.keys())
            for _kk in _keys:
                if _kk not in lstTasks_:
                    self.__map.pop(_kk, None)
            _keys.clear()
            del _keys

            res = []
            for _kk in self.__map.keys():
                _val = self.__map[_kk] + 1
                self.__map[_kk] = _val
                if _val >= self.__mr:
                    res.append(_kk)
            return res if len(res) > 0 else None

        def RemoveTask(self, agentTID_ : int):
            if agentTID_ is None:
                pass
            elif self.__map is None:
                pass
            elif agentTID_ not in self.__map:
                pass
            else:
                self.__map.pop(agentTID_)

        def _CleanUp(self):
            if self.__map is not None:
                self.__map.clear()
                del self.__map
                self.__map = None
            self.__mr = None

    class _DispBackLogEntry(_AbsSlotsObject):
        __slots__ = [ '__rc' , '__rm' , '__m' , '__at' , '__bC' , '__bX' , '__uid' , '__dm' , '__dp' , '__cb' ]

        _MAX_RETRY_COUNT = 3

        def __init__(self, bXMsg_ : bool, msgUID_ : int, msgDump_ : bytes, lstDispTgt_ : list, retryMap_ : dict, pldDump_ =None, bCustomPL_ =None, customDesCB_ =None):
            super().__init__()
            self.__m   = None
            self.__at  = lstDispTgt_
            self.__bC  = bCustomPL_
            self.__bX  = bXMsg_
            self.__cb  = customDesCB_
            self.__dm  = msgDump_
            self.__dp  = pldDump_
            self.__rc  = 1
            self.__rm  = _FwsDispatcher._DeliveryRetryMap(maxRetry_=_FwsDispatcher._DispBackLogEntry._MAX_RETRY_COUNT, map_=retryMap_)
            self.__uid = msgUID_

        @property
        def _isMaxRetryCountReached(self):
            return (self.__rc is not None) and self.__rc >= _FwsDispatcher._DispBackLogEntry._MAX_RETRY_COUNT

        @property
        def _message(self) -> _IFwMessage:
            if self.__uid is None:
                return None
            if self.__m is not None:
                return self.__m

            self.__m = _FwsDispatcher._DeserializeMsg(self.__bX, self.__uid, self.__dm, pldDump_=self.__dp, bCustomPL_=self.__bC, customDesCB_=self.__cb)
            return self.__m

        @property
        def _msgUID(self):
            return self.__uid

        @property
        def _retryMap(self):
            return self.__rm

        @property
        def _retryCount(self) -> int:
            return self.__rc

        @property
        def _dispatchTargets(self) -> list:
            return self.__at

        @property
        def _msgDump(self) -> bytes:
            return self.__dm

        @property
        def _pldDump(self):
            return self.__dp

        @property
        def _bCustomPayload(self):
            return self.__bC

        @property
        def _customDesCallback(self):
            return self.__cb

        def _UpdateDispTargetList(self, lstDispTgt_ : list):
            _lstTID = [ _ee._dispatchAgent._agentTaskID for _ee in lstDispTgt_ ]

            _lstMaxRetryReached = self.__rm.UpdateMapByList(_lstTID)
            _lstTID.clear()
            del _lstTID

            res = None
            if _lstMaxRetryReached is not None:
                res = [ _ee for _ee in lstDispTgt_ if _ee._dispatchAgent._agentTaskID in _lstMaxRetryReached]
                for _ee in res:
                    lstDispTgt_.remove(_ee)
                    _lstMaxRetryReached.append(_ee)
                del _lstMaxRetryReached

            self.__at.clear()
            del self.__at

            self.__at = None if len(lstDispTgt_) < 1 else lstDispTgt_
            return res

        def _UpdateRetryCounter(self, lstDispTgt_ : list):
            _prvCtr = self.__rc
            self.__rc  += 1
            self.__at = lstDispTgt_
            return _prvCtr >= _FwsDispatcher._DispBackLogEntry._MAX_RETRY_COUNT

        def _ToString(self):
            pass

        def _CleanUp(self):
            if self.__dm is None:
                return

            _bPldDump = False if self.__dp is None else True

            if self.__m is not None:
                if self.__dp is not None:
                    self.__m.AttachPayload(None)
                self.__m.CleanUp()
                del self.__m
                self.__m = None

            if _bPldDump:
                del self.__dp
            del self.__dm
            self.__dp = None
            self.__dm = None

            if self.__at is not None:
                self.__at.clear()
                del self.__at
                self.__at = None

            if self.__rm is not None:
                self.__rm.CleanUp()
                del self.__rm
                self.__rm = None

            self.__bX  = None
            self.__cb  = None
            self.__rc  = None
            self.__uid = None

    __slots__ = [ '__a' , '__ma' , '__md' , '__tr' , '__iq', '__p' , '__iam' ]

    __IRRESP_THRESHOLD = 9

    __sgltn  = None
    __tskPrf = None

    def __init__(self):
        self.__a   = None
        self.__p   = None
        self.__iq  = None
        self.__ma  = None
        self.__md  = None
        self.__tr  = None
        self.__iam = None

        if _FwsDispatcher.__sgltn is not None:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00061)

        _FreqMS  = 20
        _CeaseMS = 20
        _xp = _TaskXCard(runPhaseFreqMS_=_FreqMS, cceaseFreqMS_=_CeaseMS)

        super().__init__(_ERblType.eFwDsprRbl, txCard_=_xp)
        _xp.CleanUp()

        if self._rblType is None:
            self.CleanUp()
            return

        _tout = _Timeout.CreateTimeoutSec(3)
        self.__a   = _TimeAlert(_tout.toNSec)
        self.__p   = []
        self.__ma  = _Mutex()
        self.__md  = _Mutex()
        self.__iq  = _FwQueue.CreateInstance(maxSize_=_FwQueue.GetFiniteQueueDefaultSize())
        self.__tr  = _DispatchRegistry(bTaskRegistry_=True)
        self.__iam = _FwsDispatcher._DeliveryRetryMap(maxRetry_=_FwsDispatcher.__IRRESP_THRESHOLD)

        _tout.CleanUp()

    @staticmethod
    def _GetInstance(bCreate_ =False):
        res = _FwsDispatcher.__sgltn

        if res is not None:
            return res
        if not bCreate_:
            return None

        res = _FwsDispatcher()
        if res._rblType is None:
            res.CleanUp()
            return None

        _trm = _ETaskRightFlag.FwTaskRightDefaultMask()
        _ta  = { _FwTaskProfile._ATTR_KEY_RUNNABLE : res , _FwTaskProfile._ATTR_KEY_TASK_RIGHTS : _trm }
        _tp  = _FwTaskProfile(tpAttrs_=_ta)

        if not _tp.isValid:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00062)
            _tp.CleanUp()
            res.CleanUp()
            res = None
        else:
            _FwsDispatcher.__sgltn  = res
            _FwsDispatcher.__tskPrf = _tp
        return res

    @staticmethod
    def _DeserializeMsg(bXMsg_: bool, msgUID_: int, msgDump_: bytes, pldDump_=None, bCustomPL_=None, customDesCB_=None):
        _pldDes = None

        if pldDump_ is not None:
            _bCustomSD = bCustomPL_
            _bNonSD    = not _bCustomSD

            if _bCustomSD:
                try:
                    _pldDes = customDesCB_(pldDump_)
                except BaseException as _xcp:
                    logif._LogErrorEC(_EFwErrorCode.UE_00056, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwsDispatcher_TID_010).format(msgUID_, _xcp))
                    return None

                if not (isinstance(_pldDes, IPayload) and _pldDes.isValidPayload):
                    logif._LogErrorEC(_EFwErrorCode.UE_00057, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwsDispatcher_TID_011).format(msgUID_))
                    return None

            else:
                _pldDes = pldDump_

        else:
            _bNonSD = False
            _bCustomSD = False

        res = None

        if not bXMsg_:
            res = _FwMessage.DeserializeFwMsg(msgDump_)
        else:
            res = SerDes.DeserializeData(msgDump_, bTreatAsUserError_=True)

        if res is None:
            logif._LogErrorEC(_EFwErrorCode.UE_00058, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwsDispatcher_TID_009).format(msgUID_))
        elif _pldDes is not None:
            res.AttachPayload(_pldDes)
        return res

    @property
    def _isSelfManagingInternalQueue(self):
        return True

    @property
    def _numRegisterations(self):
        if self._isInvalid or not self.isRunning:
            return 0
        with self.__ma:
            return self.__tr._regSize

    def _RegisterAgentDispatchFilter(self, dispFilter_  : _DispatchFilter, dispAgent_ : _IDispAgent, callback_ : _FwCallable =None) -> bool:
        if self._isInvalid or not self.isRunning:
            return False
        if not (isinstance(dispFilter_, _DispatchFilter) and dispFilter_.isValid):
            return False
        with self.__ma:
            return self.__tr._InsertDispatchFilter(dispFilter_, dispAgent_, callback_=callback_)

    def _DeregisterAgentDispatchFilter(self, dispFilter_  : _DispatchFilter, dispAgent_ : _IDispAgent, callback_ : _FwCallable =None) -> bool:
        if self._isInvalid or not self.isRunning:
            return False
        if not (isinstance(dispFilter_, _DispatchFilter) and dispFilter_.isValid):
            return False
        with self.__ma:
            return self.__tr._EraseDispatchFilter(dispFilter_, dispAgent_, callback_=callback_)

    def _DispatchMessage(self, msg_ : _IFwMessage) -> bool:
        if _ssshare._WarnOnDisabledSubsysMsg():
            return False

        if self._isInvalid or self._isInLcCeaseMode or not self.isRunning:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00063)
            return False
        if not (isinstance(msg_, _IFwMessage) and msg_.isValid and not msg_.isInternalMsg):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00064)
            return False

        _pldOrig    = msg_.payload
        _pldDump    = None
        _bCSerDes   = False  
        _bNonSerDes = (_pldOrig is not None) and not _pldOrig.isMarshalingRequired
        _bSerDesErr = False

        _customSerCallback = None
        _customDesCallback = None

        if (_pldOrig is None) or _bNonSerDes:
            if _bNonSerDes:
                _pldOrig = msg_.AttachPayload(None)

        else:
            if _pldOrig.isCustomMarshalingRequired:
                if not _FwSubsysCoding.IsCustomPayloadSerDesEnabled():
                    return False

                _bCSerDes = True

                try:
                    _customSerCallback = _pldOrig.__class__.SerializePayload
                    _customDesCallback = _pldOrig.__class__.DeserializePayload

                    _pldDump = _customSerCallback(_pldOrig)
                except BaseException as _xcp:
                    _bSerDesErr = True
                    logif._LogErrorEC(_EFwErrorCode.UE_00059, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwsDispatcher_TID_007).format(msg_.header, _xcp))

                if not isinstance(_pldDump, bytes):
                    if not _bSerDesErr:
                        _bSerDesErr = True
                        logif._LogErrorEC(_EFwErrorCode.UE_00060, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwsDispatcher_TID_008).format(msg_.header))
                else:
                    _pldOrig = msg_.AttachPayload(None)

        if _bSerDesErr:
            if _bNonSerDes:
                msg_.AttachPayload(_pldOrig)
            return False

        if msg_.isFwMsg:
            _dump = _FwMessage.SerializeFwMsg(msg_)
        else:
            _dump = SerDes.SerializeObject(msg_, bTreatAsUserError_=True)

        _bABack = _bNonSerDes or _bCSerDes

        if _dump is None:
            if _bABack:
                msg_.AttachPayload(_pldOrig)
            return False

        _lstP     = []
        _allTgt   = None
        _retryMap = dict()

        with self.__ma:
            _allTgt = self.__tr._GetAllDispatchTargets(msg_.header)

            if _allTgt is None:
                del _dump
                if _bABack:
                    msg_.AttachPayload(_pldOrig)
                logif._LogErrorEC(_EFwErrorCode.UE_00061, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwsDispatcher_TID_001).format(msg_.header))
                return False

        with self.__md:
            _numPushed = 0
            _bMultiTgt = len(_allTgt) > 1

            for _dt in _allTgt:
                if not self.isRunning:
                    del _dump
                    if _bABack:
                        msg_.AttachPayload(_pldOrig)
                    return False

                _dagt = _dt._dispatchAgent
                _atid = None if not _dt.isValid else _dagt._agentTaskID

                if (_atid is None) or not _dagt._isOperating:
                    if _atid is None:
                        logif._LogErrorEC(_EFwErrorCode.UE_00150, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwsDispatcher_TID_005).format(msg_.header))
                    else:
                        logif._LogErrorEC(_EFwErrorCode.UE_00151, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwsDispatcher_TID_002).format(_atid, msg_.header))
                        self.__iam.RemoveTask(_atid)
                    continue

                if _atid in self.__p:
                    _lstP.append(_dt)
                    _retryMap[_atid] = 2 if self.__iam.IsThresholdReached(_atid) else 0
                    continue

                if _bNonSerDes:
                    _pldTgt = _pldOrig
                    _bCustomPL = False
                elif _bCSerDes:
                    _pldTgt = bytes(_pldDump) if _bMultiTgt else _pldDump
                    _bCustomPL = True
                else:
                    _pldTgt    = None
                    _bCustomPL = None

                _dumpTgt = bytes(_dump) if _bMultiTgt else _dump

                _opRes = _dagt._PushMessage(msg_, _dumpTgt, _pldTgt, bCustomPL_=_bCustomPL, customDesCB_=_customDesCallback, callback_=_dt._dispatchCallback)

                if not self.isRunning:
                    return False

                if _opRes.isAbort:
                    self.__iam.UpdateMap(_atid)
                    logif._LogErrorEC(_EFwErrorCode.UE_00152, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwsDispatcher_TID_013).format(_atid, msg_.header))

                    if _bMultiTgt:
                        del _dumpTgt
                        if _bCSerDes:
                            del _pldTgt
                    continue

                if _opRes.isNOK:
                    if not _dagt._isOperating:
                        self.__iam.UpdateMap(_atid)
                        logif._LogErrorEC(_EFwErrorCode.UE_00152, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwsDispatcher_TID_013).format(_atid, msg_.header))

                        if _bMultiTgt:
                            del _dumpTgt
                            if _bCSerDes:
                                del _pldTgt

                    elif not self.__iam.UpdateMap(_atid):
                        _lstP.append(_dt)
                        _retryMap[_atid] = 1
                    continue

                _numPushed += 1
                self.__iam.RemoveTask(_atid)

            _bPushedAny  = _numPushed > 0
            _bBackLogged = False

            if len(_lstP) > 0:
                if _bNonSerDes:
                    _pldTgt    = _pldOrig
                    _bCustomPL = False
                elif _bCSerDes:
                    _pldTgt    = _pldDump
                    _bCustomPL = True
                else:
                    _pldTgt    = None
                    _bCustomPL = None

                _bl = _FwsDispatcher._DispBackLogEntry(msg_.isXcoMsg, msg_.uniqueID, _dump, _lstP, _retryMap, pldDump_=_pldTgt, bCustomPL_=_bCustomPL, customDesCB_=_customDesCallback)

                if not self.__iq.PushNowait(_bl):
                    _bl.CleanUp()
                    _myTxt = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_027).join([str(_ee._dispatchAgent._agentTaskID) for _ee in _lstP])
                    logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwsDispatcher_TID_003).format(self.__iq.qsize, _myTxt, msg_.header))
                else:
                    _bBackLogged = True
                    for _dt in _lstP:
                        _dagt = _dt._dispatchAgent
                        if _dagt._agentTaskID not in self.__p:
                            self.__p.append(_dagt._agentTaskID)

            if not _bBackLogged:
                if (not _bPushedAny) or _bMultiTgt:
                    del _dump
                    if _pldDump is not None:
                        del _pldDump
            if _bABack:
                msg_.AttachPayload(_pldOrig)

            return _bPushedAny or _bBackLogged

    def _ToString(self, bVerbose_ =False, annex_ : str =None):
        if self._isInvalid:
            return None

        annex_ = _FwTDbEngine.GetText(_EFwTextID.eFwsDispatcher_ToString_001).format(self._numRegisterations)
        return _AbsFwService._ToString(self, bVerbose_, annex_)

    def _CleanUp(self):
        if _FwsDispatcher.__sgltn is None:
            return

        _FwsDispatcher.__sgltn = None

        if _FwsDispatcher.__tskPrf is not None:
            _FwsDispatcher.__tskPrf.CleanUp()
            _FwsDispatcher.__tskPrf = None

        _mtx = self.__ma
        if _mtx is not None:
            with _mtx:
                self.__ma = None

                self.__a = None

                if self.__iam is not None:
                    self.__iam.CleanUp()
                    self.__iam = None

                if self.__p is not None:
                    self.__p.clear()
                    self.__p = None

                if self.__iq is not None:
                    self.__iq.CleanUp()
                    self.__iq = None

                self.__tr.CleanUp()
                self.__tr = None

                self.__md.CleanUp()
                self.__md = None
    
            _mtx.CleanUp()

        super()._CleanUp()

    def _RunExecutable(self):
        if not self.isRunning:
            return False
        self.__tr._DropInvalidTargets()
        return self.__ProcFwDispInternalQueue()

    def __ProcFwDispInternalQueue(self) -> bool:
        with self.__md:
            _blNum = self.__iq.qsize
            if _blNum < 1:
                self.__p.clear()
                return self.isRunning

            _ii, _lstBL = _blNum, []
            while _ii > 0:
                _bl = self.__iq.PopNowait()
                if _bl is None:
                    break
                _lstBL.append(_bl)
                _ii -= 1

            _blNum = len(_lstBL)
            if _blNum < 1:
                return self.isRunning

            _lstBL = sorted(_lstBL, key=lambda _bl: _bl._msgUID)

            _lstPendingAgents = []

            for _bl in _lstBL:
                if not self.isRunning:
                    break

                _msg = _bl._message
                if _msg is None:
                    continue

                _lstP = []

                _dt        = None
                _bMultiTgt = len(_bl._dispatchTargets) > 0

                _dumpPLD = _bl._pldDump
                if _dumpPLD is not None:
                    if _bl._bCustomPayload and _bMultiTgt:
                        _dumpPLD = bytes(_dumpPLD)
                _dump = bytes(_bl._msgDump) if _bMultiTgt else _bl._msgDump

                for _dt in _bl._dispatchTargets:
                    _dagt = _dt._dispatchAgent
                    _atid = None if not _dt.isValid else _dagt._agentTaskID

                    if (_atid is None) or not _dagt._isOperating:
                        if _atid is None:
                            logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwsDispatcher_TID_005).format(_msg.header))
                        else:
                            logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwsDispatcher_TID_002).format(_atid, _msg.header))
                            self.__iam.RemoveTask(_atid)
                        continue

                    if self.__iam.IsThresholdReached(_atid):
                        continue

                    _opRes = _dagt._PushMessage(_msg, _dump, _dumpPLD, bCustomPL_=_bl._bCustomPayload, customDesCB_=_bl._customDesCallback, callback_=_dt._dispatchCallback)

                    if not self.isRunning:
                        return False

                    if _opRes.isAbort:
                        self.__iam.UpdateMap(_atid)
                        logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwsDispatcher_TID_013).format(_atid, _msg.header))

                    elif _opRes.isNOK:
                        if not _dagt._isOperating:
                            self.__iam.UpdateMap(_atid)

                        elif not self.__iam.UpdateMap(_atid):
                            _lstP.append(_dt)

                    else:
                        self.__iam.RemoveTask(_atid)

                if len(_lstP) > 0:
                    _lstMaxRetryReached =_bl._UpdateDispTargetList(_lstP)
                    _lstP = _bl._dispatchTargets

                    if _lstMaxRetryReached is not None:
                        _myTxt = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_027).join([str(_ee._dispatchAgent._agentTaskID) for _ee in _lstMaxRetryReached])
                        logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwsDispatcher_TID_004).format(_FwsDispatcher._DispBackLogEntry._MAX_RETRY_COUNT, _myTxt, _msg.uniqueID, _msg.header))
                    if _lstP is None:
                        _bl.CleanUp()
                        break

                    if not self.__iq.PushNowait(_bl):
                        _myTxt = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_027).join([str(_ee._dispatchAgent._agentTaskID) for _ee in _lstP])
                        logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwsDispatcher_TID_003).format(self.__iq.qsize, _myTxt, _msg.header))
                        _bl.CleanUp()

                    else:
                        for _dt in _lstP:
                            _atid = _dt._dispatchAgent._agentTaskID
                            if _atid not in _lstPendingAgents:
                                _lstPendingAgents.append(_atid)
                else:
                    _bl.CleanUp()

            self.__p.clear()

            if len(_lstPendingAgents) > 0:
                self.__p.extend(_lstPendingAgents)

            return self.isRunning
