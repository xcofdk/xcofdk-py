# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : taskutil.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

import string
import threading

from enum      import auto
from enum      import IntEnum
from enum      import IntFlag
from enum      import unique
from threading import RLock  as _PyRLock
from threading import Thread as _PyThread
from time      import sleep  as _PySleep
from typing    import Union

from xcofdk.fwcom import CompoundTUID

from _fw.fwssys.fwcore.logging           import vlogif
from _fw.fwssys.fwcore.base.gtimeout     import _Timeout
from _fw.fwssys.fwcore.base.util         import _Util
from _fw.fwssys.fwcore.swpfm.sysinfo     import _SystemInfo
from _fw.fwssys.fwcore.types.atomicint   import _AtomicInteger
from _fw.fwssys.fwcore.types.ebitmask    import _EBitMask
from _fw.fwssys.fwcore.types.commontypes import _FwIntEnum
from _fw.fwssys.fwcore.types.commontypes import _EDepInjCmd
from _fw.fwssys.fwcore.types.commontypes import _Limits
from _fw.fwssys.fwerrh.fwerrorcodes      import _EFwErrorCode

@unique
class _ETaskType(_FwIntEnum):
    eCFwThread       = 111
    eFwThread        = 211
    eFwMainThread    = auto()
    eXTaskThread     = auto()
    eMainXTaskThread = auto()
    eFwTask          = 311
    eFwMainTask      = auto()
    eXTaskTask       = auto()
    eMainXTaskTask   = auto()

    @property
    def isCFwThread(self):
        return self == _ETaskType.eCFwThread

    @property
    def isFwThread(self):
        return _ETaskType.eFwThread.value <= self.value <= _ETaskType.eMainXTaskThread.value

    @property
    def isFwTask(self):
        return self.value >= _ETaskType.eFwTask.value

    @property
    def isFwMain(self):
        return (self == _ETaskType.eFwMainTask) or (self == _ETaskType.eFwMainThread)

    @property
    def isFwMainThread(self):
        return self == _ETaskType.eFwMainThread

    @property
    def isFwMainTask(self):
        return self == _ETaskType.eFwMainTask

    @property
    def isXTaskThread(self):
        return _ETaskType.eXTaskThread.value <= self.value <= _ETaskType.eMainXTaskThread.value

    @property
    def isMainXTaskThread(self):
        return self == _ETaskType.eMainXTaskThread

    @property
    def isXTaskTask(self):
        return _ETaskType.eXTaskTask.value <= self.value <= _ETaskType.eMainXTaskTask.value

    @property
    def isMainXTaskTask(self):
        return self == _ETaskType.eMainXTaskTask

@unique
class _ETaskResFlag(IntFlag):
    eNone = _EBitMask.eNone.value

    @staticmethod
    def IsResourceFlagSet(resMask_, resFlags_):
        return _EBitMask.IsEnumBitFlagSet(resMask_, resFlags_)

    @staticmethod
    def AddResourceFlag(resMask_, resFlags_):
        return _EBitMask.AddEnumBitFlag(resMask_, resFlags_)

    @staticmethod
    def GetRessourcesMask() -> IntFlag:
        res = _ETaskResFlag.eNone
        return res

