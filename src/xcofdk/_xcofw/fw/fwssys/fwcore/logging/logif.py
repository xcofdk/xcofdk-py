# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : logif.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from xcofdk._xcofw.fw.fwssys.fwcore.logging            import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logdefines import _ELogType
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logdefines import _LogUtil
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logdefines import _ELogifOperationOption
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logifbase  import _LogIFBase
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes  import _CommonDefines

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine


def _IsReleaseModeEnabled() -> bool:
    if _LogIFBase.GetInstance() is None:
        return vlogif._IsReleaseModeEnabled()
    else:
        return _LogIFBase.GetInstance().isReleaseModeEnabled


def _IsFwDieModeEnabled() -> bool:
    if _LogIFBase.GetInstance() is None:
        return vlogif._IsFwDieModeEnabled()
    else:
        return _LogIFBase.GetInstance().isDieModeEnabled


def _IsFwExceptionModeEnabled() -> bool:
    if _LogIFBase.GetInstance() is None:
        return vlogif._IsFwExceptionModeEnabled()
    else:
        return _LogIFBase.GetInstance().isExceptionModeEnabled


def _IsUserDieModeEnabled() -> bool:
    _ifImpl = _LogIFBase.GetInstance()
    return (_ifImpl is not None) and _ifImpl.isUserDieModeEnabled


def _IsUserExceptionModeEnabled() -> bool:
    _ifImpl = _LogIFBase.GetInstance()
    return (_ifImpl is not None) and _ifImpl.isUserExceptionModeEnabled


def _IsFwTraceEnabled() -> bool:
    if _LogIFBase.GetInstance() is None:
        return vlogif._IsFwTraceEnabled()
    else:
        return _LogIFBase.GetInstance().isFwTraceEnabled


def _IsFwDebugEnabled() -> bool:
    if _LogIFBase.GetInstance() is None:
        return vlogif._IsFwDebugEnabled()
    else:
        return _LogIFBase.GetInstance().isFwDebugEnabled


def _IsFwInfoEnabled() -> bool:
    if _LogIFBase.GetInstance() is None:
        return vlogif._IsFwInfoEnabled()
    else:
        return _LogIFBase.GetInstance().isFwInfoEnabled


def _IsFwKPIEnabled() -> bool:
    if _LogIFBase.GetInstance() is None:
        return vlogif._IsFwKPIEnabled()
    else:
        return _LogIFBase.GetInstance().isFwKPIEnabled


def _IsFwWarningEnabled() -> bool:
    if _LogIFBase.GetInstance() is None:
        return vlogif._IsFwWarningEnabled()
    else:
        return _LogIFBase.GetInstance().isFwWarningEnabled


def _PrintException(anyXcp_):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is None:
        vlogif._PrintException(anyXcp_)
    else:
        _ifImpl._AddLog(_ELogType.FTL, msg_=anyXcp_, eLogifOpOption_=_ELogifOperationOption.ePrintXcpOnly)


def _PrintSummary(bPrintFFL_ =True):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is None:
        vlogif._PrintVSummary()
    else:
        _ifImpl._PrintSummary(bPrintFFL_=bPrintFFL_)


def _GetFormattedTraceback():
    return _LogUtil._GetFormattedTraceback()


def _LogOEC(bFatal_ , errCode_):
    vlogif._LogOEC(bFatal_, errCode_)


def _LogNewline():
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is None:
        vlogif._LogNewline()
    else:
        _ifImpl._AddLog(_ELogType.FREE, msg_=_CommonDefines._CHAR_SIGN_NEWLINE)


def _LogFree(msg_):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is None:
        vlogif._LogFree(msg_)
    else:
        _ifImpl._AddLog(_ELogType.FREE, msg_=msg_)


def _LogTrace(msg_):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is None:
        vlogif._LogTrace(msg_)
    else:
        _ifImpl._AddLog(_ELogType.TRC, msg_=msg_)
def _XLogTrace(msg_):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is None:
        vlogif._XLogTrace(msg_)
    else:
        _ifImpl._AddLog(_ELogType.XTRC, msg_=msg_)


def _LogDebug(msg_):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is None:
        vlogif._LogDebug(msg_)
    else:
        _ifImpl._AddLog(_ELogType.DBG, msg_=msg_)
