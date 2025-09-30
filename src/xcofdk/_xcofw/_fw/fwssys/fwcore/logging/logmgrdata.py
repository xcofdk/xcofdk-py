# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : logmgrdata.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

import threading

from collections import Counter as _PyCounter
from threading   import RLock   as _PyRLock

from _fw.fwssys.fwcore.logging                import vlogif
from _fw.fwssys.fwcore.logging.logdefines     import _ELogType
from _fw.fwssys.fwcore.logging.logdefines     import _LogUniqueID
from _fw.fwssys.fwcore.logging.logdefines     import _LogConfig
from _fw.fwssys.fwcore.logging.logentry       import _LogEntry
from _fw.fwssys.fwerrh.logs.logexception      import _LogException
from _fw.fwssys.fwcore.base.timeutil          import _StopWatch
from _fw.fwssys.fwcore.config.fwstartupconfig import _FwStartupConfig
from _fw.fwssys.fwcore.logrd.logrecord        import _EColorCode
from _fw.fwssys.fwcore.logrd.logrdagent       import _LogRDAgent
from _fw.fwssys.fwcore.types.aobject          import _AbsSlotsObject
from _fw.fwssys.fwcore.types.commontypes      import _CommonDefines
from _fw.fwssys.fwerrh.fwerrorcodes           import _EFwErrorCode

