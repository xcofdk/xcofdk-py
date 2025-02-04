# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : taskbadge.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum import unique

from xcofdk._xcofw.fw.fwssys.fwcore.logging           import vlogif
from xcofdk._xcofw.fw.fwssys.fwcore.base.strutil      import _StrUtil
from xcofdk._xcofw.fw.fwssys.fwcore.base.util         import _Util
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil  import _TaskUtil
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil  import _ETaskType
from xcofdk._xcofw.fw.fwssys.fwcore.ipc.tsk.taskutil  import _ETaskRightFlag
from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject     import _AbstractSlotsObject
from xcofdk._xcofw.fw.fwssys.fwcore.types.ebitmask    import _EBitMask
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes import _FwIntFlag

from xcofdk._xcofw.fw.fwssys.fwerrh.fwerrorcodes import _EFwErrorCode

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine

class _TaskBadge(_AbstractSlotsObject):

    @unique
    class _EMiscInfo(_FwIntFlag):
        ebfNone               = 0x00
        ebfEnclPyThrd         = (0x01 << 0)
        ebfAutoEnclPyThrd     = (0x01 << 1)
        ebfEnclStartupThrd    = (0x01 << 2)
        ebfExtQueueSupport    = (0x01 << 3)
        ebfIntQueueSupport    = (0x01 << 4)

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

    __slots__ = [
        '__eTskType' , '__eInfoBM' , '__taskID' , '__trMask' , '__taskName' , '__threadNID' , '__threadUID'
    ]

    def __init__( self, *
                , taskName_                 : str
                , taskID_                   : int
                , threadUID_                : int
                , taskType_                 : _ETaskType
                , trMask_                   : _ETaskRightFlag =_ETaskRightFlag.eUserTask
                , threadNID_                : int            =None
                , bEnclosingPyThrd_                          =False
                , bEnclosingStartupThrd_                     =False
                , bAutoEnclosedPyThrd_                       =False
                , bExtQueueSupport_                          =False
                , bIntQueueSupport_                          =False
                , cloneBy_                                   =None):
        super().__init__()

        self.__taskID    = None
        self.__trMask    = None
        self.__eInfoBM   = None
        self.__eTskType  = None
        self.__taskName  = None
        self.__threadNID = None
        self.__threadUID = None

        if cloneBy_ is not None:
            if not isinstance(cloneBy_, _TaskBadge):
                self.CleanUp()
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00250)
                return
            if cloneBy_.taskID is None:
                self.CleanUp()
                vlogif._LogOEC(True, _EFwErrorCode.VFE_00251)
                return

            self.__taskID    = cloneBy_.__taskID
            self.__trMask    = _ETaskRightFlag(cloneBy_.__trMask.value)
            self.__eInfoBM   = _TaskBadge._EMiscInfo(cloneBy_.__eInfoBM.value)
            self.__eTskType  = _ETaskType(cloneBy_.__eTskType.value)
            self.__taskName  = cloneBy_.__taskName
            self.__threadNID = cloneBy_.__threadNID
            self.__threadUID = cloneBy_.__threadUID
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
        elif bEnclosingPyThrd_:
            if threadNID_ is None:
                if _TaskUtil.IsNativeThreadIdSupported():
                    _bError = True
                    vlogif._LogOEC(True, _EFwErrorCode.VFE_00252)
            elif not _Util.IsInstance(threadNID_, int, bThrowx_=True):
                _bError = True
        elif bEnclosingStartupThrd_ or bAutoEnclosedPyThrd_:
            _bError = True
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00253)
        elif (bExtQueueSupport_ or bIntQueueSupport_) and not taskType_.isFwTask:
            _bError = True
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00254)

        if _bError:
            self.CleanUp()
        else:
            self.__taskID    = taskID_
            self.__trMask    = _ETaskRightFlag(trMask_.value)
            self.__eInfoBM   = _TaskBadge._EMiscInfo.DefaultMask()
            self.__eTskType  = _ETaskType(taskType_.value)
            self.__taskName  = taskName_
            self.__threadNID = threadNID_
            self.__threadUID = threadUID_

            if bEnclosingPyThrd_:
                self.__eInfoBM = _TaskBadge._EMiscInfo.AddInfoBitFlag(self.__eInfoBM, _TaskBadge._EMiscInfo.ebfEnclPyThrd)
                if bEnclosingStartupThrd_:
                    self.__eInfoBM = _TaskBadge._EMiscInfo.AddInfoBitFlag(self.__eInfoBM, _TaskBadge._EMiscInfo.ebfEnclStartupThrd)
                if bAutoEnclosedPyThrd_:
                    self.__eInfoBM = _TaskBadge._EMiscInfo.AddInfoBitFlag(self.__eInfoBM, _TaskBadge._EMiscInfo.ebfAutoEnclPyThrd)
            if bExtQueueSupport_:
                self.__eInfoBM = _TaskBadge._EMiscInfo.AddInfoBitFlag(self.__eInfoBM, _TaskBadge._EMiscInfo.ebfExtQueueSupport)
            if bIntQueueSupport_:
                self.__eInfoBM = _TaskBadge._EMiscInfo.AddInfoBitFlag(self.__eInfoBM, _TaskBadge._EMiscInfo.ebfIntQueueSupport)

    @property
    def isValid(self):
        return self.__eTskType is not None

    @property
    def isFwThread(self):
        return self.isValid and self.__eTskType.isFwThread

    @property
    def isFwTask(self):
        return self.isValid and self.__eTskType.isFwTask

    @property
    def isFwMain(self):
        return self.isValid and self.__eTskType.isFwMain

    @property
    def isFwMainThread(self):
        return self.isValid and self.__eTskType.isFwMainThread

    @property
    def isFwMainTask(self):
        return self.isValid and self.__eTskType.isFwMainTask

    @property
    def isXTaskThread(self):
        return self.isValid and self.__eTskType.isXTaskThread

    @property
    def isMainXTaskThread(self):
        return self.isValid and self.__eTskType.isMainXTaskThread

    @property
    def isXTaskTask(self):
        return self.isValid and self.__eTskType.isXTaskTask

    @property
    def isMainXTaskTask(self):
        return self.isValid and self.__eTskType.isMainXTaskTask

    @property
    def isDrivingExecutable(self):
        return self.isValid and (self.isFwTask or self.isXTaskThread)

    @property
    def isDrivingXTask(self):
        return self.isValid and (self.isXTaskTask or self.isXTaskThread)

    @property
    def isEnclosingPyThread(self):
        return self.isValid and _TaskBadge._EMiscInfo.IsEnclosingPyThread(self.__eInfoBM)

    @property
    def isEnclosingStartupThread(self):
        return self.isValid and _TaskBadge._EMiscInfo.IsEnclosingStartupThread(self.__eInfoBM)

    @property
    def isAutoEnclosed(self):
        return self.isValid and _TaskBadge._EMiscInfo.IsAutoEnclosed(self.__eInfoBM)

    @property
    def isSupportingExternalQueue(self) -> bool:
        return self.isValid and _TaskBadge._EMiscInfo.IsSupportingExtQueue(self.__eInfoBM)

    @property
    def isSupportingInternalQueue(self) -> bool:
        return self.isValid and _TaskBadge._EMiscInfo.IsSupportingIntQueue(self.__eInfoBM)

    @property
    def hasFwTaskRight(self):
        return self.isValid and self.__trMask.hasFwTaskRight

    @property
    def hasUserTaskRight(self):
        return self.isValid and self.__trMask.hasUserTaskRight

    @property
    def hasXTaskTaskRight(self):
        return self.isValid and self.__trMask.hasXTaskTaskRight

    @property
    def hasUnitTestTaskRight(self):
        return self.isValid and self.__trMask.hasUnitTestTaskRight

    @property
    def hasErrorObserverTaskRight(self):
        return self.isValid and self.__trMask.hasErrorObserverTaskRight

    @property
    def hasDieXcpTargetTaskRight(self):
        return self.isValid and self.__trMask.hasDieXcpTargetTaskRight

    @property
    def hasDieExceptionDelegateTargetTaskRight(self):
        return self.isValid and self.__trMask.hasDieExceptionDelegateTargetTaskRight

    @property
    def hasForeignErrorListnerTaskRight(self):
        return self.isValid and self.__trMask.hasForeignErrorListnerTaskRight

    @property
    def taskID(self) -> int:
        return None if not self.isValid else self.__taskID

    @property
    def taskName(self) -> str:
        return None if not self.isValid else self.__taskName

    @property
    def taskUniqueName(self) -> str:
        return self.taskName

    @property
    def threadUID(self) -> int:
        return None if not self.isValid else self.__threadUID

    @property
    def threadNID(self) -> int:
        return None if not self.isValid else self.__threadNID

    def _UpdateRuntimeIDs(self, threadUID_ : int =None, threadNID_ : int =None):
        if not self.isValid:
            return

        if threadUID_ is not None:
            _Util.IsInstance(threadUID_, int, bThrowx_=True)
            self.__threadUID = threadUID_
        if threadNID_ is not None:
            _Util.IsInstance(threadNID_, int, bThrowx_=True)
            self.__threadNID = threadNID_

    def _Clone(self):
        if self.taskID is None:
            res = None
        else:
            res = _TaskBadge(cloneBy_=self, taskName_=None, taskID_=None, threadUID_=None, taskType_=None)
            if res .taskID is None:
                res = None
        return res

    def _ToString(self, *args_, **kwargs_):
        if not self.isValid:
            return None

        _compact, excludeUID = True, True
        if len(args_) > 0:
            for _ii in range(len(args_)):
                val = args_[_ii]
                if _ii == 0:
                    _compact = val
                elif _ii == 1:
                    excludeUID = val

        ret = _FwTDbEngine.GetText(_EFwTextID.eTaskBadge_ToString_01).format(self.taskUniqueName, self.__eTskType.value, hex(self.__eInfoBM), hex(self.__trMask))
        if not _compact:
            ret += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_018).format('-' if self.threadNID is None else self.threadNID)
            if not excludeUID:
                ret += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_018).format(self.threadUID)
        return ret

    def _CleanUp(self):
        self.__taskID    = None
        self.__trMask    = None
        self.__eInfoBM   = None
        self.__eTskType  = None
        self.__taskName  = None
        self.__threadNID = None
        self.__threadUID = None
