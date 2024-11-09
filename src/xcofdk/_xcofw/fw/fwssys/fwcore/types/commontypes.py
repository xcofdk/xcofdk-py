# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : commontypes.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------



from enum   import auto
from enum   import unique
from enum   import Enum
from enum   import IntEnum
from enum   import IntFlag
from sys    import maxsize as _PY_MAX_SIZE
from typing import Union as _PyUnion

from xcofdk.fwcom.fwdefs import ETernaryCallbackResultID

from xcofdk._xcofw.fw.fwssys.fwcore.swpfm.sysinfo import _SystemInfo


class _CommonDefines:
    __SIZE__DASH_LINE_LONG        = 80
    __SIZE__DASH_LINE_SHORT       = 5
    __VALID_BOOLEAN_TRUE_AS_STR   = [ 'true'  ] #, 'yes' , 'on' , 'y']
    __VALID_BOOLEAN_FALSE_AS_STR  = [ 'false' ] #, 'no' , 'off' , 'n']

    _CHAR_SIGN_DOT                      = '.'
    _CHAR_SIGN_TAB                      = '\t'
    _CHAR_SIGN_DASH                     = '-'
    _CHAR_SIGN_HASH                     = '#'
    _CHAR_SIGN_COLON                    = ':'
    _CHAR_SIGN_COMMA                    = ','
    _CHAR_SIGN_SLASH                    = '/'
    _CHAR_SIGN_SPACE                    = ' '
    _CHAR_SIGN_NEWLINE                  = '\n'
    _CHAR_SIGN_UNDERSCORE               = '_'
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
    _CHAR_SIGN_FILE_MODE_BINARY         = 'b'

    _STR_EMPTY        = str('')
    _STR_TIME_UNIT_MS = str('ms')

    _DASH_LINE_LONG  = _CHAR_SIGN_DASH*__SIZE__DASH_LINE_LONG
    _DASH_LINE_SHORT = _CHAR_SIGN_DASH*__SIZE__DASH_LINE_SHORT

    @staticmethod
    def _StrToBool(str_ : str, bOneWayMatch_ =False) -> _PyUnion[bool, None]:
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
class _ETernaryOpResult(_FwIntEnum):

    eAbortOrFailed = ETernaryCallbackResultID.ABORT.value
    eStopOrNOK     = ETernaryCallbackResultID.STOP.value
    eContinueOrOK  = ETernaryCallbackResultID.CONTINUE.value

    @property
    def isOK(self):
        return self.isContinue

    @property
    def isContinue(self):
        return self == _ETernaryOpResult.eContinueOrOK

    @property
    def isNOK(self):
        return self.isStop

    @property
    def isStop(self):
        return self == _ETernaryOpResult.eStopOrNOK


    @property
    def isAbort(self):
        return self == _ETernaryOpResult.eAbortOrFailed

    @staticmethod
    def OK():
        return _ETernaryOpResult.Continue()

    @staticmethod
    def Continue():
        return _ETernaryOpResult.eContinueOrOK

    @staticmethod
    def NOK():
        return _ETernaryOpResult.Stop()

    @staticmethod
    def Stop():
        return _ETernaryOpResult.eStopOrNOK


    @staticmethod
    def Abort():
        return _ETernaryOpResult.eAbortOrFailed

    @staticmethod
    def ConvertFrom(execRes_ : _PyUnion[ETernaryCallbackResultID, bool, int, _FwIntEnum, IntEnum]):
        if not isinstance(execRes_, ETernaryCallbackResultID):
            if not isinstance(execRes_, _ETernaryOpResult):
                if execRes_ is None:
                    res = _ETernaryOpResult.eAbortOrFailed
                elif isinstance(execRes_, bool):
                    res = _ETernaryOpResult.eStopOrNOK if not execRes_ else _ETernaryOpResult.eContinueOrOK
                else:
                    res = None
                    if isinstance(execRes_, (int, _FwIntEnum, IntEnum)):
                        _intVal = execRes_.value if isinstance(execRes_, (_FwIntEnum, IntEnum)) else execRes_
                        if (_intVal >= _ETernaryOpResult.eAbortOrFailed.value) and (_intVal <= _ETernaryOpResult.eContinueOrOK.value):
                            res = _ETernaryOpResult(_intVal)
                    if res is None:
                        res = _ETernaryOpResult.eContinueOrOK if execRes_ else _ETernaryOpResult.eStopOrNOK
            else:
                res = execRes_
        else:
            res = _ETernaryOpResult(execRes_.value)
        return res

    @staticmethod
    def MapExecutionState2TernaryOpResult(execInst_):

        if execInst_ is None:
            res = _ETernaryOpResult.Abort()
        elif execInst_._isInvalid:
            res = _ETernaryOpResult.Abort()
        elif execInst_._isInLcCeaseMode:
            _ctlb = execInst_._lcCeaseTLB
            _bAbortingCease = (_ctlb is not None) and _ctlb.isAbortingCease
            res = _ETernaryOpResult.Abort() if _bAbortingCease else _ETernaryOpResult.Stop()
        elif not execInst_.isRunning:
            res = _ETernaryOpResult.Abort() if execInst_.isAborting else _ETernaryOpResult.Stop()
        else:
            res = _ETernaryOpResult.Continue()
        return res


@unique
class _EColorCode(IntEnum):
    NONE    = -1
    END     = auto()
    BLUE    = auto()
    RED     = auto()
    YELLOW  = auto()
    MAGENTA = auto()

    @property
    def isColor(self):
        return self.value > 0

    @property
    def isEnd(self):
        return self == _EColorCode.END

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
    def isMagenta(self):
        return self == _EColorCode.MAGENTA

    @property
    def code(self):
        res = None
        if not self.isColor:
            if self.isEnd:
                res = '\33[0m'
        elif self.isBlue:
            res = '\033[34m'
        elif self.isRed:
            res = '\033[31m'
        elif self.isYellow:
            res = '\033[33m'
        elif self.isMagenta:
            res = '\033[35m'
        return res


class _TextStyle:
    __slots__ = []

    def __init__(self):
        pass

    @staticmethod
    def ColorText(txt_ : str, color_ : _EColorCode, bAddEnd_ =True):
        if not (isinstance(txt_, str)):
            return txt_


        if not _SystemInfo._IsPythonVersionCompatible(3, 9):
            return txt_
        if not isinstance(color_, _EColorCode):
            return txt_

        _CC = color_.code
        if _CC is None:
            return txt_

        res = f'{color_.code}{txt_}'
        if color_.isEnd:
            pass
        elif bAddEnd_:
            res += f'{_EColorCode.END.code}'
        return res


class SyncPrint:

    __slots__ = []

    def __init__(self):
        pass

    __syncLck = None
    __SYNY_PRINT_TIMEOUT_SEC = 0.01

    @staticmethod
    def SetSyncLock(syncLck_):
        if SyncPrint.__syncLck is not None:
            try:
                SyncPrint.__syncLck.release()
            except RuntimeError:
                pass
            finally:
                SyncPrint.__syncLck = None
        SyncPrint.__syncLck = syncLck_

    @staticmethod
    def Print(buf_, endLine_ =None):
        _bLocked = SyncPrint.__syncLck is not None
        if _bLocked:
            _bLocked = SyncPrint.__syncLck.acquire(blocking=True, timeout=SyncPrint.__SYNY_PRINT_TIMEOUT_SEC)
        try:
            if endLine_ is not None:
                print(buf_, endLine_)
            else:
                print(buf_)
        except AttributeError as xcp:
            pass
        if _bLocked:
            SyncPrint.__syncLck.release()
