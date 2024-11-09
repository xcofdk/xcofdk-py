# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : lcexecstate.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from enum      import auto
from enum      import unique
from threading import RLock as _PyRLock

from xcofdk._xcofw.fw.fwssys.fwcore.logging            import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.logging.flattendfe import _FlattendFatalError
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcdefines       import _LcConfig
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcdefines       import _LcFrcView
from xcofdk._xcofw.fw.fwssys.fwcore.types.ebitmask     import _EBitMask
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes  import _FwEnum
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes  import _FwIntFlag
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes  import _CommonDefines
from xcofdk._xcofw.fw.fwssys.fwcore.types.apobject     import _ProtectedAbstractSlotsObject

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine


@unique
class _ELcExecutionState(_FwIntFlag):

    eIdle               = 0x000000

    ePreConfigPhase     = (0x000001 <<  0)
    eConfigPhase        = (0x000001 <<  1)
    eSemiBoostPhase     = (0x000001 <<  2)
    eFullBoostPhase     = (0x000001 <<  3)
    eCustomSetupPhase   = (0x000001 <<  4)
    eRuntimePhase       = (0x000001 <<  5)
    eMxuAutoStartPhase  = (0x000001 <<  6)
    eMxuPostStartPhase  = (0x000001 <<  7)

    eJoinPhase          = (0x000001 <<  8)
    eStopPhase          = (0x000001 <<  9)
    eShutdownPhase      = (0x000001 << 10)

    eSetupPassed        = (0x000001 << 16)
    eMxuStartPassed     = (0x000001 << 17)
    eShutdownPassed     = (0x000001 << 18)
    eStopPassed         = (0x000001 << 19)
    eJoinPassed         = (0x000001 << 20)

    eLcSetupFailure     = (0x000001 << 28)
    eLcRuntimeFailure   = (0x000001 << 29)


    @property
    def isErrorFree(self):
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
    def isTransitionalMxuStartPhase(self):
        return self.IsMxuAutoStartPhase(exclusively_=True) or self.IsMxuPostStartPhase(exclusively_=True)

    @property
    def isFailureState(self):
        return self.IsLcSetupFailure(exclusively_=True) or self.IsLcRuntimeFailure(exclusively_=True)

    @property
    def hasPassedSetupPhase(self):
        return self.IsSetupPassed()

    @property
    def hasPassedMxuStartPhase(self):
        return self.IsMxuStartPassed()

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
        return self == _ELcExecutionState.eIdle

    def IsPreConfigPhase(self, exclusively_ =False):
        return self == _ELcExecutionState.ePreConfigPhase if exclusively_ else _EBitMask.IsEnumBitFlagSet(self, _ELcExecutionState.ePreConfigPhase)

    def IsConfigPhase(self, exclusively_ =False):
        return self == _ELcExecutionState.eConfigPhase if exclusively_ else _EBitMask.IsEnumBitFlagSet(self, _ELcExecutionState.eConfigPhase)

    def IsSemiBoostPhase(self, exclusively_ =False):
        return self == _ELcExecutionState.eSemiBoostPhase if exclusively_ else _EBitMask.IsEnumBitFlagSet(self, _ELcExecutionState.eSemiBoostPhase)

    def IsFullBoostPhase(self, exclusively_ =False):
        return self == _ELcExecutionState.eFullBoostPhase if exclusively_ else _EBitMask.IsEnumBitFlagSet(self, _ELcExecutionState.eFullBoostPhase)

    def IsCustomSetupPhase(self, exclusively_ =False):
        return self == _ELcExecutionState.eCustomSetupPhase if exclusively_ else _EBitMask.IsEnumBitFlagSet(self, _ELcExecutionState.eCustomSetupPhase)

    def IsMxuAutoStartPhase(self, exclusively_ =False):
        return self == _ELcExecutionState.eMxuAutoStartPhase if exclusively_ else _EBitMask.IsEnumBitFlagSet(self, _ELcExecutionState.eMxuAutoStartPhase)

    def IsRuntimePhase(self, exclusively_ =False):
        return self == _ELcExecutionState.eRuntimePhase if exclusively_ else _EBitMask.IsEnumBitFlagSet(self, _ELcExecutionState.eRuntimePhase)

    def IsMxuPostStartPhase(self, exclusively_ =False):
        return self == _ELcExecutionState.eMxuPostStartPhase if exclusively_ else _EBitMask.IsEnumBitFlagSet(self, _ELcExecutionState.eMxuPostStartPhase)

    def IsJoinPhase(self, exclusively_ =False):
        return self == _ELcExecutionState.eJoinPhase if exclusively_ else _EBitMask.IsEnumBitFlagSet(self, _ELcExecutionState.eJoinPhase)

    def IsStopPhase(self, exclusively_ =False):
        return self == _ELcExecutionState.eStopPhase if exclusively_ else _EBitMask.IsEnumBitFlagSet(self, _ELcExecutionState.eStopPhase)

    def IsShutdownPhase(self, exclusively_ =False):
        return self == _ELcExecutionState.eShutdownPhase if exclusively_ else _EBitMask.IsEnumBitFlagSet(self, _ELcExecutionState.eShutdownPhase)

    def IsSetupPassed(self, exclusively_ =False):
        return self == _ELcExecutionState.eSetupPassed if exclusively_ else _EBitMask.IsEnumBitFlagSet(self, _ELcExecutionState.eSetupPassed)

    def IsMxuStartPassed(self, exclusively_ =False):
        return self == _ELcExecutionState.eMxuStartPassed if exclusively_ else _EBitMask.IsEnumBitFlagSet(self, _ELcExecutionState.eMxuStartPassed)

    def IsShutdownPassed(self, exclusively_ =False):
        return self == _ELcExecutionState.eShutdownPassed if exclusively_ else _EBitMask.IsEnumBitFlagSet(self, _ELcExecutionState.eShutdownPassed)

    def IsStopPassed(self, exclusively_ =False):
        return self == _ELcExecutionState.eStopPassed if exclusively_ else _EBitMask.IsEnumBitFlagSet(self, _ELcExecutionState.eStopPassed)

    def IsJoinPassed(self, exclusively_ =False):
        return self == _ELcExecutionState.eJoinPassed if exclusively_ else _EBitMask.IsEnumBitFlagSet(self, _ELcExecutionState.eJoinPassed)

    def IsLcSetupFailure(self, exclusively_ =False):
        return self == _ELcExecutionState.eLcSetupFailure if exclusively_ else _EBitMask.IsEnumBitFlagSet(self, _ELcExecutionState.eLcSetupFailure)

    def IsLcRuntimeFailure(self, exclusively_ =False):
        return self == _ELcExecutionState.eLcRuntimeFailure if exclusively_ else _EBitMask.IsEnumBitFlagSet(self, _ELcExecutionState.eLcRuntimeFailure)

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
    eMxuStartStart              = auto()  
    eMxuStartEnd                = auto()  
    eMxuStopped                 = auto()  
    eLcShutdownStart            = auto()  
    eLcShutdownEnd              = auto()  
    eLogifCreate                = auto()  
    eLogifDestroy               = auto()  


