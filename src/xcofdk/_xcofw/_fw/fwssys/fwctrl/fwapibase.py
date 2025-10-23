# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwapibase.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

import os
from   typing import List
from   typing import Tuple
from   typing import Union

from xcofdk.fwcom import LcFailure

from _fw.fwssys.fwcore.logging          import logif
from _fw.fwssys.fwcore.logging          import vlogif
from _fw.fwssys.fwcore.base.timeutil    import _TimeUtil
from _fw.fwssys.fwcore.lc.lcmgr         import _LcManager
from _fw.fwssys.fwcore.swpfm.sysinfo    import _SystemInfo
from _fw.fwssys.fwctrl.fwapiconnap      import _FwApiConnectorAP
from _fw.fwssys.fwerrh.fwerrorcodes     import _EFwErrorCode
from _fwa.fwrtecfg.fwrteconfig          import _FwRteConfig
from _fwa.fwversion                     import _FwVersion

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _FwApiBase:
    def __init__(self):
        pass

    @staticmethod
    def FwApiIsLcErrorFree() -> bool:
        return _FwApiConnectorAP._APIsLcErrorFree()

    @staticmethod
    def FwApiIsFwAvailable() -> bool:
        return _FwApiConnectorAP._APIsFwApiConnected()

    @staticmethod
    def FwApiIsXTaskRunning(xtUID_ : int) -> bool:
        return _FwApiConnectorAP._APIsXTaskRunning(xtUID_)

    @staticmethod
    def FwApiIsFTPythonVersion() -> bool:
        return _SystemInfo._IsPyVersionSupportedOfficialFTPython()

    @staticmethod
    def FwApiIsExperimentalFTPythonVersion() -> bool:
        return _SystemInfo._IsPyVersionSupportedExperimentalFTPython()

    @staticmethod
    def FwApiGetLcFailure() -> Union[LcFailure, None]:
        return _FwApiConnectorAP._APGetLcFailure()

    @staticmethod
    def FwApiGetXcofdkVer() -> str:
        return _FwVersion._GetVersionInfo(bSkipPrefix_=True)

    @staticmethod
    def FwApiGetPythonVer() -> str:
        return _SystemInfo._GetPythonVer()

    @staticmethod
    def FwApiGetPlatform() -> str:
        return _SystemInfo._GetPlatform()

    @staticmethod
    def FwApiAvailableCpuCoresCount() -> int:
        return _SystemInfo._GetCpuCoresCount()

    @staticmethod
    def FwApiStartXcoFW(startOptions_ : Union[list, str] =None) -> bool:
        _fwVer = _FwVersion._GetVersionInfo(bSkipPrefix_=True)

        if not _SystemInfo._IsPyVersionSupported():
            logif._XLogErrorEC(_EFwErrorCode.UE_00160, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwApiBase_TID_014).format(_fwVer))
            return False

        _rteCfg = _FwRteConfig._GetInstance(bFreeze_=True)
        if not _rteCfg._isValid:
            logif._XLogErrorEC(_EFwErrorCode.UE_00210, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwApiBase_TID_016).format(str(_rteCfg)))
            return False

        if _SystemInfo._IsGilDisabled():
            if _SystemInfo._IsPyVersionSupportedExperimentalFTPython():
                if not _rteCfg._isExperimentalFreeThreadingBypassed:
                    logif._XLogErrorEC(_EFwErrorCode.UE_00161, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwApiBase_TID_017).format(_SystemInfo._GetPythonVer(), _fwVer))
                    return False
                _midPart = _FwTDbEngine.GetText(_EFwTextID.eFwRteConfig_ToString_04)
                logif._XLogUrgentWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwApiBase_TID_018).format(_midPart, _SystemInfo._GetPythonVer(), _fwVer))

        if _FwApiConnectorAP._APIsFwApiConnected():
            logif._XLogErrorEC(_EFwErrorCode.UE_00001, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwApiBase_TID_001))
            return False

        if isinstance(startOptions_, str):
            startOptions_ = startOptions_.strip()
            startOptions_ = None if len(startOptions_)<1 else startOptions_.split()

        _suPolicy = _LcManager._CreateStartupPolicy(_FwApiBase.__CalcPPass(startOptions_))
        if _suPolicy is None:
            return False

        _apiRetRec = _LcManager._CreateLcMgr(_suPolicy, startOptions_)
        if _apiRetRec is None:
            logif._XLogErrorEC(_EFwErrorCode.UE_00162, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwApiBase_TID_004))
            return False
        if _apiRetRec.syncSem is not None:
            _apiRetRec.syncSem.acquire()
        return True

    @staticmethod
    def FwApiStopXcoFW() -> bool:
        return _FwApiConnectorAP._APStopFW()

    @staticmethod
    def FwApiJoinXcoFW() -> bool:
        return _FwApiConnectorAP._APJoinFW()

    @staticmethod
    def FwApiJoinTasks(tasks_: Union[int, List[int], None] =None, timeout_: Union[int, float] =None) -> Tuple[int, Union[List[int], None]]:
        _numJ, _lstUnj = _FwApiConnectorAP._APJoinTasks(tasks_, timeout_=timeout_)
        return _numJ, _lstUnj

    @staticmethod
    def FwApiJoinProcesses(procs_: Union[int, List[int], None] =None, timeout_: Union[int, float] =None) -> Tuple[int, Union[List[int], None]]:
        _numJ, _lstUnj = _FwApiConnectorAP._APJoinProcesses(procs_, timeout_=timeout_)
        return _numJ, _lstUnj

    @staticmethod
    def FwApiTerminateProcesses(procs_: Union[int, List[int], None] =None) -> int:
        return _FwApiConnectorAP._APTerminateProcesses(procs_)

    @staticmethod
    def __CalcPPass(startOptions_ : list) -> int:
        tpl = os.path.splitext(__file__)
        bn = os.path.basename(tpl[0])

        res = _TimeUtil.GetHash(__file__, bn)
        if isinstance(startOptions_, list):
            if len(startOptions_) > 0:
                _tmp = list(startOptions_)
                _tmp.append(res)
                res = _TimeUtil.GetHash(*_tmp)

        return res

