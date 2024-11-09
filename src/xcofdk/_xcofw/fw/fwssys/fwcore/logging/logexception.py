# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : logexception.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------



from xcofdk._xcofw.fw.fwssys.fwcore.logging.logdefines   import _ELogType
from xcofdk._xcofw.fw.fwssys.fwcore.logging.fatalentry   import _FatalEntry
from xcofdk._xcofw.fw.fwssys.fwcore.logging.xcoexception import _EXcoXcpType
from xcofdk._xcofw.fw.fwssys.fwcore.logging.xcoexception import _XcoException
from xcofdk._xcofw.fw.fwssys.fwcore.logging.xcoexception import _XcoBaseException
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes    import _CommonDefines

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine


class _LogException(_XcoException):

    __slots__ = [ '__enclFE' ]

    def __init__(self, eXcpLogType_ : _ELogType =None, errCode_ : int =None
                , taskName_ : str =None, taskID_ : int =None
                , shortMsg_ : str =None, longMsg_ : str =None
                , inheritanceDepth_ =3, callstackLevelOffset_ =None
                , sysOpXcp_: BaseException =None, xcpTraceback_ : str =None, initByFE_ =None, euRNum_ =None):
        self.__enclFE = None

        if eXcpLogType_ is None:
            eXcpLogType_ = _ELogType.FTL

        _checkOK = True
        if initByFE_ is not None:
            if not isinstance(initByFE_, _FatalEntry):
                _checkOK = False
                _XcoException._RaiseSystemExit(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LogException_TextID_001).format(type(initByFE_).__name__))
            elif initByFE_.isInvalid:
                _checkOK = False
                _XcoException._RaiseSystemExit(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LogException_TextID_002))
        if eXcpLogType_ == _ELogType.FTL_SYS_OP_XCP:
            if sysOpXcp_ is None:
                _checkOK = False
                _XcoException._RaiseSystemExit(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LogException_TextID_003))

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
            _myFE = _FatalEntry( eXcpLogType_
                              , errCode_=errCode_, taskName_=taskName_, taskID_=taskID_
                              , shortMsg_=shortMsg_, longMsg_=longMsg_
                              , inheritanceDepth_=inheritanceDepth_, callstackLevelOffset_=callstackLevelOffset_
                              , xcoBaseXcp_=_xbx, cloneby_=None, euRNum_=euRNum_)
            if _myFE.isInvalid:
                _myFE.CleanUp()
                _myFE = None
        self.__enclFE = _myFE

        if self.__enclFE is None:
            _xcpMsg = _CommonDefines._CHAR_SIGN_DASH
        else:
            _xcpMsg = self.__enclFE.message
            self.__enclFE._SetLogException(self)
        super().__init__(_EXcoXcpType.eLogException, xcpMsg_=_xcpMsg)

    @property
    def isFatalException(self):
        return (not self._enclosedFatalEntry is None) and self._enclosedFatalEntry.eLogType==_ELogType.FTL

    @property
    def isBadUseException(self):
        return (not self._enclosedFatalEntry is None) and self._enclosedFatalEntry.eLogType==_ELogType.FTL_BAD_USE

    @property
    def isImplErrorException(self):
        return (not self._enclosedFatalEntry is None) and self._enclosedFatalEntry.eLogType==_ELogType.FTL_IMPL_ERR

    @property
    def isNotImplementedException(self):
        return (not self._enclosedFatalEntry is None) and self._enclosedFatalEntry.eLogType==_ELogType.FTL_NOT_IMPLEMENTED_YET

    @property
    def isSystemOperationErrorException(self):
        return (not self._enclosedFatalEntry is None) and self._enclosedFatalEntry.eLogType==_ELogType.FTL_SYS_OP_ERR

    @property
    def isSystemOperationRaisedException(self):
        return (not self._enclosedFatalEntry is None) and self._enclosedFatalEntry.eLogType==_ELogType.FTL_SYS_OP_XCP

    @property
    def isNestedErrorException(self):
        return (not self._enclosedFatalEntry is None) and self._enclosedFatalEntry.eLogType==_ELogType.FTL_NESTED_ERR

    @property
    def isFlushed(self):
        return True if self._enclosedFatalEntry is None else self.__enclFE.isFlushed

    @property
    def eType(self):
        return None if self._enclosedFatalEntry is None else self.__enclFE.eLogType

    @property
    def errorCode(self):
        return None if self._enclosedFatalEntry is None else self.__enclFE.errorCode

    @property
    def shortMessage(self):
        return None if self._enclosedFatalEntry is None else self.__enclFE.shortMessage

    @classmethod
    def _CloneBase(cls_, self_):
        res = None
        if self_._enclosedFatalEntry is None:
            pass
        else:
            _cfe = self_._enclosedFatalEntry._Clone(calledByLogException_=True)
            if _cfe is None:
                pass
            else:
                if self_.isNestedErrorException:
                    nestedXcp = self_._nestedLogException.Clone()
                    res = cls_(_cfe, nestedXcp)
                elif self_.isSystemOperationRaisedException:
                    sysOpXcp = self_._enclosedFatalEntry._causedBySystemException.Clone()
                    res = cls_(sysOpXcp, None, initByFE_=_cfe)
                else:
                    res = cls_(self_._enclosedFatalEntry.eLogType, initByFE_=_cfe)

                if res._enclosedFatalEntry is None:
                    res.CleanUp()
                    _cfe.CleanUp()
                    res = None
        return res

    @property
    def _enclosedFatalEntry(self) -> _FatalEntry:
        if self.__enclFE is not None:
            if self.__enclFE.isInvalid:
                self.__enclFE = None
        return self.__enclFE

    @property
    def _isClone(self):
        return False if self._enclosedFatalEntry is None else self.__enclFE.isClone

    @property
    def _uniqueID(self):
        return None if self._enclosedFatalEntry is None else self.__enclFE.uniqueID

    @property
    def _taskID(self):
        return None if self._enclosedFatalEntry is None else self.__enclFE.taskID

    @property
    def _taskName(self):
        return None if self._enclosedFatalEntry is None else self.__enclFE.taskName

    @property
    def _callstack(self):
        return None if self._enclosedFatalEntry is None else self.__enclFE.callstack

    def _IsEqual(self, rhs_):
        res = isinstance(rhs_, _LogException)
        if not res:
            pass
        elif id(self) == id(rhs_):
            pass
        elif self.__enclFE is None:
            res = rhs_.__enclFE is None
        elif not _FatalEntry._IsEqual(self.__enclFE, rhs_.__enclFE):
            res = False
        return res

    def _DetachEnclosedFatalEntry(self):
        res = self.__enclFE
        if res is not None:
            self.__enclFE = None
            res._SetLogException(None)
        return res

    def _ToString(self):
        _myFE = self._enclosedFatalEntry
        if (_myFE is None) or _myFE.isInvalid:
            return None

        _feType = _myFE.eLogType
        if _feType == _ELogType.FTL:
            _myTxt = _FwTDbEngine.GetText(_EFwTextID.eLogException_TypeName_Fatal)
        elif _feType == _ELogType.FTL_BAD_USE:
            _myTxt = _FwTDbEngine.GetText(_EFwTextID.eLogException_TypeName_BadUse)
        elif _feType == _ELogType.FTL_IMPL_ERR:
            _myTxt = _FwTDbEngine.GetText(_EFwTextID.eLogException_TypeName_ImplError)
        elif _feType == _ELogType.FTL_NOT_IMPLEMENTED_YET:
            _myTxt = _FwTDbEngine.GetText(_EFwTextID.eLogException_TypeName_NotImplemented)
        elif _feType == _ELogType.FTL_SYS_OP_ERR:
            _myTxt = _FwTDbEngine.GetText(_EFwTextID.eLogException_TypeName_SystemOpERR)
        elif _feType == _ELogType.FTL_SYS_OP_XCP:
            _myTxt = _FwTDbEngine.GetText(_EFwTextID.eLogException_TypeName_SystemOpXCP)
        elif _feType == _ELogType.FTL_NESTED_ERR:
            _myTxt = _FwTDbEngine.GetText(_EFwTextID.eLogException_TypeName_NestedError)
        else:
            _XcoException._RaiseSystemExit(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LogException_TextID_004).format(_feType))
            return None
        return _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_009).format(_myTxt, _myFE)

    def _CleanUp(self):
        if self.__enclFE is not None:
            self.__enclFE.CleanUp()
            self.__enclFE = None
        super()._CleanUp()


