# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwapiconn.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from threading import RLock as _PyRLock

from xcofdk.fwapi.xtask import XTask

from xcofdk._xcofw.fw.fwssys.fwcore.logging             import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil    import _TaskUtil
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcexecstate      import _LcFailure
from xcofdk._xcofw.fw.fwssys.fwcore.types.apobject      import _ProtectedAbstractSlotsObject
from xcofdk._xcofw.fw.fwssys.fwcore.apiimpl.fwapiconnap import _FwApiConnectorAP


class _FwApiConnector(_ProtectedAbstractSlotsObject):

    __slots__ = [ '__fwApiLck' , '__bAvailable' ]

    def __init__(self, ppass_ : int):
        self.__fwApiLck   = None
        self.__bAvailable = False
        super().__init__(ppass_)

    def FwCNGetXTask(self, xuUniqueID_ : int =0) -> XTask:
        if not self._FwCNIsFwApiAvailable():
            return None
        return self._GetCurXTask() if xuUniqueID_==0 else self._GetXTask(xuUniqueID_)

    def FwCNGetCurXTask(self) -> XTask:
        if not self._FwCNIsFwApiAvailable():
            return None
        return self._GetCurXTask()

    def FwCNStopXcoFW(self) -> bool:
        if not self._FwCNIsFwApiAvailable():
            return False
        return self._StopFW()

    def FwCNJoinXcoFW(self) -> bool:
        if not self._FwCNIsFwApiAvailable():
            return False
        return self._JoinFW()

    def _FwCNIsFwApiAvailable(self):
        if self.__fwApiLck is None:
            return False
        with self.__fwApiLck:
            return self.__bAvailable

    def _FwCNIsLcErrorFree(self) -> bool:
        if not self._FwCNIsFwApiAvailable():
            return _LcFailure.IsLcErrorFree()
        return self._IsLcErrorFree()

    def _FwCNPublishFwApiConnector(self, bDisconnect_ =False, disconnectSleepTimespanMS_ =None):
        if self.__fwApiLck is None:
            return

        with self.__fwApiLck:
            if (not bDisconnect_) and self.__bAvailable:
                pass
            elif bDisconnect_ and not self.__bAvailable:
                pass
            else:
                self.__bAvailable = not bDisconnect_

                _fwConn = None if bDisconnect_ else self
                _FwApiConnectorAP._APSetFwApiConnector(_fwConn, self.__fwApiLck)
                if bDisconnect_:
                    if disconnectSleepTimespanMS_ is not None:
                        _TaskUtil.SleepMS(disconnectSleepTimespanMS_)

    def _FwCNSetFwApiLock(self, fwApiLck_ : _PyRLock):
        self.__fwApiLck = fwApiLck_

    def _CleanUpByOwnerRequest(self):
        if self.__fwApiLck is None:
            pass
        else:
            self._FwCNPublishFwApiConnector(bDisconnect_=True)
            self.__fwApiLck   = None
            self.__bAvailable = None
