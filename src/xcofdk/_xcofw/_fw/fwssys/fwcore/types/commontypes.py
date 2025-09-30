# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : commontypes.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

try:
    from typing import override
except ImportError:
    def override(method_):
        def FwDecoFunc(*args_, **kwargs_): return method_(*args_, **kwargs_)
        def _FwDecoFunc(*args_, **kwargs_): return method_(*args_, **kwargs_)
        return _FwDecoFunc if method_.__name__.startswith('_') else FwDecoFunc

from enum   import auto
from enum   import unique
from enum   import Enum
from enum   import IntEnum
from enum   import IntFlag
from sys    import maxsize as _PY_MAX_SIZE
from typing import Union

from xcofdk.fwcom import EExecutionCmdID

class _CommonDefines:
    __SIZE__DASH_LINE_LONG        = 80
    __SIZE__DASH_LINE_SHORT       = 5
    __VALID_BOOLEAN_TRUE_AS_STR   = [ 'true'  ] #, 'yes' , 'on' , 'y']
    __VALID_BOOLEAN_FALSE_AS_STR  = [ 'false' ] #, 'no' , 'off' , 'n']

    _CHAR_SIGN_LF                       = '\n'
    _CHAR_SIGN_CR                       = '\r'
    _CHAR_SIGN_DOT                      = '.'
    _CHAR_SIGN_TAB                      = '\t'
    _CHAR_SIGN_DASH                     = '-'
    _CHAR_SIGN_HASH                     = '#'
    _CHAR_SIGN_COLON                    = ':'
    _CHAR_SIGN_COMMA                    = ','
    _CHAR_SIGN_SLASH                    = '/'
    _CHAR_SIGN_SPACE                    = ' '
    _CHAR_SIGN_ESCAP                    = '\\'
    _CHAR_SIGN_UNDERSCORE               = '_'
    _CHAR_SIGN_APOSTROPHE               = '\''
    _CHAR_SIGN_LEFT_BRACE               = '{'
    _CHAR_SIGN_RIGHT_BRACE              = '}'
    _CHAR_SIGN_LESS_THAN                = '<'
    _CHAR_SIGN_LARGER_THAN              = '>'
    _CHAR_SIGN_LEFT_PARANTHESIS         = '('
    _CHAR_SIGN_RIGHT_PARANTHESIS        = ')'
    _CHAR_SIGN_LEFT_SQUARED_BRACKET     = '['
    _CHAR_SIGN_RIGHT_SQUARED_BRACKET    = ']'

    _CHAR_SIGN_FILE_MODE_READ           = 'r'
    _CHAR_SIGN_FILE_MODE_WRITE          = 'w'
    _CHAR_SIGN_FILE_MODE_APPEND         = 'a'
    _CHAR_SIGN_FILE_MODE_BINARY         = 'b'

    _STR_NONE          = str('None')
    _STR_EMPTY         = str('')
    _STR_TIME_UNIT_MS  = str('ms')
    _STR_ENCODING_UTF8 = str('utf-8')

    _DASH_LINE_LONG  = _CHAR_SIGN_DASH*__SIZE__DASH_LINE_LONG
    _DASH_LINE_SHORT = _CHAR_SIGN_DASH*__SIZE__DASH_LINE_SHORT

    @staticmethod
    def _StrToBool(str_ : str, bOneWayMatch_ =False) -> Union[bool, None]:
        if not isinstance(str_, str):
            return False if bOneWayMatch_ else None
        if str_ in _CommonDefines.__VALID_BOOLEAN_TRUE_AS_STR:
            return True
        if str_ in _CommonDefines.__VALID_BOOLEAN_FALSE_AS_STR:
            return False
        return False if bOneWayMatch_ else None

class _Limits:
    MAX_INT = _PY_MAX_SIZE
    MIN_INT = (MAX_INT * -1) - 1

class _FwEnum(Enum):
    @staticmethod
    def GetEnumsNum():
        return len(_FwEnum.__members__.items())

    @property
    def compactName(self) -> str:
        return self.name[1:]

class _FwIntEnum(IntEnum):
    @staticmethod
    def GetEnumsNum():
        return len(_FwIntEnum.__members__.items())

    @property
    def compactName(self) -> str:
        return self.name[1:]

