# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwcustomconfig.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from xcofdk._xcofw.fw.fwssys.fwcore.types.apobject import _ProtectedAbstractSlotsObject


class _LogHeaderFormat(_ProtectedAbstractSlotsObject):
    __slots__ = [ '__uniqueID' , '__timestamp' , '__taskName'  , '__taskID'  , '__funcName'
                , '__fileName' , '__lineNo'    , '__callstack' , '__rbyinfo' , '__euNum'
                , '__errImp'   , '__execPhase'
                ]

    def __init__( self, ppass_ : int, bFW_ : bool, bDbg_ : bool):
        super().__init__(ppass_)
        self.__euNum     = bFW_ and bDbg_
        self.__errImp    = bFW_ and bDbg_
        self.__taskID    = False
        self.__lineNo    = bFW_ and bDbg_
        self.__rbyinfo   = True
        self.__uniqueID  = bFW_ and bDbg_
        self.__taskName  = True
        self.__funcName  = bFW_ and bDbg_
        self.__fileName  = bFW_ and bDbg_
        self.__callstack = bFW_ and bDbg_
        self.__timestamp = True
        self.__execPhase = bFW_ and bDbg_

    @staticmethod
    def CreateFwLogHeaderFormat(ppass_ : int, bFW_ : bool, bRelMode_ : bool):
        return _LogHeaderFormat.__CreateFwLogHeaderFormat(ppass_, bFW_, bRelMode_)

    @property
    def isUniqueIDEnabled(self):
        return self.__uniqueID

    @property
    def isTimestampEnabled(self):
        return self.__timestamp

    @property
    def isTaskNameEnabled(self):
        return self.__taskName

    @property
    def isTaskIDEnabled(self):
        return self.__taskID

    @property
    def isFuncNameEnabled(self):
        return self.__funcName

    @property
    def isFileNameEnabled(self):
        return self.__fileName

    @property
    def isLineNoEnabled(self):
        return self.__lineNo

    @property
    def isCallstackEnabled(self):
        return self.__callstack

    @property
    def isRaisedByInfoEnabled(self):
        return self.__rbyinfo

    @property
    def isExecUnitNumEnabled(self):
        return self.__euNum

    @property
    def isErrorImpactEnabled(self):
        return self.__errImp

    @property
    def isTaskExecutionPhaseEnabled(self):
        return self.__execPhase

    @property
    def _isValid(self):
        return self.__uniqueID  is not None

    def _Update( self, *, uniqueID_ : bool =None, timestamp_ : bool =None, taskName_ : bool =None, taskID_ : bool =None, funcName_ : bool =None
                 , fileName_ : bool =None, lineNo_ : bool =None, callstack_ : bool =None, rbyinfo_ : bool =None, euNum_ : bool =None
                 , errImp_ =None, execPhase_ =None):
        if euNum_     is not None: self.__euNum     = euNum_
        if errImp_    is not None: self.__errImp    = errImp_
        if taskID_    is not None: self.__taskID    = taskID_
        if lineNo_    is not None: self.__lineNo    = lineNo_
        if rbyinfo_   is not None: self.__rbyinfo   = rbyinfo_
        if uniqueID_  is not None: self.__uniqueID  = uniqueID_
        if taskName_  is not None: self.__taskName  = taskName_
        if funcName_  is not None: self.__funcName  = funcName_
        if fileName_  is not None: self.__fileName  = fileName_
        if callstack_ is not None: self.__callstack = callstack_
        if timestamp_ is not None: self.__timestamp = timestamp_
        if execPhase_ is not None: self.__execPhase = execPhase_

    def _ToString(self, *args_, **kwargs_):
        if self.__uniqueID is None:
            res = None
        else:
            res = '{}:\n'.format(type(self).__name__)
            res += '  {:<27s} : {:<s}\n'.format('isUniqueIDEnabled'         , str(self.isUniqueIDEnabled))
            res += '  {:<27s} : {:<s}\n'.format('isTimestampEnabled'        , str(self.isTimestampEnabled))
            res += '  {:<27s} : {:<s}\n'.format('isTaskNameEnabled'         , str(self.isTaskNameEnabled))
            res += '  {:<27s} : {:<s}\n'.format('isTaskIDEnabled'           , str(self.isTaskIDEnabled))
            res += '  {:<27s} : {:<s}\n'.format('isFuncNameEnabled'         , str(self.isFuncNameEnabled))
            res += '  {:<27s} : {:<s}\n'.format('isFileNameEnabled'         , str(self.isFileNameEnabled))
            res += '  {:<27s} : {:<s}\n'.format('isLineNoEnabled'           , str(self.isLineNoEnabled))
            res += '  {:<27s} : {:<s}\n'.format('isCallstackEnabled'        , str(self.isCallstackEnabled))
            res += '  {:<27s} : {:<s}\n'.format('isRaisedByInfoEnabled'     , str(self.isRaisedByInfoEnabled))
            res += '  {:<27s} : {:<s}\n'.format('isExecUnitNumEnabled'      , str(self.isExecUnitNumEnabled))
            res += '  {:<27s} : {:<s}\n'.format('isErrorImpactEnabled'      , str(self.isErrorImpactEnabled))
            res += '  {:<27s} : {:<s}'.format('isTaskExecutionPhaseEnabled' , str(self.isTaskExecutionPhaseEnabled))
        return res

    def _CleanUpByOwnerRequest(self):
        self.__euNum     = None
        self.__errImp    = None
        self.__taskID    = None
        self.__lineNo    = None
        self.__rbyinfo   = None
        self.__uniqueID  = None
        self.__taskName  = None
        self.__funcName  = None
        self.__fileName  = None
        self.__callstack = None
        self.__timestamp = None
        self.__execPhase = None

    @staticmethod
    def __CreateFwLogHeaderFormat(ppass_, bFW_ : bool, bRelMode_ : bool):
        res = _LogHeaderFormat(ppass_, bFW_, not bRelMode_ )
        if not res._isValid:
            res = None
        return res
