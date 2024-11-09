# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : lcstate.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from xcofdk._xcofw.fw.fwssys.fwcore.types.apobject import _ProtectedAbstractSlotsObject
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcdefines   import _ELcCompID
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcdefines   import _LcFrcView


class _LcState(_ProtectedAbstractSlotsObject):

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
    def isLcPreCoreOperable(self) -> bool:
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
    def hasLcAnyStoppedState(self) -> bool:
        pass

    @property
    def hasLcAnyFailureState(self) -> bool:
        pass

    @property
    def lcFrcView(self) -> _LcFrcView:
        pass

    def HasLcCompFRC(self, eLcCompID_: _ELcCompID, atask_ =None) -> bool:
        pass

    def GetLcCompFrcView(self, eLcCompID_: _ELcCompID, atask_=None) -> _LcFrcView:
        pass
