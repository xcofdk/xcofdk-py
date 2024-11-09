# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : aprofile.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from xcofdk._xcofw.fwadapter                          import rlogif
from xcofdk._xcofw.fw.fwssys.fwcore.base.util         import _Util
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject     import _AbstractSlotsObject
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes import _FwIntEnum
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes import unique

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine


class _AbstractProfile(_AbstractSlotsObject):

    @unique
    class _EProfileType(_FwIntEnum):
        eTimer  = 0
        eTask   = 1
        eThread = 2

    @unique
    class _EValidationStatus(_FwIntEnum):
        eNone    = 0
        eInvalid = 1
        eValid   = 2
        eFrozen  = 3

    class _ProfileAttributeHandler:
        __slots__ = [ '__handler' , '__attrName' , '__optAttrsNames' ]

        def __init__(self, attrName_, handler_, optionaAttrsNames_ =None):
            self.__handler       = handler_
            self.__attrName      = attrName_
            self.__optAttrsNames = optionaAttrsNames_

        @property
        def handler(self):
            return self.__handler

        @property
        def attrName(self):
            return self.__attrName

        @property
        def optAttrsNames(self):
            return self.__optAttrsNames


    __dictProfileHandlersList = {}
    __slots__ = [ '__ptype' , '__pstatus' , '__pAttrs' ]


    _ATTR_KEY_ARGS                         = _FwTDbEngine.GetText(_EFwTextID.eAbstractProfile_AttrName_ATTR_KEY_ARGS)
    _ATTR_KEY_AUTO_START_ENCLOSED_PYTHREAD = _FwTDbEngine.GetText(_EFwTextID.eAbstractProfile_AttrName_ATTR_KEY_AUTO_START_ENCLOSED_PYTHREAD)
    _ATTR_KEY_ENCLOSED_PYTHREAD            = _FwTDbEngine.GetText(_EFwTextID.eAbstractProfile_AttrName_ATTR_KEY_ENCLOSED_PYTHREAD)
    _ATTR_KEY_KWARGS                       = _FwTDbEngine.GetText(_EFwTextID.eAbstractProfile_AttrName_ATTR_KEY_KWARGS)
    _ATTR_KEY_TASK_NAME                    = _FwTDbEngine.GetText(_EFwTextID.eAbstractProfile_AttrName_ATTR_KEY_TASK_NAME)
    _ATTR_KEY_TASK_RIGHTS                  = _FwTDbEngine.GetText(_EFwTextID.eAbstractProfile_AttrName_ATTR_KEY_TASK_RIGHTS)
    _ATTR_KEY_TASK_ID                      = _FwTDbEngine.GetText(_EFwTextID.eAbstractProfile_AttrName_ATTR_KEY_TASK_ID)


    def __init__(self, ptype_ : _FwIntEnum, profileAttrs_ : dict =None):
        super().__init__()

        self.__ptype   = None
        self.__pAttrs  = {}
        self.__pstatus = _AbstractProfile._EValidationStatus.eNone

        if not isinstance(ptype_, _AbstractProfile._EProfileType):
            rlogif._LogOEC(True, -1018)
        else:
            self.__ptype = ptype_
            self._Validate(profileAttrs_)

    @property
    def isValid(self):
        return (self.__pstatus is not None) and (self.__pstatus.value >= _AbstractProfile._EValidationStatus.eValid.value)

    @property
    def isFrozen(self):
        return (self.__pstatus is not None) and (self.__pstatus == _AbstractProfile._EValidationStatus.eFrozen)

    @property
    def isTimerProfile(self):
        return (self.__ptype is not None) and self.__ptype == _AbstractProfile._EProfileType.eTimer

    @property
    def isTaskProfile(self):
        return (self.__ptype is not None) and self.__ptype == _AbstractProfile._EProfileType.eTask

    @property
    def isThreadProfile(self):
        return (self.__ptype is not None) and self.__ptype == _AbstractProfile._EProfileType.eThread

    @property
    def isDrivingXTaskTaskProfile(self):
        return self._isDrivingXTaskTaskProfile

    @property
    def profileStatus(self):
        return self.__pstatus

    @profileStatus.setter
    def profileStatus(self, val_):
        self.__pstatus = val_

    @property
    def profileAttributes(self):
        return self.__pAttrs

    @profileAttributes.setter
    def profileAttributes(self, val_):
        self.__pAttrs = val_

    def Freeze(self, *args_, **kwargs_):
        if not self.isValid:
            rlogif._LogOEC(True, -1019)
            return False
        if not self.isFrozen:
            self.__pstatus = _AbstractProfile._EValidationStatus.eFrozen
        return True

    @staticmethod
    def _SetProfileHandlersList(className_, profileHandlersList_ : list):
        if not _Util.IsInstance(profileHandlersList_, list, bThrowx_=True):
            return False

        _phlist =  _AbstractProfile.__GetProfileHandlersList(className_)
        if _phlist is not None:
            rlogif._LogOEC(True, -1020)
            return False

        _AbstractProfile.__dictProfileHandlersList[className_] = profileHandlersList_
        return True

    @staticmethod
    def _CheckMutuallyExclusiveAttrs(dictAttrs_ : dict, mutuallyExclusiveAttrs_ : list):
        if len(dictAttrs_) == 0 or len(mutuallyExclusiveAttrs_) == 0:
            res = True
        else:
            _numMEA = 0
            for _ee in mutuallyExclusiveAttrs_:
                if _ee in dictAttrs_:
                    _numMEA += 1
            res = _numMEA < 2
        if not res:
            rlogif._LogOEC(True, -1021)
        return res

    @property
    def _isDrivingXTaskTaskProfile(self):
        return False

    def _ToString(self, *args_, **kwargs_):
        return '{}: (valid)=({})'.format(_Util.TypeName(self), self.isValid)

    def _CleanUp(self):
        if self.__pAttrs is None:
            pass
        else:
            self.__pAttrs.clear()

            self.__pstatus     = None
            self.__ptype       = None
            self.__pAttrs = None

    def _GetProfileHandlersList(self):
        return _AbstractProfile.__GetProfileHandlersList(self.__class__.__name__)

    def _GetProfileAttr(self, attrName_, ignoreStatus_ =False):
        res = None
        if self.isValid or ignoreStatus_:
            if attrName_ in self.__pAttrs:
                res = self.__pAttrs[attrName_]
        return res

    def _Validate(self, dictAttrs_ : dict):
        if self._GetProfileHandlersList() is None:
            self.__pstatus = _AbstractProfile._EValidationStatus.eInvalid
            rlogif._LogOEC(True, -1022)
            return
        elif self.__pstatus != _AbstractProfile._EValidationStatus.eNone:
            self.__pstatus = _AbstractProfile._EValidationStatus.eInvalid
            rlogif._LogOEC(True, -1023)
            return
        elif (dictAttrs_ is None) or (len(dictAttrs_) == 0):
            return

        for pah in self._GetProfileHandlersList():
            if pah.attrName not in dictAttrs_:
                continue

            _arg = dictAttrs_[pah.attrName]
            _hh = pah.handler

            _optArgs = None
            if pah.optAttrsNames is not None:
                _optArgs = list()
                for _kk in pah.optAttrsNames:
                    if _kk not in dictAttrs_:
                        _vv = None
                    else:
                        _vv = dictAttrs_[_kk]
                    _optArgs.append(_vv)
                if len(_optArgs) == 0:
                    _optArgs = None

            if _optArgs is not None:
                _hh(self, _arg, *_optArgs)
            else:
                _hh(self, _arg)

    @staticmethod
    def __GetProfileHandlersList(className_):
        res = None
        if className_ in _AbstractProfile.__dictProfileHandlersList:
            res = _AbstractProfile.__dictProfileHandlersList[className_]
        return res
