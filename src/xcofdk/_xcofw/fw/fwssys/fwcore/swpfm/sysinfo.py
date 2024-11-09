# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : sysinfo.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


import  re
import  platform
import  sys
import  sysconfig
from   typing import Tuple as _PyTuple

from multiprocessing import cpu_count as _PyCpuCount


class _SystemInfo:

    __slots__ = []

    def __init__(self):
        pass

    @staticmethod
    def _IsBigEndian():
        return sys.byteorder == 'big'

    @staticmethod
    def _IsLittleEndian():
        return sys.byteorder == 'little'

    @staticmethod
    def _IsPlatformLinux():
        return _SystemInfo.__IsPlatform('Linux')

    @staticmethod
    def _IsPlatformMacOS():
        return _SystemInfo.__IsPlatform('Darwin')

    @staticmethod
    def _IsPlatformWindows():
        return _SystemInfo.__IsPlatform('Windows')

    @staticmethod
    def _IsPythonVersion(verMajor_ : int, verMinor_ : int =None) -> bool:
        if not isinstance(verMajor_, int):
            return False
        if (verMinor_ is not None) and not isinstance(verMinor_, int):
            return False
        return _SystemInfo._IsPythonVersionCompatible(verMajor_, verMinor_=verMinor_, bExactMatch_=True)

    @staticmethod
    def _IsPythonVersionCompatible(verMajor_ : int, verMinor_ : int =None, bExactMatch_ =False) -> bool:
        if not isinstance(verMajor_, int):
            return False
        if (verMinor_ is not None) and not isinstance(verMinor_, int):
            return False

        _major = sys.version_info.major
        _minor = sys.version_info.minor
        res = _major==verMajor_ if bExactMatch_ else _major>=verMajor_
        if res and (verMinor_ is not None):
            res = _minor==verMinor_ if bExactMatch_ else _minor>=verMinor_
        return res

    @staticmethod
    def _IsFrameworkSupportingPythonVersion():
        return _SystemInfo._IsPythonVersionCompatible(3, 8)

    @staticmethod
    def _IsPythonVersionSupportingGilDisabled():
        return _SystemInfo._IsPythonVersionCompatible(3, 13)

    @staticmethod
    def _IsPythonConfiguredWithGilDisabled():
        res = False
        if _SystemInfo._IsPythonVersionSupportingGilDisabled():
            res = sysconfig.get_config_var('Py_GIL_DISABLED')
            if isinstance(res, int):
                res = False if res==0 else True
        return res

    @staticmethod
    def _IsGilEnabled():
        res = True
        if _SystemInfo._IsPythonVersionSupportingGilDisabled():
            res = sys._is_gil_enabled()
        return res

    @staticmethod
    def _IsGilDisabled():
        res = False
        if _SystemInfo._IsPythonVersionSupportingGilDisabled():
            res = not sys._is_gil_enabled()
        return res

    @staticmethod
    def _GetPythonVer() -> str:
        return platform.python_version()

    @staticmethod
    def _GetPythonVerInfo() -> _PyTuple[str, int, int]:
        return platform.python_version(), sys.version_info.major, sys.version_info.minor

    @staticmethod
    def _GetPlatform() -> str:
        return platform.system()

    @staticmethod
    def _GetCpuCoresCount() -> int:
        try:
            res = _PyCpuCount()
        except NotImplementedError as _xcp:
            res = 0
        return res


    @staticmethod
    def __IsPlatform(platformName_):
        _ncre = r'^{}$'.format(platformName_)
        _cre  = re.compile(_ncre, re.RegexFlag.IGNORECASE)
        return _cre.match(platform.system()) is not None
