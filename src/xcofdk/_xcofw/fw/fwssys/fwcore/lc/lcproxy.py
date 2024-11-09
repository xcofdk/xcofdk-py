# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : lcproxy.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from typing import Union as _PyUnion

from xcofdk._xcofw.fw.fwssys.fwcore.logging.fatalentry import _FatalEntry
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskmgr    import _TaskManager
from xcofdk._xcofw.fw.fwssys.fwcore.config.fwconfig    import _FwConfig
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcdefines       import _ELcScope
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcdefines       import _ELcCompID
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcdefines       import _ELcOperationModeID
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcstate         import _LcState


class _LcProxy(_LcState):

    __slots__  = []
    _singleton = None

    def __init__(self, ppass_ : int):
        super().__init__(ppass_)


    @property
    def isLcProxyAvailable(self) -> bool:
        pass

    @property
    def isLcProxyInfoAvailable(self) -> bool:
        pass

    @property
    def isTaskManagerApiAvailable(self) -> bool:
        pass

    @property
    def lcScope(self) -> _PyUnion[_ELcScope, None]:
        pass

    @property
    def taskManager(self) -> _PyUnion[_TaskManager, None]:
        pass

    @property
    def curProxyInfo(self):
        pass


    @property
    def isLcModeNormal(self) -> bool:
        pass

    @property
    def isLcModePreShutdown(self) -> bool:
        pass

    @property
    def isLcModeShutdown(self) -> bool:
        pass

    @property
    def isLcModeFailureHandling(self) -> bool:
        pass

    @property
    def isLcShutdownEnabled(self) -> bool:
        pass

    @property
    def eLcOperationModeID(self) -> _ELcOperationModeID:
        pass

    def _SetLcOperationalState(self, eLcCompID_: _ELcCompID, bStartStopFlag_: bool, atask_) -> bool:
        pass

    def _NotifyLcFailure(self, eFailedCompID_ : _ELcCompID, frcError_ : _FatalEntry, atask_ =None):
        pass