@unique
class _ETaskRightFlag(IntFlag):
    eNone                 = 0x0000
    eFwTask               = 0x8000
    eUserTask             = 0x4000
    eXTaskTask            = (1 << 0)
    eErrorObserver        = (1 << 2)
    eDieXcpTarget         = (1 << 3)
    eDieXcpDelegateTarget = (1 << 4)

    @staticmethod
    def FwTaskRightDefaultMask():
        return _ETaskRightFlag(_ETaskRightFlag.eFwTask)

    @staticmethod
    def UserTaskRightDefaultMask():
        return _ETaskRightFlag(_ETaskRightFlag.eUserTask)

    @staticmethod
    def AddFwTaskRightFlag(trMask_ : IntFlag, trFlags_):
        trMask_ = _EBitMask.AddEnumBitFlag(trMask_, _ETaskRightFlag.eFwTask)
        return _EBitMask.AddEnumBitFlag(trMask_, trFlags_)

    @staticmethod
    def AddUserTaskRightFlag(trMask_ : IntFlag, trFlags_):
        if _ETaskRightFlag.IsTaskRightFlagSet(trMask_, _ETaskRightFlag.eFwTask):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00314)
            return None
        return _EBitMask.AddEnumBitFlag(trMask_, trFlags_)

    @staticmethod
    def AddXTaskTaskRight(trMask_ : IntFlag):
        if not _ETaskRightFlag.IsValidTaskRightMask(trMask_):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00315)
            return None
        return _EBitMask.AddEnumBitFlag(trMask_, _ETaskRightFlag.eXTaskTask)

    @staticmethod
    def IsFwTaskRightFlagSet(trMask_, trFlags_):
        res = _ETaskRightFlag.IsValidTaskRightMask(trMask_)
        if res:
            res = _EBitMask.IsEnumBitFlagSet(trMask_, _ETaskRightFlag.eFwTask)
            if res:
                res = _EBitMask.IsEnumBitFlagSet(trMask_, trFlags_)
        return res

    @staticmethod
    def IsUserTaskRightFlagSet(trMask_ : IntFlag, trFlags_):
        res = _ETaskRightFlag.IsValidTaskRightMask(trMask_)
        if res:
            res = _EBitMask.IsEnumBitFlagSet(trMask_, _ETaskRightFlag.eUserTask)
            if res:
                res = _EBitMask.IsEnumBitFlagSet(trMask_, trFlags_)
        return res

    @staticmethod
    def IsTaskRightFlagSet(trMask_ : IntFlag, trFlags_):
        return _EBitMask.IsEnumBitFlagSet(trMask_, trFlags_)

    @staticmethod
    def IsValidFwTaskRightMask(trMask_ : IntFlag):
        res = _ETaskRightFlag.IsValidTaskRightMask(trMask_)
        if res:
            res = _EBitMask.IsEnumBitFlagSet(trMask_, _ETaskRightFlag.eFwTask)
            if res:
                res = not _EBitMask.IsEnumBitFlagSet(trMask_, _ETaskRightFlag.eUserTask)
        return res

    @staticmethod
    def IsValidUserTaskRightMask(trMask_ : IntFlag):
        res = _ETaskRightFlag.IsValidTaskRightMask(trMask_)
        if res:
            res = _EBitMask.IsEnumBitFlagSet(trMask_, _ETaskRightFlag.eUserTask)
            if res:
                res = not _EBitMask.IsEnumBitFlagSet(trMask_, _ETaskRightFlag.eFwTask)
        return res

    @staticmethod
    def IsValidTaskRightMask(trMask_ : IntFlag):
        if not _Util.IsInstance(trMask_, _ETaskRightFlag, bThrowx_=True): return False
        return _ETaskRightFlag.eNone == (trMask_ & _ETaskRightFlag.__AllInvalidFlagsMask())

    @property
    def hasFwTaskRight(self):
        return _ETaskRightFlag.IsTaskRightFlagSet(self, _ETaskRightFlag.eFwTask)

    @property
    def hasUserTaskRight(self):
        return not _ETaskRightFlag.IsTaskRightFlagSet(self, _ETaskRightFlag.eFwTask)

    @property
    def hasXTaskTaskRight(self):
        return _ETaskRightFlag.IsTaskRightFlagSet(self, _ETaskRightFlag.eXTaskTask)

    @property
    def hasErrorObserverTaskRight(self):
        return _ETaskRightFlag.IsTaskRightFlagSet(self, _ETaskRightFlag.eErrorObserver)

    @property
    def hasDieXcpTargetTaskRight(self):
        return _ETaskRightFlag.IsTaskRightFlagSet(self, _ETaskRightFlag.eDieXcpTarget)

    @property
    def hasDieExceptionDelegateTargetTaskRight(self):
        return _ETaskRightFlag.IsTaskRightFlagSet(self, _ETaskRightFlag.eDieXcpDelegateTarget)

    @property
    def hasForeignErrorListnerTaskRight(self):
        return self.hasDieXcpTargetTaskRight or self.hasDieExceptionDelegateTargetTaskRight

    @staticmethod
    def __AllValidFlagsMask():
        res = _ETaskRightFlag.eNone
        for _ee in _ETaskRightFlag:
            res |= _ee
        return res

    @staticmethod
    def __AllInvalidFlagsMask():
        res = 0xFFFF
        for _ee in _ETaskRightFlag:
            if _ee == _ETaskRightFlag.eNone: continue
            res &= ~_ee.value
        return _ETaskRightFlag(res)

