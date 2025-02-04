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

from xcofdk._xcofw.fw.fwssys.fwerrh.fwerrorcodes import _EFwErrorCode

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

def _LogErrorEC(errCode_, msg_ =None, callstackLevelOffset_ =None):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is None:
        vlogif._LogErrorEC(errCode_, msg_)
    else:
        _ifImpl._AddLog(_ELogType.ERR, msg_=msg_
            , errCode_=errCode_, callstackLevelOffset_=callstackLevelOffset_)
def _XLogErrorEC(errCode_, msg_ =None, callstackLevelOffset_ =None, bECSM_ =False):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is None:
        vlogif._XLogErrorEC(errCode_, msg_, bECSM_=bECSM_)
    else:
        _eOpt = _ELogifOperationOption.eStrictEcMatch if bECSM_ else None
        _ifImpl._AddLog(_ELogType.XERR, msg_=msg_
            , errCode_=errCode_, callstackLevelOffset_=callstackLevelOffset_, eLogifOpOption_=_eOpt)

def _LogNotSupportedEC(errCode_, msg_ =None, callstackLevelOffset_ =None):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is None:
        vlogif._LogNotSupportedEC(errCode_, msg_)
    else:
        _ifImpl._AddLog(_ELogType.ERR_NOT_SUPPORTED_YET, msg_=msg_
            , errCode_=errCode_, callstackLevelOffset_=callstackLevelOffset_)
def _XLogNotSupportedEC(errCode_, msg_ =None, callstackLevelOffset_ =None):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is None:
        vlogif._XLogNotSupportedEC(errCode_, msg_)
    else:
        _ifImpl._AddLog(_ELogType.XERR_NOT_SUPPORTED_YET, msg_=msg_
            , errCode_=errCode_, callstackLevelOffset_=callstackLevelOffset_)

def _LogFatalEC(errCode_, msg_ =None, callstackLevelOffset_ =None):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is None:
        vlogif._LogFatalEC(errCode_, msg_)
    else:
        xx = _ifImpl._AddLog(_ELogType.FTL, msg_=msg_
            , errCode_=errCode_, callstackLevelOffset_=callstackLevelOffset_)
        _LogUtil._RaiseException(xx)
def _XLogFatalEC(errCode_, msg_ =None, callstackLevelOffset_ =None, bECSM_ =False):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is None:
        vlogif._XLogFatalEC(errCode_, msg_, bECSM_=bECSM_)
    else:
        _eOpt = _ELogifOperationOption.eStrictEcMatch if bECSM_ else None
        xx = _ifImpl._AddLog(_ELogType.XFTL, msg_=msg_
            , errCode_=errCode_, callstackLevelOffset_=callstackLevelOffset_, eLogifOpOption_=_eOpt)
        _LogUtil._RaiseException(xx)

def _LogBadUseEC(errCode_, msg_ =None, callstackLevelOffset_ =None):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is None:
        vlogif._LogBadUseEC(errCode_, msg_)
    else:
        xx = _ifImpl._AddLog(_ELogType.FTL_BAD_USE, msg_=msg_
            , errCode_=errCode_, callstackLevelOffset_=callstackLevelOffset_)
        _LogUtil._RaiseException(xx)

def _LogImplErrorEC(errCode_, msg_ =None, callstackLevelOffset_ =None):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is None:
        vlogif._LogImplErrorEC(errCode_, msg_)
    else:
        xx = _ifImpl._AddLog(_ELogType.FTL_IMPL_ERR, msg_=msg_
            , errCode_=errCode_, callstackLevelOffset_=callstackLevelOffset_)
        _LogUtil._RaiseException(xx)

def _LogNotImplementedEC(errCode_, msg_ =None, callstackLevelOffset_ =None):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is None:
        vlogif._LogNotImplementedEC(errCode_, msg_)
    else:
        xx = _ifImpl._AddLog(_ELogType.FTL_NOT_IMPLEMENTED_YET, msg_=msg_
            , errCode_=errCode_, callstackLevelOffset_=callstackLevelOffset_)
        _LogUtil._RaiseException(xx)

