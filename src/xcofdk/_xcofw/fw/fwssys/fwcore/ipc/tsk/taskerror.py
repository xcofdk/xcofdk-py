# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : taskerror.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from xcofdk._xcofw.fw.fwssys.fwcore.logging            import logif
from xcofdk._xcofw.fw.fwssys.fwcore.logging            import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logdefines import _EErrorImpact
from xcofdk._xcofw.fw.fwssys.fwcore.logging.errorentry import _ErrorEntry
from xcofdk._xcofw.fw.fwssys.fwcore.base.callableif    import _CallableIF
from xcofdk._xcofw.fw.fwssys.fwcore.base.util          import _Util
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject      import _AbstractSlotsObject
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes  import _CommonDefines

from xcofdk._xcofw.fw.fwssys.fwcore.ipc.sync.mutex    import _Mutex
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskbadge import _TaskBadge

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine



class _TaskError(_AbstractSlotsObject):

    __slots__ = [ '__mtxApi' , '__tbadge' , '__cbif', '__curEE' ]

    def __init__(self, mtxApi_ : _Mutex,  taskBadge_ : _TaskBadge, taskErrorCallableIF_ : _CallableIF =None):

        super().__init__()
        self.__cbif   = None
        self.__curEE  = None
        self.__tbadge = None
        self.__mtxApi = None

        _bError = False
        if not _Util.IsInstance(mtxApi_, _Mutex, bThrowx_=True):
            _bError = True
        elif not _Util.IsInstance(taskBadge_, _TaskBadge, bThrowx_=True):
            _bError = True
        elif taskErrorCallableIF_ is None:
            if taskBadge_.hasForeignErrorListnerTaskRight:
                _bError = True
                vlogif._LogOEC(True, -1452)
        elif not (isinstance(taskErrorCallableIF_, _CallableIF) and taskErrorCallableIF_.isValid):
            _bError = True
            vlogif._LogOEC(True, -1453)

        if _bError:
            self.CleanUp()
        else:
            self.__cbif     = taskErrorCallableIF_
            self.__tbadge   = taskBadge_
            self.__mtxApi = mtxApi_

    @property
    def isErrorFree(self):
        if self.__mtxApi is None:
            return True
        with self.__mtxApi:
            self.__CheckResetCurError()
            return self.__curEE is None


    @property
    def isUserError(self):
        if self.__mtxApi is None:
            return False
        with self.__mtxApi:
            self.__CheckResetCurError()
            if self.__curEE is not None:
                res =         self.__curEE.hasErrorImpact
                res = res and self.__curEE.isUserError
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
        if self.__mtxApi is None:
            return False
        with self.__mtxApi:
            return False if self.isErrorFree else self.__curEE.isAnonymousError

    @property
    def isDistinctiveError(self):
        if self.__mtxApi is None:
            return False
        with self.__mtxApi:
            return False if self.isErrorFree else self.__curEE.isDistinctiveError

    @property
    def taskBadge(self):
        return self.__tbadge

    @property
    def taskID(self):
        return None if self.__tbadge is None else self.__tbadge.taskID

    @property
    def taskName(self):
        return None if self.__tbadge is None else self.__tbadge.taskName

    @property
    def taskUniqueName(self):
        return None if self.__tbadge is None else self.__tbadge.taskUniqueName

    @property
    def currentErrorUniqueID(self):
        if self.__mtxApi is None:
            return None
        with self.__mtxApi:
            return None if self.isErrorFree else self.__curEE.uniqueID

    @property
    def currentErrorShortMessage(self):
        if self.__mtxApi is None:
            return None
        with self.__mtxApi:
            return None if self.isErrorFree else self.__curEE.shortMessage

    @property
    def currentErrorCode(self):
        if self.__mtxApi is None:
            return None
        with self.__mtxApi:
            self.__CheckResetCurError()
            return None if self.__curEE is None else self.__curEE.errorCode

    def ClearError(self) -> bool:
        if self.__mtxApi is None:
            return False
        with self.__mtxApi:
            return self.__ClearError(False)

    @property
    def _apiMutex(self) -> _Mutex:
        return self.__mtxApi

    @property
    def _currentErrorEntry(self) -> _ErrorEntry:
        if self.__mtxApi is None:
            return None
        with self.__mtxApi:
            self.__CheckResetCurError()
            return self.__curEE

    def _ToString(self, *args_, **kwargs_):
        if self.__mtxApi is None:
            return None
        with self.__mtxApi:
            if self.isErrorFree:
                res = str(None)
            else:
                res = self.__curEE.ToString()
            res = self.__msgPrefix + res
            return res

    def _CleanUp(self):
        if self.__tbadge is None:
            pass
        else:
            if self.__cbif is not None:
                self.__cbif.CleanUp()
                self.__cbif = None

            self.__ClearError(True)
            self.__tbadge = None
            self.__mtxApi = None

    def _OnErrorNotification(self, errEntry_ : _ErrorEntry):


        _bNOT_CONSUMED = False

        if self.__mtxApi is None:
            return _bNOT_CONSUMED
        with self.__mtxApi:
            if not self._PreCheckNotification(errEntry_, bOwnError_=True):
                return _bNOT_CONSUMED

            if self.isUserError:
                _tmp = self.__curEE
                self.__curEE = None
                _tmp._UpdateErrorImpact(_EErrorImpact.eNoImpactByLogTypePrecedence)

            self.__curEE = errEntry_
            return self._CallOnTaskErrorIF(errEntry_)

    def _PreCheckNotification(self, errEntry_ : _ErrorEntry, bOwnError_ =True):
        _bPASSED = True
        if not isinstance(errEntry_, _ErrorEntry):
            vlogif._LogOEC(True, -1454)
            return not _bPASSED
        elif errEntry_.hasNoErrorImpact:
            vlogif._LogOEC(True, -1455)
            return not _bPASSED

        if bOwnError_:
            if errEntry_.IsForeignTaskError(self.taskID):
                vlogif._LogOEC(True, -1456)
                return not _bPASSED
            if self.isFatalError:
                vlogif._LogOEC(True, -1457)
                return not _bPASSED
        else:
            if errEntry_.IsMyTaskError(self.taskID):
                vlogif._LogOEC(True, -1458)
                return not _bPASSED
            if not self.taskBadge.hasForeignErrorListnerTaskRight:
                vlogif._LogOEC(True, -1459)
                return not _bPASSED
        return _bPASSED

    def _CallOnTaskErrorIF(self, errEntry_: _ErrorEntry, bForeignError_ =False):

        if self.__cbif is None:
            bN = False
        elif not self.taskBadge.hasFwTaskRight:
            bN = True
        else:
            bN = True

        _midPart = _CommonDefines._STR_EMPTY

        if not bN:
            res = True
        else:
            try:
                res = self.__cbif(errEntry_)
            except BaseException as xcp:
                res = False
        return res

    @property
    def __msgPrefix(self):
        res = _FwTDbEngine.GetText(_EFwTextID.eTaskError_MsgPrefix)
        _tuname = self.taskUniqueName
        if _tuname is None:
            pass
        else:
            res = res.rstrip() + _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_010).format(_tuname) + _CommonDefines._CHAR_SIGN_SPACE
        return res

    def __IsFatalError(self, *, bCheckNoImpactDueToFrcLinkage_ =False):
        if self.__mtxApi is None:
            return False
        with self.__mtxApi:
            self.__CheckResetCurError()
            if self.__curEE is not None:
                _errImp = self.__curEE.eErrorImpact
                res = _errImp.hasImpact
                if not res:
                    if bCheckNoImpactDueToFrcLinkage_:
                        res = _errImp.hasNoImpactDueToFrcLinkage
                if res:
                    res = self.__curEE.isFatalError
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
                if not self.taskBadge.hasUnitTestTaskRight:
                    _bCleanUpCurEE = False
                    _wngMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_TaskError_TextID_001)
                    logif._LogWarning(_wngMsg.format(self.taskID, self.currentErrorUniqueID))

            elif self.isFatalError:
                if self.__curEE.eErrorImpact.isCausedByDieMode:
                    if bOnCleanup_:
                        _bCleanUpCurEE = False
                    else:

                        if self.taskBadge.hasUnitTestTaskRight:
                            _bCleanUpCurEE = True
                        else:
                            _bCleanUpCurEE = False
                            _wngMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_TaskError_TextID_001)
                            logif._LogWarning(_wngMsg.format(self.taskID, self.currentErrorUniqueID))
            if _bCleanUpCurEE:
                self.__curEE.CleanUp()
                self.__curEE = None
            elif bOnCleanup_:
                self.__curEE = None
            res = _bCleanUpCurEE
        return res

    def __CheckResetCurError(self):
        if self.__curEE is None:
            pass
        else:
            _errImp = self.__curEE.eErrorImpact

            if _errImp is None:
                self.__curEE = None
            elif _errImp.hasNoImpact:
                if not _errImp.hasNoImpactDueToFrcLinkage:
                    self.__curEE = None


class _TaskErrorExtended(_TaskError):

    def __init__(self, mtxApi_ : _Mutex, taskBadge_ : _TaskBadge, taskErrorCallableIF_ : _CallableIF =None):
        super().__init__(mtxApi_, taskBadge_, taskErrorCallableIF_=taskErrorCallableIF_)

    def _OnErrorNotification(self, errEntry_ : _ErrorEntry):


        _bNOT_CONSUMED = False
        _bConsumed     = False

        if not isinstance(errEntry_, _ErrorEntry):
            return _bNOT_CONSUMED
        if self._apiMutex is None:
            return _bNOT_CONSUMED

        if errEntry_.IsMyTaskError(self.taskID):
            bC = _TaskError._OnErrorNotification(self, errEntry_)
        elif not self._PreCheckNotification(errEntry_, bOwnError_=False):
            bC = _bNOT_CONSUMED
        else:
            bC = self._CallOnTaskErrorIF(errEntry_, bForeignError_=True)
        return bC
