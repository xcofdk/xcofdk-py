# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : sigcheck.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum    import auto
from enum    import unique
from enum    import IntEnum
from inspect import isfunction as _PyIsFunction
from inspect import ismethod   as _PyIsMethod
from inspect import Parameter  as _PyParameter
from inspect import Signature  as _PySignature

from _fw.fwssys.fwcore.logging           import logif
from _fw.fwssys.fwcore.types.commontypes import _CommonDefines

from _fw.fwssys.fwerrh.fwerrorcodes import _EFwErrorCode

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

@unique
class _EPredefinedCallableID(IntEnum):
    eDontCare     = 0
    eSetupXtbl    = auto()
    eTearDownXtbl = auto()
    eRunXtbl      = auto()
    eProcExtMsg   = auto()
    eProcIntMsg   = auto()
    eXProcessTgt  = auto()

    def compactName(self):
        return self.name[1:]

    @property
    def isDontCare(self):
        return self == _EPredefinedCallableID.eDontCare

    @property
    def isSetupExecutable(self):
        return self == _EPredefinedCallableID.eSetupXtbl

    @property
    def isTearDownExecutable(self):
        return self == _EPredefinedCallableID.eTearDownXtbl

    @property
    def isRunExecutable(self):
        return self == _EPredefinedCallableID.eRunXtbl

    @property
    def isProcessExternalMessage(self):
        return self == _EPredefinedCallableID.eProcExtMsg

    @property
    def isProcessInternalMessage(self):
        return self == _EPredefinedCallableID.eProcIntMsg

    @property
    def isXProcessTarget(self):
        return self == _EPredefinedCallableID.eXProcessTgt

