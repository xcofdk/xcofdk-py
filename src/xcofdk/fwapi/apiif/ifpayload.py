# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xpayloadif.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from typing import Union

# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class IPayload:
    """
    Interface class representing the base object type of instances associated
    to message objects as their payload (if any).

    Also, applications may use it for sub-classing purposes enabling them for
    providing custom payload objects.

    Conceptually, payload objects tend to be a somehow organized container
    carrying data entities. But, this is not necessarily always true. They are
    simply arbitrary data structures assembled according to application
    specific, individual requirements.

    From point of view of derived classes sub-classing this class, three
    different groups of interface functions are given each of them serving for
    a specific purpose:
        - mandatory API:
          interface properties/methods to be implemented by the derived classes.

        - general API:
          basic interface properties/methods to be implemented by derived
          classes if it is supposed to represent the usual funtionality expected
          from a container type maintaining data on commonly known key-value
          mechanism. Data items managed/maintained by the container are generall
          referred to as 'parameters'.

          Note that derived classes are free to just ignore this group if they
          wish to replace it with their own data structure organization as
          indicated above.

        - SerDes API
          interface properties/methods related to (de-)serialization. Derived
          classes can override them to bypass and/or costomize SerDes.

    See:
    -----
        - XMessage
        - XMessenger


    Deprecated API:
    ----------------
    Starting with XCOFDK-py v3.0 below API entities are deprecated and not
    available anymore:
        >>> # former name of this class due to renaming
        >>> XPayloadIF = IPayload
    """

    __slots__ = []

    def __init__(self):
        pass

    # ------------------------------------------------------------------------------
    # mandatory API
    # ------------------------------------------------------------------------------
    @property
    def isValidPayload(self) -> bool:
        """
        Returns:
        ----------
            True if this instance is a valid payload object, False otherwise.
        """
        pass
    # ------------------------------------------------------------------------------
    #END mandatory API
    # ------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # container API
    # ------------------------------------------------------------------------------
    @property
    def numParameters(self) -> int:
        """
        Returns:
        ----------
            Non-negative number of data entities carried by this instance.
        """
        pass


    def IsIncludingParameter(self, paramKey_) -> bool:
        """
        Check for inclusion of a given parameter.

        Parameters:
        -------------
            - paramKey_ :
              an object serving as the unique key/identifier of the parameter
              to be checked for.

        Returns:
        ----------
            True if this instance carries a given parameter, False otherwise.

        See:
        -----
            >>> IPayload.GetParameter()
        """
        pass


    def GetParameter(self, paramKey_):
        """
        Fetch a given parameter carried by this instance.

        Parameters:
        -------------
            - paramKey_ :
              an object serving as the unique key/identifier of the parameter
              to be fetched.

        Returns:
        ----------
            the parameter specified by the passed in key if carried by this
            instance, None otherwise.

        Note:
        ------
            - The returned value is basically implementation specific. This way
              even 'None' might be a valid, contained paraemeter. In such cases
              check for inclusion in advance might may prevent disambiguation.

        See:
        -----
            >>> IPayload.IsIncludingParameter()
        """
        pass


    def DetachContainer(self) -> Union[dict, None]:
        """
        Request to detach the underlying container (if any) of this instance.

        Note:
        ------
            - This method is basically implementation specific. It is supposed
              to serve as a cleanup routine (if needed).
        """
        pass
    # ------------------------------------------------------------------------------
    #END container API
    # ------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # SerDes API
    # ------------------------------------------------------------------------------
    @property
    def isMarshalingRequired(self) -> bool:
        """
        Getter property stating whether marshaling of this instance is expected.

        Returns:
        ----------
            True if marshaling of this instance (while transmission of the
            associated message object) is required, False otherwise.

        Note:
        ------
            - More detail available in section 'SerDes' of class description
              of XMessenger.

        See:
        -----
            >>> IPayload.isCustomMarshalingRequired
        """

        # marshaling is required by default
        return True


    @property
    def isCustomMarshalingRequired(self):
        """
        Getter property stating whether custom marshaling of this instance is
        expected.

        Returns:
        ----------
            True if custom marshaling of this instance (while transmission of
            the associated message object) is required, False otherwise.

        Note:
        ------
            - Custom serialization property of instances configured to not
              requesting for marshaling at all is ignored.

        See:
        -----
            >>> IPayload.isMarshalingRequired
            >>> IPayload.SerializePayload()
            >>> IPayload.DeserializePayload()
        """

        # custom marshaling is not required by default
        return False


    @classmethod
    def SerializePayload(cls, payload_) -> bytes:
        """
        Class method for application-specific serialization of this instance.

        Parameters:
        -------------
            - payload_ :
              an instance of this class to be serialized.

        Returns:
        ----------
            byte stream of the passed in instance of this class.

        Note:
        ------
            - Derived classes must provide the implementation of the public
              static method 'CustomSerializePayload()'.

        See:
        -----
            >>> IPayload.isCustomMarshalingRequired
            >>> IPayload.DeserializePayload()
        """
        return cls.CustomSerializePayload(payload_)


    @classmethod
    def DeserializePayload(cls, dump_ : bytes):
        """
        Class method for application-specific de-serialization of this instance.

        Parameters:
        -------------
            - dump_ :
              byte stream of an instance of this class to be de-serialized.

        Returns:
        ----------
            an instance of this class represented by its byte stream passed in.

        Note:
        ------
            - Derived classes must provide the implementation of the public
              static method 'CustomDeserializePayload()'.
            - More detail available in section 'SerDes' of class description
              of XMessenger.

        See:
        -----
            - XMessage.msgPayload
            - IPayload.isCustomMarshalingRequired
            - IPayload.SerializePayload()
        """
        return cls.CustomDeserializePayload(dump_)
    # ------------------------------------------------------------------------------
    #END SerDes API
    # ------------------------------------------------------------------------------
#END class IPayload
