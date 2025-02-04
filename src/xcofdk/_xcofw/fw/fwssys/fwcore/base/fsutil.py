# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fsutil.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

import os

from xcofdk._xcofw.fw.fwssys.fwcore.logging      import logif
from xcofdk._xcofw.fw.fwssys.fwcore.base.util    import _Util
from xcofdk._xcofw.fw.fwssys.fwerrh.fwerrorcodes import _EFwErrorCode

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine

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
        li = os.path.splitext(filePath_)
        if len(li) > 0:
            return _FSUtil.GetBasename(li[0])
        else:
            return None

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
        li = os.path.splitext(filePath_)
        if len(li) > 1:
            return li[1].strip(".")
        else:
            return None

    @staticmethod
    def MkDir(dirPath_, ignoreExists_ =True, bThrowx_ =True):
        if not _Util.IsInstance(dirPath_, str, bThrowx_=bThrowx_):
            return False
    
        if os.path.isdir(dirPath_):
            if not ignoreExists_:
                if bThrowx_:
                    logif._LogBadUseEC(_EFwErrorCode.FE_00078, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FSUtil_TextID_001).format(dirPath_))
                return False
            else:
                return True
        try:
            os.makedirs(dirPath_)
        except BaseException as xcp:
            if bThrowx_:
                myMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FSUtil_TextID_002).format(dirPath_, str(xcp))
                logif._LogSysExceptionEC(_EFwErrorCode.FE_00011, myMsg, xcp, logif._GetFormattedTraceback())
            return False
        return True
