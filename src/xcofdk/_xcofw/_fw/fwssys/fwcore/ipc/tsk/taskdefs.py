# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : taskdefs.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum   import auto
from enum   import unique
from typing import Union

from _fw.fwssys.fwcore.logging import vlogif

from _fw.fwssys.fwcore.lc.lcdefines      import _ELcCompID
from _fw.fwssys.fwcore.types.aobject     import _AbsSlotsObject
from _fw.fwssys.fwcore.types.ebitmask    import _EBitMask
from _fw.fwssys.fwcore.types.commontypes import _FwIntEnum
from _fw.fwssys.fwcore.types.commontypes import _FwIntFlag
from _fw.fwssys.fwcore.types.commontypes import _CommonDefines
from _fw.fwssys.fwcore.types.commontypes import _EExecutionCmdID
from _fw.fwssys.fwcore.ipc.tsk.taskutil  import _ETaskXPhaseID
from _fw.fwssys.fwerrh.fwerrorcodes      import _EFwErrorCode

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

@unique
class _EFwsID(_FwIntEnum):
    eFwsMain    = 3750
    eFwsLogRD   = auto()
    eFwsDisp    = auto()
    eFwsProcMgr = auto()
    eFwsTmrMgr  = auto()

    @property
    def isFwsMain(self):
        return self == _EFwsID.eFwsMain

    @property
    def isFwsDisp(self):
        return self == _EFwsID.eFwsDisp

    @property
    def isFwsPMgr(self):
        return self == _EFwsID.eFwsProcMgr

    @property
    def isFwsLogRD(self):
        return self == _EFwsID.eFwsLogRD

    @property
    def isFwsTmrMgr(self):
        return self == _EFwsID.eFwsTmrMgr

@unique
class _ERblType(_FwIntEnum):
    eUserRbl      = 2750
    eUTRbl        = auto()
    eXTaskRbl     = auto()
    eMainXTaskRbl = auto()
    eFwRbl        = auto()
    eFwMainRbl    = _EFwsID.eFwsMain.value
    eFwDsprRbl    = _EFwsID.eFwsDisp.value
    eFwProcMgrRbl = _EFwsID.eFwsProcMgr.value
    eFwLogRDRbl   = _EFwsID.eFwsLogRD.value
    eFwTmrMgrRbl  = _EFwsID.eFwsTmrMgr.value

    @property
    def isUserRunnable(self):
        return not self.isFwRunnable

    @property
    def isXTaskRunnable(self):
        return (self == _ERblType.eXTaskRbl) or (self == _ERblType.eMainXTaskRbl)

    @property
    def isMainXTaskRunnable(self):
        return self == _ERblType.eMainXTaskRbl

    @property
    def isUnitTestRunnable(self):
        return self == _ERblType.eUTRbl

    @property
    def isFwRunnable(self):
        return self.value >= _ERblType.eFwRbl.value

    @property
    def isFwMainRunnable(self):
        return self == _ERblType.eFwMainRbl

    @property
    def isFwDispatcherRunnable(self):
        return self == _ERblType.eFwDsprRbl

    @property
    def isFwProcessMgrRunnable(self):
        return self == _ERblType.eFwProcMgrRbl

    @property
    def isFwLogRDRunnable(self):
        return self == _ERblType.eFwLogRDRbl

    @property
    def isFwTimerMgrRunnable(self):
        return self == _ERblType.eFwTmrMgrRbl

    @property
    def toFwcID(self) -> _EFwsID:
        _vv = self.value
        return None if _vv < _ERblType.eFwMainRbl.value else _EFwsID(_vv)

    @property
    def toLcCompID(self) -> _ELcCompID:
        if self.isMainXTaskRunnable:
            res = _ELcCompID.eMainXTask
        elif self.isXTaskRunnable:
            res = _ELcCompID.eXTask
        elif self.isFwMainRunnable:
            res = _ELcCompID.eFwMain
        elif self.isFwDispatcherRunnable:
            res = _ELcCompID.eFwDspr
        elif self.isFwProcessMgrRunnable:
            res = _ELcCompID.eProcMgr
        elif self.isFwLogRDRunnable:
            res = _ELcCompID.eFwLogRD
        elif self.isFwTimerMgrRunnable:
            res = _ELcCompID.eTmrMgr
        elif self.isFwRunnable:
            res = _ELcCompID.eFwSrv
        else:
            res = _ELcCompID.eMiscComp
        return res

