# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : logif.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from _fw.fwssys.fwcore.logging            import vlogif
from _fw.fwssys.fwcore.logging.logdefines import _ELogType
from _fw.fwssys.fwcore.logging.logdefines import _LogUtil
from _fw.fwssys.fwcore.logging.logdefines import _ELogifOperationOption
from _fw.fwssys.fwcore.logging.alogmgr    import _AbsLogMgr
from _fw.fwssys.fwerrh.fwerrorcodes       import _EFwErrorCode

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

def _IsReleaseModeEnabled() -> bool:
    if _AbsLogMgr.GetInstance() is None:
        return vlogif._IsReleaseModeEnabled()
    else:
        return _AbsLogMgr.GetInstance().isReleaseModeEnabled

def _IsFwDieModeEnabled() -> bool:
    if _AbsLogMgr.GetInstance() is None:
        return vlogif._IsFwDieModeEnabled()
    else:
        return _AbsLogMgr.GetInstance().isDieModeEnabled

def _IsFwExceptionModeEnabled() -> bool:
    if _AbsLogMgr.GetInstance() is None:
        return vlogif._IsFwExceptionModeEnabled()
    else:
        return _AbsLogMgr.GetInstance().isExceptionModeEnabled

def _IsUserDieModeEnabled() -> bool:
    _lm = _AbsLogMgr.GetInstance()
    return (_lm is not None) and _lm.isUserDieModeEnabled

def _IsUserExceptionModeEnabled() -> bool:
    _lm = _AbsLogMgr.GetInstance()
    return (_lm is not None) and _lm.isUserExceptionModeEnabled

def _PrintException(anyXcp_):
    _lm = _AbsLogMgr.GetInstance()
    if _lm is None:
        vlogif._PrintException(anyXcp_)
    else:
        _lm._AddLog(_ELogType.FTL, msg_=anyXcp_, logifOpOption_=_ELogifOperationOption.ePrintXcpOnly)

def _PrintSummary():
    _lm = _AbsLogMgr.GetInstance()
    if _lm is None:
        vlogif._PrintVSummary()
    else:
        _lm._PrintSummary()

def _GetFormattedTraceback():
    return _LogUtil._GetFormattedTraceback()

def _LogOEC(bFatal_ , errCode_):
    vlogif._LogOEC(bFatal_, errCode_)

def _XLogTrace(msg_):
    _lm = _AbsLogMgr.GetInstance()
    if _lm is None:
        vlogif._XLogTrace(msg_)
    else:
        _lm._AddLog(_ELogType.XTRC, msg_=msg_)

def _XLogDebug(msg_):
    _lm = _AbsLogMgr.GetInstance()
    if _lm is None:
        vlogif._XLogDebug(msg_)
    else:
        _lm._AddLog(_ELogType.XDBG, msg_=msg_)

def _LogInfo(msg_):
    _lm = _AbsLogMgr.GetInstance()
    if _lm is None:
        vlogif._LogInfo(msg_)
    else:
        _lm._AddLog(_ELogType.INF, msg_=msg_)
def _XLogInfo(msg_, bAC_ =False):
    _lm = _AbsLogMgr.GetInstance()
    if _lm is None:
        vlogif._XLogInfo(msg_, bAC_=bAC_)
    else:
        _lt = _ELogType.INF if not (bAC_ or not vlogif._VLoggingImpl._IsSilentFwLogLevel()) else _ELogType.XINF
        _lm._AddLog(_ELogType.XINF, msg_=msg_)

def _LogKPI(msg_):
    _lm = _AbsLogMgr.GetInstance()
    if _lm is None:
        vlogif._LogKPI(msg_)
    else:
        _lm._AddLog(_ELogType.KPI, msg_=msg_)

def _LogUrgentWarning(msg_):
    _lm = _AbsLogMgr.GetInstance()
    if _lm is None:
        vlogif._LogUrgentWarning(msg_)
    else:
        _lm._AddLog(_ELogType.WNG_URGENT, msg_=msg_)
