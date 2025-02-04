# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwmainif.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from xcofdk._xcofw.fw.fwssys.fwcore.logging.fatalentry import _FatalEntry
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcdefines       import _ELcCompID
from xcofdk._xcofw.fw.fwssys.fwcore.lcmon.lcmonimpl    import _LcMonitorImpl
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcproxydefines  import _ELcShutdownRequest
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject      import _AbstractSlotsObject

from xcofdk._xcofw.fw.fwssys.fwcore.ipc.sync.semaphore import _BinarySemaphore
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.atask      import  _AbstractTask

class _FwMainIF(_AbstractSlotsObject):

    __slots__ = []

    def __init__(self):
        super().__init__()

    @property
    def lcMonitorImpl(self) -> _LcMonitorImpl:
        pass

    def StartFwMain(self, semStart_: _BinarySemaphore) -> bool:
        pass

    def StopFwMain(self, semStop_: _BinarySemaphore =None) -> bool:
        pass

    def FinalizeCustomSetup(self) -> bool:
        pass

    def ProcessShutdownAction(self, eShutdownAction_: _ELcShutdownRequest, eFailedCompID_: _ELcCompID =None, frcError_: _FatalEntry =None, atask_: _AbstractTask =None):
        pass
