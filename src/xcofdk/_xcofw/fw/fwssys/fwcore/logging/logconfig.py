# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : logconfig.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


import os
from enum import Enum


from xcofdk._xcofw.fw.fwssys.fwcore.logging.logdefines import _ELogLevel
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logdefines import _LogUniqueID
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes  import _CommonDefines

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine



class _LoggingDefaultConfig:

    _dieMode            = True
    _eLogLevel          = _ELogLevel.eInfo
    _releaseMode        = True
    _exceptionMode      = True
    _vsysExitMode       = not _releaseMode
    _outputRedirection  = None

    @staticmethod
    def ToString():
        _myFmtStr = _CommonDefines._STR_EMPTY
        return _myFmtStr.format(_LoggingDefaultConfig._vsysExitMode, _LoggingDefaultConfig._releaseMode, _LoggingDefaultConfig._dieMode
                               , _LoggingDefaultConfig._exceptionMode, _LoggingDefaultConfig._eLogLevel.compactName, _LoggingDefaultConfig._outputRedirection)

    @staticmethod
    def _Restore():
        _LogUniqueID._Reset()

        _LoggingDefaultConfig._dieMode           = True
        _LoggingDefaultConfig._eLogLevel         = _ELogLevel.eInfo
        _LoggingDefaultConfig._releaseMode       = True
        _LoggingDefaultConfig._exceptionMode     = True
        _LoggingDefaultConfig._vsysExitMode      = not _LoggingDefaultConfig._releaseMode
        _LoggingDefaultConfig._outputRedirection = None

    @staticmethod
    def _SetUp(bDieMode_ =None, bExceptionMode_ =None, bRelMode_ =None, bVSysExitMode_ =None, eLogLevel_ =None):
        if bRelMode_ is not None:
            if not bRelMode_:
                if bDieMode_       is None: bDieMode_       = True
                if bExceptionMode_ is None: bExceptionMode_ = True
                if bVSysExitMode_  is None: bVSysExitMode_  = True
                if eLogLevel_      is None: eLogLevel_      = _ELogLevel.eDebug
            elif bVSysExitMode_ is None:
                bVSysExitMode_ = False

        if bDieMode_       is not None: _LoggingDefaultConfig._dieMode       = bDieMode_
        if bExceptionMode_ is not None: _LoggingDefaultConfig._exceptionMode = bExceptionMode_
        if bRelMode_       is not None: _LoggingDefaultConfig._releaseMode   = bRelMode_
        if bVSysExitMode_  is not None: _LoggingDefaultConfig._vsysExitMode  = bVSysExitMode_
        if eLogLevel_      is not None: _LoggingDefaultConfig._eLogLevel     = eLogLevel_

        logCfg = _LoggingConfig.GetInstance(bCreate_=False)
        if logCfg is not None:
            logCfg.CleanUp()
        logCfg = _LoggingConfig.GetInstance()
        return _LoggingDefaultConfig.ToString()


class _LoggingConfig:

    __slots__ = [ '__bDieMode' , '__bRelMode' , '__bXcpMode' , '__bOutpR' , '__eLL'  ]
    __singleton = None

    def __init__( self, bRelMode_ : bool =None, bDieMode_ : bool =None, bXcpMode_ : bool =None
                , eLogLevel_ : Enum =None, bOutputRedirection_ : bool =None, bInitByEnvConfig_ =False):
        if _LoggingConfig.__singleton is not None:
            self.CleanUp()
        else:
            _LoggingConfig.__singleton = self

            if bInitByEnvConfig_:
                if _LoggingEnvConfig.IsEnvVarsEvaluationEnabled():
                    envConf = _LoggingEnvConfig()
                    if bDieMode_ is None:
                        bDieMode_ = envConf.dieMode
                    if bXcpMode_ is None:
                        bXcpMode_ = envConf.exceptionMode
                    if eLogLevel_ is None:
                        eLogLevel_ = envConf.eLogLevel
                    envConf.CleanUp()

            if bDieMode_ is None:
                bDieMode_ = _LoggingDefaultConfig._dieMode
            if bRelMode_ is None:
                bRelMode_ = _LoggingDefaultConfig._releaseMode
            if bXcpMode_ is None:
                bXcpMode_ = _LoggingDefaultConfig._exceptionMode
            if eLogLevel_ is None:
                eLogLevel_ = _LoggingDefaultConfig._eLogLevel
            if bOutputRedirection_ is None:
                bOutputRedirection_ = _LoggingDefaultConfig._outputRedirection

            self.__eLL      = _ELogLevel(eLogLevel_.value)
            self.__bOutpR   = bOutputRedirection_
            self.__bDieMode = bDieMode_
            self.__bRelMode = bRelMode_
            self.__bXcpMode = bXcpMode_

    def __str__(self):
        return self.ToString()

    @staticmethod
    def GetInstance(bCreate_ =True):
        res = _LoggingConfig.__singleton
        if res is None:
            if bCreate_:
                _LoggingConfig.__singleton = _LoggingConfig()
                res = _LoggingConfig.__singleton
        return res

    @property
    def dieMode(self):
        return self.__bDieMode

    @property
    def eLogLevel(self):
        return self.__eLL

    @property
    def releaseMode(self):
        return self.__bRelMode

    @property
    def exceptionMode(self):
        return self.__bXcpMode

    @property
    def outputRedirection(self):
        return self.__bOutpR

    def ToString(self):
        _myFmtStr = _CommonDefines._STR_EMPTY
        return _myFmtStr.format(type(self).__name__, _LoggingDefaultConfig._vsysExitMode, self.releaseMode, self.dieMode
                              , self.exceptionMode, self.eLogLevel.compactName, self.outputRedirection)

    def CleanUp(self):
        if _LoggingConfig.__singleton is not None:
            self.__eLL      = None
            self.__bOutpR   = None
            self.__bDieMode = None
            self.__bRelMode = None
            self.__bXcpMode = None
            _LoggingConfig.__singleton = None

    @property
    def _isVSystemExistEnabled(self):
        return _LoggingDefaultConfig._vsysExitMode


