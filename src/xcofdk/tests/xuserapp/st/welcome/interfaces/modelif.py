# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : modelif.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from enum   import auto
from enum   import IntEnum
from enum   import unique
from typing import List

from xuserapp.util.userAppUtil  import UserAppUtil
from xuserapp.util.userAppRLock import UserAppRLock as RLock


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
@unique
class EModelItemID(IntEnum):
    # info
    eXcofdkVersion = 0
    ePythonVersion = auto()
    eHostPlatfrom  = auto()
    eNumCpuCores   = auto()
    #
    # MT
    eMainTaskInfo       = auto()
    ePostingPaused      = auto()
    eServiceTaskInfo    = auto()
    eFibonacciReply     = auto()
    eServiceTaskGilSpec = auto()
    #
    # MP
    eMPServiceProcess       = auto()
    eMPServiceProcessResult = auto()
#END class EModelItemID


class TaskInfo:
    __slots__ = [ '__tname'      , '__tuid'
                , '__stime'      , '__dtime'
                , '__cntSnt'     , '__cntRcv'
                , '__bMainTask'  , '__bAsync'
                , '__srvTaskNo'  , '__cntErrSnt'
                , '__cntSrvTasksTotalRcv'
                , '__cntSrvTasksTotalSnt'
                , '__cntSrvTasksTotalErrSnt'
                , '__cntOutOfOrderRcv'
                , '__cntSrvTasksTotalOutOfOrderRcv'
                ]

    def __init__(self, taskName_ : str, taskUID_ : int, startTime_ : str, bAsync_ =True, bMainTask_ =False, serviceTaskNo_ : int =None):
        self.__bAsync    = bAsync_
        self.__bMainTask = bMainTask_

        self.__tuid      = taskUID_
        self.__tname     = taskName_
        self.__stime     = startTime_
        self.__dtime     = ''
        self.__cntSnt    = 0
        self.__cntRcv    = 0
        self.__cntErrSnt = 0
        self.__srvTaskNo = serviceTaskNo_

        self.__cntSrvTasksTotalRcv    = 0
        self.__cntSrvTasksTotalSnt    = 0
        self.__cntSrvTasksTotalErrSnt = 0

        self.__cntOutOfOrderRcv              = 0
        self.__cntSrvTasksTotalOutOfOrderRcv = 0

    @property
    def isMainTask(self) -> bool:
        return self.__bMainTask

    @property
    def isAsyncTask(self) -> bool:
        return self.__bAsync

    @property
    def serviceTaskNo(self):
        return self.__srvTaskNo

    @property
    def taskName(self) -> str:
        return self.__tname

    @property
    def taskUID(self) -> int:
        return self.__tuid

    @property
    def taskStartTime(self) -> str:
        return self.__stime

    @property
    def taskDurationTime(self) -> str:
        return self.__dtime

    @property
    def messageCountSent(self) -> int:
        return self.__cntSnt

    @property
    def messageCountReceived(self) -> int:
        return self.__cntRcv

    @property
    def failuresCountSent(self) -> int:
        return self.__cntErrSnt

    @property
    def outOfOrderReceivedCount(self):
        return self.__cntOutOfOrderRcv

    @property
    def serviceTasksTotalCountSent(self) -> int:
        return self.__cntSrvTasksTotalSnt

    @property
    def serviceTasksTotalCountReceived(self) -> int:
        return self.__cntSrvTasksTotalRcv

    @property
    def serviceTasksTotalFailuresCountSent(self) -> int:
        return self.__cntSrvTasksTotalErrSnt

    @property
    def serviceTasksOutOfOrderReceivedTotalCount(self) -> int:
        return self.__cntSrvTasksTotalOutOfOrderRcv

    def UpdateTaskInfo( self
                      , durationTime_                             : str =None
                      , taskName_                                 : str =None
                      , taskUID_                                  : int =None
                      , serviceTaskNo_                            : int =None
                      , msgCountSent_                             : int =None
                      , msgCountReceived_                         : int =None
                      , sendFailuresCount_                        : int =None
                      , outOfOrderCnt_                            : int =None
                      , serviceTasksTotalSentCount_               : int =None
                      , serviceTasksTotalReceivedCount_           : int =None
                      , serviceTasksTotalSendFailuresCount_       : int =None
                      , serviceTasksOutOfOrderReceivedTotalCount_ : int =None):
        if durationTime_ is not None:
            self.__dtime = durationTime_
        if taskName_ is not None:
            self.__tname = taskName_
        if taskUID_ is not None:
            self.__tuid = taskUID_
        if serviceTaskNo_ is not None:
            self.__srvTaskNo = serviceTaskNo_
        if msgCountSent_ is not None:
            self.__cntSnt = msgCountSent_
        if msgCountReceived_ is not None:
            self.__cntRcv = msgCountReceived_
        if sendFailuresCount_ is not None:
            self.__cntErrSnt = sendFailuresCount_
        if outOfOrderCnt_ is not None:
            self.__cntOutOfOrderRcv = outOfOrderCnt_
        if serviceTasksTotalSentCount_ is not None:
            self.__cntSrvTasksTotalSnt = serviceTasksTotalSentCount_
        if serviceTasksTotalReceivedCount_ is not None:
            self.__cntSrvTasksTotalRcv = serviceTasksTotalReceivedCount_
        if serviceTasksTotalSendFailuresCount_ is not None:
            self.__cntSrvTasksTotalErrSnt = serviceTasksTotalSendFailuresCount_
        if serviceTasksOutOfOrderReceivedTotalCount_ is not None:
            self.__cntSrvTasksTotalOutOfOrderRcv = serviceTasksOutOfOrderReceivedTotalCount_
