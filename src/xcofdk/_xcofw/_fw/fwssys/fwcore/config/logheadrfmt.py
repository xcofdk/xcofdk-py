# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwcustomconfig.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from _fw.fwssys.fwcore.types.apobject    import _ProtAbsSlotsObject
from _fw.fwssys.fwcore.types.commontypes import _CommonDefines

class _LogHeaderFormat(_ProtAbsSlotsObject):
    __slots__ = [ '__uid' , '__ts' , '__tn' , '__tid' , '__fcn' , '__fn' , '__no' , '__cs' , '__ri' , '__xrn' , '__ei' , '__xph' ]

    def __init__( self, ppass_ : int, bFW_ : bool, bRelMode_ : bool):
        super().__init__(ppass_)
        _bDbgMode  = not bRelMode_
        self.__cs  = True
        self.__ri  = True
        self.__tn  = True
        self.__ts  = True
        self.__tid = False
        self.__uid = _bDbgMode
        self.__ei  = bFW_ and _bDbgMode
        self.__fn  = bFW_ and _bDbgMode
        self.__no  = bFW_ and _bDbgMode
        self.__fcn = bFW_ and _bDbgMode
        self.__xph = bFW_ and _bDbgMode
        self.__xrn = bFW_ and _bDbgMode

    @staticmethod
    def CreateLogHeaderFormat(ppass_ : int, bFW_ : bool, bRelMode_ : bool):
        return _LogHeaderFormat.__CreateLogHeaderFormat(ppass_, bFW_, bRelMode_)

    @property
    def isUniqueIDEnabled(self):
        return self.__uid

    @property
    def isTimestampEnabled(self):
        return self.__ts

    @property
    def isTaskNameEnabled(self):
        return self.__tn

    @property
    def isTaskIDEnabled(self):
        return self.__tid

    @property
    def isFuncNameEnabled(self):
        return self.__fcn

    @property
    def isFileNameEnabled(self):
        return self.__fn

    @property
    def isLineNoEnabled(self):
        return self.__no

    @property
    def isCallstackEnabled(self):
        return self.__cs

    @property
    def isRaisedByInfoEnabled(self):
        return self.__ri

    @property
    def isExecUnitNumEnabled(self):
        return self.__xrn

    @property
    def isErrorImpactEnabled(self):
        return self.__ei

    @property
    def isTaskExecutionPhaseEnabled(self):
        return self.__xph

    @property
    def _isValid(self):
        return self.__uid  is not None

    def _Update( self, *, uniqueID_ : bool =None, timestamp_ : bool =None, taskName_ : bool =None
               , taskID_ : bool =None, funcName_ : bool =None, fileName_ : bool =None, lineNo_ : bool =None
               , callstack_ : bool =None, rbyinfo_ : bool =None, xrn_ : bool =None, errImp_ =None, xphaseID_ =None):
        if (rbyinfo_ is None) and (callstack_ is not None):
            rbyinfo_ = callstack_
        if xrn_       is not None: self.__xrn = xrn_
        if errImp_    is not None: self.__ei  = errImp_
        if taskID_    is not None: self.__tid = taskID_
        if lineNo_    is not None: self.__no  = lineNo_
        if rbyinfo_   is not None: self.__ri  = rbyinfo_
        if uniqueID_  is not None: self.__uid = uniqueID_
        if taskName_  is not None: self.__tn  = taskName_
        if funcName_  is not None: self.__fcn = funcName_
        if fileName_  is not None: self.__fn  = fileName_
        if callstack_ is not None: self.__cs  = callstack_
        if timestamp_ is not None: self.__ts  = timestamp_
        if xphaseID_  is not None: self.__xph = xphaseID_

    def _ToString(self):
        if self.__uid is None:
            return None
        return _CommonDefines._STR_EMPTY

    def _CleanUpByOwnerRequest(self):
        self.__cs  = None
        self.__ei  = None
        self.__fn  = None
        self.__no  = None
        self.__ri  = None
        self.__tn  = None
        self.__ts  = None
        self.__fcn = None
        self.__tid = None
        self.__uid = None
        self.__xph = None
        self.__xrn = None

    @staticmethod
    def __CreateLogHeaderFormat(ppass_, bFW_ : bool, bRelMode_ : bool):
        res = _LogHeaderFormat(ppass_, bFW_, bRelMode_ )
        if not res._isValid:
            res = None
        return res
