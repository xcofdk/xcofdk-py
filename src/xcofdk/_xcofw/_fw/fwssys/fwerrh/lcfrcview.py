# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : lcfrcview.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from typing import Union

from _fw.fwssys.fwcore.logging.logdefines import _EErrorImpact
from _fw.fwssys.fwcore.logging.logdefines import _LogErrorCode
from _fw.fwssys.fwcore.lc.lcdefines       import _ELcCompID
from _fw.fwssys.fwcore.types.commontypes  import _CommonDefines

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _LcFrcView:
    __slots__ = [ '__cid' , '__c' , '__bF' , '__bR' , '__id' , '__n']

    def __init__( self, *, cid_ : _ELcCompID, ferr_, bFFE_ : bool, bRTT_ : bool, thrdName_ : str, thrdID_ : int):
        self.__c = ferr_.Clone()

        self.__n   = thrdName_
        self.__bF  = bFFE_
        self.__bR  = bRTT_
        self.__id  = thrdID_
        self.__cid = cid_

    def __str__(self):
        return self.ToString()

    @property
    def isValid(self):
        return not self._isInvalid

    @property
    def isReportedByPyThread(self):
        return self.__bR is None

    @property
    def isReportedByFwTask(self):
        return self.__bR is not None and self.__bR

    @property
    def isReportedByFwThread(self):
        return self.__bR is not None and not self.__bR

    @property
    def dtaskUID(self):
        return None if self._isInvalid else self.__c.dtaskUID

    @property
    def dtaskName(self):
        return None if self._isInvalid else self.__c.dtaskName

    @property
    def errorMessage(self):
        return None if self._isInvalid else self.__c.message

    @property
    def errorCode(self):
        res = None if self._isInvalid else self.__c.errorCode
        res = None if _LogErrorCode.IsAnonymousErrorCode(res) else res
        return res

    @property
    def errorImpact(self) -> _EErrorImpact:
        return None if self._isInvalid else self.__c.errorImpact

    @property
    def lcCompID(self) -> _ELcCompID:
        return self.__cid

    @property
    def hostThreadID(self):
        return self.__id

    @property
    def hostThreadName(self):
        return self.__n

    @property
    def asCompactString(self) -> Union[str, None]:
        return self.__ToString(bVerbose_=False)

    @property
    def asVerboseString(self) -> Union[str, None]:
        return self.__ToString(bVerbose_=True)

    def ToString(self) -> Union[str, None]:
        return self.__ToString()

    def CleanUp(self):
        if self.__c is None:
            return

        self.__c.CleanUp()
        self.__c   = None
        self.__n   = None
        self.__bF  = None
        self.__bR  = None
        self.__id  = None
        self.__cid = None

    @property
    def _isInvalid(self):
        return self.__c is None

    @property
    def _isFFE(self):
        return False if self.__bF is None else self.__bF

    @property
    def _feClone(self):
        return self.__c

    def _UpdateTaskInfo(self, bRTT_ : bool, atsk_):
        if self.isValid:
            self.__bR = bRTT_
            if atsk_ is not None:
                self.__c._Adapt(taskName_=atsk_.dtaskName, taskID_=atsk_.dtaskUID)

    def __ToString(self, bVerbose_ =True) -> Union[str, None]:
        if self._isInvalid:
            return None

        _tid = self.dtaskUID
        if _tid is None:
            _tid = self.__id
        _tname = self.dtaskName
        if _tname is None:
            _tid = self.__n

        res = self.errorCode
        if not (isinstance(res, int) and res != _LogErrorCode.GetAnonymousErrorCode()):
            res = _CommonDefines._CHAR_SIGN_DASH

        _uname = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_011).format(_tname, _tid)

        res = _FwTDbEngine.GetText(_EFwTextID.eLcFrcView_ToString_01).format(self.dtaskUID, self.__cid.compactName, res, _uname)

        if not bVerbose_:
            res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_016).format(self.__c.shortMessage)
        else:
            res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_012).format(self.__c)
        return res
