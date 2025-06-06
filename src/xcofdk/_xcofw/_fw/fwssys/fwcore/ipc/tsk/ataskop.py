# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : ataskop.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

import threading
from enum import auto
from enum import unique

from _fw.fwssys.fwcore.logging           import vlogif
from _fw.fwssys.fwcore.base.util         import _Util
from _fw.fwssys.fwcore.ipc.tsk.taskstate import _TaskState
from _fw.fwssys.fwcore.ipc.tsk.taskutil  import _TaskUtil
from _fw.fwssys.fwcore.ipc.tsk.taskutil  import _PyThread
from _fw.fwssys.fwcore.types.aobject     import _AbsSlotsObject
from _fw.fwssys.fwcore.types.commontypes import _FwIntEnum
from _fw.fwssys.fwerrh.fwerrorcodes      import _EFwErrorCode

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

@unique
class _EATaskOpID(_FwIntEnum):
    eStart   = 0
    eRestart = auto()
    eStop    = auto()
    eCancel  = auto()
    eJoin    = auto()

    @property
    def isStart(self):
        return self==_EATaskOpID.eStart

    @property
    def isRestart(self):
        return self==_EATaskOpID.eRestart

    @property
    def isStop(self):
        return self==_EATaskOpID.eStop

    @property
    def isCancel(self):
        return self==_EATaskOpID.eCancel

    @property
    def isJoin(self):
        return self==_EATaskOpID.eJoin

@unique
class _EATaskOpCTID(_FwIntEnum):
    eNA      = -1      
    eIgnore  = auto()  
    eSyncOP  = auto()
    eASyncOP = auto()

    @property
    def isNotApplicable(self):
        return self ==  _EATaskOpCTID.eNA

    @property
    def isIgnorable(self):
        return self ==  _EATaskOpCTID.eIgnore

    @property
    def isSynchronous(self):
        return self ==  _EATaskOpCTID.eSyncOP

    @property
    def isASynchronous(self):
        return self ==  _EATaskOpCTID.eASyncOP

