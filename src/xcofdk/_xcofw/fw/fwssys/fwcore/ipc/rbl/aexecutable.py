# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : aexecutable.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes import _FwIntEnum
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes import unique


class _AbstractExecutable:

    @unique
    class _AbstractExecutableTypeID(_FwIntEnum):
        eXt     = 0xEF4
        eMXt    = 0xEF5
        eRbl    = 0xEF6
        eMRbl   = 0xEF7
        eXtRbl  = 0xEF8
        eMXtRbl = 0xEF9

        @property
        def _isXtask(self):
            return self.value <= _AbstractExecutable._AbstractExecutableTypeID.eMXt

        @property
        def _isMainXtask(self):
            return self == _AbstractExecutable._AbstractExecutableTypeID.eMXt

        @property
        def _isRunnable(self):
            return self.value > _AbstractExecutable._AbstractExecutableTypeID.eMXt

        @property
        def _isMainRunnable(self):
            return self == _AbstractExecutable._AbstractExecutableTypeID.eMRbl

        @property
        def _isXTaskRunnable(self):
            return self.value > _AbstractExecutable._AbstractExecutableTypeID.eMRbl

        @property
        def _isMainXTaskRunnable(self):
            return self == _AbstractExecutable._AbstractExecutableTypeID.eMXtRbl

    __slots__ = []

    def __init__(self):
        pass

    def __str__(self):
        return self._ToString()

    @property
    def isXtask(self) -> bool:
        _tt = self.__executableTypeID
        return (_tt is not None) and _tt._isXtask

    @property
    def isMainXtask(self) -> bool:
        _tt = self.__executableTypeID
        return (_tt is not None) and _tt._isMainXtask

    @property
    def isRunnable(self) -> bool:
        _tt = self.__executableTypeID
        return (_tt is not None) and _tt._isRunnable

    @property
    def isMainRunnable(self) -> bool:
        _tt = self.__executableTypeID
        return (_tt is not None) and _tt._isMainRunnable

    @property
    def isXTaskRunnable(self) -> bool:
        _tt = self.__executableTypeID
        return (_tt is not None) and _tt._isXTaskRunnable

    @property
    def isMainXTaskRunnable(self) -> bool:
        _tt = self.__executableTypeID
        return (_tt is not None) and _tt._isMainXTaskRunnable

    @property
    def isAttachedToFW(self) -> bool:
        return self._isAttachedToFW

    @property
    def isDetachedFromFW(self) -> bool:
        return not self._isAttachedToFW

    @property
    def isStarted(self) -> bool:
        return self._isStarted

    @property
    def isRunning(self) -> bool:
        return self._isRunning

    @property
    def isDone(self) -> bool:
        return self._isDone

    @property
    def isFailed(self) -> bool:
        return self._isFailed

    @property
    def isTerminated(self) -> bool:
        return self.isDone or self.isFailed

    @property
    def isTerminating(self) -> bool:
        return self.isStopping or self.isAborting

    @property
    def isStopping(self) -> bool:
        return self._isStopping

    @property
    def isAborting(self) -> bool:
        return self._isAborting

    @property
    def executableName(self) -> str:
        return self._executableName

    @property
    def executableUniqueID(self) -> int:
        return self._executableUniqueID

    def Start(self) -> bool:
        return self._Start()

    def Stop(self) -> bool:
        return self._Stop(cleanupDriver_=True)

    def Join(self, timeout_: [int, float] =None) -> bool:
        return self._Join(timeout_=timeout_)

    def ToString(self, *args_, **kwargs_) -> str:
        return self._ToString(*args_, **kwargs_)

    @staticmethod
    def _CalcExecutableTypeID(bMainXT_ =None, bMainRbl_=None) -> _FwIntEnum:
        res = None

        if bMainRbl_ is not None:
            if bMainRbl_:
                res = _AbstractExecutable._AbstractExecutableTypeID.eMRbl
            elif bMainXT_ is None:
                res = _AbstractExecutable._AbstractExecutableTypeID.eRbl
            elif bMainXT_:
                res = _AbstractExecutable._AbstractExecutableTypeID.eMXtRbl
            else:
                res = _AbstractExecutable._AbstractExecutableTypeID.eXtRbl
        elif bMainXT_ is not None:
            if bMainXT_:
                res = _AbstractExecutable._AbstractExecutableTypeID.eMXt
            else:
                res = _AbstractExecutable._AbstractExecutableTypeID.eXt
        if res is not None:
            res = res.value
        return res

    @property
    def __executableTypeID(self):
        idVal = self._GetMyExecutableTypeID()
        return None if idVal is None else _AbstractExecutable._AbstractExecutableTypeID(idVal)