def _XLogDebug(msg_):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is None:
        vlogif._XLogDebug(msg_)
    else:
        _ifImpl._AddLog(_ELogType.XDBG, msg_=msg_)


def _LogInfo(msg_):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is None:
        vlogif._LogInfo(msg_)
    else:
        _ifImpl._AddLog(_ELogType.INF, msg_=msg_)
def _XLogInfo(msg_):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is None:
        vlogif._XLogInfo(msg_)
    else:
        _ifImpl._AddLog(_ELogType.XINF, msg_=msg_)


def _LogKPI(msg_):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is None:
        vlogif._LogKPI(msg_)
    else:
        _ifImpl._AddLog(_ELogType.KPI, msg_=msg_)


def _LogUrgentWarning(msg_):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is None:
        vlogif._LogWarning(msg_)
    else:
        _ifImpl._AddLog(_ELogType.WNG_URGENT, msg_=msg_)

def _LogWarning(msg_):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is None:
        vlogif._LogWarning(msg_)
    else:
        _ifImpl._AddLog(_ELogType.WNG, msg_=msg_)
def _XLogWarning(msg_):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is None:
        vlogif._XLogWarning(msg_)
    else:
        _ifImpl._AddLog(_ELogType.XWNG, msg_=msg_)


def _LogError(msg_):
    _LogErrorEC(msg_, None, _LogUtil.GetCallstackLevelOffset()+1)
def _LogErrorEC(msg_, errCode_ =None, callstackLevelOffset_ =None):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is None:
        vlogif._LogErrorEC(msg_, errCode_)
    else:
        _ifImpl._AddLog(_ELogType.ERR, msg_=msg_
            , errCode_=errCode_, callstackLevelOffset_=callstackLevelOffset_)
def _XLogError(msg_):
    _XLogErrorEC(msg_, None, _LogUtil.GetCallstackLevelOffset()+1)
def _XLogErrorEC(msg_, errCode_ =None, callstackLevelOffset_ =None):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is None:
        vlogif._XLogErrorEC(msg_, errCode_)
    else:
        _ifImpl._AddLog(_ELogType.XERR, msg_=msg_
            , errCode_=errCode_, callstackLevelOffset_=callstackLevelOffset_)


def _LogNotSupported(msg_):
    _LogNotSupportedEC(msg_, None, _LogUtil.GetCallstackLevelOffset()+1)
def _LogNotSupportedEC(msg_, errCode_ =None, callstackLevelOffset_ =None):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is None:
        vlogif._LogNotSupportedEC(msg_, errCode_)
    else:
        _ifImpl._AddLog(_ELogType.ERR_NOT_SUPPORTED_YET, msg_=msg_
            , errCode_=errCode_, callstackLevelOffset_=callstackLevelOffset_)
def _XLogNotSupported(msg_):
    _XLogNotSupportedEC(msg_, None, _LogUtil.GetCallstackLevelOffset()+1)
def _XLogNotSupportedEC(msg_, errCode_ =None, callstackLevelOffset_ =None):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is None:
        vlogif._XLogNotSupportedEC(msg_, errCode_)
    else:
        _ifImpl._AddLog(_ELogType.XERR_NOT_SUPPORTED_YET, msg_=msg_
            , errCode_=errCode_, callstackLevelOffset_=callstackLevelOffset_)


def _LogFatal(msg_):
    _LogFatalEC(msg_, None, _LogUtil.GetCallstackLevelOffset()+1)
def _LogFatalEC(msg_, errCode_ =None, callstackLevelOffset_ =None):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is None:
        vlogif._LogFatalEC(msg_, errCode_)
    else:
        xx = _ifImpl._AddLog(_ELogType.FTL, msg_=msg_
            , errCode_=errCode_, callstackLevelOffset_=callstackLevelOffset_)
        _LogUtil._RaiseException(xx)
def _XLogFatal(msg_):
    _XLogFatalEC(msg_, None, _LogUtil.GetCallstackLevelOffset()+1)
