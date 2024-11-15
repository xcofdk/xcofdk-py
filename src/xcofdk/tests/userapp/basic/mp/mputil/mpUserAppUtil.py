# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : mpUserAppUtil.py
#
# Copyright(c) 2024 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from os import getpid as _PyGetPID

from xcofdk.fwcom.xmpdefs import ChildProcessResultData

from xcofdk.tests.userapp.util.userAppUtil import UserAppUtil


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class MPUserAppUtil:

    __slots__ = []

    def __init__(self):
        pass

    @staticmethod
    def Fibonacci(procResData_ : ChildProcessResultData, fiboInput_ : int):
        if not isinstance(procResData_, ChildProcessResultData):
            print(f'[{_PyGetPID()}:Fibonacci] Got bad process result object passed in: {type(procResData_).__name__}')
            return

        _fiboRes   = UserAppUtil.Fibonacci(fiboInput_)
        procResData_.exitCode   = 0
        procResData_.resultData = _fiboRes
        #print(f'[{_PyGetPID()}:FibonacciCB] Finished execution, Fibonacci({fiboInput_}): {_fiboRes}')
#END class MPUserAppUtil
