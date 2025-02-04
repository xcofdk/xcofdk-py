# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : ssdipc.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from xcofdk._xcofw.fw.fwssys.fwcore.logging                  import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.apiimpl.fwapiimplshare   import _FwApiImplShare
from xcofdk._xcofw.fw.fwssys.fwcore.apiimpl.fwapiconnap      import _FwApiConnectorAP
from xcofdk._xcofw.fw.fwssys.fwcore.apiimpl.xtask.xtaskconn  import _XTaskConnector
from xcofdk._xcofw.fw.fwssys.fwcore.config.ssysconfig.sscipc import _SSConfigIPC
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.arunnablefwc     import _AbstractRunnableFWC
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.sync.syncresbase     import _SyncResourceBase
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.sync.syncresbase     import _SyncResourcesGuard
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.arunnabledefs    import _EFwcID
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.execprofile      import _ExecutionProfile
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskmgr          import _TaskMgr
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskmgrimpl      import _TaskManagerImpl
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil         import _TaskUtil
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil         import _StartupThread
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil         import _AutoEnclosedThreadsBag
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcssysdeputy          import _ESubSysID
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcssysdeputy          import _ELcScope
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcssysdeputy          import _LcSSysDeputy
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcssysdeputy          import _FwSSysConfigBase
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes        import _FwIntEnum

from xcofdk._xcofw.fw.fwssys.fwmsg.disp.dispatchregistry import _MessageClusterMap

from xcofdk._xcofw.fw.fwssys.fwerrh.fwerrorcodes import _EFwErrorCode

from xcofdk._xcofwa.fwadmindefs import _FwSubsystemCoding

