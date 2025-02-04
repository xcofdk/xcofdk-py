# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xlogifbase.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from xcofdk._xcofw.fw.fwssys.fwcore.logging            import logif
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logdefines import _LogUtil

def _XIsDieModeEnabled():
    return logif._IsUserDieModeEnabled()

def _XIsExceptionModeEnabled():
    return logif._IsUserExceptionModeEnabled()

def _XLogTrace(msg_):
    logif._XLogTrace(msg_)

def _XLogDebug(msg_):
    logif._XLogDebug(msg_)

def _XLogInfo(msg_):
    logif._XLogInfo(msg_)

def _XLogWarning(msg_):
    logif._XLogWarning(msg_)

def _XLogError(msg_):
    _XLogErrorEC(msg_, None, _LogUtil.GetCallstackLevelOffset()+3)
def _XLogErrorEC(msg_, errCode_ =None, callstackLevelOffset_ =None):
    logif._XLogErrorEC(errCode_, msg_, callstackLevelOffset_, bECSM_=True)

def _XLogFatal(msg_):
    _XLogFatalEC(msg_, None, _LogUtil.GetCallstackLevelOffset()+3)
def _XLogFatalEC(msg_, errCode_ =None, callstackLevelOffset_ =None):
    logif._XLogFatalEC(errCode_, msg_, callstackLevelOffset_, bECSM_=True)

def _XLogException(msg_, xcp_):
    _XLogExceptionEC(msg_, None, xcp_, _LogUtil.GetCallstackLevelOffset()+3)
def _XLogExceptionEC(msg_, errCode_, xcp_, callstackLevelOffset_ =None):
    logif._XLogSysExceptionEC(errCode_, msg_, xcp_, callstackLevelOffset_=callstackLevelOffset_, bECSM_=True)

def _XIsErrorFree() -> bool:
    return logif._GetCurrentXTaskError() is None

def _XIsFatalErrorFree() -> bool:
    _curXuErr = logif._GetCurrentXTaskError()
    return True if _curXuErr is None else not _curXuErr.isFatalError

def _XGetCurrentError():
    return logif._GetCurrentXTaskError()

def _XClearCurrentError() -> bool:
    return logif._ClearCurrentXTaskError()

def _XSetError(msg_):
    _XSetErrorEC(msg_, None, _LogUtil.GetCallstackLevelOffset()+3)
def _XSetErrorEC(msg_, errCode_ =None, callstackLevelOffset_ =None):
    logif._SetXErrorEC(errCode_, msg_, callstackLevelOffset_)

def _XSetFatalError(msg_):
    _XSetFatalErrorEC(msg_, None, _LogUtil.GetCallstackLevelOffset()+3)
def _XSetFatalErrorEC(msg_, errCode_ =None, callstackLevelOffset_ =None):
    logif._SetXFatalErrorEC(errCode_, msg_, callstackLevelOffset_)

