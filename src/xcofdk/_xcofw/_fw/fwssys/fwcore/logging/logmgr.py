# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : logmgr.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from typing import Union

from _fw.fwssys.fwcore.logging                import vlogif
from _fw.fwssys.fwcore.logging.vlogif         import _VSystemExit
from _fw.fwssys.fwcore.logging.logdefines     import _GetCurThread
from _fw.fwssys.fwcore.logging.logdefines     import _ELogLevel
from _fw.fwssys.fwcore.logging.logdefines     import _ELogType
from _fw.fwssys.fwcore.logging.logdefines     import _LogUtil
from _fw.fwssys.fwcore.logging.logdefines     import _EErrorImpact
from _fw.fwssys.fwcore.logging.logdefines     import _ELogifOperationOption
from _fw.fwssys.fwcore.logging.logdefines     import _LogErrorCode
from _fw.fwssys.fwcore.logging.logentry       import _LogEntry
from _fw.fwssys.fwcore.logging.alogmgr        import _AbsLogMgr
from _fw.fwssys.fwcore.logging.logmgrdata     import _LogMgrData
from _fw.fwssys.fwcore.logrd.logrecord        import _EColorCode
from _fw.fwssys.fwcore.base.timeutil          import _KpiLogBook
from _fw.fwssys.fwcore.config.fwstartupconfig import _FwStartupConfig
from _fw.fwssys.fwcore.lc.lcxstate            import _ELcKpiID
from _fw.fwssys.fwcore.lc.ifs.iflcproxy       import _ILcProxy
from _fw.fwssys.fwcore.lc.lcproxydefines      import _ProxyInfo
from _fw.fwssys.fwcore.ipc.tsk.taskutil       import _AutoEnclosedThreadsBag
from _fw.fwssys.fwcore.types.commontypes      import _CommonDefines
from _fw.fwssys.fwcore.types.commontypes      import _EDepInjCmd
from _fw.fwssys.fwerrh.fwerrorcodes           import _EFwErrorCode
from _fw.fwssys.fwerrh.fwerrhrp               import _FwErrhRP
from _fw.fwssys.fwerrh.logs.errorlog          import _ErrorLog
from _fw.fwssys.fwerrh.logs.errorlog          import _FatalLog
from _fw.fwssys.fwerrh.logs.xcoexception      import _XcoBaseException

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _LogMgr(_FwErrhRP, _AbsLogMgr):
    __slots__ = [ '__d' ]

    def __init__( self, lcpxy_ : _ILcProxy, startupCfg_ : _FwStartupConfig):
        self.__d = None

        _FwErrhRP.__init__(self)
        _AbsLogMgr.__init__(self)

        if _AbsLogMgr._sgltn is not None:
            self.__DoCleanUp(bSkipVLogCleanup_=True)
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00437)
            return

        if not (isinstance(lcpxy_, _ILcProxy) and not lcpxy_._PxyHasLcAnyFailureState() and isinstance(startupCfg_, _FwStartupConfig) and startupCfg_._isValid):
            self.__DoCleanUp(bSkipVLogCleanup_=True)
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00438)
            return

        self.__d = _LogMgrData(startupCfg_=startupCfg_)
        if self.__d.logConf is None:
            self.__DoCleanUp(bSkipVLogCleanup_=True)
            return

        self._PcSetLcProxy(lcpxy_)

        if not self._RPSetUp(self.__d):
            self.__DoCleanUp(bSkipVLogCleanup_=True)
            return

        _xcpCaught = None
        try:
            _myMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMgr_AddLog_FmtStr_02).format(self.ToString())
            self._AddLog(_ELogType.DBG, msg_=_myMsg)
        except _VSystemExit as _xcp:
            _xcpCaught = _xcp
        except BaseException as _xcp:
            _xcpCaught = _XcoBaseException(_xcp, tb_=_LogUtil._GetFormattedTraceback())
        else:
            _AbsLogMgr._sgltn = self

        finally:
            if _xcpCaught is not None:
                self.__DoCleanUp(bSkipVLogCleanup_=True)
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00440)
            else:
                _supKpi = _KpiLogBook._GetStartupKPI()
                if _supKpi is not None:
                    _supKpi.AddKPI(_ELcKpiID.eLogifCreate)

    def _AddLog( self, logType_ : _ELogType
               , msg_           =None
               , errCode_       =None
               , sysOpXcp_      =None
               , xcpTraceback_  =None
               , unhXcoBaseXcp_ =None
               , logifOpOption_ =None):
        if self.__d is None:
            return None

        _le = None

        if logifOpOption_ is None:
            logifOpOption_ = _ELogifOperationOption.eDontCare

        if vlogif._IsVSystemExitEnabled():
            vlogif._SetVSystemExitStatus(False)

        if unhXcoBaseXcp_ is not None:
            if (not isinstance(unhXcoBaseXcp_, _XcoBaseException)) or (unhXcoBaseXcp_.uniqueID is None):
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00442)
                return None

        if not isinstance(logType_, _ELogType):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00443)
            return None

        _ltGrp = _LogUtil.GetEnabledLogTypeGroup(logType_, self.__GetLogLevel(logType_))
        if _ltGrp is None:
            return None

        if logifOpOption_.isPrintXcpOnly:
            _ts = _LogUtil.GetLogTimestamp()
            msg = _FwTDbEngine.GetText(_EFwTextID.eLogMgr_AddLog_FmtStr_01).format(_ts, _GetCurThread().name, str(msg_))
            self.__d.LMPrint(msg, color_=_EColorCode.RED)
            return None

        if _ltGrp.isNonError and self.__d.isCompactOutputFormatEnabled:
            _le = self.__CreateCompactLog(_ltGrp, logType_, shortMsg_=msg_, longMsg_=None)
            self.__d.LMPrint(_le)
            return None

        _bProcCurThrd   = _AutoEnclosedThreadsBag.IsProcessingCurPyThread()
        _bCLOnly = logifOpOption_.isCreateLogOnly

        if _bProcCurThrd:
            if not _bCLOnly:
                vlogif._VPrint(logType_, msg_, errCode_)
                return None

        if not (self._PcIsLcProxySet() and not _bProcCurThrd):
            _curPxyInfo = None
        else:
            _curPxyInfo = self._PcGetCurProxyInfo()

        if _curPxyInfo is None :
            if not _bCLOnly:
                if self.__d.pendingTaskID is not None:
                    self.__d.SetPendingTaskID(None)
                vlogif._VPrint(logType_, msg_, errCode_)
                return None

        self.__d.UpdateMaxLogTime(bRestart_=True)

        _curPxyInfo, _le = self.__CheckLogRequest( _curPxyInfo, _ltGrp, logType_, msg_=msg_
                                                 , errCode_=errCode_, sysOpXcp_=sysOpXcp_, xcpTraceback_=xcpTraceback_
                                                 , unhXcoBaseXcp_=unhXcoBaseXcp_, logifOpOption_=logifOpOption_)
        if _curPxyInfo is None:
            self.__d.UpdateMaxLogTime()
            return _le

        if self.__d.firstFatalLog is not None:
            if not self.__d.firstFatalLog.isValid:
                self.__d.firstFatalLog = None

        if _le.isFatalError:
            _le._Adapt(bCleanupPermitted_=False)
            if self.__d.firstFatalLog is None:
                self.__d.firstFatalLog = _le.Clone()

        if self.__d.pendingTaskID is not None:
            if _le.isFatalError:
                self.__d.subSeqXcp = _le._enclosedByLogException
            else:
                self.__d.LMPrint(_le)
            _curPxyInfo.CleanUp()
            self.__d.UnlockApi()

            self.__d.UpdateMaxLogTime()
            return None

        _ti    = _curPxyInfo.curTaskInfo._taskInst
        _mp    = _CommonDefines._CHAR_SIGN_DASH
        _bIN   = False
        _bMCM  = (_curPxyInfo.fwMainInfo is not None) and _curPxyInfo.fwMainInfo.isInLcCeaseMode
        _bCTAE = _curPxyInfo.curTaskInfo.isAutoEnclosed

        if _bCTAE:
            _bIN = _le.isFatalError or _bMCM
        elif _bMCM:
            _bIN = True
        elif _curPxyInfo.curTaskInfo.isInLcCeaseMode:
            _bIN = True
        if _bIN:
            _bErrImp = _le.hasErrorImpact or (_le.errorImpact is None)
            if _le.isFatalError and _bErrImp:
                _lcCID = _ti.GetLcCompID()
                if _lcCID is None:
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00444)
                elif self._PcHasLcCompAnyFailureState(_lcCID, atask_=_ti):
                    pass
                elif self._PcHasLcAnyFailureState():
                    pass
                else:
                    _errImp = _EErrorImpact.eImpactByDieError if self.isDieModeEnabled else _EErrorImpact.eImpactByFatalError
                    _le._SetErrorImpact(_errImp)
                    self._PcNotifyLcFailure(_ti.GetLcCompID(), _le, atask_=_ti)
            else:
                self.__d.LMPrint(_le)

            _curPxyInfo.CleanUp()
            self.__d.subSeqXcp = None
            self.__d.UnlockApi()

            self.__d.UpdateMaxLogTime()
            return None

        self.__d.SetPendingTaskID(_curPxyInfo.curTaskInfo.dtaskUID)
        res = self._RPProcessErrorLog(_le, _curPxyInfo, bXtLog_=logType_.isFwApiLogType, bUnhandledXcoBaseXcp_=unhXcoBaseXcp_ is not None, logifOpOption_=logifOpOption_)

        self.__d.UpdateMaxLogTime(bErrorLogTime_=True)
        if _bCTAE:
            res = None
        return res

    def _GetCurrentXTaskError(self):
        if self.__d is None:
            return None

        _curPxyInfo = self._PcGetCurProxyInfo()
        if _curPxyInfo is None:
            return None

        _curTskInfo = _curPxyInfo.curTaskInfo
        if (_curTskInfo is None) or _curTskInfo.isInLcCeaseMode or not _curTskInfo.isDrivingXTask:
            _curPxyInfo.CleanUp()
            return None

        _utc = _curTskInfo.utConn
        _curPxyInfo.CleanUp()

        return None if _utc is None else _utc._currentError

    def _GetCurrentXTaskErrorEntry(self, xuErrUniqueID_ : int) -> _ErrorLog:
        if self.__d is None:
            return None
        if not isinstance(xuErrUniqueID_, int):
            return None

        _curPxyInfo = self._PcGetCurProxyInfo()
        if (_curPxyInfo is None) or (_curPxyInfo.curTaskInfo is None) or _curPxyInfo.curTaskInfo.isInLcCeaseMode:
            if _curPxyInfo is not None:
                _curPxyInfo.CleanUp()
            return None

        _te = _curPxyInfo.curTaskInfo.taskError
        res = None if _te is None else _te._currentErrorEntry
        if res is None:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00445)
        elif res.uniqueID != xuErrUniqueID_:
            res = None
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00446)

        _curPxyInfo.CleanUp()
        return res

    def _ClearCurrentXTaskError(self) -> bool:
        if self.__d is None:
            return False

        _curPxyInfo = self._PcGetCurProxyInfo()
        if _curPxyInfo is None:
            return False

        _curTskInfo = _curPxyInfo.curTaskInfo
        if (_curTskInfo is None) or _curTskInfo.isInLcCeaseMode or not _curTskInfo.isDrivingXTask:
            _curPxyInfo.CleanUp()
            return False

        _utc = _curTskInfo.utConn
        _curPxyInfo.CleanUp()

        res = False
        if _utc is not None:
            res = _utc._ClearCurrentError()
        return res

    @property
    def isValid(self):
        return self.__d is not None

    @property
    def isReleaseModeEnabled(self) -> bool:
        return False if not self.isValid else self.__d.logConf.isReleaseModeEnabled

    @property
    def isDieXcpModeEnabled(self) -> bool:
        return self.isDieModeEnabled and self.isExceptionModeEnabled

    @property
    def isDieModeEnabled(self) -> bool:
        return False if not self.isValid else self.__d.logConf.isDieModeEnabled

    @property
    def isExceptionModeEnabled(self) -> bool:
        return False if not self.isValid else self.__d.logConf.isExceptionModeEnabled

    @property
    def isUserDieModeEnabled(self) -> bool:
        return self.isValid and self.__d.logConf.isUserDieModeEnabled

    @property
    def isUserExceptionModeEnabled(self) -> bool:
        return self.isValid and self.__d.logConf.isExceptionModeEnabled

    def _PrintSummary(self, bLcCall_ =False):
        if self.__d is None:
            return

        if vlogif._VLoggingImpl._IsSilentFwLogLevel():
            return

        _LESS_THAN_LONG    = 9*_CommonDefines._CHAR_SIGN_LESS_THAN
        _LARGER_THAN_LONG  = 9*_CommonDefines._CHAR_SIGN_LARGER_THAN
        _LARGER_THAN_SHORT = 3*_CommonDefines._CHAR_SIGN_LARGER_THAN

        if self.__d.firstFatalLog is not None:
            if not self.__d.firstFatalLog.isValid:
                self.__d.firstFatalLog = None

        _color     = _EColorCode.NONE if (self.__d.firstFatalLog is None) else _EColorCode.RED
        _bRelMode  = self.isReleaseModeEnabled
        _bPrintFFL = not (_bRelMode or (self.__d.firstFatalLog is None))

        _statMsg  = _FwTDbEngine.GetText(_EFwTextID.eLogMgr_PrintSummary_FmtStr_01) + str(self.__d.counter[_ELogType.FTL.value])
        _statMsg += _FwTDbEngine.GetText(_EFwTextID.eLogMgr_PrintSummary_FmtStr_02) + str(self.__d.counter[_ELogType.ERR.value])
        _statMsg += _FwTDbEngine.GetText(_EFwTextID.eLogMgr_PrintSummary_FmtStr_03) + str(self.__d.counter[_ELogType.WNG.value])
        _statMsg += _FwTDbEngine.GetText(_EFwTextID.eLogMgr_PrintSummary_FmtStr_04) + str(self.__d.counter[_ELogType.INF.value])
        _statMsg += f'{_CommonDefines._CHAR_SIGN_RIGHT_PARANTHESIS}{_CommonDefines._CHAR_SIGN_LF}'

        if not _bRelMode:
            _fmtStr    = 2*_FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_006)
            _statMsg  += _fmtStr.format(vlogif._PrintVSummary(bPrint_=False), _CommonDefines._CHAR_SIGN_LF)

        _psMsg = ''
        if bLcCall_:
            if not _bRelMode:
                _psMsg  = f'{_CommonDefines._CHAR_SIGN_LF}{_CommonDefines._CHAR_SIGN_LF}{_LARGER_THAN_LONG}'
                _psMsg += _FwTDbEngine.GetText(_EFwTextID.eLogMgr_PrintSummary_FmtStr_05)
                _psMsg += f'{_LESS_THAN_LONG}{_CommonDefines._CHAR_SIGN_LF}'
            else:
                _psMsg = f'{_CommonDefines._CHAR_SIGN_LF}{_CommonDefines._DASH_LINE_LONG}{_CommonDefines._CHAR_SIGN_LF}'

        _psMsg += _statMsg

        if _bPrintFFL:
            _tmp  = _FwTDbEngine.GetText(_EFwTextID.eLogMgr_PrintSummary_FmtStr_06).format(self.__d.firstFatalLog)
            _tmp += _FwTDbEngine.GetText(_EFwTextID.eLogMgr_PrintSummary_FmtStr_07)
            _tmp  = f'{_CommonDefines._CHAR_SIGN_LF}{_LARGER_THAN_SHORT} '.join(_tmp.split(_CommonDefines._CHAR_SIGN_LF))

            _psMsg += f'{_CommonDefines._CHAR_SIGN_LF}{_LARGER_THAN_SHORT}\n{_LARGER_THAN_SHORT} {_tmp}{_CommonDefines._CHAR_SIGN_LF}{_LARGER_THAN_SHORT}'
            _psMsg += f'{_CommonDefines._CHAR_SIGN_LF}{_statMsg}'

        _myMsg  = None
        _supKpi = _KpiLogBook._GetStartupKPI()
        if _supKpi.IsAddedKPI(_ELcKpiID.eLogifDestroy):
            _kpiTD = _supKpi.GetKpiTimeDelta(_ELcKpiID.eLogifDestroy, _ELcKpiID.eTextDBFirstFetch)
            _myMsg = (_FwTDbEngine.GetText(_EFwTextID.eLogMgr_PrintSummary_FmtStr_11).format(_kpiTD.timeParts))
            _kpiTD.CleanUp()

        if not _bRelMode:
            _fmtStr = 4*_FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_006)
            _psMsg += _fmtStr.format(_FwTDbEngine.GetText(_EFwTextID.eLogMgr_PrintSummary_FmtStr_08)
                                    , self.__d.maxLogTime, _FwTDbEngine.GetText(_EFwTextID.eLogMgr_PrintSummary_FmtStr_09), self.__d.maxErrorLogTime)
            _psMsg += f'{_CommonDefines._CHAR_SIGN_RIGHT_PARANTHESIS}{_CommonDefines._CHAR_SIGN_DOT}'
            if _myMsg is not None:
                _psMsg += f'{_CommonDefines._CHAR_SIGN_LF}{_myMsg}'

        if bLcCall_:
            if not _bRelMode:
                _psMsg += f'{_CommonDefines._CHAR_SIGN_LF}{_LARGER_THAN_LONG}'
                _psMsg += _FwTDbEngine.GetText(_EFwTextID.eLogMgr_PrintSummary_FmtStr_10)
                _psMsg += f'{_LESS_THAN_LONG}{_CommonDefines._CHAR_SIGN_LF}'
            else:
                if _myMsg is not None:
                    _psMsg += f'{_myMsg}{_CommonDefines._CHAR_SIGN_LF}'
                _psMsg += f'{_CommonDefines._DASH_LINE_LONG}{_CommonDefines._CHAR_SIGN_LF}'
        self.__d.LMPrint(_psMsg, color_=_color)

    @staticmethod
    def _GetInstance(lcpxy_ : _ILcProxy =None, startupCfg_ : _FwStartupConfig =None):
        if _AbsLogMgr._sgltn is None:
            _inst = _LogMgr(lcpxy_, startupCfg_)
            if _inst.__isInvalid:
                _inst.__DoCleanUp(bSkipVLogCleanup_=True)
                _inst = None
            _AbsLogMgr._sgltn = _inst
        return _AbsLogMgr._sgltn

    @staticmethod
    def _ClsDepInjection(dinjCmd_ : _EDepInjCmd):
        _logif = _AbsLogMgr.GetInstance()
        if _logif is not None:
            _logif.CleanUp()

    @property
    def _lastLogEntry(self) -> _LogEntry:
        return None if self.__d is None else self.__d.lastCreatedLogEntry

    def _ToString(self):
        if self.__d is None:
            res = _CommonDefines._STR_EMPTY
        else:
            res = _FwTDbEngine.GetText(_EFwTextID.eLogMgr_ToString_01).format(type(self).__name__, str(self.isDieModeEnabled), str(self.isExceptionModeEnabled),  self.__logLevel.compactName,  self.__userLogLevel.compactName)
        return res

    def _CleanUp(self):
        _supKpi = _KpiLogBook._GetStartupKPI()
        if _supKpi is not None:
            _supKpi.AddKPI(_ELcKpiID.eLogifDestroy)

            _kpiTD = _supKpi.GetKpiTimeDelta(_ELcKpiID.eLogifDestroy, _ELcKpiID.eLogifCreate)
            _myMsg = (_FwTDbEngine.GetText(_EFwTextID.eLogMgr_ActiveTimeKPI).format(_kpiTD.timeParts))
            self._AddLog(_ELogType.KPI, msg_=_myMsg)
            _kpiTD.CleanUp()

            self._PrintSummary(bLcCall_=True)
        self.__DoCleanUp()

        _FwErrhRP._CleanUp(self)
        _AbsLogMgr.CleanUp(self)

    def _ClearLogHistory(self):
        vlogif._ClearLogHistory()
        if self.__d is not None:
            self.__d._ClearLogHistory()

    @property
    def __isInvalid(self):
        return True if self.__d is None else self.__d.logConf is None

    @property
    def __logLevel(self) -> _ELogLevel:
        return None if self.__d is None else self.__d.logConf.logLevel

    @property
    def __userLogLevel(self) -> _ELogLevel:
        return None if self.__d is None else self.__d.logConf.userLogLevel

    def __GetLogLevel(self, logType_) -> _ELogLevel:
        return self.__userLogLevel if logType_.isFwApiLogType else self.__logLevel

    def __DoCleanUp(self, bSkipVLogCleanup_ =False):
        if self.__d is None:
            return

        if (_AbsLogMgr._sgltn is not None) and (id(self) == id(_AbsLogMgr._sgltn)):
            _AbsLogMgr._sgltn = None

        self._PcSetLcProxy(None, bForceUnset_=True)

        self.__d.CleanUp()
        self.__d = None

        if not bSkipVLogCleanup_:
            vlogif._ClearLogHistory()

    def __CheckLogRequest( self
                         , curPxyInfo_    : _ProxyInfo
                         , logTypeGrp_    : _ELogType
                         , logType_       : _ELogType
                         , msg_           =None
                         , errCode_       : Union[int, _EFwErrorCode] =None
                         , sysOpXcp_      =None
                         , xcpTraceback_  =None
                         , unhXcoBaseXcp_ =None
                         , logifOpOption_ =_ELogifOperationOption.eDontCare):
        _bCLOnly = logifOpOption_.isCreateLogOnly

        if curPxyInfo_ is None:
            if not _bCLOnly:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00447)
                return None, None

        if unhXcoBaseXcp_ is not None:
            _xcpType = _CommonDefines._STR_EMPTY if unhXcoBaseXcp_._enclosedException is None else type(unhXcoBaseXcp_._enclosedException).__name__
            msg_ = _FwTDbEngine.GetText(_EFwTextID.eLogMgr_CheckLogRequest_Msg_01).format(_xcpType, unhXcoBaseXcp_.uniqueID, unhXcoBaseXcp_.shortMessage)
            sysOpXcp_ = unhXcoBaseXcp_

        _bLockApi = logTypeGrp_.isError
        if _bLockApi: self.__d.LockApi()

        if isinstance(errCode_, _EFwErrorCode):
            errCode_ = errCode_.toSInt
        if errCode_ is not None:
            if _LogErrorCode.IsAnonymousErrorCode(errCode_):
                errCode_ = None
            elif _LogErrorCode.IsInvalidErrorCode(errCode_):
                self._AddLog(_ELogType.WNG, msg_=_FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_Logging_001).format(str(errCode_)))
            elif logType_.isFwApiLogType:
                if not _LogErrorCode.IsValidApiErrorCode(errCode_):
                    if logifOpOption_.isStrictEcMatch:
                        self._AddLog(_ELogType.WNG, msg_=_FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_Logging_002).format(errCode_))
            elif not _LogErrorCode.IsValidFwErrorCode(errCode_):
                self._AddLog(_ELogType.WNG, msg_=_FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_Logging_003).format(errCode_))

        _le         = None
        _bCaughtXcp = False

        _curTskInfo = None if curPxyInfo_ is None else curPxyInfo_.curTaskInfo
        _tid        = None if _curTskInfo is None else _curTskInfo.dtaskUID

        try:
            _tname = _GetCurThread().name if _curTskInfo is None else _curTskInfo.dtaskName

            _le = self.__CreateLog( _tname
                                  , _tid, logTypeGrp_, logType_
                                  , shortMsg_=msg_, longMsg_=None
                                  , errCode_=errCode_, sysOpXcp_=sysOpXcp_
                                  , xcpTraceback_=xcpTraceback_
                                  , xrn_=None if _curTskInfo is None else _curTskInfo.xrNumber)
        except BaseException as _xcp:
            _bCaughtXcp = True
            _LogUtil._RaiseException(_xcp)
        finally:
            if _bCaughtXcp or _le is None:
                _le = None
                if curPxyInfo_ is not None:
                    curPxyInfo_.CleanUp()
                if _bLockApi: self.__d.UnlockApi()

        if _le is None:
            return None, None

        if _le.isError:
            if _curTskInfo is not None:
                _le._Adapt(eTaskExecPhaseID_=_curTskInfo.taskXPhase)
                _le._SetTaskInstance(tskInst_=_curTskInfo._taskInst)

        if _bCLOnly:
            if _le.isFatalError:
                if _bCLOnly:
                    _le._SetErrorImpact(_EErrorImpact.eImpactByFatalErrorDueToXCmd if logifOpOption_.isCreateLogOnlyDueToExecCmdAbort else _EErrorImpact.eImpactByFatalError)

                if _curTskInfo is not None:
                    _le._Adapt(bCleanupPermitted_=False)
                if self.__d.firstFatalLog is None:
                    self.__d.firstFatalLog = _le.Clone()

            if curPxyInfo_ is not None:
                curPxyInfo_.CleanUp()
            if _bLockApi: self.__d.UnlockApi()
            return None, _le

        if curPxyInfo_ is None:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00448)
            return None, None

        if self.__d.pendingTaskID is not None:
            if logifOpOption_.isSetErrorOnly:
                curPxyInfo_.CleanUp()
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00449)
                if _bLockApi: self.__d.UnlockApi()
                return None, None

            elif _tid != self.__d.pendingTaskID:
                curPxyInfo_.CleanUp()
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00450)
                if _bLockApi: self.__d.UnlockApi()
                return None, None

            elif self.__d.subSeqXcp is not None:
                curPxyInfo_.CleanUp()
                self.__d.LMPrint(_le)
                if _bLockApi: self.__d.UnlockApi()
                return None, None

        elif self.__d.subSeqXcp is not None:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00451)
            curPxyInfo_.CleanUp()
            if _bLockApi: self.__d.UnlockApi()
            return None, None

        if _le.isError:
            _curTEE = _curTskInfo.taskError._currentErrorEntry

            if _curTEE is not None:
                if _curTEE.isFatalError:
                    if _le.isFatalError:
                        _midPart = _FwTDbEngine.GetText(_EFwTextID.eMisc_Fatal)

                        _te = _curTskInfo.taskError
                        _le._SetErrorImpact(_EErrorImpact.eNoImpactByExistingFatalError)
                        _shortMsg  = _FwTDbEngine.GetText(_EFwTextID.eLogMgr_CheckLogRequest_Msg_02)
                        _shortMsg  = _shortMsg.format(_midPart, _midPart, _te.currentErrorUniqueID)
                        _shortMsg += _FwTDbEngine.GetText(_EFwTextID.eLogMgr_CheckLogRequest_Msg_03).format(_le.uniqueID, _le.shortMessage)
                        _le._Adapt(shortMsg_=_shortMsg)
                        _buf = _shortMsg
                    else:
                        _buf = _le

                    curPxyInfo_.CleanUp()

                    self.__d.LMPrint(_buf, color_=_EColorCode.RED)
                    if _bLockApi: self.__d.UnlockApi()
                    return None, None

                else:
                    if _le.isFatalError:
                        _curTEE._UpdateErrorImpact(_EErrorImpact.eNoImpactByLogTypePrecedence)
                    else:
                        _te = _curTskInfo.taskError
                        if _curTskInfo.isAutoEnclosed:
                            _te.ClearError()
                        else:
                            _midPart = _FwTDbEngine.GetText(_EFwTextID.eMisc_Fatal) if _te.isFatalError else _FwTDbEngine.GetText(_EFwTextID.eMisc_User)

                            _le._SetErrorImpact(_EErrorImpact.eNoImpactByExistingUserError)
                            _shortMsg  = _FwTDbEngine.GetText(_EFwTextID.eLogMgr_CheckLogRequest_Msg_02)
                            _shortMsg  = _shortMsg.format(_FwTDbEngine.GetText(_EFwTextID.eMisc_User), _midPart, _te.currentErrorUniqueID)
                            _shortMsg += _FwTDbEngine.GetText(_EFwTextID.eLogMgr_CheckLogRequest_Msg_03).format(_le.uniqueID, _le.shortMessage)
                            _le._Adapt(shortMsg_=_shortMsg)

                            curPxyInfo_.CleanUp()

                            self.__d.LMPrint(_shortMsg, color_=_EColorCode.RED)
                            if _bLockApi: self.__d.UnlockApi()
                            return None, None
        else:
            curPxyInfo_.CleanUp()
            if logifOpOption_.isSetErrorOnly:
                if _bLockApi: self.__d.UnlockApi()
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00452)
            else:
                self.__d.LMPrint(_le)
                if _bLockApi: self.__d.UnlockApi()
            return None, None

        return curPxyInfo_, _le

    def __CreateLog( self, taskName_, taskID_, logTypeGrpID_ : _ELogType, logType_: _ELogType
                   , shortMsg_: str =None, longMsg_: str =None, errCode_: int =None, sysOpXcp_ =None
                   , xcpTraceback_ =None, xrn_ =None) -> Union[_ErrorLog, _FatalLog, None]:
        if logType_._absValue >= _ELogType.FTL.value:
            if logTypeGrpID_ != _ELogType.FTL:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00453)
                return None

        if logType_._absValue >= _ELogType.ERR.value:
            _le = _FwErrhRP._CreateErrorLog( taskName_, taskID_, logTypeGrpID_, logType_
                                           , shortMsg_=shortMsg_, longMsg_=longMsg_, errCode_=errCode_
                                           , sysOpXcp_=sysOpXcp_, xcpTraceback_=xcpTraceback_
                                           , xrn_=xrn_, bXcpModeEnabled_=self.isExceptionModeEnabled)
        else:
            _le = _LogEntry(logType_, taskName_=taskName_, taskID_=taskID_, shortMsg_=shortMsg_, longMsg_=longMsg_, xrn_=xrn_)

        if _le is None:
            return None
        if not _le.isValid:
            _le.CleanUp()
            return None

        self.__d.counter[logTypeGrpID_._absValue] += 1
        self.__d.AddLogEntry(_le)
        return _le

    def __CreateCompactLog( self, logTypeGrpID_ : _ELogType, logType_: _ELogType
                          , shortMsg_: str = None, longMsg_: str = None):
        _tname    = None
        _bXTask = False if self.isReleaseModeEnabled else None

        if not self._PcIsLcProxySet():
            pass
        else:
            _tmgr = self._PcGetTTaskMgr()
            if _tmgr is None:
                pass
            else:
                _tname, _bXTask = _tmgr._GetProxyInfoReplacementData()

        _le = _LogEntry(logType_, taskName_=_tname, shortMsg_=shortMsg_, longMsg_=longMsg_, bXTaskTask_=_bXTask)
        if _le is None:
            pass
        elif not _le.isValid:
            _le.CleanUp()
            _le = None
        else:
            self.__d.counter[logTypeGrpID_._absValue] += 1
            self.__d.AddLogEntry(_le)
        return _le
