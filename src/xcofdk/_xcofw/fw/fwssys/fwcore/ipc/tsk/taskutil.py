# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : taskutil.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from xcofdk._xcofw.fw.fwssys.fwcore.logging import vlogif

import threading

from enum      import IntEnum
from enum      import IntFlag
from enum      import unique
from threading import RLock  as _PyRLock
from threading import Thread as _PyThread
from time      import sleep  as _PySleep
from typing    import Union  as _PyUnion

from xcofdk._xcofw.fw.fwssys.fwcore.base.gtimeout     import _Timeout
from xcofdk._xcofw.fw.fwssys.fwcore.base.util         import _Util
from xcofdk._xcofw.fw.fwssys.fwcore.swpfm.sysinfo     import _SystemInfo
from xcofdk._xcofw.fw.fwssys.fwcore.types.atomicint   import _AtomicInteger
from xcofdk._xcofw.fw.fwssys.fwcore.types.ebitmask     import _EBitMask
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes import _FwIntEnum
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes import _Limits


@unique
class _ETaskType(_FwIntEnum):
    eFwThread        =111
    eFwMainThread    =112
    eXTaskThread     =121
    eMainXTaskThread =122
    eFwTask          =211
    eFwMainTask      =212
    eXTaskTask       =221
    eMainXTaskTask   =222

    @property
    def isFwThread(self):
        return self.value <= _ETaskType.eMainXTaskThread.value

    @property
    def isFwTask(self):
        return self.value > _ETaskType.eMainXTaskThread.value

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
        return self.isFwThread and self.value > _ETaskType.eFwMainThread.value

    @property
    def isMainXTaskThread(self):
        return self == _ETaskType.eMainXTaskThread

    @property
    def isXTaskTask(self):
        return self.isFwTask and self.value > _ETaskType.eFwMainTask.value

    @property
    def isMainXTaskTask(self):
        return self == _ETaskType.eMainXTaskTask


@unique
class _ETaskResourceFlag(IntFlag):
    eNone  = _EBitMask.eNone.value
    eTimer = (1 << 0)

    @staticmethod
    def IsResourceFlagSet(resMask_, resFlags_):
        return _EBitMask.IsEnumBitFlagSet(resMask_, resFlags_)

    @staticmethod
    def AddResourceFlag(resMask_, resFlags_):
        return _EBitMask.AddEnumBitFlag(resMask_, resFlags_)

    @staticmethod
    def GetRessourcesMask(enableTimer_ =False) -> IntFlag:
        res = _ETaskResourceFlag.eNone
        if enableTimer_:
            res = _ETaskResourceFlag.AddResourceFlag(res, _ETaskResourceFlag.eTimer)
        return res


