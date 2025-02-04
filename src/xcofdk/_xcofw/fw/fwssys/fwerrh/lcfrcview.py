# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : lcfrcview.py
#
# Copyright(c) 2024 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from xcofdk._xcofw.fw.fwssys.fwcore.logging.logdefines import _EErrorImpact
from xcofdk._xcofw.fw.fwssys.fwcore.logging.logdefines import _LogErrorCode
from xcofdk._xcofw.fw.fwssys.fwcore.lc.lcdefines       import _ELcCompID
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes  import _CommonDefines
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes  import _EColorCode
from xcofdk._xcofw.fw.fwssys.fwcore.types.commontypes  import _TextStyle

from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _EFwTextID
from xcofdk._xcofw.fw.fwtdb.fwtdbengine import _FwTDbEngine

class _LcFrcView:

    __slots__ = [ '__eCID' , '__feClone' , '__bFFE' , '__bRTT' , '__thrdID' , '__thrdName' , '__errImp' ]

    def __init__( self, *, eCID_ : _ELcCompID, ferr_, bFFE_ : bool, bRTT_ : bool, thrdName_ : str, thrdID_ : int):
        self.__bFFE     = bFFE_
        self.__bRTT     = bRTT_
        self.__eCID     = eCID_
        self.__errImp   = None
        self.__thrdID   = thrdID_
        self.__feClone  = ferr_
        self.__thrdName = thrdName_

        if (ferr_ is not None) and not ferr_.isClone:
            ferr_ = None

        if ferr_ is not None:
            _errImp = ferr_.eErrorImpact
            if _errImp is None:
                pass
            elif not _errImp.hasImpact:
                pass
            elif not _errImp.isCausedByFatalError:
                pass
            else:
                self.__errImp = _errImp

        if self.__errImp is None:
            self.CleanUp()

    def __str__(self):
        return self.ToString()

    @property
    def isValid(self):
        return not self._isInvalid

    @property
    def isReportedByPyThread(self):
        return self.__bRTT is None

    @property
    def isReportedByFwTask(self):
        return self.__bRTT is not None and self.__bRTT

    @property
    def isReportedByFwThread(self):
        return self.__bRTT is not None and not self.__bRTT

    @property
    def taskID(self):
        return None if self._isInvalid else self.__feClone.taskID

    @property
    def taskName(self):
        return None if self._isInvalid else self.__feClone.taskName

    @property
    def threadID(self):
        return self.__thrdID

    @property
    def threadName(self):
        return self.__thrdName

    @property
    def errorCode(self):
        return None if self._isInvalid else self.__feClone.errorCode

    @property
    def eLcCompID(self) -> _ELcCompID:
        return self.__eCID

    @property
    def eErrorImpact(self) -> _EErrorImpact:
        return self.__errImp

    def ToString(self, bVerbose_ =True) -> str:
        if self._isInvalid:
            return None

        _tid = self.taskID
        if _tid is None:
            _tid = self.__thrdID
        _tname = self.taskName
        if _tname is None:
            _tid = self.__thrdName

        res = self.__feClone.errorCode
        if not (isinstance(res, int) and res != _LogErrorCode.GetAnonymousErrorCode()):
            res = _CommonDefines._CHAR_SIGN_DASH

        _uname = _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_011).format(_tname, _tid)

        res = _FwTDbEngine.GetText(_EFwTextID.eLcFrcView_ToString_01).format(self.__feClone.uniqueID, self.__eCID.compactName, res, _uname)

        if not bVerbose_:
            res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_016).format(self.__feClone.shortMessage)
        else:
            res += _FwTDbEngine.GetText(_EFwTextID.eMisc_Shared_FmtStr_012).format(self.__feClone)
        res = _TextStyle.ColorText(res, _EColorCode.RED)
        return res

    def CleanUp(self):
        if self.__feClone is not None:
            self.__feClone.CleanUp()

        self.__bFFE     = None
        self.__bRTT     = None
        self.__eCID     = None
        self.__errImp   = None
        self.__thrdID   = None
        self.__feClone  = None
        self.__thrdName = None

    @property
    def _isInvalid(self):
        return self.__errImp is None

    @property
    def _isFFE(self):
        return False if self.__bFFE is None else self.__bFFE

    @property
    def _feClone(self):
        return self.__feClone