def _LogWarning(msg_):
    _lm = _AbsLogMgr.GetInstance()
    if _lm is None:
        vlogif._LogWarning(msg_)
    else:
        _lm._AddLog(_ELogType.WNG, msg_=msg_)
def _XLogUrgentWarning(msg_):
    _lm = _AbsLogMgr.GetInstance()
    if _lm is None:
        vlogif._XLogUrgentWarning(msg_)
    else:
        _lm._AddLog(_ELogType.WNG_URGENT, msg_=msg_)
def _XLogWarning(msg_, bAC_ =False):
    _lm = _AbsLogMgr.GetInstance()
    if _lm is None:
        vlogif._XLogWarning(msg_, bAC_=bAC_)
    else:
        _lt = _ELogType.WNG if not (bAC_ or not vlogif._VLoggingImpl._IsSilentFwLogLevel()) else _ELogType.XWNG
        _lm._AddLog(_lt, msg_=msg_)

def _LogErrorEC(errCode_, msg_ =None):
    _lm = _AbsLogMgr.GetInstance()
    if _lm is None:
        vlogif._LogErrorEC(errCode_, msg_)
    else:
        _lm._AddLog(_ELogType.ERR, msg_=msg_, errCode_=errCode_)
def _XLogErrorEC(errCode_, msg_ =None, bECSM_ =False):
    _lm = _AbsLogMgr.GetInstance()
    if _lm is None:
        vlogif._XLogErrorEC(errCode_, msg_, bECSM_=bECSM_)
    else:
        _eOpt = _ELogifOperationOption.eStrictEcMatch if bECSM_ else None
        _lm._AddLog(_ELogType.XERR, msg_=msg_, errCode_=errCode_, logifOpOption_=_eOpt)

def _LogNotSupportedEC(errCode_, msg_ =None):
    _lm = _AbsLogMgr.GetInstance()
    if _lm is None:
        vlogif._LogNotSupportedEC(errCode_, msg_)
    else:
        _lm._AddLog(_ELogType.ERR_NSY, msg_=msg_, errCode_=errCode_)
def _XLogNotSupportedEC(errCode_, msg_ =None):
    _lm = _AbsLogMgr.GetInstance()
    if _lm is None:
        vlogif._XLogNotSupportedEC(errCode_, msg_)
    else:
        _lm._AddLog(_ELogType.XERR_NSY, msg_=msg_, errCode_=errCode_)

def _LogFatalEC(errCode_, msg_ =None):
    _lm = _AbsLogMgr.GetInstance()
    if _lm is None:
        vlogif._LogFatalEC(errCode_, msg_)
    else:
        xx = _lm._AddLog(_ELogType.FTL, msg_=msg_, errCode_=errCode_)
        _LogUtil._RaiseException(xx)
def _XLogFatalEC(errCode_, msg_ =None, bECSM_ =False):
    _lm = _AbsLogMgr.GetInstance()
    if _lm is None:
        vlogif._XLogFatalEC(errCode_, msg_, bECSM_=bECSM_)
    else:
        _eOpt = _ELogifOperationOption.eStrictEcMatch if bECSM_ else None
        xx = _lm._AddLog(_ELogType.XFTL, msg_=msg_, errCode_=errCode_, logifOpOption_=_eOpt)
        _LogUtil._RaiseException(xx)

def _LogBadUseEC(errCode_, msg_ =None):
    _lm = _AbsLogMgr.GetInstance()
    if _lm is None:
        vlogif._LogBadUseEC(errCode_, msg_)
    else:
        xx = _lm._AddLog(_ELogType.FTL_BU, msg_=msg_, errCode_=errCode_)
        _LogUtil._RaiseException(xx)

def _LogImplErrorEC(errCode_, msg_ =None):
    _lm = _AbsLogMgr.GetInstance()
    if _lm is None:
        vlogif._LogImplErrorEC(errCode_, msg_)
    else:
        xx = _lm._AddLog(_ELogType.FTL_IE, msg_=msg_, errCode_=errCode_)
        _LogUtil._RaiseException(xx)

