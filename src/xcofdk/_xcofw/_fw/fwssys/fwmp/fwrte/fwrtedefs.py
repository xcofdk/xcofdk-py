# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwrtedefs.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum   import auto
from enum   import unique
from enum   import IntEnum
from signal import SIGTERM
try:
    from signal import SIGKILL
except (ImportError, Exception):
    SIGKILL = SIGTERM

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

@unique
class _ERteTXErrorID(IntEnum):
    eSuccess                    =  0      #      same as 'os.EX_OK'      , but its value is platform-dependent and platform-dependent  !!
    eDontCare                   = 40      #
    eLowLevelTokenError         = auto()  
    eInvalidXprocessTarget      = auto()  # 42 - same as 'os.EX_USAGE'   , but its availability/value is not clear/specified  !!
    eInvalidDXParam             = auto()  # 43 - same as 'os.EX_DATAERR' , but its availability/value is not clear/specified  !!
    eAttchToChildProcess        = auto()  
    eCreateRteToken             = auto()  
    eOpenRteToken               = auto()  
    eWriteRteToken              = auto()  
    eUnlinkRteToken             = auto()  
    eUnexpectedTokenPayload     = auto()  
    eInvalidExitCodeByHostProc  = auto()  
    eDetachedFromFW             = auto()  
    eDisallowedXcpDataType      = auto()  
    eDisallowedSuppliedDataType = auto()  
    eSysExitXcpByChildProcess   = auto()  
    eOtherXcpByChildProcess     = auto()  

    @property
    def compactName(self):
        return self.name[1:]

    @property
    def isSuccess(self):
       return self == _ERteTXErrorID.eSuccess

    @property
    def isDontCare(self):
       return self == _ERteTXErrorID.eDontCare

    @property
    def isLowLevelTokenError(self):
       return self == _ERteTXErrorID.eLowLevelTokenError

    @staticmethod
    def FromInt2Str(val_ : int):
        if not isinstance(val_, int):
            res = f'{val_}'
        elif (val_ != 0) and not (_ERteTXErrorID.eDontCare.value <= val_ <= _ERteTXErrorID.eOtherXcpByChildProcess.value):
            if val_ == (-1*SIGTERM):
                res = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XProcessConn_TID_021)
                res = f'{val_}:{res}'
            elif val_ == (-1*SIGKILL):
                res = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XProcessConn_TID_022)
                res = f'{val_}:{res}'
            else:
                res = f'{val_}'
        else:
            res = f'{val_}:{_ERteTXErrorID(val_).compactName}'
        return res
