# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : dispatchagentif.py
#
# Copyright(c) 2024 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from xcofdk._xcofw.fw.fwssys.fwcore.base.callableif   import _CallableIF
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject     import _AbstractSlotsObject
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes import _ETernaryOpResult

from xcofdk._xcofw.fw.fwssys.fwmsg.msg                 import _MessageIF
from xcofdk._xcofw.fw.fwssys.fwmsg.disp.dispatchFilter import _DispatchFilter

class _DispatchAgentIF(_AbstractSlotsObject):

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

    def _PushMessage(self, msg_ : _MessageIF, msgDump_: bytes, pldDump_=None, bCustomPL_=None, customDesCallback_=None, callback_: _CallableIF =None) -> _ETernaryOpResult:
        pass

