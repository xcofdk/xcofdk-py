# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : usertaskdefs.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum      import auto
from enum      import unique
from threading import RLock as _PyRLock
from typing    import Any   as _PyAmy
from typing    import Union

from xcofdk.fwcom     import CompoundTUID
from xcofdk.fwapi.xmt import ITaskProfile

from _fw.fwssys.assys.ifs.ifutagent      import _IUTAgent
from _fw.fwssys.assys.ifs.ifutaskconn    import _IUTaskConn
from _fw.fwssys.fwcore.types.commontypes import _CommonDefines
from _fw.fwssys.fwcore.types.serdes      import SerDes
from _fw.fwssys.fwcore.ipc.tsk.taskstate import _TaskState
from _fw.fwssys.fwcore.ipc.tsk.taskdefs  import _ETaskSelfCheckResultID
from _fw.fwssys.fwcore.types.commontypes import _FwIntEnum

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

@unique
class _EUTaskXState(_FwIntEnum):
    eUTInitialized = _TaskState._EState.eInitialized.value
    eUTPendingRun  = auto()
    eUTRunning     = auto()
    eUTDone        = auto()
    eUTCanceled    = auto()
    eUTFailed      = auto()
    eUTStopping    = auto()
    eUTCanceling   = auto()
    eUTAborting    = auto()

    @property
    def isUtStarted(self):
        return self.value > _EUTaskXState.eUTInitialized.value

    @property
    def isUtPendingRun(self):
        return self == _EUTaskXState.eUTPendingRun

    @property
    def isUtRunning(self):
        return self == _EUTaskXState.eUTRunning

    @property
    def isUtDone(self):
        return self == _EUTaskXState.eUTDone

    @property
    def isUtCanceled(self):
        return self == _EUTaskXState.eUTCanceled

    @property
    def isUtFailed(self):
        return self == _EUTaskXState.eUTFailed

    @property
    def isUtStopping(self):
        return self == _EUTaskXState.eUTStopping

    @property
    def isUtCanceling(self):
        return self == _EUTaskXState.eUTCanceling

    @property
    def isUtAborting(self):
        return self == _EUTaskXState.eUTAborting

    @property
    def isUtTerminated(self):
       return _EUTaskXState.eUTRunning.value < self.value < _EUTaskXState.eUTStopping.value

    def _ToString(self, bDetached_ : bool):
        if self.value < _EUTaskXState.eUTRunning.value:
            res = _EFwTextID.eEUTaskXState_ToString_02.value
        elif self.isUtRunning:
            res = _EFwTextID.eEUTaskXState_ToString_03.value
        elif self.isUtDone:
            res = _EFwTextID.eEUTaskXState_ToString_04.value
        elif self.isUtCanceled:
            res = _EFwTextID.eEUTaskXState_ToString_08.value
        elif self.isUtFailed:
            res = _EFwTextID.eEUTaskXState_ToString_05.value
        elif self.isUtStopping:
            res = _EFwTextID.eEUTaskXState_ToString_06.value
        elif self.isUtCanceling:
            res = _EFwTextID.eEUTaskXState_ToString_09.value
        else:
            res = _EFwTextID.eEUTaskXState_ToString_07.value

        res = _FwTDbEngine.GetText(_EFwTextID(res))
        if bDetached_:
            if not self.isUtTerminated:
                res += _FwTDbEngine.GetText(_EFwTextID.eEUTaskXState_ToString_01)
        return res

