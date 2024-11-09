# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : logifimpl.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from enum import Enum
from enum import unique

from xcofdk.fwapi.xtask.xtaskerror import XTaskException
from xcofdk.fwapi.xtask.xtaskerror import _XTaskExceptionBase

from xcofdk._xcofw.fw.fwssys.fwcore.base.timeutil             import _KpiLogBook
from xcofdk._xcofw.fw.fwssys.fwcore.config.fwstartupconfig    import _FwStartupConfig
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcexecstate            import _ELcKpiID
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcproxy                import _LcProxy
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcproxydefines         import _ProxyInfo
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil          import _AutoEnclosedThreadsBag
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject             import _AbstractSlotsObject
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes         import _CommonDefines

from xcofdk._xcofw.fw.fwssys.fwcore.logging                 import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.logging.vlogif          import _VSystemExit
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logdefines      import _GetCurThread
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logdefines      import _ELogLevel
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logdefines      import _ELogType
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logdefines      import _LogUtil
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logdefines      import _EErrorImpact
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logdefines      import _ELogifOperationOption
from xcofdk._xcofw.fw.fwssys.fwcore.logging.errorentry      import _ErrorEntry
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logentry        import _LogEntry
from xcofdk._xcofw.fw.fwssys.fwcore.logging.fatalentry      import _FatalEntry
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logifbase       import _LogIFBase
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logifimplhelper import _LogIFImplHelper
from xcofdk._xcofw.fw.fwssys.fwcore.logging.dieexception    import _DieException
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logexception    import _LogException
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logexception    import _LogExceptionFatal
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logexception    import _LogExceptionBadUse
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logexception    import _LogExceptionImplError
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logexception    import _LogExceptionNotImplemented
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logexception    import _LogExceptionSystemOpERR
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logexception    import _LogExceptionNestedError
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logexception    import _LogExceptionSystemOpXCP
from xcofdk._xcofw.fw.fwssys.fwcore.logging.xcoexception    import _XcoExceptionRoot
from xcofdk._xcofw.fw.fwssys.fwcore.logging.xcoexception    import _XcoBaseException

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine



