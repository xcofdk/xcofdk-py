# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : logentry.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


import inspect
import os
import sys
from   datetime import datetime as _Datetime

from xcofdk._xcofw.fw.fwssys.fwcore.logging            import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logdefines import _GetCurThread
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logdefines import _ELogType
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logdefines import _LogUtil
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil   import _ETaskExecutionPhaseID
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject      import _AbstractSlotsObject
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes  import _CommonDefines
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes  import _EColorCode
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes  import _TextStyle

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine


class _LogEntry(_AbstractSlotsObject):

    __slots__ = [  '__eType'    , '__filePath' , '__bFlushed' , '__funcName'
                , '__lineNo'   , '__uniqueID' , '__longMsg' , '__shortMsg'
                , '__tstamp'   , '__taskName' , '__taskID'  , '__euRNum'
                , '__eTEPhase' ]

    __bLogHighlightingEnabled  = True
    __bCompactOutputFormatMode = False

    __fmttagInclUniqueID     = True
    __fmttagInclTimestamp    = True
    __fmttagInclTaskName     = True
    __fmttagInclTaskID       = True
    __fmttagInclEuNum        = True
    __fmttagInclFuncName     = True
    __fmttagInclFileName     = True
    __fmttagInclLineNo       = True
    __fmttagInclCallstack    = True
    __fmttagInclRaisedByInfo = True
    __fmttagInclErrorImpact  = True
    __fmttagInclTExecPhase   = True

    __ufmttagInclUniqueID     = False
    __ufmttagInclTimestamp    = True
    __ufmttagInclTaskName     = True
    __ufmttagInclTaskID       = True
    __ufmttagInclEuNum        = False
    __ufmttagInclFuncName     = False
    __ufmttagInclFileName     = True
    __ufmttagInclLineNo       = True
    __ufmttagInclCallstack    = True
    __ufmttagInclRaisedByInfo = True
    __ufmttagInclErrorImpact  = False
    __ufmttagInclTExecPhase   = False

    def __init__( self, eLogType_, taskName_ : str =None, taskID_ =None
                , shortMsg_ : str =None, longMsg_ : str =None, inheritanceDepth_ =0
                , callstackLevelOffset_ =None, cloneby_ =None, doSkipSetup_ =False
                , euRNum_ =None, bXTaskTask_ =None):
        super().__init__()

        self.__eType    = None
        self.__euRNum   = None
        self.__lineNo   = None
        self.__tstamp   = None
        self.__taskID   = None
        self.__longMsg  = None
        self.__bFlushed = None
        self.__shortMsg = None
        self.__filePath = None
        self.__funcName = None
        self.__taskName = None
        self.__uniqueID = None
        self.__eTEPhase = None

        if doSkipSetup_:
            pass
        elif cloneby_ is not None:
            if not isinstance(cloneby_, _LogEntry):
                self.CleanUp()
                vlogif._LogOEC(True, -1045)
            elif not cloneby_.isValid:
                pass
            else:
                self.__eType    = cloneby_.__eType
                self.__euRNum   = cloneby_.__euRNum
                self.__lineNo   = cloneby_.__lineNo
                self.__tstamp   = cloneby_.__tstamp
                self.__taskID   = cloneby_.__taskID
                self.__longMsg  = cloneby_.__longMsg
                self.__bFlushed = cloneby_.__bFlushed
                self.__shortMsg = cloneby_.__shortMsg
                self.__filePath = cloneby_.__filePath
                self.__funcName = cloneby_.__funcName
                self.__taskName = cloneby_.__taskName
                self.__uniqueID = cloneby_.__uniqueID
                self.__eTEPhase = cloneby_.__eTEPhase
        else:
            self.__SetupEntry(eLogType_, taskName_=taskName_, taskID_=taskID_, shortMsg_=shortMsg_, longMsg_=longMsg_
                , inheritanceDepth_=inheritanceDepth_, callstackLevelOffset_=callstackLevelOffset_, euRNum_=euRNum_, bXTaskTask_=bXTaskTask_)

    def __eq__(self, other_):
        res = isinstance(other_, _LogEntry)
        if not res:
            pass
        elif id(self) == id(other_):
            pass
        elif not self.uniqueID is None and self.uniqueID == other_.uniqueID:
            pass
        else:
            res  = self.__eType    == other_.__eType
            res &= self.__euRNum   == other_.__euRNum
            res &= self.__lineNo   == other_.__lineNo
            res &= self.__tstamp   == other_.__tstamp
            res &= self.__taskID   == other_.__taskID
            res &= self.__longMsg  == other_.__longMsg
            res &= self.__shortMsg == other_.__shortMsg
            res &= self.__filePath == other_.__filePath
            res &= self.__funcName == other_.__funcName
            res &= self.__taskName == other_.__taskName
            res &= self.__uniqueID == other_.__uniqueID
            res &= self.__eTEPhase == other_.__eTEPhase
        return res

    @property
    def isValid(self) -> bool:
        return self.__eType is not None

    @property
    def isInvalid(self) -> bool:
        return self.__eType is None

    @property
    def isFwApiLog(self):
        return False if self.__eType is None else self.__eType.isFwApiLogType

    @property
    def isError(self):
        eGrpID = self.eTypeGroupID
        return False if eGrpID is None else eGrpID.isError


    @property
    def isUserError(self):
        return self.eTypeGroupID == _ELogType.ERR

    @property
    def isFatalError(self):
        return self.eTypeGroupID == _ELogType.FTL

    @property
    def isSystemFatalError(self):
        return self.isValid and (self.eLogType._absoluteValue >= _ELogType.FTL_SYS_OP_ERR.value)

    @property
    def isKPI(self):
        return self.eTypeGroupID == _ELogType.KPI

    @property
    def isWarning(self):
        return self.eTypeGroupID == _ELogType.WNG

    @property
    def isInfo(self):
        return self.eTypeGroupID == _ELogType.INF

    @property
    def isDebug(self):
        return self.eTypeGroupID == _ELogType.DBG

    @property
    def isTrace(self):
        return self.eTypeGroupID == _ELogType.TRC

    @property
    def isFreeLog(self):
        return self.eTypeGroupID == _ELogType.FREE

    @property
    def isFlushed(self):
        return self.__bFlushed == True

    @property
    def isClone(self):
        return self._isClone

    @property
    def isPendingResolution(self):
        return self._isPendingResolution

    @property
    def hasErrorImpact(self) -> bool:
        return False

    @property
    def hasNoErrorImpact(self) -> bool:
        return True

    @property
    def hasNoImpactDueToFrcLinkage(self):
        return False

    @property
    def uniqueID(self):
        return self.__uniqueID

    @property
    def eLogType(self):
        return self.__eType

    @property
    def eTypeGroupID(self):
        return _LogUtil.GetLogTypeGroup(self.__eType)

    @property
    def eErrorImpact(self):
        return None

    @property
    def header(self):
        return self.__GetHeader(bHighlight_=False)

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
        if not res is None:
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
        return None

    @property
    def euRNumber(self) -> int:
        return self._euRNumber

    @property
    def eTaskExecPhase(self) -> _ETaskExecutionPhaseID:
        return _ETaskExecutionPhaseID.eNone if self.__eTEPhase is None else self.__eTEPhase

    @property
    def callstack(self):
        return None

    def IsMyTaskError(self, myTID_ : int):
        return self.isError and (myTID_ is not None) and (myTID_ == self.taskID)

    def IsForeignTaskError(self, myTID_ : int):
        return not self.IsMyTaskError(myTID_)

    def Clone(self):
        return self._Clone()

    @staticmethod
    def _IsCompactOutputFormatEnabled() -> bool:
        return _LogEntry.__bCompactOutputFormatMode

    @staticmethod
    def _IsLogHighlightingEnabled() -> bool:
        return _LogEntry.__bLogHighlightingEnabled

    @staticmethod
    def _SetLogHighlightingMode(bEnabled_ =True):
        _LogEntry.__bLogHighlightingEnabled = bEnabled_

    @staticmethod
    def _SetFwFormatTags( includeUniqueID_     =True
                        , includeTimestamp_    =True
                        , includeTaskName_     =False
                        , includeTaskID_       =False
                        , includeFuncName_     =True
                        , includeFileName_     =True
                        , includeLineNo_       =True
                        , includeCallstack_    =True
                        , includeRaisedByInfo_ =True
                        , includeEuNum_        =None
                        , includeErrImp_       =None
                        , includeExecPhase_    =None):
        _LogEntry.__fmttagInclUniqueID     = includeUniqueID_
        _LogEntry.__fmttagInclTimestamp    = includeTimestamp_
        _LogEntry.__fmttagInclTaskName     = includeTaskName_
        _LogEntry.__fmttagInclTaskID       = includeTaskID_
        _LogEntry.__fmttagInclFuncName     = includeFuncName_
        _LogEntry.__fmttagInclFileName     = includeFileName_
        _LogEntry.__fmttagInclLineNo       = includeLineNo_
        _LogEntry.__fmttagInclCallstack    = includeCallstack_
        _LogEntry.__fmttagInclRaisedByInfo = includeRaisedByInfo_
        if includeEuNum_ is not None:
            _LogEntry.__fmttagInclEuNum = includeEuNum_
        if includeErrImp_ is not None:
            _LogEntry.__fmttagInclErrorImpact = includeErrImp_
        if includeExecPhase_ is not None:
            _LogEntry.__fmttagInclTExecPhase = includeExecPhase_

    @staticmethod
    def _GetFwFormatTags():
        return  ( _LogEntry.__fmttagInclUniqueID
                , _LogEntry.__fmttagInclTimestamp
                , _LogEntry.__fmttagInclTaskName
                , _LogEntry.__fmttagInclTaskID
                , _LogEntry.__fmttagInclFuncName
                , _LogEntry.__fmttagInclFileName
                , _LogEntry.__fmttagInclLineNo
                , _LogEntry.__fmttagInclCallstack
                , _LogEntry.__fmttagInclRaisedByInfo
                , _LogEntry.__fmttagInclEuNum
                , _LogEntry.__fmttagInclErrorImpact
                , _LogEntry.__fmttagInclTExecPhase )

    @staticmethod
    def _GetFwCompatFormatTags():
        return  ( _LogEntry.__fmttagInclTimestamp
                , _LogEntry.__fmttagInclTaskName )

    @staticmethod
    def _SetUserFormatTags( includeUniqueID_     =True
                          , includeTimestamp_    =True
                          , includeTaskName_     =False
                          , includeTaskID_       =False
                          , includeFuncName_     =True
                          , includeFileName_     =True
                          , includeLineNo_       =True
                          , includeCallstack_    =True
                          , includeRaisedByInfo_ =True
                          , includeEuNum_        =None
                          , includeErrImp_       =None
                          , includeExecPhase_    =None):
        _LogEntry.__ufmttagInclUniqueID     = includeUniqueID_
        _LogEntry.__ufmttagInclTimestamp    = includeTimestamp_
        _LogEntry.__ufmttagInclTaskName     = includeTaskName_
        _LogEntry.__ufmttagInclTaskID       = includeTaskID_
        _LogEntry.__ufmttagInclFuncName     = includeFuncName_
        _LogEntry.__ufmttagInclFileName     = includeFileName_
        _LogEntry.__ufmttagInclLineNo       = includeLineNo_
        _LogEntry.__ufmttagInclCallstack    = includeCallstack_
        _LogEntry.__ufmttagInclRaisedByInfo = includeRaisedByInfo_
        if includeEuNum_ is not None:
            _LogEntry.__ufmttagInclEuNum = includeEuNum_
        if includeErrImp_ is not None:
            _LogEntry.__ufmttagInclErrorImpact = includeErrImp_
        if includeExecPhase_ is not None:
            _LogEntry.__ufmttagInclTExecPhase = includeExecPhase_

    @staticmethod
    def _GetUserFormatTags():
        return  ( _LogEntry.__ufmttagInclUniqueID
                , _LogEntry.__ufmttagInclTimestamp
                , _LogEntry.__ufmttagInclTaskName
                , _LogEntry.__ufmttagInclTaskID
                , _LogEntry.__ufmttagInclFuncName
                , _LogEntry.__ufmttagInclFileName
                , _LogEntry.__ufmttagInclLineNo
                , _LogEntry.__ufmttagInclCallstack
                , _LogEntry.__ufmttagInclRaisedByInfo
                , _LogEntry.__ufmttagInclEuNum
                , _LogEntry.__ufmttagInclErrorImpact
                , _LogEntry.__ufmttagInclTExecPhase )

    @staticmethod
    def _GetUserCompatFormatTags():
        return  ( _LogEntry.__ufmttagInclTimestamp
                , _LogEntry.__ufmttagInclTaskName )

    @staticmethod
    def _EnableCompactOutputFormat():
        _LogEntry.__bCompactOutputFormatMode = True

    @property
    def _isSpecializedError(self):
        res = not self.eLogType.isFwApiLogType
        ree = res and self.isError
        res = res and self.eLogType != _ELogType.ERR
        res = res and self.eLogType != _ELogType.FTL
        return res

    @property
    def _isClone(self):
        return False

    @property
    def _isShared(self):
        return False

    @property
    def _isPendingResolution(self):
        return False

    @property
    def _euRNumber(self) -> int:
        return self.__euRNum

    @property
    def _type2String(self):
        return self.__TypeAsStr(bHighlight_=False)

    @property
    def _errorCode2String(self):
        return None

    @property
    def _causedBySystemException(self) -> Exception:
        return None

    @property
    def _nestedLogException(self):
        return None

    @property
    def _taskInstance(self):
        return None

    def _Clone(self):
        vlogif._LogOEC(False, -3001)
        return None

    def _SetCleanUpPermission(self, bCleanupPermitted_ : bool):
        pass

    def _ForceCleanUp(self):
        self.CleanUp()

    def _Adapt( self, eLogType_ : _ELogType =None, shortMsg_ : str =None, uniqueID_ : int =None, bFlushed_ : bool =None
              , bCleanupPermitted_ : bool =None, eTaskExecPhaseID_ : _ETaskExecutionPhaseID =None):
        if eLogType_ is not None:
            self.__eType = eLogType_
        if shortMsg_ is not None:
            self.__shortMsg = shortMsg_
        if uniqueID_ is not None:
            self.__uniqueID = uniqueID_
        if bFlushed_ is not None:
            self.__bFlushed = bFlushed_
        if bCleanupPermitted_ is not None:
            self._SetCleanUpPermission(bCleanupPermitted_)
        if eTaskExecPhaseID_ is not None:
            self.__eTEPhase = eTaskExecPhaseID_

    def _ToString(self, *args_, **kwargs_):
        _hdr = self.__GetHeader(bHighlight_=False)

        res = _CommonDefines._STR_EMPTY if _hdr is None else _hdr

        if self.shortMessage is None or self.longMessage is None:
            if self.shortMessage is not None:
                res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_016).format(self.shortMessage)
            elif self.longMessage is not None:
                res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_016).format(self.longMessage)
            elif _hdr is not None:
                res += _CommonDefines._CHAR_SIGN_SPACE + _CommonDefines._CHAR_SIGN_DASH
        else:
            res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_017).format(self.shortMessage, self.longMessage)
        if _hdr is None:
            res = res.lstrip()

        _bHIGHLIGHT = True
        if _bHIGHLIGHT:
            res = self.__HighlightText(res)

        if self.isError:
            _bFwApiLogType     = self.eLogType.isFwApiLogType
            _bInclCallstack    = _LogEntry.__ufmttagInclCallstack    if _bFwApiLogType else _LogEntry.__fmttagInclCallstack
            _bInclRaisedByInfo = _LogEntry.__ufmttagInclRaisedByInfo if _bFwApiLogType else _LogEntry.__fmttagInclRaisedByInfo

            if _bInclCallstack and (self.callstack is not None):
                res += _FwTDbEngine.GetText(_EFwTextID.eLogEntry_ToString_01).format(self.callstack.rstrip())
            if _bInclRaisedByInfo and self._causedBySystemException is not None:
                _rbxInfo = self._causedBySystemException.ToString(*args_, **kwargs_)
                _rbxInfo = _rbxInfo.split(_CommonDefines._CHAR_SIGN_NEWLINE)
                _rbxInfo = f'{_CommonDefines._CHAR_SIGN_NEWLINE}{_CommonDefines._CHAR_SIGN_TAB}'.join(_rbxInfo)
                _rbxInfo = _CommonDefines._CHAR_SIGN_TAB + _rbxInfo
                _rbxInfo = _FwTDbEngine.GetText(_EFwTextID.eLogEntry_ToString_02).format(_rbxInfo.rstrip())
                _rbxInfo = self.__HighlightText(_rbxInfo, _EColorCode.RED)
                res += _rbxInfo
            if self._nestedLogException is not None:
                _nxcp = self._nestedLogException.ToString(*args_, **kwargs_)
                _nxcp = _nxcp.split(_CommonDefines._CHAR_SIGN_NEWLINE)
                _nxcp = f'{_CommonDefines._CHAR_SIGN_NEWLINE}{_CommonDefines._CHAR_SIGN_TAB}'.join(_nxcp)
                _nxcp = _CommonDefines._CHAR_SIGN_TAB + _nxcp
                res += _FwTDbEngine.GetText(_EFwTextID.eLogEntry_ToString_03).format(_nxcp.rstrip())
        return res

    def _CleanUp(self):
        self.__eType    = None
        self.__euRNum   = None
        self.__lineNo   = None
        self.__tstamp   = None
        self.__taskID   = None
        self.__longMsg  = None
        self.__bFlushed = None
        self.__shortMsg = None
        self.__filePath = None
        self.__funcName = None
        self.__taskName = None
        self.__uniqueID = None
        self.__eTEPhase = None

    @staticmethod
    def __GetCallStackInfo(inheritanceDepth_ =0, callstackLevelOffset_ =None):
        if callstackLevelOffset_ is None:
            callstackLevelOffset_ = _LogUtil.GetCallstackLevelOffset()

        _frameIdx = _LogUtil.GetCallstackLevel() + callstackLevelOffset_ + inheritanceDepth_

        _cstack = inspect.stack()
        if (_cstack is None) or (len(_cstack) < 1):
            _frameIdx = None
        elif _frameIdx >= len(_cstack):
            _frameIdx = None

        _frame    = None
        _index    = None
        _lines    = None
        _lineNo   = None
        _filePath = None
        _funcName = None
        if _frameIdx is None:
            pass
        else:
            _frame, _filePath, _lineNo, _funcName, _lines, _index = _cstack[_frameIdx]
        return _filePath, _lineNo, _funcName

    def __HighlightText(self, txt_ : str, colorCode_ : _EColorCode =_EColorCode.NONE):
        if not _LogEntry.__bLogHighlightingEnabled:
            return txt_

        _cc = colorCode_
        if not _cc.isColor:
            if self.isError:
                _cc = _EColorCode.RED
            elif self.isKPI:
                _cc = _EColorCode.BLUE
            elif self.isWarning:
                _cc = _EColorCode.RED if self.__eType.isUrgentWarning else _EColorCode.YELLOW

        res = txt_
        if _cc.isColor:
            res = _TextStyle.ColorText(txt_, _cc)
        return res

    def __TypeAsStr(self, bHighlight_ =False):
        _grpID = self.eTypeGroupID
        if (_grpID is None) or (_grpID==_ELogType.FREE):
            res = None
        else:
            _bFwApiLogType    = self.eLogType.isFwApiLogType
            _grpTypeName      = _ELogType(_grpID.value*-1).name if _bFwApiLogType else _grpID.compactName
            _bInclErrorImpact = _LogEntry.__ufmttagInclErrorImpact if _bFwApiLogType else _LogEntry.__fmttagInclErrorImpact

            if _bInclErrorImpact and (self.eErrorImpact is not None):
                res = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_011).format(_grpTypeName, self.eErrorImpact.value)
            else:
                res = _grpTypeName

            if bHighlight_:
                res = self.__HighlightText(res)
        return res

    def __GetHeader(self, bHighlight_ =False):
        _bVerbose = self.isError or not _LogEntry.__bCompactOutputFormatMode

        if _bVerbose:
            res = self.__GetVerboseHeader(bHighlightLogType_=False)
        else:
            res = self.__GetCompactHeader(bHighlightLogType_=False)

        if bHighlight_:
            res = self.__HighlightText(res)
        return res

    def __GetVerboseHeader(self, bHighlightLogType_ =False):
        _tstr = self.__TypeAsStr(bHighlight_=bHighlightLogType_)
        if _tstr is None:
            return None

        _incUniqueID      = False
        _incTimestamp     = False
        _incTaskName      = False
        _incTaskID        = False
        _incFuncName      = False
        _incFileName      = False
        _incLineNo        = False
        _incCallstack     = False
        _incRaisedByInfo  = False
        _includeEuNum     = False
        _includeErrImp    = False
        _includeExecPhase = False

        _bUserLog = self.eLogType.isFwApiLogType
        if not _bUserLog:
            _bUserLog = (self.eTaskExecPhase is not None) and not (self.eTaskExecPhase.isRunnableExecution or self.eTaskExecPhase.isFwHandling)
        if _bUserLog:
            _incUniqueID, _incTimestamp, _incTaskName, _incTaskID, _incFuncName, _incFileName, _incLineNo, \
                _incCallstack, _incRaisedByInfo, _includeEuNum, _includeErrImp, _includeExecPhase = _LogEntry._GetUserFormatTags()
        else:
            _incUniqueID, _incTimestamp, _incTaskName, _incTaskID, _incFuncName, _incFileName, _incLineNo, \
                _incCallstack, _incRaisedByInfo, _includeEuNum, _includeErrImp, _includeExecPhase = _LogEntry._GetFwFormatTags()

        if self.taskID is None:
            _incTaskID = False

        if _incTaskName:
            if self.taskName is None:
                self.__taskName = _GetCurThread().name

        if self.functionName is None:
            _incFuncName = False
        if self.fileName is None:
            _incFileName = False
        if self.lineNo is None:
            _incLineNo = False
        elif not _incFileName:
            _incLineNo = False
        if _incUniqueID:
            if self.uniqueID == _LogUtil.GetInvalidUniqueID():
                _incUniqueID = False

        if not _incUniqueID:
            res = _CommonDefines._STR_EMPTY
        else:
            res = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_010).format(self.uniqueID)

        if not _incTimestamp:
            if not _incTaskName:
                if not _incTaskID:
                    if not _incFuncName:
                        if not _incFileName:
                            return res + _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_010).format(_tstr)

        if not _incTimestamp:
            res += _CommonDefines._CHAR_SIGN_LEFT_SQUARED_BRACKET
        else:
            res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_020).format(self.timestampMS)

        errorCode2String = self._errorCode2String
        if errorCode2String is not None:
            res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_021).format(_tstr, errorCode2String)
        else:
            res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_022).format(_tstr)

        if _incTaskName or _incTaskID:
            tmp = _CommonDefines._STR_EMPTY

            if _incTaskName:
                tmp += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_006).format(self.taskName)
            if _incTaskID:
                if _incTaskName:
                    tmp += _CommonDefines._CHAR_SIGN_COLON
                tmp += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_006).format(self.taskID)
            if _includeEuNum:
                tmp += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_018).format('-' if self.__euRNum is None else self.__euRNum)
            if self.isError and _includeExecPhase:
                tmp += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_019).format(self.eTaskExecPhase.value)
            res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_010).format(tmp)

        if _incFileName:
            if not _incLineNo:
                res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_010).format(self.fileName)
            else:
                res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_003).format(self.fileName, self.lineNo)
        if _incFuncName:
            res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_010).format(self.functionName)
        if self._isSpecializedError:
            res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_010).format(self.eLogType.name)
        return res

    def __GetCompactHeader(self, bHighlightLogType_ =False):
        _tstr = self.__TypeAsStr(bHighlight_=bHighlightLogType_)
        if _tstr is None:
            return None

        if self.__eType.isFwApiLogType:
            _incTimestamp, _incTaskName = _LogEntry._GetUserCompatFormatTags()
        else:
            _incTimestamp, _incTaskName = _LogEntry._GetFwCompatFormatTags()

        if _incTaskName:
            if self.__taskName is None:
                _incTaskName = False

        if not _incTimestamp:
            if not _incTaskName:
                return _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_010).format(_tstr)

        res  = _CommonDefines._CHAR_SIGN_LEFT_SQUARED_BRACKET if not _incTimestamp else _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_020).format(self.timestampMS)
        res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_022).format(_tstr)

        if _incTaskName:
            res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_010).format(self.__taskName)
        return res

    def __SetupEntry( self, eLogType_, taskName_ : str =None, taskID_ =None, shortMsg_ : str =None, longMsg_ : str =None
                     , inheritanceDepth_ =0, callstackLevelOffset_ =None, euRNum_ =None, bXTaskTask_ =None):
        if not isinstance(eLogType_, _ELogType):
            self.CleanUp()
            vlogif._LogOEC(True, -1046)
            return

        if taskName_ is None:
            pass
        elif not isinstance(taskName_, str):
            self.CleanUp()
            vlogif._LogOEC(True, -1047)
            return
        else:
            taskName_ = taskName_.strip()
            if len(taskName_) < 1:
                taskName_ = None

        if eLogType_.isFwApiLogType:
            if not _LogEntry.__ufmttagInclTaskName:
                pass
            elif taskName_ is None:
                taskName_ = _GetCurThread().name
        else:
            if not _LogEntry.__fmttagInclTaskName:
                pass
            elif taskName_ is None:
                taskName_ = _GetCurThread().name

        if bXTaskTask_ is not None:
            if not bXTaskTask_:
                taskName_ = None

        if shortMsg_ is not None:
            if not isinstance(shortMsg_, str):
                shortMsg_ = None
            else:
                shortMsg_ = shortMsg_.strip()
                if len(shortMsg_) == 0:
                    shortMsg_ = None
            self.__shortMsg = shortMsg_
        if longMsg_ is not None:
            if not isinstance(longMsg_, str):
                longMsg_ = None
            else:
                longMsg_ = longMsg_.strip()
                if len(longMsg_) == 0:
                    longMsg_ = None
            self.__longMsg = longMsg_

        self.__eType    = eLogType_
        self.__tstamp   = None if _FwTDbEngine.GetText(_EFwTextID.eMisc_PyModuleName_DateTime) not in sys.modules else _Datetime.now()
        self.__bFlushed = False
        self.__taskName = taskName_

        if _LogUtil.GetLogTypeGroup(eLogType_).isNonError:
            if _LogEntry.__bCompactOutputFormatMode:
                return

        if taskID_ is not None:
            if not isinstance(taskID_, int):
                taskID_ = None

        self.__euRNum   = euRNum_
        self.__taskID   = taskID_
        self.__uniqueID = _LogUtil.GetInvalidUniqueID()

        self.__filePath, self.__lineNo, self.__funcName = \
            _LogEntry.__GetCallStackInfo(inheritanceDepth_=inheritanceDepth_, callstackLevelOffset_=callstackLevelOffset_)
