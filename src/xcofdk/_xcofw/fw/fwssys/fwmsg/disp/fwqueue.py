# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : queue.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from collections import deque as _PyDeque
from enum        import IntFlag
from enum        import unique

from xcofdk._xcofw.fw.fwssys.fwcore.logging            import logif
from xcofdk._xcofw.fw.fwssys.fwcore.logging            import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.base.gtimeout      import _Timeout
from xcofdk._xcofw.fw.fwssys.fwcore.base.util          import _Util
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.sync.semaphore import _BinarySemaphore
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.sync.mutex     import _Mutex
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil   import _TaskUtil
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject      import _AbstractObject
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject      import _AbstractSlotsObject
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes  import _CommonDefines
from xcofdk._xcofw.fw.fwssys.fwcore.types.ebitmask     import _EBitMask

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine



class _FwQueue(_AbstractSlotsObject):

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

    __slots__ = [ '__bFifo'   , '__queue'   , '__mtxApi'  , '__mtxData'
                , '__optMask' , '__qstMask' , '__semSize' , '__maxSize' ]

    __theInvalidQEntry                       = __InvalidQueueEntry()
    __BLOCKING_QUEUE_DEFAULT_WAIT_TIMEOUT_MS = 50

    def __init__(self, optFlags_ =None, maxSize_ =None, bFIFO_ =True):

        super().__init__()

        self.__bFifo   = None
        self.__queue   = None
        self.__mtxApi  = None
        self.__mtxData = None
        self.__qstMask = None
        self.__optMask = None
        self.__semSize = None
        self.__maxSize = None

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
            logif._LogBadUse(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwQueue_TextID_005))
            self.CleanUp()
            return
        if _optMask != _FwQueue.EQOption.eNone:
            if maxSize_ == 0:
                logif._LogBadUse(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwQueue_TextID_006))
                self.CleanUp()
                return

        self.__bFifo   = bFIFO_
        self.__queue   = _PyDeque()
        self.__mtxApi  = _Mutex()
        self.__mtxData = _Mutex()
        self.__qstMask = _FwQueue.EQState.eIdle
        self.__optMask = _optMask
        self.__semSize = None
        self.__maxSize = maxSize_

        if _FwQueue.EQOption.IsQOptionFlagSet(self.__optMask, _FwQueue.EQOption.eBlockOnQueueSize):
            _FwQueue.EQState.AddQState(self.__qstMask, _FwQueue.EQState.eEmpty)

        self.__semSize = _BinarySemaphore()

    @staticmethod
    def GetFiniteQueueMinSize():
        return 2

    @staticmethod
    def GetFiniteQueueDefaultSize():
        return 200

    @staticmethod
    def CreateInstance(maxSize_ =None, bFIFO_ =True):
        res = _FwQueue(_FwQueue.EQOption.eNone, maxSize_, bFIFO_)
        if res.__queue is None:
            res = None
        return res

    @staticmethod
    def CreateInstanceBlockingOnSize(maxSize_ =None, bFIFO_ =True):
        res = _FwQueue(_FwQueue.EQOption.eBlockOnQueueSize, maxSize_, bFIFO_)
        if res.__queue is None:
            res = None
        return res

    @staticmethod
    def CreateInstanceExceptionOnSize(maxSize_ =None, bFIFO_ =True):
        res = _FwQueue(_FwQueue.EQOption.eExceptionOnQueueSize, maxSize_, bFIFO_)
        if res.__queue is None:
            res = None
        return res

    @property
    def isFIFO(self):
        return self.__bFifo

    @property
    def isEmpty(self):
        return self.qsize == 0

    @property
    def isFull(self):
        return (self.__maxSize != 0) and (self.qsize == self.__maxSize)


    @property
    def isBlockingOnQueueSize(self) -> bool:
        return _FwQueue.EQOption.IsQOptionFlagSet(self.__optMask, _FwQueue.EQOption.eBlockOnQueueSize)

    @property
    def isRaisingExceptionOnQueueSize(self) -> bool:
        return _FwQueue.EQOption.IsQOptionFlagSet(self.__optMask, _FwQueue.EQOption.eExceptionOnQueueSize)

    @property
    def hasInfiniteSize(self):
        return (self.__maxSize is not None) and self.__maxSize == 0

    @property
    def hasFiniteSize(self):
        return (self.__maxSize is not None) and self.__maxSize != 0

    @property
    def capacity(self):
        return self.__maxSize

    @property
    def qsize(self):
        with self.__mtxData:
            return len(self.__queue)

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
            vlogif._LogOEC(True, -1664)
            return None
        res = self.__Pop(False)
        if res is None:
            if (sleepTimeMS_ is None) or (sleepTimeMS_ <= 0):
                sleepTimeMS_ = _FwQueue.__BLOCKING_QUEUE_DEFAULT_WAIT_TIMEOUT_MS
            _TaskUtil.SleepMS(sleepTimeMS_)
        return res

    def _CleanUp(self):
        if self.__qstMask is None:
            return
        self.__PrepareCleanup()

        if self.__semSize is not None:
            self.__semSize.CleanUp()

        self.__queue.clear()
        self.__mtxApi.CleanUp()
        self.__mtxData.CleanUp()

        self.__bFifo   = None
        self.__queue   = None
        self.__mtxApi  = None
        self.__mtxData = None
        self.__qstMask = None
        self.__optMask = None
        self.__semSize = None
        self.__maxSize = None

    def _ToString(self, *args_, **kwargs_):
        res = _CommonDefines._STR_EMPTY
        return res

    def __Push(self, elem_, bBlock_ : bool, timeout_ =None):

        if bBlock_:
            if timeout_ is not None:
                if not _Timeout.IsFiniteTimeout(timeout_):
                    logif._LogError(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwQueue_TextID_001).format(str(timeout_)))
                    return False

        with self.__mtxData:
            if _FwQueue.EQState.IsBlockingState(self.__qstMask):
                if _FwQueue.EQState.IsBlockingDtorState(self.__qstMask):
                    if len(self.__queue) > 0:
                        self.__queue.pop()
                    return False

                if _FwQueue.EQState.IsBlockingEmptyState(self.__qstMask):
                    if self.isFIFO:
                        self.__queue.append(elem_)
                    else:
                        self.__queue.appendleft(elem_)

                    _FwQueue.EQState.RemoveQState(self.__qstMask, _FwQueue.EQState.eEmpty)
                    self.__semSize.Give()
                    return True

        if not bBlock_:
            _bApiLocked = self.__mtxApi.TakeNowait()
        elif timeout_ is not None:
            _bApiLocked = self.__mtxApi.TakeWait(timeout_)
        else:
            _bApiLocked = self.__mtxApi.Take()

        if not _bApiLocked:
            return False

        self.__mtxData.Take()
        self.__mtxApi.Give()

        if _FwQueue.EQState.IsBlockingDtorState(self.__qstMask):
            self.__mtxData.Give()
            return False

        if _FwQueue.EQState.IsBlockingFullState(self.__qstMask):
            self.__mtxData.Give()

            self.__semSize.Take()
            if _FwQueue.EQState.IsBlockingDtorState(self.__qstMask):
                return False

            self.__mtxData.Take()
            if _FwQueue.EQState.IsBlockingDtorState(self.__qstMask):
                self.__mtxData.Give()
                return False

            if self.isFIFO:
                self.__queue.append(elem_)
            else:
                self.__queue.appendleft(elem_)

            if self.isFull:
                _FwQueue.EQState.AddQState(self.__qstMask, _FwQueue.EQState.eFull)

            self.__mtxData.Give()
            return True

        if self.isFull:
            if self.isRaisingExceptionOnQueueSize:
                self.__mtxData.Give()
                raise ValueError(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwQueue_TextID_003).format(self.ToString()))
            else:
                self.__mtxData.Give()
                return False

        if self.isFIFO:
            self.__queue.append(elem_)
        else:
            self.__queue.appendleft(elem_)

        if _FwQueue.EQState.IsBlockingEmptyState(self.__qstMask):
            _FwQueue.EQState.RemoveQState(self.__qstMask, _FwQueue.EQState.eEmpty)
            self.__semSize.Give()
            self.__mtxData.Give()
            return True

        if self.isFull:
            if self.isBlockingOnQueueSize:
                _FwQueue.EQState.AddQState(self.__qstMask, _FwQueue.EQState.eFull)

        self.__mtxData.Give()
        return True

    def __Pop(self, bBlock_ : bool, timeout_ =None):


        if bBlock_:
            if timeout_ is not None:
                if not _Timeout.IsFiniteTimeout(timeout_):
                    logif._LogError(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwQueue_TextID_002).format(str(timeout_)))
                    return None

        with self.__mtxData:
            if _FwQueue.EQState.IsBlockingState(self.__qstMask):
                if _FwQueue.EQState.IsBlockingDtorState(self.__qstMask):
                    if len(self.__queue) > 0:
                        self.__queue.pop()
                    return None

                if _FwQueue.EQState.IsBlockingFullState(self.__qstMask):
                    if self.isFIFO:
                        res = self.__queue.popleft()
                    else:
                        res = self.__queue.pop()

                    _FwQueue.EQState.RemoveQState(self.__qstMask, _FwQueue.EQState.eFull)
                    self.__semSize.Give()
                    return res

        _bBlocking = self.isBlockingOnQueueSize

        if not bBlock_:
            _bApiLocked = self.__mtxApi.TakeNowait()
        elif timeout_ is not None:
            _bApiLocked = self.__mtxApi.TakeWait(timeout_)
        else:
            _bApiLocked = self.__mtxApi.Take()

        if not _bApiLocked:
            return None

        self.__mtxData.Take()
        self.__mtxApi.Give()

        if _FwQueue.EQState.IsBlockingDtorState(self.__qstMask):
            self.__mtxData.Give()
            return None

        if _FwQueue.EQState.IsBlockingEmptyState(self.__qstMask):
            self.__mtxData.Give()

            self.__semSize.Take()
            if _FwQueue.EQState.IsBlockingDtorState(self.__qstMask):
                return None

            self.__mtxData.Take()
            if _FwQueue.EQState.IsBlockingDtorState(self.__qstMask):
                self.__mtxData.Give()
                return None

            if self.isFIFO:
                res = self.__queue.popleft()
            else:
                res = self.__queue.pop()

            if self.isEmpty:
                _FwQueue.EQState.AddQState(self.__qstMask, _FwQueue.EQState.eEmpty)

            self.__mtxData.Give()
            return res

        if self.isEmpty:
            if self.isRaisingExceptionOnQueueSize:
                self.__mtxData.Give()
                raise ValueError(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwQueue_TextID_004).format(self.ToString()))
            else:
                self.__mtxData.Give()
                return None

        if self.isFIFO:
            res = self.__queue.popleft()
        else:
            res = self.__queue.pop()

        if _FwQueue.EQState.IsBlockingFullState(self.__qstMask):
            _FwQueue.EQState.RemoveQState(self.__qstMask, _FwQueue.EQState.eFull)
            self.__semSize.Give()
            self.__mtxData.Give()
            return res

        if self.isEmpty:
            if self.isBlockingOnQueueSize:
                _FwQueue.EQState.AddQState(self.__qstMask, _FwQueue.EQState.eEmpty)

        self.__mtxData.Give()
        return res

    def __PrepareCleanup(self):
        with self.__mtxData:
            _bIsBlocking = _FwQueue.EQState.IsBlockingState(self.__qstMask)

            while len(self.__queue):
                _elem = self.__queue.pop()
                if isinstance(_elem, (_AbstractObject, _AbstractSlotsObject)):
                    _elem.CleanUp()

            self.__queue.append(_FwQueue.__theInvalidQEntry)
            self.__qstMask = _FwQueue.EQState.eDtor

            if _bIsBlocking:
                self.__semSize.Give()

        _MAX_TRY_NUM = 5
        _tryNo = 0

        while _tryNo < _MAX_TRY_NUM:
            with self.__mtxData:
                if len(self.__queue) != 1:
                    _tryNo = 0
                else:
                    _tryNo += 1
