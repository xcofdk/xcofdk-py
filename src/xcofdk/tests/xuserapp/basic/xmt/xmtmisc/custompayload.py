# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : custompayload.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from xcofdk.fwcom import override
from xcofdk.fwapi import IPayload


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class CustomPayload(IPayload):
    """
    This custom payload class does not use any internal container.

    Instead, it just maintains member variables to implement its own, custom
    API.
    """


    __slots__ = [ '__bSer' , '__cntRcv' , '__cntSnd' , '__cntErr' , '__cntOutOfOrder' ]

    def __init__(self, cntRcv_ : int, cntSnd_ : int, cntErr_ : int, cntOutOfOrder_ : int, bSkipSer_ =False):
        super().__init__()
        self.__bSer          = not bSkipSer_
        self.__cntRcv        = cntRcv_
        self.__cntSnd        = cntSnd_
        self.__cntErr        = cntErr_
        self.__cntOutOfOrder = cntOutOfOrder_


    # --------------------------------------------------------------------------
    # custom API
    # --------------------------------------------------------------------------
    @property
    def countReceived(self):
        return self.__cntRcv

    @property
    def countSent(self):
        return self.__cntSnd

    @property
    def countFailure(self):
        return self.__cntErr

    @property
    def countOutOfOrder(self):
        return self.__cntOutOfOrder
    # --------------------------------------------------------------------------
    #END custom API
    # --------------------------------------------------------------------------


    # --------------------------------------------------------------------------
    # API inherited from IPayload
    # --------------------------------------------------------------------------
    @IPayload.isValidPayload.getter
    def isValidPayload(self) -> bool:
        return self.__bSer is not None

    @IPayload.isMarshalingRequired.getter
    def isMarshalingRequired(self) -> bool:
        return self.__bSer

    @IPayload.isCustomMarshalingRequired.getter
    def isCustomMarshalingRequired(self):
        return False

    @IPayload.numParameters.getter
    def numParameters(self) -> int:
        return 0

    @override
    def IsIncludingParameter(self, paramkey_) -> bool:
        return False

    @override
    def GetParameter(self, paramkey_):
        return None

    @override
    def DetachContainer(self):
        return None
    # --------------------------------------------------------------------------
    #END API inherited from IPayload
    # --------------------------------------------------------------------------
#END class CustomPayload
