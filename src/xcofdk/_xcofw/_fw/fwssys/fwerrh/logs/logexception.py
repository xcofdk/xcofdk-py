# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xcplog.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from _fw.fwssys.fwcore.logging.logdefines import _ELogType
from _fw.fwssys.fwcore.types.commontypes  import _CommonDefines
from _fw.fwssys.fwerrh.logs.errorlog      import _FatalLog
from _fw.fwssys.fwerrh.logs.xcoexception  import _EXcoXcpType
from _fw.fwssys.fwerrh.logs.xcoexception  import _XcoException
from _fw.fwssys.fwerrh.logs.xcoexception  import _XcoBaseException

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _LogException(_XcoException):
    __slots__ = [ '__f' ]

    def __init__( self
                , logType_ : _ELogType =None, errCode_ : int =None
                , taskName_ : str =None, taskID_ : int =None
                , shortMsg_ : str =None, longMsg_ : str =None
                , sysOpXcp_: BaseException =None, xcpTraceback_ : str =None, initByFE_ =None, xrn_ =None):
        self.__f = None

        if logType_ is None:
            logType_ = _ELogType.FTL

        _checkOK = True
        if initByFE_ is not None:
            if not isinstance(initByFE_, _FatalLog):
                _checkOK = False
                _XcoException._RaiseSystemExit(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LogException_TID_001).format(type(initByFE_).__name__))
            elif initByFE_.isInvalid:
                _checkOK = False
                _XcoException._RaiseSystemExit(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LogException_TID_002))
        if logType_ == _ELogType.FTL_SOX:
            if sysOpXcp_ is None:
                _checkOK = False
                _XcoException._RaiseSystemExit(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LogException_TID_003))

        if not _checkOK:
            _myFE = None
        elif initByFE_ is not None:
            _myFE = initByFE_
        else:
            _xbx = None
            if sysOpXcp_ is not None:
                if isinstance(sysOpXcp_, _XcoBaseException):
                    _xbx = sysOpXcp_
                else:
                    _xbx = _XcoBaseException(sysOpXcp_, tb_=xcpTraceback_, taskID_=taskID_)
            _myFE = _FatalLog( logType_
                              , errCode_=errCode_, taskName_=taskName_, taskID_=taskID_
                              , shortMsg_=shortMsg_, longMsg_=longMsg_
                              , xcoBaseXcp_=_xbx, cloneby_=None, xrn_=xrn_)
            if _myFE.isInvalid:
                _myFE.CleanUp()
                _myFE = None
        self.__f = _myFE

        if self.__f is None:
            _xcpMsg = _CommonDefines._CHAR_SIGN_DASH
        else:
            _xcpMsg = self.__f.message
            self.__f._SetLogException(self)
        super().__init__(_EXcoXcpType.eLogException, xcpMsg_=_xcpMsg)

    @property
    def isFatalException(self):
        return (not self._enclosedFatalEntry is None) and self._enclosedFatalEntry.logType==_ELogType.FTL

    @property
    def isBadUseException(self):
        return (not self._enclosedFatalEntry is None) and self._enclosedFatalEntry.logType==_ELogType.FTL_BU

    @property
    def isImplErrorException(self):
        return (not self._enclosedFatalEntry is None) and self._enclosedFatalEntry.logType==_ELogType.FTL_IE

    @property
    def isNotImplementedException(self):
        return (not self._enclosedFatalEntry is None) and self._enclosedFatalEntry.logType==_ELogType.FTL_NIY

    @property
    def isSystemOperationErrorException(self):
        return (not self._enclosedFatalEntry is None) and self._enclosedFatalEntry.logType==_ELogType.FTL_SOE

    @property
    def isSystemOperationRaisedException(self):
        return (not self._enclosedFatalEntry is None) and self._enclosedFatalEntry.logType==_ELogType.FTL_SOX

    @property
    def isNestedErrorException(self):
        return (not self._enclosedFatalEntry is None) and self._enclosedFatalEntry.logType==_ELogType.FTL_NERR

    @property
    def errorCode(self):
        return None if self._enclosedFatalEntry is None else self.__f.errorCode

    @property
    def shortMessage(self):
        return None if self._enclosedFatalEntry is None else self.__f.shortMessage

    @classmethod
    def _CloneBase(cls_, self_):
        res = None
        if self_._enclosedFatalEntry is not None:
            _cfe = self_._enclosedFatalEntry._Clone(calledByLogException_=True)
            if _cfe is not None:
                if self_.isNestedErrorException:
                    res = cls_(_cfe, self_._nestedLogException.Clone())
                elif self_.isSystemOperationRaisedException:
                    _sysOpXcp = self_._enclosedFatalEntry._causedBySystemException.Clone()
                    res = cls_(_sysOpXcp, None, initByFE_=_cfe)
                else:
                    res = cls_(self_._enclosedFatalEntry.logType, initByFE_=_cfe)

                if res._enclosedFatalEntry is None:
                    res.CleanUp()
                    _cfe.CleanUp()
                    res = None
        return res

    @property
    def _enclosedFatalEntry(self) -> _FatalLog:
        if self.__f is not None:
            if self.__f.isInvalid:
                self.__f = None
        return self.__f

    @property
    def _isClone(self):
        return False if self._enclosedFatalEntry is None else self.__f.isClone

    @property
    def _uniqueID(self):
        return None if self._enclosedFatalEntry is None else self.__f.uniqueID

    @property
    def _taskID(self):
        return None if self._enclosedFatalEntry is None else self.__f.dtaskUID

    @property
    def _taskName(self):
        return None if self._enclosedFatalEntry is None else self.__f.dtaskName

    @property
    def _callstack(self):
        return None if self._enclosedFatalEntry is None else self.__f.callstack

    def _IsEqual(self, rhs_):
        res = isinstance(rhs_, _LogException)
        if not res:
            pass
        elif id(self) == id(rhs_):
            pass
        elif self.__f is None:
            res = rhs_.__f is None
        elif not _FatalLog._IsEqual(self.__f, rhs_.__f):
            res = False
        return res

    def _DetachEnclosedFatalEntry(self):
        res = self.__f
        if res is not None:
            self.__f = None
            res._SetLogException(None)
        return res

    def _ToString(self):
        _myFE = self._enclosedFatalEntry
        if (_myFE is None) or _myFE.isInvalid:
            return None

        _feType = _myFE.logType
        if _feType == _ELogType.FTL:
            _myTxt = _FwTDbEngine.GetText(_EFwTextID.eLogException_TypeName_Fatal)
        elif _feType == _ELogType.FTL_BU:
            _myTxt = _FwTDbEngine.GetText(_EFwTextID.eLogException_TypeName_BadUse)
        elif _feType == _ELogType.FTL_IE:
            _myTxt = _FwTDbEngine.GetText(_EFwTextID.eLogException_TypeName_ImplError)
        elif _feType == _ELogType.FTL_NIY:
            _myTxt = _FwTDbEngine.GetText(_EFwTextID.eLogException_TypeName_NotImplemented)
        elif _feType == _ELogType.FTL_SOE:
            _myTxt = _FwTDbEngine.GetText(_EFwTextID.eLogException_TypeName_SystemOpERR)
        elif _feType == _ELogType.FTL_SOX:
            _myTxt = _FwTDbEngine.GetText(_EFwTextID.eLogException_TypeName_SystemOpXCP)
        elif _feType == _ELogType.FTL_NERR:
            _myTxt = _FwTDbEngine.GetText(_EFwTextID.eLogException_TypeName_NestedError)
        else:
            _XcoException._RaiseSystemExit(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LogException_TID_004).format(_feType))
            return None
        return _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_009).format(_myTxt, _myFE)

    def _CleanUp(self):
        if self.__f is not None:
            self.__f.CleanUp()
            self.__f = None
        super()._CleanUp()

