# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : euerrorbin.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from enum import unique

from xcofdk._xcofw.fw.fwssys.fwcore.logging import vlogif

from xcofdk._xcofw.fw.fwssys.fwcore.logging.fatalentry import _ErrorEntry
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.sync.mutex     import _Mutex
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject      import _AbstractSlotsObject
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes  import _FwIntEnum
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes  import _CommonDefines

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine


class _EuErrorBin(_AbstractSlotsObject):

    @unique
    class _EErrBinOpResult(_FwIntEnum):
        eErrBinOpResultOverwriteError     = -4
        eErrBinOpResultDuplicateInsertion = -3
        eErrBinOpResultInvalidObject      = -2
        eErrBinOpResultImplError          = -1
        eErrBinOpResultSuccess            = 0
        eErrBinOpResultEntryAdded         = 1

        @property
        def isErrBinOpResultSuccess(self):
            return self.value > _EuErrorBin._EErrBinOpResult.eErrBinOpResultImplError.value


        @property
        def isErrBinOpResultFailed(self):
            return not self.isErrBinOpResultSuccess


        @property
        def isErrBinOpResultDuplicateInsertionError(self):
            return self == _EuErrorBin._EErrBinOpResult.eErrBinOpResultDuplicateInsertion


    __slots__ = [ '__bin' , '__ownerTID' , '__binTID' , '__mtxApi' , '__firstFE' , '__primalFE' ]
    __APPLY_ERROR_BIN_REASSURANCE_CHECK = True

    def __init__(self, ownerTID_ : int, binTID_ : int, mtxApi_ : _Mutex, errorEntry_ : _ErrorEntry):
        self.__bin      = None
        self.__binTID   = None
        self.__mtxApi   = None
        self.__firstFE  = None
        self.__primalFE = None
        self.__ownerTID = None
        super().__init__()

        _bError = False
        if _EuErrorBin.__APPLY_ERROR_BIN_REASSURANCE_CHECK:
            if not isinstance(ownerTID_, int):
                _bError = True
                vlogif._LogOEC(True, -1477)
            elif not isinstance(binTID_, int):
                _bError = True
                vlogif._LogOEC(True, -1478)
            elif not isinstance(mtxApi_, _Mutex):
                _bError = True
                vlogif._LogOEC(True, -1479)

        if _bError:
            pass
        elif not _EuErrorBin._IsRegistrableEE(ownerTID_, errorEntry_, binTID_=binTID_):
            _bError = True

        if _bError:
            self.CleanUp()
        else:
            with mtxApi_:
                self.__bin      = errorEntry_
                self.__mtxApi   = mtxApi_
                self.__binTID   = binTID_
                self.__ownerTID = ownerTID_
                if errorEntry_.isFatalError:
                    self.__firstFE  = errorEntry_.Clone()
                    self.__primalFE = errorEntry_.Clone()

    @property
    def isForeignBin(self):
        return (self.__ownerTID is not None) and (self.__ownerTID != self.__binTID)

    @property
    def ownerTaskID(self):
        return self.__ownerTID

    @property
    def binTaskID(self):
        return self.__binTID

    @property
    def primalFatalError(self):

        return self.__primalFE

    @property
    def firstFatalError(self):

        if self.__ownerTID is None:
            res = None
        else:
            with self.__mtxApi:
                res = self.__firstFE
        return res

    @property
    def currentError(self) -> _ErrorEntry:

        if self.__ownerTID is None:
            res = None
        else:
            with self.__mtxApi:
                self.__CheckOnPendingResolution()
                res = self.__bin
        return res


    def SetCurrentError(self, errorEntry_ : _ErrorEntry, force_ =False):
        if self.__ownerTID is None:
            res = _EuErrorBin._EErrBinOpResult.eErrBinOpResultInvalidObject

        elif not _EuErrorBin._IsRegistrableEE(self.__ownerTID, errorEntry_, binTID_=self.__binTID):
            res = _EuErrorBin._EErrBinOpResult.eErrBinOpResultImplError

        else:
            res = _EuErrorBin._EErrBinOpResult.eErrBinOpResultEntryAdded
            with self.__mtxApi:
                self.__CheckOnPendingResolution()
                if self.__bin is not None:
                    if errorEntry_.uniqueID == self.__bin.uniqueID:
                        res = _EuErrorBin._EErrBinOpResult.eErrBinOpResultDuplicateInsertion
                    elif not force_:
                        res = _EuErrorBin._EErrBinOpResult.eErrBinOpResultOverwriteError
                    else:
                        _bForceCleanup = False

                        _bForceCleanup = _bForceCleanup and self.isForeignBin

                        if _bForceCleanup:
                            self.__bin._ForceCleanUp()
                        else:
                            self.__bin.CleanUp()
                        self.__bin = None

        if res.isErrBinOpResultFailed:
            pass
        else:
            self.__bin = errorEntry_
            if self.__firstFE is None:
                if errorEntry_.isFatalError:
                    self.__firstFE = errorEntry_.Clone()
        return res

    def ClearCurError(self):
        if self.__ownerTID is None:
            pass
        else:
            with self.__mtxApi:
                self.__CheckOnPendingResolution()

    def ClearFirstFatalError(self):
        if self.__ownerTID is None:
            pass
        else:
            with self.__mtxApi:
                if self.__firstFE is not None:
                    self.__firstFE.CleanUp()
                    self.__firstFE = None

    @staticmethod
    def _IsRegistrableEE(ownerTID_ : int, ee_ : _ErrorEntry, binTID_ : int =None):
        res     = True
        _bClone = False
        if not isinstance(ee_, _ErrorEntry):
            res = False
        elif not isinstance(ee_.uniqueID, int):
            res = False
        elif ee_.isClone or ee_.hasNoErrorImpact:
            _bClone = ee_.isClone
            res = False

        if not res:
            vlogif._LogOEC(True, -1480)
        else:
            if binTID_ is None:
                binTID_ = ee_.taskID
            if not (isinstance(ownerTID_, int) and isinstance(binTID_, int)):
                res = False
                vlogif._LogOEC(True, -1481)
            elif ee_.taskID != binTID_:
                res = False
                vlogif._LogOEC(True, -1482)
            elif ee_.IsForeignTaskError(ownerTID_):
                if not ee_.isPendingResolution:
                    res = False
                    vlogif._LogOEC(True, -1483)
        return res

    def _ToString(self, *args_, **kwargs_):
        if self.__ownerTID is None:
            res = None
        else:
            with self.__mtxApi:
                self.__CheckOnPendingResolution()
                res = _CommonDefines._STR_EMPTY

                if self.__ownerTID != self.__binTID:
                    res = _FwTDbEngine.GetText(_EFwTextID.eEuErrorBin_ToString_01).format(self.__ownerTID)
                res += _FwTDbEngine.GetText(_EFwTextID.eEuErrorBin_ToString_02).format(self.__binTID)

                if self.__primalFE is not None:
                    _eurNum = self.__primalFE.euRNumber
                    _myTxt  = _FwTDbEngine.GetText(_EFwTextID.eEuErrorBin_ToString_03).format(self.__primalFE.uniqueID, _CommonDefines._CHAR_SIGN_DASH if _eurNum is None else _eurNum)
                    res    += _FwTDbEngine.GetText(_EFwTextID.eEuErrorBin_ToString_07).format(_myTxt)

                if self.firstFatalError is not None:
                    _eurNum = self.__firstFE.euRNumber
                    _myTxt  = _FwTDbEngine.GetText(_EFwTextID.eEuErrorBin_ToString_04).format(self.__firstFE.uniqueID, _CommonDefines._CHAR_SIGN_DASH if _eurNum is None else _eurNum)
                    res    += _FwTDbEngine.GetText(_EFwTextID.eEuErrorBin_ToString_07).format(_myTxt)

                if self.__bin is not None:
                    _eurNum = self.__bin.euRNumber
                    _myTxt  = _FwTDbEngine.GetText(_EFwTextID.eEuErrorBin_ToString_05).format(self.__bin.uniqueID, _CommonDefines._CHAR_SIGN_DASH if _eurNum is None else _eurNum)
                    res    += _FwTDbEngine.GetText(_EFwTextID.eEuErrorBin_ToString_07).format(_myTxt)
                else:
                    res += _FwTDbEngine.GetText(_EFwTextID.eEuErrorBin_ToString_06)
        return res

    def _CleanUp(self):
        if self.__ownerTID is None:
            pass
        else:
            _myApiMtx = self.__mtxApi
            with _myApiMtx:
                if self.__bin is not None:
                    if self.isForeignBin:
                        self.__bin._ForceCleanUp()
                    else:
                        self.__bin.CleanUp()
                if self.__firstFE is not None:
                    self.__firstFE.CleanUp()
                if self.__primalFE is not None:
                    self.__primalFE.CleanUp()
                self.__bin      = None
                self.__binTID   = None
                self.__mtxApi   = None
                self.__firstFE  = None
                self.__primalFE = None
                self.__ownerTID = None

    def __CheckOnPendingResolution(self):
        if self.__bin is None:
            pass
        elif self.__bin.isInvalid:
            self.__bin = None
        elif self.__bin.isPendingResolution:
            pass
        elif self.__bin.hasNoImpactDueToFrcLinkage:
            pass
        else:
            if self.isForeignBin:
                self.__bin._ForceCleanUp()
            else:
                self.__bin.CleanUp()
            self.__bin = None


