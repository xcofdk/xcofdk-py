# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : arunnablefwc.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from xcofdk._xcofw.fw.fwssys.fwcore.logging import vlogif

from xcofdk._xcofw.fw.fwssys.fwcore.base.util             import _Util
from xcofdk._xcofw.fw.fwssys.fwcore.base.timeutil         import _TimeAlert
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject         import _AbstractSlotsObject
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.arunnabledefs import _EFwcID
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.arunnabledefs import _ERunnableType
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.arunnabledefs import _ERunnableApiID
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.arunnabledefs import _ERunnableApiFuncTag
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.rbl.arunnable     import _AbstractRunnable
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.execprofile   import _ExecutionProfile

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine


class _AbstractRunnableFWC(_AbstractRunnable):
    class _FwcEntry:
        __slots__ = [ '__eFwcID' , '__alias' , '__inst' ]

        def __init__(self, eFwcID_ :  _EFwcID, alias_ : str):
            self.__inst   = None
            self.__alias  = alias_
            self.__eFwcID = eFwcID_

        @property
        def eFwcID(self):
            return self.__eFwcID

        @property
        def taskName(self):
            return None if self.__inst is None else self.__inst.taskName

        @property
        def aliasName(self):
            return self.__alias

        @property
        def inst(self):
            return self.__inst

        def SetInstance(self, inst_):
            self.__inst = inst_

        def CleanUp(self):
            self.__inst   = None
            self.__alias  = None
            self.__eFwcID = None

    class _FwcTable:
        __dictFWCs = None

        def __init__(self):
            pass

        @staticmethod
        def IsDefinedFwc(eFwcID_ :  _EFwcID):
            return _AbstractRunnableFWC._FwcTable.__IsValidRequest(eFwcID_, bWarnOnly_=True)

        @staticmethod
        def IsActiveFwc(eFwcID_ :  _EFwcID):
            res = _AbstractRunnableFWC._FwcTable.IsDefinedFwc(eFwcID_)
            if res:
                res = _AbstractRunnableFWC._FwcTable.GetFwcInstance(eFwcID_) is not None
            return res

        @staticmethod
        def GetSize(bActiveOnly =True):
            res = 0
            dc =  _AbstractRunnableFWC._FwcTable.__dictFWCs
            if dc is None:
                pass
            else:
                if bActiveOnly:
                    lstComps = [ _vv for _vv in dc.values() if _vv.inst is not None ]
                    res = len(lstComps)
                else:
                    res = len(dc)
            return res

        @staticmethod
        def SetFwcInstance(eFwcID_ :  _EFwcID, fwc_ : _AbstractRunnable):
            if not _AbstractRunnableFWC._FwcTable.__IsValidRequest(eFwcID_):
                pass
            elif not (fwc_ is None or isinstance(fwc_, _AbstractRunnableFWC)):
                vlogif._LogOEC(True, -1231)
            else:
                tbl, _kk = _AbstractRunnableFWC._FwcTable.__dictFWCs, eFwcID_.value
                _vv = tbl[_kk]
                if fwc_ is None:
                    _vv.SetInstance(inst_=None)
                elif _vv.inst is not None:
                    vlogif._LogOEC(True, -1232)
                else:
                    _vv.SetInstance(inst_=fwc_)

        @staticmethod
        def GetFwcInstance(eFwcID_ :  _EFwcID):
            res = None
            if not _AbstractRunnableFWC._FwcTable.__IsValidRequest(eFwcID_):
                pass
            else:
                tbl, _kk = _AbstractRunnableFWC._FwcTable.__dictFWCs, eFwcID_.value
                if _kk in tbl:
                    res = tbl[_kk].inst
            return res

        @staticmethod
        def GetFwcTaskName(eFwcID_ :  _EFwcID):
            res = None
            if not _AbstractRunnableFWC._FwcTable.__IsValidRequest(eFwcID_):
                pass
            else:
                tbl, _kk = _AbstractRunnableFWC._FwcTable.__dictFWCs, eFwcID_.value
                res = tbl[_kk].taskName
            return res

        @staticmethod
        def GetFwcAliasName(eFwcID_ :  _EFwcID):
            res = None
            if not _AbstractRunnableFWC._FwcTable.__IsValidRequest(eFwcID_):
                pass
            else:
                tbl, _kk = _AbstractRunnableFWC._FwcTable.__dictFWCs, eFwcID_.value
                res = tbl[_kk].aliasName
            return res

        @staticmethod
        def _CleanUpTable():
            if _AbstractRunnableFWC._FwcTable.__dictFWCs is not None:
                tbl = _AbstractRunnableFWC._FwcTable.__dictFWCs
                _AbstractRunnableFWC._FwcTable.__dictFWCs = None

                for _vv in tbl.values():
                    _vv.CleanUp()
                tbl.clear()

        @staticmethod
        def _InitTable(lstFwcIDs_ : list =None):
            if _AbstractRunnableFWC._FwcTable.__dictFWCs is None:
                tbl = dict()

                if lstFwcIDs_ is None:
                    lstFwcIDs_ = [_mm for _nn, _mm in  _EFwcID.__members__.items()]

                for _ee in lstFwcIDs_:
                    if not isinstance(_ee,  _EFwcID):
                        vlogif._LogOEC(True, -1233)
                        break

                    if _ee ==  _EFwcID.eFwMain:
                        alias = _FwTDbEngine.GetText(_EFwTextID.eAbstractRunnableFWC_AliasName_FwMain)

                    elif _ee ==  _EFwcID.eFwDispatcher:
                        alias = _FwTDbEngine.GetText(_EFwTextID.eAbstractRunnableFWC_AliasName_FwDspr)

                    elif _ee ==  _EFwcID.eTimerManager:
                        alias = _FwTDbEngine.GetText(_EFwTextID.eAbstractRunnableFWC_AliasName_TmrMgr)

                    else:
                        vlogif._LogOEC(True, -1234)
                        break

                    tbl[_ee.value] = _AbstractRunnableFWC._FwcEntry(_ee, alias)
                _AbstractRunnableFWC._FwcTable.__dictFWCs = tbl

        @staticmethod
        def __IsValidRequest(eFwcID_ :  _EFwcID, bWarnOnly_ =False):
            res = True
            if not isinstance(eFwcID_,  _EFwcID):
                res = False
                vlogif._LogOEC(True, -1235)
            else:
                tbl = _AbstractRunnableFWC._FwcTable.__dictFWCs
                if tbl is None:
                    res = False
                else:
                    _kk = eFwcID_.value
                    if not _kk in tbl:
                        res = False
                        if bWarnOnly_:
                            pass
                        else:
                            vlogif._LogOEC(True, -1236)
            return res

    __mandatoryCustomApiMethodNames = [ _ERunnableApiID.eOnRunProgressNotification.functionName ]

    __slots__ = [ '__eFwcID' ]

    def __init__( self
                , eRblType_     : _ERunnableType
                , excludedRblM_ : _ERunnableApiFuncTag =None
                , runLogAlert_  : _TimeAlert           =None
                , execProfile_  : _ExecutionProfile    =None ):
        self.__eFwcID = None
        _AbstractSlotsObject.__init__(self)

        mmn = _AbstractRunnableFWC.GetMandatoryCustomApiMethodNamesList()
        if _Util.GetNumAttributes(self, mmn, bThrowx_=True) != len(mmn):
            vlogif._LogOEC(True, -1237)
            self.CleanUp()
            return
        if not (isinstance(eRblType_,  _ERunnableType) and eRblType_.isFwRunnable):
            vlogif._LogOEC(True, -1238)
            self.CleanUp()
            return

        _xp = execProfile_
        if _xp is None:
            _xp = _ExecutionProfile()

        numActiveOLD = _AbstractRunnableFWC.GetActiveFwcNum()
        _AbstractRunnable.__init__( self
                                  , eRblType_=eRblType_, xtaskConn_=None
                                  , excludedRblM_=excludedRblM_
                                  , runLogAlert_=runLogAlert_, execProfile_=_xp)
        if execProfile_ is None:
            _xp.CleanUp()

        if self._eRunnableType is None:
            vlogif._LogOEC(True, -1239)
            self.CleanUp()
        else:
            eFwcID  = _EFwcID(self._eRunnableType.value)
            _AbstractRunnableFWC._FwcTable.SetFwcInstance(eFwcID, self)

            _bOK =         _AbstractRunnableFWC.GetFwcInstance(eFwcID) is not None
            _bOK = _bOK and (_AbstractRunnableFWC.GetActiveFwcNum() == numActiveOLD+1)
            if not _bOK:
                vlogif._LogOEC(True, -1240)
                self.CleanUp()
            else:
                self.__eFwcID = eFwcID

    @staticmethod
    def IsDefinedFwc(eFwcID_:  _EFwcID):
       return _AbstractRunnableFWC._FwcTable.IsDefinedFwc(eFwcID_)

    @staticmethod
    def IsActiveFwc(eFwcID_:  _EFwcID):
        return _AbstractRunnableFWC._FwcTable.IsActiveFwc(eFwcID_)

    @staticmethod
    def GetDefinedFwcNum():
        return _AbstractRunnableFWC._FwcTable.GetSize(bActiveOnly=False)

    @staticmethod
    def GetActiveFwcNum():
        return _AbstractRunnableFWC._FwcTable.GetSize(bActiveOnly=True)

    @staticmethod
    def GetFwcInstance(eFwcID_:  _EFwcID):
        return _AbstractRunnableFWC._FwcTable.GetFwcInstance(eFwcID_)

    @staticmethod
    def GetFwcTaskName(eFwcID_:  _EFwcID):
        return _AbstractRunnableFWC._FwcTable.GetFwcTaskName(eFwcID_)

    @staticmethod
    def GetFwcAliasName(eFwcID_:  _EFwcID):
        return _AbstractRunnableFWC._FwcTable.GetFwcAliasName(eFwcID_)

    @staticmethod
    def _GetMandatoryCustomApiMethodNamesList():
        res = []
        tmp = _AbstractRunnable._GetMandatoryCustomApiMethodNamesList()
        if tmp is not None:
            res += tmp
        res += _AbstractRunnableFWC.__mandatoryCustomApiMethodNames
        return res

    @property
    def _eFwcID(self):
        return self.__eFwcID

    @staticmethod
    def _DefineFwcTable(lstFwcIDs_ : list = None):
        _AbstractRunnableFWC._FwcTable._InitTable(lstFwcIDs_=lstFwcIDs_)

    @staticmethod
    def _CleanUpFwcTable():
        _AbstractRunnableFWC._FwcTable._CleanUpTable()

    def _ToString(self, *args_, **kwargs_):
        return _AbstractRunnable._ToString(self, *args_, **kwargs_)

    def _CleanUp(self):
        if self._eRunnableType is None:
            return

        eFwcID = self.__eFwcID
        self.__eFwcID = None
        _AbstractRunnableFWC._FwcTable.SetFwcInstance(eFwcID, None)
        super()._CleanUp()
