# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : taskbadge.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum import unique

from _fw.fwssys.fwcore.logging           import vlogif
from _fw.fwssys.fwcore.base.strutil      import _StrUtil
from _fw.fwssys.fwcore.base.util         import _Util
from _fw.fwssys.fwcore.ipc.tsk.taskdefs  import _EFwsID
from _fw.fwssys.fwcore.ipc.tsk.taskutil  import _TaskUtil
from _fw.fwssys.fwcore.ipc.tsk.taskutil  import _ETaskType
from _fw.fwssys.fwcore.ipc.tsk.taskutil  import _ETaskRightFlag
from _fw.fwssys.fwcore.types.aobject     import _AbsSlotsObject
from _fw.fwssys.fwcore.types.ebitmask    import _EBitMask
from _fw.fwssys.fwcore.types.commontypes import _FwIntFlag
from _fw.fwssys.fwerrh.fwerrorcodes      import _EFwErrorCode

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _TaskBadge(_AbsSlotsObject):
    @unique
    class _EMiscInfo(_FwIntFlag):
        ebfNone               = 0x00
        ebfEnclPyThrd         = (0x01 << 0)
        ebfAutoEnclPyThrd     = (0x01 << 1)
        ebfEnclStartupThrd    = (0x01 << 2)
        ebfRcTask             = (0x01 << 3)
        ebfExtQueueSupport    = (0x01 << 4)
        ebfIntQueueSupport    = (0x01 << 5)

        @staticmethod
        def IsNone(eInfoBitMask_ : _FwIntFlag):
            return eInfoBitMask_ == _TaskBadge._EMiscInfo.ebfNone

        @staticmethod
        def IsEnclosingPyThread(eInfoBitMask_ : _FwIntFlag):
            return _EBitMask.IsEnumBitFlagSet(eInfoBitMask_, _TaskBadge._EMiscInfo.ebfEnclPyThrd)

        @staticmethod
        def IsEnclosingStartupThread(eInfoBitMask_ : _FwIntFlag):
            return _EBitMask.IsEnumBitFlagSet(eInfoBitMask_, _TaskBadge._EMiscInfo.ebfEnclStartupThrd)

        @staticmethod
        def IsAutoEnclosed(eInfoBitMask_ : _FwIntFlag):
            return _EBitMask.IsEnumBitFlagSet(eInfoBitMask_, _TaskBadge._EMiscInfo.ebfAutoEnclPyThrd)

        @staticmethod
        def IsRcTask(eInfoBitMask_ : _FwIntFlag):
            return _EBitMask.IsEnumBitFlagSet(eInfoBitMask_, _TaskBadge._EMiscInfo.ebfRcTask)

        @staticmethod
        def IsSupportingExtQueue(eInfoBitMask_ : _FwIntFlag):
            return _EBitMask.IsEnumBitFlagSet(eInfoBitMask_, _TaskBadge._EMiscInfo.ebfExtQueueSupport)

        @staticmethod
        def IsSupportingIntQueue(eInfoBitMask_ : _FwIntFlag):
            return _EBitMask.IsEnumBitFlagSet(eInfoBitMask_, _TaskBadge._EMiscInfo.ebfIntQueueSupport)

        @staticmethod
        def DefaultMask():
            return _TaskBadge._EMiscInfo(_TaskBadge._EMiscInfo.ebfNone.value)

        @staticmethod
        def AddInfoBitFlag(eInfoBitMask_ : _FwIntFlag, eInfoBitFlag_):
            return _EBitMask.AddEnumBitFlag(eInfoBitMask_, eInfoBitFlag_)

    __slots__ = [ '__t' , '__bm' , '__tid' , '__rm' , '__n' , '__nid' , '__uid' , '__c' ]

    def __init__( self, *
                , taskName_    : str
                , taskID_      : int
                , threadUID_   : int
                , taskType_    : _ETaskType
                , trMask_      : _ETaskRightFlag =_ETaskRightFlag.eUserTask
                , threadNID_   : int     =None
                , fwsID_       : _EFwsID =None
                , bEnclHThrd_  =False
                , bEnclSThrd_  =False
                , bAEnclHThrd_ =False
                , bXQ_         =False
                , bIQ_         =False
                , bRcTask_     =False
                , cloneBy_     =None):
        super().__init__()

        self.__c   = None
        self.__n   = None
        self.__t   = None
        self.__bm  = None
        self.__rm  = None
        self.__nid = None
        self.__tid = None
        self.__uid = None

        if cloneBy_ is not None:
            if not isinstance(cloneBy_, _TaskBadge):
                self.CleanUp()
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00250)
                return
            if cloneBy_.dtaskUID is None:
                self.CleanUp()
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00251)
                return

            self.__c   = cloneBy_.__c
            self.__n   = cloneBy_.__n
            self.__t   = _ETaskType(cloneBy_.__t.value)
            self.__bm  = _TaskBadge._EMiscInfo(cloneBy_.__bm.value)
            self.__rm  = _ETaskRightFlag(cloneBy_.__rm.value)
            self.__nid = cloneBy_.__nid
            self.__tid = cloneBy_.__tid
            self.__uid = cloneBy_.__uid
            return

        _bError = False
        if not _Util.IsInstance(taskID_, int, bThrowx_=True):
            _bError = True
        elif not _StrUtil.IsIdentifier(taskName_, bThrowx_=True):
            _bError = True
        elif not _Util.IsInstance(taskType_, _ETaskType, bThrowx_=True):
            _bError = True
        elif not _Util.IsInstance(trMask_, _ETaskRightFlag, bThrowx_=True):
            _bError = True
        elif bEnclHThrd_:
            if threadNID_ is None:
                if _TaskUtil.IsNativeThreadIdSupported():
                    _bError = True
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00252)
            elif not _Util.IsInstance(threadNID_, int, bThrowx_=True):
                _bError = True
        elif bEnclSThrd_ or bAEnclHThrd_:
            _bError = True
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00253)
        elif (bXQ_ or bIQ_) and not taskType_.isFwTask:
            _bError = True
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00254)

        if _bError:
            self.CleanUp()
        else:
            self.__c   = fwsID_
            self.__n   = taskName_
            self.__t   = _ETaskType(taskType_.value)
            self.__bm  = _TaskBadge._EMiscInfo.DefaultMask()
            self.__rm  = _ETaskRightFlag(trMask_.value)
            self.__nid = threadNID_
            self.__tid = taskID_
            self.__uid = threadUID_

            if bEnclHThrd_:
                self.__bm = _TaskBadge._EMiscInfo.AddInfoBitFlag(self.__bm, _TaskBadge._EMiscInfo.ebfEnclPyThrd)
                if bEnclSThrd_:
                    self.__bm = _TaskBadge._EMiscInfo.AddInfoBitFlag(self.__bm, _TaskBadge._EMiscInfo.ebfEnclStartupThrd)
                if bAEnclHThrd_:
                    self.__bm = _TaskBadge._EMiscInfo.AddInfoBitFlag(self.__bm, _TaskBadge._EMiscInfo.ebfAutoEnclPyThrd)
            if bXQ_:
                self.__bm = _TaskBadge._EMiscInfo.AddInfoBitFlag(self.__bm, _TaskBadge._EMiscInfo.ebfExtQueueSupport)
            if bIQ_:
                self.__bm = _TaskBadge._EMiscInfo.AddInfoBitFlag(self.__bm, _TaskBadge._EMiscInfo.ebfIntQueueSupport)
            if bRcTask_ and (taskType_.isXTaskTask or taskType_.isXTaskThread):
                self.__bm = _TaskBadge._EMiscInfo.AddInfoBitFlag(self.__bm, _TaskBadge._EMiscInfo.ebfRcTask)

    @property
    def isValid(self):
        return self.__t is not None

    @property
    def isCFwThread(self):
        return self.isValid and self.__t.isCFwThread

    @property
    def isFwThread(self):
        return self.isValid and self.__t.isFwThread

    @property
    def isFwTask(self):
        return self.isValid and self.__t.isFwTask

    @property
    def isFwMain(self):
        return self.isValid and self.__t.isFwMain

    @property
    def isFwMainThread(self):
        return self.isValid and self.__t.isFwMainThread

    @property
    def isFwMainTask(self):
        return self.isValid and self.__t.isFwMainTask

    @property
    def isXTaskThread(self):
        return self.isValid and self.__t.isXTaskThread

    @property
    def isMainXTaskThread(self):
        return self.isValid and self.__t.isMainXTaskThread

    @property
    def isXTaskTask(self):
        return self.isValid and self.__t.isXTaskTask

    @property
    def isMainXTaskTask(self):
        return self.isValid and self.__t.isMainXTaskTask

    @property
    def isDrivingXTask(self):
        return self.isValid and (self.isXTaskTask or self.isXTaskThread)

    @property
    def isRcTask(self):
        return self.isValid and _TaskBadge._EMiscInfo.IsRcTask(self.__bm)

    @property
    def isEnclosingPyThread(self):
        return self.isValid and _TaskBadge._EMiscInfo.IsEnclosingPyThread(self.__bm)

    @property
    def isEnclosingStartupThread(self):
        return self.isValid and _TaskBadge._EMiscInfo.IsEnclosingStartupThread(self.__bm)

    @property
    def isAutoEnclosed(self):
        return self.isValid and _TaskBadge._EMiscInfo.IsAutoEnclosed(self.__bm)

    @property
    def isSupportingExternalQueue(self) -> bool:
        return self.isValid and _TaskBadge._EMiscInfo.IsSupportingExtQueue(self.__bm)

    @property
    def isSupportingInternalQueue(self) -> bool:
        return self.isValid and _TaskBadge._EMiscInfo.IsSupportingIntQueue(self.__bm)

    @property
    def hasFwTaskRight(self):
        return self.isValid and self.__rm.hasFwTaskRight

    @property
    def hasUserTaskRight(self):
        return self.isValid and self.__rm.hasUserTaskRight

    @property
    def hasXTaskTaskRight(self):
        return self.isValid and self.__rm.hasXTaskTaskRight

    @property
    def hasErrorObserverTaskRight(self):
        return self.isValid and self.__rm.hasErrorObserverTaskRight

    @property
    def hasDieXcpTargetTaskRight(self):
        return self.isValid and self.__rm.hasDieXcpTargetTaskRight

    @property
    def hasDieExceptionDelegateTargetTaskRight(self):
        return self.isValid and self.__rm.hasDieExceptionDelegateTargetTaskRight

    @property
    def hasForeignErrorListnerTaskRight(self):
        return self.isValid and self.__rm.hasForeignErrorListnerTaskRight

    @property
    def fwSID(self):
        return None if not self.isValid else self.__c

    @property
    def dtaskUID(self) -> int:
        return None if not self.isValid else self.__tid

    @property
    def dtaskName(self) -> str:
        return None if not self.isValid else self.__n

    @property
    def threadUID(self) -> int:
        return None if not self.isValid else self.__uid

    @property
    def threadNID(self) -> int:
        return None if not self.isValid else self.__nid

    def _UpdateRuntimeIDs(self, threadUID_ : int =None, threadNID_ : int =None):
        if not self.isValid:
            return

        if threadUID_ is not None:
            _Util.IsInstance(threadUID_, int, bThrowx_=True)
            self.__uid = threadUID_
        if threadNID_ is not None:
            _Util.IsInstance(threadNID_, int, bThrowx_=True)
            self.__nid = threadNID_

    def _Clone(self):
        if self.dtaskUID is None:
            res = None
        else:
            res = _TaskBadge(cloneBy_=self, taskName_=None, taskID_=None, threadUID_=None, taskType_=None)
            if res .dtaskUID is None:
                res = None
        return res

    def _ToString(self, bCompact_ =True, bExcludeUID_ =True):
        if not self.isValid:
            return None

        ret = _FwTDbEngine.GetText(_EFwTextID.eTaskBadge_ToString_01).format(self.dtaskName, self.__t.value, hex(self.__bm), hex(self.__rm))
        if not bCompact_:
            ret += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_018).format('-' if self.threadNID is None else self.threadNID)
            if not bExcludeUID_:
                ret += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_018).format(self.threadUID)
        return ret

    def _CleanUp(self):
        self.__c   = None
        self.__n   = None
        self.__t   = None
        self.__bm  = None
        self.__rm  = None
        self.__nid = None
        self.__tid = None
        self.__uid = None
