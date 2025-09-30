# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : lcstate.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum   import auto
from enum   import unique
from typing import Union

from _fw.fwssys.fwcore.logging            import vlogif
from _fw.fwssys.fwcore.base.strutil       import _StrUtil
from _fw.fwssys.fwcore.logging.logdefines import _EErrorImpact
from _fw.fwssys.fwcore.logging.logdefines import _LogErrorCode
from _fw.fwssys.fwcore.ipc.tsk.afwtask    import _AbsFwTask
from _fw.fwssys.fwcore.ipc.tsk.taskutil   import _TaskUtil
from _fw.fwssys.fwcore.ipc.tsk.taskutil   import _PyRLock
from _fw.fwssys.fwcore.lc.lcdefines       import _ELcCompID
from _fw.fwssys.fwcore.lc.lcxstate        import _LcFailure
from _fw.fwssys.fwcore.lc.ifs.iflcstate   import _ILcState
from _fw.fwssys.fwcore.types.ebitmask     import _EBitMask
from _fw.fwssys.fwcore.types.commontypes  import _FwIntFlag
from _fw.fwssys.fwcore.types.commontypes  import _FwIntEnum
from _fw.fwssys.fwcore.types.commontypes  import _EExecutionCmdID
from _fw.fwssys.fwcore.types.commontypes  import _CommonDefines
from _fw.fwssys.fwerrh.fwerrorcodes       import _EFwErrorCode
from _fw.fwssys.fwerrh.logs.errorlog      import _FatalLog
from _fw.fwssys.fwerrh.lcfrcview          import _LcFrcView

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

@unique
class _ELcStateFlag(_FwIntFlag):
    ebfIdle             = 0x000000
    ebfLcStarted        = (0x000001 <<  0)
    ebfTMgrStarted      = (0x000001 <<  1)
    ebfFwCompStarted    = (0x000001 <<  2)
    ebfFwMainStarted    = (0x000001 <<  3)
    ebfUThreadStarted   = (0x000001 <<  4)
    ebfXTaskStarted     = (0x000001 <<  5)
    ebfMainXTaskStarted = (0x000001 <<  6)
    ebfMiscCompStarted  = (0x000001 <<  7)
    ebfMiscCompStopped  = (0x000001 <<  8)
    ebfMainXTaskStopped = (0x000001 <<  9)
    ebfXTaskStopped     = (0x000001 << 10)
    ebfUThreadStopped   = (0x000001 << 11)
    ebfFwMainStopped    = (0x000001 << 12)
    ebfFwCompStopped    = (0x000001 << 13)
    ebfTMgrStopped      = (0x000001 << 14)
    ebfLcStopped        = (0x000001 << 15)
    ebfLcFailed         = (0x010000 <<  0)
    ebfTMgrFailed       = (0x010000 <<  1)
    ebfFwCompFailed     = (0x010000 <<  2)
    ebfFwMainFailed     = (0x010000 <<  3)
    ebfUThreadFailed    = (0x010000 <<  4)
    ebfXTaskFailed      = (0x010000 <<  5)
    ebfMainXTaskFailed  = (0x010000 <<  6)
    ebfMiscCompFailed   = (0x010000 <<  7)

    @staticmethod
    def IsLcIdle(eLcBitMask_ : _FwIntFlag):
        return eLcBitMask_==_ELcStateFlag.ebfIdle

    @staticmethod
    def IsLcStarted(eLcBitMask_ : _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eLcBitMask_, _ELcStateFlag.ebfLcStarted)

    @staticmethod
    def IsTMgrStarted(eLcBitMask_ : _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eLcBitMask_, _ELcStateFlag.ebfTMgrStarted)

    @staticmethod
    def IsFwCompStarted(eLcBitMask_ : _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eLcBitMask_, _ELcStateFlag.ebfFwCompStarted)

    @staticmethod
    def IsFwMainStarted(eLcBitMask_ : _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eLcBitMask_, _ELcStateFlag.ebfFwMainStarted)

    @staticmethod
    def IsUThreadStarted(eLcBitMask_ : _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eLcBitMask_, _ELcStateFlag.ebfUThreadStarted)

    @staticmethod
    def IsXTaskStarted(eLcBitMask_ : _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eLcBitMask_, _ELcStateFlag.ebfXTaskStarted)

    @staticmethod
    def IsMainXTaskStarted(eLcBitMask_ : _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eLcBitMask_, _ELcStateFlag.ebfMainXTaskStarted)

    @staticmethod
    def IsMiscCompStarted(eLcBitMask_ : _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eLcBitMask_, _ELcStateFlag.ebfMiscCompStarted)

    @staticmethod
    def IsLcStopped(eLcBitMask_ : _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eLcBitMask_, _ELcStateFlag.ebfLcStopped)

    @staticmethod
    def IsTMgrStopped(eLcBitMask_ : _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eLcBitMask_, _ELcStateFlag.ebfTMgrStopped)

    @staticmethod
    def IsFwCompStopped(eLcBitMask_ : _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eLcBitMask_, _ELcStateFlag.ebfFwCompStopped)

    @staticmethod
    def IsFwMainStopped(eLcBitMask_ : _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eLcBitMask_, _ELcStateFlag.ebfFwMainStopped)

    @staticmethod
    def IsUThreadStopped(eLcBitMask_ : _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eLcBitMask_, _ELcStateFlag.ebfUThreadStopped)

    @staticmethod
    def IsXTaskStopped(eLcBitMask_ : _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eLcBitMask_, _ELcStateFlag.ebfXTaskStopped)

    @staticmethod
    def IsMainXTaskStopped(eLcBitMask_ : _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eLcBitMask_, _ELcStateFlag.ebfMainXTaskStopped)

    @staticmethod
    def IsMiscCompStopped(eLcBitMask_ : _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eLcBitMask_, _ELcStateFlag.ebfMiscCompStopped)

    @staticmethod
    def IsLcFailed(eLcBitMask_ : _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eLcBitMask_, _ELcStateFlag.ebfLcFailed)

    @staticmethod
    def IsTMgrFailed(eLcBitMask_ : _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eLcBitMask_, _ELcStateFlag.ebfTMgrFailed)

    @staticmethod
    def IsFwCompFailed(eLcBitMask_ : _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eLcBitMask_, _ELcStateFlag.ebfFwCompFailed)

    @staticmethod
    def IsFwMainFailed(eLcBitMask_ : _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eLcBitMask_, _ELcStateFlag.ebfFwMainFailed)

    @staticmethod
    def IsUThreadFailed(eLcBitMask_ : _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eLcBitMask_, _ELcStateFlag.ebfUThreadFailed)

    @staticmethod
    def IsXTaskFailed(eLcBitMask_ : _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eLcBitMask_, _ELcStateFlag.ebfXTaskFailed)

    @staticmethod
    def IsMainXTaskFailed(eLcBitMask_ : _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eLcBitMask_, _ELcStateFlag.ebfMainXTaskFailed)

    @staticmethod
    def IsMiscCompFailed(eLcBitMask_ : _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eLcBitMask_, _ELcStateFlag.ebfMiscCompFailed)

    @staticmethod
    def LcDefaultMask():
        return _ELcStateFlag(_ELcStateFlag.ebfIdle)

    @staticmethod
    def AddLcBitFlag(eLcBitMask_ : _FwIntFlag, eLcBitFlag_):
        return _EBitMask.AddEnumBitFlag(eLcBitMask_, eLcBitFlag_)

    @staticmethod
    def RemoveLcBitFlag(eLcBitMask_ : _FwIntFlag, eLcBitFlag_):
        return _EBitMask.RemoveEnumBitFlag(eLcBitMask_, eLcBitFlag_)

    @staticmethod
    def IsLcBitFlagSet(eLcBitMask_ : _FwIntFlag, eLcBitFlag_):
        return _EBitMask.IsEnumBitFlagSet(eLcBitMask_, eLcBitFlag_)

    @staticmethod
    def IsLcBitMaskExclusive(eLcBitMask_ : _FwIntFlag):
        res = False
        for _n, _m in _ELcStateFlag.__members__.items():
            if eLcBitMask_ == _m.value:
                res = True
                break
        return res

    @staticmethod
    def IsAnyStoppedBitFlagSet(eLcBitMask_ : _FwIntFlag):
        _lstbf = [ _ELcStateFlag.ebfLcStopped
                 , _ELcStateFlag.ebfTMgrStopped
                 , _ELcStateFlag.ebfFwMainStopped
                 , _ELcStateFlag.ebfMainXTaskStopped
                 , _ELcStateFlag.ebfMiscCompStopped  ]
        return _EBitMask.IsEnumBitFlagSet(eLcBitMask_, _lstbf)

    @staticmethod
    def IsAnyFailedBitFlagSet(eLcBitMask_ : _FwIntFlag):
        return eLcBitMask_ >= _ELcStateFlag.ebfLcFailed

