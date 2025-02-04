# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : lcguard.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from xcofdk._xcofw.fw.fwssys.fwcore.logging.fatalentry import _FatalEntry
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.atask      import _AbstractTask
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcdefines       import _ELcCompID
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcstate         import _LcState

class _LcGuard(_LcState):

    __slots__  = []
    _singleton = None

    def __init__(self, ppass_ : int):
        super().__init__(ppass_)
        _LcGuard._singleton = self

    def _GetLcState(self, bypassApiLock_=False) -> _LcState:
        pass

    def _SetLcOperationalState(self, eLcCompID_ : _ELcCompID, bStartStopFlag_ : bool, atask_ : _AbstractTask =None) -> bool:
        pass

    def _SetLcFailure(self, eFailedCompID_ : _ELcCompID, frcError_ : _FatalEntry, atask_ : _AbstractTask =None, bSkipReply_ =False, bInternalCall_ =False) -> bool:
        pass
