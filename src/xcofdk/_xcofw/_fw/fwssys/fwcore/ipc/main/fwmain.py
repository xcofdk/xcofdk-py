# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwmain.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from _fw.fwssys.assys.ifs.iffwmain        import _IFwMain
from _fw.fwssys.fwcore.logging            import vlogif
from _fw.fwssys.fwcore.lc.lcxstate        import _LcFailure
from _fw.fwssys.fwcore.lc.lcproxydefines  import _ELcSDRequest
from _fw.fwssys.fwcore.lc.lcmn.lcmonimpl  import _LcMonitorImpl
from _fw.fwssys.fwcore.ipc.fws.fwsmain    import _FwsMain
from _fw.fwssys.fwcore.ipc.tsk.afwtask    import _AbsFwTask
from _fw.fwssys.fwcore.ipc.tsk.fwtask     import _FwTask
from _fw.fwssys.fwcore.ipc.tsk.fwtaskprf  import _FwTaskProfile
from _fw.fwssys.fwcore.ipc.sync.semaphore import _BinarySemaphore
from _fw.fwssys.fwcore.ipc.tsk.taskutil   import _TaskUtil
from _fw.fwssys.fwcore.ipc.tsk.taskutil   import _ETaskRightFlag
from _fw.fwssys.fwcore.lc.lcdefines       import _ELcCompID
from _fw.fwssys.fwerrh.fwerrorcodes       import _EFwErrorCode
from _fw.fwssys.fwerrh.logs.errorlog      import _FatalLog

class _FwMain(_FwTask, _IFwMain):
    __slots__ = [ '__mp' , '__mr' ]
    
    __sgltn = None

    def __init__(self, lcMon_ : _LcMonitorImpl):
        self.__mp = None
        self.__mr = None
        _IFwMain.__init__(self)

        _iImplErr = None

        if _FwMain.__sgltn is not None:
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
            _FwTaskProfile._ATTR_KEY_TASK_RIGHTS             : _trm
          , _FwTaskProfile._ATTR_KEY_ON_SIZE_BLOCKING_XQUEUE : False
        }

        _tp = None

        _mrbl = _FwsMain(lcMon_)
        if _mrbl._lcMonitorImpl is None:
            _mrbl     = None
            _iImplErr = _EFwErrorCode.FE_LCSF_012

        if _iImplErr is not None:
            pass

        else:
            _tp = _FwTaskProfile(rbl_=_mrbl, tpAttrs_=_ta)
            if not _tp.isValid:
                _iImplErr = _EFwErrorCode.FE_LCSF_013

            else:
                _FwTask.__init__(self, fwtPrf_=_tp, bFwMain_=True)
                if self.taskBadge is None:
                    _myErrID = _EFwErrorCode.FE_LCSF_014
                    _FwTask.CleanUp(self)

        _ccID    = None
        _errCode = None

        if _iImplErr is not None:
            if _tp is not None:
                _tp.CleanUp()

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
            _FwMain.__sgltn = self
            self.__mp = _tp
            self.__mr = _mrbl

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

        _tspanMS = self.__mr._xcard.runPhaseFreqMS
        while self.__mr._isAwaitingCustomSetup:
            _TaskUtil.SleepMS(_tspanMS)

        res = self.__mr._isCustomSetupDone
        if not res:
            vlogif._LogOEC(False, _EFwErrorCode.VUE_00005)
        return res

    def ProcessShutdownAction(self, eShutdownAction_: _ELcSDRequest, eFailedCompID_: _ELcCompID =None, frcError_: _FatalLog =None, atask_: _AbsFwTask =None):
        if (self.__mr is None) or (self.__mr._rblType is None):
            return
        self.__mr.ProcessShutdownAction(eShutdownAction_, eFailedCompID_=eFailedCompID_, frcError_=frcError_, atask_=atask_)

    def _CleanUp(self):
        if _FwMain.__sgltn is None:
            return

        _FwMain.__sgltn = None

        super()._CleanUp()

        if self.__mr is not None:
            self.__mr.CleanUp()
        if self.__mp is not None:
            self.__mp.CleanUp()

        self.__mp = None
        self.__mr = None
