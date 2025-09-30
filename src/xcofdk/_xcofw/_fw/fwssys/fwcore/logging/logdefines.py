# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : logdefines.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

import sys
import traceback

from datetime  import datetime as _PyDateTime
from enum      import auto
from enum      import unique
from enum      import IntEnum
from sys       import maxsize as _PY_MAX_SIZE

from threading import current_thread as _GetCurThread
from threading import RLock          as _PyRLock

from _fw.fwssys.fwcore.logrd.logrecord   import _ELRType
from _fw.fwssys.fwcore.types.commontypes import _CommonDefines
from _fw.fwssys.fwcore.types.commontypes import _EDepInjCmd

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

@unique
class _ELogLevel(IntEnum):
    eFatal   = 0
    eError   = auto()
    eWarning = auto()
    eKPI     = auto()
    eInfo    = auto()
    eDebug   = auto()
    eTrace   = auto()

    @property
    def compactName(self):
        res = _FwTDbEngine.GetText(_EFwTextID(self.value+_EFwTextID.eELogLevel_Fatal.value))
        if res is None:
            res = self.name[1:]
        return res

    def IsEnclosing(self, loglevel_):
        if not isinstance(loglevel_, _ELogLevel):
            return False
        return loglevel_.value <= self.value

    def Encode(self):
        return self.compactName.lower()

    @staticmethod
    def Decode(code_ : str):
        res = None
        if isinstance(code_, str):
            for _n, _m in _ELogLevel.__members__.items():
                if _m.compactName.lower() == code_.lower():
                    res = _ELogLevel(_m.value)
                    break
        return res

@unique
class _ELogType(IntEnum):
    FREE        = _ELRType.LR_FREE.value  # free logs are 'unformatted' traces  !!??
    TRC         = _ELRType.LR_TRC.value
    DBG         = _ELRType.LR_DBG.value
    INF         = _ELRType.LR_INF.value
    KPI         = _ELRType.LR_KPI.value
    WNG         = _ELRType.LR_WNG.value
    WNG_URGENT  = auto()
    ERR         = _ELRType.LR_ERR.value  
    ERR_NSY     = auto()
    FTL         = _ELRType.LR_FTL.value  
    FTL_BU      = auto()  
    FTL_IE      = auto()  
    FTL_NIY     = auto()  
    FTL_SOE     = auto()  
    FTL_SOX     = auto()  
    FTL_NERR    = auto()  

    XTRC        = -1*TRC
    XDBG        = -1*DBG
    XINF        = -1*INF
    XKPI        = -1*KPI         
    XWNG        = -1*WNG
    XWNG_URGENT = -1*WNG_URGENT
    XERR        = -1*ERR
    XERR_NSY    = -1*ERR_NSY
    XFTL        = -1*FTL
    XFTL_SOX    = -1*FTL_SOX

    @property
    def compactName(self) -> str:
        _absSelf = _ELogType(self._absValue)
        if   _absSelf == _ELogType.TRC        : res = _FwTDbEngine.GetText(_EFwTextID.eELogType_TRC)
        elif _absSelf == _ELogType.DBG        : res = _FwTDbEngine.GetText(_EFwTextID.eELogType_DBG)
        elif _absSelf == _ELogType.INF        : res = _FwTDbEngine.GetText(_EFwTextID.eELogType_INF)
        elif _absSelf == _ELogType.KPI        : res = _FwTDbEngine.GetText(_EFwTextID.eELogType_KPI)
        elif _absSelf == _ELogType.WNG        : res = _FwTDbEngine.GetText(_EFwTextID.eELogType_WNG)
        elif _absSelf == _ELogType.WNG_URGENT : res = _FwTDbEngine.GetText(_EFwTextID.eELogType_WNG)
        elif _absSelf == _ELogType.ERR        : res = _FwTDbEngine.GetText(_EFwTextID.eELogType_ERR)
        elif _absSelf == _ELogType.ERR_NSY    : res = _FwTDbEngine.GetText(_EFwTextID.eELogType_ERR_NOT_SYET)
        elif _absSelf == _ELogType.FTL        : res = _FwTDbEngine.GetText(_EFwTextID.eELogType_FTL)
        elif _absSelf == _ELogType.FTL_BU     : res = _FwTDbEngine.GetText(_EFwTextID.eELogType_FTL_BAD_USE)
        elif _absSelf == _ELogType.FTL_IE     : res = _FwTDbEngine.GetText(_EFwTextID.eELogType_FTL_IMPL_ERR)
        elif _absSelf == _ELogType.FTL_NIY    : res = _FwTDbEngine.GetText(_EFwTextID.eELogType_FTL_NOT_IYET)
        elif _absSelf == _ELogType.FTL_SOE    : res = _FwTDbEngine.GetText(_EFwTextID.eELogType_FTL_SYS_OP_ERR)
        elif _absSelf == _ELogType.FTL_SOX    : res = _FwTDbEngine.GetText(_EFwTextID.eELogType_FTL_SYS_OP_XCP)
        elif _absSelf == _ELogType.FTL_NERR   : res = _FwTDbEngine.GetText(_EFwTextID.eELogType_FTL_NESTED_ERR)
        else:
            res = None
        if res is None:
            res = self.name
        return res

    @property
    def isFwApiLogType(self):
        return self.value < 0

    @property
    def isFree(self):
        return self == _ELogType.FREE

    @property
    def isKPI(self):
        return self._absValue == _ELogType.KPI.value

    @property
    def isWarning(self):
        return _ELogType.WNG.value <= self._absValue <= _ELogType.WNG_URGENT.value

    @property
    def isUrgentWarning(self):
        return self._absValue == _ELogType.WNG_URGENT.value

    @property
    def isNonError(self):
        return self._absValue < _ELogType.ERR.value

    @property
    def isError(self):
        return self._absValue >= _ELogType.ERR.value

    @property
    def isFatal(self):
        return self._absValue >= _ELogType.FTL.value

    @property
    def _absValue(self):
        return -1*self.value if self.value < 0 else self.value

    @property
    def _toLRLogType(self):
        return _ELRType(_LogUtil.GetLogTypeGroup(self).value)

