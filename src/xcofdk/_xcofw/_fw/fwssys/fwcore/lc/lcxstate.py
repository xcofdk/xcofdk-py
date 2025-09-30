# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : lcxstate.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum      import auto
from enum      import unique
from threading import RLock as _PyRLock
from typing    import Union

from xcofdk.fwcom import LcFailure

from _fw.fwssys.fwcore.logging            import vlogif
from _fw.fwssys.fwcore.logging.vlogif     import _ELRType
from _fw.fwssys.fwcore.logging.vlogif     import _EColorCode
from _fw.fwssys.fwcore.logging.vlogif     import _PutLR
from _fw.fwssys.fwcore.logging.logdefines import _LogErrorCode
from _fw.fwssys.fwcore.base.strutil       import _StrUtil
from _fw.fwssys.fwcore.types.ebitmask     import _EBitMask
from _fw.fwssys.fwcore.types.commontypes  import _FwEnum
from _fw.fwssys.fwcore.types.commontypes  import _EDepInjCmd
from _fw.fwssys.fwcore.types.commontypes  import _FwIntFlag
from _fw.fwssys.fwcore.types.commontypes  import _CommonDefines
from _fw.fwssys.fwcore.types.apobject     import _ProtAbsSlotsObject
from _fw.fwssys.fwerrh.fwerrorcodes       import _EFwErrorCode
from _fw.fwssys.fwerrh.lcfrcview          import _LcFrcView

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

