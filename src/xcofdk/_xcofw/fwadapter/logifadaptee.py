#!
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : logifadaptee.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

import logging as _PyLogger
from   typing import Union as _PyUnion

from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes import _CommonDefines
from xcofdk._xcofw.fw.fwssys.fwerrh.fwerrorcodes      import _EFwErrorCode

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine

class _LogifAdapteeImpl:
    _ERR_CODE_FMT_TXT_ID     = _EFwTextID.eMisc_Shared_FmtStr_009
    _LogOEC_FMT_TXT_ID_USER  = _EFwTextID.eMisc_VLogIF_AutoGeneratedUserError
    _LogOEC_FMT_TXT_ID_FATAL = _EFwTextID.eMisc_VLogIF_AutoGeneratedFatalError

    @staticmethod
    def _GetErrorLogText(errCode_ : _PyUnion[_EFwErrorCode, int], msg_ : str =None):
        if isinstance(errCode_, _EFwErrorCode):
            errCode_ = errCode_.toSInt
        if msg_ is None:
            msg_ = _CommonDefines._CHAR_SIGN_DASH
        return _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_009).format(errCode_, msg_)

def _IsReleaseModeEnabled() -> bool:
    return True

def _LogTrace(msg_):
    _PyLogger.debug(msg_)

def _LogDebug(msg_):
    _PyLogger.debug(msg_)

def _LogInfo(msg_):
    _PyLogger.info(msg_)

def _LogWarning(msg_):
    _PyLogger.warning(msg_)

def _LogErrorEC(errCode_, msg_ =None):
    _PyLogger.error(_LogifAdapteeImpl._GetErrorLogText(errCode_, msg_=msg_))

def _LogNotSupportedEC(errCode_, msg_ =None):
    _PyLogger.error(_LogifAdapteeImpl._GetErrorLogText(errCode_, msg_=msg_))

def _LogFatalEC(errCode_, msg_ =None):
    _PyLogger.critical(_LogifAdapteeImpl._GetErrorLogText(errCode_, msg_=msg_))

def _LogBadUseEC(errCode_, msg_ =None):
    _PyLogger.critical(_LogifAdapteeImpl._GetErrorLogText(errCode_, msg_=msg_))

def _LogImplErrorEC(errCode_, msg_ =None):
    _PyLogger.critical(_LogifAdapteeImpl._GetErrorLogText(errCode_, msg_=msg_))

def _LogNotImplementedEC(errCode_, msg_ =None):
    _PyLogger.critical(_LogifAdapteeImpl._GetErrorLogText(errCode_, msg_=msg_))

def _LogSysErrorEC(errCode_, msg_ =None):
    _PyLogger.critical(_LogifAdapteeImpl._GetErrorLogText(errCode_, msg_=msg_))

def _LogOEC(bFatal_ , errCode_):
    _fmtID = _LogifAdapteeImpl._LogOEC_FMT_TXT_ID_FATAL if bFatal_ else _LogifAdapteeImpl._LogOEC_FMT_TXT_ID_USER
    _myMsg = _FwTDbEngine.GetText(_fmtID)
    if _myMsg is not None:
        _myMsg = _myMsg.format(errCode_)
        if bFatal_:
            _PyLogger.critical(_myMsg)
        else:
            _PyLogger.error(_myMsg)