@unique
class _EErrorImpact(IntEnum):
    eNoImpact = 0

    eNoImpactByProcessingFailure   = 3824    
    eNoImpactByLogTypePrecedence   = auto()  
    eNoImpactByExistingFatalError  = auto()  
    eNoImpactByExistingUserError   = auto()  
    eNoImpactByOwnerCondition      = auto()  
    eNoImpactBySharedCleanup       = auto()  
    eNoImpactByFrcLinkage          = auto()  
    eNoImpactByFrcLinkageDueToXCmd = auto()  

    eImpactByDieException          = auto()  
    eImpactByLogException          = auto()  
    eImpactByDieError              = auto()  
    eImpactByFatalError            = auto()  
    eImpactByFatalErrorDueToXCmd   = auto()  
    eImpactByUserError             = auto()  

    @property
    def compactName(self):
        return self.name[1:]

    @property
    def hasImpact(self):
        return not self.hasNoImpact

    @property
    def hasNoImpact(self):
        return self.value < _EErrorImpact.eImpactByDieException.value

    @property
    def hasNoImpactDueToFrcLinkage(self):
        return (self == _EErrorImpact.eNoImpactByFrcLinkage) or (self == _EErrorImpact.eNoImpactByFrcLinkageDueToXCmd)

    @property
    def hasFatalErrorImpactDueToXCmd(self):
        return self == _EErrorImpact.eImpactByFatalErrorDueToXCmd

    @property
    def isCausedByDieMode(self):
        if self.hasNoImpact:
            return False
        else:
            res =        (self == _EErrorImpact.eImpactByDieException)
            res = res or (self == _EErrorImpact.eImpactByDieError)
            return res

    @property
    def isCausedByExceptionMode(self):
        if self.hasNoImpact:
            return False
        else:
            res =        (self == _EErrorImpact.eImpactByDieException)
            res = res or (self == _EErrorImpact.eImpactByLogException)
            return res

    @property
    def isCausedByFatalError(self):
        if self.hasNoImpact:
            return False
        else:
            res = self.isCausedByDieMode or self.isCausedByExceptionMode
            res = res or (self == _EErrorImpact.eImpactByFatalError)
            res = res or (self == _EErrorImpact.eImpactByFatalErrorDueToXCmd)
            return res

@unique
class _ELogifOperationOption(IntEnum):
    eDontCare                       = 0
    ePrintXcpOnly                   = 6704
    eStrictEcMatch                  = 6804
    eSetErrorOnly                   = 6904
    eCreateLogOnly                  = auto()
    eCreateLogOnlyDueToExecCmdAbort = auto()

    @property
    def isDontCare(self):
        return self == _ELogifOperationOption.eDontCare

    @property
    def isPrintXcpOnly(self):
        return self == _ELogifOperationOption.ePrintXcpOnly

    @property
    def isStrictEcMatch(self):
        return self == _ELogifOperationOption.eStrictEcMatch

    @property
    def isSetErrorOnly(self):
        return self == _ELogifOperationOption.eSetErrorOnly

    @property
    def isCreateLogOnly(self):
        return self.value > _ELogifOperationOption.eSetErrorOnly.value

    @property
    def isCreateLogOnlyDueToExecCmdAbort(self):
        return self == _ELogifOperationOption.eCreateLogOnlyDueToExecCmdAbort