@unique
class _ELcXState(_FwIntFlag):
    eIdle               = 0x000000

    ePreConfigPhase     = (0x000001 <<  0)
    eConfigPhase        = (0x000001 <<  1)
    eSemiBoostPhase     = (0x000001 <<  2)
    eFullBoostPhase     = (0x000001 <<  3)
    eCustomSetupPhase   = (0x000001 <<  4)
    eRuntimePhase       = (0x000001 <<  5)
    eMxtAutoStartPhase  = (0x000001 <<  6)
    eMxtPostStartPhase  = (0x000001 <<  7)

    eJoinPhase          = (0x000001 <<  8)
    eStopPhase          = (0x000001 <<  9)
    eShutdownPhase      = (0x000001 << 10)

    eSetupPassed        = (0x000001 << 16)
    eMxtStartPassed     = (0x000001 << 17)
    eShutdownPassed     = (0x000001 << 18)
    eStopPassed         = (0x000001 << 19)
    eJoinPassed         = (0x000001 << 20)

    eLcSetupFailure     = (0x000001 << 28)
    eLcRuntimeFailure   = (0x000001 << 29)

    @property
    def isFailureFree(self):
        return not (self.hasLcSetupFailure or self.hasLcRuntimeFailure)

    @property
    def isTransitionalSetupPhase(self):
        return self.isTransitionalConfigPhase() or self.isTransitionalBoostPhase() or self.IsCustomSetupPhase(exclusively_=True)

    @property
    def isTransitionalConfigPhase(self):
        return self.IsPreConfigPhase(exclusively_=True) or self.IsConfigPhase(exclusively_=True)

    @property
    def isTransitionalBoostPhase(self):
        return self.IsSemiBoostPhase(exclusively_=True) or self.IsFullBoostPhase(exclusively_=True)

    @property
    def isTransitionalMxtStartPhase(self):
        return self.IsMxtAutoStartPhase(exclusively_=True) or self.IsMxtPostStartPhase(exclusively_=True)

    @property
    def isFailureState(self):
        return self.IsLcSetupFailure(exclusively_=True) or self.IsLcRuntimeFailure(exclusively_=True)

    @property
    def hasPassedSetupPhase(self):
        return self.IsSetupPassed()

    @property
    def hasPassedMxtStartPhase(self):
        return self.IsMxtStartPassed()

    @property
    def hasPassedShutdownPhase(self):
        return self.IsShutdownPassed()

    @property
    def hasPassedStopPhase(self):
        return self.IsStopPassed()

    @property
    def hasPassedJoinPhase(self):
        return self.IsJoinPassed()

    @property
    def hasLcSetupFailure(self):
        return self.IsLcSetupFailure()

    @property
    def hasLcRuntimeFailure(self):
        return self.IsLcRuntimeFailure()

    def IsIdle(self, exclusively_ =False):
        return self == _ELcXState.eIdle

    def IsPreConfigPhase(self, exclusively_ =False):
        return self == _ELcXState.ePreConfigPhase if exclusively_ else _EBitMask.IsEnumBitFlagSet(self, _ELcXState.ePreConfigPhase)

    def IsConfigPhase(self, exclusively_ =False):
        return self == _ELcXState.eConfigPhase if exclusively_ else _EBitMask.IsEnumBitFlagSet(self, _ELcXState.eConfigPhase)

    def IsSemiBoostPhase(self, exclusively_ =False):
        return self == _ELcXState.eSemiBoostPhase if exclusively_ else _EBitMask.IsEnumBitFlagSet(self, _ELcXState.eSemiBoostPhase)

    def IsFullBoostPhase(self, exclusively_ =False):
        return self == _ELcXState.eFullBoostPhase if exclusively_ else _EBitMask.IsEnumBitFlagSet(self, _ELcXState.eFullBoostPhase)

    def IsCustomSetupPhase(self, exclusively_ =False):
        return self == _ELcXState.eCustomSetupPhase if exclusively_ else _EBitMask.IsEnumBitFlagSet(self, _ELcXState.eCustomSetupPhase)

    def IsMxtAutoStartPhase(self, exclusively_ =False):
        return self == _ELcXState.eMxtAutoStartPhase if exclusively_ else _EBitMask.IsEnumBitFlagSet(self, _ELcXState.eMxtAutoStartPhase)

    def IsRuntimePhase(self, exclusively_ =False):
        return self == _ELcXState.eRuntimePhase if exclusively_ else _EBitMask.IsEnumBitFlagSet(self, _ELcXState.eRuntimePhase)

    def IsMxtPostStartPhase(self, exclusively_ =False):
        return self == _ELcXState.eMxtPostStartPhase if exclusively_ else _EBitMask.IsEnumBitFlagSet(self, _ELcXState.eMxtPostStartPhase)

    def IsJoinPhase(self, exclusively_ =False):
        return self == _ELcXState.eJoinPhase if exclusively_ else _EBitMask.IsEnumBitFlagSet(self, _ELcXState.eJoinPhase)

    def IsStopPhase(self, exclusively_ =False):
        return self == _ELcXState.eStopPhase if exclusively_ else _EBitMask.IsEnumBitFlagSet(self, _ELcXState.eStopPhase)

    def IsShutdownPhase(self, exclusively_ =False):
        return self == _ELcXState.eShutdownPhase if exclusively_ else _EBitMask.IsEnumBitFlagSet(self, _ELcXState.eShutdownPhase)

    def IsSetupPassed(self, exclusively_ =False):
        return self == _ELcXState.eSetupPassed if exclusively_ else _EBitMask.IsEnumBitFlagSet(self, _ELcXState.eSetupPassed)

    def IsMxtStartPassed(self, exclusively_ =False):
        return self == _ELcXState.eMxtStartPassed if exclusively_ else _EBitMask.IsEnumBitFlagSet(self, _ELcXState.eMxtStartPassed)

    def IsShutdownPassed(self, exclusively_ =False):
        return self == _ELcXState.eShutdownPassed if exclusively_ else _EBitMask.IsEnumBitFlagSet(self, _ELcXState.eShutdownPassed)

    def IsStopPassed(self, exclusively_ =False):
        return self == _ELcXState.eStopPassed if exclusively_ else _EBitMask.IsEnumBitFlagSet(self, _ELcXState.eStopPassed)

    def IsJoinPassed(self, exclusively_ =False):
        return self == _ELcXState.eJoinPassed if exclusively_ else _EBitMask.IsEnumBitFlagSet(self, _ELcXState.eJoinPassed)

    def IsLcSetupFailure(self, exclusively_ =False):
        return self == _ELcXState.eLcSetupFailure if exclusively_ else _EBitMask.IsEnumBitFlagSet(self, _ELcXState.eLcSetupFailure)

    def IsLcRuntimeFailure(self, exclusively_ =False):
        return self == _ELcXState.eLcRuntimeFailure if exclusively_ else _EBitMask.IsEnumBitFlagSet(self, _ELcXState.eLcRuntimeFailure)

    @staticmethod
    def IsLcExecutionStateSet(eLcESMask_: _FwIntFlag, eLcESFlag_):
        return _EBitMask.IsEnumBitFlagSet(eLcESMask_, eLcESFlag_)

    @staticmethod
    def AddLcExecutionState(eLcESMask_: _FwIntFlag, eLcESFlag_):
        return _EBitMask.AddEnumBitFlag(eLcESMask_, eLcESFlag_)

    @staticmethod
    def RemoveLcExecutionState(eLcESMask_: _FwIntFlag, eLcESFlag_):
        return _EBitMask.RemoveEnumBitFlag(eLcESMask_, eLcESFlag_)

