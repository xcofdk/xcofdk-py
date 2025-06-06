# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xcoexception.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum   import Enum
from enum   import unique
from typing import Union

from _fw.fwssys.fwcore.logging.logdefines import _LogErrorCode
from _fw.fwssys.fwcore.logging.logdefines import _LogUniqueID
from _fw.fwssys.fwcore.types.commontypes  import _CommonDefines
from _fw.fwssys.fwcore.types.commontypes  import _EDepInjCmd

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

@unique
class _EXcoXcpType(Enum):
    eVSystemExitException   = 10
    eDieException           = 11
    eLogException           = 12
    eInternalErrorException = 13

    eXTaskException         = 40
    eXTaskDieException      = 41

    eBaseException                  = 100
    eBaseExceptionAssertionErrorr   = 101
    eBaseExceptionAttributeError    = 102
    eBaseExceptionNameError         = 103
    eBaseExceptionOSError           = 104
    eBaseExceptionPermissionError   = 105
    eBaseExceptionSyntaxError       = 106
    eBaseExceptionSystemError       = 107
    eBaseExceptionSystemExit        = 108
    eBaseExceptionTypeError         = 109
    eBaseExceptionFileNotFoundError = 110
    eBaseExceptionKeyboardInterrupt = 111
    eBaseExceptionVSystemExit       = 112

    @property
    def compactName(self):
        idx = 1
        if self.value > _EXcoXcpType.eBaseException.value:
            if self.name.find(_EXcoXcpType.eBaseException.name)==0:
                idx = len(_EXcoXcpType.eBaseException.name)
        return self.name[idx:]

    @property
    def isXTaskException(self):
        return self==_EXcoXcpType.eXTaskException

    @property
    def isXTaskDieException(self):
        return self==_EXcoXcpType.eXTaskDieException

    @property
    def isLogException(self):
        return self==_EXcoXcpType.eLogException

    @property
    def isDieException(self):
        return self==_EXcoXcpType.eDieException

    @property
    def isInternalErrorException(self):
        return self==_EXcoXcpType.eInternalErrorException

    @property
    def isVSystemExitException(self):
        return self==_EXcoXcpType.eVSystemExitException

    @property
    def isBaseException(self):
        return self.value >= _EXcoXcpType.eBaseException.value

    @property
    def isBaseExceptionAssertionError(self):
        return self==_EXcoXcpType.eBaseExceptionAssertionErrorr

    @property
    def isBaseExceptionAtrributeError(self):
        return self==_EXcoXcpType.eBaseExceptionAttributeError

    @property
    def isBaseExceptionNameError(self):
        return self==_EXcoXcpType.eBaseExceptionNameError

    @property
    def isBaseExceptionOSError(self):
        return self==_EXcoXcpType.eBaseExceptionOSError

    @property
    def isBaseExceptionPermissionError(self):
        return self==_EXcoXcpType.eBaseExceptionPermissionError

    @property
    def isBaseExceptionSyntaxError(self):
        return self==_EXcoXcpType.eBaseExceptionSyntaxError

    @property
    def isBaseExceptionSystemError(self):
        return self==_EXcoXcpType.eBaseExceptionSystemError

    @property
    def isBaseExceptionSystemExit(self):
        return self==_EXcoXcpType.eBaseExceptionSystemExit

    @property
    def isBaseExceptionTypeError(self):
        return self==_EXcoXcpType.eBaseExceptionTypeError

    @property
    def isBaseExceptionFileNotFoundError(self):
        return self==_EXcoXcpType.eBaseExceptionFileNotFoundError

    @property
    def isBaseExceptionKeyboardInterrupt(self):
        return self==_EXcoXcpType.eBaseExceptionKeyboardInterrupt

    @property
    def isBaseExceptionUspecified(self):
        return self==_EXcoXcpType.eBaseException

    @property
    def isBaseExceptionVSystemExit(self):
        return self==_EXcoXcpType.eBaseExceptionVSystemExit

class _XcoXcpRootBase(Exception):
    def __init__(self, xcpMsg_ : str =None):
        super().__init__(xcpMsg_)

    @property
    def isDieException(self):
        pass

    @property
    def uniqueID(self) -> int:
        pass

    @property
    def message(self) -> str:
        pass

    @property
    def errorCode(self) -> int:
        pass

    @property
    def callstack(self) -> str:
        pass

    @property
    def traceback(self) -> str:
        pass

