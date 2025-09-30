# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwsubsyscoding.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum   import IntFlag
from enum   import unique
from typing import Union

from .fwrtecfg.fwrteconfig import _FwRteConfig

class _FwSubsysCoding:
    @unique
    class _ESubSysFlag(IntFlag):
        eNone                    = 0x0000
        eAutoCreateCluster       = (0x0001 <<  5)
        eMandatorySenderExtQueue = (0x0001 <<  9)

        @property
        def compactName(self) -> str:
            return self.name[1:]

        @staticmethod
        def IsAutoCreateClusterSet(eSubsysMask_: IntFlag) -> bool:
            return _FwSubsysCoding._ESubSysFlag.__IsSubsysFlagSet(eSubsysMask_, _FwSubsysCoding._ESubSysFlag.eAutoCreateCluster)

        @staticmethod
        def IsMandatorySenderExtQueueSet(eSubsysMask_: IntFlag) -> bool:
            return _FwSubsysCoding._ESubSysFlag.__IsSubsysFlagSet(eSubsysMask_, _FwSubsysCoding._ESubSysFlag.eMandatorySenderExtQueue)

        @staticmethod
        def _AddBitFlag(eBitMask_: IntFlag, eBitFlags_: Union[IntFlag, list], bCheckTypeMatch_: bool =True):
            if not isinstance(eBitMask_, IntFlag): return None

            _myFlags = eBitFlags_
            if not isinstance(eBitFlags_, list):
                _myFlags = [eBitFlags_]
            for bb in _myFlags:
                if not isinstance(bb, IntFlag): return None
                if not bCheckTypeMatch_:
                    pass
                elif type(eBitMask_) != type(bb):
                    return None
                eBitMask_ |= bb
            return eBitMask_

        @staticmethod
        def _RemoveBitFlag(eBitMask_: IntFlag, eBitFlags_: Union[IntFlag, list], bCheckTypeMatch_: bool =True):
            if not isinstance(eBitMask_, IntFlag): return None

            _myFlags = eBitFlags_
            if not isinstance(eBitFlags_, list):
                _myFlags = [eBitFlags_]
            for bb in _myFlags:
                if not isinstance(bb, IntFlag): return None
                if not bCheckTypeMatch_:
                    pass
                elif type(eBitMask_) != type(bb):
                    return None
                eBitMask_ &= ~bb
            return eBitMask_

        @staticmethod
        def __IsSubsysFlagSet(eSubsysMask_: IntFlag, eBitFlags_: Union[IntFlag, list]):
            if not isinstance(eSubsysMask_, IntFlag): return False

            _myFlags = eBitFlags_
            if not isinstance(eBitFlags_, list):
                _myFlags = [eBitFlags_]
            for _bf in _myFlags:
                if type(eSubsysMask_) != type(_bf):   return False
                if not isinstance(_bf, IntFlag):      return False
                if (eSubsysMask_ & _bf).value == 0x0: return False
            return True

    __RTE_CFG = _FwRteConfig._GetInstance()

    __SUBSYSTEM_CONFIG_BM   = _ESubSysFlag.eNone
    __SUBSYSTEM_CONFIG_BM  |= _ESubSysFlag.eAutoCreateCluster

    @staticmethod
    def IsSubsysXMsgEnabled():
        return not _FwSubsysCoding.__RTE_CFG._isSubSystemMessagingDisabled

    @staticmethod
    def IsSubsysXmpEnabled():
        return not _FwSubsysCoding.__RTE_CFG._isSubSystemMultiProcessingDisabled

    @staticmethod
    def IsSubsysXmpXcpTrackingDisabled():
        return _FwSubsysCoding.__RTE_CFG._isExceptionTrackingOfChildProcessesDisabled

    @staticmethod
    def IsSubsysTmrConfigured():
        return False

    @staticmethod
    def IsInternalQueueSupportEnabled() -> bool:
        return False

    @staticmethod
    def IsSelfExternalMessagingEnabled() -> bool:
        return False

    @staticmethod
    def IsAnonymousAddressingEnabled():
        return False

    @staticmethod
    def IsAutoCreateClusterEnabled() -> bool:
        return _FwSubsysCoding._ESubSysFlag.IsAutoCreateClusterSet(_FwSubsysCoding.__SUBSYSTEM_CONFIG_BM)

    @staticmethod
    def IsNegativeDispatchFiltersEnabled():
        return False

    @staticmethod
    def IsCustomPayloadSerDesEnabled():
        return False

    @staticmethod
    def IsSenderExternalQueueSupportMandatory():
        return _FwSubsysCoding.IsSubsysXMsgEnabled() and _FwSubsysCoding._ESubSysFlag.IsMandatorySenderExtQueueSet(_FwSubsysCoding.__SUBSYSTEM_CONFIG_BM)

