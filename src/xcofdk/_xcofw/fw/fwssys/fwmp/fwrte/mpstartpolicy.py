# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : mpstartpolicy.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


import multiprocessing     as _PyMP
from   typing import Tuple as _PyTuple
from   typing import Union as _PyUnion

from xcofdk.fwcom.xmpdefs import unique
from xcofdk.fwcom.xmpdefs import IntEnum
from xcofdk.fwcom.xmpdefs import EProcessStartMethodID

from xcofdk._xcofw.fw.fwssys.fwcore.logging       import logif
from xcofdk._xcofw.fw.fwssys.fwcore.swpfm.sysinfo import _SystemInfo

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine


@unique
class _EProcessStartMethodID(IntEnum):
    eSystemDefault = EProcessStartMethodID.SystemDefault.value
    eSpawn         = EProcessStartMethodID.Spawn.value
    eFork          = EProcessStartMethodID.Fork.value

    eForkServer = -1

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
            logif._LogError(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_MPStartPolicy_TextID_001).format(type(smID_).__name__, EProcessStartMethodID.__name__))
            return False

        _curSM = _MPStartPolicy.__FetchCurrentStartMethodID()
        res = (_curSM is not None) and _curSM == smID_
        return res

    @staticmethod
    def _IsStartMethodChanged(bErrorLogOnChange_ =True) -> bool:
        _curSM = _MPStartPolicy.__FetchCurrentStartMethodID()
        if (_curSM is None) or _MPStartPolicy.__IsEncounteredFatalError():
            return True
        if _MPStartPolicy.__bSmChangeDetected:
            return True

        _ffixedSM = _MPStartPolicy.__fixedSmID

        res = False
        if _ffixedSM is not None:
            res = _curSM != _ffixedSM
            if res:
                if not _MPStartPolicy.__bSmChangeDetected:
                    _MPStartPolicy.__bSmChangeDetected = True
                    if bErrorLogOnChange_:
                        logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_MPStartPolicy_TextID_015).format(_ffixedSM.compactName, _curSM.compactName))
        return res

    @staticmethod
    def _GetSystemDefaultStartMethodID() -> _EProcessStartMethodID:
        return _EProcessStartMethodID.eFork if _SystemInfo._IsPlatformLinux() else _EProcessStartMethodID.eSpawn

    @staticmethod
    def _GetDefinedStartMethdsNameList() -> list:
        return list(_MPStartPolicy.__KNOWN_START_METHODS_NAME_LIST)

    @staticmethod
    def _GetCurrentStartMethodID() -> _PyUnion[_EProcessStartMethodID, None]:
        return _MPStartPolicy.__FetchCurrentStartMethodID()

    @staticmethod
    def _MapStartMethodToID(smName_ : str) -> _PyUnion[_EProcessStartMethodID, None]:
        if not(isinstance(smName_, str) and (len(smName_.strip())>0)):
            return None

        smName_ = smName_.strip()

        if smName_ not in _MPStartPolicy.__KNOWN_START_METHODS_NAME_LIST:
            logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_MPStartPolicy_TextID_008).format(smName_, _MPStartPolicy._ToString()))
            return None

        res = None
        for name, member in _EProcessStartMethodID.__members__.items():
            if smName_ == member.compactName:
                res = member
                break

        if res is None:
            _MPStartPolicy.__bFatalError = True
            logif._LogFatal(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_MPStartPolicy_TextID_009).format(smName_, _MPStartPolicy._ToString()))
        return res

    @staticmethod
    def _ToString():
        if _MPStartPolicy.__IsEncounteredFatalError():
            return None

        _curSM  = _MPStartPolicy.__curSmID
        _prvSM  = _MPStartPolicy.__prvSmID
        _initSM = _MPStartPolicy.__INIT_SM_ID

        _ffixedSM = _MPStartPolicy.__fixedSmID
        if _ffixedSM is not None:
            _ffixedSM = _ffixedSM.compactName
        return _FwTDbEngine.GetText(_EFwTextID.eLogMsg_MPStartPolicy_TextID_007).format(_SystemInfo._GetPlatform(), _initSM.compactName, _prvSM.compactName, _curSM.compactName, _ffixedSM)




    @staticmethod
    def __IsEncounteredFatalError():
        return _MPStartPolicy.__bFatalError

    @staticmethod
    def __GetFwTargetStartMethodID() -> _PyUnion[_EProcessStartMethodID, None]:
        res = _MPStartPolicy.__FW_TGT_SM_ID
        if res is None:
            _MPStartPolicy.__FetchCurrentStartMethodID()
            res = _MPStartPolicy.__FW_TGT_SM_ID
        return res

    @staticmethod
    def __FetchCurrentStartMethodID() -> _PyUnion[_EProcessStartMethodID, None]:
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