@unique
class _ELcKpiID(_FwEnum):
    eFwStartRequest             = 2411
    eTextDBFirstFetch           = auto()  
    eTextDBCreate               = auto()  
    eLcConfigStart              = auto()  
    eLcLogIFOperationalStart    = auto()  
    eLcLogIFOperationalEnd      = auto()  
    eLcConfigEnd                = auto()  
    eLcBoostStart               = auto()  
    eLcBoostEnd                 = auto()  
    eLcCustomSetupStart         = auto()  
    eLcCustomSetupEnd           = auto()  
    eMxtStartStart              = auto()  
    eMxtStartEnd                = auto()  
    eMxtStopped                 = auto()  
    eLcShutdownStart            = auto()  
    eLcShutdownEnd              = auto()  
    eLogifCreate                = auto()  
    eLogifDestroy               = auto()  
    eTerminalModeStart          = auto()  
    eTerminalModeEnd            = auto()  
    eAutoStopEnabledStart       = auto()  
    eAutoStopEnabledEnd         = auto()  
    eAutoStopDisabledStart      = auto()  
    eAutoStopDisabledEnd        = auto()  

class _LcXStateDriver(_ProtAbsSlotsObject):
    __slots__ = []

    def __init__(self, ppass_ : int):
        super().__init__(ppass_)

