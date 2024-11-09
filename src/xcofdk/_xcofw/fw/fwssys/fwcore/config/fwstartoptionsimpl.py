# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwstartoptionsimpl.py
#
# Copyright(c) 2024 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from enum import auto
from enum import unique

from xcofdk._xcofw.fw.fwssys.fwcore.logging                import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.base.fwargparser       import _FwArgParser
from xcofdk._xcofw.fw.fwssys.fwcore.base.fwargparser       import _ParsedNamespace
from xcofdk._xcofw.fw.fwssys.fwcore.config.fwstartuppolicy import _FwStartupPolicy
from xcofdk._xcofw.fw.fwssys.fwcore.types.apobject         import _ProtectedAbstractSlotsObject
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes      import _FwIntEnum
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes      import _CommonDefines

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine


@unique
class _EFwStartOptionID(_FwIntEnum):
    eUserLogLevel               = 0
    eUserDisableLogTimestamp    = auto()
    eUserDisableLogHighlighting = auto()


class _FwStartOptionSpec:
    __slots__ = [ '__name' , '__help' , '__default' , '__bSpd' , '__choices' ]

    def __init__(self, name_: str, default_, help_: str, bSupported_ =True):
        self.__bSpd    = bSupported_
        self.__name    = name_
        self.__help    = help_
        self.__default = default_
        self.__choices = None


    @property
    def isSupported(self):
        return self.__bSpd

    @isSupported.setter
    def isSupported(self, bSupported_ : bool):
        self.__bSpd = bSupported_

    @property
    def optionName(self):
        return self.__name

    @property
    def optionHelp(self):
        return self.__help

    @property
    def optionDefault(self):
        return self.__default

    @property
    def optionChoices(self):
        return self.__choices

    @optionChoices.setter
    def optionChoices(self, choices_):
        self.__choices = choices_