def _XLogFatalEC(msg_, errCode_ =None, callstackLevelOffset_ =None):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is None:
        vlogif._XLogFatalEC(msg_, errCode_)
    else:
        xx = _ifImpl._AddLog(_ELogType.XFTL, msg_=msg_
            , errCode_=errCode_, callstackLevelOffset_=callstackLevelOffset_)
        _LogUtil._RaiseException(xx)


def _LogBadUse(msg_):
    _LogBadUseEC(msg_, None, _LogUtil.GetCallstackLevelOffset()+1)
def _LogBadUseEC(msg_, errCode_ =None, callstackLevelOffset_ =None):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is None:
        vlogif._LogBadUseEC(msg_, errCode_)
    else:
        xx = _ifImpl._AddLog(_ELogType.FTL_BAD_USE, msg_=msg_
            , errCode_=errCode_, callstackLevelOffset_=callstackLevelOffset_)
        _LogUtil._RaiseException(xx)


def _LogImplError(msg_):
    _LogImplErrorEC(msg_, None, _LogUtil.GetCallstackLevelOffset()+1)
def _LogImplErrorEC(msg_, errCode_ =None, callstackLevelOffset_ =None):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is None:
        vlogif._LogImplErrorEC(msg_, errCode_)
    else:
        xx = _ifImpl._AddLog(_ELogType.FTL_IMPL_ERR, msg_=msg_
            , errCode_=errCode_, callstackLevelOffset_=callstackLevelOffset_)
        _LogUtil._RaiseException(xx)


def _LogNotImplemented(msg_):
    _LogNotImplementedEC(msg_, None, _LogUtil.GetCallstackLevelOffset()+1)
def _LogNotImplementedEC(msg_, errCode_ =None, callstackLevelOffset_ =None):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is None:
        vlogif._LogNotImplementedEC(msg_, errCode_)
    else:
        xx = _ifImpl._AddLog(_ELogType.FTL_NOT_IMPLEMENTED_YET, msg_=msg_
            , errCode_=errCode_, callstackLevelOffset_=callstackLevelOffset_)
        _LogUtil._RaiseException(xx)

def _LogSysError(msg_):
    _LogSysErrorEC(msg_, None, _LogUtil.GetCallstackLevelOffset()+1)
def _LogSysErrorEC(msg_, errCode_ =None, callstackLevelOffset_ =None):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is None:
        vlogif._LogSysErrorEC(msg_, errCode_)
    else:
        xx = _ifImpl._AddLog(_ELogType.FTL_SYS_OP_ERR, msg_=msg_
            , errCode_=errCode_, callstackLevelOffset_=callstackLevelOffset_)
        _LogUtil._RaiseException(xx)


def _LogSysException(msg_, sysOpXcp_, xcpTraceback_):
    _LogSysExceptionEC(msg_, None, sysOpXcp_, xcpTraceback_, _LogUtil.GetCallstackLevelOffset()+1)
def _LogSysExceptionEC(msg_, errCode_, sysOpXcp_, xcpTraceback_, callstackLevelOffset_ =None):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is None:
        if sysOpXcp_ is not None:
            if msg_ is None:
                msg_ = 'sysOpXcp: {}'.format(str(sysOpXcp_))
            else:
                msg_ += '\nsysOpXcp: {}'.format(str(sysOpXcp_))
            if xcpTraceback_ is not None:
                msg_ += '\ntraceback: {}'.format(str(xcpTraceback_))
        vlogif._LogSysExceptionEC(msg_, errCode_)
    else:
        if msg_ is None:
            msg_ = 'Caught system exception'
        xx = _ifImpl._AddLog(_ELogType.FTL_SYS_OP_XCP, msg_=msg_, errCode_=errCode_
            , sysOpXcp_=sysOpXcp_, xcpTraceback_=xcpTraceback_, callstackLevelOffset_=callstackLevelOffset_)


def _XLogSysException(msg_, sysOpXcp_):
    _LogSysExceptionEC(msg_, None, sysOpXcp_, _LogUtil.GetCallstackLevelOffset()+1)
