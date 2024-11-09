# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : ataskop.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


import threading
from enum import unique

from xcofdk._xcofw.fw.fwssys.fwcore.logging           import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.base.util         import _Util
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskstate import _TaskState
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil  import _TaskUtil
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil  import _PyThread
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject     import _AbstractSlotsObject
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes import _FwIntEnum


@unique
class _EATaskOperationID(_FwIntEnum):
    eStart   =0
    eRestart =1
    eStop    =2
    eJoin    =3

    @property
    def isStart(self):
        return self==_EATaskOperationID.eStart

    @property
    def isRestart(self):
        return self==_EATaskOperationID.eRestart

    @property
    def isStop(self):
        return self==_EATaskOperationID.eStop

    @property
    def isJoin(self):
        return self==_EATaskOperationID.eJoin


@unique
class _EATaskOperationCallTypeID(_FwIntEnum):
    eNA      =-1  
    eIgnore  =0   
    eSyncOP  =1
    eASyncOP =2

    @property
    def isNotApplicable(self):
        return self ==  _EATaskOperationCallTypeID.eNA

    @property
    def isIgnorable(self):
        return self ==  _EATaskOperationCallTypeID.eIgnore

    @property
    def isSynchronous(self):
        return self ==  _EATaskOperationCallTypeID.eSyncOP

    @property
    def isASynchronous(self):
        return self ==  _EATaskOperationCallTypeID.eASyncOP


