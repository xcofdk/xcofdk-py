# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : lcproxydefines.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from enum import unique

from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.aexecutable import _AbstractExecutable
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.atask       import _AbstractTask
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil    import _ETaskExecutionPhaseID
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcdefines        import _ELcOperationModeID
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject       import _AbstractSlotsObject
from xcofdk._xcofw.fw.fwssys.fwcore.types.ebitmask       import _EBitMask
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes   import _FwEnum
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes   import _FwIntFlag


@unique
class _ELcShutdownRequest(_FwEnum):
    eFailureHandling = 40
    ePreShutdown     = 51
    eShutdown        = 52

    @property
    def isFailureHandling(self):
        return self == _ELcShutdownRequest.eFailureHandling

    @property
    def isPreShutdown(self):
        return self == _ELcShutdownRequest.ePreShutdown

    @property
    def isShutdown(self):
        return self == _ELcShutdownRequest.eShutdown


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
    def _toLcShutdownRequest(self) -> _ELcShutdownRequest:
        if   self == _ELcOpModeBitFlag.ebfLcFailureHandling: res = _ELcShutdownRequest.eFailureHandling
        elif self == _ELcOpModeBitFlag.ebfLcPreShutdown:     res = _ELcShutdownRequest.ePreShutdown
        elif self == _ELcOpModeBitFlag.ebfLcShutdown:        res = _ELcShutdownRequest.eShutdown
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


class _TaskInfo(_AbstractSlotsObject):
    __slots__ = [ '__taskInst' , '__mtxErrImp' ]

    def __init__(self, taskInst_ : _AbstractTask, mm_):
        super().__init__()
        self.__taskInst  = taskInst_
        self.__mtxErrImp = mm_

    @property
    def isInLcCeaseMode(self):
        return False if self._isInvalid else self.__taskInst.isInLcCeaseMode

    @property
    def isFwMain(self) -> int:
        return False if self._isInvalid else (self.__mtxErrImp is not None)

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
    def hasUnitTestTaskRight(self):
        tb = self.taskBadge
        return False if tb is None else tb.hasUnitTestTaskRight

    @property
    def taskID(self) -> int:
        return None if self._isInvalid else self.taskBadge.taskID

    @property
    def taskName(self) -> str:
        return None if self._isInvalid else self.taskBadge.taskName

    @property
    def taskUniqueName(self) -> str:
        return None if self._isInvalid else self.taskBadge.taskUniqueName

    @property
    def taskError(self):
        return None if self._isInvalid else self.__taskInst.taskError

    @property
    def taskBadge(self):
        return None if self._isInvalid else self.__taskInst.taskBadge

    @property
    def linkedExecutable(self) -> _AbstractExecutable:
        return None if self._isInvalid else self.__taskInst.linkedExecutable

    @property
    def xtaskConnector(self):
        return None if self._isInvalid else self.__taskInst.xtaskConnector

    @property
    def euRNumber(self):
        return None if self._isInvalid else self.__taskInst.euRNumber

    @property
    def eTaskExecPhase(self):
        return _ETaskExecutionPhaseID.eNone if self._isInvalid else self.__taskInst.eTaskExecPhase

    @property
    def _isInvalid(self):
        _ti = self.__taskInst
        return (_ti is None) or (_ti.taskBadge is None) or (_ti.taskError is None)

    @property
    def _errorImpactSyncMutex(self):
        return None if self._isInvalid else self.__mtxErrImp

    @property
    def _isResponsive(self):
        _ti = self.__taskInst
        if (_ti is None) or (_ti.taskBadge is None):
            return False


        return _ti.linkedPyThread.is_alive()

    @property
    def _taskInst(self) -> _AbstractTask:
        return self.__taskInst

    def _ToString(self, *args_, **kwargs_):
        return type(self).__name__

    def _CleanUp(self):
        self.__taskInst  = None
        self.__mtxErrImp = None


class _ProxyInfo(_AbstractSlotsObject):

    __slots__ = [ '__ctInfo' , '__fwmInfo' ]

    def __init__(self, curTaskInst_ : _AbstractTask, fwMainTaskInfo_ : _TaskInfo):
        self.__ctInfo  = None
        self.__fwmInfo = None
        super().__init__()

        if not (isinstance(curTaskInst_, _AbstractTask) and isinstance(fwMainTaskInfo_, _TaskInfo)):
            self.CleanUp()
            return

        if curTaskInst_.threadUID == fwMainTaskInfo_._taskInst.threadUID:
            self.__ctInfo = fwMainTaskInfo_
        else:
            self.__ctInfo  = _TaskInfo(curTaskInst_, None)
            self.__fwmInfo = fwMainTaskInfo_

        if self.__ctInfo._isInvalid or not self.__ctInfo._isResponsive:
            self.CleanUp()
        elif (self.__fwmInfo is not None) and not self.__fwmInfo._isResponsive:
            self.CleanUp()

    @property
    def curTaskInfo(self) -> _TaskInfo:
        return self.__ctInfo

    @property
    def fwMainInfo(self) -> _TaskInfo:
        return self.__fwmInfo

    def _ToString(self, *args_, **kwargs_):
        pass

    def _CleanUp(self):
        if self.__ctInfo is not None:
            if self.__fwmInfo is not None:
                self.__ctInfo.CleanUp()
        self.__ctInfo  = None
        self.__fwmInfo = None
