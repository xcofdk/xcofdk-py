# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : pcerrorbin.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum import auto
from enum import unique

from _fw.fwssys.fwcore.logging           import vlogif
from _fw.fwssys.fwcore.ipc.sync.mutex    import _Mutex
from _fw.fwssys.fwcore.types.aobject     import _AbsSlotsObject
from _fw.fwssys.fwcore.types.commontypes import _FwIntEnum
from _fw.fwssys.fwcore.types.commontypes import _CommonDefines
from _fw.fwssys.fwerrh.fwerrorcodes      import _EFwErrorCode
from _fw.fwssys.fwerrh.logs.errorlog     import _ErrorLog

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _PcErrorBin(_AbsSlotsObject):
    @unique
    class _EErrBinOpResult(_FwIntEnum):
        eErrBinOpResultOverwriteError     = -4
        eErrBinOpResultDuplicateInsertion = auto()
        eErrBinOpResultInvalidObject      = auto()
        eErrBinOpResultImplError          = auto()
        eErrBinOpResultSuccess            = auto()
        eErrBinOpResultEntryAdded         = auto()

        @property
        def isErrBinOpResultSuccess(self):
            return self.value > _PcErrorBin._EErrBinOpResult.eErrBinOpResultImplError.value

        @property
        def isErrBinOpResultFailed(self):
            return not self.isErrBinOpResultSuccess

        @property
        def isErrBinOpResultDuplicateInsertionError(self):
            return self == _PcErrorBin._EErrBinOpResult.eErrBinOpResultDuplicateInsertion

    __slots__ = [ '__b' , '__ht' , '__bt' , '__ma' , '__f' , '__p' ]

    def __init__(self, ownerTID_ : int, binTID_ : int, ma_ : _Mutex, errorEntry_ : _ErrorLog):
        self.__b  = None
        self.__f  = None
        self.__p  = None
        self.__bt = None
        self.__ht = None
        self.__ma = None
        super().__init__()

        _bError = not _PcErrorBin._IsRegistrableEE(ownerTID_, errorEntry_, binTID_=binTID_)
        if _bError:
            self.CleanUp()
        else:
            with ma_:
                self.__b  = errorEntry_
                self.__bt = binTID_
                self.__ht = ownerTID_
                self.__ma = ma_
                if errorEntry_.isFatalError:
                    self.__f = errorEntry_.Clone()
                    self.__p = errorEntry_.Clone()

    @property
    def isForeignBin(self):
        return (self.__ht is not None) and (self.__ht != self.__bt)

    @property
    def ownerTaskID(self):
        return self.__ht

    @property
    def binTaskID(self):
        return self.__bt

    @property
    def firstFatalError(self):
        if self.__ht is None:
            res = None
        else:
            with self.__ma:
                res = self.__f
        return res

    @property
    def currentError(self) -> _ErrorLog:
        if self.__ht is None:
            res = None
        else:
            with self.__ma:
                self.__CheckOnPendingResolution()
                res = self.__b
        return res

    def SetCurrentError(self, errorEntry_ : _ErrorLog, force_ =False):
        if self.__ht is None:
            res = _PcErrorBin._EErrBinOpResult.eErrBinOpResultInvalidObject

        elif not _PcErrorBin._IsRegistrableEE(self.__ht, errorEntry_, binTID_=self.__bt):
            res = _PcErrorBin._EErrBinOpResult.eErrBinOpResultImplError

        else:
            res = _PcErrorBin._EErrBinOpResult.eErrBinOpResultEntryAdded
            with self.__ma:
                self.__CheckOnPendingResolution()
                if self.__b is not None:
                    if errorEntry_.uniqueID == self.__b.uniqueID:
                        res = _PcErrorBin._EErrBinOpResult.eErrBinOpResultDuplicateInsertion
                    elif not force_:
                        res = _PcErrorBin._EErrBinOpResult.eErrBinOpResultOverwriteError
                    else:
                        _bForceCleanup = False
                        _bForceCleanup = _bForceCleanup and self.isForeignBin
                        if _bForceCleanup:
                            self.__b._ForceCleanUp()
                        else:
                            self.__b.CleanUp()
                        self.__b = None

        if not res.isErrBinOpResultFailed:
            self.__b = errorEntry_
            if self.__f is None:
                if errorEntry_.isFatalError:
                    self.__f = errorEntry_.Clone()
        return res

    def ClearCurError(self):
        if self.__ht is not None:
            with self.__ma:
                self.__CheckOnPendingResolution()

    @staticmethod
    def _IsRegistrableEE(ownerTID_ : int, ee_ : _ErrorLog, binTID_ : int =None):
        res     = True
        _bClone = False
        if not isinstance(ee_, _ErrorLog):
            res = False
        elif not isinstance(ee_.uniqueID, int):
            res = False
        elif ee_.isClone or ee_.hasNoErrorImpact:
            _bClone = ee_.isClone
            res = False

        if not res:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00507)
        else:
            if binTID_ is None:
                binTID_ = ee_.dtaskUID
            if not (isinstance(ownerTID_, int) and isinstance(binTID_, int)):
                res = False
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00508)
            elif ee_.dtaskUID != binTID_:
                res = False
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00509)
            elif ee_.IsForeignTaskError(ownerTID_):
                if not ee_.isPendingResolution:
                    res = False
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00510)
        return res

    def _ToString(self):
        if self.__ht is None:
            res = None
        else:
            with self.__ma:
                self.__CheckOnPendingResolution()
                res = _CommonDefines._STR_EMPTY

                if self.__ht != self.__bt:
                    res = _FwTDbEngine.GetText(_EFwTextID.ePcErrorBin_ToString_01).format(self.__ht)
                res += _FwTDbEngine.GetText(_EFwTextID.ePcErrorBin_ToString_02).format(self.__bt)

                if self.__p is not None:
                    _eurNum = self.__p.xrNumber
                    _myTxt  = _FwTDbEngine.GetText(_EFwTextID.ePcErrorBin_ToString_03).format(self.__p.uniqueID, _CommonDefines._CHAR_SIGN_DASH if _eurNum is None else _eurNum)
                    res    += _FwTDbEngine.GetText(_EFwTextID.ePcErrorBin_ToString_07).format(_myTxt)

                if self.firstFatalError is not None:
                    _eurNum = self.__f.xrNumber
                    _myTxt  = _FwTDbEngine.GetText(_EFwTextID.ePcErrorBin_ToString_04).format(self.__f.uniqueID, _CommonDefines._CHAR_SIGN_DASH if _eurNum is None else _eurNum)
                    res    += _FwTDbEngine.GetText(_EFwTextID.ePcErrorBin_ToString_07).format(_myTxt)

                if self.__b is not None:
                    _eurNum = self.__b.xrNumber
                    _myTxt  = _FwTDbEngine.GetText(_EFwTextID.ePcErrorBin_ToString_05).format(self.__b.uniqueID, _CommonDefines._CHAR_SIGN_DASH if _eurNum is None else _eurNum)
                    res    += _FwTDbEngine.GetText(_EFwTextID.ePcErrorBin_ToString_07).format(_myTxt)
                else:
                    res += _FwTDbEngine.GetText(_EFwTextID.ePcErrorBin_ToString_06)
        return res

    def _CleanUp(self):
        if self.__ht is None:
            return

        _m = self.__ma
        with _m:
            if self.__b is not None:
                if self.isForeignBin:
                    self.__b._ForceCleanUp()
                else:
                    self.__b.CleanUp()
            if self.__f is not None:
                self.__f.CleanUp()
            if self.__p is not None:
                self.__p.CleanUp()
            self.__b  = None
            self.__f  = None
            self.__p  = None
            self.__bt = None
            self.__ht = None
            self.__ma = None

    def __CheckOnPendingResolution(self):
        if self.__b is None:
            pass
        elif self.__b.isInvalid:
            self.__b = None
        elif self.__b.isPendingResolution:
            pass
        elif self.__b.hasNoImpactDueToFrcLinkage:
            pass
        else:
            if self.isForeignBin:
                self.__b._ForceCleanUp()
            else:
                self.__b.CleanUp()
            self.__b = None

