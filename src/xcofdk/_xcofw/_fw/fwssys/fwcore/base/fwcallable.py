# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwcallable.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

import sys
from   inspect import isfunction as _PyIsFunction
from   inspect import ismethod   as _PyIsMethod
from   inspect import ismodule   as _PyIsModule
from   inspect import isclass    as _PyIsClass

from _fwadapter                           import rlogif
from _fw.fwssys.fwcore.types.aobject      import _AbsSlotsObject
from _fw.fwssys.fwcore.types.commontypes  import _CommonDefines
from _fw.fwssys.fwcore.types.commontypes  import _FwIntEnum
from _fw.fwssys.fwcore.types.commontypes  import unique

from _fw.fwssys.fwerrh.fwerrorcodes import _EFwErrorCode

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

@unique
class _ECIFSpecType(_FwIntEnum):
    eInvalid            = 0
    eByFunction         = 1
    eByModuleFunction   = 2
    eByStaticMethod     = 3
    eByInstanceMethod   = 4
    eByCallableIF       = 5
    eByCallableInstance = 6
    eByCallableClass    = 7

    @property
    def isValidSpec(self):
        return self != _ECIFSpecType.eInvalid

    @property
    def isSpecifiedByStaticMethod(self):
        return self == _ECIFSpecType.eByStaticMethod

    @property
    def isSpecifiedByInstanceMethod(self):
        return self == _ECIFSpecType.eByInstanceMethod

    @property
    def isSpecifiedByFunction(self):
        return self == _ECIFSpecType.eByFunction

    @property
    def isSpecifiedByModuleFunction(self):
        return self == _ECIFSpecType.eByModuleFunction

    @property
    def isSpecifiedByCallableIF(self):
        return self == _ECIFSpecType.eByCallableIF

    @property
    def isSpecifiedByCallableInstance(self):
        return self == _ECIFSpecType.eByCallableInstance

    @property
    def isSpecifiedByCallableClass(self):
        return self == _ECIFSpecType.eByCallableClass