class _FwIntFlag(IntFlag):
    @property
    def compactName(self) -> str:
        return self.name[1:]

    @property
    def leftMostBitPosition(self) -> int:
        return _FwIntFlag.__GetBitPosition(self, bRightMostBitPos_=False)

    @property
    def rightMostBitPosition(self) -> int:
        return _FwIntFlag.__GetBitPosition(self, bRightMostBitPos_=True)

    @staticmethod
    def __GetBitPosition(intFlag_ : IntFlag, bRightMostBitPos_) -> int:
        res    = -1
        _myVal = intFlag_.value
        for _ii in range(_myVal.bit_length()):
            if _myVal & (0x1 << _ii):
                res = _ii
                if bRightMostBitPos_:
                    break
        return res

@unique
class _ERtePolicyBase(_FwIntFlag):
    pass

@unique
class _EExecutionCmdID(_FwIntEnum):
    eAbortOrFailed = EExecutionCmdID.ABORT.value
    eCancelOrNOK   = EExecutionCmdID.CANCEL.value
    eStopOrNOK     = EExecutionCmdID.STOP.value
    eContinueOrOK  = EExecutionCmdID.CONTINUE.value

    @property
    def isOK(self):
        return self.isContinue

    @property
    def isNOK(self):
        return self.isStop or self.isCancel

    @property
    def isContinue(self):
        return self == _EExecutionCmdID.eContinueOrOK

    @property
    def isCancel(self):
        return self == _EExecutionCmdID.eCancelOrNOK

    @property
    def isStop(self):
        return self == _EExecutionCmdID.eStopOrNOK

    @property
    def isAbort(self):
        return self == _EExecutionCmdID.eAbortOrFailed

    @staticmethod
    def OK():
        return _EExecutionCmdID.Continue()

    @staticmethod
    def NOK():
        return _EExecutionCmdID.Stop()

    @staticmethod
    def Continue():
        return _EExecutionCmdID.eContinueOrOK

    @staticmethod
    def Stop():
        return _EExecutionCmdID.eStopOrNOK

    @staticmethod
    def Cancel():
        return _EExecutionCmdID.eCancelOrNOK

    @staticmethod
    def Abort():
        return _EExecutionCmdID.eAbortOrFailed

    @staticmethod
    def ConvertFrom(xcmd_ : Union[EExecutionCmdID, bool]):
        if not isinstance(xcmd_, EExecutionCmdID):
            if not isinstance(xcmd_, _EExecutionCmdID):
                if not isinstance(xcmd_, bool):
                    res = _EExecutionCmdID.eAbortOrFailed
                else:
                    res = _EExecutionCmdID.eStopOrNOK if not xcmd_ else _EExecutionCmdID.eContinueOrOK
            else:
                res = xcmd_
        else:
            res = _EExecutionCmdID(xcmd_.value)
        return res

    @staticmethod
    def MapExecState2ExecCmdID(execInst_):
        if execInst_ is None:
            res = _EExecutionCmdID.Abort()
        elif execInst_._isInvalid:
            res = _EExecutionCmdID.Abort()
        elif execInst_._isInLcCeaseMode:
            _ctlb = execInst_._lcCeaseTLB
            _bEnd = (_ctlb is not None) and _ctlb.isEndingCease
            res   = _EExecutionCmdID.Abort() if _bEnd else _EExecutionCmdID.Stop()
        elif not execInst_.isRunning:
            if execInst_.isAborting:
                res = _EExecutionCmdID.Abort()
            else:
                res = _EExecutionCmdID.Cancel() if execInst_.isCanceling else _EExecutionCmdID.Stop()
        else:
            res = _EExecutionCmdID.Continue()
        return res

@unique
class _EDepInjCmd(_FwIntEnum):
    eDontCare = 0
    eInject   = auto()
    eReInject = auto()
    eDeInject = auto()
    eFinalize = auto()

    @property
    def isInject(self):
        return self == _EDepInjCmd.eInject

    @property
    def isReInject(self):
        return self == _EDepInjCmd.eReInject

    @property
    def isDeInject(self):
        return self == _EDepInjCmd.eDeInject

    @property
    def isFinalize(self):
        return self==_EDepInjCmd.eFinalize
