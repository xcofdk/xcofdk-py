# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : iflcguard.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from _fw.fwssys.fwcore.ipc.tsk.afwtask  import _AbsFwTask
from _fw.fwssys.fwcore.lc.lcdefines     import _ELcCompID
from _fw.fwssys.fwcore.lc.ifs.iflcstate import _ILcState
from _fw.fwssys.fwerrh.logs.errorlog    import _FatalLog

class _ILcGuard(_ILcState):
    __slots__  = []
    _sgltn = None

    def __init__(self, ppass_ : int):
        super().__init__(ppass_)
        _ILcGuard._sgltn = self

    def _GGetLcState(self, bypassApiLock_=False) -> _ILcState:
        pass

    def _GSetLcOperationalState(self, lcCID_ : _ELcCompID, bStartStopFlag_ : bool, atask_ : _AbsFwTask =None) -> bool:
        pass

    def _GSetLcFailure(self, eFailedCompID_ : _ELcCompID, frcError_ : _FatalLog, atask_ : _AbsFwTask =None, bSkipReply_ =False, bInternalCall_ =False) -> bool:
        pass
