# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwtdbengine.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

import os.path
import time

from _fw.fwssys.fwcore.types.commontypes import _CommonDefines

from _fw.fwtdb.fwtextid import _EFwTextID
from _fw.fwtdb.fwtextdb import _FwTextDB
from _fw.fwtdb.fwtextdb import _ETextDBCreateStatus
from _fw.fwtdb.fwtextdb import _TDBPrint

class _FwTDbEngine:
    __slots__ = []

    __txtDB      = None
    __bPkgDist   = True
    __bLiveCheck = True

    __PDRDN   = None
    __PDRDPN  = None
    __PDRDBwD = None

    __TICKS_PER_USECOND        = 10**3
    __DB_CREATE_TIMESTAMP      = None
    __DB_FIRST_FETCH_TIMESTAMP = None

    @staticmethod
    def IsTextAvailable(fwTxtID_ : _EFwTextID) -> bool:
        return False if _FwTDbEngine.__txtDB is None else _FwTDbEngine.__txtDB._IsFwTextAvailable(fwTxtID_)

    @staticmethod
    def GetCreateStatus() -> _ETextDBCreateStatus:
        return _FwTextDB._GetCreateStatus()

    @staticmethod
    def GetText(fwTxtID_ : _EFwTextID) -> str:
        if _FwTDbEngine.__DB_FIRST_FETCH_TIMESTAMP is None:
            _FwTDbEngine.__DB_FIRST_FETCH_TIMESTAMP = _FwTDbEngine.__GetCurTicksUS()

        _BAD_RES = None if not _FwTDbEngine.__bPkgDist else _CommonDefines._STR_EMPTY

        if _FwTextDB._GetCreateStatus().isTDBIdle:
            _bPkgDist      = None
            _xcofdkRootDir = None
            _xcofdkRootDir, _bPkgDist = _FwTDbEngine._GetXcofdkRootAbsPath()
            if not _FwTDbEngine._CreateDB(_bPkgDist):
                return _BAD_RES

        if not _FwTextDB._GetCreateStatus().isTDBCreated:
            return _BAD_RES

        res =_FwTDbEngine.__txtDB._GetFwText(fwTxtID_)
        if (res is None) or (not _FwTDbEngine.__bPkgDist):
            if res is None:
                res = _BAD_RES
            elif _FwTDbEngine.__bLiveCheck:
                res = _FwTDbEngine.__HexDecode(res)
        else:
            res = _FwTDbEngine.__HexDecode(res)
        return res

    @staticmethod
    def _GetDBTimestamps():
        return _FwTDbEngine.__DB_FIRST_FETCH_TIMESTAMP, _FwTDbEngine.__DB_CREATE_TIMESTAMP

    @staticmethod
    def _CreateDB(bPkgDist_ =False, bReCreate_ =False) -> bool:
        _dbCStatus = _FwTextDB._GetCreateStatus()
        if _dbCStatus.isTDBCreated:
            return True
        if _dbCStatus.isTDBFailed:
            return False
        if _dbCStatus.isTDBDestroyed:
            if not bReCreate_:
                return False

        _FwTDbEngine.__bPkgDist = bPkgDist_

        _FwTDbEngine.__txtDB               = _FwTextDB._CreateDB(bPkgDist_, bReCreate_=bReCreate_)
        _FwTDbEngine.__DB_CREATE_TIMESTAMP = _FwTDbEngine.__GetCurTicksUS()

        if _FwTDbEngine.__txtDB is None:
            return False
        if bPkgDist_:
            return True
        if not _FwTDbEngine.__bLiveCheck:
            return True

        res = True
        _myTxt        = None
        _myTxtDB      = None
        _myfwTxtList  = None
        _myfwTxtCount = 0

        _myTxtDB      = _FwTDbEngine.__txtDB
        _myfwTxtList  = _myTxtDB._fwTextList
        _myfwTxtCount = len(_myfwTxtList)

        for _ii in range(_myfwTxtCount):
            _myTxt = _myfwTxtList[_ii]
            _myTxtH = _FwTDbEngine.__HexEncode(_myTxt)
            if (_myTxtH is None) or (_myTxt != _FwTDbEngine.__HexDecode(_myTxtH)):
                res = False
                _FwTDbEngine.__txtDB = None
                break
            _myfwTxtList[_ii] = _myTxtH

        _FwTDbEngine.__DB_CREATE_TIMESTAMP = _FwTDbEngine.__GetCurTicksUS()
        return res

    @staticmethod
    def _DestroyDB():
        if _FwTDbEngine.__txtDB is not None:
            _FwTDbEngine.__txtDB = None
            _FwTextDB._DestroyDB()

    @staticmethod
    def _GetXcofdkRootAbsPath():
        _FwTDbEngine.__Init()

        _bwDepth       = _FwTDbEngine.__PDRDBwD
        _xcofdkRootDir = os.path.normpath(__file__)

        for _ii in range(_bwDepth):
            _xcofdkRootDir = os.path.dirname(_xcofdkRootDir)
        if not os.path.exists(_xcofdkRootDir):
            _TDBPrint(f'Non-existing xco root path: {_xcofdkRootDir}\n')
            return None, None

        _rootDirBN = os.path.basename(_xcofdkRootDir)
        if _rootDirBN != _FwTDbEngine.__PDRDN:
            _TDBPrint(f'Unexpected path while trying to identify xco root path: {_xcofdkRootDir}\n')
            return None, None

        _pdirBN = os.path.basename(os.path.dirname(_xcofdkRootDir))
        _bPkgDist = _pdirBN != _FwTDbEngine.__PDRDPN

        return _xcofdkRootDir, _bPkgDist

    @staticmethod
    def __Init():
        if _FwTDbEngine.__PDRDBwD is None:
            _FwTDbEngine.__PDRDN   = _FwTDbEngine.__HexDecode('7863 6f66 646b')
            _FwTDbEngine.__PDRDPN  = _FwTDbEngine.__HexDecode('73 7263')
            _FwTDbEngine.__PDRDBwD = 4

    @staticmethod
    def __HexEncode(rawText_ : str) -> str:
        return None if not isinstance(rawText_, str) else rawText_.encode().hex(' ', 2)

    @staticmethod
    def __HexDecode(hexText_ : str) -> str:
        return None if not isinstance(hexText_, str) else bytes.fromhex(hexText_).decode()

    @staticmethod
    def __GetCurTicksUS():
        return int(time.time_ns() // _FwTDbEngine.__TICKS_PER_USECOND)
