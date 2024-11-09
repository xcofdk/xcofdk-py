# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : ssclogging.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from enum import auto
from enum import unique

from xcofdk._xcofw.fw.fwssys.fwcore.logging            import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logdefines import _ELogLevel
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes  import _FwIntEnum

from xcofdk._xcofw.fw.fwssys.fwcore.config.fwcfgdefines                import _ESubSysID
from xcofdk._xcofw.fw.fwssys.fwcore.config.logheadrfmt                 import _LogHeaderFormat
from xcofdk._xcofw.fw.fwssys.fwcore.config.ssysconfig.fwssysconfigbase import _FwSSysConfigBase
from xcofdk._xcofw.fw.fwssys.fwcore.config.ssysconfig.fwssysconfigbase import _FwStartupPolicy
from xcofdk._xcofw.fw.fwssys.fwcore.config.ssysconfig.fwssysconfigbase import _FwStartupConfig


class _SSConfigLogging(_FwSSysConfigBase):

    @unique
    class _ELoggingConfigEntityID(_FwIntEnum):
        eEnvConfig__EnvVarsEvalStatus    = 200
        eLoggingConfig__CleanUp          = auto()
        eXcoException__ReleaseModeStatus = auto()
        eLogEntryHighlighting__Set       = auto()
        eFwLogEntryHeaderFormat__Set     = auto()
        eUserLogEntryHeaderFormat__Set   = auto()
        eLogIF__CleanUp                  = auto()
        eVLoggingImpl__CleanUp           = auto()
        eLogUniqueID__Reset              = auto()
        eLoggingDefaultConfig__Setup     = auto()
        eLoggingUserConfig__Update       = auto()

    __slots__ = [ '__fwLHdrFmt' , '__userLHdrFmt']

    def __init__(self, ppass_ : int, suPolicy_ : _FwStartupPolicy, startupCfg_ : _FwStartupConfig):
        self.__fwLHdrFmt   = None
        self.__userLHdrFmt = None
        super().__init__(ppass_, _ESubSysID.eLogging, suPolicy_, startupCfg_)

        if not self.isValid:
            self.CleanUpByOwnerRequest(ppass_)
        else:
            self.__CreateLogHeaderFormat()

    @property
    def isFwDieModeEnabled(self):
        return self.fwStartupConfig._isFwDieModeEnabled

    @property
    def isFwExceptionModeEnabled(self):
        return self.fwStartupConfig._isFwExceptionModeEnabled

    @property
    def isXcoExceptionReleaseModeEnabled(self):
        return self.fwStartupConfig._isReleaseModeEnabled

    @property
    def isUserDieModeEnabled(self):
        return self.fwStartupConfig._isUserDieModeEnabled

    @property
    def isUserExceptionModeEnabled(self):
        return self.fwStartupConfig._isUserExceptionModeEnabled

    @property
    def isLogHighlightingEnabled(self):
        return self.fwStartupConfig._isUserLogHighlightingEnabled

    @property
    def isEnvVarsEvaluationEnabled(self):
        return not self.fwStartupConfig._isIgnoreEvnVarsEnabled

    @property
    def fwLogLevel(self):
        return self.fwStartupConfig._fwLogLevel

    @property
    def userLogLevel(self):
        return self.fwStartupConfig._userLogLevel

    @property
    def fwLogHeaderFormat(self):
        return self.__fwLHdrFmt

    @property
    def userLogHeaderFormat(self):
        return self.__userLHdrFmt

    def _ToString(self):
        if self.subsystemID is None:
            return None
        return _FwSSysConfigBase._ToString(self)

    def _CleanUpByOwnerRequest(self):
        if self.__userLHdrFmt is not None:
            self.__userLHdrFmt.CleanUpByOwnerRequest(self._myPPass)
            self.__userLHdrFmt = None
        if self.__fwLHdrFmt is not None:
            self.__fwLHdrFmt.CleanUpByOwnerRequest(self._myPPass)
            self.__fwLHdrFmt = None
        super()._CleanUpByOwnerRequest()

    def __CreateLogHeaderFormat(self):
        _bRelMode = self.fwStartupConfig._isReleaseModeEnabled

        _fwLHdrFmt_ = _LogHeaderFormat.CreateFwLogHeaderFormat(self._myPPass, True, _bRelMode)
        if _fwLHdrFmt_ is None:
            return False
        _fwLHdrFmt_._Update(timestamp_=self.fwStartupConfig._isUserLogTimestampEnabled)

        _userLHdrFmt_ = _LogHeaderFormat.CreateFwLogHeaderFormat(self._myPPass, False, _bRelMode)
        if _userLHdrFmt_ is None:
            return False
        _bCallStack = self.userLogLevel.value >= _ELogLevel.eDebug.value
        _userLHdrFmt_._Update(timestamp_=self.fwStartupConfig._isUserLogTimestampEnabled, callstack_=_bCallStack)

        self.__fwLHdrFmt   = _fwLHdrFmt_
        self.__userLHdrFmt = _userLHdrFmt_
        return True
