# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xmaintask.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from typing import Union

from xcofdk.fwapi     import ITask
from xcofdk.fwapi.xmt import IXTask
from xcofdk.fwapi.xmt import ITaskProfile
from xcofdk.fwapi.xmt import XTask

from _fw.fwssys.fwmt.xtaskprfext import _XTaskPrfExt


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class XMainTask(XTask):
    """
    This abstract class is inherited from class XTask representing the main
    task of an application.

    Given an application, its main task (if any) is always the singleton of
    this class.

    See:
    -----
        >>> XTask
        >>> XMainTask.__init__()
        >>> XMainTask.CreateSingleton()


    Deprecated API:
    ----------------
    Starting with XCOFDK-py v3.0 formerly used name of this class, i.e.
    MainXTask, is deprecated and not available anymore:
        >>> MainXTask = XMainTask
    """

    __slots__ = []

    # --------------------------------------------------------------------------
    # c-tor / built-in
    # --------------------------------------------------------------------------
    def __init__(self, taskProfile_ : ITaskProfile =None):
        """
        Constructor (or initializer) of the singleton of this class.

        Parameters:
        -------------
            - taskProfile_ :
              task profile to be used to configure this instance.
              If None is passed to, a new instance of class XTaskProfile (with
              default configuration) will be created and considered as passed
              in profile at construction time.

        Note:
        ------
            - The singleton will always be configured as application's main task
              if not done by the profile instance passed to (if any).
            - Also, it will be configured as a non-cyclic, synchronous task if
              no task profile was specified.
            - Attempts to create an additional instances of this class will be
              ignored causing a user error accordingly.

        See:
        -----
            >>> XTask
            >>> XMainTask.CreateSingleton()
            >>> ITask.isAttachedToFW
            >>> ITask.isSyncTask
            >>> IXTask.isMainTask
            >>> IXTask.taskProfile
            >>> ITaskProfile.isFrozen
            >>> ITaskProfile.isSyncTask
            >>> ITaskProfile.isCyclicRunPhase
            >>> ITaskProfile.runPhaseFrequencyMS
        """

        _xtp = taskProfile_
        if isinstance(_xtp, _XTaskPrfExt):
            if _xtp.isValid and not _xtp.isMainTask:
                _xtp._SetMainXTask(True)
        elif (_xtp is None) or (isinstance(_xtp, ITaskProfile) and _xtp.isValid):
            _xtp = _XTaskPrfExt(taskProfile_, True)

        if isinstance(_xtp, ITaskProfile) and _xtp.isValid:
            if taskProfile_ is None:
                _xtp.isSyncTask          = True
                _xtp.runPhaseFrequencyMS = 0
        super().__init__(_xtp)


    @classmethod
    def CreateSingleton(cls, taskProfile_ : Union[ITaskProfile, None], *args_, **kwargs_):
        """
        Class method to create the singleton of this class.

        As a class method, it is always available for classes sub-classing this
        class. Hence, user-defined derived classes must provide a protected,
        static method named '_CreateSingleton()'. Otherwise, calling this method
        will simply cause a compile time error accordingly.

        Parameters:
        -------------
            - taskProfile_ :
              refer to the constructor of this class.
            - args_ :
              optional positional arguments to be passed to the protected
              static method to be called.
            - kwargs_ :
              optional keyword arguments to be passed to the protected
              static method to be called.

        Returns:
        ----------
            Singleton of this class returned by the protected static method
            to be called.

        See:
        -----
            >>> XMainTask.__init__()
        """
        return cls._CreateSingleton(taskProfile_, *args_, **kwargs_)
    # --------------------------------------------------------------------------
    # c-tor / built-in
    # --------------------------------------------------------------------------
#END class XMainTask
