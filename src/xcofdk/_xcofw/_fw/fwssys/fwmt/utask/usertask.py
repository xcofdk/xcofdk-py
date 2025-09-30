# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : usertask.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from typing import Any   as _PyAmy
from typing import Tuple
from typing import Union

from xcofdk.fwcom     import CompoundTUID
from xcofdk.fwapi     import ITaskError
from xcofdk.fwapi.xmt import ITaskProfile
from xcofdk.fwapi.xmt import IXTask

from _fw.fwssys.assys                    import fwsubsysshare as _ssshare
from _fw.fwssys.assys.fwsubsysshare      import _FwSubsysShare
from _fw.fwssys.assys.ifs.ifxunit        import _IXUnit
from _fw.fwssys.assys.ifs.ifutask        import _IUserTask
from _fw.fwssys.assys.ifs.ifutagent      import _IUTAgent
from _fw.fwssys.fwcore.logging           import logif
from _fw.fwssys.fwcore.logging           import vlogif
from _fw.fwssys.fwctrl.fwapiconnap       import _FwApiConnectorAP
from _fw.fwssys.fwcore.base.strutil      import _StrUtil
from _fw.fwssys.fwcore.ipc.tsk.taskdefs  import _EUTaskApiID
from _fw.fwssys.fwcore.ipc.tsk.taskutil  import _TaskUtil
from _fw.fwssys.fwcore.ipc.tsk.taskmgr   import _TaskMgr
from _fw.fwssys.fwcore.ipc.tsk.taskutil  import _PyThread
from _fw.fwssys.fwcore.types.commontypes import override
from _fw.fwssys.fwcore.types.commontypes import _CommonDefines
from _fw.fwssys.fwmsg.apiimpl.xmsgimpl   import _XMsgImpl
from _fw.fwssys.fwerrh.fwerrorcodes      import _EFwErrorCode
from _fw.fwssys.fwmt.xtaskprfext         import _XTaskPrfExt
from _fw.fwssys.fwmt.utask.usertaskdefs  import _UTaskMirror
from _fw.fwssys.fwmt.utask.usertaskconn  import _UserTaskConn

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _UserTask(_IUserTask):
    __slots__ = [ '__utm' , '__xf' ]

    __sgltnID = None
    __lstBCN  = [ _FwTDbEngine.GetText(_EFwTextID.eELcCompID_XTask), _FwTDbEngine.GetText(_EFwTextID.eELcCompID_MainXTask) ]

    def __init__(self, uta_ : _IUTAgent, xtPrf_ : ITaskProfile):
        self.__xf  = None
        self.__utm = None
        super().__init__()

        if not _FwApiConnectorAP._APIsLcErrorFree():
            logif._XLogErrorEC(_EFwErrorCode.UE_00163, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTask_TID_027))
            return
        if _FwApiConnectorAP._APIsLcShutdownEnabled():
            logif._XLogErrorEC(_EFwErrorCode.UE_00164, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTask_TID_028))
            return

        if not isinstance(uta_, _IUTAgent):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00970)
            return

        self.__xf = uta_._xtInst

        _xtp   = None
        _xtpIn = None
        _xtp, _xtpIn = self.__CheckXtProfile(xtPrf_)
        if _xtp is None:
            self.__xf = None
            return

        if _xtp._utaskMirror is not None:
            self.__utm = _xtp._utaskMirror
        else:
            self.__utm = _UTaskMirror(uta_, _xtpIn, str(_xtp.aliasName))

        self.__utm._mrTaskCompUID = CompoundTUID(_xtp._bookedTaskID, _xtp._bookedTaskIndex)
        if (self.__utm.mrAliasName is None) or self.__utm.mrAliasName.endswith(_CommonDefines._CHAR_SIGN_UNDERSCORE):
            self.__utm.mrAliasName = str(_xtp.aliasName)

        _utc = _UserTaskConn(self.__utm, _xtp)
        if not _utc._isUTConnected:
            self.__xf  = None
            self.__utm = None
            logif._XLogFatalEC(_EFwErrorCode.FE_00921, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTask_TID_002).format(type(self).__name__))
            return

        if not isinstance(self.__utm.mrUTaskProfile, _XTaskPrfExt):
            if not self.__utm.mrUTaskProfile.isFrozen:
                self.__utm.mrUTaskProfile._AssignProfile(_xtp)
        if _xtp.isMainTask:
            _UserTask.__sgltnID = id(uta_._xtInst)
            _FwSubsysShare._SetMainXTaskSingleton(uta_._xtInst)
        self.__utm._MrUpdateConn(_utc, uta_, xtPrf_.isSyncTask)

    def __str__(self):
        return self._ToString()

    @_IXUnit._isAttachedToFW.getter
    def _isAttachedToFW(self) -> bool:
        return self.__isConnected

    @_IXUnit._isStarted.getter
    def _isStarted(self) -> bool:
        if self.__isInvalid:
            return False
        _utc = self.__utConn
        return self.__utm.mrIsStarted if _utc is None else _utc._isStarted

    @_IXUnit._isPendingRun.getter
    def _isPendingRun(self) -> bool:
        if self.__isInvalid:
            return False
        _utc = self.__utConn
        return False if _utc is None else _utc._isPendingRun

    @_IXUnit._isRunning.getter
    def _isRunning(self) -> bool:
        if self.__isInvalid:
            return False
        _utc = self.__utConn
        return False if _utc is None else _utc._isRunning

    @_IXUnit._isDone.getter
    def _isDone(self) -> bool:
        if self.__isInvalid:
            return False
        _utc = self.__utConn
        return self.__utm.mrIsDone if _utc is None else _utc._isDone

    @_IXUnit._isCanceled.getter
    def _isCanceled(self) -> bool:
        if self.__isInvalid:
            return False
        _utc = self.__utConn
        return self.__utm.mrIsCanceled if _utc is None else _utc._isCanceled

    @_IXUnit._isFailed.getter
    def _isFailed(self) -> bool:
        if self.__isInvalid:
            return False
        _utc = self.__utConn
        return self.__utm.mrIsFailed if _utc is None else _utc._isFailed

    @_IXUnit._isStopping.getter
    def _isStopping(self) -> bool:
        if self.__isInvalid:
            return False
        _utc = self.__utConn
        return self.__utm.mrIsStopping if _utc is None else _utc._isStopping

    @_IXUnit._isCanceling.getter
    def _isCanceling(self) -> bool:
        if self.__isInvalid:
            return False
        _utc = self.__utConn
        return self.__utm.mrIsCanceling if _utc is None else _utc._isCanceling

    @_IXUnit._isAborting.getter
    def _isAborting(self) -> bool:
        if self.__isInvalid:
            return False
        _utc = self.__utConn
        return self.__utm.mrIsAborting if _utc is None else _utc._isAborting

    @_IXUnit._isTerminated.getter
    def _isTerminated(self) -> bool:
        return self._isDone or self._isFailed or self._isCanceled

    @_IXUnit._isTerminating.getter
    def _isTerminating(self) -> bool:
        return self._isStopping or self._isCanceling or self._isAborting

    @_IXUnit._taskUID.getter
    def _taskUID(self) -> int:
        return None if self.__isInvalid else self.__utm.mrUTaskUID

    @_IXUnit._taskName.getter
    def _taskName(self) -> str:
        return None if self.__isInvalid else self.__utm.mrUTaskName

    @_IXUnit._taskProfile.getter
    def _taskProfile(self) -> ITaskProfile:
        if self.__isInvalid:
            return None
        _utc = self.__utConn
        return self.__utm.mrUTaskProfile if _utc is None else _utc._taskProfile

    @override
    def _Start(self, *args_, **kwargs_) -> bool:
        _utc = self.__utConn
        return False if _utc is None else _utc._StartUTask(*args_, **kwargs_)

    @override
    def _Stop(self, bCancel_ =False, bCleanupDriver_ =True) -> bool:
        if not self.__isConnected:
            return True
        _utc = self.__utConn
        return False if _utc is None else _utc._StopUTask(bCancel_=bCancel_, bCleanupDriver_=bCleanupDriver_)

    @override
    def _Join(self, timeout_: Union[int, float] =None) -> bool:
        if not self.__isConnected:
            return True
        _utc = self.__utConn
        return False if _utc is None else _utc._JoinUTask(timeout_=timeout_)

    @override
    def _SelfCheck(self) -> bool:
        if self.__isInvalid:
            return False

        _bScrNOK = self.__utm._mrSelfCheckResult._isScrNOK
        if not (self._isAttachedToFW and self._isStarted):
            return not _bScrNOK
        if not _bScrNOK:
            self.__utm._mrSelfCheckResult = self.__utConn._PcSelfCheck()
            _bScrNOK = self.__utm._mrSelfCheckResult._isScrNOK
        return not _bScrNOK

    @override
    def _ToString(self, bCompact_ =True):
        if not self._isAttachedToFW:
            _midPart = _FwTDbEngine.GetText(_EFwTextID.eMisc_Detached)
            if self.__utm is None:
                res = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_013)
                res = res.format(type(self).__name__, _midPart)
            else:
                res = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_014)
                res = res.format(self.__utm.mrUTaskName, _midPart, self.__utm._mrUTaskXStateAsStr)
        else:
            res       = self._taskName
            _uid      = self._taskUID
            _stateStr = None if self.__isInvalid else self.__utm._mrUTaskXStateAsStr

            if (_uid is not None) or (_stateStr is not None):
                _tmp = _CommonDefines._CHAR_SIGN_DASH if _uid is None else str(_uid)
                if _stateStr is not None:
                    _tmp += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_018).format(_stateStr)
                res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_010).format(_tmp)

            if not bCompact_:
                res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_031).format(self._taskProfile.ToString())
        return res

    @_IUserTask._isSyncTask.getter
    def _isSyncTask(self):
        return False if self.__isInvalid else self.__utm.mrUTaskProfile.isSyncTask

    @_IUserTask._isErrorFree.getter
    def _isErrorFree(self) -> bool:
        return False if self.__isInvalid else self._currentError is None

    @_IUserTask._isFatalErrorFree.getter
    def _isFatalErrorFree(self) -> bool:
        if self.__isInvalid:
            return False
        _curErr = self._currentError
        return (_curErr is None) or not _curErr.isFatalError

    @_IUserTask._taskAliasName.getter
    def _taskAliasName(self) -> str:
        return None if self.__isInvalid else self.__utm.mrAliasName

    @_IUserTask._currentError.getter
    def _currentError(self) -> ITaskError:
        if self.__isInvalid:
            return None
        _utc = self.__utConn
        return None if _utc is None else _utc._currentError

    @_IUserTask._curRunPhaseIterationNo.getter
    def _curRunPhaseIterationNo(self):
        return -1 if self.__utConn is None else self.__utConn._xrNumber

    @_IUserTask._taskCompUID.getter
    def _taskCompUID(self) -> Union[CompoundTUID, None]:
        return None if self.__isInvalid else self.__utm._mrTaskCompUID

    @override
    def _DetachFromFW(self):
        if self.__isInvalid:
            return
        _tp = self._taskProfile
        if (_tp is not None) and _tp.isMainTask:
            _FwSubsysShare._SetMainXTaskSingleton(None)

        _utc = self.__utConn
        if _utc is not None:
            _utc._DisconnectUTask(bDetachApiRequest_=True)

    @override
    def _GetTaskOwnedData(self, bDeser_ =True) -> _PyAmy:
        return None if self.__isInvalid else self.__utm._MrGetUData(bDeser_=bDeser_)

    @override
    def _SetTaskOwnedData(self, tskData_ : _PyAmy, bSer_ =False):
        if self.__isValid:
            self.__utm._MrSetUData(tskData_, bSer_=bSer_)

    @override
    def _ClearCurrentError(self) -> bool:
        if self.__isInvalid:
            return False
        if not self._isAttachedToFW:
            return True

        _utc = self.__utConn
        if _utc is None:
            return False

        _curXT = _FwApiConnectorAP._APGetCurXTask()
        if _curXT is None:
            return True

        if self._taskUID != _curXT.taskUID:
            logif._LogErrorEC(_EFwErrorCode.UE_00004, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTask_TID_014).format( self._taskUID))
            return False

        return _utc._ClearCurrentError()

    @override
    def _SetTaskError(self, bFatal_ : bool, errMsg_: str, errCode_: int =None):
        if self.__isInvalid:
            return
        if not self._isAttachedToFW:
            return

        _utc = self.__utConn
        if _utc is None:
            return

        _curXT = _FwApiConnectorAP._APGetCurXTask()
        if _curXT is None:
            return

        if self._taskUID != _curXT.taskUID:
            _msgID = _EFwTextID.eLogMsg_UserTask_TID_026 if bFatal_ else _EFwTextID.eLogMsg_UserTask_TID_025
            logif._LogErrorEC(_EFwErrorCode.UE_00005, _FwTDbEngine.GetText(_msgID).format( self._taskUID))
            return

        _utc._SetTaskError(bFatal_, errMsg_, errCode_)

    @override
    def _TriggerQueueProcessing(self, bExtQueue_ : bool) -> int:
        if _ssshare._WarnOnDisabledSubsysMsg(annexID_=_EFwTextID.eMisc_Shared_Disabled_Subsys_Msg):
            return -1
        if self.__isInvalid:
            return -1
        if not self._isAttachedToFW:
            return -1

        _utc = self.__utConn
        if _utc is None:
            return -1

        if not bExtQueue_:
            if not self._taskProfile.isInternalQueueEnabled:
                _midPart = _FwTDbEngine.GetText(_EFwTextID.eMisc_QueueType_Internal)
                logif._LogErrorEC(_EFwErrorCode.UE_00006, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTask_TID_005).format(_midPart, self._taskUID, _midPart))
                return -1
        elif not self._taskProfile.isExternalQueueEnabled:
            _midPart = _FwTDbEngine.GetText(_EFwTextID.eMisc_QueueType_External)
            logif._LogErrorEC(_EFwErrorCode.UE_00007, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTask_TID_005).format(_midPart, self._taskUID, _midPart))
            return -1
        elif self._taskProfile.isExternalQueueBlocking:
            _midPart = _FwTDbEngine.GetText(_EFwTextID.eMisc_QueueType_External)
            logif._LogErrorEC(_EFwErrorCode.UE_00008, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTask_TID_023).format(_midPart, self._taskUID, _midPart))
            return -1

        _curXT = _FwApiConnectorAP._APGetCurXTask()
        if _curXT is None:
            return -1

        if self._taskUID != _curXT.taskUID:
            _midPart = _FwTDbEngine.GetText(_EFwTextID.eMisc_QueueType_External) if bExtQueue_ else _FwTDbEngine.GetText(_EFwTextID.eMisc_QueueType_Internal)
            logif._LogErrorEC(_EFwErrorCode.UE_00009, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTask_TID_024).format(_midPart, self._taskUID, _curXT.taskUID))
            return -1

        return _utc._TriggerQueueProcessing(bExtQueue_)

    @staticmethod
    def _SendXMsg(tx_ : IXTask, xmsg_  : _XMsgImpl) -> Union[bool, None]:
        if tx_ is None:
            return False
        if not (isinstance(xmsg_, _XMsgImpl) and xmsg_.isValid):
            return False

        if tx_.isDetachedFromFW:
            return None

        _tsk = _TaskMgr().GetTask(tx_.taskUID)
        _utc = None if (_tsk is None) or not _tsk.isRunning else _tsk._utConn

        if _utc is None:
            return None

        res = _utc._SendXMsg(xmsg_)
        if not res:
            _bLRTE = False
            _bLRTE = _bLRTE or not _FwApiConnectorAP._APIsLcErrorFree()
            _bLRTE = _bLRTE or _FwApiConnectorAP._APIsLcShutdownEnabled()
            if _bLRTE:
                res = None
        return res

    def _CPrf(self, enclHThrd_ : _PyThread =None, profileAttrs_ : dict =None):
        _utc = self.__utConn
        return None if _utc is None else _utc._CPrf(enclHThrd_=enclHThrd_, profileAttrs_=profileAttrs_)

    @staticmethod
    def __IsSingletonCreated():
        return isinstance(_UserTask.__sgltnID, int)

    @property
    def __isValid(self):
        return self.__utm is not None

    @property
    def __isInvalid(self):
        return self.__utm is None

    @property
    def __isConnected(self):
        return self.__isValid and self.__utm.mrIsConnected

    @property
    def __isDisconnected(self):
        return self.__isInvalid or not self.__utm.mrIsConnected

    @property
    def __utConn(self) -> Union[_UserTaskConn, None]:
        if self.__isInvalid:
            return None
        return None if not self.__utm.mrIsConnected else self.__utm.mrUTConn

    @staticmethod
    def __IsDefaultCallback(callback_):
        return (callback_ is not None) and callback_.__qualname__.split(_CommonDefines._CHAR_SIGN_DOT)[0] in _UserTask.__lstBCN

    @staticmethod
    def __CheckSetDefaultAliasName(xtPrf_ : _XTaskPrfExt):
        if not xtPrf_.isValid:
            return False
        if xtPrf_.aliasName is None:
            if xtPrf_.isExternalQueueEnabled or xtPrf_.isInternalQueueEnabled:
                _an = _EFwTextID.eMisc_TNPrefix_CRCTask if xtPrf_.isRcTask else _EFwTextID.eMisc_TNPrefix_CXTask
            else:
                _an = _EFwTextID.eMisc_TNPrefix_RCTask if xtPrf_.isRcTask else _EFwTextID.eMisc_TNPrefix_XTask
            _an = _FwTDbEngine.GetText(_an) + str(xtPrf_._bookedTaskIndex)
            xtPrf_.aliasName = _an
        elif xtPrf_.aliasName.endswith(_CommonDefines._CHAR_SIGN_UNDERSCORE):
            _an = xtPrf_.aliasName + str(xtPrf_._bookedTaskIndex)
            xtPrf_.aliasName = _an
        return xtPrf_.isValid

    def __CheckXtProfile(self, xtPrf_ : ITaskProfile) -> Tuple[Union[_XTaskPrfExt, None], Union[ITaskProfile, None]]:
        _xtp   = xtPrf_
        _xtp2  = None
        _xtpIn = xtPrf_

        if not (isinstance(xtPrf_, ITaskProfile) and xtPrf_.isValid):
            logif._XLogErrorEC(_EFwErrorCode.UE_00165, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTask_TID_003).format(type(xtPrf_).__name__))
            return None, None

        res = _xtp
        if not isinstance(res, _XTaskPrfExt):
            res   = _XTaskPrfExt(xtPrf_=res)
            _xtp2 = res

        if not res.isValid:
            logif._XLogErrorEC(_EFwErrorCode.UE_00166, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTask_TID_004).format(str(res)))
            res = None
        else:
            res._BookTaskID()

            if not _UserTask.__CheckSetDefaultAliasName(res):
                res = None
            elif not self.__CheckMainXT(res):
                res = None
            elif not self.__CheckAliasName(res):
                res = None
            elif not self.__CheckIQueue(res):
                res = None
            elif not self.__CheckXQueue(res):
                res = None
            elif not self.__CheckRun(res):
                res = None
            elif not self.__CheckSetup(res):
                res = None
            elif not self.__CheckTeardown(res):
                res = None
            elif not self.__CheckRunPhaseFrequency(res):
                res = None
            elif not self.__CheckMaxProcTimespan(res):
                res = None

        if res is None:
            if _xtp2 is not None:
                _xtp2._CleanUp()
            _xtp, _xtpIn = None, None

        return res, _xtpIn

    def __CheckMainXT(self, xtProfileExt_: _XTaskPrfExt) -> bool:
        res  = self is not None
        if xtProfileExt_.isMainTask:
            if _UserTask.__IsSingletonCreated():
                res = False
                logif._XLogErrorEC(_EFwErrorCode.UE_00167, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTask_TID_006))
        return res

    def __CheckAliasName(self, xtProfileExt_: _XTaskPrfExt) -> bool:
        res  = True
        _xtp = xtProfileExt_

        _aliasName = _xtp.aliasName
        if _aliasName is None:
            _xtp.aliasName = type(self).__name__
        elif not isinstance(_aliasName, str):
            res = False
            logif._XLogErrorEC(_EFwErrorCode.UE_00168, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTask_TID_007).format(type(_aliasName).__name__))
        else:
            _aliasName = _aliasName.strip()
            if len(_aliasName) < 1:
                _xtp.aliasName = _StrUtil.DeCapialize(type(self).__name__)
                logif._XLogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTask_TID_008).format(_aliasName))
            elif not _TaskUtil.IsValidAliasName(_aliasName):
                res = False
                logif._XLogErrorEC(_EFwErrorCode.UE_00268, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTask_TID_029).format(_aliasName))
        return res

    def __CheckIQueue(self, xtProfileExt_: _XTaskPrfExt) -> bool:
        res  = True
        _xtp = xtProfileExt_

        _an = _EUTaskApiID.eProcessInternalMessage.functionName
        _av = getattr(self.__xf, _an, None)

        if not _xtp.isInternalQueueEnabled:
            if _av is not None:
                if not _UserTask.__IsDefaultCallback(_av):
                    logif._XLogDebug(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTask_TID_010).format(type(self).__name__, _an))
        elif _av is None:
            res = False
            logif._XLogErrorEC(_EFwErrorCode.UE_00170, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTask_TID_011).format(type(self).__name__, _an))
        return res

    def __CheckXQueue(self, xtProfileExt_: _XTaskPrfExt) -> bool:
        res  = True
        _xtp = xtProfileExt_

        _an = _EUTaskApiID.eProcessExternalMessage.functionName
        _av = getattr(self.__xf, _an, None)

        if not _xtp.isExternalQueueEnabled:
            if _av is not None:
                if not _UserTask.__IsDefaultCallback(_av):
                    logif._XLogDebug(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTask_TID_012).format(type(self).__name__, _an))
            if _xtp.isExternalQueueBlocking:
                res = False
                logif._XLogErrorEC(_EFwErrorCode.UE_00171, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTask_TID_013).format(type(self).__name__))
        elif _av is None:
            res = False
            logif._XLogErrorEC(_EFwErrorCode.UE_00172, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTask_TID_011).format(type(self).__name__, _an))
        return res

    def __CheckRun(self, xtProfileExt_: _XTaskPrfExt) -> bool:
        res  = True
        _xtp = xtProfileExt_

        _an = _EUTaskApiID.eRunXTask.functionName
        _av = getattr(self.__xf, _an, None)

        if _xtp.isExternalQueueEnabled and _xtp.isExternalQueueBlocking:
            if _av is None:
                pass
            elif not _UserTask.__IsDefaultCallback(_av):
                _av = None
                logif._XLogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTask_TID_022).format(type(self).__name__, _an))
            else:
                _av = None

        else:
            if _av is None:
                res = False
            elif _UserTask.__IsDefaultCallback(_av):
                res       = False
                _av = None
            if not res:
                logif._XLogErrorEC(_EFwErrorCode.UE_00173, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTask_TID_011).format(type(self).__name__, _an))

        if res:
            if (_av is not None) != _xtp.isRunPhaseEnabled:
                res = False
                logif._XLogFatalEC(_EFwErrorCode.FE_00922, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTask_TID_015).format(type(self).__name__, _an))
        return res

    def __CheckSetup(self, xtProfileExt_: _XTaskPrfExt) -> bool:
        res  = True
        _xtp = xtProfileExt_

        _an = _EUTaskApiID.eSetUpXTask.functionName
        _av = getattr(self.__xf, _an, None)

        if not _xtp.isSetupPhaseEnabled:
            if _av is not None:
                if not _UserTask.__IsDefaultCallback(_av):
                    logif._XLogDebug(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTask_TID_016).format(type(self).__name__, _an))
        elif _av is None:
            res = False
            logif._XLogErrorEC(_EFwErrorCode.UE_00174, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTask_TID_011).format(type(self).__name__, _an))
        return res

    def __CheckTeardown(self, xtProfileExt_: _XTaskPrfExt) -> bool:
        res  = True
        _xtp = xtProfileExt_

        _an = _EUTaskApiID.eTearDownXTask.functionName
        _av = getattr(self.__xf, _an, None)

        if not _xtp.isTeardownPhaseEnabled:
            if _av is not None:
                if not _UserTask.__IsDefaultCallback(_av):
                    logif._XLogDebug(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTask_TID_017).format(type(self).__name__, _an))
        elif _av is None:
            res = False
            logif._XLogErrorEC(_EFwErrorCode.UE_00175, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTask_TID_011).format(type(self).__name__, _an))
        return res

    def __CheckRunPhaseFrequency(self, xtProfileExt_: _XTaskPrfExt) -> bool:
        res  = True
        _xtp = xtProfileExt_

        if _xtp.runPhaseFrequencyMS < 0:
            res = False
            logif._XLogErrorEC(_EFwErrorCode.UE_00176, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTask_TID_018).format(_xtp.runPhaseFrequencyMS, type(self).__name__))

        return res

    def __CheckMaxProcTimespan(self, xtProfileExt_: _XTaskPrfExt) -> bool:
        res  = True
        _xtp = xtProfileExt_

        if _xtp.runPhaseMaxProcessingTimeMS <= 0:
            res = False
            logif._XLogErrorEC(_EFwErrorCode.UE_00177, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_UserTask_TID_021).format(_xtp.runPhaseMaxProcessingTimeMS, type(self).__name__))
        return res

