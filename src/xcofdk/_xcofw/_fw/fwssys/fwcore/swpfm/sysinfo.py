# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : sysinfo.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

import re
import platform
import sys
import sysconfig
from   typing          import Tuple
from   multiprocessing import cpu_count as _PyCpuCount

try:
    from sys import _is_gil_enabled
    def _PyIsGilEnabled(): return _is_gil_enabled()
except (ImportError, Exception):
    def _PyIsGilEnabled(): return True

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
    def _IsGilDisabled():
        return False if not _SystemInfo._IsPyVersionSupportedFTPython() else not _PyIsGilEnabled()

    @staticmethod
    def _IsPyVersionSupported():
        return _SystemInfo._IsPythonVersionCompatible(3, 8)

    @staticmethod
    def _IsPyVersionSupportedFTPython():
        return _SystemInfo._IsPythonVersionCompatible(3, 13)

    @staticmethod
    def _IsPyVersionSupportedExperimentalFTPython() -> bool:
        return _SystemInfo._IsPyVersionSupportedFTPython() and not _SystemInfo._IsPyVersionSupportedOfficialFTPython()

    @staticmethod
    def _IsPyVersionSupportedOfficialFTPython() -> bool:
        _vinfo = sys.version_info
        if not _SystemInfo._IsPyVersionSupportedFTPython():
            return False
        if _vinfo.minor < 14:
            return False
        if (_vinfo.micro==0) and (_vinfo.releaselevel!='final'):
            return False
        return True

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
    def _GetPythonVer() -> str:
        return platform.python_version()

    @staticmethod
    def _GetPythonVerInfo() -> Tuple[str, int, int]:
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
