# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwtextdb.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum import auto
from enum import Enum
from enum import unique

from _fw.fwssys.fwcore.types.commontypes import SyncPrint

from _fw.fwtdb.fwtextid  import _EFwTextID
from _fw.fwtdb.fwtextdef import _GetFwTextDefines

@unique
class _ETextDBCreateStatus(Enum):
    eTDBIdle      = 0
    eTDBCreated   = auto()
    eTDBFailed    = auto()
    eTDBDestroyed = auto()

    @property
    def isTDBIdle(self):
        return self == _ETextDBCreateStatus.eTDBIdle

    @property
    def isTDBCreated(self):
        return self == _ETextDBCreateStatus.eTDBCreated

    @property
    def isTDBFailed(self):
        return self == _ETextDBCreateStatus.eTDBFailed

    @property
    def isTDBDestroyed(self):
        return self == _ETextDBCreateStatus.eTDBDestroyed

class _FwTextDB:
    __slots__  = [ '__s' , '__bP' , '__at' , '__am' ]

    __txtDbCSt   = _ETextDBCreateStatus.eTDBIdle
    __theFwTxtDB = None

    def __init__(self, bPkgDist_ =False, bReCreate_ =False):
        self.__s  = None
        self.__am = None
        self.__at = None
        self.__bP = None

        if _FwTextDB.__txtDbCSt.isTDBCreated:
            SyncPrint.Print('[FwTDB] Violation against singleton of text DB.')
            return
        if _FwTextDB.__txtDbCSt.isTDBFailed:
            SyncPrint.Print('[FwTDB] Violation against no-re-try of failed attempts to create text DB.')
            return
        if _FwTextDB.__txtDbCSt.isTDBDestroyed:
            if not bReCreate_:
                SyncPrint.Print('[FwTDB] Violation against no-re-creation after destroy text DB.')
                return
            _FwTextDB.__txtDbCSt = _ETextDBCreateStatus.eTDBIdle

        _dictFwTxt   = _GetFwTextDefines()
        _EFwTidClass = _EFwTextID

        _allKeys = _dictFwTxt.keys()
        _allKeys = [ _kk.value for _kk in _allKeys ]
        _allKeys = sorted(_allKeys)

        self.__am = []
        self.__at = [ _dictFwTxt[_EFwTidClass(_kk)] for _kk in _allKeys ]
        self.__s  = len(self.__at)
        self.__bP = bPkgDist_

        for _n, _m in _EFwTidClass.__members__.items():
            if _m.value not in _allKeys:
                self.__am.append(_m.value)
        if len(self.__am) < 1:
            self.__am = None

        _allKeys.clear()
        _dictFwTxt.clear()

        if self.__at[0] is None:
            self._Destroy()
            _FwTextDB.__txtDbCSt = _ETextDBCreateStatus.eTDBFailed
            SyncPrint.Print(f'[FwTDB] Unexpected fatal error while trying to create text DB.')
        else:
            _FwTextDB.__txtDbCSt   = _ETextDBCreateStatus.eTDBCreated
            _FwTextDB.__theFwTxtDB = self

    @property
    def _fwTextList(self):
        return self.__at

    @property
    def _dbSize(self):
        return 0 if self.__isInvalid else self.__s

    def _IsFwTextAvailable(self, fwTxtID_ : _EFwTextID) -> bool:
        if self.__isInvalid:
            res = False
        elif not isinstance(fwTxtID_, _EFwTextID):
            res = False
        elif self.__am is None:
            res = True
        elif fwTxtID_.value in self.__am:
            res = False
        else:
            res = True
        return res

    def _GetFwText(self, fwTxtID_ : _EFwTextID):
        if self.__isInvalid:
            return None

        _bBadReq = False
        if not self._IsFwTextAvailable(fwTxtID_):
            if not isinstance(fwTxtID_, _EFwTextID):
                _bBadReq = True
                SyncPrint.Print(f'[FwTDB] Invalid fw text id object: {type(fwTxtID_).__name__}')
            else:
                SyncPrint.Print(f'[FwTDB] Missing text for passed in id: {fwTxtID_.compactName}')

        if _bBadReq:
            res = _FwTextDB.__at[_EFwTextID.eInvalidText.value] if self.__bP else None
        else:
            res = self.__at[fwTxtID_.value]
        return res

    def _Destroy(self, onFailure_ =False):
        if self.__at is not None:
            if self.__am is not None:
                self.__am.clear()
            self.__at.clear()
            self.__at = None
            self.__bP = None
            self.__am = None

            _FwTextDB.__theFwTxtDB = None
            if not onFailure_:
                _FwTextDB.__txtDbCSt = _ETextDBCreateStatus.eTDBDestroyed

    @staticmethod
    def _GetCreateStatus() -> _ETextDBCreateStatus:
        return _FwTextDB.__txtDbCSt

    @staticmethod
    def _CreateDB(bPkgDist_ =False, bReCreate_ =False):
        _FwTextDB(bPkgDist_, bReCreate_=bReCreate_)
        if not _FwTextDB.__txtDbCSt.isTDBCreated:
            SyncPrint.Print('[FwTDB] Failed to create text DB.')
        return _FwTextDB.__theFwTxtDB

    @staticmethod
    def _DestroyDB():
        if _FwTextDB.__theFwTxtDB is not None:
            _FwTextDB.__theFwTxtDB._Destroy()

    @property
    def __isInvalid(self):
        return self.__at is None
