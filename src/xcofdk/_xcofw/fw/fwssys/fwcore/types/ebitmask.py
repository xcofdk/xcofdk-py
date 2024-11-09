# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : ebitmask.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from enum   import IntFlag
from enum   import unique
from typing import Union as _PyUnion

from xcofdk._xcofw.fwadapter                  import rlogif
from xcofdk._xcofw.fw.fwssys.fwcore.base.util import _Util


@unique
class _EBitMask(IntFlag):

    eNone = 0x0

    @staticmethod
    def GetIntegerBitFlagsList(iBitMask_ : _PyUnion[int, IntFlag]):
        if not _Util.IsInstance(iBitMask_, [int, IntFlag], bThrowx_=True): return None

        if isinstance(iBitMask_, IntFlag):
            iBitMask_ = iBitMask_.value

        res = []
        if iBitMask_ == 0:
            pass
        else:
            for _ii in range(iBitMask_.bit_length()):
                bitFlag = (0x1 << _ii)
                if (bitFlag & iBitMask_) != 0:
                    res.append(bitFlag)
        return res

    @staticmethod
    def IsEnumBitFlagSet(eBitMask_ : IntFlag, eBitFlags_ : _PyUnion[IntFlag, list], bCheckTypeMatch_ : bool =True, bAny_ =False):

        if not _Util.IsInstance(eBitMask_, IntFlag, bThrowx_=True): return False

        _myFlags = eBitFlags_
        if not _Util.IsInstance(eBitFlags_, list, bThrowx_=False):
            _myFlags = [eBitFlags_]

        for bb in _myFlags:
            if not bCheckTypeMatch_: pass
            elif type(eBitMask_) != type(bb):
                rlogif._LogOEC(True, -1015)
                return False
            if not _Util.IsInstance(bb, IntFlag, bThrowx_=True): return False
            _bHit = (eBitMask_ & bb).value != _EBitMask.eNone.value
            if bAny_:
                if _bHit:
                    return True
            elif not _bHit:
                return False
        return False if bAny_ else True

    @staticmethod
    def IsAnyEnumBitFlagSet(eBitMask_ : IntFlag, eBitFlags_ : _PyUnion[IntFlag, list], bCheckTypeMatch_ : bool =True):
        return _EBitMask.IsEnumBitFlagSet(eBitMask_, eBitFlags_, bCheckTypeMatch_=bCheckTypeMatch_, bAny_=True)

    @staticmethod
    def IsIntegerBitFlagSet(iBitMask_ : int, iBitFlags_ : int):
        if not _Util.IsInstance(iBitMask_, int, bThrowx_=True): return False

        _myFlags = iBitFlags_
        if not _Util.IsInstance(iBitFlags_, list, bThrowx_=False):
            _myFlags = [iBitFlags_]
        for bb in _myFlags:
            if not _Util.IsInstance(bb, int, bThrowx_=True): return False
            if (iBitMask_ & bb) == _EBitMask.eNone.value:
                return False
        return True

    @staticmethod
    def AddEnumBitFlag(eBitMask_ : IntFlag, eBitFlags_ : _PyUnion[IntFlag, list], bCheckTypeMatch_ : bool =True):

        if not _Util.IsInstance(eBitMask_, IntFlag, bThrowx_=True): return None

        _myFlags = eBitFlags_
        if not _Util.IsInstance(eBitFlags_, list, bThrowx_=False):
            _myFlags = [eBitFlags_]
        for bb in _myFlags:
            if not _Util.IsInstance(bb, IntFlag, bThrowx_=True): return None
            if not bCheckTypeMatch_: pass
            elif type(eBitMask_) != type(bb):
                rlogif._LogOEC(True, -1016)
                return None
            eBitMask_ |= bb
        return eBitMask_

    @staticmethod
    def AddIntegerBitFlag(iBitMask_ : int, iBitFlags_ : _PyUnion[int, list]):
        if not _Util.IsInstance(iBitMask_, int, bThrowx_=True): return None

        _myFlags = iBitFlags_
        if not _Util.IsInstance(iBitFlags_, list, bThrowx_=False):
            _myFlags = [iBitFlags_]
        for bb in _myFlags:
            if not _Util.IsInstance(bb, int, bThrowx_=True): return None
            iBitMask_ |= bb
        return iBitMask_

    @staticmethod
    def RemoveEnumBitFlag(eBitMask_ : IntFlag, eBitFlags_ : _PyUnion[IntFlag, list], bCheckTypeMatch_ : bool =True):

        if not _Util.IsInstance(eBitMask_, IntFlag, bThrowx_=True): return None

        _myFlags = eBitFlags_
        if not _Util.IsInstance(eBitFlags_, list, bThrowx_=False):
            _myFlags = [eBitFlags_]
        for bb in _myFlags:
            if not _Util.IsInstance(bb, IntFlag, bThrowx_=True): return None
            if not bCheckTypeMatch_: pass
            elif type(eBitMask_) != type(bb):
                rlogif._LogOEC(True, -1017)
                return None
            eBitMask_ &= ~bb
        return eBitMask_

    @staticmethod
    def RemoveIntegerBitFlag(iBitMask_ : int, iBitFlags_ : _PyUnion[int, list]):
        if not _Util.IsInstance(iBitMask_, int, bThrowx_=True): return None

        _myFlags = iBitFlags_
        if not _Util.IsInstance(iBitFlags_, list, bThrowx_=False):
            _myFlags = [iBitFlags_]
        for bb in _myFlags:
            if not _Util.IsInstance(bb, int, bThrowx_=True): return None
            iBitMask_ &= ~bb
        return iBitMask_
