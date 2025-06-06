# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwthreadprf.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from _fw.fwssys.assys.ifs.ifutagent      import _IUTAgent
from _fw.fwssys.assys.ifs.ifutaskconn    import _IUTaskConn
from _fwadapter                          import rlogif
from _fw.fwssys.fwcore.base.fwcallable   import _FwCallable
from _fw.fwssys.fwcore.base.strutil      import _StrUtil
from _fw.fwssys.fwcore.base.util         import _Util
from _fw.fwssys.fwcore.ipc.tsk.taskutil  import _TaskUtil
from _fw.fwssys.fwcore.ipc.tsk.taskutil  import _ETaskRightFlag
from _fw.fwssys.fwcore.ipc.tsk.taskutil  import _PyThread
from _fw.fwssys.fwcore.types.aobject     import _AbsSlotsObject
from _fw.fwssys.fwcore.types.afwprofile  import _AbsFwProfile
from _fw.fwssys.fwcore.types.commontypes import _CommonDefines
from _fw.fwssys.fwerrh.fwerrorcodes      import _EFwErrorCode

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _FwThreadProfile(_AbsFwProfile):
    __slots__ = []

    _ATTR_KEY_ARGS                         = _AbsFwProfile._ATTR_KEY_ARGS
    _ATTR_KEY_KWARGS                       = _AbsFwProfile._ATTR_KEY_KWARGS
    __ATTR_KEY_TASK_ID                     = _AbsFwProfile._ATTR_KEY_TASK_ID
    _ATTR_KEY_TASK_NAME                    = _AbsFwProfile._ATTR_KEY_TASK_NAME
    _ATTR_KEY_TASK_RIGHTS                  = _AbsFwProfile._ATTR_KEY_TASK_RIGHTS
    _ATTR_KEY_ENCLOSED_PYTHREAD            = _AbsFwProfile._ATTR_KEY_ENCLOSED_PYTHREAD
    _ATTR_KEY_AUTO_START_ENCLOSED_PYTHREAD = _AbsFwProfile._ATTR_KEY_AUTO_START_ENCLOSED_PYTHREAD

    _ATTR_KEY_XTASK_CONN                   = _FwTDbEngine.GetText(_EFwTextID.eThrdP_AN_ATTR_KEY_UTASK_CONN)
    _ATTR_KEY_THREAD_TARGET                = _FwTDbEngine.GetText(_EFwTextID.eThrdP_AN_ATTR_KEY_THREAD_TARGET)

    def __init__( self
                , utaskConn_    : _IUTaskConn =None
                , taskName_     : str         =None
                , enclHThrd_    : _PyThread   =None
                , bASEnclHThrd_ : bool        =None
                , thrdTgtCIF_   : _FwCallable =None
                , args_         : list =None
                , kwargs_       : dict =None
                , tpAttrs_      : dict =None ):
        _AbsSlotsObject.__init__(self)

        _TRM_KEY   = _FwThreadProfile._ATTR_KEY_TASK_RIGHTS
        _ETHRD_KEY = _FwThreadProfile._ATTR_KEY_ENCLOSED_PYTHREAD
        _XTC_KEY   = _FwThreadProfile._ATTR_KEY_XTASK_CONN
        _TTGT_KEY  = _FwThreadProfile._ATTR_KEY_THREAD_TARGET

        _bError = False
        _dictAttrs = {}

        if self._GetProfileHandlersList() is None:
            if not _FwThreadProfile.__SetupProfileHandlersList():
                _bError = True
        if not _bError:
            if utaskConn_ is not None:
                _dictAttrs[_XTC_KEY] = utaskConn_
            if taskName_ is not None:
                _dictAttrs[_FwThreadProfile._ATTR_KEY_TASK_NAME] = taskName_
            if enclHThrd_ is not None:
                _dictAttrs[_ETHRD_KEY] = enclHThrd_
            if bASEnclHThrd_ is not None:
                _dictAttrs[_FwThreadProfile._ATTR_KEY_AUTO_START_ENCLOSED_PYTHREAD] = bASEnclHThrd_
            if thrdTgtCIF_ is not None:
                _dictAttrs[_TTGT_KEY] = thrdTgtCIF_
            if args_ is not None:
                _dictAttrs[_FwThreadProfile._ATTR_KEY_ARGS] = args_
            if kwargs_ is not None:
                _dictAttrs[_FwThreadProfile._ATTR_KEY_KWARGS] = kwargs_

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
                    if not (_Util.IsInstance(_thrdTgt, _FwCallable, bThrowx_=True) and _thrdTgt.isValid):
                        _bError = True
                    else:
                        xuConn = None if _XTC_KEY not in _dictAttrs else _dictAttrs[_XTC_KEY]
                        _enclPyThrd = None if _ETHRD_KEY not in _dictAttrs else _dictAttrs[_ETHRD_KEY]

                        if (xuConn is not None) or (_enclPyThrd is not None):
                            _bError = True
                            rlogif._LogOEC(True, _EFwErrorCode.FE_00330)
        if _bError:
            _AbsFwProfile.__init__(self, _AbsFwProfile._EProfileType.eThread, profileAttrs_=None)
            self.profileStatus = _AbsFwProfile._EValidationStatus.eInvalid
        else:
            _AbsFwProfile.__init__(self, _AbsFwProfile._EProfileType.eThread, profileAttrs_=_dictAttrs)
            if not self.isValid:
                rlogif._LogErrorEC(_EFwErrorCode.UE_00098, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_ThreadProfile_TID_004))

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
        return self._GetProfileAttr(_FwThreadProfile._ATTR_KEY_AUTO_START_ENCLOSED_PYTHREAD)

    @property
    def dtaskUID(self) -> int:
        return self._GetProfileAttr(_FwThreadProfile.__ATTR_KEY_TASK_ID)

    @property
    def dtaskName(self) -> str:
        return self._GetProfileAttr(_FwThreadProfile._ATTR_KEY_TASK_NAME)

    @property
    def taskRightsMask(self) -> _ETaskRightFlag:
        return self._GetProfileAttr(_FwThreadProfile._ATTR_KEY_TASK_RIGHTS)

    @property
    def threadTarget(self):
        return self._GetProfileAttr(_FwThreadProfile._ATTR_KEY_THREAD_TARGET)

    @property
    def utConn(self) -> _IUTaskConn:
        return self._GetProfileAttr(_FwThreadProfile._ATTR_KEY_XTASK_CONN)

    @property
    def enclosedPyThread(self) -> _PyThread:
        return self._GetProfileAttr(_FwThreadProfile._ATTR_KEY_ENCLOSED_PYTHREAD)

    @property
    def args(self) -> list:
        return self._GetProfileAttr(_FwThreadProfile._ATTR_KEY_ARGS)

    @property
    def kwargs(self) -> dict:
        return self._GetProfileAttr(_FwThreadProfile._ATTR_KEY_KWARGS)

    def Freeze(self, thrdID_ : int =0, thrdName_ : str =None):
        if self.isFrozen:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00331)
            return False
        elif not self.isValid:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00332)
            return False
        else:
            _bError     = False
            _utc        = self.utConn
            _uta        = None if _utc is None else _utc._utAgent
            _thrdTgt    = self.threadTarget
            _enclPyThrd = self.enclosedPyThread

            if (_enclPyThrd is None) and (_uta is None) and (_thrdTgt is None):
                _bError = True
            elif _enclPyThrd is not None:
                _bError = _thrdTgt is not None
            elif _uta is not None:
                _bError = _thrdTgt is not None
            else:
                _bError = _thrdTgt is None
            if _bError:
                self.profileStatus = _AbsFwProfile._EValidationStatus.eInvalid
                rlogif._LogOEC(True, _EFwErrorCode.FE_00333)
                return False

        if not _AbsFwProfile._IsAutoGeneratedTaskNameEnabled():
            _bValid  = (thrdName_ is None) and _FwThreadProfile._ATTR_KEY_TASK_NAME in self.profileAttributes
            _bValid |= (thrdName_ is not None) and _FwThreadProfile._ATTR_KEY_TASK_NAME not in self.profileAttributes
        else:
            _bValid = thrdName_ is not None
            if _FwThreadProfile._ATTR_KEY_TASK_NAME in self.profileAttributes:
                specName = self.profileAttributes[_FwThreadProfile._ATTR_KEY_TASK_NAME]
                rlogif._LogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_ThreadProfile_TID_008).format(specName))

        if not _bValid:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00334)
            self.profileStatus = _AbsFwProfile._EValidationStatus.eInvalid
            return False

        self.profileAttributes[_FwThreadProfile.__ATTR_KEY_TASK_ID] = thrdID_
        if thrdName_ is not None:
            self.profileAttributes[_FwThreadProfile._ATTR_KEY_TASK_NAME] = thrdName_

        if self.args is None:
            self.profileAttributes[_FwThreadProfile._ATTR_KEY_ARGS] = list()
        if self.kwargs is None:
            self.profileAttributes[_FwThreadProfile._ATTR_KEY_KWARGS] = dict()

        res = _AbsFwProfile.Freeze(self)
        if not res:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00715)
        return res

    def SetXTaskConn(self, utaskConn_ : _IUTaskConn, taskName_ : str =None, trMask_ : _ETaskRightFlag =None):
        if self.profileStatus != _AbsFwProfile._EValidationStatus.eNone:
            if self.isFrozen:
                rlogif._LogOEC(True, _EFwErrorCode.FE_00335)
            if self.isValid:
                self.profileStatus = _AbsFwProfile._EValidationStatus.eInvalid
                rlogif._LogOEC(True, _EFwErrorCode.FE_00336)
            else:
                rlogif._LogOEC(True, _EFwErrorCode.FE_00337)
            return False

        _bValid = _FwThreadProfile.__ValidateUTaskConn(enclHThrd_=None, utConn_=utaskConn_)
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
            self.profileStatus = _AbsFwProfile._EValidationStatus.eInvalid
        else:
            self.profileAttributes[_FwThreadProfile._ATTR_KEY_XTASK_CONN] = utaskConn_
            if taskName_ is not None:
                self.profileAttributes[_FwThreadProfile._ATTR_KEY_TASK_NAME] = taskName_
            self.profileAttributes[_FwThreadProfile._ATTR_KEY_TASK_RIGHTS] = trMask_
            self.profileStatus = _AbsFwProfile._EValidationStatus.eValid
        return self.isValid

    def SetThreadTarget(self, thrdTgtCIF_ : _FwCallable, taskName_ : str =None, trMask_ : _ETaskRightFlag =None):
        if self.profileStatus != _AbsFwProfile._EValidationStatus.eNone:
            if self.isFrozen:
                rlogif._LogOEC(True, _EFwErrorCode.FE_00339)
            if self.isValid:
                self.profileStatus = _AbsFwProfile._EValidationStatus.eInvalid
                rlogif._LogOEC(True, _EFwErrorCode.FE_00340)
            else:
                rlogif._LogOEC(True, _EFwErrorCode.FE_00341)
            return False

        _bValid = _Util.IsInstance(thrdTgtCIF_, _FwCallable, bThrowx_=True) and thrdTgtCIF_.isValid
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
            self.profileStatus = _AbsFwProfile._EValidationStatus.eInvalid
        else:
            self.profileAttributes[_FwThreadProfile._ATTR_KEY_THREAD_TARGET] = thrdTgtCIF_
            if taskName_ is not None:
                self.profileAttributes[_FwThreadProfile._ATTR_KEY_TASK_NAME] = taskName_
            self.profileAttributes[_FwThreadProfile._ATTR_KEY_TASK_RIGHTS] = trMask_
            self.profileStatus = _AbsFwProfile._EValidationStatus.eValid
        return self.isValid

    def SetEnclosedPyThread( self, enclHThrd_ : _PyThread, utaskConn_ : _IUTaskConn =None, taskName_ : str =None
                           , trMask_ : _ETaskRightFlag =None, bASEnclHThrd_ : bool =None):
        if self.profileStatus != _AbsFwProfile._EValidationStatus.eNone:
            if self.isFrozen:
                rlogif._LogOEC(True, _EFwErrorCode.FE_00343)
            if self.isValid:
                self.profileStatus = _AbsFwProfile._EValidationStatus.eInvalid
                rlogif._LogOEC(True, _EFwErrorCode.FE_00344)
            else:
                rlogif._LogOEC(True, _EFwErrorCode.FE_00345)
            return False

        _bValid = _FwThreadProfile.__ValidateUTaskConn(enclHThrd_=enclHThrd_, utConn_=utaskConn_)
        if not _bValid:
            pass
        elif taskName_ is not None:
            _bValid = _StrUtil.IsNonEmptyString(taskName_, stripBefore_=True, bThrowx_=True)
            if _bValid:
                taskName_ = str(taskName_).strip()
        else:
            taskName_ = enclHThrd_.name

        if not _bValid:
            pass
        elif trMask_ is not None:
            _bValid = _ETaskRightFlag.IsValidTaskRightMask(trMask_)
            if _bValid and utaskConn_ is not None:
                _bValid = _ETaskRightFlag.IsValidFwTaskRightMask(trMask_) or _ETaskRightFlag.IsValidUserTaskRightMask(trMask_)
                if _bValid:
                    _bValid = trMask_.hasXTaskTaskRight
                if not _bValid:
                    rlogif._LogOEC(True, _EFwErrorCode.FE_00346)
        else:
            trMask_ = _ETaskRightFlag.UserTaskRightDefaultMask()
            if utaskConn_ is not None:
                trMask_ = _ETaskRightFlag.AddXTaskTaskRight(trMask_)

        if not _bValid:
            pass
        elif bASEnclHThrd_ is None:
            bASEnclHThrd_ = False
        else:
            _bValid = _Util.IsInstance(bASEnclHThrd_, bool)

        if not _bValid:
            self.profileStatus = _AbsFwProfile._EValidationStatus.eInvalid
        else:
            if utaskConn_ is not None:
                self.profileAttributes[_FwThreadProfile._ATTR_KEY_XTASK_CONN] = utaskConn_
            self.profileAttributes[_FwThreadProfile._ATTR_KEY_ENCLOSED_PYTHREAD] = enclHThrd_
            self.profileAttributes[_FwThreadProfile._ATTR_KEY_AUTO_START_ENCLOSED_PYTHREAD] = bASEnclHThrd_
            self.profileAttributes[_FwThreadProfile._ATTR_KEY_TASK_RIGHTS] = trMask_
            self.profileStatus = _AbsFwProfile._EValidationStatus.eValid
            self.profileAttributes[_FwThreadProfile._ATTR_KEY_TASK_NAME] = taskName_
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
            self.profileStatus = _AbsFwProfile._EValidationStatus.eInvalid
        else:
            self.profileAttributes[_FwThreadProfile._ATTR_KEY_ARGS] = list(args_)
            self.profileStatus = _AbsFwProfile._EValidationStatus.eValid
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
            self.profileStatus = _AbsFwProfile._EValidationStatus.eInvalid
        else:
            self.profileAttributes[_FwThreadProfile._ATTR_KEY_KWARGS] = dict(kwargs_)
            self.profileStatus = _AbsFwProfile._EValidationStatus.eValid
        return self.isValid

    @property
    def _isDrivingXTaskTaskProfile(self):
        return self.utConn is not None

    def _ToString(self):
        return self.__class__.__name__

    def _CleanUp(self):
        _myArgs = self._GetProfileAttr(_FwThreadProfile._ATTR_KEY_ARGS, ignoreStatus_=True)
        if _myArgs is not None:
            self.profileAttributes[_FwThreadProfile._ATTR_KEY_ARGS] = None
            _myArgs.clear()

        _myKwargs = self._GetProfileAttr(_FwThreadProfile._ATTR_KEY_KWARGS, ignoreStatus_=True)
        if _myKwargs is not None:
            self.profileAttributes[_FwThreadProfile._ATTR_KEY_KWARGS] = None
            _myKwargs.clear()

        super()._CleanUp()

    def _Validate(self, dictAttrs_ : dict):
        if self._GetProfileHandlersList() is None:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00353)
            return
        elif self.profileStatus != _AbsFwProfile._EValidationStatus.eNone:
            rlogif._LogOEC(True, _EFwErrorCode.FE_00716)
            return
        elif (dictAttrs_ is None) or len(dictAttrs_) == 0:
            return

        for pah in self._GetProfileHandlersList():
            if pah.attrName not in dictAttrs_:
                continue
            elif pah.attrName == _FwThreadProfile._ATTR_KEY_XTASK_CONN:
                if _FwThreadProfile._ATTR_KEY_ENCLOSED_PYTHREAD in dictAttrs_:
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
    def __ValidateUTaskConn(enclHThrd_ : _PyThread =None, utConn_ : _IUTaskConn =None):
        if (enclHThrd_ is None) and (utConn_ is None):
            return True

        res = True
        if enclHThrd_ is not None:
            res = _Util.IsInstance(enclHThrd_, _PyThread)

        if res and (utConn_ is not None):
            res = _Util.IsInstance(utConn_, _IUTaskConn, bThrowx_=True)
            if res:
                _uta = utConn_._utAgent
                if _uta is None:
                    res = False
                    rlogif._LogOEC(True, _EFwErrorCode.FE_00354)
                elif not isinstance(_uta, _IUTAgent):
                    res = False
                    _xtStr = str(_uta)
                    if _xtStr is None:
                        _xtStr = _CommonDefines._STR_EMPTY
                    rlogif._LogOEC(True, _EFwErrorCode.FE_00356)
                elif not _uta.isAttachedToFW:
                    res = False
                    rlogif._LogOEC(True, _EFwErrorCode.FE_00355)
                else:
                    _utp = _uta.taskProfile
                    if _utp.isExternalQueueEnabled or _utp.isInternalQueueEnabled:
                        res = False
                        rlogif._LogOEC(True, _EFwErrorCode.FE_00357)
                    elif (enclHThrd_ is not None) != _utp.isSyncTask:
                        res = False
                        rlogif._LogOEC(True, _EFwErrorCode.FE_00358)
        return res

    @staticmethod
    def __SetupProfileHandlersList():
        pahList = list()

        _lstAttrKeys = [ _FwThreadProfile._ATTR_KEY_XTASK_CONN
                       , _FwThreadProfile._ATTR_KEY_TASK_NAME
                       , _FwThreadProfile._ATTR_KEY_TASK_RIGHTS
                       , _FwThreadProfile._ATTR_KEY_AUTO_START_ENCLOSED_PYTHREAD]
        pah = _AbsFwProfile._ProfileAttributeHandler(_FwThreadProfile._ATTR_KEY_ENCLOSED_PYTHREAD, _FwThreadProfile.SetEnclosedPyThread, _lstAttrKeys)
        pahList.append(pah)

        _lstAttrKeys = [_FwThreadProfile._ATTR_KEY_TASK_NAME, _FwThreadProfile._ATTR_KEY_TASK_RIGHTS]
        pah = _AbsFwProfile._ProfileAttributeHandler(_FwThreadProfile._ATTR_KEY_XTASK_CONN, _FwThreadProfile.SetXTaskConn, _lstAttrKeys)
        pahList.append(pah)

        _lstAttrKeys = [_FwThreadProfile._ATTR_KEY_TASK_NAME, _FwThreadProfile._ATTR_KEY_TASK_RIGHTS]
        pah = _AbsFwProfile._ProfileAttributeHandler(_FwThreadProfile._ATTR_KEY_THREAD_TARGET, _FwThreadProfile.SetThreadTarget, _lstAttrKeys)
        pahList.append(pah)

        pah = _AbsFwProfile._ProfileAttributeHandler(_FwThreadProfile._ATTR_KEY_ARGS, _FwThreadProfile.SetArgs)
        pahList.append(pah)

        pah = _AbsFwProfile._ProfileAttributeHandler(_FwThreadProfile._ATTR_KEY_KWARGS, _FwThreadProfile.SetKwargs)
        pahList.append(pah)

        return _AbsFwProfile._SetProfileHandlersList(_FwThreadProfile.__name__, pahList)
