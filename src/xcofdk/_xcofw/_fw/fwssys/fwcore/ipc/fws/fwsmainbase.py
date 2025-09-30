# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwsmainbase.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from _fw.fwssys.fwcore.logging            import vlogif
from _fw.fwssys.fwcore.base.gtimeout      import _Timeout
from _fw.fwssys.fwcore.base.util          import _Util
from _fw.fwssys.fwcore.base.timeutil      import _TimeAlert
from _fw.fwssys.fwcore.ipc.tsk.taskdefs   import _EFwsID
from _fw.fwssys.fwcore.ipc.tsk.taskdefs   import _ERblType
from _fw.fwssys.fwcore.ipc.tsk.taskxcard  import _TaskXCard
from _fw.fwssys.fwcore.ipc.fws.fwsdisp    import _FwsDispatcher
from _fw.fwssys.fwcore.ipc.fws.fwslogrd   import _FwsLogRD
from _fw.fwssys.fwcore.ipc.fws.fwsprocmgr import _FwsProcMgr
from _fw.fwssys.fwcore.ipc.rbl.arunnable  import _AbsRunnable
from _fw.fwssys.fwcore.ipc.fws.afwservice import _AbsFwService
from _fw.fwssys.fwcore.ipc.rbl.arbldefs   import _ERblApiID
from _fw.fwssys.fwcore.types.aobject      import _AbsSlotsObject
from _fw.fwssys.fwcore.types.commontypes  import _CommonDefines
from _fw.fwssys.fwerrh.fwerrorcodes       import _EFwErrorCode

