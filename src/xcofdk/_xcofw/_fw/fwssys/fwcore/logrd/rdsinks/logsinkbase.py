# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : logsinkbase.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from collections import deque
from typing      import List
from typing      import Union

from _fw.fwssys.fwcore.logrd.logrecord import _ELRType
from _fw.fwssys.fwcore.logrd.logrecord import _EColorCode
from _fw.fwssys.fwcore.logrd.logrecord import _LogRecord

class _LogSinkBase:
    __slots__ = [ '__c' , '__d' ]

    def __init__(self, capacity_ : int =1000):
        super().__init__()
        self.__c = capacity_
        self.__d = deque([], maxlen=capacity_)

    @property
    def isValidSink(self) -> bool:
        return self._IsValidSink()

    @property
    def isActiveSink(self) -> bool:
        return self._IsValidSink()

    @property
    def isHighLightingEnabled(self) -> bool:
        return False

    @property
    def capacity(self) -> int:
        return self.__c

    def AddLR(self, logRec_ : _LogRecord):
        if self.__isInvalid:
            return
        self.__d.append(_LogRecord(logRec_._recToStr, color_=logRec_._recColor, logType_=logRec_._recType))

    def Flush(self, backlog_: Union[_LogRecord, List[_LogRecord], None] =None) -> _ELRType:
        res = _ELRType.LR_FREE
        if self.__isInvalid:
            return res

        if backlog_ is None:
            backlog_ = self.__GetBacklog()
        if isinstance(backlog_, list):
            _CNT = len(backlog_)
            for _ii in range(_CNT):
                _rr = backlog_[_ii]
                if _rr._recType.isError:
                    res = _rr._recType
                if not self._FlushLR(_rr):
                    self.__d = deque(backlog_[_ii:], maxlen=self.__c)
                    break
                _ii += 1
        else:
            self._FlushLR(backlog_)
            if backlog_._recType.isError:
                res = backlog_._recType
        return res

    @staticmethod
    def _ColorText(txt_ : str, color_ : _EColorCode, bAddEnd_ =True):
        _cc = color_.code
        if _cc is None:
            return txt_

        res = f'{_cc}{txt_}'
        if color_.isEnd:
            pass
        elif bAddEnd_:
            res += _EColorCode.END.code
        return res

    def _IsValidSink(self) -> bool:
        return self.__d is not None

    def _FlushLR(self, logrec_: _LogRecord) -> bool:
        return False

    def _CleanUp(self):
        if self.__isInvalid:
            return
        self.__d.clear()
        self.__d = None
        self.__c = None

    @property
    def __isInvalid(self) -> bool:
        return self.__d is None

    def __GetBacklog(self) -> List[_LogRecord]:
        res = list(self.__d)
        self.__d.clear()
        return res
