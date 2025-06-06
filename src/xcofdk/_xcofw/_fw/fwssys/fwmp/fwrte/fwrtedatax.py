# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwrtedatax.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum import auto
from enum import unique
from enum import IntEnum

from _fw.fwssys.fwcore.types.commontypes import _CommonDefines
from _fw.fwssys.fwmp.fwrte.fwrtedefs     import _ERteTXErrorID
from _fw.fwssys.fwmp.fwrte.fwrteseed     import _FwRteSeed
from _fw.fwssys.fwmp.fwrte.rteexception  import _RteException

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _ChildProcExitData:
    __slots__ = [ '__xc' , '__xd' , '__ei' ]

    def __init__(self):
        self.__xc = 0
        self.__xd = None
        self.__ei = _ERteTXErrorID.eDontCare

    def __str__(self):
        return _CommonDefines._STR_EMPTY

    @property
    def isProcessSucceeded(self):
        return self.__ei.isSuccess

    @property
    def exitCode(self) -> int:
        return self.__xc

    @exitCode.setter
    def exitCode(self, xc_ : int):
        if isinstance(xc_, int):
            self.__xc = xc_

    @property
    def exitData(self) -> object:
        return self.__xd

    @exitData.setter
    def exitData(self, xd_ : object):
        self.__xd = xd_

    @property
    def errorID(self) -> _ERteTXErrorID:
        return self.__ei

    @errorID.setter
    def errorID(self, errID_ : _ERteTXErrorID):
        if isinstance(errID_, _ERteTXErrorID):
            self.__ei = errID_

class _FwRteDataExchange:
    @unique
    class _ERteDataState(IntEnum):
        eInit            = 20
        eAttachedToChild = auto()

        @property
        def compactName(self):
            return self.name[1:]

    __slots__ = [ '__st' , '__bX' , '__a' , '__k' , '__t' , '__c' , '__p' , '__m' ]

    def __init__(self, rteSeed_ : _FwRteSeed, rteTokenName_ : str, maxSDSize_ : int, bXcpTracking_ : bool):
        self.__a  = None
        self.__c  = None
        self.__k  = None
        self.__m  = None
        self.__p  = None
        self.__t  = None
        self.__bX = None
        self.__st = None

        if isinstance(rteSeed_, _FwRteSeed):
            self.__c  = rteSeed_
            self.__m  = maxSDSize_
            self.__t  = rteTokenName_
            self.__bX = bXcpTracking_
            self.__st = _FwRteDataExchange._ERteDataState.eInit

    def __str__(self):
        if not self.isValid:
            return _CommonDefines._STR_EMPTY

        _pref = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteDataExchange_TID_004).format(type(self).__name__[1:], self.__st.compactName)
        if self.__st == _FwRteDataExchange._ERteDataState.eInit:
            res = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteDataExchange_TID_004).format(_pref, self.__c, len(self.__a), len(self.__k))
        else:
            res = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteDataExchange_TID_005).format(_pref, self.__c, self.__p)
        return res

    @property
    def isValid(self):
        return self.__st is not None

    @property
    def isXcpTrackingEnabled(self):
        return self.isValid and self.__bX

    @property
    def childRteSeed(self) -> _FwRteSeed:
        return self.__c

    @property
    def rteTokenName(self):
        return self.__t

    @property
    def childProcessStartArgs(self) -> tuple:
        return self.__a

    @property
    def childProcessStartKwargs(self) -> dict:
        return self.__k

    @property
    def childProcessMaxSDSize(self) -> int:
        return self.__m

    def AttchToChildProcess(self):
        if not self.isValid:
            return

        if self.__st != _FwRteDataExchange._ERteDataState.eInit:
            _msg    = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteDataExchange_TID_001).format(self)
            _rteXcp = _RteException(msg_=_msg, code_=_ERteTXErrorID.eAttchToChildProcess.value)
            raise _rteXcp

        _pseed = self.__c.CloneAndUpdateChild()
        if _pseed is None:
            _msg    = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteDataExchange_TID_002).format(self)
            _rteXcp = _RteException(msg_=_msg, code_=_ERteTXErrorID.eAttchToChildProcess.value)
            raise _rteXcp

        self.__st = _FwRteDataExchange._ERteDataState.eAttachedToChild
        self.__p = _pseed

    def _SetPStartArgs(self, *args_, **kwargs_):
        if not self.isValid:
            return False
        if self.__st != _FwRteDataExchange._ERteDataState.eInit:
            return False

        if self.__a is not None:
            del self.__a
        if self.__k is not None:
            del self.__k

        self.__a   = tuple(args_)
        self.__k = kwargs_.copy()
        return True

    def _CleanUp(self):
        self.__a  = None
        self.__c  = None
        self.__k  = None
        self.__m  = None
        self.__p  = None
        self.__t  = None
        self.__bX = None
        self.__st = None

