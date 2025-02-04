# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xtaskconnif.py
#
# Copyright(c) 2024 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.aexecutable import _AbstractExecutable
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcproxyclient    import _LcProxyClient

class _XTaskConnectorIF(_LcProxyClient):

    __slots__ = []

    def __init__(self):
        super().__init__()

    @property
    def xtaskProfile(self):
        pass

    @property
    def _isStarted(self) -> bool:
        pass

    @property
    def _isPendingRun(self) -> bool:
        pass

    @property
    def _isRunning(self) -> bool:
        pass

    @property
    def _isDone(self) -> bool:
        pass

    @property
    def _isXTaskConnected(self) -> bool:
        pass

    @property
    def _connectedXTask(self) -> _AbstractExecutable:
        pass

    def _CleanUp(self):
        super()._CleanUp()
