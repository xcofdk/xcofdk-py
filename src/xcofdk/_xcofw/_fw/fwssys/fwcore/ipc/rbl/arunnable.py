# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : arunnable.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from typing import Union

from xcofdk.fwcom      import EExecutionCmdID
from xcofdk.fwapi.xmt  import ITaskProfile
from xcofdk.fwapi.xmsg import XMessage
from xcofdk.fwapi.xmsg import XPayload

from _fw.fwssys.assys                     import fwsubsysshare as _ssshare
from _fw.fwssys.assys.ifs.ifdispagent     import _IDispAgent
from _fw.fwssys.assys.ifs.ifutaskconn     import _IUTaskConn
from _fw.fwssys.assys.ifs.ifutagent       import _IUTAgent
from _fw.fwssys.fwcore.logging            import logif
from _fw.fwssys.fwcore.logging            import vlogif
from _fw.fwssys.fwcore.logging.logdefines import _EErrorImpact
from _fw.fwssys.fwcore.base.fwcallable    import _FwCallable
from _fw.fwssys.fwcore.base.gtimeout      import _Timeout
from _fw.fwssys.fwcore.base.sigcheck      import _CallableSignature
from _fw.fwssys.fwcore.base.timeutil      import _TimeAlert
from _fw.fwssys.fwcore.base.strutil       import _StrUtil
from _fw.fwssys.fwcore.base.util          import _Util
from _fw.fwssys.fwcore.ipc.sync.mutex     import _Mutex
from _fw.fwssys.fwcore.ipc.sync.semaphore import _BinarySemaphore
from _fw.fwssys.fwcore.ipc.rbl.arbldefs   import _ARblApiGuide
from _fw.fwssys.fwcore.ipc.rbl.arbldefs   import _ERunProgressID
from _fw.fwssys.fwcore.ipc.rbl.arbldefs   import _ERblApiFuncTag
from _fw.fwssys.fwcore.ipc.rbl.arbldefs   import _ERblExecStepID
from _fw.fwssys.fwcore.ipc.tsk            import taskmgr
from _fw.fwssys.fwcore.ipc.tsk.afwtask    import _AbsFwTask
from _fw.fwssys.fwcore.ipc.tsk.taskdefs   import _ERblType
from _fw.fwssys.fwcore.ipc.tsk.taskdefs   import _ETaskSelfCheckResultID
from _fw.fwssys.fwcore.ipc.tsk.taskstate  import _TaskState
from _fw.fwssys.fwcore.ipc.tsk.taskutil   import _TaskUtil
from _fw.fwssys.fwcore.ipc.tsk.taskutil   import _ETaskApiContextID
from _fw.fwssys.fwcore.ipc.tsk.taskutil   import _ETaskXPhaseID
from _fw.fwssys.fwcore.ipc.tsk.taskutil   import _EProcessingFeasibilityID
from _fw.fwssys.fwcore.ipc.tsk.taskxcard  import _TaskXCard
from _fw.fwssys.fwcore.ipc.xu.afwxunit    import _AbsFwXUnit
from _fw.fwssys.fwcore.lc.lcdefines       import _ELcOperationModeID
from _fw.fwssys.fwcore.lc.lcproxyclient   import _LcProxyClient
from _fw.fwssys.fwcore.lc.lcmn.lcmontlb   import _LcDynamicTLB
from _fw.fwssys.fwcore.lc.lcmn.lcmontlb   import _LcCeaseTLB
from _fw.fwssys.fwcore.lc.lcmn.lcmontlb   import _ELcCeaseTLBState
from _fw.fwssys.fwcore.types.afwprofile   import _AbsFwProfile
from _fw.fwssys.fwcore.types.afwprofile   import _AbsSlotsObject
from _fw.fwssys.fwcore.types.commontypes  import override
from _fw.fwssys.fwcore.types.commontypes  import _CommonDefines
from _fw.fwssys.fwcore.types.commontypes  import _EExecutionCmdID
from _fw.fwssys.fwerrh.fwerrorcodes       import _EFwErrorCode
from _fw.fwssys.fwerrh.pcerrhandler       import _EPcErrHandlerCBID
from _fw.fwssys.fwerrh.pcerrhandler       import _PcErrHandler
from _fw.fwssys.fwerrh.logs.errorlog      import _ErrorLog
from _fw.fwssys.fwerrh.logs.errorlog      import _FatalLog
from _fw.fwssys.fwerrh.logs.xcoexception  import _IsXTXcp
from _fw.fwssys.fwerrh.logs.xcoexception  import _XcoXcpRootBase
from _fw.fwssys.fwerrh.logs.xcoexception  import _XcoBaseException
from _fw.fwssys.fwmsg.msg                 import _IFwMessage
from _fw.fwssys.fwmsg.disp.dispfilter     import _DispatchFilter
from _fw.fwssys.fwmsg.disp.dispregistry   import _DispatchRegistry
from _fwa.fwsubsyscoding                  import _FwSubsysCoding

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _AbsRunnable(_IDispAgent, _PcErrHandler, _AbsFwXUnit):
    class _RunnableExecutionPlan(_AbsSlotsObject):
        __slots__ = [ '__ds' ]

        def __init__(self, dictSteps_ : dict):
            self.__ds = dictSteps_
            super().__init__()

        @property
        def isIncludingSetUpExecutable(self):
            return self._IsIncludingExecStep(_ERblExecStepID.eSetUpExecutable)

        @property
        def isIncludingTeardownExecutable(self):
            return self._IsIncludingExecStep(_ERblExecStepID.eTeardownExecutable)

        @property
        def isIncludingRunExecutable(self):
            return self._IsIncludingExecStep(_ERblExecStepID.eRunExecutable)

        @property
        def isIncludingCustomManagedExternalQueue(self):
            return self._IsIncludingExecStep(_ERblExecStepID.eCustomManagedExternalQueue)

        @property
        def isIncludingAutoManagedExternalQueue(self):
            return self._IsIncludingExecStep(_ERblExecStepID.eAutoManagedExternalQueue)

        @property
        def isIncludingAutoManagedExternalQueue_By_RunExecutable(self):
            return self._IsIncludingExecStep(_ERblExecStepID.eAutoManagedExternalQueue_By_RunExecutable)

        @property
        def isIncludingCustomManagedInternalQueue_By_RunExecutable(self):
            return self._IsIncludingExecStep(_ERblExecStepID.eCustomManagedInternalQueue_By_RunExecutable)

        @property
        def isIncludingCustomManagedInternalQueue_By_AutoManagedExternalQueue(self):
            return self._IsIncludingExecStep(_ERblExecStepID.eCustomManagedInternalQueue_By_AutoManagedExternalQueue)

        @property
        def isIncludingAutoManagedInternalQueue_By_RunExecutable(self):
            return self._IsIncludingExecStep(_ERblExecStepID.eAutoManagedInternalQueue_By_RunExecutable)

        @property
        def isIncludingAutoManagedInternalQueue_By_AutoManagedExternalQueue(self):
            return self._IsIncludingExecStep(_ERblExecStepID.eAutoManagedInternalQueue_By_AutoManagedExternalQueue)

        def _IsIncludingExecStep(self, eExecStepID_ : _ERblExecStepID) -> bool:
            res = False
            if self.__ds is None:
                pass
            elif not isinstance(eExecStepID_, _ERblExecStepID):
                pass
            elif not eExecStepID_ in self.__ds:
                pass
            else:
                res = self.__ds[eExecStepID_]
            return res

        def _ToString(self):
            if self.__ds is None:
                return None

            res = _CommonDefines._STR_EMPTY
            if logif._IsReleaseModeEnabled():
                return res

            for _kk, _vv in self.__ds.items():
                if _vv:
                    res += '\t{}\n'.format(_kk.compactName)
            return res

        def _CleanUp(self):
            if self.__ds is not None:
                self.__ds.clear()
                self.__ds = None

    class _RunnableExecutorTable(_AbsSlotsObject):
        __slots__ = [ '__dx' ]

        def __init__(self, dictExecutors_ : dict):
            self.__dx = dictExecutors_
            super().__init__()

        def _GetApiExecutor(self, fid_ : _ERblApiFuncTag):
            res = None
            if self.__dx is None:
                pass
            elif not isinstance(fid_, _ERblApiFuncTag):
                pass
            elif fid_ not in self.__dx:
                pass
            else:
                res = self.__dx[fid_]
            return res

        def _CleanUp(self):
            if self.__dx is not None:
                for _vv in self.__dx.values():
                    _vv.CleanUp()
                self.__dx.clear()
                self.__dx = None

    class _ARBackLogEntry(_AbsSlotsObject):
        __slots__  = [ '__m' , '__cb' , '__bC' , '__bX' , '__uid' , '__dm' , '__dp' , '__cdcb' ]

        _FwDispInst = None

        def __init__(self, bXMsg_ : bool, msgUID_ : int, msgDump_ : bytes, pldDump_ =None, bCustomPL_ =None, customDesCB_ =None, callback_ : _FwCallable =None):
            super().__init__()
            self.__m    = None
            self.__bC   = bCustomPL_
            self.__bX   = bXMsg_
            self.__cb   = callback_
            self.__dm   = msgDump_
            self.__dp   = pldDump_
            self.__uid  = msgUID_
            self.__cdcb = customDesCB_

        @property
        def _message(self) -> _IFwMessage:
            if _AbsRunnable._ARBackLogEntry._FwDispInst is None:
                return None
            if self.__uid is None:
                return None
            if self.__m is not None:
                return self.__m

            self.__m = _AbsRunnable._ARBackLogEntry._FwDispInst._DeserializeMsg(self.__bX, self.__uid, self.__dm, pldDump_=self.__dp, bCustomPL_=self.__bC, customDesCB_=self.__cdcb)
            return self.__m

        @property
        def _msgUID(self):
            return self.__uid

        @property
        def _sortKey(self):
            return abs(self.__uid)

        @property
        def _callback(self):
            return self.__cb

        def _ToString(self):
            pass

        def _CleanUp(self):
            if self.__dm is None:
                return

            _bSerDes = False
            if self.__m is not None:
                _msgPld = self.__m.AttachPayload(None)
                if _msgPld is not None:
                    _bSerDes = _msgPld.isMarshalingRequired
                    if _bSerDes:
                        if isinstance(_msgPld, XPayload):
                            _msgPld.DetachContainer()
                self.__m.CleanUp()

            if self.__dp is not None:
                if self.__bC and _bSerDes:
                    del self.__dp
            del self.__dm

            self.__m    = None
            self.__bC   = None
            self.__bX   = None
            self.__cb   = None
            self.__dm   = None
            self.__dp   = None
            self.__uid  = None
            self.__cdcb = None

    @classmethod
    def GetMCApiMNL(cls_):
        return cls_._GetMCApiMNL()

    __slots__ = [ '__a' , '__s' ,  '__xq' , '__iq' , '__md' , '__ag' , '__t' , '__utc' , '__rn' , '__tp' , '__xp' , '__xtors' , '__xc' , '__cbr' , '__ft' ]  #, '__axt' ]

    __FwDispRbl = None

    __XR_XCP_DW = _FwTDbEngine.GetText(_EFwTextID.eMisc_XML_RUNNER_XCP_MSG_DuplicateWriter)

    def __init__( self
                , rblType_     : _ERblType       =None
                , utaskConn_   : _IUTaskConn     =None
                , rblXM_       : _ERblApiFuncTag =None
                , runLogAlert_ : _TimeAlert      =None
                , txCard_      : _TaskXCard      =None
                , doSkipSetup_                   =False):
        self.__a     = None
        self.__s     = None
        self.__t     = None
        self.__ag    = None
        self.__iq    = None
        self.__md    = None
        self.__rn    = None
        self.__ft    = None
        self.__tp    = None
        self.__xc    = None
        self.__xp    = None
        self.__xq    = None
        self.__cbr   = None
        self.__utc   = None
        self.__xtors = None

        _AbsFwXUnit.__init__(self)
        _PcErrHandler.__init__(self)
        _IDispAgent.__init__(self)

        if doSkipSetup_:
            return

        if rblType_ is None:
            rblType_ = _ERblType.eUserRbl

        _bErr = False
        if not isinstance(rblType_, _ERblType):
            _bErr = True
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00091)
        elif (runLogAlert_ is not None) and not isinstance(runLogAlert_, _TimeAlert):
            _bErr = True
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00092)
        elif (txCard_ is not None) and not (isinstance(txCard_, _TaskXCard) and txCard_.isValid):
            _bErr = True
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00093)
        else:
            if txCard_ is None:
                txCard_ = _TaskXCard()
            else:
                txCard_ = txCard_._Clone()

            _utc = utaskConn_
            if rblType_.isXTaskRunnable or (_utc is not None):
                if not (rblType_.isXTaskRunnable and isinstance(_utc, _IUTaskConn)):
                    _bErr = True
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00095)
                else:
                    _uta = utaskConn_._utAgent
                    if not (isinstance(_uta, _IUTAgent) and _uta.isAttachedToFW):
                        _bErr = True
                        vlogif._LogOEC(True, _EFwErrorCode.VFE_00096)

        if not _bErr:
            if _ssshare._IsSubsysMsgDisabled():
                if rblXM_ is None:
                    rblXM_ = _ERblApiFuncTag.DefaultApiMask()
                rblXM_ = _ERblApiFuncTag.AddApiFuncTag(rblXM_, _ERblApiFuncTag.eRFTProcessExternalMsg)
                rblXM_ = _ERblApiFuncTag.AddApiFuncTag(rblXM_, _ERblApiFuncTag.eRFTProcessInternalMsg)
                rblXM_ = _ERblApiFuncTag.AddApiFuncTag(rblXM_, _ERblApiFuncTag.eRFTProcessExternalQueue)
                rblXM_ = _ERblApiFuncTag.AddApiFuncTag(rblXM_, _ERblApiFuncTag.eRFTProcessInternalQueue)

        if not _bErr:
            if (rblXM_ is not None) and not isinstance(rblXM_, _ERblApiFuncTag):
                _bErr = True
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00098)

        if not _bErr:
            self.__ag = _ARblApiGuide(self, rblXM_)
            if self.__ag.apiMask is None:
                _bErr = True
            else:
                if rblType_.isFwMainRunnable:
                    _bErr =          not self.__ag.isProvidingRunCeaseIteration
                    _bErr = _bErr or not self.__ag.isProvidingPrepareCeasing
                    _bErr = _bErr or not self.__ag.isProvidingProcFwcErrorHandlerCallback
                    if _bErr:
                        vlogif._LogOEC(True, _EFwErrorCode.VFE_00099)

                if not _bErr:
                    if not self.__CheckMutuallyExclusiveAPI():
                        _bErr = True
                    else:
                        self.__CreateExecPlan()
                        if self.__xp is None:
                            _bErr = True
                        else:
                            self.__CreateExecutorTable(rblType_.isXTaskRunnable)
                            if self.__xtors is None:
                                _bErr = True

        if _bErr:
            if self.__xtors is not None:
                self.__xtors.CleanUp()
                self.__xtors = None
            if self.__xp is not None:
                self.__xp.CleanUp()
                self.__xp = None
            if self.__ag.apiMask is not None:
                self.__ag.CleanUp()
                self.__ag = None

            _PcErrHandler._CleanUp(self)
            self.CleanUp()
        else:
            self.__a   = runLogAlert_
            self.__t   = rblType_
            self.__md  = _Mutex()
            self.__xc  = txCard_
            self.__utc = utaskConn_

            if rblType_.isFwDispatcherRunnable:
                _AbsRunnable.__FwDispRbl = self
                _AbsRunnable._ARBackLogEntry._FwDispInst = self

    def __eq__(self, other_):
        return (other_ is not None) and (id(self) == id(other_))

    @property
    def _isAttachedToFW(self) -> bool:
        return (self.__t is not None) and (self.__dtaskProfile is not None)

    @property
    def _isStarted(self) -> bool:
        res =  self.__ft is not None
        res = res and self.__ft.isStarted
        return res

    @property
    def _isPendingRun(self) -> bool:
        res =  self.__ft is not None
        res = res and self.__ft.isRunning
        return res

    @property
    def _isRunning(self) -> bool:
        res =  self.__ft is not None
        res = res and self.__ft.isRunning
        return res

    @property
    def _isDone(self):
        res =  self.__ft is not None
        res = res and self.__ft.isDone
        return res

    @property
    def _isCanceled(self):
        res =  self.__ft is not None
        res = res and self.__ft.isCanceled
        return res

    @property
    def _isFailed(self) -> bool:
        res =  self.__ft is not None
        res = res and self.__ft.isFailed
        return res

    @property
    def _isStopping(self):
        res =  self.__ft is not None
        res = res and self.__ft.isStopping
        return res

    @property
    def _isCanceling(self):
        res =  self.__ft is not None
        res = res and self.__ft.isCanceling
        return res

    @property
    def _isAborting(self):
        res =  self.__ft is not None
        res = res and self.__ft.isAborting
        return res

    @property
    def _isTerminated(self) -> bool:
        res =  self.__ft is not None
        res = res and self.__ft.isTerminated
        return res

    @property
    def _isTerminating(self) -> bool:
        res =  self.__ft is not None
        res = res and self.__ft.isTerminating
        return res

    @property
    def _taskUID(self) -> int:
        return self.__taskID

    @property
    def _taskName(self) -> str:
        return self._runnableName

    @property
    def _taskProfile(self) -> ITaskProfile:
        return None if self.__utc is None else self.__utc._taskProfile

    @override
    def _Start(self, *args_, **kwargs_):
        return self.__StartRunnable()

    @override
    def _Stop(self, bCancel_=False, bCleanupDriver_ =True):
        self.__StopRunnable(bCancel_=False, bCleanupDriver_=bCleanupDriver_)

    @override
    def _Join(self, timeout_: Union[int, float, None] =None):
        self.__JoinRunnable(timeout_=timeout_)

    @override
    def _SelfCheck(self) -> bool:
        if self._isInvalid:
            return False
        if self.__ft is None:
            return True
        return not self.__ft._SelfCheckTask()._isScrNOK

    @override
    def _ToString(self, bCompact_ =True):
        if self._isInvalid:
            return type(self).__name__

        _tb = self.taskBadge
        if (_tb is None) and (self.__dtaskProfile is None):
            return type(self).__name__

        if _tb is not None:
            res = _tb.ToString(bCompact_=bCompact_)
        else:
            res = self.__dtaskProfile.dtaskName

        if res is None:
            res = type(self).__name__
        else:
            res = _FwTDbEngine.GetText(_EFwTextID.eMisc_TNPrefix_Runnable) + res
        return res

    @property
    def isProvidingRunExecutable(self):
        return False if self.__ag is None else self.__ag.isProvidingRunExecutable

    @property
    def isProvidingSetUpRunnable(self):
        return False if self.__ag is None else self.__ag.isProvidingSetUpRunnable

    @property
    def isProvidingTearDownRunnable(self):
        return False if self.__ag is None else self.__ag.isProvidingTearDownRunnable

    @property
    def isProvidingOnTimeoutExpired(self):
        return False if self.__ag is None else self.__ag.isProvidingOnTimeoutExpired

    @property
    def isProvidingOnRunProgressNotification(self):
        return False if self.__ag is None else self.__ag.isProvidingOnRunProgressNotification

    @property
    def isProvidingProcFwcTENotification(self):
        return False if self.__ag is None else self.__ag.isProvidingProcFwcTENotification

    @property
    def isProvidingProcFwcErrorHandlerCallback(self):
        return False if self.__ag is None else self.__ag.isProvidingProcFwcErrorHandlerCallback

    @property
    def isProvidingRunCeaseIteration(self):
        return False if self.__ag is None else self.__ag.isProvidingRunCeaseIteration

    @property
    def isProvidingPrepareCeasing(self):
        return False if self.__ag is None else self.__ag.isProvidingPrepareCeasing

    @property
    def isProvidingInternalQueue(self):
        return self.isProvidingProcessInternalQueue or  self.isProvidingProcessInternalMsg

    @property
    def isProvidingProcessInternalQueue(self):
        return False if self.__ag is None else self.__ag.isProvidingProcessInternalQueue

    @property
    def isProvidingProcessInternalMsg(self):
        return False if self.__ag is None else self.__ag.isProvidingProcessInternalMsg

    @property
    def isProvidingCustomManagedInternalQueue(self):
        return self.isProvidingProcessInternalQueue

    @property
    def isProvidingAutoManagedInternalQueue(self):
        return self.isProvidingProcessInternalMsg

    @property
    def isProvidingExternalQueue(self):
        return self.isProvidingProcessExternalQueue or self.isProvidingProcessExternalMsg

    @property
    def isProvidingProcessExternalQueue(self):
        return False if self.__ag is None else self.__ag.isProvidingProcessExternalQueue

    @property
    def isProvidingProcessExternalMsg(self):
        return False if self.__ag is None else self.__ag.isProvidingProcessExternalMsg

    @property
    def isProvidingCustomManagedExternalQueue(self):
        return self.isProvidingProcessExternalQueue

    @property
    def isProvidingAutoManagedExternalQueue(self):
        return self.isProvidingProcessExternalMsg

    @override
    def _ProcErrorHandlerCallback( self
                                 , cbID_   : _EPcErrHandlerCBID
                                 , curFE_  : _FatalLog =None
                                 , lstFFE_ : list      =None) -> _EExecutionCmdID:
        if self.isProvidingProcFwcErrorHandlerCallback:
            res = self.__ag.procFwcErrorHandlerCallback(cbID_=cbID_, curFE_=curFE_, lstFFE_=lstFFE_)
        else:
            res = self.__ProcErrHdlrCallback(cbID_, curFE_=curFE_)
        return res

    @override
    def _PcIsMonitoringLcModeChange(self) -> bool:
        _tskSID = None if self.__ft is None else self.__ft.dtaskStateID
        return False if _tskSID is None else (_tskSID.isRunning or _tskSID.isStopping)

    @override
    def _PcClientName(self) -> str:
        return self._runnableName

    @override
    def _PcSelfCheck(self) -> _ETaskSelfCheckResultID:
        return self.__EvaluateSelfCheck()

    @override
    def _PcSetLcProxy(self, lcPxy_, bForceUnset_ =False):
        if not self._PcIsLcProxySet():
            _LcProxyClient._PcSetLcProxy(self, lcPxy_, bForceUnset_=bForceUnset_)
            if self._PcIsLcProxySet():
                if self.__utc is not None:
                    self.__utc._PcSetLcProxy(self, bForceUnset_=bForceUnset_)

    @override
    def _PcOnLcCeaseModeDetected(self) -> _EExecutionCmdID:
        if self._isInvalid:
            return _EExecutionCmdID.Abort()

        res = _EExecutionCmdID.Abort() if self._isAborting else _EExecutionCmdID.Stop()

        if not self._isInLcCeaseMode:
            self._CreateCeaseTLB(bEnding_=res.isAbort)
        else:
            self._UpdateCeaseTLB(res.isAbort)
        return res

    @override
    def _PcOnLcFailureDetected(self) -> _EExecutionCmdID:
        if self._isInvalid:
            return _EExecutionCmdID.Abort()

        res = _EExecutionCmdID.Abort() if self._isAborting else _EExecutionCmdID.Stop()

        if not res.isAbort:
            _bOwnLcFailureSet = False

            _ePF = self._GetProcessingFeasibility()
            if not _ePF.isFeasible:
                if not (_ePF.isInCeaseMode or _ePF.isOwnLcCompFailureSet):
                    res = _EExecutionCmdID.Abort()

                elif _ePF.isInCeaseMode:
                    pass

                else:
                    _bOwnLcFailureSet = True

            if not res.isAbort:
                if not _bOwnLcFailureSet:
                    if self._PcHasLcAnyFailureState():
                        _bOwnLcFailureSet = self._PcHasLcCompAnyFailureState(self.__t.toLcCompID, atask_=self.__ft)

                if _bOwnLcFailureSet:
                    res = _EExecutionCmdID.Abort()

        if not self._isInLcCeaseMode:
            self._CreateCeaseTLB(bEnding_=res.isAbort)
        else:
            self._UpdateCeaseTLB(res.isAbort)
        return res

    @override
    def _PcOnLcPreShutdownDetected(self) -> _EExecutionCmdID:
        if self._isInvalid:
            return _EExecutionCmdID.Abort()

        res = _EExecutionCmdID.Abort() if self._isAborting else _EExecutionCmdID.Stop()

        if not res.isAbort:
            _bOwnLcFailureSet = False

            _ePF = self._GetProcessingFeasibility()
            if not _ePF.isFeasible:
                if not (_ePF.isInCeaseMode or _ePF.isOwnLcCompFailureSet):
                    res = _EExecutionCmdID.Abort()

                elif _ePF.isInCeaseMode:
                    pass

                else:
                    _bOwnLcFailureSet = True

            if not res.isAbort:
                if not _bOwnLcFailureSet:
                    if self._PcHasLcAnyFailureState():
                        _bOwnLcFailureSet = self._PcHasLcCompAnyFailureState(self.__t.toLcCompID, atask_=self.__ft)

                if _bOwnLcFailureSet:
                    res = _EExecutionCmdID.Abort()

        if not self._isInLcCeaseMode:
            self._CreateCeaseTLB(bEnding_=res.isAbort)
        else:
            self._UpdateCeaseTLB(res.isAbort)
        return res

    @override
    def _PcOnLcShutdownDetected(self) -> _EExecutionCmdID:
        if self._isInvalid:
            return _EExecutionCmdID.Abort()

        res = _EExecutionCmdID.Abort() if self._isAborting else _EExecutionCmdID.Stop()

        if not self._isInLcCeaseMode:
            self._CreateCeaseTLB(bEnding_=True)
        else:
            self._UpdateCeaseTLB(self.isAborting)
        return res

    @property
    def _isOperating(self) -> bool:
        return not (self._isInvalid or self._isInLcCeaseMode or self._isTerminated or self._isTerminating)

    @property
    def _isFwAgent(self) -> bool:
        return False if self._isInvalid else self.__t.isFwRunnable

    @property
    def _isXTaskAgent(self) -> bool:
        return False if self._isInvalid else self.__t.isXTaskRunnable

    @property
    def _agentTaskID(self) -> int:
        return self.__taskID

    @property
    def _agentName(self) -> str:
        return self._runnableName

    def _PushMessage(self, msg_: _IFwMessage, msgDump_: bytes, pldDump_=None, bCustomPL_=None, customDesCB_=None, callback_: _FwCallable =None) -> _EExecutionCmdID:
        _bAbort = False
        if self._isInvalid or self._isInLcCeaseMode:
            _bAbort = True
        elif not self.isRunning:
            if not self.isStopping:
                _bAbort = True
            elif not self._GetTaskApiContext().isTeardown:
                _bAbort = True

        if _bAbort:
            return _EExecutionCmdID.Abort()

        _bl = _AbsRunnable._ARBackLogEntry(msg_.isXcoMsg, msg_.uniqueID, msgDump_, pldDump_=pldDump_, bCustomPL_=bCustomPL_, customDesCB_=customDesCB_, callback_=callback_)
        if not self.__xq.PushNowait(_bl):
            _bl.CleanUp()
            if self.isRunning:
                if self.__xq.qsize == self.__xq.capacity:
                    logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_AbsRunnable_TID_002).format(self.__taskID, msg_.uniqueID))
            res = _EExecutionCmdID.NOK()
        else:
            res = _EExecutionCmdID.OK()
        return res

    @property
    def isAborting(self):
        return self._isAborting

    @property
    def xrNumber(self) -> int:
        return self._xrNumber

    @property
    def taskBadge(self):
        res = self.__ft
        if res is not None:
            res = res.taskBadge
        return res

    @property
    def taskError(self):
        res = self.__ft
        if res is not None:
            res = res.taskError
        return res

    def OnTimeoutExpired(self, timer_, *args_, **kwargs_) -> _EExecutionCmdID:
        if not self.isRunning:
            return _EExecutionCmdID.Stop()
        if not self.__ag.isProvidingOnTimeoutExpired:
            _midPart = _ERblApiFuncTag.eRFTOnTimeoutExpired.functionName
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00100)
            return _EExecutionCmdID.Abort()

        _xtor = self.__xtors._GetApiExecutor(_ERblApiFuncTag.eRFTOnTimeoutExpired)
        _xtor.SetExecutorParams(param1_=timer_, args_=args_, kwargs_=kwargs_)
        _xres = self.__EvaluateExecResult(executor_=_xtor, bCheckBefore_=False, abortState_=_TaskState._EState.eTimerProcessingAborted)
        return _xres

    @property
    def _isInvalid(self) -> bool:
        return self.__t is None

    @property
    def _isStartable(self):
        if self.__ft is None:
            res = not self.__tp is None
        else:
            res  = True
            res &= self.__ft.isInitialized
            res &= not self.__ft.isStarted
        return res

    @property
    def _isAlive(self):
        res =  self.__ft is not None
        res = res and self.__ft.isAlive
        return res

    @property
    def _isPendingStopRequest(self) -> bool:
        res =  self.__ft is not None
        res = res and self.__ft.isPendingStopRequest
        return res

    @property
    def _isPendingCancelRequest(self) -> bool:
        res =  self.__ft is not None
        res = res and self.__ft.isPendingCancelRequest
        return res

    @property
    def _isInLcCeaseMode(self):
        return not self.__lcCeaseState.isNone

    @property
    def _isSelfManagingInternalQueue(self):
        return False

    @property
    def _isSelfManagingExternalQueue(self):
        return False

    @property
    def _isReturnedXCmdAbort(self):
        return (self.__ag is not None) and (self.__ag._xcmdReturn is not None) and self.__ag._xcmdReturn.isAbort

    @property
    def _rblType(self) -> _ERblType:
        return self.__t

    @property
    def _rblTask(self):
        return self.__ft

    @property
    def _dtaskName(self):
        res = self.taskBadge
        if res is not None:
            res = res.dtaskName
        return res

    @property
    def _runnableName(self):
        if self.__t is None:
            return type(self).__name__
        if self.__rn is None:
            self.__UpdateRunnableName()
        return self.__rn

    @property
    def _xcard(self) -> _TaskXCard:
        return self.__xc

    @property
    def _utConn(self) -> _IUTaskConn:
        return self.__utc

    @property
    def _utAgent(self) -> Union[_IUTAgent, None]:
        return None if self.__utc is None else self.__utc._utAgent

    @property
    def _iqueue(self):
        return self.__iq

    @property
    def _xqueue(self):
        return self.__xq

    @property
    def _xrNumber(self) -> int:
        return 0 if self.__ft is None else self.__ft.xrNumber

    @property
    def _lcDynamicTLB(self) -> _LcDynamicTLB:
        if self.__ft is None:
            res = None
        else:
            res = self.__ft.lcDynamicTLB
        return res

    @property
    def _lcCeaseTLB(self) -> _LcCeaseTLB:
        if self.__ft is None:
            res = None
        else:
            res = self.__ft.lcCeaseTLB
        return res

    @staticmethod
    def _GetMCApiMNL():
        return None

    def _CleanUp(self):
        if self._isInvalid:
            return

        _myMtx    = self.__md
        _bFlagSet = self._isInLcCeaseMode
        _PcErrHandler._CleanUp(self)

        with _myMtx:
            if self.__cbr is not None:
                self.__cbr.CleanUp()
            if self.__xc is not None:
                self.__xc.CleanUp()
            if self.__xtors is not None:
                self.__xtors.CleanUp()
            if self.__xp is not None:
                self.__xp.CleanUp()
            if self.__ag is not None:
                self.__ag.CleanUp()
            if self.__utc is not None:
                self.__utc._DisconnectUTask()
                self.__utc.CleanUp()

            self.__a     = None
            self.__s     = None
            self.__t     = None
            self.__ag    = None
            self.__iq    = None
            self.__md    = None
            self.__rn    = None
            self.__ft    = None
            self.__tp    = None
            self.__xc    = None
            self.__xp    = None
            self.__xq    = None
            self.__cbr   = None
            self.__utc   = None
            self.__xtors = None

        if not _bFlagSet:
            _myMtx.CleanUp()

    def _IncEuRNumber(self):
        if self.__ft is None: return
        self.__ft._IncEuRNumber()

        if self.__utc is None: return
        self.__utc._IncEuRNumber()

    def _GetTaskXPhase(self) -> _ETaskXPhaseID:
        if self.__ft is None:
            return _ETaskXPhaseID.eNA
        return self.__ft.taskXPhase

    def _GetTaskApiContext(self) -> _ETaskApiContextID:
        if self.__ft is None:
            return _ETaskApiContextID.eDontCare
        return self.__ft.taskApiContext

    def _GetDataMutex(self):
        return self.__md

    def _RblSetTaskXPhase(self, xphaseID_ : _ETaskXPhaseID):
        if self.__ft is None:
            return
        self.__ft._SetTaskXPhase(xphaseID_)

    def _RblSetTaskAContext(self, eACtxID_ : _ETaskApiContextID):
        if self.__ft is None:
            return
        self.__ft._SetTaskApiContext(eACtxID_)

    def _RblSetTask(self, fwtask_ : _AbsFwTask):
        if fwtask_ is None:
            self.__ft = None
            return

        if self.__ft is not None:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00101)
            return
        if self.__tp is None:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00102)
            return
        if id(fwtask_._daprofile) != id(self.__tp):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00103)
            return
        if (fwtask_.taskError is None) or fwtask_.taskError.isFatalError or fwtask_.taskError.isNoImpactFatalErrorDueToFrcLinkage:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00104)
            return

        self.__ft = fwtask_

        _PcErrHandler._SetUpPcEH(self, self.__md)
        if self._isForeignErrorListener is None:
            self.__ft = None
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00105)

        else:
            self.__UpdateRunnableName()
            self.__xc._UpdateUniqueName(self._runnableName)
        if not self.__t.isXTaskRunnable:
            self.__xc._SetStartArgs(*tuple(self.__tp.args), **self.__tp.kwargs)

    def _RblSetTaskProfile(self, fwtPrf_ : _AbsFwProfile):
        if fwtPrf_ is None:
            self.__iq = None
            self.__xq = None
            self.__tp = None
            return

        if not fwtPrf_.isValid:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00106)
            return
        if self.__tp is not None:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00107)
            return
        if self.__ft is not None:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00108)
            return

        _intQueue = None
        _extQueue = None
        if not _ssshare._IsSubsysMsgDisabled():
            _intQueue  = fwtPrf_.internalQueue
            _extQueue  = fwtPrf_.externalQueue
            _bIntQueue = _intQueue is not None
            _bExtQueue = _extQueue is not None

            if _bIntQueue != self.isProvidingInternalQueue or _bExtQueue != self.isProvidingExternalQueue:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00109)
                return

            if not self.__t.isFwDispatcherRunnable:
                if _bExtQueue:
                    self.__cbr = _DispatchRegistry(bTaskRegistry_=False)

        self.__iq = _intQueue
        self.__xq = _extQueue
        self.__tp = fwtPrf_

        self.__UpdateRunnableName()
        self.__xc._UpdateUniqueName(self._runnableName)

    def _RblSetStopSyncSem(self, semStop_ : _BinarySemaphore):
        if self._isInvalid:
            return
        with self.__ft._tstMutex:
            self.__s = semStop_

    def _SetTaskState(self, newState_ : _TaskState._EState) -> Union[_TaskState._EState, None]:
        if not _Util.IsInstance(newState_, _TaskState._EState, bThrowx_=True):
            return None

        if (self.__ft is None) or (self.__ft.taskBadge is None):
            return None

        if newState_.value < _TaskState._EState.eProcessingCanceled.value:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00110)
            return None

        if not self.isTerminating:
            if not self.__t.isFwDispatcherRunnable:
                self.__DeregDefaultDispatchFilter()

        res = self.__ft._CheckSetTaskState(newState_)
        return res

    def _CreateCeaseTLB(self, bEnding_ =False) -> _LcCeaseTLB:
        if self.__ft is None:
            res = None
        else:
            res =_AbsFwTask.CreateLcCeaseTLB(self.__ft, self.__md, bEnding_)
        return res

    def _UpdateCeaseTLB(self, bEnding_ : bool):
        _ctlb = self._lcCeaseTLB
        if _ctlb is not None:
            _ctlb.UpdateCeaseState(bEnding_)

    def _OnTENotification(self, errLog_: _ErrorLog) -> bool:
        if self._isInvalid:
            return False
        if self._isInLcCeaseMode:
            return False

        _ePF = self._GetProcessingFeasibility(errLog_=errLog_)
        if not _ePF.isFeasible:
            return False

        res = self._AddError(errLog_)
        if not res:
            pass
        elif not self.taskBadge.hasFwTaskRight:
            pass
        elif self.isProvidingProcFwcTENotification:
            self.__ag.procFwcTENotification(errLog_=errLog_)
        return res

    def _GetProcessingFeasibility(self, errLog_: _ErrorLog =None) -> _EProcessingFeasibilityID:
        res = _EProcessingFeasibilityID.eFeasible

        if self._isInvalid:
            res = _EProcessingFeasibilityID.eUnfeasible
        elif self._PcIsLcProxyModeShutdown():
            res = _EProcessingFeasibilityID.eLcProxyUnavailable
        elif not self._PcIsLcCoreOperable():
            res = _EProcessingFeasibilityID.eLcCoreInoperable
        elif self._isAborting:
            res = _EProcessingFeasibilityID.eAborting
        elif self._isInLcCeaseMode:
            if not self.__t.isFwMainRunnable:
                res = _EProcessingFeasibilityID.eInCeaseMode
            elif not self.__lcCeaseState.isCeasing:
                res = _EProcessingFeasibilityID.eInCeaseMode

        _frcv = None
        if res.isFeasible:
            if self._PcHasLcAnyFailureState():
                _frcv = self._PcGetLcCompFrcView(self.__t.toLcCompID, atask_=self.__ft)
                if _frcv is not None:
                    res = _EProcessingFeasibilityID.eOwnLcCompFailureSet

            if res.isFeasible:
                if (errLog_ is not None) and errLog_.hasNoErrorImpact:
                    res = _EProcessingFeasibilityID.eUnfeasible

        if not res.isFeasible:
            if errLog_ is not None:
                if errLog_.IsMyTaskError(self.__taskID):
                    errLog_._UpdateErrorImpact(_EErrorImpact.eNoImpactByOwnerCondition)
        if _frcv is not None:
            _frcv.CleanUp()
        return res

    def _SendMessage(self, msg_ : _IFwMessage) -> bool:
        if _ssshare._WarnOnDisabledSubsysMsg():
            return False
        if (msg_ is None) or not msg_.isValid:
            return False
        if self._isInvalid or self._isInLcCeaseMode or self.isAborting or not self.isStarted:
            return False

        _hdr = msg_.header

        if not (_hdr.typeID.isTIntraProcess and (_hdr.channelID.isChInterTask or _hdr.channelID.isChIntraTask)):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00111)
            return False

        if _hdr.isInternalMsg:
            if not self.isRunning:
                return False
            if not _FwSubsysCoding.IsInternalQueueSupportEnabled():
                return False
            if not self.isProvidingInternalQueue:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00112)
                return False
            if self.__iq.isFull:
                logif._LogErrorEC(_EFwErrorCode.UE_00067, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_AbsRunnable_TID_001).format(self.__taskID, self.__iq.qsize))
                return False
            return self.__iq.PushNowait(msg_)

        _actx = self._GetTaskApiContext()
        if not (self.isRunning or (self.isStopping and _actx.isTeardown)):
            return False

        if not self.isProvidingExternalQueue:
            if _FwSubsysCoding.IsSenderExternalQueueSupportMandatory():
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00939)
                return False

        return _AbsRunnable.__FwDispRbl._DispatchMessage(msg_)

    def _TriggerQueueProc(self, bExtQueue_ : bool) -> int:
        if _ssshare._WarnOnDisabledSubsysMsg():
            return -1
        if self._isInvalid or self._isInLcCeaseMode:
            return -1
        if not bExtQueue_:
            if not self.isProvidingInternalQueue:
                return -1
        if not self.isProvidingExternalQueue:
            return -1

        _actx = self._GetTaskApiContext()

        if not self.isRunning:
            _bIgnore = self.isStopping and _actx.isTeardown
            if _bIgnore:
                _midPart = _FwTDbEngine.GetText(_EFwTextID.eMisc_QueueType_External) if bExtQueue_ else _FwTDbEngine.GetText(_EFwTextID.eMisc_QueueType_Internal)
                logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_AbsRunnable_TID_006).format(self.__taskID, _midPart))
            return 0 if _bIgnore else -1

        if _actx.isDontCare:
            _midPart = _FwTDbEngine.GetText(_EFwTextID.eMisc_QueueType_External) if bExtQueue_ else _FwTDbEngine.GetText(_EFwTextID.eMisc_QueueType_Internal)
            logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_AbsRunnable_TID_003).format(self.__taskID, _midPart))
            return 0
        if _actx.isProcessingQueue:
            _midPart = _FwTDbEngine.GetText(_EFwTextID.eMisc_QueueType_External) if bExtQueue_ else _FwTDbEngine.GetText(_EFwTextID.eMisc_QueueType_Internal)
            logif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_AbsRunnable_TID_004).format(self.__taskID, _midPart))
            return 0

        if not bExtQueue_:
            _iqSize = self.__iq.qsize
            self.__ExecuteAutoManagedIntQueue()
            return max(0, _iqSize - self.__iq.qsize)

        self._RblSetTaskAContext(_ETaskApiContextID.eProcExtQueue if bExtQueue_ else _ETaskApiContextID.eProcIntQueue)

        _blNum = self.__xq.qsize
        if _blNum < 1:
            self._RblSetTaskAContext(_actx)
            return 0

        _ii, _lstBL = _blNum, []
        while _ii > 0:
            _bl = self.__xq.PopNowait()
            if _bl is None:
                break
            _lstBL.append(_bl)
            _ii -= 1

        _blNum = len(_lstBL)
        if _blNum < 1:
            self._RblSetTaskAContext(_actx)
            return 0

        _lstBL = sorted(_lstBL, key=lambda _bl: _bl._sortKey)

        res   = 0
        _xres = _EExecutionCmdID.Continue()
        _xtor = self.__xtors._GetApiExecutor(_ERblApiFuncTag.eRFTProcessExternalMsg)

        _eXPh = self._GetTaskXPhase()

        for _bl in _lstBL:
            _xres = _EExecutionCmdID.MapExecState2ExecCmdID(self)

            if not _xres.isContinue:
                break

            _msg = _bl._message
            if _msg is None:
                continue

            _msg2 = _msg
            if _msg.isXcoMsg:
                _msg2 = XMessage(_msg)

            _xtor.SetExecutorParams(param1_=_msg2, param2_=_bl._callback)
            _xres = self.__EvaluateExecResult(executor_=_xtor, bCheckBefore_=False)

            res += 1

            if _msg.isXcoMsg:
                _msg2._Detach()

        for _bl in _lstBL:
            _bl.CleanUp()

        self._RblSetTaskAContext(_actx)

        self._RblSetTaskXPhase(_eXPh)

        return res

    def _Run(self, semStart_):
        _caughtXcp = False

        _bInclSetup = self.__xp.isIncludingSetUpExecutable

        try:
            self._RblSetTaskXPhase(_ETaskXPhaseID.eFwHandling)
            self.__ExecutePreRun(semStart_)
            if self.isRunning:
                if _bInclSetup:
                    self.__NotifyRunProgress(_ERunProgressID.eReadyToRun)

                    if self.isRunning:
                        self._RblSetTaskAContext(_ETaskApiContextID.eSetup)
                        self.__ExecuteSetup()
                        self._RblSetTaskAContext(_ETaskApiContextID.eDontCare)

                if self.isRunning:
                    if _bInclSetup:
                        self.__NotifyRunProgress(_ERunProgressID.eExecuteSetupDone)
                    else:
                        self.__NotifyRunProgress(_ERunProgressID.eReadyToRun)

                    if self.isRunning:
                        self._RblSetTaskAContext(_ETaskApiContextID.eRun)
                        self.__ExecuteRun()
                        self._RblSetTaskAContext(_ETaskApiContextID.eDontCare)

                        if not self._isAborting:
                            if self.isRunning:
                                self.__NotifyRunProgress(_ERunProgressID.eExecuteRunDone)

                            if not self._isInLcCeaseMode:
                                if not self._lcDynamicTLB.isLcShutdownEnabled:
                                    if self.__xp.isIncludingTeardownExecutable:
                                        self._RblSetTaskAContext(_ETaskApiContextID.eTeardown)
                                        self.__ExecuteTeardown()
                                        self._RblSetTaskAContext(_ETaskApiContextID.eDontCare)

                                        self.__NotifyRunProgress(_ERunProgressID.eExecuteTeardownDone)

                if not self._isAborting:
                    self.__NotifyRunProgress(_ERunProgressID.eRunDone)

        except _XcoXcpRootBase as _xcp:
            _caughtXcp = True
            self.__HandleException(_xcp, bCaughtByApiExecutor_=False)

        except BaseException as _xcp:
            _caughtXcp = True
            _xcp = _XcoBaseException(_xcp, tb_=logif._GetFormattedTraceback())
            self.__HandleException(_xcp, bCaughtByApiExecutor_=False)

        finally:
            if self._isInvalid:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00114)
            else:
                if not self._isTerminating:
                    if _caughtXcp:
                        _st = _TaskState._EState.eProcessingAborted
                    else:
                        _st = _TaskState._EState.eProcessingStopped

                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00565)
                    self._SetTaskState(_st)

                _semStop = None
                with self.__ft._tstMutex:
                    if self.__s is not None:
                        _semStop = self.__s
                        self.__s = None

                if _semStop is not None:
                    _semStop.Give()

                if self._isTerminated:
                    if self.__t.isXTaskRunnable:
                        if self.__xp.isIncludingTeardownExecutable:
                            self._PcGetTTaskMgr()._DetachTask(self.__ft)

                self.__PreProcessCeaseMode()

                self.__ProcessCeaseMode()

    def _ExecuteTeardown(self) -> _EExecutionCmdID:
        if self._isInvalid:
            return _EExecutionCmdID.Stop()
        return self.__ExecuteTeardown()

    def _CheckNotifyLcFailure(self):
        if self._isInvalid:
            return False

        _cid = self.__t.toLcCompID

        if self._PcHasLcCompAnyFailureState(_cid, self.__ft):
            return False

        res    = False
        _frc   = None
        _myMtx = None

        _curEE = self.taskError
        if _curEE is not None:
            _curEE = _curEE._currentErrorEntry

        if (_curEE is not None) and _curEE.isFatalError:
            _frc = _curEE
            _myMtx = None if _frc is None else _frc._LockInstance()
            if _frc is not None:
                if _frc.isInvalid or not _frc.isPendingResolution:
                    if _myMtx is not None:
                        _myMtx.Give()
                    _frc, _myMtx = None, None

        if _frc is None:
            if self.isAborting:
                _bXCmdAbort = self._isReturnedXCmdAbort
                if _bXCmdAbort:
                    _xfph = _StrUtil.DeCapialize(self._GetTaskApiContext().compactName)
                    _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Shared_TID_002).format(self.__logPrefixCtr, _xfph)
                else:
                    _midPart = _FwTDbEngine.GetText(_EFwTextID.eMisc_Task) if self.__t.isXTaskRunnable else _FwTDbEngine.GetText(_EFwTextID.eMisc_TNPrefix_Runnable).lower()
                    _errMsg  = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_Shared_TID_001).format(self.__logPrefixCtr, _midPart)

                _bFwRbl  = self.__t.isFwRunnable
                _errCode = _EFwErrorCode.FE_00022 if _bFwRbl else _EFwErrorCode.FE_00923
                _frc     = logif._CreateLogFatalEC(_bFwRbl, _errCode, _errMsg, bDueToExecCmdAbort_=_bXCmdAbort)
                _myMtx   = None if _frc is None else _frc._LockInstance()

        if _frc is not None:
            _frcClone = _frc.Clone()
            if _frcClone is None:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00115)
            else:
                res = True
                self._PcNotifyLcFailure(_cid, _frcClone, atask_=self.__ft)
                _frc._UpdateErrorImpact(_EErrorImpact.eNoImpactByFrcLinkage)

            if _myMtx is not None:
                _myMtx.Give()
        return res

    @property
    def __isErrorFree(self):
        res = True
        if self.taskError is not None:
            res = self.taskError.isErrorFree
        return res

    @property
    def __taskID(self):
        res = self.taskBadge
        if res is not None:
            res = res.dtaskUID
        return res

    @property
    def __dtaskProfile(self):
        if self.__tp is not None:
            res = self.__tp
        else:
            res = self.__ft
            if res is not None:
                res = res._dtaskProfile
        return res

    @property
    def __logPrefix(self):
        res  = _FwTDbEngine.GetText(_EFwTextID.eMisc_LogPrefix_Runnable)
        res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_010).format(self._runnableName)
        return res

    @property
    def __logPrefixCtr(self):
        res  = _FwTDbEngine.GetText(_EFwTextID.eMisc_LogPrefix_Runnable)
        res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_010).format(self._runnableName)
        res += _FwTDbEngine.GetText(_EFwTextID.eMisc_LogPrefix_ExecCounter).format(self._xrNumber)
        return res

    @property
    def __lcCeaseState(self) -> _ELcCeaseTLBState:
        if self.__ft is None:
            res = _ELcCeaseTLBState.eNone
        else:
            res = self.__ft.ceaseTLBState
        return res

    def __UpdateRunnableName(self) -> str:
        res = self._dtaskName
        if res is None:
            _tskPrf = self.__dtaskProfile
            if (_tskPrf is not None) and _tskPrf.isValid:
                res = _tskPrf.dtaskName
        if res is None:
            res = type(self).__name__
        else:
            res = _FwTDbEngine.GetText(_EFwTextID.eMisc_TNPrefix_Runnable) + res

        self.__rn = res
        return res

    def __RegDefaultDispatchFilter(self) -> bool:
        if _ssshare._IsSubsysMsgDisabled():
            return False
        if self.__t.isFwDispatcherRunnable:
            return False
        if not self.isProvidingExternalQueue:
            return False

        _fwDisp = _AbsRunnable.__FwDispRbl
        if (_fwDisp is None) or not _fwDisp.isRunning:
            return False

        _dispFilter = _DispatchFilter._CreateDefaultDispatchFilter(receiverID_=self.__taskID)
        if _dispFilter is None:
            return False

        res = self.__ForwardDispatchFilterRequest(_dispFilter, callback_=None, bAdd_=True)
        if not res:
            logif._LogFatalEC(_EFwErrorCode.FE_00037, '{} Failed to register default dispatch filter.'.format(self.__logPrefix))
        return res

    def __DeregDefaultDispatchFilter(self) -> bool:
        if _ssshare._IsSubsysMsgDisabled():
            return False
        if self.__t.isFwDispatcherRunnable:
            return False
        if not self.isProvidingExternalQueue:
            return False

        _fwDisp = _AbsRunnable.__FwDispRbl
        if (_fwDisp is None) or not _fwDisp.isRunning:
            return False

        _dispFilter = _DispatchFilter._CreateDefaultDispatchFilter(receiverID_=self.__taskID)
        if _dispFilter is None:
            return False

        res = self.__ForwardDispatchFilterRequest(_dispFilter, callback_=None, bAdd_=False)
        return res

    def __ForwardDispatchFilterRequest(self, dispFilter_  : _DispatchFilter, callback_ : _FwCallable =None, bAdd_ =True) -> bool:
        if _ssshare._IsSubsysMsgDisabled():
            return False
        if self._isInvalid or self._isInLcCeaseMode:
            return False
        if self.__t.isFwDispatcherRunnable:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00116)
            return False
        if not (isinstance(dispFilter_, _DispatchFilter) and dispFilter_.isValid):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00117)
            return False

        if dispFilter_.isCustomMessageFilter:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00118)
            return False

        if dispFilter_.isInternalMessageFilter:
            if not self.isProvidingInternalQueue:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00119)
                return False
            if callback_ is not None:
                if not _CallableSignature.IsSignatureMatchingProcessInternalMessageCallback(callback_):
                    return False

        else:
            if not self.isProvidingExternalQueue:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00120)
                return False
            if callback_ is not None:
                if not _CallableSignature.IsSignatureMatchingProcessExternalMessageCallback(callback_):
                    return False

        if dispFilter_.isInternalMessageFilter:
            if bAdd_:
                res = self.__cbr._InsertDispatchFilter(dispFilter_, self, callback_=callback_)
            else:
                res = self.__cbr._EraseDispatchFilter(dispFilter_, self, callback_=callback_)
                dispFilter_.CleanUp()
        else:
            if bAdd_:
                res = _AbsRunnable.__FwDispRbl._RegisterAgentDispatchFilter(dispFilter_, self, callback_=callback_)
            else:
                res = _AbsRunnable.__FwDispRbl._DeregisterAgentDispatchFilter(dispFilter_, self, callback_=callback_)
                dispFilter_.CleanUp()
        return res

    def __StartRunnable(self):
        if not self._isStartable:
            vlogif._LogOEC(False, _EFwErrorCode.VUE_00007)
            return None
        elif (self.__ft is None) and (self.__tp is None):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00121)
            return None

        if self.__ft is not None:
            res = taskmgr._TaskMgr().StartTask(self.__ft.dtaskUID)
        else:
            res = taskmgr._TaskMgr().CreateTask(fwtPrf_=self.__tp, bStart_=True)
        return res is not None

    def __StopRunnable(self, bCancel_ =False, bCleanupDriver_ =True):
        if self.__ft is not None:
            taskmgr._TaskMgr().StopTask(self.__taskID, bCancel_=bCancel_, removeTask_=bCleanupDriver_)

    def __JoinRunnable(self, timeout_ : Union[int, float, None] =None):
        if self.__ft is None:
            pass
        elif self.__ft.isEnclosingStartupThread:
            vlogif._LogOEC(False, _EFwErrorCode.VUE_00008)
        else:
            if timeout_ is not None:
                timeout_ = _Timeout.CreateTimeout(timeout_)
            taskmgr._TaskMgr().JoinTask(self.__taskID, timeout_=timeout_)

    def __NotifyRunProgress(self, eRunProgressID_ : _ERunProgressID) -> _EExecutionCmdID:
        if self._isInLcCeaseMode:
            _xres = _EExecutionCmdID.Abort() if self.isAborting else _EExecutionCmdID.Stop()
        elif not self.isProvidingOnRunProgressNotification:
            _xres = _EExecutionCmdID.OK()
        else:
            _bWasRunning = self.isRunning
            _xtor = self.__xtors._GetApiExecutor(_ERblApiFuncTag.eRFTOnRunProgressNotification)
            _xtor.SetExecutorParams(param1_=eRunProgressID_)
            _xres = self.__EvaluateExecResult(executor_=_xtor, bCheckBefore_=None, abortState_=_TaskState._EState.eRunProgressAborted, bSkipErrProc_=eRunProgressID_.isPostRunPhase)
        return _xres

    def __ExecutePreRun(self, semStart_ : _BinarySemaphore) -> _EExecutionCmdID:
        _bCheckOK   = True
        _drvTask    = self.__ft
        _bEnclHThrd = False if _drvTask is None else _drvTask.isEnclosingPyThread

        if _drvTask is None:
            _bCheckOK = False
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00122)

        elif (self.taskError is None) or self.taskError.isFatalError or self.taskError.isNoImpactFatalErrorDueToFrcLinkage:
            _bCheckOK = False
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00124)

        elif _bEnclHThrd and (semStart_ is not None):
            _bCheckOK = False
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00125)

        elif not (_bEnclHThrd or isinstance(semStart_, _BinarySemaphore)):
            _bCheckOK = False
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00126)

        if _bCheckOK:
            if _ssshare._IsSubsysMsgDisabled():
                pass
            elif _AbsRunnable.__FwDispRbl is None:
                pass
            elif self.__t.isFwRunnable:
                pass
            elif not self.isProvidingExternalQueue:
                pass
            else:
                if not self.__t.isFwDispatcherRunnable:
                    _bCheckOK = self.__RegDefaultDispatchFilter()

        if _bCheckOK:
            if not self.__isErrorFree:
                self.taskError.ClearError()
        _xres = self.__EvaluateExecResult(xres_=_bCheckOK, bCheckBefore_=True, abortState_=_TaskState._EState.ePreRunAborted)

        if semStart_ is not None:
            semStart_.Give()
        return _xres

    def __ExecuteSetup(self):
        _xres = _EExecutionCmdID.Continue()

        if self.__xp.isIncludingSetUpExecutable:
            _xtor = self.__xtors._GetApiExecutor(_ERblApiFuncTag.eRFTSetUpExecutable)
            _xres = self.__EvaluateExecResult(executor_=_xtor, bCheckBefore_=False, abortState_=_TaskState._EState.eSetupAborted)
        return _xres

    def __ExecuteTeardown(self):
        _xres = _EExecutionCmdID.Continue()

        if self.__xp.isIncludingTeardownExecutable:
            self.__ClearCurUserError()
            _xtor = self.__xtors._GetApiExecutor(_ERblApiFuncTag.eRFTTearDownExecutable)
            _xres = self.__EvaluateExecResult(executor_=_xtor, bCheckBefore_=False, abortState_=_TaskState._EState.eTeardownAborted)
        return _xres

    def __ExecuteRun(self) -> _EExecutionCmdID:
        if self.__xp.isIncludingCustomManagedExternalQueue:
            return self.__ExecuteCustomManagedExtQueue()
        if self.__xp.isIncludingAutoManagedExternalQueue:
            return self.__ExecuteAutoManagedExtQueue(bCombinedManaged_=False)

        _bInclRunXtbl                        = self.__xp.isIncludingRunExecutable
        _bInclAutoManagedExtQueueByRunXtbl   = self.__xp.isIncludingAutoManagedExternalQueue_By_RunExecutable
        _bInclAutoManagedIntQueueByRunXtbl   = self.__xp.isIncludingAutoManagedInternalQueue_By_RunExecutable
        _bInclCustomManagedIntQueueByRunXtbl = self.__xp.isIncludingCustomManagedInternalQueue_By_RunExecutable

        _xres       = _EExecutionCmdID.Continue()
        _runCycleMS = self.__xc.runPhaseFreqMS

        _bBreak = False
        while True:
            if _bBreak:
                break
            if not _xres.isContinue:
                break

            try:
                if self._isInvalid:
                    return _EExecutionCmdID.Abort()

                self._IncEuRNumber()
                self.__ClearCurUserError()

                while True:
                    _ret = None if self._isAborting else self.isRunning
                    _xres = self.__EvaluateExecResult(xres_=_ret, bCheckBefore_=None, bSkipErrProc_=True)
                    if not _xres.isContinue:
                        break

                    if self.__cbr is not None:
                        self.__cbr._DropInvalidTargets()

                    if _bInclCustomManagedIntQueueByRunXtbl:
                        _xres = self.__ExecuteCustomManagedIntQueue()
                        if not _xres.isContinue:
                            break

                    if _bInclAutoManagedIntQueueByRunXtbl:
                        _xres = self.__ExecuteAutoManagedIntQueue()
                        if not _xres.isContinue:
                            break

                    if _bInclAutoManagedExtQueueByRunXtbl:
                        _xres = self.__ExecuteAutoManagedExtQueue(bCombinedManaged_=True)
                        if not _xres.isContinue:
                            break

                    if not _bInclRunXtbl:
                        break

                    _xtor = self.__xtors._GetApiExecutor(_ERblApiFuncTag.eRFTRunExecutable)
                    _xres = self.__EvaluateExecResult(executor_=_xtor, bCheckBefore_=True)
                    if not _xres.isContinue:
                        break

                    elif not self.isRunning:
                        _xres = self.__EvaluateExecResult(xres_=None if self._isAborting else False, bCheckBefore_=None)

                    break

            except _XcoXcpRootBase as _xcp:
                _xres = self.__HandleException(_xcp, bCaughtByApiExecutor_=False)

            except BaseException as _xcp:
                _xcp  = _XcoBaseException(_xcp, tb_=logif._GetFormattedTraceback())
                _xres = self.__HandleException(_xcp, bCaughtByApiExecutor_=False)

            finally:
                if not _xres.isContinue:
                    _bBreak = True
                elif _runCycleMS == 0:
                    _xres = _EExecutionCmdID.Stop()
                    if self.isRunning:
                        self._SetTaskState(_TaskState._EState.eProcessingStopped)
                    _bBreak = True
                else:
                    _TaskUtil.SleepMS(_runCycleMS)

            continue

        return _xres

    def __ExecuteCustomManagedExtQueue(self):
        _xres = _EExecutionCmdID.Abort()

        _actx = self._GetTaskApiContext()
        self._RblSetTaskAContext(_ETaskApiContextID.eProcExtQueue)

        _xtor = self.__xtors._GetApiExecutor(_ERblApiFuncTag.eRFTProcessExternalQueue)
        self._RblSetTaskXPhase(_ETaskXPhaseID.eRblProcExtQueue)
        _xres = self.__EvaluateExecResult(executor_=_xtor, bCheckBefore_=False)
        self._RblSetTaskXPhase(_ETaskXPhaseID.eFwHandling)

        self._RblSetTaskAContext(_actx)

        return _xres

    def __ExecuteAutoManagedExtQueue(self, bCombinedManaged_ : bool =False) -> _EExecutionCmdID:
        if not bCombinedManaged_:
            if not self.__xq.isBlockingOnQueueSize:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00940)
                return _EExecutionCmdID.Abort()

            while True:
                _xres = self.__ExecuteAutoManagedExtQueueBlocking()
                if not _xres.isContinue:
                    break
            return _xres

        _actx = self._GetTaskApiContext()
        self._RblSetTaskAContext(_ETaskApiContextID.eProcExtQueue)

        _blNum = self.__xq.qsize
        if _blNum < 1:
            self._RblSetTaskAContext(_actx)
            return _EExecutionCmdID.Continue()

        _ii, _lstBL = _blNum, []
        while _ii > 0:
            _bl = self.__xq.PopNowait()
            if _bl is None:
                break
            _lstBL.append(_bl)
            _ii -= 1

        _blNum = len(_lstBL)
        if _blNum < 1:
            self._RblSetTaskAContext(_actx)
            return _EExecutionCmdID.Continue()

        _lstBL = sorted(_lstBL, key=lambda _bl: _bl._sortKey)

        _bIncludingAutoManagedInternalQueue_By_AutoManagedExternalQueue   = self.__xp.isIncludingAutoManagedInternalQueue_By_AutoManagedExternalQueue
        _bIncludingCustomManagedInternalQueue_By_AutoManagedExternalQueue = self.__xp.isIncludingCustomManagedInternalQueue_By_AutoManagedExternalQueue

        _xres = _EExecutionCmdID.Continue()
        _xtor = self.__xtors._GetApiExecutor(_ERblApiFuncTag.eRFTProcessExternalMsg)

        for _bl in _lstBL:
            self.__ClearCurUserError()

            if _bIncludingCustomManagedInternalQueue_By_AutoManagedExternalQueue:
                _xres = self.__ExecuteCustomManagedIntQueue()

            elif _bIncludingAutoManagedInternalQueue_By_AutoManagedExternalQueue:
                _xres = self.__ExecuteAutoManagedIntQueue()

            else:
                _xres = _EExecutionCmdID.MapExecState2ExecCmdID(self)

            if not _xres.isContinue:
                break

            _msg = _bl._message
            if _msg is None:
                continue

            _msg2 = _msg
            if _msg.isXcoMsg:
                _msg2 = XMessage(_msg)

            _xtor.SetExecutorParams(param1_=_msg2, param2_=_bl._callback)
            _xres = self.__EvaluateExecResult(executor_=_xtor, bCheckBefore_=False)

            if _msg.isXcoMsg:
                _msg2._Detach()

        for _bl in _lstBL:
            _bl.CleanUp()

        self._RblSetTaskAContext(_actx)
        return _xres

    def __ExecuteAutoManagedExtQueueBlocking(self) -> _EExecutionCmdID:
        _actx = self._GetTaskApiContext()
        self._RblSetTaskAContext(_ETaskApiContextID.eProcExtQueue)

        _runCycleMS = self.__xc.runPhaseFreqMS

        _bl = None
        while True:
            _xres = _EExecutionCmdID.MapExecState2ExecCmdID(self)
            if not _xres.isContinue:
                self._RblSetTaskAContext(_actx)
                return _xres

            if _bl is not None:
                break
            _bl = self.__xq.PopBlockingQueue(sleepTimeMS_=_runCycleMS)

        _lstBL = [_bl]
        _blNum = self.__xq.qsize
        _ii    = _blNum
        while _ii > 0:
            _bl = self.__xq.PopNowait()
            if _bl is None:
                break
            _lstBL.append(_bl)
            _ii -= 1

        _lstBL = sorted(_lstBL, key=lambda _bl: _bl._sortKey)

        _bIncludingAutoManagedInternalQueue_By_AutoManagedExternalQueue   = self.__xp.isIncludingAutoManagedInternalQueue_By_AutoManagedExternalQueue
        _bIncludingCustomManagedInternalQueue_By_AutoManagedExternalQueue = self.__xp.isIncludingCustomManagedInternalQueue_By_AutoManagedExternalQueue

        _xres = _EExecutionCmdID.Continue()
        _xtor = self.__xtors._GetApiExecutor(_ERblApiFuncTag.eRFTProcessExternalMsg)

        for _bl in _lstBL:
            self._IncEuRNumber()
            self.__ClearCurUserError()

            if _bIncludingCustomManagedInternalQueue_By_AutoManagedExternalQueue:
                _xres = self.__ExecuteCustomManagedIntQueue()

            elif _bIncludingAutoManagedInternalQueue_By_AutoManagedExternalQueue:
                _xres = self.__ExecuteAutoManagedIntQueue()

            else:
                _xres = _EExecutionCmdID.MapExecState2ExecCmdID(self)

            if not _xres.isContinue:
                break

            _msg = _bl._message

            if _msg is None:
                continue

            _msg2 = _msg
            if _msg.isXcoMsg:
                _msg2 = XMessage(_msg)

            _xtor.SetExecutorParams(param1_=_msg2, param2_=_bl._callback)
            _xres = self.__EvaluateExecResult(executor_=_xtor, bCheckBefore_=False)

            if _msg.isXcoMsg:
                _msg2._Detach()

        for _bl in _lstBL:
            _bl.CleanUp()

        self._RblSetTaskAContext(_actx)
        return _xres

    def __ExecuteCustomManagedIntQueue(self) -> _EExecutionCmdID:
        _actx = self._GetTaskApiContext()
        self._RblSetTaskAContext(_ETaskApiContextID.eProcIntQueue)

        _xtor = self.__xtors._GetApiExecutor(_ERblApiFuncTag.eRFTProcessInternalQueue)
        _xres = self.__EvaluateExecResult(executor_=_xtor, bCheckBefore_=False)

        self._RblSetTaskAContext(_actx)

        return _xres

    def __ExecuteAutoManagedIntQueue(self) -> _EExecutionCmdID:
        _actx = self._GetTaskApiContext()
        self._RblSetTaskAContext(_ETaskApiContextID.eProcIntQueue)

        _lstBL = []
        _blNum = self.__iq.qsize
        _ii    = _blNum
        while _ii > 0:
            _bl = self.__iq.PopNowait()
            if _bl is None:
                break
            _lstBL.append(_bl)
            _ii -= 1

        _blNum = len(_lstBL)
        if _blNum < 1:
            self._RblSetTaskAContext(_actx)
            return _EExecutionCmdID.Continue()

        _xres = _EExecutionCmdID.MapExecState2ExecCmdID(self)
        _xtor = self.__xtors._GetApiExecutor(_ERblApiFuncTag.eRFTProcessInternalMsg)

        for _bl in _lstBL:
            if not _xres.isContinue:
                break

            self.__ClearCurUserError()

            _msg = _bl._message
            _msg2 = _msg
            if _msg.isXcoMsg:
                _msg2 = XMessage(_msg)

            _xtor.SetExecutorParams(param1_=_msg2, param2_=_bl._callback)
            _xres = self.__EvaluateExecResult(executor_=_xtor, bCheckBefore_=False)

            if _msg.isXcoMsg:
                _msg2._Detach()
            _msg.CleanUp()

        self._RblSetTaskAContext(_actx)
        return _xres

    def __ClearCurUserError(self):
        _tskErr = self.taskError
        if (_tskErr is not None) and _tskErr.isUserError:
            _tskErr.ClearError()

    def __EvaluateExecResult( self
                            , executor_     =None
                            , xres_         : Union[bool, _EExecutionCmdID] =None
                            , bCheckBefore_ : bool               =None
                            , abortState_   : _TaskState._EState =None
                            , bSkipErrProc_ : bool               =False) -> _EExecutionCmdID:
        if not ((executor_ is None) or isinstance(executor_, _RunnableApiExecutor)):
            self.__ag._SetGetReturnedExecCmd(None, bApplyConvertBefore_=False)
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00972)
            return _EExecutionCmdID.Abort()
        if not ((xres_ is None) or isinstance(xres_, (_EExecutionCmdID, bool))):
            self.__ag._SetGetReturnedExecCmd(None, bApplyConvertBefore_=False)
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00973)
            return _EExecutionCmdID.Abort()

        _bDoCheckAfter  = False
        _bDoCheckBefore = False

        if bCheckBefore_ is not None:
            _bDoCheckBefore = bCheckBefore_
            _bDoCheckAfter  = not _bDoCheckBefore

        res = _EExecutionCmdID.Continue()

        if _bDoCheckBefore and self._PcIsMonitoringLcModeChange():
            _newMode = self._PcCheckLcOperationModeChange()
            if (_newMode is not None) and not _newMode.isLcNormal:
                if _newMode.isLcCeaseMode:
                    res = self._PcOnLcCeaseModeDetected()
                elif _newMode.isLcFailureHandling:
                    res = self._PcOnLcFailureDetected()
                elif _newMode.isLcPreShutdown:
                    res = self._PcOnLcPreShutdownDetected()
                elif _newMode.isLcShutdown:
                    res = self._PcOnLcShutdownDetected()

        if not res.isContinue:
            pass
        else:
            if executor_ is None:
                res = _EExecutionCmdID.ConvertFrom(xres_)

                if res.isStop and self.isCanceling:
                    res = _EExecutionCmdID.Cancel()
            else:
                res = executor_.Execute()

            if not res.isContinue:
                pass
            elif _bDoCheckAfter and self._PcIsMonitoringLcModeChange():
                _newMode = self._PcCheckLcOperationModeChange()
                if (_newMode is not None) and not _newMode.isLcNormal:
                    if _newMode.isLcCeaseMode:
                        res = self._PcOnLcCeaseModeDetected()
                    elif _newMode.isLcFailureHandling:
                        res = self._PcOnLcFailureDetected()
                    elif _newMode.isLcPreShutdown:
                        res = self._PcOnLcPreShutdownDetected()
                    elif _newMode.isLcShutdown:
                        res = self._PcOnLcShutdownDetected()

        if not res.isContinue:
            pass
        elif self._isAborting or self._isInLcCeaseMode:
            pass
        elif bSkipErrProc_:
            pass
        else:
            res = self._ProcErrors()

        if not res.isContinue:
            _nst = None

            if res.isAbort:
                if not self.isAborting:
                    if abortState_ is None:
                        abortState_ = _TaskState._EState.eProcessingAborted
                    _nst = abortState_
            else:
                if self.isRunning or self._isPendingStopRequest or self._isPendingCancelRequest:
                    _bCancel = res.isCancel
                    _nst = _TaskState._EState.eProcessingCanceled if _bCancel else _TaskState._EState.eProcessingStopped

            if _nst is not None:
                self._SetTaskState(_nst)
        return res

    def __EvaluateSelfCheck(self) -> _ETaskSelfCheckResultID:
        if self._isInvalid:
            return _ETaskSelfCheckResultID.eScrStop

        res = self.__ft._selfCheckResult
        if res._isScrNOK or not self.isStarted:
            return res

        if self._isInLcCeaseMode:
            return _ETaskSelfCheckResultID.eScrStop

        if not self.isRunning:
            if self.isAborting or self.isFailed:
                res = _ETaskSelfCheckResultID.eScrAbort
            elif not self._GetTaskApiContext().isTeardown:
                res = _ETaskSelfCheckResultID.eScrStop
            return res

        _ret = _EExecutionCmdID.Continue()

        _newMode = self._PcCheckLcOperationModeChange()
        if (_newMode is not None) and not _newMode.isLcNormal:
            if _newMode.isLcCeaseMode:
                _ret = self._PcOnLcCeaseModeDetected()
            elif _newMode.isLcFailureHandling:
                _ret = self._PcOnLcFailureDetected()
            elif _newMode.isLcPreShutdown:
                _ret = self._PcOnLcPreShutdownDetected()
            elif _newMode.isLcShutdown:
                _ret = self._PcOnLcShutdownDetected()

        if _ret.isContinue and self._isInLcCeaseMode:
            _ret = _EExecutionCmdID.Stop()

        if not _ret.isContinue:
            res = _ETaskSelfCheckResultID.eScrAbort if _ret.isAbort else _ETaskSelfCheckResultID.eScrStop
            self._SetTaskState(_TaskState._EState.eProcessingStopped)
        else:
            res = _ETaskSelfCheckResultID.eScrOK

        if _ret.isContinue != self.isRunning:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00975)
        return res

    def __HandleException(self, xcp_ : _XcoXcpRootBase, bCaughtByApiExecutor_ =True) -> _EExecutionCmdID:
        if self._isInvalid:
            return _EExecutionCmdID.Abort()

        with self.__md:
            _xcoXcp = None if _IsXTXcp(xcp_) else xcp_
            _xbx    = None if (_xcoXcp is None) or not isinstance(_xcoXcp, _XcoBaseException) else _xcoXcp

            if _xbx is not None:
                if _xbx.xcpType.isBaseExceptionAtrributeError:
                    _xmlrMsg = _AbsRunnable.__XR_XCP_DW

                    if _xbx.shortMessage == _xmlrMsg:
                        return _EExecutionCmdID.MapExecState2ExecCmdID(self)

            if self._isAborting:
                pass

            elif _xbx is not None:
                self._ProcUnhandledXcp(_xbx)

            self._RblSetTaskXPhase(_ETaskXPhaseID.eFwHandling)

            if not (self._isAborting or self._isInLcCeaseMode):
                if not bCaughtByApiExecutor_:
                    _procRes = self._ProcErrors()

                    if not _procRes.isContinue:
                        if _procRes.isStop:
                            _nts = _TaskState._EState.eProcessingAborted
                        else:
                            if _procRes.isStop and self._isCanceling:
                               _procRes = _EExecutionCmdID.Cancel()

                            _nts = _TaskState._EState.eProcessingCanceled if _procRes.isCancel else _TaskState._EState.eProcessingStopped
                        self._SetTaskState(_nts)

            if not self.isRunning:
                if self.isAborting:
                    res = _EExecutionCmdID.Abort()
                else:
                    res = _EExecutionCmdID.Cancel() if self.isCanceling else _EExecutionCmdID.Stop()

            else:
                res = _EExecutionCmdID.Continue()
            return res

    def __CheckMutuallyExclusiveAPI(self) -> bool:
        res = True

        _tname = type(self).__name__

        _bProvidingRunExecutable        = self.__ag.isProvidingRunExecutable
        _bProvidingProcessInternalMsg   = self.__ag.isProvidingProcessInternalMsg
        _bProvidingProcessExternalMsg   = self.__ag.isProvidingProcessExternalMsg
        _bProvidingProcessInternalQueue = self.__ag.isProvidingProcessInternalQueue
        _bProvidingProcessExternalQueue = self.__ag.isProvidingProcessExternalQueue

        if _bProvidingProcessInternalMsg and _bProvidingProcessInternalQueue:
            res = False
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00127)
        elif _bProvidingProcessExternalMsg and _bProvidingProcessExternalQueue:
            res = False
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00128)
        elif _bProvidingRunExecutable and _bProvidingProcessExternalQueue:
            res = False
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00129)
        elif not (_bProvidingRunExecutable or _bProvidingProcessExternalQueue or _bProvidingProcessExternalMsg):
            res = False
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00130)
        return res

    def __CreateExecPlan(self):
        _tname = type(self).__name__

        _dsid = dict()
        for _n, _m in _ERblExecStepID.__members__.items():
            _dsid[_m] = False

        if self.isProvidingSetUpRunnable:
            _sid = _ERblExecStepID.eSetUpExecutable
            _dsid[_sid] = True

        if self.isProvidingTearDownRunnable:
            _sid = _ERblExecStepID.eTeardownExecutable
            _dsid[_sid] = True

        if self.isProvidingCustomManagedExternalQueue:
            _sid = _ERblExecStepID.eCustomManagedExternalQueue
            _dsid[_sid] = True
        else:
            _sid = _ERblExecStepID.eRunExecutable
            _dsid[_sid] = True

            if self.isProvidingAutoManagedExternalQueue:
                if not self.isProvidingRunExecutable:
                    _sid = _ERblExecStepID.eAutoManagedExternalQueue
                    _dsid[_sid] = True
                else:
                    _sid = _ERblExecStepID.eAutoManagedExternalQueue_By_RunExecutable
                    _dsid[_sid] = True

        if self.isProvidingCustomManagedInternalQueue:
            if not self.isProvidingRunExecutable:
                _sid = _ERblExecStepID.eCustomManagedInternalQueue_By_AutoManagedExternalQueue
                _dsid[_sid] = True
            else:
                _sid = _ERblExecStepID.eCustomManagedInternalQueue_By_RunExecutable
                _dsid[_sid] = True

        elif self.isProvidingAutoManagedInternalQueue:
            if not self.isProvidingRunExecutable:
                _sid = _ERblExecStepID.eAutoManagedInternalQueue_By_AutoManagedExternalQueue
                _dsid[_sid] = True
            else:
                _sid = _ERblExecStepID.eAutoManagedInternalQueue_By_RunExecutable
                _dsid[_sid] = True

        self.__xp = _AbsRunnable._RunnableExecutionPlan(_dsid)

    def __CreateExecutorTable(self, bUtRbl_ : bool):
        _dictExecutors = dict()
        for _n, _m in _ERblApiFuncTag.__members__.items():
            if not _m.isRunnableExecutionAPI:
                continue
            if not self.__ag._IsProvidingApiFunction(apiFTag_=_m):
                continue
            _dictExecutors[_m] = _RunnableApiExecutor(bUtRbl_, self.__ag, _m, self.__HandleException)

        self.__xtors = _AbsRunnable._RunnableExecutorTable(_dictExecutors)

    def __ProcErrHdlrCallback( self
                             , cbID_  : _EPcErrHandlerCBID
                             , curFE_ : _FatalLog =None) -> _EExecutionCmdID:
        if curFE_ is None:
            _tailPart = _CommonDefines._CHAR_SIGN_DOT
        else:
            _tailPart = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_023).format(curFE_.uniqueID, curFE_.shortMessage)

        if cbID_.isFwMainSpecificCallbackID:
            return _EExecutionCmdID.Abort() if self._isAborting else _EExecutionCmdID.Continue()

        _ePF = self._GetProcessingFeasibility(errLog_=curFE_)
        if not _ePF.isFeasible:
            if _ePF.isUnfeasible:
                res = _EExecutionCmdID.Abort() if self._isAborting else _EExecutionCmdID.Continue()
            else:
                res = _EExecutionCmdID.Abort()
            return res

        if not self._xcard.isLcFailureReportPermissionEnabled:
            vlogif._LogOEC(False, _EFwErrorCode.VUE_00009)
        else:
            _fe  = curFE_
            _cid = self.__t.toLcCompID
            self._PcNotifyLcFailure(_cid, _fe, atask_=self.__ft)

        res = _EExecutionCmdID.Abort()
        return res

    def __PreProcessCeaseMode(self):
        if self._isInvalid:
            return

        if self.__t.isFwMainRunnable:
            _dtlb = self._lcDynamicTLB
            _lcMon = None if _dtlb is None else _dtlb._lcMonitor

            if _lcMon is not None:
                _bAborting = self.isAborting
                if not _lcMon.isLcShutdownEnabled:
                    _lcMon._EnableCoordinatedShutdown(bManagedByMR_=not _bAborting)
                if not self._isInLcCeaseMode:
                    self._CreateCeaseTLB(bEnding_=_bAborting)

        _bCreateCTLB = self._lcDynamicTLB.isLcShutdownEnabled

        if self._CheckNotifyLcFailure():
            _bCreateCTLB = True

        if not self._isInLcCeaseMode:
            if _bCreateCTLB:
                self._CreateCeaseTLB(bEnding_=self.isAborting)

    def __ProcessCeaseMode(self):
        if self._isInvalid:
            return

        if self.__t.isFwMainRunnable:
            pass

        elif not self._isInLcCeaseMode:
            if self._lcDynamicTLB.isLcShutdownEnabled:
                self._CreateCeaseTLB(bEnding_=self.isAborting)
            else:
                return

        _eCurCS = self.__lcCeaseState
        if _eCurCS.isPrepareCeasing:
            self.__PrepareDefaultCeasing()
            _eCurCS = self.__lcCeaseState
        if _eCurCS.isEnterCeasing:
            self.__EnterDefaultCeasing()
            _eCurCS = self.__lcCeaseState
        if _eCurCS.isEndingCease:
            self.__ProcessLeavingCease()
            _eCurCS = self.__lcCeaseState

        if not _eCurCS.isDeceased:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00131)

    def __PrepareDefaultCeasing(self):
        if not self._isInLcCeaseMode:
            return

        _eCurCS = self.__lcCeaseState
        if not _eCurCS.isPrepareCeasing:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00132)
            self._lcCeaseTLB.UpdateCeaseState(True)
            return

        _bCP = self.__ag.isProvidingPrepareCeasing
        _bCP = _bCP and (self._lcCeaseTLB._lcMonitor._isCoordinatedShutdownManagedByMR or not self.__t.isFwMainRunnable)

        if _bCP:
            self.__ag.prepareCeasing()
        else:
            while True:
                _ctlb = self._lcCeaseTLB
                if _ctlb is None:
                    return

                _ctlb.IncrementCeaseAliveCounter()
                _TaskUtil.SleepMS(20)

                _ctlb = self._lcCeaseTLB
                if _ctlb is None:
                    return
                if not _ctlb.isCoordinatedShutdownRunning:
                    self._lcCeaseTLB.UpdateCeaseState(True)
                    break
                if _ctlb._isCeasingGateOpened:
                    break

            self._lcCeaseTLB.HopToNextCeaseState(bEnding_=self._isAborting)

    def __EnterDefaultCeasing(self):
        if not self._isInLcCeaseMode:
            return

        _eCurCS = self.__lcCeaseState
        if not _eCurCS.isEnterCeasing:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00133)
            self._lcCeaseTLB.UpdateCeaseState(True)
            return

        self._lcCeaseTLB.HopToNextCeaseState(bEnding_=self._isAborting)

        _bRCIter = self.__ag.isProvidingRunCeaseIteration

        _bPreShutdownPassed = False
        while True:
            if not self._lcCeaseTLB.isCeasing:
                break

            self._lcCeaseTLB.IncrementCeaseAliveCounter()

            _TaskUtil.SleepMS(self._xcard.cyclicCeaseTimespanMS)

            if self._isInvalid:
                break

            if _bRCIter:
                self.__ag.runCeaseIteration()

            if not self._lcCeaseTLB.isCeasing:
                self._lcCeaseTLB.UpdateCeaseState(True)
                break

            if not _bPreShutdownPassed:
                if self._lcCeaseTLB._isPreShutdownGateOpened:
                    _bPreShutdownPassed = True

                    if not self._PcHasLcAnyFailureState():
                        self.__ExecuteTeardown()

                    self._lcCeaseTLB.HopToNextCeaseState(bEnding_=self._isAborting)
                    continue

            if self._lcCeaseTLB._isShutdownGateOpened:
                break

        if self._lcCeaseTLB is not None:
            self._lcCeaseTLB.HopToNextCeaseState(bEnding_=self._isAborting)

    def __ProcessLeavingCease(self):
        if not self._isInLcCeaseMode:
            return

        _eCurCS = self.__lcCeaseState
        if not self._lcCeaseTLB.isEndingCease:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00134)
            if self._lcCeaseTLB.isDeceased:
                return
            self._lcCeaseTLB.UpdateCeaseState(True)

        while True:
            if (not self._lcCeaseTLB.isCoordinatedShutdownRunning) or self._lcCeaseTLB.isCoordinatedShutdownGateOpened:
                break

            self._lcCeaseTLB.IncrementCeaseAliveCounter()

            _TaskUtil.SleepMS(self._xcard.cyclicCeaseTimespanMS)

            if self._isInvalid:
                break

            _eCSR = self._lcCeaseTLB.curShutdownRequest
            if (_eCSR is None) or _eCSR.isShutdown:
                break

            continue

        if self._lcCeaseTLB is not None:
            self._lcCeaseTLB.HopToNextCeaseState(bEnding_=True)

