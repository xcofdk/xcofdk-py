# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : queue.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from collections import deque as _PyDeque
from enum        import IntFlag
from enum        import unique

from _fw.fwssys.fwcore.logging            import logif
from _fw.fwssys.fwcore.logging            import vlogif
from _fw.fwssys.fwcore.base.gtimeout      import _Timeout
from _fw.fwssys.fwcore.base.util          import _Util
from _fw.fwssys.fwcore.ipc.sync.semaphore import _BinarySemaphore
from _fw.fwssys.fwcore.ipc.sync.mutex     import _Mutex
from _fw.fwssys.fwcore.ipc.tsk.taskutil   import _TaskUtil
from _fw.fwssys.fwcore.types.aobject      import _AbsObject
from _fw.fwssys.fwcore.types.aobject      import _AbsSlotsObject
from _fw.fwssys.fwcore.types.commontypes  import _CommonDefines
from _fw.fwssys.fwcore.types.ebitmask     import _EBitMask

from _fw.fwssys.fwerrh.fwerrorcodes import _EFwErrorCode

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _FwQueue(_AbsSlotsObject):
    @unique
    class EQOption(IntFlag):
        eNone                 = _EBitMask.eNone.value
        eExceptionOnQueueSize = (1 << 0)
        eBlockOnQueueSize     = (1 << 1)

        @staticmethod
        def IsQOptionFlagSet(qoptMask_, qoptFlags_):
            return (qoptMask_ is not None) and _EBitMask.IsEnumBitFlagSet(qoptMask_, qoptFlags_)

        @staticmethod
        def AddQOptionFlag(qoptMask_, qoptFlags_):
            return _EBitMask.AddEnumBitFlag(qoptMask_, qoptFlags_)

        @staticmethod
        def RemoveQOptionFlag(qoptMask_, qoptFlags_):
            return _EBitMask.RemoveEnumBitFlag(qoptMask_, qoptFlags_)

    @unique
    class EQState(IntFlag):
        eIdle  = _EBitMask.eNone.value
        eEmpty = (1 << 0)
        eFull  = (1 << 1)
        eDtor  = (1 << 2)

        @staticmethod
        def IsIdle(qsMask_):
            return qsMask_ == _FwQueue.EQState.eIdle

        @staticmethod
        def IsBlockingState(qsMask_):
            return False if qsMask_ is None else qsMask_ == _FwQueue.EQState.eIdle

        @staticmethod
        def IsBlockingEmptyState(qsMask_):
            return False if qsMask_ is None else _FwQueue.EQState.IsQStateSet(qsMask_, _FwQueue.EQState.eEmpty)

        @staticmethod
        def IsBlockingFullState(qsMask_):
            return False if qsMask_ is None else  _FwQueue.EQState.IsQStateSet(qsMask_, _FwQueue.EQState.eFull)

        @staticmethod
        def IsBlockingDtorState(qsMask_):
            return False if qsMask_ is None else  _FwQueue.EQState.IsQStateSet(qsMask_, _FwQueue.EQState.eDtor)

        @staticmethod
        def IsDtorState(qsMask_):
            return False if qsMask_ is None else  _FwQueue.EQState.IsQStateSet(qsMask_, _FwQueue.EQState.eDtor)

        @staticmethod
        def IsQStateSet(qsMask_, qsFlags_):
            return _EBitMask.IsEnumBitFlagSet(qsMask_, qsFlags_)

        @staticmethod
        def AddQState(qsMask_, qsFlags_):
            return _EBitMask.AddEnumBitFlag(qsMask_, qsFlags_)

        @staticmethod
        def RemoveQState(qsMask_, qsFlags_):
            return _EBitMask.RemoveEnumBitFlag(qsMask_, qsFlags_)

    class __InvalidQueueEntry:
        def __init__(self):
            pass

    __slots__ = [ '__q' , '__ma' , '__md' , '__mp' , '__ms' , '__s' , '__m' , '__bF' ]

    __theInvalidQEntry                       = __InvalidQueueEntry()
    __BLOCKING_QUEUE_DEFAULT_WAIT_TIMEOUT_MS = 50

    def __init__(self, optFlags_ =None, maxSize_ =None, bFIFO_ =True):
        super().__init__()

        self.__m  = None
        self.__q  = None
        self.__s  = None
        self.__bF = None
        self.__ma = None
        self.__md = None
        self.__mp = None
        self.__ms = None

        _optMask = _FwQueue.EQOption.eNone
        if optFlags_ is not None:
            _optMask = _FwQueue.EQOption.AddQOptionFlag(_optMask, optFlags_)
            if _optMask is None:
                self.CleanUp()
                return

        if _optMask == _FwQueue.EQOption.eNone:
            if maxSize_ is None:
                maxSize_ = 0
        else:
            if maxSize_ is None:
                maxSize_ = _FwQueue.GetFiniteQueueMinSize()
            if _FwQueue.EQOption.IsQOptionFlagSet(_optMask, _FwQueue.EQOption.eBlockOnQueueSize):
                if _FwQueue.EQOption.IsQOptionFlagSet(_optMask, _FwQueue.EQOption.eExceptionOnQueueSize):
                    _optMask = _FwQueue.EQOption.RemoveQOptionFlag(_optMask, _FwQueue.EQOption.eExceptionOnQueueSize)

        if not _Util.IsInstance(maxSize_, int):
            self.CleanUp()
            return
        if not _Util.CheckMinRange(maxSize_, 0):
            self.CleanUp()
            return
        if maxSize_ == 1:
            logif._LogBadUseEC(_EFwErrorCode.FE_00454, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwQueue_TID_005))
            self.CleanUp()
            return
        if _optMask != _FwQueue.EQOption.eNone:
            if maxSize_ == 0:
                logif._LogBadUseEC(_EFwErrorCode.FE_00455, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwQueue_TID_006))
                self.CleanUp()
                return

        self.__bF = bFIFO_
        self.__q  = _PyDeque()
        self.__ma = _Mutex()
        self.__md = _Mutex()
        self.__ms = _FwQueue.EQState.eIdle
        self.__mp = _optMask
        self.__s  = None
        self.__m  = maxSize_

        if _FwQueue.EQOption.IsQOptionFlagSet(self.__mp, _FwQueue.EQOption.eBlockOnQueueSize):
            _FwQueue.EQState.AddQState(self.__ms, _FwQueue.EQState.eEmpty)
        self.__s = _BinarySemaphore()

    @staticmethod
    def GetFiniteQueueMinSize():
        return 2

    @staticmethod
    def GetFiniteQueueDefaultSize():
        return 200

    @staticmethod
    def CreateInstance(maxSize_ =None, bFIFO_ =True):
        res = _FwQueue(_FwQueue.EQOption.eNone, maxSize_, bFIFO_)
        if res.__q is None:
            res = None
        return res

    @staticmethod
    def CreateInstanceBlockingOnSize(maxSize_ =None, bFIFO_ =True):
        res = _FwQueue(_FwQueue.EQOption.eBlockOnQueueSize, maxSize_, bFIFO_)
        if res.__q is None:
            res = None
        return res

    @staticmethod
    def CreateInstanceExceptionOnSize(maxSize_ =None, bFIFO_ =True):
        res = _FwQueue(_FwQueue.EQOption.eExceptionOnQueueSize, maxSize_, bFIFO_)
        if res.__q is None:
            res = None
        return res

    @property
    def isFIFO(self):
        return self.__bF

    @property
    def isEmpty(self):
        return self.qsize == 0

    @property
    def isFull(self):
        return (self.__m != 0) and (self.qsize == self.__m)

    @property
    def isBlockingOnQueueSize(self) -> bool:
        return _FwQueue.EQOption.IsQOptionFlagSet(self.__mp, _FwQueue.EQOption.eBlockOnQueueSize)

    @property
    def isRaisingExceptionOnQueueSize(self) -> bool:
        return _FwQueue.EQOption.IsQOptionFlagSet(self.__mp, _FwQueue.EQOption.eExceptionOnQueueSize)

    @property
    def hasInfiniteSize(self):
        return (self.__m is not None) and self.__m == 0

    @property
    def hasFiniteSize(self):
        return (self.__m is not None) and self.__m != 0

    @property
    def capacity(self):
        return self.__m

    @property
    def qsize(self):
        with self.__md:
            return len(self.__q)

    def Push(self, elem_):
        return self.__Push(elem_, True)

    def PushWait(self, elem_, timeout_):
        if not _Timeout.IsFiniteTimeout(timeout_):
            return False
        return self.__Push(elem_, True, timeout_=timeout_)

    def PushNowait(self, elem_):
        return self.__Push(elem_, False)

    def Pop(self):
        return self.__Pop(True)

    def PopWait(self, timeout_):
        if not _Timeout.IsFiniteTimeout(timeout_):
            return None
        return self.__Pop(True, timeout_=timeout_)

    def PopNowait(self):
        return self.__Pop(False)

    def PopBlockingQueue(self, sleepTimeMS_ =None):
        if not self.isBlockingOnQueueSize:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00529)
            return None
        res = self.__Pop(False)
        if res is None:
            if (sleepTimeMS_ is None) or (sleepTimeMS_ <= 0):
                sleepTimeMS_ = _FwQueue.__BLOCKING_QUEUE_DEFAULT_WAIT_TIMEOUT_MS
            _TaskUtil.SleepMS(sleepTimeMS_)
        return res

    def _CleanUp(self):
        if self.__ms is None:
            return
        self.__PrepareCleanup()

        if self.__s is not None:
            self.__s.CleanUp()
        self.__q.clear()
        self.__ma.CleanUp()
        self.__md.CleanUp()

        self.__m  = None
        self.__q  = None
        self.__s  = None
        self.__bF = None
        self.__ma = None
        self.__md = None
        self.__mp = None
        self.__ms = None

    def _ToString(self):
        return _CommonDefines._STR_EMPTY

    def __Push(self, elem_, bBlock_ : bool, timeout_ =None):
        if bBlock_:
            if timeout_ is not None:
                if not _Timeout.IsFiniteTimeout(timeout_):
                    logif._LogErrorEC(_EFwErrorCode.UE_00132, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwQueue_TID_001).format(str(timeout_)))
                    return False

        with self.__md:
            if _FwQueue.EQState.IsBlockingState(self.__ms):
                if _FwQueue.EQState.IsBlockingDtorState(self.__ms):
                    if len(self.__q) > 0:
                        self.__q.pop()
                    return False

                if _FwQueue.EQState.IsBlockingEmptyState(self.__ms):
                    if self.isFIFO:
                        self.__q.append(elem_)
                    else:
                        self.__q.appendleft(elem_)

                    _FwQueue.EQState.RemoveQState(self.__ms, _FwQueue.EQState.eEmpty)
                    self.__s.Give()
                    return True

        if not bBlock_:
            _bAL = self.__ma.TakeNowait()
        elif timeout_ is not None:
            _bAL = self.__ma.TakeWait(timeout_)
        else:
            _bAL = self.__ma.Take()

        if not _bAL:
            return False

        self.__md.Take()
        self.__ma.Give()

        if _FwQueue.EQState.IsBlockingDtorState(self.__ms):
            self.__md.Give()
            return False

        if _FwQueue.EQState.IsBlockingFullState(self.__ms):
            self.__md.Give()

            self.__s.Take()
            if _FwQueue.EQState.IsBlockingDtorState(self.__ms):
                return False

            self.__md.Take()
            if _FwQueue.EQState.IsBlockingDtorState(self.__ms):
                self.__md.Give()
                return False

            if self.isFIFO:
                self.__q.append(elem_)
            else:
                self.__q.appendleft(elem_)

            if self.isFull:
                _FwQueue.EQState.AddQState(self.__ms, _FwQueue.EQState.eFull)

            self.__md.Give()
            return True

        if self.isFull:
            if self.isRaisingExceptionOnQueueSize:
                self.__md.Give()
                raise ValueError(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwQueue_TID_003).format(self.ToString()))
            else:
                self.__md.Give()
                return False

        if self.isFIFO:
            self.__q.append(elem_)
        else:
            self.__q.appendleft(elem_)

        if _FwQueue.EQState.IsBlockingEmptyState(self.__ms):
            _FwQueue.EQState.RemoveQState(self.__ms, _FwQueue.EQState.eEmpty)
            self.__s.Give()
            self.__md.Give()
            return True

        if self.isFull:
            if self.isBlockingOnQueueSize:
                _FwQueue.EQState.AddQState(self.__ms, _FwQueue.EQState.eFull)

        self.__md.Give()
        return True

    def __Pop(self, bBlock_ : bool, timeout_ =None):
        if bBlock_:
            if timeout_ is not None:
                if not _Timeout.IsFiniteTimeout(timeout_):
                    logif._LogErrorEC(_EFwErrorCode.UE_00133, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwQueue_TID_002).format(str(timeout_)))
                    return None

        with self.__md:
            if _FwQueue.EQState.IsBlockingState(self.__ms):
                if _FwQueue.EQState.IsBlockingDtorState(self.__ms):
                    if len(self.__q) > 0:
                        self.__q.pop()
                    return None

                if _FwQueue.EQState.IsBlockingFullState(self.__ms):
                    if self.isFIFO:
                        res = self.__q.popleft()
                    else:
                        res = self.__q.pop()
                    _FwQueue.EQState.RemoveQState(self.__ms, _FwQueue.EQState.eFull)
                    self.__s.Give()
                    return res

        _bBlocking = self.isBlockingOnQueueSize

        if not bBlock_:
            _bAL = self.__ma.TakeNowait()
        elif timeout_ is not None:
            _bAL = self.__ma.TakeWait(timeout_)
        else:
            _bAL = self.__ma.Take()

        if not _bAL:
            return None

        self.__md.Take()
        self.__ma.Give()

        if _FwQueue.EQState.IsBlockingDtorState(self.__ms):
            self.__md.Give()
            return None
        if _FwQueue.EQState.IsBlockingEmptyState(self.__ms):
            self.__md.Give()
            self.__s.Take()
            if _FwQueue.EQState.IsBlockingDtorState(self.__ms):
                return None

            self.__md.Take()
            if _FwQueue.EQState.IsBlockingDtorState(self.__ms):
                self.__md.Give()
                return None
            if self.isFIFO:
                res = self.__q.popleft()
            else:
                res = self.__q.pop()

            if self.isEmpty:
                _FwQueue.EQState.AddQState(self.__ms, _FwQueue.EQState.eEmpty)

            self.__md.Give()
            return res

        if self.isEmpty:
            if self.isRaisingExceptionOnQueueSize:
                self.__md.Give()
                raise ValueError(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwQueue_TID_004).format(self.ToString()))
            else:
                self.__md.Give()
                return None

        if self.isFIFO:
            res = self.__q.popleft()
        else:
            res = self.__q.pop()

        if _FwQueue.EQState.IsBlockingFullState(self.__ms):
            _FwQueue.EQState.RemoveQState(self.__ms, _FwQueue.EQState.eFull)
            self.__s.Give()
            self.__md.Give()
            return res

        if self.isEmpty:
            if self.isBlockingOnQueueSize:
                _FwQueue.EQState.AddQState(self.__ms, _FwQueue.EQState.eEmpty)

        self.__md.Give()
        return res

    def __PrepareCleanup(self):
        with self.__md:
            _bB = _FwQueue.EQState.IsBlockingState(self.__ms)

            while len(self.__q):
                _elem = self.__q.pop()
                if isinstance(_elem, (_AbsObject, _AbsSlotsObject)):
                    _elem.CleanUp()

            self.__q.append(_FwQueue.__theInvalidQEntry)
            self.__ms = _FwQueue.EQState.eDtor

            if _bB:
                self.__s.Give()

        _MTN = 5

        _c = 0
        while _c < _MTN:
            with self.__md:
                if len(self.__q) != 1:
                    _c = 0
                else:
                    _c += 1
