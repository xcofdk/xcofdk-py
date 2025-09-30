# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : ifxtaskprf.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from typing import Union

from xcofdk.fwcom import EExecutionCmdID


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class ITaskProfile:
    """
    This interface class represents the collection of all pre-instantiation
    properties needed to be laid out for the runtime configuration of a task
    instance to be created.

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
        - XTaskProfile
        - XTask
    """

    __slots__ = []


    # --------------------------------------------------------------------------
    # 1) c-tor / built-in
    # --------------------------------------------------------------------------
    def __init__(self):
        """
        See:
        -----
            - XTaskProfile.__init__()
        """
        pass


    def __str__(self) -> str:
        """
        See:
        -----
            >>> ITaskProfile.ToString()
        """
        pass
    # --------------------------------------------------------------------------
    #END 1) c-tor / built-in
    # --------------------------------------------------------------------------


    # --------------------------------------------------------------------------
    # 2) API basic (read-only) configuration
    # --------------------------------------------------------------------------
    @property
    def isValid(self) -> bool:
        """
        Returns:
        ----------
            True if current configuration of this instance is valid,
            False otherwise.

        Note:
        ------
            - A new instance of this class is always valid after construction.
            - Lateer, an instance may become invalid if an attemp to change its
              current configuration fails.
            - There is no corresponding setter for this property.

        See:
        -----
            >>> ITaskProfile.isFrozen
        """
        pass


    @property
    def isFrozen(self) -> bool:
        """
        Returns:
        ----------
            True if this instance has been made read-only, False otherwise.

        Note:
        ------
            - A frozen task profile will refuse to make changes to its current
              configuration via any of its property setters.
            - There is no corresponding setter for this property.

        See:
        -----
            >>> ITaskProfile.isValid
            >>> ITaskProfile.__init__()
        """
        pass


    @property
    def isMainTask(self) -> bool:
        """
        Returns:
        ----------
            True if this instance is the configuration of application's main
            task, False otherwise.

        Note:
        ------
            - The property defaults to False.
            - It is set to True when creating application's main task.
            - There is no corresponding setter for this property.
        """
        pass


    @property
    def isPrivilegedTask(self) -> bool:
        """
        Returns:
        ----------
            True if task(s) to be created using this instance shall be
            considered priviledged, False otherwise.

        Note:
        ------
            - The property defaults to False.
            - Privileged task instances are granted particular rights or
              permissions.
        """
        pass


    @isPrivilegedTask.setter
    def isPrivilegedTask(self, vv_ : bool):
        """
        Setter property used to configure a task with special rights or
        permissions are granted.

        Parameters:
        -------------
            - vv_ :
              True if the privileged configuration shall be enabled,
              False otherwise.

        See:
        -----
            >>> ITaskProfile.isFrozen
        """
        pass


    @property
    def isSyncTask(self) -> bool:
        """
        Returns:
        ----------
            True for configuration of synchronous execution type, False
            otherwise.

        Note:
        ------
            - The property defaults to False.
        """
        pass


    @isSyncTask.setter
    def isSyncTask(self, vv_ : bool):
        """
        Setter property used to configure synchronous execution type.

        Parameters:
        -------------
            - vv_ :
              True to enable synchronous configuration, False otherwise.

        See:
        -----
            >>> ITaskProfile.isFrozen
        """
        pass


    @property
    def aliasName(self) -> str:
        """
        Returns:
        ----------
            If configured the alias name (to be) used for a task instance,
            None otherwise.

        Note:
        ------
            - The property defaults to None.
            - If not configured, then the framework will later auto-generate
              one based on the type of the task instance to be created:
                Tsk_<INST_NO>   : for instances of class RCTask without
                                  external queue support
                CTsk_<INST_NO>  : for instances of class RCTask with
                                  external queue support
                XTsk_<INST_NO>  : for instances of class XTask without
                                  external queue support
                CXTsk_<INST_NO> : for instances of class XTask with
                                  external queue support
              with:
                - 'INST_NO' is the unique instance number of the task instance.
                - 'C' stands for 'capable of full Communication',
                  something available to a task only if created with
                  support for external queue requested for.
            - Also, for a configured alias name with a trailing '_' the
              above-mentioned 'INST_NO' will be appended to.

        See:
        -----
            >>> ITaskProfile.isExternalQueueEnabled
        """
        pass


    @aliasName.setter
    def aliasName(self, vv_ : str):
        """
        Setter property used to configure the alias name of a task.

        Parameters:
        -------------
            - vv_ :
              an arbitrary, non-empty and printable string literal without
              spaces which optionally may have a trailing '_'.

        See:
        -----
            >>> ITaskProfile.isFrozen
        """
        pass
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
            True if the run phase of task's 3-PhXF is enabled, False otherwise.

        Note:
        ------
            - The property defaults to True.
            - It resolves to False, if and only if the instacne is configured
              to support blocking external queue.
            - There is no corresponding setter for this property.

        See:
        -----
            >>> ITaskProfile.isExternalQueueBlocking
        """
        pass


    @property
    def isSetupPhaseEnabled(self) -> bool:
        """
        Returns:
        ----------
            True if the setup phase of task's 3-PhXF is enabled, False
            otherwise.

        Note:
        ------
            - The property defaults to False.
        """
        pass


    @isSetupPhaseEnabled.setter
    def isSetupPhaseEnabled(self, vv_ : bool):
        """
        Setter property used to enable the seup phase.

        Parameters:
        -------------
            - vv_ :
            True if the setup phase of task's 3-PhXF shall be enabled, False
            otherwise.

        See:
        -----
            >>> ITaskProfile.isFrozen
        """
        pass


    @property
    def isTeardownPhaseEnabled(self) -> bool:
        """
        Returns:
        ----------
            True if the teardown phase of task's 3-PhXF is enabled, False
            otherwise.

        Note:
        ------
            - The property defaults to False.
        """
        pass

    @isTeardownPhaseEnabled.setter
    def isTeardownPhaseEnabled(self, vv_ : bool):
        """
        Setter property used to enable the teardown phase.

        Parameters:
        -------------
            - vv_ :
            True if the teardown phase of task's 3-PhXF shall be enabled, False
            otherwise.

        See:
        -----
            >>> ITaskProfile.isFrozen
        """
        pass
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
            True if a task is enabled to have support for internal queue, False
            otherwise.

        Note:
        ------
            - The property defaults to False.
            - There is currently no corresponding setter for this property.
        """
        pass


    @property
    def isExternalQueueEnabled(self) -> bool:
        """
        Returns:
        ----------
            True if a task is enabled to have support for external queue, False
            otherwise.

        Note:
        ------
            - The property defaults to False.

        See:
        -----
            >>> ITaskProfile.isFrozen
            >>> ITaskProfile.isExternalQueueBlocking
        """
        pass


    @isExternalQueueEnabled.setter
    def isExternalQueueEnabled(self, vv_ : bool):
        """
        Setter property used to enable the support for external queue.

        Parameters:
        -------------
            - vv_ :
            True if support for external queue shall be enabled, False
            otherwise.

        Note:
        ------
            - The property defaults to False.
            - Disabling support for external queue will disable support for
              blocking external queue, too, if it was enabled before.
              This will also re-enable the configuration for the run phase of
              task's 3-PhXF.

        See:
        -----
            >>> ITaskProfile.isFrozen
            >>> ITaskProfile.isExternalQueueBlocking
        """
        pass


    @property
    def isExternalQueueBlocking(self) -> bool:
        """
        Returns:
        ----------
            True if a task is enabled to have support for blocking external
            queue, False otherwise.

        Note:
        ------
            - The property defaults to False.
            - If enabled, then support for external queue is enabled (if not
              done yet), too, while the configuration of the run phase of such
              a taks is disabled.

        See:
        -----
            >>> ITaskProfile.isRunPhaseEnabled
            >>> ITaskProfile.isExternalQueueEnabled
        """
        pass


    @isExternalQueueBlocking.setter
    def isExternalQueueBlocking(self, vv_ : bool):
        """
        Setter property used to enable the support for blocking external queue.

        Parameters:
        -------------
            - vv_ :
            True if support for blocking external queue shall be enabled, False
            otherwise.

        Note:
        ------
            - If enabled, then support for external queue is enabled (if not
              done already), too, while the configuration of the run phase of
              such a taks is auto-disabled by the framework.
            - Contrarily, if disabled, then the configuration of the run phase of
              such a taks is auto-enabled by the framework.

        See:
        -----
            >>> ITaskProfile.isFrozen
            >>> ITaskProfile.isRunPhaseEnabled
            >>> ITaskProfile.isExternalQueueEnabled
        """
        pass
    # --------------------------------------------------------------------------
    #END 4) API queue configuration
    # --------------------------------------------------------------------------


    # --------------------------------------------------------------------------
    # 5) API timing configuration
    # --------------------------------------------------------------------------
    @property
    def isCyclicRunPhase(self) -> bool:
        """
        Returns:
        ----------
            True if the configured run phase frequency is larger than 0 (i.e.
            meant as an instruction to the framework to execute the run phase
            repeatedly), False otherwise.

        Note:
        ------
            - Whether the run phase of a task is cyclically executed by the
              framework basically depends on the return value of the respective
              3-PhXF callback method.
            - However, if this property resolves to True, then the framework
              will execute the above-mentioned callback at the specified
              frequency, as long as it returns with an indication to continue
              the execution by the next iteration.
            - Also, the application code may use it as a supplementary property
              to control the return value of the run phase callback
              programmatically for advanced use cases.

        See:
        -----
            >>> ITaskProfile.isSingleCycleRunPhase
            >>> ITaskProfile.isRunPhaseEnabled
            >>> ITaskProfile.isExternalQueueEnabled
            >>> ITaskProfile.runPhaseFrequencyMS
            >>> EExecutionCmdID
        """
        pass


    @property
    def isSingleCycleRunPhase(self) -> bool:
        """
        Returns:
        ----------
            True if the configured run phase frequency is set to 0 (i.e. meant
            as an instruction to the framework to execute the runphase only
            once), False otherwise.

        Note:
        ------
            - Whether the run phase of a task is cyclically executed by the
              framework basically depends on the return value of the respective
              3-PhXF callback method.
            - However, if this property resolves to True, then the framework will
              execute the above-mentioned callback only once, even if it returned
              with an indication to continue the execution by the next iteration.
            - Also, the application code may use it as a supplementary property
              to control the return value of the run phase callback
              programmatically for advanced use cases.

        See:
        -----
            >>> ITaskProfile.isCyclicRunPhase
            >>> ITaskProfile.isRunPhaseEnabled
            >>> ITaskProfile.isExternalQueueEnabled
            >>> ITaskProfile.runPhaseFrequencyMS
            >>> EExecutionCmdID
        """
        pass


    @property
    def runPhaseFrequencyMS(self) -> int:
        """
        Returns:
        ----------
            A non-negatve integer value as amount of time (in milliseconds) used
            to configure a task's run phase frequency.

        Note:
        ------
            - It defaults to a pre-defined value of:
                    0 : for synchronous tasks (that is non-cyclic)
                  100 : for asynchronous tasks (that is cyclic)
            - However, by changing the default via the setter of this property,
              tasks can be turned to be either cyclic or single-cycle regardless
              of their execution type.

        See:
        -----
            >>> ITaskProfile.isCyclicRunPhase
            >>> ITaskProfile.isSingleCycleRunPhase
        """
        pass


    @runPhaseFrequencyMS.setter
    def runPhaseFrequencyMS(self, vv_ : Union[int, float]):
        """
        Setter property used to configure the run phase frequency of a task
        instance to be created.

        Parameters:
        -------------
            - vv_ :
              non-negative amount of time used as run phase frequency:
                  - for integer values, millisecond will be assumed as the
                    desired resolution or unit of the specified frequency,
                  - for floating-point values, second will be assumed as the
                    desired resolution or unit of the specified frequency.

        See:
        -----
            >>> ITaskProfile.isFrozen
        """
        pass


    @property
    def runPhaseMaxProcessingTimeMS(self) -> int:
        """
        Returns:
        ----------
            A non-negatve integer value as amount of time (in milliseconds)
            used to configure the estimated max. processing time of each
            iteration of the run phase.

        Note:
        ------
            - It defaults to a pre-defined value of 50 [ms].
        """
        pass


    @runPhaseMaxProcessingTimeMS.setter
    def runPhaseMaxProcessingTimeMS(self, vv_ : Union[int, float]):
        """
        Setter property used to configure the estimated max. processing time of
        each iteration of the run phase.

        Parameters:
        -------------
            - vv_ :
              non-negative amount of time used as the estimated max. processing
              time of each iteration of the run phase:
                  - for integer values, millisecond will be assumed as the
                    desired resolution or unit,
                  - for floating-point values, second will be assumed as the
                    desired resolution or unit.

        See:
        -----
            >>> ITaskProfile.isFrozen
        """
        pass
    # --------------------------------------------------------------------------
    #END 5) API timing configuration
    # --------------------------------------------------------------------------


    # --------------------------------------------------------------------------
    # 6) API supplementary interface
    # --------------------------------------------------------------------------
    def ToString(self) -> str:
        """
        Returns:
        ----------
            A nicely printable string representation of this instance.
        """
        pass


    def CloneProfile(self):
        """
        Create a copy or clone of this instance.

        Returns:
        ----------
            The copy instance to be created.

        Note:
        ------
            - The cloned profile returned is an exact copy of this instance,
              except it is configured by default to not be a main task profile.

        See:
        -----
            >>> ITaskProfile.isFrozen
            >>> ITaskProfile.isMainTask
            >>> ITaskProfile._AssignProfile
        """
        pass


    def _AssignProfile(self, rhs_):
        """
        Protected method designed for inernal purposes of this class.

        Parameters:
        -------------
            - rhs_ :
              task profile instance whose configuration shall be copied to this
              instance except for the property regarding being main task
              profile while is kept unchanged for this instance.

        Note:
        ------
            - The operation will be ignored if this instance is (already) frozen.

        See:
        -----
            >>> ITaskProfile.isFrozen
            >>> ITaskProfile.CloneProfile
        """
        pass
    # --------------------------------------------------------------------------
    #END 6) API supplementary interface
    # --------------------------------------------------------------------------
#END class ITaskProfile
