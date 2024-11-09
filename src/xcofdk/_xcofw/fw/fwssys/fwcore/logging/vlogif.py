# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : vlogif.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from collections import Counter as _Counter

from xcofdk._xcofw.fw.fwssys.fwcore.logging.logdefines   import _ELogLevel
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logdefines   import _ELogType
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logdefines   import _LogUniqueID
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logdefines   import _LogUtil
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logdefines   import _LogErrorCode
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logconfig    import _LoggingConfig
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logconfig    import _LoggingUserConfig
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logconfig    import _LoggingDefaultConfig
from xcofdk._xcofw.fw.fwssys.fwcore.logging.xcoexception import _EXcoXcpType
from xcofdk._xcofw.fw.fwssys.fwcore.logging.xcoexception import _XcoException
from xcofdk._xcofw.fw.fwssys.fwcore.swpfm.sysinfo        import _SystemInfo
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes    import _CommonDefines
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes    import _EColorCode
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes    import _TextStyle
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes    import SyncPrint

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine



class _VFatalError:
    __slots__ = [ '__uid' , '__errMsg' , '__errCode' ]

    def __init__(self, uniqueID_ : int, errMsg_ : str, errCode_ : int =None):
        self.__uid     = uniqueID_
        self.__errMsg  = str(errMsg_)
        self.__errCode = errCode_

    def __str__(self):
        return self.ToString()

    @property
    def uniqueID(self):
        return self.__uid

    @property
    def errorMessage(self):
        return self.__errMsg

    @property
    def errorCode(self):
        return self.__errCode

    def ToString(self):
        if self.__uid is None:
            return None

        res = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_003).format(type(self).__name__, self.__uid)
        if self.__errCode is not None:
            res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_010).format(self.__errCode)
        res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_016).format(self.__errMsg)
        return res

    def CleanUp(self):
        self.__uid     = None
        self.__errMsg  = None
        self.__errCode = None


class _VSystemExit(_XcoException):

    def __init__(self, uniqueID_, xcpMsg_ : str, errCode_ : int =None):
        self.__errCode  = errCode_
        self.__uniqueID = uniqueID_
        super().__init__(_EXcoXcpType.eVSystemExitException, xcpMsg_=xcpMsg_)

    def CleanUp(self):
        if self.__uniqueID is not None:
            self.__errCode  = None
            self.__uniqueID = None
            _XcoException.CleanUp(self)

    @property
    def errorCode(self):
        return self.__errCode

    @staticmethod
    def RaiseException(uniqueID_: int, xcpMsg_ : str, errCode_ : int =None):
        _LogUtil._RaiseException(_VSystemExit(uniqueID_, xcpMsg_, errCode_=errCode_))

    @property
    def _uniqueID(self):
        return self.__uniqueID

    def _ToString(self):
        if self.eExceptionType is None:
            return None
        return '[{}][{}] {}'.format(self.eExceptionType.compactName, self.uniqueID, self.shortMessage)

    def _Clone(self):
        res = None
        if self.eExceptionType is None:
            pass
        else:
            res = _VSystemExit(self.uniqueID, self.message)
            if res.eExceptionType is None:
                res.CleanUp()
                res = None
        return res


