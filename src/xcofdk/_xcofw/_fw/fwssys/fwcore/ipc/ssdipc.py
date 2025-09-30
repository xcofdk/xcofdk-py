# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : ssdipc.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from _fw.fwssys.assys                        import fwsubsysshare as _ssshare
from _fw.fwssys.assys.fwsubsysshare          import _FwSubsysShare
from _fw.fwssys.fwcore.logging               import vlogif
from _fw.fwssys.fwctrl.fwapiconnap           import _FwApiConnectorAP
from _fw.fwssys.fwcore.config.ssyscfg.sscipc import _SSConfigIPC
from _fw.fwssys.fwcore.ipc.fws.afwservice    import _AbsFwService
from _fw.fwssys.fwcore.ipc.sync.syncresbase  import _SyncResourceBase
from _fw.fwssys.fwcore.ipc.sync.syncresbase  import _SyncResourcesGuard
from _fw.fwssys.fwcore.ipc.tsk.taskdefs      import _EFwsID
from _fw.fwssys.fwcore.ipc.tsk.taskxcard     import _TaskXCard
from _fw.fwssys.fwcore.ipc.tsk.taskmgrimpl   import _TaskMgrImpl
from _fw.fwssys.fwcore.ipc.tsk.taskutil      import _TaskUtil
from _fw.fwssys.fwcore.ipc.tsk.taskutil      import _StartupThread
from _fw.fwssys.fwcore.ipc.tsk.taskutil      import _AutoEnclosedThreadsBag
from _fw.fwssys.fwcore.lc.lcxstate           import _LcFailure
from _fw.fwssys.fwcore.lc.lcssysdeputy       import _ESubSysID
from _fw.fwssys.fwcore.lc.lcssysdeputy       import _ELcScope
from _fw.fwssys.fwcore.lc.lcssysdeputy       import _LcSSysDeputy
from _fw.fwssys.fwcore.lc.lcssysdeputy       import _FwSSysConfigBase
from _fw.fwssys.fwcore.types.commontypes     import _EDepInjCmd
from _fw.fwssys.fwmsg.disp.dispregistry      import _MessageClusterMap
from _fw.fwssys.fwerrh.fwerrorcodes          import _EFwErrorCode
from _fw.fwssys.fwmp.fwrte.fwrtetmgr         import _FwRteTokenMgr as _RteTMgr
from _fw.fwssys.fwmp.xprocessconn            import _XProcessConn
from _fw.fwssys.fwmt.utask.usertaskconn      import _UserTaskConn

