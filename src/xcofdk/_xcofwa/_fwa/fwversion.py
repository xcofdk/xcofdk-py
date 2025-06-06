# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwversion.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

class _FwVersion:
    __VERSION_INFO_MIT = (3, 0, None, None, None)

    @staticmethod
    def _GetVersionInfo(bShort_ =False, bSkipPrefix_ =False) -> str:
        _verInfo = _FwVersion.__VERSION_INFO_MIT

        res = f'{_verInfo[0]}.{_verInfo[1]}'
        if not bSkipPrefix_:
            res =f'v{res}'

        if not bShort_:
            _patch = _verInfo[2]
            if _patch is not None:
                res += f'.{_patch}'

        _stage = _verInfo[3]
        if _stage is not None:
            res += f'{_stage}'
            _stageSeqNum = _verInfo[4]
            if _stageSeqNum is not None:
                res += f'{_stageSeqNum}'
        return res