@unique
class _ELcStateTransReq(_FwIntEnum):
    eLcFailed       = _ELcCompID.eLcMgr.value
    eLcStarted      =  -1*eLcFailed
    eLcStopped      = eLcStarted-1
    eTMgrFailed     = _ELcCompID.eTMgr.value
    eTMgrStarted    = -1*eTMgrFailed
    eTMgrStopped    =  eTMgrStarted-1
    eFwSrvFailed    = _ELcCompID.eFwSrv.value
    eFwSrvStarted   = -1*eFwSrvFailed
    eFwSrvStopped   = eFwSrvStarted-1
    eXTaskFailed    = _ELcCompID.eXTask.value
    eXTaskStarted   = -1*eXTaskFailed
    eXTaskStopped   = eXTaskStarted-1

    eMiscCompFailed  = _ELcCompID.eMiscComp.value
    eMiscCompStarted = -1*eMiscCompFailed
    eMiscCompStopped = eMiscCompStarted-1

    @property
    def isStartTransitionRequest(self):
        return (self.value > 0) and ((self.value % 10) == 1)

    @property
    def isStopTransitionRequest(self):
        return (self.value > 0) and ((self.value % 10) == 0)

    @property
    def isFailureTransitionRequest(self):
        return self.value < 0

    @property
    def compactName(self) -> str:
        if   self == _ELcStateTransReq.eLcFailed        : res = _FwTDbEngine.GetText(_EFwTextID.eLcStateImpl_ELcStateTransReq_LcFailed)
        elif self == _ELcStateTransReq.eLcStarted       : res = _FwTDbEngine.GetText(_EFwTextID.eLcStateImpl_ELcStateTransReq_LcStarted)
        elif self == _ELcStateTransReq.eLcStopped       : res = _FwTDbEngine.GetText(_EFwTextID.eLcStateImpl_ELcStateTransReq_LcStopped)
        elif self == _ELcStateTransReq.eTMgrFailed      : res = _FwTDbEngine.GetText(_EFwTextID.eLcStateImpl_ELcStateTransReq_TMgrFailed)
        elif self == _ELcStateTransReq.eTMgrStarted     : res = _FwTDbEngine.GetText(_EFwTextID.eLcStateImpl_ELcStateTransReq_TMgrStarted)
        elif self == _ELcStateTransReq.eTMgrStopped     : res = _FwTDbEngine.GetText(_EFwTextID.eLcStateImpl_ELcStateTransReq_TMgrStopped)
        elif self == _ELcStateTransReq.eFwSrvFailed     : res = _FwTDbEngine.GetText(_EFwTextID.eLcStateImpl_ELcStateTransReq_FwSrvFailed)
        elif self == _ELcStateTransReq.eFwSrvStarted    : res = _FwTDbEngine.GetText(_EFwTextID.eLcStateImpl_ELcStateTransReq_FwSrvStarted)
        elif self == _ELcStateTransReq.eFwSrvStopped    : res = _FwTDbEngine.GetText(_EFwTextID.eLcStateImpl_ELcStateTransReq_FwSrvStopped)
        elif self == _ELcStateTransReq.eXTaskFailed     : res = _FwTDbEngine.GetText(_EFwTextID.eLcStateImpl_ELcStateTransReq_XTaskFailed)
        elif self == _ELcStateTransReq.eXTaskStarted    : res = _FwTDbEngine.GetText(_EFwTextID.eLcStateImpl_ELcStateTransReq_XTaskStarted)
        elif self == _ELcStateTransReq.eXTaskStopped    : res = _FwTDbEngine.GetText(_EFwTextID.eLcStateImpl_ELcStateTransReq_XTaskStopped)
        elif self == _ELcStateTransReq.eMiscCompFailed  : res = _FwTDbEngine.GetText(_EFwTextID.eLcStateImpl_ELcStateTransReq_MiscCompFailed)
        elif self == _ELcStateTransReq.eMiscCompStarted : res = _FwTDbEngine.GetText(_EFwTextID.eLcStateImpl_ELcStateTransReq_MiscCompStarted)
        elif self == _ELcStateTransReq.eMiscCompStopped : res = _FwTDbEngine.GetText(_EFwTextID.eLcStateImpl_ELcStateTransReq_MiscCompStopped)
        else:
            res = _CommonDefines._STR_EMPTY
        return res

    @staticmethod
    def _ConvertFromLcCompID(lcCID_ : _ELcCompID, bStartStopFailFlag_ : Union[bool, None]):
        if not isinstance(lcCID_, _ELcCompID):
            return None

        _gid = lcCID_.lcCompGroupID

        if _gid == _ELcCompID.eLcMgr:
            res = _ELcStateTransReq.eLcFailed
        elif _gid == _ELcCompID.eTMgr:
            res = _ELcStateTransReq.eTMgrFailed
        elif _gid == _ELcCompID.eFwSrv:
            res = _ELcStateTransReq.eFwSrvFailed
        elif _gid == _ELcCompID.eXTask:
            res = _ELcStateTransReq.eXTaskFailed
        else:  
            res = _ELcStateTransReq.eMiscCompFailed

        if bStartStopFailFlag_ is not None:
            val = -1 * res.value
            if not bStartStopFailFlag_:
                val -= 1
            res = _ELcStateTransReq(val)
        return res