def _LogNotImplementedEC(errCode_, msg_ =None):
    _lm = _AbsLogMgr.GetInstance()
    if _lm is None:
        vlogif._LogNotImplementedEC(errCode_, msg_)
    else:
        xx = _lm._AddLog(_ELogType.FTL_NIY, msg_=msg_, errCode_=errCode_)
        _LogUtil._RaiseException(xx)

def _LogSysErrorEC(errCode_, msg_ =None):
    _lm = _AbsLogMgr.GetInstance()
    if _lm is None:
        vlogif._LogSysErrorEC(errCode_, msg_)
    else:
        xx = _lm._AddLog(_ELogType.FTL_SOE, msg_=msg_, errCode_=errCode_)
        _LogUtil._RaiseException(xx)

def _LogSysExceptionEC(errCode_, msg_, sysOpXcp_, xcpTraceback_):
    _lm = _AbsLogMgr.GetInstance()
    if _lm is None:
        if sysOpXcp_ is not None:
            if msg_ is None:
                msg_ = 'sysOpXcp: {}'.format(str(sysOpXcp_))
            elif sysOpXcp_ is not None:
                msg_ += '\nsysOpXcp: {}'.format(str(sysOpXcp_))
            if xcpTraceback_ is not None:
                msg_ += '\ntraceback: {}'.format(str(xcpTraceback_))
        vlogif._LogSysExceptionEC(errCode_, msg_)
    else:
        if msg_ is None:
            msg_ = 'Caught system exception'
        xx = _lm._AddLog(_ELogType.FTL_SOX, msg_=msg_, errCode_=errCode_, sysOpXcp_=sysOpXcp_, xcpTraceback_=xcpTraceback_)

def _XLogSysExceptionEC(errCode_, msg_, sysOpXcp_, bECSM_ =False):
    _tb     = _GetFormattedTraceback()
    _lm = _AbsLogMgr.GetInstance()
    if _lm is None:
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
        _opt = _ELogifOperationOption.eStrictEcMatch if bECSM_ else None
        xx   = _lm._AddLog(_ELogType.XFTL_SOX, msg_=msg_, errCode_=errCode_, sysOpXcp_=sysOpXcp_, xcpTraceback_=_tb, logifOpOption_=_opt)

def _LogUnhandledXcoBaseXcpEC(errCode_, xcoBaseXcp_):
    _lm = _AbsLogMgr.GetInstance()
    if _lm is None:
        vlogif._PrintException(xcoBaseXcp_, bForce_=True)
    elif (getattr(xcoBaseXcp_, _FwTDbEngine.GetText(_EFwTextID.ePreDefinedMethod_IsXcoBaseException), None) is None) or not xcoBaseXcp_.isXcoBaseException:
        vlogif._PrintException(xcoBaseXcp_, bForce_=True)
        vlogif._LogOEC(True, _EFwErrorCode.VFE_00436)
    else:
        xx = _lm._AddLog(_ELogType.FTL_SOX, msg_=None, errCode_=errCode_, sysOpXcp_=None, xcpTraceback_=None, unhXcoBaseXcp_=xcoBaseXcp_)

def _CreateLogFatalEC(bFW_, errCode_, msg_ =None, bDueToExecCmdAbort_ =False):
    _lm = _AbsLogMgr.GetInstance()
    if _lm is None:
        res = None
        vlogif._LogImplErrorEC(errCode_, msg_)
    else:
        _opt = _ELogifOperationOption.eCreateLogOnlyDueToExecCmdAbort if bDueToExecCmdAbort_ else _ELogifOperationOption.eCreateLogOnly
        res  = _lm._AddLog(_ELogType.FTL if bFW_ else _ELogType.XFTL, msg_=msg_, errCode_=errCode_, logifOpOption_=_opt)
    return res

def _CreateLogImplErrorEC(errCode_, msg_ =None):
    _lm = _AbsLogMgr.GetInstance()
    if _lm is None:
        res = None
        vlogif._LogImplErrorEC(errCode_, msg_)
    else:
        res = _lm._AddLog(_ELogType.FTL_IE, msg_=msg_, errCode_=errCode_, logifOpOption_=_ELogifOperationOption.eCreateLogOnly)
    return res