@unique
class _ETaskXPhaseID(_FwIntEnum):
    eNA = 0
    eDummyRunningAutoEnclThread        = 11
    eRunningNonDrivingXTaskSyncThread  = auto()
    eRunningNonDrivingXTaskASyncThread = auto()
    eFwHandling      = 21
    eRblSetup        = 31
    eRblTeardown     = auto()
    eRblRun          = auto()
    eRblProcIntMsg   = auto()
    eRblProcIntQueue = auto()
    eRblProcExtMsg   = auto()
    eRblProcExtQueue = auto()
    eRblMisc         = auto()
    eXTaskSetup      = 41
    eXTaskTeardown   = auto()
    eXTaskRun        = auto()
    eXTaskProcIntMsg = auto()
    eXTaskProcExtMsg = auto()

    @property
    def isNA(self):
        return self == _ETaskXPhaseID.eNA

    @property
    def isFwHandling(self):
        return self == _ETaskXPhaseID.eFwHandling

    @property
    def isRunnableExecution(self):
        return (self.value >= _ETaskXPhaseID.eRblSetup.value) and (self.value <= _ETaskXPhaseID.eRblMisc.value)

    @property
    def isXTaskExecution(self):
        return self.value >= _ETaskXPhaseID.eXTaskSetup.value

@unique
class _ETaskApiContextID(_FwIntEnum):
    eDontCare     = _ETaskXPhaseID.eNA.value
    eSetup        = _ETaskXPhaseID.eXTaskSetup.value
    eTeardown     = _ETaskXPhaseID.eXTaskTeardown.value
    eRun          = _ETaskXPhaseID.eXTaskRun.value
    eProcIntQueue = _ETaskXPhaseID.eXTaskProcIntMsg.value
    eProcExtQueue = _ETaskXPhaseID.eXTaskProcExtMsg.value

    @property
    def isDontCare(self):
        return self == _ETaskApiContextID.eDontCare

    @property
    def isSetup(self):
        return self == _ETaskApiContextID.eSetup

    @property
    def isRun(self):
        return self == _ETaskApiContextID.eRun

    @property
    def isTeardown(self):
        return self == _ETaskApiContextID.eTeardown

    @property
    def isProcessingQueue(self):
        return self.value > _ETaskApiContextID.eRun.value

@unique
class _EProcessingFeasibilityID(_FwIntEnum):
    eFeasible            = 440
    eUnfeasible          = 441
    eAborting            = 442
    eInCeaseMode         = 443
    eLcCoreInoperable    = 444
    eLcProxyUnavailable  = 445
    eOwnLcCompFailureSet = 446

    @property
    def isFeasible(self):
        return self == _EProcessingFeasibilityID.eFeasible

    @property
    def isUnfeasible(self):
        return self == _EProcessingFeasibilityID.eUnfeasible

    @property
    def isAborting(self):
        return self == _EProcessingFeasibilityID.eAborting

    @property
    def isInCeaseMode(self):
        return self == _EProcessingFeasibilityID.eInCeaseMode

    @property
    def isLcCoreInoperable(self):
        return self == _EProcessingFeasibilityID.eLcCoreInoperable

    @property
    def isLcProxyUnavailable(self):
        return self == _EProcessingFeasibilityID.eLcProxyUnavailable

    @property
    def isOwnLcCompFailureSet(self):
        return self == _EProcessingFeasibilityID.eOwnLcCompFailureSet

