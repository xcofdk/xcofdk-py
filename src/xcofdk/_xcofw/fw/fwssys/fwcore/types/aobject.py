# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : aobject.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from xcofdk._xcofw.fw.fwssys.fwcore.logging import vlogif

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine


class _AbstractObject:

    _AO_PRINT_CTOR_MSG   = False
    _AO_INIT_MEMBEER_VAR = _FwTDbEngine.GetText(_EFwTextID.ePreDefinedMethod_CleanedUp)

    def __init__(self):
        if getattr(self, _AbstractObject._AO_INIT_MEMBEER_VAR, None) is not None:
            pass
        else:
            self._cleanedup = False

    def __str__(self):
        return _AOCommon.BuiltinStr(self)


    def __del__(self):
        _AOCommon.BuiltinDel(self)

    @staticmethod
    def Delete(anobject_, posFromOrKey_ =None, posTo_ =None):
        _AOCommon.Delete(anobject_, posFromOrKey_=posFromOrKey_, posTo_=posTo_)

    def ToString(self, *args_, **kwargs_) -> str:
        return _AOCommon.ToString(self, *args_, **kwargs_)

    def CleanUp(self):
        _AOCommon.CleanUp(self)

    def ResetCleanupFlag(self):
        _AOCommon.ResetCleanupFlag(self)



class _AbstractSlotsObject:

    __slots__ = [ _FwTDbEngine.GetText(_EFwTextID.ePreDefinedMethod_CleanedUp) ]

    def __init__(self):
        if getattr(self, _AbstractObject._AO_INIT_MEMBEER_VAR, None) is not None:
            pass
        else:
            self._cleanedup = False

    def __str__(self):
        return _AOCommon.BuiltinStr(self)


    def __del__(self):
        _AOCommon.BuiltinDel(self)

    @staticmethod
    def Delete(anobject_, posFromOrKey_=None, posTo_=None):
        _AOCommon.Delete(anobject_, posFromOrKey_=posFromOrKey_, posTo_=posTo_)

    def ToString(self, *args_, **kwargs_) -> str:
        return _AOCommon.ToString(self, *args_, **kwargs_)

    def CleanUp(self):
        _AOCommon.CleanUp(self)

    def ResetCleanupFlag(self):
        _AOCommon.ResetCleanupFlag(self)