class _FwCallable(_AbsSlotsObject):
    __slots__ = [ '__f' , '__s' , '__st' , '__fn' ]

    def __init__(self, ifsource_, methodName_ : str =None, bThrowx_ =True, bWarn_ =True, cloneBy_ =None):
        self.__f  = None
        self.__s  = None
        self.__fn = None
        self.__st = None
        super().__init__()

        if cloneBy_ is not None:
            if not (isinstance(cloneBy_, _FwCallable) and cloneBy_.isValid):
                self.CleanUp()
                rlogif._LogOEC(True, _EFwErrorCode.FE_00070)
            else:
                self.__f  = cloneBy_.__f
                self.__s  = cloneBy_.__s
                self.__fn = cloneBy_.__fn
                self.__st = cloneBy_.__st
            return

        _callFunc     = None
        _ifsoruce     = None
        _ifSpecType   = None
        _callFuncName = None
        _ifSpecType, _ifsoruce, _callFunc, _callFuncName = _FwCallable.__EvaluateSpec(ifsource_, methodName_, bThrowx_, bWarn_)
        if not _ifSpecType.isValidSpec:
            pass
        elif _ifSpecType.isSpecifiedByCallableIF:
            self.__f  = _ifsoruce.__f
            self.__s  = _ifsoruce.__s
            self.__st = _ifsoruce.__st
            self.__fn = _ifsoruce.__fn
        else:
            self.__f  = _callFunc
            self.__s  = _ifsoruce
            self.__fn = _callFuncName
            self.__st = _ifSpecType

    def __eq__(self, other_):
        return not self.__ne__(other_)

    def __ne__(self, other_):
        res  = self.__f  != other_.__f
        res |= self.__s  != other_.__s
        res |= self.__fn != other_.__fn
        res |= self.__st != other_.__st
        return res

    def __hash__(self):
        if not self.isValid:
            return None
        return hash(hash(self.__f) + hash(self.__s) + hash(self.__st) + hash(self.__fn))

    def __call__(self, *args_, **kwargs_):
        if self.__st is None:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00071)
            return

        res = None
        if self.__f is None:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00562)
        elif self.__st.isSpecifiedByCallableClass:
            _inst = None if len(args_)<1 else args_[0]
            if not isinstance(_inst, self.__s):
                _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_CallableIF_TID_011).format(self.__fn, self.__st.compactName)
                rlogif._LogOEC(True, _EFwErrorCode.FE_00931)
            else:
                args_ = args_[1:]
                _inst(*args_, **kwargs_)
        else:
            res = self.__f(*args_, **kwargs_)
        return res

    @staticmethod
    def IsValidCallableSpec(ifsource_, methodName_ : str =None, bThrowx_ =False, bWarn_ =False):
        _callFunc     = None
        _ifsoruce     = None
        _ifSpecType   = None
        _callFuncName = None
        _ifSpecType, _ifsoruce, _callFunc, _callFuncName = _FwCallable.__EvaluateSpec(ifsource_, methodName_=methodName_, bThrowx_=bThrowx_, bWarn_=bWarn_)
        return _ifSpecType.isValidSpec

    @staticmethod
    def GetCallableSpecType(ifsource_, methodName_ : str =None, bThrowx_ =False, bWarn_ =False) -> _ECIFSpecType:
        _callFunc     = None
        _ifsoruce     = None
        _ifSpecType   = None
        _callFuncName = None
        _ifSpecType, _ifsoruce, _callFunc, _callFuncName = _FwCallable.__EvaluateSpec(ifsource_, methodName_=methodName_, bThrowx_=bThrowx_, bWarn_=bWarn_)
        return _ifSpecType

    @staticmethod
    def CreateInstance(ifsource_, methodName_ : str =None, bWarn_ : bool =True):
        res = _FwCallable(ifsource_, methodName_, bThrowx_=False, bWarn_=bWarn_)
        if not res.isValid:
            res = None
        return res

    @property
    def isValid(self):
        return self.__st is not None

    @property
    def ifSpecType(self) -> _ECIFSpecType:
        return self.__st

    @property
    def isSpecifiedByStaticMethod(self):
        return self.isValid and self.__st.isSpecifiedByStaticMethod

    @property
    def isSpecifiedByInstanceMethod(self):
        return self.isValid and self.__st.isSpecifiedByInstanceMethod

    @property
    def isSpecifiedByCallableInstance(self):
        return self.isValid and self.__st.isSpecifiedByCallableInstance

    @property
    def isSpecifiedByCallableClass(self):
        return self.isValid and self.__st.isSpecifiedByCallableClass

    @property
    def isSpecifiedByFunction(self):
        return self.isValid and self.__st.isSpecifiedByFunction

    @property
    def isSpecifiedByModuleFunction(self):
        return self.isValid and self.__st.isSpecifiedByModuleFunction

    @property
    def ifsoruce(self):
        return self.__s

    @property
    def callbackName(self):
        return self.__fn

    def Clone(self):
        if not self.isValid:
            return None
        res = _FwCallable(self.__s, cloneBy_=self)
        if not res.isValid:
            res.CleanUp()
            res = None
        return res

    def _CleanUp(self):
        self.__f  = None
        self.__s  = None
        self.__st = None
        self.__fn = None

    def _ToString(self):
        res = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_005).format(type(self).__name__, self.__st.compactName)
        if self.callbackName is not None:
            res +=  _FwTDbEngine.GetText(_EFwTextID.eFwCallable_ToString_01).format(self.callbackName)
        return res

    @property
    def _callbackFunction(self):
        return self.__f

    @staticmethod
    def __EvaluateSpec(ifsource_, methodName_ : str =None, bThrowx_ =True, bWarn_ =True):
        _callFunc     = None
        _ifsoruce     = None
        _ifSpecType   = None
        _callFuncName = None
        _failedRes    = _ECIFSpecType.eInvalid, None, None, None

        if isinstance(ifsource_, _FwCallable):
            if not ifsource_.isValid:
                return _failedRes
            else:
                return _ECIFSpecType.eByCallableIF, ifsource_, None, None

        if ifsource_ is None:
            if bThrowx_:
                rlogif._LogOEC(True, _EFwErrorCode.FE_00072)
            return _failedRes

        if methodName_ is not None:
            if not isinstance(methodName_, str):
                rlogif._LogOEC(True, _EFwErrorCode.FE_00073)
                return _failedRes

        if _PyIsFunction(ifsource_):
            _ifSpecType   = _ECIFSpecType.eByFunction
            _callFunc     = ifsource_
            _ifsoruce     = ifsource_
            _callFuncName = ifsource_.__name__
            if methodName_ is not None:
                if bWarn_:
                    rlogif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_CallableIF_TID_004).format(str(methodName_)))

        elif _PyIsMethod(ifsource_):
            _ifSpecType   = _ECIFSpecType.eByInstanceMethod
            _callFunc     = ifsource_
            _ifsoruce     = ifsource_.__self__
            _callFuncName = ifsource_.__name__
            if methodName_ is not None:
                if bWarn_:
                    rlogif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_CallableIF_TID_004).format(str(methodName_)))

        elif isinstance(methodName_, str):
            if isinstance(ifsource_, str):
                if not ifsource_ in sys.modules:
                    if bThrowx_:
                        rlogif._LogOEC(True, _EFwErrorCode.FE_00074)
                    return _failedRes
                ifsource_ = sys.modules[ifsource_]

            _specDetails = _CommonDefines._STR_EMPTY

            _attrVal = getattr(ifsource_, methodName_, None)
            if _attrVal is None or not (_PyIsMethod(_attrVal) or _PyIsFunction(_attrVal)):
                if bThrowx_:
                    rlogif._LogOEC(True, _EFwErrorCode.FE_00075)
                return _failedRes

            _callFunc     = _attrVal
            _ifsoruce     = ifsource_
            _callFuncName = str(methodName_)

            if _PyIsFunction(_attrVal):
                if _PyIsModule(ifsource_):
                    _ifSpecType = _ECIFSpecType.eByModuleFunction
                elif _PyIsClass(ifsource_):
                    _ifSpecType = _ECIFSpecType.eByStaticMethod
                else:
                    rlogif._LogOEC(True, _EFwErrorCode.FE_00076)
                    return _failedRes

            elif _PyIsMethod(_attrVal):
                if _PyIsClass(ifsource_):
                    _ifSpecType = _ECIFSpecType.eByStaticMethod
                else:
                    _ifSpecType = _ECIFSpecType.eByInstanceMethod

            else:
                rlogif._LogOEC(True, _EFwErrorCode.FE_00887)
                return _failedRes

        elif callable(ifsource_) and getattr(ifsource_, _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_Builtin_FuncName_Call), None) is not None:
            _bClass        = _PyIsClass(ifsource_)
            _ifSpecType    = _ECIFSpecType.eByCallableClass if _bClass else _ECIFSpecType.eByCallableInstance
            _callFunc      = ifsource_
            _ifsoruce      = ifsource_
            _callFuncName  = ifsource_.__name__ if _PyIsClass(ifsource_) else _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_Builtin_FuncName_Call)
            if methodName_ is not None:
                if bWarn_:
                    rlogif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_CallableIF_TID_004).format(methodName_))

        else:
            if bThrowx_:
                rlogif._LogOEC(True, _EFwErrorCode.FE_00077)
            return _failedRes

        return _ifSpecType, _ifsoruce, _callFunc, _callFuncName
