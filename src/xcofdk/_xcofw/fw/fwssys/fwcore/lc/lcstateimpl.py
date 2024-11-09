# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : lcstateimpl.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from enum import unique

from xcofdk._xcofw.fw.fwssys.fwcore.logging            import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.base.strutil       import _StrUtil
from xcofdk._xcofw.fw.fwssys.fwcore.logging.fatalentry import _FatalEntry
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logdefines import _EErrorImpact
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.atask      import _AbstractTask
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil   import _TaskUtil
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil   import _PyRLock
from xcofdk._xcofw.fw.fwssys.fwcore.types.ebitmask     import _EBitMask
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes  import _FwIntFlag
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes  import _FwIntEnum
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes  import _ETernaryOpResult
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes  import _CommonDefines
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcdefines       import _ELcCompID
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcdefines       import _LcFrcView
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcexecstate     import _LcFailure
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcexecstate     import _LcRuntimeFailure
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcstate         import _LcState

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine


@unique
class _ELcStateFlag(_FwIntFlag):
    ebfIdle               = 0x000000
    ebfLcStarted          = (0x000001 <<  0)
    ebfTMgrStarted        = (0x000001 <<  1)
    ebfFwCompStarted      = (0x000001 <<  2)
    ebfFwMainStarted      = (0x000001 <<  3)
    ebfXTaskStarted       = (0x000001 <<  4)
    ebfMainXTaskStarted   = (0x000001 <<  5)
    ebfMiscCompStarted    = (0x000001 <<  6)
    ebfMiscCompStopped    = (0x000001 <<  7)
    ebfMainXTaskStopped   = (0x000001 <<  8)
    ebfXTaskStopped       = (0x000001 <<  9)
    ebfFwMainStopped      = (0x000001 << 10)
    ebfFwCompStopped      = (0x000001 << 11)
    ebfTMgrStopped        = (0x000001 << 12)
    ebfLcStopped          = (0x000001 << 13)
    ebfLcFailed           = (0x010000 <<  0)
    ebfTMgrFailed         = (0x010000 <<  1)
    ebfFwCompFailed       = (0x010000 <<  2)
    ebfFwMainFailed       = (0x010000 <<  3)
    ebfXTaskFailed        = (0x010000 <<  4)
    ebfMainXTaskFailed    = (0x010000 <<  5)
    ebfMiscCompFailed     = (0x010000 <<  6)

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
        for name, member in _ELcStateFlag.__members__.items():
            res = eLcBitMask_ == member.value
            if res:
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
    eFwCompFailed   = _ELcCompID.eFwComp.value
    eFwCompStarted  = -1*eFwCompFailed
    eFwCompStopped  = eFwCompStarted-1
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
        if   self == _ELcStateTransReq.eLcFailed            : res = _FwTDbEngine.GetText(_EFwTextID.eLcStateImpl_ELcStateTransReq_LcFailed)
        elif self == _ELcStateTransReq.eLcStarted           : res = _FwTDbEngine.GetText(_EFwTextID.eLcStateImpl_ELcStateTransReq_LcStarted)
        elif self == _ELcStateTransReq.eLcStopped           : res = _FwTDbEngine.GetText(_EFwTextID.eLcStateImpl_ELcStateTransReq_LcStopped)
        elif self == _ELcStateTransReq.eTMgrFailed          : res = _FwTDbEngine.GetText(_EFwTextID.eLcStateImpl_ELcStateTransReq_TMgrFailed)
        elif self == _ELcStateTransReq.eTMgrStarted         : res = _FwTDbEngine.GetText(_EFwTextID.eLcStateImpl_ELcStateTransReq_TMgrStarted)
        elif self == _ELcStateTransReq.eTMgrStopped         : res = _FwTDbEngine.GetText(_EFwTextID.eLcStateImpl_ELcStateTransReq_TMgrStopped)
        elif self == _ELcStateTransReq.eFwCompFailed        : res = _FwTDbEngine.GetText(_EFwTextID.eLcStateImpl_ELcStateTransReq_FwCompFailed)
        elif self == _ELcStateTransReq.eFwCompStarted       : res = _FwTDbEngine.GetText(_EFwTextID.eLcStateImpl_ELcStateTransReq_FwCompStarted)
        elif self == _ELcStateTransReq.eFwCompStopped       : res = _FwTDbEngine.GetText(_EFwTextID.eLcStateImpl_ELcStateTransReq_FwCompStopped)
        elif self == _ELcStateTransReq.eXTaskFailed       : res = _FwTDbEngine.GetText(_EFwTextID.eLcStateImpl_ELcStateTransReq_XTaskFailed)
        elif self == _ELcStateTransReq.eXTaskStarted      : res = _FwTDbEngine.GetText(_EFwTextID.eLcStateImpl_ELcStateTransReq_XTaskStarted)
        elif self == _ELcStateTransReq.eXTaskStopped      : res = _FwTDbEngine.GetText(_EFwTextID.eLcStateImpl_ELcStateTransReq_XTaskStopped)
        elif self == _ELcStateTransReq.eMiscCompFailed      : res = _FwTDbEngine.GetText(_EFwTextID.eLcStateImpl_ELcStateTransReq_MiscCompFailed)
        elif self == _ELcStateTransReq.eMiscCompStarted     : res = _FwTDbEngine.GetText(_EFwTextID.eLcStateImpl_ELcStateTransReq_MiscCompStarted)
        elif self == _ELcStateTransReq.eMiscCompStopped     : res = _FwTDbEngine.GetText(_EFwTextID.eLcStateImpl_ELcStateTransReq_MiscCompStopped)
        else:
            res = ''
        return res

    @staticmethod
    def _ConvertFromLcCompID(eLcCompID_ : _ELcCompID, bStartStopFailFlag_ : [bool, None]):
        res = None
        if not isinstance(eLcCompID_, _ELcCompID):
            pass
        else:
            eGrpID = eLcCompID_.lcCompGroupID

            if eGrpID == _ELcCompID.eLcMgr:
                res = _ELcStateTransReq.eLcFailed
            elif eGrpID == _ELcCompID.eTMgr:
                res = _ELcStateTransReq.eTMgrFailed
            elif eGrpID == _ELcCompID.eFwComp:
                res = _ELcStateTransReq.eFwCompFailed
            elif eGrpID == _ELcCompID.eXTask:
                res = _ELcStateTransReq.eXTaskFailed
            else:  
                res = _ELcStateTransReq.eMiscCompFailed

            if bStartStopFailFlag_ is not None:
                val = -1 * res.value
                if not bStartStopFailFlag_:
                    val -= 1
                res = _ELcStateTransReq(val)
        return res


