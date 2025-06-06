# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : dieexception.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from _fw.fwssys.fwerrh.logs.xcoexception import _EXcoXcpType
from _fw.fwssys.fwerrh.logs.xcoexception import _XcoException

class _DieException(_XcoException):
    def __init__(self, enclLogXcp_ =None):
        if not (isinstance(enclLogXcp_, _XcoException) and enclLogXcp_.isLogException):
            _XcoException._RaiseSystemExit('Bad enclosed exception objetc {}.'.format(type(enclLogXcp_).__name__))
        else:
            super().__init__(_EXcoXcpType.eDieException, enclXcp_=enclLogXcp_)

    @property
    def shortMessage(self):
        return None if self.__isInvalid else self._enclosedLogException.shortMessage

    @property
    def _uniqueID(self):
        return None if self.__isInvalid else self._enclosedLogException.uniqueID

    @property
    def _taskID(self):
        return None if self.__isInvalid else self._enclosedLogException.dtaskUID

    def _ToString(self):
        if self.__isInvalid is None:
            res = None
        else:
            res  = '{}[{}]'.format(type(self).__name__, self.uniqueID)
            res += '\n\n{}'.format(self._enclosedLogException.ToString())
        return res

    def _CleanUp(self):
        super()._CleanUp()

    @property
    def __isInvalid(self):
        return self._enclosedLogException is None
