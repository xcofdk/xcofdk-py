# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : ebitmask.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum   import IntFlag
from enum   import unique
from typing import Union

from _fwadapter                     import rlogif
from _fw.fwssys.fwcore.base.util    import _Util
from _fw.fwssys.fwerrh.fwerrorcodes import _EFwErrorCode

@unique
class _EBitMask(IntFlag):
    eNone = 0x0

    @staticmethod
    def GetIntegerBitFlagsList(iBitMask_ : Union[int, IntFlag]):
        if not _Util.IsInstance(iBitMask_, [int, IntFlag], bThrowx_=True): return None

        if isinstance(iBitMask_, IntFlag):
            iBitMask_ = iBitMask_.value

        res = []
        if iBitMask_ != 0:
            for _ii in range(iBitMask_.bit_length()):
                bitFlag = (0x1 << _ii)
                if (bitFlag & iBitMask_) != 0:
                    res.append(bitFlag)
        return res

    @staticmethod
    def IsEnumBitFlagSet(eBitMask_ : IntFlag, eBitFlags_ : Union[IntFlag, list], bCheckTypeMatch_ : bool =True, bAny_ =False):
        if not _Util.IsInstance(eBitMask_, IntFlag, bThrowx_=True): return False

        _myFlags = eBitFlags_
        if not _Util.IsInstance(eBitFlags_, list, bThrowx_=False):
            _myFlags = [eBitFlags_]

        for _bb in _myFlags:
            if not bCheckTypeMatch_:
                pass
            elif type(eBitMask_) != type(_bb):
                rlogif._LogOEC(True, _EFwErrorCode.FE_00424)
                return False
            if not _Util.IsInstance(_bb, IntFlag, bThrowx_=True): return False
            _bHit = (eBitMask_ & _bb).value != _EBitMask.eNone.value
            if bAny_:
                if _bHit:
                    return True
            elif not _bHit:
                return False
        return False if bAny_ else True

    @staticmethod
    def IsAnyEnumBitFlagSet(eBitMask_ : IntFlag, eBitFlags_ : Union[IntFlag, list], bCheckTypeMatch_ : bool =True):
        return _EBitMask.IsEnumBitFlagSet(eBitMask_, eBitFlags_, bCheckTypeMatch_=bCheckTypeMatch_, bAny_=True)

    @staticmethod
    def IsIntegerBitFlagSet(iBitMask_ : int, iBitFlags_ : int):
        if not _Util.IsInstance(iBitMask_, int, bThrowx_=True): return False

        _myFlags = iBitFlags_
        if not _Util.IsInstance(iBitFlags_, list, bThrowx_=False):
            _myFlags = [iBitFlags_]
        for _bb in _myFlags:
            if not _Util.IsInstance(_bb, int, bThrowx_=True): return False
            if (iBitMask_ & _bb) == _EBitMask.eNone.value:
                return False
        return True

    @staticmethod
    def AddEnumBitFlag(eBitMask_ : IntFlag, eBitFlags_ : Union[IntFlag, list], bCheckTypeMatch_ : bool =True):
        if not _Util.IsInstance(eBitMask_, IntFlag, bThrowx_=True): return None

        _myFlags = eBitFlags_
        if not _Util.IsInstance(eBitFlags_, list, bThrowx_=False):
            _myFlags = [eBitFlags_]
        for _bb in _myFlags:
            if not _Util.IsInstance(_bb, IntFlag, bThrowx_=True): return None
            if not bCheckTypeMatch_: pass
            elif type(eBitMask_) != type(_bb):
                rlogif._LogOEC(True, _EFwErrorCode.FE_00425)
                return None
            eBitMask_ |= _bb
        return eBitMask_

    @staticmethod
    def AddIntegerBitFlag(iBitMask_ : int, iBitFlags_ : Union[int, list]):
        if not _Util.IsInstance(iBitMask_, int, bThrowx_=True): return None

        _myFlags = iBitFlags_
        if not _Util.IsInstance(iBitFlags_, list, bThrowx_=False):
            _myFlags = [iBitFlags_]
        for _bb in _myFlags:
            if not _Util.IsInstance(_bb, int, bThrowx_=True): return None
            iBitMask_ |= _bb
        return iBitMask_

    @staticmethod
    def RemoveEnumBitFlag(eBitMask_ : IntFlag, eBitFlags_ : Union[IntFlag, list], bCheckTypeMatch_ : bool =True):
        if not _Util.IsInstance(eBitMask_, IntFlag, bThrowx_=True): return None

        _myFlags = eBitFlags_
        if not _Util.IsInstance(eBitFlags_, list, bThrowx_=False):
            _myFlags = [eBitFlags_]
        for _bb in _myFlags:
            if not _Util.IsInstance(_bb, IntFlag, bThrowx_=True): return None
            if not bCheckTypeMatch_: pass
            elif type(eBitMask_) != type(_bb):
                rlogif._LogOEC(True, _EFwErrorCode.FE_00426)
                return None
            eBitMask_ &= ~_bb
        return eBitMask_

    @staticmethod
    def RemoveIntegerBitFlag(iBitMask_ : int, iBitFlags_ : Union[int, list]):
        if not _Util.IsInstance(iBitMask_, int, bThrowx_=True): return None

        _myFlags = iBitFlags_
        if not _Util.IsInstance(iBitFlags_, list, bThrowx_=False):
            _myFlags = [iBitFlags_]
        for _bb in _myFlags:
            if not _Util.IsInstance(_bb, int, bThrowx_=True): return None
            iBitMask_ &= ~_bb
        return iBitMask_
