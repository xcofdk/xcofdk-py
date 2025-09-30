# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : consolesink.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from _fw.fwssys.fwcore.logrd.logrecord           import _LogRecord
from _fw.fwssys.fwcore.logrd.rdsinks.logsinkbase import _LogSinkBase
from _fw.fwssys.fwcore.types.commontypes         import override

class _ConsoleSink(_LogSinkBase):
    __slots__ = [ '__bH' ]

    def __init__(self, bHLEnabled_ =True):
        super().__init__()
        self.__bH = bHLEnabled_

    @_LogSinkBase.isHighLightingEnabled.getter
    def isHighLightingEnabled(self) -> bool:
        return self.__bH

    @override
    def _FlushLR(self, logRec_ : _LogRecord) -> bool:
        _msg = logRec_._recToStr
        if self.__bH and logRec_._recColor.isColor:
            _msg = _LogSinkBase._ColorText(_msg, logRec_._recColor)
        try:
            print(_msg)
        except AttributeError as _xcp:
            pass
        return True

    @override
    def _CleanUp(self):
        if not self.isValidSink:
            return
        self.__bH = None
        super()._CleanUp()
