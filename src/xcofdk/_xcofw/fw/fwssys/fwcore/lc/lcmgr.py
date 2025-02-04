# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : lcmgr.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from xcofdk.fwcom.xmsgdefs import EPreDefinedMessagingID

from xcofdk._xcofw.fw.fwssys.fwcore.logging                 import logif
from xcofdk._xcofw.fw.fwssys.fwcore.logging                 import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.logging.fatalentry      import _FatalEntry
from xcofdk._xcofw.fw.fwssys.fwcore.apiimpl.fwapiconn       import _FwApiConnector
from xcofdk._xcofw.fw.fwssys.fwcore.apiimpl.fwapiimplshare  import _FwApiImplShare
from xcofdk._xcofw.fw.fwssys.fwcore.base.gtimeout           import _Timeout
from xcofdk._xcofw.fw.fwssys.fwcore.base.timeutil           import _KpiLogBook
from xcofdk._xcofw.fw.fwssys.fwcore.config.fwstartuppolicy  import _FwStartupPolicy
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.sync.syncresbase    import _PyRLock
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.sync.syncresbase    import _PySemaphore
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.atask           import _AbstractTask
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskmgr         import _TaskMgr
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil        import _TaskUtil
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcdefines            import _ELcScope
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcdefines            import _ELcCompID
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcdefines            import _LcConfig
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcdepmgr             import _LcDepManager
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcexecstate          import _ELcKpiID
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcexecstate          import _ELcExecutionState
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcexecstate          import _LcExecutionStateHistory
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcexecstate          import _LcFailure
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcguardimpl          import _LcGuardImpl
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcmgrtif             import _LcManagerTrustedIF
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcproxydefines       import _ELcShutdownRequest
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcproxyimpl          import _LcProxyImpl
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcstate              import _LcState
from xcofdk._xcofw.fw.fwssys.fwcore.lcmon.lcmonimpl         import _LcMonitorImpl
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject           import _AbstractSlotsObject
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes       import SyncPrint

from xcofdk._xcofw.fw.fwssys.fwerrh.fwerrorcodes import _EFwErrorCode

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine

from xcofdk._xcofwa.fwadmindefs import _FwAdapterConfig

