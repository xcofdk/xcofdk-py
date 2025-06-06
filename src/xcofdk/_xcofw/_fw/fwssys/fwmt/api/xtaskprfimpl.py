# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xtaskprfimpl.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from typing import Union

from xcofdk.fwapi.xmt import ITaskProfile

from _fw.fwssys.fwmt.xtaskprfbase        import _XTaskPrfBase
from _fw.fwssys.fwcore.types.commontypes import override

class _XTaskPrfImpl(ITaskProfile):
    __slots__ = [ '__b' ]

    def __init__(self):
        self.__b = _XTaskPrfBase()
        super().__init__()

    def __str__(self):
        return self.ToString()

    @property
    def isValid(self) -> bool:
        return False if self.__isInvalid else self.__b._isValid

    @property
    def isFrozen(self) -> bool:
        return False if self.__isInvalid else self.__b._isFrozen

    @property
    def isMainTask(self) -> bool:
        return False if self.__isInvalid else self.__b._isMainTask

    @property
    def isPrivilegedTask(self) -> bool:
        return False if self.__isInvalid else self.__b._isPrivilegedTask

    @isPrivilegedTask.setter
    def isPrivilegedTask(self, bPrivileged_ : bool):
        if self.__isValid:
            self.__b._isPrivilegedTask = bool(bPrivileged_)

    @property
    def isSyncTask(self) -> bool:
        return False if self.__isInvalid else self.__b._isSyncTask

    @isSyncTask.setter
    def isSyncTask(self, bSyncTask_ : bool):
        if self.__isValid:
            self.__b._isSyncTask = bool(bSyncTask_)

    @property
    def aliasName(self) -> str:
        return None if self.__isInvalid else self.__b._aliasName

    @aliasName.setter
    def aliasName(self, aliasName_ : str):
        if self.__isValid:
            self.__b._aliasName = aliasName_

    @property
    def isRunPhaseEnabled(self) -> bool:
        return False if self.__isInvalid else self.__b._isRunPhaseEnabled

    @property
    def isSetupPhaseEnabled(self) -> bool:
        return False if self.__isInvalid else self.__b._isSetupPhaseEnabled

    @isSetupPhaseEnabled.setter
    def isSetupPhaseEnabled(self, bEnableSetup_ : bool):
        if self.__isValid:
            self.__b._isSetupPhaseEnabled = bool(bEnableSetup_)

    @property
    def isTeardownPhaseEnabled(self) -> bool:
        return False if self.__isInvalid else self.__b._isTeardownPhaseEnabled

    @isTeardownPhaseEnabled.setter
    def isTeardownPhaseEnabled(self, bEnableTeardown_ : bool):
        if self.__isValid:
            self.__b._isTeardownPhaseEnabled = bool(bEnableTeardown_)

    @property
    def isInternalQueueEnabled(self) -> bool:
        return False if self.__isInvalid else self.__b._isInternalQueueEnabled

    @property
    def isExternalQueueEnabled(self) -> bool:
        return False if self.__isInvalid else self.__b._isExternalQueueEnabled

    @isExternalQueueEnabled.setter
    def isExternalQueueEnabled(self, bExternalQueue_ : bool):
        if self.__isValid:
            self.__b._isExternalQueueEnabled = bool(bExternalQueue_)

    @property
    def isExternalQueueBlocking(self) -> bool:
        return False if self.__isInvalid else self.__b._isExternalQueueBlocking

    @isExternalQueueBlocking.setter
    def isExternalQueueBlocking(self, bBlockingExtQueue_ : bool):
        if self.__isValid:
            self.__b._isExternalQueueBlocking = bool(bBlockingExtQueue_)

    @staticmethod
    def GetDefaultRunPhaseFrequencyMS() -> int:
        return _XTaskPrfBase._GetDefaultRunPhaseFreqMS()

    @staticmethod
    def GetDefaultRunPhaseMaxProcessingTimeMS() -> int:
        return _XTaskPrfBase._GetDefaultRunPhaseMaxProcTimeMS()

    @property
    def isCyclicRunPhase(self) -> bool:
        return False if self.__isInvalid else not self.__b._isSingleCycleRunPhase

    @property
    def isSingleCycleRunPhase(self) -> bool:
        return False if self.__isInvalid else self.__b._isSingleCycleRunPhase

    @property
    def runPhaseFrequencyMS(self) -> int:
        return 0 if self.__isInvalid else self.__b._runPhaseFrequencyMS

    @runPhaseFrequencyMS.setter
    def runPhaseFrequencyMS(self, runPhaseFreqMS_ : Union[int, float]):
        if self.__isValid:
            self.__b._runPhaseFrequencyMS = runPhaseFreqMS_

    @property
    def runPhaseMaxProcessingTimeMS(self) -> int:
        return 0 if self.__isInvalid else self.__b._runPhaseMaxProcessingTimeMS

    @runPhaseMaxProcessingTimeMS.setter
    def runPhaseMaxProcessingTimeMS(self, runPhaseMaxProcTimeMS_ : Union[int, float]):
        if self.__isValid:
            self.__b._runPhaseMaxProcessingTimeMS = runPhaseMaxProcTimeMS_

    @override
    def ToString(self) -> str:
        return None if self.__isInvalid else self.__b._ToString()

    @override
    def CloneProfile(self):
        return None if self.__isInvalid else self.__b._Clone()

    @override
    def _AssignProfile(self, rhs_):
        return None if self.__isInvalid else self.__b._AssignProfile(rhs_)

    def _Freeze(self):
        if self.__isValid:
            self.__b._Freeze()

    def _CheckFreezeState(self) -> bool:
        return False if self.__isInvalid else self.__b._CheckFreezeState()

    def _SetMainXTask(self, bMainXT_ : bool):
        if self.__isValid:
            self.__b._SetMainXTask(bMainXT_)

    def _CleanUp(self):
        if self.__isValid:
            self.__b._CleanUp()

    @property
    def __isValid(self) -> bool:
        return self.__b is not None

    @property
    def __isInvalid(self) -> bool:
        return self.__b is None
