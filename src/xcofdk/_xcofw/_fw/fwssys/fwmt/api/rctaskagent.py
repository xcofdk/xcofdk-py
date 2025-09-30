# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : rctaskagent.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from typing import Any   as _PyAny
from typing import Union
from enum   import IntEnum

from xcofdk.fwcom              import CompoundTUID
from xcofdk.fwcom              import EExecutionCmdID
from xcofdk.fwcom              import EXmsgPredefinedID
from xcofdk.fwapi              import IMessage
from xcofdk.fwapi              import ITaskError
from xcofdk.fwapi              import IPayload
from xcofdk.fwapi              import IRCTask
from xcofdk.fwapi              import IRCCommTask
from xcofdk.fwapi.xmt          import XTask
from xcofdk.fwapi.xmt          import XMainTask
from xcofdk.fwapi.xmsg.xmsgmgr import XMessenger as _XMsgMgr

from _fw.fwssys.assys                    import fwsubsysshare as _ssshare
from _fw.fwssys.fwcore.logging           import vlogif
from _fw.fwssys.fwcore.logging           import logif
from _fw.fwssys.fwmt.xcbcase             import _XCbCase
from _fw.fwssys.fwmt.xtaskprfext         import _XTaskPrfExt
from _fw.fwssys.fwcore.types.commontypes import override
from _fw.fwssys.fwcore.types.commontypes import _CommonDefines
from _fw.fwssys.fwerrh.fwerrorcodes      import _EFwErrorCode
from _fw.fwssys.fwmt.utask.usertaskdefs  import _UTaskMirror
from _fwa.fwsubsyscoding                 import _FwSubsysCoding

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _RCTAgentBase:
    __slots__ = [ '__cbc' , '__rctm' , '__cbRun' , '__cbPXM' , '__rcInst' ]

    def __init__(self):
        self.__cbc    = None
        self.__rctm   = None
        self.__cbRun  = None
        self.__cbPXM  = None
        self.__rcInst = None

    def __str__(self):
        return self._ToString()

    def _RcIsAttachedToFW(self):
        return False if self.__isInvalid else self.__asXTask.isAttachedToFW

    def _RcIsDetachedFromFW(self):
        return True if self.__isInvalid else self.__asXTask.isDetachedFromFW

    def _RcIsMainTask(self) -> bool:
        return False if self.__isInvalid else self.__rctm.mrUTaskProfile.isMainTask

    def _RcIsSyncTask(self) -> bool:
        return False if self.__isInvalid else self.__rctm.mrUTaskProfile.isSyncTask

    def _RcIsMsgTask(self):
        return False if self.__isInvalid else isinstance(self, IRCCommTask)

    def _RcIsXQueueBlocking(self) -> bool:
        return False if self.__isInvalid else self.__rctm.mrUTaskProfile.isExternalQueueBlocking

    def _RcIsStarted(self) -> bool:
        return False if self.__isInvalid else self.__asXTask.isStarted

    def _RcIsPendingRun(self) -> bool:
        return False if self.__isInvalid else self.__asXTask.isPendingRun

    def _RcIsRunning(self) -> bool:
        return False if self.__isInvalid else self.__asXTask.isRunning

    def _RcIsDone(self) -> bool:
        return False if self.__isInvalid else self.__asXTask.isDone

    def _RcIsCanceled(self) -> bool:
        return False if self.__isInvalid else self.__asXTask.isCanceled

    def _RcIsFailed(self) -> bool:
        return False if self.__isInvalid else self.__asXTask.isFailed

    def _RcIsTerminated(self) -> bool:
        return False if self.__isInvalid else self.__asXTask.isTerminated

    def _RcIsTerminating(self) -> bool:
        return False if self.__isInvalid else self.__asXTask.isTerminating

    def _RcIsStopping(self) -> bool:
        return False if self.__isInvalid else self.__asXTask.isStopping

    def _RcIsCanceling(self) -> bool:
        return False if self.__isInvalid else self.__asXTask.isCanceling

    def _RcIsErrorFree(self) -> bool:
        return False if self.__isInvalid else self.__asXTask.isErrorFree

    def _RcIsFatalErrorFree(self) -> bool:
        return False if self.__isInvalid else self.__asXTask.isFatalErrorFree

    def _RcIsFirstRunPhaseIteration(self) -> bool:
        return False if self.__isInvalid else self.__asXTask.isFirstRunPhaseIteration

    def _RcCurrentRunPhaseIterationNo(self) -> int:
        return -1 if self.__isInvalid else self.__asXTask.currentRunPhaseIterationNo

    def _RcRunPhaseFrequencyMS(self):
        return -1 if self.__isInvalid else self.__rctm.mrUTaskProfile.runPhaseFrequencyMS

    def _RcPhasedXFInstance(self):
        return None if self.__isInvalid else self.__cbc.phasedXFInst

    def _RcTaskUID(self) -> Union[int, None]:
        return None if self.__isInvalid else self.__asXTask.taskUID

    def _RcTaskName(self) -> Union[str, None]:
        return None if self.__isInvalid else self.__asXTask.taskName

    def _RcTaskAliasName(self) -> Union[str, None]:
        return None if self.__isInvalid else self.__asXTask.aliasName

    def _RcTaskCompUID(self) -> Union[CompoundTUID, None]:
        return None if self.__isInvalid else self.__asXTask.taskCompoundUID

    def _RcCurrentError(self) -> Union[ITaskError, None]:
        return None if self.__isInvalid else self.__asXTask.currentError

    def _RcClearCurrentError(self) -> bool:
        return False if self.__isInvalid else self.__asXTask.ClearCurrentError()

    def _RcSetError(self, errorMsg_ : str):
        if not self.__isInvalid:
            self.__asXTask.SetError(errorMsg_)

    def _RcSetErrorEC(self, errorMsg_ : str, errCode_: int):
        if not self.__isInvalid:
            self.__asXTask.SetErrorEC(errorMsg_, errCode_)

    def _RcSetFatalError(self, errorMsg_ : str):
        if not self.__isInvalid:
            self.__asXTask.SetFatalError(errorMsg_)

    def _RcSetFatalErrorEC(self, errorMsg_ : str, errCode_: int):
        if not self.__isInvalid:
            self.__asXTask.SetFatalErrorEC(errorMsg_, errCode_)

    def _RcSetUpTask(self, *args_, **kwargs_) -> EExecutionCmdID:
        if self._RcIsDetachedFromFW():
            return EExecutionCmdID.STOP
        _cb = self.__cbc.setupCallback
        return _cb(self.__rcInst, *args_, **kwargs_) if self.__cbc.isGeneric else _cb(*args_, **kwargs_)

    def _RcRunTask(self, *args_, **kwargs_) -> EExecutionCmdID:
        if self._RcIsDetachedFromFW():
            return EExecutionCmdID.STOP
        return self.__cbRun(self.__rcInst, *args_, **kwargs_) if self.__cbc.isGeneric else self.__cbRun(*args_, **kwargs_)

    def _RcTearDownTask(self) -> EExecutionCmdID:
        if self._RcIsDetachedFromFW():
            return EExecutionCmdID.STOP
        _cb = self.__cbc.teardownCallback
        return _cb(self.__rcInst) if self.__cbc.isGeneric else _cb()

    def _RcProcExtMsg(self, xmsg_: IMessage) -> EExecutionCmdID:
        if self._RcIsDetachedFromFW():
            return EExecutionCmdID.STOP
        return self.__cbPXM(self.__rcInst, xmsg_) if self.__cbc.isGeneric else self.__cbPXM(xmsg_)

    def _RcStart(self, *args_, **kwargs_) -> bool:
        return False if self.__isInvalid else self.__asXTask.Start(*args_, **kwargs_)

    def _RcStop(self) -> bool:
        return False if self.__isInvalid else self.__asXTask.Stop()

    def _RcCancel(self) -> bool:
        return False if self.__isInvalid else self.__asXTask.Cancel()

    def _RcJoin(self, maxWTime_: Union[int, float] =None) -> bool:
        return False if self.__isInvalid else self.__asXTask.Join(maxWTime_)

    def _RcDetachFromFW(self):
        if not self.__isInvalid:
            self.__asXTask.DetachFromFW()

    def _RcGetTaskData(self, bDeser_ =True) -> _PyAny:
        return None if self.__isInvalid else  self.__asXTask.GetTaskOwnedData(bDeserialize_=bDeser_)

    def _RcSetTaskData(self, tskData_ : _PyAny, bSer_ =False):
        if not self.__isInvalid:
            self.__asXTask.SetTaskOwnedData(tskData_, bSerialize_=bSer_)

    def _RcSelfCheck(self) -> bool:
        return False if self.__isInvalid else self.__asXTask.SelfCheck()

    def _RcSelfCheckSleep(self, st_: Union[int, float] =None) -> bool:
        return False if self.__isInvalid else self.__asXTask.SelfCheckSleep(st_)

    from _fw.fwssys.fwcore.base.timeutil import _TimeUtil
    def _RcSendMsg( self
                  , rxTask_        : Union[IRCCommTask, XTask, IntEnum, int]
                  , msgLabelID_    : Union[IntEnum, int]   =EXmsgPredefinedID.DontCare
                  , msgClusterID_  : Union[IntEnum, int]   =EXmsgPredefinedID.DontCare
                  , msgPayload_    : Union[IPayload, dict] =None) -> int:
        if _ssshare._WarnOnDisabledSubsysMsg(annexID_=_EFwTextID.eMisc_Shared_Disabled_Subsys_Msg):
            return 0
        if isinstance(rxTask_, IRCCommTask):
            rxTask_ = rxTask_.taskUID
        return 0 if self.__isInvalid else _XMsgMgr.SendMessage(rxTask_, msgLabelID_=msgLabelID_, msgClusterID_=msgClusterID_, msgPayload_=msgPayload_)

    def _RcBroadcastMsg( self
                       , msgLabelID_   : Union[IntEnum, int]
                       , msgClusterID_ : Union[IntEnum, int]   =EXmsgPredefinedID.DontCare
                       , msgPayload_   : Union[IPayload, dict] =None) -> int:
        if _ssshare._WarnOnDisabledSubsysMsg(annexID_=_EFwTextID.eMisc_Shared_Disabled_Subsys_Msg):
            return 0
        return 0 if self.__isInvalid else _XMsgMgr.BroadcastMessage(msgLabelID_, msgClusterID_=msgClusterID_, msgPayload_=msgPayload_)

    def _RcTriggerExtQProc(self) -> int:
        if _ssshare._WarnOnDisabledSubsysMsg(annexID_=_EFwTextID.eMisc_Shared_Disabled_Subsys_Msg):
            return -1
        return 0 if self.__isInvalid else self.__asXTask.TriggerExternalQueueProcessing()

    def _SetUpBase(self, cbCase_ : _XCbCase, rctMirror_ : _UTaskMirror, rctInst_ : IRCTask, penvl_ =None):
        self.__cbc    = cbCase_
        self.__rctm   = rctMirror_
        self.__cbRun  = None if cbCase_ is None else cbCase_.runCallback
        self.__cbPXM  = None if cbCase_ is None else cbCase_.procExtMsgCallback
        self.__rcInst = rctInst_

    @staticmethod
    def _EvaluateCtor( xtInst_
                     , rctInst_        : IRCTask
                     , aliasn_         : str =None
                     , cbRun_          =None
                     , cbSetup_        =None
                     , cbTeardown_     =None
                     , cbProcExtMsg_   =None
                     , cbProcIntMsg_   =None
                     , cbPhXFInst_     =None
                     , bSTask_         =False
                     , bMTask_         =False
                     , bMsgTask_       =False
                     , bBlockingExtQ_  =False
                     , bGenericParam_  =False
                     , runFreq_        : Union[int, float] =0
                     , rctClassName_   : str =None):
        if bSTask_ and bBlockingExtQ_:
            _midPart = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskPrfBase_TID_012)
            _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XRCTAgent_TID_001).format(rctClassName_, _midPart)
            logif._XLogErrorEC(_EFwErrorCode.UE_00232, _msg)
            return None, None, None

        _cbc = _XCbCase( rctClassName_=rctClassName_
                       , cbRun_=cbRun_
                       , cbSetup_=cbSetup_
                       , cbTeardown_=cbTeardown_
                       , cbProcExtMsg_=cbProcExtMsg_
                       , cbProcIntMsg_=cbProcIntMsg_
                       , cbPhXFInst_=cbPhXFInst_
                       , bMsgCase_=bMsgTask_
                       , bBlockingExtQ_=bBlockingExtQ_
                       , bGenericParam_=bGenericParam_
                       , bIQueueEnabled_=_FwSubsysCoding.IsInternalQueueSupportEnabled())
        if not _cbc.isValid:
            _cbc.CleanUp()
            return None, None, None

        _xtPrf = _XTaskPrfExt(xtPrf_=None, bMainXT_=bMTask_, rctInst_=rctInst_)
        if _xtPrf.isValid:
            if aliasn_ is not None:
                _xtPrf.aliasName = aliasn_
        if _xtPrf.isValid:
            _xtPrf.isPrivilegedTask = False
        if _xtPrf.isValid:
            _xtPrf.isSyncTask = bSTask_
        if _xtPrf.isValid:
            _xtPrf.runPhaseFrequencyMS = runFreq_

        if _xtPrf.isValid:
            _xtPrf.isSetupPhaseEnabled = _cbc.setupCallback is not None
        if _xtPrf.isValid:
            _xtPrf.isTeardownPhaseEnabled = _cbc.teardownCallback is not None
        if not _ssshare._IsSubsysMsgDisabled():
            if _xtPrf.isValid:
                _xtPrf.isExternalQueueEnabled = _cbc.procExtMsgCallback is not None
            if _xtPrf.isValid:
                _xtPrf.isExternalQueueBlocking = _cbc.runCallback is None

        if not _xtPrf.isValid:
            _xtPrf._CleanUp()
            _cbc.CleanUp()
            return None, None, None

        _utm = _UTaskMirror(xtInst_, _xtPrf, aliasn_, bRcTM_=True)

        _RCTAgentBase.__UnsetPhXFCallbacks(xtInst_, _xtPrf)
        return _cbc, _xtPrf, _utm

    def _ToString(self):
        return _CommonDefines._STR_EMPTY if self.__isInvalid else XTask.__str__(self.__asXTask)

    def _CleanUp(self):
        if self.__cbc is not None:
            self.__cbc.CleanUp()
            self.__cbc = None
        self.__rctm   = None
        self.__rcInst = None

    @property
    def __isInvalid(self):
        return self.__rctm is None

    @property
    def __asXTask(self) -> Union[XTask, None]:
        return None if not isinstance(self, XTask) else self

    @staticmethod
    def __UnsetPhXFCallbacks(xtInst_, xtPrf_ : _XTaskPrfExt):
        _lstEd = [ xtPrf_.isSetupPhaseEnabled, xtPrf_.isRunPhaseEnabled, xtPrf_.isTeardownPhaseEnabled, xtPrf_.isInternalQueueEnabled, xtPrf_.isExternalQueueEnabled]

        _lstAN = [ _EFwTextID.eEUTaskApiID_SetUpXTask, _EFwTextID.eEUTaskApiID_RunXTask, _EFwTextID.eEUTaskApiID_TearDownXTask
                 , _EFwTextID.eEUTaskApiID_ProcessInternalMessage, _EFwTextID.eEUTaskApiID_ProcessExternalMessage ]
        _lstAN = [ _FwTDbEngine.GetText(ee) for ee in _lstAN ]

        _ii, _LEN = 0, len(_lstAN)
        while _ii < _LEN:
            if not _lstEd[_ii]:
                _attrn = _lstAN[_ii]

                try:
                    if getattr(xtInst_, _attrn, None) is not None:
                        setattr(xtInst_, _attrn, None)
                except (AttributeError, Exception):
                    pass
            _ii += 1