class _XcoXcpRootImpl(_XcoXcpRootBase):
    def __init__(self, eXcpType_ : _EXcoXcpType =None, xcpMsg_ : str =None, tb_ : str =None, cst_ : str =None):
        self._tb       = tb_
        self._cst      = cst_
        self._xcpMsg   = xcpMsg_
        self._eXcpType = eXcpType_
        super().__init__(xcpMsg_)

    @property
    def isXTaskException(self):
        return False if self._eXcpType is None else self._eXcpType.isXTaskException or self._eXcpType.isXTaskDieException

    @property
    def isXTaskDieException(self):
        return False if self._eXcpType is None else self._eXcpType.isXTaskDieException

    @property
    def _message(self):
        return self._xcpMsg

    @property
    def _callstack(self) -> str:
        return self._cst

    @property
    def _traceback(self) -> str:
        return self._tb

    @property
    def _exceptionTypeName(self):
        return None if self._eXcpType is None else self._eXcpType.compactName

    @property
    def _eExceptionType(self) -> _EXcoXcpType:
        return self._eXcpType

class _XcoException(_XcoXcpRootImpl):
    __releaseModeEnabled = True

    def __init__(self, eXcpType_ : _EXcoXcpType =None, xcpMsg_ : str =None, tb_ : str =None, enclXcp_ : BaseException =None):
        self.__enclXcp  = None

        if not isinstance(eXcpType_, _EXcoXcpType):
            super().__init__()
            _XcoException._RaiseSystemExit(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoException_TID_001).format(str(eXcpType_)))
            return
        if (xcpMsg_ is not None) and not isinstance(xcpMsg_, str):
            super().__init__()
            _XcoException._RaiseSystemExit(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoException_TID_002).format(eXcpType_.name, str(xcpMsg_)))
            return
        if (tb_ is not None) and not isinstance(tb_, str):
            super().__init__()
            _XcoException._RaiseSystemExit(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoException_TID_003).format(eXcpType_.name, str(tb_)))
            return

        if enclXcp_ is not None:
            if not isinstance(enclXcp_, (_XcoException, BaseException)):
                super().__init__()
                _XcoException._RaiseSystemExit(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoException_TID_004).format(eXcpType_.name, str(enclXcp_)))
                return

            _bXcoXcp = isinstance(enclXcp_, _XcoException)
            if isinstance(enclXcp_, _XcoException) and not (enclXcp_.isLogException or enclXcp_.isVSystemExitException):
                super().__init__()
                _XcoException._RaiseSystemExit(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoException_TID_005).format(eXcpType_.name, str(enclXcp_)))
                return

            if xcpMsg_ is None:
                if isinstance(enclXcp_, _XcoException):
                    xcpMsg_ = enclXcp_.shortMessage
                else:
                    xcpMsg_ = str(enclXcp_)

        if (xcpMsg_ is None) or (len(xcpMsg_) == 0):
            xcpMsg_ = '-'

        self.__enclXcp = enclXcp_
        super().__init__(eXcpType_, xcpMsg_, tb_)

    def __str__(self):
        return self.ToString()

    def __eq__(self, rhs_):
        _a = getattr(self, _FwTDbEngine.GetText(_EFwTextID.ePreDefinedMethod_IsEqual), None)
        if _a is None:
            res = id(self) == id(rhs_)
        else:
            res = _a(rhs_)
        return res

    @property
    def isLogException(self):
        return False if self.xcpType is None else self.xcpType.isLogException

    @property
    def isDieException(self):
        return False if self.xcpType is None else self.xcpType.isDieException

    @property
    def isInternalErrorException(self):
        return False if self.xcpType is None else self.xcpType.isInternalErrorException

    @property
    def isVSystemExitException(self):
        return False if self.xcpType is None else self.xcpType.isVSystemExitException

    @property
    def isXcoBaseException(self):
        return False if self.xcpType is None else self.xcpType.isBaseException

    @property
    def isClone(self):
        return self._isClone

    @property
    def uniqueID(self) -> int:
        return self._uniqueID

    @property
    def dtaskUID(self):
        return self._taskID

    @property
    def dtaskName(self):
        return self._taskName

    @property
    def xcpTypeName(self):
        return self._exceptionTypeName

    @property
    def xcpType(self) -> _EXcoXcpType:
        return self._eExceptionType

    @property
    def message(self):
        return self._message

    @property
    def shortMessage(self):
        return self._xcpMsg

    @property
    def traceback(self) -> str:
        return self._traceback

    @property
    def callstack(self) -> str:
        return self._callstack

    @property
    def errorCode(self) -> int:
        res = None
        if self.uniqueID is None:
            pass
        elif self.isLogException:
            if self._enclosedFatalEntry is not None:
                res = self._enclosedFatalEntry.errorCode
        elif self.isDieException:
            if self._enclosedLogException is not None:
                res = self._enclosedLogException.errorCode
        return res

    def Clone(self):
        return self._Clone()

    def ToString(self):
        return self._ToString()

    def CleanUp(self):
        self._CleanUp()

    @staticmethod
    def _RaiseSystemExit(msg_):
        if not _XcoException.__releaseModeEnabled:
            raise SystemExit(msg_)

    @staticmethod
    def _DepInjection(dinjCmd_ : _EDepInjCmd, bRelMode_ : bool):
        _XcoException.__releaseModeEnabled = bRelMode_

    @property
    def _isClone(self):
        return False

    @property
    def _uniqueID(self) -> int:
        return None

    @property
    def _taskID(self):
        return None

    @property
    def _taskName(self):
        return None

    @property
    def _enclosedFatalEntry(self):
        res = self._enclosedLogException
        if res is not None:
            res = res._enclosedFatalEntry
        return res

    @property
    def _enclosedException(self):
        if isinstance(self.__enclXcp, _XcoException):
            if self.__enclXcp.uniqueID is None:
                self.__enclXcp = None
        return self.__enclXcp

    @property
    def _enclosedLogException(self):
        res = self._enclosedException
        if not isinstance(res, _XcoException):
            res = None
        return res

    @property
    def _nestedLogException(self):
        return None

    def _ToString(self):
        return self.message

    def _CleanUp(self):
        if self._eXcpType is not None:
            if isinstance(self.__enclXcp, _XcoException):
                self.__enclXcp.CleanUp()
            self._tb       = None
            self._xcpMsg   = None
            self._eXcpType = None
            self.__enclXcp = None

    def _Clone(self):
        return None

    def _SetEnclosedLogException(self, enclXcp_ : Exception):
        if self.__enclXcp is not None:
            _XcoException._RaiseSystemExit(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoException_TID_006).format(self.ToString()))
        elif not (isinstance(enclXcp_, _XcoException) and enclXcp_.isLogException):
            _XcoException._RaiseSystemExit(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoException_TID_007).format(self.xcpType.compactName, str(enclXcp_)))
        else:
            self.__enclXcp = enclXcp_

