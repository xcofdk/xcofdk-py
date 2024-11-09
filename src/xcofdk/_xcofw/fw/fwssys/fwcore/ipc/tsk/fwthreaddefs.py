# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwthreaddefs.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from enum import unique

from xcofdk._xcofw.fw.fwssys.fwcore.logging import vlogif

from xcofdk._xcofw.fw.fwssys.fwcore.apiimpl.xtask.xtaskdefs import _EXTaskApiID
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject           import _AbstractSlotsObject
from xcofdk._xcofw.fw.fwssys.fwcore.types.ebitmask          import _EBitMask
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes       import _FwIntFlag
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes       import _CommonDefines
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes       import _ETernaryOpResult
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil        import _ETaskExecutionPhaseID

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine



@unique
class _EXTaskApiFuncTag(_FwIntFlag):

    eNone = 0x0*000
    eXFTRunXTask      = (0x0001 << _EXTaskApiID.eRunXTask.value)
    eXFTSetUpXTask    = (0x0001 << _EXTaskApiID.eSetUpXTask.value)
    eXFTTearDownXTask = (0x0001 << _EXTaskApiID.eTearDownXTask.value)

    @property
    def isXTaskExecutionAPI(self):
        return self != _EXTaskApiFuncTag.eNone

    @property
    def functionName(self):
        return _EXTaskApiID(self.rightMostBitPosition).functionName

    def MapToTaskExecutionPhaseID(self) -> _ETaskExecutionPhaseID:
        if self == _EXTaskApiFuncTag.eXFTRunXTask:
            res = _ETaskExecutionPhaseID.eXTaskRun

        elif self == _EXTaskApiFuncTag.eXFTSetUpXTask:
            res = _ETaskExecutionPhaseID.eXTaskSetup

        elif self == _EXTaskApiFuncTag.eXFTTearDownXTask:
            res = _ETaskExecutionPhaseID.eXTaskTeardown

        else:
            res = _ETaskExecutionPhaseID.eNone
        return res

    @staticmethod
    def IsNone(eApiMask_: _FwIntFlag):
        return eApiMask_==_EXTaskApiFuncTag.eNone

    @staticmethod
    def IsEnabledRunXTask(eApiMask_: _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eApiMask_, _EXTaskApiFuncTag.eXFTRunXTask)

    @staticmethod
    def IsEnabledSetUpXTask(eApiMask_: _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eApiMask_, _EXTaskApiFuncTag.eXFTSetUpXTask)

    @staticmethod
    def IsEnabledTearDownXTask(eApiMask_: _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eApiMask_, _EXTaskApiFuncTag.eXFTTearDownXTask)

    @staticmethod
    def IsEnabledApiFunction(eApiMask_: _FwIntFlag, eApiFuncTag_: _FwIntFlag):
        return _EBitMask.IsEnumBitFlagSet(eApiMask_, eApiFuncTag_)

    @staticmethod
    def DefaultApiMask():
        return _EXTaskApiFuncTag.eNone

    @staticmethod
    def AddApiFuncTag(eApiMask_: _FwIntFlag, eApiFuncTag_ : _FwIntFlag):
        return _EBitMask.AddEnumBitFlag(eApiMask_, eApiFuncTag_)

    @staticmethod
    def RemoveApiFuncTag(eApiMask_: _FwIntFlag, eApiFuncTag_ : _FwIntFlag):
        return _EBitMask.RemoveEnumBitFlag(eApiMask_, eApiFuncTag_)