class _LogExceptionFatal(_LogException):
    def __init__( self, errCode_ : int =None, taskName_ : str =None, taskID_ : int =None
                , shortMsg_ : str =None, longMsg_ : str =None, callstackLevelOffset_ =None, euRNum_ =None, initByFE_ =None, bFwApiLog_ =False):
        _LogException.__init__( self, eXcpLogType_=_ELogType.XFTL if bFwApiLog_ else _ELogType.FTL
                             , errCode_=errCode_, taskName_=taskName_, taskID_=taskID_
                             , shortMsg_=shortMsg_, longMsg_=longMsg_, inheritanceDepth_=4
                             , callstackLevelOffset_=callstackLevelOffset_, euRNum_=euRNum_, initByFE_=initByFE_)

    def _Clone(self):
        res = _LogExceptionFatal._CloneBase(self)
        return res


class _LogExceptionBadUse(_LogException):
    def __init__( self, errCode_ : int =None, taskName_ : str =None, taskID_ : int =None
                , shortMsg_ : str =None, longMsg_ : str =None, callstackLevelOffset_ =None, euRNum_ =None, initByFE_ =None, bFwApiLog_ =False):
        _LogException.__init__( self, eXcpLogType_=_ELogType.FTL_BAD_USE
                             , errCode_=errCode_, taskName_=taskName_, taskID_=taskID_
                             , shortMsg_=shortMsg_, longMsg_=longMsg_, inheritanceDepth_=4
                             , callstackLevelOffset_=callstackLevelOffset_, euRNum_=euRNum_, initByFE_=initByFE_)

    def _Clone(self):
        res = _LogExceptionBadUse._CloneBase(self)
        return res