@unique
class _EFwApiBookmarkID(_FwIntEnum):
    eNA = 0

    eXTaskApiRequestStart   = 31
    eXTaskApiRequestRestart = 32
    eXTaskApiRequestStop    = 33
    eXTaskApiRequestJoin    = 34

    eXTaskApiBeginActionStart   = 74
    eXTaskApiBeginActionRestart = 75
    eXTaskApiBeginActionStop    = 76
    eXTaskApiBeginActionJoin    = 77

    @property
    def isXTaskApiRequest(self):
        return _EFwApiBookmarkID.eXTaskApiRequestStart.value <= self.value <= _EFwApiBookmarkID.eXTaskApiRequestJoin.value

    @property
    def isXTaskApiBeginAction(self):
        return _EFwApiBookmarkID.eXTaskApiBeginActionStart.value <= self.value <= _EFwApiBookmarkID.eXTaskApiBeginActionJoin.value

    @property
    def isNA(self):
        return self == _EFwApiBookmarkID.eNA

    @property
    def isXTaskApiRequestStart(self):
        return self == _EFwApiBookmarkID.eXTaskApiRequestStart

    @property
    def isXTaskApiRequestRestart(self):
        return self == _EFwApiBookmarkID.eXTaskApiRequestRestart

    @property
    def isXTaskApiRequestStop(self):
        return self == _EFwApiBookmarkID.eXTaskApiRequestStop

    @property
    def isXTaskApiRequestJoin(self):
        return self == _EFwApiBookmarkID.eXTaskApiRequestJoin

    @property
    def isXTaskApiBeginActionStart(self):
        return self == _EFwApiBookmarkID.eXTaskApiBeginActionStart

    @property
    def isXTaskApiBeginActionRetart(self):
        return self == _EFwApiBookmarkID.eXTaskApiBeginActionRestart

    @property
    def isXTaskApiBeginActionStop(self):
        return self == _EFwApiBookmarkID.eXTaskApiBeginActionStop

    @property
    def isXTaskApiBeginActionJoin(self):
        return self == _EFwApiBookmarkID.eXTaskApiBeginActionJoin

class _TaskIDDefines:
    _STARTUP_THREAD_ID             = 1001
    _TASK_ID_RANGE_SIZE            = 100000
    _TASK_ID_BASE_FACTOR           = 5
    _TASK_ID_RANGE_MAXSIZE         = 10000000
    _ENCL_TASK_ID_BASE_FACTOR      = 1
    _INVALID_TASK_ID               = _Limits.MIN_INT
    _NATIVE_THREAD_ID_SUPPORT_EVAL = -1
    _PUID_BASE                     = 2000
    _UTASK_ID_BASE                 = (_TASK_ID_RANGE_SIZE * _TASK_ID_BASE_FACTOR)      + (_STARTUP_THREAD_ID-1)
    _FWTASK_ID_BASE                = _STARTUP_THREAD_ID
    _AENCL_TASK_ID_BASE            = (_TASK_ID_RANGE_SIZE * _ENCL_TASK_ID_BASE_FACTOR) + (_STARTUP_THREAD_ID-1)

    @staticmethod
    def GetStartupThreadID():
        return _TaskIDDefines._STARTUP_THREAD_ID

