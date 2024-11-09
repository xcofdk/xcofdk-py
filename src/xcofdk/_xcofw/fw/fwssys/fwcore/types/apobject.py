# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : apobject.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------



from xcofdk._xcofw.fw.fwssys.fwcore.logging       import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject import _AbstractObject
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject import _AbstractSlotsObject
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject import _AOCommon


class _ProtectedAbstractObject(_AbstractObject):

    def __init__(self, ppass_ : int, banCleanup_ =True):
        if getattr(self, _AbstractObject._AO_INIT_MEMBEER_VAR, None) is not None:
            pass
        else:
            self.__ppass      = None
            self.__banCleanup = None
            super().__init__()
            if not isinstance(ppass_, int):
                _AbstractObject.CleanUp(self)
                vlogif._LogOEC(True, -1024)
            else:
                self.__ppass      = ppass_
                self.__banCleanup = banCleanup_

    def CleanUp(self):
        if self._isCleanupBanned:
            pass
        elif getattr(self, _AOCommon._CLEANUP_METHOD_STD, None) is None:
            pass
        else:
            _AOCommon.CleanUp(self_=self)

    def CleanUpByOwnerRequest(self, ppass_ : int):
        if self.__ppass is None:
            pass
        elif ppass_ != self.__ppass:
            pass
        else:
            _AOCommon.CleanUp(self_=self, cleanupMethodName_=_AOCommon._CLEANUP_METHOD_PROTECTED)
            self.__ppass      = None
            self.__banCleanup = None

    @property
    def _isCleanupBanned(self):
        return self.__banCleanup

    @property
    def _myPPass(self):
        return self.__ppass


class _ProtectedAbstractSlotsObject(_AbstractSlotsObject):

    __slots__ = [ '__ppass' , '__banCleanup' ]

    def __init__(self, ppass_ : int, banCleanup_ =True):
        if getattr(self, _AbstractObject._AO_INIT_MEMBEER_VAR, None) is not None:
            pass
        else:
            self.__ppass      = None
            self.__banCleanup = None
            super().__init__()
            if not isinstance(ppass_, int):
                _AbstractSlotsObject.CleanUp(self)
                vlogif._LogOEC(True, -1025)
            else:
                self.__ppass      = ppass_
                self.__banCleanup = banCleanup_

    def CleanUp(self):
        if self._isCleanupBanned:
            pass
        elif getattr(self, _AOCommon._CLEANUP_METHOD_STD, None) is None:
            pass
        else:
            _AOCommon.CleanUp(self_=self)

    def CleanUpByOwnerRequest(self, ppass_ : int):
        if self.__ppass is None:
            pass
        elif ppass_ != self.__ppass:
            pass
        else:
            _AOCommon.CleanUp(self_=self, cleanupMethodName_=_AOCommon._CLEANUP_METHOD_PROTECTED)
            self.__ppass      = None
            self.__banCleanup = None

    @property
    def _isCleanupBanned(self):
        return self.__banCleanup

    @property
    def _myPPass(self):
        return self.__ppass