class _LcExecutionStateDriver(_ProtectedAbstractSlotsObject):
    __slots__ = []

    def __init__(self, ppass_ : int):
        super().__init__(ppass_)


class _LcExecutionStateHistory(_ProtectedAbstractSlotsObject):

    __slots__ = [ '__lck' , '__eHistMask' ]

    __START_SUCCEEDED_ALL_TRANSITIONAL_STATES_MASK = 0x0000FF


    def __init__(self, ppass_: int):
        super().__init__(ppass_)
        self.__lck       = _PyRLock()
        self.__eHistMask = _ELcExecutionState.ePreConfigPhase

    def __str__(self):
        return self.ToString()

    @property
    def isValid(self):
        return not self.__isInvalid

    @property
    def isErrorFree(self):
        if self.__isInvalid: return True
        with self.__lck:
            return self.__eHistMask.isErrorFree

    @property
    def hasReachedRuntimePhase(self):
        if self.__isInvalid: return False
        with self.__lck:
            return self.__eHistMask.IsRuntimePhase()

    @property
    def hasPassedConfigPhase(self):
        return False if self.__isInvalid else self._HasPassedTransitionalExecutionState(_ELcExecutionState.eConfigPhase)

    @property
    def hasPassedBoostPhase(self):
        if self.__isInvalid:
            res = False
        else:
            res = self._HasPassedTransitionalExecutionState(_ELcExecutionState.eFullBoostPhase)
        return res

    @property
    def hasPassedCustomSetupPhase(self):
        return False if self.__isInvalid else self._HasPassedTransitionalExecutionState(_ELcExecutionState.eCustomSetupPhase)

    @property
    def hasPassedSetupPhase(self):
        if self.__isInvalid: return False
        with self.__lck:
            return self.__eHistMask.hasPassedSetupPhase

    @property
    def hasPassedMxuStartPhase(self):
        if self.__isInvalid: return False
        with self.__lck:
            return self.__eHistMask.hasPassedMxuStartPhase

    @property
    def hasPassedTeardownPhase(self):
        if self.__isInvalid:
            res = False
        elif not self.hasPassedSetupPhase:
            res = False
        elif not self.__eHistMask.hasPassedStopPhase:
            res = False
        else:
            with self.__lck:
                res = self.__eHistMask.hasPassedShutdownPhase and self.__eHistMask.hasPassedJoinPhase
        return res

    @property
    def hasLcSetupFailure(self):
        if self.isErrorFree: return False
        with self.__lck:
            return self.__eHistMask.hasLcSetupFailure

    @property
    def hasLcRuntimeFailure(self):
        if self.isErrorFree: return False
        with self.__lck:
            return self.__eHistMask.hasLcRuntimeFailure

    def IsLcExecutionStateSet(self, eExecState_ : _ELcExecutionState):
        res = False
        if self.__isInvalid:
            pass
        elif not isinstance(eExecState_, _ELcExecutionState):
            pass
        else:
            with self.__lck:
                res = _ELcExecutionState.IsLcExecutionStateSet(self.__eHistMask, eExecState_)
        return res

    def _AddExecutionState(self, eExecState_ : _ELcExecutionState, lcExecStateDriver_ : _LcExecutionStateDriver =None):
        if self.__isInvalid:
            pass
        elif not isinstance(eExecState_, _ELcExecutionState):
            pass
        elif not (eExecState_.isFailureState or isinstance(lcExecStateDriver_, _LcExecutionStateDriver)):
            vlogif._LogOEC(True, -1536)
        else:
            with self.__lck:
                if not _ELcExecutionState.IsLcExecutionStateSet(self.__eHistMask, eExecState_):
                    self.__eHistMask = _ELcExecutionState.AddLcExecutionState(self.__eHistMask, eExecState_)

    def _RemoveExecutionState(self, eExecState_ : _ELcExecutionState, lcExecStateDriver_ : _LcExecutionStateDriver =None):
        if self.__isInvalid:
            pass
        elif not isinstance(eExecState_, _ELcExecutionState):
            pass
        elif not (eExecState_.isFailureState or isinstance(lcExecStateDriver_, _LcExecutionStateDriver)):
            vlogif._LogOEC(True, -1537)
        else:
            with self.__lck:
                if _ELcExecutionState.IsLcExecutionStateSet(self.__eHistMask, eExecState_):
                    self.__eHistMask = _ELcExecutionState.RemoveLcExecutionState(self.__eHistMask, eExecState_)

    def _HasPassedTransitionalExecutionState(self, eExecState_ : _ELcExecutionState):
        res = False
        if self.__isInvalid:
            pass
        elif not isinstance(eExecState_, _ELcExecutionState):
            pass
        else:
            with self.__lck:
                if not (_ELcExecutionState.ePreConfigPhase.value < eExecState_.value < _ELcExecutionState.eJoinPhase.value):
                    vlogif._LogOEC(True, -1538)

                elif eExecState_ == _ELcExecutionState.eRuntimePhase:
                    res = self.hasReachedRuntimePhase

                elif eExecState_.isTransitionalMxuStartPhase:
                    res = eExecState_.IsMxuStartPassed()

                else:
                    res = self.hasPassedSetupPhase
                    if not res:
                        _iCurTransExceStateMask = _LcExecutionStateHistory.__START_SUCCEEDED_ALL_TRANSITIONAL_STATES_MASK & self.__eHistMask.value
                        _eCurTransExceStateMask = _ELcExecutionState(_iCurTransExceStateMask)
                        _eLastTransExecState    = _ELcExecutionState(_eCurTransExceStateMask.leftMostBitPosition)
                        res                     = _eLastTransExecState.value > eExecState_.value
        return res

    def _ToString(self):
        if self.__isInvalid:
            return None

        with self.__lck:
            if self.__eHistMask.IsIdle():
                _hist = self.__eHistMask.compactName
            else:
                _INVALID_BIT_POS     = 31
                _UPPER_TRANS_BIT_POS = 16
                _bSeparatorSet       = False
                _hist                = ''

                for _ii in range(_INVALID_BIT_POS):
                    _eExecSt = _ELcExecutionState(0x000001 << _ii)
                    if not _ELcExecutionState.IsLcExecutionStateSet(self.__eHistMask, _eExecSt):
                        continue

                    if len(_hist) < 1:
                        _hist = _eExecSt.compactName
                        continue

                    _midPart = None
                    if _ii < _UPPER_TRANS_BIT_POS:
                        _midPart = _FwTDbEngine.GetText(_EFwTextID.eELcExecutionStateHistory_ToString_02)
                    else:
                        if not _bSeparatorSet:
                            _bSeparatorSet = True
                            _midPart2 = _FwTDbEngine.GetText(_EFwTextID.eELcExecutionStateHistory_ToString_03)
                            _hist += _midPart2
                        else:
                            _midPart = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_015)

                    if _midPart is not None:
                        _hist += _midPart

                    _hist += f' {_eExecSt.compactName} '

            res = _FwTDbEngine.GetText(_EFwTextID.eELcExecutionStateHistory_ToString_01).format(type(self).__name__, _hist)
        return res

    def _CleanUpByOwnerRequest(self):
        if self.__isInvalid:
            return

        _hist = str(self)
        self.__lck       = None
        self.__eHistMask = None

    @property
    def __isInvalid(self):
        return self.__lck is None


