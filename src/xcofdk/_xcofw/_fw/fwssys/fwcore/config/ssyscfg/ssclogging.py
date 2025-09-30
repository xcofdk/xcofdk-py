# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : ssclogging.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum import auto
from enum import unique

from _fw.fwssys.fwcore.logging            import vlogif
from _fw.fwssys.fwcore.logging.logdefines import _ELogLevel
from _fw.fwssys.fwcore.types.commontypes  import _FwIntEnum

from _fw.fwssys.fwcore.config.fwcfgdefines        import _ESubSysID
from _fw.fwssys.fwcore.config.logheadrfmt         import _LogHeaderFormat
from _fw.fwssys.fwcore.config.ssyscfg.fwssyscbase import _FwSSysConfigBase
from _fw.fwssys.fwcore.config.ssyscfg.fwssyscbase import _FwStartupPolicy
from _fw.fwssys.fwcore.config.ssyscfg.fwssyscbase import _FwStartupConfig

class _SSConfigLogging(_FwSSysConfigBase):
    @unique
    class _ELoggingConfigEntityID(_FwIntEnum):
        eLogConfig__CI                   = 200
        eXcoException__ReleaseModeStatus = auto()
        eLogEntryHighlighting__Set       = auto()
        eFwLogEntryHeaderFormat__Set     = auto()
        eUserLogEntryHeaderFormat__Set   = auto()
        eLogIF__CleanUp                  = auto()
        eVLoggingImpl__CleanUp           = auto()
        eLogUniqueID__Reset              = auto()
        eLogConfig__Setup                = auto()

    __slots__ = [ '__hf' , '__hfu']

    def __init__(self, ppass_ : int, suPolicy_ : _FwStartupPolicy, startupCfg_ : _FwStartupConfig):
        self.__hf  = None
        self.__hfu = None
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
        return self.fwStartupConfig._isLogHighlightingEnabled

    @property
    def fwLogLevel(self):
        return self.fwStartupConfig._fwLogLevel

    @property
    def userLogLevel(self):
        return self.fwStartupConfig._userLogLevel

    @property
    def fwLogHeaderFormat(self):
        return self.__hf

    @property
    def userLogHeaderFormat(self):
        return self.__hfu

    def _ToString(self):
        if self.subsystemID is None:
            return None
        return _FwSSysConfigBase._ToString(self)

    def _CleanUpByOwnerRequest(self):
        if self.__hfu is not None:
            self.__hfu.CleanUpByOwnerRequest(self._myPPass)
            self.__hfu = None
        if self.__hf is not None:
            self.__hf.CleanUpByOwnerRequest(self._myPPass)
            self.__hf = None
        super()._CleanUpByOwnerRequest()

    def __CreateLogHeaderFormat(self):
        _bRM = self.fwStartupConfig._isReleaseModeEnabled
        _bCS = self.fwStartupConfig._isLogCallstackEnabled
        _bTS = self.fwStartupConfig._isLogTimestampEnabled

        _fwLHdrFmt = _LogHeaderFormat.CreateLogHeaderFormat(self._myPPass, True, _bRM)
        if _fwLHdrFmt is None:
            return False
        _fwLHdrFmt._Update(timestamp_=_bTS, callstack_=_bCS)

        _userLHdrFmt = _LogHeaderFormat.CreateLogHeaderFormat(self._myPPass, False, _bRM)
        if _userLHdrFmt is None:
            return False
        _userLHdrFmt._Update(timestamp_=_bTS, callstack_=_bCS)

        self.__hf  = _fwLHdrFmt
        self.__hfu = _userLHdrFmt
        return True
