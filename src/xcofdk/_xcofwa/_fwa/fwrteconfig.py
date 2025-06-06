# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwrteconfig.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum      import unique
from threading import RLock as _PyRLock
from typing    import List
from typing    import Union

from xcofdk.fwcom.fwdefs            import ERtePolicyID
from xcofdk.fwapi.apiif.ifrteconfig import IRteConfig

from _fw.fwssys.fwcore.logging           import logif
from _fw.fwssys.fwcore.swpfm.sysinfo     import _SystemInfo
from _fw.fwssys.fwcore.types.aobject     import _AbsSlotsObject
from _fw.fwssys.fwcore.types.commontypes import _CommonDefines
from _fw.fwssys.fwcore.types.commontypes import _ERtePolicyBase
from _fw.fwssys.fwcore.types.ebitmask    import _EBitMask
from _fw.fwssys.fwerrh.fwerrorcodes      import _EFwErrorCode

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

@unique
class _EFwRtePolicyID(_ERtePolicyBase):
    bfEnableAutoStopByDefault     = (0x00001 << 31)

    bfBypassExperimentalFTGuard   = (0x00001 << ERtePolicyID.eBypassExperimentalFTGuard.value)

    bfEnableAutoStop              = (0x00001 << ERtePolicyID.eEnableAutoStop.value)
    bfEnableForcedAutoStop        = (0x00001 << ERtePolicyID.eEnableForcedAutoStop.value)
    bfEnableTerminalMode          = (0x00001 << ERtePolicyID.eEnableTerminalMode.value)

    bfDisableSubSysXMsg           = (0x00001 << ERtePolicyID.eDisableSubSystemMessaging.value)
    bfDisableSubSysXMP            = (0x00001 << ERtePolicyID.eDisableSubSystemMultiProcessing.value)
    bfDisableSubSysXMPXcpTracking = (0x00001 << ERtePolicyID.eDisableExceptionTrackingOfChildProcesses.value)

    @staticmethod
    def _FromFwRtePolicyID(policyID_ : ERtePolicyID):
        if not isinstance(policyID_, ERtePolicyID):
            return None
        return _EFwRtePolicyID(0x00001 << policyID_.value)

