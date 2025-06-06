# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : iflcstate.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from _fw.fwssys.fwcore.types.apobject import _ProtAbsSlotsObject
from _fw.fwssys.fwcore.lc.lcdefines   import _ELcCompID
from _fw.fwssys.fwerrh.lcfrcview      import _LcFrcView

class _ILcState(_ProtAbsSlotsObject):
    __slots__ = []

    def __init__(self, ppass_ : int):
        super().__init__(ppass_)

    @property
    def isLcOperable(self) -> bool:
        pass

    @property
    def isLcCoreOperable(self) -> bool:
        pass

    @property
    def isLcStarted(self) -> bool:
        pass

    @property
    def isTaskManagerStarted(self) -> bool:
        pass

    @property
    def isFwMainStarted(self) -> bool:
        pass

    @property
    def isMainXTaskStarted(self) -> bool:
        pass

    @property
    def isLcStopped(self) -> bool:
        pass

    @property
    def isTaskManagerStopped(self) -> bool:
        pass

    @property
    def isFwMainStopped(self) -> bool:
        pass

    @property
    def isMainXTaskStopped(self) -> bool:
        pass

    @property
    def isLcFailed(self) -> bool:
        pass

    @property
    def isTaskManagerFailed(self) -> bool:
        pass

    @property
    def isFwCompFailed(self):
        pass

    @property
    def isFwMainFailed(self) -> bool:
        pass

    @property
    def isXTaskFailed(self) -> bool:
        pass

    @property
    def isMainXTaskFailed(self) -> bool:
        pass

    @property
    def isMiscCompFailed(self):
        pass

    @property
    def hasLcAnyFailureState(self) -> bool:
        pass

    @property
    def lcFrcView(self) -> _LcFrcView:
        pass

    def HasLcCompFRC(self, lcCID_: _ELcCompID, atask_ =None) -> bool:
        pass

    def GetLcCompFrcView(self, lcCID_: _ELcCompID, atask_=None) -> _LcFrcView:
        pass

