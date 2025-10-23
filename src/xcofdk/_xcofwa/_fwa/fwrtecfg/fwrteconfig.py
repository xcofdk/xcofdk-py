# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwrteconfig.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

import logging
from   enum      import unique
from   threading import RLock as _PyRLock
from   typing    import List
from   typing    import Union

from xcofdk.fwcom.fwdefs import ERtePolicyID
from xcofdk.fwcom.fwdefs import ELineEnding

from _fw.fwssys.fwcore.logging           import logif
from _fw.fwssys.fwcore.base.fsutil       import _FSUtil
from _fw.fwssys.fwcore.ipc.net.tcpsocket import _TCPListenerSocket
from _fw.fwssys.fwcore.swpfm.sysinfo     import _SystemInfo
from _fw.fwssys.fwcore.types.aobject     import _AbsSlotsObject
from _fw.fwssys.fwcore.types.commontypes import override
from _fw.fwssys.fwcore.types.commontypes import _CommonDefines
from _fw.fwssys.fwcore.types.commontypes import _ERtePolicyBase
from _fw.fwssys.fwcore.types.ebitmask    import _EBitMask
from _fw.fwssys.fwerrh.fwerrorcodes      import _EFwErrorCode
from _fwa.fwrtecfg.iffwrtecfg            import _IFwRteConfig

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

@unique
class _EFwRtePolicyID(_ERtePolicyBase):
    bfEnableAutoStopByDefault     = (0x00001 << 31)

    bfBypassExperimentalFTGuard   = (0x00001 << ERtePolicyID.eBypassExperimentalFTGuard.value)

    bfEnableAutoStop              = (0x00001 << ERtePolicyID.eEnableAutoStop.value)
    bfEnableForcedAutoStop        = (0x00001 << ERtePolicyID.eEnableForcedAutoStop.value)
    bfEnableTerminalMode          = (0x00001 << ERtePolicyID.eEnableTerminalMode.value)

    bfDisableSubSysXMsg           = (0x00001 << ERtePolicyID.eDisableSubSystemMessaging.value)
    bfDisableSubSysXMP            = (0x00001 << ERtePolicyID.eDisableSubSystemMultiProcessing.value)
    bfDisableSubSysXMPXcpTracking = (0x00001 << ERtePolicyID.eDisableExceptionTrackingOfChildProcesses.value)

    bfDisableLogRDConsoleSink     = (0x00001 << ERtePolicyID.eDisableLogRDConsoleSink)
    bfEnableLogRDFileSink         = (0x00001 << ERtePolicyID.eEnableLogRDFileSink )
    bfEnableLogRDTcpSink          = (0x00001 << ERtePolicyID.eEnableLogRDTcpSink)

    @staticmethod
    def _FromFwRtePolicyID(policyID_ : ERtePolicyID):
        if not isinstance(policyID_, ERtePolicyID):
            return None
        return _EFwRtePolicyID(0x00001 << policyID_.value)

class _RDFileHandler(logging.FileHandler):
    def __init__(self, filename_, mode_ =_CommonDefines._CHAR_SIGN_FILE_MODE_APPEND, encoding_ =None):
        super().__init__(filename_, mode=mode_, encoding=encoding_, delay=False)

    @override
    def emit(self, record_):
        _msg = record_.msg
        if _msg.endswith(_CommonDefines._CHAR_SIGN_LF):
            record_.msg = _msg[:len(_msg)-1]
        logging.FileHandler.emit(self, record_)

class _RDSinkConfig:
    __slots__ = [ '__bF' , '__fp' , '__fm' , '__pl' , '__ip' , '__pt' , '__le' ]

    def __init__( self
                , bFileSink_ : bool
                , filePath_  : str =None, fileMode_ : str =None, pyLogger_   : logging.Logger =None
                , ip_        : str =None, port_     : int =None, lineEnding_ : str            =None):
        self.__bF = bFileSink_
        self.__fp = filePath_
        self.__fm = fileMode_
        self.__pl = pyLogger_
        self.__pt = port_
        self.__ip = ip_
        self.__le = lineEnding_

    @property
    def isTcpSinkConfig(self) -> bool:
        return not self.__bF

    @property
    def isFileSinkConfig(self) -> bool:
        return self.__bF

    @property
    def filePath(self) -> str:
        return self.__fp

    @property
    def fileMode(self) -> str:
        return self.__fm

    @property
    def pyLogger(self) -> logging.Logger:
        return self.__pl

    @property
    def ip(self) -> str:
        return self.__ip

    @property
    def port(self) -> int:
        return self.__pt

    @property
    def lineEnding(self) -> str:
        return self.__le