class _ATaskOpPreCheck(_AbsSlotsObject):
    __slots__ = [ '__id' , '__idct' , '__tst' , '__dht' , '__bE' ]

    def __init__(self, taskOpID_ : _EATaskOpID, tskState_ : _TaskState, dhThrd_ : _PyThread, bEnclHThrd_ : bool, bReportErr_ =True):
        super().__init__()
        self.__bE   = None
        self.__id   = None
        self.__dht  = None
        self.__tst  = None
        self.__idct = None

        if not _Util.IsInstance(taskOpID_, _EATaskOpID, bThrowx_=True):
            self.CleanUp()
        elif not _Util.IsInstance(tskState_, _TaskState, bThrowx_=True):
            self.CleanUp()
        elif not _Util.IsInstance(dhThrd_, _PyThread, bThrowx_=True):
            self.CleanUp()
        else:
            self.__bE   = bEnclHThrd_
            self.__id   = taskOpID_
            self.__dht  = dhThrd_
            self.__tst  = tskState_
            self.__idct = _EATaskOpCTID.eNA

            self.Update(bReportErr_=bReportErr_)

    @staticmethod
    def IsJoinableHostThread(hostThrd_ : _PyThread):
        return isinstance(hostThrd_, _PyThread) and not (_TaskUtil.IsCurPyThread(hostThrd_) or _TaskUtil.IsStartupThread(hostThrd_))

    @property
    def isNotApplicable(self):
        return False if self.__idct is None else self.__idct.isNotApplicable

    @property
    def isIgnorable(self):
        return False if self.__idct is None else self.__idct.isIgnorable

    @property
    def isSynchronous(self):
        return False if self.__idct is None else self.__idct.isSynchronous

    @property
    def isASynchronous(self):
        return False if self.__idct is None else self.__idct.isASynchronous

    def Update(self, taskOpID_ : _EATaskOpID =None, bReportErr_ =True) -> _EATaskOpCTID:
        res = _EATaskOpCTID.eNA

        if self.__tst is None:
            return res

        if taskOpID_ is not None:
            if not _Util.IsInstance(taskOpID_, _EATaskOpID, bThrowx_=True):
                return res
            self.__id = taskOpID_
        if self.__id is None:
            self.__idct = res
            return res

        _eCurStateID = self.__tst.GetStateID()

        if _eCurStateID is None:
            self.__idct = res
            return res

        _prvOpCallTypeID         = None if ((self.__idct is None) or self.__idct.isNotApplicable) else self.__idct
        _bLinkedPyThrdCurThrd    = _TaskUtil.IsCurPyThread(self.__dht)
        _bLinkedPyThrdMainPyThrd = _TaskUtil.IsMainPyThread(self.__dht)
        bLinkedPyThrdStartupThrd = _TaskUtil.IsStartupThread(self.__dht)
        _bJoinable               = _bLinkedPyThrdCurThrd or not bLinkedPyThrdStartupThrd

        if not _eCurStateID.isStarted:
            res = self.__UpdateNotStarted(_eCurStateID, _bLinkedPyThrdCurThrd)

        elif _eCurStateID.isTransitional:
            res = self.__UpdateTransitional(_eCurStateID, _bLinkedPyThrdCurThrd, _bJoinable)

        else:
            res = self.__UpdateStarted(_eCurStateID, _bLinkedPyThrdCurThrd, _bJoinable)

        _doLog = False  or (_prvOpCallTypeID is None)
        _doLog = _doLog or (res != _prvOpCallTypeID)
        if _doLog:
            _doLogErr = bReportErr_ if res.isNotApplicable else False

            if _doLogErr:
                vlogif._LogOEC(False, _EFwErrorCode.VUE_00012)

        self.__idct = res
        return res

    def _ToString(self):
        if self.__id is None:
            return None
        res = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_001).format(self.__id.name, self.__idct.name)
        return res

    def _CleanUp(self):
        self.__bE   = None
        self.__id   = None
        self.__dht  = None
        self.__tst  = None
        self.__idct = None

    def __UpdateNotStarted(self, eCurStateID_ : _TaskState._EState, bLinkedPyThrdCurThrd_ : bool) -> _EATaskOpCTID:
        reqOP = self.__id.compactName
        if eCurStateID_.isStarted:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00184)
            return _EATaskOpCTID.eNA

        if not eCurStateID_.isInitialized:
            res = _EATaskOpCTID.eNA

        elif self.__id.isStart or self.__id.isRestart:
            res = _EATaskOpCTID.eSyncOP if bLinkedPyThrdCurThrd_ else _EATaskOpCTID.eASyncOP

        else:
            res = _EATaskOpCTID.eIgnore
        return res

    def __UpdateTransitional(self, eCurStateID_ : _TaskState._EState, bLinkedPyThrdCurThrd_ : bool, bLinkedPyThrdJoinable_ : bool) -> _EATaskOpCTID:
        reqOP = self.__id.compactName
        if not eCurStateID_.isTransitional:
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00185)
            return _EATaskOpCTID.eNA

        if self.__id.isStart or self.__id.isRestart:
            if eCurStateID_.isPendingRun:
                res = _EATaskOpCTID.eIgnore

            else:
                res = _EATaskOpCTID.eNA

        elif self.__id.isJoin:
            if not bLinkedPyThrdJoinable_:
                res = _EATaskOpCTID.eNA

            elif bLinkedPyThrdCurThrd_:
                res = _EATaskOpCTID.eIgnore

            else:
                res = _EATaskOpCTID.eSyncOP

        else:
            if eCurStateID_.isPendingRun:
                res = _EATaskOpCTID.eSyncOP if bLinkedPyThrdCurThrd_ else _EATaskOpCTID.eASyncOP

            else:
                res = _EATaskOpCTID.eIgnore
        return res

    def __UpdateStarted(self, eCurStateID_ : _TaskState._EState, bLinkedPyThrdCurThrd_ : bool, bLinkedPyThrdJoinable_ : bool) -> _EATaskOpCTID:
        reqOP = self.__id.compactName
        if not (eCurStateID_.isStarted and not eCurStateID_.isTransitional):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00186)
            return _EATaskOpCTID.eNA

        if self.__id.isStart or self.__id.isRestart:
            if eCurStateID_.isRunning:
                res = _EATaskOpCTID.eNA

            elif eCurStateID_.isFailed:
                if self.__id.isStart:
                    res = _EATaskOpCTID.eNA

                else:
                    res = _EATaskOpCTID.eSyncOP if bLinkedPyThrdCurThrd_ else _EATaskOpCTID.eASyncOP

            else:
                if self.__id.isStart:
                    res = _EATaskOpCTID.eNA

                else:
                    res = _EATaskOpCTID.eSyncOP if bLinkedPyThrdCurThrd_ else _EATaskOpCTID.eASyncOP

        elif self.__id.isJoin:
            if eCurStateID_.isRunning:
                if not bLinkedPyThrdJoinable_:
                    res = _EATaskOpCTID.eNA

                elif bLinkedPyThrdCurThrd_:
                    res = _EATaskOpCTID.eIgnore

                else:
                    res = _EATaskOpCTID.eSyncOP

            else:
                res = _EATaskOpCTID.eIgnore

        else:
            if eCurStateID_.isRunning:
                res = _EATaskOpCTID.eSyncOP if bLinkedPyThrdCurThrd_ else _EATaskOpCTID.eASyncOP

            else:
                res = _EATaskOpCTID.eIgnore
        return res
