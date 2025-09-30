# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : lcproxydefines.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum import unique

from _fw.fwssys.fwcore.ipc.tsk.afwtask   import _AbsFwTask
from _fw.fwssys.fwcore.ipc.tsk.taskutil  import _ETaskXPhaseID
from _fw.fwssys.fwcore.lc.lcdefines      import _ELcOperationModeID
from _fw.fwssys.fwcore.types.aobject     import _AbsSlotsObject
from _fw.fwssys.fwcore.types.ebitmask    import _EBitMask
from _fw.fwssys.fwcore.types.commontypes import _FwEnum
from _fw.fwssys.fwcore.types.commontypes import _FwIntFlag

@unique
class _ELcSDRequest(_FwEnum):
    eFailureHandling = 40
    ePreShutdown     = 51
    eShutdown        = 52

    @property
    def isFailureHandling(self):
        return self == _ELcSDRequest.eFailureHandling

    @property
    def isPreShutdown(self):
        return self == _ELcSDRequest.ePreShutdown

    @property
    def isShutdown(self):
        return self == _ELcSDRequest.eShutdown

@unique
class _ELcOpModeBitFlag(_FwIntFlag):
    ebfIdle              = 0x0000
    ebfLcNormal          = (0x0001 << _ELcOperationModeID.eLcNormal.value)
    ebfLcPreShutdown     = (0x0001 << _ELcOperationModeID.eLcPreShutdown.value)
    ebfLcShutdown        = (0x0001 << _ELcOperationModeID.eLcShutdown.value)
    ebfLcFailureHandling = (0x0001 << _ELcOperationModeID.eLcFailureHandling.value)

    @property
    def _toLcOperationModeID(self) -> _ELcOperationModeID:
        if   self == _ELcOpModeBitFlag.ebfLcNormal:          res = _ELcOperationModeID.eLcNormal
        elif self == _ELcOpModeBitFlag.ebfLcPreShutdown:     res = _ELcOperationModeID.eLcPreShutdown
        elif self == _ELcOpModeBitFlag.ebfLcShutdown:        res = _ELcOperationModeID.eLcShutdown
        elif self == _ELcOpModeBitFlag.ebfLcFailureHandling: res = _ELcOperationModeID.eLcFailureHandling
        else:
            res = _ELcOperationModeID.eIdle
        return res

    @property
    def _toLcShutdownRequest(self) -> _ELcSDRequest:
        if   self == _ELcOpModeBitFlag.ebfLcFailureHandling: res = _ELcSDRequest.eFailureHandling
        elif self == _ELcOpModeBitFlag.ebfLcPreShutdown:     res = _ELcSDRequest.ePreShutdown
        elif self == _ELcOpModeBitFlag.ebfLcShutdown:        res = _ELcSDRequest.eShutdown
        else:
            res = None
        return res

    @property
    def compactName(self) -> str:
        return self.name[3:]

    @staticmethod
    def DefaultMask():
        return _ELcOpModeBitFlag(_ELcOpModeBitFlag.ebfIdle)

    @staticmethod
    def IsNormal(eOmBitMask_ : _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eOmBitMask_, _ELcOpModeBitFlag.ebfLcNormal)

    @staticmethod
    def IsPreShutdown(eOmBitMask_ : _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eOmBitMask_, _ELcOpModeBitFlag.ebfLcPreShutdown)

    @staticmethod
    def IsShutdown(eOmBitMask_ : _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eOmBitMask_, _ELcOpModeBitFlag.ebfLcShutdown)

    @staticmethod
    def IsFailureHandling(eOmBitMask_ : _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eOmBitMask_, _ELcOpModeBitFlag.ebfLcFailureHandling)

    @staticmethod
    def IsBitFlagSet(eOmBitMask_ : _FwIntFlag, eOmBitFlag_):
        return _EBitMask.IsEnumBitFlagSet(eOmBitMask_, eOmBitFlag_)

    @staticmethod
    def AddBitFlag(eOmBitMask_ : _FwIntFlag, eOmBitFlag_):
        return _EBitMask.AddEnumBitFlag(eOmBitMask_, eOmBitFlag_)

    @staticmethod
    def RemoveBitFlag(eOmBitMask_ : _FwIntFlag, eOmBitFlag_):
        return _EBitMask.RemoveEnumBitFlag(eOmBitMask_, eOmBitFlag_)

