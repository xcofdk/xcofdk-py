# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xpayload.py
#
# Copyright(c) 2024 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from xcofdk.fwcom                 import override
from xcofdk.fwapi.xmsg.xpayloadif import XPayloadIF

from xcofdk._xcofw.fw.fwssys.fwmsg.msg import _FwPayload


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class XPayload(XPayloadIF):
    """
    This class is the default implementation of the interface class XPayloadIF.

    The subsystem of messaging uses this class whenever default payload objects
    are needed. It implements below groups of interface functions of its parent
    class:
        - mandatory API
        - general API

    That is, it represents the usual funtionality expected from a typical
    container type. In addition, it provides a few supplementary API functions
    commonly expected from a collection-like payload object. Instances of this
    class are constructed according to the design patterns Adapter or Facade,
    too.

    See:
    -----
        - XPayloadIF
        - XMessage
        - XMessageManager
    """


    __slots__ = [ '__p' ]


    def __init__(self, containerInitializer_ : dict =None, bBypassSerDes_ =False):
        """
        Constructor (initializer) of an instance of this class.

        Parameters:
        -------------
            - containerInitializer_ :
              a built-in container object (if any) used as initializer of the
              internal container of this instance.
            - bBypassSerDes_ :
              specifies the desired return value of the getter property below
              of this instance:
                  self.isMarshalingRequired

              If set to False (the default), then marshaling of this instance
              will behave as usual. Otherwise, SerDes will not take place while
              transmission of the message object(s) this instance is associated
              to. In other words, SerDes is bypassed at both endpoints of the
              respective transmission path.

        See:
        -----
            - XMessage.msgPayload
            - XPayloadIF
            - XPayload.isMarshalingRequired
        """
        super().__init__()

        self.__p = _FwPayload(cont_=containerInitializer_, bSkipSerDes_=bBypassSerDes_)
        if not self.__p.isValidPayload:
            self.__p.CleanUp()
            self.__p = None


    # --------------------------------------------------------------------------
    # Interface inherited from XPayloadIF
    # --------------------------------------------------------------------------
    @staticmethod
    def CustomSerializePayload(payload_) -> bytes:
        """
        Custom serialization is not supported by this class.

        See:
        -----
            - XPayloadIF.SerializePayload()
        """
        return None


    @staticmethod
    def CustomDeserializePayload(dump_: bytes):
        """
        Custom de-serialization is not supported by this class.

        See:
        -----
            - XPayloadIF.DeserializePayload()
        """
        return None


    @XPayloadIF.isValidPayload.getter
    def isValidPayload(self) -> bool:
        """
        See:
        -----
            - XPayloadIF.isValidPayload
        """
        return self.__p is not None


    @XPayloadIF.isMarshalingRequired.getter
    def isMarshalingRequired(self):
        """
        See:
        -----
            - XPayload.__init__()
            - XPayloadIF.isMarshalingRequired
        """
        return (self.__p is not None) and self.__p.isMarshalingRequired


    @XPayloadIF.isCustomMarshalingRequired.getter
    def isCustomMarshalingRequired(self):
        """
        Custom marshaling is not supported by this class.

        See:
        -----
            - XPayloadIF.isCustomMarshalingRequired
        """
        return False


    @XPayloadIF.numParameters.getter
    def numParameters(self) -> int:
        """
        See:
        -----
            - XPayloadIF.numParameters
            - XPayload.SetParameter()
            - XPayload.UpdatePayloadContainer()
        """
        return 0 if not self.isValidPayload else self.__p.numParameters


    @override
    def IsIncludingParameter(self, paramKey_) -> bool:
        """
        See:
        -----
            - XPayloadIF.IsIncludingParameter()
            - XPayload.SetParameter()
            - XPayload.UpdatePayloadContainer()
        """
        return False if not self.isValidPayload else self.__p.IsIncludingParameter(paramKey_)


    @override
    def GetParameter(self, paramKey_):
        """
        See:
        -----
            - XPayloadIF.GetParameter()
            - XPayload.SetParameter()
            - XPayload.UpdatePayloadContainer()
        """
        return None if not self.isValidPayload else self.__p.GetParameter(paramKey_)


    @override
    def DetachContainer(self) -> dict:
        """
        See:
        -----
            - XPayloadIF.DetachContainer()
        """
        if self.__p is None:
            return None

        res = self.__p.DetachContainer()
        self.__p.CleanUp()
        self.__p = None
        return res
    # --------------------------------------------------------------------------
    #END Interface inherited from XPayloadIF
    # --------------------------------------------------------------------------


    # --------------------------------------------------------------------------
    # supplementary API
    # --------------------------------------------------------------------------
    @property
    def payloadContainer(self) -> dict:
        """
        Getter property to get access to the underlying container.

        This property is provided for convenient as it enables direct
        manipulation of the underlying container right after instantiation.

        Returns:
        ----------
            the underlying container object of this instance if valid, None
            otherwise.

        See:
        -----
            - XPayload.isValidPayload
            - XPayload.__init__()
            - XPayload.UpdatePayloadContainer()
        """
        return None if not self.isValidPayload else self.__p.container


    def SetParameter(self, paramKey_, paramValue_) -> bool:
        """
        Add or update a parameter.

        Managed data items are stored by the usual key-value principle of
        collection types.

        Parameters:
        -------------
            - paramKey_ :
              key of the parameter to be added (or updated).
            - paramValue_ :
              value of (or reference to) the parameter to be added or updated.

        Returns:
        ----------
            True if the operation succeeds, False otherwise.

        See:
        -----
            - XPayload.isValidPayload
            - XPayload.GetParameter()
            - XPayload.IsIncludingParameter()
            - XPayload.UpdatePayloadContainer()
        """
        if not self.isValidPayload:
            return False
        return self.__p.AddParameter(paramKey_, paramValue_)


    def UpdatePayloadContainer(self, dictParams_: dict, bShallowCopy_ =True) -> bool:
        """
        Add or update a bunch of parameters.

        Managed data items are stored by the usual key-value principle of
        collection types.

        Parameters:
        -------------
            - dictParams_ :
              collection object containing parameters to be added (or updated).
            - bShallowCopy_ :
              if True then the built-in 'copy' operation of mutable collection
              types will be applied to the passed in collection object before
              actual update of the underlying container object takes place.

        Returns:
        ----------
            True if the operation succeeds, False otherwise.

        See:
        -----
            - XPayload.isValidPayload
            - XPayload.SetParameter()
            - XPayload.GetParameter()
            - XPayload.IsIncludingParameter()
        """
        if not self.isValidPayload:
            return False
        return self.__p.UpdateContainer(dictParams_, bShallowCopy_=bShallowCopy_)
    # --------------------------------------------------------------------------
    # supplementary API
    # --------------------------------------------------------------------------
#END class XPayload