@unique
class _EFrcRecTaskType(_FwIntFlag):
    eByHThrd = 0
    eByThrd  = auto()
    eByTsk   = auto()

class _TransReqPreCheckResult:
    __slots__ = [ '__c' , '__t' , '__f' , '__p' , '__fr' , '__fs' , '__ff' , '__bR' , '__bS' , '__ps' , '__tr' , '__bF' , '__fi' ]

    def __init__(self, a1_, a2_, a3_, a4_, a5_, a6_, a7_, a8_, a9_, a10_, a11_, a12_, a13_):
        self.__c  = a4_
        self.__f  = a2_
        self.__p  = a5_
        self.__t  = a1_
        self.__bF = a12_
        self.__bR = a13_
        self.__bS = a11_
        self.__ff = a8_
        self.__fi = a10_
        self.__fr = a7_
        self.__fs = a9_
        self.__ps = a6_
        self.__tr = a3_

    @property
    def lcTrans(self):
        return self.__tr

    @property
    def lcCompID(self):
        return self.__c

    @property
    def fatalError(self):
        return self.__f

    @property
    def absTask(self):
        return self.__t

    @property
    def paramsStr(self):
        return self.__p

    @property
    def paramsCurStateStr(self):
        return self.__ps

    @property
    def ebfRequest(self):
        return self.__fr

    @property
    def ebfRequestInv(self):
        return self.__fi

    @property
    def ebfCpStopped(self):
        return self.__fs

    @property
    def ebfCpFailed(self):
        return self.__ff

    @property
    def bRequestSeeded(self):
        return self.__bR

    @property
    def bStopSeeded(self):
        return self.__bS

    @property
    def bFailSeeded(self):
        return self.__bF

class _FrcRecord(_LcFrcView):
    __slots__ = []

    def __init__(self, cid_ : _ELcCompID, ferr_, atask_ : _AbsFwTask =None):
        if not (isinstance(atask_, _AbsFwTask) and atask_.isValid):
            _rtt = _EFrcRecTaskType.eByHThrd
        elif atask_.taskBadge.isFwTask:
            _rtt = _EFrcRecTaskType.eByTsk
        else:
            _rtt = _EFrcRecTaskType.eByThrd

        if _rtt == _EFrcRecTaskType.eByHThrd:
            _curThrd  = _TaskUtil.GetCurPyThread()

            _bFFE     = False
            _bRTT     = None
            _rtid     = id(_curThrd)
            _thrdID   = _rtid
            _thrdName = str(_curThrd.name)
        else:
            _bFFE     = ferr_.IsForeignTaskError(atask_.dtaskUID)
            _bRTT     = _rtt == _EFrcRecTaskType.eByTsk
            _rtid     = atask_.dtaskUID
            _thrdID   = id(atask_.dHThrd)
            _thrdName = str(atask_.dHThrd.name)
        super().__init__(cid_=cid_, ferr_=ferr_, bFFE_=_bFFE, bRTT_=_bRTT, thrdName_=_thrdName, thrdID_=_thrdID)

    def __hash__(self):
        return None if self._isInvalid else _FrcRecord.__GetHash(self.lcCompID, self.hostThreadID)

    def _IsMatching(self, cid_ : _ELcCompID, atask_ : _AbsFwTask =None):
        if cid_ != self.lcCompID:
            return False
        if (atask_ is not None) and not (isinstance(atask_, _AbsFwTask) and atask_.isValid):
            return False

        if atask_ is None:
            _hashVal = _FrcRecord.__GetHash(cid_, _TaskUtil.GetCurPyThreadUID())
        else:
            _hashVal = _FrcRecord.__GetHash(cid_, _TaskUtil.GetPyThreadUID(atask_.dHThrd))
            self.__UpdateTaskInfo(atask_)

        return _hashVal == hash(self)

    def _CloneFrcView(self) -> _LcFrcView:
        _ferr = self._feClone.Clone()

        _bRTT = None if self.isReportedByPyThread else self.isReportedByFwTask
        res   = _LcFrcView(cid_=self.lcCompID, ferr_=_ferr, bFFE_=self._isFFE, bRTT_=_bRTT, thrdName_=self.hostThreadName, thrdID_=self.hostThreadID)

        return res

    @staticmethod
    def __GetHash(cid_, tuid_):
        return hash(hash(cid_.compactName) + tuid_)

    def __UpdateTaskInfo(self, atask_ : _AbsFwTask):
        if not (isinstance(atask_, _AbsFwTask) and atask_.isValid):
            return

        if not self.isReportedByPyThread:
            return
        if self.hostThreadID != id(atask_.dHThrd):
            return

        _bRTT = atask_.taskBadge.isFwTask
        self._UpdateTaskInfo(_bRTT, atask_)