class _SSDeputyIPC(_LcSSysDeputy):
    __slots__ = []

    def __init__(self, ppass_ : int):
        super().__init__(ppass_, _ESubSysID.eIPC, _ELcScope.eFullIPC)

    def _CleanUpByOwnerRequest(self):
        _LcSSysDeputy._CleanUpByOwnerRequest(self)

    def _ProcDeputyCmd(self, tgtScope_ : _ELcScope, deputyCmd_ : _FwIntEnum, subsysCfg_ : _FwSSysConfigBase) -> bool:

        if not isinstance(deputyCmd_, _LcSSysDeputy._EDDeputyCmd):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00057)
            return False
        elif not isinstance(subsysCfg_, _SSConfigIPC):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00058)
            return False
        elif deputyCmd_.isReInject:
            return True

        res = True
        for name, member in _SSConfigIPC._EIpcConfigEntityID.__members__.items():
            if _SSDeputyIPC.__IsRequestIgnorable(tgtScope_, deputyCmd_, member):
                continue

            if member==_SSConfigIPC._EIpcConfigEntityID.eAbstractRunnableFWC__CleanFwcTable:
                if deputyCmd_.isDeInject:
                    _AbstractRunnableFWC._CleanUpFwcTable()

            elif member==_SSConfigIPC._EIpcConfigEntityID.eMessageClusterMap__CleanMap:
                if deputyCmd_.isDeInject:
                    _MessageClusterMap._CleanClusterMap()

            elif member==_SSConfigIPC._EIpcConfigEntityID.eAbstractRunnableFWC__DefineFwcTable:
                if deputyCmd_.isInject:
                    _AbstractRunnableFWC._CleanUpFwcTable()

                    _lstCID = [ _EFwcID.eFwMain ]

                    if _FwSubsystemCoding.IsSubsystemMessagingConfigured():
                        _lstCID.append(_EFwcID.eFwDispatcher)

                    _AbstractRunnableFWC._DefineFwcTable(lstFwcIDs_=_lstCID)

            elif member == _SSConfigIPC._EIpcConfigEntityID.eSyncResourcesGuard__Singleton:
                _SyncResourceBase._SetSyncResGuardConfig(subsysCfg_.isSyncResourceGuardEnabled)
                if not subsysCfg_.isSyncResourceGuardEnabled:
                    pass 
                elif deputyCmd_.isDeInject:
                    _srg = _SyncResourcesGuard._GetInstance()
                    if _srg is not None:
                        _srg.CleanUp()
                else:
                    _srg = _SyncResourcesGuard._CreateInstance()
                    if _srg is None:
                        _srg = False
                        vlogif._LogOEC(True, _EFwErrorCode.VFE_00059)
                        break

            elif member == _SSConfigIPC._EIpcConfigEntityID.eTaskID__Defines:
                _TaskUtil._SetUp(deputyCmd_.isInject)

            elif member == _SSConfigIPC._EIpcConfigEntityID.eExecutionProfile__LcMonitorRunCycle:
                if deputyCmd_.isDeInject:
                    _ExecutionProfile._SetLcMonitorCyclicRunPauseTimespanMS(None)
                else:
                    _ts = subsysCfg_.lcMonCyclicRunPauseTimespanMS
                    _ExecutionProfile._SetLcMonitorCyclicRunPauseTimespanMS(_ts)

            elif member == _SSConfigIPC._EIpcConfigEntityID.eAutoEnclosedThreadsBag:
                _AutoEnclosedThreadsBag._SetUp(deputyCmd_.isInject)

            elif member == _SSConfigIPC._EIpcConfigEntityID.eStartupThread__Singleton:
                if deputyCmd_.isDeInject:
                    _StartupThread.GetInstance()._Update(freezeUpdate_=None)
                else:
                    _StartupThread.GetInstance()._Update(freezeUpdate_=True)

            elif member == _SSConfigIPC._EIpcConfigEntityID.eTaskManager__Singleton:
                if deputyCmd_.isDeInject:
                    if _TaskMgr() is not None:
                        _TaskMgr().CleanUp()
                elif _TaskMgr() is None:
                    _tmgrImpl = _TaskManagerImpl()
                    res = _TaskMgr() is not None
                    if not res:
                        _tmgrImpl.CleanUp()
                        break

            elif member == _SSConfigIPC._EIpcConfigEntityID.eXTaskConn__PRFC:
                if deputyCmd_.isFinalize:
                    _ak = hash(str(_XTaskConnector._SetPRFC))
                    _XTaskConnector._SetPRFC(_ak, None)
                elif deputyCmd_.isDeInject:
                    pass
                elif tgtScope_.isSemiIPC:
                    _ak = hash(str(_XTaskConnector._SetPRFC))
                    res = _XTaskConnector._SetPRFC(_ak, _TaskManagerImpl)
                    if not res:
                        break

            elif member == _SSConfigIPC._EIpcConfigEntityID.eFwApi__ConnAccessLock:
                _FwApiConnectorAP._APUnsetConnAccessLock()

            elif member == _SSConfigIPC._EIpcConfigEntityID.eFwApiImplShare__AccessLock:
                if deputyCmd_.isInject:
                    _FwApiImplShare._Reset()

            else:
                res = False
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00060)
                break
        return res

    @staticmethod
    def __IsRequestIgnorable(tgtScope_ : _ELcScope, deputyCmd_ : _FwIntEnum, configEntityID_ : _SSConfigIPC._EIpcConfigEntityID):
        lst_PRE_IPC_RELEVANT_CFG_ENTITIES = [
            _SSConfigIPC._EIpcConfigEntityID.eFwApi__ConnAccessLock
          , _SSConfigIPC._EIpcConfigEntityID.eFwApiImplShare__AccessLock
        ]
        lst_SEMI_IPC_RELEVANT_CFG_ENTITIES = [
            _SSConfigIPC._EIpcConfigEntityID.eSyncResourcesGuard__Singleton
          , _SSConfigIPC._EIpcConfigEntityID.eTaskManager__Singleton
          , _SSConfigIPC._EIpcConfigEntityID.eTaskID__Defines
          , _SSConfigIPC._EIpcConfigEntityID.eExecutionProfile__LcMonitorRunCycle
          , _SSConfigIPC._EIpcConfigEntityID.eAutoEnclosedThreadsBag
          , _SSConfigIPC._EIpcConfigEntityID.eStartupThread__Singleton
          , _SSConfigIPC._EIpcConfigEntityID.eAbstractRunnableFWC__DefineFwcTable
          , _SSConfigIPC._EIpcConfigEntityID.eXTaskConn__PRFC
        ]
        lstSEMI_FULL_RELEVANT_CFG_ENTITIES = [
            _SSConfigIPC._EIpcConfigEntityID.eAbstractRunnableFWC__CleanFwcTable
          , _SSConfigIPC._EIpcConfigEntityID.eMessageClusterMap__CleanMap
          , _SSConfigIPC._EIpcConfigEntityID.eXTaskConn__PRFC
        ]

        res = False

        if configEntityID_ in lst_PRE_IPC_RELEVANT_CFG_ENTITIES:
            if not deputyCmd_.isInject:
                res = True
            elif not tgtScope_.isPreIPC:
                res = True
            else:
                res = False

        elif configEntityID_ in lst_SEMI_IPC_RELEVANT_CFG_ENTITIES:
            if deputyCmd_.isFinalize:
                if tgtScope_.isSemiIPC:
                    res = configEntityID_ != _SSConfigIPC._EIpcConfigEntityID.eXTaskConn__PRFC
                else:
                    res = True
            elif deputyCmd_.isInject and not tgtScope_.isSemiIPC:
                res = True
            elif deputyCmd_.isDeInject and not tgtScope_.isPreIPC:
                res = True

        elif configEntityID_ in lstSEMI_FULL_RELEVANT_CFG_ENTITIES:
            if deputyCmd_.isFinalize:
                if tgtScope_.isFullIPC:
                    res = configEntityID_ != _SSConfigIPC._EIpcConfigEntityID.eXTaskConn__PRFC
                else:
                    res = True
            elif deputyCmd_.isInject and not tgtScope_.isFullIPC:
                res = True
            elif deputyCmd_.isDeInject and not tgtScope_.isSemiIPC:
                res = True

        return res
