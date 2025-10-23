# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwrtetmgr.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

import pickle as _PyPickle
from   pickle   import PickleError
from   datetime import datetime as _PyDateTime
from   os       import getpid as _PyGetPID
from   typing   import Any
from   typing   import Tuple
from   typing   import Union
from   multiprocessing.shared_memory import SharedMemory as _PySHM

from xcofdk.fwcom import EXmpPredefinedID

from _fw.fwssys.fwcore.types.commontypes import override
from _fw.fwssys.fwcore.types.commontypes import _EDepInjCmd
from _fw.fwssys.fwmp.fwrte.fwrtedefs     import _ERteTXErrorID
from _fw.fwssys.fwmp.fwrte.fwrtedatax    import _ChildProcExitData
from _fw.fwssys.fwmp.fwrte.rteexception  import _RteException
from _fw.fwssys.fwmp.fwrte.rteexception  import _RtePSException
from _fw.fwssys.fwmp.fwrte.rteexception  import _RteTSException

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

class _RteTokenHeader:
    __slots__ = [ '_sz' ]

    def __init__(self, sz_ : int):
        self._sz = sz_

class _RteTokenGuide:
    __slots__ = [ '__ip' , '__fp' , '__ho' , '__xdps' , '__d' , '__mpsds' , '__mxps' ]

    _mstr   = None
    __DPSDS = 0x2800

    def __init__(self, bXcpTrackingDisabled_ =False, bForce_ =False):
        if (_RteTokenGuide._mstr is not None) and not bForce_:
            raise _RtePSException()

        self.__ho    = 0x80000000
        self.__d     = None
        self.__mxps  = 0 if bXcpTrackingDisabled_ else 0x2600
        self.__xdps  = 0x200
        self.__mpsds = 0x7FF00000
        self.__fp    = _PyPickle.dumps(None)
        self.__ip    = _PyPickle.dumps(_RteTokenHeader(self.__ho))
        self.__d     = self.__CalcDefaultSDSize()

        if not bForce_:
            _RteTokenGuide._mstr = self

    @property
    def _isTrackingProcessXcp(self) -> bool:
        return self.__mxps > 0

    @property
    def _headerSize(self) -> int:
        return len(self.__ip)

    @property
    def _headerOffset(self) -> int:
        return self.__ho

    @property
    def _minProcessSDataSize(self) -> int:
        return len(self.__fp)

    @property
    def _maxProcessSDataSize(self) -> int:
        return self.__mpsds

    @property
    def _defaultProcessSDataSize(self) -> int:
        return self.__d

    @property
    def _maxXcpPayloadSize(self) -> int:
        return self.__mxps

    @property
    def _minTokenPldSize(self) -> int:
        return len(self.__ip) + len(self.__fp)

    @property
    def _maxTokenPldSize(self) -> int:
        return len(self.__ip) + self.__xdps + self.__mpsds

    @property
    def _initialPayload(self) -> bytes:  
        return self.__ip

    @property
    def _processFailurePayload(self) -> bytes:  
        return self.__fp

    def _GetProcessPayloadSize(self, maxSDSize_: int =None):
        if maxSDSize_ is None:
            maxSDSize_ = self._defaultProcessSDataSize
        res  = len(self.__ip) + self.__xdps
        res += max(maxSDSize_, self.__mxps)
        return res

    def __CalcDefaultSDSize(self):
        res = EXmpPredefinedID.DefaultSuppliedDataMaxSize
        if not (isinstance(res, int) and (res > 0)):
            res = _RteTokenGuide.__DPSDS
        elif res < self._minProcessSDataSize:
            res = self._minProcessSDataSize
        elif res > self._maxProcessSDataSize:
            res = self._maxProcessSDataSize
        return res