class _LcXStateHistory(_ProtAbsSlotsObject):
    __slots__ = [ '__l' , '__m' ]

    __SSATSM = 0x0000FF

    def __init__(self, ppass_: int):
        super().__init__(ppass_)
        self.__l = _PyRLock()
        self.__m = _ELcXState.ePreConfigPhase

    def __str__(self):
        return self.ToString()

    @property
    def isValid(self):
        return not self.__isInvalid

    @property
    def isFailureFree(self):
        if self.__isInvalid: return True
        with self.__l:
            return self.__m.isFailureFree

    @property
    def hasReachedRuntimePhase(self):
        if self.__isInvalid: return False
        with self.__l:
            return self.__m.IsRuntimePhase()

    @property
    def hasPassedConfigPhase(self):
        return False if self.__isInvalid else self._HasPassedTransitionalExecutionState(_ELcXState.eConfigPhase)

    @property
    def hasPassedBoostPhase(self):
        if self.__isInvalid:
            res = False
        else:
            res = self._HasPassedTransitionalExecutionState(_ELcXState.eFullBoostPhase)
        return res

    @property
    def hasPassedCustomSetupPhase(self):
        return False if self.__isInvalid else self._HasPassedTransitionalExecutionState(_ELcXState.eCustomSetupPhase)

    @property
    def hasPassedSetupPhase(self):
        if self.__isInvalid: return False
        with self.__l:
            return self.__m.hasPassedSetupPhase

    @property
    def hasPassedMxtStartPhase(self):
        if self.__isInvalid: return False
        with self.__l:
            return self.__m.hasPassedMxtStartPhase

    @property
    def hasPassedTeardownPhase(self):
        if self.__isInvalid:
            res = False
        elif not self.hasPassedSetupPhase:
            res = False
        elif not self.__m.hasPassedStopPhase:
            res = False
        else:
            with self.__l:
                res = self.__m.hasPassedShutdownPhase and self.__m.hasPassedJoinPhase
        return res

    @property
    def hasLcSetupFailure(self):
        if self.isFailureFree: return False
        with self.__l:
            return self.__m.hasLcSetupFailure

    @property
    def hasLcRuntimeFailure(self):
        if self.isFailureFree: return False
        with self.__l:
            return self.__m.hasLcRuntimeFailure

    def IsLcExecutionStateSet(self, eExecState_ : _ELcXState):
        res = False
        if self.__isInvalid:
            pass
        elif not isinstance(eExecState_, _ELcXState):
            pass
        else:
            with self.__l:
                res = _ELcXState.IsLcExecutionStateSet(self.__m, eExecState_)
        return res

    def _AddExecutionState(self, eExecState_ : _ELcXState, lcExecStateDriver_ : _LcXStateDriver =None):
        if self.__isInvalid:
            pass
        elif not isinstance(eExecState_, _ELcXState):
            pass
        elif not (eExecState_.isFailureState or isinstance(lcExecStateDriver_, _LcXStateDriver)):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00325)
        else:
            with self.__l:
                if not _ELcXState.IsLcExecutionStateSet(self.__m, eExecState_):
                    self.__m = _ELcXState.AddLcExecutionState(self.__m, eExecState_)

    def _RemoveExecutionState(self, eExecState_ : _ELcXState, lcExecStateDriver_ : _LcXStateDriver =None):
        if self.__isInvalid:
            pass
        elif not isinstance(eExecState_, _ELcXState):
            pass
        elif not (eExecState_.isFailureState or isinstance(lcExecStateDriver_, _LcXStateDriver)):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00326)
        else:
            with self.__l:
                if _ELcXState.IsLcExecutionStateSet(self.__m, eExecState_):
                    self.__m = _ELcXState.RemoveLcExecutionState(self.__m, eExecState_)

    def _HasPassedTransitionalExecutionState(self, eExecState_ : _ELcXState):
        res = False
        if self.__isInvalid:
            pass
        elif not isinstance(eExecState_, _ELcXState):
            pass
        else:
            with self.__l:
                if not (_ELcXState.ePreConfigPhase.value < eExecState_.value < _ELcXState.eJoinPhase.value):
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00327)

                elif eExecState_ == _ELcXState.eRuntimePhase:
                    res = self.hasReachedRuntimePhase

                elif eExecState_.isTransitionalMxtStartPhase:
                    res = eExecState_.IsMxtStartPassed()

                else:
                    res = self.hasPassedSetupPhase
                    if not res:
                        _iCurTransExceStateMask = _LcXStateHistory.__SSATSM & self.__m.value
                        _eCurTransExceStateMask = _ELcXState(_iCurTransExceStateMask)
                        _eLastTransExecState    = _ELcXState(_eCurTransExceStateMask.leftMostBitPosition)
                        res                     = _eLastTransExecState.value > eExecState_.value
        return res

    def _ToString(self):
        if self.__isInvalid:
            return None

        with self.__l:
            if self.__m.IsIdle():
                _hist = self.__m.compactName
            else:
                _INVALID_BIT_POS     = 31
                _UPPER_TRANS_BIT_POS = 16
                _bSeparatorSet       = False
                _hist                = ''

                for _ii in range(_INVALID_BIT_POS):
                    _eExecSt = _ELcXState(0x000001 << _ii)
                    if not _ELcXState.IsLcExecutionStateSet(self.__m, _eExecSt):
                        continue

                    if len(_hist) < 1:
                        _hist = _eExecSt.compactName
                        continue

                    _midPart = None
                    if _ii < _UPPER_TRANS_BIT_POS:
                        _midPart = _FwTDbEngine.GetText(_EFwTextID.eLcXStateHistory_ToString_02)
                    else:
                        if not _bSeparatorSet:
                            _bSeparatorSet = True
                            _hist += _FwTDbEngine.GetText(_EFwTextID.eLcXStateHistory_ToString_03)
                        else:
                            _midPart = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_015)

                    if _midPart is not None:
                        _hist += _midPart

                    _hist += f' {_eExecSt.compactName} '

            res = _FwTDbEngine.GetText(_EFwTextID.eLcXStateHistory_ToString_01).format(type(self).__name__, _hist)
        return res

    def _CleanUpByOwnerRequest(self):
        if self.__isInvalid:
            return

        _hist = str(self)
        self.__l = None
        self.__m = None

    @property
    def __isInvalid(self):
        return self.__l is None