class _XcoBaseException(_XcoException):
    def __init__(self, baseXcp_ :  BaseException, tb_ : str =None, taskID_ : int =None):
        if isinstance(baseXcp_, _XcoException) and not baseXcp_.isVSystemExitException:
            _XcoException._RaiseSystemExit(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoException_TID_008).format(str(baseXcp_)))
        elif not isinstance(baseXcp_, BaseException):
            _XcoException._RaiseSystemExit(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XcoException_TID_009).format(str(baseXcp_)))
        else:
            self.__taskID   = taskID_
            self.__uniqueID = _LogUniqueID._GetNextUniqueID()

            if isinstance(baseXcp_, _XcoException):
                _xt = _EXcoXcpType.eBaseExceptionVSystemExit
            else:
                _xt = _XcoBaseException.__GetBaseExceptionType(baseXcp_)
            super().__init__(_xt, tb_=tb_, enclXcp_=baseXcp_)

    @property
    def _uniqueID(self) -> int:
        return self.__uniqueID

    @property
    def _taskID(self):
        return self.__taskID

    def _IsEqual(self, rhs_):
        res  = rhs_ is not None
        if res and (rhs_.xcpType is not None):
            res &= self.xcpType     == rhs_.xcpType
            res &= self.message            == rhs_.message
            res &= self.traceback          == rhs_.traceback
            res &= self._enclosedException == rhs_._enclosedException
        return res

    def _SetTaskID(self, taskID_ : int):
        if self.__taskID is None:
            self.__taskID = taskID_

    def _Clone(self):
        res = None
        if self.xcpType is not None:
            res = _XcoBaseException(self._enclosedException, tb_=self.traceback, taskID_=self.dtaskUID)
            if res.xcpType is None:
                res.CleanUp()
                res = None
            else:
                res.__taskID = self.dtaskUID
                res.__uniqueID = self.uniqueID
        return res

    def _ToString(self):
        res = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_010).format(self.uniqueID)
        if self.dtaskUID is not None:
            res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_010).format(self.dtaskUID)
        _midPart  = None if self._enclosedException is None else type(self._enclosedException).__name__
        if _midPart is None:
            _midPart = self.xcpType.compactName
        _midPart2 = _CommonDefines._CHAR_SIGN_DASH if self.traceback is None else self.traceback
        res += _FwTDbEngine.GetText(_EFwTextID.eXcoException_XcoBaseException_ToString_01).format(_midPart, self.message, _midPart2)
        return res

    def _CleanUp(self):
        if self.__uniqueID is not None:
            self.__taskID   = None
            self.__uniqueID = None
            super()._CleanUp()

    @staticmethod
    def __GetBaseExceptionType(baseXcp_ : BaseException):
        if isinstance(baseXcp_, AssertionError):
            res = _EXcoXcpType.eBaseExceptionAssertionErrorr
        elif isinstance(baseXcp_, AttributeError):
            res = _EXcoXcpType.eBaseExceptionAttributeError
        elif isinstance(baseXcp_, PermissionError):
            res = _EXcoXcpType.eBaseExceptionPermissionError
        elif isinstance(baseXcp_, NameError):
            res = _EXcoXcpType.eBaseExceptionNameError
        elif isinstance(baseXcp_, OSError):
            res = _EXcoXcpType.eBaseExceptionOSError
        elif isinstance(baseXcp_, SyntaxError):
            res = _EXcoXcpType.eBaseExceptionSyntaxError
        elif isinstance(baseXcp_, SystemError):
            res = _EXcoXcpType.eBaseExceptionSystemError
        elif isinstance(baseXcp_, SystemExit):
            res = _EXcoXcpType.eBaseExceptionSystemExit
        elif isinstance(baseXcp_, TypeError):
            res = _EXcoXcpType.eBaseExceptionTypeError
        elif isinstance(baseXcp_, FileNotFoundError):
            res = _EXcoXcpType.eBaseExceptionFileNotFoundError
        elif isinstance(baseXcp_, KeyboardInterrupt):
            res = _EXcoXcpType.eBaseExceptionKeyboardInterrupt
        else:
            res = _EXcoXcpType.eBaseException
        return res

