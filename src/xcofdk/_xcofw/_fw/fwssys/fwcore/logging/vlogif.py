# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : vlogif.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from collections import Counter as _PyCounter

from _fw.fwssys.fwcore.logging.logdefines import _ELogType
from _fw.fwssys.fwcore.logging.logdefines import _LogUniqueID
from _fw.fwssys.fwcore.logging.logdefines import _LogUtil
from _fw.fwssys.fwcore.logging.logdefines import _LogErrorCode
from _fw.fwssys.fwcore.logging.logdefines import _LogConfig
from _fw.fwssys.fwcore.logrd.logrecord    import _ELRType
from _fw.fwssys.fwcore.logrd.logrecord    import _EColorCode
from _fw.fwssys.fwcore.logrd.logrdagent   import _LogRDAgent
from _fw.fwssys.fwcore.swpfm.sysinfo      import _SystemInfo
from _fw.fwssys.fwcore.types.commontypes  import _CommonDefines
from _fw.fwssys.fwcore.types.commontypes  import _EDepInjCmd
from _fw.fwssys.fwerrh.fwerrorcodes       import _EFwErrorCode
from _fw.fwssys.fwerrh.logs.xcoexception  import _EXcoXcpType
from _fw.fwssys.fwerrh.logs.xcoexception  import _XcoException

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

def _PutLR(lrec_ : str, color_ : _EColorCode =_EColorCode.NONE, logType_: _ELRType =_ELRType.LR_FREE):
    _LogRDAgent._GetInstance()._PutLR(lrec_, color_=color_, logType_=logType_)

class _VFatalError:
    __slots__ = [ '__u' , '__m' , '__c' ]

    def __init__(self, uniqueID_ : int, errMsg_ : str, errCode_ : int =None):
        self.__c = errCode_
        self.__m = str(errMsg_)
        self.__u = uniqueID_

    def __str__(self):
        return self.ToString()

    @property
    def uniqueID(self):
        return self.__u

    @property
    def errorMessage(self):
        return self.__m

    @property
    def errorCode(self):
        return self.__c

    def ToString(self):
        if self.__u is None:
            return None

        res = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_003).format(type(self).__name__, self.__u)
        if self.__c is not None:
            res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_010).format(self.__c)
        res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_016).format(self.__m)
        return res

    def CleanUp(self):
        self.__c = None
        self.__m = None
        self.__u = None

class _VSystemExit(_XcoException):
    def __init__(self, uniqueID_, xcpMsg_ : str, errCode_ : int =None):
        self.__c = errCode_
        self.__u = uniqueID_
        super().__init__(_EXcoXcpType.eVSystemExitException, xcpMsg_=xcpMsg_)

    def CleanUp(self):
        if self.__u is not None:
            self.__c = None
            self.__u = None
            _XcoException.CleanUp(self)

    @property
    def errorCode(self):
        return self.__c

    @staticmethod
    def RaiseException(uniqueID_: int, xcpMsg_ : str, errCode_ : int =None):
        if _VLoggingImpl._GetInstance()._isVSystemExistEnabled:
            _LogUtil._RaiseException(_VSystemExit(uniqueID_, xcpMsg_, errCode_=errCode_))

    @property
    def _uniqueID(self):
        return self.__u

    def _ToString(self):
        if self.xcpType is None:
            return None
        return '[{}][{}] {}'.format(self.xcpType.compactName, self.uniqueID, self.shortMessage)

    def _Clone(self):
        res = None
        if self.xcpType is not None:
            res = _VSystemExit(self.uniqueID, self.message, self.__c)
            if res.xcpType is None:
                res.CleanUp()
                res = None
        return res

