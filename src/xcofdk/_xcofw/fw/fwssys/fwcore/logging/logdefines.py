# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : logdefines.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

import os
import sys
import traceback

from datetime  import datetime as _PyDateTime
from enum      import auto
from enum      import unique
from enum      import IntEnum
from sys       import maxsize as _PY_MAX_SIZE

from threading import current_thread as _GetCurThread
from threading import RLock          as _PyRLock

from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes import _CommonDefines

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine

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

    def Encode(self):
        return self.compactName.lower()

    @staticmethod
    def Decode(logLevelStrCode_ : str):
        res = None
        if not isinstance(logLevelStrCode_, str):
            pass
        else:
            for name, member in _ELogLevel.__members__.items():
                if member.compactName.lower() == logLevelStrCode_.lower():
                    res = _ELogLevel(member.value)
                    break
        return res

@unique
class _ELogType(IntEnum):

    FREE                     =  0  # free logs are 'unformatted' traces
    TRC                      = 10
    DBG                      = 20
    INF                      = 30
    KPI                      = 40
    WNG                      = 50
    WNG_URGENT               = 51
    ERR                      = 60  
    ERR_NOT_SUPPORTED_YET    = 61
    FTL                      = 70  
    FTL_BAD_USE              = 71  
    FTL_IMPL_ERR             = 72  
    FTL_NOT_IMPLEMENTED_YET  = 73  
    FTL_SYS_OP_ERR           = 74  
    FTL_SYS_OP_XCP           = 75  
    FTL_NESTED_ERR           = 76  

    XTRC                     = -1*TRC
    XDBG                     = -1*DBG
    XINF                     = -1*INF
    XKPI                     = -1*KPI         
    XWNG                     = -1*WNG
    XWNG_URGENT              = -1*WNG_URGENT  
    XERR                     = -1*ERR
    XERR_NOT_SUPPORTED_YET   = -1*ERR_NOT_SUPPORTED_YET
    XFTL                     = -1*FTL
    XFTL_SYS_OP_XCP          = -1*FTL_SYS_OP_XCP

    @property
    def compactName(self) -> str:
        _absSelf = _ELogType(self._absoluteValue)
        if   _absSelf == _ELogType.TRC                       : res = _FwTDbEngine.GetText(_EFwTextID.eELogType_TRC)
        elif _absSelf == _ELogType.DBG                       : res = _FwTDbEngine.GetText(_EFwTextID.eELogType_DBG)
        elif _absSelf == _ELogType.INF                       : res = _FwTDbEngine.GetText(_EFwTextID.eELogType_INF)
        elif _absSelf == _ELogType.KPI                       : res = _FwTDbEngine.GetText(_EFwTextID.eELogType_KPI)
        elif _absSelf == _ELogType.WNG                       : res = _FwTDbEngine.GetText(_EFwTextID.eELogType_WNG)
        elif _absSelf == _ELogType.WNG_URGENT                : res = _FwTDbEngine.GetText(_EFwTextID.eELogType_WNG)
        elif _absSelf == _ELogType.ERR                       : res = _FwTDbEngine.GetText(_EFwTextID.eELogType_ERR)
        elif _absSelf == _ELogType.ERR_NOT_SUPPORTED_YET     : res = _FwTDbEngine.GetText(_EFwTextID.eELogType_ERR_NOT_SUPPORTED_YET)
        elif _absSelf == _ELogType.FTL                       : res = _FwTDbEngine.GetText(_EFwTextID.eELogType_FTL)
        elif _absSelf == _ELogType.FTL_BAD_USE               : res = _FwTDbEngine.GetText(_EFwTextID.eELogType_FTL_BAD_USE)
        elif _absSelf == _ELogType.FTL_IMPL_ERR              : res = _FwTDbEngine.GetText(_EFwTextID.eELogType_FTL_IMPL_ERR)
        elif _absSelf == _ELogType.FTL_NOT_IMPLEMENTED_YET   : res = _FwTDbEngine.GetText(_EFwTextID.eELogType_FTL_NOT_IMPLEMENTED_YET)
        elif _absSelf == _ELogType.FTL_SYS_OP_ERR            : res = _FwTDbEngine.GetText(_EFwTextID.eELogType_FTL_SYS_OP_ERR)
        elif _absSelf == _ELogType.FTL_SYS_OP_XCP            : res = _FwTDbEngine.GetText(_EFwTextID.eELogType_FTL_SYS_OP_XCP)
        elif _absSelf == _ELogType.FTL_NESTED_ERR            : res = _FwTDbEngine.GetText(_EFwTextID.eELogType_FTL_NESTED_ERR)
        else:
            res = None
        if res is None:
            res = self.name
        return res

    @property
    def isFwApiLogType(self):
        return self.value < 0

    @property
    def isKPI(self):
        return self._absoluteValue == _ELogType.KPI.value

    @property
    def isWarning(self):
        return _ELogType.WNG.value <= self._absoluteValue <= _ELogType.WNG_URGENT.value

    @property
    def isUrgentWarning(self):
        return self._absoluteValue == _ELogType.WNG_URGENT.value

    @property
    def isNonError(self):
        return self._absoluteValue < _ELogType.ERR.value

    @property
    def isError(self):
        return self._absoluteValue >= _ELogType.ERR.value

    @property
    def isFatal(self):
        return self._absoluteValue >= _ELogType.FTL.value

    @property
    def _absoluteValue(self):
        return -1*self.value if self.value < 0 else self.value

