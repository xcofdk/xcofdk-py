# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : pcerrhandler.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum import unique

from _fw.fwssys.assys                      import fwsubsysshare as _ssshare
from _fw.fwssys.fwcore.logging             import vlogif
from _fw.fwssys.fwcore.logging             import logif
from _fw.fwssys.fwcore.base.util           import _Util
from _fw.fwssys.fwcore.ipc.sync.mutex      import _Mutex
from _fw.fwssys.fwcore.ipc.tsk.taskbadge   import _TaskBadge
from _fw.fwssys.fwcore.ipc.tsk.fwtaskerror import _FwTaskError
from _fw.fwssys.fwcore.lc.lcproxyclient    import _LcProxyClient
from _fw.fwssys.fwcore.types.commontypes   import _FwIntEnum
from _fw.fwssys.fwcore.types.commontypes   import _EExecutionCmdID
from _fw.fwssys.fwcore.types.commontypes   import _CommonDefines
from _fw.fwssys.fwerrh.fwerrorcodes        import _EFwErrorCode
from _fw.fwssys.fwerrh.pcerrorbin          import _PcErrorBin
from _fw.fwssys.fwerrh.pcerrorbin          import _PcFEBinTable
from _fw.fwssys.fwerrh.logs.errorlog       import _ErrorLog
from _fw.fwssys.fwerrh.logs.errorlog       import _FatalLog
from _fw.fwssys.fwerrh.logs.xcoexception   import _IsXTXcp
from _fw.fwssys.fwerrh.logs.xcoexception   import _XcoXcpRootBase
from _fw.fwssys.fwerrh.logs.xcoexception   import _XcoException

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

@unique
class _EPcErrHandlerCBID(_FwIntEnum):
    eAbortTaskDueToUnexpectedCall      = 3041
    eProcessFwMainDieError             = 3052
    eProcessFwMainFatalError           = 3053
    eProcessObservedForeignFatalErrors = 3061
    eAbortTaskDueToDieError            = 3071
    eAbortTaskDueToFatalError          = 3072

    @property
    def isFwMainSpecificCallbackID(self):
        return (self.value > _EPcErrHandlerCBID.eAbortTaskDueToUnexpectedCall) and \
               (self.value < _EPcErrHandlerCBID.eAbortTaskDueToDieError)

    @property
    def isAbortTaskDueToUnexpectedCall(self):
        return self == _EPcErrHandlerCBID.eAbortTaskDueToUnexpectedCall

    @property
    def isProcessFwMainDieError(self):
        return self == _EPcErrHandlerCBID.eProcessFwMainDieError

    @property
    def isProcessFwMainFatalError(self):
        return self == _EPcErrHandlerCBID.eProcessFwMainFatalError

    @property
    def isProcessObservedForeignFatalErrors(self):
        return self == _EPcErrHandlerCBID.eProcessObservedForeignFatalErrors

    @property
    def isAbortTaskDueToDieError(self):
        return self == _EPcErrHandlerCBID.eAbortTaskDueToDieError

    @property
    def isAbortTaskDueToFatalError(self):
        return self == _EPcErrHandlerCBID.eAbortTaskDueToFatalError

