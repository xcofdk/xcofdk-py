# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : atomicint.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from threading import RLock as _PyRLock

from _fwadapter                     import rlogif
from _fw.fwssys.fwcore.base.util    import _Util
from _fw.fwssys.fwerrh.fwerrorcodes import _EFwErrorCode

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _AtomicInteger(object):
    __slots__ = [ '__l' , '__bA' , '__v' ]

    def __init__(self, value_ =0):
        self.__l  = None
        self.__v  = None
        self.__bA = False

        if value_ is None:
            val = 0
        elif isinstance(value_, int):
            val = value_
        elif getattr(value_, _FwTDbEngine.GetText(_EFwTextID.eMisc_Value), None) is None:
            val = None
            rlogif._LogOEC(True, _EFwErrorCode.FE_00420)
        else:
            _Util.IsInstance(value_.value, int, bThrowx_=True)
            self.__bA = True
            val = value_

        self.__v = val
        self.__l = _PyRLock()

    @property
    def value(self):
        with self.__l:
            return self.__v if not self.__bA else self.__v.value

    @property
    def name(self):
        with self.__l:
            res = None
            if self.__bA and not getattr(self.__v, _FwTDbEngine.GetText(_EFwTextID.eMisc_Name), None) is None:
                    res = self.__v.name
            else:
                res = str(self.__v)
            return res

    def Increment(self):
        if self.__bA:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00421)

        with self.__l:
            self.__v += 1
            return self.__v

    def Decrement(self):
        if self.__bA:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00422)

        with self.__l:
            self.__v -= 1
            return self.__v

    def SetValue(self, value_):
        with self.__l:
            if self.__bA:
                _Util.GetAttribute(value_, _FwTDbEngine.GetText(_EFwTextID.eMisc_Value))

            self.__v = value_
            return self.__v if not self.__bA else self.__v.value

    def CleanUp(self):
        self.__l = None

    def ToString(self):
        return str(self)

    def __str__(self):
        with self.__l:
            val = self.__v if not self.__bA else self.__v.value
            if not self.__bA or getattr(self.__v, _FwTDbEngine.GetText(_EFwTextID.eMisc_Name), None) is None:
                res = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_006).format(val)
            else:
                res = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_011).format(getattr(self.__v, _FwTDbEngine.GetText(_EFwTextID.eMisc_Name)), val)
            return res

    def __eq__(self, other_):
        with self.__l:
            return self.__Compare(other_) == 0
    def __ne__(self, other_):
        with self.__l:
            return self.__Compare(other_) != 0
    def __lt__(self, other_):
        with self.__l:
            return self.__Compare(other_) <= -1
    def __le__(self, other_):
        with self.__l:
            _cmp = self.__Compare(other_)
            return _cmp <= -1 or _cmp == 0

    def __gt__(self, other_):
        with self.__l:
            return self.__Compare(other_) == 1

    def __ge__(self, other_):
        with self.__l:
            _cmp = self.__Compare(other_)
            return _cmp == 1 or _cmp == 0

    @property
    def _lock(self):
        return self.__l

    def __Compare(self, other_):
        if other_ is None:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00423)
            return -2

        otherValueAttr = getattr(other_, _FwTDbEngine.GetText(_EFwTextID.eMisc_Value), None)
        if otherValueAttr is None:
            if not _Util.IsInstance(other_, int, bThrowx_=True):
                return -3

        if otherValueAttr is None:
            otherVal = other_
        else:
            otherVal = other_.value

        selfVal = self.__v.value if self.__bA else self.__v

        res = 0
        if selfVal < otherVal:
            res = -1
        elif selfVal > otherVal:
            res = 1
        return res

