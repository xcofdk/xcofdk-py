# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xlogifbase.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from _fw.fwssys.fwcore.logging            import logif
from _fw.fwssys.fwcore.logging.logdefines import _LogUtil

def _XIsDieModeEnabled():
    return logif._IsUserDieModeEnabled()

def _XIsExceptionModeEnabled():
    return logif._IsUserExceptionModeEnabled()

def _XLogTrace(msg_):
    logif._XLogTrace(msg_)

def _XLogDebug(msg_):
    logif._XLogDebug(msg_)

def _XLogInfo(msg_):
    logif._XLogInfo(msg_, bAC_=True)

def _XLogWarning(msg_):
    logif._XLogWarning(msg_, bAC_=True)

def _XLogError(msg_):
    logif._XLogErrorEC(None, msg_, bECSM_=True)
def _XLogErrorEC(msg_, errCode_ =None):
    logif._XLogErrorEC(errCode_, msg_, bECSM_=True)

def _XLogFatal(msg_):
    logif._XLogFatalEC(None, msg_, bECSM_=True)
def _XLogFatalEC(msg_, errCode_ =None):
    logif._XLogFatalEC(errCode_, msg_, bECSM_=True)

def _XLogException(msg_, xcp_):
    logif._XLogSysExceptionEC(None, msg_, xcp_, bECSM_=True)
def _XLogExceptionEC(msg_, errCode_, xcp_):
    logif._XLogSysExceptionEC(errCode_, msg_, xcp_, bECSM_=True)

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
    logif._SetXErrorEC(None, msg_)
def _XSetErrorEC(msg_, errCode_ =None):
    logif._SetXErrorEC(errCode_, msg_)

def _XSetFatalError(msg_):
    logif._SetXFatalErrorEC(None, msg_)
def _XSetFatalErrorEC(msg_, errCode_ =None):
    logif._SetXFatalErrorEC(errCode_, msg_)
