# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : afwxunit.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from typing import Union

from xcofdk.fwapi.xmt import ITaskProfile

from _fw.fwssys.assys.ifs.ifxunit import _IXUnit

class _AbsFwXUnit(_IXUnit):
    __slots__ = []

    def __init__(self):
        super().__init__()

    @property
    def isAttachedToFW(self) -> bool:
        return self._isAttachedToFW

    @property
    def isDetachedFromFW(self) -> bool:
        return not self._isAttachedToFW

    @property
    def isStarted(self) -> bool:
        return self._isStarted

    @property
    def isPendingRun(self) -> bool:
        return self._isPendingRun

    @property
    def isRunning(self) -> bool:
        return self._isRunning

    @property
    def isDone(self) -> bool:
        return self._isDone

    @property
    def isCanceled(self) -> bool:
        return self._isCanceled

    @property
    def isFailed(self) -> bool:
        return self._isFailed

    @property
    def isStopping(self) -> bool:
        return self._isStopping

    @property
    def isCanceling(self) -> bool:
        return self._isCanceling

    @property
    def isAborting(self) -> bool:
        return self._isAborting

    @property
    def isTerminated(self) -> bool:
        return self._isDone or self._isFailed or self._isCanceled

    @property
    def isTerminating(self) -> bool:
        return self._isStopping or self._isAborting

    @property
    def taskUID(self) -> int:
        return self._taskUID

    @property
    def taskName(self) -> str:
        return self._taskName

    @property
    def taskProfile(self) -> ITaskProfile:
        return self._taskProfile

    def Start(self, *args_, **kwargs_) -> bool:
        return self._Start(*args_, **kwargs_)

    def Stop(self) -> bool:
        return self._Stop(bCancel_=False, bCleanupDriver_=True)

    def Cancel(self) -> bool:
        return self._Stop(bCancel_=True, bCleanupDriver_=True)

    def Join(self, timeout_: Union[int, float] =None) -> bool:
        return self._Join(timeout_=timeout_)

    def SelfCheck(self) -> bool:
        return self._SelfCheck()

