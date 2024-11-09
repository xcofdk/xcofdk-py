# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwdispatcher.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from xcofdk.fwapi.xmsg.xpayloadif import XPayloadIF

from xcofdk._xcofw.fw.fwssys.fwcore.logging            import logif
from xcofdk._xcofw.fw.fwssys.fwcore.logging            import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.base.callableif    import _CallableIF
from xcofdk._xcofw.fw.fwssys.fwcore.base.listutil      import _ListUtil
from xcofdk._xcofw.fw.fwssys.fwcore.base.timeutil      import _TimeAlert
from xcofdk._xcofw.fw.fwssys.fwcore.base.gtimeout      import _Timeout
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject      import _AbstractSlotsObject

from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.arunnabledefs import _EFwcID
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.arunnabledefs import _ERunProgressID
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.arunnabledefs import _ERunnableType
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.arunnablefwc  import _AbstractRunnableFWC
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.sync.mutex        import _Mutex
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.execprofile   import _ExecutionProfile
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskprofile   import _TaskProfile
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil      import _ETaskRightFlag

from xcofdk._xcofw.fw.fwssys.fwmsg.apiimpl.xcomsgmgrimpl import _XMsgMgrImpl

from xcofdk._xcofw.fw.fwssys.fwmsg.msg import _MessageIF
from xcofdk._xcofw.fw.fwssys.fwmsg.msg import _FwMessage

from xcofdk._xcofw.fw.fwssys.fwmsg.disp.fwqueue          import _FwQueue
from xcofdk._xcofw.fw.fwssys.fwmsg.disp.dispatchFilter   import _DispatchFilter
from xcofdk._xcofw.fw.fwssys.fwmsg.disp.dispatchagentif  import _DispatchAgentIF
from xcofdk._xcofw.fw.fwssys.fwmsg.disp.dispatchregistry import _DispatchRegistry

from xcofdk._xcofwa.fwadmindefs import _FwSubsystemCoding

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine



class _FwDispatcher(_AbstractRunnableFWC):

    class _DeliveryRetryMap(_AbstractSlotsObject):
        __slots__ = [ '__maxRetry' , '__map' ]

        def __init__(self, maxRetry_ : int, map_ : dict =None):
            self.__map      = map_
            self.__maxRetry = maxRetry_
            super().__init__()

        def IsThresholdReached(self, taskUID_ : int):
            if taskUID_ is None:
                return False
            elif self.__map is None:
                return False
            elif taskUID_ not in self.__map:
                return False
            else:
                return self.__map[taskUID_] >= self.__maxRetry

        def GetRetryCount(self, taskUID_ : int):
            if taskUID_ is None:
                return None
            elif self.__map is None:
                return 0
            elif taskUID_ not in self.__map:
                return 0
            else:
                return self.__map[taskUID_]

        def UpdateMap(self, taskUID_ : int, bWarn_ =True):
            if taskUID_ is None:
                res = False
            else:
                if self.__map is None:
                    self.__map = { taskUID_ : 1}
                elif taskUID_ not in self.__map:
                    self.__map[taskUID_] = 1
                else:
                    self.__map[taskUID_] += 1

                _newVal = self.__map[taskUID_]
                if bWarn_ and (_newVal == self.__maxRetry):
                    logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwDispatcher_TextID_012).format(self.__maxRetry, taskUID_))
                res = _newVal >= self.__maxRetry
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
                if _val >= self.__maxRetry:
                    res.append(_kk)
            return res if len(res) > 0 else None

        def RemoveTask(self, taskUID_ : int):
            if taskUID_ is None:
                pass
            elif self.__map is None:
                pass
            elif taskUID_ not in self.__map:
                pass
            else:
                self.__map.pop(taskUID_)

        def _CleanUp(self):
            if self.__map is not None:
                self.__map.clear()
                del self.__map
                self.__map = None
            self.__maxRetry = None


    class _DispBackLogEntry(_AbstractSlotsObject):
        __slots__ = [ '__msg' , '__bXMsg' , '__msgUID' , '__msgDump' , '__pldDump' , '__bCPL' , '__cdesCB' , '__retryCnt', '__lstDispTgt' , '__retryMap' ]

        _MAX_RETRY_COUNT = 3

        def __init__(self, bXMsg_ : bool, msgUID_ : int, msgDump_ : bytes, lstDispTgt_ : list, retryMap_ : dict, pldDump_ =None, bCustomPL_ =None, customDesCallback_ =None):
            super().__init__()
            self.__msg        = None
            self.__bCPL       = bCustomPL_
            self.__bXMsg      = bXMsg_
            self.__msgUID     = msgUID_
            self.__cdesCB     = customDesCallback_
            self.__msgDump    = msgDump_
            self.__pldDump    = pldDump_
            self.__retryCnt   = 1
            self.__retryMap   = _FwDispatcher._DeliveryRetryMap(maxRetry_=_FwDispatcher._DispBackLogEntry._MAX_RETRY_COUNT, map_=retryMap_)
            self.__lstDispTgt = lstDispTgt_


        @property
        def _isMaxRetryCountReached(self):
            return (self.__retryCnt is not None) and self.__retryCnt >= _FwDispatcher._DispBackLogEntry._MAX_RETRY_COUNT

        @property
        def _message(self) -> _MessageIF:
            if self.__msgUID is None:
                return None
            if self.__msg is not None:
                return self.__msg

            self.__msg = _FwDispatcher._DeserializeMsg(self.__bXMsg, self.__msgUID, self.__msgDump, pldDump_=self.__pldDump, bCustomPL_=self.__bCPL, customDesCallback_=self.__cdesCB)
            return self.__msg

        @property
        def _msgUID(self):
            return self.__msgUID

        @property
        def _retryMap(self):
            return self.__retryMap

        @property
        def _retryCount(self) -> int:
            return self.__retryCnt

        @property
        def _dispatchTargets(self) -> list:
            return self.__lstDispTgt

        @property
        def _msgDump(self) -> bytes:
            return self.__msgDump

        @property
        def _pldDump(self):
            return self.__pldDump

        @property
        def _bCustomPayload(self):
            return self.__bCPL

        @property
        def _customDesCallback(self):
            return self.__cdesCB

        def _UpdateDispTargetList(self, lstDispTgt_ : list):
            _lstTID = [ _ee._dispatchAgent._agentTaskID for _ee in lstDispTgt_ ]

            _lstMaxRetryReached = self.__retryMap.UpdateMapByList(_lstTID)
            _lstTID.clear()
            del _lstTID

            res = None
            if _lstMaxRetryReached is not None:
                res = [ _ee for _ee in lstDispTgt_ if _ee._dispatchAgent._agentTaskID in _lstMaxRetryReached]
                for _ee in res:
                    lstDispTgt_.remove(_ee)
                    _lstMaxRetryReached.append(_ee)
                del _lstMaxRetryReached

            self.__lstDispTgt.clear()
            del self.__lstDispTgt

            self.__lstDispTgt = None if len(lstDispTgt_) < 1 else lstDispTgt_
            return res

        def _UpdateRetryCounter(self, lstDispTgt_ : list):
            _prvCtr = self.__retryCnt
            self.__retryCnt  += 1
            self.__lstDispTgt = lstDispTgt_
            return _prvCtr >= _FwDispatcher._DispBackLogEntry._MAX_RETRY_COUNT

        def _ToString(self, *args_, **kwargs_):
            pass

        def _CleanUp(self):
            if self.__msgDump is None:
                return

            _bPldDump = False if self.__pldDump is None else True

            if self.__msg is not None:
                if self.__pldDump is not None:
                    self.__msg.AttachPayload(None)
                self.__msg.CleanUp()
                del self.__msg
                self.__msg = None

            if _bPldDump:
                del self.__pldDump
            del self.__msgDump
            self.__pldDump = None
            self.__msgDump = None

            if self.__lstDispTgt is not None:
                self.__lstDispTgt.clear()
                del self.__lstDispTgt
                self.__lstDispTgt = None

            if self.__retryMap is not None:
                self.__retryMap.CleanUp()
                del self.__retryMap
                self.__retryMap = None

            self.__bXMsg    = None
            self.__msgUID   = None
            self.__cdesCB   = None
            self.__retryCnt = None

    __slots__ = [ '__mtxApi' , '__mtxData' , '__treg' , '__logAlert' , '__iqueue', '__pendingAgents' , '__irrespAgentsMap' ]

    __theInstance         = None
    __theTaskProfile      = None
    __IRRESP_THRESHOLD    = 9


    def __init__(self):
        self.__treg            = None
        self.__iqueue          = None
        self.__mtxApi          = None
        self.__mtxData         = None
        self.__logAlert        = None
        self.__pendingAgents   = None
        self.__irrespAgentsMap = None

        if _FwDispatcher.__theInstance is not None:
            vlogif._LogOEC(True, -1501)

        _cyclCeaseTimespanMS    = 20
        _runPhaseFrequencyMS = 20

        cyclicMaxProcTimespanMS = None
        _xp = _ExecutionProfile(runPhaseFreqMS_=_runPhaseFrequencyMS, runPhaseMaxProcTimeMS_=cyclicMaxProcTimespanMS, cyclicCeaseTimespanMS_=_cyclCeaseTimespanMS)

        super().__init__(_ERunnableType.eFwDsprRbl, execProfile_=_xp)
        _xp.CleanUp()

        if self._eRunnableType is None:
            self.CleanUp()
            return

        _tout = _Timeout.CreateTimeoutSec(3)
        self.__treg            = _DispatchRegistry(bTaskRegistry_=True)
        self.__mtxApi          = _Mutex()
        self.__mtxData         = _Mutex()
        self.__iqueue          = _FwQueue.CreateInstance(maxSize_=_FwQueue.GetFiniteQueueDefaultSize())
        self.__logAlert        = _TimeAlert(_tout.toNSec)
        self.__pendingAgents   = []
        self.__irrespAgentsMap = _FwDispatcher._DeliveryRetryMap(maxRetry_=_FwDispatcher.__IRRESP_THRESHOLD)

        _tout.CleanUp()

    @staticmethod
    def _GetInstance(bCreate_ =False):
        res = _FwDispatcher.__theInstance

        if res is not None:
            return res
        if not bCreate_:
            return None

        res = _FwDispatcher()
        if res._eRunnableType is None:
            res.CleanUp()
            return None

        _trm   = _ETaskRightFlag.FwTaskRightDefaultMask()
        _tname = _AbstractRunnableFWC.GetFwcTaskName(_EFwcID.eFwDispatcher)
        _ta    = { _TaskProfile._ATTR_KEY_RUNNABLE    : res
                 , _TaskProfile._ATTR_KEY_TASK_NAME   : _tname
                 , _TaskProfile._ATTR_KEY_TASK_RIGHTS : _trm }
        _tp = _TaskProfile(taskProfileAttrs_=_ta)

        if res.__iqueue is None:
            vlogif._LogOEC(True, -1502)
            _tp.CleanUp()
            res.CleanUp()
            res = None
        else:
            _FwDispatcher.__theInstance    = res
            _FwDispatcher.__theTaskProfile = _tp

        return res

    @staticmethod
    def _DeserializeMsg(bXMsg_: bool, msgUID_: int, msgDump_: bytes, pldDump_=None, bCustomPL_=None, customDesCallback_=None):
        _pldDes = None

        if pldDump_ is not None:
            _bCustomSD = bCustomPL_
            _bNonSD    = not _bCustomSD

            if _bCustomSD:
                try:
                    _pldDes = customDesCallback_(pldDump_)
                except (Exception, BaseException) as xcp:
                    logif._LogError(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwDispatcher_TextID_010).format(msgUID_, xcp))
                    return None

                if not (isinstance(_pldDes, XPayloadIF) and _pldDes.isValidPayload):
                    logif._LogError(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwDispatcher_TextID_011).format(msgUID_))
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
            res = _XMsgMgrImpl._DeserializeXcoMsg(msgDump_)

        if res is None:
            logif._LogError(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwDispatcher_TextID_009).format(msgUID_))
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
        with self.__mtxApi:
            return self.__treg._regSize

    def _RegisterAgentDispatchFilter(self, dispFilter_  : _DispatchFilter, dispAgent_ : _DispatchAgentIF, callback_ : _CallableIF =None) -> bool:
        if self._isInvalid or not self.isRunning:
            return False
        if not (isinstance(dispFilter_, _DispatchFilter) and dispFilter_.isValid):
            return False
        with self.__mtxApi:
            return self.__treg._InsertDispatchFilter(dispFilter_, dispAgent_, callback_=callback_)

    def _DeregisterAgentDispatchFilter(self, dispFilter_  : _DispatchFilter, dispAgent_ : _DispatchAgentIF, callback_ : _CallableIF =None) -> bool:
        if self._isInvalid or not self.isRunning:
            return False
        if not (isinstance(dispFilter_, _DispatchFilter) and dispFilter_.isValid):
            return False
        with self.__mtxApi:
            return self.__treg._EraseDispatchFilter(dispFilter_, dispAgent_, callback_=callback_)

    def _DispatchMessage(self, msg_ : _MessageIF) -> bool:
        if not _FwSubsystemCoding.IsSubsystemMessagingConfigured():
            return False

        if self._isInvalid or self._isInLcCeaseMode or not self.isRunning:
            vlogif._LogOEC(True, -1503)
            return False
        if not (isinstance(msg_, _MessageIF) and msg_.isValid and not msg_.isInternalMsg):
            vlogif._LogOEC(True, -1504)
            return False

        _pldOrig       = msg_.payload
        _bNonSerDes    = (_pldOrig is not None) and not _pldOrig.isMarshalingRequired
        _bSerDesErr    = False
        _bCustomSerDes = False

        _pldDump = None

        _customSerCallback = None
        _customDesCallback = None

        if (_pldOrig is None) or _bNonSerDes:
            if _bNonSerDes:
                _pldOrig = msg_.AttachPayload(None)

        else:
            if _pldOrig.isCustomMarshalingRequired:
                if not _FwSubsystemCoding.IsCustomPayloadSerDesEnabled():
                    return False

                _bCustomSerDes = True

                try:
                    _customSerCallback = _pldOrig.__class__.SerializePayload
                    _customDesCallback = _pldOrig.__class__.DeserializePayload

                    _pldDump = _customSerCallback(_pldOrig)
                except (Exception, BaseException) as xcp:
                    _bSerDesErr = True
                    logif._LogError(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwDispatcher_TextID_007).format(msg_.header, xcp))

                if not isinstance(_pldDump, bytes):
                    if not _bSerDesErr:
                        _bSerDesErr = True
                        logif._LogError(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwDispatcher_TextID_008).format(msg_.header))
                else:
                    _pldOrig = msg_.AttachPayload(None)

        if _bSerDesErr:
            if _bNonSerDes:
                msg_.AttachPayload(_pldOrig)
            return False

        if msg_.isFwMsg:
            _dump = _FwMessage.SerializeFwMsg(msg_)
        else:
            _dump = _XMsgMgrImpl._SerializeXcoMsg(msg_)

        if _dump is None:
            if _bNonSerDes or _bCustomSerDes:
                msg_.AttachPayload(_pldOrig)
            return False

        _allTgt   = None
        _retryMap = dict()
        _lstPending = []

        with self.__mtxApi:
            _allTgt = self.__treg._GetAllDispatchTargets(msg_.header)

            if _allTgt is None:
                del _dump
                if _bNonSerDes or _bCustomSerDes:
                    msg_.AttachPayload(_pldOrig)
                logif._LogError(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwDispatcher_TextID_001).format(msg_.header))
                return False



        with self.__mtxData:
            _numPushed = 0
            _bMultiTgt = len(_allTgt) > 1

            for _dt in _allTgt:
                if not self.isRunning:
                    del _dump
                    if _bNonSerDes or _bCustomSerDes:
                        msg_.AttachPayload(_pldOrig)
                    return False

                _dagt = _dt._dispatchAgent
                _atid = None if not _dt.isValid else _dagt._agentTaskID

                if (_atid is None) or not _dagt._isOperating:
                    if _atid is None:
                        logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwDispatcher_TextID_005).format(msg_.header))
                    else:
                        logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwDispatcher_TextID_002).format(_atid, msg_.header))
                        self.__irrespAgentsMap.RemoveTask(_atid)
                    continue

                if _atid in self.__pendingAgents:
                    _lstPending.append(_dt)
                    _retryMap[_atid] = 2 if self.__irrespAgentsMap.IsThresholdReached(_atid) else 0
                    continue

                if _bNonSerDes:
                    _pldTgt = _pldOrig
                    _bCustomPL = False
                elif _bCustomSerDes:
                    _pldTgt = bytes(_pldDump) if _bMultiTgt else _pldDump
                    _bCustomPL = True
                else:
                    _pldTgt    = None
                    _bCustomPL = None

                _dumpTgt = bytes(_dump) if _bMultiTgt else _dump

                _opRes = _dagt._PushMessage(msg_, _dumpTgt, _pldTgt, bCustomPL_=_bCustomPL, customDesCallback_=_customDesCallback, callback_=_dt._dispatchCallback)

                if not self.isRunning:
                    return False

                if _opRes.isAbort:
                    self.__irrespAgentsMap.UpdateMap(_atid)

                    if _bMultiTgt:
                        del _dumpTgt
                        if _bCustomSerDes:
                            del _pldTgt
                    continue

                if _opRes.isNOK:
                    if not _dagt._isOperating:
                        self.__irrespAgentsMap.UpdateMap(_atid)

                        if _bMultiTgt:
                            del _dumpTgt
                            if _bCustomSerDes:
                                del _pldTgt

                    elif not self.__irrespAgentsMap.UpdateMap(_atid):
                        _lstPending.append(_dt)
                        _retryMap[_atid] = 1
                    continue

                _numPushed += 1
                self.__irrespAgentsMap.RemoveTask(_atid)

            _bPushedAny  = _numPushed > 0
            _bBackLogged = False

            if len(_lstPending) > 0:
                if _bNonSerDes:
                    _pldTgt    = _pldOrig
                    _bCustomPL = False
                elif _bCustomSerDes:
                    _pldTgt    = _pldDump
                    _bCustomPL = True
                else:
                    _pldTgt    = None
                    _bCustomPL = None

                _bl = _FwDispatcher._DispBackLogEntry(msg_.isXcoMsg, msg_.uniqueID, _dump, _lstPending, _retryMap, pldDump_=_pldTgt, bCustomPL_=_bCustomPL, customDesCallback_=_customDesCallback)

                if not self.__iqueue.PushNowait(_bl):
                    _bl.CleanUp()
                    _myTxt = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_027).join([str(_ee._dispatchAgent._agentTaskID) for _ee in _lstPending])
                    logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwDispatcher_TextID_003).format(self.__iqueue.qsize, _myTxt, msg_.header))
                else:
                    _bBackLogged = True
                    for _dt in _lstPending:
                        _dagt = _dt._dispatchAgent
                        if _dagt._agentTaskID not in self.__pendingAgents:
                            self.__pendingAgents.append(_dagt._agentTaskID)

            if not _bBackLogged:
                if (not _bPushedAny) or _bMultiTgt:
                    del _dump
                    if _pldDump is not None:
                        del _pldDump
            if _bNonSerDes or _bCustomSerDes:
                msg_.AttachPayload(_pldOrig)

            return _bPushedAny or _bBackLogged

    def _ToString(self, *args_, **kwargs_):
        if self._isInvalid:
            return None

        _verbose = False
        _lstArgs = _ListUtil.UnpackArgs(*args_, minArgsNum_=0, maxArgsNum_=1, bThrowx_=True)
        if len(_lstArgs) > 0:
            _verbose = _lstArgs[0]

        _midPart = '(#regCards)=({})'.format(self._numRegisterations)
        _myargs = (_verbose, _midPart)
        return _AbstractRunnableFWC._ToString(self, *_myargs)

    def _CleanUp(self):
        if _FwDispatcher.__theInstance is None:
            return

        _FwDispatcher.__theInstance = None

        if _FwDispatcher.__theTaskProfile is not None:
            _FwDispatcher.__theTaskProfile.CleanUp()
            _FwDispatcher.__theTaskProfile = None

        _mtx = self.__mtxApi
        if _mtx is not None:
            with _mtx:
                self.__mtxApi = None

                self.__logAlert = None

                if self.__irrespAgentsMap is not None:
                    self.__irrespAgentsMap.CleanUp()
                    self.__irrespAgentsMap = None

                if self.__pendingAgents is not None:
                    self.__pendingAgents.clear()
                    self.__pendingAgents = None

                if self.__iqueue is not None:
                    self.__iqueue.CleanUp()
                    self.__iqueue = None

                self.__treg.CleanUp()
                self.__treg = None

                self.__mtxData.CleanUp()
                self.__mtxData = None
    
            _mtx.CleanUp()

        super()._CleanUp()

    def _OnRunProgressNotification(self, eRunProgressID_ : _ERunProgressID):
        return self.isRunning

    def _SetUpRunnable(self):
        if self.__iqueue is None:
            vlogif._LogOEC(True, -1505)
            return False
        return True

    def _TearDownRunnable(self):
        return False

    def _RunExecutable(self):
        if not self.isRunning:
            return False
        self.__treg._DropInvalidTargets()
        return self.__ProcFwDispInternalQueue()


    def __ProcFwDispInternalQueue(self) -> bool:
        with self.__mtxData:
            _blNum = self.__iqueue.qsize
            if _blNum < 1:
                self.__pendingAgents.clear()
                return self.isRunning

            _ii, _lstBL = _blNum, []
            while _ii > 0:
                _bl = self.__iqueue.PopNowait()
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

                _lstPending = []
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
                            logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwDispatcher_TextID_005).format(_msg.header))
                        else:
                            logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwDispatcher_TextID_002).format(_atid, _msg.header))
                            self.__irrespAgentsMap.RemoveTask(_atid)
                        continue

                    if self.__irrespAgentsMap.IsThresholdReached(_atid):
                        continue

                    _opRes = _dagt._PushMessage(_msg, _dump, _dumpPLD, bCustomPL_=_bl._bCustomPayload, customDesCallback_=_bl._customDesCallback, callback_=_dt._dispatchCallback)

                    if not self.isRunning:
                        return False

                    if _opRes.isAbort:
                        self.__irrespAgentsMap.UpdateMap(_atid)
                        continue

                    if _opRes.isNOK:
                        if not _dagt._isOperating:
                            self.__irrespAgentsMap.UpdateMap(_atid)

                        elif not self.__irrespAgentsMap.UpdateMap(_atid):
                            _lstPending.append(_dt)
                        continue

                    self.__irrespAgentsMap.RemoveTask(_atid)

                if len(_lstPending) > 0:
                    _lstMaxRetryReached =_bl._UpdateDispTargetList(_lstPending)
                    _lstPending = _bl._dispatchTargets

                    if _lstMaxRetryReached is not None:
                        _myTxt = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_027).join([str(_ee._dispatchAgent._agentTaskID) for _ee in _lstMaxRetryReached])
                        logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwDispatcher_TextID_004).format(_FwDispatcher._DispBackLogEntry._MAX_RETRY_COUNT, _myTxt, _msg.uniqueID, _msg.header))
                    if _lstPending is None:
                        _bl.CleanUp()
                        break

                    if not self.__iqueue.PushNowait(_bl):
                        _myTxt = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_027).join([str(_ee._dispatchAgent._agentTaskID) for _ee in _lstPending])
                        logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwDispatcher_TextID_003).format(self.__iqueue.qsize, _myTxt, _msg.header))
                        _bl.CleanUp()

                    else:
                        for _dt in _lstPending:
                            _atid = _dt._dispatchAgent._agentTaskID
                            if _atid not in _lstPendingAgents:
                                _lstPendingAgents.append(_atid)
                else:
                    _bl.CleanUp()

            self.__pendingAgents.clear()
            if len(_lstPendingAgents) > 0:
                self.__pendingAgents.extend(_lstPendingAgents)

            return self.isRunning