def _XLogSysExceptionEC(msg_, errCode_, sysOpXcp_, callstackLevelOffset_ =None):
    _tb     = _GetFormattedTraceback()
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is None:
        if sysOpXcp_ is not None:
            if msg_ is None:
                msg_ = 'sysOpXcp: {}'.format(str(sysOpXcp_))
            else:
                msg_ += '\nsysOpXcp: {}'.format(str(sysOpXcp_))
            if _tb is not None:
                msg_ += '\ntraceback: {}'.format(str(_tb))
        vlogif._LogSysExceptionEC(msg_, errCode_)
    else:
        if msg_ is None:
            msg_ = 'Caught system exception'
        xx = _ifImpl._AddLog(_ELogType.XFTL_SYS_OP_XCP, msg_=msg_, errCode_=errCode_
            , sysOpXcp_=sysOpXcp_, xcpTraceback_=_tb, callstackLevelOffset_=callstackLevelOffset_)


def _LogUnhandledXcoBaseXcp(xcoBaseXcp_):
    _LogUnhandledXcoBaseXcpEC(xcoBaseXcp_, None, _LogUtil.GetCallstackLevelOffset()+1)
def _LogUnhandledXcoBaseXcpEC(xcoBaseXcp_, errCode_, callstackLevelOffset_=None):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is None:
        vlogif._PrintException(xcoBaseXcp_)
    elif (getattr(xcoBaseXcp_, _FwTDbEngine.GetText(_EFwTextID.ePreDefinedMethod_IsXcoBaseException), None) is None) or not xcoBaseXcp_.isXcoBaseException:
        vlogif._LogBadUse(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LogIF_TextID_001).format(str(xcoBaseXcp_)))
    else:
        xx = _ifImpl._AddLog(_ELogType.FTL_SYS_OP_XCP, msg_=None, errCode_=errCode_, sysOpXcp_=None, xcpTraceback_=None
            , callstackLevelOffset_=callstackLevelOffset_, unhandledXcoBaseXcp_=xcoBaseXcp_)


def _CreateLogFatal(msg_, bDueToExecApiAboort_ =False):
    return _CreateLogFatalEC(msg_, None, bDueToExecApiAboort_, _LogUtil.GetCallstackLevelOffset()+1)
def _CreateLogFatalEC(msg_, errCode_ =None, bDueToExecApiAboort_ =False, callstackLevelOffset_ =None):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is None:
        res = None
        vlogif._LogImplErrorEC(msg_, errCode_)
    else:
        res = _ifImpl._AddLog( _ELogType.FTL, msg_=msg_, errCode_=errCode_, callstackLevelOffset_=callstackLevelOffset_
                             , eLogifOpOption_=_ELogifOperationOption.eCreateLogOnlyDueToExecApiAbort if bDueToExecApiAboort_ else _ELogifOperationOption.eCreateLogOnly)
    return res


def _CreateLogImplError(msg_):
    return _CreateLogImplErrorEC(msg_, None, _LogUtil.GetCallstackLevelOffset()+1)
def _CreateLogImplErrorEC(msg_, errCode_ =None, callstackLevelOffset_ =None):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is None:
        res = None
        vlogif._LogImplErrorEC(msg_, errCode_)
    else:
        res = _ifImpl._AddLog( _ELogType.FTL_IMPL_ERR, msg_=msg_, errCode_=errCode_, callstackLevelOffset_=callstackLevelOffset_
                             , eLogifOpOption_=_ELogifOperationOption.eCreateLogOnly)
    return res


def _GetCurrentXTaskError():
    res, _ifImpl = None, _LogIFBase.GetInstance()
    if _ifImpl is None:
        pass
    else:
        res = _ifImpl._GetCurrentXTaskError()
    return res


def _GetCurrentXTaskErrorEntry(xuErrUniqueID_ : int):
    res, _ifImpl = None, _LogIFBase.GetInstance()
    if _ifImpl is None:
        pass
    else:
        res = _ifImpl._GetCurrentXTaskErrorEntry(xuErrUniqueID_)
    return res


def _ClearCurrentXTaskError() -> bool:
    res, _ifImpl = None, _LogIFBase.GetInstance()
    if _ifImpl is None:
        pass
    else:
        res = _ifImpl._ClearCurrentXTaskError()
    return res


def _SetError(msg_):
    _SetErrorEC(msg_, None, _LogUtil.GetCallstackLevelOffset()+1)