@unique
class _EErrorImpact(IntEnum):
    eNoImpact = 0

    eNoImpactByOperationFailureSetError     = 3824    
    eNoImpactByLogTypePrecedence            = auto()  
    eNoImpactByExistingFatalError           = auto()  
    eNoImpactByExistingUserError            = auto()  
    eNoImpactByOwnerCondition               = auto()  
    eNoImpactBySharedCleanup                = auto()  
    eNoImpactByAutoEnclosedThreadOwnership  = auto()  
    eNoImpactByFrcLinkage                   = auto()  
    eNoImpactByFrcLinkageDueToExecApiReturn = auto()  
    eNoImpactByOtherReason                  = auto()  

    eImpactByDieException                   = auto()  
    eImpactByLogException                   = auto()  
    eImpactByDieError                       = auto()  
    eImpactByFatalError                     = auto()  
    eImpactByFatalErrorDueToExecApiReturn   = auto()  
    eImpactByUserError                      = auto()  

    @property
    def compactName(self):
        return self.name[1:]

    @property
    def hasImpact(self):
        return self.value > _EErrorImpact.eNoImpactByOtherReason.value

    @property
    def hasNoImpact(self):
        return not self.hasImpact

    @property
    def hasNoImpactDueToFrcLinkage(self):
        return (self == _EErrorImpact.eNoImpactByFrcLinkage) or (self == _EErrorImpact.eNoImpactByFrcLinkageDueToExecApiReturn)

    @property
    def isFatalErrorImpactDueToExecutionApiReturn(self):
        return self == _EErrorImpact.eImpactByFatalErrorDueToExecApiReturn

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
            res = res or (self == _EErrorImpact.eImpactByFatalErrorDueToExecApiReturn)
            return res

@unique
class _ELogifOperationOption(IntEnum):
    eDontCare                       = 0
    ePrintXcpOnly                   = 6704
    eStrictEcMatch                  = 6804
    eSetErrorOnly                   = 6904
    eCreateLogOnly                  = auto()
    eCreateLogOnlyDueToExecApiAbort = auto()

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
        return self.value >= _ELogifOperationOption.eCreateLogOnly.value

    @property
    def isCreateLogOnlyDueToExecApiAbort(self):
        return self == _ELogifOperationOption.eCreateLogOnlyDueToExecApiAbort

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
    def _Reset():
        if _LogUniqueID.__uidLock is not None:
            uidLL = _LogUniqueID.__uidLock
            with uidLL:
                _LogUniqueID.__uidLock = None
        _LogUniqueID.__nextUniqueID = 0