class _LogExceptionImplError(_LogException):
    def __init__( self, errCode_ : int =None, taskName_ : str =None, taskID_ : int =None
                , shortMsg_ : str =None, longMsg_ : str =None, callstackLevelOffset_ =None, euRNum_ =None, initByFE_ =None, bFwApiLog_ =False):
        _LogException.__init__( self, eXcpLogType_=_ELogType.FTL_IMPL_ERR
                             , errCode_=errCode_, taskName_=taskName_, taskID_=taskID_
                             , shortMsg_=shortMsg_, longMsg_=longMsg_, inheritanceDepth_=4
                             , callstackLevelOffset_=callstackLevelOffset_, euRNum_=euRNum_, initByFE_=initByFE_)

    def _Clone(self):
        res = _LogExceptionImplError._CloneBase(self)
        return res


class _LogExceptionNotImplemented(_LogException):
    def __init__( self, errCode_ : int =None, taskName_ : str =None, taskID_ : int =None
                , shortMsg_ : str =None, longMsg_ : str =None, callstackLevelOffset_ =None, euRNum_ =None, initByFE_ =None, bFwApiLog_ =False):
        _LogException.__init__( self, eXcpLogType_=_ELogType.FTL_NOT_IMPLEMENTED_YET
                             , errCode_=errCode_, taskName_=taskName_, taskID_=taskID_
                             , shortMsg_=shortMsg_, longMsg_=longMsg_, inheritanceDepth_=4
                             , callstackLevelOffset_=callstackLevelOffset_, euRNum_=euRNum_, initByFE_=initByFE_)

    def _Clone(self):
        res = _LogExceptionNotImplemented._CloneBase(self)
        return res


