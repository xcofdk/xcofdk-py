# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : lcmgrtif.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from xcofdk._xcofw.fw.fwssys.fwcore.logging.fatalentry import _FatalEntry
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.atask      import _AbstractTask
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcdefines       import _ELcCompID
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcexecstate     import _LcExecutionStateDriver
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcproxydefines  import _ELcShutdownRequest


class _LcManagerTrustedIF(_LcExecutionStateDriver):

    __slots__ = []

    def __init__(self, ppass_ : int):
        super().__init__(ppass_)

    def _TIFPreCheckLcFailureNotification(self, eFailedCompID_ : _ELcCompID):
        pass

    def _TIFOnLcFailure(self, eFailedCompID_ : _ELcCompID, frcError_ : _FatalEntry, atask_ : _AbstractTask =None, bPrvRequestReply_ =True):
        pass

    def _TIFOnLcShutdownRequest(self, eShutdownRequest_: _ELcShutdownRequest) -> bool:
        pass

    def _TIFFinalizeStopFW(self, bCleanUpLcMgr_ : bool):
        pass
