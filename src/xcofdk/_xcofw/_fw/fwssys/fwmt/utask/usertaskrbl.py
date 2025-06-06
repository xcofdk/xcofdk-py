# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : usertaskrbl.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from typing import Union

from xcofdk.fwapi.xmt import ITaskProfile

from _fw.fwssys.assys.ifs                import _IUTaskConn
from _fw.fwssys.assys.ifs.ifutagent      import _IUTAgent
from _fw.fwssys.fwcore.logging           import vlogif
from _fw.fwssys.fwcore.base.util         import _Util
from _fw.fwssys.fwcore.ipc.rbl.arbldefs  import _ERblApiFuncTag
from _fw.fwssys.fwcore.ipc.rbl.arunnable import _AbsRunnable
from _fw.fwssys.fwcore.ipc.tsk.taskdefs  import _ERblType
from _fw.fwssys.fwcore.types.aobject     import _AbsSlotsObject
from _fw.fwssys.fwerrh.fwerrorcodes      import _EFwErrorCode

class _UserTaskRbl(_AbsRunnable):
    __mcamn = None

    __slots__ = [ '__mm' , '__bR' , '__bS' , '__bT' , '__bPXM' , '__bPIM' ]

    def __init__(self, utConn_ : _IUTaskConn):
        self.__mm   = None
        self.__bR   = None
        self.__bS   = None
        self.__bT   = None
        self.__bPIM = None
        self.__bPXM = None
        _AbsSlotsObject.__init__(self)

        _xm = None
        _doSkipSetup = False
        if not isinstance(utConn_, _IUTaskConn):
            _doSkipSetup = True
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00161)
        else:
            _uta = utConn_._utAgent
            if _uta is None:
                _doSkipSetup = True
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00162)
            elif not isinstance(_uta, _IUTAgent):
                _doSkipSetup = True
                _xtStr = str(_uta)
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00163)
            elif not ((utConn_._xCard is not None) and utConn_._xCard.isValid):
                _doSkipSetup = True
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00164)
            elif not self.__CheckAPI(_uta):
                _doSkipSetup = True
            else:
                _xm = _UserTaskRbl.__GetRblApiXMask(_uta)
                _doSkipSetup = _xm is None

        self.__mm = True
        if _doSkipSetup:
            super().__init__(doSkipSetup_=True)
            self.CleanUp()
            return

        _rt = _ERblType.eMainXTaskRbl if utConn_._taskProfile.isMainTask else _ERblType.eXTaskRbl
        super().__init__(rblType_=_rt, utaskConn_=utConn_, rblXM_=_xm , txCard_=utConn_._xCard)
        if self.__isInvalid:
            self.CleanUp()

    @staticmethod
    def _GetMCApiMNL():
        res = []
        _tmp = _AbsRunnable._GetMCApiMNL()
        if _tmp is not None:
            res += _tmp
        if _UserTaskRbl.__mcamn is not None:
            res += _UserTaskRbl.__mcamn
        return res

    def _CleanUp(self):
        if self.__isInvalid:
            return
        self.__mm   = None
        self.__bR   = None
        self.__bS   = None
        self.__bT   = None
        self.__bPIM = None
        self.__bPXM = None
        super()._CleanUp()

    def _RunExecutable(self):
        return self.__ExecuteApiFunc(_ERblApiFuncTag.eRFTRunExecutable)

    def _SetUpExecutable(self):
        return self.__ExecuteApiFunc(_ERblApiFuncTag.eRFTSetUpExecutable)

    def _TearDownExecutable(self):
        return self.__ExecuteApiFunc(_ERblApiFuncTag.eRFTTearDownExecutable)

    def _ProcessInternalMsg(self, msg_, callback_ =None):
        return self.__ExecuteApiFunc(_ERblApiFuncTag.eRFTProcessInternalMsg, msg_, callback_)

    def _ProcessExternalMsg(self, msg_, callback_ =None):
        return self.__ExecuteApiFunc(_ERblApiFuncTag.eRFTProcessExternalMsg, msg_, callback_)

    @staticmethod
    def __GetRblApiXMask(utsk_ : _IUTAgent) -> Union[_ERblApiFuncTag, None]:
        if not (isinstance(utsk_.taskProfile, ITaskProfile) and utsk_.taskProfile.isValid):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00165)
            return None

        _utp = utsk_.taskProfile
        res  = _ERblApiFuncTag.DefaultApiMask()
        res  = _ERblApiFuncTag.AddApiFuncTag(res, _ERblApiFuncTag.eRFTProcessInternalQueue)
        res  = _ERblApiFuncTag.AddApiFuncTag(res, _ERblApiFuncTag.eRFTOnRunProgressNotification)

        if not _utp.isInternalQueueEnabled:
            res = _ERblApiFuncTag.AddApiFuncTag(res, _ERblApiFuncTag.eRFTProcessInternalMsg)

        if not _utp.isExternalQueueEnabled:
            res = _ERblApiFuncTag.AddApiFuncTag(res, _ERblApiFuncTag.eRFTProcessExternalMsg)
            res = _ERblApiFuncTag.AddApiFuncTag(res, _ERblApiFuncTag.eRFTProcessExternalQueue)

        else:
            res = _ERblApiFuncTag.AddApiFuncTag(res, _ERblApiFuncTag.eRFTProcessExternalQueue)

            if _utp.isExternalQueueBlocking:
                res = _ERblApiFuncTag.AddApiFuncTag(res, _ERblApiFuncTag.eRFTRunExecutable)

        if not _utp.isSetupPhaseEnabled:
            res = _ERblApiFuncTag.AddApiFuncTag(res, _ERblApiFuncTag.eRFTSetUpExecutable)

        if not _utp.isTeardownPhaseEnabled:
            res = _ERblApiFuncTag.AddApiFuncTag(res, _ERblApiFuncTag.eRFTTearDownExecutable)
        return res

    @property
    def __isInvalid(self):
        return (self.__mm is None) or (self._rblType is None)

    def __CheckAPI(self, uta_ : _IUTAgent) -> bool:
        _mmn = _UserTaskRbl.GetMCApiMNL()
        _numMandatoryApiMehtods = _Util.GetNumAttributes(self, _mmn, bThrowx_=True)
        if _numMandatoryApiMehtods != len(_mmn):
            res = False
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00171)
        else:
            res = True
            _utp = uta_.taskProfile
            self.__bR   = (not _utp.isExternalQueueEnabled) or (not _utp.isExternalQueueBlocking)
            self.__bS   = _utp.isSetupPhaseEnabled
            self.__bT   = _utp.isTeardownPhaseEnabled
            self.__bPIM = _utp.isInternalQueueEnabled
            self.__bPXM = _utp.isExternalQueueEnabled
        return res

    def __ExecuteApiFunc(self, apiFID_ : _ERblApiFuncTag, msg_ =None, callback_ =None):
        if self.__isInvalid:
            return None

        res     = None
        _xti    = self._utAgent._xtInst
        _bRun   = apiFID_ == _ERblApiFuncTag.eRFTRunExecutable
        _bSetup = (not _bRun) and (apiFID_ == _ERblApiFuncTag.eRFTSetUpExecutable)

        if apiFID_ == _ERblApiFuncTag.eRFTProcessExternalMsg:
            if not self.__bPXM:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00166)
            elif not self.isRunning:
                res = False
            elif callback_ is not None:
                res = callback_(msg_)
            else:
                res = _xti.ProcessExternalMessage(msg_)

        elif _bSetup:
            if not self.__bS:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00167)
            else:
                _args   = self._xcard.args
                _kwargs = self._xcard.kwargs
                res     = False if not self.isRunning else _xti.SetUpXTask(*_args, **_kwargs)
        elif apiFID_ == _ERblApiFuncTag.eRFTTearDownExecutable:
            if not self.__bT:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00168)
            else:
                res = False if not self._isTerminating else _xti.TearDownXTask()
        elif _bRun:
            if not self.__bR:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00169)
            elif not self.isProvidingSetUpRunnable:
                _args   = self._xcard.args
                _kwargs = self._xcard.kwargs
                res     = False if not self.isRunning else _xti.RunXTask(*_args, **_kwargs)
            else:
                res = False if not self.isRunning else _xti.RunXTask()
        else:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00170)
        return res
