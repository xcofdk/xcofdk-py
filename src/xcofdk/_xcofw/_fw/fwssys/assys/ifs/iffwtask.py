# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : iffwtask.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from typing import Union

from _fw.fwssys.assys.ifs.ifxunit         import _IXUnit
from _fw.fwssys.fwcore.lc.ifs.iflcproxy   import _ILcProxy
from _fw.fwssys.fwcore.base.gtimeout      import _Timeout
from _fw.fwssys.fwcore.ipc.sync.semaphore import _BinarySemaphore
from _fw.fwssys.fwcore.ipc.tsk.ataskop    import _ATaskOpPreCheck
from _fw.fwssys.fwcore.ipc.tsk.taskdefs   import _ETaskSelfCheckResultID
from _fw.fwssys.fwcore.ipc.tsk.taskutil   import _ETaskXPhaseID
from _fw.fwssys.fwcore.ipc.tsk.taskutil   import _ETaskApiContextID
from _fw.fwssys.fwcore.ipc.tsk.taskxcard  import _TaskXCard
from _fw.fwssys.fwcore.types.afwprofile   import _AbsFwProfile
from _fw.fwssys.fwcore.lc.lcdefines       import _ELcCompID
from _fw.fwssys.fwerrh.logs.xcoexception  import _XcoXcpRootBase

class _IFwTask:
    __slots__ = []

    def __init__(self):
        pass

    def __str__(self):
       return self._ToString()

    def _isInvalid(self):
        return True

    @property
    def _isAlive(self) -> bool:
        return False

    @property
    def _isAutoStartEnclHThrdEnabled(self):
        return False

    @property
    def _daprofile(self) -> Union[_AbsFwProfile, None]:
       return None

    @property
    def _xcard(self) -> Union[_TaskXCard, None]:
        return None

    @property
    def _dxUnit(self) -> Union[_IXUnit, None]:
        return None

    @property
    def _xrNumber(self) -> int:
        return -1

    def _GetTaskXPhase(self) -> _ETaskXPhaseID:
        pass

    def _GetTaskApiContext(self) -> _ETaskApiContextID:
        pass

    def _GetLcCompID(self) -> _ELcCompID:
        pass

    def _ToString(self) -> str:
        pass

    def _IncEuRNumber(self) -> int:
        pass

    def _PropagateLcProxy(self, lcProxy_ : _ILcProxy =None):
        pass

    def _ProcUnhandledException(self, xcp_: _XcoXcpRootBase):
        pass

    def _SelfCheckTask(self) -> _ETaskSelfCheckResultID:
        pass

    def _StartTask(self, semStart_ : _BinarySemaphore =None, tskOpPCheck_ : _ATaskOpPreCheck =None, curTask_ =None) -> bool:
        pass

    def _StopTask(self, bCancel_ =False, semStop_ : _BinarySemaphore =None, tskOpPCheck_ : _ATaskOpPreCheck =None, curTask_ =None) -> bool:
        pass

    def _JoinTask(self, timeout_ : _Timeout =None, tskOpPCheck_ : _ATaskOpPreCheck =None, curTask_ =None) -> bool:
        pass
