# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xtaskprfbase.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum   import unique
from enum   import IntFlag
from typing import Union

from xcofdk.fwapi.xmt import ITaskProfile

from _fw.fwssys.assys                    import fwsubsysshare as _ssshare
from _fw.fwssys.fwcore.logging           import logif
from _fw.fwssys.fwcore.ipc.tsk.taskutil  import _TaskUtil
from _fw.fwssys.fwcore.types.ebitmask    import _EBitMask
from _fw.fwssys.fwerrh.fwerrorcodes      import _EFwErrorCode

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _XTaskPrfBase:
    @unique
    class _ETaskPrfFlag(IntFlag):
        bfNone             = 0x0000
        bfFrozen           = (0x0001 <<  0)
        bfDFreq            = (0x0001 <<  1)
        bfMainXT           = (0x0001 <<  2)
        bfSyncTask         = (0x0001 <<  3)
        bfRunPhase         = (0x0001 <<  4)
        bfIntqueue         = (0x0001 <<  5)
        bfExtQueue         = (0x0001 <<  6)
        bfSetupPhase       = (0x0001 <<  7)
        bfPrivileged       = (0x0001 <<  8)
        bfTeardownPhase    = (0x0001 <<  9)
        bfBlockingExtQueue = (0x0001 << 10)

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

    __slots__ = [ '__bm' , '__an' , '__mpt' , '__f' ]

    def __init__(self):
        self.__bm  = _XTaskPrfBase._ETaskPrfFlag.bfNone
        self.__bm |= _XTaskPrfBase._ETaskPrfFlag.bfDFreq
        self.__bm |= _XTaskPrfBase._ETaskPrfFlag.bfRunPhase

        self.__f   = _XTaskPrfBase.__DEFAULT_CYCLIC_RPTS_MS
        self.__an  = None
        self.__mpt = _XTaskPrfBase.__DEFAULT_CYCLIC_MPTS_MS

    def __str__(self):
        return self._ToString()

    @property
    def _isValid(self) -> bool:
        return not self.__isInvalid

    @property
    def _isFrozen(self) -> bool:
        return False if self.__isInvalid else _XTaskPrfBase._ETaskPrfFlag.IsTaskPrfFlagSet(self.__bm, _XTaskPrfBase._ETaskPrfFlag.bfFrozen)

    @property
    def _isMainTask(self) -> bool:
        return self.__isValid and _XTaskPrfBase._ETaskPrfFlag.IsTaskPrfFlagSet(self.__bm, _XTaskPrfBase._ETaskPrfFlag.bfMainXT)

    @property
    def _isPrivilegedTask(self) -> bool:
        return self.__isValid and _XTaskPrfBase._ETaskPrfFlag.IsTaskPrfFlagSet(self.__bm, _XTaskPrfBase._ETaskPrfFlag.bfPrivileged)

    @_isPrivilegedTask.setter
    def _isPrivilegedTask(self, bPrivileged_ : bool):
        if not self._CheckFreezeState():
            return
        if bPrivileged_:
            self.__bm = _XTaskPrfBase._ETaskPrfFlag.AddTaskPrfFlag(self.__bm, _XTaskPrfBase._ETaskPrfFlag.bfPrivileged)
        else:
            self.__bm = _XTaskPrfBase._ETaskPrfFlag.RemoveTaskPrfFlag(self.__bm, _XTaskPrfBase._ETaskPrfFlag.bfPrivileged)

    @property
    def _isSyncTask(self) -> bool:
        return self.__isValid and _XTaskPrfBase._ETaskPrfFlag.IsTaskPrfFlagSet(self.__bm, _XTaskPrfBase._ETaskPrfFlag.bfSyncTask)

    @_isSyncTask.setter
    def _isSyncTask(self, bSyncTask_ : bool):
        if not self._CheckFreezeState():
            return
        if bSyncTask_:
            if self._isExternalQueueBlocking:
                logif._XLogErrorEC(_EFwErrorCode.UE_00179, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskPrfBase_TID_012))
                self._CleanUp()
                return

            self.__bm = _XTaskPrfBase._ETaskPrfFlag.AddTaskPrfFlag(self.__bm, _XTaskPrfBase._ETaskPrfFlag.bfSyncTask)
            if self.__isDefaultRunFreq:
                self.__f  = 0
                self.__bm = _XTaskPrfBase._ETaskPrfFlag.RemoveTaskPrfFlag(self.__bm, _XTaskPrfBase._ETaskPrfFlag.bfDFreq)
        else:
            self.__bm = _XTaskPrfBase._ETaskPrfFlag.RemoveTaskPrfFlag(self.__bm, _XTaskPrfBase._ETaskPrfFlag.bfSyncTask)

    @property
    def _aliasName(self) -> str:
        return self.__an

    @_aliasName.setter
    def _aliasName(self, aliasName_ : str):
        if not self._CheckFreezeState():
            return
        if not _TaskUtil.IsValidAliasName(aliasName_):
            logif._XLogErrorEC(_EFwErrorCode.UE_00267, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskPrfBase_TID_013).format(str(aliasName_)))
            self._CleanUp()
            return
        self.__an = str(aliasName_)

    @property
    def _isRunPhaseEnabled(self) -> bool:
        return self._isValid and _XTaskPrfBase._ETaskPrfFlag.IsTaskPrfFlagSet(self.__bm, _XTaskPrfBase._ETaskPrfFlag.bfRunPhase)

    @_isRunPhaseEnabled.setter
    def _isRunPhaseEnabled(self, bEnableRun_ : bool):
        if not self._CheckFreezeState():
            return
        if bEnableRun_:
            self.__bm = _XTaskPrfBase._ETaskPrfFlag.AddTaskPrfFlag(self.__bm, _XTaskPrfBase._ETaskPrfFlag.bfRunPhase)
        else:
            self.__bm = _XTaskPrfBase._ETaskPrfFlag.RemoveTaskPrfFlag(self.__bm, _XTaskPrfBase._ETaskPrfFlag.bfRunPhase)

    @property
    def _isSetupPhaseEnabled(self) -> bool:
        return self.__isValid and _XTaskPrfBase._ETaskPrfFlag.IsTaskPrfFlagSet(self.__bm, _XTaskPrfBase._ETaskPrfFlag.bfSetupPhase)

    @_isSetupPhaseEnabled.setter
    def _isSetupPhaseEnabled(self, bEnableSetup_ : bool):
        if not self._CheckFreezeState():
            return
        if bEnableSetup_:
            self.__bm = _XTaskPrfBase._ETaskPrfFlag.AddTaskPrfFlag(self.__bm, _XTaskPrfBase._ETaskPrfFlag.bfSetupPhase)
        else:
            self.__bm = _XTaskPrfBase._ETaskPrfFlag.RemoveTaskPrfFlag(self.__bm, _XTaskPrfBase._ETaskPrfFlag.bfSetupPhase)

    @property
    def _isTeardownPhaseEnabled(self) -> bool:
        return self.__isValid and _XTaskPrfBase._ETaskPrfFlag.IsTaskPrfFlagSet(self.__bm, _XTaskPrfBase._ETaskPrfFlag.bfTeardownPhase)

    @_isTeardownPhaseEnabled.setter
    def _isTeardownPhaseEnabled(self, bEnableTeardown_ : bool):
        if not self._CheckFreezeState():
            return
        if bEnableTeardown_:
            self.__bm = _XTaskPrfBase._ETaskPrfFlag.AddTaskPrfFlag(self.__bm, _XTaskPrfBase._ETaskPrfFlag.bfTeardownPhase)
        else:
            self.__bm = _XTaskPrfBase._ETaskPrfFlag.RemoveTaskPrfFlag(self.__bm, _XTaskPrfBase._ETaskPrfFlag.bfTeardownPhase)

    @property
    def _isInternalQueueEnabled(self) -> bool:
        return False

    @property
    def _isExternalQueueEnabled(self) -> bool:
        return self.__isValid and _XTaskPrfBase._ETaskPrfFlag.IsTaskPrfFlagSet(self.__bm, _XTaskPrfBase._ETaskPrfFlag.bfExtQueue)

    @_isExternalQueueEnabled.setter
    def _isExternalQueueEnabled(self, bExternalQueue_ : bool):
        if not self._CheckFreezeState():
            return
        if _ssshare._WarnOnDisabledSubsysMsg(annexID_=_EFwTextID.eMisc_Shared_Disabled_Subsys_Msg):
            self._CleanUp()
            return
        if bExternalQueue_:
            self.__bm = _XTaskPrfBase._ETaskPrfFlag.AddTaskPrfFlag(self.__bm, _XTaskPrfBase._ETaskPrfFlag.bfExtQueue)
        else:
            self.__bm = _XTaskPrfBase._ETaskPrfFlag.RemoveTaskPrfFlag(self.__bm, _XTaskPrfBase._ETaskPrfFlag.bfExtQueue)
            if self._isExternalQueueBlocking:
                self._isRunPhaseEnabled       = True
                self._isExternalQueueBlocking = False

    @property
    def _isExternalQueueBlocking(self) -> bool:
        return self.__isValid and _XTaskPrfBase._ETaskPrfFlag.IsTaskPrfFlagSet(self.__bm, _XTaskPrfBase._ETaskPrfFlag.bfBlockingExtQueue)

    @_isExternalQueueBlocking.setter
    def _isExternalQueueBlocking(self, bBlockingExtQueue_ : bool):
        if not self._CheckFreezeState():
            return
        if _ssshare._WarnOnDisabledSubsysMsg(annexID_=_EFwTextID.eMisc_Shared_Disabled_Subsys_Msg):
            self._CleanUp()
            return
        if bBlockingExtQueue_:
            if self._isSyncTask:
                logif._XLogErrorEC(_EFwErrorCode.UE_00179, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskPrfBase_TID_012))
                self._CleanUp()
                return

            self.__bm = _XTaskPrfBase._ETaskPrfFlag.AddTaskPrfFlag(self.__bm, _XTaskPrfBase._ETaskPrfFlag.bfBlockingExtQueue)
            self._isRunPhaseEnabled = False
            if not self._isExternalQueueEnabled:
                self._isExternalQueueEnabled = True
            if self.__f == 0:
                self.__f = _XTaskPrfBase.__DEFAULT_CYCLIC_RPTS_MS
        else:
            self.__bm = _XTaskPrfBase._ETaskPrfFlag.RemoveTaskPrfFlag(self.__bm, _XTaskPrfBase._ETaskPrfFlag.bfBlockingExtQueue)
            self._isRunPhaseEnabled = True

    @property
    def _isSingleCycleRunPhase(self) -> bool:
        return self.__isValid and (self.__f == 0)

    @property
    def _runPhaseFrequencyMS(self) -> int:
        return -1 if self.__isInvalid else self.__f

    @_runPhaseFrequencyMS.setter
    def _runPhaseFrequencyMS(self, runPhaseFreqMS_ : Union[int, float]):
        if not self._CheckFreezeState():
            return
        if isinstance(runPhaseFreqMS_, float):
            runPhaseFreqMS_ = int(1000*runPhaseFreqMS_)

        if not isinstance(runPhaseFreqMS_, int):
            logif._XLogErrorEC(_EFwErrorCode.UE_00181, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskPrfBase_TID_006).format(type(runPhaseFreqMS_).__name__))
            self._CleanUp()
            return
        if runPhaseFreqMS_ < 0:
            logif._XLogErrorEC(_EFwErrorCode.UE_00182, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskPrfBase_TID_007).format(runPhaseFreqMS_))
            self._CleanUp()
            return
        if (runPhaseFreqMS_ == 0) and self._isExternalQueueBlocking:
            return
        self.__f  = runPhaseFreqMS_
        self.__bm = _XTaskPrfBase._ETaskPrfFlag.RemoveTaskPrfFlag(self.__bm, _XTaskPrfBase._ETaskPrfFlag.bfDFreq)

    @property
    def _runPhaseMaxProcessingTimeMS(self) -> int:
        return self.__mpt

    @_runPhaseMaxProcessingTimeMS.setter
    def _runPhaseMaxProcessingTimeMS(self, runPhaseMPTMS_ : Union[int, float]):
        if not self._CheckFreezeState():
            return
        if isinstance(runPhaseMPTMS_, float):
            runPhaseMPTMS_ = int(1000*runPhaseMPTMS_)

        if not isinstance(runPhaseMPTMS_, int):
            logif._XLogErrorEC(_EFwErrorCode.UE_00183, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskPrfBase_TID_004).format(type(runPhaseMPTMS_).__name__))
            self._CleanUp()
            return
        if runPhaseMPTMS_ < 1:
            logif._XLogErrorEC(_EFwErrorCode.UE_00184, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskPrfBase_TID_005).format(runPhaseMPTMS_))
            self._CleanUp()
            return
        self.__mpt = runPhaseMPTMS_

    @staticmethod
    def _GetDefaultRunPhaseFreqMS():
        return _XTaskPrfBase.__DEFAULT_CYCLIC_RPTS_MS

    @staticmethod
    def _GetDefaultRunPhaseMaxProcTimeMS():
        return _XTaskPrfBase.__DEFAULT_CYCLIC_MPTS_MS

    def _Clone(self):
        res = _XTaskPrfBase()
        res.__Assign(self)
        return res

    def _AssignProfile(self, rhs_):
        if not self._CheckFreezeState():
            return None
        if not isinstance(rhs_, ITaskProfile):
            return None
        if not rhs_.isValid:
            return None

        self._isSyncTask             = rhs_.isSyncTask
        self._isPrivilegedTask       = rhs_.isPrivilegedTask
        self._isRunPhaseEnabled      = rhs_.isRunPhaseEnabled
        self._isSetupPhaseEnabled    = rhs_.isSetupPhaseEnabled
        self._isTeardownPhaseEnabled = rhs_.isTeardownPhaseEnabled

        if not _ssshare._IsSubsysMsgDisabled():
            self._isExternalQueueEnabled  = rhs_.isExternalQueueEnabled
            self._isExternalQueueBlocking = rhs_.isExternalQueueBlocking
        self._aliasName                   = str(rhs_.aliasName)
        self._runPhaseFrequencyMS         = rhs_.runPhaseFrequencyMS
        self._runPhaseMaxProcessingTimeMS = rhs_.runPhaseMaxProcessingTimeMS

        if rhs_.runPhaseFrequencyMS != _XTaskPrfBase._GetDefaultRunPhaseFreqMS():
            self.__bm = _XTaskPrfBase._ETaskPrfFlag.RemoveTaskPrfFlag(self.__bm, _XTaskPrfBase._ETaskPrfFlag.bfDFreq)

        if rhs_.isFrozen and not self._isFrozen:
            self._Freeze(bCheckMM_=False)
        return self

    def _Freeze(self, bCheckMM_ =True):
        if self._isFrozen:
            return

        if bCheckMM_:
            _bRun = self._isRunPhaseEnabled
            _bXQ  = self._isExternalQueueEnabled
            _bBXQ = self._isExternalQueueBlocking

            if not _bRun:
                _bMisMatch = not (_bXQ and _bBXQ)
            else:
                _bMisMatch = _bBXQ

            if _bMisMatch:
                logif._XLogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskPrfBase_TID_010).format(str(_bRun), str(_bXQ), str(_bBXQ)))

        self.__bm = _XTaskPrfBase._ETaskPrfFlag.AddTaskPrfFlag(self.__bm, _XTaskPrfBase._ETaskPrfFlag.bfFrozen)

    def _ToString(self) -> str:
        _fmt = _FwTDbEngine.GetText(_EFwTextID.eXTaskPrfBase_ToString_15)
        res  = _FwTDbEngine.GetText(_EFwTextID.eXTaskPrfBase_ToString_01)
        res += _fmt.format(_FwTDbEngine.GetText(_EFwTextID.eXTaskPrfBase_ToString_02), str(self._aliasName))
        res += _fmt.format(_FwTDbEngine.GetText(_EFwTextID.eXTaskPrfBase_ToString_03), str(self._isMainTask))
        res += _fmt.format(_FwTDbEngine.GetText(_EFwTextID.eXTaskPrfBase_ToString_11), str(self._isSyncTask))
        res += _fmt.format(_FwTDbEngine.GetText(_EFwTextID.eXTaskPrfBase_ToString_05), str(self._isPrivilegedTask))
        res += _fmt.format(_FwTDbEngine.GetText(_EFwTextID.eXTaskPrfBase_ToString_14), str(self._isRunPhaseEnabled))
        res += _fmt.format(_FwTDbEngine.GetText(_EFwTextID.eXTaskPrfBase_ToString_06), str(self._isSetupPhaseEnabled))
        res += _fmt.format(_FwTDbEngine.GetText(_EFwTextID.eXTaskPrfBase_ToString_07), str(self._isTeardownPhaseEnabled))
        res += _fmt.format(_FwTDbEngine.GetText(_EFwTextID.eXTaskPrfBase_ToString_04), str(not self._isSingleCycleRunPhase))
        if not _ssshare._IsSubsysMsgDisabled():
            res += _fmt.format(_FwTDbEngine.GetText(_EFwTextID.eXTaskPrfBase_ToString_08), str(self._isInternalQueueEnabled))
            res += _fmt.format(_FwTDbEngine.GetText(_EFwTextID.eXTaskPrfBase_ToString_09), str(self._isExternalQueueEnabled))
            res += _fmt.format(_FwTDbEngine.GetText(_EFwTextID.eXTaskPrfBase_ToString_10), str(self._isExternalQueueBlocking))
        res += _fmt.format(_FwTDbEngine.GetText(_EFwTextID.eXTaskPrfBase_ToString_12), str(self._runPhaseFrequencyMS))
        res += _fmt.format(_FwTDbEngine.GetText(_EFwTextID.eXTaskPrfBase_ToString_13), str(self._runPhaseMaxProcessingTimeMS))
        return res

    def _SetMainXTask(self, bMainXT_ : bool):
        if not self._CheckFreezeState():
            return
        self.__bm = _XTaskPrfBase._ETaskPrfFlag.AddTaskPrfFlag(self.__bm, _XTaskPrfBase._ETaskPrfFlag.bfMainXT)

    def _CleanUp(self):
        self.__f   = None
        self.__an  = None
        self.__bm  = None
        self.__mpt = None

    def _CheckFreezeState(self) -> bool:
        if self.__isInvalid:
            return False
        if self._isFrozen:
            logif._XLogErrorEC(_EFwErrorCode.UE_00185, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskPrfBase_TID_009))
            return False
        return True

    @property
    def __isValid(self) -> bool:
        return self.__bm is not None

    @property
    def __isInvalid(self) -> bool:
        return self.__bm is None

    @property
    def __isDefaultRunFreq(self):
        return False if self.__isInvalid else _XTaskPrfBase._ETaskPrfFlag.IsTaskPrfFlagSet(self.__bm, _XTaskPrfBase._ETaskPrfFlag.bfDFreq)

    def __Assign(self, rhs_):
        if not self._CheckFreezeState():
            return None
        if not isinstance(rhs_, _XTaskPrfBase):
            return None
        if not rhs_._isValid:
            return None

        self._isSyncTask             = rhs_._isSyncTask
        self._isPrivilegedTask       = rhs_._isPrivilegedTask
        self._isRunPhaseEnabled      = rhs_._isRunPhaseEnabled
        self._isSetupPhaseEnabled    = rhs_._isSetupPhaseEnabled
        self._isTeardownPhaseEnabled = rhs_._isTeardownPhaseEnabled

        if not _ssshare._IsSubsysMsgDisabled():
            self._isExternalQueueEnabled  = rhs_._isExternalQueueEnabled
            self._isExternalQueueBlocking = rhs_._isExternalQueueBlocking
        self._aliasName                   = str(rhs_._aliasName)
        self._runPhaseFrequencyMS         = rhs_._runPhaseFrequencyMS
        self._runPhaseMaxProcessingTimeMS = rhs_._runPhaseMaxProcessingTimeMS

        if self.__isDefaultRunFreq != rhs_.__isDefaultRunFreq:
            if rhs_.__isDefaultRunFreq:
                self.__bm = _XTaskPrfBase._ETaskPrfFlag.AddTaskPrfFlag(self.__bm, _XTaskPrfBase._ETaskPrfFlag.bfDFreq)
            else:
                self.__bm = _XTaskPrfBase._ETaskPrfFlag.RemoveTaskPrfFlag(self.__bm, _XTaskPrfBase._ETaskPrfFlag.bfDFreq)

        if rhs_._isFrozen and not self._isFrozen:
            self._Freeze(bCheckMM_=False)
        return self