class _FwRteToken(_PySHM):
    def __init__(self, name=None, create=False, size=0):
        super().__init__(name=name, create=create, size=size)

    @override
    def close(self):
        pass

    @override
    def unlink(self):
        pass

    @staticmethod
    def _GetTokenGuide() -> _RteTokenGuide:
        return _RteTokenGuide._mstr

    @property
    def _tokenName(self):
        return self.name

    def _Close(self):
        try:
            super().close()
        except (Exception, BaseException) as _xcp:
            pass

    def _IsReadyToLoad(self) -> _ERteTXErrorID:
        try:
            _tg     = _FwRteToken._GetTokenGuide()
            _dmpHdr = self.buf[:_tg._headerSize:]
            _hdr    = _PyPickle.loads(_dmpHdr)
            res     = _ERteTXErrorID.eSuccess if (_hdr._sz>_tg._headerOffset) else _ERteTXErrorID.eDontCare
            del _dmpHdr
        except (IndexError, PickleError, Exception) as _xcp:
            res = _ERteTXErrorID.eLowLevelTokenError
        return res

    def _ReadUnlink(self) -> Any:
        return self.__ReadUnlink()

    def _CloseUnlink(self):
        self._Close()
        self.__Unlink()

    def _WriteClose(self, tknPld_ : _ChildProcExitData, tkng_ : _RteTokenGuide, maxSDSize_ : int) -> Union[_RteTSException, None]:
        return self.__WriteClose(tknPld_, tkng_, maxSDSize_)

    def __Unlink(self):
        try:
            super().unlink()
        except (Exception, BaseException) as _xcp:
            pass

    def __WriteClose(self, tknPld_ : _ChildProcExitData, tg_ : _RteTokenGuide, maxSDSize_ : int) -> Union[_RteTSException, None]:
        _WRITE_ERR_ID = _ERteTXErrorID.eWriteRteToken

        if not (isinstance(tknPld_, _ChildProcExitData) and self.size>=tg_._minTokenPldSize):
            self._Close()
            _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteException_TID_014).format(self.name, self.size, tg_._minTokenPldSize)
            return _RteTSException(msg_=_msg, code_=_WRITE_ERR_ID.value)

        _CAPC      = self.size - tg_._headerSize
        _tname     = self.name
        _rteXcp    = None
        _msgPrfx   = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteException_TID_009).format(_PyGetPID())
        _dmpPld    = None
        _dmpPldLen = 0

        try:
            _dmpPld = _PyPickle.dumps(tknPld_)
            _dmpPldLen = len(_dmpPld)
            if (_dmpPldLen > maxSDSize_) or (_dmpPldLen > _CAPC):
                if _dmpPldLen > maxSDSize_:
                    _msg = _msgPrfx + _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteException_TID_015).format(_dmpPldLen, maxSDSize_)
                else:
                    _msg = _msgPrfx + _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteException_TID_004).format(_dmpPldLen, _CAPC)
                del _dmpPld
                _dmpPld = None

                _rteXcp = _RteTSException(msg_=_msg, code_=_WRITE_ERR_ID.value, maxXPS_=tg_._maxXcpPayloadSize)
                if tg_._isTrackingProcessXcp:
                    _dmpPld = _rteXcp._Serialize()
                if _dmpPld is None:
                    _dmpPld = tg_._processFailurePayload
                _dmpPldLen = len(_dmpPld)
        except (PickleError, Exception) as _xcp:
            _msg    = _msgPrfx + _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteException_TID_005)
            _dmpPld = None

            _rteXcp = _RteTSException(msg_=_msg, code_=_WRITE_ERR_ID.value, xcp_=_xcp, maxXPS_=tg_._maxXcpPayloadSize)
            if tg_._isTrackingProcessXcp:
                _dmpPld = _rteXcp._Serialize()
            if _dmpPld is None:
                _dmpPld = tg_._processFailurePayload
            _dmpPldLen = len(_dmpPld)

        _hdr = _RteTokenHeader(tg_._headerOffset+_dmpPldLen)
        try:
            _dmpHdr = _PyPickle.dumps(_hdr)
            if len(_dmpHdr) != tg_._headerSize:
                if _rteXcp is None:
                    _msg    = _msgPrfx + _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteException_TID_006).format(tg_._headerSize, len(_dmpHdr))
                    _rteXcp = _RteTSException(msg_=_msg, code_=_WRITE_ERR_ID.value, maxXPS_=tg_._maxXcpPayloadSize)

                del _dmpHdr
                del _dmpPld
                self._Close()
                return _rteXcp
        except (PickleError, Exception) as _xcp:
            if _rteXcp is None:
                _msg    = _msgPrfx + _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteException_TID_007).format(_hdr._sz)
                _rteXcp = _RteTSException(msg_=_msg, code_=_WRITE_ERR_ID.value, xcp_=_xcp, maxXPS_=tg_._maxXcpPayloadSize)

            del _dmpPld
            self._Close()
            return _rteXcp

        _dmpToken    = _dmpHdr + _dmpPld
        _dmpTokenLen = len(_dmpToken)
        try:
            self.buf[0:_dmpTokenLen] = _dmpToken
        except (IndexError, Exception) as _xcp:
            _msg    = _msgPrfx + _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteException_TID_008).format(_dmpTokenLen)
            _rteXcp = _RteTSException(msg_=_msg, code_=_WRITE_ERR_ID.value, xcp_=_xcp)

        self._Close()
        del _dmpToken
        del _dmpHdr
        del _dmpPld
        return _rteXcp

    def __ReadUnlink(self) -> Any:
        _UNLINK_ERR_ID = _ERteTXErrorID.eUnlinkRteToken

        _tg      = _FwRteToken._GetTokenGuide()
        _buf     = self.buf
        _tname   = self.name
        _bufLen  = self.size
        _msgPrfx = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteException_TID_009).format(_PyGetPID())

        if not (_tg._minTokenPldSize <= _bufLen <= _tg._maxTokenPldSize):
            _msg = _msgPrfx + _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteException_TID_010).format(_bufLen)
            self._CloseUnlink()
            return _RtePSException(msg_=_msg, code_=_UNLINK_ERR_ID.value)

        _hdr     = None
        _hdrLen  = _tg._headerSize
        try:
            _hdrDump = bytes(_buf[:_hdrLen])
            _hdr     = _PyPickle.loads(_hdrDump)
            del _hdrDump
        except (IndexError, PickleError, Exception) as _xcp:
            _msg = _msgPrfx + _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteException_TID_011).format(_bufLen)
            self._CloseUnlink()
            return _RtePSException(msg_=_msg, code_=_UNLINK_ERR_ID.value, xcp_=_xcp)

        _pldLen = _hdr._sz - _tg._headerOffset
        if (_pldLen < 1) or (_bufLen < (_hdrLen+_pldLen)):
            _msg = _msgPrfx + _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteException_TID_012).format(_bufLen, _hdrLen, _pldLen)
            self._CloseUnlink()
            return _RtePSException(msg_=_msg, code_=_UNLINK_ERR_ID.value)

        _pld = None
        try:
            _pldDump = bytes(_buf[_hdrLen:_hdrLen + _pldLen])
            _pld = _PyPickle.loads(_pldDump)
            del _pldDump
        except (IndexError, PickleError, Exception) as _xcp:
            _msg = _msgPrfx + _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteException_TID_013).format(_bufLen, _hdrLen, _pldLen)
            self._CloseUnlink()
            return _RtePSException(msg_=_msg, code_=_UNLINK_ERR_ID.value, xcp_=_xcp)

        self._CloseUnlink()
        return _pld