class _CallableSignature(_PySignature):
    __slots__ = [ '__cid' ]

    def __init__(self, parameters=None, *, return_annotation=_PySignature.empty, __validate_parameters__=True):
        self.__cid = None
        super().__init__(parameters, return_annotation=return_annotation, __validate_parameters__=__validate_parameters__)

    def __str__(self):
        if self.__cid is None:
            return None
        return _FwTDbEngine.GetText(_EFwTextID.eCallableSignature_ToString_01).format(self.__cid.compactName, _PySignature.__str__(self))

    @staticmethod
    def IsCallback(callable_, bCheckOnMethodOrFunc_ =True):
        res = callable(callable_)
        if bCheckOnMethodOrFunc_:
            res = _PyIsMethod(callable_) or _PyIsFunction(callable_)
        return res

    @staticmethod
    def IsFunction(callable_):
        return callable(callable_) and _PyIsFunction(callable_)

    @staticmethod
    def IsInstanceMethod(callable_):
        return callable(callable_) and _PyIsMethod(callable_)

    @staticmethod
    def IsSignatureMatchingRunExecutableCallback(callable_, bDoLogOnError_ =True):
        return _CallableSignature.CheckSignature(_EPredefinedCallableID.eRunXtbl, callable_, bDoLogOnError_=bDoLogOnError_)

    @staticmethod
    def IsSignatureMatchingSetupExecutableCallback(callable_, bDoLogOnError_ =True):
        return _CallableSignature.CheckSignature(_EPredefinedCallableID.eSetupXtbl, callable_, bDoLogOnError_=bDoLogOnError_)

    @staticmethod
    def IsSignatureMatchingTearDownExecutableCallback(callable_, bDoLogOnError_ =True):
        return _CallableSignature.CheckSignature(_EPredefinedCallableID.eTearDownXtbl, callable_, bDoLogOnError_=bDoLogOnError_)

    @staticmethod
    def IsSignatureMatchingProcessExternalMessageCallback(callable_, bDoLogOnError_ =True):
        return _CallableSignature.CheckSignature(_EPredefinedCallableID.eProcExtMsg, callable_, bDoLogOnError_=bDoLogOnError_)

    @staticmethod
    def IsSignatureMatchingProcessInternalMessageCallback(callable_, bDoLogOnError_ =True):
        return _CallableSignature.CheckSignature(_EPredefinedCallableID.eProcIntMsg, callable_, bDoLogOnError_=bDoLogOnError_)

    @staticmethod
    def IsSignatureMatchingXProcessTargetCallback(callable_, bDoLogOnError_ =True):
        return _CallableSignature.CheckSignature(_EPredefinedCallableID.eXProcessTgt, callable_, bDoLogOnError_=bDoLogOnError_)

    @staticmethod
    def CheckSignature(callableID_ : _EPredefinedCallableID, callable_, bDoLogOnError_ =True) -> bool:
        _sig = _CallableSignature.__CreateInstance(callableID_, callable_)
        if _sig is None:
            res = False
        else:
            res  = _sig.__CheckSignature()
            _sig = None

        if not res:
            if bDoLogOnError_:
                _CallableSignature.__DoLogError(callableID_, callable_)
        return res

    @staticmethod
    def CheckSignatureParamsCount(callable_, minPosParamsCount_ : int, bIgnoreTail_ : bool, bDoLogOnError_ =False) -> bool:
        _sig = _CallableSignature.__CreateInstance(_EPredefinedCallableID.eDontCare, callable_, bCheckOnMethodOrFunc_=False)
        if _sig is None:
            res = False
        else:
            res  = _sig.__CheckSignatureParamsCount(minPosParamsCount_, bIgnoreTail_)
            _sig = None

        if not res:
            if bDoLogOnError_:
                _CallableSignature.__DoLogError(_EPredefinedCallableID.eDontCare, callable_, bCheckOnMethodOrFunc_=False)
        return res

    @property
    def callableID(self) -> _EPredefinedCallableID:
        return self.__cid

    @property
    def __requiredParamsCount(self) -> int:
        if self.callableID.isProcessExternalMessage or self.callableID.isProcessInternalMessage:
            res = 1
        else:
            res = 0
        return res

    @staticmethod
    def __CreateInstance(callableID_ : _EPredefinedCallableID, callable_, bCheckOnMethodOrFunc_ =True):
        if not _CallableSignature.IsCallback(callable_, bCheckOnMethodOrFunc_=bCheckOnMethodOrFunc_):
            res = None
        else:
            res = _CallableSignature.from_callable(callable_)
            if not isinstance(res, _CallableSignature):
                res = None
            else:
                res.__cid = callableID_
        return res

    @staticmethod
    def __IsParamOptional(param_ : _PyParameter):
        return (param_.kind == _PyParameter.VAR_POSITIONAL) or (param_.kind == _PyParameter.VAR_KEYWORD) or (param_.default != _PyParameter.empty)

    @staticmethod
    def __DoLogError(callableID_: _EPredefinedCallableID, callable_, bCheckOnMethodOrFunc_ =True):
        if callableID_.isDontCare or not _CallableSignature.IsCallback(callable_, bCheckOnMethodOrFunc_=bCheckOnMethodOrFunc_):
            _myMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_CallableSignature_TID_006).format(str(callable_))
        else:
            if callableID_.isSetupExecutable:
                _context     = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_CallableSignature_TID_001)
                _expectedSig = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_CallableSignature_TID_010)
            elif callableID_.isTearDownExecutable:
                _context     = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_CallableSignature_TID_002)
                _expectedSig = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_CallableSignature_TID_009)
            elif callableID_.isRunExecutable:
                _context     = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_CallableSignature_TID_003)
                _expectedSig = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_CallableSignature_TID_010)
            elif callableID_.isProcessExternalMessage:
                _context     = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_CallableSignature_TID_004)
                _expectedSig = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_CallableSignature_TID_011)
            elif callableID_.isProcessInternalMessage:
                _context     = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_CallableSignature_TID_005)
                _expectedSig = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_CallableSignature_TID_011)
            elif callableID_.isXProcessTarget:
                _context     = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_CallableSignature_TID_012)
                _expectedSig = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_CallableSignature_TID_013)
            else:
                _context     = _CommonDefines._STR_EMPTY
                _expectedSig = _CommonDefines._STR_EMPTY

            if _PyIsMethod(callable_):
                _callbackType = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_CallableSignature_TID_007)
            else:
                _callbackType = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_CallableSignature_TID_008)

            _myMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_CallableSignature_TID_014).format(_callbackType, _context, str(callable_), _expectedSig)
        logif._LogErrorEC(_EFwErrorCode.UE_00034, _myMsg)

    def __GetParameter(self, idx_ : int) -> _PyParameter:
        res = None

        _params = self.parameters
        if not ((idx_ < 0) or (idx_ >= len(_params))):
            _ii = 0
            for _vv in _params.values():
                if _ii == idx_:
                    res = _vv
                    break
                _ii += 1
        return res

    def __CheckSignature(self) -> bool:
        if self.callableID.isDontCare:
            return True

        _REQ_PARAMS_COUNT = self.__requiredParamsCount

        _params    = self.parameters
        _numParams = len(_params)

        if _numParams < _REQ_PARAMS_COUNT:
            return False

        res = True
        if not (self.callableID.isSetupExecutable or self.callableID.isRunExecutable or self.callableID.isXProcessTarget):
            for _ii in range(_REQ_PARAMS_COUNT, _numParams):
                _pp = self.__GetParameter(_ii)
                if not _CallableSignature.__IsParamOptional(_pp):
                    res = False
                break
        return res

    def __CheckSignatureParamsCount(self, minPosParamsCount_ : int, bIgnoreTail_ : bool) -> bool:
        if minPosParamsCount_ < 0:
            return True

        _params    = self.parameters
        _numParams = len(_params)

        res = True
        if _numParams < minPosParamsCount_:
            res = False

        elif not (bIgnoreTail_ or (_numParams == minPosParamsCount_)):
            for _ii in range(minPosParamsCount_, _numParams):
                _pp = self.__GetParameter(_ii)
                if not _CallableSignature.__IsParamOptional(_pp):
                    res = False
                break
        return res
