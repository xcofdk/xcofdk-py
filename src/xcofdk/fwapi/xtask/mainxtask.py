# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : mainxtask.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from typing import Union

from xcofdk.fwapi.xtask import XTaskProfile
from xcofdk.fwapi.xtask import XTask

from xcofdk._xcofw.fw.fwssys.fwcore.apiimpl.xtask.xtaskprfext  import _XTaskProfileExt
from xcofdk._xcofw.fw.fwssys.fwcore.apiimpl.xtask.xtaskprfbase import _XTaskProfileBase


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class MainXTask(XTask):
    """
    This class is inherited from class XTask representing the main task of an
    application.

    Given an application, its main task is always the singleton of this class.

    See:
    -----
        - XTask
        - MainXTask.CreateSingleton()
    """

    __slots__ = []

    def __init__(self, taskProfile_ : XTaskProfile =None):
        """
        Constructor (initializer) of instances of this class.

        Parameters:
        -------------
            - taskProfile_ :
              task profile to be associated with this instance.
              If None is passed to, a new task profile (with default values)
              will be created and used instead. Otherwise, passed in profile
              will be cloned and used as a read-only copy.

        Note:
        ------
            - For the task profile instance effectively associated with this
              instance below property will always resolve to True:
                  >>> self.xtaskProfile.isMainTask == True
            - If None was passed in as task profile, task type of this instance
              will be asynchronous by default, that is below property will
              resolve to False:
                  >>> self.xtaskProfile.isSynchronousTask == False

        See:
        -----
            - XTask
            - MainXTask
            - MainXTask.CreateSingleton()
            - XTask.isAttachedToFW
            - XTask.xtaskProfile
        """
        _xtp = taskProfile_
        if isinstance(_xtp, _XTaskProfileExt):
            if _xtp.isValid and not _xtp.isMainTask:
                _XTaskProfileBase._SetMainXTask(_xtp, True)
        else:
            _xtp = _XTaskProfileExt(taskProfile_, True)

        if _xtp.isValid:
            if taskProfile_ is None:
                _xtp.isSynchronousTask = False
        super().__init__(_xtp)


    @classmethod
    def CreateSingleton(cls, taskProfile_ : Union[XTaskProfile, None], *args_, **kwargs_):
        """
        Class method to create the singleton of this class.

        As a class method, it is always available for classes sub-classing this class.

        Derived classes must provide the implementation of the protected, static
        method '_CreateSingleton()', otherwise a call to this method will simply
        cause a compile error accordingly.

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
            to be called

        See:
        -----
            - MainXTask.__init__()
        """
        return cls._CreateSingleton(taskProfile_, *args_, **kwargs_)
#END class MainXTask
