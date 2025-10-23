# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : lcdepmgr.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from _fw.fwssys.assys                               import fwsubsysshare as _ssshare
from _fw.fwssys.fwcore.logging                      import vlogif
from _fw.fwssys.fwcore.logging.vlogif               import _PutLR
from _fw.fwssys.fwcore.logging.logdefines           import _LogConfig
from _fw.fwssys.fwcore.base.timeutil                import _TimeUtil
from _fw.fwssys.fwcore.config.fwconfig              import _FwConfig
from _fw.fwssys.fwcore.config.fwsoptionsimpl        import _FwSOptionsImpl
from _fw.fwssys.fwcore.config.fwstartuppolicy       import _FwStartupPolicy
from _fw.fwssys.fwcore.config.ssyscfg.sscsupervisor import _SSConfigSupervisor
from _fw.fwssys.fwcore.lc.lcdefines                 import _ELcScope
from _fw.fwssys.fwcore.lc.lcxstate                  import _LcFailure
from _fw.fwssys.fwcore.lc.ifs.iflcguard             import _ILcGuard
from _fw.fwssys.fwcore.ssdsupervisor                import _SSDeputySupervisor
from _fw.fwssys.fwcore.swpfm.sysinfo                import _SystemInfo
from _fw.fwssys.fwcore.types.apobject               import _ProtAbsSlotsObject
from _fw.fwssys.fwcore.types.commontypes            import _CommonDefines
from _fw.fwssys.fwcore.types.commontypes            import _EExecutionCmdID
from _fw.fwssys.fwerrh.fwerrorcodes                 import _EFwErrorCode
from _fw.fwssys.fwerrh.logs.xcoexception            import _XcoXcpRootBase
from _fw.fwssys.fwerrh.logs.xcoexception            import _XcoBaseException
from _fwa.fwversion                                 import _FwVersion

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _LcDepManager(_ProtAbsSlotsObject):
    __slots__ = [ '__h' , '__s' , '__g' , '__c' , '__sd' , '__sc'  ]

    __sgltn = None

    def __init__(self, ppass_ : int, suPolicy_ : _FwStartupPolicy, lcGuard_ : _ILcGuard, startOptions_ : list):
        self.__c  = None
        self.__g  = None
        self.__s  = None
        self.__h  = None
        self.__sc = None
        self.__sd = None

        _errMsg    = None
        _iImplErr  = None
        _xcpCaught = None
        try:
            super().__init__(ppass_)

            if _LcDepManager.__sgltn is not None:
                _iImplErr = _EFwErrorCode.FE_LCSF_025
            elif not isinstance(suPolicy_, _FwStartupPolicy):
                _iImplErr = _EFwErrorCode.FE_LCSF_026
            elif not isinstance(lcGuard_, _ILcGuard):
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

            self.__g = lcGuard_
            self.__h = _lcDMH
            self.__s = _ELcScope.eIdle

            self.__sc = _SSConfigSupervisor(_lcDMH, suPolicy_, self.fwConfig.fwStartupConfig)
            if self.__sc.subsystemID is None:
                self.CleanUpByOwnerRequest(ppass_)
                _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_028)
                return

            self.__sd = _SSDeputySupervisor(_lcDMH, self.__sc)
            if self.__sd.deputyID is None:
                self.CleanUpByOwnerRequest(ppass_)
                _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_029)
                return

            _ures = self.UpdateLcScope(_ELcScope.ePreIPC)

            if _ures.isOK:
                _logCfg = _LogConfig()

                if suPolicy_.isReleaseModeEnabled != _logCfg.isReleaseModeEnabled:
                    _ures = _EExecutionCmdID.Abort()

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

            _LcDepManager.__sgltn = self
        except BaseException as _xcp:
            _xcpCaught = _XcoBaseException(_xcp, tb_=vlogif._GetFormattedTraceback(), taskID_=None)
        finally:
            if _xcpCaught is not None:
                self.CleanUpByOwnerRequest(ppass_)
                _LcFailure.CheckSetLcSetupFailure(_EFwErrorCode.FE_LCSF_088)

                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcDepManager_TID_001).format(str(_xcpCaught))
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00323)

    @property
    def lcScope(self) -> _ELcScope:
        return self.__s

    @property
    def fwConfig(self) -> _FwConfig:
        return self.__c

    @property
    def subsystemConfigSupervisor(self):
        return self.__sc

    @property
    def ignoredUnsupportedCmdLineArgs(self) -> list:
        return None if self.__c is None else _FwSOptionsImpl._GetUnsupportedOptionsNameList()

    def UpdateLcScope(self, tgtScope_ : _ELcScope, bForceReinject_ =False, bFinalize_ =False) -> _EExecutionCmdID:
        if self.__isInvalid:
            return _EExecutionCmdID.NOK()

        if tgtScope_ == self.lcScope:
            if not (bForceReinject_ or bFinalize_):
                return _EExecutionCmdID.OK()

        _iImplErr = None

        _badUseMsg = None
        _myLcState = self.__g._GGetLcState(bypassApiLock_=True)

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
                res = _EExecutionCmdID.OK()
            else:
                res = _EExecutionCmdID.NOK()
                if not _LcFailure.IsSetupPhasePassed():
                    _LcFailure.CheckSetLcSetupFailure(_iImplErr)
                if _badUseMsg is not None:
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00324)
            return res

        res      = _EExecutionCmdID.OK()
        _myXcp   = None
        _errMsg  = None
        _errCode = None
        try:
            if not self.__sd.SwitchLcScope(tgtScope_, self.lcScope, bForceReinject_=bForceReinject_, bFinalize_=bFinalize_):
                res      = _EExecutionCmdID.NOK()
                _errCode = _EFwErrorCode.FE_LCSF_090
                _errMsg  = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcDepManager_TID_003).format(self.lcScope.compactName, tgtScope_.compactName)
        except _XcoXcpRootBase as _xcp:
            _myXcp = _xcp
        except BaseException as _xcp:
            _myXcp = _XcoBaseException(_xcp, tb_=vlogif._GetFormattedTraceback(), taskID_=None)
        finally:
            if _myXcp is not None:
                res      = _EExecutionCmdID.NOK()
                _errCode = _EFwErrorCode.FE_LCSF_091
                _errMsg  = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcDepManager_TID_004).format(_myXcp)

        if not res.isOK:
            if not _LcFailure.IsSetupPhasePassed():
                _LcFailure.CheckSetLcSetupFailure(_errCode, errMsg_=_errMsg)
            vlogif._LogOEC(True, _errCode)
        else:
            self.__s = tgtScope_
        return res

    def _ToString(self):
        if self.__isInvalid:
            return None
        _myTxt = _FwTDbEngine.GetText(_EFwTextID.eLcDepManager_ToString_01)
        return _myTxt.format(type(self).__name__, self.lcScope.compactName, self.__g._GGetLcState(bypassApiLock_=True))

    def _CleanUpByOwnerRequest(self):
        if _LcDepManager.__sgltn is not None:
            if id(_LcDepManager.__sgltn) == id(self):
                _LcDepManager.__sgltn = None

        if self.__h is not None:
            if self.__sd is not None:
                self.__sd.CleanUpByOwnerRequest(self.__h)
            if self.__sc is not None:
                self.__sc.CleanUpByOwnerRequest(self.__h)
            if self.__c is not None:
                self.__c.CleanUpByOwnerRequest(self.__h)
            self.__c  = None
            self.__g  = None
            self.__s  = None
            self.__h  = None
            self.__sc = None
            self.__sd = None

    @property
    def __isInvalid(self) -> bool:
        return self.__h is None

    @staticmethod
    def __GetPreamble():
        _dlLong  = _CommonDefines._DASH_LINE_LONG
        _dlShort = _CommonDefines._DASH_LINE_SHORT

        _pyv  = _SystemInfo._GetPythonVer()
        if _SystemInfo._IsGilDisabled():
            _pyv += _CommonDefines._CHAR_SIGN_SPACE + _FwTDbEngine.GetText(_EFwTextID.eFwApiBase_StartPreamble_FT_Python)
        _pyv  = _FwTDbEngine.GetText(_EFwTextID.eFwApiBase_StartPreamble_Python_Version).format(_pyv)
        _xcov = _FwVersion._GetVersionInfo(bShort_=False)

        res = _FwTDbEngine.GetText(_EFwTextID.eFwApiBase_StartPreamble)
        res = res.format(_dlLong, _dlShort, _dlShort, _xcov, _dlShort, _pyv, _dlShort, _dlLong)
        return res

    @staticmethod
    def __CreatePrerequisites(lcDMH_ : int, suPolicy_ : _FwStartupPolicy, startOptions_ : list) -> _FwSOptionsImpl:
        _sopt     = None
        _errCode  = None
        _bPrintSP = True

        if not suPolicy_.isValid:
            _errCode = _EFwErrorCode.FE_LCSF_037
        else:
            _sopt = _FwSOptionsImpl(lcDMH_, suPolicy_, [])
            if not _sopt._isValid:
                _sopt.CleanUpByOwnerRequest(lcDMH_)
                _sopt    = None
                _errCode = _EFwErrorCode.FE_LCSF_038
            else:
                _sopt.CleanUpByOwnerRequest(lcDMH_)
                _sopt = _FwSOptionsImpl(lcDMH_, suPolicy_, startOptions_=startOptions_)
                if not _sopt._isValid:
                    _sopt.CleanUpByOwnerRequest(lcDMH_)
                    _sopt = None
                elif _sopt._IsSilentFwLogLevel():
                    _bPrintSP = False
                elif _sopt._isSuppressStartPreambleEnabled:
                    _bPrintSP = False

        if _bPrintSP:
            _PutLR(_LcDepManager.__GetPreamble())
            _PutLR(_FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_006).format(_ssshare._GetRteConfig()))
        if _errCode is not None:
            _LcFailure.CheckSetLcSetupFailure(_errCode)
            vlogif._LogOEC(True, _errCode)
        return _sopt

    def __LoadConfig(self, lcDMH_ : int, suPolicy_ : _FwStartupPolicy, fwSOpt_ : _FwSOptionsImpl) -> bool:
        self.__c = _FwConfig(lcDMH_, suPolicy_, fwSOpt_)
        if not self.__c.isValid:
            self.__c.CleanUpByOwnerRequest(lcDMH_)
            self.__c = None

            if _LcFailure.IsLcErrorFree():
                _errMsg  = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcDepManager_TID_002).format()
                _errCode = _EFwErrorCode._EFwErrorCode.FE_LCSF_089

                _LcFailure.CheckSetLcSetupFailure(_errCode, errMsg_=_errMsg)
                vlogif._LogOEC(True, _errCode)
        return self.__c is not None