@unique
class _EUTaskApiID(_FwIntEnum):
    eRunXTask               = 0
    eSetUpXTask             = auto()
    eTearDownXTask          = auto()
    eProcessInternalMessage = auto()
    eProcessExternalMessage = auto()

    @property
    def functionName(self):
        return _FwTDbEngine.GetText(_EFwTextID(self.value+_EFwTextID.eEUTaskApiID_RunXTask.value))

@unique
class _EUTaskApiFuncTag(_FwIntFlag):
    eNone = 0x0*000
    eXFTRunXTask      = (0x0001 << _EUTaskApiID.eRunXTask.value)
    eXFTSetUpXTask    = (0x0001 << _EUTaskApiID.eSetUpXTask.value)
    eXFTTearDownXTask = (0x0001 << _EUTaskApiID.eTearDownXTask.value)

    @property
    def isXTaskExecutionAPI(self):
        return self != _EUTaskApiFuncTag.eNone

    @property
    def functionName(self):
        return _EUTaskApiID(self.rightMostBitPosition).functionName

    def MapToTaskExecutionPhaseID(self) -> _ETaskXPhaseID:
        if self == _EUTaskApiFuncTag.eXFTRunXTask:
            res = _ETaskXPhaseID.eXTaskRun

        elif self == _EUTaskApiFuncTag.eXFTSetUpXTask:
            res = _ETaskXPhaseID.eXTaskSetup

        elif self == _EUTaskApiFuncTag.eXFTTearDownXTask:
            res = _ETaskXPhaseID.eXTaskTeardown

        else:
            res = _ETaskXPhaseID.eNA
        return res

    @staticmethod
    def IsNone(eApiMask_: _FwIntFlag):
        return eApiMask_==_EUTaskApiFuncTag.eNone

    @staticmethod
    def IsEnabledRunXTask(eApiMask_: _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eApiMask_, _EUTaskApiFuncTag.eXFTRunXTask)

    @staticmethod
    def IsEnabledSetUpXTask(eApiMask_: _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eApiMask_, _EUTaskApiFuncTag.eXFTSetUpXTask)

    @staticmethod
    def IsEnabledTearDownXTask(eApiMask_: _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eApiMask_, _EUTaskApiFuncTag.eXFTTearDownXTask)

    @staticmethod
    def IsEnabledApiFunction(eApiMask_: _FwIntFlag, apiFTag_: _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eApiMask_, apiFTag_)

    @staticmethod
    def DefaultApiMask():
        return _EUTaskApiFuncTag.eNone

    @staticmethod
    def AddApiFuncTag(eApiMask_: _FwIntFlag, apiFTag_ : _FwIntFlag):
        return _EBitMask.AddEnumBitFlag(eApiMask_, apiFTag_)

    @staticmethod
    def RemoveApiFuncTag(eApiMask_: _FwIntFlag, apiFTag_ : _FwIntFlag):
        return _EBitMask.RemoveEnumBitFlag(eApiMask_, apiFTag_)

@unique
class _ETaskSelfCheckResultID(_FwIntEnum):
    eScrNA    = 0
    eScrOK    = auto()
    eScrStop  = auto()
    eScrAbort = auto()

    @property
    def _isScrNOK(self):
        return self.value > _ETaskSelfCheckResultID.eScrOK.value

    @property
    def _isScrStop(self):
        return self == _ETaskSelfCheckResultID.eScrStop

    @property
    def _isScrAbort(self):
        return self == _ETaskSelfCheckResultID.eScrAbort

