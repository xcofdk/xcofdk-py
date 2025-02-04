# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : taskprofile.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from xcofdk._xcofw.fwadapter                              import rlogif
from xcofdk._xcofw.fw.fwssys.fwcore.base.listutil         import _ListUtil
from xcofdk._xcofw.fw.fwssys.fwcore.base.strutil          import _StrUtil
from xcofdk._xcofw.fw.fwssys.fwcore.base.util             import _Util
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject         import _AbstractSlotsObject
from xcofdk._xcofw.fw.fwssys.fwcore.types.aprofile        import _AbstractProfile
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.arunnabledefs import _ERunnableApiFuncTag
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.arunnable     import _AbstractRunnable
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil      import _TaskUtil
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil      import _ETaskResourceFlag
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil      import _ETaskRightFlag
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil      import _PyThread

from xcofdk._xcofw.fw.fwssys.fwerrh.fwerrorcodes import _EFwErrorCode

from xcofdk._xcofwa.fwadmindefs import _FwSubsystemCoding

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine

if not _FwSubsystemCoding.IsSubsystemMessagingConfigured():
    _FwQueue, _FwTimer, _TimerProfile = object, object, object
else:
    from xcofdk._xcofw.fw.fwssys.fwmsg.disp.fwqueue import _FwQueue
    _FwTimer, _TimerProfile = object, object

