# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwrtetoken.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


import pickle as _PyPickle
from os                            import getpid       as _PyGetPID
from multiprocessing.shared_memory import SharedMemory as _PySharedMemory
from datetime                      import datetime     as _PyDateTime

from xcofdk.fwcom.xmpdefs import EXPMPreDefinedID



class _FwRteToken:


    __bPRINT_MSG                 = False
    __TOKEN_HEADER_SIZE          = None
    __TOKEN_HEADER_OFFSET        = 0x80000000
    __INITIAL_TOKEN_BYTES        = None
    __FAILURE_TOKEN_BYTES        = None
    __MAX_TOKEN_PAYLOAD_SIZE     = 0x7FFFFFFF
    __MIN_TOKEN_PAYLOAD_SIZE     = None
    __DEFAULT_TOKEN_PAYLOAD_SIZE = None



    __slots__ = []

    def __init__(self):
        pass


    @staticmethod
    def GetMinPayloadSize():
        return _FwRteToken.__GetMinPayloadSize()

    @staticmethod
    def GetMaxPayloadSize():
        return _FwRteToken.__GetMaxPayloadSize()

    @staticmethod
    def GetDefaultPayloadSize():
        return _FwRteToken.__GetDefaultPayloadSize()

    @staticmethod
    def GetNextUniqueTokenName():
        _dtNow = _PyDateTime.now()
        res = "{:>03d}".format(_dtNow.microsecond // 1000)
        res = _dtNow.strftime("%H_%M_%S__") + res
        res = f'xrtet_{_PyGetPID()}_{res}'
        return res

    @staticmethod
    def IsTokenReadyToLoad(shm_ : _PySharedMemory):
        if not isinstance(shm_, _PySharedMemory):
            _FwRteToken.__PrintErrMsg(f'Bad RTE token object type to check: \'{type(shm_).__name__}\'')
            return False

        _minTokenSize = _FwRteToken.__GetMinTokenSize()
        if shm_.size < _minTokenSize:
            shm_.close()
            _FwRteToken.__PrintErrMsg(f'Found size of passed in RTE token \'{type(shm_).__name__}\' set to {shm_.size}, expecting a min. size of {_minTokenSize}.')
            return False

        return _FwRteToken.__IsTokenReadyToLoad(shm_)

    @staticmethod
    def CreateToken(tokeName_ : str, maxDataSize_ : int =None) -> _PySharedMemory:
        _FwRteToken.__CheckGetTokenHeaderSize()

        if not (isinstance(tokeName_, str) and len(tokeName_.strip()) > 0):
            _FwRteToken.__PrintErrMsg(f'Bad name to create RTE token: \'{str(tokeName_)}\'')
            return None
        tokeName_ = tokeName_.strip()

        if maxDataSize_ is None:
            maxDataSize_ = _FwRteToken.__GetDefaultPayloadSize()

        if not (isinstance(maxDataSize_, int) and (_FwRteToken.__GetMinPayloadSize() <= maxDataSize_ <=_FwRteToken.__GetMaxPayloadSize())):
            _range = f'[{_FwRteToken.__GetMinPayloadSize()}..{_FwRteToken.__GetMaxPayloadSize()}]'
            _FwRteToken.__PrintErrMsg(f'Invalid max. data size of {maxDataSize_} passed in to create RTE token \'{str(tokeName_)}\', expecting a value in range: {_range}')
            return None

        return _FwRteToken.__CreateToken(tokeName_, maxDataSize_)

    @staticmethod
    def OpenToken(tokeName_ : str) -> _PySharedMemory:
        _FwRteToken.__CheckGetTokenHeaderSize()

        if not (isinstance(tokeName_, str) and len(tokeName_.strip()) > 0):
            _FwRteToken.__PrintErrMsg(f'Bad name to open RTE token: \'{str(tokeName_)}\'')
            return None
        tokeName_ = tokeName_.strip()

        return _FwRteToken.__OpenToken(tokeName_)

    @staticmethod
    def WriteCloseToken(shm_ : _PySharedMemory, tokenPayload_ : object):
        if not isinstance(shm_, _PySharedMemory):
            _FwRteToken.__PrintErrMsg(f'Bad RTE token object type to write data to: \'{type(shm_).__name__}\'')
            return False

        _minTokenSize = _FwRteToken.__GetMinTokenSize()
        if shm_.size < _minTokenSize:
            shm_.close()
            _FwRteToken.__PrintErrMsg(f'Found size of passed in RTE token \'{type(shm_).__name__}\' set to {shm_.size}, expecting a min. size of {_minTokenSize}.')
            return False

        return _FwRteToken.__WriteCloseToken(shm_, tokenPayload_)

    @staticmethod
    def ReadUnlinkToken(shm_ : _PySharedMemory, bIgnoreError_ =False):
        if not _FwRteToken.IsTokenReadyToLoad(shm_):
            if isinstance(shm_, _PySharedMemory):
                _FwRteToken.CloseUnlinkToken(shm_)
            return False, None
        return _FwRteToken.__ReadUnlinkToken(shm_, bIgnoreError_)

    @staticmethod
    def CloseUnlinkToken(shm_ : _PySharedMemory):
        if isinstance(shm_, _PySharedMemory):
            shm_.close()
            shm_.unlink()


    @staticmethod
    def __IsTokenAvailable(tokeName_ : str) -> bool:
        try:
            _shm = _PySharedMemory(name=tokeName_, create=False, size=0)
        except (FileNotFoundError, BaseException):
            _shm = None

        res = _shm is not None
        if res:
            _shm.close()
        return res

    @staticmethod
    def __IsTokenReadyToLoad(shm_ : _PySharedMemory) -> bool:
        _dumpHdr = shm_.buf[:_FwRteToken.__TOKEN_HEADER_SIZE:]
        _hdr     = _PyPickle.loads(_dumpHdr)

        del _dumpHdr
        return _hdr > _FwRteToken.__TOKEN_HEADER_OFFSET

    @staticmethod
    def __CreateToken(tokeName_ : str, maxDataSize_ : int) -> _PySharedMemory:
        _FwRteToken.__PrintMsg(f'Creating RTE token {tokeName_} of size {maxDataSize_}...')

        res, _errMsg = None, None
        try:
            res           = _PySharedMemory(name=tokeName_, create=True, size=maxDataSize_)
            _initBytes    = _FwRteToken.__GetInitialTokenBytes()
            _initBytesLen = len(_initBytes)
            res.buf[:_initBytesLen] = _initBytes
        except FileExistsError as xcp:
            _errMsg  = f'Cauhgt {type(xcp).__name__} exception below while trying to create RTE token \'{tokeName_}\' of size {maxDataSize_}:\n\t{type(xcp).__name__} : {xcp}'
            _errMsg += f'\n\tNOTE:'
            _errMsg += f'\n\t  - An (orphaned) shared memory file \'{tokeName_}\' exists alrady, most probably from a previous, failed attempt to create a child process.'
            _errMsg += f'\n\t  - If so, remove that file and try it again after resolving the root cause of previous failure(s).'
        except BaseException as xcp:
            _errMsg = f'Cauhgt {type(xcp).__name__} exception below while trying to create RTE token \'{tokeName_}\' of size {maxDataSize_}:\n\t{type(xcp).__name__} : {xcp}'

        if res is None:
            _FwRteToken.__PrintErrMsg(_errMsg)
        else:
            _FwRteToken.__PrintMsg(f'Created RTE token: name={tokeName_} , size={maxDataSize_}')
        return res

    @staticmethod
    def __OpenToken(tokeName_ : str) -> _PySharedMemory:
        _FwRteToken.__PrintMsg(f'Trying to open RTE token {tokeName_}...')

        try:
            res = _PySharedMemory(name=tokeName_, create=False, size=0)
        except (FileNotFoundError, BaseException) as xcp:
            res = None
            _FwRteToken.__PrintErrMsg(f'Cauhgt exception below while trying to open RTE token \'{tokeName_}\':\n\t{type(xcp).__name__} : {xcp}')

        if res is not None:
            _FwRteToken.__PrintMsg(f'Opened RTE token: name={tokeName_} , size={res.size}')
        return res

    @staticmethod
    def __WriteCloseToken(shm_ : _PySharedMemory, tokenPayload_ : object):
        _tokeName = shm_.name
        _FwRteToken.__PrintMsg(f'RTE token {_tokeName}: Trying to write to token...')

        _tokenPldCapacity = shm_.size - _FwRteToken.__TOKEN_HEADER_SIZE

        res, _bNonePld = True, False

        _dumpPldLen = 0
        try:
            _dumpPld = _PyPickle.dumps(tokenPayload_)
            _dumpPldLen = len(_dumpPld)
            if _dumpPldLen > _tokenPldCapacity:
                _FwRteToken.__PrintErrMsg('RTE token {}: Passed in payload size of {} exceeds token\'s payload capacity of {}; will use \'None\' as payload instead.'.format(_tokeName, _dumpPldLen, _tokenPldCapacity))
                del _dumpPld

                res, _bNonePld = False, True
                _dumpPld    = _FwRteToken.__GetFailureTokenBytes()
                _dumpPldLen = len(_dumpPld)
        except (Exception, BaseException) as xcp:
            _FwRteToken.__PrintErrMsg('RTE token {}: Cauhgt exception below while trying to serialize token payload; will use \'None\' as payload instead: {}:\n\t{} : {}'.format(_tokeName, str(tokenPayload_), type(xcp).__name__, xcp))

            res, _bNonePld = False, True
            _dumpPld    = _FwRteToken.__GetFailureTokenBytes()
            _dumpPldLen = len(_dumpPld)
        if _dumpPld is None:
            shm_.close()
            return False


        _hdr = _FwRteToken.__TOKEN_HEADER_OFFSET + _dumpPldLen
        try:
            _dumpHdr = _PyPickle.dumps(_hdr)
            if len(_dumpHdr) != _FwRteToken.__TOKEN_HEADER_SIZE:
                _FwRteToken.__PrintErrMsg('RTE token {}: Unexpected mismatch of expected token header size of {}: {}'.format(_tokeName, _FwRteToken.__TOKEN_HEADER_SIZE, len(_dumpHdr)))

                del _dumpHdr
                _dumpHdr = None
        except (Exception, BaseException) as xcp:
            _dumpHdr = None
            _FwRteToken.__PrintErrMsg('RTE token {}: Cauhgt exception below while trying to serialize token header: {}:\n\t{} : {}'.format(_tokeName, _hdr, type(xcp).__name__, xcp))
        if _dumpHdr is None:
            shm_.close()
            return False


        _dumpToken    = bytearray(_dumpHdr + _dumpPld)
        _dumpTokenLen = len(_dumpToken)


        shm_.buf[:_dumpTokenLen] = _dumpToken
        shm_.close()


        del _dumpToken
        del _dumpHdr
        if not _bNonePld:
            del _dumpPld

        if res:
            _FwRteToken.__PrintMsg(f'RTE token {_tokeName}: Written payload into token: tokenSize={_dumpTokenLen} , payloadSize={_dumpPldLen}')
        return res

    @staticmethod
    def __ReadUnlinkToken(shm_ : _PySharedMemory, bIgnoreError_ : bool):
        _tokenName = shm_.name
        _FwRteToken.__PrintMsg(f'RTE token {_tokenName}: Trying to read RTE token...')

        _failedRes = False, None

        _buf    = shm_.buf
        _bufLen = shm_.size
        if not (_FwRteToken.__GetMinTokenSize() <= _bufLen <= _FwRteToken.__MAX_TOKEN_PAYLOAD_SIZE):
            _FwRteToken.CloseUnlinkToken(shm_)
            if not bIgnoreError_:
                _FwRteToken.__PrintErrMsg(f'RTE token {_tokenName}: Unexpected size of {_bufLen} of RTE token.')
            _FwRteToken.CloseUnlinkToken(shm_)
            return _failedRes


        _hdrLen = _FwRteToken.__TOKEN_HEADER_SIZE
        _hdrDump = bytes(_buf[:_hdrLen])
        try:
            _hdr = _PyPickle.loads(_hdrDump)
        except (Exception, BaseException) as xcp:
            _hdr = None
            if not bIgnoreError_:
                _FwRteToken.__PrintErrMsg('RTE token {}: Cauhgt exception below while trying to de-serialize token header:\n\t{} : {}'.format(_tokenName, type(xcp).__name__, xcp))
        if _hdr is None:
            _FwRteToken.CloseUnlinkToken(shm_)
            return _failedRes


        _pldLen = _hdr - _FwRteToken.__TOKEN_HEADER_OFFSET
        if _bufLen < (_hdrLen+_pldLen):
            if not bIgnoreError_:
                _FwRteToken.__PrintErrMsg('RTE token {}: Unexpected size of RTE token payload: bufSize={} , headerLen={} , payloadLen={}'.format(_tokenName, _bufLen, _hdrLen, _pldLen))
            _FwRteToken.CloseUnlinkToken(shm_)
            return _failedRes

        _FwRteToken.__PrintMsg(f'RTE token {_tokenName}: Trying to de-serialize token payload: bufSize={_bufLen} , headerLen={_hdrLen} , payloadLen={_pldLen}')


        _bDesFailed, _pld = False, None

        _pldDump = bytes(_buf[_hdrLen:_hdrLen+_pldLen])
        try:
            _pld = _PyPickle.loads(_pldDump)
        except (Exception, BaseException) as xcp:
            _bDesFailed = True
            if bIgnoreError_:
                _FwRteToken.__PrintErrMsg('RTE token {}: Cauhgt exception below while trying to de-serialize token payload:\n\t{} : {}'.format(_tokenName, type(xcp).__name__, xcp))
        if _bDesFailed:
            _FwRteToken.CloseUnlinkToken(shm_)
            return _failedRes

        _FwRteToken.__PrintMsg(f'RTE token {_tokenName}: Loaded RTE token: payloadType={type(_pld).__name__}')
        _FwRteToken.CloseUnlinkToken(shm_)
        return True, _pld

    @staticmethod
    def __PrintMsg(msg_ : str, bForce_ =False):
        if not _FwRteToken.__bPRINT_MSG:
            pass
        else:
            print(f'[RteIpcT] {msg_}')

    @staticmethod
    def __PrintErrMsg(msg_ : str):
        print(f'[RteIpcT][ERROR] {msg_}')

    @staticmethod
    def __GetMinTokenSize():
        return _FwRteToken.__CheckGetTokenHeaderSize() + _FwRteToken.__MIN_TOKEN_PAYLOAD_SIZE

    @staticmethod
    def __GetMaxTokenSize():
        return _FwRteToken.__CheckGetTokenHeaderSize() + _FwRteToken.__MAX_TOKEN_PAYLOAD_SIZE

    @staticmethod
    def __GetMinPayloadSize():
        _FwRteToken.__CheckGetTokenHeaderSize()
        return _FwRteToken.__MIN_TOKEN_PAYLOAD_SIZE

    @staticmethod
    def __GetMaxPayloadSize():
        return  _FwRteToken.__MAX_TOKEN_PAYLOAD_SIZE

    @staticmethod
    def __GetDefaultPayloadSize():
        res = _FwRteToken.__DEFAULT_TOKEN_PAYLOAD_SIZE
        if res is None:
            res = EXPMPreDefinedID.DefaultUserDefinedResultDataMaxSize
            if not isinstance(res, int):
                res = 1024
            elif res < _FwRteToken.__GetMinPayloadSize():
                res = _FwRteToken.__GetMinPayloadSize()
            elif res > _FwRteToken.__GetMaxPayloadSize():
                res = _FwRteToken.__GetMaxPayloadSize()
            _FwRteToken.__DEFAULT_TOKEN_PAYLOAD_SIZE = res
        return res

    @staticmethod
    def __GetInitialTokenBytes():
        if _FwRteToken.__INITIAL_TOKEN_BYTES is None:
            _FwRteToken.__INITIAL_TOKEN_BYTES = bytearray(_PyPickle.dumps(_FwRteToken.__TOKEN_HEADER_OFFSET))
        return _FwRteToken.__INITIAL_TOKEN_BYTES

    @staticmethod
    def __GetFailureTokenBytes():
        if _FwRteToken.__FAILURE_TOKEN_BYTES is None:
            _FwRteToken.__FAILURE_TOKEN_BYTES = bytearray(_PyPickle.dumps(None))
        return _FwRteToken.__FAILURE_TOKEN_BYTES

    @staticmethod
    def __CheckGetTokenHeaderSize():
        if _FwRteToken.__TOKEN_HEADER_SIZE is None:
            _tmp = _FwRteToken.__MAX_TOKEN_PAYLOAD_SIZE + _FwRteToken.__TOKEN_HEADER_OFFSET
            _tmp = _PyPickle.dumps(_tmp)
            if _tmp is None:
                _FwRteToken.__TOKEN_HEADER_SIZE = 19
            else:
                _FwRteToken.__TOKEN_HEADER_SIZE = len(_tmp)
            del _tmp

            _tmp = _PyPickle.dumps(None)
            if _tmp is None:
                _FwRteToken.__MIN_TOKEN_PAYLOAD_SIZE = 4
            else:
                _FwRteToken.__MIN_TOKEN_PAYLOAD_SIZE = len(_tmp)
            del _tmp

        return _FwRteToken.__TOKEN_HEADER_SIZE


