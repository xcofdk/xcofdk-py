# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : __init__.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


"""
Package 'xcofdk.fwapi.xmt' represents the public interface and classes of
framework's multithreading subsystem 'xmt'.
"""


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from typing import Union

from xcofdk.fwapi.apiif.ifxtask import ITaskProfile
from xcofdk.fwapi.apiif.ifxtask import IXTask

from .xtaskprofile   import XTaskProfile
from .xtask          import XTask
from .xmaintask      import XMainTask
from .xtaskexception import XTaskException

from _fw.fwssys.fwctrl.fwapiconnap import _FwApiConnectorAP


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
def GetCurXTask() -> Union[IXTask, None]:
    """
    This function enables application code to get access to the application
    task currently executed by framework.

     Returns:
     ----------
        - None if:
              - the framework or the currently executed task is affected by
                the limited RTE mode, or
              - not called from within the 3-PhXF of the currently executed
                instance of class XTask,
        - currently executed instance of class XTask otherwise.
          Note that the task state of the returned task is 'running' unless
          the call was made out of the teardown phase.

    See:
    ------
        - XTask.isRunning
    """
    return _FwApiConnectorAP._APGetCurXTask()