class _TransReqPreCheckResult:
    __slots__ = [
                  '__eLcTrans' , '__eLcCompID' , '__fatalError' , '__absTask' , '__paramsStr' , '__paramsCurStateStr'
                , '__ebfRequest' , '__ebfRequestInv' , '__ebfCpStopped' , '__ebfCpFailed'
                , '__bRequestSeeded' , '__bStopSeeded' , '__bFailSeeded' ]

    def __init__(self, a1_, a2_, a3_, a4_, a5_, a6_, a7_, a8_, a9_, a10_, a11_, a12_, a13_):
        self.__absTask           = a1_
        self.__fatalError        = a2_
        self.__eLcTrans          = a3_
        self.__eLcCompID         = a4_
        self.__paramsStr         = a5_
        self.__paramsCurStateStr = a6_

        self.__ebfRequest        = a7_
        self.__ebfCpFailed       = a8_
        self.__ebfCpStopped      = a9_
        self.__ebfRequestInv     = a10_

        self.__bStopSeeded       = a11_
        self.__bFailSeeded       = a12_
        self.__bRequestSeeded    = a13_

    @property
    def eLcTrans(self):
        return self.__eLcTrans

    @property
    def eLcCompID(self):
        return self.__eLcCompID

    @property
    def fatalError(self):
        return self.__fatalError

    @property
    def absTask(self):
        return self.__absTask

    @property
    def paramsStr(self):
        return self.__paramsStr

    @property
    def paramsCurStateStr(self):
        return self.__paramsCurStateStr

    @property
    def ebfRequest(self):
        return self.__ebfRequest

    @property
    def ebfRequestInv(self):
        return self.__ebfRequestInv

    @property
    def ebfCpStopped(self):
        return self.__ebfCpStopped

    @property
    def ebfCpFailed(self):
        return self.__ebfCpFailed

    @property
    def bRequestSeeded(self):
        return self.__bRequestSeeded

    @property
    def bStopSeeded(self):
        return self.__bStopSeeded

    @property
    def bFailSeeded(self):
        return self.__bFailSeeded


