# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwconfig.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

import os.path

from _fw.fwssys.fwcore.logging                import vlogif
from _fw.fwssys.fwcore.base.fsutil            import _FSUtil
from _fw.fwssys.fwcore.config.fwsoptionsimpl  import _FwSOptionsImpl
from _fw.fwssys.fwcore.config.fwstartupconfig import _FwStartupConfig
from _fw.fwssys.fwcore.config.fwstartuppolicy import _FwStartupPolicy
from _fw.fwssys.fwcore.types.apobject         import _ProtAbsSlotsObject
from _fw.fwssys.fwcore.types.commontypes      import _CommonDefines
from _fw.fwssys.fwerrh.fwerrorcodes           import _EFwErrorCode

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _FwConfig(_ProtAbsSlotsObject):
    __slots__ = [ '__so' , '__cdp' , '__suc' ]

    __CFG_DIR_REL_PATH = None

    def __init__(self, ppass_ : int, suPolicy_ : _FwStartupPolicy, fwSOpt_ : _FwSOptionsImpl):
        super().__init__(ppass_)
        self.__so  = None
        self.__suc = None
        self.__cdp = None

        self.__SetUpDirPaths(suPolicy_)
        if not self.isValid:
            self.CleanUpByOwnerRequest(ppass_)
            vlogif._XLogFatalEC(_EFwErrorCode.FE_00902, _FwTDbEngine.GetText(_EFwTextID.eFwConfig_TID_003))
        else:
            self.__suc = _FwStartupConfig(ppass_, suPolicy_, fwSOpt_)
            if not self.__suc._isValid:
                self.CleanUpByOwnerRequest(ppass_)
            else:
                self.__so = fwSOpt_

    @property
    def isValid(self) -> bool:
        return self.__cdp is not None

    @property
    def fwCoreDirPath(self) -> str:
        return self.__cdp

    @property
    def fwStartOptions(self) -> _FwSOptionsImpl:
        return self.__so

    @property
    def fwStartupConfig(self) -> _FwStartupConfig:
        return self.__suc

    def _ToString(self):
        if not self.isValid:
            return None
        return _CommonDefines._STR_EMPTY

    def _CleanUpByOwnerRequest(self):
        self.__cdp = None

        if self.__so is not None:
            self.__so.CleanUpByOwnerRequest(self.__so._myPPass)
            self.__so = None
        if self.__suc is not None:
            self.__suc.CleanUpByOwnerRequest(self._myPPass)
            self.__suc = None

    def __SetUpDirPaths(self, suPolicy_ : _FwStartupPolicy):
        _fwCoreRelPath = '_xcofw'
        _FwConfig.__CFG_DIR_REL_PATH = None

        if not suPolicy_.isPackageDist:
            _fwCoreRelPath                = _FwTDbEngine.GetText(_EFwTextID.eFwConfig_TID_001)
            _FwConfig.__CFG_DIR_REL_PATH  = _FwTDbEngine.GetText(_EFwTextID.eFwConfig_TID_002)

        _fwCoreDir = os.path.join(suPolicy_.xcofdkRootDir, _fwCoreRelPath)
        if not _FSUtil.IsExistingDir(_fwCoreDir):
            vlogif._XLogFatalEC(_EFwErrorCode.FE_00903, _FwTDbEngine.GetText(_EFwTextID.eFwConfig_TID_004))
            return

        _fwConfigDir = _fwCoreDir if _FwConfig.__CFG_DIR_REL_PATH is None else os.path.join(_fwCoreDir, _FwConfig.__CFG_DIR_REL_PATH)
        if not _FSUtil.IsExistingDir(_fwConfigDir):
            vlogif._XLogFatalEC(_EFwErrorCode.FE_00904, _FwTDbEngine.GetText(_EFwTextID.eFwConfig_TID_005))
            return
        self.__cdp = _fwCoreDir
