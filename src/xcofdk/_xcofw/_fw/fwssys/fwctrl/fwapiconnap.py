# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwapiconnap.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from threading import RLock as _PyRLock
from typing    import List
from typing    import Tuple
from typing    import Union

from xcofdk.fwcom               import LcFailure
from xcofdk.fwapi               import IRCTask
from xcofdk.fwapi               import IRCCommTask
from xcofdk.fwapi.apiif.ifxtask import IXTask

from _fw.fwssys.fwcore.lc.lcxstate       import _LcFailure
from _fw.fwssys.fwcore.types.commontypes import _EDepInjCmd
from _fw.fwssys.fwcore.types.apobject    import _ProtAbsSlotsObject

class _FwApiConnectorAP:
    __slots__ = []

    __theCAL  = None
    __theFwCN = None

    def __init__(self):
        pass

    @staticmethod
    def _APIsFwApiConnected():
        if _FwApiConnectorAP.__theCAL is None: return False
        with _FwApiConnectorAP.__theCAL:
            return _FwApiConnectorAP.__theFwCN is not None

    @staticmethod
    def _APIsLcErrorFree() -> bool:
        return _LcFailure.IsLcErrorFree() if _FwApiConnectorAP.__IsFwApiDisconnected() else _FwApiConnectorAP.__theFwCN._FwCNIsLcErrorFree()

    @staticmethod
    def _APIsLcShutdownEnabled() -> bool:
        return False if _FwApiConnectorAP.__IsFwApiDisconnected() else _FwApiConnectorAP.__theFwCN._FwCNIsLcShutdownEnabled()

    @staticmethod
    def _APIsXTaskRunning(xtUID_ : int) -> bool:
        return False if _FwApiConnectorAP.__IsFwApiDisconnected() else _FwApiConnectorAP.__theFwCN._FwCNIsXTaskRunning(xtUID_)

    @staticmethod
    def _APGetLcFailure() -> Union[LcFailure, None]:
        return _LcFailure._GetLcFailure() if _FwApiConnectorAP.__IsFwApiDisconnected() else _FwApiConnectorAP.__theFwCN._FwCNGetLcFailure()

    @staticmethod
    def _APGetXTask(xtUID_ : int =0):
        if xtUID_ == 0:
            return _FwApiConnectorAP._APGetCurXTask()
        return None if _FwApiConnectorAP.__IsFwApiDisconnected() else _FwApiConnectorAP.__theFwCN.FwCNGetXTask(xtUID_)

    @staticmethod
    def _APGetCurXTask() -> Union[IXTask, None]:
        return None if _FwApiConnectorAP.__IsFwApiDisconnected() else _FwApiConnectorAP.__theFwCN.FwCNGetCurXTask()

    @staticmethod
    def _APGetCurRcTask() -> Union[IRCTask, IRCCommTask, None]:
        return None if _FwApiConnectorAP.__IsFwApiDisconnected() else _FwApiConnectorAP.__theFwCN.FwCNGetCurRcTask()

    @staticmethod
    def _APStopFW():
        return False if _FwApiConnectorAP.__IsFwApiDisconnected() else _FwApiConnectorAP.__theFwCN.FwCNStopXcoFW()

    @staticmethod
    def _APJoinFW():
        return False if _FwApiConnectorAP.__IsFwApiDisconnected() else _FwApiConnectorAP.__theFwCN.FwCNJoinXcoFW()

    @staticmethod
    def _APJoinTasks(tasks_: Union[int, List[int], None] =None, timeout_: Union[int, float] =None) -> Tuple[int, Union[List[int], None]]:
        if _FwApiConnectorAP.__IsFwApiDisconnected():
            return 0, None
        _numJ, _lstUnj = _FwApiConnectorAP.__theFwCN.FwCNJoinTasks(tasks_, timeout_=timeout_)
        return _numJ, _lstUnj

    @staticmethod
    def _APJoinProcesses(procs_: Union[int, List[int], None] =None, timeout_: Union[int, float] =None) -> Tuple[int, Union[List[int], None]]:
        if _FwApiConnectorAP.__IsFwApiDisconnected():
            return 0, None
        _numJ, _lstUnj = _FwApiConnectorAP.__theFwCN.FwCNJoinProcesses(procs_, timeout_=timeout_)
        return _numJ, _lstUnj

    @staticmethod
    def _APTerminateProcesses(procs_: Union[int, List[int], None] =None) -> int:
        return _FwApiConnectorAP.__theFwCN.FwCNTerminateProcesses(procs_)

    @staticmethod
    def _APSetFwApiConnector(fwConnecctor_ : _ProtAbsSlotsObject, connAccessLck_ : _PyRLock):
        if connAccessLck_ is not None:
            if _FwApiConnectorAP.__theCAL is None:
                _FwApiConnectorAP.__theCAL = connAccessLck_

        _accessLck = _FwApiConnectorAP.__theCAL
        if _accessLck is not None:
            with _accessLck:
                _FwApiConnectorAP.__theFwCN = fwConnecctor_
                if fwConnecctor_ is None:
                    _FwApiConnectorAP.__theCAL = None

    @staticmethod
    def _DepInjection(dinjCmd_ : _EDepInjCmd):
        _FwApiConnectorAP.__theFwCN          = None
        _FwApiConnectorAP.__theCAL = None

    @staticmethod
    def __IsFwApiDisconnected():
        if _FwApiConnectorAP.__theCAL is None: return True
        with _FwApiConnectorAP.__theCAL:
            return _FwApiConnectorAP.__theFwCN is None
