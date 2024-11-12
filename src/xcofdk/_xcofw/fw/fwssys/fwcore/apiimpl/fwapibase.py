# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwapibase.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


import os
from   typing import Union

from xcofdk._xcofw.fw.fwssys.fwcore.logging                import logif
from xcofdk._xcofw.fw.fwssys.fwcore.base.timeutil          import _TimeUtil
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcmgr               import _LcManager
from xcofdk._xcofw.fw.fwssys.fwcore.swpfm.sysinfo          import _SystemInfo
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes      import _CommonDefines
from xcofdk._xcofw.fw.fwssys.fwcore.apiimpl.fwapiconnap    import _FwApiConnectorAP
from xcofdk._xcofwa.fwversion                              import _FwVersion

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine


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

        if not _SystemInfo._IsFrameworkSupportingPythonVersion():
            logif._XLogError(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwApiBase_TextID_014).format(_fwVer))
            return False

        if _SystemInfo._IsGilDisabled():
            logif._XLogError(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwApiBase_TextID_016).format(_SystemInfo._GetPythonVer(), _fwVer))
            return False


        if _FwApiConnectorAP._APIsFwApiConnected():
            logif._LogError(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwApiBase_TextID_001))
            return False

        if isinstance(startOptions_, str):
            startOptions_ = startOptions_.strip()
            startOptions_ = None if len(startOptions_)<1 else startOptions_.split()

        _suPolicy = _LcManager._CreateStartupPolicy(_FwApiBase.__CalcPPass(startOptions_))
        if _suPolicy is None:
            return False

        print(_FwApiBase.__GetPreamble())

        _apiRetRec = _LcManager._CreateLcMgr(_suPolicy, startOptions_)
        if _apiRetRec is None:
            logif._XLogError(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwApiBase_TextID_004))
            return False

        if _apiRetRec.syncSem is not None:
            _apiRetRec.syncSem.acquire()

        return True

    @staticmethod
    def FwApiStopXcoFW() -> bool:
        return _FwApiConnectorAP._APStopFW()

    @staticmethod
    def FwApiJoinXcoFW() -> bool:
        res = _FwApiConnectorAP._APJoinFW()
        return res

    @staticmethod
    def FwApiGetXTask(xuUniqueID_ : int =0):
        if xuUniqueID_ == 0:
            return _FwApiConnectorAP._APGetCurXTask()
        return _FwApiConnectorAP._APGetXTask(xuUniqueID_)

    @staticmethod
    def FwApiGetCurXTask():
        return _FwApiConnectorAP._APGetCurXTask()


    @staticmethod
    def __GetPreamble():
        _dlLong  = _CommonDefines._DASH_LINE_LONG
        _dlShort = _CommonDefines._DASH_LINE_SHORT

        _verstr = _SystemInfo._GetPythonVer()
        _verstr = _FwTDbEngine.GetText(_EFwTextID.eFwApiBase_StartPreamble_Python_Version).format(_verstr)

        res = _FwTDbEngine.GetText(_EFwTextID.eFwApiBase_StartPreamble)
        res = res.format(_dlLong, _dlShort, _dlShort, _FwVersion._GetVersionInfo(bShort_=False), _dlShort, _verstr, _dlShort, _dlLong)
        return res

    @staticmethod
    def __CalcPPass(startOptions_ : list) -> int:
        tpl = os.path.splitext(__file__)
        bn = os.path.basename(tpl[0])

        res = _TimeUtil.GetHash(__file__, bn)
        if isinstance(startOptions_, list):
            if len(startOptions_) > 0:
                tmp = list(startOptions_)
                tmp.append(res)
                res = _TimeUtil.GetHash(*tmp)

        return res