class _LcSetupFailure:

    __slots__ = [ '__errMsg' , '__errCode' ]

    def __init__(self, errMsg_ : str, errCode_ : int =None):
        self.__errMsg  = None
        self.__errCode = None

        self._Update(errMsg_, errCode_=errCode_)

    def __str__(self):
        return self.ToString()

    @property
    def isValid(self) -> bool:
        return self.__errMsg is not None

    @property
    def errorMessage(self) -> str:
        return self.__errMsg

    @property
    def errorCode(self) -> int:
        return self.__errCode

    def ToString(self, bCompact_ =False):
        if not self.isValid:
            return None

        res = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_010).format(type(self).__name__)
        if self.__errCode is not None:
            res += _FwTDbEngine.GetText(_EFwTextID.eLcSetupFailure_ToString_01).format(self.__errCode)
        res += _FwTDbEngine.GetText(_EFwTextID.eLcSetupFailure_ToString_02).format(self.__errMsg)
        return res

    def _Update(self, errMsg_: str, errCode_: int = None):
        if not isinstance(errMsg_, str):
            _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcSetupFailure_TextID_001).format(type(errMsg_).__name__)
            vlogif._XLogFatal(_errMsg)
            vlogif._LogOEC(True, -1539)
        elif len(errMsg_.strip()) == 0:
            _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcSetupFailure_TextID_002)
            vlogif._XLogFatal(_errMsg)
            vlogif._LogOEC(True, -1540)
        elif (errCode_ is not None) and not (isinstance(errCode_, int) and errCode_ > 0):
            _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcSetupFailure_TextID_003).format(str(errCode_))
            vlogif._XLogFatal(_errMsg)
            vlogif._LogOEC(True, -1541)
        else:
            self.__errMsg  = errMsg_
            self.__errCode = errCode_

    def _ClearLcFailure(self):
        self.__errMsg  = None
        self.__errCode = None