class _LcManager(_FwApiConnector, _LcManagerTrustedIF):

    class _FwApiReturnRecord:
        __slots__ = [ '__mainXT' , '__syncSem' ]

        def __init__(self, mainXT_, syncSem_):
            self.__mainXT  = mainXT_
            self.__syncSem = syncSem_

        @property
        def syncSem(self) -> _PySemaphore:
            return self.__syncSem

        @property
        def mainXTask(self):
            return self.__mainXT

    class _LcMgrSetupRunner(_AbstractSlotsObject):
        __slots__ = [ '__lcMgr' , '__ppass' , '__mainXT' , '__cmdLineArgs' , '__bSetupOK' ]

        def __init__(self, lcMgr_, ppass_ : int, startOptions_ : list, mainXT_ =None):

            self.__lcMgr       = lcMgr_
            self.__ppass       = ppass_
            self.__mainXT      = mainXT_
            self.__bSetupOK    = False
            self.__cmdLineArgs = startOptions_
            super().__init__()

        def __call__(self, *args_, **kwargs_):
            self.__bSetupOK = self.__lcMgr._AsyncSetUpLcMgr(self.__ppass, self.__cmdLineArgs, mainXT_=self.__mainXT)

        def _CleanUp(self):
            self.__lcMgr       = None
            self.__ppass       = None
            self.__mainXT      = None
            self.__bSetupOK    = None
            self.__cmdLineArgs = None

        @property
        def isLcMgrSetupRunnerSucceeded(self):
            return self.__bSetupOK

    __slots__ = [  '__fwSUP'   , '__fwApiLck' , '__lcDMgr'   , '__lcGImpl'   , '__lcPxyImpl'
                , '__tgtScope' , '__mainXT'   , '__semSSLcG' , '__lcMonImpl' , '__eExecHist'
                , '__lcKPI' ]

    __theLcM     = None
    __MSG_PREFIX = _FwTDbEngine.GetText(_EFwTextID.eLcManager_MsgPrefix)

    def __init__(self, ppass_ : int, suPolicy_ : _FwStartupPolicy, startOptions_ : list, mainXT_ =None):

        self.__lcKPI     = None
        self.__fwSUP     = None
        self.__lcDMgr    = None
        self.__mainXT    = None
        self.__lcGImpl   = None
        self.__fwApiLck  = None
        self.__semSSLcG  = None
        self.__tgtScope  = None
        self.__eExecHist = None
        self.__lcPxyImpl = None
        self.__lcMonImpl = None
        _FwApiConnector.__init__(self, ppass_)
        _LcManagerTrustedIF.__init__(self, ppass_)

        if suPolicy_.isSyncPrintEnabled:
            SyncPrint.SetSyncLock(_PyRLock())

        if _LcManager.__theLcM is not None:
            self.CleanUpByOwnerRequest(ppass_)
            _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_047)

            vlogif._LogOEC(True, _EFwErrorCode.VFE_00359)
            return

        if _FwAdapterConfig._IsRedirectPyLoggingEnabled() or _FwAdapterConfig._IsLogIFDefaultConfigReleaseModeDisabled():
            self.CleanUpByOwnerRequest(ppass_)
            _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_048)

            vlogif._LogOEC(True, _EFwErrorCode.VFE_00360)
            return

        _LcManager.__theLcM = self

        _lcKPI = _KpiLogBook._GetStartupKPI()
        _lcKPI.AddKPI(_ELcKpiID.eLcConfigStart)

        self.__fwApiLck = _PyRLock()
        _FwApiConnector._FwCNSetFwApiLock(self, self.__fwApiLck)

        _tgtScope = _LcConfig.GetTargetScope()
        _errMsg  = None
        _lcfMsg  = None
        _errCode = None

        _eExpectedExecState = _ELcExecutionState.ePreConfigPhase

        self.__eExecHist = _LcFailure._GetLcExecutionStateHistory()
        if (self.__eExecHist is None) or not self.__eExecHist.IsLcExecutionStateSet(_eExpectedExecState):
            self.CleanUpByOwnerRequest(ppass_)
            _lcfMsg  = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TextID_039).format(_eExpectedExecState.compactName)
            _errMsg  = f'{_LcManager.__MSG_PREFIX}' + _lcfMsg
            _errCode = _EFwErrorCode.FE_LCSF_092

        elif (startOptions_ is not None) and not isinstance(startOptions_, list):
            self.CleanUpByOwnerRequest(ppass_)
            _lcfMsg  = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TextID_034).format(type(startOptions_).__name__)
            _errMsg  = f'{_LcManager.__MSG_PREFIX}' + _lcfMsg
            _errCode = _EFwErrorCode.FE_LCSF_093

        elif not isinstance(_tgtScope, _ELcScope):
            self.CleanUpByOwnerRequest(ppass_)
            _lcfMsg  = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TextID_035).format(type(_tgtScope).__name__)
            _errMsg  = f'{_LcManager.__MSG_PREFIX}' + _lcfMsg
            _errCode = _EFwErrorCode.FE_LCSF_094

        elif _tgtScope.isIdle:
            self.CleanUpByOwnerRequest(ppass_)
            _lcfMsg  = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TextID_036).format(_tgtScope.value, _tgtScope.compactName)
            _errMsg  = f'{_LcManager.__MSG_PREFIX}' + _lcfMsg
            _errCode = _EFwErrorCode.FE_LCSF_095

        else:
            _myGuard = _LcGuardImpl(self._myPPass, self)

            if _LcFailure.IsLcNotErrorFree():
                _myGuard.CleanUpByOwnerRequest(ppass_)
                self.CleanUpByOwnerRequest(ppass_)
            else:
                self.__lcKPI   = _lcKPI
                self.__fwSUP   = suPolicy_
                self.__lcGImpl = _myGuard

        if (_errMsg is not None) or _LcFailure.IsLcNotErrorFree():
            if _LcFailure.IsLcErrorFree():
                if _errCode is None:
                    _errCode = _EFwErrorCode.FE_LCSF_049
                _LcFailure.CheckSetLcSetupFailure(_errCode)

            if _errMsg is not None:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00361)

    def _IsLcErrorFree(self):
        if _LcManager.__theLcM is None:
            return _LcFailure.IsLcErrorFree()

        with self.__fwApiLck:
            res = _LcFailure.IsLcErrorFree()
            if res:
                if self.__lcGImpl is not None:
                    res = not self.__lcGImpl.hasLcAnyFailureState
            return res

    def _IsLcShutdownEnabled(self):
        if _LcManager.__theLcM is None:
            return False
        if not _LcConfig.IsTargetScopeIPC():
            return False

        with self.__fwApiLck:
            return (self.__lcMonImpl is not None) and self.__lcMonImpl.isLcShutdownEnabled

    def _IsXTaskRunning(self, xtUID_ : int):
        if _LcManager.__theLcM is None:
            return False
        if not _LcConfig.IsTargetScopeIPC():
            return False

        if isinstance(xtUID_, EPreDefinedMessagingID) and xtUID_==EPreDefinedMessagingID.MainTask:
            _mt = _LcManager.__GetMainXTask()
            return (_mt is not None) and _mt.isRunning

        with self.__fwApiLck:
            res     = False
            _tskMgr = _TaskMgr()

            _bOK = self.__lcMonImpl is not None
            _bOK = _bOK and not self.__lcMonImpl.isLcShutdownEnabled
            _bOK = _bOK and (_tskMgr is not None)
            _bOK = _bOK and (self.__lcPxyImpl is not None) and self.__lcPxyImpl._PxyIsLcProxyModeNormal()
            if not _bOK:
                pass
            else:
                _myTsk      = _tskMgr._GetTask(xtUID_, bDoWarn_=False)
                _myTskBadge = None if _myTsk is None else _myTsk.taskBadge
                if (_myTskBadge is None) or not _myTskBadge.isDrivingXTask:
                    pass
                else:
                    res = _myTsk._xtaskConnector._isRunning
            return res

    def _StopFW(self) -> bool:
        if _LcManager.__theLcM is None:
            return True

        with self.__fwApiLck:
            _bDoStop = False if self.__lcMonImpl.isLcShutdownEnabled else True
            if _bDoStop:
                logif._LogInfo(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TextID_012))
                self.__StopFW(bInternalRequest_=False)
            return True

    def _JoinFW(self) -> bool:
        logif._LogInfo(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TextID_043))
        res = self.__JoinFW(bInternalRequest_=False)

        _mainXT = self.__mainXT
        if _mainXT is None:
            _mainXT = _LcManager.__GetMainXTask()

        if _mainXT is not None:
            _mainXT.DetachFromFW()

        return res

    def _GetXTask(self, xtUID_ : int =0):
        if not _LcConfig.IsTargetScopeIPC():
            return None
        if _LcManager.__theLcM is None:
            return None
        if xtUID_ == 0:
            return self._GetCurXTask()

        with self.__fwApiLck:
            res     = None
            _tskMgr = _TaskMgr()

            _bOK = True
            _bOK = _bOK and not self.__lcMonImpl.isLcShutdownEnabled
            _bOK = _bOK and (_tskMgr is not None)
            _bOK = _bOK and (self.__lcPxyImpl is not None) and self.__lcPxyImpl._PxyIsLcProxyModeNormal()
            if not _bOK:
                logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TextID_045).format(xtUID_))
            else:
                _myTsk      = _tskMgr._GetTask(xtUID_, bDoWarn_=False)
                _myTskBadge = None if _myTsk is None else _myTsk.taskBadge
                if (_myTskBadge is None) or not _myTskBadge.isDrivingXTask:
                    pass
                else:
                    res = _myTsk._xtaskConnector._connectedXTask
                if res is None:
                    logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TextID_046).format(xtUID_))
                elif res.isDetachedFromFW:
                    logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TextID_047).format(res.xtaskUniqueID))
            return res

    def _GetCurXTask(self):
        if not _LcConfig.IsTargetScopeIPC():
            return None
        if _LcManager.__theLcM is None:
            return None

        with self.__fwApiLck:
            res     = None
            _tskMgr = _TaskMgr()

            _bOK = True
            _bOK = _bOK and not self.__lcMonImpl.isLcShutdownEnabled
            _bOK = _bOK and (_tskMgr is not None)
            _bOK = _bOK and (self.__lcPxyImpl is not None) and self.__lcPxyImpl._PxyIsLcProxyModeNormal()
            if not _bOK:
                logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TextID_001))
            else:
                _curTsk = _tskMgr._GetCurTask()
                _myTskBadge = None if _curTsk is None else _curTsk.taskBadge
                if (_myTskBadge is None) or not _myTskBadge.isDrivingXTask:
                    pass
                else:
                    res = _curTsk._xtaskConnector._connectedXTask
                if res is None:
                    logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TextID_002))
                elif res.isDetachedFromFW:
                    logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TextID_003).format(res.xtaskUniqueID))
            return res

    def _TIFPreCheckLcFailureNotification(self, eFailedCompID_ : _ELcCompID):
        res = False
        if (self.__eExecHist is None) or (_TaskMgr() is None):
            pass
        elif not self.__eExecHist.hasPassedCustomSetupPhase:
            pass 
        elif self.__lcPxyImpl._PxyIsLcProxyModeShutdown():
            pass 
        else:
            res = True
        return res

    def _TIFOnLcFailure(self, eFailedCompID_: _ELcCompID, frcError_: _FatalEntry, atask_: _AbstractTask =None, bPrvRequestReply_ =True):

        if not self._TIFPreCheckLcFailureNotification(eFailedCompID_):
            return

        self.__lcPxyImpl._PxyProcessShutdownRequest( _ELcShutdownRequest.eFailureHandling
                                                   , eFailedCompID_=eFailedCompID_
                                                   , frcError_=frcError_
                                                   , atask_=atask_
                                                   , bPrvRequestReply_=bPrvRequestReply_)

    def _TIFOnLcShutdownRequest(self, eShutdownRequest_: _ELcShutdownRequest) -> bool:
        if (_LcManager.__theLcM is None) or (self.__lcPxyImpl is None):
            return False

        if eShutdownRequest_.isFailureHandling:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00362)
            return False

        _curSDR = self.__lcMonImpl.eCurrentShutdownRequest

        if eShutdownRequest_.isShutdown:
            if not _curSDR.isShutdown:
                self.__lcPxyImpl._PxyProcessShutdownRequest(_ELcShutdownRequest.eShutdown, bPrvRequestReply_=False)

        else:
            if _curSDR is None:
                self.__StopFW()
        return True

    def _TIFFinalizeStopFW(self, bCleanUpLcMgr_ : bool):
        if _LcManager.__theLcM is None:
            return False

        _mainXT = self.__mainXT
        if _mainXT is None:
            _mainXT = _LcManager.__GetMainXTask()

        if _mainXT is not None:
            if _mainXT.isRunning:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00363)

        if self.__lcPxyImpl is not None:
            self.__lcPxyImpl._PxyStopFwMain()

            _xtUID = None if _mainXT is None else _mainXT.xtaskUniqueID

            _srt = self.__lcPxyImpl._PxyJoinFwMain(mainXTUID_=_xtUID)

            if _srt is not None:
                _NUM = len(_srt)

                _tiEMThrd = None
                for _ii in range(_NUM):
                    _ti = _srt[_ii]

                    if not _ti.isValid:
                        _srt[_ii] = None
                        continue

                    if _ti.isEnclosingPyThread and _TaskUtil.IsMainPyThread(_ti.linkedPyThread):
                        _tiEMThrd = _ti
                        _srt[_ii] = None
                        continue

                    _ti.JoinTask()
                    _ti.CleanUp()
                    _srt[_ii] = None
                _srt.clear()

                if _tiEMThrd is not None:
                    _bJOIN_MANAGED_BY_LCMGR = True

                    if not _bJOIN_MANAGED_BY_LCMGR:
                        _tout = _Timeout.TimespanToTimeout(2000)
                        while True:
                            if _tiEMThrd.JoinTask(timeout_=_tout):
                                break
                        _tout.CleanUp()
                    else:
                        _totalTimeMS   = 0
                        _timeSpanMS    = 20
                        _tiEMThrdUName = _tiEMThrd.taskUniqueName if _tiEMThrd.linkedExecutable is None else _tiEMThrd.linkedExecutable.executableName

                        try:
                            while not (_tiEMThrd.isDone or _tiEMThrd.isFailed):
                                if not _tiEMThrd.isValid:
                                    break

                                _TaskUtil.SleepMS(_timeSpanMS)
                                _totalTimeMS += _timeSpanMS

                        except KeyboardInterrupt:
                            pass
                        except BaseException as xcp:
                            pass

                    _tiEMThrd.CleanUp()

        if (self.__curLcScope is None) or (self.__curLcScope.lcTransitionalOrder < _ELcScope.eSemiIPC.value):
            _curLcScope = None if self.__curLcScope is None else self.__curLcScope.compactName
        else:
            for _ii in range((self.__curLcScope.value-1), (_ELcScope.eIdle.value-1), -1):
                self.__UpdateScope(srcScope_=self.__curLcScope, dstScope_=_ELcScope(_ii))

        if self.__lcGImpl is not None:
            if self.__lcGImpl._isRunning:
                if self.__semSSLcG is None:
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00364)
                else:
                    _bSTOP_SyNC_NEEDED = False

                    _semSS = self.__semSSLcG if _bSTOP_SyNC_NEEDED else None
                    self.__lcGImpl._Stop(_semSS)
                    if _semSS is not None:
                        _semSS.acquire()

        self.__eExecHist._AddExecutionState(_ELcExecutionState.eStopPassed, self)

        if bCleanUpLcMgr_:
            if not self.__lcState.isLcStopped:
                if not self.__lcState.isLcFailed:
                    self.__SetLcOpState(_ELcCompID.eLcMgr, False)

            self.CleanUpByOwnerRequest(self._myPPass)

        return True

    @staticmethod
    def _CreateLcMgr(startupPolicy_ : _FwStartupPolicy, startOptions_ : list):
        if _LcManager.__theLcM is not None:
            return None

        res = _LcManager.__DoCreateLcMgr(startupPolicy_, startOptions_)
        if res is None:
            _LcFailure._PrintLcResult(bReinforcePrint_=False)
        return res

    @staticmethod
    def _CreateStartupPolicy(ppass_ : int) -> _FwStartupPolicy:
        _STARTUP_FAILURE_ERR_MSG = 'Encountered severe error while preparing for startup.'

        _dbCreateSt = _FwTDbEngine.GetCreateStatus()
        if not _dbCreateSt.isTDBIdle:
            if not _dbCreateSt.isTDBCreated:
                _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_096, errMsg_=_STARTUP_FAILURE_ERR_MSG)
                return None

        _lcKPI = _KpiLogBook._CreateStartupKPI(_ELcKpiID.eFwStartRequest)
        if not _lcKPI.isValid:
            _lcKPI.CleanUp()
            _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_097, errMsg_=_STARTUP_FAILURE_ERR_MSG)
            return None

        res = _FwStartupPolicy(ppass_)

        if not res.isValid:
            res.CleanUpByOwnerRequest(ppass_)
            res = None
            _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_098, errMsg_=_STARTUP_FAILURE_ERR_MSG)

        elif _dbCreateSt.isTDBIdle:
            _FwTDbEngine._CreateDB(res.isPackageDist)

            _dbCreateSt = _FwTDbEngine.GetCreateStatus()
            if not _dbCreateSt.isTDBCreated:
                res.CleanUpByOwnerRequest(ppass_)
                res = None
                _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_099, errMsg_=_STARTUP_FAILURE_ERR_MSG)

        if res is not None:
            _dbFirstFetchTS = None
            _dbCreateTS     = None
            _dbFirstFetchTS, _dbCreateTS = _FwTDbEngine._GetDBTimestamps()
            _lcKPI.AddKPI(_ELcKpiID.eTextDBFirstFetch, usTimeTicksKPI_=_dbFirstFetchTS)
            _lcKPI.AddKPI(_ELcKpiID.eTextDBCreate, usTimeTicksKPI_=_dbCreateTS)
        return res

    def _AsyncSetUpLcMgr(self, ppass_ : int, startOptions_ : list, mainXT_ =None):
        return self.__SetUp(ppass_, startOptions_, mainXT_=mainXT_)

    def _ToString(self):
        if self.__lcDMgr is None:
            res = None
        else:
            _LC_STATE_COMPACT_OUTPUT = True
            res = _FwTDbEngine.GetText(_EFwTextID.eLcManager_ToString)
            res = res.format(self.__tgtScope.compactName, self.__curLcScope.compactName, self.__lcState.ToString(_LC_STATE_COMPACT_OUTPUT))
        return res

    def _CleanUpByOwnerRequest(self):
        if _LcManager.__theLcM is not None:
            if id(_LcManager.__theLcM) == id(self):
                _LcManager.__theLcM = None
                _FwApiConnector._CleanUpByOwnerRequest(self)

        if self.__lcDMgr is not None:
            if self.__lcPxyImpl is not None:
                self.__lcPxyImpl.CleanUpByOwnerRequest(self._myPPass)
            self.__lcDMgr.CleanUpByOwnerRequest(self._myPPass)

        if self.__lcGImpl is not None:
            self.__lcGImpl.CleanUpByOwnerRequest(self._myPPass)

        if self.__lcMonImpl is not None:
            self.__lcMonImpl.CleanUpByOwnerRequest(self._myPPass)

        if self.__fwSUP is not None:
            self.__fwSUP.CleanUpByOwnerRequest(self._myPPass)

        if self.__lcKPI is not None:
            self.__lcKPI.CleanUp()

        if self.__eExecHist is not None:
            self.__lcKPI     = None
            self.__fwSUP     = None
            self.__lcDMgr    = None
            self.__mainXT    = None
            self.__lcGImpl   = None
            self.__fwApiLck  = None
            self.__semSSLcG  = None
            self.__tgtScope  = None
            self.__eExecHist = None
            self.__lcPxyImpl = None
            self.__lcMonImpl = None
            vlogif._PrintVSummary(bPrint_=True)

    @property
    def __lcState(self) -> _LcState:
        return None if self.__lcGImpl is None else self.__lcGImpl._GetLcState(bypassApiLock_=True)

    @property
    def __curLcScope(self) -> _ELcScope:
        return None if self.__lcDMgr is None else self.__lcDMgr.lcScope

    @staticmethod
    def __DoCreateLcMgr(startupPolicy_ : _FwStartupPolicy, startOptions_ : list):
        if _LcManager.__theLcM is not None:
            return None

        _lcKPI = _KpiLogBook._GetStartupKPI()

        if not (isinstance(startupPolicy_, _FwStartupPolicy) and startupPolicy_.isValid):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00365)
            return None

        if not (isinstance(_lcKPI, _KpiLogBook) and _lcKPI.isValid):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00366)
            return None

        _kpiTD = _lcKPI.GetKpiTimeDelta(_ELcKpiID.eTextDBCreate)
        if _kpiTD is not None:
            vlogif._LogKPI(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TextID_004).format(_kpiTD.timeParts))
            _kpiTD.CleanUp()

        _ppass = startupPolicy_._myPPass

        _LcFailure._ClearInstance()

        _eExecHist = _LcFailure._GetLcExecutionStateHistory()
        if _eExecHist is not None:
            _eExecHist.CleanUpByOwnerRequest(_eExecHist._myPPass)
            _eExecHist = None

        _eExecHist = _LcExecutionStateHistory(_ppass)
        if not _eExecHist.IsLcExecutionStateSet(_ELcExecutionState.ePreConfigPhase):
            _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_104, errMsg_=_EFwTextID.eLogMsg_LcManager_TextID_038)
            _eExecHist.CleanUpByOwnerRequest(_ppass)
            return None
        _LcFailure._SetLcExecutionStateHistory(_eExecHist)

        _lcmgr = _LcManager(_ppass, startupPolicy_, startOptions_, mainXT_=None)

        if not _eExecHist.isErrorFree:
            _lcmgr.CleanUpByOwnerRequest(_ppass)
            return None

        _lcMgrSetupRunner  = _LcManager._LcMgrSetupRunner(_lcmgr, _ppass, startOptions_, mainXT_=None)
        _bLcGuardStarted   = _lcmgr.__StartLcGuard(_lcMgrSetupRunner)

        _bAsyncSetupOK = _bLcGuardStarted and _LcFailure.IsSetupPhasePassed()
        _bAsyncSetupOK = _bAsyncSetupOK   and _lcMgrSetupRunner.isLcMgrSetupRunnerSucceeded
        _bAsyncSetupOK = _bAsyncSetupOK   and _eExecHist.isErrorFree
        _bAsyncSetupOK = _bAsyncSetupOK   and _eExecHist.hasPassedSetupPhase
        _bAsyncSetupOK = _bAsyncSetupOK   and _eExecHist.hasReachedRuntimePhase

        _bStopFW = False

        if not _bAsyncSetupOK:
            _bStopFW = _bLcGuardStarted
        elif not _lcmgr.__CheckStartMainXT(True):
            _bStopFW = True

        res = _lcmgr.__DetermineAsyncStartupResult(_bAsyncSetupOK, True)
        if res is None:
            _bStopFW = True

        if _bStopFW:
            _lcmgr.__StopFW()
            _lcmgr.__JoinFW()
        return res

    @staticmethod
    def __GetMainXTask():
        return _FwApiImplShare._GetMainXTask()

    def __SetLcOpState( self, eLcCompID_ : _ELcCompID, bStartStopFlag_ : bool, atask_ : _AbstractTask =None) -> bool:
        if self.__lcGImpl is None:
            res = False
        else:
            res = self.__lcGImpl._SetLcOperationalState(eLcCompID_, bStartStopFlag_, atask_=atask_)
        return res

    def __BoostFW(self, reinjectCurScope_: bool =False) -> bool:
        self.__lcKPI.AddKPI(_ELcKpiID.eLcConfigEnd)

        self.__lcKPI.AddKPI(_ELcKpiID.eLcBoostStart)
        self.__eExecHist._AddExecutionState(_ELcExecutionState.eSemiBoostPhase, self)

        res = self.__BoostSemiIPC(reinjectCurScope_=reinjectCurScope_)
        res = res and _LcFailure.IsLcErrorFree()
        res = res and self.__eExecHist.IsLcExecutionStateSet(_ELcExecutionState.eSemiBoostPhase)

        if res:
            self.__eExecHist._AddExecutionState(_ELcExecutionState.eFullBoostPhase, self)

            res = self.__BoostFullIPC()
            res = res and _LcFailure.IsLcErrorFree()
            res = res and self.__eExecHist.IsLcExecutionStateSet(_ELcExecutionState.eFullBoostPhase)

        if not res:
            pass
        else:
            res = self.__curLcScope == self.__tgtScope
            if not res:
                _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_050)
            else:
                res = self.__lcPxyImpl._PxySyncStarFwMainByAsynStartup()
                res = res and _LcFailure.IsLcErrorFree()

        if not res:
            if _LcFailure.IsLcErrorFree():
                _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_051)
        else:
            self.__lcGImpl._SetLcMonitorImpl(self.__lcMonImpl)
            _TaskMgr()._SetLcMonitorImpl(self.__lcMonImpl)
        return res

    def __BoostSemiIPC(self, reinjectCurScope_ : bool =False) -> bool:
        _NO_SUPPORT_FOR_INTERMEDIATE_SCOPES_AT_RUNTIME = True
        if _NO_SUPPORT_FOR_INTERMEDIATE_SCOPES_AT_RUNTIME:
            if reinjectCurScope_:
                reinjectCurScope_ = False

        eFinalScope = _LcConfig.GetTargetScope()

        _bBadUse = False
        _bBadUse = _bBadUse or (eFinalScope.lcTransitionalOrder < _ELcScope.eSemiIPC.value)
        _bBadUse = _bBadUse or not self.__curLcScope.isPreIPC
        _bBadUse = _bBadUse or not self.__lcState.isLcStarted
        _bBadUse = _bBadUse or self.__lcState.hasLcAnyFailureState
        if _bBadUse:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00367)

            _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_052)
            return False

        if reinjectCurScope_:
            if not self.__UpdateScope(self.__curLcScope, self.__curLcScope, bForceReinject_=True):
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00368)
                return False

        if self.__tgtScope.lcTransitionalOrder < _ELcScope.eSemiIPC.value:
            self.__tgtScope = _ELcScope.eSemiIPC

        _bFinalScopeSemiIPC = eFinalScope.isSemiIPC

        res = self.__UpdateScope(self.__curLcScope, self.__tgtScope, bFinalize_=_bFinalScopeSemiIPC)
        if res:
            res = res and self.__curLcScope.isSemiIPC
            res = res and self.__lcState.isLcStarted
            res = res and self.__lcState.isTaskManagerStarted
            if not res:
                _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_053)
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00369)

        if res:
            if _bFinalScopeSemiIPC:
                self.__CreateLcProxy()

                res = res and _LcFailure.IsLcErrorFree()
                res = res and self.__lcPxyImpl is not None
                res = res and self.__lcState.isLcStarted
                res = res and self.__lcState.isTaskManagerStarted
                res = res and self.__lcState.isFwMainStarted
                if not res:
                    if _LcFailure.IsLcErrorFree():
                        _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_054)
                        vlogif._LogOEC(True, _EFwErrorCode.VFE_00370)
        return res

    def __BoostFullIPC(self) -> bool:
        eFinalScope = _LcConfig.GetTargetScope()

        _bBadUse = False    or _LcFailure.IsLcNotErrorFree()
        _bBadUse = _bBadUse or not eFinalScope.isFullIPC
        _bBadUse = _bBadUse or not self.__curLcScope.isSemiIPC
        _bBadUse = _bBadUse or not self.__lcState.isLcStarted
        _bBadUse = _bBadUse or not self.__lcState.isTaskManagerStarted
        _bBadUse = _bBadUse or self.__lcState.hasLcAnyFailureState
        if _bBadUse:
            if _LcFailure.IsLcErrorFree():
                _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_056)
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00371)
            return False

        if self.__tgtScope != eFinalScope:
            self.__tgtScope = eFinalScope

        res = self.__UpdateScope(self.__curLcScope, self.__tgtScope, bFinalize_=True)

        res = res and _LcFailure.IsLcErrorFree()
        res = res and self.__curLcScope.isFullIPC
        res = res and self.__lcState.isLcStarted
        res = res and self.__lcState.isTaskManagerStarted

        if not res:
            if _LcFailure.IsLcErrorFree():
                _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_057)
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00372)
            return False

        self.__CreateLcProxy()

        res = res and _LcFailure.IsLcErrorFree()
        res = res and self.__lcPxyImpl is not None
        res = res and self.__lcState.isLcStarted
        res = res and self.__lcState.isTaskManagerStarted
        res = res and self.__lcState.isFwMainStarted

        if not res:
            if _LcFailure.IsLcErrorFree():
                _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_058)

            if self.__lcPxyImpl is None:
                pass
            else:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00373)
        return res

    def __StopFW(self, bInternalRequest_ =True) -> bool:
        if _LcManager.__theLcM is None:
            return False

        if not bInternalRequest_:
            if self.__lcMonImpl is not None:
                self.__eExecHist._AddExecutionState(_ELcExecutionState.eStopPhase, self)

                self.__lcMonImpl._EnableCoordinatedShutdown()
                return True

        vlogif._LogNewline()
        vlogif._LogNewline()

        self.__eExecHist._AddExecutionState(_ELcExecutionState.eStopPhase, self)

        res = self.__lcPxyImpl is not None
        if not res:
            pass
        elif self.__lcMonImpl.eCurrentShutdownRequest is not None:
            pass
        else:
            self.__lcPxyImpl._PxyProcessShutdownRequest(_ELcShutdownRequest.ePreShutdown, bPrvRequestReply_=False)
        return res

    def __JoinFW(self, bInternalRequest_ =True) -> bool:
        if _LcManager.__theLcM is None:
            return True

        _bDoJoin            = False
        _bWasLcNotErrorFree = _LcFailure.IsLcNotErrorFree()

        if self.__lcGImpl is None:
            pass
        elif self.__lcMonImpl is None:
            pass
        else:
            _bDoJoin = True

            with self.__fwApiLck:
                if self.__lcMonImpl._isCurrentThreadAttachedToFW:
                    _bDoJoin = False
                    logif._LogErrorEC(_EFwErrorCode.UE_00103, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TextID_010).format(_TaskUtil.GetCurPyThread().name))
                elif not bInternalRequest_:
                    if not self.__eExecHist.IsLcExecutionStateSet(_ELcExecutionState.eStopPhase):
                        self.__StopFW(bInternalRequest_=False)

            if _bDoJoin:
                logif._LogInfo(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TextID_011))
                try:
                    self.__eExecHist._AddExecutionState(_ELcExecutionState.eJoinPhase, self)

                    _TaskUtil.SleepMS(200)
                    self.__lcGImpl._Join()

                    self.__eExecHist._AddExecutionState(_ELcExecutionState.eJoinPassed, self)
                except KeyboardInterrupt:
                    pass 
                except BaseException as xcp:
                    pass 

        if not self.__lcState.isLcStopped:
            if not self.__lcState.isLcFailed:
                self.__SetLcOpState(_ELcCompID.eLcMgr, False)

        self.CleanUpByOwnerRequest(self._myPPass)

        if _bDoJoin:
            _LcFailure._PrintLcResult()

        res = _LcFailure.IsLcErrorFree() or _bWasLcNotErrorFree
        return res

    def __SetUp(self, ppass_: int, startOptions_: list, mainXT_ =None):

        if _LcFailure.IsLcNotErrorFree():
            _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_059)
            return False

        if not self.__eExecHist.IsLcExecutionStateSet(_ELcExecutionState.ePreConfigPhase):
            _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_060)
            return False

        self.__eExecHist._AddExecutionState(_ELcExecutionState.eConfigPhase, self)

        _tgtScope = _LcConfig.GetTargetScope()
        _lcdm = _LcDepManager(ppass_, self.__fwSUP, self.__lcGImpl, startOptions_)

        res = True
        res = res and _LcFailure.IsLcErrorFree()
        res = res and (_lcdm.lcScope is not None)
        res = res and _lcdm.lcScope.isPreIPC
        res = res and self.__SetLcOpState(_ELcCompID.eLcMgr, True)

        if not res:
            if _LcFailure.IsLcErrorFree():
                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TextID_013).format(_FwTDbEngine.GetText(_EFwTextID.eMisc_Async))
                _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_102, errMsg_=_errMsg)
            _lcdm.CleanUpByOwnerRequest(ppass_)
            return False

        _rclTSMS = _lcdm.subsystemConfigSupervisor.subsystemConfigIPC.lcGuardRunCycleLoopTimespanMS
        self.__lcGImpl._UpdateRunCycleLoopTimespanMS(_rclTSMS)

        self.__mainXT   = mainXT_
        self.__lcDMgr   = _lcdm
        self.__tgtScope = _ELcScope(_tgtScope.value)

        vlogif._LogNewline()
        vlogif._LogNewline()

        res = True
        res = res and self.__BoostFW()                 
        res = res and _LcFailure.IsLcErrorFree()       
        res = res and self.__lcDMgr is not None        
        res = res and self.__lcGImpl is not None       
        res = res and self.__lcGImpl.isLcCoreOperable  

        if not res:
            if _LcFailure.IsLcErrorFree():
                _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_061)

        else:
            self.__lcKPI.AddKPI(_ELcKpiID.eLcBoostEnd)
            self.__lcKPI.AddKPI(_ELcKpiID.eLcCustomSetupStart)

            self.__eExecHist._AddExecutionState(_ELcExecutionState.eCustomSetupPhase, self)
            res = self.__lcPxyImpl._PxyFinalizeSetup()
            res = res and _LcFailure.IsLcErrorFree()

            if not res:
                if _LcFailure.IsLcErrorFree():
                    _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_062)
        if not res:
            logif._XLogFatalEC(_EFwErrorCode.FE_00928, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TextID_017))
        else:
            self.__lcKPI.AddKPI(_ELcKpiID.eLcCustomSetupEnd)
            self.__eExecHist._AddExecutionState(_ELcExecutionState.eSetupPassed, self)
            self.__eExecHist._AddExecutionState(_ELcExecutionState.eRuntimePhase, self)
            print()

            if not self.__fwSUP.isReleaseModeEnabled:
                self.__PrintLcKPI()

            _kpiTD = self.__lcKPI.GetKpiTimeDelta(_ELcKpiID.eTextDBCreate)
            logif._LogKPI(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TextID_004).format(_kpiTD.timeParts))
            _kpiTD.CleanUp()

            _kpiTD = self.__lcKPI.GetKpiTimeDelta(_ELcKpiID.eLcCustomSetupEnd, _ELcKpiID.eLcConfigStart)
            logif._LogKPI(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TextID_018).format(_kpiTD.timeParts))
            _kpiTD.CleanUp()

            if not logif._IsReleaseModeEnabled():
                print()
                print()

        _vffe = vlogif._GetFirstFatalError()
        if not res:
            if _vffe is not None:
                if _LcFailure.IsLcErrorFree():
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00374)
        elif _vffe is not None:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00375)
        return res

    def __PrintLcKPI(self, bForce_ =False):
        if (self.__lcKPI is None) or not self.__lcKPI.isValid:
            return
        if (self.__fwSUP is None) or not self.__fwSUP.isValid:
            return
        if self.__fwSUP.isPackageDist and not bForce_:
            return
        _myTxt = self.__lcKPI.ToString()
        if len(_myTxt) > 0:
            logif._LogKPI(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TextID_014).format(_myTxt))

    def __UpdateScope(self, srcScope_ : _ELcScope, dstScope_ : _ELcScope, bForceReinject_ =False, bFinalize_ =False):
        if _LcFailure.IsLcNotErrorFree() and not _LcFailure.IsConfigPhasePassed():
            return True

        res= True
        if srcScope_ == dstScope_:
            if not (bForceReinject_ or bFinalize_):
                pass
            elif bForceReinject_:
                _ures = self.__lcDMgr.UpdateLcScope(dstScope_, bForceReinject_=True)
                res = _ures.isOK
            else:
                _ures = self.__lcDMgr.UpdateLcScope(dstScope_, bFinalize_=True)
                res = _ures.isOK
        else:
            _bTMgrAvailable = None
            if dstScope_.lcTransitionalOrder < srcScope_.lcTransitionalOrder:
                if srcScope_ == _ELcScope.eSemiIPC:
                    _bTMgrAvailable = False
                _nextScopeVal = srcScope_.value - 1
            else:
                _nextScopeVal = srcScope_.value + 1
                if _nextScopeVal == _ELcScope.eSemiIPC.value:
                    _bTMgrAvailable = True

            if _bTMgrAvailable is not None:
                if not _bTMgrAvailable:
                    if not self.__lcState.isTaskManagerFailed:
                        self.__SetLcOpState(_ELcCompID.eTMgr, False)

            _tgtScope = _ELcScope(_nextScopeVal)
            _ures = self.__lcDMgr.UpdateLcScope(_tgtScope)
            res = _ures.isOK
            if res and (_bTMgrAvailable is not None):
                if _bTMgrAvailable:
                    res = _TaskMgr() is not None
                    if not res:
                        vlogif._LogOEC(True, _EFwErrorCode.VFE_00376)
                    elif not self.__SetLcOpState(_ELcCompID.eTMgr, True):
                        res = False
                        vlogif._LogOEC(True, _EFwErrorCode.VFE_00377)
        if not res:
            if _LcFailure.IsLcErrorFree():
                if not _LcFailure.IsSetupPhasePassed():
                    _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_063)
        return res

    def __CreateLcProxy(self):
        _lcMon  = _LcMonitorImpl(self._myPPass, self.__eExecHist)
        _bMonOK = _lcMon.isValid and not _lcMon.isDummyMonitor

        if not _bMonOK:
            _lcMon.CleanUpByOwnerRequest(self._myPPass)
            _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_070, errMsg_=_EFwTextID.eLogMsg_LcManager_TextID_019)
            return

        self.__lcMonImpl = _lcMon
        _lcPxyImpl = _LcProxyImpl(self._myPPass, self.__curLcScope, self.__lcGImpl, self.__lcMonImpl, self.__lcDMgr.fwConfig.fwStartupConfig, None)

        if _lcPxyImpl._PxyGetTaskMgr() is None:
            _lcPxyImpl.CleanUpByOwnerRequest(self._myPPass)
            _lcPxyImpl = None

            if self.__lcState.isTaskManagerStarted:
                self.__SetLcOpState(_ELcCompID.eTMgr, False)

            if _LcFailure.IsLcErrorFree():
                _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_071, errMsg_=_EFwTextID.eLogMsg_LcManager_TextID_020)

        elif not self.__SetLcOpState(_ELcCompID.eFwMain, True):
            _lcPxyImpl.CleanUpByOwnerRequest(self._myPPass)
            _lcPxyImpl = None

            if _LcFailure.IsLcErrorFree():
                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TextID_021).format(_ELcCompID.eFwMain.compactName)
                _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_001, errMsg_=_errMsg)

        if _lcPxyImpl is None:
            self.__lcMonImpl.CleanUpByOwnerRequest(self._myPPass)
            self.__lcMonImpl = None
        else:
            self.__lcPxyImpl = _lcPxyImpl

    def __StartLcGuard(self, lcMgrSetupRunner_):
        if lcMgrSetupRunner_ is None:
            _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_064)

            vlogif._LogOEC(True, _EFwErrorCode.VFE_00378)
            return False

        self.__semSSLcG = _PySemaphore(1)
        self.__semSSLcG.acquire()

        if not self.__lcGImpl._Start(self.__semSSLcG, lcMgrSetupRunner_):
            res = False
            if _LcFailure.IsLcErrorFree():
                _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_002, errMsg_=_EFwTextID.eLogMsg_LcManager_TextID_022)
        else:
            self.__semSSLcG.acquire()

            if not self.__lcGImpl._isRunning:
                res = False
                if _LcFailure.IsLcErrorFree():
                    _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_065)
            else:
                res = True
        return res

    def __CheckStartMainXT(self, bSkipAutoStartMainXT_ : bool =True) -> bool:
        if not (self.__eExecHist.hasPassedSetupPhase and self.__eExecHist.hasReachedRuntimePhase):
            return False

        _mainXT = self.__mainXT

        if _mainXT is None:
            self._FwCNPublishFwApiConnector()
            return True

        if bSkipAutoStartMainXT_:
            self._FwCNPublishFwApiConnector()
            return True

        self.__eExecHist._AddExecutionState(_ELcExecutionState.eMxuAutoStartPhase, self)
        self.__lcKPI.AddKPI(_ELcKpiID.eMxuStartStart)

        res = self.__StartMainXTByAsyncStartup(_mainXT)
        return res

    def __StartMainXTByAsyncStartup(self, mainXT_, bRequestByResumeAutoStart_ =False):
        if not (self.__eExecHist.hasPassedSetupPhase and self.__eExecHist.hasReachedRuntimePhase):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00379)
            return False
        if not (self.__eExecHist.IsLcExecutionStateSet(_ELcExecutionState.eMxuAutoStartPhase) or self.__eExecHist.IsLcExecutionStateSet(_ELcExecutionState.eMxuPostStartPhase)):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00380)
            return False

        _mxt = mainXT_

        if _mxt.xtaskProfile.isSynchronousTask:
            if not self.__SetLcOpState(_ELcCompID.eMainXTask, True):
                logif._LogFatalEC(_EFwErrorCode.FE_00040, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TextID_023).format(2))
                return False

        if not self._FwCNIsFwApiAvailable():
            self._FwCNPublishFwApiConnector()

        res = _mxt.Start()
        res = res and not (_mxt.isFailed or _mxt.isTerminating)

        vlogif._LogNewline()
        vlogif._LogNewline()

        if not res:
            logif._LogErrorEC(_EFwErrorCode.UE_00104, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TextID_024).format(_mxt))

            if not self.__lcState.isMainXTaskFailed:
                if self.__lcState.isMainXTaskStarted:
                    if not (_mxt.isFailed or _mxt.isTerminating):
                        self.__SetLcOpState(_ELcCompID.eMainXTask, False)

        elif not (self.__lcState.isMainXTaskFailed or self.__lcState.isMainXTaskStopped):
            res = self.__SetLcOpState(_ELcCompID.eMainXTask, True)
            if not res:
                logif._LogFatalEC(_EFwErrorCode.FE_00041, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TextID_023).format(3))

        if res:
            self.__lcKPI.AddKPI(_ELcKpiID.eMxuStartEnd)
            self.__eExecHist._AddExecutionState(_ELcExecutionState.eMxuStartPassed, self)
        return res

    def __DetermineAsyncStartupResult(self, bAsyncStartupOK_ : bool, bSkipAutoStartMainXT_ : bool =True):
        res = None
        _mainXT = self.__mainXT

        if not bAsyncStartupOK_:
            if self.__eExecHist.isErrorFree:
                if self.__eExecHist.hasPassedSetupPhase and self.__eExecHist.hasReachedRuntimePhase:
                    if _mainXT is None:
                        _bOK = not self.__eExecHist.hasPassedMxuStartPhase
                    else:
                        _bOK = not (bSkipAutoStartMainXT_ or self.__eExecHist.hasPassedMxuStartPhase)
                else:
                    _bOK = False

                if not _bOK:
                    if self.__eExecHist.hasReachedRuntimePhase:
                        self.__eExecHist._RemoveExecutionState(_ELcExecutionState.eRuntimePhase, self)
                    if self.__eExecHist.hasPassedMxuStartPhase:
                        self.__eExecHist._RemoveExecutionState(_ELcExecutionState.eMxuStartPassed, self)
                    if self.__eExecHist.hasPassedSetupPhase:
                        self.__eExecHist._RemoveExecutionState(_ELcExecutionState.eSetupPassed, self)

                    _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TextID_040).format(self.__eExecHist)
                    _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_003, errMsg_=_errMsg)

        else:
            _bOK = self.__eExecHist.isErrorFree
            _bOK = _bOK and self.__eExecHist.hasPassedSetupPhase
            _bOK = _bOK and self.__eExecHist.hasReachedRuntimePhase
            if _bOK:
                if _mainXT is None:
                    _bOK = not self.__eExecHist.hasPassedMxuStartPhase
                else:
                    _bOK = bSkipAutoStartMainXT_ or self.__eExecHist.hasPassedMxuStartPhase

            if not _bOK:
                if self.__eExecHist.hasReachedRuntimePhase:
                    self.__eExecHist._RemoveExecutionState(_ELcExecutionState.eRuntimePhase, self)
                if self.__eExecHist.hasPassedMxuStartPhase:
                    self.__eExecHist._RemoveExecutionState(_ELcExecutionState.eMxuStartPassed, self)
                if self.__eExecHist.hasPassedSetupPhase:
                    self.__eExecHist._RemoveExecutionState(_ELcExecutionState.eSetupPassed, self)

                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcManager_TextID_041).format(self.__eExecHist)
                logif._XLogFatalEC(_EFwErrorCode.FE_00929, _errMsg)

                if self.__eExecHist.isErrorFree:
                    _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_004, errMsg_=_errMsg)

            else:
                res = _LcManager._FwApiReturnRecord(_mainXT, None)
        return res