class _LogIFImpl(_AbstractSlotsObject, _LogIFBase):

    @unique
    class _EDieExceptionTarget(Enum):
        eFwMain   = 0
        eRESERVED = 1

    __logExceptionClassMap = {
          _ELogType.FTL                     : _LogExceptionFatal
        , _ELogType.FTL_BAD_USE             : _LogExceptionBadUse
        , _ELogType.FTL_IMPL_ERR            : _LogExceptionImplError
        , _ELogType.FTL_NOT_IMPLEMENTED_YET : _LogExceptionNotImplemented
        , _ELogType.FTL_SYS_OP_ERR          : _LogExceptionSystemOpERR
        , _ELogType.FTL_SYS_OP_XCP          : _LogExceptionSystemOpXCP
        , _ELogType.XFTL                    : _LogExceptionFatal
        , _ELogType.XFTL_SYS_OP_XCP         : _LogExceptionSystemOpXCP
    }

    __slots__ = [ '__helper' , '__lcpxy' ]
    __dieXcpTarget = None

    def __init__( self
                , bRelMode_           : bool             =None
                , bDieMode_           : bool             =None
                , bXcpMode_           : bool             =None
                , eLogLevel_          : _ELogLevel       =None
                , bOutputRedirection_ : bool             =None
                , lcpxy_              : _LcProxy         =None
                , startupCfg_         : _FwStartupConfig =None):
        self.__lcpxy  = None
        self.__helper = None

        _AbstractSlotsObject.__init__(self)
        _LogIFBase.__init__(self)

        if _LogIFBase._theInstance is not None:
            self.__DoCleanUp(bSkipVLogCleanup_=True)
            vlogif._LogOEC(True, -1048)
            return
        if (lcpxy_ is not None) and not (isinstance(lcpxy_, _LcProxy) and lcpxy_.isLcProxyAvailable):
            self.__DoCleanUp(bSkipVLogCleanup_=True)
            vlogif._LogOEC(True, -1049)
            return

        self.__helper = _LogIFImplHelper(startupCfg_=startupCfg_)
        if self.__helper.fwStartupConfig is None:
            self.__DoCleanUp(bSkipVLogCleanup_=True)
            return

        self.__helper.SetupConfig(bRelMode_=bRelMode_, bDieMode_=bDieMode_, bXcpMode_=bXcpMode_, eLogLevel_=eLogLevel_, bOutputRedirection_=bOutputRedirection_)
        if self.__helper.logConf is None:
            self.__DoCleanUp(bSkipVLogCleanup_=True)
            return

        if _LogIFImpl.__dieXcpTarget is not None:
            if _LogIFImpl.__dieXcpTarget != _LogIFImpl._EDieExceptionTarget.eFwMain:
                self.__DoCleanUp(bSkipVLogCleanup_=True)
                vlogif._LogOEC(True, -1050)
                return
        else:
            _LogIFImpl.__dieXcpTarget = _LogIFImpl._EDieExceptionTarget.eFwMain

        self.__lcpxy = lcpxy_

        _xcpCaught = None
        try:
            _myMsg = _FwTDbEngine.GetText(_EFwTextID.eLogIFImpl_AddLog_FmtStr_02).format(self.ToString())
            self._AddLog(_ELogType.DBG, msg_=_myMsg, callstackLevelOffset_=_LogUtil.GetCallstackLevelOffset()-1)
        except _VSystemExit as _xcp:
            _xcpCaught = _xcp
        except BaseException as _xcp:
            _xcpCaught = _XcoBaseException(_xcp, tb_=_LogUtil._GetFormattedTraceback())
        else:
            _LogIFBase._theInstance = self

        finally:
            if _xcpCaught is not None:
                self.__DoCleanUp(bSkipVLogCleanup_=True)
                vlogif._LogOEC(True, -1051)
            else:
                _supKpi = _KpiLogBook._GetStartupKPI()
                if _supKpi is not None:
                    _supKpi.AddKPI(_ELcKpiID.eLogifCreate)

    @property
    def isValid(self):
        return self.__helper is not None

    @property
    def isReleaseModeEnabled(self) -> bool:
        return False if not self.isValid else self.__helper.logConf.releaseMode

    @property
    def isDieXcpModeEnabled(self) -> bool:
        return self.isDieModeEnabled and self.isExceptionModeEnabled

    @property
    def isDieModeEnabled(self) -> bool:
        if not self.isValid: return False
        else: return self.__helper.logConf.dieMode

    @property
    def isExceptionModeEnabled(self) -> bool:
        return False if not self.isValid else self.__helper.logConf.exceptionMode

    @property
    def isUserDieModeEnabled(self) -> bool:
        return self.isValid and self.__helper.fwStartupConfig._isUserDieModeEnabled

    @property
    def isUserExceptionModeEnabled(self) -> bool:
        return self.isValid and self.__helper.fwStartupConfig._isUserExceptionModeEnabled

    @property
    def isFwTraceEnabled(self):
        return self.__IsFwLogLevelEnabled(_ELogLevel.eTrace)

    @property
    def isFwDebugEnabled(self):
        return self.__IsFwLogLevelEnabled(_ELogLevel.eDebug)

    @property
    def isFwInfoEnabled(self):
        return self.__IsFwLogLevelEnabled(_ELogLevel.eInfo)

    @property
    def isFwKPIEnabled(self):
        return self.__IsFwLogLevelEnabled(_ELogLevel.eKPI)

    @property
    def isFwWarningEnabled(self):
        return self.__IsFwLogLevelEnabled(_ELogLevel.eWarning)

    @property
    def eLogLevel(self) -> _ELogLevel:
        return None if self.__helper is None else self.__helper.logConf.eLogLevel

    def _PrintSummary(self, bPrintFFL_ =True, bLcCall_ =False):
        if self.__helper is None:
            return

        _LESS_THAN_LONG    = 9*_CommonDefines._CHAR_SIGN_LESS_THAN
        _LARGER_THAN_LONG  = 9*_CommonDefines._CHAR_SIGN_LARGER_THAN
        _LARGER_THAN_SHORT = 3*_CommonDefines._CHAR_SIGN_LARGER_THAN

        if self.__helper.firstFatalLog is not None:
            if not self.__helper.firstFatalLog.isValid:
                self.__helper.firstFatalLog = None

        _bRelMode = self.isReleaseModeEnabled

        if (self.__helper.firstFatalLog is None) or _bRelMode:
            bPrintFFL_ = False

        _statMsg  = _FwTDbEngine.GetText(_EFwTextID.eLogIFImpl_PrintSummary_FmtStr_01) + str(self.__helper.counter[_ELogType.FTL.value])
        _statMsg += _FwTDbEngine.GetText(_EFwTextID.eLogIFImpl_PrintSummary_FmtStr_02) + str(self.__helper.counter[_ELogType.ERR.value])
        _statMsg += _FwTDbEngine.GetText(_EFwTextID.eLogIFImpl_PrintSummary_FmtStr_03) + str(self.__helper.counter[_ELogType.WNG.value])
        _statMsg += _FwTDbEngine.GetText(_EFwTextID.eLogIFImpl_PrintSummary_FmtStr_04) + str(self.__helper.counter[_ELogType.INF.value])
        _statMsg += f'{_CommonDefines._CHAR_SIGN_RIGHT_PARANTHESIS}{_CommonDefines._CHAR_SIGN_NEWLINE}'

        if not _bRelMode:
            _fmtStr = 2*_FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_006)
            _statMsg += _fmtStr.format(vlogif._PrintVSummary(bPrint_=False), _CommonDefines._CHAR_SIGN_NEWLINE)

        _psMsg = ''
        if bLcCall_:
            if not _bRelMode:
                _psMsg  = f'{_CommonDefines._CHAR_SIGN_NEWLINE}{_CommonDefines._CHAR_SIGN_NEWLINE}{_LARGER_THAN_LONG}'
                _psMsg += _FwTDbEngine.GetText(_EFwTextID.eLogIFImpl_PrintSummary_FmtStr_05)
                _psMsg += f'{_LESS_THAN_LONG}{_CommonDefines._CHAR_SIGN_NEWLINE}'
            else:
                _psMsg = f'{_CommonDefines._CHAR_SIGN_NEWLINE}{_CommonDefines._DASH_LINE_LONG}{_CommonDefines._CHAR_SIGN_NEWLINE}'

        _psMsg += _statMsg

        if bPrintFFL_:
            tmp  = _FwTDbEngine.GetText(_EFwTextID.eLogIFImpl_PrintSummary_FmtStr_06).format(self.__helper.firstFatalLog)
            tmp += _FwTDbEngine.GetText(_EFwTextID.eLogIFImpl_PrintSummary_FmtStr_07)
            tmp  = f'{_CommonDefines._CHAR_SIGN_NEWLINE}{_LARGER_THAN_SHORT} '.join(tmp.split(_CommonDefines._CHAR_SIGN_NEWLINE))

            _psMsg += f'{_CommonDefines._CHAR_SIGN_NEWLINE}{_LARGER_THAN_SHORT}\n{_LARGER_THAN_SHORT} {tmp}{_CommonDefines._CHAR_SIGN_NEWLINE}{_LARGER_THAN_SHORT}'
            _psMsg += f'{_CommonDefines._CHAR_SIGN_NEWLINE}{_statMsg}'

        _myMsg  = None
        _supKpi = _KpiLogBook._GetStartupKPI()
        if _supKpi.IsAddedKPI(_ELcKpiID.eLogifDestroy):
            _kpiTD = _supKpi.GetKpiTimeDelta(_ELcKpiID.eLogifDestroy, _ELcKpiID.eTextDBFirstFetch)
            _myMsg = (_FwTDbEngine.GetText(_EFwTextID.eLogIFImpl_PrintSummary_FmtStr_11).format(_kpiTD.timeParts))
            _kpiTD.CleanUp()

        if not _bRelMode:
            _fmtStr = 4*_FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_006)
            _psMsg += _fmtStr.format(_FwTDbEngine.GetText(_EFwTextID.eLogIFImpl_PrintSummary_FmtStr_08), self.__helper.maxLogTime, _FwTDbEngine.GetText(_EFwTextID.eLogIFImpl_PrintSummary_FmtStr_09), self.__helper.maxErrorLogTime)
            _psMsg += f'{_CommonDefines._CHAR_SIGN_RIGHT_PARANTHESIS}{_CommonDefines._CHAR_SIGN_DOT}'
            if _myMsg is not None:
                _psMsg += f'{_CommonDefines._CHAR_SIGN_NEWLINE}{_myMsg}'

        if bLcCall_:
            if not _bRelMode:
                _psMsg += f'{_CommonDefines._CHAR_SIGN_NEWLINE}{_LARGER_THAN_LONG}'
                _psMsg += _FwTDbEngine.GetText(_EFwTextID.eLogIFImpl_PrintSummary_FmtStr_10)
                _psMsg += f'{_LESS_THAN_LONG}{_CommonDefines._CHAR_SIGN_NEWLINE}'
            else:
                if _myMsg is not None:
                    _psMsg += f'{_myMsg}{_CommonDefines._CHAR_SIGN_NEWLINE}'
                _psMsg += f'{_CommonDefines._DASH_LINE_LONG}{_CommonDefines._CHAR_SIGN_NEWLINE}'
        self.__helper.Flush(_psMsg)

    @staticmethod
    def _GetInstance(lcpxy_ : _LcProxy =None, startupCfg_ : _FwStartupConfig =None):
        if _LogIFBase._theInstance is None:
            inst = _LogIFImpl(lcpxy_=lcpxy_, startupCfg_=startupCfg_)
            if inst.__isInvalid:
                inst.__DoCleanUp(bSkipVLogCleanup_=True)
                inst = None
            _LogIFBase._theInstance = inst
        return _LogIFBase._theInstance

    @staticmethod
    def _SetupLoggingConfig(bRelMode_ : bool =None, bDieMode_ : bool =None, bXcpMode_ : bool =None
                          , eLogLevel_ : _ELogLevel =None, bOutputRedirection_ : bool =None):
        if _LogIFBase._theInstance is not None:
            vlogif._LogOEC(True, -1052)
        else:
            _LogIFBase._theInstance = _LogIFImpl(
                bRelMode_=bRelMode_, bDieMode_=bDieMode_, bXcpMode_=bXcpMode_, eLogLevel_=eLogLevel_, bOutputRedirection_=bOutputRedirection_)
        return _LogIFBase._theInstance

    @property
    def _lastLogEntry(self) -> _LogEntry:
        return None if self.__helper is None else self.__helper.lastCreatedLogEntry

    def _ToString(self, *args_, **kwargs_):
        if self.__helper is None:
            res = _CommonDefines._STR_EMPTY
        else:
            res = _FwTDbEngine.GetText(_EFwTextID.eLogIFImpl_ToString_01).format(type(self).__name__, self.eLogLevel.compactName, str(self.isDieModeEnabled), str(self.isExceptionModeEnabled))
        return res

    def _CleanUp(self):
        _supKpi = _KpiLogBook._GetStartupKPI()
        if _supKpi is not None:

            _supKpi.AddKPI(_ELcKpiID.eLogifDestroy)

            _kpiTD = _supKpi.GetKpiTimeDelta(_ELcKpiID.eLogifDestroy, _ELcKpiID.eLogifCreate)
            _myMsg = (_FwTDbEngine.GetText(_EFwTextID.eLogIFImpl_ActiveTimeKPI).format(_kpiTD.timeParts))
            self._AddLog(_ELogType.KPI, msg_=_myMsg)
            _kpiTD.CleanUp()

            self._PrintSummary(bPrintFFL_=True, bLcCall_=True)
        self.__DoCleanUp()

    def _ClearLogHistory(self):
        if not self.isReleaseModeEnabled:
            _statMsg = vlogif._PrintVSummary(bPrint_=False)
        else:
            _statMsg = None
        vlogif._LogFree('[LogIF] Clearing complete vlog/log history...\n')
        vlogif._ClearLogHistory()
        if self.__helper is not None:
            self.__helper._ClearLogHistory()

        if _statMsg is not None:
            vlogif._LogFree('[LogIF] Cleared history:\n\t{}\n'.format(_statMsg))

    def _AddLog( self, eLogType_ : _ELogType
               , msg_                  =None
               , errCode_              =None
               , sysOpXcp_             =None
               , xcpTraceback_         =None
               , callstackLevelOffset_ =None
               , unhandledXcoBaseXcp_  =None
               , eLogifOpOption_       =None):

        if self.__helper is None:
            return None

        _le         = None
        _curPxyInfo = None

        if eLogifOpOption_ is None:
            eLogifOpOption_ = _ELogifOperationOption.eDontCare

        if vlogif._IsVSystemExitEnabled():
            vlogif._SetVSystemExitStatus(False)

        if unhandledXcoBaseXcp_ is not None:
            if (not isinstance(unhandledXcoBaseXcp_, _XcoBaseException)) or (unhandledXcoBaseXcp_.uniqueID is None):
                vlogif._LogOEC(True, -1053)
                return None

        if not isinstance(eLogType_, _ELogType):
            vlogif._LogOEC(True, -1054)
            return None

        _curLL       = self.__helper.fwStartupConfig._userLogLevel if eLogType_.isFwApiLogType else self.eLogLevel
        _eLogTypeGrp = _LogUtil.GetEnabledLogTypeGroup(eLogType_, _curLL)
        if _eLogTypeGrp is None:
            return None

        if eLogifOpOption_.isPrintXcpOnly:
            _ts = _LogUtil.GetLogTimestamp()
            msg = _FwTDbEngine.GetText(_EFwTextID.eLogIFImpl_AddLog_FmtStr_01).format(_ts, _GetCurThread().name, str(msg_))
            self.__helper.Flush(msg)
            return None

        if _eLogTypeGrp.isNonError and self.__helper.isCompactOutputFormatEnabled:
            _le = self.__CreateCompactLog(_eLogTypeGrp, eLogType_, shortMsg_=msg_, longMsg_=None)
            self.__helper.Flush(_le)
            return None

        _bProcCurThrd   = _AutoEnclosedThreadsBag.IsProcessingCurPyThread()
        _bCreateLogOnly = eLogifOpOption_.isCreateLogOnly

        if _bProcCurThrd:
            if not _bCreateLogOnly:
                vlogif._VPrint(eLogType_, msg_, errCode_)
                return None

        if (self.__lcpxy is None) or _bProcCurThrd:
            pass
        else:
            _curPxyInfo = self.__lcpxy.curProxyInfo

        if _curPxyInfo is None :
            if not _bCreateLogOnly:
                if self.__helper.pendingTaskID is not None:
                    self.__helper.SetPendingTaskID(None)


                vlogif._VPrint(eLogType_, msg_, errCode_)
                return None

        self.__helper.UpdateMaxLogTime(bRestart_=True)

        _curPxyInfo, _le = self.__CheckLogRequest( _curPxyInfo, _eLogTypeGrp, eLogType_, msg_=msg_
                                                 , errCode_=errCode_, sysOpXcp_=sysOpXcp_, xcpTraceback_=xcpTraceback_
                                                 , callstackLevelOffset_=callstackLevelOffset_, unhandledXcoBaseXcp_=unhandledXcoBaseXcp_
                                                 , eLogifOpOption_=eLogifOpOption_)
        if _curPxyInfo is None:
            self.__helper.UpdateMaxLogTime()
            return _le

        if self.__helper.firstFatalLog is not None:
            if not self.__helper.firstFatalLog.isValid:
                self.__helper.firstFatalLog = None

        if _le.isFatalError:
            if self.isDieModeEnabled:
                _bCUP = _curPxyInfo.curTaskInfo.hasUnitTestTaskRight
                _le._Adapt(bCleanupPermitted_=_bCUP)

            if self.__helper.firstFatalLog is None:
                self.__helper.firstFatalLog = _le.Clone()

        if self.__helper.pendingTaskID is not None:
            if _le.isFatalError:
                self.__helper.subSeqXcp = _le._enclosedByLogException
            else:
                self.__helper.Flush(_le)
            _curPxyInfo.CleanUp()
            self.__helper.UnlockApi()

            self.__helper.UpdateMaxLogTime()
            return None

        _bALWAYS_IGNORE = False
        if _bALWAYS_IGNORE:
            if _curPxyInfo.curTaskInfo.taskBadge.isAutoEnclosed:
                _le._UpdateErrorImpact(eErrImpact_=_EErrorImpact.eNoImpactByAutoEnclosedThreadOwnership)

                self.__helper.UpdateMaxLogTime()
                return None

        if _curPxyInfo.curTaskInfo.isInLcCeaseMode or ((_curPxyInfo.fwMainInfo is not None) and _curPxyInfo.fwMainInfo.isInLcCeaseMode):
            if _le.isFatalError and _le.hasErrorImpact:
                _myTskInst = _curPxyInfo.curTaskInfo._taskInst
                _lcCompID  = _myTskInst.GetLcCompID()
                if _lcCompID is None:
                    vlogif._LogOEC(True, -1055)
                elif self.__lcpxy.HasLcCompFRC(_lcCompID, atask_=_myTskInst):
                    pass
                else:
                    _errImp = _EErrorImpact.eImpactByDieError if self.isDieModeEnabled else _EErrorImpact.eImpactByFatalError
                    _le._SetErrorImpact(_errImp)
                    self.__lcpxy._NotifyLcFailure(_myTskInst.GetLcCompID(), _le, atask_=_myTskInst)
            else:
                self.__helper.Flush(_le)

            _curPxyInfo.CleanUp()
            self.__helper.subSeqXcp = None
            self.__helper.UnlockApi()

            self.__helper.UpdateMaxLogTime()
            return None

        self.__helper.SetPendingTaskID(_curPxyInfo.curTaskInfo.taskID)
        res = self.__ProcessErrorLog(_le, _curPxyInfo, bXuLog_=eLogType_.isFwApiLogType, bUnhandledXcoBaseXcp_=unhandledXcoBaseXcp_ is not None, eLogifOpOption_=eLogifOpOption_)

        self.__helper.UpdateMaxLogTime(bErrorLogTime_=True)
        return res

    def _GetCurrentXTaskError(self):
        if self.__helper is None:
            return None

        _curPxyInfo = None if self.__lcpxy is None else self.__lcpxy.curProxyInfo
        if _curPxyInfo is None:
            return None

        _curTskInfo = _curPxyInfo.curTaskInfo
        if (_curTskInfo is None) or _curTskInfo.isInLcCeaseMode or not _curTskInfo.isDrivingXTask:
            _curPxyInfo.CleanUp()
            return None

        _xtc = _curTskInfo.xtaskConnector
        _curPxyInfo.CleanUp()

        return None if _xtc is None else _xtc._currentError

    def _GetCurrentXTaskErrorEntry(self, xuErrUniqueID_ : int) -> _ErrorEntry:
        if self.__helper is None:
            return None
        if not isinstance(xuErrUniqueID_, int):
            return None

        _curPxyInfo = None if self.__lcpxy is None else self.__lcpxy.curProxyInfo
        if (_curPxyInfo is None) or (_curPxyInfo.curTaskInfo is None) or _curPxyInfo.curTaskInfo.isInLcCeaseMode:
            if _curPxyInfo is not None:
                _curPxyInfo.CleanUp()
            return None

        _te = _curPxyInfo.curTaskInfo.taskError
        res = None if _te is None else _te._currentErrorEntry
        if res is None:
            vlogif._LogOEC(True, -1056)
        elif res.uniqueID != xuErrUniqueID_:
            res = None
            vlogif._LogOEC(True, -1057)

        _curPxyInfo.CleanUp()
        return res

    def _ClearCurrentXTaskError(self) -> bool:
        if self.__helper is None:
            return False

        _curPxyInfo = None if self.__lcpxy is None else self.__lcpxy.curProxyInfo
        if _curPxyInfo is None:
            return False

        _curTskInfo = _curPxyInfo.curTaskInfo
        if (_curTskInfo is None) or _curTskInfo.isInLcCeaseMode or not _curTskInfo.isDrivingXTask:
            _curPxyInfo.CleanUp()
            return False

        _xtc = _curTskInfo.xtaskConnector
        _curPxyInfo.CleanUp()

        res = False
        if _xtc is not None:
            res = _xtc._ClearCurrentError()
        return res


    @property
    def __isInvalid(self):
        return True if self.__helper is None else self.__helper.logConf is None

    @staticmethod
    def __IsDieXcpTargetMainTask():
        return _LogIFImpl.__dieXcpTarget == _LogIFImpl._EDieExceptionTarget.eFwMain

    @staticmethod
    def __NotifyCheckTaskError(curPxyInfo_ : _ProxyInfo, taskError_, errEntry_ : _ErrorEntry, bFTE_ : bool):
        _bConsumed = taskError_._OnErrorNotification(errEntry_)
        return _bConsumed

    @staticmethod
    def __NotifyTaskError(errEntry_ : _ErrorEntry, curPxyInfo_ : _ProxyInfo, errEvalCurTask_, errEvalFwMain_):
        res = True

        if errEvalFwMain_ is None:
            _bDoNotifCurTask = True
        else:
            errEntry_._SetErrorImpact(errEvalFwMain_, mtxErrImpact_=curPxyInfo_.fwMainInfo._errorImpactSyncMutex)
            res = _LogIFImpl.__NotifyCheckTaskError(curPxyInfo_, curPxyInfo_.fwMainInfo.taskError, errEntry_, True)

            if not res:
                _bDoNotifCurTask = False
            elif errEntry_.hasNoErrorImpact:
                _bDoNotifCurTask = False
            else:
                _bDoNotifCurTask = True

        if not res:
            pass
        else:
            if errEvalFwMain_ is None:
                errEntry_._SetErrorImpact(errEvalCurTask_)
            res =_LogIFImpl.__NotifyCheckTaskError(curPxyInfo_, curPxyInfo_.curTaskInfo.taskError, errEntry_, False)
        return res

    def __IsFwLogLevelEnabled(self, eFwLogLevel_) -> bool:
        return False if self.eLogLevel is None else _LogUtil.GetEnabledLogTypeGroup(eFwLogLevel_, self.eLogLevel) is not None

    def __DoCleanUp(self, bSkipVLogCleanup_ =False):
        if self.__helper is None:
            return

        if (_LogIFBase._theInstance is not None) and (id(self) == id(_LogIFBase._theInstance)):
            _LogIFBase._theInstance = None

        self.__helper.CleanUp()
        self.__lcpxy  = None
        self.__helper = None

        if not bSkipVLogCleanup_:
            vlogif._ClearLogHistory()

    def __CheckLogRequest( self
                         , curPxyInfo_           : _ProxyInfo
                         , eLogTypeGrp_          : _ELogType
                         , eLogType_             : _ELogType
                         , msg_                  =None
                         , errCode_              : int =None
                         , sysOpXcp_             =None
                         , xcpTraceback_         =None
                         , callstackLevelOffset_ =None
                         , unhandledXcoBaseXcp_  =None
                         , eLogifOpOption_       =_ELogifOperationOption.eDontCare
                         ):
        _bCreateLogOnly = eLogifOpOption_.isCreateLogOnly

        if curPxyInfo_ is None:
            if not _bCreateLogOnly:
                vlogif._LogOEC(True, -1058)
                return None, None

        if unhandledXcoBaseXcp_ is not None:
            xcpType = _CommonDefines._STR_EMPTY if unhandledXcoBaseXcp_._enclosedException is None else type(unhandledXcoBaseXcp_._enclosedException).__name__
            msg_ = _FwTDbEngine.GetText(_EFwTextID.eLogIFImpl_CheckLogRequest_Msg_01).format(xcpType, unhandledXcoBaseXcp_.uniqueID, unhandledXcoBaseXcp_.shortMessage)
            sysOpXcp_ = unhandledXcoBaseXcp_

        _bLockApi = eLogTypeGrp_.isError
        if _bLockApi: self.__helper.LockApi()


        _le        = None
        _caughtXcp = False

        _curTskInfo = None if curPxyInfo_ is None else curPxyInfo_.curTaskInfo
        _tid        = None if _curTskInfo is None else _curTskInfo.taskID

        try:
            _tname = _GetCurThread().name if _curTskInfo is None else _curTskInfo.taskName

            _le = self.__CreateLog( _tname
                                  , _tid
                                  , eLogTypeGrp_, eLogType_
                                  , shortMsg_=msg_, longMsg_=None
                                  , errCode_=errCode_, sysOpXcp_=sysOpXcp_
                                  , xcpTraceback_=xcpTraceback_, callstackLevelOffset_=callstackLevelOffset_
                                  , euRNum_=None if _curTskInfo is None else _curTskInfo.euRNumber)
        except BaseException as _xcp:
            _caughtXcp = True
            _LogUtil._RaiseException(_xcp)
        finally:
            if _caughtXcp or _le is None:
                if curPxyInfo_ is not None:
                    curPxyInfo_.CleanUp()
                if _bLockApi: self.__helper.UnlockApi()

                if _caughtXcp:
                    pass
                else:
                    return None, None

        if _le.isError:
            if _curTskInfo is not None:
                _le._Adapt(eTaskExecPhaseID_=_curTskInfo.eTaskExecPhase)
                _le._SetTaskInstance(tskInst_=_curTskInfo._taskInst)

        if _bCreateLogOnly:

            if _le.isFatalError:
                if _bCreateLogOnly:
                    _le._SetErrorImpact(_EErrorImpact.eImpactByFatalErrorDueToExecApiReturn if eLogifOpOption_.isCreateLogOnlyDueToExecApiAbort else _EErrorImpact.eImpactByFatalError)

                if self.isDieModeEnabled:
                    if _curTskInfo is not None:
                        _le._Adapt(bCleanupPermitted_=_curTskInfo.hasUnitTestTaskRight)
                if self.__helper.firstFatalLog is None:
                    self.__helper.firstFatalLog = _le.Clone()

            if curPxyInfo_ is not None:
                curPxyInfo_.CleanUp()
            if _bLockApi: self.__helper.UnlockApi()
            return None, _le

        if curPxyInfo_ is None:
            vlogif._LogOEC(True, -1059)
            return None, None

        if self.__helper.pendingTaskID is not None:
            if eLogifOpOption_.isSetErrorOnly:
                curPxyInfo_.CleanUp()
                vlogif._LogOEC(True, -1060)
                if _bLockApi: self.__helper.UnlockApi()
                return None, None

            elif _tid != self.__helper.pendingTaskID:
                curPxyInfo_.CleanUp()
                vlogif._LogOEC(True, -1061)
                if _bLockApi: self.__helper.UnlockApi()
                return None, None

            elif self.__helper.subSeqXcp is not None:
                curPxyInfo_.CleanUp()
                self.__helper.Flush(_le)
                if _bLockApi: self.__helper.UnlockApi()
                return None, None

        elif self.__helper.subSeqXcp is not None:
            vlogif._LogOEC(True, -1062)
            curPxyInfo_.CleanUp()
            if _bLockApi: self.__helper.UnlockApi()
            return None, None

        if _le.isError:
            _curTEE = _curTskInfo.taskError._currentErrorEntry

            if _curTEE is not None:

                if _curTEE.isFatalError:

                    if _le.isFatalError:
                        _midPart = _FwTDbEngine.GetText(_EFwTextID.eMisc_Fatal)

                        _te = _curTskInfo.taskError
                        _le._SetErrorImpact(_EErrorImpact.eNoImpactByExistingFatalError)
                        _shortMsg  = _FwTDbEngine.GetText(_EFwTextID.eLogIFImpl_CheckLogRequest_Msg_02)
                        _shortMsg  = _shortMsg.format(_midPart, _midPart, _te.currentErrorUniqueID)
                        _shortMsg += _FwTDbEngine.GetText(_EFwTextID.eLogIFImpl_CheckLogRequest_Msg_03).format(_le.uniqueID, _le.shortMessage)
                        _le._Adapt(shortMsg_=_shortMsg)
                        _buf = _shortMsg
                    else:
                        _buf = _le

                    curPxyInfo_.CleanUp()

                    self.__helper.Flush(_buf)
                    if _bLockApi: self.__helper.UnlockApi()
                    return None, None

                else:
                    if _le.isFatalError:
                        _curTEE._UpdateErrorImpact(_EErrorImpact.eNoImpactByLogTypePrecedence)
                    else:
                        _te = _curTskInfo.taskError
                        _midPart = _FwTDbEngine.GetText(_EFwTextID.eMisc_Fatal) if _te.isFatalError else _FwTDbEngine.GetText(_EFwTextID.eMisc_User)

                        _le._SetErrorImpact(_EErrorImpact.eNoImpactByExistingUserError)
                        _shortMsg  = _FwTDbEngine.GetText(_EFwTextID.eLogIFImpl_CheckLogRequest_Msg_02)
                        _shortMsg  = _shortMsg.format(_FwTDbEngine.GetText(_EFwTextID.eMisc_User), _midPart, _te.currentErrorUniqueID)
                        _shortMsg += _FwTDbEngine.GetText(_EFwTextID.eLogIFImpl_CheckLogRequest_Msg_03).format(_le.uniqueID, _le.shortMessage)
                        _le._Adapt(shortMsg_=_shortMsg)

                        curPxyInfo_.CleanUp()

                        self.__helper.Flush(_shortMsg)
                        if _bLockApi: self.__helper.UnlockApi()
                        return None, None

        else:
            curPxyInfo_.CleanUp()
            if eLogifOpOption_.isSetErrorOnly:
                if _bLockApi: self.__helper.UnlockApi()
                vlogif._LogOEC(True, -1063)
            else:
                self.__helper.Flush(_le)
                if _bLockApi: self.__helper.UnlockApi()
            return None, None

        return curPxyInfo_, _le

    def __CreateLog(self, taskName_, taskID_, eLogTypeGrpID_ : _ELogType, eLogType_: _ELogType
                    , shortMsg_: str = None, longMsg_: str = None
                    , errCode_: int = None, sysOpXcp_=None, xcpTraceback_=None, callstackLevelOffset_ =None, euRNum_ =None):

        if eLogType_._absoluteValue >= _ELogType.FTL.value:
            if eLogTypeGrpID_ != _ELogType.FTL:
                vlogif._LogOEC(True, -1064)
                return None

            _xcpCls = _LogIFImpl.__logExceptionClassMap[eLogType_]
            if eLogType_._absoluteValue == _ELogType.FTL_SYS_OP_XCP.value:
                _xcp = _xcpCls(sysOpXcp_, xcpTraceback_, errCode_=errCode_
                    , taskName_=taskName_, taskID_=taskID_, shortMsg_=shortMsg_, longMsg_=longMsg_
                    , callstackLevelOffset_=callstackLevelOffset_, euRNum_=euRNum_)
            else:
                _xcp = _xcpCls(errCode_=errCode_
                    , taskName_=taskName_, taskID_=taskID_, shortMsg_=shortMsg_, longMsg_=longMsg_
                    , callstackLevelOffset_=callstackLevelOffset_, euRNum_=euRNum_, bFwApiLog_=eLogType_.isFwApiLogType)

            if self.isExceptionModeEnabled:
                _le = _xcp._enclosedFatalEntry
            else:
                _le = _xcp._DetachEnclosedFatalEntry()
                _xcp.CleanUp()
        elif eLogType_._absoluteValue >= _ELogType.ERR.value:
            _le = _ErrorEntry(eLogType_, errCode_=errCode_, taskName_=taskName_, taskID_=taskID_
                , shortMsg_=shortMsg_, longMsg_=longMsg_, callstackLevelOffset_=callstackLevelOffset_, euRNum_=euRNum_)
        else:
            _le = _LogEntry(eLogType_, taskName_=taskName_, taskID_=taskID_
                , shortMsg_=shortMsg_, longMsg_=longMsg_, callstackLevelOffset_=callstackLevelOffset_, euRNum_=euRNum_)

        if _le is None:
            return None
        if not _le.isValid:
            _le.CleanUp()
            return None

        if _le.isError:
            if not isinstance(_le, _ErrorEntry):
                tmp = str(_le)
                _le.CleanUp()
                vlogif._LogOEC(True, -1065)
                return None
            elif isinstance(_le, _FatalEntry):
                if _le._enclosedByLogException is None:
                    tmp = str(_le)
                    _le.CleanUp()
                    vlogif._LogOEC(True, -1066)
                    return None
            elif _le._enclosedByLogException is not None:
                tmp = str(_le)
                _le.CleanUp()
                vlogif._LogOEC(True, -1067)
                return None

        self.__helper.counter[eLogTypeGrpID_._absoluteValue] += 1
        self.__helper.AddLogEntry(_le)
        return _le

    def __CreateCompactLog( self, eLogTypeGrpID_ : _ELogType, eLogType_: _ELogType
                          , shortMsg_: str = None, longMsg_: str = None):

        _tname    = None
        _bXTask = False if self.isReleaseModeEnabled else None

        if self.__lcpxy is None:
            pass
        else:
            _tmgr = self.__lcpxy.taskManager

            if _tmgr is None:
                pass
            else:
                _tname, _bXTask = _tmgr._GetProxyInfoReplacementData()

        _le = _LogEntry(eLogType_, taskName_=_tname, shortMsg_=shortMsg_, longMsg_=longMsg_, bXTaskTask_=_bXTask)
        if _le is None:
            pass
        elif not _le.isValid:
            _le.CleanUp()
            _le = None
        else:
            self.__helper.counter[eLogTypeGrpID_._absoluteValue] += 1
            self.__helper.AddLogEntry(_le)
        return _le

    def __ProcessErrorLog(self, errEntry_ : _ErrorEntry, curPxyInfo_, bXuLog_ : bool, bUnhandledXcoBaseXcp_ =False, eLogifOpOption_ =_ELogifOperationOption.eDontCare):

        _eevFM = None
        _eevCT = None
        _eevCT, _eevFM = self.__EvaluateErrorLog(errEntry_, curPxyInfo_)

        if _eevCT is None:
            curPxyInfo_.CleanUp()
            self.__helper.SetPendingTaskID(None)
            if self.__helper.subSeqXcp is not None:
                self.__helper.subSeqXcp.CleanUp()
                self.__helper.subSeqXcp = None
            self.__helper.UnlockApi()
            return None

        _xcpCaught = None
        _bSEOK     = False
        try:
            _bSEOK = _LogIFImpl.__NotifyTaskError(errEntry_, curPxyInfo_, _eevCT, _eevFM)
        except _XcoExceptionRoot as _xcp:
            _xcpCaught = _xcp
        except BaseException as _xcp:
            _xcpCaught = _XcoBaseException(_xcp, tb_=_LogUtil._GetFormattedTraceback(), taskID_=curPxyInfo_.curTaskInfo.taskID)


        _bCTAE = curPxyInfo_.curTaskInfo.taskBadge.isAutoEnclosed

        curPxyInfo_.CleanUp()
        _ssXcp = self.__helper.subSeqXcp
        self.__helper.subSeqXcp = None
        self.__helper.SetPendingTaskID(None)
        self.__helper.UnlockApi()

        res = None

        if not _bSEOK:

            if _ssXcp is not None:
                _ssXcp.CleanUp()

            if _xcpCaught is not None:
                if not _xcpCaught.isXTaskException:
                    _xcpCaught.CleanUp()

            if errEntry_.hasErrorImpact:
                errEntry_._UpdateErrorImpact(_EErrorImpact.eNoImpactByOperationFailureSetError)

        elif errEntry_.hasNoErrorImpact:
            pass
        elif eLogifOpOption_.isSetErrorOnly or bUnhandledXcoBaseXcp_:
            if _ssXcp is not None:
                _ssXcp.CleanUp()
        elif not _eevCT.isCausedByExceptionMode:
            if _ssXcp is not None:
                _ssXcp.CleanUp()

            self.__helper.Flush(errEntry_)

        else:
            res = self.__RaiseException(errEntry_._enclosedByLogException, _eevCT, bXuLog_, _bCTAE, subSeqXcp_=_ssXcp)
        return res

    def __EvaluateErrorLog(self, errEntry_, curPxyInfo_):

        _eevCT, _eevFM = None, None

        if not _LogIFImpl.__IsDieXcpTargetMainTask():
            vlogif._LogOEC(True, -1068)
            return _eevCT, _eevFM

        _fwmInfo = curPxyInfo_.fwMainInfo

        if errEntry_.isFatalError:

            if self.isDieXcpModeEnabled:

                if _fwmInfo is None:
                    if not curPxyInfo_.curTaskInfo.taskBadge.hasDieXcpTargetTaskRight:
                        vlogif._LogOEC(True, -1069)
                    else:
                        _eevCT = _EErrorImpact.eImpactByDieException
                else:
                    _eevCT = _EErrorImpact.eImpactByDieException

                    if not _fwmInfo.taskBadge.hasDieExceptionDelegateTargetTaskRight:
                        vlogif._LogOEC(True, -1070)
                    else:
                        _eevFM = _EErrorImpact.eImpactByDieException

            elif self.isExceptionModeEnabled:
                _eevCT = _EErrorImpact.eImpactByLogException

                if _fwmInfo is not None:
                    if _fwmInfo.taskBadge.hasErrorObserverTaskRight:
                        _eevFM = _EErrorImpact.eImpactByLogException

            elif self.isDieModeEnabled:
                _eevCT = _EErrorImpact.eImpactByDieError

                if _fwmInfo is not None:
                    _eevFM = _EErrorImpact.eImpactByDieError

            else:
                _eevCT = _EErrorImpact.eImpactByFatalError

                if _fwmInfo is not None:
                    if _fwmInfo.taskBadge.hasErrorObserverTaskRight:
                        _eevFM = _EErrorImpact.eImpactByFatalError
        else:
            _eevCT = _EErrorImpact.eImpactByUserError

            if _fwmInfo is not None:
                if _fwmInfo.taskBadge.hasErrorObserverTaskRight:
                    _eevFM = _EErrorImpact.eImpactByUserError

        if _eevCT is None:
            vlogif._LogOEC(True, -1071)
            _eevCT, _eevFM = None, None
        elif (_fwmInfo is not None) and (_eevFM is None):
            _eevCT = None
            vlogif._LogOEC(True, -1072)

        return _eevCT, _eevFM

    def __RaiseException(self, logXcp_ : _LogException, eevCurTask_ : _EErrorImpact, bXuLog_ : bool, bCurTaskAutoEnclosed_ : bool, subSeqXcp_ =None):
        if not isinstance(logXcp_, _LogException):
            vlogif._LogOEC(True, -1073)
            return None
        if not (isinstance(eevCurTask_, _EErrorImpact) and eevCurTask_.isCausedByExceptionMode):
            vlogif._LogOEC(True, -1074)
            return None


        if subSeqXcp_ is not None:
            logXcp_ = _LogExceptionNestedError(logXcp_, subSeqXcp_)

        res          = None
        _bRaiseXtXcp = bXuLog_

        if not _bRaiseXtXcp:
            _myFE = logXcp_._enclosedFatalEntry
            _bRaiseXtXcp = _myFE.eTaskExecPhase.isXTaskExecution

        if eevCurTask_.isCausedByDieMode:

            if eevCurTask_ == _EErrorImpact.eImpactByDieException:
                if bCurTaskAutoEnclosed_:
                    pass
                elif _bRaiseXtXcp:
                    _xtXcpBase = _XTaskExceptionBase(uid_=logXcp_.uniqueID, xm_=logXcp_.message, ec_=logXcp_.errorCode, tb_=logXcp_.traceback, cst_=logXcp_.callstack, bDieXcp_=True, clone_=None)
                    res = XTaskException(_xtXcpBase)
                else:
                    res = _DieException(enclLogXcp_=logXcp_)
        else:

            if eevCurTask_ != _EErrorImpact.eImpactByLogException:
                pass
            else:
                if bCurTaskAutoEnclosed_:
                    self.__helper.Flush(logXcp_)
                elif _bRaiseXtXcp:
                    _xtXcpBase = _XTaskExceptionBase(uid_=logXcp_.uniqueID, xm_=logXcp_.message, ec_=logXcp_.errorCode, tb_=logXcp_.traceback, cst_=logXcp_.callstack, bDieXcp_=False, clone_=None)
                    res = XTaskException(_xtXcpBase)
                else:
                    res = logXcp_

        if (res is None) and bCurTaskAutoEnclosed_:
            return None

        _bOK =        isinstance(res, XTaskException)
        _bOK = _bOK or isinstance(res, _LogException)
        _bOK = _bOK or isinstance(res, _DieException)
        _bOK = _bOK or isinstance(res._enclosedLogException, _LogException)
        if not _bOK:
            vlogif._LogOEC(True, -1075)
            return None

        return res


