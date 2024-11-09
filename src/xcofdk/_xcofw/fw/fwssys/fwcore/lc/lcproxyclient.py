# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : lcproxyclient.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from xcofdk._xcofw.fw.fwssys.fwcore.logging           import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject     import _AbstractSlotsObject
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes import _ETernaryOpResult
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcdefines      import _ELcOperationModeID
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcproxy        import _LcProxy


class _LcProxyClient(_AbstractSlotsObject):

    __slots__  = [ '__lcPxy' , '__eLcOpModeID' ]

    def __init__(self):
        super().__init__()
        self.__lcPxy       = None
        self.__eLcOpModeID = None

    def _OnLcCeaseModeDetected(self) -> _ETernaryOpResult:
        return _ETernaryOpResult.Stop()

    def _OnLcFailureDetected(self) -> _ETernaryOpResult:
        return _ETernaryOpResult.Stop()

    def _OnLcPreShutdownDetected(self) -> _ETernaryOpResult:
        return _ETernaryOpResult.Stop()

    def _OnLcShutdownDetected(self) -> _ETernaryOpResult:
        return _ETernaryOpResult.Stop()

    @property
    def _isLcProxyAvailable(self):
        return (self.__lcPxy is not None) and self.__lcPxy.isLcProxyAvailable

    @property
    def _isLcProxyOperable(self):
        return (self.__lcPxy is not None) and self.__lcPxy.isLcModeNormal

    @property
    def _isLcShutdownEnabled(self) -> bool:
        return (self.__lcPxy is not None) and self.__lcPxy.isLcShutdownEnabled

    @property
    def _isLcProxyClientMonitoringLcModeChange(self) -> bool:
        return False

    @property
    def _lcProxy(self) -> _LcProxy:
        return self.__lcPxy

    @property
    def _lcProxyClientName(self) -> str:
        res = self.taskUniqueName
        if res is None:
            res = type(self).__name__
        return res

    def _CheckLcOperationModeChange(self) -> _ELcOperationModeID:
        if self.__lcPxy is None:
            res = None
        elif not self._isLcProxyClientMonitoringLcModeChange:
            res = None
            vlogif._LogOEC(True, -1566)
        else:
            if not self.__lcPxy.isLcProxyAvailable:
                eNewID = _ELcOperationModeID.eLcShutdown
            else:
                eNewID = self.__lcPxy.eLcOperationModeID

            if eNewID != self.__eLcOpModeID:
                res = eNewID
                self.__eLcOpModeID = eNewID
            else:
                res = None
        return res

    def _SetLcProxy(self, lcPxy_ : _LcProxy):
        if lcPxy_ is None:
            return
        if self.__lcPxy is not None:
            return

        if not isinstance(lcPxy_, _LcProxy):
            vlogif._LogOEC(True, -1567)
        elif not lcPxy_.isLcProxyAvailable:
            vlogif._LogOEC(True, -1568)
        else:
            self.__lcPxy       = lcPxy_
            self.__eLcOpModeID = lcPxy_.eLcOperationModeID

    def _CleanUp(self):
        self.__lcPxy       = None
        self.__eLcOpModeID = None
