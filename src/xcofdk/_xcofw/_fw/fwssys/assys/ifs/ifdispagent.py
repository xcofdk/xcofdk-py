# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : ifdispagent.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from _fw.fwssys.fwcore.base.fwcallable   import _FwCallable
from _fw.fwssys.fwcore.types.aobject     import _AbsSlotsObject
from _fw.fwssys.fwcore.types.commontypes import _EExecutionCmdID
from _fw.fwssys.fwmsg.msg                import _IFwMessage

class _IDispAgent(_AbsSlotsObject):
    __slots__ = []

    def __init__(self):
        super().__init__()

    @property
    def _isOperating(self) -> bool:
        pass

    @property
    def _isFwAgent(self) -> bool:
        pass

    @property
    def _isXTaskAgent(self) -> bool:
        pass

    @property
    def _agentTaskID(self) -> int:
        pass

    @property
    def _agentName(self) -> str:
        pass

    def _PushMessage(self, msg_ : _IFwMessage, msgDump_: bytes, pldDump_=None, bCustomPL_=None, customDesCB_=None, callback_: _FwCallable =None) -> _EExecutionCmdID:
        pass

