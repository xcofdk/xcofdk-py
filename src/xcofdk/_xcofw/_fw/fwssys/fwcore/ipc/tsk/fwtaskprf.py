# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwtaskprf.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from _fwadapter                          import rlogif
from _fw.fwssys.fwcore.base.strutil      import _StrUtil
from _fw.fwssys.fwcore.base.util         import _Util
from _fw.fwssys.fwcore.types.aobject     import _AbsSlotsObject
from _fw.fwssys.fwcore.types.afwprofile  import _AbsFwProfile
from _fw.fwssys.fwcore.ipc.rbl.arunnable import _AbsRunnable
from _fw.fwssys.fwcore.ipc.tsk.taskutil  import _TaskUtil
from _fw.fwssys.fwcore.ipc.tsk.taskutil  import _ETaskResFlag
from _fw.fwssys.fwcore.ipc.tsk.taskutil  import _ETaskRightFlag
from _fw.fwssys.fwcore.ipc.tsk.taskutil  import _PyThread
from _fw.fwssys.fwmsg.disp.fwqueue       import _FwQueue
from _fw.fwssys.fwerrh.fwerrorcodes      import _EFwErrorCode

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _FwTaskProfile(_AbsFwProfile):
    __slots__ = []

    _ATTR_KEY_ARGS                         = _AbsFwProfile._ATTR_KEY_ARGS
    _ATTR_KEY_KWARGS                       = _AbsFwProfile._ATTR_KEY_KWARGS
    __ATTR_KEY_TASK_ID                     = _AbsFwProfile._ATTR_KEY_TASK_ID
    _ATTR_KEY_TASK_NAME                    = _AbsFwProfile._ATTR_KEY_TASK_NAME
    _ATTR_KEY_TASK_RIGHTS                  = _AbsFwProfile._ATTR_KEY_TASK_RIGHTS
    _ATTR_KEY_ENCLOSED_PYTHREAD            = _AbsFwProfile._ATTR_KEY_ENCLOSED_PYTHREAD
    _ATTR_KEY_AUTO_START_ENCLOSED_PYTHREAD = _AbsFwProfile._ATTR_KEY_AUTO_START_ENCLOSED_PYTHREAD

    _ATTR_KEY_TIMER                        = _FwTDbEngine.GetText(_EFwTextID.eFwTP_AN_ATTR_KEY_TIMER)
    _ATTR_KEY_RUNNABLE                     = _FwTDbEngine.GetText(_EFwTextID.eFwTP_AN_ATTR_KEY_RUNNABLE)
    __ATTR_KEY_EXT_QUEUE                   = _FwTDbEngine.GetText(_EFwTextID.eFwTP_AN_ATTR_KEY_EXT_QUEUE)
    __ATTR_KEY_INT_QUEUE                   = _FwTDbEngine.GetText(_EFwTextID.eFwTP_AN_ATTR_KEY_INT_QUEUE)
    _ATTR_KEY_TIMER_PROFILE                = _FwTDbEngine.GetText(_EFwTextID.eFwTP_AN_ATTR_KEY_TIMER_PROFILE)
    _ATTR_KEY_RESOURCES_MASK               = _FwTDbEngine.GetText(_EFwTextID.eFwTP_AN_ATTR_KEY_RESOURCES_MASK)
    _ATTR_KEY_EXTERNAL_QUEUE_SIZE          = _FwTDbEngine.GetText(_EFwTextID.eFwTP_AN_ATTR_KEY_EXTERNAL_QUEUE_SIZE)
    _ATTR_KEY_DELAYED_START_TIME_SPAN      = _FwTDbEngine.GetText(_EFwTextID.eFwTP_AN_ATTR_KEY_DELAYED_START_TIME_SPAN)
    _ATTR_KEY_ON_SIZE_BLOCKING_XQUEUE      = _FwTDbEngine.GetText(_EFwTextID.eFwTP_AN_ATTR_KEY_ON_SIZE_BLOCKING_XQUEUE)
    __ATTR_KEY_TIMER_RESOURCE              = _FwTDbEngine.GetText(_EFwTextID.eFwTP_AN_ATTR_KEY_TIMER_RESOURCE)

    def __init__( self
                , rbl_            : _AbsRunnable  =None
                , taskName_       : str           =None
                , rmask_          : _ETaskResFlag =None
                , delayedStartMS_ : int           =None
                , enclHThrd_      : _PyThread     =None
                , bASEnclHThrd_   : bool =None
                , args_           : list =None
                , kwargs_         : dict =None
                , tpAttrs_        : dict =None ):
        _AbsSlotsObject.__init__(self)

        _SB_KEY   = _FwTaskProfile._ATTR_KEY_ON_SIZE_BLOCKING_XQUEUE
        _RBL_KEY  = _FwTaskProfile._ATTR_KEY_RUNNABLE
        _TRM_KEY  = _FwTaskProfile._ATTR_KEY_TASK_RIGHTS
        _RESM_KEY = _FwTaskProfile._ATTR_KEY_RESOURCES_MASK

        _bError    = False
        _dictAttrs = {}

        if self._GetProfileHandlersList() is None:
            if not _FwTaskProfile.__SetupProfileHandlersList():
                _bError = True
        if not _bError:
            if rbl_ is not None:
                _dictAttrs[_RBL_KEY] = rbl_
            if taskName_ is not None:
                _dictAttrs[_FwTaskProfile._ATTR_KEY_TASK_NAME] = taskName_
            if rmask_ is not None:
                _dictAttrs[_RESM_KEY] = rmask_
            if delayedStartMS_ is not None:
                _dictAttrs[_FwTaskProfile._ATTR_KEY_DELAYED_START_TIME_SPAN] = delayedStartMS_
            if enclHThrd_ is not None:
                _dictAttrs[_FwTaskProfile._ATTR_KEY_ENCLOSED_PYTHREAD] = enclHThrd_
            if bASEnclHThrd_ is not None:
                _dictAttrs[_FwTaskProfile._ATTR_KEY_AUTO_START_ENCLOSED_PYTHREAD] = bASEnclHThrd_
            if args_ is not None:
                _dictAttrs[_FwTaskProfile._ATTR_KEY_ARGS] = args_
            if kwargs_ is not None:
                _dictAttrs[_FwTaskProfile._ATTR_KEY_KWARGS] = kwargs_

            if tpAttrs_ is not None:
                if not _Util.IsInstance(tpAttrs_, dict, bThrowx_=True):
                    _bError = True
                else:
                    for _kk in tpAttrs_.keys():
                        if tpAttrs_[_kk] is None:
                            continue
                        if _kk not in _dictAttrs:
                            _dictAttrs[_kk] = tpAttrs_[_kk]
                            continue

                        _bError = True
                        rlogif._LogOEC(True, _EFwErrorCode.FE_00289)
                        break
        if not _bError:
            _sb   = None if _SB_KEY not in _dictAttrs else _dictAttrs[_SB_KEY]
            _rbl  = None if _RBL_KEY not in _dictAttrs else _dictAttrs[_RBL_KEY]
            _trm  = None if _TRM_KEY not in _dictAttrs else _dictAttrs[_TRM_KEY]
            _resm = None if _RESM_KEY  not in _dictAttrs else _dictAttrs[_RESM_KEY]

            if _rbl is None:
                _bError = True
                rlogif._LogOEC(True, _EFwErrorCode.FE_00290)
            elif _rbl._rblType is None:
                _bError = True
                rlogif._LogOEC(True, _EFwErrorCode.FE_00291)
            elif (_trm is not None) and not _ETaskRightFlag.IsValidTaskRightMask(_trm):
                _bError = True
                rlogif._LogOEC(True, _EFwErrorCode.FE_00292)
            elif (_resm is not None) and not isinstance(_resm, _ETaskResFlag):
                _bError = True
                rlogif._LogOEC(True, _EFwErrorCode.FE_00293)
            else:
                _uta = _rbl._utAgent if _rbl._rblType.isXTaskRunnable else None

                if (_resm is not None) and (_uta is not None):
                    _bError = True
                    rlogif._LogOEC(True, _EFwErrorCode.FE_00294)
                elif (_sb is not None) and (_uta is not None):
                    _bError = True
                    rlogif._LogOEC(True, _EFwErrorCode.FE_00295)
                else:
                    if _trm is not None:
                        _dictAttrs[_TRM_KEY] = _trm
                    if _rbl._rblType.isXTaskRunnable:
                        _resm = _ETaskResFlag.GetRessourcesMask()
                        if not (_resm is None or _resm == _ETaskResFlag.eNone):
                            _dictAttrs[_RESM_KEY] = _resm
                    if (_sb is None) and not _rbl._rblType.isXTaskRunnable:
                        _dictAttrs[_SB_KEY] = True

        if _bError:
            _AbsFwProfile.__init__(self, _AbsFwProfile._EProfileType.eTask, profileAttrs_=None)
            self.profileStatus = _AbsFwProfile._EValidationStatus.eInvalid
        else:
            _AbsFwProfile.__init__(self, _AbsFwProfile._EProfileType.eTask, profileAttrs_=_dictAttrs)
        _dictAttrs.clear()

    @property
    def isEnclosingPyThread(self):
        res  = self.isValid
        if not res:
            pass
        else:
            res = self.enclosedPyThread is not None
        return res

    @property
    def isEnclosingStartupThread(self):
        res  = self.isEnclosingPyThread
        if not res:
            pass
        else:
            res = _TaskUtil.IsStartupThread(self.enclosedPyThread)
        return res

    @property
    def isAutoStartEnclHThrdEnabled(self) -> bool:
        return self._GetProfileAttr(_FwTaskProfile._ATTR_KEY_AUTO_START_ENCLOSED_PYTHREAD)

    @property
    def isExternalQueueEnabled(self) -> bool:
        return self.externalQueue is not None

    @property
    def isInternalQueueEnabled(self) -> bool:
        return self.internalQueue is not None

    @property
    def isExternalQueueOnSizeBlocking(self):
        res = self.externalQueue is not None
        if res:
            res = self._GetProfileAttr(_FwTaskProfile._ATTR_KEY_ON_SIZE_BLOCKING_XQUEUE)
            res = res == True
        return res

    @property
    def dtaskUID(self) -> int:
        return self._GetProfileAttr(_FwTaskProfile.__ATTR_KEY_TASK_ID)

    @property
    def dtaskName(self) -> str:
        return self._GetProfileAttr(_FwTaskProfile._ATTR_KEY_TASK_NAME)

    @property
    def taskRightsMask(self):
        return self._GetProfileAttr(_FwTaskProfile._ATTR_KEY_TASK_RIGHTS)

    @property
    def runnable(self) -> _AbsRunnable:
        return self._GetProfileAttr(_FwTaskProfile._ATTR_KEY_RUNNABLE)

    @property
    def resourcesMask(self):
        return self._GetProfileAttr(_FwTaskProfile._ATTR_KEY_RESOURCES_MASK)

    @property
    def delayedStartTimeSpanMS(self):
        res = self._GetProfileAttr(_FwTaskProfile._ATTR_KEY_DELAYED_START_TIME_SPAN)
        if res is None:
            res = 0
        return res

    @property
    def enclosedPyThread(self) -> _PyThread:
        return self._GetProfileAttr(_FwTaskProfile._ATTR_KEY_ENCLOSED_PYTHREAD)

    @property
    def args(self) -> list:
        return self._GetProfileAttr(_FwTaskProfile._ATTR_KEY_ARGS)

    @property
    def kwargs(self) -> dict:
        return self._GetProfileAttr(_FwTaskProfile._ATTR_KEY_KWARGS)

    @property
    def internalQueue(self) -> _FwQueue:
        return self._GetProfileAttr(_FwTaskProfile.__ATTR_KEY_INT_QUEUE)

    @property
    def externalQueue(self) -> _FwQueue:
        return self._GetProfileAttr(_FwTaskProfile.__ATTR_KEY_EXT_QUEUE)

    @property
    def externalQueueSize(self) -> int:
        return self._GetProfileAttr(_FwTaskProfile._ATTR_KEY_EXTERNAL_QUEUE_SIZE)

    def Freeze(self, tskID_ : int =0, tskName_ : str =None):
        if self.isFrozen:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00296)
            return False
        elif not self.isValid:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00297)
            return False
        elif self.runnable is None:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00298)
            return False

        if not _AbsFwProfile._IsAutoGeneratedTaskNameEnabled():
            _bValid  = (tskName_ is None) and _FwTaskProfile._ATTR_KEY_TASK_NAME in self.profileAttributes
            _bValid |= (tskName_ is not None) and _FwTaskProfile._ATTR_KEY_TASK_NAME not in self.profileAttributes
        else:
            _bValid = tskName_ is not None
            if _FwTaskProfile._ATTR_KEY_TASK_NAME in self.profileAttributes:
                _specName = self.profileAttributes[_FwTaskProfile._ATTR_KEY_TASK_NAME]
                rlogif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_TaskProfile_TID_011).format(_specName))

        if not _bValid:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00299)
            self.profileStatus = _AbsFwProfile._EValidationStatus.eInvalid
            return False

        self.profileAttributes[_FwTaskProfile.__ATTR_KEY_TASK_ID] = tskID_
        if tskName_ is not None:
            self.profileAttributes[_FwTaskProfile._ATTR_KEY_TASK_NAME] = tskName_

        if self.args is None:
            self.profileAttributes[_FwTaskProfile._ATTR_KEY_ARGS] = list()
        if self.kwargs is None:
            self.profileAttributes[_FwTaskProfile._ATTR_KEY_KWARGS] = dict()

        res = _AbsFwProfile.Freeze(self)
        if not res:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00708)
        return res

    def SetRunnable( self
                   , rbl_            : _AbsRunnable
                   , taskName_       : str             =None
                   , trMask_         : _ETaskRightFlag =None
                   , delayedStartMS_ : int             =None):
        if not self.__ValidateRunnable(rbl_, delayedStartMS_=delayedStartMS_):
            self.profileStatus = _AbsFwProfile._EValidationStatus.eInvalid
            return False

        _bValid = True
        if rbl_.isProvidingInternalQueue or rbl_.isProvidingExternalQueue:
            _bValid = self.__SetResources(rbl_, rmask_=None)
        if _bValid:
            if taskName_ is not None:
                _bValid = _StrUtil.IsNonEmptyString(taskName_, stripBefore_=True, bThrowx_=True)
                if _bValid:
                    taskName_ = str(taskName_).strip()
        if _bValid:
            if trMask_ is not None:
                _bValid = _ETaskRightFlag.IsValidTaskRightMask(trMask_)
                if _bValid and rbl_._rblType.isXTaskRunnable:
                    _bValid = _ETaskRightFlag.IsValidFwTaskRightMask(trMask_) or _ETaskRightFlag.IsValidUserTaskRightMask(trMask_)
                    if _bValid:
                        _bValid = trMask_.hasXTaskTaskRight
                    if not _bValid:
                        rlogif._LogOEC(True, _EFwErrorCode.FE_00300)
            else:
                trMask_ = _ETaskRightFlag.UserTaskRightDefaultMask()
                if rbl_._rblType.isXTaskRunnable:
                    trMask_ = _ETaskRightFlag.AddXTaskTaskRight(trMask_)

        if _bValid:
            if delayedStartMS_ is not None:
                _bValid  = _Util.IsInstance(delayedStartMS_, int)
                _bValid = _bValid and _Util.CheckMinRange(delayedStartMS_, 1, bThrowx_=True)

        if not _bValid:
            self.profileStatus = _AbsFwProfile._EValidationStatus.eInvalid
        else:
            self.profileAttributes[_FwTaskProfile._ATTR_KEY_RUNNABLE] = rbl_
            if taskName_ is not None:
                self.profileAttributes[_FwTaskProfile._ATTR_KEY_TASK_NAME] = taskName_
            if delayedStartMS_ is not None:
                self.profileAttributes[_FwTaskProfile._ATTR_KEY_DELAYED_START_TIME_SPAN] = delayedStartMS_
            self.profileAttributes[_FwTaskProfile._ATTR_KEY_TASK_RIGHTS] = trMask_

            self.profileStatus = _AbsFwProfile._EValidationStatus.eValid
            rbl_._RblSetTaskProfile(self)
        return self.isValid

    def SetEnclosedPyThread( self
                           , enclHThrd_    : _PyThread
                           , rbl_          : _AbsRunnable
                           , taskName_     : str             =None
                           , trMask_       : _ETaskRightFlag =None
                           , bASEnclHThrd_ : bool            =None):
        if not self.__ValidateRunnable(rbl_, enclHThrd_=enclHThrd_):
            return False

        _bValid = True
        if rbl_.isProvidingInternalQueue or rbl_.isProvidingExternalQueue:
            _bValid = self.__SetResources(rbl_, rmask_=None)
        if _bValid:
            if taskName_ is not None:
                _bValid = _StrUtil.IsNonEmptyString(taskName_, stripBefore_=True, bThrowx_=True)
                if _bValid:
                    taskName_ = str(taskName_).strip()
            else:
                taskName_ = enclHThrd_.name
        if _bValid:
            if trMask_ is not None:
                _bValid = _ETaskRightFlag.IsValidTaskRightMask(trMask_)
                if _bValid and rbl_._rblType.isXTaskRunnable:
                    _bValid = _ETaskRightFlag.IsValidFwTaskRightMask(trMask_) or _ETaskRightFlag.IsValidUserTaskRightMask(trMask_)
                    if _bValid:
                        _bValid = trMask_.hasXTaskTaskRight
                    if not _bValid:
                        rlogif._LogOEC(True, _EFwErrorCode.FE_00301)
            else:
                trMask_ = _ETaskRightFlag.UserTaskRightDefaultMask()
                if rbl_._rblType.isXTaskRunnable:
                    trMask_ = _ETaskRightFlag.AddXTaskTaskRight(trMask_)

        if _bValid:
            if bASEnclHThrd_ is None:
                bASEnclHThrd_ = False
            else:
                _bValid = _bValid and _Util.IsInstance(bASEnclHThrd_, bool)

        if not _bValid:
            self.profileStatus = _AbsFwProfile._EValidationStatus.eInvalid
        else:
            self.profileAttributes[_FwTaskProfile._ATTR_KEY_RUNNABLE] = rbl_
            self.profileAttributes[_FwTaskProfile._ATTR_KEY_ENCLOSED_PYTHREAD] = enclHThrd_
            self.profileAttributes[_FwTaskProfile._ATTR_KEY_AUTO_START_ENCLOSED_PYTHREAD] = bASEnclHThrd_
            self.profileAttributes[_FwTaskProfile._ATTR_KEY_TASK_RIGHTS] = trMask_
            self.profileAttributes[_FwTaskProfile._ATTR_KEY_TASK_NAME] = taskName_

            self.profileStatus = _AbsFwProfile._EValidationStatus.eValid
            rbl_._RblSetTaskProfile(self)
        return self.isValid

    def SetResources(self, rmask_ : _ETaskResFlag =None, timerResource_ =None):
        _rr =  self._GetProfileAttr(_FwTaskProfile._ATTR_KEY_RUNNABLE, ignoreStatus_=False)
        if _rr is None:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00302)
            return False
        else:
            return self.__SetResources(_rr, rmask_=rmask_, timerResource_=timerResource_)

    def SetArgs(self, args_ : list):
        if self.isFrozen:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00303)
            return False
        elif not self.isValid:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00304)
            return False
 
        _bValid = _Util.IsInstance(args_, list)
        if _bValid and (self.args is not None):
            _bValid = False
            rlogif._LogOEC(True, _EFwErrorCode.FE_00305)
 
        if not _bValid:
            self.profileStatus = _AbsFwProfile._EValidationStatus.eInvalid
        else:
            self.profileAttributes[_FwTaskProfile._ATTR_KEY_ARGS] = list(args_)
            self.profileStatus = _AbsFwProfile._EValidationStatus.eValid
        return self.isValid

    def SetKwargs(self, kwargs_ : dict):
        if self.isFrozen:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00306)
            return False
        elif not self.isValid:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00307)
            return False
 
        _bValid = _Util.IsInstance(kwargs_, dict)
        if _bValid and (self.kwargs is not None):
            _bValid = False
            rlogif._LogOEC(True, _EFwErrorCode.FE_00308)
 
        if not _bValid:
            self.profileStatus = _AbsFwProfile._EValidationStatus.eInvalid
        else:
            self.profileAttributes[_FwTaskProfile._ATTR_KEY_KWARGS] = dict(kwargs_)
            self.profileStatus = _AbsFwProfile._EValidationStatus.eValid
        return self.isValid

    @property
    def _isDrivingXTaskTaskProfile(self):
        res  = self.runnable
        if res is not None:
            res = res._rblType.isXTaskRunnable
        return res

    def _ToString(self):
        return self.__class__.__name__

    def _CleanUp(self):
        _myArgs = self._GetProfileAttr(_FwTaskProfile._ATTR_KEY_ARGS, ignoreStatus_=True)
        if _myArgs is not None:
            self.profileAttributes[_FwTaskProfile._ATTR_KEY_ARGS] = None
            _myArgs.clear()

        _myKwargs = self._GetProfileAttr(_FwTaskProfile._ATTR_KEY_KWARGS, ignoreStatus_=True)
        if _myKwargs is not None:
            self.profileAttributes[_FwTaskProfile._ATTR_KEY_KWARGS] = None
            _myKwargs.clear()

        _intQueue = self._GetProfileAttr(_FwTaskProfile.__ATTR_KEY_INT_QUEUE, ignoreStatus_=True)
        if _intQueue is not None:
            self.profileAttributes[_FwTaskProfile.__ATTR_KEY_INT_QUEUE] = None
            _intQueue.CleanUp()

        _extQueue = self._GetProfileAttr(_FwTaskProfile.__ATTR_KEY_EXT_QUEUE, ignoreStatus_=True)
        if _extQueue is not None:
            self.profileAttributes[_FwTaskProfile.__ATTR_KEY_EXT_QUEUE] = None
            _extQueue.CleanUp()

        super()._CleanUp()

    def __ValidateRunnable (self
                           , rbl_            : _AbsRunnable
                           , delayedStartMS_ : int       =None
                           , enclHThrd_      : _PyThread =None):
        if self.profileStatus != _AbsFwProfile._EValidationStatus.eNone:
            if self.isFrozen:
                rlogif._LogOEC(True, _EFwErrorCode.FE_00309)
            elif self.isValid:
                self.profileStatus = _AbsFwProfile._EValidationStatus.eInvalid
                rlogif._LogOEC(True, _EFwErrorCode.FE_00310)
            else:
                rlogif._LogOEC(True, _EFwErrorCode.FE_00311)

            return False

        _bCheckOK =         _Util.IsInstance(rbl_, _AbsRunnable, bThrowx_=True)
        _bCheckOK = _bCheckOK and ((enclHThrd_ is None) or _Util.IsInstance(enclHThrd_, _PyThread, bThrowx_=True))
        _bCheckOK = _bCheckOK and ((delayedStartMS_ is None) or _Util.IsInstance(delayedStartMS_, int, bThrowx_=True))

        if not _bCheckOK:
            return False

        if rbl_._rblType is None:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00312)
            return False

        if rbl_._rblType.isXTaskRunnable:
            _uta  = rbl_._utAgent
            _utp = _uta.taskProfile
            if _utp.isSyncTask:
                _bCheckOK = enclHThrd_ is not None
            else:
                _bCheckOK = enclHThrd_ is None

            if not _bCheckOK:
                rlogif._LogOEC(True, _EFwErrorCode.FE_00313)
            elif delayedStartMS_ is not None:
                _bCheckOK = False
                rlogif._LogOEC(True, _EFwErrorCode.FE_00314)

            if not _bCheckOK:
                return False

        return True

    def __SetResources( self, rbl_ : _AbsRunnable, rmask_ : _ETaskResFlag =None, timerResource_ =None):
        if self.isFrozen:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00315)
            return False
        if not self.isValid:
            if self.profileStatus != _AbsFwProfile._EValidationStatus.eNone:
                rlogif._LogOEC(True, _EFwErrorCode.FE_00316)
                return False

        if not _Util.IsInstance(rbl_, _AbsRunnable, bThrowx_=True):
            self.profileStatus = _AbsFwProfile._EValidationStatus.eInvalid
            return False
        if rmask_ is not None:
            if _Util.IsInstance(rmask_, _ETaskResFlag, bThrowx_=True):
                self.profileStatus = _AbsFwProfile._EValidationStatus.eInvalid
                return False
        else:
            rmask_ = _ETaskResFlag.eNone

        _bValid, _rmask = True, self.resourcesMask
        if _rmask is None:
            _rmask = _ETaskResFlag.eNone

        if _bValid and rbl_.isProvidingInternalQueue:
            if self.internalQueue is None:
                _intQueue = _FwQueue.CreateInstance()
                _bValid = _intQueue is not None
                if _bValid:
                    self.profileAttributes[_FwTaskProfile.__ATTR_KEY_INT_QUEUE] = _intQueue

        if _bValid and rbl_.isProvidingExternalQueue:
            _xqSize = self._GetProfileAttr(_FwTaskProfile._ATTR_KEY_EXTERNAL_QUEUE_SIZE, ignoreStatus_=True)
            if _xqSize is not None:
                if not (_Util.IsInstance(_xqSize, int, bThrowx_=True) and _Util.CheckMinRange(_xqSize, 0)):
                    self.profileStatus = _AbsFwProfile._EValidationStatus.eInvalid
                    return False
            elif rbl_._rblType.isXTaskRunnable:
                _xqSize = _FwQueue.GetFiniteQueueDefaultSize()
            _bOnSizeBlockingXQ = not (rbl_.isProvidingAutoManagedExternalQueue and rbl_.isProvidingRunExecutable)

            if rbl_._rblType.isXTaskRunnable:
                _bAttrOnSizeBlockingXQ = rbl_._utAgent.taskProfile.isExternalQueueBlocking
            else:
                _bAttrOnSizeBlockingXQ = self._GetProfileAttr(_FwTaskProfile._ATTR_KEY_ON_SIZE_BLOCKING_XQUEUE, ignoreStatus_=True)
            if _bAttrOnSizeBlockingXQ is not None:
                if _bAttrOnSizeBlockingXQ != _bOnSizeBlockingXQ:
                    self.profileStatus = _AbsFwProfile._EValidationStatus.eInvalid
                    rlogif._LogOEC(True, _EFwErrorCode.FE_00324)
                    return False

            if self.externalQueue is None:
                if not _bOnSizeBlockingXQ:
                    _extQueue = _FwQueue.CreateInstance(maxSize_=_xqSize)
                else:
                    _extQueue = _FwQueue.CreateInstanceBlockingOnSize(maxSize_=_xqSize)
                _bValid = _extQueue is not None
                if _bValid:
                    self.profileAttributes[_FwTaskProfile.__ATTR_KEY_EXT_QUEUE] = _extQueue
                    self.profileAttributes[_FwTaskProfile._ATTR_KEY_ON_SIZE_BLOCKING_XQUEUE] = _bOnSizeBlockingXQ
                    if _xqSize is not None:
                        self.profileAttributes[_FwTaskProfile._ATTR_KEY_EXTERNAL_QUEUE_SIZE] = _xqSize

        if not _bValid:
            self.profileStatus = _AbsFwProfile._EValidationStatus.eInvalid
        return _bValid

    def _Validate(self, dictAttrs_ : dict):
        if self._GetProfileHandlersList() is None:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00325)
            return
        elif self.profileStatus != _AbsFwProfile._EValidationStatus.eNone:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00709)
            return
        elif (dictAttrs_ is None) or len(dictAttrs_) == 0:
            return
        elif not _AbsFwProfile._CheckMutuallyExclusiveAttrs(dictAttrs_, [_FwTaskProfile._ATTR_KEY_TIMER, _FwTaskProfile._ATTR_KEY_TIMER_PROFILE]):
            return

        for _pah in self._GetProfileHandlersList():
            if _pah.attrName not in dictAttrs_:
                continue
            elif _pah.attrName == _FwTaskProfile._ATTR_KEY_RUNNABLE:
                if _FwTaskProfile._ATTR_KEY_ENCLOSED_PYTHREAD in dictAttrs_:
                    continue

            _arg = dictAttrs_[_pah.attrName]
            _hh = _pah.handler

            _optArgs = None
            if _pah.optAttrsNames is not None:
                _optArgs = list()
                for _kk in _pah.optAttrsNames:
                    if _kk not in dictAttrs_:
                        _vv = None
                    else:
                        _vv = dictAttrs_[_kk]
                    _optArgs.append(_vv)
                if len(_optArgs) == 0:
                    _optArgs = None

            if _optArgs is not None:
                _hh(self, _arg, *_optArgs)
            else:
                _hh(self, _arg)

    @staticmethod
    def __SetupProfileHandlersList():
        _pahList = list()

        _lstAttrKeys = [ _FwTaskProfile._ATTR_KEY_TASK_NAME
                      , _FwTaskProfile._ATTR_KEY_TASK_RIGHTS
                      , _FwTaskProfile._ATTR_KEY_DELAYED_START_TIME_SPAN ]
        _pah = _AbsFwProfile._ProfileAttributeHandler(_FwTaskProfile._ATTR_KEY_RUNNABLE, _FwTaskProfile.SetRunnable, _lstAttrKeys)
        _pahList.append(_pah)

        _lstAttrKeys = [ _FwTaskProfile._ATTR_KEY_RUNNABLE
                      , _FwTaskProfile._ATTR_KEY_TASK_NAME
                      , _FwTaskProfile._ATTR_KEY_TASK_RIGHTS
                      , _FwTaskProfile._ATTR_KEY_AUTO_START_ENCLOSED_PYTHREAD ]
        _pah = _AbsFwProfile._ProfileAttributeHandler(_FwTaskProfile._ATTR_KEY_ENCLOSED_PYTHREAD, _FwTaskProfile.SetEnclosedPyThread, _lstAttrKeys)
        _pahList.append(_pah)

        _lstAttrKeys = [ _FwTaskProfile.__ATTR_KEY_TIMER_RESOURCE ]
        _pah = _AbsFwProfile._ProfileAttributeHandler(_FwTaskProfile._ATTR_KEY_RESOURCES_MASK, _FwTaskProfile.SetResources, _lstAttrKeys)
        _pahList.append(_pah)

        _pah = _AbsFwProfile._ProfileAttributeHandler(_FwTaskProfile._ATTR_KEY_ARGS, _FwTaskProfile.SetArgs)
        _pahList.append(_pah)

        _pah = _AbsFwProfile._ProfileAttributeHandler(_FwTaskProfile._ATTR_KEY_KWARGS, _FwTaskProfile.SetKwargs)
        _pahList.append(_pah)

        return _AbsFwProfile._SetProfileHandlersList(_FwTaskProfile.__name__, _pahList)
