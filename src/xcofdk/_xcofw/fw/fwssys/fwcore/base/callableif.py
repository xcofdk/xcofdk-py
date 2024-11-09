# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : callableif.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


import sys
from   inspect import isfunction as _Isfunction
from   inspect import ismethod   as _Ismethod
from   inspect import ismodule   as _Ismodule
from   inspect import isclass    as _Isclass

from xcofdk._xcofw.fwadapter                           import rlogif
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject      import _AbstractSlotsObject
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes  import _CommonDefines
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes  import _FwIntEnum
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes  import unique

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine



@unique
class _EIFSpecType(_FwIntEnum):
    eInvalid            = 0
    eByFunction         = 1
    eByModuleFunction   = 2
    eByStaticMethod     = 3
    eByInstanceMethod   = 4
    eByCallableInstance = 5
    eByCallableIF       = 6

    @property
    def isValidSpec(self):
        return self != _EIFSpecType.eInvalid

    @property
    def isSpecifiedByStaticMethod(self):
        return self == _EIFSpecType.eByStaticMethod

    @property
    def isSpecifiedByInstanceMethod(self):
        return self == _EIFSpecType.eByInstanceMethod

    @property
    def isSpecifiedByCallableInstance(self):
        return self == _EIFSpecType.eByCallableInstance

    @property
    def isSpecifiedByFunction(self):
        return self == _EIFSpecType.eByFunction

    @property
    def isSpecifiedByModuleFunction(self):
        return self == _EIFSpecType.eByModuleFunction

    @property
    def isSpecifiedByCallableIF(self):
        return self == _EIFSpecType.eByCallableIF


