# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : flattendfe.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


import os
from datetime import datetime as _Datetime

from xcofdk._xcofw.fw.fwssys.fwcore.logging.logdefines   import _EErrorImpact
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logdefines   import _ELogType
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logdefines   import _LogUtil
from xcofdk._xcofw.fw.fwssys.fwcore.logging.xcoexception import _EXcoXcpType
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil     import _ETaskExecutionPhaseID


class _FlattendFatalError:

    __slots__ = [  '__eType'      ,  '__filePath'   ,  '__funcName'  , '__lineNo'
                , '__uniqueID'    ,  '__longMsg'    ,  '__shortMsg'  , '__tstamp'
                , '__taskName'    ,  '__taskID'     ,  '__euRNum'    , '__eTEPhase'
                , '__bFFE'        ,  '__errCode'    ,  '__eErrImp'   ,  '__header'
                , '__callstack'   ,  '__blabla'     ,  '__sysXcp'    ,  '__sysXcpTB'
                , '__eSysXcpType'
                ]

    def __init__( self, feClone_, bForeignFE_ =False):
        if (feClone_ is None) or not feClone_.isValid:
            self.__bFFE        = None
            self.__eType       = None
            self.__euRNum      = None
            self.__header      = None
            self.__lineNo      = None
            self.__tstamp      = None
            self.__taskID      = None
            self.__sysXcp      = None
            self.__errCode     = None
            self.__eErrImp     = None
            self.__longMsg     = None
            self.__shortMsg    = None
            self.__filePath    = None
            self.__funcName    = None
            self.__taskName    = None
            self.__uniqueID    = None
            self.__eTEPhase    = None
            self.__sysXcpTB    = None
            self.__callstack   = None
            self.__eSysXcpType = None
        else:
            self.__bFFE      = bForeignFE_
            self.__eType     = feClone_.eLogType
            self.__euRNum    = feClone_.euRNumber
            self.__header    = feClone_.header
            self.__lineNo    = feClone_.lineNo
            self.__tstamp    = feClone_.timestampToDatetime
            self.__taskID    = feClone_.taskID
            self.__errCode   = feClone_.errorCode
            self.__eErrImp   = feClone_.eErrorImpact
            self.__longMsg   = None if feClone_.longMessage is None else str(feClone_.longMessage)
            self.__shortMsg  = None if feClone_.shortMessage is None else str(feClone_.shortMessage)
            self.__filePath  = feClone_.filePath
            self.__funcName  = feClone_.functionName
            self.__taskName  = feClone_.taskName
            self.__uniqueID  = feClone_.uniqueID
            self.__eTEPhase  = feClone_.eTaskExecPhase
            self.__callstack = feClone_.callstack

            sysXcp = feClone_._causedBySystemException
            if sysXcp is not None:
                self.__sysXcp      = sysXcp._enclosedException
                self.__sysXcpTB    = sysXcp.traceback
                self.__eSysXcpType = sysXcp.eExceptionType
            else:
                self.__sysXcp      = None
                self.__sysXcpTB    = None
                self.__eSysXcpType = None

    @property
    def isValid(self) -> bool:
        return self.__eType is not None

    @property
    def isSystemFatalError(self):
        return self.isValid and (self.eLogType._absoluteValue >= _ELogType.FTL_SYS_OP_ERR.value)

    @property
    def isForeignFatalError(self):
        return self.__bFFE

    @property
    def uniqueID(self):
        return self.__uniqueID

    @property
    def eLogType(self) -> _ELogType:
        return self.__eType

    @property
    def eErrorImpact(self) -> _EErrorImpact:
        return self.__eErrImp

    @property
    def header(self):
        return self.__header

    @property
    def message(self):
        res = self.shortMessage
        if res is None:
            res = self.longMessage
        return res

    @property
    def shortMessage(self):
        return self.__shortMsg

    @property
    def longMessage(self):
        return self.__longMsg

    @property
    def taskName(self):
        return self.__taskName

    @property
    def taskID(self):
        return self.__taskID

    @property
    def lineNo(self):
        return self.__lineNo

    @property
    def fileName(self):
        res = self.filePath
        if res is not None:
            res = os.path.basename(os.path.realpath(res))
        return res

    @property
    def filePath(self):
        return self.__filePath

    @property
    def functionName(self):
        return self.__funcName

    @property
    def timestamp(self):
        return self.timestampMS

    @property
    def timestampMS(self):
        return _LogUtil.GetLogTimestamp(self.__tstamp, microsec_=False)

    @property
    def timestampUS(self):
        return _LogUtil.GetLogTimestamp(self.__tstamp, microsec_=True)

    @property
    def timestampToDatetime(self) -> _Datetime:
        return None if self.__tstamp is None else _Datetime.fromisoformat(self.__tstamp.isoformat())

    @property
    def errorCode(self) -> int:
        return self.__errCode

    @property
    def euRNumber(self) -> int:
        return self.__euRNum

    @property
    def eTaskExecPhase(self) -> _ETaskExecutionPhaseID:
        return _ETaskExecutionPhaseID.eNone if self.__eTEPhase is None else self.__eTEPhase

    @property
    def callstack(self):
        return None

    @property
    def causedByBaseException(self) -> BaseException:
        return self.__sysXcp

    @property
    def causedByBaseExceptionTraceback(self) -> str:
        return self.__sysXcpTB

    @property
    def eCausedByBaseExceptionType(self) -> _EXcoXcpType:
        return self.__eSysXcpType

    def ToString(self, *args_, **kwargs_):
        pass
