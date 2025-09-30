# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwerrhrp.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum   import IntEnum
from enum   import unique
from typing import Union

from xcofdk.fwapi.xmt import XTaskException

from _fw.fwssys.fwcore.logging            import vlogif
from _fw.fwssys.fwcore.logging.logdefines import _LogUtil
from _fw.fwssys.fwcore.logging.logdefines import _ELogType
from _fw.fwssys.fwcore.logging.logdefines import _EErrorImpact
from _fw.fwssys.fwcore.logging.logdefines import _ELogifOperationOption
from _fw.fwssys.fwcore.logging.logmgrdata import _LogMgrData
from _fw.fwssys.fwcore.lc.lcproxyclient   import _LcProxyClient
from _fw.fwssys.fwcore.lc.lcproxydefines  import _TaskInfo
from _fw.fwssys.fwcore.lc.lcproxydefines  import _ProxyInfo
from _fw.fwssys.fwcore.types.commontypes  import _CommonDefines
from _fw.fwssys.fwerrh.fwerrorcodes       import _EFwErrorCode
from _fw.fwssys.fwerrh.logs.errorlog      import _ErrorLog
from _fw.fwssys.fwerrh.logs.errorlog      import _FatalLog
from _fw.fwssys.fwerrh.logs.logexception  import _LogException
from _fw.fwssys.fwerrh.logs.logexception  import _LogExceptionFatal
from _fw.fwssys.fwerrh.logs.logexception  import _LogExceptionBadUse
from _fw.fwssys.fwerrh.logs.logexception  import _LogExceptionImplError
from _fw.fwssys.fwerrh.logs.logexception  import _LogExceptionNestedError
from _fw.fwssys.fwerrh.logs.logexception  import _LogExceptionNotImplemented
from _fw.fwssys.fwerrh.logs.logexception  import _LogExceptionSystemOpERR
from _fw.fwssys.fwerrh.logs.logexception  import _LogExceptionSystemOpXCP
from _fw.fwssys.fwerrh.logs.dieexception  import _DieException
from _fw.fwssys.fwerrh.logs.xcoexception  import _IsXTXcp
from _fw.fwssys.fwerrh.logs.xcoexception  import _XcoXcpRootBase
from _fw.fwssys.fwerrh.logs.xcoexception  import _XcoBaseException
from _fw.fwssys.fwerrh.logs.xcoexception  import _XTaskXcpImpl

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _FwErrhRP(_LcProxyClient):
    @unique
    class _EDieExceptionTarget(IntEnum):
        eFwMain   = 0
        eRESERVED = 1

    __slots__ = [ '__pd' ]

    __dieXcpTgt = None

    __logXcpClassMap = {
          _ELogType.FTL      : _LogExceptionFatal
        , _ELogType.FTL_BU   : _LogExceptionBadUse
        , _ELogType.FTL_IE   : _LogExceptionImplError
        , _ELogType.FTL_NIY  : _LogExceptionNotImplemented
        , _ELogType.FTL_SOE  : _LogExceptionSystemOpERR
        , _ELogType.FTL_SOX  : _LogExceptionSystemOpXCP
        , _ELogType.XFTL     : _LogExceptionFatal
        , _ELogType.XFTL_SOX : _LogExceptionSystemOpXCP
    }

    def __init__(self):
        self.__pd = None
        super().__init__()

    def _CleanUp(self):
        super()._CleanUp()
        self.__pd = None

    @staticmethod
    def _CreateErrorLog( taskName_, taskID_, logTypeGrpID_ : _ELogType, logType_: _ELogType
                       , shortMsg_: str = None, longMsg_: str = None, errCode_: int = None
                       , sysOpXcp_=None, xcpTraceback_=None, xrn_ =None, bXcpModeEnabled_ =True
                       ) -> Union[_ErrorLog, _FatalLog, None]:
        if logType_._absValue < _ELogType.ERR.value:
            return None

        _bFatal = logType_._absValue >= _ELogType.FTL.value
        if _bFatal and (logTypeGrpID_ != _ELogType.FTL):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00453)
            return None

        if _bFatal:
            _xcpCls = _FwErrhRP.__logXcpClassMap[logType_]
            if logType_._absValue == _ELogType.FTL_SOX.value:
                _xcp = _xcpCls(sysOpXcp_, xcpTraceback_, errCode_=errCode_, taskName_=taskName_, taskID_=taskID_, shortMsg_=shortMsg_, longMsg_=longMsg_, xrn_=xrn_, bFwApiLog_=logType_.isFwApiLogType)
            else:
                _xcp = _xcpCls(errCode_=errCode_, taskName_=taskName_, taskID_=taskID_, shortMsg_=shortMsg_, longMsg_=longMsg_, xrn_=xrn_, bFwApiLog_=logType_.isFwApiLogType)

            if bXcpModeEnabled_:
                res = _xcp._enclosedFatalEntry
            else:
                res = _xcp._DetachEnclosedFatalEntry()
                _xcp.CleanUp()
        else:
            res = _ErrorLog(logType_, errCode_=errCode_, taskName_=taskName_, taskID_=taskID_, shortMsg_=shortMsg_, longMsg_=longMsg_, xrn_=xrn_)
        return res

    def _RPSetUp(self, data_ : _LogMgrData):
        if _FwErrhRP.__dieXcpTgt is not None:
            if _FwErrhRP.__dieXcpTgt != _FwErrhRP._EDieExceptionTarget.eFwMain:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00439)
                return False

        self.__pd = data_
        _FwErrhRP.__dieXcpTgt = _FwErrhRP._EDieExceptionTarget.eFwMain
        return True

    def _RPProcessErrorLog(self, errLog_: _ErrorLog, curPxyInfo_, bXtLog_: bool, bUnhandledXcoBaseXcp_=False, logifOpOption_=_ELogifOperationOption.eDontCare):
        return self.__ProcessErrorLog( errLog_, curPxyInfo_, bXtLog_ , bUnhandledXcoBaseXcp_, logifOpOption_)

    @staticmethod
    def __NotifyTaskError(errLog_ : _ErrorLog, curPxyInfo_ : _ProxyInfo, errEvalCurTask_, errEvalFwMain_):
        res    = True
        _bCTAE = curPxyInfo_.curTaskInfo.taskBadge.isAutoEnclosed

        if errEvalFwMain_ is None:
            _bDoNotifCurTask = True
        else:
            errLog_._SetErrorImpact(errEvalFwMain_, mtxErrImpact_=curPxyInfo_.fwMainInfo._errorImpactSyncMutex)
            res = _FwErrhRP.__NotifyCheckTaskError(curPxyInfo_.fwMainInfo, errLog_, True)

            if not res:
                _bDoNotifCurTask = False
            elif errLog_.hasNoErrorImpact:
                _bDoNotifCurTask = False
            else:
                _bDoNotifCurTask = True

        if res:
            if errEvalFwMain_ is None:
                errLog_._SetErrorImpact(errEvalCurTask_)
            if _bDoNotifCurTask:
                res =_FwErrhRP.__NotifyCheckTaskError(curPxyInfo_.curTaskInfo, errLog_, False)
        return res

    @staticmethod
    def __NotifyCheckTaskError(taskInfo_ : _TaskInfo, errLog_ : _ErrorLog, bFTE_ : bool):
        _tskErr = taskInfo_.taskError
        _bConsumed = _tskErr._OnErrorNotification(errLog_)
        return _bConsumed

    def __ProcessErrorLog(self, errLog_ : _ErrorLog, curPxyInfo_, bXtLog_ : bool, bUnhandledXcoBaseXcp_, logifOpOption_):
        _bCTAE = curPxyInfo_.curTaskInfo.taskBadge.isAutoEnclosed

        if errLog_.isFatalError and _bCTAE:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00979)
            return None

        _eevFM = None
        _eevCT = None
        _eevCT, _eevFM = self.__EvaluateErrorLog(errLog_, curPxyInfo_)

        if _eevCT is None:
            curPxyInfo_.CleanUp()
            self.__pd.SetPendingTaskID(None)
            if self.__pd.subSeqXcp is not None:
                self.__pd.subSeqXcp.CleanUp()
                self.__pd.subSeqXcp = None
            self.__pd.UnlockApi()
            return None

        _xcpCaught = None
        _bSEOK     = False
        try:
            _bSEOK = _FwErrhRP.__NotifyTaskError(errLog_, curPxyInfo_, _eevCT, _eevFM)
        except _XcoXcpRootBase as _xcp:
            _xcpCaught = _xcp
        except BaseException as _xcp:
            _xcpCaught = _XcoBaseException(_xcp, tb_=_LogUtil._GetFormattedTraceback(), taskID_=curPxyInfo_.curTaskInfo.dtaskUID)

        curPxyInfo_.CleanUp()
        _ssXcp = self.__pd.subSeqXcp
        self.__pd.subSeqXcp = None
        self.__pd.SetPendingTaskID(None)
        self.__pd.UnlockApi()

        res = None

        if not _bSEOK:
            if _ssXcp is not None:
                _ssXcp.CleanUp()

            if _xcpCaught is not None:
                if not _IsXTXcp(_xcpCaught):
                    _xcpCaught.CleanUp()

            if errLog_.hasErrorImpact:
                errLog_._UpdateErrorImpact(_EErrorImpact.eNoImpactByProcessingFailure)
        elif errLog_.hasNoErrorImpact:
            pass
        elif logifOpOption_.isSetErrorOnly or bUnhandledXcoBaseXcp_:
            if _ssXcp is not None:
                _ssXcp.CleanUp()
        elif not _eevCT.isCausedByExceptionMode:
            if _ssXcp is not None:
                _ssXcp.CleanUp()
            self.__pd.LMPrint(errLog_)
        else:
            res = _FwErrhRP.__RaiseException(errLog_._enclosedByLogException, _eevCT, bXtLog_, subSeqXcp_=_ssXcp)
        return res

    def __EvaluateErrorLog(self, errLog_, curPxyInfo_):
        _eevCT, _eevFM = None, None

        if _FwErrhRP.__dieXcpTgt != _FwErrhRP._EDieExceptionTarget.eFwMain:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00454)
            return _eevCT, _eevFM

        _fwmInfo = curPxyInfo_.fwMainInfo

        if errLog_.isFatalError:
            if self.isDieXcpModeEnabled:
                if _fwmInfo is None:
                    if not curPxyInfo_.curTaskInfo.taskBadge.hasDieXcpTargetTaskRight:
                        vlogif._LogOEC(True, _EFwErrorCode.VFE_00455)
                    else:
                        _eevCT = _EErrorImpact.eImpactByDieException
                else:
                    _eevCT = _EErrorImpact.eImpactByDieException
                    if not _fwmInfo.taskBadge.hasDieExceptionDelegateTargetTaskRight:
                        vlogif._LogOEC(True, _EFwErrorCode.VFE_00456)
                    else:
                        _eevFM = _EErrorImpact.eImpactByDieException
            elif self.isExceptionModeEnabled:
                _eevCT = _EErrorImpact.eImpactByLogException
                if _fwmInfo is not None:
                    if _fwmInfo.taskBadge.hasErrorObserverTaskRight:
                        _eevFM = _EErrorImpact.eImpactByLogException
            elif self.isDieModeEnabled:
                _eevCT = _EErrorImpact.eImpactByDieError
                if _fwmInfo is not None:
                    _eevFM = _EErrorImpact.eImpactByDieError
            else:
                _eevCT = _EErrorImpact.eImpactByFatalError
                if _fwmInfo is not None:
                    if _fwmInfo.taskBadge.hasErrorObserverTaskRight:
                        _eevFM = _EErrorImpact.eImpactByFatalError
        else:
            _eevCT = _EErrorImpact.eImpactByUserError
            if _fwmInfo is not None:
                if _fwmInfo.taskBadge.hasErrorObserverTaskRight:
                    _eevFM = _EErrorImpact.eImpactByUserError
        if _eevCT is None:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00457)
            _eevCT, _eevFM = None, None
        elif (_fwmInfo is not None) and (_eevFM is None):
            _eevCT = None
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00458)
        return _eevCT, _eevFM

    @staticmethod
    def __RaiseException(logXcp_ : _LogException, eevCurTask_ : _EErrorImpact, bXtLog_ : bool, subSeqXcp_ =None):
        if not isinstance(logXcp_, _LogException):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00459)
            return None
        if not (isinstance(eevCurTask_, _EErrorImpact) and eevCurTask_.isCausedByExceptionMode):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00460)
            return None

        if subSeqXcp_ is not None:
            logXcp_ = _LogExceptionNestedError(logXcp_, subSeqXcp_)

        res          = None
        _bRaiseXtXcp = bXtLog_

        if not _bRaiseXtXcp:
            _bRaiseXtXcp = logXcp_._enclosedFatalEntry.taskXPhase.isXTaskExecution
        if eevCurTask_.isCausedByDieMode:
            if eevCurTask_ == _EErrorImpact.eImpactByDieException:
                if _bRaiseXtXcp:
                    _impl = _XTaskXcpImpl(uid_=logXcp_.uniqueID, xm_=logXcp_.message, ec_=logXcp_.errorCode, tb_=logXcp_.traceback, cst_=logXcp_.callstack, bDieXcp_=True, clone_=None)
                    res = XTaskException(_impl)
                else:
                    res = _DieException(enclLogXcp_=logXcp_)
        else:
            if eevCurTask_ == _EErrorImpact.eImpactByLogException:
                if _bRaiseXtXcp:
                    _impl = _XTaskXcpImpl(uid_=logXcp_.uniqueID, xm_=logXcp_.message, ec_=logXcp_.errorCode, tb_=logXcp_.traceback, cst_=logXcp_.callstack, bDieXcp_=False, clone_=None)
                    res = XTaskException(_impl)
                else:
                    res = logXcp_

        _bOK =         isinstance(res, XTaskException)
        _bOK = _bOK or isinstance(res, _LogException)
        _bOK = _bOK or isinstance(res, _DieException)
        _bOK = _bOK or isinstance(res._enclosedLogException, _LogException)
        if not _bOK:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00461)
            return None
        return res
