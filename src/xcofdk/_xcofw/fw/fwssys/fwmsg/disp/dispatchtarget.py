# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : dispatchtarget.py
#
# Copyright(c) 2024 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from xcofdk._xcofw.fw.fwssys.fwcore.logging           import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.base.callableif   import _CallableIF
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject     import _AbstractSlotsObject

from xcofdk._xcofw.fw.fwssys.fwmsg.disp.dispatchagentif import _DispatchAgentIF


class _DispatchTarget(_AbstractSlotsObject):

    __slots__ = [ '__dispAgent' , '__dispCallback' , '__bAutoDestroy' ]

    def __init__(self, agent_ : _DispatchAgentIF, callback_ : _CallableIF =None, bAutoDestroy_ =False):
        self.__dispAgent    = None
        self.__dispCallback = None
        self.__bAutoDestroy = None
        super().__init__()

        if not self.__IsValid(agent_=agent_, callback_=callback_):
            self.CleanUp()
            vlogif._LogOEC(True, -1669)
            return

        self.__dispAgent    = agent_
        self.__dispCallback = callback_
        self.__bAutoDestroy = bAutoDestroy_

    def __eq__(self, other_):
        if not isinstance(other_, _DispatchTarget):
            return False
        if not (self.isValid and other_.isValid):
            return False
        if id(self.__dispAgent) != id(other_.__dispAgent):
            return False
        if self.__dispCallback is None:
            if other_.__dispCallback is not None:
                return False
        elif other_.__dispCallback is None:
                return False
        elif id(self.__dispCallback) != id(other_.__dispCallback):
                return False
        return True

    def __ne__(self, other_):
        if not isinstance(other_, _DispatchTarget):
            return True
        if not (self.isValid and other_.isValid):
            return True
        if id(self.__dispAgent) == id(other_.__dispAgent):
            return False
        if self.__dispCallback is None:
            if other_.__dispCallback is None:
                return False
        elif other_.__dispCallback is not None:
            return False
        elif id(self.__dispCallback) == id(other_.__dispCallback):
            return False
        return True

    def __hash__(self):
        if not self.isValid:
            return None
        return hash(id(self.__dispAgent) + 0 if self.__dispCallback is None else hash(id(self.__dispCallback)))

    @property
    def isValid(self) -> bool:
        return self.__IsValid()

    @property
    def _isAgentDispatch(self) -> bool:
        return self.__IsValid() and self.__dispCallback is None

    @property
    def _isCallbackDispatch(self) -> bool:
        return self.__IsValid() and self.__dispCallback is not None

    @property
    def _dispatchAgent(self):
        return self.__dispAgent

    @property
    def _dispatchCallback(self):
        return self.__dispCallback

    def _IsSameAgent(self, other_, bSkipPreCheck_ =False):
        if not bSkipPreCheck_:
            if not isinstance(other_, _DispatchTarget):
                return False
            if not (self.isValid and other_.isValid):
                return False
        return id(self.__dispAgent) == id(other_.__dispAgent)

    def _ToString(self, *args_, **kwargs_) -> str:
        return None if self.__IsValid() else self.__dispAgent._agentName

    def _CleanUp(self):
        if self.__dispAgent is None:
            return

        if self.__bAutoDestroy and (self.__dispCallback is not None):
            self.__dispCallback.CleanUp()
            self.__dispCallback = None

        self.__dispAgent    = None
        self.__bAutoDestroy = None

    def __IsValid(self, agent_ : _DispatchAgentIF =None, callback_ : _CallableIF =None):
        if agent_ is not None:
            res = isinstance(agent_, _DispatchAgentIF)
            if res and (callback_ is not None):
                res = isinstance(callback_, _CallableIF)
        else:
            agent_    = self.__dispAgent
            callback_ = self.__dispCallback
            res       = self.__dispAgent is not None

        if not res:
            pass
        elif not agent_._isOperating:
            res = False
        elif callback_ is not None:
            res = callback_.isValid
        return res
