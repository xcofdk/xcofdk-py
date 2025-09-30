# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwstartoptionsimpl.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum   import auto
from enum   import unique
from typing import Union

from _fw.fwssys.fwcore.logging                import vlogif
from _fw.fwssys.fwcore.logging.logdefines     import _ELogLevel
from _fw.fwssys.fwcore.base.fwargparser       import _FwArgParser
from _fw.fwssys.fwcore.base.fwargparser       import _ParsedNamespace
from _fw.fwssys.fwcore.config.fwstartuppolicy import _FwStartupPolicy
from _fw.fwssys.fwcore.lc.lcxstate            import _LcFailure
from _fw.fwssys.fwcore.types.apobject         import _ProtAbsSlotsObject
from _fw.fwssys.fwcore.types.commontypes      import _FwIntEnum
from _fw.fwssys.fwcore.types.commontypes      import _CommonDefines
from _fw.fwssys.fwerrh.fwerrorcodes           import _EFwErrorCode

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

@unique
class _EFwStartOptionID(_FwIntEnum):
    eUserLogLevel               = 0
    eFwLogLevel                 = auto()
    eDisableLogTimestamp        = auto()
    eDisableLogHighlighting     = auto()
    eDisableLogCallstack        = auto()
    eSuppressStartPreamble      = auto()

class _FwStartOptionSpec:
    __slots__ = [ '__n' , '__h' , '__d' , '__bS' , '__c' ]

    def __init__(self, name_: str, default_, help_: str, bSupported_ =True):
        self.__c  = None
        self.__d  = default_
        self.__h  = help_
        self.__n  = name_
        self.__bS = bSupported_

    @property
    def isSupported(self):
        return self.__bS

    @isSupported.setter
    def isSupported(self, bSupported_ : bool):
        self.__bS = bSupported_

    @property
    def optionName(self):
        return self.__n

    @property
    def optionHelp(self):
        return self.__h

    @property
    def optionDefault(self):
        return self.__d

    @property
    def optionChoices(self):
        return self.__c

    @optionChoices.setter
    def optionChoices(self, choices_):
        self.__c = choices_

