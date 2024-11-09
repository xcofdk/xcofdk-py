# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwpayload.py
#
# Copyright(c) 2024 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from xcofdk.fwcom                 import override
from xcofdk.fwapi.xmsg.xpayloadif import XPayloadIF

from xcofdk._xcofw.fw.fwssys.fwcore.logging        import logif
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject  import _AbstractObject
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject  import _AbstractSlotsObject
from xcofdk._xcofw.fw.fwssys.fwcore.types.apobject import _ProtectedAbstractObject
from xcofdk._xcofw.fw.fwssys.fwcore.types.apobject import _ProtectedAbstractSlotsObject

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine


class _FwPayload(_AbstractSlotsObject, XPayloadIF):
    __slots__ = [ '__cont' , '__bSerDes' ]

    def __init__(self, cont_ : dict =None, bShallowCopy_ =True, bSkipSerDes_ =False):
        self.__cont    = None
        self.__bSerDes = None
        _AbstractSlotsObject.__init__(self)
        XPayloadIF.__init__(self)

        if cont_ is None:
            cont_ = dict()
        elif not isinstance(cont_, dict):
            self.CleanUp()
            logif._LogError(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_Payload_TextID_001).format(type(cont_).__name__))
        elif bShallowCopy_:
            cont_ = cont_.copy()
        self.__cont    = cont_
        self.__bSerDes = not bSkipSerDes_


    @staticmethod
    def CustomSerializePayload(payload_) -> bytes:
        return None

    @staticmethod
    def CustomDeserializePayload(dump_: bytes):
        return None

    @XPayloadIF.isValidPayload.getter
    def isValidPayload(self) -> bool:
        return self.__cont is not None

    @XPayloadIF.isMarshalingRequired.getter
    def isMarshalingRequired(self):
        return self.__bSerDes

    @XPayloadIF.isCustomMarshalingRequired.getter
    def isCustomMarshalingRequired(self):
        return False

    @XPayloadIF.numParameters.getter
    def numParameters(self) -> int:
        return 0 if self.__cont is None else len(self.__cont)

    @override
    def IsIncludingParameter(self, paramkey_) -> bool:
        return False if self.__cont is None else paramkey_ in self.__cont

    @override
    def GetParameter(self, paramkey_):
        return self.__GetParameter(paramkey_, bRaiseExceptionOnKeyNotFound_=False)

    @override
    def DetachContainer(self) -> dict:
        res = self.__cont
        self.__cont = None
        return res


    @property
    def container(self) -> dict:
        return self.__cont

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
        if self.__cont is not None:
            _bSerDes = self.isMarshalingRequired
            if not _bSerDes:
                pass
            else:
                for _kk in self.__cont:
                    _vv = self.__cont[_kk]
                    if isinstance(_vv, (_AbstractObject, _AbstractSlotsObject)):
                        if isinstance(_vv, (_ProtectedAbstractObject, _ProtectedAbstractSlotsObject)):
                            _vv.CleanUpByOwnerRequest(_vv._myPPass)
                        else:
                            _vv.CleanUp()
                self.__cont.clear()

            self.__cont    = None
            self.__bSerDes = None

    def _ToString(self, *args_, **kwargs_):
        pass

    def __GetParameter(self, paramkey_, bRaiseExceptionOnKeyNotFound_ =False):
        if (self.__cont is None) or paramkey_ not in self.__cont:
            res = None
        else:
            res = self.__cont[paramkey_]

        if res is None:
            if bRaiseExceptionOnKeyNotFound_:
                raise KeyError(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_Payload_TextID_002).format(paramkey_))
        return res

    def __AddParameter(self, paramkey_, paramval_, bOverwrite_ =True) -> bool:
        if self.__cont is None:
            return False
        if (not bOverwrite_) and paramkey_ in self.__cont:
            return False

        self.__cont[paramkey_] = paramval_
        return True

    def __UpdateContainer(self, dictParams_ : dict, bShallowCopy_ =True, bOverwrite_ =True) -> bool:
        if (self.__cont is None) or not (isinstance(dictParams_, dict) and len(dictParams_)):
            return False

        _keys = dictParams_.keys()
        if not bOverwrite_:
            for _kk in _keys:
                if _kk in self.__cont:
                    return False

        if bShallowCopy_:
            dictParams_ = dictParams_.copy()
        self.__cont.update(dictParams_)
        if bShallowCopy_:
            dictParams_.clear()
        return True
