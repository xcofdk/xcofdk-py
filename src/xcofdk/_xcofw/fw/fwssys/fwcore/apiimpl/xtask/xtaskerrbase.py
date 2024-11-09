# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xtaskerrbase.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from xcofdk._xcofw.fw.fwssys.fwcore.logging.logdefines import _LogErrorCode

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine


class _XTaskErrorBase:
    __slots__ = [ '__uid' , '__em' , '__ec' , '__bFE' , '__bDE' ]

    def __init__(self, uid_ : int, bFatal_ : bool, bDie_ : bool, errMsg_ : str, errCode_ : int =None):
        self.__bFE = bFatal_
        self.__bDE = bDie_
        self.__em  = errMsg_
        self.__ec  = errCode_
        self.__uid =  uid_

    def __str__(self):
        res  = _EFwTextID.eXTaskErrorBase_ToString_01 if self._isFatalError else _EFwTextID.eXTaskErrorBase_ToString_02
        res  = _FwTDbEngine.GetText(res)
        res += f'[{self._uniqueID}]'
        if self._errorCode is not None:
            if not _LogErrorCode.IsAnonymousErrorCode(self._errorCode):
                res += f'[{self._errorCode}]'
        res += f' {self._message}'
        return res

    @property
    def _isFatalError(self) -> bool:
        return self.__bFE

    @property
    def _isDieError(self) -> bool:
        return self.__bDE

    @property
    def _uniqueID(self) -> int:
        return self.__uid

    @property
    def _message(self) -> str:
        return self.__em

    @property
    def _errorCode(self) -> int:
        return self.__ec