class _VLoggingImpl:
    __slots__ = [ '__bV', '__f', '__c', '__n' , '__cfg' ]

    __sgltn   = None
    _VLOG_PFX = None
    __bFWLLSM = False

    def __init__( self):
        self.__c   = _PyCounter()
        self.__f   = None
        self.__n   = 0
        self.__bV  = None
        self.__cfg = _LogConfig()

        for _n, _m in _ELogType.__members__.items():
            self.__c[_m._absValue] = 0
        _VLoggingImpl.__sgltn = self

    @property
    def firstFatalError(self):
        return self.__f

    def CleanUp(self):
        if self.__c is None:
            return

        self.__c.clear()
        if self.__f is not None:
            self.__f.CleanUp()
        self.__c   = None
        self.__f   = None
        self.__n   = None
        self.__bV  = None
        self.__cfg = None

    @property
    def _isVSystemExistEnabled(self):
        _vinst = _VLoggingImpl._GetInstance()
        return _vinst.__cfg.isVSystemExistEnabled if self.__bV is None else self.__bV

    @property
    def _counter(self):
        return self.__c

    def _UpdateCounter(self, logTypeGrpID_):
        self.__n += 1
        self.__c[logTypeGrpID_._absValue] += 1

    def _SetFirstFatalError(self, uniqueID_: int, errMsg_ : str, errCode_ : int =None):
        if self.__f is None:
            self.__f = _VFatalError(uniqueID_, errMsg_, errCode_=errCode_)

    def _SetVSystemExitStatus(self, vsysexitEnabled_: bool):
        self.__bV = vsysexitEnabled_
        self.__cfg.CleanUp()
        self.__cfg = _LogConfig(bVSEMode_=vsysexitEnabled_)

    def _ClearLogHistory(self):
        res = self.__n
        if self.__c is not None:
            if self.__f is not None:
                self.__f.CleanUp()
            self.__c.clear()
            self.__f = None
            self.__n = 0
        return res

    @staticmethod
    def _IsFwDieModeEnabled():
        _vinst = _VLoggingImpl._GetInstance()
        return _vinst.__cfg.isDieModeEnabled

    @staticmethod
    def _IsFwExceptionModeEnabled():
        _vinst = _VLoggingImpl._GetInstance()
        return _vinst.__cfg.isExceptionModeEnabled

    @staticmethod
    def _IsReleaseModeEnabled():
        _vinst = _VLoggingImpl._GetInstance()
        return _vinst.__cfg.isReleaseModeEnabled

    @staticmethod
    def _IsLogLevelEnabled(logType_):
        if logType_.isUrgentWarning:
            return True
        _vinst = _VLoggingImpl._GetInstance()
        _curLL  = _vinst.__cfg.userLogLevel if logType_.isFwApiLogType else _vinst.__cfg.logLevel
        return _LogUtil.GetEnabledLogTypeGroup(logType_, _curLL) is not None

    @staticmethod
    def _IsSilentFwLogLevel():
        return _VLoggingImpl.__bFWLLSM

    @staticmethod
    def _GetInstance(bCreate_ =True):
        if _VLoggingImpl.__sgltn is None:
            _VLoggingImpl.__sgltn = _VLoggingImpl()
        return _VLoggingImpl.__sgltn

    @staticmethod
    def _DepInjection(dinjCmd_ : _EDepInjCmd, bSM_ : bool):
        if _VLoggingImpl.__sgltn is not None:
            _VLoggingImpl.__sgltn.CleanUp()
        _VLoggingImpl.__sgltn = None
        if dinjCmd_.isInject:
            _VLoggingImpl.__bFWLLSM = bSM_

def _IsFwDieModeEnabled():
    return _VLoggingImpl._IsFwDieModeEnabled()

def _IsFwExceptionModeEnabled():
    return _VLoggingImpl._IsFwExceptionModeEnabled()

def _IsReleaseModeEnabled():
    return _VLoggingImpl._IsReleaseModeEnabled()

def _LogNewline():
    pass

def _LogFree(msg_, bPFX_ =True):
    if msg_ is None:
        msg_ = _CommonDefines._STR_EMPTY
    if bPFX_ and not _IsReleaseModeEnabled():
        msg_ = _VLoggingImpl._VLOG_PFX + msg_
    _PutLR(msg_)

def _LogTrace(msg_):
    _VPrint(_ELogType.TRC, msg_, None)