class _FwRteTokenMgr:
    __slots__ = []

    def __init__(self):
        pass

    @staticmethod
    def IsXcpTrackingDisabled():
        _tg = _FwRteToken._GetTokenGuide()
        return _tg._isTrackingProcessXcp

    @staticmethod
    def CheckSuppliedDataSize(maxSDSize_ : int =None) -> Tuple[int, Union[str, None]]:
        _tg  = _FwRteToken._GetTokenGuide()
        _err = None
        if maxSDSize_ is None:
            maxSDSize_ = _tg._defaultProcessSDataSize
        if not (isinstance(maxSDSize_, int) and (_tg._minProcessSDataSize <= maxSDSize_ <= _tg._maxProcessSDataSize)):
            _err = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteTokenMgr_TID_005).format(str(maxSDSize_), _tg._minProcessSDataSize, _tg._maxProcessSDataSize)
        return maxSDSize_, _err

    @staticmethod
    def CreateToken(puid_ : int, maxSDSize_ : int =None) -> _FwRteToken:
        _tg = _FwRteToken._GetTokenGuide()
        _bufSize = _tg._GetProcessPayloadSize(maxSDSize_=maxSDSize_)
        return _FwRteTokenMgr.__CreateToken(puid_, _bufSize)

    @staticmethod
    def OpenToken(tokeName_ : str) -> _FwRteToken:
        return _FwRteTokenMgr.__OpenToken(tokeName_)

    @staticmethod
    def _DepInjection(dinjCmd_ : _EDepInjCmd, bXcpTrackingDisabled_ =False):
        if not dinjCmd_.isDeInject:
            try:
                if _RteTokenGuide._mstr is not None:
                    return False
                _tg = _RteTokenGuide(bXcpTrackingDisabled_=bXcpTrackingDisabled_)
                if _tg._isTrackingProcessXcp:
                    _RteException._DepInjection(_tg._maxXcpPayloadSize)
            except _RtePSException as _xcp:
                return False
        return True

    @staticmethod
    def __GetNextUniqueTokenName(puid_ : int):
        _dtNow = _PyDateTime.now()
        res    = "{:>03d}".format(_dtNow.microsecond // 1000)
        res    = _dtNow.strftime("%H_%M_%S__") + res
        res    = f'xrtet_{_PyGetPID()}_{puid_}__{res}'
        return res

    @staticmethod
    def __CreateToken(puid_ : int, bufSize_ : int) -> _FwRteToken:
        _tg    = _FwRteToken._GetTokenGuide()
        _tname = _FwRteTokenMgr.__GetNextUniqueTokenName(puid_)

        res = None
        try:
            res           = _FwRteToken(name=_tname, create=True, size=bufSize_)
            _initBytes    = _tg._initialPayload
            _initBytesLen = len(_initBytes)
            res.buf[:_initBytesLen] = _initBytes
        except FileExistsError as _xcp:
            _msg    = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteTokenMgr_TID_001).format(_tname, type(_xcp).__name__, _xcp)
            _msg   += _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteTokenMgr_TID_002).format(_tname)
            _rteXcp = _RtePSException(msg_=_msg, code_=_ERteTXErrorID.eCreateRteToken.value)
            raise _rteXcp

        except (IndexError, Exception) as _xcp:
            if res is not None:
                res._CloseUnlink()
            _msg    = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteTokenMgr_TID_001).format(_tname, type(_xcp).__name__, _xcp)
            _rteXcp = _RtePSException(msg_=_msg, code_=_ERteTXErrorID.eCreateRteToken.value)
            raise _rteXcp
        return res

    @staticmethod
    def __OpenToken(tokeName_ : str) -> _FwRteToken:
        if not (isinstance(tokeName_, str) and len(tokeName_.strip()) > 0):
            _msg    = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteTokenMgr_TID_003).format(str(tokeName_))
            _rteXcp = _RteTSException(msg_=_msg, code_=_ERteTXErrorID.eOpenRteToken.value)
            raise _rteXcp

        tokeName_ = tokeName_.strip()

        try:
            res = _FwRteToken(name=tokeName_)
        except (FileNotFoundError, Exception) as _xcp:
            _msg    = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_FwRteTokenMgr_TID_004).format(tokeName_, type(_xcp).__name__, _xcp)
            _rteXcp = _RteTSException(msg_=_msg, code_=_ERteTXErrorID.eOpenRteToken.value)
            raise _rteXcp
        return res
