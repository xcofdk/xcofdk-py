# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : tiftmgr.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from typing import List
from typing import Tuple
from typing import Union

from xcofdk.fwapi.xmt import IXTask

class _ITTMgr:
    __slots__ = []

    def __init__(self):
        pass

    def _GetCurTask(self, bAutoEncl_ =False):
        pass

    def _GetXTasks(self, bRunningOnly_ =True, bJoinableOnly_ =True, bUID_ =True, lstUIDs_ : list =None) -> Tuple[List[Union[int, IXTask]], Union[List[int], None]]:
        pass

    def _GetProxyInfoReplacementData(self):
        pass

    def _GetTaskErrorByTID(self, taskID_ : int):
        pass

    def _SetLcMonitorImpl(self, lcMonImpl_):
        pass

    def _InjectLcProxy(self, lcProxy_):
        pass

    def _StopAllTasks(self, bCleanupStoppedTasks_ =True, lstSkipTaskIDs_ =None) -> list:
        pass

    def _AddTaskEntry(self, taskInst_, bRemoveAutoEnclTE_ =True) -> Union[int, None]:
        pass

    def _DetachTask(self, taskInst_, cleanup_=True):
        pass
