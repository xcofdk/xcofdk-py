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
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcdefines       import _ELcScope
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcdefines       import _ELcCompID
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcdefines       import _ELcOperationModeID
from xcofdk._xcofw.fw.fwssys.fwcore.types.apobject     import _ProtectedAbstractSlotsObject
from xcofdk._xcofw.fw.fwssys.fwerrh.lcfrcview          import _LcFrcView

class _LcProxy(_ProtectedAbstractSlotsObject):

    __slots__  = []
    _singleton = None

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

    def _PxyIsTaskMgrApiAvailable(self) -> bool:
        pass

    def _PxyIsTaskMgrFailed(self) -> bool:
        pass

    def _PxyHasLcAnyFailureState(self) -> bool:
        pass

    def _PxyHasLcCompAnyFailureState(self, eLcCompID_: _ELcCompID, atask_ =None) -> bool:
        pass

    def _PxyGetCurProxyInfo(self):
        pass

    def _PxyGetTaskMgr(self) -> _PyUnion[_TaskManager, None]:
        pass

    def _PxyGetLcFrcView(self) -> _LcFrcView:
        pass

    def _PxyGetLcCompFrcView(self, eLcCompID_ : _ELcCompID, atask_ =None) -> _LcFrcView:
        pass

    def _PxySetLcOperationalState(self, eLcCompID_: _ELcCompID, bStartStopFlag_: bool, atask_) -> bool:
        pass

    def _PxyNotifyLcFailure(self, eFailedCompID_ : _ELcCompID, frcError_ : _FatalEntry, atask_ =None):
        pass
