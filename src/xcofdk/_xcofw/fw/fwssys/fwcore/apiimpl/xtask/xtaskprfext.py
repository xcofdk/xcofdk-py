# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xtaskprfext.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from enum import unique
from enum import IntFlag

from xcofdk._xcofw.fw.fwssys.fwcore.logging                    import logif
from xcofdk._xcofw.fw.fwssys.fwcore.apiimpl.xtask.xtaskprfbase import _XTaskProfileBase
from xcofdk._xcofw.fw.fwssys.fwcore.types.ebitmask             import _EBitMask

from xcofdk.fwapi.xtask.xtaskprofile import XTaskProfile

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine


class _XTaskProfileExt(XTaskProfile):

    @unique
    class _ETaskPrfExtFlag(IntFlag):
        bfNone     = 0x0000
        bfFrozen   = (0x0001 << 0)
        bfUnitTest = (0x0001 << 1)

        @property
        def compactName(self) -> str:
            return self.name[2:]

        @staticmethod
        def AddTaskPrfFlag(tprfBM_: IntFlag, tprfBF_):
            return _EBitMask.AddEnumBitFlag(tprfBM_, tprfBF_)

        @staticmethod
        def RemoveTaskPrfFlag(tprfBM_: IntFlag, tprfBF_):
            return _EBitMask.RemoveEnumBitFlag(tprfBM_, tprfBF_)

        @staticmethod
        def IsTaskPrfFlagSet(tprfBM_: IntFlag, tprfBF_):
            return _EBitMask.IsEnumBitFlagSet(tprfBM_, tprfBF_)


    __slots__ = [ '__bmExt' ]

    def __init__(self, xtProfile_ : XTaskProfile =None, bMainXT_ =False):
        self.__bmExt = _XTaskProfileExt._ETaskPrfExtFlag.bfNone
        super().__init__()

        if xtProfile_ is None:
            pass
        elif not (isinstance(xtProfile_, XTaskProfile) and xtProfile_.isValid):
            self._CleanUp()
            logif._XLogError(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskProfileExt_TextID_001).format(type(xtProfile_).__name__))
        elif XTaskProfile._AssignProfile(self, xtProfile_) is None:
            self._CleanUp()
            logif._XLogError(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskProfileExt_TextID_002).format(type(xtProfile_).__name__))

        if bMainXT_ != self.isMainTask:
            _XTaskProfileBase._SetMainXTask(self, bMainXT_)

    def __str__(self):
        return self.ToString()

    @property
    def isFrozen(self) -> bool:
        return self._isFrozen

    @property
    def isUnitTest(self) -> bool:
        return self._isValid and _XTaskProfileExt._ETaskPrfExtFlag.IsTaskPrfFlagSet(self.__bmExt, _XTaskProfileExt._ETaskPrfExtFlag.bfUnitTest)

    @isUnitTest.setter
    def isUnitTest(self, bUnitTest_ : bool):
        if not self._CheckFreezeState(): return
        if bUnitTest_:
            self.__bmExt = _XTaskProfileExt._ETaskPrfExtFlag.AddTaskPrfFlag(self.__bmExt, _XTaskProfileExt._ETaskPrfExtFlag.bfUnitTest)
        else:
            self.__bmExt = _XTaskProfileExt._ETaskPrfExtFlag.RemoveTaskPrfFlag(self.__bmExt, _XTaskProfileExt._ETaskPrfExtFlag.bfUnitTest)

    def ToString(self, bVerbose_=True) -> str:
        res = XTaskProfile._ToString(self, bVerbose_=bVerbose_)
        if bVerbose_:
            res += '\t{:<32} : {}\n'.format(_FwTDbEngine.GetText(_EFwTextID.eXTaskProfileExt_ToString_01), str(self.isUnitTest))
        return res

    def CloneProfile(self):
        res = _XTaskProfileExt()
        res = _XTaskProfileExt._AssignProfile(res, self)
        return res

    @property
    def _isFrozen(self) -> bool:
        return self._isValid and _XTaskProfileExt._ETaskPrfExtFlag.IsTaskPrfFlagSet(self.__bmExt, _XTaskProfileExt._ETaskPrfExtFlag.bfFrozen)

    def _Freeze(self):
        if self._isFrozen:
            return

        _bRunEnabled              = self._isRunPhaseEnabled
        _bExtQueueEnabled         = self._isExternalQueueEnabled
        _bBlockingExtQueueEnabled = self._isExternalQueueBlocking

        if not _bRunEnabled:
            _bMisMatch = not (_bExtQueueEnabled and _bBlockingExtQueueEnabled)
        else:
            _bMisMatch = _bBlockingExtQueueEnabled

        if _bMisMatch:
            logif._XLogWarning(_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XTaskProfileExt_TextID_003).format(str(_bRunEnabled), str(_bExtQueueEnabled), str(_bBlockingExtQueueEnabled)))

        self.__bmExt = _XTaskProfileExt._ETaskPrfExtFlag.AddTaskPrfFlag(self.__bmExt, _XTaskProfileExt._ETaskPrfExtFlag.bfFrozen)

    def _AssignProfile(self, rhs_):
        if not self._CheckFreezeState(): return None
        if not isinstance(rhs_, _XTaskProfileExt):
            return None
        if XTaskProfile._AssignProfile(self, rhs_) is None:
            return None

        self.isUnitTest = rhs_.isUnitTest
        return self

    def _CleanUp(self):
        self.__bmExt = None
        _XTaskProfileBase._CleanUp(self)
