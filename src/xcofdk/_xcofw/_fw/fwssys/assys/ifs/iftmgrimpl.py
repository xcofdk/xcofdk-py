# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : iftmgrimpl.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from typing import Union

from _fw.fwssys.fwcore.ipc.tsk.taskdefs  import _ETaskSelfCheckResultID
from _fw.fwssys.fwerrh.logs.xcoexception import _XcoXcpRootBase

class _ITMgrImpl:
    __slots__ = []

    def __init__(self):
        pass

    @property
    def _isTMgrAvailable(self):
        pass

    def _IsCurTask(self, taskID_: int) -> bool:
        pass

    def _CreateTask( self
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
        pass

    def _CreateThread( self
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
        pass

    def _GetCurTaskBadge(self):
        pass
    
    def _GetTask(self, taskID_, bDoWarn_ =True):
        pass

    def _GetTaskID(self, taskName_):
        pass

    def _GetTaskBadge(self, taskID_, bDoWarn_ =True):
        pass

    def _GetTaskError(self, taskID_=None):
        pass

    def _StartTask(self, taskID_, tskOpPCheck_ =None) -> bool:
        pass

    def _StopTask(self, taskID_, bCancel_ =False, removeTask_ =True, tskOpPCheck_ =None) -> bool:
        pass

    def _JoinTask(self, taskID_, timeout_ =None, tskOpPCheck_ =None) -> bool:
        pass

    def _SelfCheckTask(self, taskID_ : int) -> _ETaskSelfCheckResultID:
        pass

    def _StartUTask(self, utConn_, tskOpPCheck_ =None) -> bool:
        pass

    def _StopUTask(self, utConn_, bCancel_ =False, bCleanupDriver_ =True, tskOpPCheck_ =None) -> bool:
        pass

    def _JoinUTask(self, utConn_, timeout_ =None, tskOpPCheck_ =None) -> bool:
        pass

    def _ProcUnhandledXcp(self, xcp_: _XcoXcpRootBase):
        pass