class _RCTAgent(XTask, _RCTAgentBase):
    __slots__ = []

    def __init__( self
                , rctInst_        : IRCTask
                , aliasn_         : str =None
                , cbRun_          =None
                , cbSetup_        =None
                , cbTeardown_     =None
                , cbProcExtMsg_   =None
                , cbProcIntMsg_   =None
                , cbPhXFInst_     =None
                , bSTask_         =False
                , bMsgTask_       =False
                , bBlockingExtQ_  =False
                , bGenericParam_  =False
                , runFreq_        : Union[int, float] =0):
        self.__cbc    = None
        self.__rctm   = None
        self.__cbRun  = None
        self.__cbPXM  = None
        self.__rcInst = None
        _RCTAgentBase.__init__(self)

        _cbc, _xtPrf, _utm = None, None, None

        if bMsgTask_ and _ssshare._WarnOnDisabledSubsysMsg(annexID_=_EFwTextID.eMisc_Shared_Disabled_Subsys_Msg):
            pass
        elif bMsgTask_ and not isinstance(rctInst_, IRCCommTask):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00932)
        elif (not bMsgTask_) and not isinstance(rctInst_, IRCTask):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00933)
        else:
            _cbc, _xtPrf, _utm = _RCTAgentBase._EvaluateCtor( self
                                                            , rctInst_
                                                            , aliasn_=aliasn_
                                                            , cbRun_=cbRun_
                                                            , cbSetup_=cbSetup_
                                                            , cbTeardown_=cbTeardown_
                                                            , cbProcExtMsg_=cbProcExtMsg_
                                                            , cbProcIntMsg_=cbProcIntMsg_
                                                            , cbPhXFInst_=cbPhXFInst_
                                                            , bSTask_=bSTask_
                                                            , bMTask_=False
                                                            , bMsgTask_=bMsgTask_
                                                            , bBlockingExtQ_=bBlockingExtQ_
                                                            , bGenericParam_=bGenericParam_
                                                            , runFreq_=runFreq_
                                                            , rctClassName_=rctInst_.__class__.__name__)

        if _xtPrf is None:
            rctInst_ = None
        else:
            _xtPrf._utaskMirror = _utm
            XTask.__init__(self, taskProfile_=_xtPrf)

        self._SetUpBase(_cbc, _utm, rctInst_)

    def __str__(self):
        return _RCTAgentBase.__str__(self)

    @override
    def SetUpXTask(self, *args_, **kwargs_) -> EExecutionCmdID:
        return self._RcSetUpTask(*args_, **kwargs_)

    @override
    def RunXTask(self, *args_, **kwargs_) -> EExecutionCmdID:
        return self._RcRunTask(*args_, **kwargs_)

    @override
    def TearDownXTask(self) -> EExecutionCmdID:
        return self._RcTearDownTask()

    @override
    def ProcessExternalMessage(self, xmsg_: IMessage) -> EExecutionCmdID:
        return self._RcProcExtMsg(xmsg_)

