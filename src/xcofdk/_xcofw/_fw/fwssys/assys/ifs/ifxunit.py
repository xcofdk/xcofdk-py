# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : ifxunit.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from typing import Union

from xcofdk.fwapi.xmt import ITaskProfile

class _IXUnit:
    __slots__ = []

    def __init__(self):
        pass

    def __str__(self):
       return self._ToString()

    @property
    def _isAttachedToFW(self) -> bool:
        pass

    @property
    def _isStarted(self) -> bool:
        pass

    @property
    def _isPendingRun(self) -> bool:
        pass

    @property
    def _isRunning(self) -> bool:
        pass

    @property
    def _isDone(self) -> bool:
        pass

    @property
    def _isCanceled(self) -> bool:
        pass

    @property
    def _isFailed(self) -> bool:
        pass

    @property
    def _isStopping(self) -> bool:
        pass

    @property
    def _isCanceling(self) -> bool:
        pass

    @property
    def _isAborting(self) -> bool:
        pass

    @property
    def _isTerminated(self) -> bool:
        pass

    @property
    def _isTerminating(self) -> bool:
        pass

    @property
    def _taskUID(self) -> int:
        pass

    @property
    def _taskName(self) -> str:
        pass

    @property
    def _taskProfile(self) -> ITaskProfile:
        pass

    def _Start(self, *args_, **kwargs_) -> bool:
        pass

    def _Stop(self, bCancel_=False, bCleanupDriver_=True) -> bool:
        pass

    def _Join(self, timeout_: Union[int, float, None] =None) -> bool:
        pass

    def _SelfCheck(self) -> bool:
        pass

    def _ToString(self, *args_, **kwargs_) -> str:
        pass