class _UTaskApiGuide(_AbsSlotsObject):
    __slots__ = [ '__m' , '__ht' , '__xcr' , '__xm' , '__phxr' , '__phxs' , '__phxt' ]

    def __init__(self, fwthrd_, xtXM_ : _EUTaskApiFuncTag):
        self.__m    = None
        self.__ht   = None
        self.__xm   = None
        self.__xcr  = None
        self.__phxr = None
        self.__phxs = None
        self.__phxt = None

        super().__init__()

        if fwthrd_ is None:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00245)
            self.CleanUp()
            return

        _xf = None
        if xtXM_ is not None:
            if not isinstance(xtXM_, _EUTaskApiFuncTag):
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00247)
                self.CleanUp()
                return

            _xf = _EBitMask.GetIntegerBitFlagsList(xtXM_)
            if _xf is None:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00248)
                self.CleanUp()
                return
            elif len(_xf) == 0:
                _xf = None

        self.__m  = _EUTaskApiFuncTag.DefaultApiMask()
        self.__ht = fwthrd_
        self.__xm = xtXM_

        _em  = _CommonDefines._STR_EMPTY
        _uta = fwthrd_._utConn._utAgent

        for _n, _m in _EUTaskApiFuncTag.__members__.items():
            if _m == _EUTaskApiFuncTag.eNone:
                continue
            elif _EBitMask.IsEnumBitFlagSet(self.__m, _m):
                continue
            elif _xf is not None:
                if _m.value in _xf:
                    continue

            _apiFunc = getattr(_uta._xtInst, _m.functionName, None)
            if _apiFunc is None:
                continue

            self.__m = _EUTaskApiFuncTag.AddApiFuncTag(self.__m, _m)

            if _m == _EUTaskApiFuncTag.eXFTRunXTask:
                self.runXTask = _apiFunc
            elif _m == _EUTaskApiFuncTag.eXFTSetUpXTask:
                self.setUpXTask = _apiFunc
            elif _m == _EUTaskApiFuncTag.eXFTTearDownXTask:
                self.tearDownXTask = _apiFunc
            else:
                self.__m = None
                break

        if self.runXTask is None:
            self.__m = None
        if self.__m is None:
            self.__ht = None
            self.__xm = None
            self.CleanUp()
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00249)

    @property
    def isProvidingRunXTask(self):
        return False if self.__m is None else _EUTaskApiFuncTag.IsEnabledRunXTask(self.__m)

    @property
    def isProvidingSetUpXTask(self):
        return False if self.__m is None else _EUTaskApiFuncTag.IsEnabledSetUpXTask(self.__m)

    @property
    def isProvidingTearDownXTask(self):
        return False if self.__m is None else _EUTaskApiFuncTag.IsEnabledTearDownXTask(self.__m)

    @property
    def runXTask(self):
        return self.__phxr

    @runXTask.setter
    def runXTask(self, val_):
        self.__phxr = val_

    @property
    def setUpXTask(self):
        return self.__phxs

    @setUpXTask.setter
    def setUpXTask(self, val_):
        self.__phxs = val_

    @property
    def tearDownXTask(self):
        return self.__phxt

    @tearDownXTask.setter
    def tearDownXTask(self, val_):
        self.__phxt = val_

    @property
    def apiMask(self) -> _EUTaskApiFuncTag:
        return self.__m

    @property
    def exclApiMask(self) -> _EUTaskApiFuncTag:
        return self.__xm

    @property
    def _xcmdReturn(self) -> _EExecutionCmdID:
        return self.__xcr

    @property
    def _fwThread(self):
        return self.__ht

    def _IsProvidingApiFunction(self, apiFTag_ : _EUTaskApiFuncTag):
        return False if self.__m is None else _EUTaskApiFuncTag.IsEnabledApiFunction(self.__m, apiFTag_)

    def _ToString(self, bCompact_ =True):
        if self.__m is None:
            return None

        _myTxt = _UTaskApiGuide.__ApiMask2String(self.__m)
        res = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_ApiGuide_ApiMask)
        res = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_004).format(type(self).__name__, res, _myTxt)
        if not bCompact_:
            if self.__xm is not None:
                _myTxt = _UTaskApiGuide.__ApiMask2String(self.__xm, bExcluded_=True)
                res   += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_NewlineTab) + _myTxt
        return res

    def _CleanUp(self):
        self.__m   = None
        self.__ht  = None
        self.__xm  = None
        self.__xcr = None
        self.runXTask      = None
        self.setUpXTask    = None
        self.tearDownXTask = None

    def _SetGetReturnedExecCmd(self, xcmd_ : Union[_EExecutionCmdID, None], bApplyConvertBefore_ =True) -> _EExecutionCmdID:
        if not bApplyConvertBefore_:
            res = xcmd_
        else:
            res = _EExecutionCmdID.ConvertFrom(xcmd_)
        self.__xcr = res
        return res

    @staticmethod
    def __ApiMask2String(xuApiMask_ : _EUTaskApiFuncTag, bExcluded_ =False):
        res = _EFwTextID.eMisc_Shared_ApiGuide_ExcludedApiMask if bExcluded_ else _EFwTextID.eMisc_Shared_ApiGuide_ApiMask
        res = _FwTDbEngine.GetText(res)
        res = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_005).format(res, hex(xuApiMask_))

        _myTxt = _CommonDefines._STR_EMPTY
        for _n, _m in _EUTaskApiFuncTag.__members__.items():
            if _m == _EUTaskApiFuncTag.eNone:
                continue
            if not _EBitMask.IsEnumBitFlagSet(xuApiMask_, _m):
                continue
            _myTxt += _CommonDefines._CHAR_SIGN_TAB + _m.functionName + _CommonDefines._CHAR_SIGN_LF

        if len(_myTxt) > 0:
            _myTxt = _myTxt.rstrip()
            res   += _CommonDefines._CHAR_SIGN_LF + _myTxt
        return res
