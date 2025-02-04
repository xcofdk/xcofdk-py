# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : lcproxyclient.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from typing import Union as _PyUnion

from xcofdk._xcofw.fw.fwssys.fwcore.logging            import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.logging.fatalentry import _FatalEntry
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskmgr    import _TaskManager
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcdefines       import _ELcCompID
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcdefines       import _ELcOperationModeID
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcproxy         import _LcProxy
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject      import _AbstractSlotsObject
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes  import _ETernaryOpResult

from xcofdk._xcofw.fw.fwssys.fwerrh.fwerrorcodes import _EFwErrorCode
from xcofdk._xcofw.fw.fwssys.fwerrh.lcfrcview    import _LcFrcView

class _LcProxyClient(_AbstractSlotsObject):

    __slots__  = [ '__lcPxy' , '__lcOpModeID' ]

    def __init__(self):
        super().__init__()
        self.__lcPxy      = None
        self.__lcOpModeID = None

    def _CleanUp(self):
        self.__lcPxy      = None
        self.__lcOpModeID = None

    def _PcClientName(self) -> str:
        return type(self).__name__

    def _PcSetLcProxy(self, lcPxy_ : _PyUnion[_LcProxy, _AbstractSlotsObject], bForceUnset_ =False):
        if lcPxy_ is None:
            if bForceUnset_:
                self.__lcPxy      = None
                self.__lcOpModeID = None
            return
        if self.__isProxySet:
            return
        if isinstance(lcPxy_, _LcProxyClient) and lcPxy_._PcIsLcProxySet():
            lcPxy_ = lcPxy_._PcGetLcProxy()

        if not isinstance(lcPxy_, _LcProxy):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00381)
        elif lcPxy_._PxyIsLcProxyModeShutdown():
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00382)
        else:
            self.__lcPxy      = lcPxy_
            self.__lcOpModeID = lcPxy_._PxyGetLcProxyOperationMode()

    def _PcIsMonitoringLcModeChange(self) -> bool:
        return False

    def _PcOnLcCeaseModeDetected(self) -> _ETernaryOpResult:
        return _ETernaryOpResult.Stop()

    def _PcOnLcFailureDetected(self) -> _ETernaryOpResult:
        return _ETernaryOpResult.Stop()

    def _PcOnLcPreShutdownDetected(self) -> _ETernaryOpResult:
        return _ETernaryOpResult.Stop()

    def _PcOnLcShutdownDetected(self) -> _ETernaryOpResult:
        return _ETernaryOpResult.Stop()

    def _PcIsLcOperable(self) -> bool:
        return self.__isProxySet and self.__lcPxy._PxyIsLcOperable()

    def _PcIsLcCoreOperable(self) -> bool:
        return self.__isProxySet and self.__lcPxy._PxyIsLcCoreOperable()

    def _PcIsLcProxyModeNormal(self):
        return self.__isProxySet and self.__lcPxy._PxyIsLcProxyModeNormal()

    def _PcIsLcProxyModeShutdown(self):
        return self.__isProxySet and self.__lcPxy._PxyIsLcProxyModeShutdown()

    def _PcIsLcMonShutdownEnabled(self) -> bool:
        return self.__isProxySet and self.__lcPxy._PxyIsLcMonShutdownEnabled()

    def _PcIsMainXTaskStarted(self) -> bool:
        return self.__isProxySet and self.__lcPxy._PxyIsMainXTaskStarted()

    def _PcIsMainXTaskStopped(self) -> bool:
        return self.__isProxySet and self.__lcPxy._PxyIsMainXTaskStopped()

    def _PcIsMainXTaskFailed(self) -> bool:
        return self.__isProxySet and self.__lcPxy._PxyIsMainXTaskFailed()

    def _PcIsTaskMgrApiAvailable(self):
        return self.__isProxySet and self.__lcPxy._PxyIsTaskMgrApiAvailable()

    def _PcIsTaskMgrFailed(self) -> bool:
        return self.__isProxySet and self.__lcPxy._PxyIsTaskMgrFailed()

    def _PcHasLcAnyFailureState(self) -> bool:
        return self.__isProxySet and self.__lcPxy._PxyHasLcAnyFailureState()

    def _PcHasLcCompAnyFailureState(self, eLcCompID_: _ELcCompID, atask_ =None) -> bool:
        return self.__isProxySet and self.__lcPxy._PxyHasLcCompAnyFailureState(eLcCompID_, atask_=atask_)

    def _PcGetCurProxyInfo(self):
        return None if not self.__isProxySet else self.__lcPxy._PxyGetCurProxyInfo()

    def _PcGetTaskMgr(self) -> _PyUnion[_TaskManager, None]:
        return None if not self.__isProxySet else self.__lcPxy._PxyGetTaskMgr()

    def _PcGetLcFrcView(self) -> _LcFrcView:
        return None if not self.__isProxySet else self.__lcPxy._PxyGetLcFrcView()

    def _PcGetLcCompFrcView(self, eLcCompID_ : _ELcCompID, atask_ =None) -> _LcFrcView:
        return None if not self.__isProxySet else self.__lcPxy._PxyGetLcCompFrcView(eLcCompID_, atask_=atask_)

    def _PcNotifyLcFailure(self, eFailedCompID_ : _ELcCompID, frcError_ : _FatalEntry, atask_ =None):
        if self.__isProxySet:
            self.__lcPxy._PxyNotifyLcFailure(eFailedCompID_, frcError_, atask_=atask_)

    def _PcSetLcOperationalState(self, eLcCompID_: _ELcCompID, bStartStopFlag_: bool, atask_) -> bool:
        return self.__isProxySet and self.__lcPxy._PxySetLcOperationalState(eLcCompID_, bStartStopFlag_, atask_)

    def _PcIsLcProxySet(self) -> bool:
        return self.__isProxySet

    def _PcGetLcProxy(self) -> _LcProxy:
        return self.__lcPxy

    def _PcCheckLcOperationModeChange(self) -> _ELcOperationModeID:
        if self.__lcPxy is None:
            res = None
        elif not self._PcIsMonitoringLcModeChange():
            res = None
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00383)
        else:
            if self.__lcPxy._PxyIsLcProxyModeShutdown():
                _newID = _ELcOperationModeID.eLcShutdown
            else:
                _newID = self.__lcPxy._PxyGetLcProxyOperationMode()

            if _newID != self.__lcOpModeID:
                res = _newID
                self.__lcOpModeID = _newID
            else:
                res = None
        return res

    @property
    def __isProxySet(self) -> bool:
        return self.__lcPxy is not None