#END class TaskInfo


class ServiceTaskGilSpec:
    __slots__ = [ '__bDeficientFreq' , '__bGilPaused'
                , '__fiboInput'      , '__fiboCpuTimeMS'
                , '__runPhaseFreqMS' , '__deficientRunPhaseFreqMS'
                ]

    __DEFAULT_FIBO_INPUT                  = 22
    __DEFAULT_FIBO_CPU_TIME_MS            = 7.523
    __DEFAULT_RUN_PHASE_FREQ_MS           = 100
    __DEFAULT_DEFICIENT_RUN_PHASE_FREQ_MS = 80

    def __init__(self, fiboInput_ : int =None, fiboCpuTimeMS_ : float =None, runPhaseFreqMS_ : int =None, deficientRunPhaseFreqMS_ =None):
        self.__bGilPaused     = False
        self.__bDeficientFreq = False

        # fibonacci input
        if not (isinstance(fiboInput_, int) and (fiboInput_ > 0)):
            self.__fiboInput = ServiceTaskGilSpec.__DEFAULT_FIBO_INPUT
        else:
            self.__fiboInput = fiboInput_

        # fibonacci cpu consumption time
        if not (isinstance(fiboCpuTimeMS_, float) and (fiboCpuTimeMS_ > 0.0)):
            self.__fiboCpuTimeMS = ServiceTaskGilSpec.__DEFAULT_FIBO_CPU_TIME_MS
        else:
            self.__fiboCpuTimeMS = fiboCpuTimeMS_

        # run-phase frequency
        if not (isinstance(runPhaseFreqMS_, int) and (runPhaseFreqMS_ > 0)):
            self.__runPhaseFreqMS = ServiceTaskGilSpec.__DEFAULT_RUN_PHASE_FREQ_MS
        else:
            self.__runPhaseFreqMS = runPhaseFreqMS_

        # deficient run-phase frequency
        if not (isinstance(deficientRunPhaseFreqMS_, int) and (deficientRunPhaseFreqMS_ > 0)):
            self.__deficientRunPhaseFreqMS = ServiceTaskGilSpec.__DEFAULT_DEFICIENT_RUN_PHASE_FREQ_MS
        else:
            self.__deficientRunPhaseFreqMS = deficientRunPhaseFreqMS_

    @property
    def isGilPaused(self) -> bool:
        return self.__bGilPaused

    @isGilPaused.setter
    def isGilPaused(self, bGilPaused_ : bool):
        self.__bGilPaused = bGilPaused_

    @property
    def isDeficientFrequencyForced(self) -> bool:
        return self.__bDeficientFreq

    @isDeficientFrequencyForced.setter
    def isDeficientFrequencyForced(self, bDeficient_ : bool):
        self.__bDeficientFreq = bDeficient_

    @property
    def fibonacciInput(self):
        return self.__fiboInput

    @property
    def fibonacciCpuTimeMS(self):
        return self.__fiboCpuTimeMS

    @property
    def runPhaseFrequencyMS(self):
        return self.__runPhaseFreqMS

    @property
    def deficientRunPhaseFrequencyMS(self):
        return self.__deficientRunPhaseFreqMS
