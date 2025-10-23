# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : mpstartpolicy.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

import multiprocessing as _PyMP
from   enum   import IntEnum
from   enum   import unique
from   typing import Union

from xcofdk.fwcom.xmpdefs import EProcessStartMethodID

from _fw.fwssys.fwcore.logging       import logif
from _fw.fwssys.fwcore.swpfm.sysinfo import _SystemInfo

from _fw.fwssys.fwerrh.fwerrorcodes import _EFwErrorCode

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

@unique
class _EProcessStartMethodID(IntEnum):
    eSystemDefault = EProcessStartMethodID.SystemDefault.value
    eSpawn         = EProcessStartMethodID.Spawn.value
    eFork          = EProcessStartMethodID.Fork.value
    eForkServer    = EProcessStartMethodID.ForkServer.value

    @property
    def compactName(self):
        res = self.name[1:]
        res = res.lower()
        return res

    @property
    def isSystemDefault(self):
        return self == _EProcessStartMethodID.eSystemDefault

    @property
    def isSpawn(self):
        return self == _EProcessStartMethodID.eSpawn

    @property
    def isFork(self):
        return self == _EProcessStartMethodID.eFork

    @property
    def isForkServer(self):
        return self == _EProcessStartMethodID.eForkServer

class _MPStartPolicy:
    __slots__ = []

    __KNOWN_START_METHODS_NAME_LIST = [
        _EProcessStartMethodID.eSystemDefault.compactName
      , _EProcessStartMethodID.eSpawn.compactName
      , _EProcessStartMethodID.eFork.compactName
      , _EProcessStartMethodID.eForkServer.compactName
    ]

    __bSETTER_DOES_NEVER_FORCE             = False
    __bGETTER_RETURNS_NONE_IF_SM_NOT_FIXED = True

    __INIT_SM_ID   = None
    __FW_TGT_SM_ID = None

    __curSmID           = None
    __prvSmID           = None
    __fixedSmID         = None
    __bFatalError       = False
    __bSmChangeDetected = False

    def __init__(self):
        pass

    @staticmethod
    def _IsCurrentStartMethod(smID_ : _EProcessStartMethodID) -> bool:
        if not isinstance(smID_, _EProcessStartMethodID):
            logif._LogErrorEC(_EFwErrorCode.UE_00119, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_MPStartPolicy_TID_001).format(type(smID_).__name__, EProcessStartMethodID.__name__))
            return False

        _curSM = _MPStartPolicy.__FetchCurrentStartMethodID()
        if _curSM is None:
            return False
        if _curSM.isSystemDefault:
            _curSM = _MPStartPolicy._GetSystemDefaultStartMethodID()
        res = (_curSM is not None) and (_curSM == smID_)
        return res

    @staticmethod
    def _IsStartMethodChanged(bErrorLogOnChange_ =True) -> bool:
        _curSM = _MPStartPolicy.__FetchCurrentStartMethodID()
        if (_curSM is None) or _MPStartPolicy.__IsEncounteredFatalError():
            return True
        if _MPStartPolicy.__bSmChangeDetected:
            return True

        _fixedSM = _MPStartPolicy.__fixedSmID

        res = False
        if _fixedSM is not None:
            res = _curSM != _fixedSM
            if res:
                if not _MPStartPolicy.__bSmChangeDetected:
                    _MPStartPolicy.__bSmChangeDetected = True
                    if bErrorLogOnChange_:
                        logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_MPStartPolicy_TID_015).format(_fixedSM.compactName, _curSM.compactName))
        return res

    @staticmethod
    def _GetSystemDefaultStartMethodID() -> _EProcessStartMethodID:
        if _SystemInfo._IsPlatformLinux():
            res = _EProcessStartMethodID.eForkServer if _SystemInfo._IsPyVersionSupportedFTPython() else _EProcessStartMethodID.eFork
        else:
            res = _EProcessStartMethodID.eSpawn
        return res

    @staticmethod
    def _GetDefinedStartMethdsNameList() -> list:
        return [_MPStartPolicy._MapStartMethodToID(_sm).compactName for _sm in _PyMP.get_all_start_methods()]

    @staticmethod
    def _GetCurrentStartMethodID() -> Union[_EProcessStartMethodID, None]:
        res = _MPStartPolicy.__FetchCurrentStartMethodID()
        if (res is not None) and res.isSystemDefault:
            res = _MPStartPolicy._GetSystemDefaultStartMethodID()
        return res

    @staticmethod
    def _MapStartMethodToID(smName_ : str) -> Union[_EProcessStartMethodID, None]:
        if not(isinstance(smName_, str) and (len(smName_.strip())>0)):
            return None

        smName_ = smName_.strip()

        if smName_ not in _MPStartPolicy.__KNOWN_START_METHODS_NAME_LIST:
            logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_MPStartPolicy_TID_008).format(smName_, _MPStartPolicy._ToString()))
            return None

        res = None
        for _n, _m in _EProcessStartMethodID.__members__.items():
            if smName_ == _m.compactName:
                res = _m
                break

        if res is None:
            _MPStartPolicy.__bFatalError = True
            logif._LogFatalEC(_EFwErrorCode.FE_00048, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_MPStartPolicy_TID_009).format(smName_, _MPStartPolicy._ToString()))
        return res

    @staticmethod
    def _ToString():
        if _MPStartPolicy.__IsEncounteredFatalError():
            return None

        _curSM  = _MPStartPolicy.__curSmID
        _prvSM  = _MPStartPolicy.__prvSmID
        _initSM = _MPStartPolicy.__INIT_SM_ID

        _fixedSM = _MPStartPolicy.__fixedSmID
        if _fixedSM is not None:
            _fixedSM = _fixedSM.compactName
        return _FwTDbEngine.GetText(_EFwTextID.eLogMsg_MPStartPolicy_TID_007).format(_SystemInfo._GetPlatform(), _initSM.compactName, _prvSM.compactName, _curSM.compactName, _fixedSM)

    @staticmethod
    def __IsEncounteredFatalError():
        return _MPStartPolicy.__bFatalError

    @staticmethod
    def __GetFwTargetStartMethodID() -> Union[_EProcessStartMethodID, None]:
        res = _MPStartPolicy.__FW_TGT_SM_ID
        if res is None:
            _MPStartPolicy.__FetchCurrentStartMethodID()
            res = _MPStartPolicy.__FW_TGT_SM_ID
        return res

    @staticmethod
    def __FetchCurrentStartMethodID() -> Union[_EProcessStartMethodID, None]:
        if _MPStartPolicy.__IsEncounteredFatalError():
            return None

        _sm = _PyMP.get_start_method(allow_none=_MPStartPolicy.__bGETTER_RETURNS_NONE_IF_SM_NOT_FIXED)
        if _sm is None:
            _sm = _EProcessStartMethodID.eSystemDefault.compactName
        res = _MPStartPolicy._MapStartMethodToID(_sm)

        if (res is None) or _MPStartPolicy.__IsEncounteredFatalError():
            return None

        if _MPStartPolicy.__INIT_SM_ID is None:
            _MPStartPolicy.__curSmID      = res
            _MPStartPolicy.__prvSmID      = res
            _MPStartPolicy.__INIT_SM_ID   = res
            _MPStartPolicy.__FW_TGT_SM_ID = res

        if res != _MPStartPolicy.__curSmID:
            _MPStartPolicy.__prvSmID = _MPStartPolicy.__curSmID
            _MPStartPolicy.__curSmID = res

        if not res.isSystemDefault:
            if _MPStartPolicy.__fixedSmID is None:
                _MPStartPolicy.__fixedSmID = res

        return res

