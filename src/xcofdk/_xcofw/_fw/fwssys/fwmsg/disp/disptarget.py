# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : disptarget.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from _fw.fwssys.assys.ifs.ifdispagent  import _IDispAgent
from _fw.fwssys.fwcore.logging         import vlogif
from _fw.fwssys.fwcore.base.fwcallable import _FwCallable
from _fw.fwssys.fwcore.types.aobject   import _AbsSlotsObject
from _fw.fwssys.fwerrh.fwerrorcodes    import _EFwErrorCode

class _DispatchTarget(_AbsSlotsObject):
    __slots__ = [ '__a' , '__c' , '__bA' ]

    def __init__(self, agent_ : _IDispAgent, callback_ : _FwCallable =None, bAutoDestroy_ =False):
        self.__a  = None
        self.__c  = None
        self.__bA = None
        super().__init__()

        if not self.__IsValid(agent_=agent_, callback_=callback_):
            self.CleanUp()
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00528)
            return

        self.__a  = agent_
        self.__c  = callback_
        self.__bA = bAutoDestroy_

    def __eq__(self, other_):
        if not isinstance(other_, _DispatchTarget):
            return False
        if not (self.isValid and other_.isValid):
            return False
        if id(self.__a) != id(other_.__a):
            return False
        if self.__c is None:
            if other_.__c is not None:
                return False
        elif other_.__c is None:
                return False
        elif id(self.__c) != id(other_.__c):
                return False
        return True

    def __ne__(self, other_):
        if not isinstance(other_, _DispatchTarget):
            return True
        if not (self.isValid and other_.isValid):
            return True
        if id(self.__a) == id(other_.__a):
            return False
        if self.__c is None:
            if other_.__c is None:
                return False
        elif other_.__c is not None:
            return False
        elif id(self.__c) == id(other_.__c):
            return False
        return True

    def __hash__(self):
        if not self.isValid:
            return None
        return hash(id(self.__a) + 0 if self.__c is None else hash(id(self.__c)))

    @property
    def isValid(self) -> bool:
        return self.__IsValid()

    @property
    def _isCallbackDispatch(self) -> bool:
        return self.__IsValid() and self.__c is not None

    @property
    def _dispatchAgent(self):
        return self.__a

    @property
    def _dispatchCallback(self):
        return self.__c

    def _IsSameAgent(self, other_, bSkipPreCheck_ =False):
        if not bSkipPreCheck_:
            if not isinstance(other_, _DispatchTarget):
                return False
            if not (self.isValid and other_.isValid):
                return False
        return id(self.__a) == id(other_.__a)

    def _ToString(self) -> str:
        return None if self.__IsValid() else self.__a._agentName

    def _CleanUp(self):
        if self.__a is None:
            return

        if self.__bA and (self.__c is not None):
            self.__c.CleanUp()
        self.__a  = None
        self.__c  = None
        self.__bA = None

    def __IsValid(self, agent_ : _IDispAgent =None, callback_ : _FwCallable =None):
        if agent_ is not None:
            res = isinstance(agent_, _IDispAgent)
            if res and (callback_ is not None):
                res = isinstance(callback_, _FwCallable)
        else:
            agent_    = self.__a
            callback_ = self.__c
            res       = self.__a is not None

        if not res:
            pass
        elif not agent_._isOperating:
            res = False
        elif callback_ is not None:
            res = callback_.isValid
        return res