class _FwRteConfig(_AbsSlotsObject, IRteConfig):
    __slots__ = [ '__l' , '__bm' , '__bF' , '__m' ]

    __sgltn = None

    def __init__(self):
        self.__l  = _PyRLock()
        self.__m  = None
        self.__bF = False
        self.__bm = _EFwRtePolicyID.bfEnableAutoStopByDefault
        _AbsSlotsObject.__init__(self)
        IRteConfig.__init__(self)

        if _FwRteConfig.__sgltn is None:
            _FwRteConfig.__sgltn = self

    def __str__(self):
        return self.ToString()

    @IRteConfig.isValid.getter
    def isValid(self) -> bool:
        return self._isValid

    @IRteConfig.isAutoStopEnabled.getter
    def isAutoStopEnabled(self) -> bool:
        return self._isAutoStopEnabled

    @IRteConfig.isForcedAutoStopEnabled.getter
    def isForcedAutoStopEnabled(self) -> bool:
        return self._isForcedAutoStopEnabled

    @IRteConfig.isTerminalModeEnabled.getter
    def isTerminalModeEnabled(self) -> bool:
        return self._isTerminalModeEnabled

    @IRteConfig.isExperimentalFreeThreadingBypassed.getter
    def isExperimentalFreeThreadingBypassed(self) -> bool:
        return self._isExperimentalFTBypassed

    @IRteConfig.isSubSystemMessagingDisabled.getter
    def isSubSystemMessagingDisabled(self) -> bool:
        return self._isSubSysXMsgDisabled

    @IRteConfig.isSubSystemMultiProcessingDisabled.getter
    def isSubSystemMultiProcessingDisabled(self) -> bool:
        return self._isSubSysXmpDisabled

    @IRteConfig.isExceptionTrackingOfChildProcessesDisabled.getter
    def isExceptionTrackingOfChildProcessesDisabled(self) -> bool:
        return self._isSubSysXmpXcpTrackingDisabled

    @property
    def _isValid(self) -> bool:
        if not self.__IsValid():
            return False
        with self.__l:
            return self.__m is None

    @property
    def _isFrozen(self) -> bool:
        if not self.__IsValid():
            return False
        with self.__l:
            return (self.__m is None) and self.__bF

    @property
    def _isAutoStopEnabled(self) -> bool:
        return self.__IsRtePolicySet(ERtePolicyID.eEnableAutoStop) or self._isAutoStopEnabledByDefault

    @property
    def _isAutoStopEnabledByDefault(self) -> bool:
        return self.__IsRtePolicySet(_EFwRtePolicyID.bfEnableAutoStopByDefault)

    @property
    def _isForcedAutoStopEnabled(self) -> bool:
        return self.__IsRtePolicySet(ERtePolicyID.eEnableForcedAutoStop)

    @property
    def _isTerminalModeEnabled(self) -> bool:
        return self.__IsRtePolicySet(ERtePolicyID.eEnableTerminalMode)

    @property
    def _isExperimentalFTBypassed(self) -> bool:
        return self.__IsRtePolicySet(ERtePolicyID.eBypassExperimentalFTGuard)

    @property
    def _isSubSysXMsgDisabled(self) -> bool:
        return self.__IsRtePolicySet(ERtePolicyID.eDisableSubSystemMessaging)

    @property
    def _isSubSysXmpDisabled(self) -> bool:
        return self.__IsRtePolicySet(ERtePolicyID.eDisableSubSystemMultiProcessing)

    @property
    def _isSubSysXmpXcpTrackingDisabled(self) -> bool:
        return self.__IsRtePolicySet(ERtePolicyID.eDisableExceptionTrackingOfChildProcesses)

    @staticmethod
    def _GetInstance(bFreeze_ =False):
        res = _FwRteConfig.__sgltn
        if res is None:
            res = _FwRteConfig()
        if bFreeze_ and not res._isFrozen:
            res.__bF = True
        return res

    @staticmethod
    def _ConfigureRtePolicy(rtePolicy_ : Union[ERtePolicyID, List[ERtePolicyID]]) -> IRteConfig:
        res = _FwRteConfig._GetInstance()
        if res._isFrozen:
            if isinstance(rtePolicy_, ERtePolicyID) or (isinstance(rtePolicy_, list) and len(rtePolicy_)):
                logif._XLogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteConfig_TID_001))
            return res

        with res.__l:
            _bm = res.__bm

            _bBypassXFT = None
            _bEnableTM  = None
            _bEnableAS  = None
            _bEnableFAS = None

            if rtePolicy_ is None:
                rtePolicy_ = []
            elif not isinstance(rtePolicy_, list):
                rtePolicy_ = [rtePolicy_]

            for _pp in rtePolicy_:
                if not isinstance(_pp, ERtePolicyID):
                    res.__m = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteConfig_TID_005).format(str(_pp))
                    logif._XLogErrorEC(_EFwErrorCode.UE_00212, res.__m)
                    return res

                if _pp == ERtePolicyID.eEnableAutoStop:
                    _bEnableAS = True
                elif _pp == ERtePolicyID.eEnableForcedAutoStop:
                    _bEnableFAS = True
                elif _pp == ERtePolicyID.eEnableTerminalMode:
                    _bEnableTM = True
                elif _pp == ERtePolicyID.eBypassExperimentalFTGuard:
                    _bBypassXFT = True
                elif _pp == ERtePolicyID.eDisableSubSystemMessaging:
                    pass
                elif _pp == ERtePolicyID.eDisableSubSystemMultiProcessing:
                    pass
                elif _pp == ERtePolicyID.eDisableExceptionTrackingOfChildProcesses:
                    pass
                else:
                    res.__m = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteConfig_TID_006).format(str(_pp))
                    logif._XLogErrorEC(_EFwErrorCode.UE_00213, res.__m)
                    return res

                _bm = _EBitMask.AddEnumBitFlag(_bm, _EFwRtePolicyID._FromFwRtePolicyID(_pp))

            if _EBitMask.IsEnumBitFlagSet(_bm, _EFwRtePolicyID.bfDisableSubSysXMP):
                if not _EBitMask.IsEnumBitFlagSet(_bm, _EFwRtePolicyID.bfDisableSubSysXMPXcpTracking):
                    _bm = _EBitMask.AddEnumBitFlag(_bm, _EFwRtePolicyID.bfDisableSubSysXMPXcpTracking)

            if _bBypassXFT is not None:
                if _bBypassXFT and not _SystemInfo._IsFTPyVersionSupported():
                    _pp = _EFwRtePolicyID._FromFwRtePolicyID(ERtePolicyID.eBypassExperimentalFTGuard)
                    _bm = _EBitMask.RemoveEnumBitFlag(_bm, _pp)
                    _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteConfig_TID_003).format(_SystemInfo._GetPythonVer())
                    logif._XLogWarning(_msg)

            if _bEnableAS is None:
                _bEnableAS = _EBitMask.IsEnumBitFlagSet(_bm, _EFwRtePolicyID.bfEnableAutoStop)
            if _bEnableFAS is None:
                _bEnableFAS = _EBitMask.IsEnumBitFlagSet(_bm, _EFwRtePolicyID.bfEnableForcedAutoStop)
            if _bEnableTM is None:
                _bEnableTM = _EBitMask.IsEnumBitFlagSet(_bm, _EFwRtePolicyID.bfEnableTerminalMode)

            if _bEnableAS or _bEnableFAS or _bEnableTM:
                if _bEnableAS and _bEnableFAS:
                    res.__m = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteConfig_TID_007)
                    logif._XLogErrorEC(_EFwErrorCode.UE_00214, res.__m)
                    return res

                if _bEnableAS and _EBitMask.IsEnumBitFlagSet(_bm, _EFwRtePolicyID.bfEnableForcedAutoStop):
                    res.__m = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteConfig_TID_008)
                    logif._XLogErrorEC(_EFwErrorCode.UE_00215, res.__m)
                    return res

                if _bEnableFAS and _EBitMask.IsEnumBitFlagSet(_bm, _EFwRtePolicyID.bfEnableAutoStop):
                    res.__m = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteConfig_TID_009)
                    logif._XLogErrorEC(_EFwErrorCode.UE_00216, res.__m)
                    return res

                if (_bEnableAS or _bEnableFAS) and _bEnableTM:
                    res.__m = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteConfig_TID_004)
                    logif._XLogErrorEC(_EFwErrorCode.UE_00211, res.__m)
                    return res

                if _EBitMask.IsEnumBitFlagSet(_bm, _EFwRtePolicyID.bfEnableAutoStopByDefault):
                    _bm = _EBitMask.RemoveEnumBitFlag(_bm, _EFwRtePolicyID.bfEnableAutoStopByDefault)

            res.__m  = None
            res.__bm = _bm

        return res

    def _ToString(self):
        if not self.__IsValid():
            return None

        with self.__l:
            _txtAS = str(self._isAutoStopEnabled)
            if self._isAutoStopEnabledByDefault:
                _txtAS += _CommonDefines._CHAR_SIGN_SPACE + _FwTDbEngine.GetText(_EFwTextID.eFwRteConfig_ToString_07)

            _FMT = _FwTDbEngine.GetText(_EFwTextID.eFwRteConfig_ToString_11)
            res  = _FwTDbEngine.GetText(_EFwTextID.eFwRteConfig_ToString_01)
            res += _FMT.format(_FwTDbEngine.GetText(_EFwTextID.eFwRteConfig_ToString_02) , _txtAS)
            res += _FMT.format(_FwTDbEngine.GetText(_EFwTextID.eFwRteConfig_ToString_06) , str(self._isForcedAutoStopEnabled))
            res += _FMT.format(_FwTDbEngine.GetText(_EFwTextID.eFwRteConfig_ToString_03) , str(self._isTerminalModeEnabled))
            res += _FMT.format(_FwTDbEngine.GetText(_EFwTextID.eFwRteConfig_ToString_04) , str(self._isExperimentalFTBypassed))
            res += _FMT.format(_FwTDbEngine.GetText(_EFwTextID.eFwRteConfig_ToString_08) , str(self._isSubSysXMsgDisabled))
            res += _FMT.format(_FwTDbEngine.GetText(_EFwTextID.eFwRteConfig_ToString_09) , str(self._isSubSysXmpDisabled))
            res += _FMT.format(_FwTDbEngine.GetText(_EFwTextID.eFwRteConfig_ToString_10) , str(self._isSubSysXmpXcpTrackingDisabled))
            if self.__m is not None:
                res += _FwTDbEngine.GetText(_EFwTextID.eFwRteConfig_ToString_05).format(self.__m)
            res += _CommonDefines._CHAR_SIGN_NEWLINE
        return res

    def _CleanUp(self):
        if _FwRteConfig.__sgltn is not None:
            _FwRteConfig.__sgltn = None
        self.__l  = None
        self.__m  = None
        self.__bF = None
        self.__bm = None

    def __IsValid(self) -> bool:
        return self.__bm is not None

    def __IsRtePolicySet(self, rtePolicyID_ : Union[ERtePolicyID, _EFwRtePolicyID]):
        if not self.__IsValid():
            return False

        with self.__l:
            res = isinstance(rtePolicyID_, _EFwRtePolicyID)
            if (not res) and isinstance(rtePolicyID_, ERtePolicyID):
                res = True
                rtePolicyID_ = _EFwRtePolicyID._FromFwRtePolicyID(rtePolicyID_)
            res = res and _EBitMask.IsEnumBitFlagSet(self.__bm, rtePolicyID_)
        return res
