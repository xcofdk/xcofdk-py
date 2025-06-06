# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xtaskprofile.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from typing import Union

from xcofdk.fwcom     import override
from xcofdk.fwapi.xmt import ITaskProfile

from _fw.fwssys.fwmt.api.xtaskprfimpl import _XTaskPrfImpl


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class XTaskProfile(ITaskProfile):
    """
    This class is the implementation of its interface class ITaskProfile.

    Instances of this class are passed to the respective constructor of either
    XTask or XMainTask when creating new task instances.

    A new instance of this class is provided with default configuration after
    its construction. Sample code snippet below prints out the default:
        >>> from xcofdk.fwapi     import xlogif
        >>> from xcofdk.fwapi.xmt import XTaskProfile
        >>>
        >>> #...
        >>> _xtPrf = XTaskProfile()
        >>> xlogif.LogInfo(f'{_xtPrf}')
        >>>
        >>> # The outuput will look like as shown below:
        >>> #   [15:31:16.902 XINF] Task profile :
        >>> #        aliasName                   : None
        >>> #        isMainTask                  : False
        >>> #        isSyncTask                  : False
        >>> #        isPrivilegedTask            : False
        >>> #        isRunPhaseEnabled           : True
        >>> #        isSetupPhaseEnabled         : False
        >>> #        isTeardownPhaseEnabled      : False
        >>> #        isCyclicRunPhase            : True
        >>> #        isInternalQueueEnabled      : False
        >>> #        isExternalQueueEnabled      : False
        >>> #        isExternalQueueBlocking     : False
        >>> #        runPhaseFrequencyMS         : 100
        >>> #        runPhaseMaxProcessingTimeMS : 50

    After a task profile instance is created, its modifiable properties can be
    changed via their respective property setter if required. Doing so, that
    instance represents then a task profile properly confifured in accordance
    with the application requirements, and so it is ready to be passed to the
    constructor of the next task instance to be created.

    Once the creation of an instance of the abstract class XTask is succeeded,
    the task profile passed to the constructor is cloned as an internal,
    ready-only (or 'frozen') copy ready to be accessed by the framework as the
    single source of information regarding that task's configuration at runtime.

    For quick orientation and guidance on by when to use which API property,
    the interface is arranged in subsets each of them labeled in accordance to
    the given logical context by a comment block of the form:
        >>> # --------------------------------------------------------------
        >>> # SecNo) title of interface subset
        >>> # --------------------------------------------------------------

    Currently available interface subsets of class XTaskProfile are as follows:
        1) c-tor / built-in
        2) API basic (read-only) configuration
        3) API 3-PhXF configuration
        4) API queue configuration
        5) API timing configuration
        6) API supplementary interface

    Note:
    ------
        - In this documentation the term 'task configuration' always refers to
          a given instance of this class (supposed to be) used for a task
          instance (to be created).
    See:
    -----
        - XTask
        - XMainTask
        >>> ITaskProfile
        >>> XTaskProfile.__init__()


    Deprecated API:
    ----------------
    Starting with XCOFDK-py v3.0 below API functions/properties (formerly part of
    class XTaskProfile) are deprecated and not available anymore:

        >>> @property
        >>> def isSynchronousTask(self) -> int:
        >>>     return self.isSyncTask
        >>>
        >>> def CreateSynchronousTaskProfile():
        >>>     return XTaskProfile.CreateSyncTaskProfile()
        >>>
        >>> def CreateAsynchronousTaskProfile():
        >>>     return XTaskProfile.CreateAsyncTaskProfile()
    """

    __slots__ = [ '__impl' ]


    # --------------------------------------------------------------------------
    # 1) c-tor / built-in
    # --------------------------------------------------------------------------
    def __init__(self):
        """
        Constructor (initializer) of an instances of this class.

        It initalizes this instance by assigning the respective default value
        to each of its properties.

        Note:
        ------
            - A new instance of this class is always valid after construction.
            - Later, an instance may become invalid if an attemp to change its
              current configuration fails.

        See:
        -----
            - class XTask
            - class XMainTask
            >>> ITaskProfile.isValid
        """
        super().__init__()
        self.__impl = _XTaskPrfImpl()


    def __str__(self) -> str:
        """
        Returns:
        ----------
            A nicely printable string representation of this instance.
        """
        return str(self.__impl)


    @staticmethod
    def CreateSyncTaskProfile(aliasName_ : str =None, bPrivilegedTask_ =False, runPhaseFreqMS_ : Union[int, float] =0):
        """
        Create a new task profile which can be used to create a synchronous
        task.

        Parameters:
        -------------
            - aliasName_ :
              alias name to be used for the task instance to be created.
            - bPrivilegedTask_ :
              if True the task instance to be created will be considered
              prrviledged.

        Returns:
        ----------
            If successful new task profile instance initialized according to
            the passed in arguments and usable for creating synchronous tasks,
            None otherwise.

        See:
        -----
            >>> ITaskProfile.aliasName
            >>> ITaskProfile.isPrivilegedTask
            >>> XTaskProfile.CreateAsyncTaskProfile()
        """
        res = XTaskProfile()
        res.isPrivilegedTask = bPrivilegedTask_
        res.isSyncTask       = True
        res.runPhaseFrequencyMS = runPhaseFreqMS_

        if aliasName_ is not None:
            res.aliasName = aliasName_

        if not res.isValid:
            res = None
        elif res.aliasName != aliasName_:
            res = None
        elif res.isPrivilegedTask != bPrivilegedTask_:
            res = None

        return res


    @staticmethod
    def CreateAsyncTaskProfile(aliasName_ : str =None, bPrivilegedTask_ =False, runPhaseFreqMS_ : Union[int, float] =None):
        """
        Create a new task profile which can be used to create an asynchronous
        task.

        Parameters:
        -------------
            - aliasName_ :
              alias name to be used for the task instance to be created.
            - bPrivilegedTask_ :
              if True the task instance to be created will be considered
              prrviledged.
            - runPhaseFreqMS_ :
              run phase frequency to be used for the task instance to be created.

        Returns:
        ----------
            If successful new task profile instance initialized according to
            the passed in arguments and usable for creating asynchronous tasks,
            None otherwise.

        See:
        -----
            >>> ITaskProfile.aliasName
            >>> ITaskProfile.isPrivilegedTask
            >>> ITaskProfile.runPhaseFrequencyMS
            >>> XTaskProfile.CreateAsyncTaskProfile()
        """
        res = XTaskProfile()
        res.isSyncTask       = False
        res.isPrivilegedTask = bPrivilegedTask_

        if aliasName_ is not None:
            res.aliasName = aliasName_
        if runPhaseFreqMS_ is not None:
            res.runPhaseFrequencyMS = runPhaseFreqMS_

        if not res.isValid:
            res = None
        elif res.aliasName != aliasName_:
            res = None
        elif res.isPrivilegedTask != bPrivilegedTask_:
            res = None
        elif runPhaseFreqMS_ is not None:
            _freq = int(1000 * runPhaseFreqMS_) if isinstance(runPhaseFreqMS_, float) else runPhaseFreqMS_

            if res.runPhaseFrequencyMS != _freq:
                res = None
        return res
    # --------------------------------------------------------------------------
    #END 1) c-tor / built-in
    # --------------------------------------------------------------------------


    # --------------------------------------------------------------------------
    # 2) API basic (read-only) configuration
    # --------------------------------------------------------------------------
    @property
    def isValid(self) -> bool:
        """
        See:
        -----
            >>> ITaskProfile.isValid
        """
        return self.__impl.isValid


    @property
    def isFrozen(self) -> bool:
        """
        See:
        -----
            >>> ITaskProfile.isFrozen
        """
        return self.__impl.isFrozen


    @property
    def isMainTask(self) -> bool:
        """
        See:
        -----
            >>> ITaskProfile.isMainTask
        """
        return self.__impl.isMainTask


    @property
    def isPrivilegedTask(self) -> bool:
        """
        See:
        -----
            >>> ITaskProfile.isPrivilegedTask
        """
        return self.__impl.isPrivilegedTask


    @isPrivilegedTask.setter
    def isPrivilegedTask(self, bPrivileged_ : bool):
        """
        See:
        -----
            >>> ITaskProfile.isPrivilegedTask
        """
        self.__impl.isPrivilegedTask = bool(bPrivileged_)


    @property
    def isSyncTask(self) -> bool:
        """
        See:
        -----
            >>> ITaskProfile.isSyncTask
        """
        return self.__impl.isSyncTask


    @isSyncTask.setter
    def isSyncTask(self, bSynchronousTask_ : bool):
        """
        See:
        -----
            >>> ITaskProfile.isSyncTask
        """
        self.__impl.isSyncTask = bool(bSynchronousTask_)


    @property
    def aliasName(self) -> str:
        """
        See:
        -----
            >>> ITaskProfile.aliasName
        """
        return self.__impl.aliasName


    @aliasName.setter
    def aliasName(self, aliasName_ : str):
        """
        See:
        -----
            >>> ITaskProfile.aliasName
        """
        self.__impl.aliasName = aliasName_
    # --------------------------------------------------------------------------
    #END 2) API basic (read-only) configuration
    # --------------------------------------------------------------------------


    # --------------------------------------------------------------------------
    # 3) API 3-PhXF configuration
    # --------------------------------------------------------------------------
    @property
    def isRunPhaseEnabled(self) -> bool:
        """
        See:
        -----
            >>> ITaskProfile.isRunPhaseEnabled
        """
        return self.__impl.isRunPhaseEnabled


    @property
    def isSetupPhaseEnabled(self) -> bool:
        """
        See:
        -----
            >>> ITaskProfile.isSetupPhaseEnabled
        """
        return self.__impl.isSetupPhaseEnabled


    @isSetupPhaseEnabled.setter
    def isSetupPhaseEnabled(self, bEnableSetup_ : bool):
        """
        See:
        -----
            >>> ITaskProfile.isSetupPhaseEnabled
        """
        self.__impl.isSetupPhaseEnabled = bool(bEnableSetup_)


    @property
    def isTeardownPhaseEnabled(self) -> bool:
        """
        See:
        -----
            >>> ITaskProfile.isTeardownPhaseEnabled
        """
        return self.__impl.isTeardownPhaseEnabled


    @isTeardownPhaseEnabled.setter
    def isTeardownPhaseEnabled(self, bEnableTeardown_ : bool):
        """
        See:
        -----
            >>> ITaskProfile.isTeardownPhaseEnabled
        """
        self.__impl.isTeardownPhaseEnabled = bool(bEnableTeardown_)
    # --------------------------------------------------------------------------
    #END 3) API 3-PhXF configuration
    # --------------------------------------------------------------------------


    # --------------------------------------------------------------------------
    # 4) API queue configuration
    # --------------------------------------------------------------------------
    @property
    def isInternalQueueEnabled(self) -> bool:
        """
        See:
        -----
            >>> ITaskProfile.isInternalQueueEnabled
        """
        return self.__impl.isInternalQueueEnabled


    @property
    def isExternalQueueEnabled(self) -> bool:
        """
        See:
        -----
            >>> ITaskProfile.isExternalQueueEnabled
        """
        return self.__impl.isExternalQueueEnabled


    @isExternalQueueEnabled.setter
    def isExternalQueueEnabled(self, bExternalQueue_ : bool):
        """
        See:
        -----
            >>> ITaskProfile.isExternalQueueEnabled
        """
        self.__impl.isExternalQueueEnabled = bool(bExternalQueue_)


    @property
    def isExternalQueueBlocking(self) -> bool:
        """
        See:
        -----
            >>> ITaskProfile.isExternalQueueBlocking
        """
        return self.__impl.isExternalQueueBlocking


    @isExternalQueueBlocking.setter
    def isExternalQueueBlocking(self, bBlockingExtQueue_ : bool):
        """
        See:
        -----
            >>> ITaskProfile.isExternalQueueBlocking
        """
        self.__impl.isExternalQueueBlocking = bool(bBlockingExtQueue_)
    # --------------------------------------------------------------------------
    #END 4) API queue configuration
    # --------------------------------------------------------------------------


    # --------------------------------------------------------------------------
    # 5) API timing configuration
    # --------------------------------------------------------------------------
    @staticmethod
    def GetDefaultRunPhaseFrequencyMS() -> int:
        """
        Returns:
        ----------
            A positive integer value as amount of time (in milliseconds) used
            for default-configuration of the frequency of a cyclic run phase.

        Note:
        ------
              - Current default value returned is 100.

        See:
        -----
            >>> ITaskProfile.isRunPhaseEnabled
            >>> ITaskProfile.isExternalQueueBlocking
            >>> ITaskProfile.runPhaseFrequencyMS
            >>> XTaskProfile.GetDefaultRunPhaseMaxProcessingTimeMS()
        """
        return _XTaskPrfImpl.GetDefaultRunPhaseFrequencyMS()


    @staticmethod
    def GetDefaultRunPhaseMaxProcessingTimeMS() -> int:
        """
        Returns:
        ----------
            A positive integer value as amount of time (in milliseconds) used
            for default-configuration of the estimated maximum processing time
            of a cyclic run phase.

        Note:
        ------
            - Current default value returned is 50.

        See:
        -----
            >>> ITaskProfile.isRunPhaseEnabled
            >>> ITaskProfile.isExternalQueueBlocking
            >>> ITaskProfile.runPhaseMaxProcessingTimeMS
            >>> XTaskProfile.GetDefaultRunPhaseFrequencyMS()
        """
        return _XTaskPrfImpl.GetDefaultRunPhaseMaxProcessingTimeMS()


    @property
    def isCyclicRunPhase(self) -> bool:
        """
        See:
        -----
            >>> ITaskProfile.isCyclicRunPhase
        """
        return self.__impl.isCyclicRunPhase


    @property
    def isSingleCycleRunPhase(self) -> bool:
        """
        See:
        -----
            >>> ITaskProfile.isSingleCycleRunPhase
        """
        return self.__impl.isSingleCycleRunPhase


    @property
    def runPhaseFrequencyMS(self) -> int:
        """
        See:
        -----
            >>> ITaskProfile.runPhaseFrequencyMS
        """
        return self.__impl.runPhaseFrequencyMS


    @runPhaseFrequencyMS.setter
    def runPhaseFrequencyMS(self, runPhaseFreqMS_ : Union[int, float]):
        """
        See:
        -----
            >>> ITaskProfile.runPhaseFrequencyMS
        """
        self.__impl.runPhaseFrequencyMS = runPhaseFreqMS_


    @property
    def runPhaseMaxProcessingTimeMS(self) -> int:
        """
        See:
        -----
            >>> ITaskProfile.runPhaseMaxProcessingTimeMS
        """
        return self.__impl.runPhaseMaxProcessingTimeMS


    @runPhaseMaxProcessingTimeMS.setter
    def runPhaseMaxProcessingTimeMS(self, runPhaseMaxProcTimeMS_ : Union[int, float]):
        """
        See:
        -----
            >>> ITaskProfile.runPhaseMaxProcessingTimeMS
        """
        self.__impl.runPhaseMaxProcessingTimeMS = runPhaseMaxProcTimeMS_
    # --------------------------------------------------------------------------
    #END 5) API timing configuration
    # --------------------------------------------------------------------------


    # --------------------------------------------------------------------------
    # 6) API supplementary interface
    # --------------------------------------------------------------------------
    @override
    def CloneProfile(self):
        """
        See:
        -----
            >>> ITaskProfile.CloneProfile()
        """
        return self.__impl.CloneProfile()


    @override
    def _AssignProfile(self, rhs_):
        """
        See:
        -----
            >>> ITaskProfile._AssignProfile()
        """
        return self.__impl._AssignProfile(rhs_)
    # --------------------------------------------------------------------------
    #END 6) API supplementary interface
    # --------------------------------------------------------------------------
#END class XTaskProfile
