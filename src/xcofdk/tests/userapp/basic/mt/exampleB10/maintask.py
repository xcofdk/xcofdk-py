# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : maintask.py
#
# Copyright(c) 2023-2024 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from typing import Union

from xcofdk.fwcom import xlogif
from xcofdk.fwcom import override
from xcofdk.fwcom import ETernaryCallbackResultID

from xcofdk.fwapi.xtask import MainXTask
from xcofdk.fwapi.xtask import XTaskProfile

from xcofdk.tests.userapp.basic.mt.exampleB10.servicetask import MyService
from xcofdk.tests.userapp.basic.mt.exampleB10.servicetask import GetMyServiceTaskProfile


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
def GetMyMainTaskProfile() -> XTaskProfile:
    """
    Return an instance of 'XTaskProfile' which can be passed to the c-tor of
    class 'MyMainTask' as depicted below:

        >>> myMainTask = MyMainTask(xcounitPrf_=GetMyMainTaskProfile())
    """

    # create a default task profile and properly set attribute values relevant
    # for the returned instance of XTaskProfile.
    res = XTaskProfile.CreateSynchronousTaskProfile(aliasName_='myMainTask')
    res.isSetupPhaseEnabled         = True
    res.isTeardownPhaseEnabled      = True
    res.runPhaseMaxProcessingTimeMS = 70
    return res
#END GetMyMainTaskProfile()


class MyMainTask(MainXTask):

    __slots__ = [ '__srv' ]

    def __init__(self, taskProfile_ : XTaskProfile =None):
        self.__srv = None

        if taskProfile_ is None:
            taskProfile_ = GetMyMainTaskProfile()
        super().__init__(taskProfile_=taskProfile_)

    @override
    def SetUpXTask(self) -> ETernaryCallbackResultID:
        xlogif.LogInfo(f'Creating service task...')
        self.__srv = MyService(taskProfile_=GetMyServiceTaskProfile())
        xlogif.LogInfo(f'Done setup-phase of task {self.xtaskAliasName}.')
        return ETernaryCallbackResultID.CONTINUE

    @override
    def RunXTask(self) -> ETernaryCallbackResultID:
        xlogif.LogInfo(f'Starting run-phase of task {self.xtaskAliasName}...')

        xlogif.LogInfo(f'Starting service task {self.__srv.xtaskAliasName}...')
        self.__srv.Start()

        res = self.__srv.isStarted and not (self.__srv.isAborting or self.__srv.isFailed)
        if not res:
            xlogif.LogFatal(f'Failed to start service task {self.__srv.xtaskAliasName}.')

        xlogif.LogInfo(f'Done run-phase of task {self.xtaskAliasName}.')
        return ETernaryCallbackResultID.ABORT if not res else ETernaryCallbackResultID.STOP
    
    @override
    def TearDownXTask(self) -> ETernaryCallbackResultID:
        self.__srv.Join()
        xlogif.LogInfo(f'Done teardown-phase of task {self.xtaskAliasName}.')
        return ETernaryCallbackResultID.STOP

    @staticmethod
    def _CreateSingleton(taskProfile_ : Union[XTaskProfile, None]):
        res = MyMainTask(taskProfile_=taskProfile_)
        if res.isDetachedFromFW:
            res = None
            xlogif.LogError('Failed to create main task.')
        return res
#END class MyMainTask
