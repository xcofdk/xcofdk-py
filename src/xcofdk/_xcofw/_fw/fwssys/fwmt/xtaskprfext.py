# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xtaskprfext.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum import unique
from enum import IntFlag

from xcofdk.fwapi     import IRCTask
from xcofdk.fwapi.xmt import ITaskProfile

from _fw.fwssys.fwcore.logging          import logif
from _fw.fwssys.fwcore.ipc.tsk.taskutil import _TaskUtil
from _fw.fwssys.fwcore.types.ebitmask   import _EBitMask
from _fw.fwssys.fwerrh.fwerrorcodes     import _EFwErrorCode
from _fw.fwssys.fwmt.api.xtaskprfimpl   import _XTaskPrfImpl
from _fw.fwssys.fwmt.utask.usertaskdefs import _UTaskMirror

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _XTaskPrfExt(_XTaskPrfImpl):
    @unique
    class _ETaskPrfExtFlag(IntFlag):
        bfNone     = 0x0000
        bfRcTask   = (0x0001 << 0)
        bfUnitTest = (0x0001 << 1)

        @property
        def compactName(self) -> str:
            return self.name[2:]

        @staticmethod
        def AddTaskPrfFlag(tprfBM_: IntFlag, tprfBF_):
            return _EBitMask.AddEnumBitFlag(tprfBM_, tprfBF_)

        @staticmethod
        def RemoveTaskPrfFlag(tprfBM_: IntFlag, tprfBF_):
            return _EBitMask.RemoveEnumBitFlag(tprfBM_, tprfBF_)

        @staticmethod
        def IsTaskPrfFlagSet(tprfBM_: IntFlag, tprfBF_):
            return _EBitMask.IsEnumBitFlagSet(tprfBM_, tprfBF_)

    __slots__ = [ '__xbm' , '__utm' , '__i' , '__tid' , '__idx' ]

    def __init__(self, xtPrf_ : ITaskProfile =None, bMainXT_ =False, rctInst_ : IRCTask =None):
        self.__i   = rctInst_
        self.__idx = None
        self.__tid = None
        self.__utm = None
        self.__xbm = _XTaskPrfExt._ETaskPrfExtFlag.bfNone
        super().__init__()

        if xtPrf_ is None:
            pass
        elif not (isinstance(xtPrf_, ITaskProfile) and xtPrf_.isValid):
            self._CleanUp()
            logif._XLogErrorEC(_EFwErrorCode.UE_00186, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskPrfExt_TID_001).format(type(xtPrf_).__name__))
        else:
            _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskPrfExt_TID_002)
            if isinstance(xtPrf_, _XTaskPrfExt):
                if _XTaskPrfExt._AssignProfile(self, xtPrf_) is None:
                    self._CleanUp()
                    logif._XLogErrorEC(_EFwErrorCode.UE_00235, _msg.format(type(xtPrf_).__name__))
            elif _XTaskPrfImpl._AssignProfile(self, xtPrf_) is None:
                self._CleanUp()
                logif._XLogErrorEC(_EFwErrorCode.UE_00187, _msg.format(type(xtPrf_).__name__))

        if self.isValid:
            if bMainXT_ != self.isMainTask:
                super()._SetMainXTask(bMainXT_)
            if rctInst_ is not None:
                self.__xbm = _XTaskPrfExt._ETaskPrfExtFlag.AddTaskPrfFlag(self.__xbm, _XTaskPrfExt._ETaskPrfExtFlag.bfRcTask)

    def __str__(self):
        return self.ToString()

    @property
    def isRcTask(self) -> bool:
        return self.isValid and _XTaskPrfExt._ETaskPrfExtFlag.IsTaskPrfFlagSet(self.__xbm, _XTaskPrfExt._ETaskPrfExtFlag.bfRcTask)

    @property
    def isUnitTest(self) -> bool:
        return self.isValid and _XTaskPrfExt._ETaskPrfExtFlag.IsTaskPrfFlagSet(self.__xbm, _XTaskPrfExt._ETaskPrfExtFlag.bfUnitTest)

    @isUnitTest.setter
    def isUnitTest(self, bUnitTest_ : bool):
        if not self._CheckFreezeState(): return
        if bUnitTest_:
            self.__xbm = _XTaskPrfExt._ETaskPrfExtFlag.AddTaskPrfFlag(self.__xbm, _XTaskPrfExt._ETaskPrfExtFlag.bfUnitTest)
        else:
            self.__xbm = _XTaskPrfExt._ETaskPrfExtFlag.RemoveTaskPrfFlag(self.__xbm, _XTaskPrfExt._ETaskPrfExtFlag.bfUnitTest)

    def ToString(self) -> str:
        res  = super().ToString()
        _fmt = _FwTDbEngine.GetText(_EFwTextID.eXTaskPrfBase_ToString_15)
        res += _fmt.format(_FwTDbEngine.GetText(_EFwTextID.eXTaskPrfExt_ToString_02), str(self.isRcTask))
        return res

    def CloneProfile(self):
        res = _XTaskPrfExt()
        res = _XTaskPrfExt._AssignProfile(res, self)
        return res

    @property
    def _rcTaskInst(self) -> IRCTask:
        return self.__i

    @property
    def _utaskMirror(self) -> _UTaskMirror:
        return self.__utm

    @_utaskMirror.setter
    def _utaskMirror(self, utm_ : _UTaskMirror):
        self.__utm = utm_

    @property
    def _bookedTaskID(self) -> int:
        return self.__tid

    @property
    def _bookedTaskIndex(self) -> int:
        return self.__idx

    def _BookTaskID(self):
        if self.__tid is None:
            self.__tid, self.__idx = _TaskUtil.GetNextTaskID(True)

    def _AssignProfile(self, rhs_):
        if not self._CheckFreezeState(): return None
        if not isinstance(rhs_, _XTaskPrfExt):
            return None
        if super()._AssignProfile(rhs_) is None:
            return None

        self.__i   = rhs_.__i
        self.__idx = rhs_.__idx
        self.__tid = rhs_.__tid
        self.isUnitTest = rhs_.isUnitTest

        if rhs_.isMainTask:
            super()._SetMainXTask(True)

        if self.__i is not None:
            self.__xbm = _XTaskPrfExt._ETaskPrfExtFlag.AddTaskPrfFlag(self.__xbm, _XTaskPrfExt._ETaskPrfExtFlag.bfRcTask)
        return self

    def _CleanUp(self):
        self.__i   = None
        self.__idx = None
        self.__tid = None
        self.__xbm = None
        self.__utm = None
        super()._CleanUp()
