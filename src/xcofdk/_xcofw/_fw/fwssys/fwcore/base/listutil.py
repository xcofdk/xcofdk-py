# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : listutil.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from _fw.fwssys.fwcore.base.util import _Util

class _ListUtil:
    @staticmethod
    def GetIndex(alist_ : list, item_):
        res = -1
        if isinstance(alist_, list):
            _OWN_SOLUTION = False

            if _OWN_SOLUTION:
                _LGTH = len(alist_)
                if _LGTH != 0:
                    hits = [_ii for _ii in range(_LGTH) if alist_[_ii] == item_]
                    if len(hits) > 0:
                        res = hits[0]
            else:
                try:
                    res = alist_.index(item_)
                except ValueError:
                    res = -1
        return res

    @staticmethod
    def GetMaxLen(sequence_):
        if isinstance(sequence_, dict):
            res = max( [len(_kk) for _kk in sequence_.keys()] )
        elif isinstance(sequence_, list):
            res = max( [len(_kk) for _kk in sequence_] )
        else:
            res = 0
        return res

    @staticmethod
    def Clone(srcList_, includeDuplicates_ =False):
        if srcList_ is None:
            return None

        _tmp = srcList_
        if not isinstance(srcList_, list):
            _Util.GetAttribute(srcList_, '__iter__')
            _tmp = list(srcList_)

        if includeDuplicates_:
            res = list(_tmp)
        else:
            res = list()
            for _ee in _tmp:
                if not _ee in res:
                    res.append(_ee)
        return res

    @staticmethod
    def Unite(srcList_, otherList_, inplace_ =False):
        if otherList_ is None:
            return srcList_
        _Util.IsInstance(otherList_, list)

        if inplace_:
            for _ee in otherList_:
                if not _ee in srcList_:
                    srcList_.append(_ee)
            res = srcList_
        else:
            res = list(set(srcList_).union(otherList_))
        return res

    @staticmethod
    def Complement(listA_ : list, listB_ : list):
        if listA_ is None or listB_ is None:
            return listA_
        return [ _ee for _ee in listA_ if _ee not in listB_ ]

    @staticmethod
    def HasDuplicates(alist_ : list, bThrowx_ =False):
        if not _Util.IsInstance(alist_, list, bThrowx_=bThrowx_): return False
        return len(alist_) != len(set(alist_))

    @staticmethod
    def RemoveDuplicates(alist_ : list, inplace_ =False, bThrowx_ =False):
        if not _Util.IsInstance(alist_, list, bThrowx_=bThrowx_): return None

        res = []
        for _ee in alist_:
            if not _ee in res:
                res.append(_ee)

        if inplace_:
            if len(res) > 0:
                alist_.clear()
                alist_ += res
                res.clear()
            res = alist_
        return res

