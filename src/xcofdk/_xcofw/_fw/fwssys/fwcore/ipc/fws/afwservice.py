# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : afwservice.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from _fw.fwssys.assys                    import fwsubsysshare as _ssshare
from _fw.fwssys.fwcore.logging           import vlogif
from _fw.fwssys.fwcore.base.util         import _Util
from _fw.fwssys.fwcore.base.timeutil     import _TimeAlert
from _fw.fwssys.fwcore.types.aobject     import _AbsSlotsObject
from _fw.fwssys.fwcore.ipc.rbl.arbldefs  import _ERblApiFuncTag
from _fw.fwssys.fwcore.ipc.rbl.arunnable import _AbsRunnable
from _fw.fwssys.fwcore.ipc.tsk.taskdefs  import _EFwsID
from _fw.fwssys.fwcore.ipc.tsk.taskdefs  import _ERblType
from _fw.fwssys.fwcore.ipc.tsk.taskxcard import _TaskXCard
from _fw.fwssys.fwcore.types.commontypes import _EDepInjCmd
from _fw.fwssys.fwerrh.fwerrorcodes      import _EFwErrorCode

class _AbsFwService(_AbsRunnable):
    class _FwsEntry:
        __slots__ = [ '__sid' , '__i' ]

        def __init__(self, fwSID_ :  _EFwsID):
            self.__i   = None
            self.__sid = fwSID_

        @property
        def fwsName(self):
            return None if self.__i is None else self.__i._dtaskName

        @property
        def fwsInst(self):
            return self.__i

        def SetInst(self, inst_):
            self.__i = inst_

        def CleanUp(self):
            self.__i   = None
            self.__sid = None

    class _FwsTable:
        __tbl = None

        def __init__(self):
            pass

        @staticmethod
        def _IsDefinedFws(fwSID_ :  _EFwsID, bWarn_ =False):
            return _AbsFwService._FwsTable.__IsValidRequest(fwSID_, bWarnOnly_=True if bWarn_ else None)

        @staticmethod
        def _IsActiveFws(fwSID_ :  _EFwsID):
            res = _AbsFwService._FwsTable._IsDefinedFws(fwSID_, bWarn_=True)
            res = res and (_AbsFwService._FwsTable._GetFwsInstance(fwSID_) is not None)
            return res

        @staticmethod
        def _GetSize(bActiveOnly =True):
            res = 0
            _dc =  _AbsFwService._FwsTable.__tbl
            if _dc is not None:
                if bActiveOnly:
                    _lstFwc = [ _vv for _vv in _dc.values() if _vv.fwsInst is not None ]
                    res = len(_lstFwc)
                else:
                    res = len(_dc)
            return res

        @staticmethod
        def _SetFwsInst(fwSID_ :  _EFwsID, fwc_ : _AbsRunnable):
            if not _AbsFwService._FwsTable.__IsValidRequest(fwSID_):
                pass
            elif fwSID_.isFwsDisp and _ssshare._IsSubsysMsgDisabled():
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00957)
            elif fwSID_.isFwsPMgr and _ssshare._IsSubsysMPDisabled():
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00958)
            elif not (fwc_ is None or isinstance(fwc_, _AbsFwService)):
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00151)
            else:
                _tbl, _kk = _AbsFwService._FwsTable.__tbl, fwSID_.value
                _vv = _tbl[_kk]
                if fwc_ is None:
                    _vv.SetInst(inst_=None)
                elif _vv.fwsInst is not None:
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00152)
                else:
                    _vv.SetInst(inst_=fwc_)

        @staticmethod
        def _GetFwsInstance(fwSID_ :  _EFwsID):
            res = None
            if _AbsFwService._FwsTable.__IsValidRequest(fwSID_):
                _tbl, _kk = _AbsFwService._FwsTable.__tbl, fwSID_.value
                if _kk in _tbl:
                    res = _tbl[_kk].fwsInst
            return res

        @staticmethod
        def _CleanUpTable():
            if _AbsFwService._FwsTable.__tbl is not None:
                _tbl = _AbsFwService._FwsTable.__tbl
                _AbsFwService._FwsTable.__tbl = None

                for _vv in _tbl.values():
                    _vv.CleanUp()
                _tbl.clear()

        @staticmethod
        def _InitTable(lstFwcIDs_ : list =None):
            if _AbsFwService._FwsTable.__tbl is None:
                _tbl = dict()

                if lstFwcIDs_ is None:
                    lstFwcIDs_ = [ _mm for _nn, _mm in  _EFwsID.__members__.items() ]

                for _ee in lstFwcIDs_:
                    if not isinstance(_ee,  _EFwsID):
                        vlogif._LogOEC(True, _EFwErrorCode.VFE_00153)
                        break
                    _tbl[_ee.value] = _AbsFwService._FwsEntry(_ee)
                _AbsFwService._FwsTable.__tbl = _tbl

        @staticmethod
        def __IsValidRequest(fwSID_ :  _EFwsID, bWarnOnly_ : bool =None):
            res = True
            if not isinstance(fwSID_,  _EFwsID):
                res = False
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00155)
            else:
                _tbl = _AbsFwService._FwsTable.__tbl
                if _tbl is None:
                    res = False
                elif fwSID_.value not in _tbl:
                    res = False
                    if bWarnOnly_ is not None:
                        if not bWarnOnly_:
                            vlogif._LogOEC(True, _EFwErrorCode.VFE_00156)
            return res

    __mcamn = None

    __slots__ = [ '__sid' ]

    def __init__( self
                , rblType_     : _ERblType
                , rblXM_       : _ERblApiFuncTag =None
                , runLogAlert_ : _TimeAlert      =None
                , txCard_      : _TaskXCard      =None ):
        self.__sid = None
        _AbsSlotsObject.__init__(self)

        _mmn = _AbsFwService.GetMCApiMNL()
        if _Util.GetNumAttributes(self, _mmn, bThrowx_=True) != len(_mmn):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00157)
            self.CleanUp()
            return
        if not (isinstance(rblType_,  _ERblType) and rblType_.isFwRunnable):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00158)
            self.CleanUp()
            return

        _xc = txCard_
        if _xc is None:
            _xc = _TaskXCard()

        _oldNumActive = _AbsFwService.GetActiveFwsNum()
        _AbsRunnable.__init__(self, rblType_=rblType_, utaskConn_=None , rblXM_=rblXM_ , runLogAlert_=runLogAlert_, txCard_=_xc)
        if txCard_ is None:
            _xc.CleanUp()

        if self._rblType is None:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00159)
            self.CleanUp()
        else:
            _sid  = _EFwsID(self._rblType.value)
            _AbsFwService._FwsTable._SetFwsInst(_sid, self)

            _bOK =          _AbsFwService._GetFwsInstance(_sid) is not None
            _bOK = _bOK and (_AbsFwService.GetActiveFwsNum() == _oldNumActive+1)
            if not _bOK:
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00160)
                self.CleanUp()
            else:
                self.__sid = _sid

    @staticmethod
    def IsDefinedFws(fwSID_:  _EFwsID, bWarn_ =False):
        return _AbsFwService._FwsTable._IsDefinedFws(fwSID_, bWarn_=bWarn_)

    @staticmethod
    def IsActiveFws(fwSID_:  _EFwsID):
        return _AbsFwService._FwsTable._IsActiveFws(fwSID_)

    @staticmethod
    def GetDefinedFwsNum():
        return _AbsFwService._FwsTable._GetSize(bActiveOnly=False)

    @staticmethod
    def GetActiveFwsNum():
        return _AbsFwService._FwsTable._GetSize(bActiveOnly=True)

    @staticmethod
    def _GetFwsInstance(fwSID_:  _EFwsID):
        return _AbsFwService._FwsTable._GetFwsInstance(fwSID_)

    @staticmethod
    def _GetMCApiMNL():
        res = []
        _tmp = _AbsRunnable._GetMCApiMNL()
        if _tmp is not None:
            res += _tmp
        if _AbsFwService.__mcamn is not None:
            res += _AbsFwService.__mcamn
        return res

    @property
    def _fwSID(self):
        return self.__sid

    @staticmethod
    def _ClsDepInjection(dinjCmd_ : _EDepInjCmd, fwSID_:  _EFwsID =None, lstFwcIDs_ : list =None):
        res = None
        if dinjCmd_.isDeInject:
            _AbsFwService._FwsTable._CleanUpTable()
        elif fwSID_ is not None:
            res = _AbsFwService._GetFwsInstance(fwSID_)
        elif lstFwcIDs_ is not None:
            _AbsFwService._FwsTable._InitTable(lstFwcIDs_=lstFwcIDs_)
        return res

    def _ToString(self, bVerbose_ =False, annex_ : str =None):
        res = _AbsRunnable._ToString(self, not bVerbose_)
        if (res is not None) and (annex_ is not None):
            res += annex_
        return res

    def _CleanUp(self):
        if self._rblType is None:
            return

        _sid = self.__sid
        self.__sid = None
        _AbsFwService._FwsTable._SetFwsInst(_sid, None)
        super()._CleanUp()
