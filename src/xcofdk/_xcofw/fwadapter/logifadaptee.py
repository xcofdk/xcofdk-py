#!
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : logifadaptee.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


import logging as _PyLogger

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine


def _LogTrace(msg_):
    _PyLogger.debug(msg_)

def _LogDebug(msg_):
    _PyLogger.debug(msg_)

def _LogInfo(msg_):
    _PyLogger.info(msg_)

def _LogWarning(msg_):
    _PyLogger.warning(msg_)

def _LogError(msg_ =None):
    _PyLogger.error(msg_)

def _LogNotSupported(msg_ =None):
    _PyLogger.error(msg_)

def _LogFatal(msg_ =None):
    _PyLogger.critical(msg_)

def _LogBadUse(msg_ =None):
    _PyLogger.critical(msg_)

def _LogImplError(msg_ =None):
    _PyLogger.critical(msg_)

def _LogNotImplemented(msg_ =None):
    _PyLogger.critical(msg_)

def _LogSysError(msg_ =None):
    _PyLogger.critical(msg_)

def _LogOEC(bFatal_ , errCode_):
    _fmtID = _EFwTextID.eMisc_VLogIF_AutoGeneratedFatalError if bFatal_ else _EFwTextID.eMisc_VLogIF_AutoGeneratedUserError
    _myMsg = _FwTDbEngine.GetText(_fmtID)
    if _myMsg is not None:
        _myMsg = _myMsg.format(errCode_)
        if bFatal_:
            _PyLogger.critical(_myMsg)
        else:
            _PyLogger.error(_myMsg)
