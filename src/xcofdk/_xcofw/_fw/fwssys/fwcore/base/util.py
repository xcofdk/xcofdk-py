# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : util.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

import inspect

from _fw.fwssys.fwcore.logging           import logif
from _fw.fwssys.fwcore.types.commontypes import _CommonDefines
from _fw.fwssys.fwerrh.fwerrorcodes      import _EFwErrorCode

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

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
                logif._LogBadUseEC(_EFwErrorCode.FE_00101, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Util_TID_001))
        else:
            lstClasses = [class_]

        for cc in lstClasses:
            if not inspect.isclass(cc):
                logif._LogBadUseEC(_EFwErrorCode.FE_00102, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Util_TID_002).format(str(cc)))
            if isinstance(obj_, cc):
                return True

        if bThrowx_:
            if not isinstance(class_, list):
                _classesAsStr = class_.__name__
            else:
                _classesAsStr = [ cc.__name__ for cc in class_ ]
                _classesAsStr = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_015).join(_classesAsStr)
                _classesAsStr = _CommonDefines._CHAR_SIGN_LEFT_SQUARED_BRACKET + _classesAsStr.strip() + _CommonDefines._CHAR_SIGN_RIGHT_SQUARED_BRACKET
            logif._LogBadUseEC(_EFwErrorCode.FE_00103, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Util_TID_003).format(_Util.TypeName(obj_), _classesAsStr))
        return False

    @staticmethod
    def GetAttribute(obj_, attrname_ : str, bThrowx_ : bool =True):
        if obj_ is None or attrname_ is None or not isinstance(attrname_, str):
            if bThrowx_:
                logif._LogBadUseEC(_EFwErrorCode.FE_00104, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Util_TID_004).format(obj_, attrname_))
            return None

        res = getattr(obj_, attrname_, None)
        if res is None:
            if bThrowx_:
                logif._LogBadUseEC(_EFwErrorCode.FE_00105, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Util_TID_005).format(_Util.TypeName(obj_), attrname_))
        return res

    @staticmethod
    def GetNumAttributes(obj_, attrNames_ : list, bThrowx_ : bool =True):
        if obj_ is None or not isinstance(attrNames_, list):
            if bThrowx_:
                logif._LogBadUseEC(_EFwErrorCode.FE_00106, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Util_TID_006).format(_Util.TypeName(obj_), _Util.TypeName(attrNames_)))
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
                logif._LogBadUseEC(_EFwErrorCode.FE_00107, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Util_TID_007).format('optional' if isOptionalAttr_ else 'required', _Util.TypeName(obj_), numAttrs, str(mutuallyExclusiveAttrs_)))
        return res

    @staticmethod
    def CheckRange(value_, minrange_, maxrange_, bThrowx_ : bool =True):
        if value_ is None or minrange_ is None or maxrange_ is None:
            if bThrowx_:
                logif._LogBadUseEC(_EFwErrorCode.FE_00108, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Util_TID_008).format(value_, minrange_, maxrange_))
            return False

        res  = not value_ < minrange_
        res &= not value_ > maxrange_
        if not res:
            if bThrowx_:
                logif._LogBadUseEC(_EFwErrorCode.FE_00109, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Util_TID_009).format(value_, minrange_, maxrange_))
        return res

    @staticmethod
    def CheckMinRange(value_, minrange_, bThrowx_ : bool =True):
        if value_ is None or minrange_ is None:
            if bThrowx_:
                logif._LogBadUseEC(_EFwErrorCode.FE_00110, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Util_TID_010).format(value_, minrange_))
            return False

        res = not value_ < minrange_
        if not res:
            if bThrowx_:
                logif._LogBadUseEC(_EFwErrorCode.FE_00111, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Util_TID_011).format(value_, minrange_))
        return res

    @staticmethod
    def CheckMaxRange(value_, maxrange_, bThrowx_ : bool =True):
        if value_ is None or maxrange_ is None:
            if bThrowx_:
                logif._LogBadUseEC(_EFwErrorCode.FE_00112, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Util_TID_012).format(value_, maxrange_))
            return False

        res = not value_ > maxrange_
        if not res:
            if bThrowx_:
                logif._LogBadUseEC(_EFwErrorCode.FE_00113, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Util_TID_013).format(value_, maxrange_))
        return res