class _FwSOptionsImpl(_ProtAbsSlotsObject):
    __USAGE               = None
    __PARSER              = None
    __ALL_OPT_UNSUPPORTED = None
    __ALL_OPT_SPEC_TABLE  = None
    __ALL_OPT_NAME_TABLE  = None

    __slots__ = [ '__ao' , '__pns' ]

    def __init__(self, ppass_ : int, startupPolicy_ : _FwStartupPolicy, startOptions_ : list):
        self.__ao  = None
        self.__pns = None
        super().__init__(ppass_)

        _parser = _FwSOptionsImpl.__PARSER
        if _parser is None:
            if _FwSOptionsImpl.__GetOptionsSpecTable(startupPolicy_) is None:
                self.CleanUpByOwnerRequest(ppass_)
                return

            _parser = _FwSOptionsImpl.__CreateParser()
            if _parser is None:
                self.CleanUpByOwnerRequest(ppass_)
                return

        _lstOpts = _FwSOptionsImpl.__ValidateStartOptions(startOptions_)
        if _lstOpts is None:
            self.CleanUpByOwnerRequest(ppass_)
            return

        _pns = _FwSOptionsImpl.__ParseStartOptions(_lstOpts, startupPolicy_.isReleaseModeEnabled)
        if _pns is None:
            self.CleanUpByOwnerRequest(ppass_)
            return

        self.__ao  = _lstOpts
        self.__pns = _pns

    @staticmethod
    def _GetUsage() -> str:
        return _FwSOptionsImpl.__USAGE

    @staticmethod
    def _GetUnsupportedOptionsNameList() -> list:
        return _FwSOptionsImpl.__ALL_OPT_UNSUPPORTED

    @property
    def _isValid(self):
        return not self.__isInvalid

    @property
    def _isLogTimestampDisabled(self) -> bool:
        return False if self.__isInvalid else self.__pns.disable_log_timestamp

    @property
    def _isLogHighlightingDisabled(self) -> bool:
        return False if self.__isInvalid else self.__pns.disable_log_highlighting

    @property
    def _isLogCallstackDisabled(self) -> bool:
        return False if self.__isInvalid else self.__pns.disable_log_callstack

    @property
    def _isSuppressStartPreambleEnabled(self) -> bool:
        if self.__isInvalid:
            return False
        return True if self._IsSilentFwLogLevel() else self.__pns.suppress_start_preamble

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
    def _userLogLevel(self) -> str:
        return None if self.__isInvalid else self.__pns.log_level

    @property
    def _userConfigFile(self) -> str:
        return None

    @property
    def _fwwCustomConfigFile(self) -> str:
        return None

    @property
    def _fwLogLevel(self) -> str:
        return None if self.__isInvalid else self.__pns.fw_log_level

    @property
    def _isFwDieModeDisabled(self) -> bool:
        return False

    @property
    def _isFwExceptionModeDisabled(self) -> bool:
        return False

    @property
    def _isReleaseModeEnabled(self) -> bool:
        return True

    @property
    def _isReleaseModeDisabled(self) -> bool:
        return False

    @property
    def _isIgnoreUserConfigFileEnabled(self) -> bool:
        return False

    @property
    def _isIgnoreFwCustomConfigFileEnabled(self) -> bool:
        return False

    @property
    def _fwStartOptionsList(self) -> list:
        return self.__ao

    def _IsSilentFwLogLevel(self) -> bool:
        return False if self.__isInvalid else not self._IsFwLogLevelEnabled(_ELogLevel.eWarning)

    def _IsFwLogLevelEnabled(self, loglevl_ : _ELogLevel) -> bool:
        _fwLL = _ELogLevel.Decode(self._fwLogLevel)
        return False if _fwLL is None else _fwLL.IsEnclosing(loglevl_)

    def _ToString(self):
        if self.__isInvalid:
            return None
        return _CommonDefines._STR_EMPTY

    def _CleanUpByOwnerRequest(self):
        if self.__ao is not None:
            self.__ao.clear()
        self.__ao  = None
        self.__pns = None

    @property
    def __isInvalid(self):
        return self.__pns is None

    @staticmethod
    def __GetFwProgName():
        res = _FwTDbEngine.GetText(_EFwTextID.eFwSOptionsImpl_ParserProgName)
        if res is None:
            _errCode = _EFwErrorCode.FE_LCSF_006
            _LcFailure.CheckSetLcSetupFailure(_errCode)
            vlogif._LogOEC(True, _errCode)
        return res

    @staticmethod
    def __GetOptionSpec(optID_: _EFwStartOptionID):
        res      = None
        _specTbl = _FwSOptionsImpl.__GetOptionsSpecTable()
        if _specTbl is None:
            pass
        elif optID_.value not in _specTbl:
            pass
        else:
            res = _specTbl[optID_.value]
        return res

    @staticmethod
    def __AddOptionSpec(optID_ : _EFwStartOptionID, bSupported_ : bool, helpID_: _EFwTextID, default_ =None) -> dict:
        _nameTbl = _FwSOptionsImpl.__ALL_OPT_NAME_TABLE
        if _nameTbl is None:
            _errCode = _EFwErrorCode.FE_LCSF_007
            _LcFailure.CheckSetLcSetupFailure(_errCode)
            vlogif._LogOEC(True, _errCode)
            return None

        if (default_ is not None) and isinstance(default_, _EFwTextID):
            default_ = _FwTDbEngine.GetText(default_)
        _spec = _FwStartOptionSpec(_nameTbl[optID_.value], default_, _FwTDbEngine.GetText(helpID_), bSupported_=bSupported_)

        _specTbl = _FwSOptionsImpl.__ALL_OPT_SPEC_TABLE
        if _specTbl is None:
            _specTbl = {}
            _FwSOptionsImpl.__ALL_OPT_SPEC_TABLE = _specTbl
        _specTbl[optID_.value] = _spec
        return _specTbl

    @staticmethod
    def __ValidateStartOptions(startOptions_ : list) -> Union[list, None]:
        if startOptions_ is not None:
            if not isinstance(startOptions_, list):
                vlogif._XLogErrorEC(_EFwErrorCode.UE_00188, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwSOptionsImpl_TID_097).format(type(startOptions_).__name__))
                return None

        res = []

        if startOptions_ is not None:
            for _ee in startOptions_:
                if not (isinstance(_ee, str) and len(_ee.strip()) > 0):
                    vlogif._XLogErrorEC(_EFwErrorCode.UE_00189, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwSOptionsImpl_TID_098).format(startOptions_))
                    return None

                _ee = _ee.strip()
                if _ee.startswith(_CommonDefines._CHAR_SIGN_HASH):
                    break
                res.append(_ee)

        return res

    @staticmethod
    def __CreateParser() -> _FwArgParser:
        res = _FwSOptionsImpl.__PARSER
        if res is not None:
            return res

        _progName = _FwSOptionsImpl.__GetFwProgName()
        if _progName is None:
            return res

        _allSpec = _FwSOptionsImpl.__GetOptionsSpecTable()

        _lstAD = []
        for _spec in _allSpec.values():
            _specDefault = _spec.optionDefault

            if (_specDefault is None) or (not isinstance(_specDefault, bool)):
                action = _FwTDbEngine.GetText(_EFwTextID.eMisc_PyParserArgAction_Store)
            else:
                action = _FwTDbEngine.GetText(_EFwTextID.eMisc_PyParserArgAction_StoreFalse) if _specDefault else _FwTDbEngine.GetText(_EFwTextID.eMisc_PyParserArgAction_StoreTrue)

            _argDef = { 'name': _spec.optionName, 'action': action, 'default': _specDefault, 'help': _spec.optionHelp }
            if _spec.optionChoices is not None:
                _argDef['choices'] = _spec.optionChoices
            _lstAD.append( _argDef )

        res = _FwArgParser(_progName, argumentDefault_=None, bAddHelp_=False, bExitOnError_=False)
        if not res.isErrorFree:
            res = None
            _errCode = _EFwErrorCode.FE_LCSF_008
            _LcFailure.CheckSetLcSetupFailure(_errCode)
            vlogif._LogOEC(True, _errCode)
        else:
            for _ee in _lstAD:
                _name = _ee.pop('name')
                res.AddArgument(_name,  **_ee )

            _tmp   = _FwSOptionsImpl.__ALL_OPT_UNSUPPORTED
            _usage = res.GetUsage()
            if _tmp is not None:
                _tmp   = _CommonDefines._CHAR_SIGN_SPACE.join(_tmp)
                _usage = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwSOptionsImpl_TID_094).format(_usage, _tmp)
            _FwSOptionsImpl.__USAGE  = _usage
            _FwSOptionsImpl.__PARSER = res

        for _ee in _lstAD:
            _ee.clear()
        _lstAD.clear()

        return res

    @staticmethod
    def __ParseStartOptions(startOptions_ : list, bRelMode_ =True) -> _ParsedNamespace:
        _parser = _FwSOptionsImpl.__PARSER
        if (_parser is None) or not _parser.isErrorFree:
            return None

        res = None
        try:
            res = _parser.Parse(startOptions_)
        except Exception as _xcp:
            _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwSOptionsImpl_TID_092).format(_xcp)
            vlogif._XLogErrorEC(_EFwErrorCode.UE_00190, _errMsg)
        finally:
            _SOPT_STR = _CommonDefines._CHAR_SIGN_DASH if len(startOptions_) < 1 else _CommonDefines._CHAR_SIGN_SPACE.join(startOptions_)

            if (res is None) or not _parser.isErrorFree:
                res = None
                if _parser.isErrorFree:
                    _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwSOptionsImpl_TID_093).format(_SOPT_STR, _FwSOptionsImpl._GetUsage())
                else:
                    _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwSOptionsImpl_TID_096).format(_SOPT_STR, _parser.errorMessage, _FwSOptionsImpl._GetUsage())
                    _parser.ClearError()
                vlogif._XLogErrorEC(_EFwErrorCode.UE_00191, _errMsg)
        return res

    @staticmethod
    def __GetOptionsSpecTable(startupPolicy_ : _FwStartupPolicy =None) -> dict:
        if _FwSOptionsImpl.__ALL_OPT_SPEC_TABLE is not None:
            return _FwSOptionsImpl.__ALL_OPT_SPEC_TABLE

        if not (isinstance(startupPolicy_, _FwStartupPolicy) and startupPolicy_.isValid):
            _errCode = _EFwErrorCode.FE_LCSF_009
            _LcFailure.CheckSetLcSetupFailure(_errCode)
            vlogif._LogOEC(True, _errCode)
            return None

        _GT  = _FwTDbEngine.GetText
        _EID = _EFwStartOptionID

        _allON = {
              _EID.eUserLogLevel.value               : _GT(_EFwTextID.eFwSOptionsImpl_ArgSpec_Name_UserLogLevel)
            , _EID.eFwLogLevel.value                 : _GT(_EFwTextID.eFwSOptionsImpl_ArgSpec_Name_FwLogLevel)
            , _EID.eDisableLogTimestamp.value        : _GT(_EFwTextID.eFwSOptionsImpl_ArgSpec_Name_DisableLogTimestamp)
            , _EID.eDisableLogHighlighting.value     : _GT(_EFwTextID.eFwSOptionsImpl_ArgSpec_Name_DisableLogHighlighting)
            , _EID.eDisableLogCallstack              : _GT(_EFwTextID.eFwSOptionsImpl_ArgSpec_Name_DisableLogCallstack)
            , _EID.eSuppressStartPreamble            : _GT(_EFwTextID.eFwSOptionsImpl_ArgSpec_Name_SuppressStartPreamble)
        }
        _FwSOptionsImpl.__ALL_OPT_NAME_TABLE = _allON

        _AOS  = _FwSOptionsImpl.__AddOptionSpec
        _fwLL = _EFwTextID.eMisc_LogLevel_Error

        res  = _AOS( _EID.eUserLogLevel            , True  , _EFwTextID.eFwSOptionsImpl_ArgSpec_Help_UserLogLevel            , _EFwTextID.eMisc_LogLevel_Info )
        res  = _AOS( _EID.eFwLogLevel              , True  , _EFwTextID.eFwSOptionsImpl_ArgSpec_Help_FwLogLevel              , _fwLL )
        res  = _AOS( _EID.eDisableLogTimestamp     , True  , _EFwTextID.eFwSOptionsImpl_ArgSpec_Help_DisableLogTimestamp     , False )
        res  = _AOS( _EID.eDisableLogHighlighting  , True  , _EFwTextID.eFwSOptionsImpl_ArgSpec_Help_DisableLogHighlighting  , False )
        res  = _AOS( _EID.eDisableLogCallstack     , True  , _EFwTextID.eFwSOptionsImpl_ArgSpec_Help_DisableLogCallstack     , False )
        res  = _AOS( _EID.eSuppressStartPreamble   , True  , _EFwTextID.eFwSOptionsImpl_ArgSpec_Help_SuppressStartPreamble   , False )

        _FwSOptionsImpl.__GetOptionSpec(_EID.eUserLogLevel).optionChoices = _GT(_EFwTextID.eFwSOptionsImpl_ArgSpec_Choices_UserLogLevel).split()
        _FwSOptionsImpl.__GetOptionSpec(_EID.eFwLogLevel).optionChoices   = _GT(_EFwTextID.eFwSOptionsImpl_ArgSpec_Choices_FwLogLevel).split()

        _allUns = [_vv.optionName for _vv in res.values() if not _vv.isSupported]
        if len(_allUns) < 1:
            _allUns = None
        _FwSOptionsImpl.__ALL_OPT_UNSUPPORTED = _allUns
        return res

