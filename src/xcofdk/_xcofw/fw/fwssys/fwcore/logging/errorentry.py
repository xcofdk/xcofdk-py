# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : errorentry.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from xcofdk._xcofw.fw.fwssys.fwcore.logging            import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logdefines import _ELogType
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logdefines import _EErrorImpact
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logdefines import _LogErrorCode
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logentry   import _LogEntry


class _ErrorEntry(_LogEntry):

    __slots__ = [ '__errCode' , '__eErrImpact' , '__mtxErrImpact' , '__tskInst' , '__bClone' ]

    def __init__(self, eErrorLogType_ : _ELogType, errCode_ : int =None
                , taskName_ : str =None, taskID_ : int =None
                , shortMsg_ : str =None, longMsg_ : str =None, inheritanceDepth_ =1
                , callstackLevelOffset_ =None, cloneby_ =None, doSkipSetup_ =False, euRNum_ =None):

        self.__bClone       = None
        self.__errCode      = None
        self.__tskInst      = None
        self.__eErrImpact   = None
        self.__mtxErrImpact = None

        if doSkipSetup_:
            super().__init__(None, doSkipSetup_=True)
            return

        _bOK = False
        _bOK, errCode_ = _ErrorEntry.__EvaluateParams(eErrorLogType_, errCode_, taskName_, taskID_)
        if not _bOK:
            super().__init__(None, doSkipSetup_=True)
            return

        super().__init__(eErrorLogType_, taskName_=taskName_, taskID_=taskID_
            , shortMsg_=shortMsg_, longMsg_=longMsg_, inheritanceDepth_=inheritanceDepth_
            , callstackLevelOffset_=callstackLevelOffset_, cloneby_=cloneby_, euRNum_=euRNum_)
        if self.isInvalid:
            errCode_ = None
        elif cloneby_ is not None:
            if not isinstance(cloneby_, _ErrorEntry):
                vlogif._LogOEC(True, -1084)
            elif cloneby_.isInvalid:
                vlogif._LogOEC(True, -1085)
            else:
                errCode_ = cloneby_.errorCode

        if errCode_ is not None:
            self.__errCode = errCode_

    def __eq__(self, other_):
        res = isinstance(other_, _ErrorEntry)
        if not res:
            pass
        elif id(self) == id(other_):
            pass
        elif (self.uniqueID is not None) and (self.uniqueID == other_.uniqueID):
            pass
        elif not _LogEntry.__eq__(self, other_):
            res = False
        else:
            res = self.__errCode == other_.__errCode
        return res

    @property
    def isAnonymousError(self):
        return _LogErrorCode.IsAnonymousErrorCode(self.__errCode)

    @property
    def isDistinctiveError(self):
        return not _LogErrorCode.IsAnonymousErrorCode(self.__errCode)

    @property
    def hasErrorImpact(self) -> bool:
        _errImp = None if self.isInvalid else self.eErrorImpact
        return False if _errImp is None else _errImp.hasImpact

    @property
    def hasNoErrorImpact(self) -> bool:
        _errImp = None if self.isInvalid else self.eErrorImpact
        return True if _errImp is None else _errImp.hasNoImpact

    @property
    def hasNoImpactDueToFrcLinkage(self):
        _errImp = None if self.isInvalid else self.eErrorImpact
        return False if _errImp is None else _errImp.hasNoImpactDueToFrcLinkage

    @property
    def eErrorImpact(self) -> _EErrorImpact:
        _myMtx = self._LockInstance()
        res = self.__eErrImpact
        if _myMtx is not None:
            _myMtx.Give()
        return res

    @property
    def errorCode(self) -> int:
        return self.__errCode

    @property
    def _enclosedByLogException(self):
        return None

    @property
    def _isClone(self):
        return self.isValid and self.__bClone

    @property
    def _isShared(self):
        return False if self.isInvalid else self.__mtxErrImpact is not None

    @property
    def _isPendingResolution(self):
        if self.isInvalid:
            return False

        _myMtx = self._LockInstance()
        res = (self.__eErrImpact is not None) and self.__eErrImpact.hasImpact
        if _myMtx is not None:
            _myMtx.Give()
        return res

    @property
    def _errorCode2String(self):
        res = self.__errCode
        if res is not None:
            if _LogErrorCode.IsAnonymousErrorCode(res):
                res = None
            else:
                res = str(res)
        return res

    @property
    def _taskInstance(self):
        return self.__tskInst

    def _CleanUp(self):
        super()._CleanUp()
        self.__bClone       = None
        self.__errCode      = None
        self.__tskInst      = None
        self.__eErrImpact   = None
        self.__mtxErrImpact = None

    def _ForceCleanUp(self):
        self.CleanUp()

    def _SetTaskInstance(self, tskInst_):
        if self.isInvalid:
            pass
        else:
            self.__tskInst = tskInst_

    def _SetErrorImpact(self, eErrImpact_ : _EErrorImpact, mtxErrImpact_ =None):
        if not isinstance(eErrImpact_, _EErrorImpact):
            vlogif._LogOEC(True, -1086)
            return

        _curErrImp = self.eErrorImpact
        _curErrImpStr = str(None) if _curErrImp is None else _curErrImp.compactName
        if _curErrImp is not None:
            vlogif._LogOEC(True, -1087)
            return
        if (mtxErrImpact_ is not None) and (self.__mtxErrImpact is not None):
            vlogif._LogOEC(True, -1088)
            return

        self.__eErrImpact   = eErrImpact_
        self.__mtxErrImpact = mtxErrImpact_

    def _UpdateErrorImpact(self, eErrImpact_ : _EErrorImpact):
        if not isinstance(eErrImpact_, _EErrorImpact):
            vlogif._LogOEC(True, -1089)
            return
        if self.__eErrImpact is None:
            vlogif._LogOEC(True, -1090)
            return

        _myMtx = self._LockInstance()

        if eErrImpact_.hasNoImpactDueToFrcLinkage:
            if self.__eErrImpact.isFatalErrorImpactDueToExecutionApiReturn:
                eErrImpact_ = _EErrorImpact.eNoImpactByFrcLinkageDueToExecApiReturn

        _tmp              = self.__eErrImpact
        self.__eErrImpact = eErrImpact_

        if _myMtx is not None:
            _myMtx.Give()

    def _Clone(self) -> _LogEntry:
        if self.isInvalid:
            res = None
        else:
            res = _ErrorEntry(self.eLogType, cloneby_=self)
            if res.isInvalid:
                res.CleanUp()
                res = None
            else:
                res._MakeClone(self.eErrorImpact, self._taskInstance)
        return res

    def _MakeClone(self, eErrorImpact_ : _EErrorImpact, tskInst_):
        if self.isValid:
            self.__bClone     = True
            self.__tskInst    = tskInst_
            self.__eErrImpact = None if eErrorImpact_ is None else _EErrorImpact(eErrorImpact_.value)

    def _LockInstance(self):
        res = self.__mtxErrImpact
        if self.isInvalid or (res is None):
            res = None
        else:
            res.Take()
        return res

    @staticmethod
    def __EvaluateParams(eErrorLogType_, errCode_, taskName_, taskID_):
        res = isinstance(eErrorLogType_, _ELogType)
        res = res and eErrorLogType_.isError
        if not res:
            vlogif._LogOEC(True, -1091)
        else:
            if errCode_ is None:
                errCode_ = _LogErrorCode.GetAnonymousErrorCode()
            else:
                res = isinstance(errCode_, int)
                res = res and (errCode_ != _LogErrorCode.GetInvalidErrorCode())
                if not res:
                    _midPart = str(errCode_)
                    if not isinstance(errCode_, int):
                        _midPart = '\'{}\''.format(errCode_)
                    vlogif._LogOEC(True, -1092)
                    errCode_ = None
        return res, errCode_