class _XTaskXcpImpl(_XcoXcpRootImpl):
    def __init__(self, *, uid_ : int =None, xm_ : str =None, ec_ : int =None, tb_ : str =None, cst_ : str =None, bDieXcp_ =False, clone_ : _XcoXcpRootImpl =None):
        if clone_ is not None:
            xm_  = clone_._message
            ec_  = clone_.errorCode
            tb_  = clone_._traceback
            cst_ = clone_._callstack
            uid_ = clone_.uniqueID
            _xt  = _EXcoXcpType.eXTaskDieException if clone_.isXTaskDieException else _EXcoXcpType.eXTaskException
        else:
            _xt = _EXcoXcpType.eXTaskDieException if bDieXcp_ else _EXcoXcpType.eXTaskException

        self.__ec  = ec_
        self.__uid = uid_
        super().__init__(_xt, xm_, tb_, cst_)

    def __str__(self):
        return self.__ToString()

    @property
    def _isDieException(self):
        return self.isXTaskDieException

    @property
    def _uniqueID(self) -> int:
        return self.__uid

    @property
    def _errorCode(self) -> int:
        return self.__ec

    def __ToString(self) -> str:
        res = _FwTDbEngine.GetText(_EFwTextID.eXcoException_XTaskExceptionBase_ToString_01).format(self._uniqueID)
        if self._errorCode is not None:
            if not _LogErrorCode.IsAnonymousErrorCode(self._errorCode):
                res += f'[{self._errorCode}]'
        res += f' {self._message}'
        if self._callstack is not None:
            res += _FwTDbEngine.GetText(_EFwTextID.eLogEntry_ToString_01).format(self._callstack.rstrip())
        return res

class _XTaskXcpBase(_XcoXcpRootBase):
    def __init__(self, xcp_ : Exception):
        self.__xcp = None if not isinstance(xcp_, _XTaskXcpImpl) else xcp_
        super().__init__()

    def __str__(self):
        return _CommonDefines._STR_EMPTY if self.__isInvalid else str(self.__impl)

    @property
    def isDieException(self):
        return False if self.__isInvalid else self.__impl._isDieException

    @property
    def uniqueID(self) -> int:
        return 0 if self.__isInvalid else  self.__impl._uniqueID

    @property
    def message(self) -> str:
        return _CommonDefines._STR_EMPTY if self.__isInvalid else  self.__impl._message

    @property
    def errorCode(self) -> int:
        return 0 if self.__isInvalid else  self.__impl._errorCode

    @property
    def callstack(self) -> str:
        return _CommonDefines._STR_EMPTY if self.__isInvalid else  self.__impl._callstack

    @property
    def traceback(self) -> str:
        return _CommonDefines._STR_EMPTY if self.__isInvalid else  self.__impl._traceback

    @property
    def __impl(self) -> Union[_XTaskXcpImpl, None]:
        return None if not isinstance(self.__xcp, _XTaskXcpImpl) else self.__xcp

    @property
    def __isInvalid(self):
        return self.__xcp is None

def _IsLogXcp(x_ : Exception):
    return isinstance(x_, _XcoException) and x_.isLogException

def _IsXTXcp(x_ : Exception):
    return isinstance(x_, _XTaskXcpBase)

def _IsXTDieXcp(x_ : Exception):
    return isinstance(x_, _XTaskXcpBase) and x_.isDieException
