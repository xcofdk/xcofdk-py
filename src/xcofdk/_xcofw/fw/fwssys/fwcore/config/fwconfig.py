# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwconfig.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


import os.path

from xcofdk._xcofw.fw.fwssys.fwcore.logging                   import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.base.fsutil               import _FSUtil
from xcofdk._xcofw.fw.fwssys.fwcore.config.fwstartoptionsimpl import _FwStartOptionsImpl
from xcofdk._xcofw.fw.fwssys.fwcore.config.fwstartupconfig    import _FwStartupConfig
from xcofdk._xcofw.fw.fwssys.fwcore.config.fwstartuppolicy    import _FwStartupPolicy
from xcofdk._xcofw.fw.fwssys.fwcore.types.apobject            import _ProtectedAbstractSlotsObject
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes         import _CommonDefines

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine


class _FwConfig(_ProtectedAbstractSlotsObject):

    __slots__ = [ '__fwCoreDirPath' , '__cfgStartup' , '__fwSOpt' ]

    __CFG_DIR_REL_PATH = None

    def __init__(self, ppass_ : int, suPolicy_ : _FwStartupPolicy, fwSOpt_ : _FwStartOptionsImpl):
        super().__init__(ppass_)
        self.__fwSOpt        = None
        self.__cfgStartup    = None
        self.__fwCoreDirPath = None

        self.__SetUpDirPaths(suPolicy_)
        if not self.isValid:
            self.CleanUpByOwnerRequest(ppass_)
            vlogif._XLogFatal("[CFG] Failed to retrieve xco dir info.")
        else:
            self.__cfgStartup = _FwStartupConfig(ppass_, suPolicy_, fwSOpt_)
            if not self.__cfgStartup._isValid:
                self.CleanUpByOwnerRequest(ppass_)
            else:
                self.__fwSOpt = fwSOpt_

    @property
    def isValid(self) -> bool:
        return self.__fwCoreDirPath is not None

    @property
    def fwCoreDirPath(self) -> str:
        return self.__fwCoreDirPath


    @property
    def fwStartOptions(self) -> _FwStartOptionsImpl:
        return self.__fwSOpt

    @property
    def fwStartupConfig(self) -> _FwStartupConfig:
        return self.__cfgStartup

    def _ToString(self, *args_, **kwargs_):
        if not self.isValid:
            return None

        res   = "Xco dir info:\n"
        res  += "  {:<18s} : {:<s}\n".format("FwCoreDirPath"   , self.fwCoreDirPath)
        res  += _CommonDefines._CHAR_SIGN_NEWLINE
        return res

    def _CleanUpByOwnerRequest(self):
        self.__fwCoreDirPath = None

        if self.__fwSOpt is not None:
            self.__fwSOpt.CleanUpByOwnerRequest(self.__fwSOpt._myPPass)
            self.__fwSOpt = None
        if self.__cfgStartup is not None:
            self.__cfgStartup.CleanUpByOwnerRequest(self._myPPass)
            self.__cfgStartup = None

    def __SetUpDirPaths(self, suPolicy_ : _FwStartupPolicy):
        _fwCoreRelPath = '_xcofw'
        _FwConfig.__CFG_DIR_REL_PATH = None

        if not suPolicy_.isPackageDist:
            _fwCoreRelPath                = _FwTDbEngine.GetText(_EFwTextID.eFwConfig_FwCoreRelPath)
            _FwConfig.__CFG_DIR_REL_PATH  = _FwTDbEngine.GetText(_EFwTextID.eFwConfig_FwCfgDirRelPath)

        _fwCoreDir = os.path.join(suPolicy_.xcofdkRootDir, _fwCoreRelPath)
        if not _FSUtil.IsExistingDir(_fwCoreDir):
            vlogif._XLogFatal('[CFG] Non-existing fw core dir.')
            return

        _fwConfigDir = _fwCoreDir if _FwConfig.__CFG_DIR_REL_PATH is None else os.path.join(_fwCoreDir, _FwConfig.__CFG_DIR_REL_PATH)
        if not _FSUtil.IsExistingDir(_fwConfigDir):
            vlogif._XLogFatal('[CFG] Non-existing fw config dir.')
            return
        self.__fwCoreDirPath = _fwCoreDir