class _LcStateImpl(_LcState):

    @unique
    class _EFrcRecordTaskType(_FwIntFlag):
        ePyThread = 0
        eFwThread = 1
        eFwTask   = 2

        @property
        def isPyThread(self):
            return self == _LcStateImpl._EFrcRecordTaskType.ePyThread

        @property
        def isFwThread(self):
            return self == _LcStateImpl._EFrcRecordTaskType.eFwThread

        @property
        def isFwTask(self):
            return self == _LcStateImpl._EFrcRecordTaskType.eFwTask


    class _FrcRecord:
        __slots__ = [ '__eCID' , '__feClone' , '__ttype' , '__tskName' , '__thrdName' , '__tid' , '__tuid' , '__bFFE' ]

        def __init__(self, eCID_ : _ELcCompID, ferr_, atask_ : _AbstractTask =None):
            self.__eCID    = eCID_
            self.__feClone = ferr_

            if not (isinstance(atask_, _AbstractTask) and (atask_.taskBadge is not None)):
                ttype = _LcStateImpl._EFrcRecordTaskType.ePyThread
            elif atask_.isFwTask:
                ttype = _LcStateImpl._EFrcRecordTaskType.eFwTask
            else:
                ttype = _LcStateImpl._EFrcRecordTaskType.eFwThread

            if ttype.isPyThread:
                _curThrd = _TaskUtil.GetCurPyThread()
                _tuid    = id(_curThrd)
                _tname   = str(_curThrd.name)

                self.__tid      = _tuid
                self.__tuid     = _tuid
                self.__bFFE     = False
                self.__tskName  = _tname
                self.__thrdName = _tname
            else:
                self.__tid      = atask_.taskID
                self.__tuid     = id(atask_.linkedPyThread)
                self.__bFFE     = ferr_.IsForeignTaskError(atask_.taskID)
                self.__tskName  = str(atask_.taskName)
                self.__thrdName = str(atask_.linkedPyThread.name)
            self.__ttype = ttype

        def __str__(self):
            return self.ToString()

        def __hash__(self):
            return None if self.__isInvalid else hash(hash(self.__eCID.compactName) + self.__tuid)

        @property
        def isForeignFatalError(self):
            return self.__bFFE

        @property
        def isReportedByPyThread(self):
            return False if self.__isInvalid else self.__ttype.isPyThread

        @property
        def isReportedByFwTask(self):
            return False if self.__isInvalid else self.__ttype.isFwTask

        @property
        def isReportedByFwThread(self):
            return False if self.__isInvalid else self.__ttype.isFwThread

        @property
        def eCID(self):
            return self.__eCID

        @property
        def fatalErrorClone(self):
            return self.__feClone

        @property
        def reportingTaskID(self):
            return self.__tid

        @property
        def reportingTaskName(self):
            return self.__tskName

        def IsMatching(self, eCID_ : _ELcCompID, atask_ : _AbstractTask =None):
            if self.__isInvalid:
                return False
            elif eCID_ != self.__eCID:
                return False
            elif not ((atask_ is None) or (isinstance(atask_, _AbstractTask) and (atask_.taskBadge is not None))):
                return False

            if atask_ is None:
                atask_ = _TaskUtil.GetCurPyThread()
                _hashVal = hash(hash(eCID_.compactName) + id(atask_))
            else:
                _hashVal = hash(hash(eCID_.compactName) + id(atask_.linkedPyThread))
                self.__UpdateTaskInfo(atask_)

            return _hashVal == hash(self)

        def ToString(self) -> str:
            if self.__isInvalid:
                res = None
            else:
                res = _FwTDbEngine.GetText(_EFwTextID.eLcStateImpl_FrcEntry_ToString_001)
                res = res.format( self.__eCID.compactName, self.__tskName, self.__tid, self.__feClone.uniqueID, self.__feClone.shortMessage)
            return res

        def CleanUp(self):
            if self.__feClone is not None:
                self.__feClone.CleanUp()
                self.__feClone = None
            self.__tid     = None
            self.__bFFE    = None
            self.__eCID    = None
            self.__tuid    = None
            self.__ttype   = None
            self.__tskName = None
            self.__feClone = None

        def _CreateFrcView(self) -> _LcFrcView:
            if self.__isInvalid:
                return None

            _ferr = self.__feClone.Clone()
            if (_ferr is None) or _ferr.isInvalid:
                if _ferr is  not None:
                    _ferr.CleanUp()
                vlogif._LogOEC(True, -1562)
                return None

            _bTType = None if self.isReportedByPyThread else self.isReportedByFwTask
            _tid    = None if _bTType is None else self.__tid
            _tname  = None if _bTType is None else self.__tskName

            res = _LcFrcView( eCID_=self.__eCID, ferr_=_ferr, bForeignFE_=self.__bFFE, bTType_=_bTType
                            , tskName_=_tname, thrdName_=self.__thrdName, tid_=_tid, tuid_=self.__tuid)
            if not res.isValid:
                res.CleanUp()
                res = None
                vlogif._LogOEC(True, -1563)
            return res

        @property
        def __isInvalid(self):
            return self.__eCID is None

        def __UpdateTaskInfo(self, atask_ : _AbstractTask):
            if self.__isInvalid:
                return

            if not self.isReportedByPyThread:
                return

            _tuid = id(atask_.linkedPyThread)

            if self.__tuid != _tuid:
                return

            prvStr = self.ToString()
            self.__tid     = atask_.taskID
            self.__tuid    = _tuid
            self.__bFFE    = (self.__feClone is not None) and self.__feClone.IsForeignTaskError(atask_.taskID)
            self.__ttype   = _LcStateImpl._EFrcRecordTaskType.eFwTask if atask_.isFwTask else _LcStateImpl._EFrcRecordTaskType.eFwThread
            self.__tskName = str(atask_.taskName)
            self.__tskName = str(atask_.linkedPyThread.name)


    class _FrcRecordManager:
        __slots__ = [ '__lstFrcRecs' ]

        def __init__(self):
            self.__lstFrcRecs = None

        def __str__(self):
            return self.ToString()

        @property
        def firstFrcRecord(self):
            res = None
            if self.__lstFrcRecs is not None:
                res = self.__lstFrcRecs[0]
            return res

        def FindFrcRecord(self, eCID_ : _ELcCompID, atask_ : _AbstractTask =None):
            if eCID_ is None:
                _LcStateImpl._RaiseException(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcStateImpl_TextID_001))
                return None
            elif self.__lstFrcRecs is None:
                return None

            res = None
            for _ee in self.__lstFrcRecs:
                if _ee.IsMatching(eCID_, atask_=atask_):
                    res = _ee
            return res

        def AddFrcRecord(self, eCID_ : _ELcCompID, ferr_, atask_ : _AbstractTask =None):
            if (eCID_ is None) or (ferr_ is None):
                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcStateImpl_TextID_002).format(str(eCID_) if eCID_ is None else eCID_.compactName)
                _LcStateImpl._RaiseException(_errMsg)
                return

            if self.__lstFrcRecs is None:
                self.__lstFrcRecs = []

            self.__lstFrcRecs.append(_LcStateImpl._FrcRecord(eCID_, ferr_, atask_=atask_))

        def UpdateLcRuntimeFailure(self):
            if self.__lstFrcRecs is None:
                return

            _lstRuntimeFailures = []
            for _ee in self.__lstFrcRecs:
                _frcv = _ee._CreateFrcView()
                if _frcv is None:

                    vlogif._LogOEC(True, -1564)
                    return
                _lstRuntimeFailures.append(_LcRuntimeFailure(_frcv))

            _LcFailure.UpdateLcRuntimeFailure(_lstRuntimeFailures)

        def ToString(self) -> str:
            res = None
            if self.__lstFrcRecs is not None:
                _NUM = len(self.__lstFrcRecs)
                if _NUM > 0:
                    res = ''
                    for _ii in range(_NUM):
                        if _ii > 0:
                            if _ii == 1:
                                res += _FwTDbEngine.GetText(_EFwTextID.eLcStateImpl_FrcList_ToString_001)
                            res += _FwTDbEngine.GetText(_EFwTextID.eLcStateImpl_FrcList_ToString_002).format(_ii)
                        res += self.__lstFrcRecs[_ii].ToString()
            return res

        def CleanUp(self):
            self._Reset()

        def _Reset(self):
            if self.__lstFrcRecs is not None:
                for _ee in self.__lstFrcRecs:
                    _ee.CleanUp()
                self.__lstFrcRecs.clear()
                self.__lstFrcRecs = None


    __slots__ = [ '__eBitMask' , '__apiLock' , '__frcRecMgr' ]

    def __init__(self, ppass_ : int):
        super().__init__(ppass_)

        self.__apiLock   = _PyRLock()
        self.__eBitMask  = _ELcStateFlag.LcDefaultMask()
        self.__frcRecMgr = _LcStateImpl._FrcRecordManager()

    @property
    def isLcOperable(self) -> bool:
        if self.__isInvalid: return False
        with self.__apiLock:
            _mm = _ELcStateFlag.ebfLcStarted | _ELcStateFlag.ebfTMgrStarted | _ELcStateFlag.ebfFwMainStarted
            res = _ELcStateFlag.IsLcBitFlagSet(self.__eBitMask, _mm)
            res = res and not _ELcStateFlag.IsAnyFailedBitFlagSet(self.__eBitMask)
            return res

    @property
    def isLcCoreOperable(self) -> bool:
        if self.__isInvalid: return False
        with self.__apiLock:
            _mm = _ELcStateFlag.ebfLcStarted | _ELcStateFlag.ebfTMgrStarted | _ELcStateFlag.ebfFwMainStarted
            res = _ELcStateFlag.IsLcBitFlagSet(self.__eBitMask, _mm)
            return res

    @property
    def isLcPreCoreOperable(self) -> bool:
        if self.__isInvalid: return False
        with self.__apiLock:
            _mm = _ELcStateFlag.ebfLcStarted | _ELcStateFlag.ebfTMgrStarted
            res = _ELcStateFlag.IsLcBitFlagSet(self.__eBitMask, _mm)
            return res

    @property
    def isLcStarted(self):
        if self.__isInvalid: return False
        with self.__apiLock:
            return _ELcStateFlag.IsLcStarted(self.__eBitMask)

    @property
    def isTaskManagerStarted(self):
        if self.__isInvalid: return False
        with self.__apiLock:
            return _ELcStateFlag.IsTMgrStarted(self.__eBitMask)


    @property
    def isFwMainStarted(self):
        if self.__isInvalid: return False
        with self.__apiLock:
            return _ELcStateFlag.IsFwMainStarted(self.__eBitMask)


    @property
    def isMainXTaskStarted(self):
        if self.__isInvalid: return False
        with self.__apiLock:
            return _ELcStateFlag.IsMainXTaskStarted(self.__eBitMask)


    @property
    def isLcStopped(self):
        if self.__isInvalid: return True
        with self.__apiLock:
            return _ELcStateFlag.IsLcStopped(self.__eBitMask)

    @property
    def isTaskManagerStopped(self):
        if self.__isInvalid: return False
        with self.__apiLock:
            return _ELcStateFlag.IsTMgrStopped(self.__eBitMask)


    @property
    def isFwMainStopped(self):
        if self.__isInvalid: return True
        with self.__apiLock:
            return _ELcStateFlag.IsFwMainStopped(self.__eBitMask)


    @property
    def isMainXTaskStopped(self):
        if self.__isInvalid: return True
        with self.__apiLock:
            return _ELcStateFlag.IsMainXTaskStopped(self.__eBitMask)


    @property
    def isLcFailed(self):
        if self.__isInvalid: return True
        with self.__apiLock:
            return _ELcStateFlag.IsLcFailed(self.__eBitMask)

    @property
    def isTaskManagerFailed(self):
        if self.__isInvalid: return False
        with self.__apiLock:
            return _ELcStateFlag.IsTMgrFailed(self.__eBitMask)

    @property
    def isFwCompFailed(self):
        if self.__isInvalid: return True
        with self.__apiLock:
            return _ELcStateFlag.IsFwCompFailed(self.__eBitMask)

    @property
    def isFwMainFailed(self):
        if self.__isInvalid: return True
        with self.__apiLock:
            return _ELcStateFlag.IsFwMainFailed(self.__eBitMask)

    @property
    def isXTaskFailed(self):
        if self.__isInvalid: return False
        with self.__apiLock:
            return _ELcStateFlag.IsXTaskFailed(self.__eBitMask)

    @property
    def isMainXTaskFailed(self):
        if self.__isInvalid: return False
        with self.__apiLock:
            return _ELcStateFlag.IsMainXTaskFailed(self.__eBitMask)

    @property
    def isMiscCompFailed(self):
        if self.__isInvalid: return False
        with self.__apiLock:
            return _ELcStateFlag.IsMiscCompFailed(self.__eBitMask)

    @property
    def isLcStartedExclusive(self):
        if self.__isInvalid: return False
        with self.__apiLock:
            return _ELcStateFlag.IsLcBitMaskExclusive(self.__eBitMask) and self.isLcStarted

    @property
    def hasLcAnyStoppedState(self):
        if self.__isInvalid: return True
        with self.__apiLock:
            return _ELcStateFlag.IsAnyStoppedBitFlagSet(self.__eBitMask)

    @property
    def hasLcAnyFailureState(self):
        if self.__isInvalid: return True
        with self.__apiLock:
            return _ELcStateFlag.IsAnyFailedBitFlagSet(self.__eBitMask)

    @property
    def lcFrcView(self) -> _LcFrcView:
        res = None
        if self.__isInvalid:
            pass
        else:
            with self.__apiLock:
                res = self.__firstFrcRecord
                if res is not None:
                    res = res._CreateFrcView()
        return res

    def HasLcCompFRC(self, eLcCompID_ : _ELcCompID, atask_ : _AbstractTask =None) -> bool:
        if self.__isInvalid: return False
        with self.__apiLock:
            return self.__frcRecMgr.FindFrcRecord(eLcCompID_, atask_=atask_) is not None

    def GetLcCompFrcView(self, eLcCompID_ : _ELcCompID, atask_ : _AbstractTask =None) -> _LcFrcView:
        if self.__isInvalid: return None
        with self.__apiLock:
            res = self.__frcRecMgr.FindFrcRecord(eLcCompID_, atask_=atask_)
            if res is not None:
                res = res._CreateFrcView()
            return res

    @property
    def _isLcIdle(self):
        if self.__isInvalid: return False
        with self.__apiLock:
            return _ELcStateFlag.IsLcIdle(self.__eBitMask)

    def _SetLcState(self, eLcCompID_ : _ELcCompID, bStartStopFailFlag_ : [bool, None], frcError_ : _FatalEntry =None, atask_ : _AbstractTask =None) -> bool:

        if self.__isInvalid:
            return False

        with self.__apiLock:
            pcr = self.__PreCheckSetRequest(eLcCompID_, bStartStopFailFlag_, frcError_=frcError_, atask_=atask_)
            if pcr is None:
                return False

            _eCheckRes = self.__CheckRuleViolation__LcAlreadyStopped(pcr)
            if not _eCheckRes.isContinue:
                return _eCheckRes.isStop

            _eCheckRes = self.__CheckRuleViolation__StartTransition(pcr)
            if not _eCheckRes.isContinue:
                return _eCheckRes.isStop

            _eCheckRes = self.__CheckRuleViolation__StopTransition(pcr)
            if not _eCheckRes.isContinue:
                return _eCheckRes.isStop

            _eCheckRes = self.__CheckRuleViolation__UnsupportStartStopTransition(pcr)
            if not _eCheckRes.isContinue:
                return _eCheckRes.isStop

            _eCheckRes = self.__CheckRuleViolation__ResetSameTransition(pcr)
            if not _eCheckRes.isContinue:
                return _eCheckRes.isStop

            return self.__UpdateLcState(pcr)

    def _RestoreCurBitMask(self, eBitMask_ : _FwIntFlag):
        if self.__isInvalid:
            return
        if not isinstance(eBitMask_, _ELcStateFlag):
            return
        with self.__apiLock:
            self.__eBitMask = eBitMask_

    def _ToString(self, *args_, **kwargs_):
        if self.__isInvalid:
            return None

        _bCompact = False
        if len(args_) > 0:
            for _ii in range(len(args_)):
                if _ii == 0:
                    _bCompact = args_[_ii]

        with self.__apiLock:
            res = ''

            if self._isLcIdle:
                res += _FwTDbEngine.GetText(_EFwTextID.eLcStateImpl_ToString_01)
            else:
                _xco     = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_Name_Xco)
                _comp    = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_Name_Comp)
                _main    = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_Name_Main)
                _mainXco = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_Name_MainXco)
                _midPart = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_027)

                if   self.isLcFailed:            res += _CommonDefines._CHAR_SIGN_SPACE   + _ELcStateTransReq.eLcFailed.compactName
                elif self.isLcStarted:           res += _CommonDefines._CHAR_SIGN_SPACE   + _ELcStateTransReq.eLcStarted.compactName
                elif self.isLcStopped:           res += _CommonDefines._CHAR_SIGN_SPACE   + _ELcStateTransReq.eLcStopped.compactName

                if   self.isTaskManagerFailed:   res += _midPart + _ELcStateTransReq.eTMgrFailed.compactName
                elif self.isTaskManagerStarted:  res += _midPart + _ELcStateTransReq.eTMgrStarted.compactName
                elif self.isTaskManagerStopped:  res += _midPart + _ELcStateTransReq.eTMgrStopped.compactName

                if   self.isFwCompFailed:        res += _midPart + _ELcStateTransReq.eFwCompFailed.compactName

                if   self.isFwMainFailed:        res += _midPart + _StrUtil.ReplaceSubstring(_ELcStateTransReq.eFwCompFailed.compactName, _comp, _main)
                elif self.isFwMainStarted:       res += _midPart + _StrUtil.ReplaceSubstring(_ELcStateTransReq.eFwCompStarted.compactName, _comp, _main)
                elif self.isFwMainStopped:       res += _midPart + _StrUtil.ReplaceSubstring(_ELcStateTransReq.eFwCompStopped.compactName, _comp, _main)

                if   self.isXTaskFailed:       res += _midPart + _ELcStateTransReq.eXTaskFailed.compactName

                if   self.isMainXTaskFailed:   res += _midPart + _StrUtil.ReplaceSubstring(_ELcStateTransReq.eXTaskFailed.compactName, _xco, _mainXco)
                elif self.isMainXTaskStarted:  res += _midPart + _StrUtil.ReplaceSubstring(_ELcStateTransReq.eXTaskStarted.compactName, _xco, _mainXco)
                elif self.isMainXTaskStopped:  res += _midPart + _StrUtil.ReplaceSubstring(_ELcStateTransReq.eXTaskStopped.compactName, _xco, _mainXco)

                if   self.isMiscCompFailed:      res += _midPart + _ELcStateTransReq.eMiscCompFailed.compactName

            res = _FwTDbEngine.GetText(_EFwTextID.eLcStateImpl_ToString_02).format(hex(self.__eBitMask), res)
            if not _bCompact:
                _myTxt = self.__frcRecMgr.ToString()
                if _myTxt is not None:
                    res += f'{_CommonDefines._CHAR_SIGN_NEWLINE}{_CommonDefines._CHAR_SIGN_TAB}{_myTxt}'
            return res

    def _CleanUpByOwnerRequest(self):
        if self.__isInvalid:
            pass
        else:
            if self.__frcRecMgr is not None:
                self.__frcRecMgr.CleanUp()
            self.__apiLock   = None
            self.__eBitMask  = None
            self.__frcRecMgr = None

    @property
    def __isInvalid(self):
        return self.__eBitMask is None

    @property
    def __firstFrcRecord(self):
        return None if self.__isInvalid else self.__frcRecMgr.firstFrcRecord

    def __CheckRuleViolation__LcAlreadyStopped(self, pcr_ : _TransReqPreCheckResult) -> _ETernaryOpResult:
        if self.isLcStopped:
            _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcStateImpl_TextID_004).format(pcr_.paramsCurStateStr)
            _LcStateImpl._RaiseException(_errMsg)
            return _ETernaryOpResult.Abort()
        return _ETernaryOpResult.Continue()

    def __CheckRuleViolation__StartTransition(self, pcr_ : _TransReqPreCheckResult) -> _ETernaryOpResult:
        if pcr_.eLcTrans.isStartTransitionRequest:
            if pcr_.bStopSeeded or pcr_.bFailSeeded:
                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcStateImpl_TextID_005).format(pcr_.paramsCurStateStr)
                _LcStateImpl._RaiseException(_errMsg)
                return _ETernaryOpResult.Abort()
        return _ETernaryOpResult.Continue()

    def __CheckRuleViolation__StopTransition(self, pcr_ : _TransReqPreCheckResult) -> _ETernaryOpResult:
        if pcr_.eLcTrans.isStopTransitionRequest:
            if pcr_.bFailSeeded:
                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcStateImpl_TextID_006).format(pcr_.paramsCurStateStr)
                _LcStateImpl._RaiseException(_errMsg)
                return _ETernaryOpResult.Abort()
        return _ETernaryOpResult.Continue()

    def __CheckRuleViolation__UnsupportStartStopTransition(self, pcr_ : _TransReqPreCheckResult) -> _ETernaryOpResult:
        if not pcr_.eLcTrans.isFailureTransitionRequest:
            _bIgnore =             (pcr_.ebfRequest == _ELcStateFlag.ebfFwCompStarted) or (pcr_.ebfRequest == _ELcStateFlag.ebfFwCompStopped)
            _bIgnore = _bIgnore or (pcr_.ebfRequest == _ELcStateFlag.ebfXTaskStarted) or (pcr_.ebfRequest == _ELcStateFlag.ebfXTaskStopped)
            _bIgnore = _bIgnore or (pcr_.ebfRequest == _ELcStateFlag.ebfMiscCompStarted) or (pcr_.ebfRequest == _ELcStateFlag.ebfMiscCompStopped)
            if _bIgnore:
                return _ETernaryOpResult.Stop()
        return _ETernaryOpResult.Continue()

    def __CheckRuleViolation__ResetSameTransition(self, pcr_ : _TransReqPreCheckResult) -> _ETernaryOpResult:
        if     pcr_.eLcTrans.isFailureTransitionRequest \
           and ((pcr_.ebfRequest == _ELcStateFlag.ebfFwCompFailed) or (pcr_.ebfRequest == _ELcStateFlag.ebfXTaskFailed) or (pcr_.ebfRequest == _ELcStateFlag.ebfMiscCompFailed)):
            _frc = self.__frcRecMgr.FindFrcRecord(pcr_.eLcCompID, atask_=pcr_.absTask)
            if _frc is not None:
                return _ETernaryOpResult.Abort()
        elif pcr_.bRequestSeeded:
            return _ETernaryOpResult.Stop()
        return _ETernaryOpResult.Continue()

    def __UpdateLcState( self, pcr_ : _TransReqPreCheckResult):
        _eOldBitMask = self.__eBitMask

        if pcr_.ebfRequestInv is not None:
            self.__eBitMask = _ELcStateFlag.RemoveLcBitFlag(self.__eBitMask, pcr_.ebfRequestInv)

            if _ELcStateFlag.IsLcBitFlagSet(self.__eBitMask, pcr_.ebfRequestInv):
                self.__eBitMask = _eOldBitMask
                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcStateImpl_TextID_007).format(pcr_.paramsCurStateStr)
                _LcStateImpl._RaiseException(_errMsg)
                return False

        self.__eBitMask = _ELcStateFlag.AddLcBitFlag(self.__eBitMask, pcr_.ebfRequest)

        if not _ELcStateFlag.IsLcBitFlagSet(self.__eBitMask, pcr_.ebfRequest):
            self.__eBitMask = _eOldBitMask
            _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcStateImpl_TextID_008).format(1, pcr_.paramsCurStateStr)
            _LcStateImpl._RaiseException(_errMsg)
            return False

        res = self.__eBitMask != _eOldBitMask
        if not res:
            self.__eBitMask = _eOldBitMask
            _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcStateImpl_TextID_008).format(2, pcr_.paramsCurStateStr)
            _LcStateImpl._RaiseException(_errMsg)
            return False

        _frcErr = None
        if pcr_.fatalError is not None:
            _bClone = pcr_.fatalError.isClone
            if _bClone:
                _frcErr = pcr_.fatalError
            else:
                _frcErr = pcr_.fatalError.Clone()
                if _frcErr is None:
                    self.__eBitMask = _eOldBitMask
                    _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcStateImpl_TextID_010).format(type(pcr_.fatalError).__name__, pcr_.paramsCurStateStr, str(pcr_.fatalError))
                    _LcStateImpl._RaiseException(_errMsg)
                    return False

            self.__frcRecMgr.AddFrcRecord(pcr_.eLcCompID, _frcErr, atask_=pcr_.absTask)
            if not self.HasLcCompFRC(pcr_.eLcCompID, atask_=pcr_.absTask):
                self.__eBitMask = _eOldBitMask
                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcStateImpl_TextID_008).format(3, pcr_.paramsCurStateStr)
                _LcStateImpl._RaiseException(_errMsg)
                return False

            if not _bClone:
                pcr_.fatalError._UpdateErrorImpact(_EErrorImpact.eNoImpactByFrcLinkage)



        _frcRec = self.__firstFrcRecord
        if self.hasLcAnyFailureState:
            if _frcRec is None:
                self.__eBitMask = _eOldBitMask
                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcStateImpl_TextID_012).format(4, pcr_.paramsCurStateStr)
                _LcStateImpl._RaiseException(_errMsg)
                return False
        elif _frcRec is not None:
            self.__eBitMask = _eOldBitMask
            _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcStateImpl_TextID_012).format(5, pcr_.paramsCurStateStr)
            _LcStateImpl._RaiseException(_errMsg)
            return False

        _LcFailure._SetCurrentLcState(self.ToString(), self.lcFrcView)
        self.__frcRecMgr.UpdateLcRuntimeFailure()
        return res

    def __PreCheckSetRequest(self, eLcCompID_: _ELcCompID, bStartStopFailFlag_: [bool, None], frcError_: _FatalEntry =None, atask_: _AbstractTask =None) -> _TransReqPreCheckResult:
        if not isinstance(eLcCompID_, _ELcCompID):
            _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcStateImpl_TextID_013).format(type(eLcCompID_).__name__)
            _LcStateImpl._RaiseException(_errMsg)
            return None

        a3 = _ELcStateTransReq._ConvertFromLcCompID(eLcCompID_, bStartStopFailFlag_=bStartStopFailFlag_)
        if a3 is None:
            _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcStateImpl_TextID_011).format(
                eLcCompID_.compactName, eLcCompID_.value)
            _LcStateImpl._RaiseException(_errMsg)
            return None

        a5 = _FwTDbEngine.GetText(_EFwTextID.eLcStateImpl_UpdateLcState_PreCheckSetRequest_FmtStr_01).format(
            hex(self.__eBitMask), eLcCompID_.compactName, str(bStartStopFailFlag_), a3.compactName, type(frcError_).__name__, type(atask_).__name__)
        a6 = a5 + _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_012).format(self)

        if not ((atask_ is None) or (isinstance(atask_, _AbstractTask) and (atask_.taskBadge is not None))):
            _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcStateImpl_TextID_014).format(1, a5)
            _LcStateImpl._RaiseException(_errMsg)
            return None

        if a3.isFailureTransitionRequest:
            if (bStartStopFailFlag_ is not None) or (not isinstance(frcError_, _FatalEntry)) or frcError_.hasNoErrorImpact:
                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcStateImpl_TextID_014).format(2, a5)
                _LcStateImpl._RaiseException(_errMsg)
                return None

        else:
            if not (isinstance(bStartStopFailFlag_, bool) and (frcError_ is None)):
                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcStateImpl_TextID_014).format(3, a5)
                _LcStateImpl._RaiseException(_errMsg)
                return None

        a8      = _LcStateImpl.__Enum2RelatedFailedBitFlag(a3, eLcCompID_)
        a9     = _LcStateImpl.__Enum2RelatedStoppedBitFlag(a3, eLcCompID_)
        a7, a10 = _LcStateImpl.__Enum2BitFlagsPair(a3, eLcCompID_)

        if (a7 is None) or (a8 is None) or (a9 is None):
            return None

        a11 = _ELcStateFlag.IsLcBitFlagSet(self.__eBitMask, a8)
        a12 = _ELcStateFlag.IsLcBitFlagSet(self.__eBitMask, a9)
        a13  = _ELcStateFlag.IsLcBitFlagSet(self.__eBitMask, a7)

        res = _TransReqPreCheckResult( atask_, frcError_, a3, eLcCompID_, a5, a6, a7, a8, a9, a10, a11, a12, a13)
        return res

    @staticmethod
    def __Enum2BitFlagsPair(eLcSTReq_ : _ELcStateTransReq, eLcCompID_ : _ELcCompID):
        res     = None
        _resInv = None

        if eLcCompID_ == _ELcCompID.eLcMgr:
            if   eLcSTReq_ == _ELcStateTransReq.eLcStarted: res, _resInv = _ELcStateFlag.ebfLcStarted , None
            elif eLcSTReq_ == _ELcStateTransReq.eLcStopped: res, _resInv = _ELcStateFlag.ebfLcStopped , _ELcStateFlag.ebfLcStarted
            elif eLcSTReq_ == _ELcStateTransReq.eLcFailed:  res, _resInv = _ELcStateFlag.ebfLcFailed  , _ELcStateFlag.ebfLcStarted

        elif eLcCompID_ == _ELcCompID.eTMgr:
            if   eLcSTReq_ == _ELcStateTransReq.eTMgrStarted: res, _resInv = _ELcStateFlag.ebfTMgrStarted , None
            elif eLcSTReq_ == _ELcStateTransReq.eTMgrStopped: res, _resInv = _ELcStateFlag.ebfTMgrStopped , _ELcStateFlag.ebfTMgrStarted
            elif eLcSTReq_ == _ELcStateTransReq.eTMgrFailed:  res, _resInv = _ELcStateFlag.ebfTMgrFailed  , _ELcStateFlag.ebfTMgrStarted

        elif eLcCompID_.lcCompGroupID == _ELcCompID.eFwComp:
            if eLcSTReq_ == _ELcStateTransReq.eFwCompStarted:
                if eLcCompID_ == _ELcCompID.eFwMain:
                    res, _resInv = _ELcStateFlag.ebfFwMainStarted , None
                else:
                    res, _resInv = _ELcStateFlag.ebfFwCompStarted , None
            elif eLcSTReq_ == _ELcStateTransReq.eFwCompStopped:
                if eLcCompID_==_ELcCompID.eFwMain:
                    res, _resInv = _ELcStateFlag.ebfFwMainStopped, _ELcStateFlag.ebfFwMainStarted
                else:
                    res, _resInv = _ELcStateFlag.ebfFwCompStopped , _ELcStateFlag.ebfFwCompStarted
            elif eLcSTReq_ == _ELcStateTransReq.eFwCompFailed:
                if eLcCompID_==_ELcCompID.eFwMain:
                    res, _resInv = _ELcStateFlag.ebfFwMainFailed , _ELcStateFlag.ebfFwMainStarted
                else:
                    res, _resInv = _ELcStateFlag.ebfFwCompFailed , _ELcStateFlag.ebfFwCompStarted

        elif eLcCompID_.lcCompGroupID == _ELcCompID.eXTask:
            if eLcSTReq_ == _ELcStateTransReq.eXTaskStarted:
                if eLcCompID_ == _ELcCompID.eMainXTask:
                    res, _resInv = _ELcStateFlag.ebfMainXTaskStarted , None
                else:
                    res, _resInv = _ELcStateFlag.ebfXTaskStarted , None
            elif eLcSTReq_ == _ELcStateTransReq.eXTaskStopped:
                if eLcCompID_ == _ELcCompID.eMainXTask:
                    res, _resInv = _ELcStateFlag.ebfMainXTaskStopped , _ELcStateFlag.ebfMainXTaskStarted
                else:
                    res, _resInv = _ELcStateFlag.ebfXTaskStopped , _ELcStateFlag.ebfXTaskStarted
            elif eLcSTReq_ == _ELcStateTransReq.eXTaskFailed:
                if eLcCompID_==_ELcCompID.eMainXTask:
                    res, _resInv = _ELcStateFlag.ebfMainXTaskFailed , _ELcStateFlag.ebfMainXTaskStarted
                else:
                    res, _resInv = _ELcStateFlag.ebfXTaskFailed, _ELcStateFlag.ebfXTaskStarted

        elif eLcCompID_ == _ELcCompID.eMiscComp:
            if   eLcSTReq_ == _ELcStateTransReq.eMiscCompStarted: res, _resInv = _ELcStateFlag.ebfMiscCompStarted , None
            elif eLcSTReq_ == _ELcStateTransReq.eMiscCompStopped: res, _resInv = _ELcStateFlag.ebfMiscCompStopped , _ELcStateFlag.ebfMiscCompStarted
            elif eLcSTReq_ == _ELcStateTransReq.eMiscCompFailed:  res, _resInv = _ELcStateFlag.ebfMiscCompFailed  , _ELcStateFlag.ebfMiscCompStarted

        if res is None:
            _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcStateImpl_TextID_009).format(1, eLcSTReq_.compactName, eLcCompID_.compactName)
            _LcStateImpl._RaiseException(_errMsg)
        return res, _resInv

    @staticmethod
    def __Enum2RelatedFailedBitFlag(eLcSTReq_ : _ELcStateTransReq, eLcCompID_ : _ELcCompID):
        _bMain = (eLcCompID_==_ELcCompID.eFwMain) or (eLcCompID_==_ELcCompID.eMainXTask)

        if eLcSTReq_ == _ELcStateTransReq.eLcStarted or eLcSTReq_ == _ELcStateTransReq.eLcStopped or eLcSTReq_ == _ELcStateTransReq.eLcFailed:
            res = _ELcStateFlag.ebfLcFailed

        elif eLcSTReq_ == _ELcStateTransReq.eTMgrStarted or eLcSTReq_ == _ELcStateTransReq.eTMgrStopped or eLcSTReq_ == _ELcStateTransReq.eTMgrFailed:
            res = _ELcStateFlag.ebfTMgrFailed

        elif eLcSTReq_ == _ELcStateTransReq.eFwCompStarted or eLcSTReq_ == _ELcStateTransReq.eFwCompStopped or eLcSTReq_ == _ELcStateTransReq.eFwCompFailed:
            res = _ELcStateFlag.ebfFwMainFailed if _bMain else _ELcStateFlag.ebfFwCompFailed

        elif eLcSTReq_ == _ELcStateTransReq.eXTaskStarted or eLcSTReq_ == _ELcStateTransReq.eXTaskStopped or eLcSTReq_ == _ELcStateTransReq.eXTaskFailed:
            res = _ELcStateFlag.ebfMainXTaskFailed if _bMain else _ELcStateFlag.ebfXTaskFailed

        elif eLcSTReq_ == _ELcStateTransReq.eMiscCompStarted or eLcSTReq_ == _ELcStateTransReq.eMiscCompStopped or eLcSTReq_ == _ELcStateTransReq.eMiscCompFailed:
            res = _ELcStateFlag.ebfMiscCompFailed

        else:
            res = None
            _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcStateImpl_TextID_009).format(2, eLcSTReq_.compactName, eLcCompID_.compactName)
            _LcStateImpl._RaiseException(_errMsg)
        return res

    @staticmethod
    def __Enum2RelatedStoppedBitFlag(eLcSTReq_ : _ELcStateTransReq, eLcCompID_ : _ELcCompID):
        _bMain = (eLcCompID_==_ELcCompID.eFwMain) or (eLcCompID_==_ELcCompID.eMainXTask)

        if eLcSTReq_ == _ELcStateTransReq.eLcStarted or eLcSTReq_ == _ELcStateTransReq.eLcStopped or eLcSTReq_ == _ELcStateTransReq.eLcFailed:
            res = _ELcStateFlag.ebfLcStopped

        elif eLcSTReq_ == _ELcStateTransReq.eTMgrStarted or eLcSTReq_ == _ELcStateTransReq.eTMgrStopped or eLcSTReq_ == _ELcStateTransReq.eTMgrFailed:
            res =  _ELcStateFlag.ebfTMgrStopped

        elif eLcSTReq_ == _ELcStateTransReq.eFwCompStarted or eLcSTReq_ == _ELcStateTransReq.eFwCompStopped or eLcSTReq_ == _ELcStateTransReq.eFwCompFailed:
            res =  _ELcStateFlag.ebfFwMainStopped if _bMain else _ELcStateFlag.ebfFwCompStopped

        elif eLcSTReq_ == _ELcStateTransReq.eXTaskStarted or eLcSTReq_ == _ELcStateTransReq.eXTaskStopped or eLcSTReq_ == _ELcStateTransReq.eXTaskFailed:
            res =  _ELcStateFlag.ebfMainXTaskStopped if _bMain else _ELcStateFlag.ebfXTaskStopped

        elif eLcSTReq_ == _ELcStateTransReq.eMiscCompStarted or eLcSTReq_ == _ELcStateTransReq.eMiscCompStopped or eLcSTReq_ == _ELcStateTransReq.eMiscCompFailed:
            res =  _ELcStateFlag.ebfMiscCompStopped

        else:
            res =None
            _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcStateImpl_TextID_009).format(3, eLcSTReq_.compactName, eLcCompID_.compactName)
            _LcStateImpl._RaiseException(_errMsg)
        return res

    @staticmethod
    def _RaiseException(xcpMsg_):
        if vlogif._IsVSystemExitEnabled():
            raise SystemExit(xcpMsg_)
        else:
            vlogif._LogOEC(True, -1565)
