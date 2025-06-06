# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xcbcase.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from enum    import auto
from enum    import unique
from inspect import isclass as _PyIsClass

from _fw.fwssys.fwcore.logging           import vlogif
from _fw.fwssys.fwcore.logging           import logif
from _fw.fwssys.fwcore.base.fwcallable   import _FwCallable
from _fw.fwssys.fwcore.base.sigcheck     import _CallableSignature
from _fw.fwssys.fwcore.types.aobject     import _AbsSlotsObject
from _fw.fwssys.fwcore.types.commontypes import _CommonDefines
from _fw.fwssys.fwerrh.fwerrorcodes      import _EFwErrorCode
from _fw.fwssys.fwcore.types.commontypes import _FwIntEnum

from _fw.fwtdb.fwtdbengine import _EFwTextID
from _fw.fwtdb.fwtdbengine import _FwTDbEngine

@unique
class _EXCallbackID(_FwIntEnum):
    eSetup      = 0
    eRun        = auto()
    eTeardown   = auto()
    eProcExtMsg = auto()
    eProcIntMsg = auto()

    @property
    def isSetup(self):
        return self == _EXCallbackID.eSetup

    @property
    def isRun(self):
        return self == _EXCallbackID.eRun

    @property
    def isTeardown(self):
        return self == _EXCallbackID.eTeardown

    @property
    def isProcExtMsg(self):
        return self == _EXCallbackID.eProcExtMsg

    @property
    def isProcIntMsg(self):
        return self == _EXCallbackID.eProcIntMsg

class _XCallback(_AbsSlotsObject):
    __slots__ = [ '__id' , '__cbif' , '__bG' ]

    def __init__(self, id_ : _EXCallbackID, cbif_ : _FwCallable, bGeneric_ : bool):
        super().__init__()
        self.__bG   = bGeneric_
        self.__id   = id_
        self.__cbif = cbif_

    def __call__(self, *args_, **kwargs_):
        if self.__isInvalid:
            return None
        return self.__cbif(*args_, **kwargs_)

    @property
    def isValid(self):
        return not self.__isInvalid

    @property
    def isSetup(self):
        return False if self.__isInvalid else self.__id.isSetup

    @property
    def isRun(self):
        return False if self.__isInvalid else self.__id.isRun

    @property
    def isTeardown(self):
        return False if self.__isInvalid else self.__id.isTeardown

    @property
    def isProcExtMsg(self):
        return False if self.__isInvalid else self.__id.isProcExtMsg

    @property
    def isProcIntMsg(self):
        return False if self.__isInvalid else self.__id.isProcIntMsg

    @property
    def isGeneric(self):
        return False if self.__isInvalid else self.__bG

    @property
    def callbackID(self):
        return self.__id

    @property
    def callbackName(self):
        return None if self.__isInvalid else self.__cbif.callbackName

    @property
    def ifsoruce(self):
        return None if self.__isInvalid else self.__cbif.ifsoruce

    @property
    def ifSpecType(self):
        return None if self.__isInvalid else self.__cbif.ifSpecType

    def CheckCallbackSignature(self, rctClassName_ : str):
        return self.__CheckCallbackSignature(rctClassName_)

    @property
    def _callbackFunction(self):
        return None if self.__isInvalid else self.__cbif._callbackFunction

    def _ToString(self):
        if self.__isInvalid:
            return None
        _midPart = _FwTDbEngine.GetText(_EFwTextID.eXCbCase_XCallback_ToString_001) if self.isGeneric else _CommonDefines._STR_EMPTY
        return _FwTDbEngine.GetText(_EFwTextID.eXCbCase_XCallback_ToString_002).format(_midPart, self.callbackID.compactName, self.callbackName)

    def _CleanUp(self):
        if self.__cbif is not None:
            self.__cbif.CleanUp()
        self.__bG   = None
        self.__id   = None
        self.__cbif = None

    @property
    def __isInvalid(self):
        return self.__id is None

    def __CheckCallbackSignature(self, rctClassName_ : str):
        if self.__isInvalid:
            return False

        _cbif = self.__cbif
        if not callable(_cbif._callbackFunction):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00567)
            return False

        if not (_cbif.isSpecifiedByFunction or _cbif.isSpecifiedByCallableInstance or _cbif.isSpecifiedByInstanceMethod):
            _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XCbCase_TID_012).format(rctClassName_, _cbif.callbackName)
            logif._XLogErrorEC(_EFwErrorCode.UE_00227, _msg)
            return False

        _bGen = self.isGeneric
        if self.__id.isTeardown:
            _bIgnoreTail       = False
            _minPosParamsCount = 1 if _bGen else 0
        elif self.__id.value < _EXCallbackID.eTeardown.value:
            _bIgnoreTail       = True
            _minPosParamsCount = 1 if _bGen else -1
        else:
            _bIgnoreTail       = False
            _minPosParamsCount = 2 if _bGen else 1

        res = _CallableSignature.CheckSignatureParamsCount(_cbif._callbackFunction, _minPosParamsCount, _bIgnoreTail, bDoLogOnError_=False)
        if not res:
            if _minPosParamsCount < 1:
                _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XCbCase_TID_015).format(rctClassName_, _cbif.callbackName, _cbif.callbackName)
            else:
                _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XCbCase_TID_013).format(rctClassName_, _cbif.callbackName, _minPosParamsCount, _cbif.callbackName)
            if self.isGeneric:
                _msg += _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XCbCase_TID_014)
            logif._XLogErrorEC(_EFwErrorCode.UE_00228, _msg)
        return res

