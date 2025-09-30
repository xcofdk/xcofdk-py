# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xprocagent.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from typing    import Union as Any
from threading import RLock as _PyRLock
from typing    import Union

from xcofdk.fwapi.xmp.xprocessxcp import PTException
from xcofdk.fwapi.xmp.xprocessxcp import PTWrappedException

from _fw.fwssys.assys                    import fwsubsysshare as _ssshare
from _fw.fwssys.assys.ifs                import _IXProcAgent
from _fw.fwssys.fwcore.logging           import logif
from _fw.fwssys.fwcore.types.commontypes import override
from _fw.fwssys.fwcore.types.commontypes import _CommonDefines
from _fw.fwssys.fwmp.fwrte.fwrtedefs     import _ERteTXErrorID
from _fw.fwssys.fwmp.fwrte.rteexception  import _RteException
from _fw.fwssys.fwmp.xprocessstate       import _EPState
from _fw.fwssys.fwmp.xprocessconn        import _XProcessConn

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _XProcessAgent(_IXProcAgent):
    __slots__ = [ '__pn' , '__l' , '__pan' , '__pid' , '__uid' , '__pxc' , '__psd' , '__xpc' , '__tst' , '__pxcp' ]

    def __init__(self, target_, aliasn_ : str =None, name_ : str =None, maxSDSize_ : int =None):
        super().__init__()
        self.__l    = None
        self.__pn   = None
        self.__pan  = None
        self.__tst  = None
        self.__pxc  = None
        self.__psd  = None
        self.__pid  = None
        self.__uid  = None
        self.__xpc  = None
        self.__pxcp = None

        if _ssshare._WarnOnDisabledSubsysMP(annexID_=_EFwTextID.eMisc_Shared_Disabled_Subsys_MP):
            return
        if not _ssshare._IsRteStarted():
            logif._LogUrgentWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XProcessAgent_001))
            return
        if not _XProcessConn._IsAvailable():
            return

        _xpc = _XProcessConn(self, target_, aliasn_=aliasn_, name_=name_, maxSDSize_=maxSDSize_)
        if not _xpc.isValid:
            _xpc.CleanUp()
            self.CleanUp()
            return

        self.__l   = _PyRLock()
        self.__pn  = _xpc._processName
        self.__pan = _xpc._processAliasName
        self.__uid = _xpc._xprocessUID
        self.__xpc = _xpc

    def __str__(self) -> str:
        return self._ToString()

    @_IXProcAgent._isAttachedToFW.getter
    def _isAttachedToFW(self):
        if self.__isInvalid:
            return False
        with self.__l:
            return self.__xpc is not None

    @_IXProcAgent._isStarted.getter
    def _isStarted(self) -> bool:
        if self.__isInvalid:
            return False
        with self.__l:
            if self.__tst is not None:
                return True
            _pst = self.__UpdateTermState()
            return False if (_pst is None) else _pst.isPStarted

    @_IXProcAgent._isTerminated.getter
    def _isTerminated(self) -> bool:
        if self.__isInvalid:
            return False
        with self.__l:
            if self.__tst is not None:
                return True
            _pst = self.__UpdateTermState()
            return True if (_pst is None) else _pst.isPTerminated

    @_IXProcAgent._xprocessPID.getter
    def _xprocessPID(self) -> int:
        return self.__pid

    @_IXProcAgent._xprocessAliasName.getter
    def _xprocessAliasName(self):
        return self.__pan

    @_IXProcAgent._xprocessName.getter
    def _xprocessName(self) -> str:
        return self.__pn

    @override
    def _OnPTerminated(self, tst_ : _EPState, xc_ : int, sd_ : Any):
        with self.__l:
            if (self.__xpc is not None) or tst_.isPTerminatedByCmd:
                self.__pxc = xc_
                self.__tst = tst_
                self.__xpc = None
                if isinstance(sd_, _RteException):
                    self.__pxcp = PTWrappedException(sd_) if isinstance(sd_.reason, str) else PTException(sd_)
                else:
                    self.__psd = sd_

    @property
    def _isRunning(self) -> bool:
        if self.__isInvalid:
            return False
        with self.__l:
            if self.__tst is not None:
                return False
            _pst = self.__UpdateTermState()
            return False if (_pst is None) else _pst.isPRunning

    @property
    def _isDone(self) -> bool:
        if self.__isInvalid:
            return False
        with self.__l:
            if self.__tst is not None:
                return self.__tst.isPDone
            _pst = self.__UpdateTermState()
            return False if (_pst is None) else _pst.isPDone

    @property
    def _isFailed(self) -> bool:
        if self.__isInvalid:
            return False
        with self.__l:
            if self.__tst is not None:
                return self.__tst.isPFailed
            _pst = self.__UpdateTermState()
            return False if (_pst is None) else _pst.isPFailed

    @property
    def _isTerminatedByCmd(self) -> bool:
        if self.__isInvalid:
            return False
        with self.__l:
            if self.__tst is not None:
                return self.__tst.isPTerminatedByCmd
            _pst = self.__UpdateTermState()
            return False if (_pst is None) else _pst.isPTerminatedByCmd

    @property
    def _xprocessExitCode(self) -> Union[int, None]:
        if self.__isInvalid:
            return None
        with self.__l:
            return self.__pxc

    @property
    def _xprocessExitCodeAsStr(self):
        if self.__isInvalid:
            return None
        with self.__l:
            return _ERteTXErrorID.FromInt2Str(self.__pxc)

    @property
    def _xprocessSuppliedData(self) -> Any:
        if self.__isInvalid:
            return None
        with self.__l:
            return self.__psd

    @property
    def _xprocessException(self) -> Union[PTException, PTWrappedException, None]:
        if self.__isInvalid:
            return None
        with self.__l:
            return self.__pxcp

    def _Start(self, *args_, **kwargs_) -> bool:
        if self.__isInvalid:
            return False
        with self.__l:
            if self.__xpc is None:
                return False

            res = self.__xpc._StartProcess(*args_, **kwargs_)
            if res:
                self.__pn  = self.__xpc._processName
                self.__pid = self.__xpc._processPID
                self.__uid = self.__xpc._xprocessUID
            return res

    def _Join(self, maxWTime_: Union[int, float] =None):
        if self.__isInvalid:
            return False

        _xpc = None
        with self.__l:
            if self.__tst is not None:
                return True
            if self.__xpc is None:
                return False
            _xpc = self.__xpc

        return _xpc._JoinProcess(timeout_=maxWTime_)

    def _Terminate(self) -> bool:
        res = False
        if not self.__isInvalid:
            with self.__l:
                if self.__xpc is not None:
                    _xpc = self.__xpc
                    self.__xpc = None
                    res = _xpc._TerminateProcess()
        return res

    def _DetachFromFW(self):
        if self.__isInvalid:
            return
        with self.__l:
            if self.__xpc is not None:
                _xpc = self.__xpc
                self.__xpc = None

                _pst = _xpc._DetachFromFW()
                if (_pst is not None) and (self.__tst is None):
                    if _pst.isPTerminated:
                        self.__tst = _pst
                if self.__pxc is None:
                    self.__pxc = _ERteTXErrorID.eDetachedFromFW.value

    def _ToString(self):
        _US = _CommonDefines._CHAR_SIGN_DASH
        if self.__isInvalid:
            return _FwTDbEngine.GetText(_EFwTextID.eXProcessAgent_ToString_001).format(_US, _US, _US, _US, _US, _US)

        with self.__l:
            _n   = _US if self.__pn  is None else self.__pn
            _an  = _US if self.__pan is None else self.__pan
            _xc  = _US if self.__pxc is None else self._xprocessExitCodeAsStr
            _pid = _US if self.__pid is None else self.__pid
            _uid = _US if self.__uid is None else self.__uid
            _bDn = _US if self.__tst is None else _FwTDbEngine.GetText(_EFwTextID.eXProcessAgent_ToString_002).format(str(self.__tst.isPDone), self.__tst.compactName)
            if (_uid is not None) and _uid == 0:
                _uid = None
            res   = _FwTDbEngine.GetText(_EFwTextID.eXProcessAgent_ToString_001).format(_uid, _an, _n, _pid, _xc, _bDn)
            return res

    def _CleanUp(self):
        if self.__isInvalid:
            return
        self.__xpc = None

    @property
    def __isInvalid(self) -> bool:
        return self.__uid is None

    def __UpdateTermState(self) -> Union[_EPState, None]:
        if self.__xpc is None:
            res = self.__tst
        else:
            res = self.__xpc._GetPState()
            if (res is not None) and res.isPTerminated:
                if self.__tst is None:
                    self.__tst = res
        return res

