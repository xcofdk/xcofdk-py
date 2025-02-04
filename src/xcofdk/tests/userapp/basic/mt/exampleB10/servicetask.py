# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : servicetask.py
#
# Copyright(c) 2023-2024 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from xcofdk.fwcom import xlogif
from xcofdk.fwcom import override
from xcofdk.fwcom import ETernaryCallbackResultID

from xcofdk.fwapi.xtask import XTask
from xcofdk.fwapi.xtask import XTaskProfile


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
def GetMyServiceTaskProfile() -> XTaskProfile:
    """
    Return an instance of 'XTaskProfile' which can be passed to the c-tor
    of class 'MyService' as depicted below:

        >>> asyncTask = MyService(xcounitPrf_=GetMyServiceTaskProfile())
    """

    # create a default task profile and properly set attribute values relevant
    # for the returned instance of XTaskProfile.
    res = XTaskProfile.CreateAsynchronousTaskProfile(aliasName_='myService', runPhaseFreqMS_=120)

    res.runPhaseMaxProcessingTimeMS = 20
    return res
#END GetMyServiceTaskProfile()


class MyService(XTask):

    __slots__ = []

    def __init__(self, taskProfile_ : XTaskProfile =None):
        super().__init__(taskProfile_=taskProfile_)

    @override
    def RunXTask(self) -> ETernaryCallbackResultID:
        xlogif.LogInfo(f'Nothing to do, done run-phase of task {self.xtaskAliasName}.')
        return ETernaryCallbackResultID.STOP
#END class MyService