class _LoggingUserConfig:
    _userDieMode       = True
    _eUserLogLevel     = _ELogLevel.eInfo
    _userExceptionMode = True

    @staticmethod
    def ToString():
        _myFmtStr = _CommonDefines._STR_EMPTY
        return _myFmtStr.format(_LoggingUserConfig._userDieMode, _LoggingUserConfig._userExceptionMode, _LoggingUserConfig._eUserLogLevel.compactName)

    @staticmethod
    def _Update(bUserDieMode_ =None, bUserXcpMode_ =None, eUserLogLevel_ =None):
        if bUserDieMode_  is not None: _LoggingUserConfig._userDieMode       = bUserDieMode_
        if bUserXcpMode_  is not None: _LoggingUserConfig._userExceptionMode = bUserXcpMode_
        if eUserLogLevel_ is not None: _LoggingUserConfig._eUserLogLevel     = eUserLogLevel_
        return _LoggingUserConfig.ToString()


class _LoggingEnvConfig:

    __slots__ = [ '__bDieMode' , '__bXcpMode' , '__eLL' ]

    _envVarNameDieMode   = _FwTDbEngine.GetText(_EFwTextID.eLoggingEnvConfig_EnvVarName_DieMode)
    _envVarNameXcpMode   = _FwTDbEngine.GetText(_EFwTextID.eLoggingEnvConfig_EnvVarName_XcpMode)
    _envVarNameLogLevel  = _FwTDbEngine.GetText(_EFwTextID.eLoggingEnvConfig_EnvVarName_LogLevel)
    __envVarsEvalEnabled = False

    def __init__(self):
        self.__eLL      = None
        self.__bDieMode = None
        self.__bXcpMode = None
        self.__EvaluateEnvConfig()

    def CleanUp(self):
        self.__eLL      = None
        self.__bDieMode = None
        self.__bXcpMode = None

    @staticmethod
    def IsEnvVarsEvaluationEnabled():
        return _LoggingEnvConfig.__envVarsEvalEnabled

    @staticmethod
    def _InjectEvaluationStatus(envVarsEvalEnabled_: bool):
        _LoggingEnvConfig.__envVarsEvalEnabled = envVarsEvalEnabled_

    @property
    def dieMode(self):
        return self.__bDieMode

    @property
    def eLogLevel(self):
        return self.__eLL

    @property
    def exceptionMode(self):
        return self.__bXcpMode

    def __EvaluateEnvConfig(self):
        if not _LoggingEnvConfig.__envVarsEvalEnabled:
            return


        if _LoggingEnvConfig._envVarNameDieMode in os.environ:
            envVal = os.environ.get(_LoggingEnvConfig._envVarNameDieMode)
            if envVal is None or len(envVal.strip()) == 0:
                pass
            else:
                try:
                    self.__bDieMode = _CommonDefines._StrToBool(envVal.lower(), bOneWayMatch_=True)
                except ValueError:
                    pass

        if _LoggingEnvConfig._envVarNameXcpMode in os.environ:
            envVal = os.environ.get(_LoggingEnvConfig._envVarNameXcpMode)
            if envVal is None or len(envVal.strip()) == 0:
                pass
            else:
                try:
                    self.__bXcpMode = _CommonDefines._StrToBool(envVal.lower(), bOneWayMatch_=True)
                except ValueError:
                    pass

        if _LoggingEnvConfig._envVarNameLogLevel in os.environ:
            envVal = os.environ.get(_LoggingEnvConfig._envVarNameLogLevel)
            if envVal is None or len(envVal.strip()) == 0:
                pass
            else:
                for name, member in _ELogLevel.__members__.items():
                    if envVal == member.compactName:
                        self.__eLL = member
                        break