class _EuFEBinTable(_AbstractSlotsObject):

    __slots__ = [ '__tbl' , '__ownerTID' , '__mtxApi' ]

    def __init__(self, ownerTID_ : int, mtxApi_ : _Mutex):
        self.__tbl      = None
        self.__mtxApi   = None
        self.__ownerTID = None
        super().__init__()

        if not isinstance(ownerTID_, int):
            self.CleanUp()
            vlogif._LogOEC(True, -1484)
        elif not isinstance(mtxApi_, _Mutex):
            self.CleanUp()
            vlogif._LogOEC(True, -1485)
        else:
            self.__mtxApi   = mtxApi_
            self.__ownerTID = ownerTID_

    @property
    def isEmpty(self):
        return self.feeBinTableSize == 0

    @property
    def isNotEmpty(self):
        return self.feeBinTableSize != 0

    @property
    def ownerTaskID(self):
        return self.__ownerTID

    @property
    def feeBinTableSize(self):
        res = 0
        if self.__isInvalid:
            pass
        else:
            with self.__mtxApi:
                res = 0 if self.__tbl is None else len(self.__tbl)
        return res

    def AddForeginErrorEntry(self, fee_ : _ErrorEntry, force_ =False):

        if self.__isInvalid:
            res = _EuErrorBin._EErrBinOpResult.eErrBinOpResultInvalidObject
        elif not _EuErrorBin._IsRegistrableEE(self.__ownerTID, fee_, binTID_=None):
            res = _EuErrorBin._EErrBinOpResult.eErrBinOpResultImplError
        elif fee_.taskID == self.__ownerTID:
            res = _EuErrorBin._EErrBinOpResult.eErrBinOpResultImplError
            vlogif._LogOEC(True, -1486)
        else:
            with self.__mtxApi:
                _feBin = self.__GetFeBin(fee_.taskID)
                if _feBin is None:
                    _feBin = _EuErrorBin(self.__ownerTID, fee_.taskID, self.__mtxApi, fee_)
                    if _feBin.ownerTaskID is None:
                        res = _EuErrorBin._EErrBinOpResult.eErrBinOpResultImplError
                        _feBin.CleanUp()
                    else:
                        res = _EuErrorBin._EErrBinOpResult.eErrBinOpResultEntryAdded
                        if self.__tbl is None:
                            self.__tbl = dict()
                        self.__tbl[_feBin.binTaskID] = _feBin
                else:
                    res = _feBin.SetCurrentError(fee_, force_=force_)
        if res.isErrBinOpResultFailed:
            vlogif._LogOEC(True, -1487)
        return res

    def GetAllPending(self, bFatalErrorsOnly_ =True) -> list:
        res = None
        if self.__isInvalid:
            pass
        else:
            with self.__mtxApi:
                if self.__tbl is None:
                    pass
                else:
                    res = []
                    for _kk in list(self.__tbl.keys()):
                        _feBin = self.__tbl[_kk]
                        _curErr = _feBin.currentError
                        if _curErr is None:
                            self.__tbl.pop(_kk)
                            _feBin.CleanUp()
                        elif _curErr.isFatalError:
                            res.append(_curErr)
                        elif not bFatalErrorsOnly_:
                            if _curErr.hasNoImpactDueToFrcLinkage:
                                res.append(_curErr)
                    if len(res) == 0:
                        res = None
        return res

    def RemoveAllResolved(self):
        if self.__isInvalid:
            pass
        else:
            with self.__mtxApi:
                if self.__tbl is None:
                    pass
                else:
                    for _kk in list(self.__tbl.keys()):
                        _feBin = self.__tbl[_kk]
                        if _feBin.currentError is None:
                            self.__tbl.pop(_kk)
                            _feBin.CleanUp()

    def _ToString(self, *args_, **kwargs_):
        res = None
        if self.__isInvalid:
            pass
        else:
            res = 'ownerTID={} , feeBinTableSize={}'.format(self.ownerTaskID, self.feeBinTableSize)
        return res

    def _CleanUp(self):
        if self.__isInvalid:
            pass
        else:
            _myApiMtx = self.__mtxApi
            with _myApiMtx:
                if self.__tbl is not None:
                    for _kk in list(self.__tbl.keys()):
                        _feBin = self.__tbl.pop(_kk)
                        _feBin.CleanUp()
                    self.__tbl.clear()
                    self.__tbl = None

                self.__mtxApi   = None
                self.__ownerTID = None

    @property
    def __isInvalid(self):
        return self.__ownerTID is None

    def __GetFeBin(self, feBinTaskID_ : int):
        res = None
        if self.__tbl is None:
            pass
        elif feBinTaskID_ in self.__tbl:
            res = self.__tbl[feBinTaskID_]
            if res .currentError is None:
                res.CleanUp()
                res = None
                self.__tbl.pop(feBinTaskID_)
        return res
