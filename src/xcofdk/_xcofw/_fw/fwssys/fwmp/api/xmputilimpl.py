# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xmputilimpl.py.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from xcofdk.fwcom.xmpdefs import EProcessStartMethodID

from _fw.fwssys.assys                    import fwsubsysshare as _ssshare
from _fw.fwssys.fwcore.logging           import logif
from _fw.fwssys.fwcore.types.commontypes import _CommonDefines
from _fw.fwssys.fwctrl.fwapibase         import _FwApiBase
from _fw.fwssys.fwmp.fwrte.mpstartpolicy import _EProcessStartMethodID
from _fw.fwssys.fwmp.fwrte.mpstartpolicy import _MPStartPolicy
from _fw.fwssys.fwerrh.fwerrorcodes      import _EFwErrorCode

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _XMPUtilImpl:
    __slots__ = []

    __VALID_START_METHODS_NAME_LIST = None

    def __init__(self):
        pass

    @staticmethod
    def _MPIsCurrentStartMethod(smID_ : EProcessStartMethodID) -> bool:
        if _ssshare._WarnOnDisabledSubsysMP(annexID_=_EFwTextID.eMisc_Shared_Disabled_Subsys_MP):
            return False
        if not _XMPUtilImpl.__IsFWAvailable():
            return False
        if not isinstance(smID_, EProcessStartMethodID):
            logif._LogErrorEC(_EFwErrorCode.UE_00118, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XMPUtilImpl_TID_001).format(type(smID_).__name__, EProcessStartMethodID.__name__))
            return False
        return _MPStartPolicy._IsCurrentStartMethod(_EProcessStartMethodID(smID_.value))

    @staticmethod
    def _MPIsValidStartMethodName(smName_ : str) -> bool:
        if _ssshare._WarnOnDisabledSubsysMP(annexID_=_EFwTextID.eMisc_Shared_Disabled_Subsys_MP):
            return False
        if not isinstance(smName_, str):
            return False
        _lstValid = _XMPUtilImpl._MPGetDefinedStartMethdsNameList()
        return smName_ in _lstValid

    @staticmethod
    def _MPGetSystemDefaultStartMethodID() -> EProcessStartMethodID:
        if _ssshare._WarnOnDisabledSubsysMP(annexID_=_EFwTextID.eMisc_Shared_Disabled_Subsys_MP):
            return None
        return EProcessStartMethodID(_MPStartPolicy._GetSystemDefaultStartMethodID().value)

    @staticmethod
    def _MPGetCurrentStartMethodID() -> EProcessStartMethodID:
        if not _XMPUtilImpl.__IsFWAvailable():
            return None

        res = _MPStartPolicy._GetCurrentStartMethodID()
        if res is None:
            pass
        elif res.value < 0:
            res = None
        else:
            res = EProcessStartMethodID(res.value)
        return res

    @staticmethod
    def _MPGetCurrentStartMethodName() -> str:
        if not _XMPUtilImpl.__IsFWAvailable():
            return None

        _curSM = _MPStartPolicy._GetCurrentStartMethodID()
        return _CommonDefines._CHAR_SIGN_DASH if _curSM is None else _curSM.compactName

    @staticmethod
    def _MPMapStartMethodToID(smName_ : str) -> EProcessStartMethodID:
        if _ssshare._WarnOnDisabledSubsysMP(annexID_=_EFwTextID.eMisc_Shared_Disabled_Subsys_MP):
            return None
        if smName_ is None:
            smName_ = EProcessStartMethodID.SystemDefault.name.lower()
        res = _MPStartPolicy._MapStartMethodToID(smName_)
        if not ((res is None) or (res.value < 0)):
            res = EProcessStartMethodID(res.value)
        return res

    @staticmethod
    def _MPCurrentStartMethodAsString() -> str:
        if not _XMPUtilImpl.__IsFWAvailable():
            return None
        return _MPStartPolicy._ToString()

    @staticmethod
    def _MPGetDefinedStartMethdsNameList() -> list:
        if not _XMPUtilImpl.__IsFWAvailable():
            return None
        return _MPStartPolicy._GetDefinedStartMethdsNameList()

    @staticmethod
    def __IsFWAvailable():
        if _ssshare._WarnOnDisabledSubsysMP(annexID_=_EFwTextID.eMisc_Shared_Disabled_Subsys_MP):
            return False
        res = _FwApiBase.FwApiIsFwAvailable()
        if not res:
            logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XMPUtilImpl_TID_002))
        return res

