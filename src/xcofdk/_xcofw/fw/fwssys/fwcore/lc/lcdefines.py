# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : lcdefines.py
#
# Copyright(c) 2023-2024 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes  import _FwIntEnum
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes  import unique

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine

@unique
class _ELcScope(_FwIntEnum):
    eIdle    =0
    ePreIPC  =1  
    eSemiIPC =2  
    eFullIPC =3  

    @property
    def isIdle(self):
        return self == _ELcScope.eIdle

    @property
    def isPreIPC(self):
        return self == _ELcScope.ePreIPC

    @property
    def isIPC(self):
        return self.isFullIPC or self.isSemiIPC

    @property
    def isSemiIPC(self):
        return self == _ELcScope.eSemiIPC

    @property
    def isFullIPC(self):
        return self == _ELcScope.eFullIPC

    @property
    def lcTransitionalOrder(self):
        return self.value

@unique
class _ELcOperationModeID(_FwIntEnum):
    eLcCeaseMode       = -2
    eIdle              = -1
    eLcNormal          = 0
    eLcPreShutdown     = 1
    eLcShutdown        = 2
    eLcFailureHandling = 8

    @property
    def isIdle(self):
        return self == _ELcOperationModeID.eIdle

    @property
    def isLcCeaseMode(self):
        return self == _ELcOperationModeID.eLcCeaseMode

    @property
    def isLcNormal(self):
        return self == _ELcOperationModeID.eLcNormal

    @property
    def isLcPreShutdown(self):
        return self == _ELcOperationModeID.eLcPreShutdown

    @property
    def isLcShutdown(self):
        return self == _ELcOperationModeID.eLcShutdown

    @property
    def isLcFailureHandling(self):
        return self == _ELcOperationModeID.eLcFailureHandling

    @property
    def isLcShutdownSequenceMode(self):
        return self.value  > _ELcOperationModeID.eLcNormal.value

@unique
class _ELcCompID(_FwIntEnum):
    eLcMgr    = -7311
    eTMgr     = -7411
    eFwComp   = -7511
    eXTask    = -7611
    eMiscComp = -7711

    eLcDMgr  = eLcMgr  - 1
    eLcPxy   = eLcDMgr - 1
    eFwMain  = eFwComp  - 1
    eFwDspr  = eFwMain  - 1
    eTmrMgr  = eFwDspr  - 1
    eMainXTask = eXTask - 1
    eFwRbl   = eMiscComp - 1
    eUserRbl = eFwRbl    - 1
    eUTRbl   = eUserRbl  - 1
    eFwThrd  = eUTRbl    - 1

    @property
    def compactName(self) -> str:
        if   self == _ELcCompID.eLcMgr      : res = _FwTDbEngine.GetText(_EFwTextID.eELcCompID_LcMgr)
        elif self == _ELcCompID.eTMgr       : res = _FwTDbEngine.GetText(_EFwTextID.eELcCompID_TMgr)
        elif self == _ELcCompID.eFwComp     : res = _FwTDbEngine.GetText(_EFwTextID.eELcCompID_FwComp)
        elif self == _ELcCompID.eXTask      : res = _FwTDbEngine.GetText(_EFwTextID.eELcCompID_XTask)
        elif self == _ELcCompID.eMiscComp   : res = _FwTDbEngine.GetText(_EFwTextID.eELcCompID_MiscComp)
        elif self == _ELcCompID.eLcDMgr     : res = _FwTDbEngine.GetText(_EFwTextID.eELcCompID_LcDMgr)
        elif self == _ELcCompID.eLcPxy      : res = _FwTDbEngine.GetText(_EFwTextID.eELcCompID_LcPxy)
        elif self == _ELcCompID.eFwMain     : res = _FwTDbEngine.GetText(_EFwTextID.eELcCompID_FwMain)
        elif self == _ELcCompID.eFwDspr     : res = _FwTDbEngine.GetText(_EFwTextID.eELcCompID_FwDspr)
        elif self == _ELcCompID.eTmrMgr     : res = _FwTDbEngine.GetText(_EFwTextID.eELcCompID_TmrMgr)
        elif self == _ELcCompID.eMainXTask  : res = _FwTDbEngine.GetText(_EFwTextID.eELcCompID_MainXTask)
        elif self == _ELcCompID.eFwRbl      : res = _FwTDbEngine.GetText(_EFwTextID.eELcCompID_FwRbl)
        elif self == _ELcCompID.eUserRbl    : res = _FwTDbEngine.GetText(_EFwTextID.eELcCompID_UserRbl)
        elif self == _ELcCompID.eUTRbl      : res = _FwTDbEngine.GetText(_EFwTextID.eELcCompID_UTRbl)
        elif self == _ELcCompID.eFwThrd     : res = _FwTDbEngine.GetText(_EFwTextID.eELcCompID_FwThrd)
        else:
            res = ''
        return res

    @property
    def lcCompGroupID(self):
        return _ELcCompID.__GetGropID(self)

    @property
    def isXtask(self):
        return (self == _ELcCompID.eXTask) or (self == _ELcCompID.eMainXTask)

    @property
    def isMainXtask(self):
        return self == _ELcCompID.eMainXTask

    @property
    def isFwComp(self):
        return (self == _ELcCompID.eFwComp) or self.isFwMain

    @property
    def isFwMain(self):
        return self == _ELcCompID.eFwMain

    @property
    def isTaskManager(self):
        return self == _ELcCompID.eTMgr

    @staticmethod
    def __GetGropID(eLcCompID_ : _FwIntEnum):
        if not isinstance(eLcCompID_, _ELcCompID):
            return None

        val = eLcCompID_.value

        if val == _ELcCompID.eTMgr.value:
            return _ELcCompID.eTMgr

        elif val > _ELcCompID.eTMgr.value:
            return _ELcCompID.eLcMgr

        elif (val <= _ELcCompID.eFwComp.value) and (val > _ELcCompID.eXTask.value):
            return _ELcCompID.eFwComp

        elif (val <= _ELcCompID.eXTask.value) and (val > _ELcCompID.eMiscComp.value):
            return _ELcCompID.eXTask

        else:  
            return _ELcCompID.eMiscComp

class _LcConfig:
    __eTargetScope = None

    @staticmethod
    def IsTargetScopeIPC():
        return True

    @staticmethod
    def GetTargetScope() -> _ELcScope:
        if _LcConfig.__eTargetScope is None:
            _LcConfig.__eTargetScope = _ELcScope.eFullIPC
        return _LcConfig.__eTargetScope

    @staticmethod
    def ToString():
        res = _FwTDbEngine.GetText(_EFwTextID.eLcConfig_ToString).format(str(_LcConfig.GetTargetScope().compactName))
        return res

    @staticmethod
    def _SetTargetScope(tgtScope_ : _ELcScope):

        if isinstance(tgtScope_, _ELcScope):
            _LcConfig.__eTargetScope = tgtScope_

    @staticmethod
    def _Restore():
        _LcConfig.__eTargetScope = None