class _VLoggingImpl:
    _VANILLA_LOG_PREFIX = None
    __singleton         = None

    def __init__( self):
        self.__ffe             = None
        self.__counter         = _Counter()
        self.__numLogs         = 0
        self.__vsysexitEnabled = None

        for name, member in _ELogType.__members__.items():
            self.__counter[member._absoluteValue] = 0
        _VLoggingImpl.__singleton = self

    @staticmethod
    def _IsFwDieModeEnabled():
        return _LoggingConfig.GetInstance().dieMode

    @staticmethod
    def _IsFwExceptionModeEnabled():
        return _LoggingConfig.GetInstance().exceptionMode

    @staticmethod
    def _IsReleaseModeEnabled():
        return _LoggingConfig.GetInstance().releaseMode

    @staticmethod
    def IsLogLevelEnabled(eLogType_):
        _curLL = _LoggingUserConfig._eUserLogLevel if eLogType_.isFwApiLogType else _LoggingConfig.GetInstance().eLogLevel
        return _LogUtil.GetEnabledLogTypeGroup(eLogType_, _curLL) is not None

    @property
    def firstFatalError(self):
        return self.__ffe

    def CleanUp(self):
        if self.__counter is None:
            return

        self.__counter.clear()
        if self.__ffe is not None:
            self.__ffe.CleanUp()

        self.__ffe             = None
        self.__counter         = None
        self.__numLogs         = None
        self.__vsysexitEnabled = None

    @property
    def _isVSystemExistEnabled(self):
        return _LoggingConfig.GetInstance()._isVSystemExistEnabled if self.__vsysexitEnabled is None else self.__vsysexitEnabled


    @property
    def _counter(self):
        return self.__counter

    @staticmethod
    def _GetInstance(bCreate_ =True):
        if _VLoggingImpl.__singleton is None:
            _VLoggingImpl.__singleton = _VLoggingImpl()
        return _VLoggingImpl.__singleton

    @staticmethod
    def _CleanUp():
        if _VLoggingImpl.__singleton is not None:
            _VLoggingImpl.__singleton.CleanUp()
        _VLoggingImpl.__singleton = None

    def _UpdateCounter(self, eLogTypeGrpID_):
        self.__numLogs += 1
        self.__counter[eLogTypeGrpID_._absoluteValue] += 1

    def _SetFirstFatalError(self, uniqueID_: int, errMsg_ : str, errCode_ : int =None):
        if self.__ffe is None:
            self.__ffe = _VFatalError(uniqueID_, errMsg_, errCode_=errCode_)

    def _SetVSystemExitStatus(self, vsysexitEnabled_: bool):
        self.__vsysexitEnabled = vsysexitEnabled_
        _LoggingDefaultConfig._SetUp(bVSysExitMode_=vsysexitEnabled_)

    def _ClearLogHistory(self):
        res = self.__numLogs
        if self.__counter is not None:
            if self.__ffe is not None:
                self.__ffe.CleanUp()

            self.__counter.clear()
            self.__ffe     = None
            self.__numLogs = 0
        return res


def _IsFwDieModeEnabled():
    return _VLoggingImpl._IsFwDieModeEnabled()

def _IsFwExceptionModeEnabled():
    return _VLoggingImpl._IsFwExceptionModeEnabled()

def _IsReleaseModeEnabled():
    return _VLoggingImpl._IsReleaseModeEnabled()

def _IsFwTraceEnabled():
    return _VLoggingImpl.IsLogLevelEnabled(_ELogLevel.eTrace)

def _IsFwDebugEnabled():
    return _VLoggingImpl.IsLogLevelEnabled(_ELogLevel.eDebug)

def _IsFwInfoEnabled():
    return _VLoggingImpl.IsLogLevelEnabled(_ELogLevel.eInfo)

def _IsFwKPIEnabled():
    return _VLoggingImpl.IsLogLevelEnabled(_ELogLevel.eKPI)

def _IsFwWarningEnabled():
    return _VLoggingImpl.IsLogLevelEnabled(_ELogLevel.eWarning)

def _LogNewline():
    _LogFree(_CommonDefines._CHAR_SIGN_NEWLINE)

def _LogFree(msg_):
    _VPrint(_ELogType.FREE, msg_, None)

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
def _XLogInfo(msg_):
    _VPrint(_ELogType.XINF, msg_, None)

def _LogKPI(msg_):
    _VPrint(_ELogType.KPI, msg_, None)

def _LogWarning(msg_):
    _VPrint(_ELogType.WNG, msg_, None)
def _XLogWarning(msg_):
    _VPrint(_ELogType.XWNG, msg_, None)

def _LogError(msg_):
    _LogErrorEC(msg_)
def _LogErrorEC(msg_, errCode_ =None):
    _VPrint(_ELogType.ERR, msg_, errCode_)
def _XLogError(msg_):
    _XLogErrorEC(msg_)
def _XLogErrorEC(msg_, errCode_ =None):
    _VPrint(_ELogType.XERR, msg_, errCode_)

def _LogNotSupported(msg_):
    _LogNotSupportedEC(msg_)
def _LogNotSupportedEC(msg_, errCode_ =None):
    _VPrint(_ELogType.ERR_NOT_SUPPORTED_YET, msg_, errCode_)
def _XLogNotSupported(msg_):
    _XLogNotSupportedEC(msg_)
def _XLogNotSupportedEC(msg_, errCode_ =None):
    _VPrint(_ELogType.XERR_NOT_SUPPORTED_YET, msg_, errCode_)

def _LogFatal(msg_):
    _LogFatalEC(msg_)
def _LogFatalEC(msg_, errCode_ =None):
    _VPrint(_ELogType.FTL, msg_, errCode_)
def _XLogFatal(msg_):
    _XLogFatalEC(msg_)
def _XLogFatalEC(msg_, errCode_ =None):
    _VPrint(_ELogType.XFTL, msg_, errCode_)

def _LogBadUse(msg_):
    _LogBadUseEC(msg_)