class _CallableIF(_AbstractSlotsObject):

    __slots__ = [ '__callFunc' , '__ifsoruce' , '__ifSpecType' , '__callFuncName' ]

    def __init__(self, ifsource_, methodName_ : str =None, bThrowx_ =True, bWarn_ =True, cloneBy_ =None):

        self.__callFunc     = None
        self.__ifsoruce     = None
        self.__ifSpecType   = None
        self.__callFuncName = None
        super().__init__()

        if cloneBy_ is not None:
            if not (isinstance(cloneBy_, _CallableIF) and cloneBy_.isValid):
                self.CleanUp()
                rlogif._LogOEC(True, -1142)
            else:
                self.__callFunc     = cloneBy_.__callFunc
                self.__ifsoruce     = cloneBy_.__ifsoruce
                self.__ifSpecType   = cloneBy_.__ifSpecType
                self.__callFuncName = cloneBy_.__callFuncName
            return

        _callFunc     = None
        _ifsoruce     = None
        _ifSpecType   = None
        _callFuncName = None
        _ifSpecType, _ifsoruce, _callFunc, _callFuncName = _CallableIF.__EvaluateSpec(ifsource_, methodName_, bThrowx_, bWarn_)
        if not _ifSpecType.isValidSpec:
            pass
        elif _ifSpecType.isSpecifiedByCallableIF:
            self.__callFunc     = _ifsoruce.__callFunc
            self.__ifsoruce     = _ifsoruce.__ifsoruce
            self.__ifSpecType   = _ifsoruce.__ifSpecType
            self.__callFuncName = _ifsoruce.__callFuncName
        else:
            self.__callFunc     = _callFunc
            self.__ifsoruce     = _ifsoruce
            self.__ifSpecType   = _ifSpecType
            self.__callFuncName = _callFuncName

    def __eq__(self, other_):
        return not self.__ne__(other_)

    def __ne__(self, other_):
        res  = self.__callFunc     != other_.__callFunc
        res |= self.__ifsoruce     != other_.__ifsoruce
        res |= self.__ifSpecType   != other_.__ifSpecType
        res |= self.__callFuncName != other_.__callFuncName
        return res

    def __hash__(self):
        if not self.isValid:
            return None
        return hash(hash(self.__callFunc) + hash(self.__ifsoruce) + hash(self.__ifSpecType) + hash(self.__callFuncName))

    def __call__(self, *args_, **kwargs_):
        if self.__ifSpecType is None:
            rlogif._LogOEC(True, -1143)
            return

        res = None
        if self.__callFunc is None:
            rlogif._LogOEC(True, -1144)
        else:
            res = self.__callFunc(*args_, **kwargs_)
        return res

    @staticmethod
    def IsValidCallableSpec(ifsource_, methodName_ : str =None, bThrowx_ =False, bWarn_ =False):
        _callFunc     = None
        _ifsoruce     = None
        _ifSpecType   = None
        _callFuncName = None
        _ifSpecType, _ifsoruce, _callFunc, _callFuncName = _CallableIF.__EvaluateSpec(ifsource_, methodName_=methodName_, bThrowx_=bThrowx_, bWarn_=bWarn_)
        return _ifSpecType.isValidSpec

    @staticmethod
    def GetCallableSpecType(ifsource_, methodName_ : str =None, bThrowx_ =False, bWarn_ =False) -> _EIFSpecType:
        _callFunc     = None
        _ifsoruce     = None
        _ifSpecType   = None
        _callFuncName = None
        _ifSpecType, _ifsoruce, _callFunc, _callFuncName = _CallableIF.__EvaluateSpec(ifsource_, methodName_=methodName_, bThrowx_=bThrowx_, bWarn_=bWarn_)
        return _ifSpecType

    @staticmethod
    def CreateInstance(ifsource_, methodName_ : str =None, bWarn_ : bool =True):

        res = _CallableIF(ifsource_, methodName_, bThrowx_=False, bWarn_=bWarn_)
        if not res.isValid:
            res = None
        return res

    @property
    def isValid(self):
        return self.__ifSpecType is not None

    @property
    def ifSpecType(self) -> _EIFSpecType:
        return self.__ifSpecType

    @property
    def isSpecifiedByStaticMethod(self):
        return self.isValid and self.__ifSpecType.isSpecifiedByStaticMethod

    @property
    def isSpecifiedByInstanceMethod(self):
        return self.isValid and self.__ifSpecType.isSpecifiedByInstanceMethod

    @property
    def isSpecifiedByCallableInstance(self):
        return self.isValid and self.__ifSpecType.isSpecifiedByCallableInstance

    @property
    def isSpecifiedByFunction(self):
        return self.isValid and self.__ifSpecType.isSpecifiedByFunction

    @property
    def isSpecifiedByModuleFunction(self):
        return self.isValid and self.__ifSpecType.isSpecifiedByModuleFunction

    @property
    def ifsoruce(self):
        return self.__ifsoruce

    @property
    def methodName(self):
        return self.__callFuncName

    def Clone(self):
        if not self.isValid:
            return None
        res = _CallableIF(self.__ifsoruce, cloneBy_=self)
        if not res.isValid:
            res.CleanUp()
            res = None
        return res

    def _CleanUp(self):
        self.__callFunc     = None
        self.__ifsoruce     = None
        self.__ifSpecType   = None
        self.__callFuncName = None

    def _ToString(self, *args_, **kwargs_):
        res = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_005).format(type(self).__name__, self.__ifSpecType.compactName)
        if self.methodName is not None:
            res +=  _FwTDbEngine.GetText(_EFwTextID.eCallableIF_ToString_01).format(self.methodName)
        return res

    @staticmethod
    def __EvaluateSpec(ifsource_, methodName_ : str =None, bThrowx_ =True, bWarn_ =True):
        _callFunc     = None
        _ifsoruce     = None
        _ifSpecType   = None
        _callFuncName = None
        _failedRes    = _EIFSpecType.eInvalid, None, None, None

        if isinstance(ifsource_, _CallableIF):
            if not ifsource_.isValid:
                return _failedRes
            else:
                return _EIFSpecType.eByCallableIF, ifsource_, None, None

        if ifsource_ is None:
            if bThrowx_:
                rlogif._LogOEC(True, -1145)
            return _failedRes

        if methodName_ is not None:
            if not isinstance(methodName_, str):
                rlogif._LogOEC(True, -1146)
                return _failedRes

        if _Isfunction(ifsource_):
            _ifSpecType   = _EIFSpecType.eByFunction
            _callFunc     = ifsource_
            _ifsoruce     = ifsource_
            _callFuncName = ifsource_.__name__
            if methodName_ is not None:
                if bWarn_:
                    rlogif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_CallableIF_TextID_004).format(str(methodName_)))

        elif _Ismethod(ifsource_):
            _ifSpecType   = _EIFSpecType.eByInstanceMethod
            _callFunc     = ifsource_
            _ifsoruce     = ifsource_.__self__
            _callFuncName = ifsource_.__name__
            if methodName_ is not None:
                if bWarn_:
                    rlogif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_CallableIF_TextID_004).format(str(methodName_)))

        elif isinstance(methodName_, str):
            if isinstance(ifsource_, str):
                if not ifsource_ in sys.modules:
                    if bThrowx_:
                        rlogif._LogOEC(True, -1147)
                    return _failedRes
                ifsource_ = sys.modules[ifsource_]

            _specDetails = _CommonDefines._STR_EMPTY

            _attrVal = getattr(ifsource_, methodName_, None)

            if _attrVal is None or not (_Ismethod(_attrVal) or _Isfunction(_attrVal)):
                if bThrowx_:
                    rlogif._LogOEC(True, -1148)
                return _failedRes

            _callFunc     = _attrVal
            _ifsoruce     = ifsource_
            _callFuncName = str(methodName_)

            if _Isfunction(_attrVal):
                if _Ismodule(ifsource_):
                    _ifSpecType = _EIFSpecType.eByModuleFunction
                elif _Isclass(ifsource_):
                    _ifSpecType = _EIFSpecType.eByStaticMethod
                else:
                    rlogif._LogOEC(True, -1149)
                    return _failedRes

            elif _Ismethod(_attrVal):
                if _Isclass(ifsource_):
                    _ifSpecType = _EIFSpecType.eByStaticMethod
                else:
                    _ifSpecType = _EIFSpecType.eByInstanceMethod

            else:
                rlogif._LogOEC(True, -1150)
                return _failedRes

        elif isinstance(ifsource_, object) and getattr(ifsource_, _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_Builtin_FuncName_Call), None) is not None:
            _ifSpecType   = _EIFSpecType.eByCallableInstance
            _callFunc     = ifsource_
            _ifsoruce     = ifsource_
            _callFuncName = ifsource_.__class__.__name__
            if methodName_ is not None:
                if bWarn_:
                    rlogif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_CallableIF_TextID_008).format(methodName_))

        else:
            if bThrowx_:
                rlogif._LogOEC(True, -1151)
            return _failedRes

        return _ifSpecType, _ifsoruce, _callFunc, _callFuncName