class _LcSetupFailure:
    __slots__ = [ '__m' , '__c' ]

    def __init__(self, errCode_ : Union[_EFwErrorCode, int], errMsg_ : str =None):
        self.__c = None
        self.__m = None
        self._Update(errCode_, errMsg_=errMsg_)

    def __str__(self):
        return self.ToString()

    @property
    def isValid(self) -> bool:
        return self.__c is not None

    @property
    def errorMessage(self) -> str:
        return self.__m

    @property
    def errorCode(self) -> int:
        return self.__c

    def ToString(self):
        if not self.isValid:
            return None

        _prefix = type(self).__name__[1:]
        if self.__c is None:
            res = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_010).format(_prefix)
        else:
            res = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_003).format(_prefix, self.__c)

        _errMsg = self.__m
        if _errMsg is None:
            _errMsg = _CommonDefines._CHAR_SIGN_DASH
        res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_016).format(self.__m)
        return res

    def _Update(self, errCode_ : Union[_EFwErrorCode, int], errMsg_ : str =None):
        if isinstance(errCode_, _EFwErrorCode):
            errCode_ = errCode_.toSInt
        if not (_LogErrorCode.IsValidFwErrorCode(errCode_) and not _LogErrorCode.IsAnonymousErrorCode(errCode_)):
            _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcSetupFailure_TID_003).format(str(errCode_))
            vlogif._LogOEC(True, _EFwErrorCode.FE_LCSF_999)
            errCode_ = _EFwErrorCode.FE_LCSF_999

        _bStrMsg = isinstance(errMsg_, str)
        if not (_bStrMsg and (len(errMsg_.strip()) > 0)):
            if errMsg_ is None:
                errMsg_ = _CommonDefines._CHAR_SIGN_DASH
            elif not _bStrMsg:
                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcSetupFailure_TID_001).format(type(errMsg_).__name__)
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00328)
                errMsg_ = str(errMsg_)
            else:
                errMsg_ = _CommonDefines._CHAR_SIGN_DASH
                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcSetupFailure_TID_002)
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00329)

        self.__c = errCode_
        self.__m = errMsg_

    def _ClearLcFailure(self):
        self.__c = None
        self.__m = None