class _UTaskMirror:
    __slots__ = [ '__a' , '__ust' , '__xp' , '__c' , '__bS' , '__bR' , '__an' , '__sr' , '__uid' , '__n' , '__l' , '__ud' , '__cuid' ]

    def __init__(self, a_: _IUTAgent, xtPrf_: ITaskProfile, aliasName_: str, bRcTM_=False):
        self.__c    = None
        self.__n    = None
        self.__bS   = None
        self.__ud   = None
        self.__ust  = None
        self.__uid  = None
        self.__cuid = None

        self.__a  = a_
        self.__l  = _PyRLock()
        self.__an = aliasName_
        self.__bR = bRcTM_
        self.__sr = _ETaskSelfCheckResultID.eScrNA
        self.__xp = xtPrf_

    def __str__(self):
        return self.__ToString()

    @property
    def mrIsStarted(self) -> bool:
        return False if self.__ust is None else self.__ust.isUtStarted

    @property
    def mrIsDone(self) -> bool:
        return False if self.__ust is None else self.__ust.isUtDone

    @property
    def mrIsCanceled(self) -> bool:
        return False if self.__ust is None else self.__ust.isUtCanceled

    @property
    def mrIsFailed(self) -> bool:
        return False if self.__ust is None else self.__ust.isUtFailed

    @property
    def mrIsStopping(self) -> bool:
        return False if self.__ust is None else (self.__ust.isUtStopping or self.__ust.isUtCanceling)

    @property
    def mrIsCanceling(self) -> bool:
        return False if self.__ust is None else self.__ust.isUtCanceling

    @property
    def mrIsAborting(self) -> bool:
        return False if self.__ust is None else self.__ust.isUtAborting

    @property
    def mrIsConnected(self) -> bool:
        return False if self.__c is None else self.__c._isUTConnected

    @property
    def mrUTConn(self) -> _IUTaskConn:
        return self.__c

    @property
    def mrUTAgent(self) -> _IUTAgent:
        return self.__a

    @property
    def mrAliasName(self) -> str:
        return self.__an

    @mrAliasName.setter
    def mrAliasName(self, aliasn_ : str):
        self.__an = aliasn_

    @property
    def mrUTaskName(self) -> str:
        return self.mrAliasName if self.__n is None else self.__n

    @property
    def mrUTaskUID(self) -> int:
        return self.__uid

    @property
    def mrUTaskProfile(self) -> ITaskProfile:
        return self.__xp

    @property
    def _mrIsRcTaskMirror(self):
        return self.__bR

    @property
    def _mrUTaskXState(self) -> _EUTaskXState:
        return self.__ust

    @property
    def _mrUTaskXStateAsStr(self) -> str:
        return self.__MapUtXStateToString()

    @property
    def _mrTaskCompUID(self) -> Union[CompoundTUID, None]:
        return self.__cuid

    @_mrTaskCompUID.setter
    def _mrTaskCompUID(self, info_ : CompoundTUID):
        if isinstance(info_, (CompoundTUID, tuple)) and (self.__cuid is None):
            self.__cuid = info_

    @property
    def _mrSelfCheckResult(self) -> _ETaskSelfCheckResultID:
        return self.__sr

    @_mrSelfCheckResult.setter
    def _mrSelfCheckResult(self, scr_ : _ETaskSelfCheckResultID):
        self.__sr = scr_

    def _MrUpdateConn(self, c_ : _IUTaskConn, a_ : _IUTAgent, bSyncTask_ : bool):
        self.__a  = a_
        self.__c  = c_
        self.__bS = bSyncTask_

    def _MrUpdateTaskID(self, tuid_ : int, tname_ : str):
        self.__n   = tname_
        self.__uid = tuid_

    def _MrUpdateTaskState(self, xtState_ : _EUTaskXState, bDetach_ =False):
        self.__ust = xtState_
        if bDetach_:
            self.__a = None
            self.__c = None

    def _MrGetUData(self, bDeser_ =True) -> _PyAmy:
        with self.__l:
            res = self.__ud
            if bDeser_ and isinstance(res, bytes):
                res = SerDes.DeserializeData(res, bTreatAsUserError_=True)
            return res

    def _MrSetUData(self, tskData_ : _PyAmy, bSer_ =False):
        with self.__l:
            _ud = tskData_
            if bSer_ and not isinstance(tskData_, bytes):
                _ud = SerDes.SerializeObject(tskData_, bTreatAsUserError_=True, bAllowNone_=True)
            self.__ud = _ud

    def __ToString(self):
        res = _FwTDbEngine.GetText(_EFwTextID.eUserTaskConn_XTaskMirror_ToString_01)
        res = res.format(self.mrUTaskName, self.__MapUtXStateToString())
        return res

    def __MapUtXStateToString(self) -> str:
        if not self.mrIsConnected:
            res = _CommonDefines._STR_NONE if self.__ust is None else self.__ust._ToString(bDetached_=True)
        else:
            res = self.__c._utXStateToString
        return res