class _LogExceptionFatal(_LogException):
    def __init__( self, errCode_ : int =None, taskName_ : str =None, taskID_ : int =None
                , shortMsg_ : str =None, longMsg_ : str =None, xrn_ =None, initByFE_ =None, bFwApiLog_ =False):
        _LogException.__init__( self, logType_=_ELogType.XFTL if bFwApiLog_ else _ELogType.FTL
                             , errCode_=errCode_, taskName_=taskName_, taskID_=taskID_
                             , shortMsg_=shortMsg_, longMsg_=longMsg_, xrn_=xrn_, initByFE_=initByFE_)

    def _Clone(self):
        res = _LogExceptionFatal._CloneBase(self)
        return res

class _LogExceptionBadUse(_LogException):
    def __init__( self, errCode_ : int =None, taskName_ : str =None, taskID_ : int =None
                , shortMsg_ : str =None, longMsg_ : str =None, xrn_ =None, initByFE_ =None, bFwApiLog_ =False):
        _LogException.__init__( self, logType_=_ELogType.FTL_BU
                             , errCode_=errCode_, taskName_=taskName_, taskID_=taskID_
                             , shortMsg_=shortMsg_, longMsg_=longMsg_, xrn_=xrn_, initByFE_=initByFE_)

    def _Clone(self):
        res = _LogExceptionBadUse._CloneBase(self)
        return res