class _PcFEBinTable(_AbsSlotsObject):
    __slots__ = [ '__t' , '__ht' , '__ma' ]

    def __init__(self, ownerTID_ : int, ma_ : _Mutex):
        self.__t  = None
        self.__ht = None
        self.__ma = None
        super().__init__()

        if not isinstance(ownerTID_, int):
            self.CleanUp()
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00511)
        elif not isinstance(ma_, _Mutex):
            self.CleanUp()
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00512)
        else:
            self.__ht = ownerTID_
            self.__ma = ma_

    @property
    def isEmpty(self):
        return self.feeBinTableSize == 0

    @property
    def ownerTaskID(self):
        return self.__ht

    @property
    def feeBinTableSize(self):
        if self.__isInvalid:
            return 0

        with self.__ma:
            res = 0 if self.__t is None else len(self.__t)
        return res

    def AddForeginErrorEntry(self, fee_ : _ErrorLog, force_ =False):
        if self.__isInvalid:
            res = _PcErrorBin._EErrBinOpResult.eErrBinOpResultInvalidObject
        elif not _PcErrorBin._IsRegistrableEE(self.__ht, fee_, binTID_=None):
            res = _PcErrorBin._EErrBinOpResult.eErrBinOpResultImplError
        elif fee_.dtaskUID == self.__ht:
            res = _PcErrorBin._EErrBinOpResult.eErrBinOpResultImplError
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00513)
        else:
            with self.__ma:
                _feBin = self.__GetFeBin(fee_.dtaskUID)
                if _feBin is None:
                    _feBin = _PcErrorBin(self.__ht, fee_.dtaskUID, self.__ma, fee_)
                    if _feBin.ownerTaskID is None:
                        res = _PcErrorBin._EErrBinOpResult.eErrBinOpResultImplError
                        _feBin.CleanUp()
                    else:
                        res = _PcErrorBin._EErrBinOpResult.eErrBinOpResultEntryAdded
                        if self.__t is None:
                            self.__t = dict()
                        self.__t[_feBin.binTaskID] = _feBin
                else:
                    res = _feBin.SetCurrentError(fee_, force_=force_)
        if res.isErrBinOpResultFailed:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00514)
        return res

    def GetAllPending(self) -> list:
        if self.__isInvalid:
            return None

        with self.__ma:
            if self.__t is None:
                return None

            res = []
            for _kk in list(self.__t.keys()):
                _feBin = self.__t[_kk]
                _curErr = _feBin.currentError
                if _curErr is None:
                    self.__t.pop(_kk)
                    _feBin.CleanUp()
                elif _curErr.isFatalError:
                    res.append(_curErr)
            if len(res) == 0:
                res = None
        return res

    def _ToString(self):
        res = None
        if not self.__isInvalid:
            res = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_030).format(self.ownerTaskID, self.feeBinTableSize)
        return res

    def _CleanUp(self):
        if self.__isInvalid:
            return

        _m = self.__ma
        with _m:
            if self.__t is not None:
                for _kk in list(self.__t.keys()):
                    _feBin = self.__t.pop(_kk)
                    _feBin.CleanUp()
                self.__t.clear()
                self.__t = None

            self.__ht = None
            self.__ma = None

    @property
    def __isInvalid(self):
        return self.__ht is None

    def __GetFeBin(self, feBinTaskID_ : int):
        if self.__t is None:
            return None

        res = None
        if feBinTaskID_ in self.__t:
            res = self.__t[feBinTaskID_]
            if res .currentError is None:
                res.CleanUp()
                res = None
                self.__t.pop(feBinTaskID_)
        return res
