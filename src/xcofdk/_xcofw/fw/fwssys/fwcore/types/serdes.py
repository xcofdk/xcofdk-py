# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : serdes.py
#
# Copyright(c) 2023-2024 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


import pickle as _PyPickle
from   enum import Enum
from   enum import unique

from xcofdk._xcofw.fwadapter                          import rlogif
from xcofdk._xcofw.fw.fwssys.fwcore.logging           import logif
from xcofdk._xcofw.fw.fwssys.fwcore.base.fsutil       import _FSUtil
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject     import _AbstractObject
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes import _CommonDefines

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine


@unique
class _EPPVersion(Enum):

    eVersion0 =0
    eVersion1 =1
    eVersion2 =2
    eVersion3 =3
    eVersion4 =4
    eVersion5 =5


class SerDes(_AbstractObject):

    __ppVersion  = _EPPVersion(_PyPickle.HIGHEST_PROTOCOL)


    def __init__(self, filePath_ =None, binaryFormat_ =True):
        super().__init__()

        self.__fh           = None
        self.__filePath     = filePath_
        self.__writeOpened  = False
        self.__readOpened   = False
        self.__binaryFormat = True

        if not binaryFormat_:
            logif._LogNotSupported(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_SerDes_TextID_001).format(str(self.filePath)))

    @staticmethod
    def SerializeObject(obj_, bTreatAsUserError_ =False) -> bytes:
        res = None
        if obj_ is None:
            rlogif._LogOEC(True, -1007)
            return res

        try:
            res = _PyPickle.dumps(obj_, SerDes.__ppVersion.value)
        except( _PyPickle.PickleError, Exception, BaseException ) as xcp:
            _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_SerDes_TextID_003).format(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_SerDes_TextID_002), xcp)
            if bTreatAsUserError_:
                logif._LogError(_msg)
            else:
                logif._LogFatal(_msg)
        return res

    @staticmethod
    def DeserializeData(data_ : bytes, bTreatAsUserError_ =False):
        res = None
        if not isinstance(data_, bytes):
            rlogif._LogOEC(True, -1008)
            return res

        try:
            res = _PyPickle.loads(data_)
        except( _PyPickle.PickleError, Exception, BaseException ) as xcp:
            _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_SerDes_TextID_004).format(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_SerDes_TextID_002), xcp)
            if bTreatAsUserError_:
                logif._LogError(_msg)
            else:
                logif._LogFatal(_msg)
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
            rlogif._LogOEC(True, -1009)
            return res

        try:
            res = _PyPickle.dumps(obj_, SerDes.__ppVersion.value)
        except (_PyPickle.PickleError, BaseException) as xcp:
            _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_SerDes_TextID_005).format(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_SerDes_TextID_002), self)
            logif._LogSysException(_msg, xcp, logif._GetFormattedTraceback())
        return res

    def Deserialize(self, data_ : bytes):
        res = None
        if data_ is None:
            rlogif._LogOEC(True, -1010)
            return res

        try:
            res = _PyPickle.loads(data_)
        except ( _PyPickle.PickleError, BaseException) as xcp:
            _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_SerDes_TextID_006).format(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_SerDes_TextID_002), self)
            logif._LogSysException(_msg, xcp, logif._GetFormattedTraceback())
        return res

    def SerializeToFile(self, obj_, autoCloseFile_ =True):
        if obj_ is None:
            rlogif._LogOEC(True, -1011)
            return False

        dirPath = _FSUtil.GetDirPath(self.__filePath)
        _FSUtil.MkDir(dirPath)

        if not self.__IsFileOpen(True):
            if not self.__OpenFile(True):
                return False

        try:
            _PyPickle.dump(obj_, self.__fh, SerDes.__ppVersion.value)
        except BaseException as xcp:
            _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_SerDes_TextID_007).format(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_SerDes_TextID_002), self)
            logif._LogSysException(_msg, xcp, logif._GetFormattedTraceback())

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
        except BaseException as xcp:
            _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_SerDes_TextID_008).format(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_SerDes_TextID_002), self)
            logif._LogSysException(_msg, xcp, logif._GetFormattedTraceback())

        if autoCloseFile_ or res is None:
            self.CloseFile()
        return res

    def CloseFile(self):
        if self.__writeOpened or self.__readOpened:
            self.__fh.close()
            self.__fh = None
            self.__writeOpened = False
            self.__readOpened = False

    def _ToString(self, *args_, **kwargs_):
        if len(args_) > 1:
            rlogif._LogOEC(True, -1012)
            return _CommonDefines._STR_EMPTY

        if len(kwargs_) > 0:
            rlogif._LogOEC(True, -1013)
            return _CommonDefines._STR_EMPTY

        bPropsOnly = False

        for _ii in range(len(args_)):
            if 0 == _ii: bPropsOnly = args_[_ii]

        if self.__filePath is None:
            res = _FwTDbEngine.GetText(_EFwTextID.eSerDes_ToString_03).format(self.__binaryFormat)
        else:
            res = _FwTDbEngine.GetText(_EFwTextID.eSerDes_ToString_04).format(self.__binaryFormat, self.__filePath)

        if not bPropsOnly:
            res = _FwTDbEngine.GetText(_EFwTextID.eSerDes_ToString_02).format(res)
        return res

    def _CleanUp(self):
        self.CloseFile()
        self.__filePath = None

    def __OpenFile(self, writeMode_):
        if self.filePath is None:
            rlogif._LogOEC(True, -1014)
            return False

        if self.__IsFileOpen(not writeMode_):
            if self.__writeOpened:
                logif._LogImplError(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_SerDes_TextID_009).format(self))
            else:
                logif._LogImplError(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_SerDes_TextID_010).format(self))
            return False

        if self.__IsFileOpen(writeMode_):
            return True

        try:
            _mode  = _CommonDefines._CHAR_SIGN_FILE_MODE_WRITE if writeMode_ else _CommonDefines._CHAR_SIGN_FILE_MODE_READ
            _mode += _CommonDefines._CHAR_SIGN_FILE_MODE_BINARY if self.isBinaryFormat else _CommonDefines._STR_EMPTY
            _fh = open(self.filePath, _mode)
        except (FileNotFoundError, BaseException) as xcp:
            _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_SerDes_TextID_011).format(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_SerDes_TextID_002), self)
            logif._LogSysException(_msg, xcp, logif._GetFormattedTraceback())
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

