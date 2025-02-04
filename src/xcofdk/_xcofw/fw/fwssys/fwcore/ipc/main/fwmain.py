# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwmain.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from xcofdk._xcofw.fw.fwssys.fwcore.logging               import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.logging.fatalentry    import _FatalEntry
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcexecstate        import _LcFailure
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcproxydefines     import _ELcShutdownRequest
from xcofdk._xcofw.fw.fwssys.fwcore.lcmon.lcmonimpl       import _LcMonitorImpl
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.fwc.mainrunnable  import _MainRunnable
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.arunnabledefs import _ELcCompID
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.atask         import _AbstractTask
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.fwtask        import _FwTask
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskprofile   import _TaskProfile
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.main.fwmainif     import _FwMainIF
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.sync.semaphore    import _BinarySemaphore
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil      import _TaskUtil
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil      import _ETaskRightFlag

from xcofdk._xcofw.fw.fwssys.fwerrh.fwerrorcodes import _EFwErrorCode

class _FwMain(_FwTask, _FwMainIF):

    __slots__ = [ '__mtp' , '__mrbl' ]
    __fwmSgltn = None

    def __init__(self, lcMon_ : _LcMonitorImpl):
        self.__mtp  = None
        self.__mrbl = None
        _FwMainIF.__init__(self)

        _iImplErr = None

        if _FwMain.__fwmSgltn is not None:
            _iImplErr = _EFwErrorCode.FE_LCSF_010
        elif not isinstance(lcMon_, _LcMonitorImpl):
            _iImplErr = _EFwErrorCode.FE_LCSF_011

        if _iImplErr is not None:
            self.CleanUp()
            _LcFailure.CheckSetLcSetupFailure(_iImplErr)

            if _iImplErr == _EFwErrorCode.FE_LCSF_010:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00079)
            else:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00080)
            return

        _lstTR = [ _ETaskRightFlag.eDieXcpTarget, _ETaskRightFlag.eErrorObserver, _ETaskRightFlag.eDieXcpDelegateTarget ]
        _trm   = _ETaskRightFlag.FwTaskRightDefaultMask()
        _trm   = _ETaskRightFlag.AddFwTaskRightFlag(_trm, _lstTR)
        _lstTR.clear()

        _ta = {
            _TaskProfile._ATTR_KEY_TASK_RIGHTS             : _trm
          , _TaskProfile._ATTR_KEY_ON_SIZE_BLOCKING_XQUEUE : False
        }

        _mtp = None

        _mrbl = _MainRunnable(lcMon_)
        if _mrbl._lcMonitorImpl is None:
            _mrbl     = None
            _iImplErr = _EFwErrorCode.FE_LCSF_012

        if _iImplErr is not None:
            pass

        else:
            _mtp = _TaskProfile(runnable_=_mrbl, taskProfileAttrs_=_ta)
            if not _mtp.isValid:
                _iImplErr = _EFwErrorCode.FE_LCSF_013

            else:
                _FwTask.__init__(self, taskPrf_=_mtp, bFwMain_=True)
                if self.taskBadge is None:
                    _myErrID = _EFwErrorCode.FE_LCSF_014
                    _FwTask.CleanUp(self)

        _ccID    = None
        _errCode = None

        if _iImplErr is not None:
            if _mtp is not None:
                _mtp.CleanUp()

            if _mrbl is not None:
                _mrbl.CleanUp()

            _LcFailure.CheckSetLcSetupFailure(_iImplErr)

            if _iImplErr == _EFwErrorCode.FE_LCSF_012:
                vlogif._LogOEC(True, _iImplErr)
            elif _iImplErr == _EFwErrorCode.FE_LCSF_013:
                vlogif._LogOEC(True, _iImplErr)
            elif _iImplErr == _EFwErrorCode.FE_LCSF_014:
                vlogif._LogOEC(True, _iImplErr)
            else:  
                vlogif._LogOEC(True, _errCode)
        else:
            _FwMain.__fwmSgltn = self
            self.__mtp  = _mtp
            self.__mrbl = _mrbl

    @property
    def lcMonitorImpl(self) -> _LcMonitorImpl:
        return None if self.__mrbl is None else self.__mrbl._lcMonitorImpl

    def StartFwMain(self, semStart_: _BinarySemaphore) -> bool:
        res = _FwTask.StartTask(self, semStart_=semStart_)
        if not res:
            vlogif._LogOEC(False, _EFwErrorCode.VUE_00002)
        else:
            res = self.isRunning
            if not res:
                vlogif._LogOEC(False, _EFwErrorCode.VUE_00003)
        return res

    def StopFwMain(self, semStop_: _BinarySemaphore =None) -> bool:
        res = _FwTask.StopTask(self, semStop_=semStop_)
        if not res:
            vlogif._LogOEC(False, _EFwErrorCode.VUE_00004)
        return res

    def FinalizeCustomSetup(self) -> bool:
        if not self._PcIsLcProxyModeNormal():
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00081)
            return False

        _tspanMS = self.__mrbl._executionProfile.runPhaseFreqMS
        while self.__mrbl._isAwaitingCustomSetup:
            _TaskUtil.SleepMS(_tspanMS)

        res = self.__mrbl._isCustomSetupDone
        if not res:
            vlogif._LogOEC(False, _EFwErrorCode.VUE_00005)
        return res

    def ProcessShutdownAction(self, eShutdownAction_: _ELcShutdownRequest, eFailedCompID_: _ELcCompID =None, frcError_: _FatalEntry =None, atask_: _AbstractTask =None):
        if (self.__mrbl is None) or (self.__mrbl._eRunnableType is None):
            return
        self.__mrbl.ProcessShutdownAction(eShutdownAction_, eFailedCompID_=eFailedCompID_, frcError_=frcError_, atask_=atask_)

    def _CleanUp(self):
        if _FwMain.__fwmSgltn is None:
            return

        _FwMain.__fwmSgltn = None

        super()._CleanUp()

        if self.__mrbl is not None:
            self.__mrbl.CleanUp()
        if self.__mtp is not None:
            self.__mtp.CleanUp()

        self.__mtp  = None
        self.__mrbl = None