def _XLogTrace(msg_):
    _VPrint(_ELogType.XTRC, msg_, None)

def _LogDebug(msg_):
    _VPrint(_ELogType.DBG, msg_, None)
def _XLogDebug(msg_):
    _VPrint(_ELogType.XDBG, msg_, None)

def _LogInfo(msg_):
    _VPrint(_ELogType.INF, msg_, None)
def _XLogInfo(msg_, bAC_ =False):
    _lt = _ELogType.INF if not (bAC_ or not _VLoggingImpl._IsSilentFwLogLevel()) else _ELogType.XINF
    _VPrint(_lt, msg_, None)

def _LogKPI(msg_):
    _VPrint(_ELogType.KPI, msg_, None)

def _LogUrgentWarning(msg_):
    _VPrint(_ELogType.WNG_URGENT, msg_, None)
def _LogWarning(msg_):
    _VPrint(_ELogType.WNG, msg_, None)
def _XLogUrgentWarning(msg_):
    _VPrint(_ELogType.XWNG_URGENT, msg_, None)
def _XLogWarning(msg_, bAC_ =False):
    _lt = _ELogType.WNG if not (bAC_ or not _VLoggingImpl._IsSilentFwLogLevel()) else _ELogType.XWNG
    _VPrint(_lt, msg_, None)

def _LogErrorEC(errCode_, msg_ =None):
    if _IsReleaseModeEnabled():
        _LogOEC(False , errCode_)
    else:
        _VPrint(_ELogType.ERR, msg_, errCode_)
def _XLogErrorEC(errCode_, msg_ =None, bECSM_ =False):
    _VPrint(_ELogType.XERR, msg_, errCode_, bECSM_=bECSM_)

def _LogNotSupportedEC(errCode_, msg_ =None):
    if _IsReleaseModeEnabled():
        _LogOEC(False , errCode_)
    else:
        _VPrint(_ELogType.ERR_NSY, msg_, errCode_)
def _XLogNotSupportedEC(errCode_, msg_ =None):
    _VPrint(_ELogType.XERR_NSY, msg_, errCode_)

def _LogFatalEC(errCode_, msg_ =None):
    if _IsReleaseModeEnabled():
        _LogOEC(True , errCode_)
    else:
        _VPrint(_ELogType.FTL, msg_, errCode_)
def _XLogFatalEC(errCode_, msg_ =None, bECSM_ =False):
    _VPrint(_ELogType.XFTL, msg_, errCode_, bECSM_=bECSM_)

def _LogBadUseEC(errCode_, msg_ =None):
    if _IsReleaseModeEnabled():
        _LogOEC(True , errCode_)
    else:
        _VPrint(_ELogType.FTL_BU, msg_, errCode_)

def _LogImplErrorEC(errCode_, msg_ =None):
    if _IsReleaseModeEnabled():
        _LogOEC(True , errCode_)
    else:
        _VPrint(_ELogType.FTL_IE, msg_, errCode_)

def _LogNotImplementedEC(errCode_, msg_ =None):
    if _IsReleaseModeEnabled():
        _LogOEC(True , errCode_)
    else:
        _VPrint(_ELogType.FTL_NIY, msg_, errCode_)

def _LogSysErrorEC(errCode_, msg_ =None):
    if _IsReleaseModeEnabled():
        _LogOEC(True , errCode_)
    else:
        _VPrint(_ELogType.FTL_SOE, msg_, errCode_)

def _LogSysExceptionEC(errCode_, msg_ =None, bECSM_ =False):
    if _IsReleaseModeEnabled():
        _LogOEC(True , errCode_)
    else:
        _VPrint(_ELogType.FTL_SOX, msg_, errCode_, bECSM_=bECSM_)

def _PrintException(anyXcp_, bForce_=False):
    if anyXcp_ is not None:
        _myMsg = _FwTDbEngine.GetText(_EFwTextID.eVLogIF_PrintException_FmtStr_01).format(type(anyXcp_).__name__, str(anyXcp_))
        _VPrint(None, _myMsg, None, bForce_=bForce_)

