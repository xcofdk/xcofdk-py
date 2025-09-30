# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwpayload.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from typing import Union

from xcofdk.fwapi import IPayload

from _fw.fwssys.fwcore.logging           import logif
from _fw.fwssys.fwcore.types.commontypes import override
from _fw.fwssys.fwcore.types.aobject     import _AbsObject
from _fw.fwssys.fwcore.types.aobject     import _AbsSlotsObject
from _fw.fwssys.fwcore.types.apobject    import _ProtAbsObject
from _fw.fwssys.fwcore.types.apobject    import _ProtAbsSlotsObject
from _fw.fwssys.fwerrh.fwerrorcodes      import _EFwErrorCode

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _FwPayload(_AbsSlotsObject, IPayload):
    __slots__ = [ '__d' , '__bS' ]

    def __init__(self, cont_ : dict =None, bShallowCopy_ =True, bSkipSerDes_ =False):
        self.__d  = None
        self.__bS = None
        _AbsSlotsObject.__init__(self)
        IPayload.__init__(self)

        if cont_ is None:
            cont_ = dict()
        elif not isinstance(cont_, dict):
            self.CleanUp()
            logif._LogErrorEC(_EFwErrorCode.UE_00136, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Payload_TID_001).format(type(cont_).__name__))
        elif bShallowCopy_:
            cont_ = cont_.copy()
        self.__d  = cont_
        self.__bS = not bSkipSerDes_

    @staticmethod
    def CustomSerializePayload(payload_) -> bytes:
        return None

    @staticmethod
    def CustomDeserializePayload(dump_: bytes):
        return None

    @IPayload.isValidPayload.getter
    def isValidPayload(self) -> bool:
        return self.__d is not None

    @IPayload.isMarshalingRequired.getter
    def isMarshalingRequired(self) -> bool:
        return self.__bS

    @IPayload.isCustomMarshalingRequired.getter
    def isCustomMarshalingRequired(self):
        return False

    @IPayload.numParameters.getter
    def numParameters(self) -> int:
        return 0 if self.__d is None else len(self.__d)

    @override
    def IsIncludingParameter(self, paramkey_) -> bool:
        return False if self.__d is None else paramkey_ in self.__d

    @override
    def GetParameter(self, paramkey_):
        return self.__GetParameter(paramkey_, bRaiseExceptionOnKeyNotFound_=False)

    @override
    def DetachContainer(self) -> Union[dict, None]:
        res = self.__d
        self.__d = None
        return res

    @property
    def container(self) -> dict:
        return self.__d

    def GetParameterRaiseException(self, paramkey_):
        return self.__GetParameter(paramkey_, bRaiseExceptionOnKeyNotFound_=True)

    def AddParameter(self, paramkey_, paramval_):
        return self.__AddParameter(paramkey_, paramval_, bOverwrite_=True)

    def AddParameterNoOverwrite(self, paramkey_, paramval_):
        return self.__AddParameter(paramkey_, paramval_, bOverwrite_=False)

    def UpdateContainer(self, dictParams_: dict, bShallowCopy_ =True):
        return self.__UpdateContainer(dictParams_, bShallowCopy_=bShallowCopy_, bOverwrite_=True)

    def UpdateContainerNoOverwrite(self, dictParams_: dict, bShallowCopy_ =True):
        return self.__UpdateContainer(dictParams_, bShallowCopy_=bShallowCopy_, bOverwrite_=False)

    def _CleanUp(self):
        if self.__d is not None:
            _bSerDes = self.isMarshalingRequired
            if _bSerDes:
                for _kk in self.__d:
                    _vv = self.__d[_kk]
                    if isinstance(_vv, (_AbsObject, _AbsSlotsObject)):
                        if isinstance(_vv, (_ProtAbsObject, _ProtAbsSlotsObject)):
                            _vv.CleanUpByOwnerRequest(_vv._myPPass)
                        else:
                            _vv.CleanUp()
                self.__d.clear()

            self.__d  = None
            self.__bS = None

    def _ToString(self):
        pass

    def __GetParameter(self, paramkey_, bRaiseExceptionOnKeyNotFound_ =False):
        if (self.__d is None) or paramkey_ not in self.__d:
            res = None
        else:
            res = self.__d[paramkey_]

        if res is None:
            if bRaiseExceptionOnKeyNotFound_:
                raise KeyError(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_Payload_TID_002).format(paramkey_))
        return res

    def __AddParameter(self, paramkey_, paramval_, bOverwrite_ =True) -> bool:
        if self.__d is None:
            return False
        if (not bOverwrite_) and paramkey_ in self.__d:
            return False

        self.__d[paramkey_] = paramval_
        return True

    def __UpdateContainer(self, dictParams_ : dict, bShallowCopy_ =True, bOverwrite_ =True) -> bool:
        if (self.__d is None) or not (isinstance(dictParams_, dict) and len(dictParams_)):
            return False

        _keys = dictParams_.keys()
        if not bOverwrite_:
            for _kk in _keys:
                if _kk in self.__d:
                    return False

        if bShallowCopy_:
            dictParams_ = dictParams_.copy()
        self.__d.update(dictParams_)
        if bShallowCopy_:
            dictParams_.clear()
        return True
