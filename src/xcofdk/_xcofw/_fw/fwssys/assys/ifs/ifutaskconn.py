# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : ifutaskconn.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from _fw.fwssys.assys.ifs.ifutagent import _IUTAgent

class _IUTaskConn:
    __slots__ = []

    def __init__(self):
        pass

    @property
    def _isUTConnected(self) -> bool:
        pass

    @property
    def _taskUID(self) -> int:
        pass

    @property
    def _taskProfile(self):
        pass

    @property
    def _xCard(self):
        pass

    @property
    def _utAgent(self) -> _IUTAgent:
        pass

    def _IncEuRNumber(self):
        pass

    def _UpdateUTD(self, atask_):
        pass

    def _PcSetLcProxy(self, lcPxy_, bForceUnset_=False):
        pass

    def _DisconnectUTask(self, bDetachApiRequest_ =False):
        pass

    def CleanUp(self):
        pass
