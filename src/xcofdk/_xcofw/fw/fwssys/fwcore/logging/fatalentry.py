# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fatalentry.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

import traceback

from xcofdk._xcofw.fw.fwssys.fwcore.logging            import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logdefines import _EErrorImpact
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logdefines import _ELogType
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logdefines import _LogUtil
from xcofdk._xcofw.fw.fwssys.fwcore.logging.errorentry import _ErrorEntry
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject      import _AbstractSlotsObject
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes  import _CommonDefines

from xcofdk._xcofw.fw.fwssys.fwerrh.fwerrorcodes import _EFwErrorCode

class _FatalEntry(_ErrorEntry):

    __slots__  = [ '__xcoBaseXcp', '__callstack' , '__logXcp' , '__bCleanupPermitted' ]

    def __init__(self, eXcpLogType_ : _ELogType, errCode_ : int =None
                , taskName_ : str =None, taskID_ : int =None
                , shortMsg_ : str =None, longMsg_ : str =None
                , inheritanceDepth_ =2, callstackLevelOffset_ =None
                , xcoBaseXcp_ =None, cloneby_ =None, euRNum_ =None):

        self.__logXcp            = None
        self.__callstack         = None
        self.__xcoBaseXcp        = None
        self.__bCleanupPermitted = None

        if cloneby_ is not None:
            if not (isinstance(cloneby_, _FatalEntry) and cloneby_.isValid):
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00431)
                super().__init__(None, doSkipSetup_=True)
                return
        elif eXcpLogType_._absoluteValue == _ELogType.FTL_SYS_OP_XCP.value:
            if xcoBaseXcp_ is None:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00432)
                super().__init__(None, doSkipSetup_=True)
                return

        super().__init__( eXcpLogType_, errCode_=errCode_, taskName_=taskName_, taskID_=taskID_
                        , shortMsg_=shortMsg_, longMsg_=longMsg_, inheritanceDepth_=inheritanceDepth_
                        , callstackLevelOffset_=callstackLevelOffset_, cloneby_=cloneby_, euRNum_=euRNum_)
        if self.isInvalid:
            pass
        elif cloneby_ is not None:
            self.__bCleanupPermitted = True

            if self.__xcoBaseXcp is not None:
                self.__xcoBaseXcp.CleanUp()
                self.__xcoBaseXcp = None

            self.__callstack = cloneby_.__callstack

            if cloneby_.__xcoBaseXcp is not None:
                self.__xcoBaseXcp = cloneby_.__xcoBaseXcp.Clone()
        else:
            self.__bCleanupPermitted = True

            self.__callstack = _FatalEntry.__GetFormattedCallStack(callstackLevelOffset_=callstackLevelOffset_)
            if self.eLogType._absoluteValue == _ELogType.FTL_SYS_OP_XCP.value:
                self.__xcoBaseXcp = xcoBaseXcp_

    def __eq__(self, rhs_):
        res = isinstance(rhs_, _FatalEntry)
        if not res:
            pass
        elif self.__logXcp is None:
            res = self._IsEqual(rhs_)
        else:
            res = self.__logXcp == rhs_.__logXcp
        return res

    @property
    def callstack(self):
        return self.__callstack

    @property
    def _isCleanupPermitted(self):
        return self.__bCleanupPermitted == True

    @property
    def _enclosedByLogException(self):
        return self.__logXcp

    @property
    def _causedBySystemException(self) -> Exception:
        return self.__xcoBaseXcp

    @property
    def _nestedLogException(self):
        return None if self.__logXcp is None else self.__logXcp._nestedLogException

    def _IsEqual(self, rhs_):
        res = isinstance(rhs_, _FatalEntry)
        if not res:
            pass
        elif id(self) == id(rhs_):
            pass
        elif not self.uniqueID is None and self.uniqueID == rhs_.uniqueID:
            pass
        elif not _ErrorEntry.__eq__(self, rhs_):
            res = False
        else:
            res  = self.__xcoBaseXcp == rhs_.__xcoBaseXcp
            if res:
                if self.__logXcp is None:
                    res = rhs_.__logXcp is None
        return res

    def _CleanUp(self):
        if self.isInvalid:
            return

        _uid    = self.uniqueID
        _bClone = self.isClone

        if not self._isCleanupPermitted:
            _AbstractSlotsObject.ResetCleanupFlag(self)

        else:
            _errImp   = self.eErrorImpact
            _bFlagSet = (not self._isShared) or (_errImp == _EErrorImpact.eNoImpactBySharedCleanup)

            if not _bFlagSet:
                _AbstractSlotsObject.ResetCleanupFlag(self)
                if _errImp is not None:
                    if _errImp != _EErrorImpact.eNoImpactBySharedCleanup:
                        self._UpdateErrorImpact(_EErrorImpact.eNoImpactBySharedCleanup)
            else:
                super()._CleanUp()
                if self.__xcoBaseXcp is not None:
                    self.__xcoBaseXcp.CleanUp()
                self.__logXcp            = None
                self.__callstack         = None
                self.__xcoBaseXcp        = None
                self.__bCleanupPermitted = None

    def _SetLogException(self, logXcp_):
        self.__logXcp = logXcp_

    def _SetCleanUpPermission(self, bCleanupPermitted_ : bool):
        if isinstance(bCleanupPermitted_, bool):
            self.__bCleanupPermitted = bCleanupPermitted_

    def _ForceCleanUp(self):
        if self.isInvalid:
            return

        _myMtx = self._LockInstance()

        _errImp = self.eErrorImpact
        if _errImp is not None:
            if _errImp != _EErrorImpact.eNoImpactBySharedCleanup:
                self._UpdateErrorImpact(_EErrorImpact.eNoImpactBySharedCleanup)
        self.__bCleanupPermitted = True
        self.CleanUp()

        if _myMtx is not None:
            _myMtx.Give()

    def _Clone(self, calledByLogException_ =False) -> _ErrorEntry:
        if self.isInvalid:
            res = None
        else:
            _logXcp = self.__logXcp
            if (_logXcp is not None) and _logXcp._enclosedFatalEntry is None:
                _logXcp = None

            if (_logXcp is not None) and not calledByLogException_:
                res = _logXcp.Clone()
                if res is not None:
                    res = res._enclosedFatalEntry
            else:
                res = _FatalEntry(self.eLogType, cloneby_=self)
                if res.isInvalid:
                    res.CleanUp()
                    res = None
                else:
                    res._MakeClone(self.eErrorImpact, self._taskInstance)
        return res

    @staticmethod
    def __GetFormattedCallStack(header_ =None, callstackLevelOffset_ =None):
        _NUM_CALLSTACK_SKIP_LINES = _LogUtil.GetCallstackLevel() + 1

        _clines = traceback.format_list(traceback.extract_stack())

        if callstackLevelOffset_ is None:
            callstackLevelOffset_ = _LogUtil.GetCallstackLevelOffset()

        numSkipTrailingLines_ = _NUM_CALLSTACK_SKIP_LINES + callstackLevelOffset_
        if numSkipTrailingLines_ > 0:
            _numLines = len(_clines)
            if _numLines > numSkipTrailingLines_:
                _numLines -= numSkipTrailingLines_
                _clines = _clines[0:_numLines]

        _clines = [_ee for _ee in _clines if len(_ee) > 0 and not _ee.isspace()]
        res = _CommonDefines._STR_EMPTY.join(_clines)
        if header_ is not None:
            res = header_ + _CommonDefines._CHAR_SIGN_NEWLINE + res
        return res