def _LogBadUseEC(msg_, errCode_ =None):
    _VPrint(_ELogType.FTL_BAD_USE, msg_, errCode_)

def _LogImplError(msg_):
    _LogImplErrorEC(msg_)
def _LogImplErrorEC(msg_, errCode_ =None):
    _VPrint(_ELogType.FTL_IMPL_ERR, msg_, errCode_)

def _LogNotImplemented(msg_):
    _LogNotImplementedEC(msg_)
def _LogNotImplementedEC(msg_, errCode_ =None):
    _VPrint(_ELogType.FTL_NOT_IMPLEMENTED_YET, msg_, errCode_)

def _LogSysError(msg_):
    _LogSysErrorEC(msg_)
def _LogSysErrorEC(msg_, errCode_ =None):
    _VPrint(_ELogType.FTL_SYS_OP_ERR, msg_, errCode_)

def _LogSysException(msg_):
    _LogSysExceptionEC(msg_)
def _LogSysExceptionEC(msg_, errCode_ =None):
    _VPrint(_ELogType.FTL_SYS_OP_XCP, msg_, errCode_)

def _PrintException(anyXcp_):
    if anyXcp_ is None:
        pass
    else:
        _myMsg = _FwTDbEngine.GetText(_EFwTextID.eVLogIF_PrintException_FmtStr_01).format(type(anyXcp_).__name__, str(anyXcp_))
        _VPrint(None, _myMsg, None)

def _GetFormattedTraceback():
    return _LogUtil._GetFormattedTraceback()

def _PrintVSummary(bPrint_ =True):
    vinst = _VLoggingImpl._GetInstance(bCreate_=False)
    if (vinst is None) or vinst._IsReleaseModeEnabled():
        return None

    _statMsg  = _FwTDbEngine.GetText(_EFwTextID.eVLogIF_PrintSummary_FmtStr_01) + str(vinst._counter[_ELogType.FTL.value])
    _statMsg += _FwTDbEngine.GetText(_EFwTextID.eVLogIF_PrintSummary_FmtStr_02) + str(vinst._counter[_ELogType.ERR.value])
    _statMsg += _FwTDbEngine.GetText(_EFwTextID.eVLogIF_PrintSummary_FmtStr_03) + str(vinst._counter[_ELogType.WNG.value])
    _statMsg += _FwTDbEngine.GetText(_EFwTextID.eVLogIF_PrintSummary_FmtStr_04) + str(vinst._counter[_ELogType.INF.value])
    _statMsg += _CommonDefines._CHAR_SIGN_RIGHT_PARANTHESIS

    if bPrint_:
        _LESS_THAN_LONG    = 9*_CommonDefines._CHAR_SIGN_LESS_THAN
        _LARGER_THAN_LONG  = 9*_CommonDefines._CHAR_SIGN_LARGER_THAN

        _psMsg  = f'{_CommonDefines._CHAR_SIGN_NEWLINE}{_CommonDefines._CHAR_SIGN_NEWLINE}{_LARGER_THAN_LONG}'
        _psMsg += _FwTDbEngine.GetText(_EFwTextID.eVLogIF_PrintSummary_FmtStr_05)
        _psMsg += f'{_LESS_THAN_LONG}{_CommonDefines._CHAR_SIGN_NEWLINE}'
        _psMsg += f'{_statMsg}{_CommonDefines._CHAR_SIGN_NEWLINE}'
        _psMsg += _LARGER_THAN_LONG
        _psMsg += _FwTDbEngine.GetText(_EFwTextID.eVLogIF_PrintSummary_FmtStr_06)
        _psMsg += f'{_LESS_THAN_LONG}{_CommonDefines._CHAR_SIGN_NEWLINE}'
        SyncPrint.Print(_psMsg)
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
        _myMsg = _myMsg.format(errCode_)
        if bFatal_:
            _VPrint(_ELogType.FTL, _myMsg, None, bForce_=True)
        else:
            _VPrint(_ELogType.ERR, _myMsg, None, bForce_=True)

def _SetVSystemExitStatus(vsysexitEnabled_ : bool):
    vinst   = _VLoggingImpl._GetInstance()
    curMode = vinst._isVSystemExistEnabled
    if vsysexitEnabled_ != curMode:
        vinst._SetVSystemExitStatus(vsysexitEnabled_)
        _LogDebug(_FwTDbEngine.GetText(_EFwTextID.eVLogIF_SetVSystemExitStatus).format(str(curMode), str(vsysexitEnabled_)))