class _LcFailure:
    __slots__ = [ '__l' , '__sf' , '__nrf' ]

    __bFWLLSM          = False
    __theLcFRC         = None
    __theLcState       = None
    __theLcFailure     = None
    __theLcXStateHist  = None
    __bLcResultPrinted = False

    def __init__(self, lcFailure_ : Union[int, _LcSetupFailure], bIgnoreHist_ =False):
        self.__l   = None
        self.__sf  = None
        self.__nrf = 0

        if _LcFailure.__theLcFailure is not None:
            _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcXStateHistory_TID_001)
            vlogif._XLogFatalEC(_EFwErrorCode.VFE_00332, _errMsg)
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00332)
            return
        if (_LcFailure.__theLcXStateHist is None) and not bIgnoreHist_:
            _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcXStateHistory_TID_002)
            vlogif._XLogFatalEC(_EFwErrorCode.VFE_00333, _errMsg)
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00333)
            return

        _bError = False
        if isinstance(lcFailure_, _LcSetupFailure):
            if not lcFailure_.isValid:
                _bError = True
                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcXStateHistory_TID_003).format(type(lcFailure_).__name__)
                vlogif._XLogFatalEC(_EFwErrorCode.VFE_00334, _errMsg)
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00334)
            else:
                self.__sf = lcFailure_

        elif not (isinstance(lcFailure_, int) and (lcFailure_>0)):
            _bError = True
            _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcXStateHistory_TID_004).format(str(lcFailure_))
            vlogif._XLogFatalEC(_EFwErrorCode.VFE_00335, _errMsg)
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00335)

        else:
            self.__nrf = lcFailure_

        if not _bError:
            self.__l = _PyRLock()
            _LcFailure.__theLcFailure = self

    def __str__(self):
        return self.__ToString()

    @staticmethod
    def IsLcErrorFree():
        if _LcFailure.__theLcXStateHist is None:
            res = _LcFailure.__theLcFailure is None
        else:
            res = _LcFailure.__theLcXStateHist.isFailureFree
        return res

    @staticmethod
    def IsLcNotErrorFree():
        return False if _LcFailure.__theLcXStateHist is None else not _LcFailure.__theLcXStateHist.isFailureFree

    @staticmethod
    def IsConfigPhasePassed():
        return False if _LcFailure.__theLcXStateHist is None else _LcFailure.__theLcXStateHist.hasPassedConfigPhase

    @staticmethod
    def IsSetupPhasePassed():
        return False if _LcFailure.__theLcXStateHist is None else _LcFailure.__theLcXStateHist.hasPassedSetupPhase

    @staticmethod
    def AsStr():
        _lcFailure = _LcFailure.__theLcFailure
        return _CommonDefines._STR_EMPTY if (_lcFailure is None) else str(_lcFailure)

    @staticmethod
    def CheckSetLcSetupFailure(errCode_ : Union[_EFwErrorCode, int], errMsg_ : Union[str, _EFwTextID] =None, bForce_ =False):
        _lcFailure = _LcFailure.__theLcFailure

        if errMsg_ is None:
            errMsg_ = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcFailure_TID_001)
        elif isinstance(errMsg_, _EFwTextID):
            errMsg_ = _FwTDbEngine.GetText(errMsg_)

        if _lcFailure is not None:
            _errMsg = str(errMsg_)
            if errCode_ is not None:
                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_009).format(str(errCode_), errMsg_)

            if not _lcFailure.__isLcSetupFailure:
                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcFailure_TID_003).format(_errMsg)
                vlogif._XLogFatalEC(_EFwErrorCode.VFE_00337, _errMsg)
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00337)
            elif bForce_:
                _lcFailure.__UpdateLcSetupFailure(errCode_, errMsg_=errMsg_)

        else:
            _xstHist = _LcFailure._GetLcXStateHistory()
            if _xstHist is not None:
                if _xstHist.IsLcExecutionStateSet(_ELcXState.eSetupPassed):
                    if not bForce_:
                        _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcFailure_TID_006)
                        vlogif._LogOEC(True, _EFwErrorCode.VFE_00338)

                _xstHist._AddExecutionState(_ELcXState.eLcSetupFailure, None)

            _lcSF = _LcSetupFailure(errCode_, errMsg_=errMsg_)
            if _lcSF.isValid:
                _LcFailure(_lcSF, bIgnoreHist_=_xstHist is None)

                _lcFailure = _LcFailure.__GetInstance()
                if (_lcFailure is None) or not _lcFailure.__isLcSetupFailure:
                    _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcFailure_TID_005)
                    vlogif._XLogFatalEC(_EFwErrorCode.VFE_00339, _errMsg)
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00339)

    @property
    def isValid(self) -> bool:
        return self.__l is not None

    @staticmethod
    def _GetLcFailure() -> Union[LcFailure, None]:
        res  = None
        _lcf = _LcFailure.__theLcFailure
        if _lcf is not None:
            _ff = _lcf.__sf if _lcf.__isLcSetupFailure else _LcFailure.__theLcFRC
            res = LcFailure(str(_LcFailure.__theLcState), _ff.errorMessage, _ff.errorCode)
        return res

    @staticmethod
    def _PrintLcResult(bForcePrint_ =False):
        if _LcFailure.__bLcResultPrinted:
            if not bForcePrint_:
                return

        _lcFailure  = _LcFailure.__GetInstance()
        _bErrorFree = _LcFailure.IsLcErrorFree()

        if (_lcFailure is None) != _bErrorFree:
            _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcFailure_TID_015).format(_StrUtil.ToBool(_lcFailure is None), _StrUtil.ToBool(_bErrorFree))
            vlogif._XLogFatalEC(_EFwErrorCode.VFE_00976, _errMsg)
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00976)
            _bErrorFree = _lcFailure is None

        if _bErrorFree and _LcFailure.__bFWLLSM:
            if not bForcePrint_:
                return

        _LcFailure.__bLcResultPrinted = True

        _cc = _EColorCode.GREEN if _bErrorFree else _EColorCode.RED
        _lt = _ELRType.LR_FREE if _bErrorFree else _ELRType.LR_FTL

        if not _bErrorFree:
            if not _FwTDbEngine.GetCreateStatus().isTDBCreated:
                if _lcFailure.__isLcSetupFailure:
                    _PutLR(str(_lcFailure), color_=_cc, logType_=_lt)
                return

        _dLL = _CommonDefines._DASH_LINE_LONG
        _dLS = _CommonDefines._DASH_LINE_SHORT

        _resStr = _EFwTextID.eMisc_LcResultSuccess if _bErrorFree else _EFwTextID.eMisc_LcResultFailed
        _resStr = _FwTDbEngine.GetText(_resStr)
        _resStr = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcFailure_TID_016).format(_resStr)

        _curLcSt = _LcFailure._GetCurrentLcState()
        if _curLcSt is None:
            if _lcFailure is not None:
                _myTxt   = str(_lcFailure)
                _resStr += f'{_CommonDefines._CHAR_SIGN_LF}{_dLS} {_CommonDefines._CHAR_SIGN_TAB}{_myTxt}'
        else:
            _myTxt   = f'{_CommonDefines._CHAR_SIGN_LF}{_CommonDefines._CHAR_SIGN_TAB}{_curLcSt}'
            _myTxt   = f'{_CommonDefines._CHAR_SIGN_LF}{_dLS} '.join(_myTxt.split(_CommonDefines._CHAR_SIGN_LF))
            _resStr += _myTxt

        _resStr = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcFailure_TID_017).format(_dLL, _resStr, _dLS, _dLL)
        _PutLR(_resStr, color_=_cc, logType_=_lt)

    @staticmethod
    def _ClearInstance():
        if _LcFailure.__theLcFailure is not None:
            _LcFailure.__theLcFailure.__ClearLcFailure()
            _LcFailure.__theLcFailure = None

    @staticmethod
    def _GetCurrentLcFRC() -> _LcFrcView:
        return _LcFailure.__theLcFRC

    @staticmethod
    def _GetCurrentLcState() -> str:
        return _LcFailure.__theLcState

    @staticmethod
    def _SetCurrentLcState(curLcState_ : str, lcFRC_ : _LcFrcView, numFRC_ : int =0):
        _LcFailure.__theLcFRC   = lcFRC_
        _LcFailure.__theLcState = curLcState_
        if lcFRC_ is not None:
            _LcFailure.__UpdateFrcCount(numFRC_)

    @staticmethod
    def _GetLcXStateHistory() -> _LcXStateHistory:
        return _LcFailure.__theLcXStateHist

    @staticmethod
    def _SetLcXStateHistory(eExecStateHistory_ : _LcXStateHistory):
        if isinstance(eExecStateHistory_, _LcXStateHistory):
            _LcFailure.__theLcXStateHist = eExecStateHistory_

    @staticmethod
    def _DepInjection(dinjCmd_ : _EDepInjCmd, bSM_ : bool):
        if dinjCmd_.isInject:
            _LcFailure.__bFWLLSM = bSM_

    @staticmethod
    def __GetInstance():
        return _LcFailure.__theLcFailure

    @property
    def __isLcSetupFailure(self):
        if not self.isValid: return False
        with self.__l:
            return self.__sf is not None

    @property
    def __isLcRuntimeFailure(self):
        if not self.isValid: return False
        with self.__l:
            return self.__nrf > 0

    def __UpdateLcSetupFailure(self, errCode_ : Union[_EFwErrorCode, int], errMsg_ : str =None):
        if not self.isValid:
            return
        if not self.__isLcSetupFailure:
            _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcFailure_TID_011)
            vlogif._XLogFatalEC(_EFwErrorCode.VFE_00343, _errMsg)
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00343)
            return

        with self.__l:
            self.__sf._Update(errCode_, errMsg_=errMsg_)

    @staticmethod
    def __UpdateFrcCount(numFRC_ : int):
       _lcFailure = _LcFailure.__theLcFailure

       if _lcFailure is not None:
           if not _lcFailure.__isLcRuntimeFailure:
               _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcFailure_TID_007)
               vlogif._XLogFatalEC(_EFwErrorCode.VFE_00977, _errMsg)
               vlogif._LogOEC(True, _EFwErrorCode.VFE_00977)
           elif numFRC_ < 1:
               _lcFailure.__ClearLcFailure()
               _LcFailure.__theLcFailure = None
           else:
               _lcFailure.__nrf = numFRC_

       else:
           _xstHist = _LcFailure._GetLcXStateHistory()
           if _xstHist is not None:
               _xstHist._AddExecutionState(_ELcXState.eLcRuntimeFailure, None)

           _LcFailure(numFRC_)
           _lcFailure = _LcFailure.__GetInstance()

           if (_lcFailure is None) or not _lcFailure.__isLcRuntimeFailure:
               _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcFailure_TID_010)
               vlogif._XLogFatalEC(_EFwErrorCode.VFE_00978, _errMsg)
               vlogif._LogOEC(True, _EFwErrorCode.VFE_00978)
           elif not _lcFailure.isValid:
               _lcFailure.__ClearLcFailure()
               _LcFailure.__theLcFailure = None

    def __ToString(self) -> str:
        if not self.isValid:
            return _CommonDefines._STR_EMPTY

        with self.__l:
            if self.__isLcSetupFailure:
                res = self.__sf.ToString()
            else:
                res = str(_LcFailure.__theLcState)
            return res

    def __ClearLcFailure(self):
        if not self.isValid:
            return

        if self.__isLcSetupFailure:
            self.__sf._ClearLcFailure()
            self.__sf = None
        self.__l   = None
        self.__nrf = None
