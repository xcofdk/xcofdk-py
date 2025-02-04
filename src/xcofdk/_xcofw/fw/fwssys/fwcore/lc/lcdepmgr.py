# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : lcdepmgr.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from xcofdk._xcofw.fw.fwssys.fwcore.logging                         import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logconfig               import _LoggingDefaultConfig
from xcofdk._xcofw.fw.fwssys.fwcore.logging.xcoexception            import _XcoExceptionRoot
from xcofdk._xcofw.fw.fwssys.fwcore.logging.xcoexception            import _XcoBaseException
from xcofdk._xcofw.fw.fwssys.fwcore.base.timeutil                   import _TimeUtil
from xcofdk._xcofw.fw.fwssys.fwcore.config.fwconfig                 import _FwConfig
from xcofdk._xcofw.fw.fwssys.fwcore.config.fwstartoptionsimpl       import _FwStartOptionsImpl
from xcofdk._xcofw.fw.fwssys.fwcore.config.fwstartuppolicy          import _FwStartupPolicy
from xcofdk._xcofw.fw.fwssys.fwcore.config.ssysconfig.sscsupervisor import _SSConfigSupervisor
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcdefines                    import _ELcScope
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcexecstate                  import _LcFailure
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcguard                      import _LcGuard
from xcofdk._xcofw.fw.fwssys.fwcore.ssdsupervisor                   import _SSDeputySupervisor
from xcofdk._xcofw.fw.fwssys.fwcore.swpfm.sysinfo                   import _SystemInfo
from xcofdk._xcofw.fw.fwssys.fwcore.types.apobject                  import _ProtectedAbstractSlotsObject
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes               import _TextStyle
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes               import _CommonDefines
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes               import _ETernaryOpResult

from xcofdk._xcofw.fw.fwssys.fwerrh.fwerrorcodes import _EFwErrorCode

from xcofdk._xcofwa.fwversion import _FwVersion

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine

class _LcDepManager(_ProtectedAbstractSlotsObject):

    __slots__ = [ '__lcDMH'  , '__lcScope'    , '__lcGuard'
                , '__fwCfg'  , '__ssdepSupv'  , '__sscfgSupv'  ]
    __theLcDMImpl = None

    def __init__(self, ppass_ : int, suPolicy_ : _FwStartupPolicy, lcGuard_ : _LcGuard, startOptions_ : list):
        self.__fwCfg     = None
        self.__lcDMH     = None
        self.__lcScope   = None
        self.__lcGuard   = None
        self.__sscfgSupv = None
        self.__ssdepSupv = None

        _errMsg    = None
        _iImplErr  = None
        _xcpCaught = None
        try:
            super().__init__(ppass_)

            if _LcDepManager.__theLcDMImpl is not None:
                _iImplErr = _EFwErrorCode.FE_LCSF_025
            elif not isinstance(suPolicy_, _FwStartupPolicy):
                _iImplErr = _EFwErrorCode.FE_LCSF_026
            elif not isinstance(lcGuard_, _LcGuard):
                _iImplErr = _EFwErrorCode.FE_LCSF_027

            if _iImplErr is not None:
                self.CleanUpByOwnerRequest(ppass_)

                _LcFailure.CheckSetLcSetupFailure(_iImplErr)
                if _errMsg is not None:
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00320)
                return

            _lcDMH = _TimeUtil.GetHash(type(self).__name__)

            _sopt = _LcDepManager.__CreatePrerequisites(_lcDMH, suPolicy_, startOptions_)
            if _sopt is None :
                self.CleanUpByOwnerRequest(ppass_)
                return

            if not self.__LoadConfig(_lcDMH, suPolicy_, _sopt):
                self.CleanUpByOwnerRequest(ppass_)
                return

            self.__lcDMH   = _lcDMH
            self.__lcScope = _ELcScope.eIdle
            self.__lcGuard = lcGuard_

            self.__sscfgSupv = _SSConfigSupervisor(_lcDMH, suPolicy_, self.fwConfig.fwStartupConfig)
            if self.__sscfgSupv.subsystemID is None:
                self.CleanUpByOwnerRequest(ppass_)
                _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_028)
                return

            self.__ssdepSupv = _SSDeputySupervisor(_lcDMH, self.__sscfgSupv)
            if self.__ssdepSupv.deputyID is None:
                self.CleanUpByOwnerRequest(ppass_)
                _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_029)
                return

            _ures = self.UpdateLcScope(_ELcScope.ePreIPC)

            if _ures.isOK:
                if suPolicy_.isReleaseModeEnabled != _LoggingDefaultConfig._releaseMode:
                    _ures = _ETernaryOpResult.Abort()

                    if suPolicy_.isReleaseModeEnabled:
                        _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_030)
                        if _errMsg is not None:
                            vlogif._LogOEC(True, _EFwErrorCode.VFE_00321)
                    else:
                        _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_031)
                        if _errMsg is not None:
                            vlogif._LogOEC(True, _EFwErrorCode.VFE_00322)

            if not _ures.isOK:
                self.CleanUpByOwnerRequest(ppass_)
                return

            _LcDepManager.__theLcDMImpl = self

        except BaseException as xcp:
            _xcpCaught = _XcoBaseException(xcp, tb_=vlogif._GetFormattedTraceback(), taskID_=None)
        finally:
            if _xcpCaught is not None:
                self.CleanUpByOwnerRequest(ppass_)
                _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_088)

                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcDepManager_TextID_001).format(str(_xcpCaught))
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00323)

    @property
    def lcScope(self) -> _ELcScope:
        return self.__lcScope

    @property
    def fwConfig(self) -> _FwConfig:
        return self.__fwCfg

    @property
    def subsystemConfigSupervisor(self):
        return self.__sscfgSupv

    @property
    def ignoredUnsupportedCmdLineArgs(self) -> list:
        return None if self.__fwCfg is None else _FwStartOptionsImpl._GetUnsupportedOptionsNameList()

    def UpdateLcScope(self, tgtScope_ : _ELcScope, bForceReinject_ =False, bFinalize_ =False) -> _ETernaryOpResult:
        if self.__isInvalid:
            return _ETernaryOpResult.NOK()

        if tgtScope_ == self.lcScope:
            if not (bForceReinject_ or bFinalize_):
                return _ETernaryOpResult.OK()

        _iImplErr = None

        _badUseMsg = None
        _myLcState = self.__lcGuard._GetLcState(bypassApiLock_=True)

        if not isinstance(tgtScope_, _ELcScope):
            _iImplErr = _EFwErrorCode.FE_LCSF_032
        elif _myLcState.isLcStopped:
            _iImplErr = _EFwErrorCode.FE_LCSF_033
        elif abs(tgtScope_.lcTransitionalOrder - self.lcScope.lcTransitionalOrder) > 1:
            _iImplErr = _EFwErrorCode.FE_LCSF_034
        elif _LcFailure.IsLcNotErrorFree() and not _LcFailure.IsConfigPhasePassed():
            _iImplErr = 0
        elif _myLcState.hasLcAnyFailureState:
            if _myLcState.isLcFailed:
                _iImplErr = _EFwErrorCode.FE_LCSF_035
            elif tgtScope_.lcTransitionalOrder > self.lcScope.lcTransitionalOrder:
                _iImplErr = _EFwErrorCode.FE_LCSF_036

        if _iImplErr is not None:
            if _iImplErr == 0:
                res = _ETernaryOpResult.OK()
            else:
                if not _LcFailure.IsSetupPhasePassed():
                    _LcFailure.CheckSetLcSetupFailure(_iImplErr)

                if _badUseMsg is not None:
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00324)
                res = _ETernaryOpResult.NOK()
            return res

        res      = _ETernaryOpResult.OK()
        _myXcp   = None
        _errMsg  = None
        _errCode = None
        try:
            if not self.__ssdepSupv.SwitchLcScope(tgtScope_, self.lcScope, bForceReinject_=bForceReinject_, bFinalize_=bFinalize_):
                res      = _ETernaryOpResult.NOK()
                _errCode = _EFwErrorCode.FE_LCSF_090
                _errMsg  = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcDepManager_TextID_003).format(self.lcScope.compactName, tgtScope_.compactName)
        except _XcoExceptionRoot as xcp:
            _myXcp = xcp
        except BaseException as xcp:
            _myXcp = _XcoBaseException(xcp, tb_=vlogif._GetFormattedTraceback(), taskID_=None)
        finally:
            if _myXcp is not None:
                res      = _ETernaryOpResult.NOK()
                _errCode = _EFwErrorCode.FE_LCSF_091
                _errMsg  = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcDepManager_TextID_004).format(_myXcp)

        if not res.isOK:
            if not _LcFailure.IsSetupPhasePassed():
                _LcFailure.CheckSetLcSetupFailure(_errCode, errMsg_=_errMsg)
            vlogif._LogOEC(True, _errCode)
        else:
            self.__lcScope = tgtScope_
        return res

    def _ToString(self):
        if self.__isInvalid:
            return None
        _myTxt = _FwTDbEngine.GetText(_EFwTextID.eLcDepManager_ToString_01)
        return _myTxt.format(type(self).__name__, self.lcScope.compactName, self.__lcGuard._GetLcState(bypassApiLock_=True))

    def _CleanUpByOwnerRequest(self):
        if _LcDepManager.__theLcDMImpl is not None:
            if id(_LcDepManager.__theLcDMImpl) == id(self):
                _LcDepManager.__theLcDMImpl = None

        if self.__lcDMH is not None:
            if self.__ssdepSupv is not None:
                self.__ssdepSupv.CleanUpByOwnerRequest(self.__lcDMH)
                self.__ssdepSupv = None
            if self.__sscfgSupv is not None:
                self.__sscfgSupv.CleanUpByOwnerRequest(self.__lcDMH)
                self.__sscfgSupv = None
            if self.__fwCfg is not None:
                self.__fwCfg.CleanUpByOwnerRequest(self.__lcDMH)
                self.__fwCfg = None
            self.__lcDMH   = None
            self.__lcScope = None
            self.__lcGuard = None

    @property
    def __isInvalid(self) -> bool:
        return self.__lcDMH is None

    @staticmethod
    def __GetPreamble():

        _dlLong  = _CommonDefines._DASH_LINE_LONG
        _dlShort = _CommonDefines._DASH_LINE_SHORT

        _verstr = _SystemInfo._GetPythonVer()
        _verstr = _FwTDbEngine.GetText(_EFwTextID.eFwApiBase_StartPreamble_Python_Version).format(_verstr)

        res = _FwTDbEngine.GetText(_EFwTextID.eFwApiBase_StartPreamble)
        res = res.format(_dlLong, _dlShort, _dlShort, _FwVersion._GetVersionInfo(bShort_=False), _dlShort, _verstr, _dlShort, _dlLong)
        return res

    @staticmethod
    def __CreatePrerequisites(lcDMH_ : int, suPolicy_ : _FwStartupPolicy, startOptions_ : list) -> _FwStartOptionsImpl:
        _sopt     = None
        _errCode  = None
        _bPrintSP = True

        if not suPolicy_.isValid:
            _errCode = _EFwErrorCode.FE_LCSF_037
        else:
            _sopt = _FwStartOptionsImpl(lcDMH_, suPolicy_, [])
            if not _sopt._isValid:
                _sopt.CleanUpByOwnerRequest(lcDMH_)
                _sopt    = None
                _errCode = _EFwErrorCode.FE_LCSF_038
            else:
                _TextStyle._SetHighlightingMode(_sopt._isUserLogHighlightingDisabled)

                _sopt.CleanUpByOwnerRequest(lcDMH_)
                _sopt = _FwStartOptionsImpl(lcDMH_, suPolicy_, startOptions_=startOptions_)
                if not _sopt._isValid:
                    _sopt.CleanUpByOwnerRequest(lcDMH_)
                    _sopt = None
                elif _sopt._isSuppressStartPreambleEnabled:
                    _bPrintSP = False

                _TextStyle._SetHighlightingMode(_sopt._isUserLogHighlightingDisabled)

        if _bPrintSP:
            print(_LcDepManager.__GetPreamble())
        if _errCode is not None:
            _LcFailure.CheckSetLcSetupFailure(_errCode)
            vlogif._LogOEC(True, _errCode)
        return _sopt

    def __LoadConfig(self, lcDMH_ : int, suPolicy_ : _FwStartupPolicy, fwSOpt_ : _FwStartOptionsImpl) -> bool:
        self.__fwCfg = _FwConfig(lcDMH_, suPolicy_, fwSOpt_)
        if not self.__fwCfg.isValid:
            self.__fwCfg.CleanUpByOwnerRequest(lcDMH_)
            self.__fwCfg = None

            if _LcFailure.IsLcErrorFree():
                _errMsg  = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcDepManager_TextID_002).format()
                _errCode = _EFwErrorCode._EFwErrorCode.FE_LCSF_089

                _LcFailure.CheckSetLcSetupFailure(_errCode, errMsg_=_errMsg)
                vlogif._LogOEC(True, _errCode)
        return self.__fwCfg is not None
