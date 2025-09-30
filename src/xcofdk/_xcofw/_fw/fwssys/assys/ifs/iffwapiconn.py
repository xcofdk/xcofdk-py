# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwapiconn.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from typing import List
from typing import Tuple
from typing import Union

from xcofdk.fwcom     import LcFailure
from xcofdk.fwapi     import IRCTask
from xcofdk.fwapi     import IRCCommTask
from xcofdk.fwapi.xmt import IXTask

from _fw.fwssys.fwcore.types.apobject import _ProtAbsSlotsObject

class _IFwApiConn(_ProtAbsSlotsObject):
    __slots__ = []

    def __init__(self, ppass_ : int):
        super().__init__(ppass_)

    def _IsLcErrorFree(self):
        pass

    def _IsLcShutdownEnabled(self):
        pass

    def _IsXTaskRunning(self, xtUID_ : int) -> bool:
        pass

    def _GetLcFailure(self) -> Union[LcFailure, None]:
        pass

    def _GetXTask(self, xtUID_ : int =0) -> Union[IXTask, None]:
        pass

    def _GetCurXTask(self, bRcTask_ =False) -> Tuple[Union[IXTask, None], Union[IRCTask, None]]:
        pass

    def _GetCurRcTask(self) -> Union[IRCTask, IRCCommTask, None]:
        pass

    def _StopFW(self) -> bool:
        pass

    def _JoinFW(self) -> bool:
        pass

    def _JoinTasks(self, tasks_: Union[int, List[int], None] =None, timeout_: Union[int, float] =None) -> Tuple[int, Union[List[int], None]]:
        pass

    def _JoinProcesses(self, procs_: Union[int, List[int], None] =None, timeout_: Union[int, float] =None) -> Tuple[int, Union[List[int], None]]:
        pass

    def _TerminateProcesses(self, procs_: Union[int, List[int], None] =None) -> int:
        pass

    def _CleanUpByOwnerRequest(self):
        pass
