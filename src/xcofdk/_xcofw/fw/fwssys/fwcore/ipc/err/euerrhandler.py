# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : euerrhandler.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from enum import unique

from xcofdk._xcofw.fw.fwssys.fwcore.logging import vlogif

from xcofdk._xcofw.fw.fwssys.fwcore.logging              import logif
from xcofdk._xcofw.fw.fwssys.fwcore.logging.errorentry   import _ErrorEntry
from xcofdk._xcofw.fw.fwssys.fwcore.logging.fatalentry   import _FatalEntry
from xcofdk._xcofw.fw.fwssys.fwcore.logging.xcoexception import _XcoExceptionRoot
from xcofdk._xcofw.fw.fwssys.fwcore.logging.xcoexception import _XcoException
from xcofdk._xcofw.fw.fwssys.fwcore.base.util            import _Util
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcdefines         import _LcConfig
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcproxy           import _LcProxy
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcproxyclient     import _LcProxyClient
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes    import _FwIntEnum
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes    import _ETernaryOpResult
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes    import _CommonDefines

from xcofdk._xcofw.fw.fwssys.fwcore.ipc.sync.mutex     import _Mutex
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskbadge  import _TaskBadge
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskerror  import _TaskError
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.err.euerrorbin import _EuErrorBin
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.err.euerrorbin import _EuFEBinTable

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine


@unique
class _EErrorHandlerCallbackID(_FwIntEnum):

    eAbortTaskDueToUnexpectedCall      = 3041
    eProcessFwMainDieError             = 3052
    eProcessFwMainFatalError           = 3053
    eProcessObservedForeignFatalErrors = 3061
    eAbortTaskDueToDieError            = 3071
    eAbortTaskDueToFatalError          = 3072

    @property
    def isFwMainSpecificCallbackID(self):
        return (self.value > _EErrorHandlerCallbackID.eAbortTaskDueToUnexpectedCall) and \
               (self.value < _EErrorHandlerCallbackID.eAbortTaskDueToDieError)

    @property
    def isAbortTaskDueToUnexpectedCall(self):
        return self == _EErrorHandlerCallbackID.eAbortTaskDueToUnexpectedCall

    @property
    def isProcessFwMainDieError(self):
        return self == _EErrorHandlerCallbackID.eProcessFwMainDieError

    @property
    def isProcessFwMainFatalError(self):
        return self == _EErrorHandlerCallbackID.eProcessFwMainFatalError

    @property
    def isProcessObservedForeignFatalErrors(self):
        return self == _EErrorHandlerCallbackID.eProcessObservedForeignFatalErrors

    @property
    def isAbortTaskDueToDieError(self):
        return self == _EErrorHandlerCallbackID.eAbortTaskDueToDieError

    @property
    def isAbortTaskDueToFatalError(self):
        return self == _EErrorHandlerCallbackID.eAbortTaskDueToFatalError