@unique
class _ETaskRightFlag(IntFlag):

    eNone                 = 0x0000
    eFwTask               = 0x8000
    eUserTask             = 0x4000
    eXTaskTask          = (1 << 0)
    eUTTask               = (1 << 1)
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
            vlogif._LogOEC(True, -1446)
            return None
        return _EBitMask.AddEnumBitFlag(trMask_, trFlags_)

    @staticmethod
    def AddXTaskTaskRight(trMask_ : IntFlag):
        if not _ETaskRightFlag.IsValidTaskRightMask(trMask_):
            vlogif._LogOEC(True, -1447)
            return None
        return _EBitMask.AddEnumBitFlag(trMask_, _ETaskRightFlag.eXTaskTask)

    @staticmethod
    def AddUnitTestTaskRight(trMask_ : IntFlag):
        if not _ETaskRightFlag.IsValidTaskRightMask(trMask_):
            vlogif._LogOEC(True, -1448)
            return None
        return _EBitMask.AddEnumBitFlag(trMask_, _ETaskRightFlag.eUTTask)

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
    def hasUnitTestTaskRight(self):
        return _ETaskRightFlag.IsTaskRightFlagSet(self, _ETaskRightFlag.eUTTask)

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
class _ETaskExecutionPhaseID(_FwIntEnum):
    eNone = 0
    eDummyRunningAutoEnclosedThread         = 11
    eRunningNonDrivingExecutableSyncThread  = 12
    eRunningNonDrivingExecutableASyncThread = 13
    eFwHandling  = 21
    eRblSetup        = 31
    eRblTeardown     = 32
    eRblRun          = 33
    eRblProcIntMsg   = 34
    eRblProcIntQueue = 35
    eRblProcExtMsg   = 36
    eRblProcExtQueue = 37
    eRblMisc         = 38
    eXTaskSetup      = 41
    eXTaskTeardown   = 42
    eXTaskRun        = 43
    eXTaskProcIntMsg = 44
    eXTaskProcExtMsg = 45

    @property
    def isNone(self):
        return self == _ETaskExecutionPhaseID.eNone

    @property
    def isFwHandling(self):
        return self == _ETaskExecutionPhaseID.eFwHandling

    @property
    def isRunnableExecution(self):
        return (self.value >= _ETaskExecutionPhaseID.eRblSetup.value) and (self.value <= _ETaskExecutionPhaseID.eRblMisc.value)

    @property
    def isXTaskExecution(self):
        return self.value >= _ETaskExecutionPhaseID.eXTaskSetup.value

    @property
    def isNonDrivingExecutableThreadExecution(self):
        return (self.value >= _ETaskExecutionPhaseID.eDummyRunningAutoEnclosedThread.value) and (self.value <= _ETaskExecutionPhaseID.eRunningNonDrivingExecutableASyncThread.value)


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
    eNone = 0
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
    def isNone(self):
        return self == _EFwApiBookmarkID.eNone

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
    _TASK_ID_RANGE_MAXSIZE         = 1000000
    _ENCL_TASK_ID_BASE_FACTOR      = 1
    _INVALID_TASK_ID               = _Limits.MIN_INT
    _NATIVE_THREAD_ID_SUPPORT_EVAL = -1
    _XTASK_ID_BASE                 = (_TASK_ID_RANGE_SIZE * _TASK_ID_BASE_FACTOR)      + (_STARTUP_THREAD_ID-1)
    _FWTASK_ID_BASE                = _STARTUP_THREAD_ID
    _AENCL_TASK_ID_BASE            = (_TASK_ID_RANGE_SIZE * _ENCL_TASK_ID_BASE_FACTOR) + (_STARTUP_THREAD_ID-1)

    @staticmethod
    def GetStartupThreadID():
        return _TaskIDDefines._STARTUP_THREAD_ID



class _StartupThread:
    __singleton    = None
    __updateFrozen = False

    __slots__   = [ '__pythrd' , '__tid' ]

    def __str__(self):
        return self.ToString()

    def __init__(self, taskID_ : int =None):
        self.__tid    = None
        self.__pythrd = None
        if _StartupThread.__singleton is not None:
            vlogif._LogOEC(True, -1449)
        else:
            if taskID_ is None:
                taskID_ = _TaskIDDefines.GetStartupThreadID()

            self.__tid    = taskID_
            self.__pythrd = threading.current_thread()

            _StartupThread.__singleton = self

    @staticmethod
    def GetInstance():
        if _StartupThread.__singleton is None:
            _StartupThread(taskID_=None)
        return _StartupThread.__singleton

    @property
    def isMainPyThread(self):
        return (self.__pythrd is not None) and (type(self.__pythrd) == type(threading.main_thread()))

    @property
    def pyThreadName(self) -> str:
        return None if self.__pythrd is None else self.__pythrd.name

    @property
    def taskName(self):
        return self.pyThreadName

    @property
    def taskID(self):
        return self.__tid

    @property
    def uniqueID(self):
        return None if self.__pythrd is None else id(self.__pythrd)

    def ToString(self, *args_, **kwargs_) -> str:
        if self.__pythrd is None:
            res = None
        else:
            res = '{}: (tasnName, taskID, uniqueID)=({}, {}, {})'.format(type(self).__name__, self.taskName, self.taskID, self.uniqueID)
        return res

    def CleanUp(self):
        self.__tid    = None
        self.__pythrd = None
        if _StartupThread.__singleton is not None:
            if id(_StartupThread.__singleton) == id(self):
                _StartupThread.__singleton = None

    @property
    def _pyThread(self):
        return self.__pythrd

    def _Update(self, taskID_ : int =None, freezeUpdate_ =True):
        if self.__pythrd is None:
            vlogif._LogOEC(True, -1450)
        elif _StartupThread.__updateFrozen and (freezeUpdate_ is not None):
            vlogif._LogOEC(True, -1451)
        else:
            _StartupThread.__updateFrozen = False if freezeUpdate_ is None else freezeUpdate_

            self.__pythrd = threading.current_thread()
            if taskID_ is not None:
                self.__tid = taskID_


