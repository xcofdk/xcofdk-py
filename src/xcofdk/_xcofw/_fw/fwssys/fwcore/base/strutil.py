# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : strutil.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

import re

from _fw.fwssys.fwcore.logging           import logif
from _fw.fwssys.fwcore.base.util         import _Util
from _fw.fwssys.fwcore.types.commontypes import _CommonDefines

from _fw.fwssys.fwerrh.fwerrorcodes import _EFwErrorCode

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _StrUtil:
    __cpHexString = re.compile(r'^\s*0x([0-9A-F]+)\s*$', re.RegexFlag.IGNORECASE)

    @staticmethod
    def Length(str_ : str) -> int:
        res = 0
        if not str_ is None:
            res = len(str_)
        return res

    @staticmethod
    def IsEmpty(str_ : str, stripBefore_ =True) -> bool:
        if str_ is None:
            return True

        if stripBefore_:
            str_ = str_.strip()
        return len(str_) == 0

    @staticmethod
    def IsNonEmpty(str_ : str, stripBefore_ =True) -> bool:
        return not _StrUtil.IsEmpty(str_, stripBefore_)

    @staticmethod
    def IsString(obj_, bThrowx_ =False):
        res = isinstance(obj_, str)
        if not res:
            if bThrowx_:
                logif._LogFatalEC(_EFwErrorCode.FE_00032, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_StrUtil_TID_001).format(_Util.TypeName(obj_)))
        return res

    @staticmethod
    def IsEmptyString(obj_, stripBefore_ =True, bThrowx_ =False):
        res = _StrUtil.IsString(obj_, bThrowx_)
        if res:
            res = _StrUtil.IsEmpty(obj_, stripBefore_)
            if not res:
                if bThrowx_:
                    logif._LogFatalEC(_EFwErrorCode.FE_00033, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_StrUtil_TID_002).format(obj_))
        return res

    @staticmethod
    def IsNonEmptyString(obj_, stripBefore_ =True, bThrowx_ =False):
        res = _StrUtil.IsString(obj_, bThrowx_)
        if res:
            res = _StrUtil.IsNonEmpty(obj_, stripBefore_)
            if not res:
                if bThrowx_:
                    logif._LogFatalEC(_EFwErrorCode.FE_00034, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_StrUtil_TID_003))
        return res

    @staticmethod
    def IsHexString(hexStr_):
        return _StrUtil.__cpHexString.match(hexStr_) is not None

    @staticmethod
    def IsIdentifier(str_ : str, bThrowx_ : bool =False):
        res  = isinstance(str_, str)
        res &= str_.isidentifier()
        if not res:
            if bThrowx_:
                logif._LogBadUseEC(_EFwErrorCode.FE_00089, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_StrUtil_TID_004).format(str_))
        return res

    @staticmethod
    def ToBool(str_, bThrowx_ =False) -> bool:
        res = bool(_CommonDefines._StrToBool(str_))
        if res is None:
            if bThrowx_:
                res = False
                logif._LogBadUseEC(_EFwErrorCode.FE_00090, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_StrUtil_TID_006).format(str_))
        return res

    @staticmethod
    def ToCamelCase(str_, startWithLowerCase_ =True, bThrowx_ =False):
        if not _Util.IsInstance(str_, str, bThrowx_):
            return None

        _lst = re.split('[^a-zA-Z0-9]', str_)
        _lst = [ cc.capitalize() for cc in _lst if cc.isalnum() ]
        res  = ''.join(_lst)
        _LEN = len(res)

        if _LEN < 1:
            return res
        if startWithLowerCase_:
            if res[0].isupper():
                _tmp = res[0].lower()
                res  = _tmp if _LEN < 2 else _tmp+res[1:]
        return res

    @staticmethod
    def DeCapialize(str_, bThrowx_ =False):
        if not _Util.IsInstance(str_, str, bThrowx_):
            return None

        _LEN = len(str_)
        if _LEN < 1:
            return str_
        if str_[0].islower():
            return str_
        res = str_[0].lower()
        if _LEN > 1:
            res += str_[1:]
        return res

    @staticmethod
    def ToUpper(str_, asIdentifier_ =False, bThrowx_ =False):
        if not _Util.IsInstance(str_, str, bThrowx_):
            return None

        res = str_.upper()
        if asIdentifier_:
            _lst = re.split('[^A-Z0-9]', res)
            res = '_'.join(_lst)
        return res

    @staticmethod
    def ReplaceSubstring(astr_ : str, substrOld_ : str, substrNew_ : str, count_ =1):
        res = None
        if not (isinstance(astr_, str) and isinstance(substrOld_, str)):
            pass
        elif (substrNew_ is not None) and not isinstance(substrNew_, str):
            pass
        elif not isinstance(count_, int):
            pass
        elif (len(astr_) == 0) or (len(substrOld_) == 0):
            pass
        else:
            if count_ < 1:
                res = astr_
            else:
                if substrNew_ is None:
                    substrNew_ = _CommonDefines._STR_EMPTY
                res = astr_.replace(substrOld_, substrNew_, count_)

        if res is None:
            logif._LogBadUseEC(_EFwErrorCode.FE_00091, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_StrUtil_TID_005).format(str(astr_), str(substrOld_), str(substrNew_), str(count_)))
        return res

    @staticmethod
    def ListToString(list_, separator_ =_CommonDefines._CHAR_SIGN_SPACE, itemsTostringFunc_ =str):
        res = _CommonDefines._STR_EMPTY
        if isinstance(list_, list):
            if len(list_) > 0:
                res = [ itemsTostringFunc_(_ee) for _ee in list_ ]
                res = separator_.join(res)
        return res

    @staticmethod
    def IndentLines(str_ : str, times_ : int =1):
        if not isinstance(str_, str):
            str_ = str(str_)
        if len(str_.strip()) == 0:
            return _CommonDefines._STR_EMPTY

        _tmp  = None
        _tabs = None
        res, _tabs, _tmp = _CommonDefines._STR_EMPTY, _CommonDefines._STR_EMPTY, str_.split(_CommonDefines._CHAR_SIGN_LF)

        if (not isinstance(times_, int)) or (times_ < 1):
            times_ = 1
        while times_ > 0:
            _tabs += '\t'
            times_ -= 1
        for _ee in _tmp:
            res += _tabs + _ee + _CommonDefines._CHAR_SIGN_LF
        return res.rstrip()
