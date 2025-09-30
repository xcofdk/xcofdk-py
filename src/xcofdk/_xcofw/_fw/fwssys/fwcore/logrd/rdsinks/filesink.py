# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : filesink.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

import logging

from _fw.fwssys.fwcore.logrd.logrecord           import _LogRecord
from _fw.fwssys.fwcore.logrd.rdsinks.logsinkbase import _LogSinkBase
from _fw.fwssys.fwcore.types.commontypes         import override

class _FileSink(_LogSinkBase):
    __slots__ = [ '__l' ]

    def __init__(self, pyLogger_ : logging.Logger):
        super().__init__()
        self.__l = pyLogger_

    @_LogSinkBase.isValidSink.getter
    def isValidSink(self) -> bool:
        return super()._IsValidSink() and (self.__l is not None)

    @override
    def _FlushLR(self, logRec_ : _LogRecord) -> bool:
        if not self.isValidSink:
            return False
        self.__l.info(logRec_._recToStr)
        return True

    @override
    def _CleanUp(self):
        if not self.isValidSink:
            return
        self.__l = None
        super()._CleanUp()
