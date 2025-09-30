# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : apobject.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from _fw.fwssys.fwcore.logging       import vlogif
from _fw.fwssys.fwcore.types.aobject import _AbsObject
from _fw.fwssys.fwcore.types.aobject import _AbsSlotsObject
from _fw.fwssys.fwcore.types.aobject import _AOCommon
from _fw.fwssys.fwerrh.fwerrorcodes  import _EFwErrorCode

class _ProtAbsObject(_AbsObject):
    def __init__(self, ppass_ : int):
        if getattr(self, _AbsObject._AO_INIT_MEMBEER_VAR, None) is not None:
            pass
        else:
            self.__p   = None
            self.__bBC = None
            super().__init__()
            if not isinstance(ppass_, int):
                _AbsObject.CleanUp(self)
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00485)
            else:
                self.__p   = ppass_
                self.__bBC = True

    def CleanUp(self):
        if self.__bBC:
            pass
        elif getattr(self, _AOCommon._CLEANUP_METHOD_STD, None) is None:
            pass
        else:
            _AOCommon.CleanUp(self_=self)

    def CleanUpByOwnerRequest(self, ppass_ : int):
        if self.__p is None:
            pass
        elif ppass_ != self.__p:
            pass
        else:
            _AOCommon.CleanUp(self_=self, cleanupMethodName_=_AOCommon._CLEANUP_METHOD_PROTECTED)
            self.__p   = None
            self.__bBC = None

    @property
    def _myPPass(self):
        return self.__p

class _ProtAbsSlotsObject(_AbsSlotsObject):
    __slots__ = [ '__p' , '__bBC' ]

    def __init__(self, ppass_ : int):
        if getattr(self, _AbsObject._AO_INIT_MEMBEER_VAR, None) is not None:
            pass
        else:
            self.__p   = None
            self.__bBC = None
            super().__init__()
            if not isinstance(ppass_, int):
                _AbsSlotsObject.CleanUp(self)
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00486)
            else:
                self.__p   = ppass_
                self.__bBC = True

    def CleanUp(self):
        if self.__bBC:
            pass
        elif getattr(self, _AOCommon._CLEANUP_METHOD_STD, None) is None:
            pass
        else:
            _AOCommon.CleanUp(self_=self)

    def CleanUpByOwnerRequest(self, ppass_ : int):
        if self.__p is None:
            pass
        elif ppass_ != self.__p:
            pass
        else:
            _AOCommon.CleanUp(self_=self, cleanupMethodName_=_AOCommon._CLEANUP_METHOD_PROTECTED)
            self.__p   = None
            self.__bBC = None

    @property
    def _myPPass(self):
        return self.__p
