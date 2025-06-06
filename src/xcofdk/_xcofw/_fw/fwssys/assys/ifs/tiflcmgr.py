# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : tiflcmgr.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from _fw.fwssys.fwcore.ipc.tsk.afwtask   import _AbsFwTask
from _fw.fwssys.fwcore.lc.lcdefines      import _ELcCompID
from _fw.fwssys.fwcore.lc.lcxstate       import _LcXStateDriver
from _fw.fwssys.fwcore.lc.lcproxydefines import _ELcSDRequest
from _fw.fwssys.fwerrh.logs.errorlog     import _FatalLog

class _TILcManager(_LcXStateDriver):
    __slots__ = []

    def __init__(self, ppass_ : int):
        super().__init__(ppass_)

    def _TIFPreCheckLcFailureNotification(self, eFailedCompID_ : _ELcCompID):
        pass

    def _TIFOnLcFailure(self, eFailedCompID_ : _ELcCompID, frcError_ : _FatalLog, atask_ : _AbsFwTask =None, bPrvRequestReply_ =True):
        pass

    def _TIFOnLcShutdownRequest(self, eShutdownRequest_: _ELcSDRequest) -> bool:
        pass

    def _TIFFinalizeStopFW(self, bCleanUpLcMgr_ : bool):
        pass