class _PcErrHandler(_LcProxyClient):
    __slots__  = [ '__ma' , '__md' , '__b' , '__fb' ]

    def __init__(self):
        self.__b  = None
        self.__fb = None
        self.__ma = None
        self.__md = None
        super().__init__()

    def _ProcErrorHandlerCallback( self
                                 , cbID_   : _EPcErrHandlerCBID
                                 , curFE_  : _FatalLog =None
                                 , lstFFE_ : list      =None) -> _EExecutionCmdID:
        vlogif._LogOEC(True, _EFwErrorCode.VFE_00487)
        return _EExecutionCmdID.Abort()

    @property
    def _isForeignErrorListener(self):
        return None if self.__ma is None else self.__myTaskBadge.hasForeignErrorListnerTaskRight

    @property
    def _curOwnError(self):
        if self.__ma is None: return None
        with self.__ma:
            res = None if self.__b is None else self.__b.currentError
            if res is not None:
                if res.hasNoImpactDueToFrcLinkage:
                    res = None
            return res

    def _AddError(self, euEEntry_ : _ErrorLog) -> bool:
        try:
            if self.__ma is None:
                _opr = _PcErrorBin._EErrBinOpResult.eErrBinOpResultInvalidObject
            elif not isinstance(euEEntry_, _ErrorLog):
                _opr = _PcErrorBin._EErrBinOpResult.eErrBinOpResultImplError
            elif euEEntry_.isInvalid:
                _opr = _PcErrorBin._EErrBinOpResult.eErrBinOpResultSuccess
            elif euEEntry_.hasNoErrorImpact:
                _opr    = _PcErrorBin._EErrBinOpResult.eErrBinOpResultSuccess
                _errImp = euEEntry_.errorImpact
            else:
                _bFErr = euEEntry_.IsForeignTaskError(self.__myTaskBadge.dtaskUID)
                if _bFErr:
                    with self.__md:
                        _opr = self.__AddForeignErrorEntry(euEEntry_, forceOperation_=False)
                else:
                    with self.__ma:
                        _opr = self.__SetOwnErrorEntry(euEEntry_, forceOperation_=False)
            res = _opr.isErrBinOpResultSuccess
            if not res:
                if _opr.isErrBinOpResultDuplicateInsertionError:
                    res = True
        except KeyboardInterrupt:
            res = False
            _midPart = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_PcErrHandler_TID_002).format(euEEntry_.uniqueID, euEEntry_.shortMessage)
            _msg     = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_KeyboardInterrupt).format(self.__myTaskBadge.dtaskName, _midPart)
            _ssshare._BookKBI(_msg)
        except BaseException as _xcp:
            res = False
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00968)
        return res

    def _ProcErrors(self, bCheckForFEOnly_ =False) -> _EExecutionCmdID:
        if self.__ma is None:
            return _EExecutionCmdID.Abort()

        with (self.__ma):
            _myTB            = self.__myTaskBadge
            _bAborting       = self.__isAborting
            _bInvalidPxy     = not self._PcIsLcProxySet()
            _bInvalidBadge   = _myTB is None
            _bSomeLcFailure  = self._PcHasLcAnyFailureState()
            _bPxyUnavailable = self._PcIsLcProxyModeShutdown()
            _bUnexpectedCall = _bInvalidBadge or _bInvalidPxy or _bAborting or _bPxyUnavailable

            if _bUnexpectedCall or _bSomeLcFailure:
                if _bUnexpectedCall:
                    _callbackID = _EPcErrHandlerCBID.eAbortTaskDueToUnexpectedCall
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00488)

                    _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_PcErrHandler_TID_001).format(self.__myUniqueName)
                    _myFE = logif._CreateLogImplErrorEC(_EFwErrorCode.FE_00025, _errMsg)
                    res = self._ProcErrorHandlerCallback(_callbackID, curFE_=_myFE)
                else:
                    res = _EExecutionCmdID.MapExecState2ExecCmdID(self)
                return res

            _bAllEmpty       = None
            _bEmptyEeBin     = None
            _pendingFErrList = None
            _bAllEmpty, _bEmptyEeBin, _pendingFErrList = self.__GetErrBinStatus()

            if _bAllEmpty:
                return _EExecutionCmdID.MapExecState2ExecCmdID(self)

            if not (_bEmptyEeBin or bCheckForFEOnly_):
                _curOwnErr = self.__b.currentError

                if _curOwnErr.errorImpact.isCausedByDieMode:
                    if _myTB.isFwMain:
                        _callbackID = _EPcErrHandlerCBID.eProcessFwMainDieError
                        return self._ProcErrorHandlerCallback(_callbackID, curFE_=_curOwnErr)

                    _callbackID = _EPcErrHandlerCBID.eAbortTaskDueToDieError
                    return self._ProcErrorHandlerCallback(_callbackID, curFE_=_curOwnErr)

                if _curOwnErr.errorImpact.isCausedByFatalError:
                    if _myTB.isFwMain:
                        _callbackID = _EPcErrHandlerCBID.eProcessFwMainFatalError
                        return self._ProcErrorHandlerCallback(_callbackID, curFE_=_curOwnErr)

                    _callbackID = _EPcErrHandlerCBID.eAbortTaskDueToFatalError
                    return self._ProcErrorHandlerCallback(_callbackID, curFE_=_curOwnErr)
                self.__b.ClearCurError()

                return _EExecutionCmdID.MapExecState2ExecCmdID(self)

            if not _myTB.hasForeignErrorListnerTaskRight:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00489)
                return _EExecutionCmdID.Abort()
            elif self._GetStoredFFEsList() is None:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00490)
                return _EExecutionCmdID.Abort()

            _bProcFErrList = (_pendingFErrList is not None) or (len(self._GetStoredFFEsList()) > 0)

            if not _bProcFErrList:
                res = _EExecutionCmdID.MapExecState2ExecCmdID(self)
            else:
                res = self.__ProcForeignErrors(_pendingFErrList)

            return res

    def _ProcUnhandledXcp(self, xcp_: _XcoXcpRootBase):
        if self.__ma is None:
            return False
        if not isinstance(xcp_, _XcoXcpRootBase):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00491)
            return False

        _bXTskXcp = _IsXTXcp(xcp_)
        _myXcoXcp = None if _bXTskXcp else xcp_
        if (_myXcoXcp is not None) and not isinstance(_myXcoXcp, _XcoException):
            _myXcoXcp = None

        if not (_bXTskXcp or (_myXcoXcp is not None)):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00492)
            return False
        elif (_myXcoXcp is not None) and not (_myXcoXcp.isXcoBaseException or _myXcoXcp.isLogException or _myXcoXcp.isDieException):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00493)
            return False

        if _bXTskXcp:
            _myFE = logif._GetCurrentXTaskErrorEntry(xcp_.uniqueID)
            if _myFE is None:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00494)
                return False
            _myXcpUID   = _myFE.uniqueID
            _myXcpTName = _myFE.dtaskName
            _myXcpMsg   = _myFE.shortMessage

        else:
            _myXcpUID   = _myXcoXcp.uniqueID
            _myXcpTName = _myXcoXcp.dtaskName
            _myXcpMsg   = _myXcoXcp.shortMessage

        if _bXTskXcp or not _myXcoXcp.isXcoBaseException:
            _curOwnErr = self._curOwnError

            if (_myXcoXcp is not None) and _myXcoXcp.dtaskUID != self.__myTaskBadge.dtaskUID:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00495)
                return False
            if _curOwnErr is None:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00496)
                return False
            if _curOwnErr.uniqueID == _myXcpUID:
                return True
            if _curOwnErr.isFatalError:
                return True

            vlogif._LogOEC(True, _EFwErrorCode.VFE_00497)
            return False
        logif._LogUnhandledXcoBaseXcpEC(_EFwErrorCode.FE_00018, _myXcoXcp)
        return True

    def _SetUpPcEH(self, ma_ : _Mutex):
        if self.__ma is not None:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00498)
        if not _Util.IsInstance(ma_, _Mutex, bThrowx_=True):
            return

        _rn = getattr(self, _FwTDbEngine.GetText(_EFwTextID.ePreDefinedMethod_XRNumber), None)
        _tb = getattr(self, _FwTDbEngine.GetText(_EFwTextID.ePreDefinedMethod_TaskBadge), None)
        _te = getattr(self, _FwTDbEngine.GetText(_EFwTextID.ePreDefinedMethod_TaskError), None)
        if _tb is None:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00499)
            return
        if _te is None:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00500)
            return
        if _rn is None:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00501)
            return

        _feeBin    = None
        _mtxDataMe = None

        if _tb.hasForeignErrorListnerTaskRight:
            _mtxDataMe = _Mutex()
            _feeBin = _PcFEBinTable(_tb.dtaskUID, _mtxDataMe)
            if _feeBin.ownerTaskID is None:
                _feeBin.CleanUp()
                _mtxDataMe.CleanUp()
                return

        self.__fb   = _feeBin
        self.__md  = _mtxDataMe
        self.__ma = ma_

    def _ToString(self):
        res = None
        if self.__ma is not  None:
            with self.__ma:
                _midPart = _CommonDefines._CHAR_SIGN_DASH if self.__b is None else self.__b.ToString()
                res      = _FwTDbEngine.GetText(_EFwTextID.ePcErrHandler_ToString_01).format(self.__myTaskBadge.dtaskName, _midPart)
                if self.__fb is not None:
                    res += _FwTDbEngine.GetText(_EFwTextID.ePcErrHandler_ToString_02).format(self.__fb.ToString())
        return res

    def _CleanUp(self):
        super()._CleanUp()

        if self.__ma is not None:
            if self.__md is not None:
                self.__md.CleanUp()
                self.__md = None
            if self.__fb is not None:
                self.__fb.CleanUp()
                self.__fb = None
            if self.__b is not None:
                self.__b.CleanUp()
                self.__b = None
            self.__ma = None

    @property
    def __isAborting(self) -> bool:
        return True if self.__ma is None else self.isAborting

    @property
    def __myTaskBadge(self) -> _TaskBadge:
        return None if self.__ma is None else self.taskBadge

    @property
    def __myTaskError(self) -> _FwTaskError:
        return None if self.__ma is None else self.taskError

    @property
    def __myUniqueName(self):
        _tskBadge = self.__myTaskBadge
        return type(self).__name__ if _tskBadge is None else _tskBadge.dtaskName

    @property
    def __myXRNumber(self) -> int:
        return None if self.__ma is None else self.xrNumber

    def __SetOwnErrorEntry(self, ownErrorEntry_ : _ErrorLog, forceOperation_ =False) -> _PcErrorBin._EErrBinOpResult:
        res = _PcErrorBin._EErrBinOpResult.eErrBinOpResultInvalidObject
        if not ownErrorEntry_.isInvalid:
            if self.__b is None:
                eeBin = _PcErrorBin(ownErrorEntry_.dtaskUID, ownErrorEntry_.dtaskUID, self.__ma, ownErrorEntry_)
                if eeBin.currentError is None:
                    eeBin.CleanUp()
                else:
                    self.__b = eeBin
                    res = _PcErrorBin._EErrBinOpResult.eErrBinOpResultSuccess
            else:
                res = self.__b.SetCurrentError(ownErrorEntry_, force_=forceOperation_)
        return res

    def __AddForeignErrorEntry(self, foreignErrorEntry_: _ErrorLog, forceOperation_ =False):
        if self.__fb is None:
            res = _PcErrorBin._EErrBinOpResult.eErrBinOpResultImplError
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00502)
        else:
            res = self.__fb.AddForeginErrorEntry(foreignErrorEntry_, force_=forceOperation_)
        return res

    def __GetErrBinStatus(self):
        _bAllEmpty       = True
        _bEmptyEeBin     = True
        _pendingFErrList = None

        if self.__ma is None:
            return _bAllEmpty, _bEmptyEeBin, _pendingFErrList

        if self.__fb is not None:
            with self.__md:
                _pendingFErrList = self.__fb.GetAllPending()

        _bEmptyEeBin = True if self.__b is None else self.__b.currentError is None
        _numPending  = None if _pendingFErrList is None else len(_pendingFErrList)
        _bAllEmpty   = _bEmptyEeBin and ((_numPending is None) or (_numPending == 0))

        return _bAllEmpty, _bEmptyEeBin, _pendingFErrList

    def __ProcForeignErrors(self, pendingFErrList_ : list) -> _EExecutionCmdID:
        self._CheckSFFEsPS()

        _lstStoredFFEs = self._GetStoredFFEsList()
        _numStored = len(_lstStoredFFEs)

        _lstNew = pendingFErrList_

        if _lstNew is None:
            if _numStored > 0:
                _lstStoredFFEs.clear()
                _callbackID = _EPcErrHandlerCBID.eProcessObservedForeignFatalErrors
                res = self._ProcErrorHandlerCallback(_callbackID, lstFFE_=None)
            else:
                res = _EExecutionCmdID.MapExecState2ExecCmdID(self)
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
            else:
                _lstNew.clear()
                _lstNew = None

        if _lstNew is not None:
            _callbackID = _EPcErrHandlerCBID.eProcessObservedForeignFatalErrors
            res = self._ProcErrorHandlerCallback(_callbackID, lstFFE_=_lstNew)
        else:
            res = _EExecutionCmdID.MapExecState2ExecCmdID(self)
        return res
