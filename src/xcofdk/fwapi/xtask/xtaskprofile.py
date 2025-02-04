# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xtaskprofile.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from typing import Union

from xcofdk._xcofw.fw.fwssys.fwcore.apiimpl.xtask.xtaskprfbase import _XTaskProfileBase


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class XTaskProfile(_XTaskProfileBase):
    """
    This class is a container of all defined properties available for instances
    of class XTask (or of classes derived from).

    Strictly spoken, the term 'defined properties' rather means the collection
    of all 'pre-instantiation' properties needed to lay out, i.e. to configure,
    the execution frame of an instance of class XTask to be created (see section
    'Execution frame 3-PhXF' in class description of XTask).

    In other words, an instance of this class used to create a new task instance
    is actually the 'configurator' of that task with respect to its runtime
    constitution.

    Instances of this class are created with all properies set to their
    respective devault value. Sample code snippet below prints out the default
    values:
        >>> from xcofdk.fwcom       import xlogif
        >>> from xcofdk.fwapi.xtask import XTaskProfile
        >>>
        >>> #...
        >>> xtPrf = XTaskProfile()
        >>> xlogif.LogInfo(f'xtPrf: {xtPrf}')
        >>>
        >>> # The outuput will look like as shown below:
        >>> #   [11:13:29.075 XINF] xuPrf:  XTask profile :
        >>> #        aliasName                   : None
        >>> #        isMainTask                  : False
        >>> #        isPrivilegedTask            : False
        >>> #        isSynchronousTask           : False
        >>> #        isRunPhaseEnabled           : True
        >>> #        isSetupPhaseEnabled         : False
        >>> #        isTeardownPhaseEnabled      : False
        >>> #        isInternalQueueEnabled      : False
        >>> #        isExternalQueueEnabled      : False
        >>> #        isExternalQueueBlocking     : False
        >>> #        runPhaseFrequencyMS         : 100
        >>> #        runPhaseMaxProcessingTimeMS : 50

    After a task profile instance is created, its modifiable properties can be
    changed via their respective setter. Doing so, that instance represents then
    a properly configured task profile ready to be passed to the constructor
    of the next task instance to be created.

    Once the creation of an instance of class XTask is succeeded, the associated
    task profile instance of that task becomes 'frozen' making the profile is an
    internal, read-only source of information only whenever it is accessed.

    For quick orientation and guidance on by when to use what, the interface is
    arranged in logical, context-driven subsets each labeled by a comment block
    of the form:
        >>> # --------------------------------------------------------------
        >>> # title of interface subset
        >>> # --------------------------------------------------------------

    Currently available interface subsets of class XTaskProfile are as follows:
        1) API construction
        2) API basic (read-only) configuration
        3) API 3-PhXF configuration
        4) API queue configuration
        5) API timing configuration
        6) API supplementary interface

    See:
    -----
        - XTask
        - MainXTask
        - XTaskProfile.__init__()
        - XTaskProfile.isFrozen
    """

    __slots__ = []


    # --------------------------------------------------------------------------
    # 1) API construction
    # --------------------------------------------------------------------------
    @staticmethod
    def CreateSynchronousTaskProfile(aliasName_ : str =None, bPrivilegedTask_ =False, runPhaseFreqMS_ : Union[int, float] =0):
        """
        Create a new task profile which can be used to create a synchronous task.

        Parameters:
        -------------
            - aliasName_ :
              alias name (if any) to be used to initialize the respective
              property of the instance to be created.
            - bPrivilegedTask_ :
              boolean flag to be used to initialize the respective property of
              the instance to be created.

        Returns:
        ----------
            If successful new task profile instance initialized according to
            the passed in arguments and usable for creating synchronous tasks,
            None otherwise.

        See:
        -----
            - XTaskProfile.aliasName
            - XTaskProfile.isPrivilegedTask
        """
        res = XTaskProfile()
        res.isPrivilegedTask    = bPrivilegedTask_
        res.isSynchronousTask   = True
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
    def CreateAsynchronousTaskProfile(aliasName_ : str =None, bPrivilegedTask_ =False, runPhaseFreqMS_ : Union[int, float] =None):
        """
        Create a new task profile which can be used to create an asynchronous task.

        Parameters:
        -------------
            - aliasName_ :
              alias name (if any) to be used to initialize the respective
              property of the instance to be created.
            - bPrivilegedTask_ :
              boolean flag to be used to initialize the respective property of
              othe instance to be created.
            - runPhaseFreqMS_ :
              run phase frequency (if any) to be used to initialize the
              respective property of the instance to be created.

        Returns:
        ----------
            If successful new task profile instance initialized according to
            the passed in arguments and usable for creating asynchronous tasks,
            None otherwise.

        See:
        -----
            - XTaskProfile.aliasName
            - XTaskProfile.isPrivilegedTask
            - XTaskProfile.runPhaseFrequencyMS
        """
        res = XTaskProfile()
        res.isPrivilegedTask  = bPrivilegedTask_
        res.isSynchronousTask = False

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


    def __init__(self):
        """
        Constructor (initializer) of instances of this class.

        It initalizes this instance by assigning the respective default value
        to each of its properties.

        Note:
        ------
            - New task profile instances are always valid.
            - See also the description of this class above.

        See:
        -----
            - XTask
            - MainXTask
            - XTaskProfile.isValid
        """
        super().__init__()
    # --------------------------------------------------------------------------
    #END 1) API construction
    # --------------------------------------------------------------------------


    def __str__(self):
        """
        String representation of this instance.

        Returns:
        ----------
            A string object as representation of this instance.
        """
        return _XTaskProfileBase.__str__(self)


    # --------------------------------------------------------------------------
    # 2) API basic (read-only) configuration
    # --------------------------------------------------------------------------
    @property
    def isValid(self) -> bool:
        """
        Returns:
        ----------
            True if this instance is valid, False otherwise.

        Note:
        ------
            This property is basically used for internal purposes related to
            cloned objects of this class.
        """
        return self._isValid


    @property
    def isFrozen(self) -> bool:
        """
        Returns:
        ----------
            True if this instance is made read-only, False otherwise.

        Note:
        ------
            A frozen task profile will refuse to make changes to its current
            configuration via any of its property setters.

        See:
        -----
            XTaskProfile
        """
        return self._isFrozen


    @property
    def isMainTask(self) -> bool:
        """
        Returns:
        ----------
            True if this instance is configured to be associated with the
            singleton of class MainXTask, False otherwise.

        Note:
        ------
            - The property defaults to False.
            - It is set to True when creating the singleton of class MainXTask.
            - There is no corresponding setter for this property.

        See:
        -----
            MainXTask.__init__()
        """
        return self._isMainTask


    @property
    def isPrivilegedTask(self) -> bool:
        """
        Returns:
        ----------
            True if this instance is configured to be associated with a
            privileged task instance, False otherwise.

        Note:
        ------
            - The property defaults to False.
            - Privileged task instances are granted particular rights or
              permissions.

        See:
        -----
            XTask.__init__()
        """
        return self._isPrivilegedTask


    @isPrivilegedTask.setter
    def isPrivilegedTask(self, bPrivileged_ : bool):
        """
        Setter property used to configure a task instance to be created with
        special rights or permissions are granted.

        Parameters:
        -------------
            - bPrivileged_ :
              boolean flag indicating whether privileged configuration shall
              be granted (if True) or not (if False).
        """
        self._isPrivilegedTask = bool(bPrivileged_)


    @property
    def isSynchronousTask(self) -> bool:
        """
        Returns:
        ----------
            True if this instance is configured to be associated with a task
            instance supposed to be executed sychronously, False otherwise.

        Note:
        ------
            - The property defaults to False.
            - Task types are described in class description of XTask.

        See:
        -----
            - XTask
            - XTask.__init__()
        """
        return self._isSynchronousTask


    @isSynchronousTask.setter
    def isSynchronousTask(self, bSynchronousTask_ : bool):
        """
        Setter property used to configure a task instance to be created with
        it is executed synchronously.

        Parameters:
        -------------
            - bSynchronousTask_ :
              boolean flag indicating whether the execution shall be
              synchronously (if True) or not (if False).

        Note:
        ------
            Task types are described in class description of XTask.

        See:
        -----
            - XTask
            - XTask.__init__()
        """
        self._isSynchronousTask = bool(bSynchronousTask_)


    @property
    def aliasName(self) -> str:
        """
        Returns:
        ----------
            If configured the alias name which is used when creating a task
            instance, None otherwise.

        Note:
        ------
            - The property defaults to None.
            - If not configured then the framework will auto-generate a (not
              necessarily unique) alias when creating the associated task
              instance.

        See:
        -----
            - XTask
            - XTask.__init__()
        """
        return self._aliasName


    @aliasName.setter
    def aliasName(self, aliasName_ : str):
        """
        Setter property to configure the alias name of a task instance to be
        created.

        Parameters:
        -------------
            - aliasName_ :
              alias name to be set, it must be a valid Python identifier.

        See:
        -----
            - XTask
            - XTask.__init__()
        """
        self._aliasName = aliasName_
    # --------------------------------------------------------------------------
    #END 2) API basic (read-only) configuration
    # --------------------------------------------------------------------------


    # --------------------------------------------------------------------------
    # 3) API 3-PhXF configuration
    # --------------------------------------------------------------------------
    @property
    def isRunPhaseEnabled(self) -> bool:
        """
        Returns:
        ----------
            True if this instance is configured to be associated with a task
            instance whose run phase of 3-PhXF is enabled, False otherwise.

        Note:
        ------
            - The property defaults to True.
            - It resolves to False, if and only if the instacne is configured
              to enable a blocking external queue.
            - There is no corresponding setter for this property.
            - 3-PhXF is described in class description of XTask.

        See:
        -----
            - XTask
            - XTask.__init__()
            - XTaskProfile.isExternalQueueEnabled
            - XTaskProfile.isExternalQueueBlocking
        """
        return self._isRunPhaseEnabled


    @property
    def isSetupPhaseEnabled(self) -> bool:
        """
        Returns:
        ----------
            True if this instance is configured to be associated with a task
            instance whose setup phase of 3-PhXF is enabled, False otherwise.

        Note:
        ------
            - The property defaults to False.
            - 3-PhXF is described in class description of XTask.

        See:
        -----
            - XTask
            - XTask.__init__()
        """
        return self._isSetupPhaseEnabled


    @isSetupPhaseEnabled.setter
    def isSetupPhaseEnabled(self, bEnableSetup_ : bool):
        """
        Setter property used to configure a task instance to be created with
        its setup phase is enabled.

        Parameters:
        -------------
            - bEnableSetup_ :
              boolean flag indicating whether setup phase configuration shall be
              enabled (if True) or not (if False).

        Note:
        ------
            3-PhXF is described in class description of XTask.

        See:
        -----
            - XTask
            - XTask.__init__()
        """
        self._isSetupPhaseEnabled = bool(bEnableSetup_)


    @property
    def isTeardownPhaseEnabled(self) -> bool:
        """
        Returns:
        ----------
            True if this instance is configured to be associated with a task
            instance whose teardown phase of 3-PhXF is enabled, False otherwise.

        Note:
        ------
            - The property defaults to False.
            - 3-PhXF is described in class description of XTask.

        See:
        -----
            - XTask
            - XTask.__init__()
        """
        return self._isTeardownPhaseEnabled


    @isTeardownPhaseEnabled.setter
    def isTeardownPhaseEnabled(self, bEnableTeardown_ : bool):
        """
        Setter property used to configure a task instance to be created with
        its teardown phase is enabled.

        Parameters:
        -------------
            - bEnableTeardown_ :
              boolean flag indicating whether teardown phase configuration shall
              be enabled (if True) or not (if False).

        Note:
        ------
            3-PhXF is described in class description of XTask.

        See:
        -----
            - XTask
            - XTask.__init__()
        """
        self._isTeardownPhaseEnabled = bool(bEnableTeardown_)
    # --------------------------------------------------------------------------
    #END 3) API 3-PhXF configuration
    # --------------------------------------------------------------------------


    # --------------------------------------------------------------------------
    # 4) API queue configuration
    # --------------------------------------------------------------------------
    @property
    def isInternalQueueEnabled(self) -> bool:
        """
        Returns:
        ----------
            True if this instance is configured to be associated with a task
            instance whose internal queue support is enabled, False otherwise.

        Note:
        ------
            - The property defaults to False.
            - There is currently no corresponding setter for this property.
            - 3-PhXF is described in class description of XTask.

        See:
        -----
            - XTask
            - XTask.__init__()
        """
        return self._isInternalQueueEnabled


    @property
    def isExternalQueueEnabled(self) -> bool:
        """
        Returns:
        ----------
            True if this instance is configured to be associated with a task
            instance whose external queue support is enabled, False otherwise.

        Note:
        ------
            - The property defaults to False.
            - 3-PhXF is described in class description of XTask.

        See:
        -----
            - XTask
            - XTask.__init__()
            - XTaskProfile.isRunPhaseEnabled()
            - XTaskProfile.isExternalQueueBlocking()
        """
        return self._isExternalQueueEnabled


    @isExternalQueueEnabled.setter
    def isExternalQueueEnabled(self, bExternalQueue_ : bool):
        """
        Setter property used to configure a task instance to be created with
        its external support is enabled.

        Parameters:
        -------------
            - bExternalQueue_ :
              boolean flag indicating whether external queue support shall be
              enabled (if True) or not (if False).

        Note:
        ------
            - If the setter property is used to disable external queue, then
              the respective configuration for support of blocking external
              queue will be disabled, too, if it was enabled before.
              In the latter case the run phase configuration will be
              re-enabled.
            - 3-PhXF is described in class description of XTask.

        See:
        -----
            - XTask
            - XTask.__init__()
            - XTaskProfile.isRunPhaseEnabled()
            - XTaskProfile.isExternalQueueBlocking()
        """
        self._isExternalQueueEnabled = bool(bExternalQueue_)


    @property
    def isExternalQueueBlocking(self) -> bool:
        """
        Returns:
        ----------
            True if this instance is configured to be associated with a task
            instance whose external queue support is configured to be blocking,
            False otherwise.

        Note:
        ------
            - The property defaults to False.
            - 3-PhXF is described in class description of XTask.

        See:
        -----
            - XTask
            - XTask.__init__()
            - XTaskProfile.isRunPhaseEnabled()
            - XTaskProfile.isExternalQueueEnabled()
        """
        return self._isExternalQueueBlocking


    @isExternalQueueBlocking.setter
    def isExternalQueueBlocking(self, bBlockingExtQueue_ : bool):
        """
        Setter property used to configure a task instance to be created with
        its external support is enabled.

        Parameters:
        -------------
            - bBlockingExtQueue_ :
              boolean flag indicating whether blocking external queue support
              shall be enabled (if True) or not (if False).

        Note:
        ------
            - If the setter property is used to enable blocking external queue
              support, then the respective configuration for support of external
              queue will be enabled, too, if it was disabled before.
              Also, the run phase configuration will be disabled.
            - If the setter property is used to disable blocking external queue
              support, then the run phase configuration will be re-enabled.
            - 3-PhXF is described in class description of XTask.

        See:
        -----
            - XTask
            - XTask.__init__()
            - XTaskProfile.isRunPhaseEnabled()
            - XTaskProfile.isExternalQueueEnabled()
        """
        self._isExternalQueueBlocking = bool(bBlockingExtQueue_)
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
            for default-configuration of the frequency of the (cyclic) run
            phase.

        Note:
        ------
              - Current default value returned is 100.
              - Run phase is described in section 'Execution frame 3-PhXF' in
                class description of XTask.

        See:
        -----
            - XTask
            - XTaskProfile
            - XTaskProfile.runPhaseFrequencyMS
        """
        return _XTaskProfileBase._GetDefaultRunPhaseFrequencyMS()


    @staticmethod
    def GetDefaultRunPhaseMaxProcessingTimeMS() -> int:
        """
        Returns:
        ----------
            A positive integer value as amount of time (in milliseconds) used
            for default-configuration of the estimated maximum processing time
            of the (cyclic) run phase.

        Note:
        ------
            - Current default value returned is 50.
            - Run phase is described in section 'Execution frame 3-PhXF' in
              class description of XTask.

        See:
        -----
            - XTask
            - XTaskProfile
            - XTaskProfile.runPhaseMaxProcessingTimeMS
        """
        return _XTaskProfileBase._GetDefaultRunPhaseMaxProcessingTimeMS()


    @property
    def isSingleCycleRunPhase(self) -> bool:
        """
        Returns:
        ----------
            True if this instance is configured to be associated with a task
            instance whose run phase frequency is set to 0, False otherwise.

        Note:
        ------
            - 3-PhXF is described in class description of XTask.
            - The framework never evaluates this property when executing a task.
              The application code, however, may use it as a supplementary
              property controlling the return value of the callback method
              'RunXTask()' programmatically for advanced use cases.

        See:
        -----
            - XTask
            - XTaskProfile.runPhaseFrequencyMS
        """
        return self._isSingleCycleRunPhase


    @property
    def runPhaseFrequencyMS(self) -> int:
        """
        Returns:
        ----------
            A non-negatve integer value as amount of time (in milliseconds) used
            to configure a task's run phase frequency.

        Note:
        ------
            - It defaults to the return value of the static method
              'GetDefaultRunPhaseFrequencyMS()'.
            - The special value of 0 will make the run phase become so-called
              'single-cycle run phase'.
            - Run phase is described in section 'Execution frame 3-PhXF' in
              class description of XTask.

        See:
        -----
            - XTask
            - XTaskProfile
            - XTaskProfile.isSingleCycleRunPhase
            - XTaskProfile.GetDefaultRunPhaseFrequencyMS()
        """
        return self._runPhaseFrequencyMS


    @runPhaseFrequencyMS.setter
    def runPhaseFrequencyMS(self, runPhaseFreqMS_ : Union[int, float]):
        """
        Setter property used to configure the run phase frequency of a task
        instance to be created.

        Parameters:
        -------------
            - runPhaseFreqMS_ :
              non-negative amount of time used as run phase frequency.

        Note:
        ------
            - If an integer value is passed to, millisecond will be assumed as
              the resolution or unit of the specified frequency.
            - If a float vlaue is passed to, second will be assumed as the
              resolution or unit of the specified frequency. It will be
              converted to its equivalent millisecond value then.
            - Run phase is described in section 'Execution frame 3-PhXF' in
              class description of XTask.

        See:
        -----
            - XTask
            - XTask.__init__()
        """
        self._runPhaseFrequencyMS = runPhaseFreqMS_


    @property
    def runPhaseMaxProcessingTimeMS(self) -> int:
        """
        Returns:
        ----------
            A positive integer value as amount of time (in milliseconds) used
            to configure the estimated maximum processing time of a task's run
            phase.

        Note:
        ------
            - It defaults to the return value of the static method
              'GetDefaultRunPhaseMaxProcessingTimeMS()'.
            - Run phase is described in section 'Execution frame 3-PhXF' in
              class description of XTask.

        See:
        -----
            - XTask
            - XTaskProfile
            - XTaskProfile.GetDefaultRunPhaseMaxProcessingTimeMS()
        """
        return self._runPhaseMaxProcessingTimeMS


    @runPhaseMaxProcessingTimeMS.setter
    def runPhaseMaxProcessingTimeMS(self, runPhaseMaxProcTimeMS_ : Union[int, float]):
        """
        Setter property used to configure the estimated maximum processing time
        of a task's run phase.

        Parameters:
        -------------
            - runPhaseMaxProcTimeMS_ :
              positive amount of time used as the estimated maximum processing
              time of the run phase.

        Note:
        ------
            - If an integer value is passed to, millisecond will be assumed as
              the resolution or unit of the specified time value.
            - If a float vlaue is passed to, second will be assumed as the
              resolution or unit of the specified time value. It will be
              converted to its equivalent millisecond value then.
            - Run phase is described in section 'Execution frame 3-PhXF' in
              class description of XTask.

        See:
        -----
            - XTask
            - XTask.__init__()
        """
        self._runPhaseMaxProcessingTimeMS = runPhaseMaxProcTimeMS_
    # --------------------------------------------------------------------------
    #END 5) API timing configuration
    # --------------------------------------------------------------------------


    # --------------------------------------------------------------------------
    # 6) API supplementary interface
    # --------------------------------------------------------------------------
    def CloneProfile(self):
        """
        Create a copy or clone of this instance.

        Returns:
        ----------
            The copy instance to be created.

        Note:
        ------
            - The property below of the returned object will still resolve to
              False regardless of the respective configuration of this instance:
                  >>> XTaskProfile.isMainTask == False

        See:
        -----
            - XTaskProfile.__init__()
            - XTaskProfile.isMainTask
            - XTaskProfile._AssignProfile()
        """
        return _XTaskProfileBase._Clone(self)


    def _AssignProfile(self, rhs_):
        """
        Protected method designed for inernal purposes of this class.

        Parameters:
        -------------
            - rhs_ :
              task profile instance whose configuration shall be copied to this
              instance except for the property 'XTaskProfile.isMainTask' which
              remains unchanged.

        Note:
        ------
            Requested operation will be ignored if this instance is (already)
            frozen.

        See:
        -----
            - XTaskProfile.isFrozen
            - XTaskProfile.isMainTask
            - XTaskProfile.CloneProfile()
        """
        return _XTaskProfileBase._AssignProfile(self, rhs_)
    # --------------------------------------------------------------------------
    #END 6) API supplementary interface
    # --------------------------------------------------------------------------
#END class XTaskProfile
