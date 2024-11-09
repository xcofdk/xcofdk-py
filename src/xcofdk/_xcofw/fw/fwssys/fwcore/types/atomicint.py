# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : atomicint.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from threading import RLock as _PyRLock

from xcofdk._xcofw.fwadapter                  import rlogif
from xcofdk._xcofw.fw.fwssys.fwcore.base.util import _Util

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine


class _AtomicInteger(object):

    __slots__ = [ '__lock' , '__bAttr' , '__value' ]

    def __init__(self, value_ =0):

        self.__lock  = None
        self.__bAttr = False
        self.__value = None

        if value_ is None:
            val = 0
        elif isinstance(value_, int):
            val = value_
        elif getattr(value_, _FwTDbEngine.GetText(_EFwTextID.eMisc_Value), None) is None:
            val = None
            rlogif._LogOEC(True, -1041)
        else:
            _Util.IsInstance(value_.value, int, bThrowx_=True)
            self.__bAttr = True
            val = value_

        self.__value = val
        self.__lock = _PyRLock()

    @property
    def value(self):
        with self.__lock:
            return self.__value if not self.__bAttr else self.__value.value

    @property
    def name(self):
        with self.__lock:
            res = None
            if self.__bAttr and not getattr(self.__value, _FwTDbEngine.GetText(_EFwTextID.eMisc_Name), None) is None:
                    res = self.__value.name
            else:
                res = str(self.__value)
            return res

    def Increment(self):
        if self.__bAttr:
            rlogif._LogOEC(True, -1042)

        with self.__lock:
            self.__value += 1
            return self.__value

    def Decrement(self):
        if self.__bAttr:
            rlogif._LogOEC(True, -1043)

        with self.__lock:
            self.__value -= 1
            return self.__value

    def SetValue(self, value_):
        with self.__lock:
            if self.__bAttr:
                _Util.GetAttribute(value_, _FwTDbEngine.GetText(_EFwTextID.eMisc_Value))

            self.__value = value_
            return self.__value if not self.__bAttr else self.__value.value

    def CleanUp(self):
        self.__lock = None

    def ToString(self):
        return str(self)

    def __str__(self):
        with self.__lock:
            val = self.__value if not self.__bAttr else self.__value.value
            if not self.__bAttr or getattr(self.__value, _FwTDbEngine.GetText(_EFwTextID.eMisc_Name), None) is None:
                res = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_006).format(val)
            else:
                res = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_011).format(getattr(self.__value, _FwTDbEngine.GetText(_EFwTextID.eMisc_Name)), val)
            return res

    def __eq__(self, other_):
        with self.__lock:
            return self.__Compare(other_) == 0
    def __ne__(self, other_):
        with self.__lock:
            return self.__Compare(other_) != 0
    def __lt__(self, other_):
        with self.__lock:
            return self.__Compare(other_) <= -1
    def __le__(self, other_):
        with self.__lock:
            cmp = self.__Compare(other_)
            return cmp <= -1 or cmp == 0

    def __gt__(self, other_):
        with self.__lock:
            return self.__Compare(other_) == 1

    def __ge__(self, other_):
        with self.__lock:
            cmp = self.__Compare(other_)
            return cmp == 1 or cmp == 0

    @property
    def _lock(self):
        return self.__lock

    def __Compare(self, other_):
        if other_ is None:
            rlogif._LogOEC(True, -1044)
            return -2

        otherValueAttr = getattr(other_, _FwTDbEngine.GetText(_EFwTextID.eMisc_Value), None)
        if otherValueAttr is None:
            if not _Util.IsInstance(other_, int, bThrowx_=True):
                return -3

        if otherValueAttr is None:
            otherVal = other_
        else:
            otherVal = other_.value

        selfVal = self.__value.value if self.__bAttr else self.__value

        res = 0
        if selfVal < otherVal:
            res = -1
        elif selfVal > otherVal:
            res = 1
        return res