class _AOCommon:
    _CLEANUP_METHOD_PROTECTED       = _FwTDbEngine.GetText(_EFwTextID.ePreDefinedMethod_CleanUpByOwnerRequest)
    _CLEANUP_METHOD_STD             = _FwTDbEngine.GetText(_EFwTextID.ePreDefinedMethod_CleanUp)
    __TOSTRING_METHOD_STD           = _FwTDbEngine.GetText(_EFwTextID.ePreDefinedMethod_ToString)
    __totalNumMissingManagedCleanup = 0

    @staticmethod
    def BuiltinStr(self_):
        return self_.ToString()


    @staticmethod
    def BuiltinDel(self_):

        if getattr(self_, _AbstractObject._AO_INIT_MEMBEER_VAR, None) is None:
            vlogif._LogOEC(True, -1026)
        elif not self_._cleanedup:
            _AOCommon.__totalNumMissingManagedCleanup += 1

    @staticmethod
    def Delete(anobject_, posFromOrKey_=None, posTo_=None):

        if anobject_ is None:
            pass
        elif posFromOrKey_ is not None:
            _AOCommon.__DeleteByPos(anobject_, posFromOrKey_, posTo_)
        elif isinstance(anobject_, list) and len(anobject_) > 0:
            for _ii in range(len(anobject_)):
                _ee = anobject_[_ii]
                anobject_[_ii] = None
                _AOCommon.Delete(_ee)
                _ee = None
            anobject_.clear()
            _AOCommon.Delete(anobject_)
        elif isinstance(anobject_, dict) and len(anobject_) > 0:
            keys = anobject_.keys()
            vals = anobject_.values()
            for _kk in keys:
                _AOCommon.Delete(_kk)
            keys.clear()
            for _vv in vals:
                _AOCommon.Delete(_vv)
            vals.clear()
            anobject_.clear()
            _AOCommon.Delete(anobject_)
        elif isinstance(anobject_, (_AbstractObject, _AbstractSlotsObject)):
            anobject_.CleanUp()

    @staticmethod
    def ResetCleanupFlag(self_):
        if getattr(self_, _AbstractObject._AO_INIT_MEMBEER_VAR, None) is not None:
            self_._cleanedup = False

    @staticmethod
    def ToString(self_, *args_, **kwargs_) -> str:
        if getattr(self_, _AOCommon.__TOSTRING_METHOD_STD, None) is None:
            vlogif._LogOEC(True, -1027)
            res = '(class, id, xid)=({}, {}, {}'.format(type(self_).__name__, id(self_), hex(id(self_)))
        else:
            res = self_._ToString(*args_, **kwargs_)
        return res

    @staticmethod
    def CleanUp(self_, cleanupMethodName_ =None):


        if getattr(self_, _AbstractObject._AO_INIT_MEMBEER_VAR, None) is None:
            vlogif._LogOEC(True, -1028)
        elif self_._cleanedup:
            pass
        else:
            self_._cleanedup = True

            mn = cleanupMethodName_
            if mn is None:
                mn = _AOCommon._CLEANUP_METHOD_STD
            if getattr(self_, mn, None) is None:
                pass
            else:
                if cleanupMethodName_ is not None:
                    if cleanupMethodName_ != _AOCommon._CLEANUP_METHOD_PROTECTED:
                        vlogif._LogOEC(True, -1029)
                    else:
                        self_._CleanUpByOwnerRequest()
                else:
                    self_._CleanUp()


    @staticmethod
    def __DeleteByPos(anobject_, posFromOrKey_, posTo_=None):
        _strTo = str(posTo_)
        _strFrom = str(posFromOrKey_)

        if not isinstance(anobject_, (list, dict)):
            vlogif._LogOEC(True, -1030)
            return
        elif posFromOrKey_ is None:
            vlogif._LogOEC(True, -1031)
            return
        elif len(anobject_)==0:
            vlogif._LogOEC(True, -1032)
            return
        elif isinstance(anobject_, dict):
            if posFromOrKey_ not in anobject_:
                vlogif._LogOEC(True, -1033)
                return
            elif posTo_ is not None:
                vlogif._LogOEC(True, -1034)
                return
        elif isinstance(anobject_, list):
            if not isinstance(posFromOrKey_, int):
                if posFromOrKey_!='':
                    vlogif._LogOEC(True, -1035)
                    return
                else:
                    posFromOrKey_ = len(anobject_) - 1
                if posFromOrKey_ < 0:
                    posFromOrKey_ = len(anobject_) - 1
                    if posFromOrKey_ < 0:
                        vlogif._LogOEC(True, -1036)
                        return
                if posFromOrKey_ >= len(anobject_):
                    vlogif._LogOEC(True, -1037)
                    return
            if posTo_ is not None:
                if not isinstance(posTo_, int):
                    if posTo_!='':
                        vlogif._LogOEC(True, -1038)
                        return
                    else:
                        posTo_ = len(anobject_) - 1
                elif posTo_ < 0:
                    posTo_ = len(anobject_) - 1
                    if posTo_ < 0:
                        vlogif._LogOEC(True, -1039)
                        return
                if posTo_ > len(anobject_):
                    vlogif._LogOEC(True, -1040)
                    return

        if isinstance(anobject_, dict):
            val = anobject_.pop(posFromOrKey_)
            _AOCommon.Delete(val)
        elif isinstance(anobject_, list):
            if posTo_ is None:
                posTo_ = posFromOrKey_ + 1
            elif posTo_ < posFromOrKey_:
                posFromOrKey_, posTo_ = posTo_, posFromOrKey_
            for _ii in range(posFromOrKey_, posTo_):
                val = anobject_.pop(_ii)
                _AOCommon.Delete(val)
