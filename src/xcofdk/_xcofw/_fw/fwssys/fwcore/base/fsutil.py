# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fsutil.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

import os
from   datetime import datetime as _PyDateTime

from _fw.fwssys.fwcore.logging      import logif
from _fw.fwssys.fwcore.base.util    import _Util
from _fw.fwssys.fwerrh.fwerrorcodes import _EFwErrorCode

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _FSUtil:
    __slots__ = []

    @staticmethod
    def GetOsSeparator():
        return os.sep

    @staticmethod
    def IsExistingFile(filePath_, bThrowx_ =True):
        if not _Util.IsInstance(filePath_, str, bThrowx_=bThrowx_):
            return False
        return os.path.isfile(filePath_)

    @staticmethod
    def IsExistingDir(dirPath_, bThrowx_ =True):
        if not _Util.IsInstance(dirPath_, str, bThrowx_=bThrowx_):
            return False
        return os.path.isdir(dirPath_)

    @staticmethod
    def IsExistingOSPath(osPath_, bThrowx_ =True):
        if not _Util.IsInstance(osPath_, str, bThrowx_=bThrowx_):
            return False
        return os.path.exists(osPath_)

    @staticmethod
    def IsAbsolutePath(somePath_, bThrowx_ =True):
        if not _Util.IsInstance(somePath_, str, bThrowx_=bThrowx_):
            return False
        return os.path.isabs(somePath_)

    @staticmethod
    def IsRelativePath(somePath_, bThrowx_ =True):
        if not _Util.IsInstance(somePath_, str, bThrowx_=bThrowx_):
            return False
        return not _FSUtil.IsAbsolutePath(somePath_)

    @staticmethod
    def GetCWD():
        return os.getcwd()

    @staticmethod
    def GetBasename(somePath_, bThrowx_ =True):
        if not _Util.IsInstance(somePath_, str, bThrowx_=bThrowx_):
            return False
        return os.path.basename(somePath_)

    @staticmethod
    def GetFileBasename(filePath_, bThrowx_ =True):
        if not _Util.IsInstance(filePath_, str, bThrowx_=bThrowx_):
            return False
        _lst = os.path.splitext(filePath_)
        return None if len(_lst)<1 else  _FSUtil.GetBasename(_lst[0])

    @staticmethod
    def GetDirPath(somePath_, bThrowx_ =True):
        if not _Util.IsInstance(somePath_, str, bThrowx_=bThrowx_):
            return False
        return os.path.dirname(somePath_)

    @staticmethod
    def GetAbsPath(somePath_, bThrowx_ =True):
        if not _Util.IsInstance(somePath_, str, bThrowx_=bThrowx_):
            return False
        return os.path.abspath(somePath_)

    @staticmethod
    def GetNormalizedPath(somePath_, bThrowx_ =True):
        if not _Util.IsInstance(somePath_, str, bThrowx_=bThrowx_):
            return False
        return os.path.normpath(somePath_)

    @staticmethod
    def GetFileExtension(filePath_, bThrowx_ =True):
        if not _Util.IsInstance(filePath_, str, bThrowx_=bThrowx_):
            return False
        _lst = os.path.splitext(filePath_)
        return None if len(_lst)<1 else _lst[1].strip(".")

    @staticmethod
    def MkDir(dirPath_, ignoreExists_ =True, bThrowx_ =True):
        if not _Util.IsInstance(dirPath_, str, bThrowx_=bThrowx_):
            return False
    
        if os.path.isdir(dirPath_):
            if not ignoreExists_:
                if bThrowx_:
                    logif._LogBadUseEC(_EFwErrorCode.FE_00078, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FSUtil_TID_001).format(dirPath_))
                return False
            else:
                return True
        try:
            os.makedirs(dirPath_)
        except Exception as _xcp:
            if bThrowx_:
                myMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FSUtil_TID_002).format(dirPath_, str(_xcp))
                logif._LogSysExceptionEC(_EFwErrorCode.FE_00011, myMsg, _xcp, logif._GetFormattedTraceback())
            return False
        return True

    @staticmethod
    def GetUniqueFileNameTS() -> str:
        res = _PyDateTime.now().isoformat(timespec='milliseconds')
        res =  res[res.index('T')+1:]
        res = res.replace(':', '_').replace('.', '_')
        return res

    @staticmethod
    def GetLogFilePath(filePath_ : str =None):
        if filePath_ is None:
            res = os.getcwd()
        else:
            res = os.path.normpath(filePath_)
            if not os.path.isabs(res):
                res = os.path.join(os.getcwd(), res)
        if os.path.isdir(res):
            res = os.path.join(res, f'xcofdk_log__{_FSUtil.GetUniqueFileNameTS()}.txt')
            res = os.path.normpath(res)
        return res