class _EuErrorHandler(_LcProxyClient):


    __slots__  = [ '__mtxApiEH' , '__mtxData' , '__eeBin' , '__feeBin' ]
    __bIGONRE_FOREGIN_USER_ERRORS       = True
    __APPLY_ERROR_BIN_REASSURANCE_CHECK = False

    def __init__(self):
        self.__eeBin    = None
        self.__feeBin   = None
        self.__mtxData  = None
        self.__mtxApiEH = None
        super().__init__()

        _EuErrorHandler.__APPLY_ERROR_BIN_REASSURANCE_CHECK = False

    def _ProcErrorHandlerCallback( self
                                 , eCallbackID_           : _EErrorHandlerCallbackID
                                 , curFatalError_         : _FatalEntry               =None
                                 , lstForeignFatalErrors_ : list                     =None) -> _ETernaryOpResult:
        vlogif._LogOEC(True, -1460)
        return _ETernaryOpResult.Abort()

    @property
    def _isForeignErrorListener(self):
        return None if self.__mtxApiEH is None else self.__myTaskBadge.hasForeignErrorListnerTaskRight


    @property
    def _curOwnError(self):
        if self.__mtxApiEH is None: return None
        with self.__mtxApiEH:
            res = None if self.__eeBin is None else self.__eeBin.currentError
            if res is not None:
                if res.hasNoImpactDueToFrcLinkage:
                    res = None
            return res

    def _AddEuError(self, euEEntry_ : _ErrorEntry) -> bool:

        try:
            if self.__mtxApiEH is None:
                _opr = _EuErrorBin._EErrBinOpResult.eErrBinOpResultInvalidObject
            elif not isinstance(euEEntry_, _ErrorEntry):
                _opr = _EuErrorBin._EErrBinOpResult.eErrBinOpResultImplError
            elif euEEntry_.isInvalid:
                _opr = _EuErrorBin._EErrBinOpResult.eErrBinOpResultSuccess
            elif euEEntry_.hasNoErrorImpact:
                _opr    = _EuErrorBin._EErrBinOpResult.eErrBinOpResultSuccess
            else:
                _bFErr = euEEntry_.IsForeignTaskError(self.__myTaskBadge.taskID)

                if _bFErr:
                    with self.__mtxData:
                        _opr = self.__AddForeignErrorEntry(euEEntry_, forceOperation_=False)
                else:
                    with self.__mtxApiEH:
                        _opr = self.__SetOwnErrorEntry(euEEntry_, forceOperation_=False)
            res = _opr.isErrBinOpResultSuccess
            if not res:
                if not _opr.isErrBinOpResultDuplicateInsertionError:
                    pass
                else:
                    res = True

        except KeyboardInterrupt as xcp:
            res = False
        except BaseException as xcp:
            res = False
        return res

    def _ProcEuErrors(self, bCheckForFatalErrorsOnly_ =False) -> _ETernaryOpResult:

        if self.__mtxApiEH is None:
            return _ETernaryOpResult.Abort()

        with (self.__mtxApiEH):
            _myLcPxy    = self.__myLcProxy
            _myTskBadge = self.__myTaskBadge

            _bAborting       = self.isAborting
            _bInvalidPxy     = _myLcPxy is None
            _bInvalidBadge   = _myTskBadge is None
            _bSomeLcFailure  = _myLcPxy.hasLcAnyFailureState
            _bPxyUnavailable = not _myLcPxy.isLcProxyAvailable
            _bUnexpectedCall = _bInvalidBadge or _bInvalidPxy or _bAborting or _bPxyUnavailable

            if _bUnexpectedCall or _bSomeLcFailure:
                if _bUnexpectedCall:
                    _callbackID = _EErrorHandlerCallbackID.eAbortTaskDueToUnexpectedCall
                    vlogif._LogOEC(True, -1461)

                    _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_EuErrorHandler_TextID_001).format(self.__myUniqueName)
                    _myFE = logif._CreateLogImplError(_errMsg)
                    res = self._ProcErrorHandlerCallback(_callbackID, curFatalError_=_myFE)
                else:
                    res = _ETernaryOpResult.MapExecutionState2TernaryOpResult(self)
                return res

            _bAllEmpty       = None
            _bEmptyEeBin     = None
            _pendingFErrList = None
            _bAllEmpty, _bEmptyEeBin, _pendingFErrList = self.__GetEuErrorBinStatus()

            if _bAllEmpty:
                return _ETernaryOpResult.MapExecutionState2TernaryOpResult(self)

            if not (_bEmptyEeBin or bCheckForFatalErrorsOnly_):
                _curOwnErr = self.__eeBin.currentError

                if _curOwnErr.eErrorImpact.isCausedByDieMode:

                    if _myTskBadge.isFwMain:
                        _callbackID = _EErrorHandlerCallbackID.eProcessFwMainDieError
                        return self._ProcErrorHandlerCallback(_callbackID, curFatalError_=_curOwnErr)

                    _callbackID = _EErrorHandlerCallbackID.eAbortTaskDueToDieError
                    return self._ProcErrorHandlerCallback(_callbackID, curFatalError_=_curOwnErr)


                if _curOwnErr.eErrorImpact.isCausedByFatalError:
                    if _myTskBadge.isFwMain:
                        _callbackID = _EErrorHandlerCallbackID.eProcessFwMainFatalError
                        return self._ProcErrorHandlerCallback(_callbackID, curFatalError_=_curOwnErr)

                    _callbackID = _EErrorHandlerCallbackID.eAbortTaskDueToFatalError
                    return self._ProcErrorHandlerCallback(_callbackID, curFatalError_=_curOwnErr)

                self.__eeBin.ClearCurError()

                return _ETernaryOpResult.MapExecutionState2TernaryOpResult(self)



            if not _myTskBadge.hasForeignErrorListnerTaskRight:
                vlogif._LogOEC(True, -1462)
                return _ETernaryOpResult.Abort()
            elif self._GetStoredFFEsList() is None:
                vlogif._LogOEC(True, -1463)
                return _ETernaryOpResult.Abort()

            _bProcFErrList = (_pendingFErrList is not None) or (len(self._GetStoredFFEsList()) > 0)

            if not _bProcFErrList:
                res = _ETernaryOpResult.MapExecutionState2TernaryOpResult(self)
            else:
                res = self.__ProcForeignErrors(_pendingFErrList)

            return res

    def _ProcUnhandledXcp(self, xcp_: _XcoExceptionRoot):

        if self.__mtxApiEH is None:
            return False
        if not isinstance(xcp_, _XcoExceptionRoot):
            vlogif._LogOEC(True, -1464)
            return False

        _myXcoXcp = None if xcp_.isXTaskException else xcp_
        if (_myXcoXcp is not None) and not isinstance(_myXcoXcp, _XcoException):
            _myXcoXcp = None

        if not (xcp_.isXTaskException or (_myXcoXcp is not None)):
            vlogif._LogOEC(True, -1465)
            return False
        elif (_myXcoXcp is not None) and not (_myXcoXcp.isXcoBaseException or _myXcoXcp.isLogException or _myXcoXcp.isDieException):
            vlogif._LogOEC(True, -1466)
            return False

        if xcp_.isXTaskException:
            _myFE = logif._GetCurrentXTaskErrorEntry(xcp_.uniqueID)
            if _myFE is None:
                vlogif._LogOEC(True, -1467)
                return False
            _myXcpUID   = _myFE.uniqueID
            _myXcpTName = _myFE.taskName
            _myXcpMsg   = _myFE.shortMessage

        else:
            _myXcpUID   = _myXcoXcp.uniqueID
            _myXcpTName = _myXcoXcp.taskName
            _myXcpMsg   = _myXcoXcp.shortMessage

        if xcp_.isXTaskException or not _myXcoXcp.isXcoBaseException:
            _curOwnErr = self._curOwnError

            if (_myXcoXcp is not None) and _myXcoXcp.taskID != self.__myTaskBadge.taskID:
                vlogif._LogOEC(True, -1468)
                return False
            if _curOwnErr is None:
                vlogif._LogOEC(True, -1469)
                return False
            if _curOwnErr.uniqueID == _myXcpUID:
                return True
            if _curOwnErr.isFatalError:
                return True

            vlogif._LogOEC(True, -1470)
            return False

        logif._LogUnhandledXcoBaseXcp(_myXcoXcp)
        return True

    def _SetUpEuEH(self, mtxApi_ : _Mutex):
        if self.__mtxApiEH is not None:
            vlogif._LogOEC(True, -1471)
        if not _Util.IsInstance(mtxApi_, _Mutex, bThrowx_=True):
            return

        _rn = getattr(self, _FwTDbEngine.GetText(_EFwTextID.ePreDefinedMethod_EuRNumber), None)
        _tb = getattr(self, _FwTDbEngine.GetText(_EFwTextID.ePreDefinedMethod_TaskBadge), None)
        _te = getattr(self, _FwTDbEngine.GetText(_EFwTextID.ePreDefinedMethod_TaskError), None)
        if _tb is None:
            vlogif._LogOEC(True, -1472)
            return
        if _te is None:
            vlogif._LogOEC(True, -1473)
            return
        if _rn is None:
            vlogif._LogOEC(True, -1474)
            return

        _feeBin    = None
        _mtxDataMe = None

        if _tb.hasForeignErrorListnerTaskRight:
            _mtxDataMe = _Mutex()
            _feeBin = _EuFEBinTable(_tb.taskID, _mtxDataMe)
            if _feeBin.ownerTaskID is None:
                _feeBin.CleanUp()
                _mtxDataMe.CleanUp()
                return

        self.__feeBin   = _feeBin
        self.__mtxData  = _mtxDataMe
        self.__mtxApiEH = mtxApi_

    def _ToString(self, *args_, **kwargs_):
        res = None
        if self.__mtxApiEH is None:
            pass
        else:
            with self.__mtxApiEH:
                _midPart = _CommonDefines._CHAR_SIGN_DASH if self.__eeBin is None else self.__eeBin.ToString()
                res      = _FwTDbEngine.GetText(_EFwTextID.eEuErrorHandler_ToString_01).format(self.__myTaskBadge.taskUniqueName, _midPart)
                if self.__feeBin is not None:
                    res += _FwTDbEngine.GetText(_EFwTextID.eEuErrorHandler_ToString_02).format(self.__feeBin.ToString())
        return res

    def _CleanUp(self):
        super()._CleanUp()

        if self.__mtxApiEH is not None:
            if self.__mtxData is not None:
                self.__mtxData.CleanUp()
                self.__mtxData = None
            if self.__feeBin is not None:
                self.__feeBin.CleanUp()
                self.__feeBin = None
            if self.__eeBin is not None:
                self.__eeBin.CleanUp()
                self.__eeBin = None
            self.__mtxApiEH = None

    @property
    def __myTaskBadge(self) -> _TaskBadge:
        return None if self.__mtxApiEH is None else self.taskBadge

    @property
    def __myTaskError(self) -> _TaskError:
        return None if self.__mtxApiEH is None else self.taskError

    @property
    def __myUniqueName(self):
        return type(self).__name__ if self.__myTaskBadge is None else self.__myTaskBadge.taskUniqueName

    @property
    def __myEuRNumber(self) -> int:
        return None if self.__mtxApiEH is None else self.euRNumber

    @property
    def __myLcProxy(self) -> _LcProxy:
        return None if self.__mtxApiEH is None else self._lcProxy

    def __SetOwnErrorEntry(self, ownErrorEntry_ : _ErrorEntry, forceOperation_ =False) -> _EuErrorBin._EErrBinOpResult:
        res = _EuErrorBin._EErrBinOpResult.eErrBinOpResultInvalidObject
        if ownErrorEntry_.isInvalid:
            pass
        else:
            if self.__eeBin is None:
                eeBin = _EuErrorBin(ownErrorEntry_.taskID, ownErrorEntry_.taskID, self.__mtxApiEH, ownErrorEntry_)
                if eeBin.currentError is None:
                    eeBin.CleanUp()
                else:
                    self.__eeBin = eeBin
                    res = _EuErrorBin._EErrBinOpResult.eErrBinOpResultSuccess
            else:
                res = self.__eeBin.SetCurrentError(ownErrorEntry_, force_=forceOperation_)
        return res

    def __AddForeignErrorEntry(self, foreignErrorEntry_: _ErrorEntry, forceOperation_ =False):
        if self.__feeBin is None:

            res = _EuErrorBin._EErrBinOpResult.eErrBinOpResultImplError
            vlogif._LogOEC(True, -1475)
        else:
            res = self.__feeBin.AddForeginErrorEntry(foreignErrorEntry_, force_=forceOperation_)
        return res

    def __GetEuErrorBinStatus(self):
        _bAllEmpty       = True
        _bEmptyEeBin     = True
        _pendingFErrList = None

        if self.__mtxApiEH is None:
            return _bAllEmpty, _bEmptyEeBin, _pendingFErrList

        if self.__feeBin is not None:
            with self.__mtxData:
                _pendingFErrList = self.__feeBin.GetAllPending(bFatalErrorsOnly_=_EuErrorHandler.__bIGONRE_FOREGIN_USER_ERRORS)

        _bEmptyEeBin = True if self.__eeBin is None else self.__eeBin.currentError is None
        _numPending  = None if _pendingFErrList is None else len(_pendingFErrList)
        _bAllEmpty   = _bEmptyEeBin and ((_numPending is None) or (_numPending == 0))

        if _EuErrorHandler.__APPLY_ERROR_BIN_REASSURANCE_CHECK:
            _bMisMatch = False
            _bEmptyTE  = self.__myTaskError.isErrorFree

            if _bEmptyTE != _bEmptyEeBin:
                _bMisMatch = True
            elif not _bEmptyEeBin:
                if self.__myTaskError is None:
                    _bMisMatch = True
                elif (self.__eeBin is None) or (self.__eeBin.currentError is None):
                    _bMisMatch = True
                elif self.__myTaskError.currentErrorUniqueID != self.__eeBin.currentError.uniqueID:
                    _bMisMatch = True
            if _bMisMatch:
                vlogif._LogOEC(True, -1476)

                if _bEmptyTE:
                    _bEmptyEeBin = True
                    if self.__eeBin is not None:
                        self.__eeBin.ClearCurError()
                    _bAllEmpty = _numPending == 0
                else:
                    _bAllEmpty, _bEmptyEeBin = False, False
                    self.__SetOwnErrorEntry(self.__myTaskError._currentErrorEntry)

        return _bAllEmpty, _bEmptyEeBin, _pendingFErrList

    def __ProcForeignErrors(self, pendingFErrList_ : list) -> _ETernaryOpResult:
        self._CheckStoredFFEsOnPendingStatus()

        _lstStoredFFEs = self._GetStoredFFEsList()
        _numStored = len(_lstStoredFFEs)

        _lstNew = pendingFErrList_

        if _lstNew is None:
            if _numStored > 0:
                _lstStoredFFEs.clear()

                _callbackID = _EErrorHandlerCallbackID.eProcessObservedForeignFatalErrors
                res = self._ProcErrorHandlerCallback(_callbackID, lstForeignFatalErrors_=None)
            else:
                res = _ETernaryOpResult.MapExecutionState2TernaryOpResult(self)

            return res

        if _numStored > 0:
            if len(_lstNew) != _numStored:
                _bSameList = False
            else:
                _bSameList = True
                for _ee in _lstStoredFFEs:
                    if not _ee.isPendingResolution:
                        _bSameList = False
                        break

                    _hit = [ ee2 for ee2 in _lstNew if ee2.uniqueID==_ee.uniqueID ]

                    if len(_hit) == 0:
                        _bSameList = False
                        break

            if not _bSameList:
                _lstStoredFFEs.clear()
                pass
            else:
                _lstNew.clear()
                _lstNew = None

        if _lstNew is not None:
            _callbackID = _EErrorHandlerCallbackID.eProcessObservedForeignFatalErrors
            res = self._ProcErrorHandlerCallback(_callbackID, lstForeignFatalErrors_=_lstNew)
        else:
            res = _ETernaryOpResult.MapExecutionState2TernaryOpResult(self)
        return res
