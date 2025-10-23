# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xmpdefs.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


"""
Module 'xcofdk.fwcom.xmpdefs' is part of framework's multiprocessing subsystem,
i.e. 'xmp'.

It mainly provides commonly used type definitions, e.g.:
    - enum class EXmpPredefinedID
    - enum class EProcessStartMethodID

    See:
    -----
        - class XProcess
"""


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from enum import auto
from enum import unique
from enum import IntEnum


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
@unique
class EProcessStartMethodID(IntEnum):
    """
    Enum class providing symbolic IDs for process start methods recommended to
    use in connection with framework's subsystem of multiprocessing.

    Python's multiprocessing package defines three possible start methods:
        - spawn
        - fork
        - forkserver

    Note:
    ------
        - For details of process start methods refer to the official
          documentation following link below:
              https://docs.python.org/3/library/multiprocessing.html#contexts-and-start-methods

    See:
    -----
        - class XmpUtil
        - XmpUtil.GetDefinedStartMethdsNameList()
        - XmpUtil.MapStartMethodToID()
    """

    SystemDefault = 0
    Spawn         = auto()
    Fork          = auto()
    ForkServer    = auto()
#END class EProcessStartMethodID


@unique
class EXmpPredefinedID(IntEnum):
    """
    Enum class providing pre-defined IDs used in the context of framework's
    multiprocessing interface.

    The IDs currently defined are as follows:
        - MinSuppliedDataSize
          min. size of a byte stream representing the value or object (including
          None), also referred to as supplied data, returned by the target
          callback fucntion of a child process,

        - MaxSuppliedDataSize
          max. size of a byte stream representing the above-mentioned supplied
          data, (= 0x7FF0.0000 or 2146435072 or ca. 2GB)

        - DefaultSuppliedDataMaxSize:
          default value used for a child process as maximum length of a byte
          stream representing the above-mentioned supplied data.

          Current value of 10240 (i.e. 10 KB) is large enough for a byte stream
          occupying a list of up to 1022 integer values each equal to the
          built-in constant 'sys.maxsize'.

    Note:
    ------
        - This enum class and its members must not be changed or extended by
          additional enum members.

    See:
    -----
        - class XProcess


    Deprecated API:
    ----------------
    Starting with XCOFDK-py v3.0 below classes are deprecated and not available
    anymore:
        - class ChildProcessResultData
        >>> # enum class 'EXPMPreDefinedID' (and its members) due to renaming
        >>> EXPMPreDefinedID = EXmpPredefinedID
    """

    MinSuppliedDataSize        = 4
    MaxSuppliedDataSize        = 0x7FF00000
    DefaultSuppliedDataMaxSize = 10240
#END class EXmpPredefinedID