def _ClearLogHistory():
    numLogs = _VLoggingImpl._GetInstance()._ClearLogHistory()
    _LogDebug(_FwTDbEngine.GetText(_EFwTextID.eVLogIF_ClearLogHistory).format(numLogs))

def _HighlightText(txt_ : str, eLogType_ : _ELogType):
    if _SystemInfo._IsPlatformWindows():
        return txt_

    _cc = _EColorCode.NONE
    if eLogType_.isError:
        _cc = _EColorCode.RED
    elif eLogType_.isKPI:
        _cc = _EColorCode.BLUE
    elif eLogType_.isWarning:
        _cc = _EColorCode.RED if eLogType_.isUrgentWarning else _EColorCode.YELLOW

    res = txt_
    if _cc.isColor:
        res = _TextStyle.ColorText(txt_, _cc)
    return res

def _VPrint(eLogType_ : _ELogType, msg_, errCode_, bForce_ =False):
    if _VLoggingImpl._VANILLA_LOG_PREFIX is None:
        _VLoggingImpl._VANILLA_LOG_PREFIX = _FwTDbEngine.GetText(_EFwTextID.eMisc_VLogIF_VanillaLogPrefix)

    _bFwApiLog = False if eLogType_ is None else eLogType_.isFwApiLogType

    if _IsReleaseModeEnabled() and not _bFwApiLog:
        if not bForce_:
            return
    if eLogType_ is None:
        if not isinstance(msg_, str):
            msg_ = str(msg_)
        msg = _VLoggingImpl._VANILLA_LOG_PREFIX + msg_
        SyncPrint.Print(msg)
        return
    elif not _VLoggingImpl.IsLogLevelEnabled(eLogType_):
        return

    _eLogTypeGrpID = _LogUtil.GetLogTypeGroup(eLogType_)
    _bFatal        = _eLogTypeGrpID == _ELogType.FTL

    if eLogType_ == _ELogType.FREE:
        _outMsg = _CommonDefines._STR_EMPTY
    else:
        _ts      = _LogUtil.GetLogTimestamp()
        _grpName = _ELogType(_eLogTypeGrpID.value*-1).name if _bFwApiLog else _eLogTypeGrpID.compactName

        if not _bFwApiLog:
            _outMsg = _FwTDbEngine.GetText(_EFwTextID.eVLogIF_VPrint_FmtStr_01).format(_ts, _grpName)
            if eLogType_ != _eLogTypeGrpID:
                _outMsg += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_010).format(eLogType_.name)
        else:
            _outMsg = _FwTDbEngine.GetText(_EFwTextID.eVLogIF_VPrint_FmtStr_03).format(_ts, _grpName)

    _myMsg   = None
    _bIgnore = None

    _myMsg = msg_
    if _myMsg is not None:
        if not isinstance(_myMsg, str):
            _myMsg = str(_myMsg)
    if errCode_ is not None:
        if not _LogErrorCode.IsAnonymousErrorCode(errCode_):
            if errCode_!= _LogErrorCode.GetInvalidErrorCode():
                _myTxt = _FwTDbEngine.GetText(_EFwTextID.eVLogIF_VPrint_FmtStr_02).format(str(errCode_))
                if _myMsg is None:
                    _myMsg = _myTxt
                else:
                    _myMsg = f'{_myTxt} {_myMsg}'

    if _myMsg is None:
        pass
    elif len(_outMsg) == 0:
        _outMsg = _myMsg
    else:
        _outMsg += _CommonDefines._CHAR_SIGN_SPACE + _myMsg

    _uid     = None
    _endLine = None

    if eLogType_ == _ELogType.FREE:
        if not _bFwApiLog:
            _outMsg = _VLoggingImpl._VANILLA_LOG_PREFIX + _outMsg
        _endLine = ''
    elif not _bFwApiLog:
        _uid    = _GetNextUniqueID()
        _outMsg = _FwTDbEngine.GetText(_EFwTextID.eVLogIF_VPrint_FmtStr_04).format(_VLoggingImpl._VANILLA_LOG_PREFIX, _uid, _outMsg)

    _outMsg = _HighlightText(_outMsg, _eLogTypeGrpID)

    vinst = _VLoggingImpl._GetInstance()
    vinst._UpdateCounter(_eLogTypeGrpID)

    SyncPrint.Print(_outMsg, endLine_=_endLine)

    if _bFatal:
        if vinst.firstFatalError is None:
            vinst._SetFirstFatalError(_uid, _outMsg, errCode_=errCode_)

        if not _bFwApiLog:
            if vinst._isVSystemExistEnabled:
                _VSystemExit.RaiseException(_uid, _outMsg, errCode_=errCode_)