class _LogUtil:
    __DEFAULT_CALLSTACK_LEVEL        = 4
    __DEFAULT_CALLSTACK_LEVEL_OFFSET = 3

    __callstackLevelOffset  = __DEFAULT_CALLSTACK_LEVEL_OFFSET

    @staticmethod
    def GetCallstackLevel():
        return _LogUtil.__DEFAULT_CALLSTACK_LEVEL

    @staticmethod
    def GetCallstackLevelOffset():
        return _LogUtil.__callstackLevelOffset

    @staticmethod
    def GetInvalidUniqueID():
        return -1

    @staticmethod
    def GetLogTimestamp(tstamp_ : _PyDateTime =None, microsec_=False) -> str:

        if tstamp_ is None:
            if _PyDateTime.__name__ not in sys.modules:
                res = _FwTDbEngine.GetText(_EFwTextID.eTimeUtil_GetTimeStamp_FmrStr_01)
                if microsec_:
                    res += 3*_CommonDefines._CHAR_SIGN_DASH
                return res

            tstamp_ = _PyDateTime.now()

        if microsec_:
            secfraction = _FwTDbEngine.GetText(_EFwTextID.eTimeUtil_GetTimeStamp_FmrStr_02).format(tstamp_.microsecond)
        else:
            secfraction  = _FwTDbEngine.GetText(_EFwTextID.eTimeUtil_GetTimeStamp_FmrStr_03).format(tstamp_.microsecond // 1000)
        res = tstamp_.strftime(_FwTDbEngine.GetText(_EFwTextID.eTimeUtil_GetTimeStamp_FmrStr_04)) + secfraction
        return res

    @staticmethod
    def GetLogTypeGroup(eLogType_):
        if eLogType_ is None:
            return None

        _absVal = eLogType_._absoluteValue
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
    def GetEnabledLogTypeGroup(eLogType_ : _ELogType, eCurLL_ : _ELogLevel):
        _clr = _LogUtil.GetLogTypeGroup(eLogType_)
        if _clr is None:
            _bEnabled = False
        else:
            _bEnabled  = _clr.value >= _ELogType.FTL.value  and eCurLL_       == _ELogLevel.eFatal
            _bEnabled |= _clr.value >= _ELogType.ERR.value  and eCurLL_       == _ELogLevel.eError
            _bEnabled |= _clr.value >= _ELogType.WNG.value  and eCurLL_       == _ELogLevel.eWarning
            _bEnabled |= _clr.value >= _ELogType.INF.value  and eCurLL_       == _ELogLevel.eInfo
            _bEnabled |= _clr.value >= _ELogType.DBG.value  and eCurLL_       == _ELogLevel.eDebug
            _bEnabled |= _clr.value >= _ELogType.TRC.value  and eCurLL_       == _ELogLevel.eTrace
            _bEnabled |= _clr.value == _ELogType.FREE.value and eCurLL_.value  > _ELogLevel.eWarning.value
        return _clr if _bEnabled else None

    @staticmethod
    def _GetFormattedTraceback():

        res = traceback.format_exc()
        if res is not None:
            res = res.split(_CommonDefines._CHAR_SIGN_NEWLINE)
            res = f'{_CommonDefines._CHAR_SIGN_NEWLINE}{_CommonDefines._CHAR_SIGN_TAB}'.join(res)
            res = _CommonDefines._CHAR_SIGN_TAB + res
        return res

    @staticmethod
    def _RaiseException(xx_):
        if xx_ is not None:
            raise xx_

    @staticmethod
    def _EnableCallstackLevelOffset():
        _LogUtil.__callstackLevelOffset = _LogUtil.__DEFAULT_CALLSTACK_LEVEL_OFFSET

    @staticmethod
    def _DisableCallstackLevelOffset():
        _LogUtil.__callstackLevelOffset = -1

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
