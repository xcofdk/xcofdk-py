# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xprocessconn.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from multiprocessing import Process as _PyProcess

from xcofdk.fwcom.xmpdefs import ChildProcessResultData

from xcofdk._xcofw.fw.fwssys.fwcore.logging           import logif
from xcofdk._xcofw.fw.fwssys.fwcore.base.sigcheck     import _CallableSignature
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.sync.mutex    import _Mutex
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject     import _AbstractSlotsObject
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes import _CommonDefines

from xcofdk._xcofw.fw.fwssys.fwmp.apiimpl.xprocessbaseif import _XProcessBaseIF
from xcofdk._xcofw.fw.fwssys.fwmp.xprocesstarget         import _EProcessTargetExitCodeID
from xcofdk._xcofw.fw.fwssys.fwmp.xprocesstarget         import _XProcessTarget
from xcofdk._xcofw.fw.fwssys.fwmp.xprocessstate          import _XProcessState
from xcofdk._xcofw.fw.fwssys.fwmp.fwrte.fwrteseed        import _FwRteSeed
from xcofdk._xcofw.fw.fwssys.fwmp.fwrte.fwrtetoken       import _FwRteToken
from xcofdk._xcofw.fw.fwssys.fwmp.fwrte.fwrtedataex      import _FwRteDataExchange
from xcofdk._xcofw.fw.fwssys.fwmp.fwrte.mpstartpolicy    import _MPStartPolicy

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine


class _XProcessConnector(_AbstractSlotsObject):

    __slots__ = [ '__hproc' , '__mtxApi' , '__xproc' , '__xptgt' , '__xpst' , '__rtedex' , '__rtetoken' ]

    def __init__( self, xprocess_ : _XProcessBaseIF, target_, name_ : str =None, args_ : tuple =None, kwargs_ : dict =None, maxDataSize_ : int =None):
        self.__xpst     = None
        self.__xptgt    = None
        self.__hproc    = None
        self.__xproc    = None
        self.__rtedex   = None
        self.__mtxApi   = None
        self.__rtetoken = None
        super().__init__()

        if _MPStartPolicy._IsStartMethodChanged():
            self.CleanUp()
            logif._LogError(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XProcessConnector_TextID_001))
            return

        if not isinstance(xprocess_, _XProcessBaseIF):
            self.CleanUp()
            return
        if not _CallableSignature.IsSignatureMatchingXProcessTargetCallback(target_):
            self.CleanUp()
            return

        if maxDataSize_ is None:
            maxDataSize_ = _FwRteToken.GetDefaultPayloadSize()
        if not (isinstance(maxDataSize_, int) and (_FwRteToken.GetMinPayloadSize() <= maxDataSize_ <= _FwRteToken.GetMaxPayloadSize())):
            self.CleanUp()
            logif._LogError(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XProcessConnector_TextID_002).format(str(maxDataSize_), _FwRteToken.GetMinPayloadSize(), _FwRteToken.GetMaxPayloadSize()))
            return

        _tokenName = _FwRteToken.GetNextUniqueTokenName()
        _token     = _FwRteToken.CreateToken(_tokenName, maxDataSize_=maxDataSize_)
        if _token is None:
            self.CleanUp()
            return

        _rtede = _FwRteDataExchange(_FwRteSeed.CheckCreateInitialInstance(), _tokenName, maxDataSize_, args_=args_, kwargs_=kwargs_)
        if not (_rtede.isValid and _rtede.currentWarningMessage is None):
            logif._LogFatal(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XProcessConnector_TextID_003).format(_CommonDefines._CHAR_SIGN_DASH if not _rtede.isValid else _rtede.currentWarningMessage))

            _FwRteToken.CloseUnlinkToken(_token)
            self.CleanUp()
            return

        _xpTgt = _XProcessTarget(target_)
        _hproc = _PyProcess(target=_xpTgt, name=name_, args=(_rtede,), daemon=False)

        self.__xpst     = _XProcessState(xpState_=None, hostProc_=_hproc)
        self.__hproc    = _hproc
        self.__xproc    = xprocess_
        self.__xptgt    = _hproc
        self.__mtxApi   = _Mutex()
        self.__rtedex   = _rtede
        self.__rtetoken = _token


    @property
    def isValid(self):
        return not self.__isInvalid

    @property
    def _processPID(self) -> int:
        return None if self.__isInvalid else self.__hproc.pid

    @property
    def _processName(self) -> str:
        return None if self.__isInvalid else self.__hproc.name

    @property
    def _processExitCode(self) -> int:
        return None if self.__isInvalid else self.__hproc.exitcode

    @property
    def _processResult(self) -> ChildProcessResultData:
        return None if self.__isInvalid else self.__rtedex.childProcessResult



    def _GetCurProcessState(self) -> _XProcessState:
        if self.__isInvalid:
            return None

        with self.__mtxApi:
            if (self.__rtetoken is not None) and not self.__xpst.isPTerminated:
                if _FwRteToken.IsTokenReadyToLoad(self.__rtetoken):
                    self._JoinProcess()
            return self.__xpst

    def _StartProcess(self) -> bool:
        if self.__isInvalid:
            return False
        if self.__xpst.isPStarted:
            return False

        with self.__mtxApi:
            self.__hproc.start()
            self.__xpst.SetGetStateID(_XProcessState._EPState.ePRunning)
            return True

    def _JoinProcess(self):
        if self.__isInvalid:
            return
        if not self.__xpst.isPStarted:
            return
        if self.__xpst.isPTerminated:
            return

        self.__hproc.join()

        with self.__mtxApi:
            _ec    = self.__hproc.exitcode
            _pst   = _XProcessState._EPState.ePDone
            _pname = f'{self._processName}:{self._processPID}'

            _ecTxt = f'{_ec}'
            if _ec > _EProcessTargetExitCodeID.eErrorExitCode_UserDefined.value:
                _ecTxt += f' ({_EProcessTargetExitCodeID.FromExitCode(_ec).compactName()})'

            _bLoaded, _proRes = _FwRteToken.ReadUnlinkToken(self.__rtetoken, bIgnoreError_=False)

            self.__rtetoken = None
            self.__xproc._SetProcessExitCode(_ec)

            if not (_bLoaded and isinstance(_proRes, ChildProcessResultData)):
                _pst = _XProcessState._EPState.ePFailed
                self.__xpst.SetGetStateID(_XProcessState._EPState.ePFailed)
                logif._LogError(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XProcessConnector_TextID_006).format(_pname, _ecTxt))

            else:
                self.__xproc._SetProcessResult(_proRes)
                self.__rtedex.childProcessResult = _proRes

                if _ec != 0:
                    _pst = _XProcessState._EPState.ePFailed
                    logif._LogError(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XProcessConnector_TextID_007).format(_pname, _ecTxt))
                elif _proRes.isProcessFailed:
                    _pst = _XProcessState._EPState.ePFailed
                    logif._LogError(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XProcessConnector_TextID_008).format(_pname))

                self.__xpst.SetGetStateID(_pst)

    def _DetachFromFW(self):
        if self.__isInvalid:
            return
        self._JoinProcess()
        _ec, _procRes = self._processExitCode, self._processResult
        self.CleanUp()
        return _ec, _procRes

    def _CleanUp(self):
        if self.__isInvalid:
            return

        if self.__rtetoken is not None:
            _FwRteToken.CloseUnlinkToken(self.__rtetoken)
            self.__rtetoken = None

        self.__xpst.CleanUp()
        self.__mtxApi.CleanUp()

        self.__xpst   = None
        self.__xptgt  = None
        self.__hproc  = None
        self.__xproc  = None
        self.__mtxApi = None
        self.__rtedex = None

    def _ToString(self, *args_, **kwargs_):
        if not self.isValid:
            return None
        return _FwTDbEngine.GetText(_EFwTextID.eXProcessConnector_ToString_01).format(self._processName, self.__rtedex)


    @property
    def __isInvalid(self):
        return self.__rtedex is None
