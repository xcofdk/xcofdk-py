# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : userAppRLock.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from threading import RLock as _PyRLock


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class UserAppRLock:

    __slots__ = [ '__pylck' ]

    def __init__(self, bThreadSafe_ =False):
        self.__pylck = _PyRLock() if bThreadSafe_ else None

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.release()

    def acquire(self, blocking =True, timeout =-1) -> bool:
        if self.__pylck is None:
            return True
        else:
            return self.__pylck.acquire(blocking=blocking, timeout=timeout)

    def release(self):
        if self.__pylck is None:
            pass
        else:
            self.__pylck.release()
#END class UserAppRLock
