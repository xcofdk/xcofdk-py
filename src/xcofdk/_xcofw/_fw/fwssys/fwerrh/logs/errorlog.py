# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : errorlog.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

import traceback

from _fw.fwssys.fwcore.logging            import vlogif
from _fw.fwssys.fwcore.logging.logdefines import _ELogType
from _fw.fwssys.fwcore.logging.logdefines import _EErrorImpact
from _fw.fwssys.fwcore.logging.logdefines import _LogErrorCode
from _fw.fwssys.fwcore.logging.logentry   import _LogEntry
from _fw.fwssys.fwcore.types.aobject      import _AbsSlotsObject
from _fw.fwssys.fwcore.types.commontypes  import _CommonDefines
from _fw.fwssys.fwerrh.fwerrorcodes       import _EFwErrorCode

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _ErrorLog(_LogEntry):
    __slots__ = [ '__c' , '__ei' , '__m' , '__i' , '__bC' ]

    def __init__(self, errLogType_ : _ELogType, errCode_ : int =None
                , taskName_ : str =None, taskID_ : int =None
                , shortMsg_ : str =None, longMsg_ : str =None
                , cloneby_ =None, doSkipSetup_ =False, xrn_ =None):
        self.__c  = None
        self.__i  = None
        self.__m  = None
        self.__bC = None
        self.__ei = None

        if doSkipSetup_:
            super().__init__(None, doSkipSetup_=True)
            return

        _bOK = False
        _bOK, errCode_ = _ErrorLog.__EvaluateParams(errLogType_, errCode_, taskName_, taskID_)
        if not _bOK:
            super().__init__(None, doSkipSetup_=True)
            return

        super().__init__( errLogType_, taskName_=taskName_, taskID_=taskID_
                        , shortMsg_=shortMsg_, longMsg_=longMsg_, cloneby_=cloneby_, xrn_=xrn_)
        if self.isInvalid:
            errCode_ = None
        elif cloneby_ is not None:
            if not isinstance(cloneby_, _ErrorLog):
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00422)
            elif cloneby_.isInvalid:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00423)
            else:
                errCode_ = cloneby_.errorCode

        if errCode_ is not None:
            self.__c = errCode_

    @property
    def isAnonymousError(self):
        return _LogErrorCode.IsAnonymousErrorCode(self.__c)

    @property
    def isDistinctiveError(self):
        return not _LogErrorCode.IsAnonymousErrorCode(self.__c)

    @property
    def hasErrorImpact(self) -> bool:
        _errImp = None if self.isInvalid else self.errorImpact
        return False if _errImp is None else _errImp.hasImpact

    @property
    def hasNoErrorImpact(self) -> bool:
        _errImp = None if self.isInvalid else self.errorImpact
        return True if _errImp is None else _errImp.hasNoImpact

    @property
    def hasNoImpactDueToFrcLinkage(self):
        _errImp = None if self.isInvalid else self.errorImpact
        return False if _errImp is None else _errImp.hasNoImpactDueToFrcLinkage

    @property
    def errorImpact(self) -> _EErrorImpact:
        _m  = self._LockInstance()
        res = self.__ei
        if _m is not None:
            _m.Give()
        return res

    @property
    def errorCode(self) -> int:
        return self.__c

    @property
    def _enclosedByLogException(self):
        return None

    @property
    def _isClone(self):
        return self.isValid and self.__bC

    @property
    def _isShared(self):
        return False if self.isInvalid else self.__m is not None

    @property
    def _isPendingResolution(self):
        if self.isInvalid:
            return False

        _m  = self._LockInstance()
        res = (self.__ei is not None) and self.__ei.hasImpact
        if _m is not None:
            _m.Give()
        return res

    @property
    def _errorCode2String(self):
        res = self.__c
        if res is not None:
            if _LogErrorCode.IsAnonymousErrorCode(res):
                res = None
            else:
                res = str(res)
        return res

    @property
    def _taskInstance(self):
        return self.__i

    def _CleanUp(self):
        super()._CleanUp()
        self.__c  = None
        self.__i  = None
        self.__m  = None
        self.__bC = None
        self.__ei = None

    def _ForceCleanUp(self):
        self.CleanUp()

    def _SetTaskInstance(self, tskInst_, bAdaptTaskInfo_ =False):
        if not self.isInvalid:
            self.__i = tskInst_
            if bAdaptTaskInfo_ and (tskInst_ is not None) and tskInst_.isValid:
                self._Adapt(taskName_=tskInst_.dtaskName, taskID_=tskInst_.dtaskUID)

    def _SetErrorImpact(self, eErrImpact_ : _EErrorImpact, mtxErrImpact_ =None):
        if not isinstance(eErrImpact_, _EErrorImpact):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00424)
            return

        if self.errorImpact is not None:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00425)
            return
        if (mtxErrImpact_ is not None) and (self.__m is not None):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00426)
            return

        self.__m  = mtxErrImpact_
        self.__ei = eErrImpact_

    def _UpdateErrorImpact(self, eErrImpact_ : _EErrorImpact):
        if not isinstance(eErrImpact_, _EErrorImpact):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00427)
            return
        if self.__ei is None:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00428)
            return

        _m = self._LockInstance()

        if eErrImpact_.hasNoImpactDueToFrcLinkage:
            if self.__ei.hasFatalErrorImpactDueToXCmd:
                eErrImpact_ = _EErrorImpact.eNoImpactByFrcLinkageDueToXCmd

        _tmp      = self.__ei
        self.__ei = eErrImpact_
        if _m is not None:
            _m.Give()

    def _Clone(self) -> _LogEntry:
        if self.isInvalid:
            res = None
        else:
            res = _ErrorLog(self.logType, cloneby_=self)
            if res.isInvalid:
                res.CleanUp()
                res = None
            else:
                res._MakeClone(self.errorImpact, self._taskInstance)
        return res

    def _MakeClone(self, eErrorImpact_ : _EErrorImpact, tskInst_):
        if self.isValid:
            self.__i  = tskInst_
            self.__bC = True
            self.__ei = None if eErrorImpact_ is None else _EErrorImpact(eErrorImpact_.value)

    def _LockInstance(self):
        res = self.__m
        if self.isInvalid or (res is None):
            res = None
        else:
            res.Take()
        return res

    @staticmethod
    def __EvaluateParams(errLogType_, errCode_, taskName_, taskID_):
        res = isinstance(errLogType_, _ELogType)
        res = res and errLogType_.isError
        if not res:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00429)
        else:
            if errCode_ is None:
                errCode_ = _LogErrorCode.GetAnonymousErrorCode()
            else:
                _bEcOK = isinstance(errCode_, int)
                _bEcOK = _bEcOK and (errCode_ != _LogErrorCode.GetInvalidErrorCode())
                if not _bEcOK:
                    if not errLogType_.isFwApiLogType:
                        vlogif._LogOEC(True, _EFwErrorCode.VFE_00430)
                    else:
                        vlogif._XLogErrorEC(_EFwErrorCode.UE_00260, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_ErrorLog_TID_001).format(type(errCode_).__name__, str(errCode_)))
                    errCode_ = None
        return res, errCode_

