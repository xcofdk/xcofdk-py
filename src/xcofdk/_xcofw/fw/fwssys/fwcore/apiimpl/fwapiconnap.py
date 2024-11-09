# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwapiconnap.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from threading import RLock as _PyRLock

from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcexecstate import _LcFailure
from xcofdk._xcofw.fw.fwssys.fwcore.types.apobject import _ProtectedAbstractSlotsObject


class _FwApiConnectorAP:

    __slots__ = []
    __theFwCN          = None
    __theConnAccessLck = None

    def __init__(self):
        pass

    @staticmethod
    def _APGetXTask(xuUniqueID_ : int =0):
        if xuUniqueID_ == 0:
            return _FwApiConnectorAP._APGetCurXTask()
        return None if _FwApiConnectorAP.__IsFwApiDisconnected() else _FwApiConnectorAP.__theFwCN.FwCNGetXTask(xuUniqueID_)

    @staticmethod
    def _APGetCurXTask():
        return None if _FwApiConnectorAP.__IsFwApiDisconnected() else _FwApiConnectorAP.__theFwCN.FwCNGetCurXTask()

    @staticmethod
    def _APStopFW():
        return False if _FwApiConnectorAP.__IsFwApiDisconnected() else _FwApiConnectorAP.__theFwCN.FwCNStopXcoFW()

    @staticmethod
    def _APJoinFW():
        return False if _FwApiConnectorAP.__IsFwApiDisconnected() else _FwApiConnectorAP.__theFwCN.FwCNJoinXcoFW()

    @staticmethod
    def _APIsLcErrorFree() -> bool:
        return _LcFailure.IsLcErrorFree() if _FwApiConnectorAP.__IsFwApiDisconnected() else _FwApiConnectorAP.__theFwCN._FwCNIsLcErrorFree()

    @staticmethod
    def _APIsFwApiConnected():
        if _FwApiConnectorAP.__theConnAccessLck is None: return False
        with _FwApiConnectorAP.__theConnAccessLck:
            return _FwApiConnectorAP.__theFwCN is not None

    @staticmethod
    def _APSetFwApiConnector(fwConnecctor_ : _ProtectedAbstractSlotsObject, connAccessLck_ : _PyRLock):
        if connAccessLck_ is not None:
            if _FwApiConnectorAP.__theConnAccessLck is None:
                _FwApiConnectorAP.__theConnAccessLck = connAccessLck_

        _accessLck = _FwApiConnectorAP.__theConnAccessLck
        if _accessLck is None:
            pass
        else:
            with _accessLck:
                _FwApiConnectorAP.__theFwCN = fwConnecctor_
                if fwConnecctor_ is None:
                    _FwApiConnectorAP.__theConnAccessLck = None

    @staticmethod
    def _APUnsetConnAccessLock():
        _FwApiConnectorAP.__theFwCN           = None
        _FwApiConnectorAP.__theConnAccessLck = None

    @staticmethod
    def __IsFwApiDisconnected():
        if _FwApiConnectorAP.__theConnAccessLck is None: return True
        with _FwApiConnectorAP.__theConnAccessLck:
            return _FwApiConnectorAP.__theFwCN is None