class _TaskProfile(_AbstractProfile):

    __slots__ = []

    _ATTR_KEY_ARGS                         = _AbstractProfile._ATTR_KEY_ARGS
    _ATTR_KEY_KWARGS                       = _AbstractProfile._ATTR_KEY_KWARGS
    __ATTR_KEY_TASK_ID                     = _AbstractProfile._ATTR_KEY_TASK_ID
    _ATTR_KEY_TASK_NAME                    = _AbstractProfile._ATTR_KEY_TASK_NAME
    _ATTR_KEY_TASK_RIGHTS                  = _AbstractProfile._ATTR_KEY_TASK_RIGHTS
    _ATTR_KEY_ENCLOSED_PYTHREAD            = _AbstractProfile._ATTR_KEY_ENCLOSED_PYTHREAD
    _ATTR_KEY_AUTO_START_ENCLOSED_PYTHREAD = _AbstractProfile._ATTR_KEY_AUTO_START_ENCLOSED_PYTHREAD

    _ATTR_KEY_TIMER                        = _FwTDbEngine.GetText(_EFwTextID.eTaskProfile_AttrName_ATTR_KEY_TIMER)
    _ATTR_KEY_RUNNABLE                     = _FwTDbEngine.GetText(_EFwTextID.eTaskProfile_AttrName_ATTR_KEY_RUNNABLE)
    __ATTR_KEY_EXT_QUEUE                   = _FwTDbEngine.GetText(_EFwTextID.eTaskProfile_AttrName_ATTR_KEY_EXT_QUEUE)
    __ATTR_KEY_INT_QUEUE                   = _FwTDbEngine.GetText(_EFwTextID.eTaskProfile_AttrName_ATTR_KEY_INT_QUEUE)
    _ATTR_KEY_TIMER_PROFILE                = _FwTDbEngine.GetText(_EFwTextID.eTaskProfile_AttrName_ATTR_KEY_TIMER_PROFILE)
    _ATTR_KEY_RESOURCES_MASK               = _FwTDbEngine.GetText(_EFwTextID.eTaskProfile_AttrName_ATTR_KEY_RESOURCES_MASK)
    _ATTR_KEY_EXTERNAL_QUEUE_SIZE          = _FwTDbEngine.GetText(_EFwTextID.eTaskProfile_AttrName_ATTR_KEY_EXTERNAL_QUEUE_SIZE)
    _ATTR_KEY_DELAYED_START_TIME_SPAN      = _FwTDbEngine.GetText(_EFwTextID.eTaskProfile_AttrName_ATTR_KEY_DELAYED_START_TIME_SPAN)
    _ATTR_KEY_ON_SIZE_BLOCKING_XQUEUE      = _FwTDbEngine.GetText(_EFwTextID.eTaskProfile_AttrName_ATTR_KEY_ON_SIZE_BLOCKING_XQUEUE)
    __ATTR_KEY_TIMER_RESOURCE              = _FwTDbEngine.GetText(_EFwTextID.eTaskProfile_AttrName_ATTR_KEY_TIMER_RESOURCE)

    __bUSE_AUTO_GENERATED_TASK_NAMES_ONLY = True

    def __init__( self
                , runnable_                   : _AbstractRunnable    =None
                , taskName_                   : str                  =None
                , resourcesMask_              : _ETaskResourceFlag    =None
                , delayedStartTimeSpanMS_     : int                  =None
                , enclosedPyThread_           : _PyThread            =None
                , bAutoStartEnclosedPyThread_ : bool                 =None
                , args_                       : list                 =None
                , kwargs_                     : dict                 =None
                , taskProfileAttrs_           : dict                 =None ):

        _AbstractSlotsObject.__init__(self)

        _SB_KEY   = _TaskProfile._ATTR_KEY_ON_SIZE_BLOCKING_XQUEUE
        _RBL_KEY  = _TaskProfile._ATTR_KEY_RUNNABLE
        _TRM_KEY  = _TaskProfile._ATTR_KEY_TASK_RIGHTS
        _RESM_KEY = _TaskProfile._ATTR_KEY_RESOURCES_MASK

        _bError    = False
        _dictAttrs = {}

        if self._GetProfileHandlersList() is None:
            if not _TaskProfile.__SetupProfileHandlersList():
                _bError = True
        if not _bError:
            if runnable_ is not None:
                _dictAttrs[_RBL_KEY] = runnable_
            if taskName_ is not None:
                _dictAttrs[_TaskProfile._ATTR_KEY_TASK_NAME] = taskName_
            if resourcesMask_ is not None:
                _dictAttrs[_RESM_KEY] = resourcesMask_
            if delayedStartTimeSpanMS_ is not None:
                _dictAttrs[_TaskProfile._ATTR_KEY_DELAYED_START_TIME_SPAN] = delayedStartTimeSpanMS_
            if enclosedPyThread_ is not None:
                _dictAttrs[_TaskProfile._ATTR_KEY_ENCLOSED_PYTHREAD] = enclosedPyThread_
            if bAutoStartEnclosedPyThread_ is not None:
                _dictAttrs[_TaskProfile._ATTR_KEY_AUTO_START_ENCLOSED_PYTHREAD] = bAutoStartEnclosedPyThread_
            if args_ is not None:
                _dictAttrs[_TaskProfile._ATTR_KEY_ARGS] = args_
            if kwargs_ is not None:
                _dictAttrs[_TaskProfile._ATTR_KEY_KWARGS] = kwargs_

            if taskProfileAttrs_ is not None:
                if not _Util.IsInstance(taskProfileAttrs_, dict, bThrowx_=True):
                    _bError = True
                else:
                    for _kk in taskProfileAttrs_.keys():
                        if taskProfileAttrs_[_kk] is None:
                            continue
                        if _kk not in _dictAttrs:
                            _dictAttrs[_kk] = taskProfileAttrs_[_kk]
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
            elif _rbl._eRunnableType is None:
                _bError = True
                rlogif._LogOEC(True, _EFwErrorCode.FE_00291)
            elif (_trm is not None) and not _ETaskRightFlag.IsValidTaskRightMask(_trm):
                _bError = True
                rlogif._LogOEC(True, _EFwErrorCode.FE_00292)
            elif (_resm is not None) and not isinstance(_resm, _ETaskResourceFlag):
                _bError = True
                rlogif._LogOEC(True, _EFwErrorCode.FE_00293)
            elif (_resm is not None) and _rbl._eRunnableType.isXTaskRunnable:
                _bError = True
                rlogif._LogOEC(True, _EFwErrorCode.FE_00294)
            elif (_sb is not None) and _rbl._eRunnableType.isXTaskRunnable:
                _bError = True
                rlogif._LogOEC(True, _EFwErrorCode.FE_00295)
            else:
                if _trm is not None:
                    _dictAttrs[_TRM_KEY] = _trm
                if _rbl._eRunnableType.isXTaskRunnable:

                    _resm = _ETaskResourceFlag.GetRessourcesMask(False)
                    if not (_resm is None or _resm == _ETaskResourceFlag.eNone):
                        _dictAttrs[_RESM_KEY] = _resm
                if (_sb is None) and not _rbl._eRunnableType.isXTaskRunnable:
                    _dictAttrs[_SB_KEY] = True

        if _bError:
            _AbstractProfile.__init__(self, _AbstractProfile._EProfileType.eTask, profileAttrs_=None)
            self.profileStatus = _AbstractProfile._EValidationStatus.eInvalid
        else:
            _AbstractProfile.__init__(self, _AbstractProfile._EProfileType.eTask, profileAttrs_=_dictAttrs)
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
    def isAutoStartEnclosedPyThreadEnabled(self) -> bool:
        return self._GetProfileAttr(_TaskProfile._ATTR_KEY_AUTO_START_ENCLOSED_PYTHREAD)

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
            res = self._GetProfileAttr(_TaskProfile._ATTR_KEY_ON_SIZE_BLOCKING_XQUEUE)
            res = res == True
        return res

    @property
    def hasTimerResource(self):
        res = self.resourcesMask
        if res is not None:
            res = _ETaskResourceFlag.IsResourceFlagSet(res, _ETaskResourceFlag.eTimer)
        return res

    @property
    def taskID(self) -> int:
        return self._GetProfileAttr(_TaskProfile.__ATTR_KEY_TASK_ID)

    @property
    def taskName(self) -> str:
        return self._GetProfileAttr(_TaskProfile._ATTR_KEY_TASK_NAME)

    @property
    def taskRightsMask(self):
        return self._GetProfileAttr(_TaskProfile._ATTR_KEY_TASK_RIGHTS)

    @property
    def runnable(self) -> _AbstractRunnable:
        return self._GetProfileAttr(_TaskProfile._ATTR_KEY_RUNNABLE)

    @property
    def resourcesMask(self):
        return self._GetProfileAttr(_TaskProfile._ATTR_KEY_RESOURCES_MASK)

    @property
    def delayedStartTimeSpanMS(self):
        res = self._GetProfileAttr(_TaskProfile._ATTR_KEY_DELAYED_START_TIME_SPAN)
        if res is None:
            res = 0
        return res

    @property
    def enclosedPyThread(self) -> _PyThread:
        return self._GetProfileAttr(_TaskProfile._ATTR_KEY_ENCLOSED_PYTHREAD)

    @property
    def args(self) -> list:
        return self._GetProfileAttr(_TaskProfile._ATTR_KEY_ARGS)

    @property
    def kwargs(self) -> dict:
        return self._GetProfileAttr(_TaskProfile._ATTR_KEY_KWARGS)

    @property
    def timerResource(self) -> _FwTimer:
        return self._GetProfileAttr(_TaskProfile._ATTR_KEY_TIMER)

    @property
    def timerProfile(self) -> _TimerProfile:
        res = self.timerResource
        if res is not None:
            res = res.timerProfile
        return res

    @property
    def internalQueue(self) -> _FwQueue:
        return self._GetProfileAttr(_TaskProfile.__ATTR_KEY_INT_QUEUE)

    @property
    def externalQueue(self) -> _FwQueue:
        return self._GetProfileAttr(_TaskProfile.__ATTR_KEY_EXT_QUEUE)

    @property
    def externalQueueSize(self) -> int:
        return self._GetProfileAttr(_TaskProfile._ATTR_KEY_EXTERNAL_QUEUE_SIZE)

    def Freeze(self, *args_, **kwargs_):
        if self.isFrozen:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00296)
            return False
        elif not self.isValid:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00297)
            return False
        elif self.runnable is None:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00298)
            return False

        _lstArgs = _ListUtil.UnpackArgs(*args_, minArgsNum_=1, maxArgsNum_=2, bThrowx_=True)
        if len(_lstArgs) == 0:
            return False

        _tskID   = 0
        _tskName = None
        for _ii in range(len(_lstArgs)):
            val = _lstArgs[_ii]
            if   _ii == 0: _tskID   = val
            elif _ii == 1: _tskName = val

        if not _TaskProfile.__bUSE_AUTO_GENERATED_TASK_NAMES_ONLY:
            _bValid  = (_tskName is None) and _TaskProfile._ATTR_KEY_TASK_NAME in self.profileAttributes
            _bValid |= (_tskName is not None) and not _TaskProfile._ATTR_KEY_TASK_NAME in self.profileAttributes
        else:
            _bValid = _tskName is not None
            if _TaskProfile._ATTR_KEY_TASK_NAME in self.profileAttributes:
                _specName = self.profileAttributes[_TaskProfile._ATTR_KEY_TASK_NAME]
                rlogif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_TaskProfile_TextID_011).format(_specName))

        if not _bValid:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00299)
            self.profileStatus = _AbstractProfile._EValidationStatus.eInvalid
            return False

        self.profileAttributes[_TaskProfile.__ATTR_KEY_TASK_ID] = _tskID
        if _tskName is not None:
            if not _TaskProfile.__bUSE_AUTO_GENERATED_TASK_NAMES_ONLY:
                self.profileAttributes[_TaskProfile._ATTR_KEY_TASK_NAME] = _tskName

        if self.args is None:
            self.profileAttributes[_TaskProfile._ATTR_KEY_ARGS] = list()
        if self.kwargs is None:
            self.profileAttributes[_TaskProfile._ATTR_KEY_KWARGS] = dict()

        res = _AbstractProfile.Freeze(self)
        if not res:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00708)
        return res

    def SetRunnable( self
                   , runnable_               : _AbstractRunnable
                   , taskName_               : str               =None
                   , trMask_                 : _ETaskRightFlag    =None
                   , delayedStartTimeSpanMS_ : int               =None):

        bValidRunnable = self.__ValidateRunnable(runnable_, delayedStartTimeSpanMS_=delayedStartTimeSpanMS_)
        if not bValidRunnable:
            self.profileStatus = _AbstractProfile._EValidationStatus.eInvalid
            return False

        _bValid = True
        if runnable_.isProvidingInternalQueue or runnable_.isProvidingExternalQueue:
            _bValid = self.__SetResources(runnable_, resourcesMask_=None)
        if _bValid:
            if taskName_ is not None:
                _bValid = _StrUtil.IsNonEmptyString(taskName_, stripBefore_=True, bThrowx_=True)
                if _bValid:
                    taskName_ = str(taskName_).strip()
        if _bValid:
            if trMask_ is not None:
                _bValid = _ETaskRightFlag.IsValidTaskRightMask(trMask_)
                if _bValid and runnable_._eRunnableType.isXTaskRunnable:
                    _bValid = _ETaskRightFlag.IsValidFwTaskRightMask(trMask_) or _ETaskRightFlag.IsValidUserTaskRightMask(trMask_)
                    if _bValid:
                        _bValid = trMask_.hasXTaskTaskRight
                    if not _bValid:
                        rlogif._LogOEC(True, _EFwErrorCode.FE_00300)
            else:
                trMask_ = _ETaskRightFlag.UserTaskRightDefaultMask()
                if runnable_._eRunnableType.isXTaskRunnable:
                    trMask_ = _ETaskRightFlag.AddXTaskTaskRight(trMask_)

        if _bValid:
            if delayedStartTimeSpanMS_ is not None:
                _bValid  = _Util.IsInstance(delayedStartTimeSpanMS_, int)
                _bValid = _bValid and _Util.CheckMinRange(delayedStartTimeSpanMS_, 1, bThrowx_=True)

        if not _bValid:
            self.profileStatus = _AbstractProfile._EValidationStatus.eInvalid
        else:
            self.profileAttributes[_TaskProfile._ATTR_KEY_RUNNABLE] = runnable_
            if taskName_ is not None:
                if not _TaskProfile.__bUSE_AUTO_GENERATED_TASK_NAMES_ONLY:
                    self.profileAttributes[_TaskProfile._ATTR_KEY_TASK_NAME] = taskName_
            if delayedStartTimeSpanMS_ is not None:
                self.profileAttributes[_TaskProfile._ATTR_KEY_DELAYED_START_TIME_SPAN] = delayedStartTimeSpanMS_
            self.profileAttributes[_TaskProfile._ATTR_KEY_TASK_RIGHTS] = trMask_

            self.profileStatus = _AbstractProfile._EValidationStatus.eValid
            runnable_._SetTaskProfile(self)
        return self.isValid

    def SetEnclosedPyThread( self
                           , enclosedPyThread_           : _PyThread
                           , runnable_                   : _AbstractRunnable
                           , taskName_                   : str               =None
                           , trMask_                     : _ETaskRightFlag    =None
                           , bAutoStartEnclosedPyThread_ : bool              =None):
        if not self.__ValidateRunnable(runnable_, enclosedPyThread_=enclosedPyThread_):
            return False

        _bValid = True
        if runnable_.isProvidingInternalQueue or runnable_.isProvidingExternalQueue:
            _bValid = self.__SetResources(runnable_, resourcesMask_=None)
        if _bValid:
            if taskName_ is not None:
                _bValid = _StrUtil.IsNonEmptyString(taskName_, stripBefore_=True, bThrowx_=True)
                if _bValid:
                    taskName_ = str(taskName_).strip()
            else:
                taskName_ = enclosedPyThread_.name
        if _bValid:
            if trMask_ is not None:
                _bValid = _ETaskRightFlag.IsValidTaskRightMask(trMask_)
                if _bValid and runnable_._eRunnableType.isXTaskRunnable:
                    _bValid = _ETaskRightFlag.IsValidFwTaskRightMask(trMask_) or _ETaskRightFlag.IsValidUserTaskRightMask(trMask_)
                    if _bValid:
                        _bValid = trMask_.hasXTaskTaskRight
                    if not _bValid:
                        rlogif._LogOEC(True, _EFwErrorCode.FE_00301)
            else:
                trMask_ = _ETaskRightFlag.UserTaskRightDefaultMask()
                if runnable_._eRunnableType.isXTaskRunnable:
                    trMask_ = _ETaskRightFlag.AddXTaskTaskRight(trMask_)

        if _bValid:
            if bAutoStartEnclosedPyThread_ is None:
                bAutoStartEnclosedPyThread_ = False
            else:
                _bValid = _bValid and _Util.IsInstance(bAutoStartEnclosedPyThread_, bool)

        if not _bValid:
            self.profileStatus = _AbstractProfile._EValidationStatus.eInvalid
        else:
            self.profileAttributes[_TaskProfile._ATTR_KEY_RUNNABLE] = runnable_
            self.profileAttributes[_TaskProfile._ATTR_KEY_ENCLOSED_PYTHREAD] = enclosedPyThread_
            self.profileAttributes[_TaskProfile._ATTR_KEY_AUTO_START_ENCLOSED_PYTHREAD] = bAutoStartEnclosedPyThread_
            self.profileAttributes[_TaskProfile._ATTR_KEY_TASK_RIGHTS] = trMask_
            if not _TaskProfile.__bUSE_AUTO_GENERATED_TASK_NAMES_ONLY:
                self.profileAttributes[_TaskProfile._ATTR_KEY_TASK_NAME] = taskName_

            self.profileStatus = _AbstractProfile._EValidationStatus.eValid
            runnable_._SetTaskProfile(self)
        return self.isValid

    def AddResourceTimer(self, timerResource_):
        return self.SetResources(resourcesMask_=_ETaskResourceFlag.eTimer, timerResource_=timerResource_)

    def SetResources(self, resourcesMask_ : _ETaskResourceFlag =None, timerResource_ =None):
        _rr =  self._GetProfileAttr(_TaskProfile._ATTR_KEY_RUNNABLE, ignoreStatus_=False)
        if _rr is None:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00302)
            return False
        else:
            return self.__SetResources(_rr, resourcesMask_=resourcesMask_, timerResource_=timerResource_)

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
            self.profileStatus = _AbstractProfile._EValidationStatus.eInvalid
        else:
            self.profileAttributes[_TaskProfile._ATTR_KEY_ARGS] = list(args_)
            self.profileStatus = _AbstractProfile._EValidationStatus.eValid
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
            self.profileStatus = _AbstractProfile._EValidationStatus.eInvalid
        else:
            self.profileAttributes[_TaskProfile._ATTR_KEY_KWARGS] = dict(kwargs_)
            self.profileStatus = _AbstractProfile._EValidationStatus.eValid
        return self.isValid

    @property
    def _isDrivingXTaskTaskProfile(self):
        res  = self.runnable
        if res is not None:
            res = res._eRunnableType.isXTaskRunnable
        return res

    def _ToString(self, *args_, **kwargs_):
        _rr      = self._GetProfileAttr(_TaskProfile._ATTR_KEY_RUNNABLE, ignoreStatus_=True)
        _xtsk = None if _rr is None else _rr._xtaskInst
        _ept     = self._GetProfileAttr(_TaskProfile._ATTR_KEY_ENCLOSED_PYTHREAD, ignoreStatus_=True)

        if _xtsk is not None:
            _ownerTitle = _FwTDbEngine.GetText(_EFwTextID.eMisc_XTask)
            _ownerName  = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_006).format(_xtsk.xtaskName)
        elif _ept is not None:
            _ownerTitle = _FwTDbEngine.GetText(_EFwTextID.eMisc_EnclPyThread)
            _ownerName  = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_011).format(_ept.name, _ept.native_id)
        elif _rr is not None:
            _ownerTitle = _FwTDbEngine.GetText(_EFwTextID.eMisc_Runnable)
            _ownerName  = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_006).format(_rr.ToString())
        else:
            _ownerTitle = _FwTDbEngine.GetText(_EFwTextID.eMisc_Id)
            _ownerName  = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_006).format(id(self))

        _resm = self.resourcesMask

        if _resm is None:
            _resm = _ETaskResourceFlag.eNone
        if not self.isValid:
            res = _FwTDbEngine.GetText(_EFwTextID.eTaskProfile_ToString_01).format(_ownerTitle, _ownerName)
        else:
            _lenArgs   = 0 if self.args is None else len(self.args)
            _lenKwargs = 0 if self.kwargs is None else len(self.kwargs)

            if self.isEnclosingPyThread:
                res = _FwTDbEngine.GetText(_EFwTextID.eTaskProfile_ToString_02).format(
                    _ownerTitle, _ownerName, hex(_resm), hex(self.taskRightsMask), self.isAutoStartEnclosedPyThreadEnabled, _lenArgs, _lenKwargs)
            else:
                if self.taskName is None:
                    res = _FwTDbEngine.GetText(_EFwTextID.eTaskProfile_ToString_03).format(
                        _ownerTitle, _ownerName, hex(_resm), hex(self.taskRightsMask), self.delayedStartTimeSpanMS, _lenArgs, _lenKwargs)
                else:
                    res = _FwTDbEngine.GetText(_EFwTextID.eTaskProfile_ToString_04).format(
                        _ownerTitle, _ownerName, self.taskName, hex(_resm), hex(self.taskRightsMask), self.delayedStartTimeSpanMS, _lenArgs, _lenKwargs)
        res = '{}: {}'.format(type(self).__name__, res)
        return res

    def _CleanUp(self):
        _myArgs = self._GetProfileAttr(_TaskProfile._ATTR_KEY_ARGS, ignoreStatus_=True)
        if _myArgs is not None:
            self.profileAttributes[_TaskProfile._ATTR_KEY_ARGS] = None
            _myArgs.clear()

        _myKwargs = self._GetProfileAttr(_TaskProfile._ATTR_KEY_KWARGS, ignoreStatus_=True)
        if _myKwargs is not None:
            self.profileAttributes[_TaskProfile._ATTR_KEY_KWARGS] = None
            _myKwargs.clear()

        _intQueue = self._GetProfileAttr(_TaskProfile.__ATTR_KEY_INT_QUEUE, ignoreStatus_=True)
        if _intQueue is not None:
            self.profileAttributes[_TaskProfile.__ATTR_KEY_INT_QUEUE] = None
            _intQueue.CleanUp()

        _extQueue = self._GetProfileAttr(_TaskProfile.__ATTR_KEY_EXT_QUEUE, ignoreStatus_=True)
        if _extQueue is not None:
            self.profileAttributes[_TaskProfile.__ATTR_KEY_EXT_QUEUE] = None
            _extQueue.CleanUp()

        super()._CleanUp()

    def __ValidateRunnable (self
                           , runnable_               : _AbstractRunnable
                           , delayedStartTimeSpanMS_ : int               =None
                           , enclosedPyThread_       : _PyThread         =None):

        if self.profileStatus != _AbstractProfile._EValidationStatus.eNone:
            if self.isFrozen:
                rlogif._LogOEC(True, _EFwErrorCode.FE_00309)
            elif self.isValid:
                self.profileStatus = _AbstractProfile._EValidationStatus.eInvalid
                rlogif._LogOEC(True, _EFwErrorCode.FE_00310)
            else:
                rlogif._LogOEC(True, _EFwErrorCode.FE_00311)

            return False

        _bCheckOK =         _Util.IsInstance(runnable_, _AbstractRunnable, bThrowx_=True)
        _bCheckOK = _bCheckOK and ((enclosedPyThread_ is None) or _Util.IsInstance(enclosedPyThread_, _PyThread, bThrowx_=True))
        _bCheckOK = _bCheckOK and ((delayedStartTimeSpanMS_ is None) or _Util.IsInstance(delayedStartTimeSpanMS_, int, bThrowx_=True))

        if not _bCheckOK:
            return False

        if runnable_._eRunnableType is None:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00312)
            return False

        if runnable_._eRunnableType.isXTaskRunnable:
            if runnable_._xtaskInst.xtaskProfile.isSynchronousTask:
                _bCheckOK = enclosedPyThread_ is not None
            else:
                _bCheckOK = enclosedPyThread_ is None

            if not _bCheckOK:
                rlogif._LogOEC(True, _EFwErrorCode.FE_00313)
            elif delayedStartTimeSpanMS_ is not None:
                _bCheckOK = False
                rlogif._LogOEC(True, _EFwErrorCode.FE_00314)

            if not _bCheckOK:
                return False

        return True

    def __SetResources( self, runnable_ : _AbstractRunnable, resourcesMask_ : _ETaskResourceFlag =None, timerResource_ =None):
        if self.isFrozen:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00315)
            return False
        if not self.isValid:
            if self.profileStatus != _AbstractProfile._EValidationStatus.eNone:
                rlogif._LogOEC(True, _EFwErrorCode.FE_00316)
                return False

        if not _Util.IsInstance(runnable_, _AbstractRunnable, bThrowx_=True):
            self.profileStatus = _AbstractProfile._EValidationStatus.eInvalid
            return False
        if resourcesMask_ is not None:
            if _Util.IsInstance(resourcesMask_, _ETaskResourceFlag, bThrowx_=True):
                self.profileStatus = _AbstractProfile._EValidationStatus.eInvalid
                return False
        else:
            resourcesMask_ = _ETaskResourceFlag.eNone

        _bValid, _rmask = True, self.resourcesMask
        if _rmask is None:
            _rmask = _ETaskResourceFlag.eNone

        if _ETaskResourceFlag.IsResourceFlagSet(resourcesMask_, _ETaskResourceFlag.eTimer):
            _bValid = not self.isEnclosingStartupThread
            if not _bValid:
                rlogif._LogOEC(True, _EFwErrorCode.FE_00317)
            else:
                _bValid = not _ETaskResourceFlag.IsResourceFlagSet(_rmask, _ETaskResourceFlag.eTimer)
                if not _bValid:
                    rlogif._LogOEC(True, _EFwErrorCode.FE_00318)
                else:
                    _bValid = _Util.IsInstance(timerResource_, [_FwTimer, _TimerProfile])
                    if not _bValid:
                        rlogif._LogOEC(True, _EFwErrorCode.FE_00319)
                    else:
                        callbackIF = timerResource_.callbackIF
                        _bValid = _bValid and callbackIF.isSpecifiedByInstanceMethod
                        _bValid = _bValid and id(callbackIF.ifsource) == id(runnable_)
                        _bValid = _bValid and callbackIF.methodName == _FwTDbEngine.GetText(_EFwTextID.eMisc_CallbackFunctionName_OnTimeoutExpired)
                        if not _bValid:
                            rlogif._LogOEC(True, _EFwErrorCode.FE_00320)
                        else:
                            _bValid = _Util.GetAttribute(runnable_, _ERunnableApiFuncTag.eRFTOnTimeoutExpired.functionName) is not None
                            if not _bValid:
                                rlogif._LogOEC(True, _EFwErrorCode.FE_00321)
                            else:
                                timerres = timerResource_
                                if isinstance(timerResource_, _TimerProfile):
                                    timerres = _FwTimer.CreateTimer(timerProfile_=timerResource_)
                                _bValid = timerres is not None
                                if _bValid:
                                    self.profileAttributes[_TaskProfile._ATTR_KEY_TIMER] = timerres
                                    _rmask = _ETaskResourceFlag.AddResourceFlag(_rmask, _ETaskResourceFlag.eTimer)
                                    self.profileAttributes[_TaskProfile._ATTR_KEY_RESOURCES_MASK] = _rmask

        if _bValid and runnable_.isProvidingInternalQueue:
            if not _FwSubsystemCoding.IsSubsystemMessagingConfigured():
                _bValid = False
                rlogif._LogOEC(True, _EFwErrorCode.FE_00322)
            else:
                if self.internalQueue is None:
                    _intQueueSize = _FwQueue.GetFiniteQueueDefaultSize()
                    _intQueue = _FwQueue.CreateInstance()
                    _bValid = _intQueue is not None
                    if _bValid:
                        self.profileAttributes[_TaskProfile.__ATTR_KEY_INT_QUEUE] = _intQueue

        if _bValid and runnable_.isProvidingExternalQueue:
            if not _FwSubsystemCoding.IsSubsystemMessagingConfigured():
                _bValid = False
                rlogif._LogOEC(True, _EFwErrorCode.FE_00323)
            else:
                _extQueueSize = self._GetProfileAttr(_TaskProfile._ATTR_KEY_EXTERNAL_QUEUE_SIZE, ignoreStatus_=True)
                if _extQueueSize is not None:
                    if not (_Util.IsInstance(_extQueueSize, int, bThrowx_=True) and _Util.CheckMinRange(_extQueueSize, 0)):
                        self.profileStatus = _AbstractProfile._EValidationStatus.eInvalid
                        return False
                elif runnable_._eRunnableType.isXTaskRunnable:
                    _extQueueSize = _FwQueue.GetFiniteQueueDefaultSize()

                _bOnSizeBlockingXQueue = not (runnable_.isProvidingAutoManagedExternalQueue and runnable_.isProvidingRunExecutable)

                if runnable_._eRunnableType.isXTaskRunnable:
                    _bAttrOnSizeBlockingXQueue = runnable_._xtaskInst.xtaskProfile.isExternalQueueBlocking
                else:
                    _bAttrOnSizeBlockingXQueue = self._GetProfileAttr(_TaskProfile._ATTR_KEY_ON_SIZE_BLOCKING_XQUEUE, ignoreStatus_=True)
                if _bAttrOnSizeBlockingXQueue is not None:
                    if _bAttrOnSizeBlockingXQueue != _bOnSizeBlockingXQueue:
                        self.profileStatus = _AbstractProfile._EValidationStatus.eInvalid
                        rlogif._LogOEC(True, _EFwErrorCode.FE_00324)
                        return False

                if self.externalQueue is None:
                    if not _bOnSizeBlockingXQueue:
                        _extQueue = _FwQueue.CreateInstance(maxSize_=_extQueueSize)
                    else:
                        _extQueue = _FwQueue.CreateInstanceBlockingOnSize(maxSize_=_extQueueSize)
                    _bValid = _extQueue is not None
                    if _bValid:
                        self.profileAttributes[_TaskProfile.__ATTR_KEY_EXT_QUEUE] = _extQueue
                        self.profileAttributes[_TaskProfile._ATTR_KEY_ON_SIZE_BLOCKING_XQUEUE] = _bOnSizeBlockingXQueue
                        if _extQueueSize is not None:
                            self.profileAttributes[_TaskProfile._ATTR_KEY_EXTERNAL_QUEUE_SIZE] = _extQueueSize

        if not _bValid:
            self.profileStatus = _AbstractProfile._EValidationStatus.eInvalid
        return _bValid

    def _Validate(self, dictAttrs_ : dict):
        if self._GetProfileHandlersList() is None:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00325)
            return
        elif self.profileStatus != _AbstractProfile._EValidationStatus.eNone:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00709)
            return
        elif (dictAttrs_ is None) or len(dictAttrs_) == 0:
            return
        elif not _AbstractProfile._CheckMutuallyExclusiveAttrs(dictAttrs_, [_TaskProfile._ATTR_KEY_TIMER, _TaskProfile._ATTR_KEY_TIMER_PROFILE]):
            return

        for _pah in self._GetProfileHandlersList():
            if _pah.attrName not in dictAttrs_:
                continue
            elif _pah.attrName == _TaskProfile._ATTR_KEY_RUNNABLE:
                if _TaskProfile._ATTR_KEY_ENCLOSED_PYTHREAD in dictAttrs_:
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

        _lstAttrKeys = [ _TaskProfile._ATTR_KEY_TASK_NAME
                      , _TaskProfile._ATTR_KEY_TASK_RIGHTS
                      , _TaskProfile._ATTR_KEY_DELAYED_START_TIME_SPAN ]
        _pah = _AbstractProfile._ProfileAttributeHandler(_TaskProfile._ATTR_KEY_RUNNABLE, _TaskProfile.SetRunnable, _lstAttrKeys)
        _pahList.append(_pah)

        _lstAttrKeys = [ _TaskProfile._ATTR_KEY_RUNNABLE
                      , _TaskProfile._ATTR_KEY_TASK_NAME
                      , _TaskProfile._ATTR_KEY_TASK_RIGHTS
                      , _TaskProfile._ATTR_KEY_AUTO_START_ENCLOSED_PYTHREAD ]
        _pah = _AbstractProfile._ProfileAttributeHandler(_TaskProfile._ATTR_KEY_ENCLOSED_PYTHREAD, _TaskProfile.SetEnclosedPyThread, _lstAttrKeys)
        _pahList.append(_pah)

        _lstAttrKeys = [ _TaskProfile.__ATTR_KEY_TIMER_RESOURCE ]
        _pah = _AbstractProfile._ProfileAttributeHandler(_TaskProfile._ATTR_KEY_RESOURCES_MASK, _TaskProfile.SetResources, _lstAttrKeys)
        _pahList.append(_pah)

        _pah = _AbstractProfile._ProfileAttributeHandler(_TaskProfile._ATTR_KEY_ARGS, _TaskProfile.SetArgs)
        _pahList.append(_pah)

        _pah = _AbstractProfile._ProfileAttributeHandler(_TaskProfile._ATTR_KEY_KWARGS, _TaskProfile.SetKwargs)
        _pahList.append(_pah)

        return _AbstractProfile._SetProfileHandlersList(_TaskProfile.__name__, _pahList)