class _RCMTAgent(XMainTask, _RCTAgentBase):
    __slots__ = []

    def __init__( self
                , rctInst_        : IRCTask
                , aliasn_         : str =None
                , cbRun_          =None
                , cbSetup_        =None
                , cbTeardown_     =None
                , cbProcExtMsg_   =None
                , cbProcIntMsg_   =None
                , cbPhXFInst_     =None
                , bSTask_         =False
                , bMsgTask_       =False
                , bBlockingExtQ_  =False
                , bGenericParam_  =False
                , runFreq_        : Union[int, float] =0):
        self.__cbc    = None
        self.__rctm   = None
        self.__cbRun  = None
        self.__cbPXM  = None
        self.__rcInst = None
        _RCTAgentBase.__init__(self)

        _cbc, _xtPrf, _utm = None, None, None

        if bMsgTask_ and _ssshare._WarnOnDisabledSubsysMsg(annexID_=_EFwTextID.eMisc_Shared_Disabled_Subsys_Msg):
            pass
        elif bMsgTask_ and not isinstance(rctInst_, IRCCommTask):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00937)
        elif (not bMsgTask_) and not isinstance(rctInst_, IRCTask):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00938)
        else:
            _cbc, _xtPrf, _utm = _RCTAgentBase._EvaluateCtor( self
                                                            , rctInst_
                                                            , aliasn_=aliasn_
                                                            , cbRun_=cbRun_
                                                            , cbSetup_=cbSetup_
                                                            , cbTeardown_=cbTeardown_
                                                            , cbProcExtMsg_=cbProcExtMsg_
                                                            , cbProcIntMsg_=cbProcIntMsg_
                                                            , cbPhXFInst_=cbPhXFInst_
                                                            , bSTask_=bSTask_
                                                            , bMTask_=True
                                                            , bMsgTask_=bMsgTask_
                                                            , bBlockingExtQ_=bBlockingExtQ_
                                                            , bGenericParam_=bGenericParam_
                                                            , runFreq_=runFreq_
                                                            , rctClassName_=rctInst_.__class__.__name__)
        if _xtPrf is None:
            rctInst_ = None
        else:
            _xtPrf._utaskMirror = _utm
            XTask.__init__(self, taskProfile_=_xtPrf)

        self._SetUpBase(_cbc, _utm, rctInst_, None)

    def __str__(self):
        return _RCTAgentBase.__str__(self)

    @override
    def SetUpXTask(self, *args_, **kwargs_) -> EExecutionCmdID:
        return self._RcSetUpTask(*args_, **kwargs_)

    @override
    def RunXTask(self, *args_, **kwargs_) -> EExecutionCmdID:
        return self._RcRunTask(*args_, **kwargs_)

    @override
    def TearDownXTask(self) -> EExecutionCmdID:
        return self._RcTearDownTask()

    @override
    def ProcessExternalMessage(self, xmsg_: IMessage) -> EExecutionCmdID:
        return self._RcProcExtMsg(xmsg_)
