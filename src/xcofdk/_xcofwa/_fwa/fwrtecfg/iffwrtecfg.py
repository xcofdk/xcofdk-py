# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : iffwrtecfg.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

class _IFwRteConfig:
    __slots__ = []

    def __init__(self):
        pass

    def __str__(self) -> str:
        pass

    @property
    def _isValid(self) -> bool:
        pass

    @property
    def _isAutoStopEnabled(self) -> bool:
        pass

    @property
    def _isForcedAutoStopEnabled(self) -> bool:
        pass

    @property
    def _isTerminalModeEnabled(self) -> bool:
        pass

    @property
    def _isExperimentalFreeThreadingBypassed(self) -> bool:
        pass

    @property
    def _isSubSystemMessagingDisabled(self) -> bool:
        pass

    @property
    def _isSubSystemMultiProcessingDisabled(self) -> bool:
        pass

    @property
    def _isExceptionTrackingOfChildProcessesDisabled(self) -> bool:
        pass

    @property
    def _isLogRDConsoleSinkDisabled(self) -> bool:
        pass

    @property
    def _isLogRDFileSinkEnabled(self) -> bool:
        pass

    @property
    def _isLogRDTcpSinkEnabled(self) -> bool:
        pass