class _FrcRecMgr:
    __slots__ = [ '__ar' ]

    def __init__(self):
        self.__ar = None

    def __str__(self):
        return self.ToString()

    @property
    def size(self) -> int:
        return 0 if self.__ar is None else len(self.__ar)

    @property
    def firstFrcRecord(self) -> _FrcRecord:
        return None if self.__ar is None else self.__ar[0]

    def FindFrcRecord(self, cid_ : _ELcCompID, atask_ : _AbsFwTask =None) -> Union[_FrcRecord, None]:
        if cid_ is None:
            _LcState._RaiseException(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcStateImpl_TID_001))
            return None
        elif self.__ar is None:
            return None

        res = None
        for _ee in self.__ar:
            if _ee._IsMatching(cid_, atask_=atask_):
                res = _ee
        return res

    def AddFrcRecord(self, cid_ : _ELcCompID, ferr_, atask_ : _AbsFwTask =None) -> bool:
        if (cid_ is None) or not (isinstance(ferr_, _FatalLog) and ferr_.isClone):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00408)
            _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcStateImpl_TID_002).format(str(cid_), str(ferr_))
            _LcState._RaiseException(_errMsg)
            return False
        if (atask_ is None) and (ferr_._taskInstance is not None):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00409)
            return False

        if self.__ar is None:
            self.__ar = []

        _r = _FrcRecord(cid_, ferr_, atask_=atask_)
        self.__ar.append(_r)
        return True

    def ToString(self) -> str:
        res = None
        if self.__ar is not None:
            _NUM = len(self.__ar)
            if _NUM > 0:
                res = _CommonDefines._STR_EMPTY
                for _ii in range(_NUM):
                    if _ii > 0:
                        if _ii == 1:
                            res += _FwTDbEngine.GetText(_EFwTextID.eLcStateImpl_FrcList_ToString_001)
                        res += _FwTDbEngine.GetText(_EFwTextID.eLcStateImpl_FrcList_ToString_002).format(_ii)
                    res += self.__ar[_ii].ToString()
        return res

    def CleanUp(self):
        if self.__ar is not None:
            for _ee in self.__ar:
                _ee.CleanUp()
            self.__ar.clear()
            self.__ar = None