class _XTaskApiGuide(_AbstractSlotsObject):
    __slots__ = [
        '__fwthrd'
      , '__eApiMask'
      , '__eExclApiMask'
      , '__eExecApiFuncRet'

      , '__runXTask'
      , '__setUpXTask'
      , '__tearDownXTask'
    ]

    def __init__(self, fwthrd_, excludedXuM_ : _EXTaskApiFuncTag):
        self.__fwthrd          = None
        self.__eApiMask        = None
        self.__eExclApiMask    = None
        self.__eExecApiFuncRet = None

        self.__runXTask      = None
        self.__setUpXTask    = None
        self.__tearDownXTask = None

        super().__init__()

        if fwthrd_ is None:
            vlogif._LogOEC(True, -1253)
            self.CleanUp()
            return
        if fwthrd_._linkedExecutable is None:
            vlogif._LogOEC(True, -1254)
            self.CleanUp()
            return

        _exclApiFuncs = None
        if excludedXuM_ is not None:
            if not isinstance(excludedXuM_, _EXTaskApiFuncTag):
                vlogif._LogOEC(True, -1255)
                self.CleanUp()
                return

            _exclApiFuncs = _EBitMask.GetIntegerBitFlagsList(excludedXuM_)
            if _exclApiFuncs is None:
                vlogif._LogOEC(True, -1256)
                self.CleanUp()
                return
            elif len(_exclApiFuncs) == 0:
                _exclApiFuncs = None

        self.__fwthrd       = fwthrd_
        self.__eApiMask     = _EXTaskApiFuncTag.DefaultApiMask()
        self.__eExclApiMask = excludedXuM_

        _errMsg  = _CommonDefines._STR_EMPTY
        _xtsk = fwthrd_._linkedExecutable
        for name, member in _EXTaskApiFuncTag.__members__.items():
            if member == _EXTaskApiFuncTag.eNone:
                continue
            elif _EBitMask.IsEnumBitFlagSet(self.__eApiMask, member):
                continue
            elif _exclApiFuncs is not None:
                if member.value in _exclApiFuncs:
                    continue

            _apiFunc = getattr(_xtsk, member.functionName, None)
            if _apiFunc is None:
                continue

            self.__eApiMask = _EXTaskApiFuncTag.AddApiFuncTag(self.__eApiMask, member)

            if   member == _EXTaskApiFuncTag.eXFTRunXTask:      self.runXTask      = _apiFunc
            elif member == _EXTaskApiFuncTag.eXFTSetUpXTask:    self.setUpXTask    = _apiFunc
            elif member == _EXTaskApiFuncTag.eXFTTearDownXTask: self.tearDownXTask = _apiFunc


            else:
                self.__eApiMask = None
                break

        if self.runXTask is None:
            self.__eApiMask = None

        if self.__eApiMask is None:
            self.__fwthrd       = None
            self.__eExclApiMask = None
            self.CleanUp()

            vlogif._LogOEC(True, -1257)

    @property
    def runXTask(self):
        return self.__runXTask

    @runXTask.setter
    def runXTask(self, val_):
        self.__runXTask = val_

    @property
    def setUpXTask(self):
        return self.__setUpXTask

    @setUpXTask.setter
    def setUpXTask(self, val_):
        self.__setUpXTask = val_

    @property
    def tearDownXTask(self):
        return self.__tearDownXTask

    @tearDownXTask.setter
    def tearDownXTask(self, val_):
        self.__tearDownXTask = val_

    @property
    def eApiMask(self) -> _EXTaskApiFuncTag:
        return self.__eApiMask

    @property
    def eExcludedApiMask(self) -> _EXTaskApiFuncTag:
        return self.__eExclApiMask

    @property
    def isProvidingRunXTask(self):
        return False if self.__eApiMask is None else _EXTaskApiFuncTag.IsEnabledRunXTask(self.__eApiMask)

    @property
    def isProvidingSetUpXTask(self):
        return False if self.__eApiMask is None else _EXTaskApiFuncTag.IsEnabledSetUpXTask(self.__eApiMask)

    @property
    def isProvidingTearDownXTask(self):
        return False if self.__eApiMask is None else _EXTaskApiFuncTag.IsEnabledTearDownXTask(self.__eApiMask)

    @property
    def _fwThread(self):
        return self.__fwthrd

    @property
    def _eExecutionApiFunctionReturn(self) -> _ETernaryOpResult:
        return self.__eExecApiFuncRet

    def _IsProvidingApiFunction(self, eApiFuncTag_ : _EXTaskApiFuncTag):
        return False if self.__eApiMask is None else _EXTaskApiFuncTag.IsEnabledApiFunction(self.__eApiMask, eApiFuncTag_)

    def _ToString(self, *args_, **kwargs_):
        if self.__eApiMask is None:
            return None

        _bCompact = True
        for _ii in range(len(args_)):
            if 0 == _ii: _bCompact = args_[_ii]

        _myTxt = _XTaskApiGuide.__ApiMask2String(self.__eApiMask)
        res = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_ApiGuide_ApiMask)
        res = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_004).format(type(self).__name__, res, _myTxt)
        if not _bCompact:
            if self.__eExclApiMask is not None:
                _myTxt = _XTaskApiGuide.__ApiMask2String(self.__eExclApiMask, bExcluded_=True)
                res   += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_NewlineTab) + _myTxt
        return res

    def _CleanUp(self):
        self.__fwthrd          = None
        self.__eApiMask        = None
        self.__eExclApiMask    = None
        self.__eExecApiFuncRet = None

        self.runXTask      = None
        self.setUpXTask    = None
        self.tearDownXTask = None

    def _SetGetExecutionApiFunctionReturn(self, execRet_ : _ETernaryOpResult, bApplyConvertBefore_ =True) -> _ETernaryOpResult:
        if not bApplyConvertBefore_:
            res = execRet_
        else:
            res = _ETernaryOpResult.ConvertFrom(execRet_)
        self.__eExecApiFuncRet = res
        return res

    @staticmethod
    def __ApiMask2String(xuApiMask_ : _EXTaskApiFuncTag, bExcluded_ =False):
        res = _EFwTextID.eMisc_Shared_ApiGuide_ExcludedApiMask if bExcluded_ else _EFwTextID.eMisc_Shared_ApiGuide_ApiMask
        res = _FwTDbEngine.GetText(res)
        res = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_005).format(res, hex(xuApiMask_))

        _myTxt = _CommonDefines._STR_EMPTY
        for name, member in _EXTaskApiFuncTag.__members__.items():
            if member == _EXTaskApiFuncTag.eNone:
                continue
            if not _EBitMask.IsEnumBitFlagSet(xuApiMask_, member):
                continue
            _myTxt += _CommonDefines._CHAR_SIGN_TAB + member.functionName + _CommonDefines._CHAR_SIGN_NEWLINE

        if len(_myTxt) > 0:
            _myTxt = _myTxt.rstrip()
            res   += _CommonDefines._CHAR_SIGN_NEWLINE + _myTxt
        return res