class _LogMgrData(_AbsSlotsObject):
    __slots__ = [ '__f' , '__s' , '__lc', '__c', '__p', '__l' , '__nl', '__al', '__sw' , '__m' , '__me' , '__cfg' , '__rda']

    def __init__(self, startupCfg_ : _FwStartupConfig):
        super().__init__()

        self.__c   = _PyCounter()
        self.__f   = None
        self.__l   = _PyRLock()
        self.__m   = 0
        self.__p   = None
        self.__s   = None
        self.__al  = []
        self.__lc  = None
        self.__me  = 0
        self.__nl  = 0
        self.__sw  = _StopWatch()
        self.__cfg = None
        self.__rda = _LogRDAgent._GetInstance()

        for _n, _m in _ELogType.__members__.items():
            self.__c[_m._absValue] = 0
        self.__SetupConfig(startupCfg_)

    @property
    def isValid(self):
        return self.__cfg is not None

    @property
    def isCompactOutputFormatEnabled(self):
        return _LogEntry._IsCompactOutputFormatEnabled()

    @property
    def counter(self) -> _PyCounter:
        return self.__c

    @property
    def subSeqXcp(self):
        return self.__s

    @subSeqXcp.setter
    def subSeqXcp(self, val_):
        self.__s = val_

    @property
    def firstFatalLog(self):
        return self.__f

    @firstFatalLog.setter
    def firstFatalLog(self, val_):
        self.__f = val_

    @property
    def lastCreatedLogEntry(self):
        return self.__lc

    @lastCreatedLogEntry.setter
    def lastCreatedLogEntry(self, val_):
        self.__lc = val_

    @property
    def logConf(self) -> _LogConfig:
        return self.__cfg

    @property
    def maxLogTime(self) -> int:
        return self.__m

    @property
    def maxErrorLogTime(self) -> int:
        return self.__me

    @property
    def pendingTaskID(self):
        return self.__p

    def SetPendingTaskID(self, pendingTaskID_):
        self.__p = pendingTaskID_

    def UnlockApi(self, bFullUnlock_ =False):
        self.LockApi(bLock_=False, bFullUnlock_=bFullUnlock_)

    def LockApi(self, bLock_ : bool =True, bFullUnlock_ =False):
        if (self.__l is None) or (self.__nl is None):
            return
        elif (not bLock_) and bFullUnlock_:
            while self.__nl > 0:
                self.LockApi(False)
            return

        _ctn = None
        if bLock_:
            self.__l.acquire()
            self.__nl += 1
        else:
            self.__nl -= 1
            self.__l.release()

    def AddLogEntry(self, le_ : _LogEntry, doAddOnly_ =False):
        if (le_ is None) or ( not le_.isValid):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00466)
        elif not le_.logType.isNonError:
            if not (le_.isFreeLog or doAddOnly_):
                le_._Adapt(uniqueID_=_LogUniqueID._GetNextUniqueID())
            self.__al.append(le_)

    def LMPrint(self, buf_, color_ : _EColorCode =None):
        if self.__rda is None:
            return

        if isinstance(buf_, _LogException):
            buf_ = buf_._enclosedFatalEntry
        if not isinstance(buf_, _LogEntry):
            buf_ = _CommonDefines._STR_EMPTY if buf_ is None else str(buf_)
        else:
            buf_ = buf_._logRecord
        self.__rda._PutLR(buf_, color_=color_)

    def UpdateMaxLogTime(self, bErrorLogTime_ =False, bRestart_ =False) -> int:
        if self.__sw is None:
            return None

        if bRestart_:
            self.__sw.Restart()

        self.__sw.Stop()
        res = self.__sw.timeDelta.totalMS

        if bErrorLogTime_:
            if res > self.__me:
                self.__me = res
            else:
                res = None
        else:
            if res > self.__m:
                self.__m = res
            else:
                res = None
        return res

    def _ToString(self):
        return None

    def _CleanUp(self):
        if self.__al is None:
            return

        if self.__lc is not None:
            self.__lc.CleanUp()
        if self.__f is not None:
            self.__f.CleanUp()
        if self.__s is not None:
            self.__s.CleanUp()
        if self.__cfg is not None:
            self.__cfg.CleanUp()
        self.__c.clear()
        self.UnlockApi(bFullUnlock_=True)

        if self.__sw is not None:
            self.__sw.CleanUp()

        for _ii in range(len(self.__al)-1, -1, -1):
            _ee = self.__al[_ii]
            self.__al[_ii] = None
            _ee._ForceCleanUp()
        self.__al.clear()

        self.__c   = None
        self.__f   = None
        self.__l   = None
        self.__m   = None
        self.__p   = None
        self.__s   = None
        self.__al  = None
        self.__lc  = None
        self.__me  = None
        self.__nl  = None
        self.__sw  = None
        self.__cfg = None
        self.__rda = None

    def _ClearLogHistory(self):
        if self.__al is None:
            return

        if self.__lc is not None:
            self.__lc.CleanUp()
            self.__lc = None
        if self.__f is not None:
            self.__f.CleanUp()
            self.__f = None
        if self.__s is not None:
            self.__s.CleanUp()
            self.__s = None
        self.__c.clear()

        _NUM_LOGS = len(self.__al)
        if _NUM_LOGS > 0:
            for _ii in range(len(self.__al)-1, -1, -1):
                _ee = self.__al[_ii]
                self.__al[_ii] = None
                _ee.CleanUp()
            self.__al.clear()
        self.__p = None

    def __SetupConfig(self, startupCfg_ : _FwStartupConfig):
        _logCfg = _LogConfig()

        _bMisMatch = False
        _bMisMatch = _bMisMatch or (startupCfg_._isReleaseModeEnabled       != _logCfg.isReleaseModeEnabled)
        _bMisMatch = _bMisMatch or (startupCfg_._isFwDieModeEnabled         != _logCfg.isDieModeEnabled)
        _bMisMatch = _bMisMatch or (startupCfg_._isFwExceptionModeEnabled   != _logCfg.isExceptionModeEnabled)
        _bMisMatch = _bMisMatch or (startupCfg_._fwLogLevel                 != _logCfg.logLevel)
        _bMisMatch = _bMisMatch or (startupCfg_._isUserDieModeEnabled       != _logCfg.isUserDieModeEnabled)
        _bMisMatch = _bMisMatch or (startupCfg_._isUserExceptionModeEnabled != _logCfg.isExceptionModeEnabled)
        _bMisMatch = _bMisMatch or (startupCfg_._userLogLevel               != _logCfg.userLogLevel)

        if _bMisMatch:
            self.CleanUp()
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00462)
            return False

        _bMatch = True
        _bMatch = _bMatch and vlogif._IsFwDieModeEnabled()       == _logCfg.isDieModeEnabled
        _bMatch = _bMatch and vlogif._IsReleaseModeEnabled()     == _logCfg.isReleaseModeEnabled
        _bMatch = _bMatch and vlogif._IsFwExceptionModeEnabled() == _logCfg.isExceptionModeEnabled

        if not _bMatch:
            _logCfg.CleanUp()
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00465)
            return False
        self.__cfg = _logCfg
        return True
