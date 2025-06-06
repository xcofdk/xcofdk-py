# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : iflcproxy.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from typing import Union

from _fw.fwssys.assys.ifs.tiftmgr      import _ITTMgr
from _fw.fwssys.fwcore.ipc.tsk.taskmgr import _TaskManager
from _fw.fwssys.fwcore.lc.lcdefines    import _ELcCompID
from _fw.fwssys.fwcore.lc.lcdefines    import _ELcOperationModeID
from _fw.fwssys.fwcore.types.apobject  import _ProtAbsSlotsObject
from _fw.fwssys.fwerrh.logs.errorlog   import _FatalLog
from _fw.fwssys.fwerrh.lcfrcview       import _LcFrcView

class _ILcProxy(_ProtAbsSlotsObject):
    __slots__  = []
    _sgltn = None

    def __init__(self, ppass_ : int):
        super().__init__(ppass_)

    def _PxyIsLcProxyModeNormal(self) -> bool:
        pass

    def _PxyIsLcProxyModeShutdown(self) -> bool:
        pass

    def _PxyIsLcMonShutdownEnabled(self) -> bool:
        pass

    def _PxyGetLcProxyOperationMode(self) -> _ELcOperationModeID:
        pass

    def _PxyIsLcProxyInfoAvailable(self) -> bool:
        pass

    def _PxyIsLcOperable(self) -> bool:
        pass

    def _PxyIsLcCoreOperable(self) -> bool:
        pass

    def _PxyIsMainXTaskStarted(self) -> bool:
        pass

    def _PxyIsMainXTaskStopped(self) -> bool:
        pass

    def _PxyIsMainXTaskFailed(self) -> bool:
        pass

    def _PxyIsTaskMgrAvailable(self) -> bool:
        pass

    def _PxyIsTaskMgrFailed(self) -> bool:
        pass

    def _PxyHasLcAnyFailureState(self) -> bool:
        pass

    def _PxyHasLcCompAnyFailureState(self, lcCID_: _ELcCompID, atask_ =None) -> bool:
        pass

    def _PxyGetCurProxyInfo(self):
        pass

    def _PxyGetTaskMgr(self) -> Union[_TaskManager, None]:
        pass

    def _PxyGetTTaskMgr(self) -> Union[_ITTMgr, None]:
        pass

    def _PxyGetLcFrcView(self) -> _LcFrcView:
        pass

    def _PxyGetLcCompFrcView(self, lcCID_ : _ELcCompID, atask_ =None) -> _LcFrcView:
        pass

    def _PxySetLcOperationalState(self, lcCID_: _ELcCompID, bStartStopFlag_: bool, atask_) -> bool:
        pass

    def _PxyNotifyLcFailure(self, eFailedCompID_ : _ELcCompID, frcError_ : _FatalLog, atask_ =None):
        pass
