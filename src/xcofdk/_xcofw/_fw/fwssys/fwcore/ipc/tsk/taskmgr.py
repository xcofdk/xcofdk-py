# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : taskmgr.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from typing import Union

from _fw.fwssys.assys.ifs.iftmgrimpl     import _ITMgrImpl
from _fw.fwssys.assys.ifs.tiftmgr        import _ITTMgr
from _fw.fwssys.fwcore.ipc.tsk.taskdefs  import _ETaskSelfCheckResultID
from _fw.fwssys.fwcore.types.aobject     import _AbsSlotsObject
from _fw.fwssys.fwerrh.logs.xcoexception import _XcoXcpRootBase

class _TaskManager(_AbsSlotsObject):
    __slots__    = []
    _theTMgrImpl = None

    def __init__(self):
        super().__init__()

    @property
    def isTMgrAvailable(self):
        return self.__impl._isTMgrAvailable

    def IsCurTask(self, taskID_: int) -> bool:
        return self.__impl._IsCurTask(taskID_)

    def CreateTask( self
                  , fwtPrf_         =None 
                  , rbl_            =None 
                  , taskName_       : str  =None
                  , enclHThrd_      =None 
                  , rmask_          =None 
                  , delayedStartMS_ : int  =None
                  , args_           : list =None
                  , kwargs_         : dict =None
                  , tpAttrs_        : dict =None
                  , bStart_         =False
                  , tskOpPCheck_    =None 
                  ) -> Union[int, None]:
        return self.__impl._CreateTask( fwtPrf_=fwtPrf_
                                      , rbl_=rbl_
                                      , taskName_=taskName_
                                      , rmask_=rmask_
                                      , delayedStartMS_=delayedStartMS_
                                      , enclHThrd_=enclHThrd_
                                      , args_=args_
                                      , kwargs_=kwargs_
                                      , tpAttrs_=tpAttrs_
                                      , bStart_=bStart_
                                      , tskOpPCheck_=tskOpPCheck_)

    def CreateThread( self
                    , fwthrdPrf_   =None 
                    , utaskConn_   =None 
                    , taskName_    : str  =None
                    , enclHThrd_   =None 
                    , bStart_      : bool =None
                    , thrdTgtCIF_  =None 
                    , args_        : list =None
                    , kwargs_      : dict =None
                    , tpAttrs_     : dict =None
                    , tskOpPCheck_ =None  
                    ) -> Union[int, None]:
        return self.__impl._CreateThread( fwthrdPrf_=fwthrdPrf_
                                        , utaskConn_=utaskConn_
                                        , taskName_=taskName_
                                        , enclHThrd_=enclHThrd_
                                        , bStart_=bStart_
                                        , thrdTgtCIF_=thrdTgtCIF_
                                        , args_=args_
                                        , kwargs_=kwargs_
                                        , tpAttrs_=tpAttrs_
                                        , tskOpPCheck_=tskOpPCheck_)

    def GetCurTaskBadge(self):
        return self.__impl._GetCurTaskBadge()
    
    def GetTask(self, taskID_, bDoWarn_ =True):
        return self.__impl._GetTask(taskID_, bDoWarn_=bDoWarn_)

    def GetTaskID(self, taskName_):
        return self.__impl._GetTaskID(taskName_)

    def GetTaskBadge(self, taskID_, bDoWarn_ =True):
        return self.__impl._GetTaskBadge(taskID_, bDoWarn_=bDoWarn_)

    def GetTaskError(self, taskID_=None):
        return self.__impl._GetTaskError(taskID_)

    def StartTask(self, taskID_, tskOpPCheck_ =None) -> bool:
        return self.__impl._StartTask(taskID_, tskOpPCheck_=tskOpPCheck_)

    def StopTask(self, taskID_, bCancel_ =False, removeTask_ =True, tskOpPCheck_ =None) -> bool:
        return self.__impl._StopTask(taskID_, bCancel_=bCancel_, removeTask_=removeTask_, tskOpPCheck_=tskOpPCheck_)

    def CancelTask(self, taskID_, removeTask_ =True, tskOpPCheck_ =None) -> bool:
        return self.__impl._StopTask(taskID_, bCancel_=True, removeTask_=removeTask_, tskOpPCheck_=tskOpPCheck_)

    def JoinTask(self, taskID_, timeout_ =None, tskOpPCheck_ =None) -> bool:
        return self.__impl._JoinTask(taskID_, timeout_=timeout_, tskOpPCheck_=tskOpPCheck_)

    def SelfCheckTask(self, taskID_ : int) -> _ETaskSelfCheckResultID:
        return self.__impl._SelfCheckTask(taskID_)

    def StartUTask(self, utConn_, tskOpPCheck_ =None) -> bool:
        return self.__impl._StartUTask(utConn_, tskOpPCheck_=tskOpPCheck_)

    def StopUTask(self, utConn_, bCancel_ =False, bCleanupDriver_ =True, tskOpPCheck_ =None) -> bool:
        return self.__impl._StopUTask(utConn_, bCancel_=bCancel_, bCleanupDriver_=bCleanupDriver_, tskOpPCheck_=tskOpPCheck_)

    def JoinUTask(self, utConn_, timeout_ =None, tskOpPCheck_ =None) -> bool:
        return self.__impl._JoinUTask(utConn_, timeout_=timeout_, tskOpPCheck_=tskOpPCheck_)

    def _ProcUnhandledException(self, xcp_: _XcoXcpRootBase):
        return self.__impl._ProcUnhandledXcp(xcp_)

    @property
    def __impl(self) -> Union[_ITMgrImpl, None]:
        return None if not isinstance(self, _ITMgrImpl) else self

def _TaskMgr() -> _TaskManager:
    return _TaskManager._theTMgrImpl

def _TTaskMgr() -> _ITTMgr:
    _tm = _TaskManager._theTMgrImpl
    return None if not isinstance(_tm, _ITTMgr) else _tm
