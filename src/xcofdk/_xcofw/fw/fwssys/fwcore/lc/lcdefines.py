# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : lcdefines.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from xcofdk._xcofw.fw.fwssys.fwcore.logging.logdefines import _EErrorImpact
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


class _LcFrcView:

    __slots__ = [ '__eCID' , '__feClone' , '__bFFE' , '__bTType' , '__tid' , '__tuid' , '__tskName', '__thrdName' , '__errImp' ]

    def __init__( self, *, eCID_ : _ELcCompID, ferr_, bForeignFE_ : bool, bTType_ : bool
                , tskName_ : str, thrdName_ : str, tid_ : int, tuid_ : int ):
        self.__tid      = tid_
        self.__eCID     = eCID_
        self.__tuid     = tuid_
        self.__bFFE     = bForeignFE_
        self.__bTType   = bTType_
        self.__errImp   = None
        self.__feClone  = ferr_
        self.__tskName  = tskName_
        self.__thrdName = thrdName_

        _bError = True

        if ferr_ is None:
            pass
        elif not ferr_.isClone:
            pass
        elif ferr_.eErrorImpact is None:
            pass
        elif not ferr_.eErrorImpact.hasImpact:
            pass
        elif not ferr_.eErrorImpact.isCausedByFatalError:
            pass
        else:
            _bError = False

        if _bError:
            self.CleanUp()
        else:
            self.__errImp = ferr_.eErrorImpact

    def __str__(self):
        return self.ToString()

    @property
    def isValid(self):
        return self.__eCID is not None

    @property
    def isForeignFatalError(self):
        return self.__bFFE

    @property
    def isReportedByPyThread(self):
        return self.__bTType is None

    @property
    def isReportedByAbstractTask(self):
        return self.__bTType is not None

    @property
    def isReportedByFwTask(self):
        return (self.__bTType is not None) and (self.__bTType == True)

    @property
    def isReportedByFwThread(self):
        return (self.__bTType is not None) and (self.__bTType == False)

    @property
    def eLcCompID(self) -> _ELcCompID:
        return self.__eCID

    @property
    def eErrorImpact(self) -> _EErrorImpact:
        return self.__errImp

    @property
    def fatalErrorClone(self):
        return self.__feClone

    @property
    def taskName(self):
        return self.__tskName

    @property
    def threadName(self):
        return self.__thrdName

    @property
    def taskID(self):
        return self.__tid

    @property
    def taskUID(self):
        return self.__tuid

    def ToString(self, bVerbose_ =True) -> str:
        if not self.isValid:
            return None

        if self.isReportedByPyThread:
            _uname = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_011).format(self.__thrdName, self.__tuid)
        else:
            _uname = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_011).format(self.__tskName, self.__tid)

        if self.__feClone is not None:
            res = _FwTDbEngine.GetText(_EFwTextID.eLcFrcView_ToString_01).format(self.__eCID.compactName, _uname, self.__feClone.uniqueID, self.__feClone.shortMessage)
            if bVerbose_:
                res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_012).format(str(self.__feClone))
        else:
            res = _FwTDbEngine.GetText(_EFwTextID.eLcFrcView_ToString_02).format(self.__eCID.compactName, _uname)
        return res

    def CleanUp(self):
        if self.__feClone is not None:
            self.__feClone.CleanUp()

        self.__tid      = None
        self.__eCID     = None
        self.__tuid     = None
        self.__bFFE     = None
        self.__bTType   = None
        self.__errImp   = None
        self.__feClone  = None
        self.__tskName  = None
        self.__thrdName = None

    def _DetachFatalError(self):
        res = self.__feClone
        self.__feClone = None
        return res


class _LcConfig:
    __eTargetScope = None

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