class _LcRuntimeFailure:

    __slots__ = [ '__frcStrC' , '__frcStrV' , '__flFE']

    __bDEFAULT_STR_MODE_VERBOSE = True

    def __init__(self, frcView_ : _LcFrcView):
        self.__flFE    = None
        self.__frcStrC = None
        self.__frcStrV = None

        if not (isinstance(frcView_, _LcFrcView) and frcView_.isValid):
            _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcRuntimeFailure_TextID_001).format(type(frcView_).__name__)
            vlogif._XLogFatal(_errMsg)
            vlogif._LogOEC(True, -1542)
        else:
            self.__flFE = _FlattendFatalError(frcView_.fatalErrorClone, bForeignFE_=frcView_.isForeignFatalError)
            if not self.__flFE.isValid:
                self.__flFE = None
                vlogif._LogOEC(True, -1543)
            else:
                self.__frcStrC = frcView_.ToString(bVerbose_=False)
                self.__frcStrV = frcView_.ToString(bVerbose_=True)

                frcView_.CleanUp()

    def __str__(self):
        return self.ToString()

    @property
    def isValid(self) -> bool:
        return self.__flFE is not None

    def ToString(self, bCompact_ =False):
        if not self.isValid:
            return None

        _bVerbose = _LcRuntimeFailure.__bDEFAULT_STR_MODE_VERBOSE
        if _bVerbose:
            if self.__flFE.eErrorImpact.isFatalErrorImpactDueToExecutionApiReturn:
                _bVerbose = False
            elif bCompact_:
                _bVerbose = False
        return self.__frcStrV if _bVerbose else self.__frcStrC

    @property
    def _flattendFatalError(self) -> _FlattendFatalError:
        return self.__flFE

    def _ClearLcFailure(self):
        if not self.isValid:
            return

        self.__flFE    = None
        self.__frcStrC = None
        self.__frcStrV = None


