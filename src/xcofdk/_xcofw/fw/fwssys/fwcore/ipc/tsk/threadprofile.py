# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : threadprofile.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from xcofdk.fwapi.xtask import XTask

from xcofdk._xcofw.fwadapter                                import rlogif
from xcofdk._xcofw.fw.fwssys.fwcore.apiimpl.xtask.xtaskconn import _XTaskConnector
from xcofdk._xcofw.fw.fwssys.fwcore.base.callableif         import _CallableIF
from xcofdk._xcofw.fw.fwssys.fwcore.base.listutil           import _ListUtil
from xcofdk._xcofw.fw.fwssys.fwcore.base.strutil            import _StrUtil
from xcofdk._xcofw.fw.fwssys.fwcore.base.util               import _Util
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil        import _TaskUtil
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil        import _ETaskRightFlag
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil        import _PyThread
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject           import _AbstractSlotsObject
from xcofdk._xcofw.fw.fwssys.fwcore.types.aprofile          import _AbstractProfile

from xcofdk._xcofw.fw.fwssys.fwerrh.fwerrorcodes import _EFwErrorCode

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine

class _ThreadProfile(_AbstractProfile):

    __slots__ = []

    _ATTR_KEY_ARGS                         = _AbstractProfile._ATTR_KEY_ARGS
    _ATTR_KEY_KWARGS                       = _AbstractProfile._ATTR_KEY_KWARGS
    __ATTR_KEY_TASK_ID                     = _AbstractProfile._ATTR_KEY_TASK_ID
    _ATTR_KEY_TASK_NAME                    = _AbstractProfile._ATTR_KEY_TASK_NAME
    _ATTR_KEY_TASK_RIGHTS                  = _AbstractProfile._ATTR_KEY_TASK_RIGHTS
    _ATTR_KEY_ENCLOSED_PYTHREAD            = _AbstractProfile._ATTR_KEY_ENCLOSED_PYTHREAD
    _ATTR_KEY_AUTO_START_ENCLOSED_PYTHREAD = _AbstractProfile._ATTR_KEY_AUTO_START_ENCLOSED_PYTHREAD

    _ATTR_KEY_XTASK_CONN                   = _FwTDbEngine.GetText(_EFwTextID.eThreadProfile_AttrName_ATTR_KEY_XTASK_CONN)
    _ATTR_KEY_THREAD_TARGET                = _FwTDbEngine.GetText(_EFwTextID.eThreadProfile_AttrName_ATTR_KEY_THREAD_TARGET)

    __bUSE_AUTO_GENERATED_TASK_NAMES_ONLY = True

    def __init__( self
                , xtaskConn_                  : _XTaskConnector =None
                , taskName_                   : str             =None
                , enclosedPyThread_           : _PyThread       =None
                , bAutoStartEnclosedPyThread_ : bool            =None
                , threadTargetCallableIF_     : _CallableIF     =None
                , args_                       : list            =None
                , kwargs_                     : dict            =None
                , threadProfileAttrs_         : dict            =None ):

        _AbstractSlotsObject.__init__(self)

        _TRM_KEY   = _ThreadProfile._ATTR_KEY_TASK_RIGHTS
        _ETHRD_KEY = _ThreadProfile._ATTR_KEY_ENCLOSED_PYTHREAD
        _XUC_KEY   = _ThreadProfile._ATTR_KEY_XTASK_CONN
        _TTGT_KEY  = _ThreadProfile._ATTR_KEY_THREAD_TARGET

        _bError = False
        _dictAttrs = {}

        if self._GetProfileHandlersList() is None:
            if not _ThreadProfile.__SetupProfileHandlersList():
                _bError = True
        if not _bError:
            if xtaskConn_ is not None:
                _dictAttrs[_XUC_KEY] = xtaskConn_
            if taskName_ is not None:
                _dictAttrs[_ThreadProfile._ATTR_KEY_TASK_NAME] = taskName_
            if enclosedPyThread_ is not None:
                _dictAttrs[_ETHRD_KEY] = enclosedPyThread_
            if bAutoStartEnclosedPyThread_ is not None:
                _dictAttrs[_ThreadProfile._ATTR_KEY_AUTO_START_ENCLOSED_PYTHREAD] = bAutoStartEnclosedPyThread_
            if threadTargetCallableIF_ is not None:
                _dictAttrs[_TTGT_KEY] = threadTargetCallableIF_
            if args_ is not None:
                _dictAttrs[_ThreadProfile._ATTR_KEY_ARGS] = args_
            if kwargs_ is not None:
                _dictAttrs[_ThreadProfile._ATTR_KEY_KWARGS] = kwargs_

            if threadProfileAttrs_ is not None:
                if not _Util.IsInstance(threadProfileAttrs_, dict, bThrowx_=True):
                    _bError = True
                else:
                    for _kk in threadProfileAttrs_.keys():
                        if threadProfileAttrs_[_kk] is None:
                            continue
                        if _kk not in _dictAttrs:
                            _dictAttrs[_kk] = threadProfileAttrs_[_kk]
                            continue

                        _bError = True
                        rlogif._LogOEC(True, _EFwErrorCode.FE_00328)
                        break
        if not _bError:
            _trm = None if _TRM_KEY not in _dictAttrs else _dictAttrs[_TRM_KEY]

            if (_trm is not None) and not _ETaskRightFlag.IsValidTaskRightMask(_trm):
                _bError = True
                rlogif._LogOEC(True, _EFwErrorCode.FE_00329)
            else:
                if _trm is not None:
                    _dictAttrs[_TRM_KEY] = _trm

                _thrdTgt  = None if _TTGT_KEY  not in _dictAttrs else _dictAttrs[_TTGT_KEY]

                if _thrdTgt is not None:
                    if not (_Util.IsInstance(_thrdTgt, _CallableIF, bThrowx_=True) and _thrdTgt.isValid):
                        _bError = True
                    else:
                        xuConn = None if _XUC_KEY not in _dictAttrs else _dictAttrs[_XUC_KEY]
                        _enclPyThrd = None if _ETHRD_KEY not in _dictAttrs else _dictAttrs[_ETHRD_KEY]

                        if (xuConn is not None) or (_enclPyThrd is not None):
                            _bError = True
                            rlogif._LogOEC(True, _EFwErrorCode.FE_00330)
        if _bError:
            _AbstractProfile.__init__(self, _AbstractProfile._EProfileType.eThread, profileAttrs_=None)
            self.profileStatus = _AbstractProfile._EValidationStatus.eInvalid
        else:
            _AbstractProfile.__init__(self, _AbstractProfile._EProfileType.eThread, profileAttrs_=_dictAttrs)
            if not self.isValid:
                rlogif._LogErrorEC(_EFwErrorCode.UE_00098, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_ThreadProfile_TextID_004))
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
        return self._GetProfileAttr(_ThreadProfile._ATTR_KEY_AUTO_START_ENCLOSED_PYTHREAD)

    @property
    def taskID(self) -> int:
        return self._GetProfileAttr(_ThreadProfile.__ATTR_KEY_TASK_ID)

    @property
    def taskName(self) -> str:
        return self._GetProfileAttr(_ThreadProfile._ATTR_KEY_TASK_NAME)

    @property
    def taskRightsMask(self) -> _ETaskRightFlag:
        return self._GetProfileAttr(_ThreadProfile._ATTR_KEY_TASK_RIGHTS)

    @property
    def threadTarget(self):
        return self._GetProfileAttr(_ThreadProfile._ATTR_KEY_THREAD_TARGET)

    @property
    def xtaskConnector(self) -> _XTaskConnector:
        return self._GetProfileAttr(_ThreadProfile._ATTR_KEY_XTASK_CONN)

    @property
    def xtaskInst(self) -> XTask:
        _xtc = self.xtaskConnector
        return None if _xtc is None else _xtc._connectedXTask

    @property
    def enclosedPyThread(self) -> _PyThread:
        return self._GetProfileAttr(_ThreadProfile._ATTR_KEY_ENCLOSED_PYTHREAD)

    @property
    def args(self) -> list:
        return self._GetProfileAttr(_ThreadProfile._ATTR_KEY_ARGS)

    @property
    def kwargs(self) -> dict:
        return self._GetProfileAttr(_ThreadProfile._ATTR_KEY_KWARGS)

    def Freeze(self, *args_, **kwargs_):
        if self.isFrozen:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00331)
            return False
        elif not self.isValid:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00332)
            return False
        else:
            _bError     = False
            _xtsk    = self.xtaskInst
            _thrdTgt    = self.threadTarget
            _enclPyThrd = self.enclosedPyThread

            if (_enclPyThrd is None) and (_xtsk is None) and (_thrdTgt is None):
                _bError = True
            elif _enclPyThrd is not None:
                _bError = _thrdTgt is not None
            elif _xtsk is not None:
                _bError = _thrdTgt is not None
            else:
                _bError = _thrdTgt is None
            if _bError:
                self.profileStatus = _AbstractProfile._EValidationStatus.eInvalid
                rlogif._LogOEC(True, _EFwErrorCode.FE_00333)
                return False

        _lstArgs = _ListUtil.UnpackArgs(*args_, minArgsNum_=1, maxArgsNum_=2, bThrowx_=True)
        if len(_lstArgs) == 0:
            return False

        _tid   = 0
        _tname = None
        for _ii in range(len(_lstArgs)):
            val = _lstArgs[_ii]
            if   _ii == 0: _tid   = val
            elif _ii == 1: _tname = val

        if not _ThreadProfile.__bUSE_AUTO_GENERATED_TASK_NAMES_ONLY:
            _bValid  = (_tname is None)     and _ThreadProfile._ATTR_KEY_TASK_NAME     in self.profileAttributes
            _bValid |= (_tname is not None) and not _ThreadProfile._ATTR_KEY_TASK_NAME in self.profileAttributes
        else:
            _bValid = _tname is not None
            if _ThreadProfile._ATTR_KEY_TASK_NAME in self.profileAttributes:
                specName = self.profileAttributes[_ThreadProfile._ATTR_KEY_TASK_NAME]
                rlogif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_ThreadProfile_TextID_008).format(specName))

        if not _bValid:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00334)
            self.profileStatus = _AbstractProfile._EValidationStatus.eInvalid
            return False

        self.profileAttributes[_ThreadProfile.__ATTR_KEY_TASK_ID] = _tid
        if _tname is not None:
            self.profileAttributes[_ThreadProfile._ATTR_KEY_TASK_NAME] = _tname

        if self.args is None:
            self.profileAttributes[_ThreadProfile._ATTR_KEY_ARGS] = list()
        if self.kwargs is None:
            self.profileAttributes[_ThreadProfile._ATTR_KEY_KWARGS] = dict()

        res = _AbstractProfile.Freeze(self)
        if not res:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00715)
        return res

    def SetXTaskConn(self, xtaskConn_ : _XTaskConnector, taskName_ : str =None, trMask_ : _ETaskRightFlag =None):
        if self.profileStatus != _AbstractProfile._EValidationStatus.eNone:
            if self.isFrozen:
                rlogif._LogOEC(True, _EFwErrorCode.FE_00335)
            if self.isValid:
                self.profileStatus = _AbstractProfile._EValidationStatus.eInvalid
                rlogif._LogOEC(True, _EFwErrorCode.FE_00336)
            else:
                rlogif._LogOEC(True, _EFwErrorCode.FE_00337)
            return False

        _bValid = _ThreadProfile.__ValidateXTaskConn(enclosedPyThread_=None, xtaskConn_=xtaskConn_)
        if not _bValid:
            pass
        elif taskName_ is not None:
            _bValid = _StrUtil.IsNonEmptyString(taskName_, stripBefore_=True, bThrowx_=True)
            if _bValid:
                taskName_ = str(taskName_).strip()
        if not _bValid:
            pass
        elif trMask_ is not None:
            _bValid = _ETaskRightFlag.IsValidTaskRightMask(trMask_)
            if _bValid:
                _bValid = _ETaskRightFlag.IsValidFwTaskRightMask(trMask_) or _ETaskRightFlag.IsValidUserTaskRightMask(trMask_)
                if _bValid:
                    _bValid = trMask_.hasXTaskTaskRight
                if not _bValid:
                    rlogif._LogOEC(True, _EFwErrorCode.FE_00338)
        else:
            trMask_ = _ETaskRightFlag.UserTaskRightDefaultMask()
            trMask_ = _ETaskRightFlag.AddXTaskTaskRight(trMask_)

        if not _bValid:
            self.profileStatus = _AbstractProfile._EValidationStatus.eInvalid
        else:
            self.profileAttributes[_ThreadProfile._ATTR_KEY_XTASK_CONN] = xtaskConn_
            if taskName_ is not None:
                self.profileAttributes[_ThreadProfile._ATTR_KEY_TASK_NAME] = taskName_
            self.profileAttributes[_ThreadProfile._ATTR_KEY_TASK_RIGHTS] = trMask_
            self.profileStatus = _AbstractProfile._EValidationStatus.eValid
        return self.isValid

    def SetThreadTarget(self, threadTargetCallableIF_ : _CallableIF, taskName_ : str =None, trMask_ : _ETaskRightFlag =None):
        if self.profileStatus != _AbstractProfile._EValidationStatus.eNone:
            if self.isFrozen:
                rlogif._LogOEC(True, _EFwErrorCode.FE_00339)
            if self.isValid:
                self.profileStatus = _AbstractProfile._EValidationStatus.eInvalid
                rlogif._LogOEC(True, _EFwErrorCode.FE_00340)
            else:
                rlogif._LogOEC(True, _EFwErrorCode.FE_00341)
            return False

        _bValid = _Util.IsInstance(threadTargetCallableIF_, _CallableIF, bThrowx_=True) and threadTargetCallableIF_.isValid
        if not _bValid:
            pass
        elif taskName_ is not None:
            _bValid = _StrUtil.IsNonEmptyString(taskName_, stripBefore_=True, bThrowx_=True)
            if _bValid:
                taskName_ = str(taskName_).strip()
        if not _bValid:
            pass
        elif trMask_ is not None:
            _bValid = _ETaskRightFlag.IsValidTaskRightMask(trMask_)
            if _bValid:
                _bValid = _ETaskRightFlag.IsValidUserTaskRightMask(trMask_)
                if not _bValid:
                    rlogif._LogOEC(True, _EFwErrorCode.FE_00342)
        else:
            trMask_ = _ETaskRightFlag.UserTaskRightDefaultMask()

        if not _bValid:
            self.profileStatus = _AbstractProfile._EValidationStatus.eInvalid
        else:
            self.profileAttributes[_ThreadProfile._ATTR_KEY_THREAD_TARGET] = threadTargetCallableIF_
            if taskName_ is not None:
                self.profileAttributes[_ThreadProfile._ATTR_KEY_TASK_NAME] = taskName_
            self.profileAttributes[_ThreadProfile._ATTR_KEY_TASK_RIGHTS] = trMask_
            self.profileStatus = _AbstractProfile._EValidationStatus.eValid
        return self.isValid

    def SetEnclosedPyThread(self, enclosedPyThread_ : _PyThread, xtaskConn_ : _XTaskConnector =None, taskName_ : str =None
                            , trMask_ : _ETaskRightFlag =None, bAutoStartEnclosedPyThread_ : bool =None):
        if self.profileStatus != _AbstractProfile._EValidationStatus.eNone:
            if self.isFrozen:
                rlogif._LogOEC(True, _EFwErrorCode.FE_00343)
            if self.isValid:
                self.profileStatus = _AbstractProfile._EValidationStatus.eInvalid
                rlogif._LogOEC(True, _EFwErrorCode.FE_00344)
            else:
                rlogif._LogOEC(True, _EFwErrorCode.FE_00345)
            return False

        _bValid = _ThreadProfile.__ValidateXTaskConn(enclosedPyThread_=enclosedPyThread_, xtaskConn_=xtaskConn_)
        if not _bValid:
            pass
        elif taskName_ is not None:
            _bValid = _StrUtil.IsNonEmptyString(taskName_, stripBefore_=True, bThrowx_=True)
            if _bValid:
                taskName_ = str(taskName_).strip()
        else:
            taskName_ = enclosedPyThread_.name

        if not _bValid:
            pass
        elif trMask_ is not None:
            _bValid = _ETaskRightFlag.IsValidTaskRightMask(trMask_)
            if _bValid and xtaskConn_ is not None:
                _bValid = _ETaskRightFlag.IsValidFwTaskRightMask(trMask_) or _ETaskRightFlag.IsValidUserTaskRightMask(trMask_)
                if _bValid:
                    _bValid = trMask_.hasXTaskTaskRight
                if not _bValid:
                    rlogif._LogOEC(True, _EFwErrorCode.FE_00346)
        else:
            trMask_ = _ETaskRightFlag.UserTaskRightDefaultMask()
            if xtaskConn_ is not None:
                trMask_ = _ETaskRightFlag.AddXTaskTaskRight(trMask_)

        if not _bValid:
            pass
        elif bAutoStartEnclosedPyThread_ is None:
            bAutoStartEnclosedPyThread_ = False
        else:
            _bValid = _Util.IsInstance(bAutoStartEnclosedPyThread_, bool)

        if not _bValid:
            self.profileStatus = _AbstractProfile._EValidationStatus.eInvalid
        else:
            if xtaskConn_ is not None:
                self.profileAttributes[_ThreadProfile._ATTR_KEY_XTASK_CONN] = xtaskConn_
            self.profileAttributes[_ThreadProfile._ATTR_KEY_ENCLOSED_PYTHREAD] = enclosedPyThread_
            self.profileAttributes[_ThreadProfile._ATTR_KEY_AUTO_START_ENCLOSED_PYTHREAD] = bAutoStartEnclosedPyThread_
            self.profileAttributes[_ThreadProfile._ATTR_KEY_TASK_RIGHTS] = trMask_
            self.profileStatus = _AbstractProfile._EValidationStatus.eValid
            if not _ThreadProfile.__bUSE_AUTO_GENERATED_TASK_NAMES_ONLY:
                self.profileAttributes[_ThreadProfile._ATTR_KEY_TASK_NAME] = taskName_
        return self.isValid

    def SetArgs(self, args_ : list):
        if self.isFrozen:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00347)
            return False
        elif not self.isValid:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00348)
            return False
 
        _bValid = _Util.IsInstance(args_, list)
        if _bValid and (self.args is not None):
            _bValid = False
            rlogif._LogOEC(True, _EFwErrorCode.FE_00349)
 
        if not _bValid:
            self.profileStatus = _AbstractProfile._EValidationStatus.eInvalid
        else:
            self.profileAttributes[_ThreadProfile._ATTR_KEY_ARGS] = list(args_)
            self.profileStatus = _AbstractProfile._EValidationStatus.eValid
        return self.isValid

    def SetKwargs(self, kwargs_ : dict):
        if self.isFrozen:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00350)
            return False
        elif not self.isValid:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00351)
            return False
 
        _bValid = _Util.IsInstance(kwargs_, dict)
        if _bValid and (self.kwargs is not None):
            _bValid = False
            rlogif._LogOEC(True, _EFwErrorCode.FE_00352)
 
        if not _bValid:
            self.profileStatus = _AbstractProfile._EValidationStatus.eInvalid
        else:
            self.profileAttributes[_ThreadProfile._ATTR_KEY_KWARGS] = dict(kwargs_)
            self.profileStatus = _AbstractProfile._EValidationStatus.eValid
        return self.isValid

    @property
    def _isDrivingXTaskTaskProfile(self):
        return self.xtaskConnector is not None

    def _ToString(self, *args_, **kwargs_):
        _xtsk = self._GetProfileAttr(_FwTDbEngine.GetText(_EFwTextID.eMisc_XTask), ignoreStatus_=True)
        _thrdTgt = self._GetProfileAttr(_ThreadProfile._ATTR_KEY_THREAD_TARGET, ignoreStatus_=True)
        _ept     = self._GetProfileAttr(_ThreadProfile._ATTR_KEY_ENCLOSED_PYTHREAD, ignoreStatus_=True)

        if _ept is not None:
            _ownerTitle = _FwTDbEngine.GetText(_EFwTextID.eMisc_EnclPyThread)
            _ownerName  = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_011).format(_ept.name, _ept.native_id)
        elif _xtsk is not None:
            _ownerTitle = _FwTDbEngine.GetText(_EFwTextID.eMisc_XTask)
            _ownerName  = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_006).format(_xtsk)
        elif _thrdTgt is not None:
            _ownerTitle = _FwTDbEngine.GetText(_EFwTextID.eMisc_ThreadTarget)
            _ownerName  = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_006).format(_thrdTgt.ToString())
        else:
            _ownerTitle = _FwTDbEngine.GetText(_EFwTextID.eMisc_Id)
            _ownerName  = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_006).format(id(self))

        if not self.isValid:
            res = _FwTDbEngine.GetText(_EFwTextID.eThreadProfile_ToString_01).format(_ownerTitle, _ownerName)
        else:
            _lenArgs   = 0 if self.args is None else len(self.args)
            _lenKwargs = 0 if self.kwargs is None else len(self.kwargs)

            if self.isEnclosingPyThread:
                res = _FwTDbEngine.GetText(_EFwTextID.eThreadProfile_ToString_02).format(
                    _ownerTitle, _ownerName, hex(self.taskRightsMask), self.isAutoStartEnclosedPyThreadEnabled, _lenArgs, _lenKwargs)
            else:
                if self.taskName is None:
                    res = _FwTDbEngine.GetText(_EFwTextID.eThreadProfile_ToString_03).format(_ownerTitle, _ownerName, hex(self.taskRightsMask), _lenArgs, _lenKwargs)
                else:
                    res = _FwTDbEngine.GetText(_EFwTextID.eThreadProfile_ToString_04).format(_ownerTitle, _ownerName, self.taskName, hex(self.taskRightsMask), _lenArgs, _lenKwargs)
        res = '{}: {}'.format(type(self).__name__, res)
        return res

    def _CleanUp(self):
        _myArgs = self._GetProfileAttr(_ThreadProfile._ATTR_KEY_ARGS, ignoreStatus_=True)
        if _myArgs is not None:
            self.profileAttributes[_ThreadProfile._ATTR_KEY_ARGS] = None
            _myArgs.clear()

        _myKwargs = self._GetProfileAttr(_ThreadProfile._ATTR_KEY_KWARGS, ignoreStatus_=True)
        if _myKwargs is not None:
            self.profileAttributes[_ThreadProfile._ATTR_KEY_KWARGS] = None
            _myKwargs.clear()

        super()._CleanUp()

    def _Validate(self, dictAttrs_ : dict):
        if self._GetProfileHandlersList() is None:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00353)
            return
        elif self.profileStatus != _AbstractProfile._EValidationStatus.eNone:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00716)
            return
        elif (dictAttrs_ is None) or len(dictAttrs_) == 0:
            return

        for pah in self._GetProfileHandlersList():
            if pah.attrName not in dictAttrs_:
                continue
            elif pah.attrName == _ThreadProfile._ATTR_KEY_XTASK_CONN:
                if _ThreadProfile._ATTR_KEY_ENCLOSED_PYTHREAD in dictAttrs_:
                    continue

            arg = dictAttrs_[pah.attrName]
            _hh = pah.handler

            optArgs = None
            if pah.optAttrsNames is not None:
                optArgs = list()
                for _kk in pah.optAttrsNames:
                    if _kk not in dictAttrs_:
                        _vv = None
                    else:
                        _vv = dictAttrs_[_kk]
                    optArgs.append(_vv)
                if len(optArgs) == 0:
                    optArgs = None

            if optArgs is not None:
                _hh(self, arg, *optArgs)
            else:
                _hh(self, arg)

    @staticmethod
    def __ValidateXTaskConn(enclosedPyThread_ : _PyThread =None, xtaskConn_ : _XTaskConnector =None):
        if (enclosedPyThread_ is None) and (xtaskConn_ is None):
            return True

        res = True
        if enclosedPyThread_ is not None:
            res = _Util.IsInstance(enclosedPyThread_, _PyThread)

        if res and (xtaskConn_ is not None):
            res = _Util.IsInstance(xtaskConn_, _XTaskConnector, bThrowx_=True)
            if res:
                _xt = xtaskConn_._connectedXTask
                if _xt is None:
                    res = False
                    rlogif._LogOEC(True, _EFwErrorCode.FE_00354)
                elif not _xt.isAttachedToFW:
                    res = False
                    rlogif._LogOEC(True, _EFwErrorCode.FE_00355)
                elif (not _xt.isXtask) or not isinstance(_xt, XTask):
                    res = False
                    execStr = str(_xt)
                    rlogif._LogOEC(True, _EFwErrorCode.FE_00356)
                elif _xt.xtaskProfile.isExternalQueueEnabled or _xt.xtaskProfile.isInternalQueueEnabled:
                    res = False
                    rlogif._LogOEC(True, _EFwErrorCode.FE_00357)
                elif (enclosedPyThread_ is not None) != _xt.xtaskProfile.isSynchronousTask:
                    res = False
                    rlogif._LogOEC(True, _EFwErrorCode.FE_00358)
        return res

    @staticmethod
    def __SetupProfileHandlersList():
        pahList = list()

        _lstAttrKeys = [_ThreadProfile._ATTR_KEY_XTASK_CONN, _ThreadProfile._ATTR_KEY_TASK_NAME, _ThreadProfile._ATTR_KEY_TASK_RIGHTS, _ThreadProfile._ATTR_KEY_AUTO_START_ENCLOSED_PYTHREAD]
        pah = _AbstractProfile._ProfileAttributeHandler(_ThreadProfile._ATTR_KEY_ENCLOSED_PYTHREAD, _ThreadProfile.SetEnclosedPyThread, _lstAttrKeys)
        pahList.append(pah)

        _lstAttrKeys = [_ThreadProfile._ATTR_KEY_TASK_NAME, _ThreadProfile._ATTR_KEY_TASK_RIGHTS]
        pah = _AbstractProfile._ProfileAttributeHandler(_ThreadProfile._ATTR_KEY_XTASK_CONN, _ThreadProfile.SetXTaskConn, _lstAttrKeys)
        pahList.append(pah)

        _lstAttrKeys = [_ThreadProfile._ATTR_KEY_TASK_NAME, _ThreadProfile._ATTR_KEY_TASK_RIGHTS]
        pah = _AbstractProfile._ProfileAttributeHandler(_ThreadProfile._ATTR_KEY_THREAD_TARGET, _ThreadProfile.SetThreadTarget, _lstAttrKeys)
        pahList.append(pah)

        pah = _AbstractProfile._ProfileAttributeHandler(_ThreadProfile._ATTR_KEY_ARGS, _ThreadProfile.SetArgs)
        pahList.append(pah)

        pah = _AbstractProfile._ProfileAttributeHandler(_ThreadProfile._ATTR_KEY_KWARGS, _ThreadProfile.SetKwargs)
        pahList.append(pah)

        return _AbstractProfile._SetProfileHandlersList(_ThreadProfile.__name__, pahList)