def _LogSysErrorEC(errCode_, msg_ =None, callstackLevelOffset_ =None):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is None:
        vlogif._LogSysErrorEC(errCode_, msg_)
    else:
        xx = _ifImpl._AddLog(_ELogType.FTL_SYS_OP_ERR, msg_=msg_
            , errCode_=errCode_, callstackLevelOffset_=callstackLevelOffset_)
        _LogUtil._RaiseException(xx)

def _LogSysExceptionEC(errCode_, msg_, sysOpXcp_, xcpTraceback_, callstackLevelOffset_ =None):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is None:
        if sysOpXcp_ is not None:
            if msg_ is None:
                msg_ = 'sysOpXcp: {}'.format(str(sysOpXcp_))
            else:
                msg_ += '\nsysOpXcp: {}'.format(str(sysOpXcp_))
            if xcpTraceback_ is not None:
                msg_ += '\ntraceback: {}'.format(str(xcpTraceback_))
        vlogif._LogSysExceptionEC(errCode_, msg_)
    else:
        if msg_ is None:
            msg_ = 'Caught system exception'
        xx = _ifImpl._AddLog(_ELogType.FTL_SYS_OP_XCP, msg_=msg_, errCode_=errCode_
            , sysOpXcp_=sysOpXcp_, xcpTraceback_=xcpTraceback_, callstackLevelOffset_=callstackLevelOffset_)

def _XLogSysExceptionEC(errCode_, msg_, sysOpXcp_, callstackLevelOffset_ =None, bECSM_ =False):
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
        vlogif._LogSysExceptionEC(errCode_, msg_, bECSM_=bECSM_)
    else:
        if msg_ is None:
            msg_ = 'Caught system exception'
        _eOpt = _ELogifOperationOption.eStrictEcMatch if bECSM_ else None
        xx = _ifImpl._AddLog(_ELogType.XFTL_SYS_OP_XCP, msg_=msg_, errCode_=errCode_
            , sysOpXcp_=sysOpXcp_, xcpTraceback_=_tb, callstackLevelOffset_=callstackLevelOffset_, eLogifOpOption_=_eOpt)

def _LogUnhandledXcoBaseXcpEC(errCode_, xcoBaseXcp_, callstackLevelOffset_=None):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is None:
        vlogif._PrintException(xcoBaseXcp_)
    elif (getattr(xcoBaseXcp_, _FwTDbEngine.GetText(_EFwTextID.ePreDefinedMethod_IsXcoBaseException), None) is None) or not xcoBaseXcp_.isXcoBaseException:
        vlogif._LogOEC(True, _EFwErrorCode.VFE_00436)
    else:
        xx = _ifImpl._AddLog(_ELogType.FTL_SYS_OP_XCP, msg_=None, errCode_=errCode_, sysOpXcp_=None, xcpTraceback_=None
            , callstackLevelOffset_=callstackLevelOffset_, unhandledXcoBaseXcp_=xcoBaseXcp_)

def _CreateLogFatalEC(bFW_, errCode_, msg_ =None, bDueToExecApiAboort_ =False, callstackLevelOffset_ =None):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is None:
        res = None
        vlogif._LogImplErrorEC(errCode_, msg_)
    else:
        res = _ifImpl._AddLog( _ELogType.FTL if bFW_ else _ELogType.XFTL, msg_=msg_, errCode_=errCode_, callstackLevelOffset_=callstackLevelOffset_
                             , eLogifOpOption_=_ELogifOperationOption.eCreateLogOnlyDueToExecApiAbort if bDueToExecApiAboort_ else _ELogifOperationOption.eCreateLogOnly)
    return res

def _CreateLogImplErrorEC(errCode_, msg_ =None, callstackLevelOffset_ =None):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is None:
        res = None
        vlogif._LogImplErrorEC(errCode_, msg_)
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