class _FatalLog(_ErrorLog):
    __slots__  = [ '__bx', '__cs' , '__lx' , '__bP' ]

    def __init__(self, logType_ : _ELogType, errCode_ : int =None
                , taskName_ : str =None, taskID_ : int =None
                , shortMsg_ : str =None, longMsg_ : str =None
                , xcoBaseXcp_ =None, cloneby_ =None, xrn_ =None):
        self.__bP = None
        self.__bx = None
        self.__cs = None
        self.__lx = None

        if cloneby_ is not None:
            if not (isinstance(cloneby_, _FatalLog) and cloneby_.isValid):
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00431)
                super().__init__(None, doSkipSetup_=True)
                return
        else:
            if not isinstance(logType_, _ELogType):
                logType_ = _ELogType.FTL
            if logType_._absValue == _ELogType.FTL_SOX.value:
                if xcoBaseXcp_ is None:
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00432)
                    super().__init__(None, doSkipSetup_=True)
                    return

        super().__init__( logType_, errCode_=errCode_, taskName_=taskName_, taskID_=taskID_
                        , shortMsg_=shortMsg_, longMsg_=longMsg_, cloneby_=cloneby_, xrn_=xrn_)
        if self.isInvalid:
            pass
        elif cloneby_ is not None:
            self.__bP = True

            if self.__bx is not None:
                self.__bx.CleanUp()
                self.__bx = None

            self.__cs = cloneby_.__cs

            if cloneby_.__bx is not None:
                self.__bx = cloneby_.__bx.Clone()
        else:
            self.__bP = True

            self.__cs = _FatalLog.__GetFCS(logType_)
            if self.logType._absValue == _ELogType.FTL_SOX.value:
                self.__bx = xcoBaseXcp_

    @property
    def callstack(self) -> str:
        return self.__cs

    @property
    def _isCleanupPermitted(self):
        return self.__bP == True

    @property
    def _enclosedByLogException(self):
        return self.__lx

    @property
    def _causedBySystemException(self) -> Exception:
        return self.__bx

    @property
    def _nestedLogException(self):
        return None if self.__lx is None else self.__lx._nestedLogException

    def _IsEqual(self, rhs_):
        res = isinstance(rhs_, _FatalLog)
        if not res:
            pass
        elif id(self) == id(rhs_):
            pass
        elif not self.uniqueID is None and self.uniqueID == rhs_.uniqueID:
            pass
        elif not _ErrorLog.__eq__(self, rhs_):
            res = False
        else:
            res  = self.__bx == rhs_.__bx
            if res:
                if self.__lx is None:
                    res = rhs_.__lx is None
        return res

    def _CleanUp(self):
        if self.isInvalid:
            return

        _uid    = self.uniqueID
        _bClone = self.isClone

        if not self._isCleanupPermitted:
            _AbsSlotsObject.ResetCleanupFlag(self)
        else:
            _errImp   = self.errorImpact
            _bFlagSet = (not self._isShared) or (_errImp == _EErrorImpact.eNoImpactBySharedCleanup)
            if not _bFlagSet:
                _AbsSlotsObject.ResetCleanupFlag(self)
                if _errImp is not None:
                    if _errImp != _EErrorImpact.eNoImpactBySharedCleanup:
                        self._UpdateErrorImpact(_EErrorImpact.eNoImpactBySharedCleanup)
            else:
                super()._CleanUp()
                if self.__bx is not None:
                    self.__bx.CleanUp()
                self.__bP = None
                self.__bx = None
                self.__cs = None
                self.__lx = None

    def _SetLogException(self, logXcp_):
        self.__lx = logXcp_

    def _SetCleanUpPermission(self, bCleanupPermitted_ : bool):
        if isinstance(bCleanupPermitted_, bool):
            self.__bP = bCleanupPermitted_

    def _ForceCleanUp(self):
        if self.isInvalid:
            return

        _m = self._LockInstance()

        _errImp = self.errorImpact
        if _errImp is not None:
            if _errImp != _EErrorImpact.eNoImpactBySharedCleanup:
                self._UpdateErrorImpact(_EErrorImpact.eNoImpactBySharedCleanup)
        self.__bP = True
        self.CleanUp()

        if _m is not None:
            _m.Give()

    def _Clone(self, calledByLogException_ =False) -> _ErrorLog:
        if self.isInvalid:
            res = None
        else:
            _logXcp = self.__lx
            if (_logXcp is not None) and _logXcp._enclosedFatalEntry is None:
                _logXcp = None

            if (_logXcp is not None) and not calledByLogException_:
                res = _logXcp.Clone()
                if res is not None:
                    res = res._enclosedFatalEntry
            else:
                res = _FatalLog(self.logType, cloneby_=self)
                if res.isInvalid:
                    res.CleanUp()
                    res = None
                else:
                    res._MakeClone(self.errorImpact, self._taskInstance)
        return res

    @staticmethod
    def __GetFCS(logType_ : _ELogType):
        _numSkip = 9
        if logType_.isFwApiLogType:
            _numSkip += 2

        _cs     = traceback.format_list(traceback.extract_stack())
        _csSize = len(_cs)
        if _csSize > _numSkip:
            _csSize -= _numSkip
            _cs = _cs[0:_csSize]

        _cs = [_ee for _ee in _cs if len(_ee) > 0 and not _ee.isspace()]
        res = _CommonDefines._STR_EMPTY.join(_cs)
        return res