class _FwStartOptionsImpl(_ProtectedAbstractSlotsObject):

    __ME = True

    __USAGE               = None
    __PARSER              = None
    __ALL_OPT_UNSUPPORTED = None
    __ALL_OPT_SPEC_TABLE  = None
    __ALL_OPT_NAME_TABLE  = None

    __slots__ = [ '__lstOpts' , '__pns' ]

    def __init__(self, ppass_ : int, startupPolicy_ : _FwStartupPolicy, startOptions_ : list):
        self.__pns     = None
        self.__lstOpts = None
        super().__init__(ppass_)

        _parser = _FwStartOptionsImpl.__PARSER
        if _parser is None:
            if _FwStartOptionsImpl.__GetOptionsSpecTable(startupPolicy_) is None:
                self.CleanUpByOwnerRequest(ppass_)
                return

            _parser = _FwStartOptionsImpl.__CreateParser()
            if _parser is None:
                self.CleanUpByOwnerRequest(ppass_)
                return

        _lstOpts = _FwStartOptionsImpl.__ValidateStartOptions(startOptions_)
        if _lstOpts is None:
            self.CleanUpByOwnerRequest(ppass_)
            return

        _pns = _FwStartOptionsImpl.__ParseStartOptions(_lstOpts, startupPolicy_.isReleaseModeEnabled)
        if _pns is None:
            self.CleanUpByOwnerRequest(ppass_)
            return

        self.__pns     = _pns
        self.__lstOpts = _lstOpts

    @staticmethod
    def _Reset():
        if _FwStartOptionsImpl.__ALL_OPT_UNSUPPORTED is not None:
            _FwStartOptionsImpl.__ALL_OPT_UNSUPPORTED.clear()
        if _FwStartOptionsImpl.__ALL_OPT_SPEC_TABLE is not None:
            _FwStartOptionsImpl.__ALL_OPT_SPEC_TABLE.clear()
        if _FwStartOptionsImpl.__ALL_OPT_NAME_TABLE is not None:
            _FwStartOptionsImpl.__ALL_OPT_NAME_TABLE.clear()

        _FwStartOptionsImpl.__USAGE = None
        _FwStartOptionsImpl.__PARSER = None
        _FwStartOptionsImpl.__ALL_OPT_UNSUPPORTED = None
        _FwStartOptionsImpl.__ALL_OPT_SPEC_TABLE = None
        _FwStartOptionsImpl.__ALL_OPT_NAME_TABLE = None

    @staticmethod
    def _GetUsage() -> str:
        return _FwStartOptionsImpl.__USAGE

    @staticmethod
    def _GetUnsupportedOptionsNameList() -> list:
        return _FwStartOptionsImpl.__ALL_OPT_UNSUPPORTED

    @property
    def _isValid(self):
        return self.__pns is not None


    @property
    def _userLogLevel(self) -> str:
        return None if not self._isValid else self.__pns.log_level

    @property
    def _isUserLogTimestampDisabled(self) -> bool:
        return False if not self._isValid else self.__pns.disable_log_timestamp

    @property
    def _isUserLogHighlightingDisabled(self) -> bool:
        return False if not self._isValid else self.__pns.disable_log_highlighting

    @property
    def _isUserDieModeDisabled(self) -> bool:
        return False

    @property
    def _isUserSuppressFwWarningsEnabled(self) -> bool:
        return False

    @property
    def _isUserExceptionModeDisabled(self) -> bool:
        return False

    @property
    def _userConfigFile(self) -> str:
        return None

    @property
    def _fwwCustomConfigFile(self) -> str:
        return None

    @property
    def _fwLogLevel(self) -> str:
        return _FwTDbEngine.GetText(_EFwTextID.eMisc_LogLevel_Info)

    @property
    def _isFwDieModeDisabled(self) -> bool:
        return False

    @property
    def _isFwExceptionModeDisabled(self) -> bool:
        return False

    @property
    def _isReleaseModeEnabled(self) -> bool:
        return False

    @property
    def _isReleaseModeDisabled(self) -> bool:
        return False

    @property
    def _isIgnoreEvnVarsEnabled(self) -> bool:
        return False

    @property
    def _isIgnoreUserConfigFileEnabled(self) -> bool:
        return False

    @property
    def _isIgnoreFwCustomConfigFileEnabled(self) -> bool:
        return False

    @property
    def _fwStartOptionsList(self) -> list:
        return self.__lstOpts

    def _ToString(self):
        if not self._isValid:
            return None

        res  = 'FW start options:\n'
        res += '  {:<25s} : {:<s}\n'.format('ignoreEnvVars'        , str(self._isIgnoreEvnVarsEnabled))
        res += _CommonDefines._CHAR_SIGN_NEWLINE
        res += '  {:<25s} : {:<s}\n'.format('ignoreUserConfig'     , str(self._isIgnoreUserConfigFileEnabled))
        res += '  {:<25s} : {:<s}\n'.format('userConfigFile'       , str(self._userConfigFile))
        res += _CommonDefines._CHAR_SIGN_NEWLINE
        res += '  {:<25s} : {:<s}\n'.format('ignoreFwCustomConfig' , str(self._isIgnoreFwCustomConfigFileEnabled))
        res += '  {:<25s} : {:<s}\n'.format('fwCustomConfigFile'   , str(self._fwwCustomConfigFile))
        res += _CommonDefines._CHAR_SIGN_NEWLINE
        res += '  {:<25s} : {:<s}\n'.format('fwDieMode'            , str(not self._isFwDieModeDisabled))
        res += '  {:<25s} : {:<s}\n'.format('fwXcpMode'            , str(not self._isFwExceptionModeDisabled))
        res += '  {:<25s} : {:<s}\n'.format('fwLogLevel'           , self._fwLogLevel)
        res += _CommonDefines._CHAR_SIGN_NEWLINE
        res += '  {:<25s} : {:<s}\n'.format('userDieMode'          , str(not self._isUserDieModeDisabled))
        res += '  {:<25s} : {:<s}\n'.format('userXcpMode'          , str(not self._isUserExceptionModeDisabled))
        res += '  {:<25s} : {:<s}\n'.format('userLogLevel'         , str(self._userLogLevel))
        res += '  {:<25s} : {:<s}\n'.format('suppressFwWarnings'   , str(self._isUserSuppressFwWarningsEnabled))
        res += '  {:<25s} : {:<s}\n'.format('userLogTimestamp'     , str(not self._isUserLogTimestampDisabled))
        res += '  {:<25s} : {:<s}\n'.format('userLogHighlighting'  , str(not self._isUserLogHighlightingDisabled))
        res += _CommonDefines._CHAR_SIGN_NEWLINE
        res += '  {:<25s} : {:<s}\n'.format('enableReleaseMode'    , str(self._isReleaseModeEnabled))
        res += '  {:<25s} : {:<s}\n'.format('disableReleaseMode'   , str(self._isReleaseModeDisabled))
        res += _CommonDefines._CHAR_SIGN_NEWLINE
        return res

    def _CleanUpByOwnerRequest(self):
        if self.__lstOpts is not None:
            self.__lstOpts.clear()

        self.__pns     = None
        self.__lstOpts = None


    @staticmethod
    def __IsME():
        return _FwStartOptionsImpl.__ME

    @staticmethod
    def __GetFwProgName():
        res = _FwTDbEngine.GetText(_EFwTextID.eFwStartOptionsImpl_ParserProgName)
        if res is None:
            _errMsg = _FwTDbEngine.GetText(_EFwTextID.eMisc_ImplError_Param).format(601)
            vlogif._LogOEC(True, -1621)
        return res

    @staticmethod
    def __GetOptionSpec(optID_: _EFwStartOptionID):
        res      = None
        _specTbl = _FwStartOptionsImpl.__GetOptionsSpecTable()
        if _specTbl is None:
            pass
        elif optID_.value not in _specTbl:
            pass
        else:
            res = _specTbl[optID_.value]
        return res

    @staticmethod
    def __AddOptionSpec(optID_ : _EFwStartOptionID, bSupported_ : bool, helpID_: _EFwTextID, default_ =None) -> dict:
        _nameTbl = _FwStartOptionsImpl.__ALL_OPT_NAME_TABLE
        if _nameTbl is None:
            _errMsg = _FwTDbEngine.GetText(_EFwTextID.eMisc_ImplError_Param).format(602)
            vlogif._LogOEC(True, -1622)
            return None

        if (default_ is not None) and isinstance(default_, _EFwTextID):
            default_ = _FwTDbEngine.GetText(default_)
        _spec = _FwStartOptionSpec(_nameTbl[optID_.value], default_, _FwTDbEngine.GetText(helpID_), bSupported_=bSupported_)

        _specTbl = _FwStartOptionsImpl.__ALL_OPT_SPEC_TABLE
        if _specTbl is None:
            _specTbl = {}
            _FwStartOptionsImpl.__ALL_OPT_SPEC_TABLE = _specTbl
        _specTbl[optID_.value] = _spec
        return _specTbl

    @staticmethod
    def __ValidateStartOptions(startOptions_ : list) -> list:
        if startOptions_ is not None:
            if not isinstance(startOptions_, list):
                vlogif._XLogError(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwStartOptionsImpl_TextID_097).format(type(startOptions_).__name__))
                return None

        res = []

        if startOptions_ is not None:
            for _ee in startOptions_:
                if not (isinstance(_ee, str) and len(_ee.strip()) > 0):
                    vlogif._XLogError(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwStartOptionsImpl_TextID_098).format(startOptions_))
                    return None

                _ee = _ee.strip()
                if _ee.startswith(_CommonDefines._CHAR_SIGN_HASH):
                    break
                res.append(_ee)

        return res

    @staticmethod
    def __CreateParser() -> _FwArgParser:
        res = _FwStartOptionsImpl.__PARSER
        if res is not None:
            return res

        _progName = _FwStartOptionsImpl.__GetFwProgName()
        if _progName is None:
            return res

        _allSpec = _FwStartOptionsImpl.__GetOptionsSpecTable()

        _lstAD = []
        for _spec in _allSpec.values():
            _specDefault = _spec.optionDefault

            if (_specDefault is None) or (not isinstance(_specDefault, bool)):
                action = _FwTDbEngine.GetText(_EFwTextID.eMisc_PyParserArgAction_Store)
            else:
                action = _FwTDbEngine.GetText(_EFwTextID.eMisc_PyParserArgAction_StoreFalse) if _specDefault else _FwTDbEngine.GetText(_EFwTextID.eMisc_PyParserArgAction_StoreTrue)

            _argDef = {'name': _spec.optionName, 'action': action, 'default': _specDefault, 'help': _spec.optionHelp}
            if _spec.optionChoices is not None:
                _argDef['choices'] = _spec.optionChoices
            if _spec.optionName == _FwTDbEngine.GetText(_EFwTextID.eFwStartOptionsImpl_ArgSpec_Name_FwCrashCookie):
                _argDef['type'] = int

            _lstAD.append( _argDef )

        res = _FwArgParser(_progName, argumentDefault_=None, bAddHelp_=False, bExitOnError_=False)
        if not res.isErrorFree:
            res = None
            _errMsg = _FwTDbEngine.GetText(_EFwTextID.eMisc_ImplError_Param).format(603)
            vlogif._LogOEC(True, -1623)
        else:
            for _ee in _lstAD:
                _name = _ee.pop('name')
                res.AddArgument(_name,  **_ee )

            _tmp   = _FwStartOptionsImpl.__ALL_OPT_UNSUPPORTED
            _usage = res.GetUsage()
            if _tmp is not None:
                _tmp   = _CommonDefines._CHAR_SIGN_SPACE.join(_tmp)
                _usage = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwStartOptionsImpl_TextID_094).format(_usage, _tmp)
            _FwStartOptionsImpl.__USAGE  = _usage
            _FwStartOptionsImpl.__PARSER = res

        for _ee in _lstAD:
            _ee.clear()
        _lstAD.clear()

        return res

    @staticmethod
    def __ParseStartOptions(startOptions_ : list, bRelMode_ =True) -> _ParsedNamespace:
        _parser = _FwStartOptionsImpl.__PARSER
        if (_parser is None) or not _parser.isErrorFree:
            return None

        res = None
        try:
            res = _parser.Parse(startOptions_)
        except Exception as xcp:
            _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwStartOptionsImpl_TextID_092).format(xcp)
            vlogif._XLogError(_errMsg)
        finally:
            _SOPT_STR = _CommonDefines._CHAR_SIGN_DASH if len(startOptions_) < 1 else _CommonDefines._CHAR_SIGN_SPACE.join(startOptions_)

            if (res is None) or not _parser.isErrorFree:
                res = None
                if _parser.isErrorFree:
                    _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwStartOptionsImpl_TextID_093).format(_SOPT_STR, _FwStartOptionsImpl._GetUsage())
                else:
                    _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwStartOptionsImpl_TextID_096).format(_SOPT_STR, _parser.errorMessage, _FwStartOptionsImpl._GetUsage())
                    _parser.ClearError()
                vlogif._XLogError(_errMsg)
            elif (not _FwStartOptionsImpl.__IsME()) and res.enable_release_mode and res.disable_release_mode:
                res = None
                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwStartOptionsImpl_TextID_091).format(_SOPT_STR, _FwStartOptionsImpl._GetUsage())
                vlogif._LogOEC(False, -3034)
            else:
                if not bRelMode_:
                    _FwArgParser.PrintNamespace(res)

        return res

    @staticmethod
    def __GetOptionsSpecTable(startupPolicy_ : _FwStartupPolicy =None) -> dict:
        if _FwStartOptionsImpl.__ALL_OPT_SPEC_TABLE is not None:
            return _FwStartOptionsImpl.__ALL_OPT_SPEC_TABLE

        if not (isinstance(startupPolicy_, _FwStartupPolicy) and startupPolicy_.isValid):
            _errMsg = _FwTDbEngine.GetText(_EFwTextID.eMisc_ImplError_Param).format(605)
            vlogif._LogOEC(True, -1624)
            return None

        _GT  = _FwTDbEngine.GetText
        _EID = _EFwStartOptionID

        _allON = {
              _EID.eUserLogLevel.value               : _GT(_EFwTextID.eFwStartOptionsImpl_ArgSpec_Name_UserLogLevel)
            , _EID.eUserDisableLogTimestamp.value    : _GT(_EFwTextID.eFwStartOptionsImpl_ArgSpec_Name_UserDisableLogTimestamp)
            , _EID.eUserDisableLogHighlighting.value : _GT(_EFwTextID.eFwStartOptionsImpl_ArgSpec_Name_UserDisableLogHighlighting)
        }
        _FwStartOptionsImpl.__ALL_OPT_NAME_TABLE = _allON

        _AOS = _FwStartOptionsImpl.__AddOptionSpec

        res  = _AOS( _EID.eUserLogLevel                , True  , _EFwTextID.eFwStartOptionsImpl_ArgSpec_Help_UserLogLevel                ,  _EFwTextID.eMisc_LogLevel_Info )
        res  = _AOS( _EID.eUserDisableLogTimestamp     , True  , _EFwTextID.eFwStartOptionsImpl_ArgSpec_Help_UserDisableLogTimestamp     ,  False )
        res  = _AOS( _EID.eUserDisableLogHighlighting  , True  , _EFwTextID.eFwStartOptionsImpl_ArgSpec_Help_UserDisableLogHighlighting  ,  False )

        _FwStartOptionsImpl.__GetOptionSpec(_EID.eUserLogLevel).optionChoices = _GT(_EFwTextID.eFwStartOptionsImpl_ArgSpec_Choices_UserLogLevel).split()

        _allUnsupported = [_vv.optionName for _vv in res.values() if not _vv.isSupported]
        if len(_allUnsupported) < 1:
            _allUnsupported = None
        _FwStartOptionsImpl.__ALL_OPT_UNSUPPORTED = _allUnsupported
        return res

