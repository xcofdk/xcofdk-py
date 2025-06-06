# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : lcproxyclient.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from typing import Union

from _fw.fwssys.assys.ifs.tiftmgr        import _ITTMgr
from _fw.fwssys.fwcore.logging           import vlogif
from _fw.fwssys.fwcore.ipc.tsk.taskdefs  import _ETaskSelfCheckResultID
from _fw.fwssys.fwcore.ipc.tsk.taskmgr   import _TaskManager
from _fw.fwssys.fwcore.lc.lcdefines      import _ELcCompID
from _fw.fwssys.fwcore.lc.lcdefines      import _ELcOperationModeID
from _fw.fwssys.fwcore.lc.ifs.iflcproxy  import _ILcProxy
from _fw.fwssys.fwcore.types.aobject     import _AbsSlotsObject
from _fw.fwssys.fwcore.types.commontypes import _EExecutionCmdID
from _fw.fwssys.fwerrh.fwerrorcodes      import _EFwErrorCode
from _fw.fwssys.fwerrh.logs.errorlog     import _FatalLog
from _fw.fwssys.fwerrh.lcfrcview         import _LcFrcView

class _LcProxyClient(_AbsSlotsObject):
    __slots__  = [ '__p' , '__m' ]

    def __init__(self):
        super().__init__()
        self.__m = None
        self.__p = None

    def _CleanUp(self):
        self.__m = None
        self.__p = None

    def _PcIsMonitoringLcModeChange(self) -> bool:
        return False

    def _PcClientName(self) -> str:
        return type(self).__name__

    def _PcSelfCheck(self) -> _ETaskSelfCheckResultID:
        return _ETaskSelfCheckResultID.eScrStop if not self.__isProxySet else _ETaskSelfCheckResultID.eScrOK

    def _PcSetLcProxy(self, lcPxy_ : Union[_ILcProxy, _AbsSlotsObject], bForceUnset_ =False):
        if lcPxy_ is None:
            if bForceUnset_:
                self.__m = None
                self.__p = None
            return
        if self.__isProxySet:
            return
        if isinstance(lcPxy_, _LcProxyClient) and lcPxy_._PcIsLcProxySet():
            lcPxy_ = lcPxy_._PcGetLcProxy()

        if not isinstance(lcPxy_, _ILcProxy):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00381)
        elif lcPxy_._PxyIsLcProxyModeShutdown():
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00382)
        else:
            self.__m = lcPxy_._PxyGetLcProxyOperationMode()
            self.__p = lcPxy_

    def _PcOnLcCeaseModeDetected(self) -> _EExecutionCmdID:
        return _EExecutionCmdID.Stop()

    def _PcOnLcFailureDetected(self) -> _EExecutionCmdID:
        return _EExecutionCmdID.Stop()

    def _PcOnLcPreShutdownDetected(self) -> _EExecutionCmdID:
        return _EExecutionCmdID.Stop()

    def _PcOnLcShutdownDetected(self) -> _EExecutionCmdID:
        return _EExecutionCmdID.Stop()

    def _PcIsLcOperable(self) -> bool:
        return self.__isProxySet and self.__p._PxyIsLcOperable()

    def _PcIsLcCoreOperable(self) -> bool:
        return self.__isProxySet and self.__p._PxyIsLcCoreOperable()

    def _PcIsLcProxyModeNormal(self):
        return self.__isProxySet and self.__p._PxyIsLcProxyModeNormal()

    def _PcIsLcProxyModeShutdown(self):
        return self.__isProxySet and self.__p._PxyIsLcProxyModeShutdown()

    def _PcIsLcMonShutdownEnabled(self) -> bool:
        return self.__isProxySet and self.__p._PxyIsLcMonShutdownEnabled()

    def _PcIsMainXTaskStarted(self) -> bool:
        return self.__isProxySet and self.__p._PxyIsMainXTaskStarted()

    def _PcIsMainXTaskStopped(self) -> bool:
        return self.__isProxySet and self.__p._PxyIsMainXTaskStopped()

    def _PcIsMainXTaskFailed(self) -> bool:
        return self.__isProxySet and self.__p._PxyIsMainXTaskFailed()

    def _PcIsTaskMgrAvailable(self):
        return self.__isProxySet and self.__p._PxyIsTaskMgrAvailable()

    def _PcIsTaskMgrFailed(self) -> bool:
        return self.__isProxySet and self.__p._PxyIsTaskMgrFailed()

    def _PcHasLcAnyFailureState(self) -> bool:
        return self.__isProxySet and self.__p._PxyHasLcAnyFailureState()

    def _PcHasLcCompAnyFailureState(self, lcCID_: _ELcCompID, atask_ =None) -> bool:
        return self.__isProxySet and self.__p._PxyHasLcCompAnyFailureState(lcCID_, atask_=atask_)

    def _PcGetCurProxyInfo(self):
        return None if not self.__isProxySet else self.__p._PxyGetCurProxyInfo()

    def _PcGetTaskMgr(self) -> Union[_TaskManager, None]:
        return None if not self.__isProxySet else self.__p._PxyGetTaskMgr()

    def _PcGetTTaskMgr(self) -> Union[_ITTMgr, None]:
        return None if not self.__isProxySet else self.__p._PxyGetTTaskMgr()

    def _PcGetLcFrcView(self) -> _LcFrcView:
        return None if not self.__isProxySet else self.__p._PxyGetLcFrcView()

    def _PcGetLcCompFrcView(self, lcCID_ : _ELcCompID, atask_ =None) -> _LcFrcView:
        return None if not self.__isProxySet else self.__p._PxyGetLcCompFrcView(lcCID_, atask_=atask_)

    def _PcNotifyLcFailure(self, eFailedCompID_ : _ELcCompID, frcError_ : _FatalLog, atask_ =None):
        if self.__isProxySet:
            self.__p._PxyNotifyLcFailure(eFailedCompID_, frcError_, atask_=atask_)

    def _PcSetLcOperationalState(self, lcCID_: _ELcCompID, bStartStopFlag_: bool, atask_) -> bool:
        return self.__isProxySet and self.__p._PxySetLcOperationalState(lcCID_, bStartStopFlag_, atask_)

    def _PcIsLcProxySet(self) -> bool:
        return self.__isProxySet

    def _PcGetLcProxy(self) -> _ILcProxy:
        return self.__p

    def _PcCheckLcOperationModeChange(self) -> _ELcOperationModeID:
        if self.__p is None:
            res = None
        elif not self._PcIsMonitoringLcModeChange():
            res = None
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00383)
        else:
            if self.__p._PxyIsLcProxyModeShutdown():
                _newID = _ELcOperationModeID.eLcShutdown
            else:
                _newID = self.__p._PxyGetLcProxyOperationMode()

            if _newID != self.__m:
                res = _newID
                self.__m = _newID
            else:
                res = None
        return res

    @property
    def __isProxySet(self) -> bool:
        return self.__p is not None
