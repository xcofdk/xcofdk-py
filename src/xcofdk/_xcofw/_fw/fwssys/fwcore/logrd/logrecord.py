# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : rdrecord.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum   import auto
from enum   import unique
from enum   import IntEnum
from typing import Union

@unique
class _ELRType(IntEnum):
    LR_FREE = 0
    LR_TRC  = 10
    LR_DBG  = 20
    LR_INF  = 30
    LR_KPI  = 40
    LR_WNG  = 50
    LR_ERR  = 60
    LR_FTL  = 70

    @property
    def isFree(self):
        return self == _ELRType.LR_FREE

    @property
    def isInfo(self):
        return self == _ELRType.LR_INF

    @property
    def isWarning(self):
        return self == _ELRType.LR_WNG

    @property
    def isError(self):
        return self.value >= _ELRType.LR_ERR.value

    @property
    def isFatal(self):
        return self == _ELRType.LR_FTL.value

@unique
class _EColorCode(IntEnum):
    NONE    = -1
    END     = auto()
    GREEN   = auto()
    BLUE    = auto()
    RED     = auto()
    YELLOW  = auto()

    @property
    def isColor(self):
        return self.value > _EColorCode.END.value

    @property
    def isEnd(self):
        return self == _EColorCode.END

    @property
    def isGreen(self):
        return self == _EColorCode.GREEN

    @property
    def isBlue(self):
        return self == _EColorCode.BLUE

    @property
    def isRed(self):
        return self == _EColorCode.RED

    @property
    def isYellow(self):
        return self == _EColorCode.YELLOW

    @property
    def code(self):
        res = _EColorCode.NONE
        if not self.isColor:
            if self.isEnd:
                res = '\033[0m'
        elif self.isGreen:
            res = '\033[32m'
        elif self.isBlue:
            res = '\033[34m'
        elif self.isRed:
            res = '\033[31m'
        elif self.isYellow:
            res = '\033[33m'
        return res

class _IRDLogRP:
    __slots__ = []

    def __init__(self):
        pass

    @property
    def _recStr(self) -> str:
        pass

    @property
    def _logRecord(self):
        pass

    def _CleanUpLE(self):
        pass

class _LogRecord:
    __slots__ = [ '__c', '__r', '__t' ]

    def __init__(self, rec_: Union[_IRDLogRP, str], color_: _EColorCode = _EColorCode.NONE, logType_: _ELRType =_ELRType.LR_FREE):
        self.__c = color_
        self.__r = rec_
        self.__t = logType_

    @property
    def _recType(self) -> _ELRType:
        return self.__t

    @property
    def _recColor(self) -> _EColorCode:
        return self.__c

    @property
    def _recToStr(self) -> str:
        res = self.__r
        if not isinstance(res, str):
            res = res._recStr
        return res

    @property
    def _recItem(self) -> Union[_IRDLogRP, str]:
        return self.__r

    def _CleanUp(self):
        if self.__r is None:
            return
        if (not self.__t.isError) and isinstance(self.__r, _IRDLogRP):
            self.__r._CleanUpLE()
        self.__c = None
        self.__r = None
        self.__t = None