def _SetErrorEC(errCode_, msg_ =None, callstackLevelOffset_ =None):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is not None:
        _ifImpl._AddLog(_ELogType.ERR, msg_=msg_, errCode_=errCode_
            , callstackLevelOffset_=callstackLevelOffset_, eLogifOpOption_=_ELogifOperationOption.eSetErrorOnly)
def _SetXErrorEC(errCode_, msg_ =None, callstackLevelOffset_ =None):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is not None:
        _ifImpl._AddLog(_ELogType.XERR, msg_=msg_, errCode_=errCode_
            , callstackLevelOffset_=callstackLevelOffset_, eLogifOpOption_=_ELogifOperationOption.eSetErrorOnly)

def _SetNotSupportedErrorEC(errCode_, msg_ =None, callstackLevelOffset_ =None):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is not None:
        _ifImpl._AddLog(_ELogType.ERR_NOT_SUPPORTED_YET, msg_=msg_
            , errCode_=errCode_, callstackLevelOffset_=callstackLevelOffset_, eLogifOpOption_=_ELogifOperationOption.eSetErrorOnly)

def _SetFatalErrorEC(errCode_, msg_ =None, callstackLevelOffset_ =None):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is not None:
        _ifImpl._AddLog(_ELogType.FTL, msg_=msg_, errCode_=errCode_
            , callstackLevelOffset_=callstackLevelOffset_, eLogifOpOption_=_ELogifOperationOption.eSetErrorOnly)
def _SetXFatalErrorEC(errCode_, msg_ =None, callstackLevelOffset_ =None):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is not None:
        _ifImpl._AddLog(_ELogType.XFTL, msg_=msg_, errCode_=errCode_
            , callstackLevelOffset_=callstackLevelOffset_, eLogifOpOption_=_ELogifOperationOption.eSetErrorOnly)

def _SetBadUseErrorEC(errCode_, msg_ =None, callstackLevelOffset_ =None):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is not None:
        _ifImpl._AddLog(_ELogType.FTL_BAD_USE, msg_=msg_, errCode_=errCode_
            , callstackLevelOffset_=callstackLevelOffset_, eLogifOpOption_=_ELogifOperationOption.eSetErrorOnly)

def _SetImplErrorEC(errCode_, msg_ =None, callstackLevelOffset_ =None):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is not None:
        _ifImpl._AddLog(_ELogType.FTL_IMPL_ERR, msg_=msg_, errCode_=errCode_
            , callstackLevelOffset_=callstackLevelOffset_, eLogifOpOption_=_ELogifOperationOption.eSetErrorOnly)

def _SetNotImplementedErrorEC(errCode_, msg_ =None, callstackLevelOffset_ =None):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is not None:
        _ifImpl._AddLog(_ELogType.FTL_NOT_IMPLEMENTED_YET, msg_=msg_, errCode_=errCode_
            , callstackLevelOffset_=callstackLevelOffset_, eLogifOpOption_=_ELogifOperationOption.eSetErrorOnly)

def _SetSysErrorEC(errCode_, msg_ =None, callstackLevelOffset_ =None):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is not None:
        _ifImpl._AddLog(_ELogType.FTL_SYS_OP_ERR, msg_=msg_, errCode_=errCode_
            , callstackLevelOffset_=callstackLevelOffset_, eLogifOpOption_=_ELogifOperationOption.eSetErrorOnly)

def _SetSysExceptionErrorEC(errCode_, msg_, sysOpXcp_, xcpTraceback_, callstackLevelOffset_ =None):
    _ifImpl = _LogIFBase.GetInstance()
    if _ifImpl is not None:
        _ifImpl._AddLog(_ELogType.FTL_SYS_OP_XCP, msg_=msg_, errCode_=errCode_
            , sysOpXcp_=sysOpXcp_, xcpTraceback_=xcpTraceback_, callstackLevelOffset_=callstackLevelOffset_, eLogifOpOption_=_ELogifOperationOption.eSetErrorOnly)