class _StartupThread:
    __bF    = False
    __sgltn = None

    __slots__  = [ '__h' , '__tid' ]

    def __str__(self):
        return self.ToString()

    def __init__(self, taskID_ : int =None):
        self.__h   = None
        self.__tid = None
        if _StartupThread.__sgltn is not None:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00317)
        else:
            if taskID_ is None:
                taskID_ = _TaskIDDefines.GetStartupThreadID()

            self.__h   = threading.current_thread()
            self.__tid = taskID_

            _StartupThread.__sgltn = self

    @property
    def isMainPyThread(self):
        return (self.__h is not None) and (type(self.__h) == type(threading.main_thread()))

    @property
    def dtaskName(self):
        return self.hostThreadName

    @property
    def dtaskUID(self):
        return self.__tid

    @property
    def hostThreadName(self) -> str:
        return None if self.__h is None else self.__h.name

    @property
    def hostThreadUID(self):
        return None if self.__h is None else id(self.__h)

    def ToString(self) -> str:
        if self.__h is None:
            res = None
        else:
            res = '{}: (tasnName, taskUID, hostThrdUID)=({}, {}, {})'.format(type(self).__name__, self.dtaskName, self.dtaskUID, self.hostThreadUID)
        return res

    def CleanUp(self):
        self.__h   = None
        self.__tid = None
        if _StartupThread.__sgltn is not None:
            if id(_StartupThread.__sgltn) == id(self):
                _StartupThread.__sgltn = None

    @staticmethod
    def _GetInstance():
        if _StartupThread.__sgltn is None:
            _StartupThread(taskID_=None)
        return _StartupThread.__sgltn

    @staticmethod
    def _DepInjection(dinjCmd_: _EDepInjCmd, bFreezeUpdate_ =None):
        _StartupThread._GetInstance().__Update(dinjCmd_, bFreezeUpdate_=bFreezeUpdate_)

    def __Update(self, dinjCmd_: _EDepInjCmd, bFreezeUpdate_ =False, taskID_ : int =None):
        res = False
        if self.__h is None:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00318)
        elif _StartupThread.__bF and (bFreezeUpdate_ is not None):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00319)
        else:
            res = dinjCmd_.isDeInject or isinstance(bFreezeUpdate_, bool)
            if res:
                _StartupThread.__bF = False if dinjCmd_.isDeInject else bFreezeUpdate_

                self.__h = threading.current_thread()
                if taskID_ is not None:
                    self.__tid = taskID_
        return res

class _AutoEnclosedThreadsBag:
    __bag = None
    __lck = None

    @staticmethod
    def IsProcessingCurPyThread(curPyThrd_ =None):
        if _AutoEnclosedThreadsBag.__lck is None:
            return False

        res = False
        with _AutoEnclosedThreadsBag.__lck:
            if _AutoEnclosedThreadsBag.__bag is not None:
                if curPyThrd_ is None:
                    curPyThrd_ = threading.current_thread()
                res = curPyThrd_ in _AutoEnclosedThreadsBag.__bag
        return res

    @staticmethod
    def _AddPyThread(pythrd_ : _PyThread):
        if _AutoEnclosedThreadsBag.__lck is None:
            return

        with _AutoEnclosedThreadsBag.__lck:
            if _AutoEnclosedThreadsBag.__bag is None:
                _AutoEnclosedThreadsBag.__bag = []
            if pythrd_ not in _AutoEnclosedThreadsBag.__bag:
                _AutoEnclosedThreadsBag.__bag.append(pythrd_)

    @staticmethod
    def _RemovePyThread(pythrd_ : _PyThread):
        if _AutoEnclosedThreadsBag.__lck is None:
            return

        with _AutoEnclosedThreadsBag.__lck:
            if _AutoEnclosedThreadsBag.__bag is None:
                return

            if pythrd_ in _AutoEnclosedThreadsBag.__bag:
                _AutoEnclosedThreadsBag.__bag.remove(pythrd_)
                if len(_AutoEnclosedThreadsBag.__bag) == 0:
                    _AutoEnclosedThreadsBag.__bag = None

    @staticmethod
    def _DepInjection(dinjCmd_ : _EDepInjCmd):
        if _AutoEnclosedThreadsBag.__bag is not None:
            _AutoEnclosedThreadsBag.__bag.clear()
            _AutoEnclosedThreadsBag.__bag = None
        _AutoEnclosedThreadsBag.__lck = None if dinjCmd_.isDeInject else _PyRLock()

