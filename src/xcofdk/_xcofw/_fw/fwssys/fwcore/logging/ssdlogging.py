# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : ssdlogging.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from _fw.fwssys.fwcore.logging                    import logif
from _fw.fwssys.fwcore.logging                    import vlogif
from _fw.fwssys.fwcore.logging.logdefines         import _LogUniqueID
from _fw.fwssys.fwcore.logging.logdefines         import _LogConfig
from _fw.fwssys.fwcore.logging.logentry           import _LogEntry
from _fw.fwssys.fwcore.logging.logmgr             import _LogMgr
from _fw.fwssys.fwcore.config.fwcfgdefines        import _ESubSysID
from _fw.fwssys.fwcore.config.ssyscfg.fwssyscbase import _FwSSysConfigBase
from _fw.fwssys.fwcore.config.ssyscfg.ssclogging  import _SSConfigLogging
from _fw.fwssys.fwcore.lc.lcdefines               import _ELcScope
from _fw.fwssys.fwcore.lc.lcssysdeputy            import _LcSSysDeputy
from _fw.fwssys.fwcore.types.commontypes          import _EDepInjCmd
from _fw.fwssys.fwerrh.fwerrorcodes               import _EFwErrorCode
from _fw.fwssys.fwerrh.logs.xcoexception          import _XcoException

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _SSDeputyLogging(_LcSSysDeputy):
    __slots__ = []

    def __init__(self, ppass_ : int):
        super().__init__(ppass_, _ESubSysID.eLogging, _ELcScope.ePreIPC)

    def _CleanUpByOwnerRequest(self):
        _LcSSysDeputy._CleanUpByOwnerRequest(self)

    def _ProcDeputyCmd(self, tgtScope_ : _ELcScope, dinjCmd_ : _EDepInjCmd, subsysCfg_ : _FwSSysConfigBase) -> bool:
        if not isinstance(dinjCmd_, _EDepInjCmd):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00468)
            return False
        elif not isinstance(subsysCfg_, _SSConfigLogging):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00469)
            return False
        elif dinjCmd_.isFinalize:
            return True

        res = True
        for _n, _m in _SSConfigLogging._ELoggingConfigEntityID.__members__.items():
            if dinjCmd_.isDeInject and (_m != _SSConfigLogging._ELoggingConfigEntityID.eLogIF__CleanUp):
                continue

            if _m == _SSConfigLogging._ELoggingConfigEntityID.eLogConfig__CI:
                _LogConfig._DepInjection(dinjCmd_)

            elif _m == _SSConfigLogging._ELoggingConfigEntityID.eXcoException__ReleaseModeStatus:
                _XcoException._DepInjection(dinjCmd_, subsysCfg_.isXcoExceptionReleaseModeEnabled)

            elif _m == _SSConfigLogging._ELoggingConfigEntityID.eLogEntryHighlighting__Set:
                _LogEntry._DepInjection(dinjCmd_, subsysCfg_.isLogHighlightingEnabled)

            elif _m == _SSConfigLogging._ELoggingConfigEntityID.eFwLogEntryHeaderFormat__Set:
                _hdrCfg = subsysCfg_.fwLogHeaderFormat
                _LogEntry._DepInjection(dinjCmd_, None, False
                                       , includeUniqueID_=_hdrCfg.isUniqueIDEnabled
                                       , includeTimestamp_=_hdrCfg.isTimestampEnabled
                                       , includeTaskName_=_hdrCfg.isTaskNameEnabled
                                       , includeTaskID_=_hdrCfg.isTaskIDEnabled
                                       , includeFuncName_=_hdrCfg.isFuncNameEnabled
                                       , includeFileName_=_hdrCfg.isFileNameEnabled
                                       , includeLineNo_=_hdrCfg.isLineNoEnabled
                                       , includeCallstack_=_hdrCfg.isCallstackEnabled
                                       , includeRaisedByInfo_=_hdrCfg.isRaisedByInfoEnabled
                                       , includeEuNum_=_hdrCfg.isExecUnitNumEnabled
                                       , includeErrImp_=_hdrCfg.isErrorImpactEnabled
                                       , includeExecPhase_=_hdrCfg.isExecUnitNumEnabled)

            elif _m == _SSConfigLogging._ELoggingConfigEntityID.eUserLogEntryHeaderFormat__Set:
                _hdrCfg = subsysCfg_.userLogHeaderFormat
                _LogEntry._DepInjection(dinjCmd_, None, True
                                       , includeUniqueID_=_hdrCfg.isUniqueIDEnabled
                                       , includeTimestamp_=_hdrCfg.isTimestampEnabled
                                       , includeTaskName_=_hdrCfg.isTaskNameEnabled
                                       , includeTaskID_=_hdrCfg.isTaskIDEnabled
                                       , includeFuncName_=_hdrCfg.isFuncNameEnabled
                                       , includeFileName_=_hdrCfg.isFileNameEnabled
                                       , includeLineNo_=_hdrCfg.isLineNoEnabled
                                       , includeCallstack_=_hdrCfg.isCallstackEnabled
                                       , includeRaisedByInfo_=_hdrCfg.isRaisedByInfoEnabled
                                       , includeEuNum_=_hdrCfg.isExecUnitNumEnabled
                                       , includeErrImp_=_hdrCfg.isErrorImpactEnabled
                                       , includeExecPhase_=_hdrCfg.isExecUnitNumEnabled)

            elif _m == _SSConfigLogging._ELoggingConfigEntityID.eLogIF__CleanUp:
                _LogMgr._DepInjection(dinjCmd_)

            elif _m == _SSConfigLogging._ELoggingConfigEntityID.eVLoggingImpl__CleanUp:
                vlogif._VLoggingImpl._DepInjection(dinjCmd_, subsysCfg_.fwStartupConfig._isSilentFwLogLevel)

            elif _m == _SSConfigLogging._ELoggingConfigEntityID.eLogUniqueID__Reset:
                _LogUniqueID._DepInjection(dinjCmd_)

            elif _m == _SSConfigLogging._ELoggingConfigEntityID.eLogConfig__Setup:
                _bRelMode   = subsysCfg_.fwStartupPolicy.isReleaseModeEnabled
                _bDieMode   = subsysCfg_.isFwDieModeEnabled
                _bXcpMode   = subsysCfg_.isFwExceptionModeEnabled
                _logLevel   = subsysCfg_.fwLogLevel
                _ulogLevel  = subsysCfg_.userLogLevel
                _bVSEtMode  = not _bRelMode

                _LogConfig._DepInjection( dinjCmd_
                                        , bRelMode_=_bRelMode
                                        , eLogLevel_=_logLevel
                                        , eUserLogLevel_=_ulogLevel
                                        , bDieMode_=_bDieMode
                                        , bXcpMode_=_bXcpMode
                                        , bVSEMode_=_bVSEtMode)
            else:
                res = False
                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_SSDeputyLogging_TID_001).format(_m.value)

                if subsysCfg_.fwStartupPolicy.isReleaseModeEnabled:
                    logif._LogImplErrorEC(_EFwErrorCode.FE_00820, _errMsg)
                else:
                    logif._LogImplErrorEC(_EFwErrorCode.FE_00821, _errMsg)
                break
        return res
