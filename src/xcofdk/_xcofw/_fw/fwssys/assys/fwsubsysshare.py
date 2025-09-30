# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwsubsysshare.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from threading import RLock as _PyRLock

from _fw.fwssys.fwcore.logging             import logif
from _fw.fwssys.fwcore.logging             import vlogif
from _fw.fwssys.fwcore.config.fwcfgdefines import _ESubSysID
from _fw.fwssys.fwcore.types.commontypes   import _CommonDefines
from _fw.fwssys.fwcore.types.commontypes   import _EDepInjCmd
from _fw.fwssys.fwerrh.fwerrorcodes        import _EFwErrorCode
from _fwa.fwrtecfg.fwrteconfig             import _FwRteConfig
from _fwa.fwsubsyscoding                   import _FwSubsysCoding

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _FwSubsysShare:
    __slots__ = []

    __lstWng = None
    __numKBI = 0
    __theMXT = None
    __theLck = _PyRLock()

    def __init__(self):
        pass

    @staticmethod
    def _GetMainXTask():
        with _FwSubsysShare.__theLck:
            res = _FwSubsysShare.__theMXT
            if res is None:
                return None

            if not res.isAttachedToFW:
                res = None
                _FwSubsysShare.__theMXT = None
            return res

    @staticmethod
    def _SetMainXTaskSingleton(mainXT_):
        with _FwSubsysShare.__theLck:
            _FwSubsysShare.__theMXT = mainXT_

    @staticmethod
    def _IsSubsysDisabled(eSSysID_ : _ESubSysID):
        return _FwSubsysShare.__CheckOnDisabledSubsys(eSSysID_, bWarn_=False, bForce_=False, annexID_=None)

    @staticmethod
    def _WarnOnDisabledSubsys(eSSysID_ : _ESubSysID, bForce_ =False, annexID_ : _EFwTextID =None):
        return _FwSubsysShare.__CheckOnDisabledSubsys(eSSysID_, bWarn_=True, bForce_=bForce_, annexID_=annexID_)

    @staticmethod
    def _BookKBI(wngMsg_ : str, bIgnoreWng_ =False, bVLog_ =False) -> int :
        return _FwSubsysShare.__BookKBI(wngMsg_, bIgnoreWng_=bIgnoreWng_, bVLog_=bVLog_)

    @staticmethod
    def _DepInjection(dinjCmd_ : _EDepInjCmd):
        if dinjCmd_.isDeInject:
            if _FwSubsysShare.__lstWng is not None:
                _FwSubsysShare.__lstWng.clear()
            _FwSubsysShare.__lstWng = None
            _FwSubsysShare.__theMXT = None
        else:
            _FwSubsysShare.__numKBI = 0
            _FwSubsysShare.__theLck = _PyRLock()

    @staticmethod
    def __CheckOnDisabledSubsys(eSSysID_ : _ESubSysID, bWarn_ =True, bForce_ =False, annexID_ : _EFwTextID =None):
        if not isinstance(eSSysID_, _ESubSysID):
            return True
        if not eSSysID_.isPublicSubsystem:
            return False

        _msgID = None
        _errID = None
        if eSSysID_.isTmr:
            _bDisabled = not _FwSubsysCoding.IsSubsysTmrConfigured()
            if _bDisabled:
                _errID = _EFwErrorCode.UE_00239
                _msgID = _EFwTextID.eLogMsg_FwSubsysShare_TID_001
        elif eSSysID_.isMP:
            _bDisabled = not _FwSubsysCoding.IsSubsysXmpEnabled()
            if _bDisabled:
                _errID = _EFwErrorCode.UE_00240
                _msgID = _EFwTextID.eLogMsg_FwSubsysShare_TID_002
        else:  
            _bDisabled = not _FwSubsysCoding.IsSubsysXMsgEnabled()
            if _bDisabled:
                _errID = _EFwErrorCode.UE_00241
                _msgID = _EFwTextID.eLogMsg_FwSubsysShare_TID_003

        if not _bDisabled:
            return False

        if bWarn_:
            _bWarn = bForce_
            _bLck  = _FwSubsysShare.__theLck is not None
            if _bLck:
                _FwSubsysShare.__theLck.acquire()

            if _FwSubsysShare.__lstWng is None:
                _FwSubsysShare.__lstWng = []
            if eSSysID_.value not in _FwSubsysShare.__lstWng:
                _bWarn = True
                _FwSubsysShare.__lstWng.append(eSSysID_.value)
            if _bWarn:
                _msg = _FwTDbEngine.GetText(_msgID)
                if isinstance(annexID_, _EFwTextID):
                    _msg = _msg[0:len(_msg)-1]
                    _msg += _CommonDefines._CHAR_SIGN_COLON + _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_012).format(_FwTDbEngine.GetText(annexID_))
                logif._XLogErrorEC(_errID, _msg)
            if _bLck:
                _FwSubsysShare.__theLck.release()
        return True

    @staticmethod
    def __BookKBI(wngMsg_ : str, bIgnoreWng_ =False, bVLog_ =False) -> int :
        _bLck = _FwSubsysShare.__theLck is not None
        if _bLck:
            _FwSubsysShare.__theLck.acquire()

        if not bIgnoreWng_:
            if bVLog_:
                vlogif._LogUrgentWarning(wngMsg_)
            else:
                logif._LogUrgentWarning(wngMsg_)
        _FwSubsysShare.__numKBI += 1

        if _bLck:
            _FwSubsysShare.__theLck.release()
        return _FwSubsysShare.__numKBI

def _IsRteStarted() -> bool:
    return _FwRteConfig._GetInstance()._isRteStarted
def _IsLogRDConsoleSinkEnabled() -> bool:
    return not _FwRteConfig._GetInstance()._isLogRDConsoleSinkDisabled
def _IsLogRDActiveServiceRequired() -> bool:
    return _FwRteConfig._GetInstance()._isLogRDActiveServiceRequired
def _GetRteConfig() -> _FwRteConfig:
    return _FwRteConfig._GetInstance()

def _IsSubsysDisabled(eSSysID_ : _ESubSysID):
    return _FwSubsysShare._IsSubsysDisabled(eSSysID_)
def _WarnOnDisabledSubsys(eSSysID_ : _ESubSysID, bForce_ =False, annexID_ : _EFwTextID =None):
    return _FwSubsysShare._WarnOnDisabledSubsys(eSSysID_, bForce_=bForce_, annexID_=annexID_)

def _IsSubsysMPDisabled():
    return _FwSubsysShare._IsSubsysDisabled(_ESubSysID.eMP)
def _WarnOnDisabledSubsysMP(bForce_ =False, annexID_ : _EFwTextID =None):
    return _FwSubsysShare._WarnOnDisabledSubsys(_ESubSysID.eMP, bForce_=bForce_, annexID_=annexID_)
def _IsSubsysMPXcpTrackingDisabled():
    return _FwSubsysCoding.IsSubsysXmpXcpTrackingDisabled()

def _IsSubsysMsgDisabled():
    return _FwSubsysShare._IsSubsysDisabled(_ESubSysID.eMsg)
def _WarnOnDisabledSubsysMsg(bForce_ =False, annexID_ : _EFwTextID =None):
    return _FwSubsysShare._WarnOnDisabledSubsys(_ESubSysID.eMsg, bForce_=bForce_, annexID_=annexID_)

def _BookKBI(wngMsg_ : str, bIgnoreWng_ =False, bVLog_ =False):
    return _FwSubsysShare._BookKBI(wngMsg_, bIgnoreWng_=bIgnoreWng_, bVLog_=bVLog_)