class _FwsMainBase(_AbsFwService):
    __slots__ = [ '_md' , '__dc' , '__bA' ]

    __mcamn = [ _ERblApiID.ePrepareCeasing.functionName
              , _ERblApiID.eRunCeaseIteration.functionName
              , _ERblApiID.eProcFwcErrorHandlerCallback.functionName
              , _ERblApiID.eOnRunProgressNotification.functionName
              ]

    def __init__(self):
        _AbsSlotsObject.__init__(self)

        self._md  = None
        self.__bA = None
        self.__dc = None

        if not ((_AbsFwService.GetDefinedFwsNum() > 0) and _AbsFwService.IsDefinedFws(_EFwsID.eFwsMain, bWarn_=True)):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00067)
            return

        _mmn = _FwsMainBase.GetMCApiMNL()
        if _Util.GetNumAttributes(self, _mmn, bThrowx_=True) != len(_mmn):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00068)
            return

        _tout     = _Timeout.CreateTimeoutSec(3)
        _logAlert = _TimeAlert(_tout.toNSec)
        _tout.CleanUp()

        _xc = _TaskXCard(bLcMonitor_=True)

        _AbsFwService.__init__(self, _ERblType.eFwMainRbl, rblXM_=None, runLogAlert_=_logAlert, txCard_=_xc)
        _xc.CleanUp()

        _mtxDataMe = _AbsRunnable._GetDataMutex(self)
        if (self._rblType is None) or (_mtxDataMe is None):
            self.CleanUp()
        elif not self.__CreateFWSs():
            self.__CleanUpFWSs()
            self.CleanUp()

        if self._rblType != _ERblType.eFwMainRbl:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00069)
            return
        self._md = _mtxDataMe

    def _StartFWCs(self):
        return self.__StartFWSs()

    def _ToString(self, bVerbose_ =False, annex_ : str =None):
        return _AbsFwService._ToString(self, bVerbose_, annex_)

    def _CleanUp(self):
        super()._CleanUp()
        self._md  = None
        self.__bA = None
        self.__dc = None

    @property
    def _isAwaitingCustomSetup(self):
        if self._isInvalid:
            return False
        if self.__bA is None:
            return False
        with self._md:
            return self.__bA

    @property
    def _isCustomSetupDone(self):
        if self._isInvalid:
            return True
        if self.__bA is None:
            return True

        with self._md:
            if self.__bA:
                res = False
            elif self.__dc is None:
                res = True
            else:
                _keys = list(self.__dc.keys())
                _keys.sort(reverse=True)
                for _kk in _keys:
                    _sid = _EFwsID(_kk)
                    _fws = self.__GetFws(_sid)
                    res = _fws.isRunning
                    if not res:
                        break
            return res

    @property
    def _isCustomSetupFailed(self):
        if self._isInvalid:
            return False
        if self.__bA is None:
            return False
        if self._isAwaitingCustomSetup:
            return False
        return not self._isCustomSetupDone

    @staticmethod
    def _GetMCApiMNL():
        ret = []
        _tmp = _AbsFwService._GetMCApiMNL()
        if _tmp is not None:
            ret += _tmp
        ret += _FwsMainBase.__mcamn
        return ret

    def __CreateFWSs(self):
        if _AbsFwService.GetDefinedFwsNum() < 2:
            self.__bA = True
            return True
        res, self.__dc = False, {}

        _sid  = _EFwsID.eFwsLogRD
        if _AbsFwService.IsDefinedFws(_sid):
            _FwsLogRD._GetInstance(bCreate_=True)
            _comp = _AbsFwService._GetFwsInstance(_sid)

            res = _comp is not None
            res = res and _AbsFwService.IsActiveFws(_sid)
            res = res and self.__AddFws(_sid, _comp)
            if not res:
                if _comp is not None:
                    _comp.CleanUp()
                return False

        _sid = _EFwsID.eFwsDisp
        if _AbsFwService.IsDefinedFws(_sid):
            _FwsDispatcher._GetInstance(bCreate_=True)
            _comp = _AbsFwService._GetFwsInstance(_sid)

            res = _comp is not None
            res = res and _AbsFwService.IsActiveFws(_sid)
            res = res and self.__AddFws(_sid, _comp)
            if not res:
                if _comp is not None:
                    _comp.CleanUp()
                return False

        _sid = _EFwsID.eFwsProcMgr
        if _AbsFwService.IsDefinedFws(_sid):
            _FwsProcMgr._GetInstance(bCreate_=True)
            _comp = _AbsFwService._GetFwsInstance(_sid)

            res = _comp is not None
            res = res and _AbsFwService.IsActiveFws(_sid)
            res = res and self.__AddFws(_sid, _comp)
            if not res:
                if _comp is not None:
                    _comp.CleanUp()
                return False

        if res:
            self.__bA = True
        return True

    def __StartFWSs(self):
        if _AbsFwService.GetDefinedFwsNum() < 2:
            with self._md:
                self.__bA = False
            return True

        res   = False
        _keys = list(self.__dc.keys())
        _keys.sort(reverse=False)
        for _kk in _keys:
            _sid, _vv  = _EFwsID(_kk), self.__dc[_kk]
            _x = None
            try:
                res = _vv.Start()
            except Exception as _xcp:
                _x = _xcp
            if not res:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00075)
                break

            res = _vv.isRunning
            if not res:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00076)
                break

        if not res:
            for _kk in _keys:
                _vv = self.__dc[_kk]
                if _vv.isRunning:
                    _sid = _EFwsID(_kk)
                    _vv.Stop()

        with self._md:
            self.__bA = False
        return res

    def __CleanUpFWSs(self):
        if (self.__dc is None) or len(self.__dc) == 0:
            self.__dc = None
            return

        _keys = list(self.__dc.keys())
        _keys.sort(reverse=True)
        for _kk in _keys:
            _vv = self.__dc.pop(_kk)
            _vv.CleanUp()

        self.__dc.clear()
        self.__dc = None

    def __GetFws(self, fwSID_ :  _EFwsID) -> _AbsFwService:
        res = None
        if self.__dc is None:
            pass
        elif not fwSID_.value in self.__dc:
            pass
        else:
            res = self.__dc[fwSID_.value]
        return res

    def __AddFws(self, fwSID_ :  _EFwsID, fwc_ : _AbsFwService):
        if not (isinstance(fwSID_,  _EFwsID) and isinstance(fwc_, _AbsFwService)):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00077)
            return False
        elif fwSID_.value in self.__dc:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00078)
            return False
        self.__dc[fwSID_.value] = fwc_
        return True
