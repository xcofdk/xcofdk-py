# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xprocesstarget.py
#
# Copyright(c) 2024 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum import auto
from enum import unique
from enum import IntEnum

from sys import exit as _PyExitByMainThread

from xcofdk.fwcom.xmpdefs import EXPMPreDefinedID
from xcofdk.fwcom.xmpdefs import ChildProcessResultData

from xcofdk._xcofw.fw.fwssys.fwmp.fwrte.fwrtetoken  import _FwRteToken
from xcofdk._xcofw.fw.fwssys.fwmp.fwrte.fwrtedataex import _FwRteDataExchange

@unique
class _EProcessTargetExitCodeID(IntEnum):
    eSuccess = EXPMPreDefinedID.ProcessExitCodeSuccess.value
    eErrorExitCode_UserDefined               = EXPMPreDefinedID.MaxUserDefinedProcessExitCode
    eErrorExitCode_Unexpected                = EXPMPreDefinedID.UnexpectedUserDefinedProcessExitCode
    eErrorExitCode_InvalidXprocessTarget     = auto()
    eErrorExitCode_RteDataDes                = auto()
    eErrorExitCode_AttchToChildProcess       = auto()
    eErrorExitCode_ExceptionByTargetCallback = auto()
    eErrorExitCode_OpenRteToken              = auto()
    eErrorExitCode_WriteRteToken             = auto()

    @staticmethod
    def FromExitCode(exitCode_ : int):
        if not (isinstance(exitCode_, int) and EXPMPreDefinedID.ProcessExitCodeSuccess.value <= exitCode_ <EXPMPreDefinedID.MaxUserDefinedProcessExitCode.value):
            res = _EProcessTargetExitCodeID.eErrorExitCode_Unexpected
        else:
            res = _EProcessTargetExitCodeID(exitCode_)
        return res

    def compactName(self):
        return self.name[1:]

    @property
    def isSuccess(self):
        return self == _EProcessTargetExitCodeID.eSuccess

    @property
    def isInvalidXprocessTargetErro(self):
        return self == _EProcessTargetExitCodeID.eErrorExitCode_InvalidXprocessTarget

    @property
    def isUserDefined(self):
        return self == _EProcessTargetExitCodeID.eErrorExitCode_UserDefined

    @property
    def isRteDataDesError(self):
        return self == _EProcessTargetExitCodeID.eErrorExitCode_RteDataDes

    @property
    def isAttchToChildProcessError(self):
        return self == _EProcessTargetExitCodeID.eErrorExitCode_AttchToChildProcess

    @property
    def isExceptionByTargetCallbackError(self):
        return self == _EProcessTargetExitCodeID.eErrorExitCode_ExceptionByTargetCallback

    @property
    def isOpenRteTokenError(self):
        return self == _EProcessTargetExitCodeID.eErrorExitCode_OpenRteToken

    @property
    def isWriteRteTokenError(self):
        return self == _EProcessTargetExitCodeID.eErrorExitCode_WriteRteToken

class _XProcessTarget:
    __slots__ = [ '__hprocTgt' ]

    def __init__(self, hpTarget_):
        self.__hprocTgt = hpTarget_

    def __call__(self, rteDataExchange_ : _FwRteDataExchange, *args_, **kwargs_):
        return self.__CallChildProcessTarget(rteDataExchange_)

    def isValid(self):
        return self.__hprocTgt is not None

    @staticmethod
    def __PrintInfo(info_ : str):
        print(info_)

    def __CallChildProcessTarget(self, rteDataExchange_ : _FwRteDataExchange):
        if not self.isValid:
            _PyExitByMainThread(_EProcessTargetExitCodeID.eErrorExitCode_InvalidXprocessTarget.value)

        _rteDataEx = rteDataExchange_
        if not (isinstance(_rteDataEx, _FwRteDataExchange) and _rteDataEx.isValid):
            _PyExitByMainThread(_EProcessTargetExitCodeID.eErrorExitCode_RteDataDes.value)

        if not _rteDataEx.AttchToChildProcess():
            _XProcessTarget.__PrintInfo(f'[XPTgt] {_rteDataEx.currentWarningMessage}')
            _PyExitByMainThread(_EProcessTargetExitCodeID.eErrorExitCode_AttchToChildProcess.value)

        _rteToken = _FwRteToken.OpenToken(_rteDataEx.rteTokenName)
        if _rteToken is None:
            _XProcessTarget.__PrintInfo(f'[XPTgt] Failed to pen RTE token {_rteDataEx.rteTokenName}.')
            _PyExitByMainThread(_EProcessTargetExitCodeID.eErrorExitCode_OpenRteToken.value)

        _procRes = ChildProcessResultData(rteDataExchange_.childProcessResultDataMaxSize)

        try:
            self.__hprocTgt(_procRes, *_rteDataEx.childProcessStartArgs, **_rteDataEx.childProcessStartKwargs)

        except SystemExit as xcp:
            _XProcessTarget.__PrintInfo('[XPTgt] Caught SystemExit exception below while trying to call target callback on child process side: {}\n\t{}'.format(_rteDataEx.childRteSeed, xcp))

            if xcp.code is None:
                _ec = 0
            elif isinstance(xcp.code, int):
                _ec = _EProcessTargetExitCodeID.FromExitCode(xcp.code)
            else:
                _ec = 1
            _procRes.exitCode = _ec

        except BaseException as xcp:
            _errMsg = '[XPTgt] Caught {} exception below while trying to call target callback on child process side: {}\n\t{}'.format(type(xcp).__name__, _rteDataEx.childRteSeed, xcp)
            if isinstance(xcp, TypeError):
                _errMsg += '\n\tNOTE:'
                _errMsg += '\n\t  - The target callback function must take an instance of class \'ChildProcessResultData\' as its first argument.'
                _errMsg += '\n\t  - Also, positional and/or keyword arguments (if any) passed to the constructor of the associated XProcess instance must '
                _errMsg += '\n\t    correspond to the remaining arguments of target callback function\'s signature.'
            _XProcessTarget.__PrintInfo(_errMsg)

            _rteToken.close()
            _PyExitByMainThread(_EProcessTargetExitCodeID.eErrorExitCode_ExceptionByTargetCallback.value)

        else:
            if not _FwRteToken.WriteCloseToken(_rteToken, _procRes):
                _XProcessTarget.__PrintInfo('[XPTgt] Encountered failure while trying to write to RTE token {}'.format(_rteDataEx.rteTokenName))
                _PyExitByMainThread(_EProcessTargetExitCodeID.eErrorExitCode_WriteRteToken.value)

        _PyExitByMainThread(_procRes.exitCode)
