# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xmputilimpl.py.py
#
# Copyright(c) 2024 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from xcofdk.fwcom         import fwutil
from xcofdk.fwcom.xmpdefs import EProcessStartMethodID

from xcofdk._xcofw.fw.fwssys.fwcore.logging           import logif
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes import _CommonDefines

from xcofdk._xcofw.fw.fwssys.fwmp.fwrte.mpstartpolicy import _EProcessStartMethodID
from xcofdk._xcofw.fw.fwssys.fwmp.fwrte.mpstartpolicy import _MPStartPolicy

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine


class _XMPUtilImpl:
    __slots__ = []

    __VALID_START_METHODS_NAME_LIST = None

    def __init__(self):
        pass


    @staticmethod
    def _MPIsCurrentStartMethod(smID_ : EProcessStartMethodID) -> bool:
        if not _XMPUtilImpl.__IsFWAvailable():
            return False
        if not isinstance(smID_, EProcessStartMethodID):
            logif._LogError(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XMPUtilImpl_TextID_001).format(type(smID_).__name__, EProcessStartMethodID.__name__))
            return False
        return _MPStartPolicy._IsCurrentStartMethod(_EProcessStartMethodID(smID_.value))

    @staticmethod
    def _MPIsValidStartMethodName(smName_ : str) -> bool:
        _lstValid = _XMPUtilImpl._MPGetDefinedStartMethdsNameList()

        if not isinstance(smName_, str):
            return False
        return smName_ in _lstValid

    @staticmethod
    def _MPGetSystemDefaultStartMethodID() -> EProcessStartMethodID:
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
        if _curSM is None:
            return _CommonDefines._CHAR_SIGN_DASH

        res = _curSM.compactName
        if _curSM.isSystemDefault:
            res += _FwTDbEngine.GetText(_EFwTextID.eXMPUtilImpl_ToString_01).format(_XMPUtilImpl._MPGetSystemDefaultStartMethodID().name.lower())
        return res

    @staticmethod
    def _MPMapStartMethodToID(smName_ : str) -> EProcessStartMethodID:
        if smName_ is None:
            smName_ = EProcessStartMethodID.SystemDefault.name.lower()
        res = _MPStartPolicy._MapStartMethodToID(smName_)
        if (res is None) or (res.value < 0):
            pass
        else:
            res = EProcessStartMethodID(res.value)
        return res

    @staticmethod
    def _MPCurrentStartMethodAsString() -> str:
        if not _XMPUtilImpl.__IsFWAvailable():
            return None
        return _MPStartPolicy._ToString()

    @staticmethod
    def _MPGetDefinedStartMethdsNameList() -> list:
        return _MPStartPolicy._GetDefinedStartMethdsNameList()


    @staticmethod
    def __IsFWAvailable():
        res = fwutil.IsFwAvailable()
        if not res:
            logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XMPUtilImpl_TextID_002))
        return res


