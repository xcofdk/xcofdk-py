# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xprocesstgt.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from sys import exit as _PySysExit

from _fw.fwssys.fwmp.fwrte.fwrtedefs    import _ERteTXErrorID
from _fw.fwssys.fwmp.fwrte.fwrtetmgr    import _FwRteToken
from _fw.fwssys.fwmp.fwrte.fwrtetmgr    import _RteTokenGuide
from _fw.fwssys.fwmp.fwrte.fwrtetmgr    import _FwRteTokenMgr as _RteTMgr
from _fw.fwssys.fwmp.fwrte.fwrtedatax   import _ChildProcExitData
from _fw.fwssys.fwmp.fwrte.fwrtedatax   import _FwRteDataExchange
from _fw.fwssys.fwmp.fwrte.rteexception import _RteTSException

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _XProcessTarget:
    __slots__ = [ '__t' ]

    def __init__(self, hpTarget_):
        self.__t = hpTarget_

    def __call__(self, rteDX_ : _FwRteDataExchange, *args_, **kwargs_):
        return self.__ExecuteTarget(rteDX_)

    def isValid(self):
        return self.__t is not None

    @staticmethod
    def __Exit(errID_ : _ERteTXErrorID, rteTkn_ : _FwRteToken =None, procXD_ : _ChildProcExitData =None, tkng_ : _RteTokenGuide =None, maxSDSize_ : int =None):
        _xc = errID_.value
        if rteTkn_ is not None:
            _rteXcp = rteTkn_._WriteClose(procXD_, tkng_, maxSDSize_)
            if _rteXcp is not None:
                _xc = _rteXcp.code
        _PySysExit(_xc)

    def __ExecuteTarget(self, rteDX_ : _FwRteDataExchange):
        _errID, _rteTkn, _procXD, _tkng, _msds = None, None, None, None, None

        _bBreak = False
        while True:
            if _bBreak:
                break

            if not self.isValid:
                _errID = _ERteTXErrorID.eInvalidXprocessTarget
                break
            if not (isinstance(rteDX_, _FwRteDataExchange) and rteDX_.isValid):
                _errID = _ERteTXErrorID.eInvalidDXParam
                break
            try:
                rteDX_.AttchToChildProcess()
                _rteTkn = _RteTMgr.OpenToken(rteDX_.rteTokenName)
            except _RteTSException as _xcp:
                _errID = _xcp.code
                break

            _DISALLOWED_TYPES = (_RteTSException,)

            _xc     = 0
            _xd     = None
            _msds   = rteDX_.childProcessMaxSDSize
            _tkng   = _XProcessTarget.__GetTokenGuide(rteDX_.isXcpTrackingEnabled)
            _procXD = _ChildProcExitData()

            try:
                _xd = self.__t(*rteDX_.childProcessStartArgs, **rteDX_.childProcessStartKwargs)
                if isinstance(_xd, _DISALLOWED_TYPES):
                    _errID = _ERteTXErrorID.eDisallowedSuppliedDataType
                    if _tkng._isTrackingProcessXcp:
                        _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XProcessTarget_TID_002).format(rteDX_.childRteSeed, str(_xd))
                        _xd = _RteTSException(msg_=_msg, code_=_errID.value, maxXPS_=_tkng._maxXcpPayloadSize)
                    else:
                        _xd = None
                else:
                    _errID = _ERteTXErrorID.eSuccess

            except SystemExit as _xcp:
                _xc    = _xcp.code if isinstance(_xcp.code, int) else 0
                _errID = _ERteTXErrorID.eSysExitXcpByChildProcess
                if _tkng._isTrackingProcessXcp:
                    _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XProcessTarget_TID_001).format(type(_xcp).__name__, rteDX_.childRteSeed.seed)
                    _xd = _RteTSException(msg_=_msg, code_=_errID.value, xcp_=_xcp, maxXPS_=_tkng._maxXcpPayloadSize)

            except BaseException as _xcp:
                if isinstance(_xcp, _DISALLOWED_TYPES):
                    _errID = _ERteTXErrorID.eDisallowedXcpDataType
                    _xc    = _errID.value
                    if _tkng._isTrackingProcessXcp:
                        _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XProcessTarget_TID_003).format(rteDX_.childRteSeed, str(_xcp))
                        _xd = _RteTSException(msg_=_msg, code_=_errID.value, maxXPS_=_tkng._maxXcpPayloadSize)
                else:
                    _errID = _ERteTXErrorID.eOtherXcpByChildProcess
                    _xc    = _errID.value
                    if _tkng._isTrackingProcessXcp:
                        _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XProcessTarget_TID_001).format(type(_xcp).__name__, rteDX_.childRteSeed.seed)
                        _xd = _RteTSException(msg_=_msg, code_=_errID.value, xcp_=_xcp, maxXPS_=_tkng._maxXcpPayloadSize)

            finally:
                _procXD.errorID  = _errID
                _procXD.exitCode = _xc
                _procXD.exitData = _xd

                rteDX_._CleanUp()
                _bBreak = True

        _XProcessTarget.__Exit(_errID, _rteTkn, _procXD, _tkng, _msds)

    @staticmethod
    def __GetTokenGuide(bXcpTracking_ : bool):
        res = _FwRteToken._GetTokenGuide()
        if (res is None) or (res._isTrackingProcessXcp != bXcpTracking_):
            res = _RteTokenGuide(bXcpTracking_, bForce_=True)
        return res