class _FwRteConfig(_AbsSlotsObject, _IFwRteConfig):
    __slots__ = [ '__l' , '__bm' , '__bF' , '__fc' , '__tc', '__m' ]

    __sgltn = None

    def __init__(self):
        self.__l  = _PyRLock()
        self.__m  = None
        self.__bF = False
        self.__bm = _EFwRtePolicyID.bfEnableAutoStopByDefault
        self.__fc = None
        self.__tc = None
        _AbsSlotsObject.__init__(self)
        _IFwRteConfig.__init__(self)

        if _FwRteConfig.__sgltn is None:
            _FwRteConfig.__sgltn = self

    def __str__(self):
        return self.ToString()

    @_IFwRteConfig._isValid.getter
    def _isValid(self) -> bool:
        if not self.__IsValid():
            return False
        with self.__l:
            return self.__m is None

    @_IFwRteConfig._isAutoStopEnabled.getter
    def _isAutoStopEnabled(self) -> bool:
        return self.__IsRtePolicySet(ERtePolicyID.eEnableAutoStop) or self._isAutoStopEnabledByDefault

    @_IFwRteConfig._isForcedAutoStopEnabled.getter
    def _isForcedAutoStopEnabled(self) -> bool:
        return self.__IsRtePolicySet(ERtePolicyID.eEnableForcedAutoStop)

    @_IFwRteConfig._isTerminalModeEnabled.getter
    def _isTerminalModeEnabled(self) -> bool:
        return self.__IsRtePolicySet(ERtePolicyID.eEnableTerminalMode)

    @_IFwRteConfig._isExperimentalFreeThreadingBypassed.getter
    def _isExperimentalFreeThreadingBypassed(self) -> bool:
        return self.__IsRtePolicySet(ERtePolicyID.eBypassExperimentalFTGuard)

    @_IFwRteConfig._isSubSystemMessagingDisabled.getter
    def _isSubSystemMessagingDisabled(self) -> bool:
        return self.__IsRtePolicySet(ERtePolicyID.eDisableSubSystemMessaging)

    @_IFwRteConfig._isSubSystemMultiProcessingDisabled.getter
    def _isSubSystemMultiProcessingDisabled(self) -> bool:
        return self.__IsRtePolicySet(ERtePolicyID.eDisableSubSystemMultiProcessing)

    @_IFwRteConfig._isExceptionTrackingOfChildProcessesDisabled.getter
    def _isExceptionTrackingOfChildProcessesDisabled(self) -> bool:
        return self.__IsRtePolicySet(ERtePolicyID.eDisableExceptionTrackingOfChildProcesses)

    @_IFwRteConfig._isLogRDConsoleSinkDisabled.getter
    def _isLogRDConsoleSinkDisabled(self) -> bool:
        return self.__IsRtePolicySet(ERtePolicyID.eDisableLogRDConsoleSink)

    @_IFwRteConfig._isLogRDFileSinkEnabled.getter
    def _isLogRDFileSinkEnabled(self) -> bool:
        return self.__IsRtePolicySet(ERtePolicyID.eEnableLogRDFileSink)

    @_IFwRteConfig._isLogRDTcpSinkEnabled.getter
    def _isLogRDTcpSinkEnabled(self) -> bool:
        return self.__IsRtePolicySet(ERtePolicyID.eEnableLogRDTcpSink)

    @property
    def _isFrozen(self) -> bool:
        if not self.__IsValid():
            return False
        with self.__l:
            return (self.__m is None) and self.__bF

    @property
    def _isRteStarted(self) -> bool:
        return self._isFrozen

    @property
    def _isAutoStopEnabledByDefault(self) -> bool:
        return self.__IsRtePolicySet(_EFwRtePolicyID.bfEnableAutoStopByDefault)

    @property
    def _isLogRDActiveServiceRequired(self) -> bool:
        return self._isLogRDFileSinkEnabled or self._isLogRDTcpSinkEnabled

    @property
    def _rdTcpSinkConfig(self) -> Union[_RDSinkConfig, None]:
        return self.__tc

    @property
    def _rdFileSinkConfig(self) -> Union[_RDSinkConfig, None]:
        return self.__fc

    @staticmethod
    def _GetInstance(bFreeze_ =False):
        res = _FwRteConfig.__sgltn
        if res is None:
            res = _FwRteConfig()
        if bFreeze_ and not res._isFrozen:
            res.__bF = True
        return res

    @staticmethod
    def _ConfigureRtePolicy( rtePolicy_          : Union[ERtePolicyID, List[ERtePolicyID]]
                           , rdFileSinkPath_     : Union[str, None] =None
                           , rdFileSinkEncoding_ : Union[str, None] =_CommonDefines._STR_ENCODING_UTF8
                           , rdFileSinkAppend_   : bool             =False
                           , rdTcpSinkIpAddr_    : str              =None
                           , rdTcpSinkPort_      : int              =None
                           , rdTcpSinkLineEnding_: ELineEnding      =ELineEnding.NOLE ) -> _IFwRteConfig:
        res = _FwRteConfig._GetInstance()
        if res._isFrozen:
            if isinstance(rtePolicy_, ERtePolicyID) or (isinstance(rtePolicy_, list) and len(rtePolicy_)):
                logif._XLogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteConfig_TID_001))
            return res

        with res.__l:
            _bm = res.__bm

            _bBypassXFT = None
            _bEnableTM  = None
            _bEnableAS  = None
            _bEnableFAS = None

            if rtePolicy_ is None:
                rtePolicy_ = []
            elif not isinstance(rtePolicy_, list):
                rtePolicy_ = [rtePolicy_]

            for _pp in rtePolicy_:
                if not isinstance(_pp, ERtePolicyID):
                    res.__m = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteConfig_TID_005).format(str(_pp))
                    logif._XLogErrorEC(_EFwErrorCode.UE_00212, res.__m)
                    return res

                if _pp == ERtePolicyID.eEnableAutoStop:
                    _bEnableAS = True
                elif _pp == ERtePolicyID.eEnableForcedAutoStop:
                    _bEnableFAS = True
                elif _pp == ERtePolicyID.eEnableTerminalMode:
                    _bEnableTM = True
                elif _pp == ERtePolicyID.eBypassExperimentalFTGuard:
                    _bBypassXFT = True
                elif _pp == ERtePolicyID.eDisableSubSystemMessaging:
                    pass
                elif _pp == ERtePolicyID.eDisableSubSystemMultiProcessing:
                    pass
                elif _pp == ERtePolicyID.eDisableExceptionTrackingOfChildProcesses:
                    pass
                elif _pp == ERtePolicyID.eDisableLogRDConsoleSink:
                    pass
                elif (_pp == ERtePolicyID.eEnableLogRDFileSink) or (_pp == ERtePolicyID.eEnableLogRDTcpSink):
                    res = _FwRteConfig._ConfigureRDSink( _pp
                                                       , rdFileSinkPath_=rdFileSinkPath_
                                                       , rdFileSinkEncoding_=rdFileSinkEncoding_
                                                       , rdFileSinkAppend_=rdFileSinkAppend_
                                                       , rdTcpSinkIpAddr_=rdTcpSinkIpAddr_
                                                       , rdTcpSinkPort_=rdTcpSinkPort_
                                                       , rdTcpSinkLineEnding_=rdTcpSinkLineEnding_)
                else:
                    res.__m = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteConfig_TID_006).format(str(_pp))
                    logif._XLogErrorEC(_EFwErrorCode.UE_00213, res.__m)

                if res.__m is not None:
                    return res
                _bm = _EBitMask.AddEnumBitFlag(_bm, _EFwRtePolicyID._FromFwRtePolicyID(_pp))

            if _EBitMask.IsEnumBitFlagSet(_bm, _EFwRtePolicyID.bfDisableSubSysXMP):
                if not _EBitMask.IsEnumBitFlagSet(_bm, _EFwRtePolicyID.bfDisableSubSysXMPXcpTracking):
                    _bm = _EBitMask.AddEnumBitFlag(_bm, _EFwRtePolicyID.bfDisableSubSysXMPXcpTracking)

            if _bBypassXFT is not None:
                if _bBypassXFT:
                    _pp = _EFwRtePolicyID._FromFwRtePolicyID(ERtePolicyID.eBypassExperimentalFTGuard)
                    if not _SystemInfo._IsPyVersionSupportedFTPython():
                        _bm = _EBitMask.RemoveEnumBitFlag(_bm, _pp)
                        _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteConfig_TID_003).format(_SystemInfo._GetPythonVer())
                        logif._XLogWarning(_msg)
                    elif not _SystemInfo._IsGilDisabled():
                        _bm = _EBitMask.RemoveEnumBitFlag(_bm, _pp)
                        _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteConfig_TID_002).format(_SystemInfo._GetPythonVer())
                        logif._XLogWarning(_msg)
                    elif _SystemInfo._IsPyVersionSupportedOfficialFTPython():
                        _bm = _EBitMask.RemoveEnumBitFlag(_bm, _pp)
                        _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteConfig_TID_017).format(_SystemInfo._GetPythonVer())
                        logif._XLogWarning(_msg)

            if _bEnableAS is None:
                _bEnableAS = _EBitMask.IsEnumBitFlagSet(_bm, _EFwRtePolicyID.bfEnableAutoStop)
            if _bEnableFAS is None:
                _bEnableFAS = _EBitMask.IsEnumBitFlagSet(_bm, _EFwRtePolicyID.bfEnableForcedAutoStop)
            if _bEnableTM is None:
                _bEnableTM = _EBitMask.IsEnumBitFlagSet(_bm, _EFwRtePolicyID.bfEnableTerminalMode)

            if _bEnableAS or _bEnableFAS or _bEnableTM:
                if _bEnableAS and _bEnableFAS:
                    res.__m = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteConfig_TID_007)
                    logif._XLogErrorEC(_EFwErrorCode.UE_00214, res.__m)
                    return res

                if _bEnableAS and _EBitMask.IsEnumBitFlagSet(_bm, _EFwRtePolicyID.bfEnableForcedAutoStop):
                    res.__m = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteConfig_TID_008)
                    logif._XLogErrorEC(_EFwErrorCode.UE_00215, res.__m)
                    return res

                if _bEnableFAS and _EBitMask.IsEnumBitFlagSet(_bm, _EFwRtePolicyID.bfEnableAutoStop):
                    res.__m = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteConfig_TID_009)
                    logif._XLogErrorEC(_EFwErrorCode.UE_00216, res.__m)
                    return res

                if (_bEnableAS or _bEnableFAS) and _bEnableTM:
                    res.__m = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteConfig_TID_004)
                    logif._XLogErrorEC(_EFwErrorCode.UE_00211, res.__m)
                    return res

                if _EBitMask.IsEnumBitFlagSet(_bm, _EFwRtePolicyID.bfEnableAutoStopByDefault):
                    _bm = _EBitMask.RemoveEnumBitFlag(_bm, _EFwRtePolicyID.bfEnableAutoStopByDefault)

            res.__m  = None
            res.__bm = _bm
        return res

    @staticmethod
    def _ConfigureRDSink( rtePolicy_          : ERtePolicyID
                        , rdFileSinkPath_     : Union[str, None] =None
                        , rdFileSinkEncoding_ : Union[str, None] =_CommonDefines._STR_ENCODING_UTF8
                        , rdFileSinkAppend_   : bool             =False
                        , rdTcpSinkIpAddr_    : str              =None
                        , rdTcpSinkPort_      : int              =None
                        , rdTcpSinkLineEnding_: ELineEnding      =ELineEnding.NOLE ) -> _IFwRteConfig:
        res = _FwRteConfig._GetInstance()
        if res._isFrozen:
            return res

        _ec = None
        if (rtePolicy_ != ERtePolicyID.eEnableLogRDFileSink) and (rtePolicy_ != ERtePolicyID.eEnableLogRDTcpSink):
            _ec     = _EFwErrorCode.UE_00261
            res.__m = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteConfig_TID_005).format(str(rtePolicy_))
        elif (rtePolicy_ == ERtePolicyID.eEnableLogRDFileSink) and (res.__fc is not None):
            _ec     = _EFwErrorCode.UE_00262
            res.__m = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteConfig_TID_010)
        elif (rtePolicy_ == ERtePolicyID.eEnableLogRDTcpSink) and (res.__tc is not None):
            _ec     = _EFwErrorCode.UE_00263
            res.__m = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteConfig_TID_011)

        if res.__m is not None:
            logif._XLogErrorEC(_ec, res.__m)
            return res

        if rtePolicy_ == ERtePolicyID.eEnableLogRDFileSink:
            _fm = _CommonDefines._CHAR_SIGN_FILE_MODE_APPEND if rdFileSinkAppend_ else _CommonDefines._CHAR_SIGN_FILE_MODE_WRITE
            _fp = _FSUtil.GetLogFilePath(filePath_=rdFileSinkPath_)

            try:
                _pylog = logging.getLogger(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteConfig_TID_012))
                _pylog.setLevel(logging.INFO)
                _fmt = logging.Formatter(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteConfig_TID_013))
                _fh = _RDFileHandler(_fp, mode_=_fm, encoding_=rdFileSinkEncoding_)
                _fh.setLevel(logging.INFO)
                _fh.setFormatter(_fmt)
                _pylog.addHandler(_fh)
                res.__fc = _RDSinkConfig(True, filePath_=_fp, fileMode_=_fm, pyLogger_=_pylog)
            except (FileNotFoundError, Exception) as _xcp:
                res.__m = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteConfig_TID_014).format(type(_xcp).__name__, _xcp)
                logif._XLogErrorEC(_EFwErrorCode.UE_00264, res.__m)

        elif rtePolicy_ == ERtePolicyID.eEnableLogRDTcpSink:
            if not isinstance(rdTcpSinkLineEnding_, ELineEnding):
                rdTcpSinkLineEnding_ = f'{rdTcpSinkLineEnding_}'
                if not isinstance(rdTcpSinkIpAddr_, str):
                    rdTcpSinkIpAddr_ = f'{rdTcpSinkIpAddr_}'
                if not isinstance(rdTcpSinkPort_, int):
                    rdTcpSinkPort_ = f'{rdTcpSinkPort_}'
                res.__m = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteConfig_TID_016).format(rdTcpSinkLineEnding_, rdTcpSinkIpAddr_, rdTcpSinkPort_)
                logif._XLogErrorEC(_EFwErrorCode.UE_00266, res.__m)
            else:
                _xcp = _TCPListenerSocket._CheckListenerParams(ip_=rdTcpSinkIpAddr_, port_=rdTcpSinkPort_, timeout_=_TCPListenerSocket._DEFAULT_LISTENER_TIMEOUT)
                if _xcp is not None:
                    if not isinstance(rdTcpSinkIpAddr_, str):
                        rdTcpSinkIpAddr_ = f'{rdTcpSinkIpAddr_}'
                    if not isinstance(rdTcpSinkPort_, int):
                        rdTcpSinkPort_ = f'{rdTcpSinkPort_}'
                    res.__m = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteConfig_TID_015).format(type(_xcp).__name__, rdTcpSinkIpAddr_, rdTcpSinkPort_, _xcp)
                    logif._XLogErrorEC(_EFwErrorCode.UE_00265, res.__m)
                else:
                    res.__tc = _RDSinkConfig(False, ip_=rdTcpSinkIpAddr_, port_=rdTcpSinkPort_, lineEnding_=_FwRteConfig._EncodeLineEnding(rdTcpSinkLineEnding_))
        return res

    def _ToString(self):
        if not self.__IsValid():
            return None

        with self.__l:
            _txtAS = str(self._isAutoStopEnabled)
            if self._isAutoStopEnabledByDefault:
                _txtAS += _CommonDefines._CHAR_SIGN_SPACE + _FwTDbEngine.GetText(_EFwTextID.eFwRteConfig_ToString_07)

            _FMT = _FwTDbEngine.GetText(_EFwTextID.eFwRteConfig_ToString_11)
            res  = _FwTDbEngine.GetText(_EFwTextID.eFwRteConfig_ToString_01)
            res += _FMT.format(_FwTDbEngine.GetText(_EFwTextID.eFwRteConfig_ToString_02) , _txtAS)
            res += _FMT.format(_FwTDbEngine.GetText(_EFwTextID.eFwRteConfig_ToString_06) , str(self._isForcedAutoStopEnabled))
            res += _FMT.format(_FwTDbEngine.GetText(_EFwTextID.eFwRteConfig_ToString_03) , str(self._isTerminalModeEnabled))
            res += _FMT.format(_FwTDbEngine.GetText(_EFwTextID.eFwRteConfig_ToString_04) , str(self._isExperimentalFreeThreadingBypassed))
            res += _FMT.format(_FwTDbEngine.GetText(_EFwTextID.eFwRteConfig_ToString_08) , str(self._isSubSystemMessagingDisabled))
            res += _FMT.format(_FwTDbEngine.GetText(_EFwTextID.eFwRteConfig_ToString_09) , str(self._isSubSystemMultiProcessingDisabled))
            res += _FMT.format(_FwTDbEngine.GetText(_EFwTextID.eFwRteConfig_ToString_10) , str(self._isExceptionTrackingOfChildProcessesDisabled))
            res += _FMT.format(_FwTDbEngine.GetText(_EFwTextID.eFwRteConfig_ToString_12) , str(self._isLogRDConsoleSinkDisabled))
            res += _FMT.format(_FwTDbEngine.GetText(_EFwTextID.eFwRteConfig_ToString_13) , str(self._isLogRDFileSinkEnabled))
            res += _FMT.format(_FwTDbEngine.GetText(_EFwTextID.eFwRteConfig_ToString_14) , str(self._isLogRDTcpSinkEnabled))
            if self.__m is not None:
                res += _FwTDbEngine.GetText(_EFwTextID.eFwRteConfig_ToString_05).format(self.__m)
        return res

    def _CleanUp(self):
        if _FwRteConfig.__sgltn is not None:
            _FwRteConfig.__sgltn = None
        self.__l  = None
        self.__m  = None
        self.__bF = None
        self.__bm = None
        self.__fc = None
        self.__tc = None

    @staticmethod
    def _EncodeLineEnding(rdTcpSinkLineEnding_: ELineEnding) -> Union[str, None]:
        if not isinstance(rdTcpSinkLineEnding_, ELineEnding):
            res = None
        elif rdTcpSinkLineEnding_ == ELineEnding.NOLE:
            res = _CommonDefines._STR_EMPTY
        elif rdTcpSinkLineEnding_ == ELineEnding.LF:
            res = _CommonDefines._CHAR_SIGN_LF
        elif rdTcpSinkLineEnding_ == ELineEnding.CR:
            res = _CommonDefines._CHAR_SIGN_CR
        else:  
            res = _CommonDefines._CHAR_SIGN_CR + _CommonDefines._CHAR_SIGN_LF
        return res

    def __IsValid(self) -> bool:
        return self.__bm is not None

    def __IsRtePolicySet(self, rtePolicyID_ : Union[ERtePolicyID, _EFwRtePolicyID]):
        if not self.__IsValid():
            return False

        with self.__l:
            res = isinstance(rtePolicyID_, _EFwRtePolicyID)
            if (not res) and isinstance(rtePolicyID_, ERtePolicyID):
                res = True
                rtePolicyID_ = _EFwRtePolicyID._FromFwRtePolicyID(rtePolicyID_)
            res = res and _EBitMask.IsEnumBitFlagSet(self.__bm, rtePolicyID_)
        return res
