# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xtaskprfbase.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from enum import unique
from enum import IntFlag

from xcofdk._xcofw.fw.fwssys.fwcore.logging        import logif
from xcofdk._xcofw.fw.fwssys.fwcore.types.ebitmask import _EBitMask

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine

from xcofdk._xcofwa.fwadmindefs import _FwSubsystemCoding


class _XTaskProfileBase:
    @unique
    class _ETaskPrfFlag(IntFlag):
        bfNone             = 0x0000
        bfMainXT           = (0x0001 << 0)
        bfSyncTask         = (0x0001 << 1)
        bfRunPhase         = (0x0001 << 2)
        bfIntqueue         = (0x0001 << 3)
        bfExtQueue         = (0x0001 << 4)
        bfSetupPhase       = (0x0001 << 5)
        bfPrivileged       = (0x0001 << 6)
        bfTeardownPhase    = (0x0001 << 7)
        bfBlockingExtQueue = (0x0001 << 8)

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


    __DEFAULT_CYCLIC_MPTS_MS = 50
    __DEFAULT_CYCLIC_RPTS_MS = 100

    __slots__ = [ '__bm' , '__aliasName' , '__runPhaseMaxProcTimeMS' , '__runPhaseFreqMS' ]

    def __init__(self):
        self.__bm  = _XTaskProfileBase._ETaskPrfFlag.bfNone
        self.__bm |= _XTaskProfileBase._ETaskPrfFlag.bfRunPhase

        self.__aliasName             = None
        self.__runPhaseFreqMS        = _XTaskProfileBase.__DEFAULT_CYCLIC_RPTS_MS
        self.__runPhaseMaxProcTimeMS = _XTaskProfileBase.__DEFAULT_CYCLIC_MPTS_MS

    def __str__(self):
        return self._ToString()

    @staticmethod
    def _GetDefaultRunPhaseFrequencyMS():
        return _XTaskProfileBase.__DEFAULT_CYCLIC_RPTS_MS

    @staticmethod
    def _GetDefaultRunPhaseMaxProcessingTimeMS():
        return _XTaskProfileBase.__DEFAULT_CYCLIC_MPTS_MS

    @property
    def _isValid(self) -> bool:
        return not self.__isInvalid

    @property
    def _isFrozen(self) -> bool:
        return False

    @property
    def _isMainTask(self) -> bool:
        return self.__isValid and _XTaskProfileBase._ETaskPrfFlag.IsTaskPrfFlagSet(self.__bm, _XTaskProfileBase._ETaskPrfFlag.bfMainXT)

    @property
    def _isPrivilegedTask(self) -> bool:
        return self.__isValid and _XTaskProfileBase._ETaskPrfFlag.IsTaskPrfFlagSet(self.__bm, _XTaskProfileBase._ETaskPrfFlag.bfPrivileged)

    @_isPrivilegedTask.setter
    def _isPrivilegedTask(self, bPrivileged_ : bool):
        if not self._CheckFreezeState(): return
        if bPrivileged_:
            self.__bm = _XTaskProfileBase._ETaskPrfFlag.AddTaskPrfFlag(self.__bm, _XTaskProfileBase._ETaskPrfFlag.bfPrivileged)
        else:
            self.__bm = _XTaskProfileBase._ETaskPrfFlag.RemoveTaskPrfFlag(self.__bm, _XTaskProfileBase._ETaskPrfFlag.bfPrivileged)

    @property
    def _isRunPhaseEnabled(self) -> bool:
        return self._isValid and _XTaskProfileBase._ETaskPrfFlag.IsTaskPrfFlagSet(self.__bm, _XTaskProfileBase._ETaskPrfFlag.bfRunPhase)

    @_isRunPhaseEnabled.setter
    def _isRunPhaseEnabled(self, bEnableRun_ : bool):
        if not self._CheckFreezeState(): return
        if bEnableRun_:
            self.__bm = _XTaskProfileBase._ETaskPrfFlag.AddTaskPrfFlag(self.__bm, _XTaskProfileBase._ETaskPrfFlag.bfRunPhase)
        else:
            self.__bm = _XTaskProfileBase._ETaskPrfFlag.RemoveTaskPrfFlag(self.__bm, _XTaskProfileBase._ETaskPrfFlag.bfRunPhase)

    @property
    def _isSetupPhaseEnabled(self) -> bool:
        return self.__isValid and _XTaskProfileBase._ETaskPrfFlag.IsTaskPrfFlagSet(self.__bm, _XTaskProfileBase._ETaskPrfFlag.bfSetupPhase)

    @_isSetupPhaseEnabled.setter
    def _isSetupPhaseEnabled(self, bEnableSetup_ : bool):
        if not self._CheckFreezeState(): return
        if bEnableSetup_:
            self.__bm = _XTaskProfileBase._ETaskPrfFlag.AddTaskPrfFlag(self.__bm, _XTaskProfileBase._ETaskPrfFlag.bfSetupPhase)
        else:
            self.__bm = _XTaskProfileBase._ETaskPrfFlag.RemoveTaskPrfFlag(self.__bm, _XTaskProfileBase._ETaskPrfFlag.bfSetupPhase)

    @property
    def _isTeardownPhaseEnabled(self) -> bool:
        return self.__isValid and _XTaskProfileBase._ETaskPrfFlag.IsTaskPrfFlagSet(self.__bm, _XTaskProfileBase._ETaskPrfFlag.bfTeardownPhase)

    @_isTeardownPhaseEnabled.setter
    def _isTeardownPhaseEnabled(self, bEnableTeardown_ : bool):
        if not self._CheckFreezeState(): return
        if bEnableTeardown_:
            self.__bm = _XTaskProfileBase._ETaskPrfFlag.AddTaskPrfFlag(self.__bm, _XTaskProfileBase._ETaskPrfFlag.bfTeardownPhase)
        else:
            self.__bm = _XTaskProfileBase._ETaskPrfFlag.RemoveTaskPrfFlag(self.__bm, _XTaskProfileBase._ETaskPrfFlag.bfTeardownPhase)

    @property
    def _isInternalQueueEnabled(self) -> bool:
        return False

    @property
    def _isExternalQueueEnabled(self) -> bool:
        return self.__isValid and _XTaskProfileBase._ETaskPrfFlag.IsTaskPrfFlagSet(self.__bm, _XTaskProfileBase._ETaskPrfFlag.bfExtQueue)

    @_isExternalQueueEnabled.setter
    def _isExternalQueueEnabled(self, bExternalQueue_ : bool):
        if not self._CheckFreezeState(): return
        if not _FwSubsystemCoding.IsSubsystemMessagingConfigured():
            logif._XLogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskProfileBase_TextID_002))
        elif bExternalQueue_:
            self.__bm = _XTaskProfileBase._ETaskPrfFlag.AddTaskPrfFlag(self.__bm, _XTaskProfileBase._ETaskPrfFlag.bfExtQueue)
        else:
            self.__bm = _XTaskProfileBase._ETaskPrfFlag.RemoveTaskPrfFlag(self.__bm, _XTaskProfileBase._ETaskPrfFlag.bfExtQueue)
            if self._isExternalQueueBlocking:
                self._isRunPhaseEnabled       = True
                self._isExternalQueueBlocking = False

    @property
    def _isExternalQueueBlocking(self) -> bool:
        return self.__isValid and _XTaskProfileBase._ETaskPrfFlag.IsTaskPrfFlagSet(self.__bm, _XTaskProfileBase._ETaskPrfFlag.bfBlockingExtQueue)

    @_isExternalQueueBlocking.setter
    def _isExternalQueueBlocking(self, bBlockingExtQueue_ : bool):
        if not self._CheckFreezeState(): return
        if not _FwSubsystemCoding.IsSubsystemMessagingConfigured():
            logif._XLogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskProfileBase_TextID_003))
        else:
            if bBlockingExtQueue_:
                if self._isSynchronousTask:
                    logif._XLogError(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskProfileBase_TextID_012))
                    return

                self.__bm = _XTaskProfileBase._ETaskPrfFlag.AddTaskPrfFlag(self.__bm, _XTaskProfileBase._ETaskPrfFlag.bfBlockingExtQueue)
                self._isRunPhaseEnabled = False
                if not self._isExternalQueueEnabled:
                    self._isExternalQueueEnabled = True
            else:
                self.__bm = _XTaskProfileBase._ETaskPrfFlag.RemoveTaskPrfFlag(self.__bm, _XTaskProfileBase._ETaskPrfFlag.bfBlockingExtQueue)
                self._isRunPhaseEnabled = True

    @property
    def _isSynchronousTask(self) -> bool:
        return self.__isValid and _XTaskProfileBase._ETaskPrfFlag.IsTaskPrfFlagSet(self.__bm, _XTaskProfileBase._ETaskPrfFlag.bfSyncTask)

    @_isSynchronousTask.setter
    def _isSynchronousTask(self, bSynchronousTask_ : bool):
        if not self._CheckFreezeState(): return
        elif bSynchronousTask_:
            self.__runPhaseFreqMS = 0
            self.__bm = _XTaskProfileBase._ETaskPrfFlag.AddTaskPrfFlag(self.__bm, _XTaskProfileBase._ETaskPrfFlag.bfSyncTask)
        else:
            self.__bm = _XTaskProfileBase._ETaskPrfFlag.RemoveTaskPrfFlag(self.__bm, _XTaskProfileBase._ETaskPrfFlag.bfSyncTask)

    @property
    def _isSingleCycleRunPhase(self) -> bool:
        return self._runPhaseFrequencyMS == 0

    @property
    def _aliasName(self) -> str:
        return self.__aliasName

    @_aliasName.setter
    def _aliasName(self, aliasName_ : str):
        if not self._CheckFreezeState(): return
        if not (isinstance(aliasName_, str) and aliasName_.isidentifier()):
            logif._XLogError(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskProfileBase_TextID_011).format(str(aliasName_)))
            return
        self.__aliasName = str(aliasName_)

    @property
    def _runPhaseFrequencyMS(self) -> int:
        return self.__runPhaseFreqMS

    @_runPhaseFrequencyMS.setter
    def _runPhaseFrequencyMS(self, runPhaseFreqMS_ : [int, float]):

        if not self._CheckFreezeState(): return
        if isinstance(runPhaseFreqMS_, float):
            runPhaseFreqMS_ = int(1000*runPhaseFreqMS_)

        if not isinstance(runPhaseFreqMS_, int):
            logif._XLogError(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskProfileBase_TextID_006).format(type(runPhaseFreqMS_).__name__))
            self._CleanUp()
            return
        if runPhaseFreqMS_ < 0:
            logif._XLogError(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskProfileBase_TextID_007).format(runPhaseFreqMS_))
            self._CleanUp()
            return
        self.__runPhaseFreqMS = runPhaseFreqMS_

    @property
    def _runPhaseMaxProcessingTimeMS(self) -> int:
        return self.__runPhaseMaxProcTimeMS

    @_runPhaseMaxProcessingTimeMS.setter
    def _runPhaseMaxProcessingTimeMS(self, runPhaseMaxProcTimeMS_ : [int, float]):

        if not self._CheckFreezeState(): return
        if isinstance(runPhaseMaxProcTimeMS_, float):
            runPhaseMaxProcTimeMS_ = int(1000*runPhaseMaxProcTimeMS_)

        if not isinstance(runPhaseMaxProcTimeMS_, int):
            logif._XLogError(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskProfileBase_TextID_004).format(type(runPhaseMaxProcTimeMS_).__name__))
            self._CleanUp()
            return
        if runPhaseMaxProcTimeMS_ < 1:
            logif._XLogError(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskProfileBase_TextID_005).format(runPhaseMaxProcTimeMS_))
            self._CleanUp()
            return
        self.__runPhaseMaxProcTimeMS = runPhaseMaxProcTimeMS_

    def _ToString(self, bVerbose_ =True) -> str:
        res = _FwTDbEngine.GetText(_EFwTextID.eXTaskProfileBase_ToString_01)
        res += '\t{:<32} : {}\n'.format(_FwTDbEngine.GetText(_EFwTextID.eXTaskProfileBase_ToString_02), str(self._aliasName))
        res += '\t{:<32} : {}\n'.format(_FwTDbEngine.GetText(_EFwTextID.eXTaskProfileBase_ToString_03), str(self._isMainTask))
        res += '\t{:<32} : {}\n'.format(_FwTDbEngine.GetText(_EFwTextID.eXTaskProfileBase_ToString_05), str(self._isPrivilegedTask))
        res += '\t{:<32} : {}\n'.format(_FwTDbEngine.GetText(_EFwTextID.eXTaskProfileBase_ToString_11), str(self._isSynchronousTask))

        if bVerbose_:
            res += '\t{:<32} : {}\n'.format(_FwTDbEngine.GetText(_EFwTextID.eXTaskProfileBase_ToString_14), str(self._isRunPhaseEnabled))
            res += '\t{:<32} : {}\n'.format(_FwTDbEngine.GetText(_EFwTextID.eXTaskProfileBase_ToString_06), str(self._isSetupPhaseEnabled))
            res += '\t{:<32} : {}\n'.format(_FwTDbEngine.GetText(_EFwTextID.eXTaskProfileBase_ToString_07), str(self._isTeardownPhaseEnabled))
            res += '\t{:<32} : {}\n'.format(_FwTDbEngine.GetText(_EFwTextID.eXTaskProfileBase_ToString_08), str(self._isInternalQueueEnabled))
            res += '\t{:<32} : {}\n'.format(_FwTDbEngine.GetText(_EFwTextID.eXTaskProfileBase_ToString_09), str(self._isExternalQueueEnabled))
            res += '\t{:<32} : {}\n'.format(_FwTDbEngine.GetText(_EFwTextID.eXTaskProfileBase_ToString_10), str(self._isExternalQueueBlocking))
            res += '\t{:<32} : {}\n'.format(_FwTDbEngine.GetText(_EFwTextID.eXTaskProfileBase_ToString_12), str(self._runPhaseFrequencyMS))
            res += '\t{:<32} : {}\n'.format(_FwTDbEngine.GetText(_EFwTextID.eXTaskProfileBase_ToString_13), str(self._runPhaseMaxProcessingTimeMS))
        return res

    def _Clone(self):
        res = _XTaskProfileBase()
        res = _XTaskProfileBase._AssignProfile(res, self)
        return res

    def _AssignProfile(self, rhs_):
        if not self._CheckFreezeState(): return None
        if not isinstance(rhs_, _XTaskProfileBase):
            return None
        if rhs_.__isInvalid:
            return None

        self._isPrivilegedTask       = rhs_._isPrivilegedTask
        self._isSynchronousTask      = rhs_._isSynchronousTask
        self._isRunPhaseEnabled      = rhs_._isRunPhaseEnabled
        self._isSetupPhaseEnabled    = rhs_._isSetupPhaseEnabled
        self._isTeardownPhaseEnabled = rhs_._isTeardownPhaseEnabled

        if _FwSubsystemCoding.IsSubsystemMessagingConfigured():
            self._isExternalQueueEnabled  = rhs_._isExternalQueueEnabled
            self._isExternalQueueBlocking = rhs_._isExternalQueueBlocking
        self._aliasName                   = str(rhs_._aliasName)
        self._runPhaseFrequencyMS         = rhs_._runPhaseFrequencyMS
        self._runPhaseMaxProcessingTimeMS = rhs_._runPhaseMaxProcessingTimeMS
        return self

    def _SetMainXTask(self, bMainXT_ : bool):
        if not self._CheckFreezeState(): return
        self.__bm = _XTaskProfileBase._ETaskPrfFlag.AddTaskPrfFlag(self.__bm, _XTaskProfileBase._ETaskPrfFlag.bfMainXT)

    def _CleanUp(self):
        self.__bm        = None
        self.__aliasName = None

        self.__runPhaseFreqMS         = None
        self.__runPhaseMaxProcTimeMS  = None

    def _CheckFreezeState(self) -> bool:
        if self.__isInvalid:
            return False
        if self._isFrozen:
            logif._XLogError(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskProfileBase_TextID_009))
            return False
        return True

    @property
    def __isValid(self) -> bool:
        return self.__bm is not None

    @property
    def __isInvalid(self) -> bool:
        return self.__bm is None


