# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwapiconn.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from threading import RLock as _PyRLock
from typing    import List
from typing    import Tuple
from typing    import Union

from xcofdk.fwcom     import LcFailure
from xcofdk.fwapi     import IRCTask
from xcofdk.fwapi     import IRCCommTask
from xcofdk.fwapi.xmt import IXTask

from _fw.fwssys.assys.ifs.iffwapiconn   import _IFwApiConn
from _fw.fwssys.fwcore.logging          import vlogif
from _fw.fwssys.fwcore.ipc.tsk.taskutil import _TaskUtil
from _fw.fwssys.fwcore.lc.lcxstate      import _LcFailure
from _fw.fwssys.fwctrl.fwapiconnap      import _FwApiConnectorAP

class _FwApiConnector(_IFwApiConn):
    __slots__ = [ '__l' , '__bA' ]

    def __init__(self, ppass_ : int):
        self.__l  = None
        self.__bA = False
        super().__init__(ppass_)

    def _FwCNIsFwApiAvailable(self):
        if self.__l is None:
            return False
        with self.__l:
            return self.__bA

    def _FwCNIsLcErrorFree(self) -> bool:
        if not self._FwCNIsFwApiAvailable():
            return _LcFailure.IsLcErrorFree()
        return self._IsLcErrorFree()

    def _FwCNIsLcShutdownEnabled(self) -> bool:
        if not self._FwCNIsFwApiAvailable():
            return False
        return self._IsLcShutdownEnabled()

    def _FwCNIsXTaskRunning(self, xtUID_ : int) -> bool:
        if not self._FwCNIsFwApiAvailable():
            return False
        return self._IsXTaskRunning(xtUID_)

    def _FwCNGetLcFailure(self) -> Union[LcFailure, None]:
        if not self._FwCNIsFwApiAvailable():
            return _LcFailure._GetLcFailure()
        return self._GetLcFailure()

    def FwCNGetXTask(self, xtUID_ : int =0) -> Union[IXTask, None]:
        if not self._FwCNIsFwApiAvailable():
            return None
        if xtUID_ == 0:
            res, _dc = self._GetCurXTask()
        else:
            res = self._GetXTask(xtUID_)
        return res

    def FwCNGetCurXTask(self) -> Union[IXTask, None]:
        if not self._FwCNIsFwApiAvailable():
            return None
        res, _dc = self._GetCurXTask()
        return res

    def FwCNGetCurRcTask(self) -> Union[IRCTask, IRCCommTask, None]:
        if not self._FwCNIsFwApiAvailable():
            return None
        return self._GetCurRcTask()

    def FwCNStopXcoFW(self) -> bool:
        if not self._FwCNIsFwApiAvailable():
            return False
        return self._StopFW()

    def FwCNJoinXcoFW(self) -> bool:
        if not self._FwCNIsFwApiAvailable():
            return False
        return self._JoinFW()

    def FwCNJoinTasks(self, tasks_: Union[int, List[int], None] =None, timeout_: Union[int, float] =None) -> Tuple[int, Union[List[int], None]]:
        if not self._FwCNIsFwApiAvailable():
            return 0, None
        _numJ, _lstUnj = self._JoinTasks(tasks_, timeout_=timeout_)
        return _numJ, _lstUnj

    def FwCNJoinProcesses(self, procs_: Union[int, List[int], None] =None, timeout_: Union[int, float] =None) -> Tuple[int, Union[List[int], None]]:
        if not self._FwCNIsFwApiAvailable():
            return 0, None
        _numJ, _lstUnj = self._JoinProcesses(procs_, timeout_=timeout_)
        return _numJ, _lstUnj

    def FwCNTerminateProcesses(self, procs_: Union[int, List[int], None] =None) -> int:
        if not self._FwCNIsFwApiAvailable():
            return 0
        return self._TerminateProcesses(procs_)

    def _FwCNPublishFwApiConnector(self, bDisconnect_ =False, disconnectSleepTimespanMS_ =None):
        if self.__l is None:
            return

        with self.__l:
            if (not bDisconnect_) and self.__bA:
                pass
            elif bDisconnect_ and not self.__bA:
                pass
            else:
                self.__bA = not bDisconnect_

                _fwConn = None if bDisconnect_ else self
                _FwApiConnectorAP._APSetFwApiConnector(_fwConn, self.__l)
                if bDisconnect_:
                    if disconnectSleepTimespanMS_ is not None:
                        _TaskUtil.SleepMS(disconnectSleepTimespanMS_)

    def _FwCNSetFwApiLock(self, fwApiLck_ : _PyRLock):
        self.__l = fwApiLck_

    def _CleanUpByOwnerRequest(self):
        if self.__l is None:
            return
        self._FwCNPublishFwApiConnector(bDisconnect_=True)
        self.__l  = None
        self.__bA = None
        super()._CleanUpByOwnerRequest()