#END ServiceTaskGilSpec


class MPServiceProcess:
    __slots__ = [ '__ctrMpRun'   , '__bPaused' , '__dtime'
                , '__procDTotal' , '__mpSM' , '__numErr'
                ]

    def __init__(self):
        self.__mpSM       = ''
        self.__dtime      = ''
        self.__numErr     = 0
        self.__bPaused    = False
        self.__ctrMpRun   = 0
        self.__procDTotal = None

    @property
    def isPaused(self):
        return self.__bPaused

    @isPaused.setter
    def isPaused(self, bPaused_ : bool):
        self.__bPaused = bPaused_

    @property
    def durationTime(self) -> str:
        return self.__dtime

    @durationTime.setter
    def durationTime(self, dtime_ : str):
        self.__dtime = dtime_

    @property
    def mpRunCount(self):
        return self.__ctrMpRun

    @mpRunCount.setter
    def mpRunCount(self, mpRunCount_ : int):
        self.__ctrMpRun = mpRunCount_

    @property
    def mpNumErrors(self):
        return self.__numErr

    @mpNumErrors.setter
    def mpNumErrors(self, numErrors_ : int):
        self.__numErr = numErrors_

    @property
    def mpStartMethod(self) -> str:
        return self.__mpSM

    @mpStartMethod.setter
    def mpStartMethod(self, mpStartMethod_ : str):
        self.__mpSM = mpStartMethod_

    @property
    def processElapsedTimeTotalSEC(self):
        return '-' if self.__procDTotal is None else self.__procDTotal

    @processElapsedTimeTotalSEC.setter
    def processElapsedTimeTotalSEC(self, totalElapsedTime_ : str):
        self.__procDTotal = totalElapsedTime_
#END class MPServiceProcess


class MPServiceProcessResult:
    __slots__ = [ '__fiboInput' , '__fiboResult'   , '__procName'
                , '__startTime' , '__procDuration' , '__fiboCpuTime'
                , '__bFrozen'
                ]

    __DEFAULT_FIBO_INPUT        = 36
    __DEFAULT_FIBO_CPU_TIME_SEC = 2.9

    def __init__(self, fiboInput_ : int =None, fiboCpuTimeSEC_ : float =None):
        # fibonacci input
        if not (isinstance(fiboInput_, int) and (fiboInput_ > 0)):
            self.__fiboInput = MPServiceProcessResult.__DEFAULT_FIBO_INPUT
        else:
            self.__fiboInput = fiboInput_

        # fibonacci cpu consumption time
        if not (isinstance(fiboCpuTimeSEC_, float) and (fiboCpuTimeSEC_ > 0.0)):
            self.__fiboCpuTime = MPServiceProcessResult.__DEFAULT_FIBO_CPU_TIME_SEC
        else:
            self.__fiboCpuTime = fiboCpuTimeSEC_

        self.__bFrozen      = False
        self.__procName     = None
        self.__startTime    = None
        self.__fiboResult   = None
        self.__procDuration = None

    @property
    def isFrozen(self):
        return self.__bFrozen

    @property
    def processName(self):
        return '-' if self.__procName is None else self.__procName

    @property
    def processElapsedTimeSEC(self):
        return '-' if self.__procDuration is None else self.__procDuration

    @property
    def fibonacciInput(self):
        return self.__fiboInput

    @property
    def fibonacciResult(self):
        return '-' if self.__fiboResult is None else self.__fiboResult

    @property
    def fibonacciCpuTimeSEC(self):
        return self.__fiboCpuTime

    def UpdateResult(self, procName_ : str =None, bReset_ =False, fiboResult_ : int =None):
        if self.__bFrozen and not bReset_:
            return

        if bReset_:
            self.__bFrozen      = False
            self.__procName     = None
            self.__startTime    = None
            self.__fiboResult   = None
            self.__procDuration = None
            return

        if procName_ is not None:
            if self.__procName is None:
                self.__procName  = procName_
                self.__startTime = UserAppUtil.GetCurrentTime()
            return

        if fiboResult_ is not None:
            self.__bFrozen = True
            self.__fiboResult   = fiboResult_
            self.__procDuration = UserAppUtil.DeltaTime2Str(self.__startTime, bLeftStripUnsetFields_=True)
            self.__startTime    = None
            return

        if self.__startTime is not None:
            self.__procDuration = UserAppUtil.DeltaTime2Str(self.__startTime, bLeftStripUnsetFields_=True)