class _LcState(_ILcState):
    __slots__ = [ '__l' , '__m' , '__rm' ]

    def __init__(self, ppass_ : int):
        super().__init__(ppass_)

        self.__l  = _PyRLock()
        self.__m  = _ELcStateFlag.LcDefaultMask()
        self.__rm = _FrcRecMgr()

    @property
    def isLcOperable(self) -> bool:
        if self.__isInvalid: return False
        with self.__l:
            _mm = _ELcStateFlag.ebfLcStarted | _ELcStateFlag.ebfTMgrStarted | _ELcStateFlag.ebfFwMainStarted
            res = _ELcStateFlag.IsLcBitFlagSet(self.__m, _mm)
            res = res and not _ELcStateFlag.IsAnyFailedBitFlagSet(self.__m)
            return res

    @property
    def isLcCoreOperable(self) -> bool:
        if self.__isInvalid: return False
        with self.__l:
            _mm = _ELcStateFlag.ebfLcStarted | _ELcStateFlag.ebfTMgrStarted | _ELcStateFlag.ebfFwMainStarted
            res = _ELcStateFlag.IsLcBitFlagSet(self.__m, _mm)
            return res

    @property
    def isLcStarted(self):
        if self.__isInvalid: return False
        with self.__l:
            return _ELcStateFlag.IsLcStarted(self.__m)

    @property
    def isTaskManagerStarted(self):
        if self.__isInvalid: return False
        with self.__l:
            return _ELcStateFlag.IsTMgrStarted(self.__m)

    @property
    def isFwMainStarted(self):
        if self.__isInvalid: return False
        with self.__l:
            return _ELcStateFlag.IsFwMainStarted(self.__m)

    @property
    def isMainXTaskStarted(self):
        if self.__isInvalid: return False
        with self.__l:
            return _ELcStateFlag.IsMainXTaskStarted(self.__m)

    @property
    def isLcStopped(self):
        if self.__isInvalid: return True
        with self.__l:
            return _ELcStateFlag.IsLcStopped(self.__m)

    @property
    def isTaskManagerStopped(self):
        if self.__isInvalid: return False
        with self.__l:
            return _ELcStateFlag.IsTMgrStopped(self.__m)

    @property
    def isFwMainStopped(self):
        if self.__isInvalid: return True
        with self.__l:
            return _ELcStateFlag.IsFwMainStopped(self.__m)

    @property
    def isMainXTaskStopped(self):
        if self.__isInvalid: return True
        with self.__l:
            return _ELcStateFlag.IsMainXTaskStopped(self.__m)

    @property
    def isLcFailed(self):
        if self.__isInvalid: return True
        with self.__l:
            return _ELcStateFlag.IsLcFailed(self.__m)

    @property
    def isTaskManagerFailed(self):
        if self.__isInvalid: return False
        with self.__l:
            return _ELcStateFlag.IsTMgrFailed(self.__m)

    @property
    def isFwCompFailed(self):
        if self.__isInvalid: return True
        with self.__l:
            return _ELcStateFlag.IsFwCompFailed(self.__m)

    @property
    def isFwMainFailed(self):
        if self.__isInvalid: return True
        with self.__l:
            return _ELcStateFlag.IsFwMainFailed(self.__m)

    @property
    def isUThreadFailed(self):
        if self.__isInvalid: return False
        with self.__l:
            return _ELcStateFlag.IsUThreadFailed(self.__m)

    @property
    def isXTaskFailed(self):
        if self.__isInvalid: return False
        with self.__l:
            return _ELcStateFlag.IsXTaskFailed(self.__m)

    @property
    def isMainXTaskFailed(self):
        if self.__isInvalid: return False
        with self.__l:
            return _ELcStateFlag.IsMainXTaskFailed(self.__m)

    @property
    def isMiscCompFailed(self):
        if self.__isInvalid: return False
        with self.__l:
            return _ELcStateFlag.IsMiscCompFailed(self.__m)

    @property
    def isLcStartedExclusive(self):
        if self.__isInvalid: return False
        with self.__l:
            return _ELcStateFlag.IsLcBitMaskExclusive(self.__m) and self.isLcStarted

    @property
    def hasLcAnyFailureState(self):
        if self.__isInvalid: return True
        with self.__l:
            return _ELcStateFlag.IsAnyFailedBitFlagSet(self.__m)

    @property
    def lcFrcView(self) -> _LcFrcView:
        res = None
        if not self.__isInvalid:
            with self.__l:
                _ffrc = self.__firstFrcRecord
                if _ffrc is not None:
                    res = _ffrc._CloneFrcView()
        return res

    def HasLcCompFRC(self, lcCID_ : _ELcCompID, atask_ : _AbsFwTask =None) -> bool:
        if self.__isInvalid: return False
        with self.__l:
            return self.__rm.FindFrcRecord(lcCID_, atask_=atask_) is not None

    def GetLcCompFrcView(self, lcCID_ : _ELcCompID, atask_ : _AbsFwTask =None) -> Union[_LcFrcView, None]:
        if self.__isInvalid:
            return None
        with self.__l:
            res = self.__rm.FindFrcRecord(lcCID_, atask_=atask_)
            if res is not None:
                res = res._CloneFrcView()
            return res

    @property
    def _isLcIdle(self):
        if self.__isInvalid: return False
        with self.__l:
            return _ELcStateFlag.IsLcIdle(self.__m)

    @staticmethod
    def _RaiseException(xcpMsg_):
        if vlogif._IsVSystemExitEnabled():
            raise SystemExit(xcpMsg_)
        else:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00413)

    def _SetLcState(self, lcCID_ : _ELcCompID, bStartStopFailFlag_ : Union[bool, None], frcError_ : _FatalLog =None, atask_ : _AbsFwTask =None) -> bool:
        if self.__isInvalid:
            return False

        with self.__l:
            _pcr = self.__PreCheckSetRequest(lcCID_, bStartStopFailFlag_, frcError_=frcError_, atask_=atask_)
            if _pcr is None:
                return False

            _eCheckRes = self.__CheckRuleViolation__LcAlreadyStopped(_pcr)
            if not _eCheckRes.isContinue:
                return _eCheckRes.isStop

            _eCheckRes = self.__CheckRuleViolation__StartTransition(_pcr)
            if not _eCheckRes.isContinue:
                return _eCheckRes.isStop

            _eCheckRes = self.__CheckRuleViolation__StopTransition(_pcr)
            if not _eCheckRes.isContinue:
                return _eCheckRes.isStop

            _eCheckRes = self.__CheckRuleViolation__UnsupportStartStopTransition(_pcr)
            if not _eCheckRes.isContinue:
                return _eCheckRes.isStop

            _eCheckRes = self.__CheckRuleViolation__ResetSameTransition(_pcr)
            if not _eCheckRes.isContinue:
                return _eCheckRes.isStop

            return self.__UpdateLcState(_pcr)

    def _RestoreCurBitMask(self, eBitMask_ : _FwIntFlag):
        if self.__isInvalid:
            return
        if not isinstance(eBitMask_, _ELcStateFlag):
            return
        with self.__l:
            self.__m = eBitMask_

    def _ToString(self, bCompact_ =False):
        if self.__isInvalid:
            return None
        if bCompact_:
            bCompact_ = not self.hasLcAnyFailureState

        with self.__l:
            res = _CommonDefines._STR_EMPTY

            if self._isLcIdle:
                res += _FwTDbEngine.GetText(_EFwTextID.eLcStateImpl_ToString_01)
            else:
                _srv     = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_Name_Srv)
                _main    = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_Name_Main)
                _xtsk    = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_Name_XTask)
                _mxtsk   = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_Name_MainXTask)
                _uthrd   = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_Name_UThread)
                _midPart = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_027)

                if   self.isLcFailed:           res += _CommonDefines._CHAR_SIGN_SPACE + _ELcStateTransReq.eLcFailed.compactName
                elif self.isLcStarted:          res += _CommonDefines._CHAR_SIGN_SPACE + _ELcStateTransReq.eLcStarted.compactName
                elif self.isLcStopped:          res += _CommonDefines._CHAR_SIGN_SPACE + _ELcStateTransReq.eLcStopped.compactName

                if   self.isTaskManagerFailed:  res += _midPart + _ELcStateTransReq.eTMgrFailed.compactName
                elif self.isTaskManagerStarted: res += _midPart + _ELcStateTransReq.eTMgrStarted.compactName
                elif self.isTaskManagerStopped: res += _midPart + _ELcStateTransReq.eTMgrStopped.compactName

                if   self.isFwCompFailed:       res += _midPart + _ELcStateTransReq.eFwSrvFailed.compactName

                if   self.isFwMainFailed:       res += _midPart + _StrUtil.ReplaceSubstring(_ELcStateTransReq.eFwSrvFailed.compactName, _srv, _main)
                elif self.isFwMainStarted:      res += _midPart + _StrUtil.ReplaceSubstring(_ELcStateTransReq.eFwSrvStarted.compactName, _srv, _main)
                elif self.isFwMainStopped:      res += _midPart + _StrUtil.ReplaceSubstring(_ELcStateTransReq.eFwSrvStopped.compactName, _srv, _main)

                if   self.isUThreadFailed:      res += _midPart + _StrUtil.ReplaceSubstring(_ELcStateTransReq.eXTaskFailed.compactName, _xtsk, _uthrd)

                if   self.isXTaskFailed:        res += _midPart + _ELcStateTransReq.eXTaskFailed.compactName

                if   self.isMainXTaskFailed:    res += _midPart + _StrUtil.ReplaceSubstring(_ELcStateTransReq.eXTaskFailed.compactName, _xtsk, _mxtsk)
                elif self.isMainXTaskStarted:   res += _midPart + _StrUtil.ReplaceSubstring(_ELcStateTransReq.eXTaskStarted.compactName, _xtsk, _mxtsk)
                elif self.isMainXTaskStopped:   res += _midPart + _StrUtil.ReplaceSubstring(_ELcStateTransReq.eXTaskStopped.compactName, _xtsk, _mxtsk)

                if   self.isMiscCompFailed:     res += _midPart + _ELcStateTransReq.eMiscCompFailed.compactName

            if not vlogif._IsReleaseModeEnabled():
                res = _FwTDbEngine.GetText(_EFwTextID.eLcStateImpl_ToString_02).format(hex(self.__m), res)
            else:
                res = _FwTDbEngine.GetText(_EFwTextID.eLcStateImpl_ToString_03).format(res)

            _ffr = self.__rm.firstFrcRecord
            if _ffr is not None:
                _ec = _ffr.errorCode
                if not (isinstance(_ec, int) and _ec != _LogErrorCode.GetAnonymousErrorCode()):
                    _ec = _CommonDefines._CHAR_SIGN_DASH
                res += _FwTDbEngine.GetText(_EFwTextID.eLcStateImpl_ToString_04).format(_ec)

            if not bCompact_:
                _myTxt = self.__rm.ToString()
                if _myTxt is not None:
                    res += f'{_CommonDefines._CHAR_SIGN_LF}{_CommonDefines._CHAR_SIGN_TAB}{_myTxt}'
            return res

    def _CleanUpByOwnerRequest(self):
        if not self.__isInvalid:
            if self.__rm is not None:
                self.__rm.CleanUp()
            self.__l  = None
            self.__m  = None
            self.__rm = None

    @property
    def __isInvalid(self):
        return self.__m is None

    @property
    def __firstFrcRecord(self) -> _FrcRecord:
        return None if self.__isInvalid else self.__rm.firstFrcRecord

    def __CheckRuleViolation__LcAlreadyStopped(self, pcr_ : _TransReqPreCheckResult) -> _EExecutionCmdID:
        if self.isLcStopped:
            _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcStateImpl_TID_004).format(pcr_.paramsCurStateStr)
            _LcState._RaiseException(_errMsg)
            return _EExecutionCmdID.Abort()
        return _EExecutionCmdID.Continue()

    def __CheckRuleViolation__StartTransition(self, pcr_ : _TransReqPreCheckResult) -> _EExecutionCmdID:
        if self is None: pass
        if pcr_.lcTrans.isStartTransitionRequest:
            if pcr_.bStopSeeded or pcr_.bFailSeeded:
                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcStateImpl_TID_005).format(pcr_.paramsCurStateStr)
                _LcState._RaiseException(_errMsg)
                return _EExecutionCmdID.Abort()
        return _EExecutionCmdID.Continue()

    def __CheckRuleViolation__StopTransition(self, pcr_ : _TransReqPreCheckResult) -> _EExecutionCmdID:
        if self is None: pass
        if pcr_.lcTrans.isStopTransitionRequest:
            if pcr_.bFailSeeded:
                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcStateImpl_TID_006).format(pcr_.paramsCurStateStr)
                _LcState._RaiseException(_errMsg)
                return _EExecutionCmdID.Abort()
        return _EExecutionCmdID.Continue()

    def __CheckRuleViolation__UnsupportStartStopTransition(self, pcr_ : _TransReqPreCheckResult) -> _EExecutionCmdID:
        if self is None: pass
        if not pcr_.lcTrans.isFailureTransitionRequest:
            _bIgnore =             (pcr_.ebfRequest == _ELcStateFlag.ebfFwCompStarted) or (pcr_.ebfRequest == _ELcStateFlag.ebfFwCompStopped)
            _bIgnore = _bIgnore or (pcr_.ebfRequest == _ELcStateFlag.ebfXTaskStarted) or (pcr_.ebfRequest == _ELcStateFlag.ebfXTaskStopped)
            _bIgnore = _bIgnore or (pcr_.ebfRequest == _ELcStateFlag.ebfMiscCompStarted) or (pcr_.ebfRequest == _ELcStateFlag.ebfMiscCompStopped)
            if _bIgnore:
                return _EExecutionCmdID.Stop()
        return _EExecutionCmdID.Continue()

    def __CheckRuleViolation__ResetSameTransition(self, pcr_ : _TransReqPreCheckResult) -> _EExecutionCmdID:
        if self is None: pass
        if     pcr_.lcTrans.isFailureTransitionRequest \
           and ((pcr_.ebfRequest == _ELcStateFlag.ebfFwCompFailed) or (pcr_.ebfRequest == _ELcStateFlag.ebfXTaskFailed) or (pcr_.ebfRequest == _ELcStateFlag.ebfMiscCompFailed)):
            _frc = self.__rm.FindFrcRecord(pcr_.lcCompID, atask_=pcr_.absTask)
            if _frc is not None:
                return _EExecutionCmdID.Abort()
        elif pcr_.bRequestSeeded:
            return _EExecutionCmdID.Stop()
        return _EExecutionCmdID.Continue()

    def __UpdateLcState( self, pcr_ : _TransReqPreCheckResult):
        _eOldBitMask = self.__m

        if pcr_.ebfRequestInv is not None:
            self.__m = _ELcStateFlag.RemoveLcBitFlag(self.__m, pcr_.ebfRequestInv)

            if _ELcStateFlag.IsLcBitFlagSet(self.__m, pcr_.ebfRequestInv):
                self.__m = _eOldBitMask
                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcStateImpl_TID_007).format(pcr_.paramsCurStateStr)
                _LcState._RaiseException(_errMsg)
                return False

        self.__m = _ELcStateFlag.AddLcBitFlag(self.__m, pcr_.ebfRequest)

        if not _ELcStateFlag.IsLcBitFlagSet(self.__m, pcr_.ebfRequest):
            self.__m = _eOldBitMask
            _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcStateImpl_TID_008).format(1, pcr_.paramsCurStateStr)
            _LcState._RaiseException(_errMsg)
            return False

        res = self.__m != _eOldBitMask
        if not res:
            self.__m = _eOldBitMask
            _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcStateImpl_TID_008).format(2, pcr_.paramsCurStateStr)
            _LcState._RaiseException(_errMsg)
            return False

        _frcErr = None
        if pcr_.fatalError is not None:
            _bClone = pcr_.fatalError.isClone
            if _bClone:
                _frcErr = pcr_.fatalError
            else:
                _frcErr = pcr_.fatalError.Clone()
                if _frcErr is None:
                    self.__m = _eOldBitMask
                    _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcStateImpl_TID_010).format(type(pcr_.fatalError).__name__, pcr_.paramsCurStateStr, str(pcr_.fatalError))
                    _LcState._RaiseException(_errMsg)
                    return False

            _bOK = self.__rm.AddFrcRecord(pcr_.lcCompID, _frcErr, atask_=pcr_.absTask)
            if not (_bOK and self.HasLcCompFRC(pcr_.lcCompID, atask_=pcr_.absTask)):
                self.__m = _eOldBitMask
                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcStateImpl_TID_008).format(3, pcr_.paramsCurStateStr)
                _LcState._RaiseException(_errMsg)
                return False

            if not _bClone:
                pcr_.fatalError._UpdateErrorImpact(_EErrorImpact.eNoImpactByFrcLinkage)

        _frcRec = self.__firstFrcRecord
        if self.hasLcAnyFailureState:
            if _frcRec is None:
                self.__m = _eOldBitMask
                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcStateImpl_TID_012).format(4, pcr_.paramsCurStateStr)
                _LcState._RaiseException(_errMsg)
                return False
        elif _frcRec is not None:
            self.__m = _eOldBitMask
            _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcStateImpl_TID_012).format(5, pcr_.paramsCurStateStr)
            _LcState._RaiseException(_errMsg)
            return False

        _LcFailure._SetCurrentLcState(self.ToString(), self.lcFrcView, self.__rm.size)
        return res

    def __PreCheckSetRequest(self, lcCID_: _ELcCompID, bStartStopFailFlag_: Union[bool, None], frcError_: _FatalLog =None, atask_: _AbsFwTask =None) -> _TransReqPreCheckResult:
        if not isinstance(lcCID_, _ELcCompID):
            _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcStateImpl_TID_013).format(type(lcCID_).__name__)
            _LcState._RaiseException(_errMsg)
            return None

        a3 = _ELcStateTransReq._ConvertFromLcCompID(lcCID_, bStartStopFailFlag_=bStartStopFailFlag_)
        if a3 is None:
            _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcStateImpl_TID_011).format(
                lcCID_.compactName, lcCID_.value)
            _LcState._RaiseException(_errMsg)
            return None

        a5 = _FwTDbEngine.GetText(_EFwTextID.eLcStateImpl_UpdateLcState_PreCheckSetRequest_FmtStr_01).format(
            hex(self.__m), lcCID_.compactName, str(bStartStopFailFlag_), a3.compactName, type(frcError_).__name__, type(atask_).__name__)
        a6 = a5 + _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_012).format(self)

        if not ((atask_ is None) or (isinstance(atask_, _AbsFwTask) and atask_.isValid)):
            _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcStateImpl_TID_014).format(1, a5)
            _LcState._RaiseException(_errMsg)
            return None

        if a3.isFailureTransitionRequest:
            if (bStartStopFailFlag_ is not None) or (not isinstance(frcError_, _FatalLog)) or frcError_.hasNoErrorImpact:
                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcStateImpl_TID_014).format(2, a5)
                _LcState._RaiseException(_errMsg)
                return None

        else:
            if not (isinstance(bStartStopFailFlag_, bool) and (frcError_ is None)):
                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcStateImpl_TID_014).format(3, a5)
                _LcState._RaiseException(_errMsg)
                return None

        a8      = _LcState.__Enum2RelatedFailedBitFlag(a3, lcCID_)
        a9     = _LcState.__Enum2RelatedStoppedBitFlag(a3, lcCID_)
        a7, a10 = _LcState.__Enum2BitFlagsPair(a3, lcCID_)

        if (a7 is None) or (a8 is None) or (a9 is None):
            return None

        a11 = _ELcStateFlag.IsLcBitFlagSet(self.__m, a8)
        a12 = _ELcStateFlag.IsLcBitFlagSet(self.__m, a9)
        a13  = _ELcStateFlag.IsLcBitFlagSet(self.__m, a7)

        res = _TransReqPreCheckResult( atask_, frcError_, a3, lcCID_, a5, a6, a7, a8, a9, a10, a11, a12, a13)
        return res

    @staticmethod
    def __Enum2BitFlagsPair(lcSTReq_ : _ELcStateTransReq, lcCID_ : _ELcCompID):
        res     = None
        _resInv = None

        _cgID = lcCID_.lcCompGroupID

        if lcCID_ == _ELcCompID.eLcMgr:
            if   lcSTReq_ == _ELcStateTransReq.eLcStarted:   res, _resInv = _ELcStateFlag.ebfLcStarted , None
            elif lcSTReq_ == _ELcStateTransReq.eLcStopped:   res, _resInv = _ELcStateFlag.ebfLcStopped , _ELcStateFlag.ebfLcStarted
            elif lcSTReq_ == _ELcStateTransReq.eLcFailed:    res, _resInv = _ELcStateFlag.ebfLcFailed  , _ELcStateFlag.ebfLcStarted

        elif lcCID_ == _ELcCompID.eTMgr:
            if   lcSTReq_ == _ELcStateTransReq.eTMgrStarted: res, _resInv = _ELcStateFlag.ebfTMgrStarted , None
            elif lcSTReq_ == _ELcStateTransReq.eTMgrStopped: res, _resInv = _ELcStateFlag.ebfTMgrStopped , _ELcStateFlag.ebfTMgrStarted
            elif lcSTReq_ == _ELcStateTransReq.eTMgrFailed:  res, _resInv = _ELcStateFlag.ebfTMgrFailed  , _ELcStateFlag.ebfTMgrStarted

        elif _cgID == _ELcCompID.eFwSrv:
            if lcSTReq_ == _ELcStateTransReq.eFwSrvStarted:
                if lcCID_ == _ELcCompID.eFwMain:
                    res, _resInv = _ELcStateFlag.ebfFwMainStarted , None
                else:
                    res, _resInv = _ELcStateFlag.ebfFwCompStarted , None
            elif lcSTReq_ == _ELcStateTransReq.eFwSrvStopped:
                if lcCID_==_ELcCompID.eFwMain:
                    res, _resInv = _ELcStateFlag.ebfFwMainStopped, _ELcStateFlag.ebfFwMainStarted
                else:
                    res, _resInv = _ELcStateFlag.ebfFwCompStopped , _ELcStateFlag.ebfFwCompStarted
            elif lcSTReq_ == _ELcStateTransReq.eFwSrvFailed:
                if lcCID_==_ELcCompID.eFwMain:
                    res, _resInv = _ELcStateFlag.ebfFwMainFailed , _ELcStateFlag.ebfFwMainStarted
                else:
                    res, _resInv = _ELcStateFlag.ebfFwCompFailed , _ELcStateFlag.ebfFwCompStarted

        elif _cgID == _ELcCompID.eXTask:
            if lcSTReq_ == _ELcStateTransReq.eXTaskStarted:
                if lcCID_ == _ELcCompID.eMainXTask:
                    res, _resInv = _ELcStateFlag.ebfMainXTaskStarted , None
                elif lcCID_ == _ELcCompID.eXTask:
                    res, _resInv = _ELcStateFlag.ebfXTaskStarted , None
                else:
                    res, _resInv = _ELcStateFlag.ebfUThreadStarted , None
            elif lcSTReq_ == _ELcStateTransReq.eXTaskStopped:
                if lcCID_ == _ELcCompID.eMainXTask:
                    res, _resInv = _ELcStateFlag.ebfMainXTaskStopped , _ELcStateFlag.ebfMainXTaskStarted
                elif lcCID_ == _ELcCompID.eXTask:
                    res, _resInv = _ELcStateFlag.ebfXTaskStopped , _ELcStateFlag.ebfXTaskStarted
                else:
                    res, _resInv = _ELcStateFlag.ebfUThreadStopped , _ELcStateFlag.ebfUThreadStarted
            elif lcSTReq_ == _ELcStateTransReq.eXTaskFailed:
                if lcCID_==_ELcCompID.eMainXTask:
                    res, _resInv = _ELcStateFlag.ebfMainXTaskFailed , _ELcStateFlag.ebfMainXTaskStarted
                elif lcCID_==_ELcCompID.eXTask:
                    res, _resInv = _ELcStateFlag.ebfXTaskFailed , _ELcStateFlag.ebfXTaskStarted
                else:
                    res, _resInv = _ELcStateFlag.ebfUThreadFailed, _ELcStateFlag.ebfUThreadStarted

        else:
            if   lcSTReq_ == _ELcStateTransReq.eMiscCompStarted: res, _resInv = _ELcStateFlag.ebfMiscCompStarted , None
            elif lcSTReq_ == _ELcStateTransReq.eMiscCompStopped: res, _resInv = _ELcStateFlag.ebfMiscCompStopped , _ELcStateFlag.ebfMiscCompStarted
            elif lcSTReq_ == _ELcStateTransReq.eMiscCompFailed:  res, _resInv = _ELcStateFlag.ebfMiscCompFailed  , _ELcStateFlag.ebfMiscCompStarted

        if res is None:
            _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcStateImpl_TID_009).format(1, lcSTReq_.compactName, lcCID_.compactName)
            _LcState._RaiseException(_errMsg)
        return res, _resInv

    @staticmethod
    def __Enum2RelatedFailedBitFlag(lcSTReq_ : _ELcStateTransReq, lcCID_ : _ELcCompID):
        _bMain = (lcCID_==_ELcCompID.eFwMain) or (lcCID_==_ELcCompID.eMainXTask)

        if lcSTReq_ == _ELcStateTransReq.eLcStarted or lcSTReq_ == _ELcStateTransReq.eLcStopped or lcSTReq_ == _ELcStateTransReq.eLcFailed:
            res = _ELcStateFlag.ebfLcFailed

        elif lcSTReq_ == _ELcStateTransReq.eTMgrStarted or lcSTReq_ == _ELcStateTransReq.eTMgrStopped or lcSTReq_ == _ELcStateTransReq.eTMgrFailed:
            res = _ELcStateFlag.ebfTMgrFailed

        elif lcSTReq_ == _ELcStateTransReq.eFwSrvStarted or lcSTReq_ == _ELcStateTransReq.eFwSrvStopped or lcSTReq_ == _ELcStateTransReq.eFwSrvFailed:
            res = _ELcStateFlag.ebfFwMainFailed if _bMain else _ELcStateFlag.ebfFwCompFailed

        elif lcSTReq_ == _ELcStateTransReq.eXTaskStarted or lcSTReq_ == _ELcStateTransReq.eXTaskStopped or lcSTReq_ == _ELcStateTransReq.eXTaskFailed:
            if _bMain:
                res = _ELcStateFlag.ebfMainXTaskFailed
            elif lcCID_.isXtask:
                res = _ELcStateFlag.ebfXTaskFailed
            else:
                res = _ELcStateFlag.ebfUThreadFailed

        elif lcSTReq_ == _ELcStateTransReq.eMiscCompStarted or lcSTReq_ == _ELcStateTransReq.eMiscCompStopped or lcSTReq_ == _ELcStateTransReq.eMiscCompFailed:
            res = _ELcStateFlag.ebfMiscCompFailed

        else:
            res = None
            _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcStateImpl_TID_009).format(2, lcSTReq_.compactName, lcCID_.compactName)
            _LcState._RaiseException(_errMsg)
        return res

    @staticmethod
    def __Enum2RelatedStoppedBitFlag(lcSTReq_ : _ELcStateTransReq, lcCID_ : _ELcCompID):
        _bMain = (lcCID_==_ELcCompID.eFwMain) or (lcCID_==_ELcCompID.eMainXTask)

        if lcSTReq_ == _ELcStateTransReq.eLcStarted or lcSTReq_ == _ELcStateTransReq.eLcStopped or lcSTReq_ == _ELcStateTransReq.eLcFailed:
            res = _ELcStateFlag.ebfLcStopped

        elif lcSTReq_ == _ELcStateTransReq.eTMgrStarted or lcSTReq_ == _ELcStateTransReq.eTMgrStopped or lcSTReq_ == _ELcStateTransReq.eTMgrFailed:
            res =  _ELcStateFlag.ebfTMgrStopped

        elif lcSTReq_ == _ELcStateTransReq.eFwSrvStarted or lcSTReq_ == _ELcStateTransReq.eFwSrvStopped or lcSTReq_ == _ELcStateTransReq.eFwSrvFailed:
            res =  _ELcStateFlag.ebfFwMainStopped if _bMain else _ELcStateFlag.ebfFwCompStopped

        elif lcSTReq_ == _ELcStateTransReq.eXTaskStarted or lcSTReq_ == _ELcStateTransReq.eXTaskStopped or lcSTReq_ == _ELcStateTransReq.eXTaskFailed:
            if _bMain:
                res = _ELcStateFlag.ebfMainXTaskStopped
            elif lcCID_.isXtask:
                res = _ELcStateFlag.ebfXTaskStopped
            else:
                res = _ELcStateFlag.ebfUThreadStopped

        elif lcSTReq_ == _ELcStateTransReq.eMiscCompStarted or lcSTReq_ == _ELcStateTransReq.eMiscCompStopped or lcSTReq_ == _ELcStateTransReq.eMiscCompFailed:
            res =  _ELcStateFlag.ebfMiscCompStopped

        else:
            res =None
            _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcStateImpl_TID_009).format(3, lcSTReq_.compactName, lcCID_.compactName)
            _LcState._RaiseException(_errMsg)
        return res
