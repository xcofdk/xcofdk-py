# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwtaskerror.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from typing import Union

from _fw.fwssys.fwcore.logging            import logif
from _fw.fwssys.fwcore.logging            import vlogif
from _fw.fwssys.fwcore.logging.logdefines import _EErrorImpact
from _fw.fwssys.fwcore.base.fwcallable    import _FwCallable
from _fw.fwssys.fwcore.base.util          import _Util
from _fw.fwssys.fwcore.ipc.sync.mutex     import _Mutex
from _fw.fwssys.fwcore.ipc.tsk.taskbadge  import _TaskBadge
from _fw.fwssys.fwcore.types.aobject      import _AbsSlotsObject
from _fw.fwssys.fwcore.types.commontypes  import _CommonDefines
from _fw.fwssys.fwerrh.fwerrorcodes       import _EFwErrorCode
from _fw.fwssys.fwerrh.logs.errorlog      import _ErrorLog
from _fw.fwssys.fwerrh.logs.errorlog      import _FatalLog

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _FwTaskError(_AbsSlotsObject):
    __slots__ = [ '__ma' , '__tb' , '__cbi', '__cee' ]

    def __init__(self, ma_ : _Mutex,  taskBadge_ : _TaskBadge, teCBIF_ : _FwCallable =None):
        super().__init__()
        self.__ma  = None
        self.__tb  = None
        self.__cbi = None
        self.__cee = None

        _bError = False
        if not _Util.IsInstance(ma_, _Mutex, bThrowx_=True):
            _bError = True
        elif not _Util.IsInstance(taskBadge_, _TaskBadge, bThrowx_=True):
            _bError = True
        elif teCBIF_ is None:
            if taskBadge_.hasForeignErrorListnerTaskRight:
                _bError = True
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00255)
        elif not (isinstance(teCBIF_, _FwCallable) and teCBIF_.isValid):
            _bError = True
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00256)

        if _bError:
            self.CleanUp()
        else:
            self.__ma = ma_
            self.__tb  = taskBadge_
            self.__cbi = teCBIF_

    @property
    def isErrorFree(self):
        if self.__ma is None:
            return True
        with self.__ma:
            self.__CheckResetCurError()
            return self.__cee is None

    @property
    def isUserError(self):
        if self.__ma is None:
            return False
        with self.__ma:
            self.__CheckResetCurError()
            if self.__cee is not None:
                res =         self.__cee.hasErrorImpact
                res = res and self.__cee.isUserError
            else:
                res = False
            return res

    @property
    def isFatalError(self):
        return self.__IsFatalError(bCheckNoImpactDueToFrcLinkage_=False)

    @property
    def isNoImpactFatalErrorDueToFrcLinkage(self):
        return self.__IsFatalError(bCheckNoImpactDueToFrcLinkage_=True)

    @property
    def isAnonymousError(self):
        if self.__ma is None:
            return False
        with self.__ma:
            return False if self.isErrorFree else self.__cee.isAnonymousError

    @property
    def isDistinctiveError(self):
        if self.__ma is None:
            return False
        with self.__ma:
            return False if self.isErrorFree else self.__cee.isDistinctiveError

    @property
    def taskBadge(self):
        return self.__tb

    @property
    def dtaskUID(self):
        return None if self.__tb is None else self.__tb.dtaskUID

    @property
    def dtaskName(self):
        return None if self.__tb is None else self.__tb.dtaskName

    @property
    def currentErrorUniqueID(self):
        if self.__ma is None:
            return None
        with self.__ma:
            return None if self.isErrorFree else self.__cee.uniqueID

    @property
    def currentErrorShortMessage(self):
        if self.__ma is None:
            return None
        with self.__ma:
            return None if self.isErrorFree else self.__cee.shortMessage

    @property
    def currentErrorCode(self):
        if self.__ma is None:
            return None
        with self.__ma:
            self.__CheckResetCurError()
            return None if self.__cee is None else self.__cee.errorCode

    def ClearError(self) -> bool:
        if self.__ma is None:
            return False
        with self.__ma:
            return self.__ClearError(False)

    @property
    def _apiMutex(self) -> _Mutex:
        return self.__ma

    @property
    def _currentErrorEntry(self) -> Union[_ErrorLog, _FatalLog]:
        if self.__ma is None:
            return None
        with self.__ma:
            self.__CheckResetCurError()
            return self.__cee

    def _ToString(self):
        if self.__ma is None:
            return None
        with self.__ma:
            if self.isErrorFree:
                res = _CommonDefines._STR_NONE
            else:
                res = self.__cee.ToString()
            res = self.__msgPrefix + res
            return res

    def _CleanUp(self):
        if self.__tb is not None:
            if self.__cbi is not None:
                self.__cbi.CleanUp()
                self.__cbi = None

            self.__ClearError(True)
            self.__ma = None
            self.__tb = None

    def _OnErrorNotification(self, errLog_ : _ErrorLog):
        res = False

        if self.__ma is None:
            return res
        with self.__ma:
            if not self._PreCheckNotification(errLog_, bOwnError_=True):
                return res

            if self.isUserError:
                _tmp = self.__cee
                self.__cee = None
                _tmp._UpdateErrorImpact(_EErrorImpact.eNoImpactByLogTypePrecedence)

            self.__cee = errLog_
            return self._CallOnTaskErrorIF(errLog_)

    def _PreCheckNotification(self, errLog_ : _ErrorLog, bOwnError_ =True):
        _bPASSED = True
        if not isinstance(errLog_, _ErrorLog):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00257)
            return not _bPASSED
        elif errLog_.hasNoErrorImpact:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00258)
            return not _bPASSED

        if bOwnError_:
            if errLog_.IsForeignTaskError(self.dtaskUID):
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00259)
                return not _bPASSED
            if self.isFatalError:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00260)
                return not _bPASSED
        else:
            if errLog_.IsMyTaskError(self.dtaskUID):
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00261)
                return not _bPASSED
            if not self.taskBadge.hasForeignErrorListnerTaskRight:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00262)
                return not _bPASSED
        return _bPASSED

    def _CallOnTaskErrorIF(self, errLog_: _ErrorLog, bForeignError_ =False):
        _bN = self.__cbi is not None
        if not _bN:
            res = True
        else:
            try:
                res = self.__cbi(errLog_)
            except BaseException as _xcp:
                res = False
        return res

    @property
    def __msgPrefix(self):
        res = _FwTDbEngine.GetText(_EFwTextID.eFwTaskError_MsgPrefix)
        _tname = self.dtaskName
        if _tname is not None:
            res = res.rstrip() + _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_010).format(_tname) + _CommonDefines._CHAR_SIGN_SPACE
        return res

    def __IsFatalError(self, *, bCheckNoImpactDueToFrcLinkage_ =False):
        if self.__ma is None:
            return False
        with self.__ma:
            self.__CheckResetCurError()
            if self.__cee is not None:
                _errImp = self.__cee.errorImpact
                res = _errImp.hasImpact
                if not res:
                    if bCheckNoImpactDueToFrcLinkage_:
                        res = _errImp.hasNoImpactDueToFrcLinkage
                if res:
                    res = self.__cee.isFatalError
            else:
                res = False
            return res

    def __ClearError(self, bOnCleanup_ : bool) -> bool:
        if self.isErrorFree:
            res = True
        else:
            self.__CheckResetCurError()

            _bCleanUpCurEE = True

            if self.isNoImpactFatalErrorDueToFrcLinkage:
                _bCleanUpCurEE = False
                _wngMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwTaskError_TID_001)
                logif._LogWarning(_wngMsg.format(self.dtaskUID, self.currentErrorUniqueID))

            elif self.isFatalError:
                if self.__cee.errorImpact.isCausedByDieMode:
                    if bOnCleanup_:
                        _bCleanUpCurEE = False
                    else:
                        _bCleanUpCurEE = False
                        _wngMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwTaskError_TID_001)
                        logif._LogWarning(_wngMsg.format(self.dtaskUID, self.currentErrorUniqueID))
            if _bCleanUpCurEE:
                self.__cee.CleanUp()
                self.__cee = None
            elif bOnCleanup_:
                self.__cee = None
            res = _bCleanUpCurEE
        return res

    def __CheckResetCurError(self):
        if self.__cee is not None:
            _errImp = self.__cee.errorImpact

            if _errImp is None:
                self.__cee = None
            elif _errImp.hasNoImpact:
                if not _errImp.hasNoImpactDueToFrcLinkage:
                    self.__cee = None

class _TaskErrorExtended(_FwTaskError):
    __slots__ = []

    def __init__(self, ma_ : _Mutex, taskBadge_ : _TaskBadge, teCBIF_ : _FwCallable =None):
        super().__init__(ma_, taskBadge_, teCBIF_=teCBIF_)

    def _OnErrorNotification(self, errLog_ : _ErrorLog):
        res = False

        if not isinstance(errLog_, _ErrorLog):
            return res
        if self._apiMutex is None:
            return res

        if errLog_.IsMyTaskError(self.dtaskUID):
            res = _FwTaskError._OnErrorNotification(self, errLog_)
        elif not self._PreCheckNotification(errLog_, bOwnError_=False):
            pass
        else:
            res = self._CallOnTaskErrorIF(errLog_, bForeignError_=True)
        return res