class _LogExceptionImplError(_LogException):
    def __init__( self, errCode_ : int =None, taskName_ : str =None, taskID_ : int =None
                , shortMsg_ : str =None, longMsg_ : str =None, xrn_ =None, initByFE_ =None, bFwApiLog_ =False):
        _LogException.__init__( self, logType_=_ELogType.FTL_IE
                             , errCode_=errCode_, taskName_=taskName_, taskID_=taskID_
                             , shortMsg_=shortMsg_, longMsg_=longMsg_, xrn_=xrn_, initByFE_=initByFE_)

    def _Clone(self):
        res = _LogExceptionImplError._CloneBase(self)
        return res

class _LogExceptionNotImplemented(_LogException):
    def __init__( self, errCode_ : int =None, taskName_ : str =None, taskID_ : int =None
                , shortMsg_ : str =None, longMsg_ : str =None, xrn_ =None, initByFE_ =None, bFwApiLog_ =False):
        _LogException.__init__( self, logType_=_ELogType.FTL_NIY
                             , errCode_=errCode_, taskName_=taskName_, taskID_=taskID_
                             , shortMsg_=shortMsg_, longMsg_=longMsg_, xrn_=xrn_, initByFE_=initByFE_)

    def _Clone(self):
        res = _LogExceptionNotImplemented._CloneBase(self)
        return res

class _LogExceptionSystemOpERR(_LogException):
    def __init__( self, errCode_ : int =None, taskName_ : str =None, taskID_ : int =None
                , shortMsg_ : str =None, longMsg_ : str =None, xrn_ =None, initByFE_ =None, bFwApiLog_ =False):
        _LogException.__init__( self, logType_=_ELogType.FTL_SOE
                             , errCode_=errCode_, taskName_=taskName_, taskID_=taskID_
                             , shortMsg_=shortMsg_, longMsg_=longMsg_, xrn_=xrn_, initByFE_=initByFE_)

    def _Clone(self):
        res = _LogExceptionSystemOpERR._CloneBase(self)
        return res

class _LogExceptionSystemOpXCP(_LogException):
    def __init__( self, sysOpXcp_ : BaseException, xcpTraceback_ : str =None, errCode_ : int =None
                , taskName_ : str =None, taskID_ : int =None
                , shortMsg_ : str =None, longMsg_ : str =None, xrn_ =None, initByFE_ =None, bFwApiLog_ =False):
        _LogException.__init__( self, logType_=_ELogType.XFTL_SOX if bFwApiLog_ else _ELogType.FTL_SOX
                             , errCode_=errCode_, taskName_=taskName_, taskID_=taskID_
                             , shortMsg_=shortMsg_, longMsg_=longMsg_, sysOpXcp_=sysOpXcp_
                             , xcpTraceback_=xcpTraceback_, xrn_=xrn_, initByFE_=initByFE_)

    @property
    def _causedBySystemException(self) -> _XcoBaseException:
        return None if self._enclosedFatalEntry is None else self._enclosedFatalEntry._causedBySystemException

    def _Clone(self):
        res = _LogExceptionSystemOpXCP._CloneBase(self)
        return res

class _LogExceptionNestedError(_LogException):
    def __init__(self, mainXcp_ : _LogException, nestedXcp_ : _LogException):
        if not isinstance(mainXcp_, _LogException):
            _XcoException._RaiseSystemExit(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LogException_TID_005).format(type(mainXcp_).__name__))
            return

        _myFE = mainXcp_._enclosedFatalEntry
        if _myFE is None:
            _XcoException._RaiseSystemExit(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LogException_TID_006).format(type(mainXcp_).__name__))
            return
        if not isinstance(nestedXcp_, _LogException):
            _XcoException._RaiseSystemExit(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LogException_TID_007).format(type(nestedXcp_).__name__))
            return
        if nestedXcp_._enclosedFatalEntry is None:
            _XcoException._RaiseSystemExit(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LogException_TID_008))
            return

        super().__init__(logType_=_ELogType.FTL_NERR, initByFE_=_myFE)
        if self.xcpType is not None:
            _myTxt = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_009).format(type(self).__name__, _myFE.shortMessage)
            self._enclosedFatalEntry._Adapt(logType_=_ELogType.FTL_NERR, shortMsg_=_myTxt, bCleanupPermitted_=mainXcp_._enclosedFatalEntry._isCleanupPermitted)
            self._SetEnclosedLogException(nestedXcp_)

            if _myFE.errorImpact is not None:
                self._enclosedFatalEntry._SetErrorImpact(_myFE.errorImpact)

    @property
    def _nestedLogException(self):
        return self._enclosedLogException

    def _Clone(self):
        res = _LogExceptionNestedError._CloneBase(self)
        return res
