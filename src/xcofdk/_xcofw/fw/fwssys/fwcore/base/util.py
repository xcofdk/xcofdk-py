# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : util.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


import inspect
import os

from inspect import currentframe as _Currentframe
from inspect import getframeinfo as _Getframeinfo
from typing import Tuple as _Tuple

from xcofdk._xcofw.fw.fwssys.fwcore.logging           import logif
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes import _CommonDefines

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine


class _Util:
    __slots__ = []

    @staticmethod
    def TypeName(obj_):
        return type(obj_).__name__

    @staticmethod
    def IsInstance(obj_, class_, bThrowx_ : bool =True):
        lstClasses = class_
        if isinstance(class_, list):
            if len(class_) == 0:
                logif._LogBadUse(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_Util_TextID_001))
        else:
            lstClasses = [class_]

        for cc in lstClasses:
            if not inspect.isclass(cc):
                logif._LogBadUse(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_Util_TextID_002).format(str(cc)))
            if isinstance(obj_, cc):
                return True

        if bThrowx_:
            if not isinstance(class_, list):
                _classesAsStr = class_.__name__
            else:
                _classesAsStr = [ cc.__name__ for cc in class_ ]
                _classesAsStr = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_015).join(_classesAsStr)
                _classesAsStr = _CommonDefines._CHAR_SIGN_LEFT_SQUARED_BRACKET + _classesAsStr.strip() + _CommonDefines._CHAR_SIGN_RIGHT_SQUARED_BRACKET
            logif._LogBadUse(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_Util_TextID_003).format(_Util.TypeName(obj_), _classesAsStr))
        return False

    @staticmethod
    def GetAttribute(obj_, attrname_ : str, bThrowx_ : bool =True):
        if obj_ is None or attrname_ is None or not isinstance(attrname_, str):
            if bThrowx_:
                logif._LogBadUse(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_Util_TextID_004).format(obj_, attrname_))
            return None

        res = getattr(obj_, attrname_, None)
        if res is None:
            if bThrowx_:
                logif._LogBadUse(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_Util_TextID_005).format(_Util.TypeName(obj_), attrname_))
        return res

    @staticmethod
    def GetNumAttributes(obj_, attrNames_ : list, bThrowx_ : bool =True):
        if obj_ is None or not isinstance(attrNames_, list):
            if bThrowx_:
                logif._LogBadUse(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_Util_TextID_006).format(_Util.TypeName(obj_), _Util.TypeName(attrNames_)))
            return -1

        res = 0
        for _ee in attrNames_:
            if not isinstance(_ee, str):
                continue
            if getattr(obj_, _ee, None) is not None:
                res += 1
        return res

    @staticmethod
    def CheckMutuallyExclusiveAttributes(obj_, mutuallyExclusiveAttrs_ : list, isOptionalAttr_ : bool =False, bThrowx_ : bool =True):
        numAttrs = _Util.GetNumAttributes(obj_, mutuallyExclusiveAttrs_, bThrowx_=True)
        if numAttrs < 0:
            return False

        if isOptionalAttr_:
            res = numAttrs <= 1
        else:
            res = numAttrs == 1
        if not res:
            if bThrowx_:
                logif._LogBadUse(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_Util_TextID_007).format('optional' if isOptionalAttr_ else 'required', _Util.TypeName(obj_), numAttrs, str(mutuallyExclusiveAttrs_)))
        return res

    @staticmethod
    def CheckRange(value_, minrange_, maxrange_, bThrowx_ : bool =True):
        if value_ is None or minrange_ is None or maxrange_ is None:
            if bThrowx_:
                logif._LogBadUse(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_Util_TextID_008).format(value_, minrange_, maxrange_))
            return False

        res  = not value_ < minrange_
        res &= not value_ > maxrange_
        if not res:
            if bThrowx_:
                logif._LogBadUse(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_Util_TextID_009).format(value_, minrange_, maxrange_))
        return res

    @staticmethod
    def CheckMinRange(value_, minrange_, bThrowx_ : bool =True):
        if value_ is None or minrange_ is None:
            if bThrowx_:
                logif._LogBadUse(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_Util_TextID_010).format(value_, minrange_))
            return False

        res = not value_ < minrange_
        if not res:
            if bThrowx_:
                logif._LogBadUse(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_Util_TextID_011).format(value_, minrange_))
        return res

    @staticmethod
    def CheckMaxRange(value_, maxrange_, bThrowx_ : bool =True):
        if value_ is None or maxrange_ is None:
            if bThrowx_:
                logif._LogBadUse(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_Util_TextID_012).format(value_, maxrange_))
            return False

        res = not value_ > maxrange_
        if not res:
            if bThrowx_:
                logif._LogBadUse(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_Util_TextID_013).format(value_, maxrange_))
        return res

    @staticmethod
    def CopyAttributes(fromNamespace_, toNamespace_):
        if fromNamespace_ is None or toNamespace_ is None:
            if fromNamespace_ is None:
                logif._LogBadUse(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_Util_TextID_014))
            else:
                logif._LogBadUse(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_Util_TextID_015))

        for _ee in fromNamespace_.__dict__.items():
            setattr(toNamespace_, _ee[0], _ee[1])

    @staticmethod
    def GetCurrentStack() -> _Tuple[list, int]:
        cstack = inspect.stack()
        return cstack, len(cstack)

    @staticmethod
    def GetCurrentFrameInfo() -> _Tuple[str, str, str, int]:
        curframeinfo = _Getframeinfo(_Currentframe())
        filePath = os.path.realpath(curframeinfo.filename)
        fileName = os.path.basename(filePath)
        return filePath, fileName, curframeinfo.function, curframeinfo.lineno

    @staticmethod
    def GetCallStackInfo(level_ =3) -> _Tuple[str, str, str, int]:
        filePath, fileName, functionName, lineNo = None, None, None, None
        cstack = inspect.stack()
        if level_ >= len(cstack):
            pass
        else:
            frame, filePath, lineNo, functionName, lines, index = cstack[level_]
            fileName = os.path.basename(os.path.realpath(filePath))
        return filePath, fileName, functionName, lineNo
