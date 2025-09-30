# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xprocessconn.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from signal          import SIGTERM
from typing          import Tuple
from typing          import Union
from multiprocessing import Process as _PyProcess

from _fw.fwssys.assys                    import fwsubsysshare as _ssshare
from _fw.fwssys.assys.ifs                import _IFwsProcMgr
from _fw.fwssys.assys.ifs                import _IXProcAgent
from _fw.fwssys.assys.ifs                import _IXProcConn
from _fw.fwssys.fwcore.logging           import logif
from _fw.fwssys.fwcore.logging           import vlogif
from _fw.fwssys.fwcore.base.sigcheck     import _CallableSignature
from _fw.fwssys.fwcore.base.gtimeout     import _Timeout
from _fw.fwssys.fwcore.ipc.sync.mutex    import _Mutex
from _fw.fwssys.fwcore.ipc.tsk.taskutil  import _TaskUtil
from _fw.fwssys.fwcore.types.commontypes import override
from _fw.fwssys.fwcore.types.commontypes import _CommonDefines
from _fw.fwssys.fwcore.types.commontypes import _EDepInjCmd
from _fw.fwssys.fwmp.fwrte.fwrtedefs     import _ERteTXErrorID
from _fw.fwssys.fwmp.fwrte.fwrteseed     import _FwRteSeed
from _fw.fwssys.fwmp.fwrte.fwrtetmgr     import _FwRteTokenMgr as _RteTMgr
from _fw.fwssys.fwmp.fwrte.fwrtedatax    import _ChildProcExitData
from _fw.fwssys.fwmp.fwrte.fwrtedatax    import _FwRteDataExchange
from _fw.fwssys.fwmp.fwrte.mpstartpolicy import _MPStartPolicy
from _fw.fwssys.fwmp.fwrte.rteexception  import _RteException
from _fw.fwssys.fwmp.fwrte.rteexception  import _RtePSException
from _fw.fwssys.fwmp.fwrte.rteexception  import _RteTSException
from _fw.fwssys.fwmp.xprocesstgt         import _XProcessTarget
from _fw.fwssys.fwmp.xprocessstate       import _EPState
from _fw.fwssys.fwmp.xprocessstate       import _XProcessState
from _fw.fwssys.fwerrh.fwerrorcodes      import _EFwErrorCode

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _XProcessConn(_IXProcConn):
    __slots__ = [ '__u' , '__n' , '__an' , '__h' , '__st' , '__ma' , '__dx' , '__t' , '__a' ]

    __pmi = None

    def __init__( self, xpa_ : _IXProcAgent, target_, aliasn_ : str =None, name_ : str =None, maxSDSize_ : int =None):
        self.__a  = None
        self.__n  = None
        self.__t  = None
        self.__u  = None
        self.__h  = None
        self.__an = None
        self.__dx = None
        self.__ma = None
        self.__st = None
        super().__init__()

        if _XProcessConn.__IsUnAvailable():
            return

        if _MPStartPolicy._IsStartMethodChanged():
            self.CleanUp()
            logif._LogErrorEC(_EFwErrorCode.UE_00113, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XProcessConn_TID_001))
            return

        if not isinstance(xpa_, _IXProcAgent):
            self.CleanUp()
            return

        if aliasn_ is not None:
            if not _TaskUtil.IsValidAliasName(aliasn_):
                logif._LogErrorEC(_EFwErrorCode.UE_00248, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XProcessConn_TID_013).format(str(aliasn_)))
                self.CleanUp()
                return
            aliasn_ = aliasn_.strip()

        if name_ is not None:
            if not (isinstance(name_, str) and len(name_.strip())):
                logif._LogErrorEC(_EFwErrorCode.UE_00246, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XProcessConn_TID_004).format(str(name_)))
                self.CleanUp()
                return
            name_ = name_.strip()

        if not _CallableSignature.IsSignatureMatchingXProcessTargetCallback(target_):
            self.CleanUp()
            return

        maxSDSize_, _errMsg = _RteTMgr.CheckSuppliedDataSize(maxSDSize_)
        if _errMsg is not None:
            self.CleanUp()
            logif._LogErrorEC(_EFwErrorCode.UE_00252, _errMsg)
            return

        _puid, _pidx = _TaskUtil.GetNextProcessID()

        try:
            _token = _RteTMgr.CreateToken(_puid, maxSDSize_=maxSDSize_)
        except _RtePSException as _xcp:
            logif._LogErrorEC(_EFwErrorCode.UE_00251, _xcp.message)
            self.CleanUp()
            return

        _rtedx = _FwRteDataExchange(_FwRteSeed.CheckCreateMasterSeed(), _token._tokenName, maxSDSize_, _RteTMgr.IsXcpTrackingDisabled())
        if not _rtedx.isValid:
            logif._LogFatalEC(_EFwErrorCode.FE_00047, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XProcessConn_TID_003))

            _token._CloseUnlink()
            self.CleanUp()
            return

        if (aliasn_ is None) or aliasn_.endswith(_CommonDefines._CHAR_SIGN_UNDERSCORE):
            if aliasn_ is None:
                aliasn_ = _FwTDbEngine.GetText(_EFwTextID.eMisc_TNPrefix_Process)
            aliasn_ += str(_pidx)

        _xpTgt = _XProcessTarget(target_)
        _hproc = _PyProcess(target=_xpTgt, name=name_, args=(_rtedx,), daemon=False)
        if not isinstance(_hproc.authkey, bytes):
            _xpTgt = None
            _rtedx._CleanUp()
            _token._CloseUnlink()
            self.CleanUp()
            logif._LogErrorEC(_EFwErrorCode.UE_00250, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XProcessConn_TID_018).format(aliasn_ if name_ is None else name_))
            return

        self.__a  = xpa_
        self.__u  = -1 * _puid
        self.__ma = _Mutex()

        if _XProcessConn.__IsPMISet():
            self.__pmiInst._AddProcess(self, self.__u)
            if not self._PcIsLcProxySet():
                _xpTgt = None
                _rtedx._CleanUp()
                _token._CloseUnlink()
                self.CleanUp()
                return

        self.__h  = _hproc
        self.__n  = _hproc.name
        self.__t  = _token
        self.__dx = _rtedx
        self.__an = aliasn_
        self.__st = _XProcessState(hostProc_=_hproc)

    @_IXProcConn._xprocessAgent.getter
    def _xprocessAgent(self) -> _IXProcAgent:
        return self.__a

    @override
    def _ConfirmPUID(self):
        if not self.__isInvalid:
            self.__u *= -1

    @property
    def isValid(self):
        return not self.__isInvalid

    @property
    def _processPID(self) -> int:
        return None if self.__isInvalid or (self.__h is None) else self.__h.pid

    @property
    def _processName(self) -> str:
        return None if self.__isInvalid else self.__n

    @property
    def _processAliasName(self) -> str:
        return None if self.__isInvalid else self.__an

    @property
    def _xprocessUID(self) -> int:
        res = None if self.__isInvalid else self.__u
        if res < 0:
            res = 0
        return res

    def _GetPState(self) -> Union[_EPState, None]:
        if self.__isInvalid:
            return None
        if not self._PcIsLcProxyModeNormal():
            return None

        _mtx = self.__ma
        with _mtx:
            res = self.__GetPState()

        if (res is not None) and res.isPTerminated:
            self._CleanUp(bSkipMtx_=True)
            self.CleanUp()
            _mtx.CleanUp()
        return res

    def _StartProcess(self, *args_, **kwargs_) -> bool:
        if self.__isInvalid:
            return False

        _pst = self.__st.GetPStateID()
        if (_pst is None) or _pst.isPStarted:
            return False
        if not _XProcessConn.__IsPMISet():
            return False

        with self.__ma:
            if not self.__dx._SetPStartArgs(*args_, **kwargs_):
                return False
            if not self._PcIsLcProxySet():
                self.__pmiInst._AddProcess(self, self.__u)
                if not self._PcIsLcProxySet():
                    self.CleanUp()
                    return False
                if not self._PcIsLcProxyModeNormal():
                    _pn = f'{self._processAliasName}:{self._processPID}'
                    logif._LogInfo(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwsProcMgr_TID_003).format(_pn))
                    return False

            self.__h.start()

            self.__n = self.__h.name
            self.__st.SetGetPStateID(_EPState.ePRunning)
            return True

    def _JoinProcess(self, timeout_: Union[int, float] =None):
        if self.__isInvalid:
            return False
        if not self._PcIsLcProxyModeNormal():
            return False

        _xpa = self.__a
        if _xpa is None:
            return False

        if not _xpa._isAttachedToFW:
            return False
        if (not _xpa._isStarted) or _xpa._isTerminated:
            return True

        if timeout_ is not None:
            timeout_ = _Timeout.TimespanToTimeout(timeout_)
            if timeout_ is None:
                return False

        _MAX_TIME_MS = 0 if (timeout_ is None) else timeout_.toMSec
        _timeSpanMS  = 100
        _totalTimeMS = 0

        _pn   = f'{self._processAliasName}:{self._processPID}'
        _prfx = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XProcessConn_TID_002).format(_pn)

        res   = False
        _bXcp = False
        while True:
            if _bXcp:
                break

            try:
                _xpa = self.__a
                if (_xpa is None) or _xpa._isTerminated:
                    res = True
                    break
                if not _xpa._isAttachedToFW:
                    break

                _TaskUtil.SleepMS(_timeSpanMS)

                _totalTimeMS += _timeSpanMS
                if (_MAX_TIME_MS > 0) and (_totalTimeMS >= _MAX_TIME_MS):
                    break

            except KeyboardInterrupt:
                _bXcp = True
                _midPart = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XProcessConn_TID_012).format(_pn)
                _msg     = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_KeyboardInterrupt).format(_prfx, _midPart)
                _ssshare._BookKBI(_msg, bVLog_=True)
            except BaseException as _xcp:
                _bXcp = True
                _msg  = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XProcessConn_TID_023).format(_pn, str(_xcp))
                vlogif._LogUrgentWarning(_msg)
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00969)
        return res

    def _TerminateProcess(self) -> bool:
        if self.__isInvalid:
            return False

        _mtx = self.__ma
        with _mtx:
            _pst = self.__st.GetPStateID()
            if (_pst is None) or (not _pst.isPStarted) or _pst.isPTerminated:
                return False if (_pst is None) or (not _pst.isPStarted) else True

            self.__h.terminate()
            _pst =self.__GetPState(bTermByCmd_=True)

        if (_pst is not None) and _pst.isPTerminated:
            self._CleanUp(bSkipMtx_=True)
            self.CleanUp()
            _mtx.CleanUp()
        return True

    def _DetachFromFW(self) -> Union[_EPState, None]:
        if self.__isInvalid:
            return None

        _mtx = self.__ma
        with _mtx:
            self.__a = None
            res = self.__GetPState()
            self._CleanUp(bSkipMtx_=True)

        self.CleanUp()
        _mtx.CleanUp()
        return res

    def _CleanUp(self, bSkipMtx_ =False):
        if self.__isInvalid:
            return

        _mtx = self.__ma
        self.__ma = None

        if not bSkipMtx_:
            _mtx.CleanUp()

        if self.__h is not None:
            self.__CloseHostProc()

        if self.__t is not None:
            self.__t._CloseUnlink()
        if self.__dx is not None:
            self.__dx._CleanUp()

        self.__st.CleanUp()

        self.__a  = None
        self.__n  = None
        self.__t  = None
        self.__u  = None
        self.__h  = None
        self.__an = None
        self.__dx = None
        self.__st = None
        super()._CleanUp()

    def _ToString(self):
        if self.__isInvalid:
            return None
        return _FwTDbEngine.GetText(_EFwTextID.eXProcessConn_ToString_01).format(self._processAliasName, self._processName, self.__dx)

    @staticmethod
    def _IsAvailable():
        return not _XProcessConn.__IsUnAvailable()

    @staticmethod
    def _ClsDepInjection(dinjCmd_ : _EDepInjCmd, ak_, pmi_ : _IFwsProcMgr):
        return _XProcessConn.__SetPMI(dinjCmd_, ak_, pmi_)

    @staticmethod
    def __IsPMISet():
        return isinstance(_XProcessConn.__pmi, _IFwsProcMgr)

    @staticmethod
    def __IsUnAvailable():
        return (_XProcessConn.__pmi is None) or isinstance(_XProcessConn.__pmi, int)

    @staticmethod
    def __SetPMI(dinjCmd_ : _EDepInjCmd, ak_, pmi_ : _IFwsProcMgr):
        res = False
        _ak = hash(str(_XProcessConn.__init__))

        if ak_ != _ak:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00953)
        else:
            _pmi = _XProcessConn.__pmi
            if dinjCmd_.isDeInject:
                if isinstance(_pmi, _IFwsProcMgr):
                    res = True
                    _XProcessConn.__pmi = id(_pmi)
            elif _pmi is None:
                if pmi_ is not None:
                    res = True
                    _XProcessConn.__pmi = pmi_
        if not res:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00955)
        return res

    @staticmethod
    def __FetchExitCode(hproc_ : _PyProcess):
        _bA, _xc = hproc_.is_alive(), None
        if not _bA:
            _xc = hproc_.exitcode
        return _bA, _xc

    @property
    def __isInvalid(self):
        return self.__ma is None

    @property
    def __pmiInst(self) -> Union[_IFwsProcMgr, None]:
        _pmi = _XProcessConn.__pmi
        return None if not isinstance(_pmi, _IFwsProcMgr) else _pmi

    def __IsReadyToLoad(self) -> _ERteTXErrorID:
        _MAX_RETRY = 1 if self.__h.is_alive() else 3
        _TIMES_MS  = 50

        _cnt = 1
        while True:
            _errID = self.__t._IsReadyToLoad()
            if not _errID.isDontCare:
                break
            if _cnt >= _MAX_RETRY:
                break

            _TaskUtil.SleepMS(_TIMES_MS)
            _cnt += 1
        return _errID

    def __CloseHostProc(self, bWait_ =True) -> Tuple[bool, Union[int, None]]:
        if self.__isInvalid or (self.__h is None):
            return False, None

        _MAX_TIME_MS = 300
        _timeMS      = 50
        _totalTimeMS = 0

        _hproc   = self.__h
        self.__h = None

        if not bWait_:
            res, _xc = _XProcessConn.__FetchExitCode(_hproc)
        else:
            while True:
                _TaskUtil.SleepMS(_timeMS)
                _totalTimeMS += _timeMS

                res, _xc = _XProcessConn.__FetchExitCode(_hproc)
                if not res:
                    break
                if _totalTimeMS >= _MAX_TIME_MS:
                    break

        if not res:
            try:
                _hproc.close()
            except (ValueError, Exception) as _xcp:
                pass
        return res, _xc

    def __UnlinkToken(self):
        if self.__t is None:
            return None

        try:
            res = self.__t._ReadUnlink()
            if (res is not None) and not isinstance(res, (_ChildProcExitData, _RteException)):
                _msg  = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XProcessConn_TID_002).format(f'{self._processAliasName}:{self._processPID}')
                _msg += _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XProcessConn_TID_016).format(type(res).__name__)
                res  = _RtePSException(msg_=_msg, code_=_ERteTXErrorID.eUnexpectedTokenPayload.value)
        except _RteException as _xcp:
            res = _xcp
        return res

    def __GetPState(self, bTermByCmd_ =False) -> Union[_EPState, None]:
        while True:
            res = self.__st.GetPStateID()
            if (res is None) or not res.isPStarted:
                break
            if res.isPTerminated:
                break

            if self.__n is None:
                self.__n = self.__h.name

            _errID = self.__IsReadyToLoad()

            res = self.__UpdatePState(_errID, bTermByCmd_=bTermByCmd_)
            break
        return res

    def __UpdatePState(self, errID_ : _ERteTXErrorID, bTermByCmd_ =False) -> Union[_EPState, None]:
        _bA, _xc = _XProcessConn.__FetchExitCode(self.__h)
        _bT      = bTermByCmd_ or not _bA
        _sd      = None
        _pn      = f'{self._processAliasName}:{self._processPID}'
        _prfx    = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XProcessConn_TID_002).format(_pn)

        if bTermByCmd_:
            errID_ = _ERteTXErrorID.eDontCare

            self.__st._UnsetHostProcess()
            _bAlive, _xc = self.__CloseHostProc(bWait_=False)

            _msg = _prfx
            if _bAlive:
                _msg += _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XProcessConn_TID_014).format(300)
                logif._LogUrgentWarning(_msg)
            else:
                _msg += _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XProcessConn_TID_015)
                logif._LogWarning(_msg)

        if not errID_.isDontCare:
            res = _EPState.ePFailed

            if errID_.isLowLevelTokenError:
                _xc = errID_.value
                _msg = _prfx + _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XProcessConn_TID_017)
                logif._LogErrorEC(_EFwErrorCode.UE_00249, _msg)

            else:
                _procXD = self.__UnlinkToken()

                self.__dx._CleanUp()
                self.__dx = None
                self.__t  = None

                if self.__h is not None:
                    self.__st._UnsetHostProcess()
                    _bAlive, _xc = self.__CloseHostProc(bWait_=False)

                if isinstance(_procXD, _RteException):
                    _xc  = _procXD.code
                    _msg = _prfx
                    if isinstance(_procXD, _RtePSException):
                        _msg += _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XProcessConn_TID_008).format(str(_procXD))
                        logif._LogErrorEC(_EFwErrorCode.UE_00115, _msg)
                    else:
                        _msg += _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XProcessConn_TID_020).format(str(_procXD))
                        logif._LogErrorEC(_EFwErrorCode.UE_00254, _msg)

                elif _procXD is None:
                    if _xc is None:
                        _xc = _ERteTXErrorID.eWriteRteToken.value
                    _msg = _prfx + _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XProcessConn_TID_019)
                    logif._LogErrorEC(_EFwErrorCode.UE_00253, _msg)

                else:
                    _sd = _procXD.exitData
                    _xc = _procXD.exitCode

                    if isinstance(_sd, _RteTSException):
                        _xc  = _sd.code
                        _msg = _prfx + _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XProcessConn_TID_006).format(str(_sd))
                        logif._LogErrorEC(_EFwErrorCode.UE_00255, _msg)
                    elif not _procXD.isProcessSucceeded:
                        _msg = _prfx + _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XProcessConn_TID_007).format(_xc, _procXD.errorID.compactName)
                        logif._LogErrorEC(_EFwErrorCode.UE_00116, _msg)
                    else:
                        res = _EPState.ePDone
        elif _bT:
            _msg = _prfx
            if not isinstance(_xc, int):
                _xc2  = _ERteTXErrorID.eInvalidExitCodeByHostProc.value
                _msg += _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XProcessConn_TID_010).format(str(_xc), _xc2)
                _xc   = _xc2
            else:
                _midPart = _xc if _xc != (-1*SIGTERM) else _ERteTXErrorID.FromInt2Str(_xc)
                _msg    += _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XProcessConn_TID_011).format(_midPart)

            if _xc == 0:
                if bTermByCmd_:
                    res = _EPState.ePTermByCmd
                else:
                    res = _EPState.ePDone
                logif._LogWarning(_msg)
            elif not (bTermByCmd_ or (_xc == (-1*SIGTERM))):
                res = _EPState.ePFailed
                logif._LogErrorEC(_EFwErrorCode.UE_00247, _msg)
            else:
                res = _EPState.ePTermByCmd
                logif._LogWarning(_msg)
        else:
            res = self.__st.GetPStateID()

        if res is not None:
            if res != self.__st.GetPStateID():
                self.__st.SetGetPStateID(res)

            if res.isPTerminated:
                if self.__a is not None:
                    self.__a._OnPTerminated(res, _xc, _sd)
        return res
