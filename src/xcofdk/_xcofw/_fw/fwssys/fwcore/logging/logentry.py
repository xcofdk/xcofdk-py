# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : logentry.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

import inspect
import os
import sys
from   datetime import datetime as _Datetime
from   typing import Union

from _fw.fwssys.fwcore.logging            import vlogif
from _fw.fwssys.fwcore.logging.logdefines import _GetCurThread
from _fw.fwssys.fwcore.logging.logdefines import _ELogType
from _fw.fwssys.fwcore.logging.logdefines import _LogUtil
from _fw.fwssys.fwcore.logrd.logrecord    import _EColorCode
from _fw.fwssys.fwcore.logrd.logrecord    import _LogRecord
from _fw.fwssys.fwcore.logrd.logrecord    import _IRDLogRP
from _fw.fwssys.fwcore.ipc.tsk.taskutil   import _ETaskXPhaseID
from _fw.fwssys.fwcore.types.aobject      import _AbsSlotsObject
from _fw.fwssys.fwcore.types.commontypes  import _CommonDefines
from _fw.fwssys.fwcore.types.commontypes  import _EDepInjCmd
from _fw.fwssys.fwcore.types.commontypes  import override

from _fw.fwssys.fwerrh.fwerrorcodes import _EFwErrorCode

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _LogEntry(_AbsSlotsObject, _IRDLogRP):
    __slots__ = [ '__t' , '__fp' , '__fn' , '__no' , '__uid' , '__ml' , '__ms' , '__tst' , '__tn' , '__tid' , '__xrn' , '__xph' , '__lr' ]

    __bLHE  = True
    __bCOFE = True

    __fmttagInclUniqueID      = True
    __fmttagInclTimestamp     = True
    __fmttagInclTaskName      = True
    __fmttagInclTaskID        = True
    __fmttagInclEuNum         = True
    __fmttagInclFuncName      = True
    __fmttagInclFileName      = True
    __fmttagInclLineNo        = True
    __fmttagInclCallstack     = True
    __fmttagInclRaisedByInfo  = True
    __fmttagInclErrorImpact   = True
    __fmttagInclTExecPhase    = True

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

    def __init__( self, logType_, taskName_ : str =None, taskID_ : int =None
                , shortMsg_ : str =None, longMsg_ : str =None
                , cloneby_ =None, doSkipSetup_ =False, xrn_ =None, bXTaskTask_ =None):
        _AbsSlotsObject.__init__(self)
        _IRDLogRP.__init__(self)

        self.__t   = None
        self.__fp  = None
        self.__fn  = None
        self.__lr  = None
        self.__ml  = None
        self.__ms  = None
        self.__no  = None
        self.__tn  = None
        self.__tid = None
        self.__tst = None
        self.__uid = None
        self.__xph = None
        self.__xrn = None

        if doSkipSetup_:
            pass
        elif cloneby_ is not None:
            if not isinstance(cloneby_, _LogEntry):
                self.CleanUp()
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00433)
            elif not cloneby_.isValid:
                pass
            else:
                self.__t   = cloneby_.__t
                self.__fp  = cloneby_.__fp
                self.__fn  = cloneby_.__fn
                self.__lr  = cloneby_.__lr
                self.__ml  = cloneby_.__ml
                self.__ms  = cloneby_.__ms
                self.__no  = cloneby_.__no
                self.__tn  = cloneby_.__tn
                self.__tid = cloneby_.__tid
                self.__tst = cloneby_.__tst
                self.__uid = cloneby_.__uid
                self.__xph = cloneby_.__xph
                self.__xrn = cloneby_.__xrn
        else:
            self.__SetupEntry(logType_, taskName_=taskName_, taskID_=taskID_, shortMsg_=shortMsg_, longMsg_=longMsg_, xrn_=xrn_, bXTaskTask_=bXTaskTask_)

    @property
    def isValid(self) -> bool:
        return self.__t is not None

    @property
    def isInvalid(self) -> bool:
        return self.__t is None

    @property
    def isFwApiLog(self):
        return False if self.__t is None else self.__t.isFwApiLogType

    @property
    def isError(self):
        _gid = self._logTypeGrpID
        return False if _gid is None else _gid.isError

    @property
    def isUserError(self):
        return self._logTypeGrpID == _ELogType.ERR

    @property
    def isFatalError(self):
        return self._logTypeGrpID == _ELogType.FTL

    @property
    def isKPI(self):
        return self._logTypeGrpID == _ELogType.KPI

    @property
    def isWarning(self):
        return self._logTypeGrpID == _ELogType.WNG

    @property
    def isFreeLog(self):
        return self._logTypeGrpID == _ELogType.FREE

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
        return self.__uid

    @property
    def logType(self):
        return self.__t

    @property
    def errorImpact(self):
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
        return self.__ms

    @property
    def longMessage(self):
        return self.__ml

    @property
    def dtaskName(self):
        return self.__tn

    @property
    def dtaskUID(self):
        return self.__tid

    @property
    def lineNo(self):
        return self.__no

    @property
    def fileName(self):
        res = self.filePath
        if not res is None:
            res = os.path.basename(os.path.realpath(res))
        return res

    @property
    def filePath(self):
        return self.__fp

    @property
    def functionName(self):
        return self.__fn

    @property
    def timestampMS(self):
        return _LogUtil.GetLogTimestamp(self.__tst)

    @property
    def errorCode(self) -> int:
        return None

    @property
    def xrNumber(self) -> int:
        return self._xrNumber

    @property
    def taskXPhase(self) -> _ETaskXPhaseID:
        return _ETaskXPhaseID.eNA if self.__xph is None else self.__xph

    @property
    def callstack(self) -> str:
        return None

    def IsMyTaskError(self, myTID_ : int):
        return self.isError and (myTID_ is not None) and (myTID_ == self.dtaskUID)

    def IsForeignTaskError(self, myTID_ : int):
        return not self.IsMyTaskError(myTID_)

    def Clone(self):
        return self._Clone()

    @_IRDLogRP._recStr.getter
    def _recStr(self) -> str:
        return self.ToString()

    @_IRDLogRP._logRecord.getter
    def _logRecord(self):
        return self.__lr

    @override
    def _CleanUpLE(self):
        self.CleanUp()

    @staticmethod
    def _IsCompactOutputFormatEnabled() -> bool:
        return _LogEntry.__bCOFE

    @staticmethod
    def _ClsDepInjection( dinjCmd_             : _EDepInjCmd
                        , bHLMode_             : bool =None
                        , bUserFmt_            =False
                        , includeUniqueID_     =True
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
        if bHLMode_ is not None:
            _LogEntry.__bLHE = bHLMode_
        else:
            if includeCallstack_ is None:
                includeCallstack_ = False if bUserFmt_ else True

            if bUserFmt_:
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
            else:
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

    @property
    def _isSpecializedError(self):
        res = not self.logType.isFwApiLogType
        ree = res and self.isError
        res = res and self.logType != _ELogType.ERR
        res = res and self.logType != _ELogType.FTL
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
    def _logTypeGrpID(self):
        return _LogUtil.GetLogTypeGroup(self.__t)

    @property
    def _xrNumber(self) -> int:
        return self.__xrn

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
        vlogif._LogOEC(False, _EFwErrorCode.VUE_00038)
        return None

    def _SetCleanUpPermission(self, bCleanupPermitted_ : bool):
        pass

    def _ForceCleanUp(self):
        self.CleanUp()

    def _Adapt( self, logType_ : _ELogType =None, shortMsg_ : str =None, uniqueID_ : int =None
              , bCleanupPermitted_ : bool =None, eTaskExecPhaseID_ : _ETaskXPhaseID =None, taskName_ : str =None, taskID_ : int =None):
        if logType_ is not None:
            self.__t = logType_
        if shortMsg_ is not None:
            self.__ms = shortMsg_
        if uniqueID_ is not None:
            self.__uid = uniqueID_
        if bCleanupPermitted_ is not None:
            self._SetCleanUpPermission(bCleanupPermitted_)
        if eTaskExecPhaseID_ is not None:
            self.__xph = eTaskExecPhaseID_
        if taskName_ is not None:
            self.__tn = taskName_
        if taskID_ is not None:
            self.__tid = taskID_

    def _ToString(self):
        _hdr = self.__GetHeader(bHighlight_=False)
        res  = _CommonDefines._STR_EMPTY if _hdr is None else _hdr

        if (self.shortMessage is None) or (self.longMessage is None):
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

        if self.isFatalError:
            _bUserLog = self.logType.isFwApiLogType

            _cs = self.__FmtCallstack()
            if _cs is not None:
                res += _cs

            _rbi = self.__FmtTraceback()
            if _rbi is not None:
                res += _rbi

            if self._nestedLogException is not None:
                _nxcp = str(self._nestedLogException)
                _nxcp = _nxcp.split(_CommonDefines._CHAR_SIGN_LF)
                _nxcp = f'{_CommonDefines._CHAR_SIGN_LF}{_CommonDefines._CHAR_SIGN_TAB}'.join(_nxcp)
                _nxcp = _CommonDefines._CHAR_SIGN_TAB + _nxcp
                res  += _FwTDbEngine.GetText(_EFwTextID.eLogEntry_ToString_03).format(_nxcp.rstrip())
        return res

    def __FmtCallstack(self) -> Union[str, None]:
        if self.isInvalid or (not self.isFatalError) or (self.callstack is None):
            return None

        _bInclCS = _LogEntry.__ufmttagInclCallstack if self.logType.isFwApiLogType else _LogEntry.__fmttagInclCallstack
        if not _bInclCS:
            return None

        return _FwTDbEngine.GetText(_EFwTextID.eLogEntry_ToString_01).format(self.callstack.rstrip())

    def __FmtTraceback(self) -> Union[str, None]:
        if self.isInvalid or (not self.isFatalError) or (self._causedBySystemException is None):
            return None

        _bInclRBI = _LogEntry.__ufmttagInclRaisedByInfo if self.logType.isFwApiLogType else _LogEntry.__fmttagInclRaisedByInfo
        if not _bInclRBI:
            return None

        res = str(self._causedBySystemException)
        res = res.split(_CommonDefines._CHAR_SIGN_LF)
        res = f'{_CommonDefines._CHAR_SIGN_LF}{_CommonDefines._CHAR_SIGN_TAB}'.join(res)
        res = _CommonDefines._CHAR_SIGN_TAB + res
        return _FwTDbEngine.GetText(_EFwTextID.eLogEntry_ToString_02).format(res.rstrip())

    def _CleanUp(self):
        self.__t   = None
        self.__fp  = None
        self.__fn  = None
        self.__lr  = None
        self.__ml  = None
        self.__ms  = None
        self.__no  = None
        self.__tn  = None
        self.__tid = None
        self.__tst = None
        self.__uid = None
        self.__xph = None
        self.__xrn = None

    @staticmethod
    def __GetFwFormatTags():
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
    def __GetFwCompatFormatTags():
        return  ( _LogEntry.__fmttagInclTimestamp
                , _LogEntry.__fmttagInclTaskName )

    @staticmethod
    def __GetUserFormatTags():
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
    def __GetUserCompatFormatTags():
        return  ( _LogEntry.__ufmttagInclTimestamp
                , _LogEntry.__ufmttagInclTaskName )

    def __GetColorCode(self) -> _EColorCode:
        if self.isError:
            res = _EColorCode.RED
        elif self.isKPI:
            res = _EColorCode.BLUE
        elif self.isWarning:
            res = _EColorCode.RED if self.__t.isUrgentWarning else _EColorCode.YELLOW
        else:
            res = _EColorCode.NONE
        return res

    def __TypeAsStr(self, bHighlight_ =False):
        _grpID = self._logTypeGrpID
        if (_grpID is None) or (_grpID==_ELogType.FREE):
            res = None
        else:
            _bFwApiLogType    = self.logType.isFwApiLogType
            _grpTypeName      = _ELogType(_grpID.value*-1).name if _bFwApiLogType else _grpID.compactName
            _bInclErrorImpact = _LogEntry.__ufmttagInclErrorImpact if _bFwApiLogType else _LogEntry.__fmttagInclErrorImpact

            if _bInclErrorImpact and (self.errorImpact is not None):
                res = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_011).format(_grpTypeName, '{0:03X}'.format(self.errorImpact.value))
            else:
                res = _grpTypeName
        return res

    def __GetHeader(self, bHighlight_ =False):
        _bVerbose = self.isError or not _LogEntry._IsCompactOutputFormatEnabled()

        if _bVerbose:
            res = self.__GetVerboseHeader(bHighlightLogType_=False)
        else:
            res = self.__GetCompactHeader(bHighlightLogType_=False)
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

        _bUserLog = self.logType.isFwApiLogType
        if not _bUserLog:
            _bUserLog = (self.taskXPhase is not None) and not (self.taskXPhase.isRunnableExecution or self.taskXPhase.isFwHandling)
        if _bUserLog:
            _incUniqueID, _incTimestamp, _incTaskName, _incTaskID, _incFuncName, _incFileName, _incLineNo, \
                _incCallstack, _incRaisedByInfo, _includeEuNum, _includeErrImp, _includeExecPhase = _LogEntry.__GetUserFormatTags()
        else:
            _incUniqueID, _incTimestamp, _incTaskName, _incTaskID, _incFuncName, _incFileName, _incLineNo, \
                _incCallstack, _incRaisedByInfo, _includeEuNum, _includeErrImp, _includeExecPhase = _LogEntry.__GetFwFormatTags()

        if self.dtaskUID is None:
            _incTaskID = False

        if _incTaskName:
            if self.dtaskName is None:
                self.__tn = _GetCurThread().name

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

        _errCode2Str = self._errorCode2String
        if _errCode2Str is not None:
            res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_021).format(_tstr, _errCode2Str)
        else:
            res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_022).format(_tstr)

        if _incTaskName or _incTaskID:
            _tmp = _CommonDefines._STR_EMPTY

            if _incTaskName:
                _tmp += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_006).format(self.dtaskName)
            if _incTaskID:
                if _incTaskName:
                    _tmp += _CommonDefines._CHAR_SIGN_COLON
                _tmp += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_006).format(self.dtaskUID)
            if _includeEuNum:
                _tmp += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_018).format('-' if self.__xrn is None else self.__xrn)
            if self.isError and _includeExecPhase:
                _tmp += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_019).format(self.taskXPhase.value)
            res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_010).format(_tmp)
        return res

    def __GetCompactHeader(self, bHighlightLogType_ =False):
        _tstr = self.__TypeAsStr(bHighlight_=bHighlightLogType_)
        if _tstr is None:
            return None

        if self.__t.isFwApiLogType:
            _incTimestamp, _incTaskName = _LogEntry.__GetUserCompatFormatTags()
        else:
            _incTimestamp, _incTaskName = _LogEntry.__GetFwCompatFormatTags()

        if _incTaskName:
            if self.__tn is None:
                self.__tn = _GetCurThread().name

        if not _incTimestamp:
            if not _incTaskName:
                return _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_010).format(_tstr)

        res  = _CommonDefines._CHAR_SIGN_LEFT_SQUARED_BRACKET if not _incTimestamp else _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_020).format(self.timestampMS)
        res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_022).format(_tstr)

        if _incTaskName:
            res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_010).format(self.__tn)
        return res

    def __SetupEntry( self
                    , logType_ : _ELogType, taskName_ : str =None, taskID_ : int =None, shortMsg_ : str =None
                    , longMsg_ : str =None, xrn_ =None, bXTaskTask_ =None):
        if not isinstance(logType_, _ELogType):
            self.CleanUp()
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00434)
            return

        if taskName_ is None:
            pass
        elif not isinstance(taskName_, str):
            self.CleanUp()
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00435)
            return
        else:
            taskName_ = taskName_.strip()
            if len(taskName_) < 1:
                taskName_ = None

        if logType_.isFwApiLogType:
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
            if logType_.isFree or not isinstance(shortMsg_, str):
                pass
            else:
                shortMsg_ = shortMsg_.strip()
                if len(shortMsg_) == 0:
                    shortMsg_ = None
        if shortMsg_ is None:
            shortMsg_ = _CommonDefines._STR_EMPTY

        if taskID_ is not None:
            if not isinstance(taskID_, int):
                taskID_ = None

        self.__t   = logType_
        self.__ms  = shortMsg_
        self.__tn  = taskName_
        self.__tid = taskID_
        self.__tst = None if _Datetime.__name__ not in sys.modules else _Datetime.now()
        self.__uid = _LogUtil.GetInvalidUniqueID()
        self.__xrn = xrn_
        self.__lr  = _LogRecord(self, color_=self.__GetColorCode(), logType_=self.__t._toLRLogType)