def _SetErrorEC(msg_, errCode_ =None, callstackLevelOffset_ =None):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is not None:
        _ifImpl._AddLog(_ELogType.ERR, msg_=msg_, errCode_=errCode_
            , callstackLevelOffset_=callstackLevelOffset_, eLogifOpOption_=_ELogifOperationOption.eSetErrorOnly)


def _SetNotSupportedError(msg_):
    _SetNotSupportedErrorEC(msg_, None, _LogUtil.GetCallstackLevelOffset()+1)
def _SetNotSupportedErrorEC(msg_, errCode_ =None, callstackLevelOffset_ =None):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is not None:
        _ifImpl._AddLog(_ELogType.ERR_NOT_SUPPORTED_YET, msg_=msg_
            , errCode_=errCode_, callstackLevelOffset_=callstackLevelOffset_, eLogifOpOption_=_ELogifOperationOption.eSetErrorOnly)


def _SetFatalError(msg_):
    _SetFatalErrorEC(msg_, None, _LogUtil.GetCallstackLevelOffset()+1)
def _SetFatalErrorEC(msg_, errCode_ =None, callstackLevelOffset_ =None):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is not None:
        _ifImpl._AddLog(_ELogType.FTL, msg_=msg_, errCode_=errCode_
            , callstackLevelOffset_=callstackLevelOffset_, eLogifOpOption_=_ELogifOperationOption.eSetErrorOnly)


def _SetBadUseError(msg_):
    _SetBadUseErrorEC(msg_, None, _LogUtil.GetCallstackLevelOffset()+1)
def _SetBadUseErrorEC(msg_, errCode_ =None, callstackLevelOffset_ =None):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is not None:
        _ifImpl._AddLog(_ELogType.FTL_BAD_USE, msg_=msg_, errCode_=errCode_
            , callstackLevelOffset_=callstackLevelOffset_, eLogifOpOption_=_ELogifOperationOption.eSetErrorOnly)


def _SetImplError(msg_):
    _SetImplErrorEC(msg_, None, _LogUtil.GetCallstackLevelOffset()+1)
def _SetImplErrorEC(msg_, errCode_ =None, callstackLevelOffset_ =None):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is not None:
        _ifImpl._AddLog(_ELogType.FTL_IMPL_ERR, msg_=msg_, errCode_=errCode_
            , callstackLevelOffset_=callstackLevelOffset_, eLogifOpOption_=_ELogifOperationOption.eSetErrorOnly)


def _SetNotImplementedError(msg_):
    _SetNotImplementedErrorEC(msg_, None, _LogUtil.GetCallstackLevelOffset()+1)
def _SetNotImplementedErrorEC(msg_, errCode_ =None, callstackLevelOffset_ =None):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is not None:
        _ifImpl._AddLog(_ELogType.FTL_NOT_IMPLEMENTED_YET, msg_=msg_, errCode_=errCode_
            , callstackLevelOffset_=callstackLevelOffset_, eLogifOpOption_=_ELogifOperationOption.eSetErrorOnly)

def _SetSysError(msg_):
    _SetSysErrorEC(msg_, None, _LogUtil.GetCallstackLevelOffset()+1)
def _SetSysErrorEC(msg_, errCode_ =None, callstackLevelOffset_ =None):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is not None:
        _ifImpl._AddLog(_ELogType.FTL_SYS_OP_ERR, msg_=msg_, errCode_=errCode_
            , callstackLevelOffset_=callstackLevelOffset_, eLogifOpOption_=_ELogifOperationOption.eSetErrorOnly)


def _SetSysExceptionError(msg_, sysOpXcp_, xcpTraceback_):
    _SetSysExceptionErrorEC(msg_, None, sysOpXcp_, xcpTraceback_, _LogUtil.GetCallstackLevelOffset()+1)
def _SetSysExceptionErrorEC(msg_, errCode_, sysOpXcp_, xcpTraceback_, callstackLevelOffset_ =None):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is not None:
        _ifImpl._AddLog(_ELogType.FTL_SYS_OP_XCP, msg_=msg_, errCode_=errCode_
            , sysOpXcp_=sysOpXcp_, xcpTraceback_=xcpTraceback_, callstackLevelOffset_=callstackLevelOffset_, eLogifOpOption_=_ELogifOperationOption.eSetErrorOnly)


