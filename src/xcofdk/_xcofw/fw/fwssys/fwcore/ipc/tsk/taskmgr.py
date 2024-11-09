# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : taskmgr.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


from typing import Union as _PyUnion

from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject        import _AbstractSlotsObject
from xcofdk._xcofw.fw.fwssys.fwcore.logging.xcoexception import _XcoExceptionRoot


class _TaskManager(_AbstractSlotsObject):

    __slots__    = []
    _theTMgrImpl = None

    def __init__(self):
        super().__init__()

    @property
    def isTaskManagerApiAvailable(self):
        return self._isTaskManagerApiAvailable

    def CreateTask( self
                  , taskPrf_                       =None 
                  , runnable_                      =None 
                  , taskName_               : str  =None
                  , enclosedPyThread_              =None 
                  , resourcesMask_                 =None 
                  , delayedStartTimeSpanMS_ : int  =None
                  , args_                   : list =None
                  , kwargs_                 : dict =None
                  , taskProfileAttrs_       : dict =None
                  , bStart_                        =False
                  , tskOpPreCheck_                 =None 
                  ) -> _PyUnion[int, None]:
        return self._CreateTask( taskPrf_=taskPrf_
                               , runnable_=runnable_
                               , taskName_=taskName_
                               , resourcesMask_=resourcesMask_
                               , delayedStartTimeSpanMS_=delayedStartTimeSpanMS_
                               , enclosedPyThread_=enclosedPyThread_
                               , args_=args_
                               , kwargs_=kwargs_
                               , taskProfileAttrs_=taskProfileAttrs_
                               , bStart_=bStart_
                               , tskOpPreCheck_=tskOpPreCheck_)

    def CreateThread( self
                    , thrdProfile_                   =None 
                    , xtaskConn_                     =None 
                    , taskName_               : str  =None
                    , enclosedPyThread_              =None 
                    , bStart_                 : bool =None
                    , threadTargetCallableIF_        =None 
                    , args_                   : list =None
                    , kwargs_                 : dict =None
                    , threadProfileAttrs_     : dict =None
                    , tskOpPreCheck_                 =None  
                    ) -> _PyUnion[int, None]:
        return self._CreateThread( thrdProfile_=thrdProfile_
                                 , xtaskConn_=xtaskConn_
                                 , taskName_=taskName_
                                 , enclosedPyThread_=enclosedPyThread_
                                 , bStart_=bStart_
                                 , threadTargetCallableIF_=threadTargetCallableIF_
                                 , args_=args_
                                 , kwargs_=kwargs_
                                 , threadProfileAttrs_=threadProfileAttrs_
                                 , tskOpPreCheck_=tskOpPreCheck_)


    def GetCurTaskBadge(self):
        return self._GetCurTaskBadge()
    
    def GetCurTaskError(self, taskID_ =None):
        return self._GetCurTaskError(taskID_)
    
    def GetTask(self, taskID_, bDoWarn_ =True):
        return self._GetTask(taskID_, bDoWarn_=bDoWarn_)

    def GetTaskID(self, taskName_):
        return self._GetTaskID(taskName_)

    def GetTaskBadge(self, taskID_, bDoWarn_ =True):
        return self._GetTaskBadge(taskID_, bDoWarn_=bDoWarn_)

    def StartTask(self, taskID_, tskOpPreCheck_ =None) -> bool:
        return self._StartTask(taskID_, tskOpPreCheck_=tskOpPreCheck_)

    def RestartTask(self, taskID_, tskOpPreCheck_ =None) -> bool:
        return self._RestartTask(taskID_, tskOpPreCheck_=tskOpPreCheck_)

    def StopTask(self, taskID_, removeTask_ =True, tskOpPreCheck_ =None) -> bool:
        return self._StopTask(taskID_, removeTask_=removeTask_, tskOpPreCheck_=tskOpPreCheck_)

    def JoinTask(self, taskID_, timeout_ =None, tskOpPreCheck_ =None) -> bool:
        return self._JoinTask(taskID_, timeout_=timeout_, tskOpPreCheck_=tskOpPreCheck_)

    def StartXTask(self, xtConn_, tskOpPreCheck_ =None) -> bool:
        return self._StartXTask(xtConn_, tskOpPreCheck_=tskOpPreCheck_)

    def StopXTask(self, xtConn_, cleanupDriver_ =True, tskOpPreCheck_ =None) -> bool:
        return self._StopXTask(xtConn_, cleanupDriver_=cleanupDriver_, tskOpPreCheck_=tskOpPreCheck_)

    def JoinXTask(self, xtConn_, timeout_ =None, tskOpPreCheck_ =None) -> bool:
        return self._JoinXTask(xtConn_, timeout_=timeout_, tskOpPreCheck_=tskOpPreCheck_)

    def PrintTaskTable(self, tabPrefixed_ =False, printNavtiveID_ =False, printIdent_ =False):
        self._PrintTaskTable(tabPrefixed_=tabPrefixed_, printNavtiveID_=printNavtiveID_, printIdent_=printIdent_)

    def _ProcUnhandledException(self, xcp_: _XcoExceptionRoot):
        return self._ProcUnhandledXcp(xcp_)

    def _CleanUp(self):
        pass


def _TaskMgr() -> _TaskManager:
    return _TaskManager._theTMgrImpl
