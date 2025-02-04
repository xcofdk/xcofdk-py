# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwrtedataex.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum import auto
from enum import unique
from enum import IntEnum

from xcofdk.fwcom.xmpdefs import ChildProcessResultData

from xcofdk._xcofw.fw.fwssys.fwmp.fwrte.fwrteseed import _FwRteSeed

class _FwRteDataExchange:

    @unique
    class _ERteDataState(IntEnum):
        eInit                = 20
        eAttachedToChild     = auto()

        @property
        def compactName(self):
            return self.name[1:]

    __slots__ = [ '__st' , '__wngMsg' , '__args' , '__kwargs' , '__rtetn'
                , '__childRteSeed' , '__parentRteSeed' , '__childProcRes'
                , '__childProcMaxDataSize'
                ]

    def __init__(self, rteSeed_ : _FwRteSeed, rteTokenName_ : str, maxResultDataSize_ : int, args_ : tuple =None, kwargs_ : dict =None):
        self.__st     = None
        self.__args   = None
        self.__rtetn  = None
        self.__kwargs = None
        self.__wngMsg = None

        self.__childProcRes         = None
        self.__childRteSeed         = None
        self.__parentRteSeed        = None
        self.__childProcMaxDataSize = maxResultDataSize_

        if isinstance(rteSeed_, _FwRteSeed):
            self.__st = _FwRteDataExchange._ERteDataState.eInit

            self.__args   = () if args_ is None else tuple(args_)
            self.__kwargs = {} if kwargs_ is None else kwargs_.copy()

            self.__rtetn        = rteTokenName_
            self.__childRteSeed = rteSeed_

    def __str__(self):
        if not self.isValid:
            return None

        _pref = f'[_FwRteDataExchange::{self.__st.compactName}] :'

        if self.__st == _FwRteDataExchange._ERteDataState.eInit:
            res = '{}\n\t{}\n\t#args={} , #kwargs_={}'.format(_pref, self.__childRteSeed, len(self.__args), len(self.__kwargs))

        else:
            res = '{}\n\tchild process: {}\n\tparent process: {}'.format(_pref, self.__childRteSeed, self.__parentRteSeed)

        return res

    @property
    def isValid(self):
        return self.__st is not None

    @property
    def isAttchToChildProcess(self):
        return self.isValid and (self.__st == _FwRteDataExchange._ERteDataState.eAttachedToChild)

    @property
    def childRteSeed(self) -> _FwRteSeed:
        return self.__childRteSeed

    @property
    def parentRteSeed(self) -> _FwRteSeed:
        return self.__parentRteSeed

    @property
    def rteTokenName(self):
        return self.__rtetn

    @property
    def childProcessStartArgs(self) -> tuple:
        return self.__args

    @property
    def childProcessStartKwargs(self) -> dict:
        return self.__kwargs

    @property
    def childProcessResultDataMaxSize(self) -> int:
        return self.__childProcMaxDataSize

    @property
    def childProcessResult(self) -> ChildProcessResultData:
        return self.__childProcRes

    @childProcessResult.setter
    def childProcessResult(self, procResData_ : ChildProcessResultData):
        self.__childProcRes = procResData_

    @property
    def currentWarningMessage(self) -> str:
        return self.__wngMsg

    def AttchToChildProcess(self) -> bool:
        if not self.isValid:
            return False
        if self.__st != _FwRteDataExchange._ERteDataState.eInit:
            self.__wngMsg = '[RteDE] RTE data exchange has been attached to child process already: {}'.format(self)
            return False

        _parentRteSeed = self.__childRteSeed.CloneAndUpdate()
        if _parentRteSeed is None:
            self.__wngMsg = '[RteDE] Failed to attach RTE data exchange to child process: {}'.format(self)
        else:
            self.__st = _FwRteDataExchange._ERteDataState.eAttachedToChild
            self.__parentRteSeed = _parentRteSeed
        return _parentRteSeed is not None