class _TaskUtil:
    __bGDXFT          = None
    __nextPUID        = None
    __nextUTaskID     = None
    __nextFwTaskID    = None
    __nextAEnclTaskID = None
    __MAIN_PYTHREAD   = None

    @staticmethod
    def IsNativeThreadIdSupported():
        if _TaskIDDefines._NATIVE_THREAD_ID_SUPPORT_EVAL == -1:
            _TaskIDDefines._NATIVE_THREAD_ID_SUPPORT_EVAL = 0
            if _SystemInfo._IsPythonVersionCompatible(3, 8):
                _TaskIDDefines._NATIVE_THREAD_ID_SUPPORT_EVAL = 1
        return _TaskIDDefines._NATIVE_THREAD_ID_SUPPORT_EVAL == 1

    @staticmethod
    def IsCurPyThread(hthrd_ : _PyThread):
        if not isinstance(hthrd_, _PyThread):
            return False
        return _TaskUtil.GetPyThreadUID(hthrd_) == _TaskUtil.GetPyThreadUID(_TaskUtil.GetCurPyThread())

    @staticmethod
    def IsStartupThread(hthrd_ : _PyThread):
        res, _uid = False, _TaskUtil.GetPyThreadUID(hthrd_)
        if _uid is None:
            pass
        elif _StartupThread._GetInstance() is None:
            pass
        else:
            res = _uid == _StartupThread._GetInstance().hostThreadUID
        return res

    @staticmethod
    def IsMainPyThread(hthrd_ : _PyThread):
        return type(hthrd_) == type(_TaskUtil.GetMainPyThread())

    @staticmethod
    def GetInvalidTaskID():
        return int(_TaskIDDefines._INVALID_TASK_ID)

    @staticmethod
    def IsValidFwTaskID(tskID_ : Union[IntEnum, int]):
        if not isinstance(tskID_, (IntEnum, int)):
            return False
        if isinstance(tskID_, IntEnum):
            tskID_ = tskID_.value
        return (tskID_ > _TaskIDDefines._FWTASK_ID_BASE) and (tskID_ < _TaskIDDefines._AENCL_TASK_ID_BASE)

    @staticmethod
    def IsValidUserTaskID(tskID_ : Union[IntEnum, int]):
        if not isinstance(tskID_, (IntEnum, int)):
            return False
        if isinstance(tskID_, IntEnum):
            tskID_ = tskID_.value
        return tskID_ > _TaskIDDefines._UTASK_ID_BASE

    @staticmethod
    def IsValidAliasName(aliasName_ : str) -> bool:
        res = isinstance(aliasName_, str) and len(aliasName_)
        if res:
            res = aliasName_.isprintable()
            if res:
                _tmp = [ _cc for _cc in list(string.whitespace) if aliasName_.find(_cc)>-1 ]
                res = False if len(_tmp) else True
        return res

    @staticmethod
    def GetNextTaskID(bUserTask_ : bool, bEnclSThrd_ : bool =False, bAEnclHThrd_ =False) -> CompoundTUID:
        _idx = None
        if bEnclSThrd_:
            res = _TaskUtil.GetStartupThread().dtaskUID
        elif bAEnclHThrd_:
            if _TaskUtil.__nextAEnclTaskID is None:
                _TaskUtil.__nextAEnclTaskID = _AtomicInteger(_TaskIDDefines._AENCL_TASK_ID_BASE)
            res = _TaskUtil.__nextAEnclTaskID.Increment()
        elif not bUserTask_:
            if _TaskUtil.__nextFwTaskID is None:
                _TaskUtil.__nextFwTaskID = _AtomicInteger(_TaskIDDefines._FWTASK_ID_BASE)
            res = _TaskUtil.__nextFwTaskID.Increment()
        else:
            if _TaskUtil.__nextUTaskID is None:
                _TaskUtil.__nextUTaskID = _AtomicInteger(_TaskIDDefines._UTASK_ID_BASE)
            res = _TaskUtil.__nextUTaskID.Increment()
            _idx = res - _TaskIDDefines._UTASK_ID_BASE
        return CompoundTUID(res, _idx)

    @staticmethod
    def GetNextProcessID() -> CompoundTUID:
        if _TaskUtil.__nextPUID is None:
            _TaskUtil.__nextPUID = _AtomicInteger(_TaskIDDefines._PUID_BASE)
        res  = _TaskUtil.__nextPUID.Increment()
        _idx = res - _TaskIDDefines._PUID_BASE
        return CompoundTUID(res, _idx)

    @staticmethod
    def GetStartupThread() -> _StartupThread:
        return _StartupThread._GetInstance()

    @staticmethod
    def GetMainPyThread():
        if _TaskUtil.__MAIN_PYTHREAD is None:
            _TaskUtil.__MAIN_PYTHREAD = threading.main_thread()
        return _TaskUtil.__MAIN_PYTHREAD

    @staticmethod
    def GetCurPyThread():
        return threading.current_thread()

    @staticmethod
    def GetPyThreadUID(hthrd_):
        return None if hthrd_ is None else id(hthrd_)

    @staticmethod
    def GetCurPyThreadUID():
        return _TaskUtil.GetPyThreadUID(_TaskUtil.GetCurPyThread())

    @staticmethod
    def GetCurPyThreadRuntimeID():
        if _TaskUtil.IsNativeThreadIdSupported():
            return threading.get_native_id()
        else:
            return threading.get_ident()

    @staticmethod
    def JoinPyThread(thrd_ : _PyThread, timeoutSEC_ : float =None):
        thrd_.join(timeout=timeoutSEC_)

    @staticmethod
    def Sleep(timeout_ : Union[float, _Timeout]):
        _tt = None
        if not isinstance(timeout_, _Timeout):
            if not isinstance(timeout_, float):
                vlogif._LogOEC(False, _EFwErrorCode.VUE_00029)
                return

            _tt = _Timeout.CreateTimeoutSec(timeout_)
            timeout_ = _tt
        if _Timeout.IsFiniteTimeout(timeout_, bThrowx_=True):
            _PySleep(timeout_.toSec)
        if _tt is not None:
            _tt.CleanUp()

    @staticmethod
    def SleepMS(timeSpanMS_ : Union[int, _Timeout]):
        _tt = _Timeout.CreateTimeoutMS(timeSpanMS_)
        if not _Timeout.IsFiniteTimeout(_tt, bThrowx_=True):
            return

        _tts = _tt.toSec
        _tt.CleanUp()
        _PySleep(_tts)

    @staticmethod
    def _StartHThread(hthrd_ : _PyThread) -> bool:
        res = isinstance(hthrd_, _PyThread) and not hthrd_.is_alive()
        if res:
            hthrd_.start()
            if _TaskUtil.__bGDXFT:
                _TaskUtil.SleepMS(5)
        return res

    @staticmethod
    def _DepInjection(dinjCmd_ : _EDepInjCmd):
        if _TaskUtil.__bGDXFT is None:
            _TaskUtil.__bGDXFT = _SystemInfo._IsGilDisabled()

        if dinjCmd_.isDeInject:
            if _TaskUtil.__nextUTaskID is not None:
                _TaskUtil.__nextUTaskID.CleanUp()
                _TaskUtil.__nextUTaskID = None
            if _TaskUtil.__nextAEnclTaskID is not None:
                _TaskUtil.__nextAEnclTaskID.CleanUp()
                _TaskUtil.__nextAEnclTaskID = None
            if _TaskUtil.__nextFwTaskID is not None:
                _TaskUtil.__nextFwTaskID.CleanUp()
                _TaskUtil.__nextFwTaskID = None
            if _TaskUtil.__nextPUID is not None:
                _TaskUtil.__nextPUID.CleanUp()
                _TaskUtil.__nextPUID = None
        else:
            if _TaskUtil.__nextUTaskID is None:
                _TaskUtil.__nextUTaskID = _AtomicInteger(_TaskIDDefines._UTASK_ID_BASE)
            if _TaskUtil.__nextAEnclTaskID is None:
                _TaskUtil.__nextAEnclTaskID = _AtomicInteger(_TaskIDDefines._AENCL_TASK_ID_BASE)
            if _TaskUtil.__nextFwTaskID is None:
                _TaskUtil.__nextFwTaskID = _AtomicInteger(_TaskIDDefines._FWTASK_ID_BASE)
            if _TaskUtil.__nextPUID is None:
                _TaskUtil.__nextPUID = _AtomicInteger(_TaskIDDefines._PUID_BASE)