def _GetCurrentXTaskError():
    res, _lm = None, _AbsLogMgr.GetInstance()
    if _lm is None:
        pass
    else:
        res = _lm._GetCurrentXTaskError()
    return res

def _GetCurrentXTaskErrorEntry(xuErrUniqueID_ : int):
    res, _lm = None, _AbsLogMgr.GetInstance()
    if _lm is None:
        pass
    else:
        res = _lm._GetCurrentXTaskErrorEntry(xuErrUniqueID_)
    return res

def _ClearCurrentXTaskError() -> bool:
    res, _lm = None, _AbsLogMgr.GetInstance()
    if _lm is None:
        pass
    else:
        res = _lm._ClearCurrentXTaskError()
    return res

def _SetErrorEC(errCode_, msg_ =None):
    _lm = _AbsLogMgr.GetInstance()
    if _lm is not None:
        _lm._AddLog(_ELogType.ERR, msg_=msg_, errCode_=errCode_, logifOpOption_=_ELogifOperationOption.eSetErrorOnly)
def _SetXErrorEC(errCode_, msg_ =None):
    _lm = _AbsLogMgr.GetInstance()
    if _lm is not None:
        _lm._AddLog(_ELogType.XERR, msg_=msg_, errCode_=errCode_, logifOpOption_=_ELogifOperationOption.eSetErrorOnly)

def _SetNotSupportedErrorEC(errCode_, msg_ =None):
    _lm = _AbsLogMgr.GetInstance()
    if _lm is not None:
        _lm._AddLog(_ELogType.ERR_NSY, msg_=msg_, errCode_=errCode_, logifOpOption_=_ELogifOperationOption.eSetErrorOnly)

def _SetFatalErrorEC(errCode_, msg_ =None):
    _lm = _AbsLogMgr.GetInstance()
    if _lm is not None:
        _lm._AddLog(_ELogType.FTL, msg_=msg_, errCode_=errCode_, logifOpOption_=_ELogifOperationOption.eSetErrorOnly)
def _SetXFatalErrorEC(errCode_, msg_ =None):
    _lm = _AbsLogMgr.GetInstance()
    if _lm is not None:
        _lm._AddLog(_ELogType.XFTL, msg_=msg_, errCode_=errCode_, logifOpOption_=_ELogifOperationOption.eSetErrorOnly)

def _SetBadUseErrorEC(errCode_, msg_ =None):
    _lm = _AbsLogMgr.GetInstance()
    if _lm is not None:
        _lm._AddLog(_ELogType.FTL_BU, msg_=msg_, errCode_=errCode_, logifOpOption_=_ELogifOperationOption.eSetErrorOnly)

def _SetImplErrorEC(errCode_, msg_ =None):
    _lm = _AbsLogMgr.GetInstance()
    if _lm is not None:
        _lm._AddLog(_ELogType.FTL_IE, msg_=msg_, errCode_=errCode_, logifOpOption_=_ELogifOperationOption.eSetErrorOnly)

def _SetNotImplementedErrorEC(errCode_, msg_ =None):
    _lm = _AbsLogMgr.GetInstance()
    if _lm is not None:
        _lm._AddLog(_ELogType.FTL_NIY, msg_=msg_, errCode_=errCode_, logifOpOption_=_ELogifOperationOption.eSetErrorOnly)

def _SetSysErrorEC(errCode_, msg_ =None):
    _lm = _AbsLogMgr.GetInstance()
    if _lm is not None:
        _lm._AddLog(_ELogType.FTL_SOE, msg_=msg_, errCode_=errCode_, logifOpOption_=_ELogifOperationOption.eSetErrorOnly)

def _SetSysExceptionErrorEC(errCode_, msg_, sysOpXcp_, xcpTraceback_):
    _lm = _AbsLogMgr.GetInstance()
    if _lm is not None:
        _lm._AddLog(_ELogType.FTL_SOX, msg_=msg_, errCode_=errCode_, sysOpXcp_=sysOpXcp_, xcpTraceback_=xcpTraceback_, logifOpOption_=_ELogifOperationOption.eSetErrorOnly)