class _AutoEnclosedThreadsBag:
    __theBag    = None
    __theApiLck = None

    @staticmethod
    def IsProcessingCurPyThread(curPyThrd_ =None):
        res = False
        if _AutoEnclosedThreadsBag.__theApiLck is None:
            pass
        else:
            with _AutoEnclosedThreadsBag.__theApiLck:
                if _AutoEnclosedThreadsBag.__theBag is not None:
                    if curPyThrd_ is None:
                        curPyThrd_ = threading.current_thread()
                    res = curPyThrd_ in _AutoEnclosedThreadsBag.__theBag
        return res

    @staticmethod
    def _AddPyThread(pythrd_ : _PyThread):
        if _AutoEnclosedThreadsBag.__theApiLck is None:
            pass
        else:
            with _AutoEnclosedThreadsBag.__theApiLck:
                if _AutoEnclosedThreadsBag.__theBag is None:
                    _AutoEnclosedThreadsBag.__theBag = []
                if pythrd_ not in _AutoEnclosedThreadsBag.__theBag:
                    _AutoEnclosedThreadsBag.__theBag.append(pythrd_)

    @staticmethod
    def _RemovePyThread(pythrd_ : _PyThread):
        if _AutoEnclosedThreadsBag.__theApiLck is None:
            pass
        else:
            with _AutoEnclosedThreadsBag.__theApiLck:
                if _AutoEnclosedThreadsBag.__theBag is None:
                    pass
                elif pythrd_ in _AutoEnclosedThreadsBag.__theBag:
                    _AutoEnclosedThreadsBag.__theBag.remove(pythrd_)
                    if len(_AutoEnclosedThreadsBag.__theBag) == 0:
                        _AutoEnclosedThreadsBag.__theBag = None

    @staticmethod
    def _SetUp(set_):
        if _AutoEnclosedThreadsBag.__theBag is not None:
            _AutoEnclosedThreadsBag.__theBag.clear()
            _AutoEnclosedThreadsBag.__theBag = None
        _AutoEnclosedThreadsBag.__theApiLck = None if not set_ else _PyRLock()