class _LogUniqueID:
    __uidLock      = None
    __nextUniqueID = 0

    @staticmethod
    def _GetNextUniqueID():
        if _LogUniqueID.__uidLock is None:
            _LogUniqueID.__uidLock = _PyRLock()
        with _LogUniqueID.__uidLock:
            _LogUniqueID.__nextUniqueID += 1
            return _LogUniqueID.__nextUniqueID

    @staticmethod
    def _DepInjection(dinjCmd_ : _EDepInjCmd):
        if _LogUniqueID.__uidLock is not None:
            uidLL = _LogUniqueID.__uidLock
            with uidLL:
                _LogUniqueID.__uidLock = None
        _LogUniqueID.__nextUniqueID = 0

class _LogConfig:
    __slots__ = [ '__bRM' , '__bXM' , '__bDM' , '__bUDM' , '__bVSEM' , '__eLL'  , '__eULL' ]

    __cc        = None
    __bRelMode  = True
    __bXcpMode  = True
    __bDieMode  = True
    __bUDieMode = True
    __bVSEMode  = not __bRelMode
    __logLevel  = _ELogLevel.eError
    __ulogLevel = _ELogLevel.eInfo

    def __init__( self
                , bRelMode_      : bool       =None
                , eLogLevel_     : _ELogLevel =None
                , eUserLogLevel_ : _ELogLevel =None
                , bDieMode_      : bool       =None
                , bUserDieMode_  : bool       =None
                , bXcpMode_      : bool       =None
                , bVSEMode_      : bool       =None):
        self.__bRM   = None
        self.__bXM   = None
        self.__bDM   = None
        self.__eLL   = None
        self.__eULL  = None
        self.__bUDM  = None
        self.__bVSEM = None

        _cc = _LogConfig.__cc

        if _cc is None:
            _LogConfig.__cc = id(self)
            _cc = _LogConfig()
            _cc._RestoreDefault()
            _LogConfig.__cc = _cc

        if not isinstance(_cc, _LogConfig):
            return

        self.__Assign(_cc)

        _lstp = [bRelMode_, eLogLevel_, eUserLogLevel_, bDieMode_, bUserDieMode_, bXcpMode_, bVSEMode_]
        _lstp = [ee for ee in _lstp if ee is not None]

        if len(_lstp) < 1:
            return

        if bRelMode_      is not None: self.__bRM   = bRelMode_
        if bDieMode_      is not None: self.__bDM   = bDieMode_
        if bXcpMode_      is not None: self.__bXM   = bXcpMode_
        if bVSEMode_      is not None: self.__bVSEM = bVSEMode_
        if eLogLevel_     is not None: self.__eLL   = eLogLevel_
        if bUserDieMode_  is not None: self.__bUDM  = bUserDieMode_
        if eUserLogLevel_ is not None: self.__eULL  = eUserLogLevel_

        _cc.__Assign(self)

    def __str__(self):
        return self.ToString()

    @property
    def isReleaseModeEnabled(self):
        return self.__bRM

    @property
    def isExceptionModeEnabled(self):
        return self.__bXM

    @property
    def isVSystemExistEnabled(self):
        return self.__bVSEM

    @property
    def isDieModeEnabled(self):
        return self.__bDM

    @property
    def isUserDieModeEnabled(self):
        return self.__bUDM

    @property
    def logLevel(self):
        return self.__eLL

    @property
    def userLogLevel(self):
        return self.__eULL

    def ToString(self):
        return _CommonDefines._STR_EMPTY

    def CleanUp(self):
        if self != _LogConfig.__cc:
            self.__bRM   = None
            self.__bXM   = None
            self.__bDM   = None
            self.__eLL   = None
            self.__eULL  = None
            self.__bUDM  = None
            self.__bVSEM = None

    @staticmethod
    def _DepInjection( dinjCmd_       : _EDepInjCmd
                     , bRelMode_      =None
                     , eLogLevel_     =None
                     , eUserLogLevel_ =None
                     , bDieMode_      =None
                     , bXcpMode_      =None
                     , bVSEMode_      =None):
        if bRelMode_ is None:
            _logCfg = _LogConfig()
            _logCfg.CleanUp()
        else:
            _logCfg = _LogConfig( bRelMode_=bRelMode_
                                , eLogLevel_=eLogLevel_
                                , eUserLogLevel_=eUserLogLevel_
                                , bDieMode_=bDieMode_
                                , bXcpMode_=bXcpMode_
                                , bVSEMode_=bVSEMode_)
            _logCfg.CleanUp()

    def _RestoreDefault(self):
        self.__bRM   = _LogConfig.__bRelMode
        self.__bXM   = _LogConfig.__bXcpMode
        self.__bDM   = _LogConfig.__bDieMode
        self.__eLL   = _LogConfig.__logLevel
        self.__eULL  = _LogConfig.__ulogLevel
        self.__bUDM  = _LogConfig.__bUDieMode
        self.__bVSEM = _LogConfig.__bVSEMode

        _cc = _LogConfig.__cc
        if isinstance(_cc, _LogConfig) and self != _cc:
            _cc.__Assign(self)

    def __Assign(self, rhs_):
        self.__bRM   = rhs_.__bRM
        self.__bXM   = rhs_.__bXM
        self.__bDM   = rhs_.__bDM
        self.__eLL   = rhs_.__eLL
        self.__eULL  = rhs_.__eULL
        self.__bUDM  = rhs_.__bUDM
        self.__bVSEM = rhs_.__bVSEM

