# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : ssdlogging.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from xcofdk._xcofw.fw.fwssys.fwcore.config.fwcfgdefines                import _ESubSysID
from xcofdk._xcofw.fw.fwssys.fwcore.config.ssysconfig.fwssysconfigbase import _FwSSysConfigBase
from xcofdk._xcofw.fw.fwssys.fwcore.config.ssysconfig.ssclogging       import _SSConfigLogging
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcdefines                       import _ELcScope
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcssysdeputy                    import _LcSSysDeputy
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes                  import _FwIntEnum

from xcofdk._xcofw.fw.fwssys.fwcore.logging              import logif
from xcofdk._xcofw.fw.fwssys.fwcore.logging              import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logdefines   import _LogUniqueID
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logconfig    import _LoggingConfig
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logconfig    import _LoggingUserConfig
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logconfig    import _LoggingDefaultConfig
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logconfig    import _LoggingEnvConfig
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logentry     import _LogEntry
from xcofdk._xcofw.fw.fwssys.fwcore.logging.xcoexception import _XcoException
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logifbase    import _LogIFBase

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine


class _SSDeputyLogging(_LcSSysDeputy):

    __slots__ = []

    def __init__(self, ppass_ : int):
        super().__init__(ppass_, _ESubSysID.eLogging, _ELcScope.ePreIPC)

    def _CleanUpByOwnerRequest(self):
        _LcSSysDeputy._CleanUpByOwnerRequest(self)

    def _ProcDeputyCmd(self, tgtScope_ : _ELcScope, deputyCmd_ : _FwIntEnum, subsysCfg_ : _FwSSysConfigBase) -> bool:

        if not isinstance(deputyCmd_, _LcSSysDeputy._EDDeputyCmd):
            vlogif._LogOEC(True, -1093)
            return False
        elif not isinstance(subsysCfg_, _SSConfigLogging):
            vlogif._LogOEC(True, -1094)
            return False
        elif deputyCmd_.isFinalize:
            return True

        res = True

        for name, member in _SSConfigLogging._ELoggingConfigEntityID.__members__.items():

            if deputyCmd_.isDeInject and (member != _SSConfigLogging._ELoggingConfigEntityID.eLogIF__CleanUp):
                continue

            if member == _SSConfigLogging._ELoggingConfigEntityID.eEnvConfig__EnvVarsEvalStatus:
                _LoggingEnvConfig._InjectEvaluationStatus(not subsysCfg_.fwStartupConfig._isIgnoreEvnVarsEnabled)

            elif member == _SSConfigLogging._ELoggingConfigEntityID.eLoggingConfig__CleanUp:
                _loggCfg = _LoggingConfig.GetInstance(bCreate_=False)
                if _loggCfg is not None:
                    _loggCfg.CleanUp()

            elif member == _SSConfigLogging._ELoggingConfigEntityID.eXcoException__ReleaseModeStatus:
                _XcoException._InjectReleaseModeStatus(subsysCfg_.isXcoExceptionReleaseModeEnabled)

            elif member == _SSConfigLogging._ELoggingConfigEntityID.eLogEntryHighlighting__Set:
                _LogEntry._SetLogHighlightingMode(subsysCfg_.isLogHighlightingEnabled)

            elif member == _SSConfigLogging._ELoggingConfigEntityID.eFwLogEntryHeaderFormat__Set:
                _hdrCfg = subsysCfg_.fwLogHeaderFormat
                _LogEntry._SetFwFormatTags( includeUniqueID_=_hdrCfg.isUniqueIDEnabled
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

            elif member == _SSConfigLogging._ELoggingConfigEntityID.eUserLogEntryHeaderFormat__Set:
                _hdrCfg = subsysCfg_.userLogHeaderFormat
                _LogEntry._SetUserFormatTags( includeUniqueID_=_hdrCfg.isUniqueIDEnabled
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

            elif member == _SSConfigLogging._ELoggingConfigEntityID.eLogIF__CleanUp:
                if _LogIFBase.GetInstance() is not None:
                    _LogIFBase.GetInstance().CleanUp()

            elif member == _SSConfigLogging._ELoggingConfigEntityID.eVLoggingImpl__CleanUp:
                vlogif._VLoggingImpl._CleanUp()

            elif member == _SSConfigLogging._ELoggingConfigEntityID.eLogUniqueID__Reset:
                _LogUniqueID._Reset()

            elif member == _SSConfigLogging._ELoggingConfigEntityID.eLoggingDefaultConfig__Setup:
                _paramDieMode      = subsysCfg_.isFwDieModeEnabled
                _paramXcpMode      = subsysCfg_.isFwExceptionModeEnabled
                _paramLogLevel     = subsysCfg_.fwLogLevel
                _paramRelMode      = subsysCfg_.fwStartupPolicy.isReleaseModeEnabled
                _paramVsysExitMode = not _paramRelMode

                _strCurDefault    = None
                _strNewDefault    = None
                _strDefaultLogCfg = None
                _strDefaultLogCfg = _LoggingDefaultConfig._SetUp(bDieMode_=_paramDieMode, bExceptionMode_=_paramXcpMode, bRelMode_=_paramRelMode, bVSysExitMode_=_paramVsysExitMode, eLogLevel_=_paramLogLevel)
            elif member == _SSConfigLogging._ELoggingConfigEntityID.eLoggingUserConfig__Update:
                _paramDieMode  = subsysCfg_.isUserDieModeEnabled
                _paramXcpMode  = subsysCfg_.isUserExceptionModeEnabled
                _paramLogLevel = subsysCfg_.userLogLevel

                _strCurCfg = None
                _strNewCfg = None
                _strNewCfg = _LoggingUserConfig._Update(bUserDieMode_=_paramDieMode, bUserXcpMode_=_paramXcpMode, eUserLogLevel_=_paramLogLevel)
            else:
                res = False
                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_SSDeputyLogging_TextID_001).format(member.value)

                if subsysCfg_.fwStartupPolicy.isReleaseModeEnabled:
                    logif._LogImplError(_errMsg)
                else:
                    logif._LogImplError(_errMsg)
                break
        return res