class _LcFailure:

    __slots__ = [ '__apiLck' , '__lcSF' , '__lstRF' ]

    __theLcFRC            = None
    __theLcState          = None
    __theLcFailure        = None
    __theLcExecStateHist  = None
    __bLcResultPrintedOut = False

    def __init__(self, lcFailure_ : [list, _LcSetupFailure]):
        self.__lcSF   = None
        self.__lstRF  = None
        self.__apiLck = None

        if _LcFailure.__theLcFailure is not None:
            _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcExecutionStateHistory_TextID_001)
            vlogif._XLogFatal(_errMsg)
            vlogif._LogOEC(True, -1544)
            return
        if _LcFailure.__theLcExecStateHist is None:
            _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcExecutionStateHistory_TextID_002)
            vlogif._XLogFatal(_errMsg)
            vlogif._LogOEC(True, -1545)
            return

        bError = False
        if isinstance(lcFailure_, _LcSetupFailure):
            if not lcFailure_.isValid:
                bError = True
                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcExecutionStateHistory_TextID_003).format(type(lcFailure_).__name__)
                vlogif._XLogFatal(_errMsg)
                vlogif._LogOEC(True, -1546)
            else:
                self.__lcSF = lcFailure_

        elif not isinstance(lcFailure_, list):
            bError = True
            _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcExecutionStateHistory_TextID_004).format(type(lcFailure_).__name__)
            vlogif._XLogFatal(_errMsg)
            vlogif._LogOEC(True, -1547)

        else:
            for _ee in lcFailure_:
                if not (isinstance(_ee, _LcRuntimeFailure) and _ee.isValid):
                    bError = True
                    _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcExecutionStateHistory_TextID_005).format(str(_ee))
                    vlogif._XLogFatal(_errMsg)
                    vlogif._LogOEC(True, -1548)
                    break
                continue

            if not bError:
                self.__lstRF = lcFailure_

        if not bError:
            self.__apiLck = _PyRLock()
            _LcFailure.__theLcFailure = self

    def __str__(self):
        return self.ToString()

    @staticmethod
    def IsLcErrorFree():
        return True if _LcFailure.__theLcExecStateHist is None else _LcFailure.__theLcExecStateHist.isErrorFree

    @staticmethod
    def IsLcNotErrorFree():
        return False if _LcFailure.__theLcExecStateHist is None else not _LcFailure.__theLcExecStateHist.isErrorFree

    @staticmethod
    def IsConfigPhasePassed():
        return False if _LcFailure.__theLcExecStateHist is None else _LcFailure.__theLcExecStateHist.hasPassedConfigPhase

    @staticmethod
    def IsSetupPhasePassed():
        return False if _LcFailure.__theLcExecStateHist is None else _LcFailure.__theLcExecStateHist.hasPassedSetupPhase

    @staticmethod
    def GetInstance():
        return _LcFailure.__theLcFailure

    @staticmethod
    def CheckSetLcSetupFailure(errMsg_ : str =None, errCode_ : int =None, bForce_ =False):
        _theLcFailure = _LcFailure.__theLcFailure

        if errMsg_ is None:
            errMsg_ = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcFailure_TextID_001)

        if _theLcFailure is not None:
            _paramsStr = errMsg_
            if errCode_ is not None:
                _paramsStr = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcFailure_TextID_002).format(str(errCode_), errMsg_)

            if not _theLcFailure.isLcSetupFailure:
                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcFailure_TextID_003).format(_paramsStr)
                vlogif._XLogFatal(_errMsg)
                vlogif._LogOEC(True, -1549)
            elif not bForce_:
                pass
            else:
                _theLcFailure.__UpdateLcSetupFailure(errMsg_, errCode_=errCode_)

        else:
            _theExecState = _LcFailure._GetLcExecutionStateHistory()
            if _theExecState is not None:
                if _theExecState.IsLcExecutionStateSet(_ELcExecutionState.eSetupPassed):
                    if not bForce_:
                        _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcFailure_TextID_006)
                        vlogif._LogOEC(True, -1550)

                _theExecState._AddExecutionState(_ELcExecutionState.eLcSetupFailure, None)

            _lcSF = _LcSetupFailure(errMsg_, errCode_=errCode_)
            if not _lcSF.isValid:
                pass
            else:
                _LcFailure(_lcSF)

                _theLcFailure = _LcFailure.GetInstance()
                if (_theLcFailure is None) or not _theLcFailure.isLcSetupFailure:
                    _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcFailure_TextID_005)
                    vlogif._XLogFatal(_errMsg)
                    vlogif._LogOEC(True, -1551)

    @staticmethod
    def UpdateLcRuntimeFailure(lstRuntimeFailures_ : list):
        _theLcFailure = _LcFailure.__theLcFailure

        if _theLcFailure is not None:
            if not _theLcFailure.isLcRuntimeFailure:
                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcFailure_TextID_007)
                vlogif._XLogFatal(_errMsg)
                vlogif._LogOEC(True, -1552)
            elif not _theLcFailure.__UpdateLcRuntimeFailure(lstRuntimeFailures_):
                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcFailure_TextID_008)
                vlogif._XLogFatal(_errMsg)
                vlogif._LogOEC(True, -1553)

        else:
            _theExecState = _LcFailure._GetLcExecutionStateHistory()
            if _theExecState is not None:
                _theExecState._AddExecutionState(_ELcExecutionState.eLcRuntimeFailure, None)

            if not _LcFailure(lstRuntimeFailures_).isValid:
                pass
            else:
                _theLcFailure = _LcFailure.GetInstance()
                if (_theLcFailure is None) or not _theLcFailure.isLcRuntimeFailure:
                    _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcFailure_TextID_010)
                    vlogif._XLogFatal(_errMsg)
                    vlogif._LogOEC(True, -1554)

    @property
    def isValid(self) -> bool:
        return self.__apiLck is not None

    @property
    def isLcSetupFailure(self):
        if not self.isValid: return False
        with self.__apiLck:
            return self.__lcSF is not None

    @property
    def isLcRuntimeFailure(self):
        if not self.isValid: return False
        with self.__apiLck:
            return self.__lstRF is not None

    @property
    def lcRuntimeFailuresCount(self):
        if not self.isValid: return 0
        with self.__apiLck:
            return 0 if self.__lstRF is None else len(self.__lstRF)

    def ToString(self, bCompact_ =False) -> str:
        if not self.isValid:
            return _CommonDefines._STR_EMPTY

        with self.__apiLck:
            if self.isLcSetupFailure:
                res = self.__lcSF.ToString(bCompact_=bCompact_)
            else:
                res = _FwTDbEngine.GetText(_EFwTextID.eLcFailure_ToString_01)
                _NUM = len(self.__lstRF)
                for _ii in range(_NUM):
                    if _ii > 0:
                        if _ii==1:
                            res += _FwTDbEngine.GetText(_EFwTextID.eLcFailure_ToString_02)
                        res += _FwTDbEngine.GetText(_EFwTextID.eLcFailure_ToString_03).format(_ii)
                    res += self.__lstRF[_ii].ToString(bCompact_=bCompact_)
            return res


    @staticmethod
    def _PrintLcResult(bReinforcePrint_ =False):
        __MIN_RUNTIME_FAILURES = 1

        if _LcFailure.__bLcResultPrintedOut:
            if not bReinforcePrint_:
                return

        _LcFailure.__bLcResultPrintedOut = True

        _errMsg       = None
        _bErrorFree   = _LcFailure.IsLcErrorFree()
        _theLcFailure = _LcFailure.GetInstance()

        if not _bErrorFree:
            if not _FwTDbEngine.GetCreateStatus().isTDBCreated:
                if _theLcFailure is not None:
                    if _theLcFailure._lcSetupFailure is not None:
                        print(_theLcFailure._lcSetupFailure.errorMessage)
                return

            if _theLcFailure is not None:
                if _theLcFailure.isLcSetupFailure:
                    _bPrintDetails = True
                elif _theLcFailure.lcRuntimeFailuresCount >= __MIN_RUNTIME_FAILURES:
                    _bPrintDetails = True
                else:
                    _bPrintDetails = False

                if _bPrintDetails:
                    _myTxt = str(_theLcFailure)
                    _myTxt = f'\n{_CommonDefines._DASH_LINE_SHORT} '.join(_myTxt.split(_CommonDefines._CHAR_SIGN_NEWLINE))

                    _errMsg  = _FwTDbEngine.GetText(_EFwTextID.eLcFailure_PrintLcResult_FmtStr_02).format(_CommonDefines._DASH_LINE_SHORT)
                    _errMsg += f'{_CommonDefines._DASH_LINE_SHORT} {_myTxt}'

        _resStr = _EFwTextID.eMisc_LcResultSuccess if _bErrorFree else _EFwTextID.eMisc_LcResultFailed
        _resStr = _FwTDbEngine.GetText(_resStr)
        _resStr = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcFailure_TextID_015).format(_resStr)

        if _LcFailure._GetCurrentLcState() is not None:
            _myTxt = str(_LcFailure._GetCurrentLcState())
            _myTxt = f'\n{_CommonDefines._DASH_LINE_SHORT} '.join(_myTxt.split(_CommonDefines._CHAR_SIGN_NEWLINE))
            _resStr += _FwTDbEngine.GetText(_EFwTextID.eLcFailure_PrintLcResult_FmtStr_01).format(_CommonDefines._DASH_LINE_SHORT, _myTxt)

        print()
        print(_CommonDefines._DASH_LINE_LONG)
        print(_FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_001).format(_CommonDefines._DASH_LINE_SHORT, _resStr))
        print(_CommonDefines._DASH_LINE_SHORT)
        if _errMsg is not None:
            print(_errMsg)
            print(_CommonDefines._DASH_LINE_SHORT)
        print(_CommonDefines._DASH_LINE_LONG)
        print()

    @staticmethod
    def _ClearInstance():
        if _LcFailure.__theLcFailure is not None:
            _LcFailure.__theLcFailure._ClearLcFailure()
            _LcFailure.__theLcFailure = None

    @staticmethod
    def _GetCurrentLcFRC() -> _LcFrcView:
        return _LcFailure.__theLcFRC

    @staticmethod
    def _GetCurrentLcState():
        return _LcFailure.__theLcState

    @staticmethod
    def _SetCurrentLcState(curLcState_ : str, lcFRC_ : _LcFrcView):
        _LcFailure.__theLcFRC   = lcFRC_
        _LcFailure.__theLcState = curLcState_

    @staticmethod
    def _GetLcExecutionStateHistory() -> _LcExecutionStateHistory:
        return _LcFailure.__theLcExecStateHist

    @staticmethod
    def _SetLcExecutionStateHistory(eExecStateHistory_ : _LcExecutionStateHistory):
        if isinstance(eExecStateHistory_, _LcExecutionStateHistory):
            _LcFailure.__theLcExecStateHist = eExecStateHistory_

    @property
    def _lcSetupFailure(self) -> _LcSetupFailure:
        return None if not self.isLcSetupFailure else self.__lcSF

    @property
    def _lcRuntimeFailuresList(self) -> list:
        return None if not self.isLcRuntimeFailure else self.__lstRF

    def _ClearLcFailure(self):
        if not self.isValid:
            return

        if self.isLcSetupFailure:
            self.__lcSF._ClearLcFailure()
            self.__lcSF = None
        else:
            for _ee in self.__lstRF:
                _ee._ClearLcFailure()
            self.__lstRF.clear()
            self.__lstRF = None
        self.__apiLck = None

    def __UpdateLcSetupFailure(self, errMsg_ : str, errCode_ : int =None):
        if not self.isValid:
            return
        if not self.isLcSetupFailure:
            _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcFailure_TextID_011)
            vlogif._XLogFatal(_errMsg)
            vlogif._LogOEC(True, -1555)
            return

        with self.__apiLck:
            self.__lcSF._Update(errMsg_, errCode_=errCode_)

    def __UpdateLcRuntimeFailure(self, lstRuntimeFailures_: list):
        if not self.isValid:
            return False
        if self.isLcSetupFailure:
            _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcFailure_TextID_012)
            vlogif._XLogFatal(_errMsg)
            vlogif._LogOEC(True, -1556)
            return False

        with self.__apiLck:
            if not isinstance(lstRuntimeFailures_, list):
                _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcFailure_TextID_013).format(type(lstRuntimeFailures_).__name__)
                vlogif._XLogFatal(_errMsg)
                vlogif._LogOEC(True, -1557)
                return False

            for _ee in lstRuntimeFailures_:
                if not (isinstance(_ee, _LcRuntimeFailure) and _ee.isValid):
                    _errMsg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_LcFailure_TextID_014).format(str(_ee))
                    vlogif._XLogFatal(_errMsg)
                    vlogif._LogOEC(True, -1558)
                    return False
                continue

            self.__lstRF = lstRuntimeFailures_
            return True
