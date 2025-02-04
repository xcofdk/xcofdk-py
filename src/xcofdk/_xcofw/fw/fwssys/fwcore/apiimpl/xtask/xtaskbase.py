# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xtaskbase.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from typing import Tuple as _Tuple

from xcofdk.fwapi.xtask import XTaskError
from xcofdk.fwapi.xtask import XTaskProfile

from xcofdk._xcofw.fw.fwssys.fwcore.logging             import logif
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.aexecutable import _AbstractExecutable
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil    import _PyThread
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes   import _CommonDefines

from xcofdk._xcofw.fw.fwssys.fwcore.apiimpl.fwapiconnap       import _FwApiConnectorAP
from xcofdk._xcofw.fw.fwssys.fwcore.apiimpl.fwapiimplshare    import _FwApiImplShare
from xcofdk._xcofw.fw.fwssys.fwcore.apiimpl.xtask.xtaskdefs   import _EXTaskApiID
from xcofdk._xcofw.fw.fwssys.fwcore.apiimpl.xtask.xtaskconn   import _XTaskMirror
from xcofdk._xcofw.fw.fwssys.fwcore.apiimpl.xtask.xtaskconn   import _XTaskConnector
from xcofdk._xcofw.fw.fwssys.fwcore.apiimpl.xtask.xtaskprfext import _XTaskProfileExt
from xcofdk._xcofw.fw.fwssys.fwmsg.apiimpl.xcomsgimpl         import _XMsgImpl
from xcofdk._xcofw.fw.fwssys.fwerrh.fwerrorcodes              import _EFwErrorCode

from xcofdk._xcofwa.fwadmindefs import _FwSubsystemCoding

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine

class _XTaskBase(_AbstractExecutable):

    __slots__ = [ '__xtm' ]

    __singletonID       = None
    __lstBaseClassNames = [ _FwTDbEngine.GetText(_EFwTextID.eELcCompID_XTask), _FwTDbEngine.GetText(_EFwTextID.eELcCompID_MainXTask) ]

    def __init__(self, xtProfile_ : XTaskProfile =None):
        self.__xtm = None
        super().__init__()

        if not _FwApiConnectorAP._APIsLcErrorFree():
            logif._XLogErrorEC(_EFwErrorCode.UE_00163, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskBase_TextID_027))
            return
        if _FwApiConnectorAP._APIsLcShutdownEnabled():
            logif._XLogErrorEC(_EFwErrorCode.UE_00164, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskBase_TextID_028))
            return

        _xtp   = None
        _xtpIn = None
        _xtp, _xtpIn = self.__CheckXtProfile(xtProfile_)
        if _xtp is None:
            return

        _xt = _AbstractExecutable._CalcExecutableTypeID(bMainXT_=_xtp.isMainTask, bMainRbl_=None)
        if _xt is None:
            logif._XLogFatalEC(_EFwErrorCode.FE_00920, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskBase_TextID_001).format(str(_xtp.isMainTask)))
            return

        self.__xtm = _XTaskMirror(self, _xtpIn, _xt, str(_xtp.aliasName))
        _xtc = _XTaskConnector(self.__xtm, _xtp)
        if not _xtc._isXTaskConnected:
            self.__xtm = None
            logif._XLogFatalEC(_EFwErrorCode.FE_00921, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskBase_TextID_002).format(type(self).__name__))
            return

        if _xtp.isMainTask:
            _XTaskBase.__singletonID = id(self)
            _FwApiImplShare._SetMainXTaskSingleton(self)

    def __str__(self):
        return self._ToString()

    @property
    def _isAttachedToFW(self) -> bool:
        return self.__isConnected

    @property
    def _isStarted(self) -> bool:
        if self.__isInvalid:
            return False
        _xtc = self.__xtaskConnector
        return self.__xtm.isStarted if _xtc is None else _xtc._isStarted

    @property
    def _isRunning(self) -> bool:
        if self.__isInvalid:
            return False
        _xtc = self.__xtaskConnector
        return False if _xtc is None else _xtc._isRunning

    @property
    def _isDone(self) -> bool:
        if self.__isInvalid:
            return False
        _xtc = self.__xtaskConnector
        return self.__xtm.isDone if _xtc is None else _xtc._isDone

    @property
    def _isFailed(self) -> bool:
        if self.__isInvalid:
            return False
        _xtc = self.__xtaskConnector
        return self.__xtm.isFailed if _xtc is None else _xtc._isFailed

    @property
    def _isStopping(self) -> bool:
        if self.__isInvalid:
            return False
        _xtc = self.__xtaskConnector
        return self.__xtm.isStopping if _xtc is None else _xtc._isStopping

    @property
    def _isAborting(self) -> bool:
        if self.__isInvalid:
            return False
        _xtc = self.__xtaskConnector
        return self.__xtm.isAborting if _xtc is None else _xtc._isAborting

    @property
    def _executableUniqueID(self) -> int:
        return None if self.__isInvalid else self.__xtm.xtaskUniqueID

    @property
    def _executableName(self) -> str:
        return None if self.__isInvalid else self.__xtm.xtaskName

    @property
    def _xtaskAliasName(self) -> str:
        return None if self.__isInvalid else self.__xtm.aliasName

    @property
    def _currentError(self) -> XTaskError:
        _xtc = self.__xtaskConnector
        return None if _xtc is None else _xtc._currentError

    @property
    def _curRunPhaseIteratoionNo(self):
        return -1 if self.__xtaskConnector is None else self.__xtaskConnector._euRNumber

    @property
    def _xtaskProfile(self) -> XTaskProfile:
        if self.__isInvalid:
            return None
        _xtc = self.__xtaskConnector
        return self.__xtm.xtaskProfile if _xtc is None else _xtc.xtaskProfile

    def _Start(self, *args_, **kwargs_) -> bool:
        if not self.__isConnected:
            return False
        _xtc = self.__xtaskConnector
        return False if _xtc is None else _xtc._StartXTask(*args_, **kwargs_)

    def _Stop(self, cleanupDriver_ =True) -> bool:
        if not self.__isConnected:
            return True
        _xtc = self.__xtaskConnector
        return False if _xtc is None else _xtc._StopXTask(cleanupDriver_=cleanupDriver_)

    def _Join(self, timeout_: [int, float] =None) -> bool:
        if not self.__isConnected:
            return True
        _xtc = self.__xtaskConnector
        return False if _xtc is None else _xtc._JoinXTask(timeout_=timeout_)

    def _DetachFromFW(self):
        if self.__isInvalid:
            return
        if (self._xtaskProfile is not None) and self._xtaskProfile.isMainTask:
            _FwApiImplShare._SetMainXTaskSingleton(None)

        _xtc = self.__xtaskConnector
        if _xtc is not None:
            _xtc._DisconnectXTask(bDetachApiRequest_=True)

    def _ClearCurrentError(self) -> bool:
        if self.__isInvalid:
            return False
        if not self._isAttachedToFW:
            return False

        _xtc = self.__xtaskConnector
        if _xtc is None:
            return False

        _curXT = _FwApiConnectorAP._APGetCurXTask()
        if _curXT is None:
            return False

        if self._executableUniqueID != _curXT._executableUniqueID:
            logif._LogErrorEC(_EFwErrorCode.UE_00004, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskBase_TextID_014).format( self._executableUniqueID))
            return False

        return _xtc._ClearCurrentError()

    def _SetTaskError(self, bFatal_ : bool, errMsg_: str, errCode_: int =None):
        if self.__isInvalid:
            return
        if not self._isAttachedToFW:
            return

        _xtc = self.__xtaskConnector
        if _xtc is None:
            return

        _curXT = _FwApiConnectorAP._APGetCurXTask()
        if _curXT is None:
            return

        if self._executableUniqueID != _curXT._executableUniqueID:
            _msgID = _EFwTextID.eLogMsg_XTaskBase_TextID_026 if bFatal_ else _EFwTextID.eLogMsg_XTaskBase_TextID_025
            logif._LogErrorEC(_EFwErrorCode.UE_00005, _FwTDbEngine.GetText(_msgID).format( self._executableUniqueID))
            return

        _xtc._SetTaskError(bFatal_, errMsg_, errCode_)

    def _TriggerQueueProcessing(self, bExtQueue_ : bool) -> int:
        if not _FwSubsystemCoding.IsSubsystemMessagingConfigured():
            return -1
        if self.__isInvalid:
            return -1
        if not self._isAttachedToFW:
            return -1

        _xtc = self.__xtaskConnector
        if _xtc is None:
            return -1

        if not bExtQueue_:
            if not self._xtaskProfile.isInternalQueueEnabled:
                _midPart = _FwTDbEngine.GetText(_EFwTextID.eMisc_QueueType_Internal)
                logif._LogErrorEC(_EFwErrorCode.UE_00006, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskBase_TextID_005).format(_midPart, self._executableUniqueID, _midPart))
                return -1
        elif not self._xtaskProfile.isExternalQueueEnabled:
            _midPart = _FwTDbEngine.GetText(_EFwTextID.eMisc_QueueType_External)
            logif._LogErrorEC(_EFwErrorCode.UE_00007, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskBase_TextID_005).format(_midPart, self._executableUniqueID, _midPart))
            return -1
        elif self._xtaskProfile.isExternalQueueBlocking:
            _midPart = _FwTDbEngine.GetText(_EFwTextID.eMisc_QueueType_External)
            logif._LogErrorEC(_EFwErrorCode.UE_00008, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskBase_TextID_023).format(_midPart, self._executableUniqueID, _midPart))
            return -1

        _curXT = _FwApiConnectorAP._APGetCurXTask()
        if _curXT is None:
            return -1

        if self._executableUniqueID != _curXT._executableUniqueID:
            _midPart = _FwTDbEngine.GetText(_EFwTextID.eMisc_QueueType_External) if bExtQueue_ else _FwTDbEngine.GetText(_EFwTextID.eMisc_QueueType_Internal)
            logif._LogErrorEC(_EFwErrorCode.UE_00009, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskBase_TextID_024).format(_midPart, self._executableUniqueID, _curXT._executableUniqueID))
            return -1

        return _xtc._TriggerQueueProcessing(bExtQueue_)

    @staticmethod
    def _SendXMsg(xtsk_, xmsg_  : _XMsgImpl) -> bool:
        if (xtsk_ is None) or xtsk_.__isInvalid:
            return False
        if not (isinstance(xmsg_, _XMsgImpl) and xmsg_.isValid):
            return False
        _xtc = xtsk_.__xtaskConnector
        if _xtc is None:
            return False
        return _xtc._SendXMsg(xmsg_)

    def _GetMyExecutableTypeID(self):
        return None if self.__isInvalid else self.__xtm._xtTypeID

    def _ToString(self, *args_, **kwargs_):
        _midPart = _FwTDbEngine.GetText(_EFwTextID.eMisc_Detached)

        if not self._isAttachedToFW:
            if self.__xtm is None:
                res = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_013)
                res = res.format(type(self).__name__, _midPart)
            else:
                res = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_014)
                res = res.format(type(self).__name__, _midPart, self.__xtm._xtStateToString)
        else:
            res       = self._executableName
            _uid      = self._executableUniqueID
            _stateStr = None if self.__isInvalid else self.__xtm._xtStateToString

            if (_uid is not None) or (_stateStr is not None):
                _tmp = _CommonDefines._CHAR_SIGN_DASH if _uid is None else str(_uid)
                if _stateStr is not None:
                    _tmp += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_018).format(_stateStr)
                res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_010).format(_tmp)

            if len(args_) > 0:
                _bCompact = True
                for _ii in range(len(args_)):
                    if 0==_ii: _bCompact = args_[_ii]
                if not _bCompact:
                    res += '\n{}'.format(self._xtaskProfile._ToString(bVerbose_=True))
        return res

    def _CPrf(self, enclosedPyThread_ : _PyThread =None, profileAttrs_ : dict =None):
        _xtc = self.__xtaskConnector
        return None if _xtc is None else _xtc._CPrf(enclosedPyThread_=enclosedPyThread_, profileAttrs_=profileAttrs_)

    @staticmethod
    def __IsSingletonCreated():
        return isinstance(_XTaskBase.__singletonID, int)

    @property
    def __isValid(self):
        return self.__xtm is not None

    @property
    def __isInvalid(self):
        return self.__xtm is None

    @property
    def __isConnected(self):
        return self.__isValid and self.__xtm.isConnected

    @property
    def __isDisconnected(self):
        return self.__isInvalid or not self.__xtm.isConnected

    @property
    def __xtaskConnector(self):
        if self.__isInvalid:
            return None
        return None if not self.__xtm.isConnected else self.__xtm.xtaskConnector

    @staticmethod
    def __IsDefaultCallback(callback_):
        return (callback_ is not None) and callback_.__qualname__.split(_CommonDefines._CHAR_SIGN_DOT)[0] in _XTaskBase.__lstBaseClassNames

    def __CheckXtProfile(self, xtProfile_ : XTaskProfile) -> _Tuple[_XTaskProfileExt, XTaskProfile]:
        _xtp   = xtProfile_
        _xtp2  = None
        _xtpIn = xtProfile_

        if xtProfile_ is None:
            _xtpIn = XTaskProfile()
            _xtp   = _XTaskProfileExt()
        elif not (isinstance(xtProfile_, XTaskProfile) and xtProfile_.isValid):
            logif._XLogErrorEC(_EFwErrorCode.UE_00165, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskBase_TextID_003).format(type(xtProfile_).__name__))
            return None, None

        res = _xtp
        if not isinstance(res, _XTaskProfileExt):
            res   = _XTaskProfileExt(xtProfile_=res)
            _xtp2 = res

        if not res.isValid:
            logif._XLogErrorEC(_EFwErrorCode.UE_00166, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskBase_TextID_004).format(str(res)))
            res = None
        else:
            self.__CheckSetDefaultAliasName(res)

            if not self.__CheckMainXT(res):
                res = None
            elif not self.__CheckAliasName(res):
                res = None
            elif not self.__CheckIntQueue(res):
                res = None
            elif not self.__CheckExtQueue(res):
                res = None
            elif not self.__CheckRun(res):
                res = None
            elif not self.__CheckSetup(res):
                res = None
            elif not self.__CheckTeardown(res):
                res = None
            elif not self.__CheckRunPhaseFrequency(res):
                res = None
            elif not self.__CheckMaxProcTimespan(res):
                res = None

        if res is None:
            if _xtp2 is not None:
                _xtp2._CleanUp()
            if xtProfile_ is None:
                _xtp._CleanUp()
                _xtpIn._CleanUp()
            _xtp, _xtpIn = None, None

        return res, _xtpIn

    def __CheckMainXT(self, xtProfileExt_: _XTaskProfileExt) -> bool:
        res  = self is not None
        if xtProfileExt_.isMainTask:
            if _XTaskBase.__IsSingletonCreated():
                res = False
                logif._XLogErrorEC(_EFwErrorCode.UE_00167, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskBase_TextID_006))
        return res

    def __CheckAliasName(self, xtProfileExt_: _XTaskProfileExt) -> bool:
        res  = True
        _xtp = xtProfileExt_

        aliasName = _xtp.aliasName
        if aliasName is None:
            _xtp.aliasName = type(self).__name__
        elif not isinstance(aliasName, str):
            res = False
            logif._XLogErrorEC(_EFwErrorCode.UE_00168, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskBase_TextID_007).format(type(aliasName).__name__))
        else:
            aliasName = aliasName.strip()
            if len(aliasName) < 1:
                _xtp.aliasName = type(self).__name__
                logif._XLogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskBase_TextID_008).format(aliasName))
            elif not aliasName.isidentifier():
                res = False
                logif._XLogErrorEC(_EFwErrorCode.UE_00169, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskBase_TextID_009).format(aliasName))
        return res

    def __CheckIntQueue(self, xtProfileExt_: _XTaskProfileExt) -> bool:
        res  = True
        _xtp = xtProfileExt_

        _mAttrName = _EXTaskApiID.eProcessInternalMessage.functionName
        _mAttrVal  = getattr(self, _mAttrName, None)

        if not _xtp.isInternalQueueEnabled:
            if _mAttrVal is not None:
                if not _XTaskBase.__IsDefaultCallback(_mAttrVal):
                    logif._XLogDebug(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskBase_TextID_010).format(type(self).__name__, _mAttrName))
        elif _mAttrVal is None:
            res = False
            logif._XLogErrorEC(_EFwErrorCode.UE_00170, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskBase_TextID_011).format(type(self).__name__, _mAttrName))
        return res

    def __CheckExtQueue(self, xtProfileExt_: _XTaskProfileExt) -> bool:
        res  = True
        _xtp = xtProfileExt_

        _mAttrName = _EXTaskApiID.eProcessExternalMessage.functionName
        _mAttrVal  = getattr(self, _mAttrName, None)

        if not _xtp.isExternalQueueEnabled:
            if _mAttrVal is not None:
                if not _XTaskBase.__IsDefaultCallback(_mAttrVal):
                    logif._XLogDebug(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskBase_TextID_012).format(type(self).__name__, _mAttrName))
            if _xtp.isExternalQueueBlocking:
                res = False
                logif._XLogErrorEC(_EFwErrorCode.UE_00171, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskBase_TextID_013).format(type(self).__name__))
        elif _mAttrVal is None:
            res = False
            logif._XLogErrorEC(_EFwErrorCode.UE_00172, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskBase_TextID_011).format(type(self).__name__, _mAttrName))
        return res

    def __CheckRun(self, xtProfileExt_: _XTaskProfileExt) -> bool:
        res  = True
        _xtp = xtProfileExt_

        _mAttrName = _EXTaskApiID.eRunXTask.functionName
        _mAttrVal   = getattr(self, _mAttrName, None)

        if _xtp.isExternalQueueEnabled and _xtp.isExternalQueueBlocking:
            if _mAttrVal is None:
                pass
            elif not _XTaskBase.__IsDefaultCallback(_mAttrVal):
                _mAttrVal = None
                logif._XLogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskBase_TextID_022).format(type(self).__name__, _mAttrName))
            else:
                _mAttrVal = None

        else:
            if _mAttrVal is None:
                res = False
            elif _XTaskBase.__IsDefaultCallback(_mAttrVal):
                res       = False
                _mAttrVal = None
            if not res:
                logif._XLogErrorEC(_EFwErrorCode.UE_00173, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskBase_TextID_011).format(type(self).__name__, _mAttrName))

        if res:
            if (_mAttrVal is not None) != _xtp.isRunPhaseEnabled:
                res = False
                logif._XLogFatalEC(_EFwErrorCode.FE_00922, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskBase_TextID_015).format(type(self).__name__, _mAttrName))
        return res

    def __CheckSetup(self, xtProfileExt_: _XTaskProfileExt) -> bool:
        res  = True
        _xtp = xtProfileExt_

        _mAttrName = _EXTaskApiID.eSetUpXTask.functionName
        _mAttrVal  = getattr(self, _mAttrName, None)

        if not _xtp.isSetupPhaseEnabled:
            if _mAttrVal is not None:
                if not _XTaskBase.__IsDefaultCallback(_mAttrVal):
                    logif._XLogDebug(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskBase_TextID_016).format(type(self).__name__, _mAttrName))
        elif _mAttrVal is None:
            res = False
            logif._XLogErrorEC(_EFwErrorCode.UE_00174, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskBase_TextID_011).format(type(self).__name__, _mAttrName))
        return res

    def __CheckTeardown(self, xtProfileExt_: _XTaskProfileExt) -> bool:
        res  = True
        _xtp = xtProfileExt_

        _mAttrName = _EXTaskApiID.eTearDownXTask.functionName
        _mAttrVal  = getattr(self, _mAttrName, None)

        if not _xtp.isTeardownPhaseEnabled:
            if _mAttrVal is not None:
                if not _XTaskBase.__IsDefaultCallback(_mAttrVal):
                    logif._XLogDebug(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskBase_TextID_017).format(type(self).__name__, _mAttrName))
        elif _mAttrVal is None:
            res = False
            logif._XLogErrorEC(_EFwErrorCode.UE_00175, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskBase_TextID_011).format(type(self).__name__, _mAttrName))
        return res

    def __CheckRunPhaseFrequency(self, xtProfileExt_: _XTaskProfileExt) -> bool:
        res  = True
        _xtp = xtProfileExt_

        if _xtp.runPhaseFrequencyMS < 0:
            res = False
            logif._XLogErrorEC(_EFwErrorCode.UE_00176, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskBase_TextID_018).format(_xtp.runPhaseFrequencyMS, type(self).__name__))

        return res

    def __CheckMaxProcTimespan(self, xtProfileExt_: _XTaskProfileExt) -> bool:
        res  = True
        _xtp = xtProfileExt_

        if _xtp.runPhaseMaxProcessingTimeMS <= 0:
            res = False
            logif._XLogErrorEC(_EFwErrorCode.UE_00177, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskBase_TextID_021).format(_xtp.runPhaseMaxProcessingTimeMS, type(self).__name__))
        return res

    def __CheckSetDefaultAliasName(self, xtProfile_ : XTaskProfile):
        if xtProfile_.aliasName is None:
            aliasName = type(self).__name__
            startChar = aliasName[0]
            if not startChar.islower():
                startChar = startChar.lower()
                aliasName = startChar + aliasName[1:] if len(aliasName) > 1 else startChar
            xtProfile_.aliasName = aliasName