class _TaskInfo(_AbsSlotsObject):
    __slots__ = [ '__t' , '__m' ]

    def __init__(self, taskInst_ : _AbsFwTask, mm_):
        super().__init__()
        self.__m = mm_
        self.__t = taskInst_

    @property
    def isInLcCeaseMode(self):
        return False if self._isInvalid else self.__t.isInLcCeaseMode

    @property
    def isFwMain(self) -> int:
        return False if self._isInvalid else (self.__m is not None)

    @property
    def isAutoEnclosed(self) -> int:
        return False if self._isInvalid else self.taskBadge.isAutoEnclosed

    @property
    def isEnclosingPyThread(self) -> int:
        return False if self._isInvalid else self.taskBadge.isEnclosingPyThread

    @property
    def isDrivingXTask(self):
        return False if self._isInvalid else self.taskBadge.isDrivingXTask

    @property
    def dtaskUID(self) -> int:
        return None if self._isInvalid else self.taskBadge.dtaskUID

    @property
    def dtaskName(self) -> str:
        return None if self._isInvalid else self.taskBadge.dtaskName

    @property
    def taskError(self):
        return None if self._isInvalid else self.__t.taskError

    @property
    def taskBadge(self):
        return None if self._isInvalid else self.__t.taskBadge

    @property
    def utConn(self):
        return None if self._isInvalid else self.__t._utConn

    @property
    def xrNumber(self):
        return None if self._isInvalid else self.__t.xrNumber

    @property
    def taskXPhase(self):
        return _ETaskXPhaseID.eNA if self._isInvalid else self.__t.taskXPhase

    @property
    def _isInvalid(self):
        _ti = self.__t
        return (_ti is None) or (_ti.taskBadge is None) or (_ti.taskError is None)

    @property
    def _errorImpactSyncMutex(self):
        return None if self._isInvalid else self.__m

    @property
    def _isResponsive(self):
        _ti = self.__t
        if (_ti is None) or (_ti.taskBadge is None):
            return False

        return _ti.dHThrd.is_alive()

    @property
    def _taskInst(self) -> _AbsFwTask:
        return self.__t

    def _ToString(self):
        return type(self).__name__

    def _CleanUp(self):
        self.__m = None
        self.__t = None

class _ProxyInfo(_AbsSlotsObject):
    __slots__ = [ '__ci' , '__mi' ]

    def __init__(self, curTaskInst_ : _AbsFwTask, fwMainTaskInfo_ : _TaskInfo):
        self.__ci = None
        self.__mi = None
        super().__init__()

        if not (isinstance(curTaskInst_, _AbsFwTask) and isinstance(fwMainTaskInfo_, _TaskInfo)):
            self.CleanUp()
            return

        if curTaskInst_.threadUID == fwMainTaskInfo_._taskInst.threadUID:
            self.__ci = fwMainTaskInfo_
        else:
            self.__ci = _TaskInfo(curTaskInst_, None)
            self.__mi = fwMainTaskInfo_

        if self.__ci._isInvalid or not self.__ci._isResponsive:
            self.CleanUp()
        elif (self.__mi is not None) and not self.__mi._isResponsive:
            self.CleanUp()

    @property
    def curTaskInfo(self) -> _TaskInfo:
        return self.__ci

    @property
    def fwMainInfo(self) -> _TaskInfo:
        return self.__mi

    def _ToString(self):
        pass

    def _CleanUp(self):
        if self.__ci is not None:
            if self.__mi is not None:
                self.__ci.CleanUp()
        self.__ci = None
        self.__mi = None
