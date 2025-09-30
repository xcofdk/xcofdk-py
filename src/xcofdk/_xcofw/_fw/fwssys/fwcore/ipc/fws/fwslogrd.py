# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwslogrd.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from threading import RLock as _PyRLock
from typing    import List

from _fw.fwssys.fwcore.logging                   import vlogif
from _fw.fwssys.fwcore.base.timeutil             import _TimeAlert
from _fw.fwssys.fwcore.base.gtimeout             import _Timeout
from _fw.fwssys.fwcore.logrd.iflogrdsrv          import _ILogRDService
from _fw.fwssys.fwcore.logrd.logrecord           import _ELRType
from _fw.fwssys.fwcore.logrd.logrecord           import _LogRecord
from _fw.fwssys.fwcore.logrd.rdsinks.tcpsink     import _TCPSink
from _fw.fwssys.fwcore.logrd.rdsinks.filesink    import _FileSink
from _fw.fwssys.fwcore.logrd.rdsinks.consolesink import _ConsoleSink
from _fw.fwssys.fwcore.ipc.fws.afwservice        import _AbsFwService
from _fw.fwssys.fwcore.ipc.net.tcpsocket         import _TCPSocket
from _fw.fwssys.fwcore.ipc.net.tcpsocket         import _TCPListenerSocket
from _fw.fwssys.fwcore.ipc.tsk.taskdefs          import _ERblType
from _fw.fwssys.fwcore.ipc.tsk.taskxcard         import _TaskXCard
from _fw.fwssys.fwcore.ipc.tsk.fwtaskprf         import _FwTaskProfile
from _fw.fwssys.fwcore.ipc.tsk.taskutil          import _ETaskRightFlag
from _fw.fwssys.fwcore.types.commontypes         import override
from _fw.fwssys.fwerrh.fwerrorcodes              import _EFwErrorCode
from _fwa.fwrtecfg.fwrteconfig                   import _FwRteConfig

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _FwsLogRD(_AbsFwService, _ILogRDService):
    __slots__ = [ '__l' , '__as' , '__fa', '__lt', '__ts' , '__bPF' ]

    __tbl    = None
    __bHL    = True
    __sgltn  = None
    __tskPrf = None

    def __init__(self):
        self.__l   = None
        self.__as  = None
        self.__fa  = None
        self.__lt  = None
        self.__ts  = None
        self.__bPF = None
        _ILogRDService.__init__(self)

        if _FwsLogRD.__sgltn is not None:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00984)
            return

        _FreqMS  = 50
        _MaxpMS  = 50
        _CeaseMS = 20
        _xc = _TaskXCard(runPhaseFreqMS_=_FreqMS, runPhaseMPTMS_=_MaxpMS, cceaseFreqMS_=_CeaseMS)

        _t = _Timeout.CreateTimeoutSec(3)
        _a = _TimeAlert(_t.toNSec)
        _t.CleanUp()

        _AbsFwService.__init__(self, _ERblType.eFwLogRDRbl, runLogAlert_=_a, txCard_=_xc)
        _xc.CleanUp()

        if self._rblType is None:
            self.CleanUp()
            return

        _t = _Timeout.CreateTimeoutMS(200)
        _a = _TimeAlert(_t.toNSec)
        _t.CleanUp()

        self.__l   = _PyRLock()
        self.__fa  = _a
        self.__as  = []
        self.__lt  = _ELRType.LR_FREE
        self.__bPF = False

    @override
    def _AddLR(self, logRec_ : _LogRecord):
        with self.__l:
            if logRec_._recType.isError and not self.__lt.isError:
                self.__lt = logRec_._recType

            for _ss in self.__as:
                _ss.AddLR(logRec_)
                if not _ss.isActiveSink:
                    continue
                if self.__lt.isFatal or self.__bPF:
                    _ss.Flush()

    @override
    def _FlushBacklog(self, backlog_ : List[_LogRecord], bHLEnabled_ : bool):
        with self.__l:
            _rteCfg = _FwRteConfig._GetInstance()
            if not _rteCfg._isLogRDConsoleSinkDisabled:
                self.__as.append(_ConsoleSink(bHLEnabled_=bHLEnabled_))
            if _rteCfg._isLogRDFileSinkEnabled:
                self.__as.append(_FileSink(_rteCfg._rdFileSinkConfig.pyLogger))
            if _rteCfg._isLogRDTcpSinkEnabled:
                self.__ts = _TCPSink(terminator_=_rteCfg._rdTcpSinkConfig.lineEnding)
                self.__as.append(self.__ts)

            for _ss in self.__as:
                if not _ss.isActiveSink:
                    for _rr in backlog_:
                        _ss.AddLR(_rr)
                    continue
                _lt = _ss.Flush(backlog_)
                if _lt.isError and not self.__lt.isError:
                    self.__lt = _lt

    @override
    def _EnablePM(self):
        self.__EnablePM()

    @staticmethod
    def _GetInstance(bCreate_ =False):
        res = _FwsLogRD.__sgltn

        if res is not None:
            return res
        if not bCreate_:
            return None

        res = _FwsLogRD()
        if res._rblType is None:
            res.CleanUp()
            return None

        _trm = _ETaskRightFlag.FwTaskRightDefaultMask()
        _ta  = { _FwTaskProfile._ATTR_KEY_RUNNABLE : res , _FwTaskProfile._ATTR_KEY_TASK_RIGHTS : _trm }
        _tp  = _FwTaskProfile(tpAttrs_=_ta)

        if not _tp.isValid:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00985)
            _tp.CleanUp()
            res.CleanUp()
            res = None
        else:
            _FwsLogRD.__sgltn  = res
            _FwsLogRD.__tskPrf = _tp
        return res

    def _ToString(self, bVerbose_ =False, annex_ : str =None):
        if self._isInvalid:
            return None
        annex_ = _FwTDbEngine.GetText(_EFwTextID.eFwsLogRD_ToString_001).format(_FwsLogRD.__bHL)
        return _AbsFwService._ToString(self, bVerbose_, annex_)

    def _CleanUp(self):
        if _FwsLogRD.__sgltn is None:
            return
        _FwsLogRD.__sgltn = None

        if _FwsLogRD.__tskPrf is not None:
            _FwsLogRD.__tskPrf.CleanUp()
            _FwsLogRD.__tskPrf = None

        self.__fa = None
        _AbsFwService._CleanUp(self)

    def _TearDownExecutable(self):
        with self.__l:
            self.__EnablePM()
            return self.isRunning

    def _RunExecutable(self):
        with self.__l:
            if not self.isRunning:
                self.__EnablePM()
                return False

            _bC = (self.__ts is not None) and not self.__ts.isActiveSink

            _bF = True if self.__lt.isError else self.__fa.CheckAlert()
            if _bF:
                for _ss in self.__as:
                    if not _ss.isActiveSink:
                        continue
                    _ss.Flush()
            if not self.__lt.isFatal:
                self.__lt = _ELRType.LR_FREE

            if _bC:
                _ss = self.__CreateSocket()
                if _ss is not None:
                    self.__ts._SetSocket(_ss)
                    self.__ts.Flush()
            return self.isRunning

    def __CreateSocket(self) -> _TCPSocket:
        _tcpCfg = _FwRteConfig._GetInstance()._rdTcpSinkConfig
        _ls = _TCPListenerSocket(ip_=_tcpCfg.ip, port_=_tcpCfg.port, timeout_=_TCPListenerSocket._DEFAULT_LISTENER_TIMEOUT)
        res = _ls._Listen()
        _ls._CleanUp()
        return res

    def __EnablePM(self):
        if self.__bPF:
            return

        self.__bPF = True
        for _ss in self.__as:
            if not _ss.isActiveSink:
                continue
            _ss.Flush()

    pass
