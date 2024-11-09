# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwadmindefs.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from enum   import IntFlag
from enum   import unique
from typing import Union as _PyUnion


class _FwAdapterConfig:

    __bLOGIF_ADAPTER_ENABLED                      = None
    __bLOGIF_ADAPTER_LL_DEBUG_ENABLED             = None
    __bLOGIF_DEFUALT_CONFIG_RELEASE_MODE_DISABLED = None
    __bLOGIF_UT_SWITCH_MODE_ENABLED               = None

    @staticmethod
    def _IsRedirectPyLoggingEnabled() -> bool:
        return _FwAdapterConfig.__bLOGIF_ADAPTER_ENABLED == True

    @staticmethod
    def _IsRedirectPyLoggingDebugLogLevelEnabled() -> bool:
        return _FwAdapterConfig.__bLOGIF_ADAPTER_LL_DEBUG_ENABLED == True

    @staticmethod
    def _IsLogIFDefaultConfigReleaseModeDisabled() -> bool:
        return _FwAdapterConfig.__bLOGIF_DEFUALT_CONFIG_RELEASE_MODE_DISABLED == True

    @staticmethod
    def _IsLogIFUTSwitchModeEnabled() -> bool:
        return _FwAdapterConfig.__bLOGIF_UT_SWITCH_MODE_ENABLED == True

    @staticmethod
    def _RedirectPyLogging(bDebugLL_ =False, bLogIFDefaultCfgRelModeDisabled_ =None):
        _FwAdapterConfig.__bLOGIF_ADAPTER_ENABLED = True
        if bDebugLL_:
            _FwAdapterConfig.__bLOGIF_ADAPTER_LL_DEBUG_ENABLED = True
        if bLogIFDefaultCfgRelModeDisabled_ is not None:
            if bLogIFDefaultCfgRelModeDisabled_:
                _FwAdapterConfig.__bLOGIF_DEFUALT_CONFIG_RELEASE_MODE_DISABLED = True

    @staticmethod
    def _EnableLogIFUTSwitchMode():
        _FwAdapterConfig.__bLOGIF_UT_SWITCH_MODE_ENABLED = True