class _XCbCase(_AbsSlotsObject):
    __slots__ = [ '__a' , '__i' ]

    __lstBaseClassNames = [_FwTDbEngine.GetText(_EFwTextID.eLogMsg_XRCTAgent_PhXF_IF_CLASS), _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XRCTAgent_PhXF_REF_IF_CLASS)]

    def __init__( self
                , rctClassName_   : str
                , cbRun_          =None
                , cbSetup_        =None
                , cbTeardown_     =None
                , cbProcExtMsg_   =None
                , cbProcIntMsg_   =None
                , cbPhXFInst_     =None
                , bMsgCase_       =False
                , bBlockingExtQ_  =False
                , bGenericParam_  =False
                , bIQueueEnabled_ =False):
        super().__init__()
        self.__a = None
        self.__i = None

        if not (isinstance(rctClassName_, str) and len(rctClassName_.strip())):
            rctClassName_ = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XCbCase_TID_018)

        _bWARN_ONLY = False

        if bBlockingExtQ_:
            bMsgCase_ = True

        _bError, cbRun_, cbSetup_, cbTeardown_, cbProcExtMsg_, cbProcIntMsg_, cbPhXFInst_ = _XCbCase.__CheckOnRedundancy(
            rctClassName_=rctClassName_
          , cbRun_=cbRun_, cbSetup_=cbSetup_, cbTeardown_=cbTeardown_
          , cbProcExtMsg_=cbProcExtMsg_, cbProcIntMsg_=cbProcIntMsg_
          , cbPhXFInst_=cbPhXFInst_, bWarnOnly_=_bWARN_ONLY)
        if _bError:
            return

        _bPhXFCB      = cbPhXFInst_ is not None
        _bPhXFClassCB = _PyIsClass(cbPhXFInst_) if _bPhXFCB else False

        _phxfDefaultInst = None
        if _bPhXFClassCB:
            try:
                _phxfDefaultInst = cbPhXFInst_()
            except BaseException as _xcp:
                _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XCbCase_TID_004).format(rctClassName_, cbPhXFInst_.__name__, str(_xcp))
                if _bWARN_ONLY:
                    logif._XLogWarning(_msg)
                else:
                    logif._XLogErrorEC(_EFwErrorCode.UE_00225, _msg)
                return

        _lstXCb            = []
        _phxfInst          = None
        _failedCbParamName = None

        while True:
            if _bPhXFCB:
                _phxfInst = _phxfDefaultInst if _bPhXFClassCB else cbPhXFInst_

                _mn = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XRCTAgent_CB_NAME_RUN)
                _cbif = _FwCallable.CreateInstance(_phxfInst, methodName_=_mn, bWarn_=False)
                if (_cbif is not None) and _XCbCase.__IsDefaultCallback(_cbif._callbackFunction):
                    _cbif.CleanUp()
                    _cbif = None
                if _cbif is not None:
                    _xcb = _XCallback(_EXCallbackID.eRun, _cbif, bGenericParam_)
                    _lstXCb.append(_xcb)
                _mn = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XRCTAgent_CB_NAME_SETUP)
                _cbif = _FwCallable.CreateInstance(_phxfInst, methodName_=_mn, bWarn_=False)
                if (_cbif is not None) and _XCbCase.__IsDefaultCallback(_cbif._callbackFunction):
                    _cbif.CleanUp()
                    _cbif = None
                if _cbif is not None:
                    _xcb = _XCallback(_EXCallbackID.eSetup, _cbif, bGenericParam_)
                    _lstXCb.append(_xcb)
                _mn = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XRCTAgent_CB_NAME_TEARDOWN)
                _cbif = _FwCallable.CreateInstance(_phxfInst, methodName_=_mn, bWarn_=False)
                if (_cbif is not None) and _XCbCase.__IsDefaultCallback(_cbif._callbackFunction):
                    _cbif.CleanUp()
                    _cbif = None
                if _cbif is not None:
                    _xcb = _XCallback(_EXCallbackID.eTeardown, _cbif, bGenericParam_)
                    _lstXCb.append(_xcb)
                _mn = _FwTDbEngine.GetText(_EFwTextID.eEUTaskApiID_ProcessExternalMessage)
                _cbif = _FwCallable.CreateInstance(_phxfInst, methodName_=_mn, bWarn_=False)
                if (_cbif is not None) and _XCbCase.__IsDefaultCallback(_cbif._callbackFunction):
                    _cbif.CleanUp()
                    _cbif = None
                if _cbif is not None:
                    _xcb = _XCallback(_EXCallbackID.eProcExtMsg, _cbif, bGenericParam_)
                    _lstXCb.append(_xcb)
                _mn = _FwTDbEngine.GetText(_EFwTextID.eEUTaskApiID_ProcessInternalMessage)
                _cbif = _FwCallable.CreateInstance(_phxfInst, methodName_=_mn, bWarn_=False)
                if (_cbif is not None) and _XCbCase.__IsDefaultCallback(_cbif._callbackFunction):
                    _cbif.CleanUp()
                    _cbif = None
                if _cbif is not None:
                    _xcb = _XCallback(_EXCallbackID.eProcIntMsg, _cbif, bGenericParam_)
                    _lstXCb.append(_xcb)
            else:
                if cbRun_ is not None:
                    _cbif = _FwCallable.CreateInstance(cbRun_, methodName_=None, bWarn_=False)
                    if _cbif is None:
                        _failedCbParamName = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XRCTAgent_CB_PARAM_NAME_001)
                        break
                    _xcb = _XCallback(_EXCallbackID.eRun, _cbif, bGenericParam_)
                    _lstXCb.append(_xcb)
                if cbSetup_ is not None:
                    _cbif = _FwCallable.CreateInstance(cbSetup_, methodName_=None, bWarn_=False)
                    if _cbif is None:
                        _failedCbParamName = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XRCTAgent_CB_PARAM_NAME_002)
                        break
                    _xcb = _XCallback(_EXCallbackID.eSetup, _cbif, bGenericParam_)
                    _lstXCb.append(_xcb)
                if cbTeardown_ is not None:
                    _cbif = _FwCallable.CreateInstance(cbTeardown_, methodName_=None, bWarn_=False)
                    if _cbif is None:
                        _failedCbParamName = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XRCTAgent_CB_PARAM_NAME_003)
                        break
                    _xcb = _XCallback(_EXCallbackID.eTeardown, _cbif, bGenericParam_)
                    _lstXCb.append(_xcb)
                if cbProcExtMsg_ is not None:
                    _cbif = _FwCallable.CreateInstance(cbProcExtMsg_, methodName_=None, bWarn_=False)
                    if _cbif is None:
                        _failedCbParamName = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XRCTAgent_CB_PARAM_NAME_004)
                        break
                    _xcb = _XCallback(_EXCallbackID.eProcExtMsg, _cbif, bGenericParam_)
                    _lstXCb.append(_xcb)
                if cbProcIntMsg_ is not None:
                    _cbif = _FwCallable.CreateInstance(cbProcIntMsg_, methodName_=None, bWarn_=False)
                    if _cbif is None:
                        _failedCbParamName = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XRCTAgent_CB_PARAM_NAME_005)
                        break
                    _xcb = _XCallback(_EXCallbackID.eProcIntMsg, _cbif, bGenericParam_)
                    _lstXCb.append(_xcb)
            break

        if len(_lstXCb) < 1:
            if _failedCbParamName is not None:
                _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XCbCase_TID_006).format(rctClassName_, _failedCbParamName)
                logif._XLogErrorEC(_EFwErrorCode.UE_00220, _msg)
            else:
                _midPart = [ _EFwTextID.eLogMsg_XRCTAgent_CB_NAME_RUN
                           , _EFwTextID.eLogMsg_XRCTAgent_CB_NAME_SETUP
                           , _EFwTextID.eLogMsg_XRCTAgent_CB_NAME_TEARDOWN
                           , _EFwTextID.eEUTaskApiID_ProcessExternalMessage
                           ]
                if bIQueueEnabled_:
                    _midPart.append(_EFwTextID.eEUTaskApiID_ProcessIntternalMessage)
                _midPart = [ _FwTDbEngine.GetText(ee) for ee in _midPart ]
                _midPart = _CommonDefines._CHAR_SIGN_SPACE.join(_midPart)
                _failedCbParamName = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XRCTAgent_CB_PARAM_NAME_006)
                _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XCbCase_TID_016).format(rctClassName_, _failedCbParamName, _midPart)
                logif._XLogErrorEC(_EFwErrorCode.UE_00230, _msg)
            return

        self.__a = _lstXCb
        self.__i = _phxfInst

        _lstIfSrc = []
        for ee in _lstXCb:
            if ee._callbackFunction in _lstIfSrc:
                self.__a = None
                self.__i = None

                _cbName = ee.callbackName
                if ee.ifSpecType.isSpecifiedByCallableInstance:
                    _cbName = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_029).format(ee.ifsoruce.__class__.__name__, _cbName)
                _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XCbCase_TID_011).format(rctClassName_, _cbName)
                logif._XLogErrorEC(_EFwErrorCode.UE_00226, _msg)
                break

            _lstIfSrc.append(ee._callbackFunction)

        if self.__a is not None:
            for ee in _lstXCb:
                if not ee.CheckCallbackSignature(rctClassName_):
                    self.__a = None
                    self.__i = None
                    break

        if self.__a is None:
            for ee in _lstXCb:
                ee.CleanUp()
            _lstXCb.clear()
            return

        _bRunCB        = self.runCallback is not None
        _bProcExtMsgCB = self.procExtMsgCallback is not None
        _bProcIntMsgCB = self.procIntMsgCallback is not None

        if bMsgCase_:
            if _bProcIntMsgCB and not bIQueueEnabled_:
                _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XCbCase_TID_008).format(rctClassName_, self.procIntMsgCallback.callbackName)
                logif._XLogErrorEC(_EFwErrorCode.UE_00221, _msg)
                self.CleanUp()
                return

            if not (_bProcExtMsgCB or _bProcIntMsgCB):
                _midPart = [_EFwTextID.eLogMsg_XRCTAgent_CB_PARAM_NAME_004, _EFwTextID.eLogMsg_XRCTAgent_CB_PARAM_NAME_006]
                if bIQueueEnabled_:
                    _midPart.insert(0, _EFwTextID.eLogMsg_XRCTAgent_CB_PARAM_NAME_003)
                _midPart = [_FwTDbEngine.GetText(ee) for ee in _midPart]
                _midPart = _CommonDefines._CHAR_SIGN_SPACE.join(_midPart)
                _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XCbCase_TID_019).format(rctClassName_, _midPart)
                logif._XLogErrorEC(_EFwErrorCode.UE_00233, _msg)
                self.CleanUp()
                return

            if bBlockingExtQ_:
                if not _bProcExtMsgCB:
                    _midPart = [_EFwTextID.eLogMsg_XRCTAgent_CB_PARAM_NAME_004 , _EFwTextID.eLogMsg_XRCTAgent_CB_PARAM_NAME_006]
                    _midPart = [_FwTDbEngine.GetText(ee) for ee in _midPart]
                    _midPart = _CommonDefines._CHAR_SIGN_SPACE.join(_midPart)
                    _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XCbCase_TID_009).format(rctClassName_, _midPart)
                    logif._XLogErrorEC(_EFwErrorCode.UE_00222, _msg)
                    self.CleanUp()
                    return
                elif _bRunCB:
                    _midPart = [ self.runCallback.callbackName, self.procExtMsgCallback.callbackName ]
                    _midPart = _CommonDefines._CHAR_SIGN_SPACE.join(_midPart)
                    _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XCbCase_TID_010).format(rctClassName_, _midPart)
                    logif._XLogErrorEC(_EFwErrorCode.UE_00223, _msg)
                    self.CleanUp()
                    return

        else:
            if _bProcExtMsgCB or _bProcIntMsgCB:
                _midPart = []
                if _bProcExtMsgCB:
                    _midPart.append(self.procExtMsgCallback.callbackName)
                if _bProcIntMsgCB:
                    _midPart.append(self.procIntMsgCallback.callbackName)
                _midPart = _CommonDefines._CHAR_SIGN_SPACE.join(_midPart)
                _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XCbCase_TID_003).format(rctClassName_, _midPart)
                logif._XLogErrorEC(_EFwErrorCode.UE_00234, _msg)
                self.CleanUp()
                return

        if not (bMsgCase_ and bBlockingExtQ_):
            if not _bRunCB:
                _midPart = [_EFwTextID.eLogMsg_XRCTAgent_CB_PARAM_NAME_004, _EFwTextID.eLogMsg_XRCTAgent_CB_PARAM_NAME_006]
                _midPart = [_FwTDbEngine.GetText(ee) for ee in _midPart]
                _midPart = _CommonDefines._CHAR_SIGN_SPACE.join(_midPart)
                _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XCbCase_TID_017).format(rctClassName_, _midPart)
                logif._XLogErrorEC(_EFwErrorCode.UE_00231, _msg)
                self.CleanUp()
                return

    def __str__(self):
        return self._ToString()

    @property
    def isValid(self):
        return self.__a is not None

    @property
    def isGeneric(self):
        return False if self.__isInvalid else self.__a[0].isGeneric

    @property
    def numCallbacks(self):
        return 0 if self.__isInvalid else len(self.__a)

    @property
    def runCallback(self):
        return self.__GetCallback(_EXCallbackID.eRun)

    @property
    def setupCallback(self):
        return self.__GetCallback(_EXCallbackID.eSetup)

    @property
    def teardownCallback(self):
        return self.__GetCallback(_EXCallbackID.eTeardown)

    @property
    def procExtMsgCallback(self):
        return self.__GetCallback(_EXCallbackID.eProcExtMsg)

    @property
    def procIntMsgCallback(self):
        return self.__GetCallback(_EXCallbackID.eProcIntMsg)

    @property
    def phasedXFInst(self):
        return self.__i

    def _ToString(self):
        if self.__isInvalid:
            return None
        _midPart = [ str(ee) for ee in self.__a ]
        _midPart = _CommonDefines._STR_EMPTY.join(_midPart)
        return _FwTDbEngine.GetText(_EFwTextID.eXCbCase_ToString_001).format(str(self.isGeneric), self.numCallbacks, _midPart)

    def _CleanUp(self):
        if self.__a is not None:
            for ee in self.__a:
                ee.CleanUp()
            self.__a.clear()
            self.__a = None
        self.__i = None

    @staticmethod
    def __IsDefaultCallback(callback_):
        return (callback_ is not None) and callback_.__qualname__.split(_CommonDefines._CHAR_SIGN_DOT)[0] in _XCbCase.__lstBaseClassNames

    @staticmethod
    def __CheckOnRedundancy( rctClassName_ : str
                           , cbRun_        =None
                           , cbSetup_      =None
                           , cbTeardown_   =None
                           , cbProcExtMsg_ =None
                           , cbProcIntMsg_ =None
                           , cbPhXFInst_   =None
                           , bWarnOnly_    =False):
        _ERR_RET = True, None, None, None, None, None, None

        _lstCB = [cbRun_, cbSetup_, cbTeardown_, cbProcExtMsg_, cbProcIntMsg_, cbPhXFInst_]
        _lstCB = [ee for ee in _lstCB if ee is not None]
        if len(_lstCB) < 1:
            _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XCbCase_TID_001).format(rctClassName_)
            logif._XLogErrorEC(_EFwErrorCode.UE_00229, _msg)
            return _ERR_RET

        if cbPhXFInst_ is not None:
            _lstCB = [cbRun_, cbSetup_, cbTeardown_, cbProcExtMsg_, cbProcIntMsg_]
            _lstNonNone = [ee for ee in _lstCB if ee is not None]
            if len(_lstNonNone):
                _midPart2 = []
                if cbRun_        is not None: _midPart2.append(_EFwTextID.eLogMsg_XRCTAgent_CB_PARAM_NAME_001)
                if cbSetup_      is not None: _midPart2.append(_EFwTextID.eLogMsg_XRCTAgent_CB_PARAM_NAME_002)
                if cbTeardown_   is not None: _midPart2.append(_EFwTextID.eLogMsg_XRCTAgent_CB_PARAM_NAME_003)
                if cbProcExtMsg_ is not None: _midPart2.append(_EFwTextID.eLogMsg_XRCTAgent_CB_PARAM_NAME_004)
                if cbProcIntMsg_ is not None: _midPart2.append(_EFwTextID.eLogMsg_XRCTAgent_CB_PARAM_NAME_005)
                _midPart2 = [_FwTDbEngine.GetText(ee) for ee in _midPart2]
                _midPart2 = _CommonDefines._CHAR_SIGN_SPACE.join(_midPart2)
                _midPart  = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XRCTAgent_CB_PARAM_NAME_006)

                if bWarnOnly_:
                    _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XCbCase_TID_002).format(rctClassName_, _midPart, _midPart2)
                    logif._XLogWarning(_msg)
                    cbRun_, cbSetup_, cbTeardown_, cbProcExtMsg_, cbProcIntMsg_ = None, None, None, None, None
                else:
                    _msg = _FwTDbEngine.GetText(_EFwTextID.eLogMsg_XCbCase_TID_005).format(rctClassName_, _midPart, _midPart2)
                    logif._XLogErrorEC(_EFwErrorCode.UE_00219, _msg)
                    return _ERR_RET

        return False, cbRun_, cbSetup_, cbTeardown_, cbProcExtMsg_, cbProcIntMsg_, cbPhXFInst_

    @property
    def __isInvalid(self):
        return self.__a is None

    def __GetCallback(self, id_ : _EXCallbackID) -> _XCallback:
        if self.__isInvalid:
            return None
        if not isinstance(id_, _EXCallbackID):
            vlogif._LogOEC(True, _EFwErrorCode.VFE_00566)
            return None

        res = None
        for _xcb in self.__a:
            if _xcb.callbackID == id_:
                res = _xcb
                break
        return res
