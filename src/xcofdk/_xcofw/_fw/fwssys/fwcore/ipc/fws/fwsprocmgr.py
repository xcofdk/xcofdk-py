# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwsprocmgr.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from typing import List
from typing import Union

from _fw.fwssys.assys.ifs                 import _IFwsProcMgr
from _fw.fwssys.assys.ifs                 import _IXProcAgent
from _fw.fwssys.assys.ifs                 import _IXProcConn
from _fw.fwssys.fwcore.logging            import logif
from _fw.fwssys.fwcore.logging            import vlogif
from _fw.fwssys.fwcore.base.timeutil      import _TimeAlert
from _fw.fwssys.fwcore.base.gtimeout      import _Timeout
from _fw.fwssys.fwcore.ipc.fws.afwservice import _AbsFwService
from _fw.fwssys.fwcore.ipc.sync.mutex     import _Mutex
from _fw.fwssys.fwcore.ipc.tsk.taskdefs   import _ERblType
from _fw.fwssys.fwcore.ipc.tsk.taskxcard  import _TaskXCard
from _fw.fwssys.fwcore.ipc.tsk.fwtaskprf  import _FwTaskProfile
from _fw.fwssys.fwcore.ipc.tsk.taskutil   import _ETaskRightFlag
from _fw.fwssys.fwcore.types.aobject      import _AbsSlotsObject
from _fw.fwssys.fwerrh.fwerrorcodes       import _EFwErrorCode

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _FwsProcMgr(_AbsFwService, _IFwsProcMgr):
    class _ProcEntry(_AbsSlotsObject):
        __slots__ = [ '__xpa' ]

        def __init__(self, xpa_ : _IXProcAgent):
            super().__init__()
            self.__xpa = xpa_

        @property
        def _xpAgent(self) -> _IXProcAgent:
            return self.__xpa

        def _ToString(self):
            pass

        def _CleanUp(self):
            self.__xpa = None

    __slots__ = [ '__ma' , '__md' ]

    __tbl    = None
    __sgltn  = None
    __tskPrf = None

    def __init__(self):
        self.__ma = None
        self.__md = None
        _IFwsProcMgr.__init__(self)

        if _FwsProcMgr.__sgltn is not None:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00951)
            return

        _FreqMS  = 40
        _CeaseMS = 20
        _xc = _TaskXCard(runPhaseFreqMS_=_FreqMS, cceaseFreqMS_=_CeaseMS)

        _t = _Timeout.CreateTimeoutSec(3)
        _a = _TimeAlert(_t.toNSec)
        _t.CleanUp()

        _AbsFwService.__init__(self, _ERblType.eFwProcMgrRbl, runLogAlert_=_a, txCard_=_xc)
        _xc.CleanUp()

        if self._rblType is None:
            self.CleanUp()
            return

        self.__ma = _Mutex()
        self.__md = _Mutex()

    @staticmethod
    def _GetInstance(bCreate_ =False):
        res = _FwsProcMgr.__sgltn

        if res is not None:
            return res
        if not bCreate_:
            return None

        res = _FwsProcMgr()
        if res._rblType is None:
            res.CleanUp()
            return None

        _trm = _ETaskRightFlag.FwTaskRightDefaultMask()
        _ta  = { _FwTaskProfile._ATTR_KEY_RUNNABLE : res , _FwTaskProfile._ATTR_KEY_TASK_RIGHTS : _trm }
        _tp  = _FwTaskProfile(tpAttrs_=_ta)

        if not _tp.isValid:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00952)
            _tp.CleanUp()
            res.CleanUp()
            res = None
        else:
            _FwsProcMgr.__sgltn  = res
            _FwsProcMgr.__tskPrf = _tp
        return res

    def _ToString(self, bVerbose_ =False, annex_ : str =None):
        if self._isInvalid:
            return None
        return _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_005).format(self._fwSID.compactName, len(_FwsProcMgr.__GetTable()))

    def _CleanUp(self):
        if _FwsProcMgr.__sgltn is None:
            return

        _FwsProcMgr.__sgltn = None

        if _FwsProcMgr.__tskPrf is not None:
            _FwsProcMgr.__tskPrf.CleanUp()
            _FwsProcMgr.__tskPrf = None

        _mtx = self.__ma
        if _mtx is not None:
            with _mtx:
                self.__ma = None

                self.__md.CleanUp()
                self.__md = None
    
            _mtx.CleanUp()

        _AbsFwService._CleanUp(self)

    def _TearDownExecutable(self):
        _tbl = _FwsProcMgr.__GetTable()
        for _vv in _tbl.values():
            if _vv._xpAgent is not None:
                _vv._DetachFromFW()
            _vv.CleanUp()
        _tbl.clear()
        _FwsProcMgr.__tbl = None
        return self.isRunning

    def _RunExecutable(self):
        with self.__md:
            _tbl = _FwsProcMgr.__GetTable()
            _rm  = _FwsProcMgr.__GetProcEntryList(bRemovableOnly_=True)
            for _kk in _rm:
                _tbl.pop(_kk)

        return self.isRunning

    def _AddProcess(self, xprocConn_ : _IXProcConn, puid_ : int) -> bool:
        if not self.isRunning:
            return False

        if self._PcHasLcAnyFailureState():
            logif._LogErrorEC(_EFwErrorCode.UE_00237, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwsProcMgr_TID_001))
            return False

        if self._PcIsLcMonShutdownEnabled():
            logif._LogErrorEC(_EFwErrorCode.UE_00238, _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwsProcMgr_TID_001))
            return False

        if not self._PcIsLcProxyModeNormal():
            return False
        if not (isinstance(xprocConn_, _IXProcConn) and (xprocConn_._xprocessAgent is not None) and isinstance(puid_, int) and (puid_<0)):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00962)
            return False

        with self.__ma:
            with self.__md:
                xprocConn_._PcSetLcProxy(self._PcGetLcProxy())
                xprocConn_._ConfirmPUID()

                _tbl = _FwsProcMgr.__GetTable()
                _tbl[-1*puid_] = _FwsProcMgr._ProcEntry(xprocConn_._xprocessAgent)
                return True

    def _GetJoinableList(self, lstPIDs_ : list =None) -> Union[List[_IXProcAgent], None]:
        if not self.isRunning:
            return None
        if self._PcHasLcAnyFailureState():
            return None
        if self._PcIsLcMonShutdownEnabled():
            return None

        with self.__md:
            res      = []
            _tbl     = _FwsProcMgr.__GetTable()
            _lst     = _FwsProcMgr.__GetProcEntryList(bJoiniableOnly_=True)
            _lstAvbl = []
            for _kk in _lst:
                _xpa = _tbl[_kk]._xpAgent
                _pid = _xpa._xprocessPID
                if _pid is None:
                    continue
                if (lstPIDs_ is not None) and _pid not in lstPIDs_:
                    continue

                _lstAvbl.append(_pid)
                res.append(_xpa)
        return res

    @staticmethod
    def __GetTable():
        res = _FwsProcMgr.__tbl
        if res is None:
            res = dict()
            _FwsProcMgr.__tbl = res
        return res

    @staticmethod
    def __GetProcEntryList(bRemovableOnly_ =False, bJoiniableOnly_ =False) -> List[int]:
        res = []

        _tbl = _FwsProcMgr.__GetTable()
        for _kk, _vv in _tbl.items():
            _xpa = _vv._xpAgent
            if _xpa is None:
                if bRemovableOnly_:
                    res.append(_kk)
                continue

            _bAttached = _xpa._isAttachedToFW
            if (not _bAttached) or _xpa._isTerminated:
                if bRemovableOnly_:
                    res.append(_kk)
            elif _bAttached and _xpa._isStarted:
                if bJoiniableOnly_:
                    res.append(_kk)
                continue
        return res
