# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xmpdefs.py
#
# Copyright(c) 2024 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


"""
Module 'xcofdk.fwcom.xmpdefs' is part of framework's multiprocessing subsstem.

It mainly provides commonly used type definitions, e.g.:
    - enum class EXPMPreDefinedID
    - enum class EProcessStartMethodID
    - class ChildProcessResultData

    Note:
    ------
        - Framework's subsystem of multiprocessing is explained in class
          description of XProcess.

    See:
    -----
        - XProcess
"""


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
import pickle as _PyPickle
from   enum import auto
from   enum import unique
from   enum import IntEnum


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

    Even though child processes, i.e. instances of class XProcess, will work
    regardless of which of the above start methods is chosen by an application,
    'forkserver' is considered by the framework as:
        - not general-purpose,
        - adding even more dependency to an auto-started server process, which
          is basically invisible to the framework, especially whenever
          termination is of concern. It simply lacks usual interface for a
          managed control,
        - not well-documented.

    To point out the abovementioned concerns, no ID corresponding to
    'forkserver' has been defined by intention.

    Note:
    ------
        - Framework's subsystem of multiprocessing is explained in class
          description of XProcess.
        - For details of process start methods refer to the official
          documentation following link below:
              https://docs.python.org/3/library/multiprocessing.html#contexts-and-start-methods
    """

    SystemDefault = 0
    Spawn         = auto()
    Fork          = auto()
#END class EProcessStartMethodID


class EXPMPreDefinedID(IntEnum):
    """
    Enum class providing pre-defined IDs used in the context of framework's
    multiprocessing interface.

    The IDs currently defined are as follows:
        - ProcessExitCodeSuccess:
          usual exit code of 0 indicating successful termination of process.

        - MaxUserDefinedProcessExitCode:
          represents maximum integer value applications can use as exit code
          of thier child processes, i.e. instances of class XProcess.

        - UnexpectedUserDefinedProcessExitCode:
          represents any integer value violating its expected range of [0..80]
          supplied by an application as exit code of thier child processes,
          i.e. instances of class XProcess.

        - DefaultUserDefinedResultDataMaxSize:
          default value used as maximum length of a byte stream representing
          the serialization of a data object (if any) assigned to instances of
          'ChildProcessResultData' as user-defined result data.

          Current value of 1024 is large enough for a byte stream occupying a
          list of up to 100 integer values equal to the built-in constant
          'sys.maxsize' (i.e. 9223372036854775807).

    Note:
    ------
        - Applications should always introduce their own enum classes (if any)
          as this enum class is not designed to be changed or extended by
          additional enum members.
        - Task/process communication is described in class description of
          XMessageManager.

    See:
    -----
        - XProcess
        - ChildProcessResultData
    """

    ProcessExitCodeSuccess               = 0
    MaxUserDefinedProcessExitCode        = 80
    UnexpectedUserDefinedProcessExitCode = 81
    DefaultUserDefinedResultDataMaxSize  = 1024
#END class EXPMPreDefinedID


class ChildProcessResultData:
    """
    This class respresnts specific execution result, i.e. exit code and data,
    supplied by child process.

    When a child process, i.e. an instance of class XProcess, is started, an
    instance of this class is passed to its callable target as argument enabling
    its execution result can be delivered to the parent process.

    The interface of this class is composed of getter and setter properties
    related to the exit code of the execution and user-defined data (if any)
    as result.

    Note:
    ------
        - Framework's subsystem of multiprocessing is explained in class
          description of XProcess.

    See:
    -----
        - XProcess
    """


    __slots__ = [ '__ec' , '__resData' , '__maxSize' ]


    def __init__(self, resultDataMaxSize_ : int =EXPMPreDefinedID.DefaultUserDefinedResultDataMaxSize):
        """
        Constructor (initializer) of instances of this class.

        Exit code and user-defined data of this instance will be set to their
        default values:
            - 0, meaning successful execution,
            - None, meaning no user-defined data supplied.

        Parameters:
        -------------
            - resultDataMaxSize_ :
              maximum length of a byte stream representing the serialization
              of the user-defined result data (if any) of this instance.

        See:
        -----
            - XProcess.__init__()
            - ChildProcessResultData.resultData
            - EXPMPreDefinedID.DefaultUserDefinedResultDataMaxSize
        """
        self.__ec      = 0
        self.__maxSize = resultDataMaxSize_
        self.__resData = None


    def __str__(self):
        """
        String representation of this instance.

        Returns:
        ----------
            A string object as representation of this instance.
        """
        _id = None if self.__resData is None else id(self.__resData)
        return 'ChildProcessResultData: exitCode={} , resultDataMaxSize={}, id(resultData)={}'.format(self.__ec, self.__maxSize, _id)


    # --------------------------------------------------------------------------
    # API
    # --------------------------------------------------------------------------
    @property
    def isProcessSucceeded(self):
        """
        Returns:
        ----------
            True if the execution of the child process has finished successfully
            indicated by an exit code of 0, False otherwise.

        See:
        -----
            - ChildProcessResultData.isProcessFailed
            - ChildProcessResultData.exitCode
        """
        return self.__ec == 0


    @property
    def isProcessFailed(self):
        """
        Returns:
        ----------
            True if the execution of the child process is failed indicated by an
            exit code other than 0, False otherwise.

        See:
        -----
            - ChildProcessResultData.isProcessSucceeded
            - ChildProcessResultData.exitCode
        """
        return not self.isProcessSucceeded


    @property
    def exitCode(self) -> int:
        """
        Getter propertry for the exit code.

        Returns:
        ----------
            0 indicating successful execution, a positive integer value
            otherwise.

        See:
        -----
            - ChildProcessResultData.isProcessSucceeded
            - ChildProcessResultData.isProcessFailed
        """
        return self.__ec


    @exitCode.setter
    def exitCode(self, exitCode_ : int):
        """
        Setter propertry for the exit code.

        Parameters:
        -------------
            - exitCode_ :
              0 to indicate successful execution, a positive integer value
              otherwise. In the latter case the value is expected to be of the
              range [0..80]

        See:
        -----
            - ChildProcessResultData.isProcessSucceeded
            - ChildProcessResultData.isProcessFailed
        """
        if not (isinstance(exitCode_, int) and (0 <= exitCode_ <= EXPMPreDefinedID.MaxUserDefinedProcessExitCode.value)):
            exitCode_ = EXPMPreDefinedID.UnexpectedUserDefinedProcessExitCode.value
        self.__ec = exitCode_


    @property
    def resultData(self) -> object:
        """
        Getter propertry for application specific, i.e. user-defined, data.

        Returns:
        ----------
            0 indicating successful execution, a positive integer value
            otherwise.
        """
        return self.__resData


    @resultData.setter
    def resultData(self, resData_ : object):
        """
        Setter propertry for application specific, i.e. user-defined, data.

        Note that the length of the byte stream of the passed in object must
        not larger than the parameter 'maxResultByteSize_' passed to the
        constructor of the associated child process, that is the instance of
        class XProcess whose execution result is going to be represented by
        this instance.

        Otherwise, the termination of the child process will result in an
        internal, reserved exit code beyond the range of [0..80].

        Parameters:
        -------------
            - resData_ :
              an arbitrary object (including None) supplied as user-defined
              result of the execution.

        See:
        -----
            - XProcess.__init__()
            - ChildProcessResultData.__init__()
            - EXPMPreDefinedID.DefaultUserDefinedResultDataMaxSize
        """
        try:
            _tmp = _PyPickle.dumps(resData_)
            if (_tmp is not None) and len(_tmp) > self.__maxSize:
                print(f'Warning, size of the byte stream of the passed in result data exceeds max. size of {self.__maxSize}.')
            del _tmp
        except (_PyPickle.PickleError, Exception, BaseException) as _xcp:
            pass
        self.__resData = resData_
    # --------------------------------------------------------------------------
    #END API
    # --------------------------------------------------------------------------
#END class ChildProcessResultData
