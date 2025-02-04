# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : logifbase.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from xcofdk._xcofw.fw.fwssys.fwcore.logging.logdefines import _ELogType

class _LogIFBase:

    __slots__    = []
    _theInstance = None

    def __init__(self):
        pass

    @staticmethod
    def GetInstance():
        return _LogIFBase._theInstance

    def ToString(self, *args_, **kwargs_):
        pass

    def CleanUp(self):
        pass

    def _AddLog( self, eLogType_: _ELogType
               , msg_                  =None
               , errCode_              =None
               , sysOpXcp_             =None
               , xcpTraceback_         =None
               , callstackLevelOffset_ =None
               , unhandledXcoBaseXcp_  =None
               , eLogifOpOption_       =None):
        pass

    def _GetCurrentXTaskError(self):
        pass

    def _GetCurrentXTaskErrorEntry(self, xuErrUniqueID_: int):
        pass

    def _ClearCurrentXTaskError(self) -> bool:
        pass