def _GetFormattedTraceback():
    return _LogUtil._GetFormattedTraceback()

def _PrintVSummary(bPrint_ =True):
    _vinst = _VLoggingImpl._GetInstance(bCreate_=False)
    if (_vinst is None) or _vinst._IsReleaseModeEnabled():
        return None

    _statMsg  = _FwTDbEngine.GetText(_EFwTextID.eVLogIF_PrintSummary_FmtStr_01) + str(_vinst._counter[_ELogType.FTL.value])
    _statMsg += _FwTDbEngine.GetText(_EFwTextID.eVLogIF_PrintSummary_FmtStr_02) + str(_vinst._counter[_ELogType.ERR.value])
    _statMsg += _FwTDbEngine.GetText(_EFwTextID.eVLogIF_PrintSummary_FmtStr_03) + str(_vinst._counter[_ELogType.WNG.value])
    _statMsg += _FwTDbEngine.GetText(_EFwTextID.eVLogIF_PrintSummary_FmtStr_04) + str(_vinst._counter[_ELogType.INF.value])
    _statMsg += _CommonDefines._CHAR_SIGN_RIGHT_PARANTHESIS

    if bPrint_:
        _LESS_THAN_LONG    = 9*_CommonDefines._CHAR_SIGN_LESS_THAN
        _LARGER_THAN_LONG  = 9*_CommonDefines._CHAR_SIGN_LARGER_THAN

        _psMsg  = f'{_CommonDefines._CHAR_SIGN_LF}{_LARGER_THAN_LONG}'
        _psMsg += _FwTDbEngine.GetText(_EFwTextID.eVLogIF_PrintSummary_FmtStr_05)
        _psMsg += f'{_LESS_THAN_LONG}{_CommonDefines._CHAR_SIGN_LF}'
        _psMsg += f'{_statMsg}{_CommonDefines._CHAR_SIGN_LF}'
        _psMsg += _LARGER_THAN_LONG
        _psMsg += _FwTDbEngine.GetText(_EFwTextID.eVLogIF_PrintSummary_FmtStr_06)
        _psMsg += f'{_LESS_THAN_LONG}'
        _PutLR(_psMsg)
    else:
        _psMsg = _statMsg
    return _psMsg

def _GetNextUniqueID():
    return _LogUniqueID._GetNextUniqueID()

def _GetFirstFatalError():
    return _VLoggingImpl._GetInstance().firstFatalError

def _IsVSystemExitEnabled():
    return _VLoggingImpl._GetInstance()._isVSystemExistEnabled

def _LogOEC(bFatal_ , errCode_):
    _fmtID = _EFwTextID.eMisc_VLogIF_AutoGeneratedFatalError if bFatal_ else _EFwTextID.eMisc_VLogIF_AutoGeneratedUserError
    _myMsg = _FwTDbEngine.GetText(_fmtID)
    if _myMsg is not None:
        if isinstance(errCode_, _EFwErrorCode):
            errCode_ = errCode_.toSInt
        _myMsg = _myMsg.format(errCode_)
        if bFatal_:
            _VPrint(_ELogType.FTL, _myMsg, None, bForce_=True)
        else:
            _VPrint(_ELogType.ERR, _myMsg, None, bForce_=True)

def _SetVSystemExitStatus(vsysexitEnabled_ : bool):
    _vinst   = _VLoggingImpl._GetInstance()
    _curMode = _vinst._isVSystemExistEnabled
    if vsysexitEnabled_ != _curMode:
        _vinst._SetVSystemExitStatus(vsysexitEnabled_)

def _ClearLogHistory():
    _VLoggingImpl._GetInstance()._ClearLogHistory()

def _GetColor(logType_ : _ELogType):
    res = _EColorCode.NONE
    if _SystemInfo._IsPlatformWindows():
       pass
    elif logType_.isError:
        res = _EColorCode.RED
    elif logType_.isKPI:
        res = _EColorCode.BLUE
    elif logType_.isWarning:
        res = _EColorCode.RED if logType_.isUrgentWarning else _EColorCode.YELLOW
    return res