class _TaskUtil:

    __nextXTaskID     = None
    __nextFwTaskID    = None
    __nextAEnclTaskID = None
    __MAIN_PYTHREAD   = None

    @staticmethod
    def IsNativeThreadIdSupported():
        if _TaskIDDefines._NATIVE_THREAD_ID_SUPPORT_EVAL == -1:
            _verstr = _SystemInfo._GetPythonVer()

            _TaskIDDefines._NATIVE_THREAD_ID_SUPPORT_EVAL = 0
            if _SystemInfo._IsPythonVersionCompatible(3, 8):
                _TaskIDDefines._NATIVE_THREAD_ID_SUPPORT_EVAL = 1
        return _TaskIDDefines._NATIVE_THREAD_ID_SUPPORT_EVAL == 1

    @staticmethod
    def IsCurPyThread(pythread_ : _PyThread):
        if not isinstance(pythread_, _PyThread):
            return False
        return _TaskUtil.GetPyThreadUniqueID(pythread_) == _TaskUtil.GetPyThreadUniqueID(_TaskUtil.GetCurPyThread())

    @staticmethod
    def IsStartupThread(pythread_ : _PyThread):
        res, uid = False, _TaskUtil.GetPyThreadUniqueID(pythread_)
        if uid is None:
            pass
        elif _StartupThread.GetInstance() is None:
            pass
        else:
            res = uid == _StartupThread.GetInstance().uniqueID
        return res

    @staticmethod
    def IsMainPyThread(pythread_ : _PyThread):
        return type(pythread_) == type(_TaskUtil.GetMainPyThread())

    @staticmethod
    def GetInvalidTaskID():
        return int(_TaskIDDefines._INVALID_TASK_ID)

    @staticmethod
    def IsValidFwTaskID(tskID_ : _PyUnion[IntEnum, int]):
        if not isinstance(tskID_, (IntEnum, int)):
            return False
        if isinstance(tskID_, IntEnum):
            tskID_ = tskID_.value
        return (tskID_ > _TaskIDDefines._FWTASK_ID_BASE) and (tskID_ < _TaskIDDefines._AENCL_TASK_ID_BASE)

    @staticmethod
    def IsValidUserTaskID(tskID_ : _PyUnion[IntEnum, int]):
        if not isinstance(tskID_, (IntEnum, int)):
            return False
        if isinstance(tskID_, IntEnum):
            tskID_ = tskID_.value
        return tskID_ > _TaskIDDefines._XTASK_ID_BASE

    @staticmethod
    def GetNextTaskID(bUserTask_ : bool, bEnclosingStartupThrd_ : bool, bAutoEnclosedPyThrd_ =False):
        if bEnclosingStartupThrd_:
            ret = _TaskUtil.GetStartupThread().taskID
        elif bAutoEnclosedPyThrd_:
            if _TaskUtil.__nextAEnclTaskID is None:
                _TaskUtil.__nextAEnclTaskID = _AtomicInteger(_TaskIDDefines._AENCL_TASK_ID_BASE)
            ret = _TaskUtil.__nextAEnclTaskID.Increment()
        elif not bUserTask_:
            if _TaskUtil.__nextFwTaskID is None:
                _TaskUtil.__nextFwTaskID = _AtomicInteger(_TaskIDDefines._FWTASK_ID_BASE)
            ret = _TaskUtil.__nextFwTaskID.Increment()
        else:
            if _TaskUtil.__nextXTaskID is None:
                _TaskUtil.__nextXTaskID = _AtomicInteger(_TaskIDDefines._XTASK_ID_BASE)
            ret = _TaskUtil.__nextXTaskID.Increment()
        return ret

    @staticmethod
    def GetStartupThread() -> _StartupThread:
        return _StartupThread.GetInstance()

    @staticmethod
    def GetMainPyThread():
        if _TaskUtil.__MAIN_PYTHREAD is None:
            _TaskUtil.__MAIN_PYTHREAD = threading.main_thread()
        return _TaskUtil.__MAIN_PYTHREAD

    @staticmethod
    def GetCurPyThread():
        return threading.current_thread()

    @staticmethod
    def GetPyThreadUniqueID(pythread_):
        return None if pythread_ is None else id(pythread_)

    @staticmethod
    def GetCurPyThreadRuntimeID():

        if _TaskUtil.IsNativeThreadIdSupported():
            return threading.get_native_id()
        else:
            return threading.get_ident()

    @staticmethod
    def Sleep(timeout_ : [float, _Timeout]):
        _tt = None
        if not isinstance(timeout_, _Timeout):
            if not isinstance(timeout_, float):
                vlogif._LogOEC(False, -3022)
                return

            _tt = _Timeout.CreateTimeoutSec(timeout_)
            timeout_ = _tt
        if _Timeout.IsFiniteTimeout(timeout_, bThrowx_=True):
            _PySleep(timeout_.toSec)
        if _tt is not None:
            _tt.CleanUp()

    @staticmethod
    def SleepMS(timeSpanMS_ : int):
        _tt = _Timeout.CreateTimeoutMS(timeSpanMS_)
        if not _Timeout.IsFiniteTimeout(_tt, bThrowx_=True):
            pass
        else:
            _tts = _tt.toSec
            _tt.CleanUp()
            _PySleep(_tts)


    @staticmethod
    def _SetUp(set_ =False):
        if not set_:
            if _TaskUtil.__nextXTaskID is not None:
                _TaskUtil.__nextXTaskID.CleanUp()
                _TaskUtil.__nextXTaskID = None
            if _TaskUtil.__nextAEnclTaskID is not None:
                _TaskUtil.__nextAEnclTaskID.CleanUp()
                _TaskUtil.__nextAEnclTaskID = None
            if _TaskUtil.__nextFwTaskID is not None:
                _TaskUtil.__nextFwTaskID.CleanUp()
                _TaskUtil.__nextFwTaskID = None
        else:
            if _TaskUtil.__nextXTaskID is None:
                _TaskUtil.__nextXTaskID = _AtomicInteger(_TaskIDDefines._XTASK_ID_BASE)
            if _TaskUtil.__nextAEnclTaskID is None:
                _TaskUtil.__nextAEnclTaskID = _AtomicInteger(_TaskIDDefines._AENCL_TASK_ID_BASE)
            if _TaskUtil.__nextFwTaskID is None:
                _TaskUtil.__nextFwTaskID = _AtomicInteger(_TaskIDDefines._FWTASK_ID_BASE)