#END MPServiceProcessResult


class FibonacciReply:
    __slots__ = [ '__sender' ,  '__fiboInput' , '__fiboResult' , '__timeMS' ]
    def __init__(self, sender_ : int, fiboInput_ : int, fiboResult : int, calcTimeMS_ : str =None):
        self.__timeMS     = calcTimeMS_
        self.__sender     = sender_
        self.__fiboInput  = fiboInput_
        self.__fiboResult = fiboResult

    @property
    def sender(self):
        return self.__sender

    @property
    def fibonacciInput(self):
        return self.__fiboInput

    @property
    def fibonacciResult(self):
        return self.__fiboResult

    @property
    def calculationTimeMS(self) -> str:
        return self.__timeMS

    @calculationTimeMS.setter
    def calculationTimeMS(self, timeMS_ : str):
        self.__timeMS = timeMS_
#END class FibonacciReply


class UserAppModelIF:

    __slots__ = [ '__lck' ]

    def __init__(self, bThreadSafe_ =False):
        #[NOTE]
        #  Thread safety of model needed only if accessed by multiple tasks.
        #

        self.__lck = RLock(bThreadSafe_=bThreadSafe_)

    @property
    def isPostingPaused(self) -> str:
        return self.__GetItem(EModelItemID.ePostingPaused)

    @property
    def xcofdkVersion(self) -> str:
        return self.__GetItem(EModelItemID.eXcofdkVersion)

    @property
    def pythonVersion(self) -> str:
        return self.__GetItem(EModelItemID.ePythonVersion)

    @property
    def hostPlatform(self) -> str:
        return self.__GetItem(EModelItemID.eHostPlatfrom)

    @property
    def numCpuCores(self) -> str:
        return self.__GetItem(EModelItemID.eNumCpuCores)

    @property
    def mainTaskInfo(self) -> TaskInfo:
        return self.__GetItem(EModelItemID.eMainTaskInfo)

    @property
    def serviceTaskInfo(self) -> TaskInfo:
        return self.__GetItem(EModelItemID.eServiceTaskInfo)

    @property
    def serviceTaskGilSpec(self) -> ServiceTaskGilSpec:
        return self.__GetItem(EModelItemID.eServiceTaskGilSpec)

    @property
    def fibonacciReplyList(self) -> List[FibonacciReply]:
        return self.__GetItem(EModelItemID.eFibonacciReply)

    @property
    def serviceProcess(self) -> MPServiceProcess:
        return self.__GetItem(EModelItemID.eMPServiceProcess)

    @property
    def serviceProcessResultList(self) -> List[MPServiceProcessResult]:
        return self.__GetItem(EModelItemID.eMPServiceProcessResult)

    def Lock(self):
        return self.__lck.acquire()

    def Unlock(self):
        self.__lck.release()

    def SetItem(self, itemID_ : EModelItemID, itemValue_):
        itemsMap = self._GetItemsMap()
        if itemsMap is None:
            return

        with self.__lck:
            itemsMap[itemID_] = itemValue_

    def _GetItemsMap(self) -> dict:
        pass

    def __GetItem(self, itemID_ : EModelItemID):
        itemsMap = self._GetItemsMap()
        if itemsMap is None:
            return None

        with self.__lck:
            if itemID_ not in itemsMap:
                return None
            return itemsMap[itemID_]
#END class UserAppModelIF
