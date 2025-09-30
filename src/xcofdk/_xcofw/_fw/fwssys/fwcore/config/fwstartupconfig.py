# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwstartupconfig.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from _fw.fwssys.fwcore.logging                import vlogif
from _fw.fwssys.fwcore.logging.logdefines     import _ELogLevel
from _fw.fwssys.fwcore.config.fwsoptionsimpl  import _FwSOptionsImpl
from _fw.fwssys.fwcore.config.fwstartuppolicy import _FwStartupPolicy
from _fw.fwssys.fwcore.types.apobject         import _ProtAbsSlotsObject
from _fw.fwssys.fwcore.types.commontypes      import _CommonDefines

class _FwStartupConfig(_ProtAbsSlotsObject):
    __slots__ = [ '__sup' , '__sopt' ]

    def __init__(self, ppass_ : int, fwStartupPolicy_ : _FwStartupPolicy, fwSOpt_ : _FwSOptionsImpl):
        self.__sup  = None
        self.__sopt = None
        super().__init__(ppass_)

        if not (fwStartupPolicy_.isValid and fwSOpt_._isValid):
            self.CleanUpByOwnerRequest(ppass_)
        else:
            self.__sup  = fwStartupPolicy_
            self.__sopt = fwSOpt_

    @property
    def _isValid(self):
        return not self.__isInvalid

    @property
    def _isReleaseModeEnabled(self) -> bool:
        if self.__isInvalid: return False
        return self.__sup.isReleaseModeEnabled and not self.__sopt._isReleaseModeDisabled

    @property
    def _isSilentFwLogLevel(self) -> bool:
        if self.__isInvalid: return False
        return self.__sopt._IsSilentFwLogLevel()

    @property
    def _isLogTimestampEnabled(self) -> bool:
        if self.__isInvalid: return False
        return not self.__sopt._isLogTimestampDisabled

    @property
    def _isLogHighlightingEnabled(self) -> bool:
        if self.__isInvalid: return False
        return not self.__sopt._isLogHighlightingDisabled

    @property
    def _isLogCallstackEnabled(self) -> bool:
        if self.__isInvalid: return False
        return not self.__sopt._isLogCallstackDisabled

    @property
    def _isUserDieModeEnabled(self) -> bool:
        if self.__isInvalid: return False
        return not self.__sopt._isUserDieModeDisabled

    @property
    def _isUserSuppressFwWarningsEnabled(self) -> bool:
        if self.__isInvalid: return False
        return self.__sopt._isUserSuppressFwWarningsEnabled

    @property
    def _isUserExceptionModeEnabled(self) -> bool:
        if self.__isInvalid: return False
        return not self.__sopt._isUserExceptionModeDisabled

    @property
    def _isFwDieModeEnabled(self) -> bool:
        if self.__isInvalid: return False
        return not self.__sopt._isFwDieModeDisabled

    @property
    def _isFwExceptionModeEnabled(self) -> bool:
        if self.__isInvalid: return False
        return not self.__sopt._isFwExceptionModeDisabled

    @property
    def _userLogLevel(self) -> _ELogLevel:
        if self.__isInvalid: return None
        return _ELogLevel.Decode(self.__sopt._userLogLevel)

    @property
    def _fwLogLevel(self) -> _ELogLevel:
        if self.__isInvalid: return None
        return _ELogLevel.Decode(self.__sopt._fwLogLevel)

    @property
    def _userConfigFile(self) -> str:
        return None if not self.__isUserConfigFileSupported else self.__sopt._userConfigFile

    @property
    def _fwwCustomConfigFile(self) -> str:
        return None if not self.__isUserConfigFileSupported else self.__sopt._fwwCustomConfigFile

    def _ToString(self):
        if self.__isInvalid:
            return None
        return _CommonDefines._STR_EMPTY

    def _CleanUpByOwnerRequest(self):
        if self.__sup is None:
            return
        self.__sup  = None
        self.__sopt = None

    @property
    def __isInvalid(self):
        return self.__sup is None

    @property
    def __isUserConfigFileSupported(self):
        return False

    @property
    def __isFwCustomConfigFileSupported(self):
        return False
