# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwstartuppolicy.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from enum import unique

from xcofdk._xcofw.fw.fwssys.fwcore.logging           import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcdefines      import _ELcScope
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcdefines      import _LcConfig
from xcofdk._xcofw.fw.fwssys.fwcore.types.apobject    import _ProtectedAbstractSlotsObject
from xcofdk._xcofw.fw.fwssys.fwcore.types.ebitmask    import _EBitMask
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes import _FwIntFlag
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes import _CommonDefines

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine


class _FwStartupPolicy(_ProtectedAbstractSlotsObject):

    @unique
    class _ESUPFlag(_FwIntFlag):
        ebfNone = 0x0000
        ebfPD   = (0x0001 << 10)
        ebfRM   = (0x0001 << 11)  
        ebfUCF  = (0x0001 << 12)  
        ebfFCCF = (0x0001 << 13)  

        @property
        def compactName(self) -> str:
            return self.name[3:]

        @property
        def isNone(self):
            return self==_FwStartupPolicy._ESUPFlag.ebfNone

        @property
        def isRM(self):
            return self==_FwStartupPolicy._ESUPFlag.ebfRM

        @property
        def isPD(self):
            return self==_FwStartupPolicy._ESUPFlag.ebfPD

        @property
        def isUCF(self):
            return self==_FwStartupPolicy._ESUPFlag.ebfUCF

        @property
        def isFCCF(self):
            return self==_FwStartupPolicy._ESUPFlag.ebfFCCF

        @staticmethod
        def IsNone(eSUPMask_: _FwIntFlag):
            return eSUPMask_==_FwStartupPolicy._ESUPFlag.ebfNone

        @staticmethod
        def IsPDSet(eSUPMask_: _FwIntFlag):
            return _EBitMask.IsEnumBitFlagSet(eSUPMask_, _FwStartupPolicy._ESUPFlag.ebfPD)

        @staticmethod
        def IsRMSet(eSUPMask_: _FwIntFlag):
            return _EBitMask.IsEnumBitFlagSet(eSUPMask_, _FwStartupPolicy._ESUPFlag.ebfRM)

        @staticmethod
        def IsUCFSet(eSUPMask_: _FwIntFlag):
            return _EBitMask.IsEnumBitFlagSet(eSUPMask_, _FwStartupPolicy._ESUPFlag.ebfUCF)

        @staticmethod
        def IsFCCFSet(eSUPMask_: _FwIntFlag):
            return _EBitMask.IsEnumBitFlagSet(eSUPMask_, _FwStartupPolicy._ESUPFlag.ebfFCCF)

        @staticmethod
        def AddSUPFlag(eSUPMask_: _FwIntFlag, eSUPFlag_):
            return _EBitMask.AddEnumBitFlag(eSUPMask_, eSUPFlag_)

        @staticmethod
        def RemoveSUPFlag(eSUPMask_: _FwIntFlag, eSUPFlag_):
            return _EBitMask.RemoveEnumBitFlag(eSUPMask_, eSUPFlag_)

        @staticmethod
        def IsSUPFlagSet(eSUPMask_: _FwIntFlag, eSUPFlag_):
            return _EBitMask.IsEnumBitFlagSet(eSUPMask_, eSUPFlag_)


    __slots__ = [ '__supbm' , '__lcTgtScp' , '__xRootDir' ]

    __SUP_BM = None  
    __SUP_TS = None  

    def __init__(self, ppass_ : int):
        super().__init__(ppass_)
        self.__supbm    = None
        self.__xRootDir = None
        self.__lcTgtScp = None

        if not self.__CheckPD():
            return
        if _FwStartupPolicy.__SUP_TS is None:
            _FwStartupPolicy.__SUP_TS = _LcConfig.GetTargetScope()
        elif _FwStartupPolicy.__SUP_TS != _LcConfig.GetTargetScope():
            vlogif._XLogFatal('Mismatch of target scope: {} vs. {}'.format(_FwStartupPolicy.__SUP_TS.value, _LcConfig.GetTargetScope().value))
            return

        self.__lcTgtScp = _FwStartupPolicy.__SUP_TS

    @property
    def isValid(self):
        return not self.__isInvalid

    @property
    def isPackageDist(self):
        return False if self.__isInvalid else _FwStartupPolicy._ESUPFlag.IsPDSet(self.__supbm)

    @property
    def isReleaseModeEnabled(self):
        return False if self.__isInvalid else _FwStartupPolicy._ESUPFlag.IsRMSet(self.__supbm)

    @property
    def isUserConfigFileSupportEnabled(self):
        return False if self.__isInvalid else _FwStartupPolicy._ESUPFlag.IsUCFSet(self.__supbm)

    @property
    def isFwCustomConfigFileSupportEnabled(self):
        return False if self.__isInvalid else _FwStartupPolicy._ESUPFlag.IsFCCFSet(self.__supbm)

    @property
    def isSyncPrintEnabled(self):
        return self.isValid and not _FwStartupPolicy._ESUPFlag.IsRMSet(self.__supbm)

    @property
    def lcTargetScope(self) -> _ELcScope:
        return None if self.__isInvalid else self.__lcTgtScp

    @property
    def xcofdkRootDir(self) -> str:
        return None if self.__isInvalid else self.__xRootDir

    def _ToString(self):
        if self.__isInvalid:
            res = None
        else:
            res  = '{}:\n'.format(type(self).__name__)
            res += '  {:<35s} : {:<s}\n'.format('isPackageDist'                      , str(self.isPackageDist))
            res += '  {:<35s} : {:<s}\n'.format('isReleaseModeEnabled'               , str(self.isReleaseModeEnabled))
            res += '  {:<35s} : {:<s}\n'.format('isUserConfigFileSupportEnabled'     , str(self.isUserConfigFileSupportEnabled))
            res += '  {:<35s} : {:<s}\n'.format('isFwCustomConfigFileSupportEnabled' , str(self.isFwCustomConfigFileSupportEnabled))
            res += '  {:<35s} : {:<s}\n'.format('lcTargetScope'                      , self.lcTargetScope.compactName)
            res += '  {:<35s} : {:<s}\n'.format('xcofdkRootDir'                      , self.xcofdkRootDir)
            res += _CommonDefines._CHAR_SIGN_NEWLINE
        return res

    def _CleanUpByOwnerRequest(self):
        self.__supbm    = None
        self.__xRootDir = None
        self.__lcTgtScp = None

    @property
    def __isInvalid(self):
        return self.__lcTgtScp is None

    @staticmethod
    def _SetUp( bRelMode_ : bool =None, bDevMode_ : bool =None, eLcTargetScope_ : _ELcScope =None
              , bEnableUserConfig_ : bool =None, bEnableFwCustomConfig_ : bool =None):
        _FwStartupPolicy.__CheckSetDefaultBM()

        _myMsg = _CommonDefines._STR_EMPTY
        _supBM = _FwStartupPolicy.__SUP_BM

        if bRelMode_ is not None:
            if _FwStartupPolicy._ESUPFlag.IsRMSet(_supBM)  != bRelMode_:
                _midPart = 'releaseMode'
                _myMsg  += f'{_midPart}={bRelMode_}  '
                if bRelMode_:
                    _supBM = _FwStartupPolicy._ESUPFlag.AddSUPFlag(_supBM, _FwStartupPolicy._ESUPFlag.ebfRM)
                else:
                    _supBM = _FwStartupPolicy._ESUPFlag.RemoveSUPFlag(_supBM, _FwStartupPolicy._ESUPFlag.ebfRM)
        if bEnableUserConfig_ is not None:
            if _FwStartupPolicy._ESUPFlag.IsUCFSet(_supBM) != bEnableUserConfig_:
                _midPart = 'enableUserConfig'
                _myMsg  += f'{_midPart}={bEnableUserConfig_}  '
                if bEnableUserConfig_:
                    _supBM = _FwStartupPolicy._ESUPFlag.AddSUPFlag(_supBM, _FwStartupPolicy._ESUPFlag.ebfUCF)
                else:
                    _supBM = _FwStartupPolicy._ESUPFlag.RemoveSUPFlag(_supBM, _FwStartupPolicy._ESUPFlag.ebfUCF)
        if bEnableFwCustomConfig_ is not None:
            if _FwStartupPolicy._ESUPFlag.IsFCCFSet(_supBM) != bEnableFwCustomConfig_:
                _midPart = 'enableFwCustomConfig'
                _myMsg  += f'{_midPart}={bEnableFwCustomConfig_}  '
                if bEnableFwCustomConfig_:
                    _supBM = _FwStartupPolicy._ESUPFlag.AddSUPFlag(_supBM, _FwStartupPolicy._ESUPFlag.ebfFCCF)
                else:
                    _supBM = _FwStartupPolicy._ESUPFlag.RemoveSUPFlag(_supBM, _FwStartupPolicy._ESUPFlag.ebfFCCF)
        if eLcTargetScope_ is not None:
            if _LcConfig.GetTargetScope() != eLcTargetScope_:
                _LcConfig._SetTargetScope(eLcTargetScope_)
                _FwStartupPolicy.__SUP_TS = _LcConfig.GetTargetScope()
                _midPart = 'lcTargetScope'
                _myMsg  += f'{_midPart}={_LcConfig.GetTargetScope().compactName}  '

        if len(_myMsg) > 0:
            _FwStartupPolicy.__SUP_BM = _supBM

    @staticmethod
    def _Restore():
        _FwStartupPolicy.__SUP_TS = None
        _FwStartupPolicy.__SUP_BM = None

        _FwStartupPolicy.__CheckSetDefaultBM()
        _LcConfig._Restore()

    @staticmethod
    def __CheckSetDefaultBM():
        if _FwStartupPolicy.__SUP_BM is None:
            _FwStartupPolicy.__SUP_BM = _FwStartupPolicy._ESUPFlag.ebfRM

    def __CheckPD(self) -> bool:
        _FwStartupPolicy.__CheckSetDefaultBM()

        _bPkgDist      = None
        _xcofdkRootDir = None
        _xcofdkRootDir, _bPkgDist = _FwTDbEngine._GetXcofdkRootAbsPath()
        if _xcofdkRootDir is None:
            return False

        if _bPkgDist:
            _FwStartupPolicy.__SUP_BM = _FwStartupPolicy._ESUPFlag.AddSUPFlag(_FwStartupPolicy.__SUP_BM, _FwStartupPolicy._ESUPFlag.ebfPD)

        self.__supbm    = _FwStartupPolicy.__SUP_BM
        self.__xRootDir = _xcofdkRootDir
        return True