class _ATaskOperationPreCheck(_AbstractSlotsObject):

    __slots__ = [ '__eOpID' , '__eOpCallTypeID' , '__tskState' , '__linkeyPyThrd' , '__isEncloPyThrd' ]

    def __init__(self, eTaskOpID_ : _EATaskOperationID, tskState_ : _TaskState, linkedPyThrd_ : _PyThread, isEncloPyThrd_ : bool, reportErr_ =True):
        super().__init__()
        self.__eOpID         = None
        self.__tskState      = None
        self.__linkeyPyThrd  = None
        self.__isEncloPyThrd = None
        self.__eOpCallTypeID = None

        if not _Util.IsInstance(eTaskOpID_, _EATaskOperationID, bThrowx_=True):
            self.CleanUp()
        elif not _Util.IsInstance(tskState_, _TaskState, bThrowx_=True):
            self.CleanUp()
        elif not _Util.IsInstance(linkedPyThrd_, _PyThread, bThrowx_=True):
            self.CleanUp()
        else:
            self.__eOpID         = eTaskOpID_
            self.__tskState      = tskState_
            self.__linkeyPyThrd  = linkedPyThrd_
            self.__isEncloPyThrd = isEncloPyThrd_
            self.__eOpCallTypeID = _EATaskOperationCallTypeID.eNA

            self.Update(reportErr_=reportErr_)

    @property
    def isNotApplicable(self):
        return False if self.__eOpCallTypeID is None else self.__eOpCallTypeID.isNotApplicable

    @property
    def isIgnorable(self):
        return False if self.__eOpCallTypeID is None else self.__eOpCallTypeID.isIgnorable

    @property
    def isSynchronous(self):
        return False if self.__eOpCallTypeID is None else self.__eOpCallTypeID.isSynchronous

    @property
    def isASynchronous(self):
        return False if self.__eOpCallTypeID is None else self.__eOpCallTypeID.isASynchronous

    @property
    def eTaskOperationID(self) -> _EATaskOperationID:
        return self.__eOpID

    @property
    def eTaskOperationCallTypeID(self) -> _EATaskOperationCallTypeID:
        return self.__eOpCallTypeID

    def Update(self, eTaskOpID_ : _EATaskOperationID =None, reportErr_ =True) -> _EATaskOperationCallTypeID:
        res = _EATaskOperationCallTypeID.eNA

        if self.__tskState is None:
            return res

        if eTaskOpID_ is not None:
            if not _Util.IsInstance(eTaskOpID_, _EATaskOperationID, bThrowx_=True):
                return res
            self.__eOpID = eTaskOpID_
        if self.__eOpID is None:
            self.__eOpCallTypeID = res
            return res

        _eCurStateID = self.__tskState.GetStateID()

        if _eCurStateID is None:
            self.__eOpCallTypeID = res
            return res

        _prvOpCallTypeID = None if ((self.__eOpCallTypeID is None) or self.__eOpCallTypeID.isNotApplicable) else self.__eOpCallTypeID
        _bLinkedPyThrdCurThrd     = _TaskUtil.IsCurPyThread(self.__linkeyPyThrd)
        _bLinkedPyThrdMainPyThrd  = _TaskUtil.IsMainPyThread(self.__linkeyPyThrd)
        bLinkedPyThrdStartupThrd = _TaskUtil.IsStartupThread(self.__linkeyPyThrd)
        _bJoinable = _bLinkedPyThrdCurThrd or not bLinkedPyThrdStartupThrd

        if not _eCurStateID.isStarted:
            res = self.__UpdateNotStarted(_eCurStateID, _bLinkedPyThrdCurThrd)

        elif _eCurStateID.isTransitional:
            res = self.__UpdateTransitional(_eCurStateID, _bLinkedPyThrdCurThrd, _bJoinable)

        else:
            res = self.__UpdateStarted(_eCurStateID, _bLinkedPyThrdCurThrd, _bJoinable)

        doLog = False or (_prvOpCallTypeID is None)
        doLog = doLog or (res != _prvOpCallTypeID)
        if not doLog:
            pass
        else:
            doLogErr = reportErr_ if res.isNotApplicable else False


            if doLogErr:
                vlogif._LogOEC(False, -3021)

        self.__eOpCallTypeID = res
        return res

    def _ToString(self, *args_, **kwargs_):
        pass

    def _CleanUp(self):
        self.__eOpID         = None
        self.__tskState      = None
        self.__linkeyPyThrd  = None
        self.__isEncloPyThrd = None
        self.__eOpCallTypeID = None

    def __UpdateNotStarted(self, eCurStateID_ : _TaskState._EState, bLinkedPyThrdCurThrd_ : bool) -> _EATaskOperationCallTypeID:
        reqOP = self.__eOpID.compactName
        if eCurStateID_.isStarted:
            vlogif._LogOEC(True, -1410)
            return _EATaskOperationCallTypeID.eNA

        if not eCurStateID_.isInitialized:
            res = _EATaskOperationCallTypeID.eNA

        elif self.__eOpID.isStart or self.__eOpID.isRestart:
            res = _EATaskOperationCallTypeID.eSyncOP if bLinkedPyThrdCurThrd_ else _EATaskOperationCallTypeID.eASyncOP

        else:
            res = _EATaskOperationCallTypeID.eIgnore
        return res

    def __UpdateTransitional(self, eCurStateID_ : _TaskState._EState, bLinkedPyThrdCurThrd_ : bool, bLinkedPyThrdJoinable_ : bool) -> _EATaskOperationCallTypeID:
        reqOP = self.__eOpID.compactName
        if not eCurStateID_.isTransitional:
            vlogif._LogOEC(True, -1411)
            return _EATaskOperationCallTypeID.eNA

        if self.__eOpID.isStart or self.__eOpID.isRestart:

            if eCurStateID_.isPendingRun:
                res = _EATaskOperationCallTypeID.eIgnore

            else:
                res = _EATaskOperationCallTypeID.eNA

        elif self.__eOpID.isJoin:

            if not bLinkedPyThrdJoinable_:
                res = _EATaskOperationCallTypeID.eNA

            elif bLinkedPyThrdCurThrd_:
                res = _EATaskOperationCallTypeID.eIgnore

            else:
                res = _EATaskOperationCallTypeID.eSyncOP

        else:

            if eCurStateID_.isPendingRun:
                res = _EATaskOperationCallTypeID.eSyncOP if bLinkedPyThrdCurThrd_ else _EATaskOperationCallTypeID.eASyncOP

            else:
                res = _EATaskOperationCallTypeID.eIgnore
        return res

    def __UpdateStarted(self, eCurStateID_ : _TaskState._EState, bLinkedPyThrdCurThrd_ : bool, bLinkedPyThrdJoinable_ : bool) -> _EATaskOperationCallTypeID:
        reqOP = self.__eOpID.compactName
        if not (eCurStateID_.isStarted and not eCurStateID_.isTransitional):
            vlogif._LogOEC(True, -1412)
            return _EATaskOperationCallTypeID.eNA

        if self.__eOpID.isStart or self.__eOpID.isRestart:

            if eCurStateID_.isRunning:
                res = _EATaskOperationCallTypeID.eNA

            elif eCurStateID_.isFailed:

                if self.__eOpID.isStart:
                    res = _EATaskOperationCallTypeID.eNA

                else:
                    res = _EATaskOperationCallTypeID.eSyncOP if bLinkedPyThrdCurThrd_ else _EATaskOperationCallTypeID.eASyncOP

            else:

                if self.__eOpID.isStart:
                    res = _EATaskOperationCallTypeID.eNA

                else:
                    res = _EATaskOperationCallTypeID.eSyncOP if bLinkedPyThrdCurThrd_ else _EATaskOperationCallTypeID.eASyncOP

        elif self.__eOpID.isJoin:

            if eCurStateID_.isRunning:

                if not bLinkedPyThrdJoinable_:
                    res = _EATaskOperationCallTypeID.eNA

                elif bLinkedPyThrdCurThrd_:
                    res = _EATaskOperationCallTypeID.eIgnore

                else:
                    res = _EATaskOperationCallTypeID.eSyncOP

            else:
                res = _EATaskOperationCallTypeID.eIgnore

        else:

            if eCurStateID_.isRunning:
                res = _EATaskOperationCallTypeID.eSyncOP if bLinkedPyThrdCurThrd_ else _EATaskOperationCallTypeID.eASyncOP

            else:
                res = _EATaskOperationCallTypeID.eIgnore
        return res
