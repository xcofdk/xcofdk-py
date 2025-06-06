# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : ifutask.py.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from typing import Any   as _PyAmy
from typing import Union

from xcofdk.fwcom import CompoundTUID
from xcofdk.fwapi import ITaskError

from _fw.fwssys.assys.ifs.ifxunit import _IXUnit

class _IUserTask(_IXUnit):
    __slots__ = []

    def __init__(self):
        super().__init__()

    @property
    def _isSyncTask(self):
        pass

    @property
    def _isErrorFree(self) -> bool:
        pass

    @property
    def _isFatalErrorFree(self) -> bool:
        pass

    @property
    def _taskAliasName(self) -> str:
        pass

    @property
    def _currentError(self) -> ITaskError:
        pass

    @property
    def _curRunPhaseIterationNo(self):
        pass

    @property
    def _taskCompUID(self) -> Union[CompoundTUID, None]:
        pass

    def _DetachFromFW(self):
        pass

    def _GetTaskOwnedData(self, bDeser_ =True) -> _PyAmy:
        pass

    def _SetTaskOwnedData(self, tskData_ : _PyAmy, bSer_ =False):
        pass

    def _ClearCurrentError(self) -> bool:
        pass

    def _SetTaskError(self, bFatal_ : bool, errMsg_: str, errCode_: int =None):
        pass

    def _TriggerQueueProcessing(self, bExtQueue_ : bool) -> int:
        pass
