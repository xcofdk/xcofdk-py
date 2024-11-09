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
from xcofdk._xcofw.fw.fwssys.fwcore.types.apobject                  import _ProtectedAbstractSlotsObject
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes               import _ETernaryOpResult

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

        _iImplErr = None
        _errMsg   = None
        _xcpCaught = None
        try:
            super().__init__(ppass_)

            if _LcDepManager.__theLcDMImpl is not None:
                _iImplErr = 501

            elif not isinstance(suPolicy_, _FwStartupPolicy):
                _iImplErr = 502

            elif not isinstance(lcGuard_, _LcGuard):
                _iImplErr = 503

            if _iImplErr is not None:
                self.CleanUpByOwnerRequest(ppass_)

                _implErrMsg = _FwTDbEngine.GetText(_EFwTextID.eMisc_ImplError_Param).format(_iImplErr)
                _LcFailure.CheckSetLcSetupFailure(errMsg_=_implErrMsg)
                if _errMsg is not None:
                    vlogif._LogOEC(True, -1592)
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
                _implErrMsg = _FwTDbEngine.GetText(_EFwTextID.eMisc_ImplError_Param).format(504)
                _LcFailure.CheckSetLcSetupFailure(errMsg_=_implErrMsg)
                return

            self.__ssdepSupv = _SSDeputySupervisor(_lcDMH, self.__sscfgSupv)
            if self.__ssdepSupv.deputyID is None:
                self.CleanUpByOwnerRequest(ppass_)
                _implErrMsg = _FwTDbEngine.GetText(_EFwTextID.eMisc_ImplError_Param).format(505)
                _LcFailure.CheckSetLcSetupFailure(errMsg_=_implErrMsg)
                return

            _ures = self.UpdateLcScope(_ELcScope.ePreIPC)

            if _ures.isOK:
                if suPolicy_.isReleaseModeEnabled != _LoggingDefaultConfig._releaseMode:
                    _ures = _ETernaryOpResult.Abort()

                    if suPolicy_.isReleaseModeEnabled:
                        _implErrMsg = _FwTDbEngine.GetText(_EFwTextID.eMisc_ImplError_Param).format(506)
                        _LcFailure.CheckSetLcSetupFailure(errMsg_=_implErrMsg)

                        if _errMsg is not None:
                            vlogif._LogOEC(True, -1593)
                    else:
                        _implErrMsg = _FwTDbEngine.GetText(_EFwTextID.eMisc_ImplError_Param).format(507)
                        _LcFailure.CheckSetLcSetupFailure(errMsg_=_implErrMsg)

                        if _errMsg is not None:
                            vlogif._LogOEC(True, -1594)

            if not _ures.isOK:
                self.CleanUpByOwnerRequest(ppass_)
                return

            _LcDepManager.__theLcDMImpl = self

        except BaseException as xcp:
            _xcpCaught = _XcoBaseException(xcp, tb_=vlogif._GetFormattedTraceback(), taskID_=None)
        finally:
            if _xcpCaught is not None:
                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcDepManager_TextID_001).format(str(_xcpCaught))
                self.CleanUpByOwnerRequest(ppass_)

                _LcFailure.CheckSetLcSetupFailure(errMsg_=_errMsg)
                vlogif._LogOEC(True, -1595)

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
            _iImplErr = 521

        elif _myLcState.isLcStopped:
            _iImplErr = 522

        elif abs(tgtScope_.lcTransitionalOrder - self.lcScope.lcTransitionalOrder) > 1:
            _iImplErr = 523

        elif _LcFailure.IsLcNotErrorFree() and not _LcFailure.IsConfigPhasePassed():
            _iImplErr = -1

        elif _myLcState.hasLcAnyFailureState:
            if _myLcState.isLcFailed:
                _iImplErr = 524

            elif tgtScope_.lcTransitionalOrder > self.lcScope.lcTransitionalOrder:
                _iImplErr = 525

        if _iImplErr is not None:
            if _iImplErr < 0:
                res = _ETernaryOpResult.OK()
            else:
                if not _LcFailure.IsSetupPhasePassed():
                    _implErrMsg = _FwTDbEngine.GetText(_EFwTextID.eMisc_ImplError_Param).format(_iImplErr)
                    _LcFailure.CheckSetLcSetupFailure(errMsg_=_implErrMsg)

                if _badUseMsg is not None:
                    vlogif._LogOEC(True, -1596)
                res = _ETernaryOpResult.NOK()
            return res

        res     = _ETernaryOpResult.OK()
        _myXcp  = None
        _errMsg = None
        try:
            if not self.__ssdepSupv.SwitchLcScope(tgtScope_, self.lcScope, bForceReinject_=bForceReinject_, bFinalize_=bFinalize_):
                res     = _ETernaryOpResult.NOK()
                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcDepManager_TextID_003).format(self.lcScope.compactName, tgtScope_.compactName)
        except _XcoExceptionRoot as xcp:
            _myXcp = xcp
        except BaseException as xcp:
            _myXcp = _XcoBaseException(xcp, tb_=vlogif._GetFormattedTraceback(), taskID_=None)
        finally:
            if _myXcp is not None:
                res     = _ETernaryOpResult.NOK()
                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcDepManager_TextID_004).format(_myXcp)

        if not res.isOK:
            if not _LcFailure.IsSetupPhasePassed():
                _LcFailure.CheckSetLcSetupFailure(errMsg_=_errMsg)
            vlogif._LogOEC(True, -1597)
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
    def __CreatePrerequisites(lcDMH_ : int, suPolicy_ : _FwStartupPolicy, startOptions_ : list) -> _FwStartOptionsImpl:
        _sopt = None

        if not suPolicy_.isValid:
            _implErrMsg = _FwTDbEngine.GetText(_EFwTextID.eMisc_ImplError_Param).format(511)
            _LcFailure.CheckSetLcSetupFailure(errMsg_=_implErrMsg)
            vlogif._LogOEC(True, -1598)
        else:
            _sopt = _FwStartOptionsImpl(lcDMH_, suPolicy_, [])
            if not _sopt._isValid:
                _sopt.CleanUpByOwnerRequest(lcDMH_)
                _sopt = None

                _implErrMsg = _FwTDbEngine.GetText(_EFwTextID.eMisc_ImplError_Param).format(512)
                _LcFailure.CheckSetLcSetupFailure(errMsg_=_implErrMsg)
                vlogif._LogOEC(True, -1599)
            else:
                _sopt.CleanUpByOwnerRequest(lcDMH_)
                _sopt = _FwStartOptionsImpl(lcDMH_, suPolicy_, startOptions_=startOptions_)
                if not _sopt._isValid:
                    _sopt.CleanUpByOwnerRequest(lcDMH_)
                    _sopt = None
        return _sopt

    def __LoadConfig(self, lcDMH_ : int, suPolicy_ : _FwStartupPolicy, fwSOpt_ : _FwStartOptionsImpl) -> bool:
        self.__fwCfg = _FwConfig(lcDMH_, suPolicy_, fwSOpt_)
        if not self.__fwCfg.isValid:
            self.__fwCfg.CleanUpByOwnerRequest(lcDMH_)
            self.__fwCfg = None

            if _LcFailure.IsLcErrorFree():
                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcDepManager_TextID_002)

                _LcFailure.CheckSetLcSetupFailure(_errMsg)
                vlogif._LogOEC(True, -1600)
        return self.__fwCfg is not None
