# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : iffwmain.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from _fw.fwssys.fwcore.lc.lcdefines       import _ELcCompID
from _fw.fwssys.fwcore.lc.lcproxydefines  import _ELcSDRequest
from _fw.fwssys.fwcore.types.aobject      import _AbsSlotsObject
from _fw.fwssys.fwcore.ipc.sync.semaphore import _BinarySemaphore
from _fw.fwssys.fwcore.ipc.tsk.afwtask    import  _AbsFwTask
from _fw.fwssys.fwerrh.logs.errorlog      import _FatalLog

class _IFwMain(_AbsSlotsObject):
    __slots__ = []

    def __init__(self):
        super().__init__()

    def StartFwMain(self, semStart_: _BinarySemaphore) -> bool:
        pass

    def StopFwMain(self, semStop_: _BinarySemaphore =None) -> bool:
        pass

    def FinalizeCustomSetup(self) -> bool:
        pass

    def ProcessShutdownAction(self, eShutdownAction_: _ELcSDRequest, eFailedCompID_: _ELcCompID =None, frcError_: _FatalLog =None, atask_: _AbsFwTask =None):
        pass
