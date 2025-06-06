# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : alogmgr.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from _fw.fwssys.fwcore.logging.logdefines import _ELogType

class _AbsLogMgr:
    __slots__ = []

    _sgltn = None

    def __init__(self):
        pass

    @staticmethod
    def GetInstance():
        return _AbsLogMgr._sgltn

    def ToString(self):
        pass

    def CleanUp(self):
        pass

    def _AddLog( self, logType_ : _ELogType
               , msg_           =None
               , errCode_       =None
               , sysOpXcp_      =None
               , xcpTraceback_  =None
               , unhXcoBaseXcp_ =None
               , logifOpOption_ =None):
        pass

    def _GetCurrentXTaskError(self):
        pass

    def _GetCurrentXTaskErrorEntry(self, xuErrUniqueID_: int):
        pass

    def _ClearCurrentXTaskError(self) -> bool:
        pass