def _VPrint(logType_ : _ELogType, msg_, errCode_, bForce_ =False, bECSM_ =False):
    if (logType_ is not None) and logType_.isFree:
        _LogFree(msg_)
        return

    _bRelMode = _IsReleaseModeEnabled()

    if _VLoggingImpl._VLOG_PFX is None:
        _VLoggingImpl._VLOG_PFX = _FwTDbEngine.GetText(_EFwTextID.eMisc_VLogIF_VanillaLogPrefix)
    _logPrfx = _VLoggingImpl._VLOG_PFX

    _bFwApiLog  = False if logType_ is None else logType_.isFwApiLogType
    _bUrgentWng = False if logType_ is None else logType_.isUrgentWarning

    if _bRelMode and not _bFwApiLog:
        if not (bForce_ or _bUrgentWng):
            return

    if logType_ is None:
        if not isinstance(msg_, str):
            msg_ = str(msg_)
        if not _bRelMode:
            msg_ = _logPrfx + msg_
        _PutLR(msg_)
        return

    if not _VLoggingImpl._IsLogLevelEnabled(logType_):
        return

    _ltg = _LogUtil.GetLogTypeGroup(logType_)

    if msg_ is None:
        msg_ = _CommonDefines._CHAR_SIGN_DASH

    if errCode_ is not None:
        if isinstance(errCode_, _EFwErrorCode):
            errCode_ = errCode_.toSInt

        if _LogErrorCode.IsAnonymousErrorCode(errCode_):
            errCode_ = None
        elif _LogErrorCode.IsInvalidErrorCode(errCode_):
            _LogWarning(_FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_Logging_001).format(str(errCode_)))
            errCode_ = None
        elif logType_.isFwApiLogType:
            if not _LogErrorCode.IsValidApiErrorCode(errCode_):
                if bECSM_:
                    _LogWarning(_FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_Logging_002).format(errCode_))
        elif not _LogErrorCode.IsValidFwErrorCode(errCode_):
            _LogWarning(_FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_Logging_003).format(errCode_))

    _grpName = _ELogType(_ltg.value*-1).name if _bFwApiLog else _ltg.compactName
    if errCode_ is not None:
        _grpName = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_011).format(_grpName, errCode_)

    _ts = _LogUtil.GetLogTimestamp()
    if not _bFwApiLog:
        _outMsg = _FwTDbEngine.GetText(_EFwTextID.eVLogIF_VPrint_FmtStr_01).format(_ts, _grpName)
        if logType_ != _ltg:
            _outMsg += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_010).format(logType_.name)
    else:
        _outMsg = _FwTDbEngine.GetText(_EFwTextID.eVLogIF_VPrint_FmtStr_03).format(_ts, _grpName)

    _myMsg   = None
    _bIgnore = None

    _myMsg = msg_
    if _myMsg is not None:
        if not isinstance(_myMsg, str):
            _myMsg = str(_myMsg)

    if len(_outMsg) == 0:
        _outMsg = _myMsg
    else:
        _outMsg += _CommonDefines._CHAR_SIGN_SPACE + _myMsg

    _uid = None
    if not _bFwApiLog:
        _uid    = _GetNextUniqueID()
        _outMsg = _FwTDbEngine.GetText(_EFwTextID.eVLogIF_VPrint_FmtStr_04).format(_CommonDefines._STR_EMPTY if _bRelMode else _logPrfx, _uid, _outMsg)

    _vinst = _VLoggingImpl._GetInstance()
    _vinst._UpdateCounter(_ltg)
    _PutLR(_outMsg, color_=_GetColor(logType_))

    if _ltg.isFatal:
        if _vinst.firstFatalError is None:
            _vinst._SetFirstFatalError(_uid, _outMsg, errCode_=errCode_)

        if not _bFwApiLog:
            if _vinst._isVSystemExistEnabled:
                _VSystemExit.RaiseException(_uid, _outMsg, errCode_=errCode_)