class _LogUtil:
    @staticmethod
    def GetInvalidUniqueID():
        return -1

    @staticmethod
    def GetLogTimestamp(tstamp_ : _PyDateTime =None, bUS_=False) -> str:
        if tstamp_ is None:
            if _PyDateTime.__name__ not in sys.modules:
                return _FwTDbEngine.GetText(_EFwTextID.eTimeUtil_GetTimeStamp_FmrStr_01)
            tstamp_ = _PyDateTime.now()

        tstamp_ = tstamp_.isoformat(timespec='milliseconds')
        return tstamp_[tstamp_.index('T')+1:]

    @staticmethod
    def GetLogTypeGroup(logType_):
        if logType_ is None:
            return None

        _absVal = logType_._absValue
        if _absVal >= _ELogType.FTL.value:
            res = _ELogType.FTL
        elif _absVal >= _ELogType.ERR.value:
            res = _ELogType.ERR
        elif _absVal >= _ELogType.WNG.value:
            res = _ELogType.WNG
        else:
            res = _ELogType(_absVal)
        return res

    @staticmethod
    def GetEnabledLogTypeGroup(logType_ : _ELogType, eCurLL_ : _ELogLevel):
        _ltg = _LogUtil.GetLogTypeGroup(logType_)
        if _ltg is None:
            return False

        _bEnabled  = _ltg.value >= _ELogType.FTL.value  and eCurLL_       == _ELogLevel.eFatal
        _bEnabled |= _ltg.value >= _ELogType.ERR.value  and eCurLL_       == _ELogLevel.eError
        _bEnabled |= _ltg.value >= _ELogType.WNG.value  and eCurLL_       == _ELogLevel.eWarning
        _bEnabled |= _ltg.value >= _ELogType.KPI.value  and eCurLL_       == _ELogLevel.eKPI
        _bEnabled |= _ltg.value >= _ELogType.INF.value  and eCurLL_       == _ELogLevel.eInfo
        _bEnabled |= _ltg.value >= _ELogType.DBG.value  and eCurLL_       == _ELogLevel.eDebug
        _bEnabled |= _ltg.value >= _ELogType.TRC.value  and eCurLL_       == _ELogLevel.eTrace
        _bEnabled |= _ltg.value == _ELogType.FREE.value and eCurLL_.value  > _ELogLevel.eWarning.value
        return _ltg if _bEnabled else None

    @staticmethod
    def _GetFormattedTraceback():
        res = traceback.format_exc()
        if res is not None:
            res = res.split(_CommonDefines._CHAR_SIGN_LF)
            res = f'{_CommonDefines._CHAR_SIGN_LF}{_CommonDefines._CHAR_SIGN_TAB}'.join(res)
            res = _CommonDefines._CHAR_SIGN_TAB + res
        return res

    @staticmethod
    def _RaiseException(xx_):
        if xx_ is not None:
            raise xx_

class _LogErrorCode:
    _RESERVED_FW_FATAL_ERR_CODE_MAX = -1001
    _RESERVED_FW_FATAL_ERR_CODE_MIN = -2999
    _RESERVED_FW_USER_ERR_CODE_MAX  = -3001
    _RESERVED_FW_USER_ERR_CODE_MIN  = -4999
    _REGULAR_FW_ERR_CODE_MAX        = -10001

    @staticmethod
    def IsInvalidErrorCode(errCode_ : int):
        return not (isinstance(errCode_, int) and (errCode_ != _LogErrorCode.GetInvalidErrorCode()))

    @staticmethod
    def IsValidFwErrorCode(errCode_ : int):
        return isinstance(errCode_, int) and (errCode_ < _LogErrorCode.GetInvalidErrorCode())

    @staticmethod
    def IsValidApiErrorCode(errCode_ : int):
        return isinstance(errCode_, int) and (errCode_ > _LogErrorCode.GetInvalidErrorCode())

    @staticmethod
    def IsAnonymousErrorCode(errCode_ : int):
        return isinstance(errCode_, int) and (errCode_ == _LogErrorCode.GetAnonymousErrorCode())

    @staticmethod
    def GetInvalidErrorCode():
        return 0

    @staticmethod
    def GetAnonymousErrorCode():
        return (_PY_MAX_SIZE * -1) - 1