class _LogExceptionSystemOpERR(_LogException):
    def __init__( self, errCode_ : int =None, taskName_ : str =None, taskID_ : int =None
                , shortMsg_ : str =None, longMsg_ : str =None, callstackLevelOffset_ =None, euRNum_ =None, initByFE_ =None, bFwApiLog_ =False):
        _LogException.__init__( self, eXcpLogType_=_ELogType.FTL_SYS_OP_ERR
                             , errCode_=errCode_, taskName_=taskName_, taskID_=taskID_
                             , shortMsg_=shortMsg_, longMsg_=longMsg_, inheritanceDepth_=4
                             , callstackLevelOffset_=callstackLevelOffset_, euRNum_=euRNum_, initByFE_=initByFE_)

    def _Clone(self):
        res = _LogExceptionSystemOpERR._CloneBase(self)
        return res


class _LogExceptionSystemOpXCP(_LogException):
    def __init__( self, sysOpXcp_ : BaseException, xcpTraceback_ : str, errCode_ : int =None
                , taskName_ : str =None, taskID_ : int =None
                , shortMsg_ : str =None, longMsg_ : str =None, callstackLevelOffset_ =None, euRNum_ =None, initByFE_ =None, bFwApiLog_ =False):
        _LogException.__init__( self, eXcpLogType_=_ELogType.FTL_SYS_OP_XCP
                             , errCode_=errCode_, taskName_=taskName_, taskID_=taskID_
                             , shortMsg_=shortMsg_, longMsg_=longMsg_, inheritanceDepth_=4
                             , callstackLevelOffset_=callstackLevelOffset_
                             , sysOpXcp_=sysOpXcp_, xcpTraceback_=xcpTraceback_, euRNum_=euRNum_, initByFE_=initByFE_)

    @property
    def _causedBySystemException(self) -> _XcoBaseException:
        return None if self._enclosedFatalEntry is None else self._enclosedFatalEntry._causedBySystemException

    def _Clone(self):
        res = _LogExceptionSystemOpXCP._CloneBase(self)
        return res


class _LogExceptionNestedError(_LogException):

    def __init__(self, mainXcp_ : _LogException, nestedXcp_ : _LogException):
        if not isinstance(mainXcp_, _LogException):
            _XcoException._RaiseSystemExit(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LogException_TextID_005).format(type(mainXcp_).__name__))
            return

        _myFE = mainXcp_._enclosedFatalEntry
        if _myFE is None:
            _XcoException._RaiseSystemExit(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LogException_TextID_006).format(type(mainXcp_).__name__))
            return
        if not isinstance(nestedXcp_, _LogException):
            _XcoException._RaiseSystemExit(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LogException_TextID_007).format(type(nestedXcp_).__name__))
            return
        if nestedXcp_._enclosedFatalEntry is None:
            _XcoException._RaiseSystemExit(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_LogException_TextID_008))
            return

        super().__init__(eXcpLogType_=_ELogType.FTL_NESTED_ERR, initByFE_=_myFE)
        if self.eExceptionType is not None:
            _myTxt = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_009).format(type(self).__name__, _myFE.shortMessage)
            self._enclosedFatalEntry._Adapt(eLogType_=_ELogType.FTL_NESTED_ERR, shortMsg_=_myTxt, bCleanupPermitted_=mainXcp_._enclosedFatalEntry._isCleanupPermitted)
            self._SetEnclosedLogException(nestedXcp_)

            if _myFE.eErrorImpact is not None:
                self._enclosedFatalEntry._SetErrorImpact(_myFE.eErrorImpact)

    @property
    def _nestedLogException(self):
        return self._enclosedLogException

    def _Clone(self):
        res = _LogExceptionNestedError._CloneBase(self)
        return res