class _RunnableApiExecutor(_AbsSlotsObject):
    __slots__ = [ '__r' , '__er' , '__ag' , '__af' , '__fid' , '__bTD' , '__xph' , '__xh' , '__p1' , '__p2' , '__aa' , '__ak' ]

    def __init__(self, bUtRbl_ : bool, apiGuide_  : _ARblApiGuide, fid_ : _ERblApiFuncTag, xcpHdlr_):
        super().__init__()
        self.__r   = None
        self.__er  = None
        self.__aa  = None
        self.__af  = None
        self.__ag  = apiGuide_
        self.__ak  = None
        self.__p1  = None
        self.__p2  = None
        self.__xh  = xcpHdlr_
        self.__bTD = False
        self.__fid = fid_
        self.__xph = None

        if not isinstance(fid_, _ERblApiFuncTag):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00135)
            self.CleanUp()
        elif xcpHdlr_ is None:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00136)
            self.CleanUp()
        elif not isinstance(apiGuide_, _ARblApiGuide):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00137)
            self.CleanUp()
        elif not isinstance(apiGuide_._runnable, _AbsRunnable):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00138)
            self.CleanUp()
        elif fid_.value < _ERblApiFuncTag.eRFTRunExecutable.value or fid_.value > _ERblApiFuncTag.eRFTOnRunProgressNotification.value:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00139)
            self.CleanUp()
        elif self.__SetApiFunc() is None:
            self.CleanUp()
        else:
            _txph = fid_.MapToTaskExecutionPhaseID(bUTask_=bUtRbl_)
            if _txph.isNA:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00140)
                self.CleanUp()
            else:
                self.__r   = apiGuide_._runnable
                self.__xph = _txph

    @property
    def apiGuide(self) -> _ARblApiGuide:
        return self.__ag

    @property
    def executionResult(self) -> _EExecutionCmdID:
        return self.__er

    def SetExecutorParams(self, param1_ =None, param2_ =None, args_ =None, kwargs_ =None):
        if self.__fid is not None:
            self.__p1 = param1_
            self.__p2 = param2_
            self.__aa = args_
            self.__ak = kwargs_

    def Execute(self) -> _EExecutionCmdID:
        if self.__fid is None:
            return self.__er

        self.__er = _EExecutionCmdID.Abort()

        if self.__af is None:
            return self.__er

        _ret = None
        try:
            self.__r._RblSetTaskXPhase(self.__xph)

            if self.__fid == _ERblApiFuncTag.eRFTSetUpExecutable:
                if not self.__r._rblType.isXTaskRunnable:
                    _args   = self.__r._xcard.args
                    _kwargs = self.__r._xcard.kwargs
                    _ret    = self.__af(*_args, **_kwargs)
                else:
                    _ret = self.__af()

            elif self.__fid == _ERblApiFuncTag.eRFTOnTimeoutExpired:
                if (self.__p1 is None) or (self.__aa is None) or (self.__ak is None):
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00142)
                else:
                    _ret = self.__af(self.__p1, *self.__aa, **self.__ak)

            else:
                if (self.__fid == _ERblApiFuncTag.eRFTProcessInternalMsg) or (self.__fid == _ERblApiFuncTag.eRFTProcessExternalMsg):
                    if self.__p1 is None:
                        vlogif._LogOEC(True, _EFwErrorCode.VFE_00143)
                    elif (self.__p2 is not None) and not (isinstance(self.__p2, _FwCallable) and self.__p2.isValid):
                        vlogif._LogOEC(True, _EFwErrorCode.VFE_00144)
                    else:
                        _ret = self.__af(self.__p1, self.__p2)

                elif self.__fid == _ERblApiFuncTag.eRFTOnRunProgressNotification:
                    if self.__p1 is None:
                        vlogif._LogOEC(True, _EFwErrorCode.VFE_00145)
                    else:
                        _ret = self.__af(self.__p1)

                elif self.__fid == _ERblApiFuncTag.eRFTTearDownExecutable:
                    if self.__bTD:
                        _ret = _EExecutionCmdID.Stop()
                    else:
                        self.__bTD = True
                        _ret = self.__af()

                elif not self.__r._rblType.isXTaskRunnable:
                    _args   = self.__r._xcard.args
                    _kwargs = self.__r._xcard.kwargs
                    _ret    = self.__af(*_args, **_kwargs)

                else:
                    _ret = self.__af()

            if (_ret is not None) and not isinstance(_ret, (EExecutionCmdID, _EExecutionCmdID, bool)):
                logif._LogErrorEC(_EFwErrorCode.UE_00259, _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_BAD_XCMD_RETURN_TYPE).format(type(_ret).__name__))
                _ret = _EExecutionCmdID.Stop()
            self.__r._RblSetTaskXPhase(_ETaskXPhaseID.eFwHandling)

            _bScrNOK = self.__r._rblTask._selfCheckResult._isScrNOK

            if _bScrNOK:
                _ret = _EExecutionCmdID.MapExecState2ExecCmdID(self)

            _ret = self.__ag._SetGetReturnedExecCmd(_ret)

            if _bScrNOK:
                pass

            elif _ret.isAbort:
                self.__r._SetTaskState(_TaskState._EState.eProcessingAborted)

                self.__r._CheckNotifyLcFailure()

        except _XcoXcpRootBase as _xcp:
            _ret = self.__xh(_xcp, bCaughtByApiExecutor_=True)

        except BaseException as _xcp:
            _xcp = _XcoBaseException(_xcp, tb_=logif._GetFormattedTraceback())
            _ret = self.__xh(_xcp, bCaughtByApiExecutor_=True)

        finally:
            self.__er = _EExecutionCmdID.ConvertFrom(_ret)

        self.__p1 = None
        self.__aa = None
        self.__ak = None
        return self.__er

    def _ToString(self):
        if self.__fid is None:
            return None
        return _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_002).format(type(self).__name__, self.__r._runnableName, self.__fid.functionName)

    def _CleanUp(self):
        self.__r   = None
        self.__er  = None
        self.__aa  = None
        self.__af  = None
        self.__ag  = None
        self.__ak  = None
        self.__p1  = None
        self.__p2  = None
        self.__xh  = None
        self.__bTD = None
        self.__fid = None
        self.__xph = None

    @property
    def __logPrefix(self):
        res = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_003)
        return res.format(self.__r._runnableName, self.__fid.functionName)

    def __SetApiFunc(self):
        if (self.__ag is None) or (self.__fid is None):
            return None

        res = None

        _bUErr = False

        if self.__fid == _ERblApiFuncTag.eRFTRunExecutable:
            res = self.__ag.runExecutable

        elif self.__fid == _ERblApiFuncTag.eRFTSetUpExecutable:
            res = self.__ag.setUpRunnable

        elif self.__fid == _ERblApiFuncTag.eRFTProcessExternalMsg:
            res = self.__ag.procExternalMsg

        elif self.__fid == _ERblApiFuncTag.eRFTProcessInternalMsg:
            res = self.__ag.procInternalMsg

        elif self.__fid == _ERblApiFuncTag.eRFTOnTimeoutExpired:
            res = self.__ag.onTimeoutExpired

        elif self.__fid == _ERblApiFuncTag.eRFTTearDownExecutable:
            res = self.__ag.tearDownRunnable

        elif self.__fid == _ERblApiFuncTag.eRFTProcessExternalQueue:
            res = self.__ag.procExternalQueue

        elif self.__fid == _ERblApiFuncTag.eRFTProcessInternalQueue:
            res = self.__ag.procInternalQueue

        elif self.__fid == _ERblApiFuncTag.eRFTOnRunProgressNotification:
            res = self.__ag.onRunProgressNotification

        else:
            _bUErr = True
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00146)

        if res is None:
            if not _bUErr:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00147)
        else:
            self.__af = res
        return res
