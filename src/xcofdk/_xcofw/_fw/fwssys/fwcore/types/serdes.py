# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : serdes.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

import pickle as _PyPickle
from   enum   import Enum
from   enum   import unique
from   typing import Union

from _fwadapter                          import rlogif
from _fw.fwssys.fwcore.logging           import logif
from _fw.fwssys.fwcore.base.fsutil       import _FSUtil
from _fw.fwssys.fwcore.types.aobject     import _AbsObject
from _fw.fwssys.fwcore.types.commontypes import _CommonDefines

from _fw.fwssys.fwerrh.fwerrorcodes import _EFwErrorCode

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

@unique
class _EPPVersion(Enum):
    eVersion0 =0
    eVersion1 =1
    eVersion2 =2
    eVersion3 =3
    eVersion4 =4
    eVersion5 =5

class SerDes(_AbsObject):
    __ppVersion  = _EPPVersion(_PyPickle.HIGHEST_PROTOCOL)

    def __init__(self, filePath_ =None, binaryFormat_ =True):
        super().__init__()

        self.__fh           = None
        self.__filePath     = filePath_
        self.__writeOpened  = False
        self.__readOpened   = False
        self.__binaryFormat = True

        if not binaryFormat_:
            logif._LogNotSupportedEC(_EFwErrorCode.UE_00145, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_SerDes_TID_001).format(str(self.filePath)))

    @staticmethod
    def IsNoneDump(data_ : bytes):
        res = isinstance(data_, bytes)
        if res:
            try:
                res = _PyPickle.loads(data_)
                res = res is None
            except (_PyPickle.PickleError, Exception):
                res = False
        return res

    @staticmethod
    def SerializeObject(obj_, bTreatAsUserError_ =False, bAllowNone_ =False) -> Union[bytes, None]:
        res = None
        if obj_ is None:
            if not bAllowNone_:
                rlogif._LogOEC(True, _EFwErrorCode.FE_00932)
                return res

        try:
            res = _PyPickle.dumps(obj_, SerDes.__ppVersion.value)
        except (_PyPickle.PickleError, Exception) as _xcp:
            _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_SerDes_TID_003).format(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_SerDes_TID_002), _xcp)
            if bTreatAsUserError_:
                logif._LogErrorEC(_EFwErrorCode.UE_00111, _msg)
            else:
                logif._LogFatalEC(_EFwErrorCode.FE_00045, _msg)
        return res

    @staticmethod
    def DeserializeData(data_ : bytes, bTreatAsUserError_ =False):
        res = None
        if not isinstance(data_, bytes):
            rlogif._LogOEC(True, _EFwErrorCode.FE_00434)
            return res

        try:
            res = _PyPickle.loads(data_)
        except (_PyPickle.PickleError, Exception) as _xcp:
            _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_SerDes_TID_004).format(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_SerDes_TID_002), _xcp)
            if bTreatAsUserError_:
                logif._LogErrorEC(_EFwErrorCode.UE_00112, _msg)
            else:
                logif._LogFatalEC(_EFwErrorCode.FE_00046, _msg)
        return res

    @property
    def isBinaryFormat(self):
        return self.__binaryFormat

    @property
    def filePath(self):
        return self.__filePath

    def Serialize(self, obj_) -> bytes:
        res = None
        if obj_ is None:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00435)
            return res

        try:
            res = _PyPickle.dumps(obj_, SerDes.__ppVersion.value)
        except (_PyPickle.PickleError, Exception) as _xcp:
            _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_SerDes_TID_005).format(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_SerDes_TID_002), self)
            logif._LogSysExceptionEC(_EFwErrorCode.FE_00006, _msg, _xcp, logif._GetFormattedTraceback())
        return res

    def Deserialize(self, data_ : bytes):
        res = None
        if data_ is None:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00436)
            return res

        try:
            res = _PyPickle.loads(data_)
        except (_PyPickle.PickleError, Exception) as _xcp:
            _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_SerDes_TID_006).format(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_SerDes_TID_002), self)
            logif._LogSysExceptionEC(_EFwErrorCode.FE_00007, _msg, _xcp, logif._GetFormattedTraceback())
        return res

    def SerializeToFile(self, obj_, autoCloseFile_ =True):
        if obj_ is None:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00437)
            return False

        dirPath = _FSUtil.GetDirPath(self.__filePath)
        _FSUtil.MkDir(dirPath)

        if not self.__IsFileOpen(True):
            if not self.__OpenFile(True):
                return False

        try:
            _PyPickle.dump(obj_, self.__fh, SerDes.__ppVersion.value)
        except (_PyPickle.PickleError, Exception) as _xcp:
            _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_SerDes_TID_007).format(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_SerDes_TID_002), self)
            logif._LogSysExceptionEC(_EFwErrorCode.FE_00008, _msg, _xcp, logif._GetFormattedTraceback())

            self.CloseFile()
            return False

        if autoCloseFile_:
            self.CloseFile()
        return True

    def DeserializeFromFile(self, autoCloseFile_ =True):
        if not self.__IsFileOpen(False):
            if not self.__OpenFile(False):
                return None

        res = None
        try:
            res = _PyPickle.load(self.__fh)
        except EOFError as e:
            res = None
        except (_PyPickle.PickleError, Exception) as _xcp:
            _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_SerDes_TID_008).format(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_SerDes_TID_002), self)
            logif._LogSysExceptionEC(_EFwErrorCode.FE_00009, _msg, _xcp, logif._GetFormattedTraceback())

        if autoCloseFile_ or res is None:
            self.CloseFile()
        return res

    def CloseFile(self):
        if self.__writeOpened or self.__readOpened:
            self.__fh.close()
            self.__fh = None
            self.__writeOpened = False
            self.__readOpened = False

    def _ToString(self, bPropsOnly_ =False):
        if self.__filePath is None:
            res = _FwTDbEngine.GetText(_EFwTextID.eSerDes_ToString_03).format(self.__binaryFormat)
        else:
            res = _FwTDbEngine.GetText(_EFwTextID.eSerDes_ToString_04).format(self.__binaryFormat, self.__filePath)

        if not bPropsOnly_:
            res = _FwTDbEngine.GetText(_EFwTextID.eSerDes_ToString_02).format(res)
        return res

    def _CleanUp(self):
        self.CloseFile()
        self.__filePath = None

    def __OpenFile(self, writeMode_):
        if self.filePath is None:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00438)
            return False

        if self.__IsFileOpen(not writeMode_):
            if self.__writeOpened:
                logif._LogImplErrorEC(_EFwErrorCode.FE_00828, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_SerDes_TID_009).format(self))
            else:
                logif._LogImplErrorEC(_EFwErrorCode.FE_00829, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_SerDes_TID_010).format(self))
            return False

        if self.__IsFileOpen(writeMode_):
            return True

        try:
            _mode  = _CommonDefines._CHAR_SIGN_FILE_MODE_WRITE if writeMode_ else _CommonDefines._CHAR_SIGN_FILE_MODE_READ
            _mode += _CommonDefines._CHAR_SIGN_FILE_MODE_BINARY if self.isBinaryFormat else _CommonDefines._STR_EMPTY
            _fh = open(self.filePath, _mode)
        except (FileNotFoundError, Exception) as _xcp:
            _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_SerDes_TID_011).format(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_SerDes_TID_002), self)
            logif._LogSysExceptionEC(_EFwErrorCode.FE_00010, _msg, _xcp, logif._GetFormattedTraceback())
            return False

        self.__fh = _fh
        if writeMode_:
            self.__writeOpened = True
        else:
            self.__readOpened = True
        return True

    def __IsFileOpen(self, writeMode_):
        if writeMode_:
            return self.__writeOpened
        else:
            return self.__readOpened

