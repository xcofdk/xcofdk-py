# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : logifimplhelper.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from collections import Counter as _Counter
from threading   import RLock as _PyRLock

from xcofdk._xcofw.fw.fwssys.fwcore.base.timeutil          import _StopWatch
from xcofdk._xcofw.fw.fwssys.fwcore.config.fwstartupconfig import _FwStartupConfig
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject          import _AbstractSlotsObject
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes      import SyncPrint

from xcofdk._xcofw.fw.fwssys.fwcore.logging              import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logdefines   import _ELogType
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logdefines   import _ELogLevel
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logdefines   import _LogUniqueID
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logconfig    import _LoggingConfig
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logconfig    import _LoggingUserConfig
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logentry     import _LogEntry
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logexception import _LogException



class _LogIFImplHelper(_AbstractSlotsObject):

    __slots__ = [
         '__firstFatalLog'  ,  '__subSeqXcp'      ,  '__lastCreatedLE'
      ,  '__counter'        ,  '__pendingTaskID'  ,  '__apiLck'
      ,  '__numLocks'       ,  '__lstLogs'        ,  '__stopWatchLT'
      ,  '__maxLT'          ,  '__maxErrLT'       ,  '__logConf'
      ,  '__fwSCfg'
    ]

    __bStoreErrorEntriesOnly = True


    def __init__(self, startupCfg_ : _FwStartupConfig):
        super().__init__()

        self.__maxLT         = 0
        self.__apiLck        = _PyRLock()
        self.__logConf       = None
        self.__lstLogs       = []
        self.__maxErrLT      = 0
        self.__numLocks      = 0
        self.__fwSCfg        = startupCfg_
        self.__subSeqXcp     = None
        self.__stopWatchLT   = _StopWatch()
        self.__lastCreatedLE = None
        self.__firstFatalLog = None
        self.__pendingTaskID = None

        self.__counter = _Counter()
        for name, member in _ELogType.__members__.items():
            self.__counter[member._absoluteValue] = 0

        _bMisMatch = False
        _bMisMatch = _bMisMatch or (startupCfg_._isUserDieModeEnabled       != _LoggingUserConfig._userDieMode)
        _bMisMatch = _bMisMatch or (startupCfg_._isUserExceptionModeEnabled != _LoggingUserConfig._userExceptionMode)
        _bMisMatch = _bMisMatch or (startupCfg_._userLogLevel               != _LoggingUserConfig._eUserLogLevel)

        if _bMisMatch:
            self.CleanUp()
            vlogif._LogOEC(True, -1076)
            return

        self.__fwSCfg = startupCfg_
        _LogEntry._EnableCompactOutputFormat()

    @property
    def isValid(self):
        return self.__fwSCfg is not None

    @property
    def isCompactOutputFormatEnabled(self):
        return _LogEntry._IsCompactOutputFormatEnabled()

    @property
    def counter(self) -> _Counter:
        return self.__counter

    @property
    def subSeqXcp(self):
        return self.__subSeqXcp

    @subSeqXcp.setter
    def subSeqXcp(self, val_):
        self.__subSeqXcp = val_

    @property
    def firstFatalLog(self):
        return self.__firstFatalLog

    @firstFatalLog.setter
    def firstFatalLog(self, val_):
        self.__firstFatalLog = val_

    @property
    def lastCreatedLogEntry(self):
        return self.__lastCreatedLE

    @lastCreatedLogEntry.setter
    def lastCreatedLogEntry(self, val_):
        self.__lastCreatedLE = val_

    @property
    def logConf(self) -> _LoggingConfig:
        if self.__logConf is not None:
            if self.__logConf.eLogLevel is None:
                self.__logConf = _LoggingConfig.GetInstance(bCreate_=False)
        return self.__logConf

    @property
    def fwStartupConfig(self) -> _FwStartupConfig:
        return self.__fwSCfg

    @property
    def maxLogTime(self) -> int:
        return self.__maxLT

    @property
    def maxErrorLogTime(self) -> int:
        return self.__maxErrLT

    @property
    def pendingTaskID(self):
        return self.__pendingTaskID

    def SetPendingTaskID(self, pendingTaskID_):
        self.__pendingTaskID = pendingTaskID_

    def SetupConfig(self, bRelMode_ : bool =None, bDieMode_: bool = None, bXcpMode_: bool = None
                   , eLogLevel_: _ELogLevel = None, bOutputRedirection_: bool = None):
        if self.__logConf is not None:
            vlogif._LogOEC(True, -1077)
            return
        if (eLogLevel_ is not None) and not isinstance(eLogLevel_, _ELogLevel):
            vlogif._LogOEC(True, -1078)
            return

        _logCfgInst = _LoggingConfig.GetInstance(bCreate_=False)
        if _logCfgInst is not None:
            _logCfgInst.CleanUp()
        self.__logConf = _LoggingConfig( bRelMode_=bRelMode_, bDieMode_=bDieMode_, bXcpMode_=bXcpMode_
                                      , eLogLevel_=eLogLevel_, bOutputRedirection_=bOutputRedirection_, bInitByEnvConfig_=True)
        _bLogConfOK = True        and vlogif._IsFwDieModeEnabled()       == self.__logConf.dieMode
        _bLogConfOK = _bLogConfOK and vlogif._IsReleaseModeEnabled()     == self.__logConf.releaseMode
        _bLogConfOK = _bLogConfOK and vlogif._IsFwExceptionModeEnabled() == self.__logConf.exceptionMode

        if not _bLogConfOK:
            msg = 'logConf=(dm:{}, xm:{}, rm:{}) vs. vlogif=(dm:{}, xm:{}, rm:{})'.format(
                str(self.__logConf.dieMode), str(self.__logConf.exceptionMode), str(self.__logConf.releaseMode)
                , str(vlogif._IsFwDieModeEnabled()), str(vlogif._IsFwExceptionModeEnabled()), str(vlogif._IsReleaseModeEnabled()))
            msg = '[LC][LogIF] Mismatch of logging config: {})'.format(msg)
            self.__logConf.CleanUp()
            self.__logConf = None
            vlogif._LogOEC(True, -1079)

    def UnlockApi(self, bFullUnlock_ =False):
        self.LockApi(bLock_=False, bFullUnlock_=bFullUnlock_)

    def LockApi(self, bLock_ : bool =True, bFullUnlock_ =False):
        if (self.__apiLck is None) or (self.__numLocks is None):
            return
        elif (not bLock_) and bFullUnlock_:
            while self.__numLocks > 0:
                self.LockApi(False)
            return

        if bLock_:
            self.__apiLck.acquire()
            self.__numLocks += 1
        else:
            self.__numLocks -= 1
            self.__apiLck.release()

    def AddLogEntry(self, le_ : _LogEntry, doAddOnly_ =False):

        if (le_ is None) or ( not le_.isValid):
            vlogif._LogOEC(True, -1080)
        else:
            bIA = le_.eLogType.isNonError and _LogIFImplHelper.__bStoreErrorEntriesOnly
            if not bIA:
                if le_.isFreeLog or doAddOnly_:
                    pass
                else:
                    le_._Adapt(uniqueID_=_LogUniqueID._GetNextUniqueID())
                self.__lstLogs.append(le_)

    def Flush(self, buf_, endLine_=None):
        if (self.logConf is not None) and self.logConf.outputRedirection:
            vlogif._LogOEC(True, -1081)
            return

        _le = buf_
        if isinstance(buf_, _LogException):
            _le = buf_._enclosedFatalEntry
        elif not isinstance(buf_, _LogEntry):
            _le = None
            buf_ = str(buf_)

        bAC = (_le is not None) and _le.eLogType.isNonError and _LogIFImplHelper.__bStoreErrorEntriesOnly

        if _le is None:
            pass
        else:
            _le._Adapt(bFlushed_=True)
            if endLine_ is None:
                if _le.eLogType == _ELogType.FREE:
                    endLine_ = ''

        SyncPrint.Print(buf_, endLine_=endLine_)
        if bAC:
            _le.CleanUp()

    def UpdateMaxLogTime(self, bErrorLogTime_ =False, bRestart_ =False) -> int:
        if self.__stopWatchLT is None:
            return None

        if bRestart_:
            self.__stopWatchLT.Restart()

        self.__stopWatchLT.Stop()
        res = self.__stopWatchLT.timeDelta.totalMS

        if bErrorLogTime_:
            if res > self.__maxErrLT:
                self.__maxErrLT = res
            else:
                res = None
        else:
            if res > self.__maxLT:
                self.__maxLT = res
            else:
                res = None
        return res

    @staticmethod
    def _IsStoreErrorEntriesOnlyEnabled() -> bool:
        return _LogIFImplHelper.__bStoreErrorEntriesOnly

    @staticmethod
    def _EnableStoreErrorEntriesOnly():
        _LogIFImplHelper.__bStoreErrorEntriesOnly = True

    @staticmethod
    def _DisableStoreErrorEntriesOnly():
        _LogIFImplHelper.__bStoreErrorEntriesOnly = False

    def _ToString(self, *args_, **kwargs_):
        return None

    def _CleanUp(self):

        if self.__lstLogs is None:
            return

        if self.__lastCreatedLE is not None:
            self.__lastCreatedLE.CleanUp()
            self.__lastCreatedLE = None
        if self.__firstFatalLog is not None:
            self.__firstFatalLog.CleanUp()
            self.__firstFatalLog = None
        if self.__subSeqXcp is not None:
            self.__subSeqXcp.CleanUp()
            self.__subSeqXcp = None

        if self.__logConf is not None:
            self.__logConf = None

        self.__counter.clear()
        self.__counter = None

        self.UnlockApi(bFullUnlock_=True)

        if self.__stopWatchLT is not None:
            self.__stopWatchLT.CleanUp()
            self.__stopWatchLT = None

        self.__maxLT         = None
        self.__apiLck        = None
        self.__fwSCfg        = None
        self.__maxErrLT      = None
        self.__numLocks      = None
        self.__pendingTaskID = None

        for _ii in range(len(self.__lstLogs)-1, -1, -1):
            _ee = self.__lstLogs[_ii]
            self.__lstLogs[_ii] = None
            _ee._ForceCleanUp()
        self.__lstLogs.clear()
        self.__lstLogs = None

    def _ClearLogHistory(self):

        if self.__lstLogs is None:
            return

        if self.__lastCreatedLE is not None:
            self.__lastCreatedLE.CleanUp()
            self.__lastCreatedLE = None
        if self.__firstFatalLog is not None:
            self.__firstFatalLog.CleanUp()
            self.__firstFatalLog = None
        if self.__subSeqXcp is not None:
            self.__subSeqXcp.CleanUp()
            self.__subSeqXcp = None

        self.__counter.clear()

        _NUM_LOGS = len(self.__lstLogs)
        if _NUM_LOGS > 0:
            for _ii in range(len(self.__lstLogs)-1, -1, -1):
                _ee = self.__lstLogs[_ii]
                self.__lstLogs[_ii] = None
                _ee.CleanUp()
            self.__lstLogs.clear()

        self.__pendingTaskID = None
