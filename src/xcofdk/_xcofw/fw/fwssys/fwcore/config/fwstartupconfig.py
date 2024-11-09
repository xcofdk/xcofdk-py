# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwstartupconfig.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from xcofdk._xcofw.fw.fwssys.fwcore.logging                   import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logdefines        import _ELogLevel
from xcofdk._xcofw.fw.fwssys.fwcore.config.fwstartoptionsimpl import _FwStartOptionsImpl
from xcofdk._xcofw.fw.fwssys.fwcore.config.fwstartuppolicy    import _FwStartupPolicy
from xcofdk._xcofw.fw.fwssys.fwcore.types.apobject            import _ProtectedAbstractSlotsObject
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes         import _CommonDefines


class _FwStartupConfig(_ProtectedAbstractSlotsObject):

    __slots__ = [ '__sup' , '__sopt' ]

    def __init__(self, ppass_ : int, fwStartupPolicy_ : _FwStartupPolicy, fwSOpt_ : _FwStartOptionsImpl):
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

        if self.__sup.isReleaseModeEnabled:
            if self.__sopt._isReleaseModeDisabled:
                res = self.__sup.isDevModeEnabled
            else:
                res = True
        else:
            if self.__sopt._isReleaseModeEnabled:
                res = self.__sup.isDevModeEnabled
            else:
                res = False
        return res

    @property
    def _isUserLogTimestampEnabled(self) -> bool:
        if self.__isInvalid: return False
        return not self.__sopt._isUserLogTimestampDisabled

    @property
    def _isUserLogHighlightingEnabled(self) -> bool:
        if self.__isInvalid: return False
        return not self.__sopt._isUserLogHighlightingDisabled

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
    def _isIgnoreEvnVarsEnabled(self) -> bool:
        if self.__isInvalid: return False
        return self.__sopt._isIgnoreEvnVarsEnabled

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

    def _ToString(self, *args_, **kwargs_):
        if self.__isInvalid:
            return None

        res  = "Startup config:\n"
        res += "  {:<25s} : {:<s}\n".format("ignoreEnvVars"      , str(self._isIgnoreEvnVarsEnabled))
        res += _CommonDefines._CHAR_SIGN_NEWLINE
        res += "  {:<25s} : {:<s}\n".format("fwDieMode"          , str(self._isFwDieModeEnabled))
        res += "  {:<25s} : {:<s}\n".format("fwXcpMode"          , str(self._isFwExceptionModeEnabled))
        res += "  {:<25s} : {:<s}\n".format("fwLogLevel"         , _ELogLevel.Encode(self._fwLogLevel))
        res += "  {:<25s} : {:<s}\n".format("fwCustomConfigFile" , str(self._fwwCustomConfigFile))
        res += _CommonDefines._CHAR_SIGN_NEWLINE
        res += "  {:<25s} : {:<s}\n".format("userDieMode"        , str(self._isUserDieModeEnabled))
        res += "  {:<25s} : {:<s}\n".format("userXcpMode"        , str(self._isUserExceptionModeEnabled))
        res += "  {:<25s} : {:<s}\n".format("userLogLevel"       , _ELogLevel.Encode(self._userLogLevel))
        res += "  {:<25s} : {:<s}\n".format("suppressFwWarnings" , str(self._isUserSuppressFwWarningsEnabled))
        res += "  {:<25s} : {:<s}\n".format("userLogTimestamp"   , str(self._isUserLogTimestampEnabled))
        res += "  {:<25s} : {:<s}\n".format("userConfigFile"     , str(self._userConfigFile))
        res += _CommonDefines._CHAR_SIGN_NEWLINE
        res += "  {:<25s} : {:<s}\n".format("releaseMode"        , str(self._isReleaseModeEnabled))
        res += _CommonDefines._CHAR_SIGN_NEWLINE
        return res

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
        if self.__isInvalid: return None
        res = False
        if self.__sup.isUserConfigFileSupportEnabled:
            res = not self.__sopt._isIgnoreUserConfigFileEnabled
        return res

    @property
    def __isFwCustomConfigFileSupported(self):
        if self.__isInvalid: return None
        res = False
        if self.__sup.isFwCustomConfigFileSupportEnabled:
            res = not self.__sopt._isIgnoreFwCustomConfigFileEnabled
        return res