class _SSDeputyIPC(_LcSSysDeputy):
    __slots__ = []

    __lstPre  = None
    __lstSemi = None
    __lstFull = None

    def __init__(self, ppass_ : int):
        super().__init__(ppass_, _ESubSysID.eIPC, _ELcScope.eFullIPC)
        _SSDeputyIPC.__SetUp()

    def _CleanUpByOwnerRequest(self):
        _LcSSysDeputy._CleanUpByOwnerRequest(self)

    def _ProcDeputyCmd(self, tgtScope_ : _ELcScope, dinjCmd_ : _EDepInjCmd, subsysCfg_ : _FwSSysConfigBase) -> bool:
        if not isinstance(dinjCmd_, _EDepInjCmd):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00057)
            return False
        elif not isinstance(subsysCfg_, _SSConfigIPC):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00058)
            return False
        elif dinjCmd_.isReInject:
            return True

        res, _mem = True, None
        for _n, _m in _SSConfigIPC._EIpcConfigEntityID.__members__.items():
            if not res:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00954)
                break

            if not _SSDeputyIPC.__CheckDeputyCmd(tgtScope_, dinjCmd_, _m):
                continue

            _mem = _SSConfigIPC._EIpcConfigEntityID(_m.value)

            if _m == _SSConfigIPC._EIpcConfigEntityID.eMessageClusterMap__CleanMap:
                if dinjCmd_.isDeInject:
                    _MessageClusterMap._DepInjection(dinjCmd_)

            elif _m == _SSConfigIPC._EIpcConfigEntityID.eAbsFwService__CleanFwsTable:
                if dinjCmd_.isDeInject:
                    _AbsFwService._DepInjection(dinjCmd_, None, None)
            elif _m == _SSConfigIPC._EIpcConfigEntityID.eAbsFwService__DefineFwsTable:
                if dinjCmd_.isInject:
                    _AbsFwService._DepInjection(_EDepInjCmd.eDeInject, None, None)

                    _lstCID = [ _EFwsID.eFwsMain ]

                    if _ssshare._IsLogRDActiveServiceRequired():
                        _lstCID.append(_EFwsID.eFwsLogRD)
                    if not _ssshare._IsSubsysMsgDisabled():
                        _lstCID.append(_EFwsID.eFwsDisp)
                    if not _ssshare._IsSubsysMPDisabled():
                        _lstCID.append(_EFwsID.eFwsProcMgr)
                    _AbsFwService._DepInjection(dinjCmd_, None, _lstCID)

            elif _m == _SSConfigIPC._EIpcConfigEntityID.eSyncResourcesGuard__Singleton:
                _bEnabled = subsysCfg_.isSyncResourceGuardEnabled
                if dinjCmd_.isInject:
                    _SyncResourceBase._DepInjection(dinjCmd_, _bEnabled)
                if _bEnabled:
                    res = _SyncResourcesGuard._DepInjection(dinjCmd_)

            elif _m == _SSConfigIPC._EIpcConfigEntityID.eTaskID__Defines:
                _TaskUtil._DepInjection(dinjCmd_)

            elif _m == _SSConfigIPC._EIpcConfigEntityID.eExecutionProfile__LcMonitorRunCycle:
                if dinjCmd_.isDeInject:
                    _TaskXCard._DepInjection(dinjCmd_)
                else:
                    _ts = subsysCfg_.lcMonCyclicRunPauseTimespanMS
                    _TaskXCard._DepInjection(dinjCmd_, _ts)

            elif _m == _SSConfigIPC._EIpcConfigEntityID.eAutoEnclosedThreadsBag:
                _AutoEnclosedThreadsBag._DepInjection(dinjCmd_)

            elif _m == _SSConfigIPC._EIpcConfigEntityID.eStartupThread__Singleton:
                if dinjCmd_.isDeInject:
                    _StartupThread._DepInjection(dinjCmd_)
                else:
                    _StartupThread._DepInjection(dinjCmd_, bFreezeUpdate_=True)

            elif _m == _SSConfigIPC._EIpcConfigEntityID.eTaskManager__Singleton:
                res = _TaskMgrImpl._DepInjection(dinjCmd_)

            elif _m == _SSConfigIPC._EIpcConfigEntityID.eXTaskConn__PRFC:
                _ak = hash(str(_UserTaskConn.__init__))
                if dinjCmd_.isFinalize or dinjCmd_.isDeInject:
                    res = _UserTaskConn._DepInjection(dinjCmd_, _ak, None)
                else:
                    res = _UserTaskConn._DepInjection(dinjCmd_, _ak, _TaskMgrImpl)

            elif _m == _SSConfigIPC._EIpcConfigEntityID.eXProcConn__PMI:
                _ak = hash(str(_XProcessConn.__init__))
                if dinjCmd_.isDeInject:
                    res = _RteTMgr._DepInjection(dinjCmd_)
                    res = res and _XProcessConn._DepInjection(dinjCmd_, _ak, None)
                else:
                    _pmi = _AbsFwService._DepInjection(_EDepInjCmd.eDontCare, _EFwsID.eFwsProcMgr, None)
                    res = _RteTMgr._DepInjection(dinjCmd_, bXcpTrackingDisabled_=_ssshare._IsSubsysMPXcpTrackingDisabled())
                    res = res and _XProcessConn._DepInjection(dinjCmd_, _ak, pmi_=_pmi)

            elif _m == _SSConfigIPC._EIpcConfigEntityID.eFwApi__ConnAccessLock:
                _FwApiConnectorAP._DepInjection(dinjCmd_)

            elif _m == _SSConfigIPC._EIpcConfigEntityID.eFwApiImplShare__AccessLock:
                _FwSubsysShare._DepInjection(dinjCmd_)

            elif _m == _SSConfigIPC._EIpcConfigEntityID.eLcFailure__LcResultSilentMode:
                _LcFailure._DepInjection(dinjCmd_, subsysCfg_.fwStartupConfig._isSilentFwLogLevel)

            else:
                res = False
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00060)
                break
        return res

    @staticmethod
    def __SetUp():
        if _SSDeputyIPC.__lstPre is not None:
            return

        _SSDeputyIPC.__lstPre = [
            _SSConfigIPC._EIpcConfigEntityID.eFwApi__ConnAccessLock
          , _SSConfigIPC._EIpcConfigEntityID.eFwApiImplShare__AccessLock
          , _SSConfigIPC._EIpcConfigEntityID.eLcFailure__LcResultSilentMode

        ]

        _SSDeputyIPC.__lstSemi = [
            _SSConfigIPC._EIpcConfigEntityID.eSyncResourcesGuard__Singleton
          , _SSConfigIPC._EIpcConfigEntityID.eTaskManager__Singleton
          , _SSConfigIPC._EIpcConfigEntityID.eTaskID__Defines
          , _SSConfigIPC._EIpcConfigEntityID.eExecutionProfile__LcMonitorRunCycle
          , _SSConfigIPC._EIpcConfigEntityID.eAutoEnclosedThreadsBag
          , _SSConfigIPC._EIpcConfigEntityID.eStartupThread__Singleton
          , _SSConfigIPC._EIpcConfigEntityID.eAbsFwService__DefineFwsTable
          , _SSConfigIPC._EIpcConfigEntityID.eXTaskConn__PRFC

        ]

        _SSDeputyIPC.__lstFull = [
            _SSConfigIPC._EIpcConfigEntityID.eAbsFwService__CleanFwsTable
          , _SSConfigIPC._EIpcConfigEntityID.eMessageClusterMap__CleanMap
          , _SSConfigIPC._EIpcConfigEntityID.eXProcConn__PMI
        ]

    @staticmethod
    def __CheckDeputyCmd(tgtScope_ : _ELcScope, dinjCmd_ : _EDepInjCmd, cfgItem_ : _SSConfigIPC._EIpcConfigEntityID):
        res = False

        if cfgItem_ in _SSDeputyIPC.__lstPre:
            if not tgtScope_.isPreIPC:
                res = True
            elif dinjCmd_.isDeInject:
                res = cfgItem_ != _SSConfigIPC._EIpcConfigEntityID.eFwApiImplShare__AccessLock

            elif not dinjCmd_.isInject:
                res = True

        elif cfgItem_ in _SSDeputyIPC.__lstSemi:
            if dinjCmd_.isFinalize:
                if tgtScope_.isSemiIPC:
                    res = cfgItem_ != _SSConfigIPC._EIpcConfigEntityID.eXTaskConn__PRFC
                else:
                    res = True
            elif dinjCmd_.isInject:
                res = not tgtScope_.isSemiIPC
            elif dinjCmd_.isDeInject:
                res = not tgtScope_.isPreIPC

        elif cfgItem_ in _SSDeputyIPC.__lstFull:
            if _ssshare._IsSubsysMPDisabled() and (cfgItem_ == _SSConfigIPC._EIpcConfigEntityID.eXProcConn__PMI):
                res = True
            elif dinjCmd_.isFinalize:
                if not tgtScope_.isFullIPC:
                    res = True
                else:
                    res = cfgItem_ != _SSConfigIPC._EIpcConfigEntityID.eXProcConn__PMI
            elif dinjCmd_.isInject:
                if not tgtScope_.isFullIPC:
                    res = True
                else:
                    res = cfgItem_ == _SSConfigIPC._EIpcConfigEntityID.eXProcConn__PMI
            elif dinjCmd_.isDeInject and not tgtScope_.isSemiIPC:
                res = True

        return not res
