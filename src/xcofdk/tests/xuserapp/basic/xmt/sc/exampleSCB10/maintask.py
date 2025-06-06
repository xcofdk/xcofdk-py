# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : maintask.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from typing import Union

from xcofdk.fwcom import override
from xcofdk.fwcom import EExecutionCmdID

from xcofdk.fwapi     import xlogif
from xcofdk.fwapi.xmt import XTask
from xcofdk.fwapi.xmt import XMainTask
from xcofdk.fwapi.xmt import XTaskProfile


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
def GetMainTaskProfile() -> XTaskProfile:
    """
    Return an instance of 'XTaskProfile' which can be passed to the c-tor of
    class 'MyMainTask' as depicted below:

        >>> myMainTask = MyMainTask(xcounitPrf_=GetMainTaskProfile())
    """

    # create a default task profile and properly set attribute values relevant
    # for the returned instance of XTaskProfile.
    res = XTaskProfile.CreateSyncTaskProfile(aliasName_='MainTask')
    res.isSetupPhaseEnabled         = True
    res.isTeardownPhaseEnabled      = True
    res.runPhaseMaxProcessingTimeMS = 70
    return res
#END GetMainTaskProfile()


def GetServiceTaskProfile() -> XTaskProfile:
    """
    Return an instance of 'XTaskProfile' which can be passed to the c-tor
    of class 'MyService' as depicted below:

        >>> asyncTask = MyService(xcounitPrf_=GetServiceTaskProfile())
    """

    # create a default task profile and properly set attribute values relevant
    # for the returned instance of XTaskProfile.
    res = XTaskProfile.CreateAsyncTaskProfile(aliasName_='SrvTask', runPhaseFreqMS_=120)

    res.runPhaseMaxProcessingTimeMS = 20
    return res
#END GetServiceTaskProfile()


class MyService(XTask):

    __slots__ = []

    def __init__(self, taskProfile_ : XTaskProfile =None):
        super().__init__(taskProfile_=taskProfile_)

    @override
    def RunXTask(self) -> EExecutionCmdID:
        if self.isFirstRunPhaseIteration:
            xlogif.LogInfo(f'Started run-phase of task {self.aliasName}.')
        if self.currentRunPhaseIterationNo < 20:
            return EExecutionCmdID.CONTINUE

        xlogif.LogInfo(f'Done, going to stop run-phase of task {self.aliasName}.')
        return EExecutionCmdID.STOP
#END class MyService


class MyMainTask(XMainTask):

    __slots__ = [ '__srv' ]

    def __init__(self, taskProfile_ : XTaskProfile =None):
        self.__srv = None

        if taskProfile_ is None:
            taskProfile_ = GetMainTaskProfile()
        super().__init__(taskProfile_=taskProfile_)

    @override
    def SetUpXTask(self) -> EExecutionCmdID:
        xlogif.LogInfo(f'Welcome to XCOFDK, creating service task...')
        self.__srv = MyService(taskProfile_=GetServiceTaskProfile())
        xlogif.LogInfo(f'Done setup-phase of task {self.aliasName}.')
        return EExecutionCmdID.CONTINUE

    @override
    def RunXTask(self) -> EExecutionCmdID:
        xlogif.LogInfo(f'Starting run-phase of task {self.aliasName}...')

        xlogif.LogInfo(f'Starting service task {self.__srv.aliasName}...')
        self.__srv.Start()

        res = self.__srv.isStarted and not (self.__srv.isAborting or self.__srv.isFailed or self.__srv.isCanceled)
        if not res:
            xlogif.LogFatal(f'Failed to start service task {self.__srv.aliasName}.')

        xlogif.LogInfo(f'Done, going to stop run-phase of task {self.aliasName}.')
        return EExecutionCmdID.ABORT if not res else EExecutionCmdID.STOP
    
    @override
    def TearDownXTask(self) -> EExecutionCmdID:
        xlogif.LogInfo(f'Done teardown phase of task {self.aliasName}.')
        return EExecutionCmdID.STOP

    @staticmethod
    def _CreateSingleton(taskProfile_ : Union[XTaskProfile, None]):
        res = MyMainTask(taskProfile_=taskProfile_)
        if res.isDetachedFromFW:
            res = None
            xlogif.LogError('Failed to create main task.')
        return res
#END class MyMainTask