class _FwSubsystemCoding:
    @unique
    class _ESubSysFlag(IntFlag):
        eNone                    = 0x0000
        eSubsysTmrMgr            = (0x0001 <<  1)
        eSubsysMsg               = (0x0001 <<  2)
        eIntQueueSupport         = (0x0001 <<  3)
        eSelfExtMessaging        = (0x0001 <<  4)
        eAutoCreateCluster       = (0x0001 <<  5)
        eAnonymousAddressing     = (0x0001 <<  6)
        eCustomPayloadSerDes     = (0x0001 <<  7)
        eNegativeDispatchFilters = (0x0001 <<  8)
        eMandatorySenderExtQueue = (0x0001 <<  9)

        @property
        def compactName(self) -> str:
            return self.name[1:]

        @staticmethod
        def IsSubsysMsgSet(eSubsysMask_: IntFlag) -> bool:
            return _FwSubsystemCoding._ESubSysFlag.__IsSubsysFlagSet(eSubsysMask_, _FwSubsystemCoding._ESubSysFlag.eSubsysMsg)

        @staticmethod
        def IsIntQueueSupportSet(eSubsysMask_: IntFlag) -> bool:
            return _FwSubsystemCoding._ESubSysFlag.__IsSubsysFlagSet(eSubsysMask_, _FwSubsystemCoding._ESubSysFlag.eIntQueueSupport)

        @staticmethod
        def IsSelfExtMessaging(eSubsysMask_: IntFlag) -> bool:
            return _FwSubsystemCoding._ESubSysFlag.__IsSubsysFlagSet(eSubsysMask_, _FwSubsystemCoding._ESubSysFlag.eSelfExtMessaging)

        @staticmethod
        def IsSubsysTmrMgrSet(eSubsysMask_: IntFlag) -> bool:
            return _FwSubsystemCoding._ESubSysFlag.__IsSubsysFlagSet(eSubsysMask_, [_FwSubsystemCoding._ESubSysFlag.eSubsysMsg, _FwSubsystemCoding._ESubSysFlag.eSubsysTmrMgr])

        @staticmethod
        def IsAutoCreateClusterSet(eSubsysMask_: IntFlag) -> bool:
            return _FwSubsystemCoding._ESubSysFlag.__IsSubsysFlagSet(eSubsysMask_, _FwSubsystemCoding._ESubSysFlag.eAutoCreateCluster)

        @staticmethod
        def IsAnonymousAddressingSet(eSubsysMask_: IntFlag) -> bool:
            return _FwSubsystemCoding._ESubSysFlag.__IsSubsysFlagSet(eSubsysMask_, _FwSubsystemCoding._ESubSysFlag.eAnonymousAddressing)

        @staticmethod
        def IsNegativeDispatchFiltersSet(eSubsysMask_: IntFlag) -> bool:
            return _FwSubsystemCoding._ESubSysFlag.__IsSubsysFlagSet(eSubsysMask_, _FwSubsystemCoding._ESubSysFlag.eNegativeDispatchFilters)

        @staticmethod
        def IsMandatorySenderExtQueueSet(eSubsysMask_: IntFlag) -> bool:
            return _FwSubsystemCoding._ESubSysFlag.__IsSubsysFlagSet(eSubsysMask_, _FwSubsystemCoding._ESubSysFlag.eMandatorySenderExtQueue)

        @staticmethod
        def IsCustomPayloadSerDesSet(eSubsysMask_: IntFlag) -> bool:
            return _FwSubsystemCoding._ESubSysFlag.__IsSubsysFlagSet(eSubsysMask_, _FwSubsystemCoding._ESubSysFlag.eCustomPayloadSerDes)

        @staticmethod
        def _AddBitFlag(eBitMask_: IntFlag, eBitFlags_: _PyUnion[IntFlag, list], bCheckTypeMatch_: bool =True):
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
        def _RemoveBitFlag(eBitMask_: IntFlag, eBitFlags_: _PyUnion[IntFlag, list], bCheckTypeMatch_: bool =True):
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
        def __IsSubsysFlagSet(eSubsysMask_: IntFlag, eBitFlags_: _PyUnion[IntFlag, list]):
            if not isinstance(eSubsysMask_, IntFlag): return False

            _myFlags = eBitFlags_
            if not isinstance(eBitFlags_, list):
                _myFlags = [eBitFlags_]
            for _bf in _myFlags:
                if type(eSubsysMask_) != type(_bf):   return False
                if not isinstance(_bf, IntFlag):      return False
                if (eSubsysMask_ & _bf).value == 0x0: return False
            return True


    __SUBSYSTEM_CONFIG_BM   = _ESubSysFlag.eNone
    __SUBSYSTEM_CONFIG_BM  |= _ESubSysFlag.eSubsysMsg
    __SUBSYSTEM_CONFIG_BM  |= _ESubSysFlag.eAutoCreateCluster
    __SUBSYSTEM_CONFIG_BM  |= _ESubSysFlag.eMandatorySenderExtQueue


    @staticmethod
    def IsSubsystemTimerManagerConfigured():
        return _FwSubsystemCoding._ESubSysFlag.IsSubsysTmrMgrSet(_FwSubsystemCoding.__SUBSYSTEM_CONFIG_BM)

    @staticmethod
    def IsSubsystemMessagingConfigured():
        return _FwSubsystemCoding._ESubSysFlag.IsSubsysMsgSet(_FwSubsystemCoding.__SUBSYSTEM_CONFIG_BM)

    @staticmethod
    def IsInternalQueueSupportEnabled() -> bool:
        res = _FwSubsystemCoding.IsSubsystemMessagingConfigured()
        res = res and _FwSubsystemCoding._ESubSysFlag.IsIntQueueSupportSet(_FwSubsystemCoding.__SUBSYSTEM_CONFIG_BM)
        return res

    @staticmethod
    def IsSelfExternalMessagingEnabled() -> bool:
        res = _FwSubsystemCoding.IsSubsystemMessagingConfigured()
        res = res and _FwSubsystemCoding._ESubSysFlag.IsSelfExtMessaging(_FwSubsystemCoding.__SUBSYSTEM_CONFIG_BM)
        return res

    @staticmethod
    def IsAnonymousAddressingEnabled():
        res = _FwSubsystemCoding.IsSubsystemMessagingConfigured()
        res = res and _FwSubsystemCoding._ESubSysFlag.IsAnonymousAddressingSet(_FwSubsystemCoding.__SUBSYSTEM_CONFIG_BM)
        return res

    @staticmethod
    def IsAutoCreateClusterEnabled() -> bool:
        res = _FwSubsystemCoding.IsSubsystemMessagingConfigured()
        res = res and _FwSubsystemCoding._ESubSysFlag.IsAutoCreateClusterSet(_FwSubsystemCoding.__SUBSYSTEM_CONFIG_BM)
        return res

    @staticmethod
    def IsNegativeDispatchFiltersEnabled():
        res = _FwSubsystemCoding.IsAnonymousAddressingEnabled()
        res = res and _FwSubsystemCoding._ESubSysFlag.IsNegativeDispatchFiltersSet(_FwSubsystemCoding.__SUBSYSTEM_CONFIG_BM)
        return res

    @staticmethod
    def IsCustomPayloadSerDesEnabled():
        res = _FwSubsystemCoding.IsSubsystemMessagingConfigured()
        res = res and _FwSubsystemCoding._ESubSysFlag.IsCustomPayloadSerDesSet(_FwSubsystemCoding.__SUBSYSTEM_CONFIG_BM)
        return res

    @staticmethod
    def IsSenderExternalQueueSupportMandatory():
        res = _FwSubsystemCoding.IsSubsystemMessagingConfigured()
        res = res and _FwSubsystemCoding._ESubSysFlag.IsMandatorySenderExtQueueSet(_FwSubsystemCoding.__SUBSYSTEM_CONFIG_BM)
        return res
