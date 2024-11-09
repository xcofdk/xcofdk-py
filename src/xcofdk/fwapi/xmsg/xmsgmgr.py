# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : xmsgmgr.py
#
# Copyright(c) 2024 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from typing import Union

from xcofdk.fwcom.xmsgdefs import IntEnum
from xcofdk.fwcom.xmsgdefs import EPreDefinedMessagingID

from xcofdk.fwapi.xtask.xtask     import XTask
from xcofdk.fwapi.xmsg.xpayloadif import XPayloadIF

from xcofdk._xcofw.fw.fwssys.fwmsg.apiimpl.xcomsgmgrimpl import _XMsgMgrImpl


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class XMessageManager:
    """
    This class represents the high-level abstraction of the messaging subsystem
    of the framework by providing a collection of public, static interface
    methods serving as the single starting point for all operations needed for
    communication via messages.

    Sections below explain terms, definitions and concepts related to the
    messaging subsystem of the framework.


    Messaging:
    ------------
    (or communication) refers to the mechanism(s) programmatically implemented
    to make the exchange of some data entity can be accomplished.

    Common, major use cases for messaging are task communication within a
    program as well as remote communication, that is inter-process and network
    communication (via incoming/outgoing messages).

    Remote communication is not supported yet, but conceptually it is quite
    similar to task communication. Hence, once released, its respective API and
    high-level abstraction will work almost the same way with no need for any
    substantial reconversion.


    Message delivery policies:
    ----------------------------
    with regard to the chosen delivery mechanism, there are different delivery
    policies each aiming for certain requirements. Framework's subsystem of
    messaging (partly) uses below three mechanisms:
        - queued delivery:
          default policy by design and supported by the framework.

          Even though this method by definition implies 'time-shifted
          processing', it ensures one of the topmost requirements of the
          framework, namely its principle of 'processing by ownership' meaning
          almost the complete procedure of a given communication path takes
          place within the exceution context of the involved communication
          partners themselves. The sender initiates the procedure in its own
          excution context, the receiver(s), too, process delivered messages in
          their own execution context.

        - synchronous forwarding via callback:
          not supported as a commonly available delivery policy, mainly due to
          its inherent affinity for potential deadlocks.

          However, there are inevitable, rare use cases causing the framework
          to apply this type of delivery. Wherever applicable the documentation
          will explicitly address the related issue.

        - priority-based delivery:
          not supported, basically because it is not considered by the framework
          general-purpose enough on one hand. It would also significantly
          increase the complexity of both the interface and its detailed design
          (or implementation) on the other hand.

          Nevertheless, future versions of the framework may have to introduce
          this delivery policy at least in a limited scope and for special
          purposes provided that related, new features of the framework require
          it to be available.

    It is worth mentioning that an outgoing message may address any possible
    receiver submitted to an arbitrary, local delivery policy not known to the
    framework. In all other cases both source and destination(s) of a message
    are required to have their own message queues as prerequisite for queued
    delivery explained above (queue configuration of tasks is explained in
    class description of XTask, sections 'Execution frame 3-PhXF' and
    'Configuration').


    Delivery retry mechanism:
    ----------------------------
    refers to the provisions related to the handling of the commonly known issue
    of 'pending' messages, that is messages which couldn't be delivered to their
    destination for whatever reason.

    Given a pending message, the default approach of the messaging subsystem can
    be outlined as a sequence of below steps:
        s1) if an internal message, do not apply any retry mechanism, so that
            the message simply get lost, otherwise:
        s2) try to deliver up to a fix number of retry attempts (including the
            initial one). The default is 3,
        s3) no need for further provisions if s1) was successful.
        s4) otherwise, drop that pending message and consider the addressee
            as potentially irresponsive,
        s5) apply no more retry for subsequent messages to be delivered to that
            addressee if s4) happens a fix number of cosecutive times. The
            default is 3.
        s6) as soon as a successful delivery takes place, re-establish the
            normal retry mechanism for the addressee.

    In other words, a destination for which the subsystem fails to deliver
    messages to for 9 consucutive times will be permanently considered
    irresponsive. It will try to deliver subsequent messages to such a
    destination in a hope-for-the-best manner, that is only once, and the first
    the such a delivery was successful, will make the subsystem that the defatul
    retry mechanism for that destination is restored again.


    Endpoints:
    -----------
    being a generic term, it refers to both source and destination of a
    communication, that is the sender (often indicated as 'Tx', i.e. transmitter
    who initiates a given data exchange) and one or more receivers (often
    indicated as 'Rx').

    Unless otherwise stated, an endpoint is always a (logical) unique, possibly
    dynamically constructed identifier which in turn uniquely specifies one or
    more communicaiton partners.

    Note also that while on sender side the involved endpoints are specified by
    their respective unique identifiers, additional attributes of the data to be
    exchanged might be necessary and used on receiver side to pinpoint source
    and/or destination endpoints.


    Addressing policy:
    --------------------
    except for the case of specific, user-defned data to be exchanged (if any),
    the spcification of the destination endpoint(s), that is the addressing, is
    all information a sender has to provide to initiate the process of exchange.

    There are three major addressing policies supported by the framework:
        - direct addressing:
          used whenever the destination endpoint is known. Such a communication
          is basically a 1-to-1 tranmission. However, endpoints may dynamically
          register for specific communication paths, so that the data exchange
          initiated by the source may rather result in a 1-to-n tranmission.

          Note also that direct messaging requires tasks to be specified by
          their unique task ID.

        - (generic) anonymous addressing:
          used whenever the destination endpoint is unknown to the sending
          endpoint, or if more than one single receiver shall be involved, or
          whenever the actual receiver(s) have to be identified by the subsystem
          based on otherwise available informationm (see subsection
          'Dispatch filter' below). In general, anonymous addressing results in
          a 1-to-n transmission.

        - alias addressing:
          refers to the special use case of the generic anonymous addressing
          via pre-defined identifiers expected to be self-explaining, e.g.:

          EPreDefinedMessagingID.MainTask:
          used whenever the main task, i.e. the singleton of class MainXTask,
          is the receiver/sender endpoint,

          EPreDefinedMessagingID.Broadcast:
          used whenever the subsystem is requested to deliver a message to all
          currently available receiver endpoints.

    Note that the abovementioned 1-to-n transmission may be understood as a
    special use case of the messaging to make kind of automated 'fire-notify'
    mechanism available to application. However, endpoints may be given the
    opportunity to declare their communication as 'private conversation' either
    on a per-transmission basis, or permanently via corresponding configuration.


    Dispatch filter:
    -----------------
    refers to the additional information needed for generic anonymous addressing
    described above. Basically, dispatch filters are 'wildcard' specification
    of (sender/receiver) endpoints. Althoug they are designed to be applicabel
    to both remote and task communications, the explanations here will focus on
    the latter type for simplicity.

    When sending a message, the parameters passed to the respective interface
    function (partly) represent a dispatch filter implicitly used by the
    subsystem to identify all available receiver tasks, even if direct or alias
    addressing was used by the sender to specify the receiver task(s).

    Application tasks may dynamically register or de-register their own dispatch
    filters making subsystem's delivery procedure customizable.

    When dealing with dispatch filters, the special 'dont-care' (meaning 'any')
    identifier provides the utmost flexibility:
        - EPreDefinedMessagingID.DontCare

    With regard to their data structure a dispatch filter consists of below
    attributes each initialized as 'dont-care' by default:
        - receiver ID:
          Rx identifier acc. to direct or alias addressing (if specified).

        - sender ID:
          Tx identifier acc. to direct or alias addressing (if specified).

        - label ID:
          pre- or user-defined identifier used as the 1st-level classification
          of a family of messages expressing (a specific) kind of relationship.

          Typicall examples for message labels could be something like either
          one of below user-defined IDs:
              LABEL_ID_JOB_REQUEST
              LABEL_ID_JOB_STATE
              LABEL_ID_JOB_REPLY

        - cluster ID:
          pre- or user-defined identifier used as the 2nd-level classification
          of a family of message labels expressing (a specific) kind of
          membership. In other words, a message cluster simply represents a
          convenient way for specifying a collection of somehow related message
          labels.

          An example for such a cluster could be the user-defined ID below
          having the exemplary message labels above as members:
              CLUSTER_ID_JOB_HANDLING

    Note also that regardless their use in dispatch filters, message label
    and/or cluster are useful methods to make application code (responsible for
    message handling, especially on receiver side) can organize the code by
    proper conditional branching more efficiently.

    Finally, message labels or message clusters must be a unique identifiers
    with an application may use the same lable/cluster for different purposes or
    in different contexts. Therefore, their classification as 1st- or 2nd-level
    is rather a matter of taste. The framework, however, prefers to refer to
    message labels as 1st-level classification as the same lable might be member
    of different message clusters at the same time.


    Message:
    ----------
    refers to a pre-defined, customizable data structure to be exchanged between
    endpoints. In other words, a message object is the smallest data entity
    supported by the subsystem of messaging for data exchange.

    Note that framework's messaging is neither designed for nor it does cover
    the otherwise known domain of 'signaling' via signals or events. Unless
    strict timing behavior is required, however, messaging may be considered an
    adequate alternative to achieve same purpose.

    Main attributes of the data structure representing a message object are
    as listed below with the first two items composing the fix portion always
    available for a given message:
        - unique ID of the message
        - message header (including sender ID, receiver ID etc.)
        - message payload (optional, see below)


    Payload:
    ---------
    refers to an optional data container which carries user-defined data known
    to both sender and receiver by some pre-agreed contract.

    In other words, message payload is the key feature available to applications
    to make their messaging customizable with below two options available for:
        - class XPayload:
          default payload implementation,

        - interface XPayloadIF:
          interface class used for sub-classing, i.e. custom marshaling.


    SerDes:
    --------
    (or serialization or marshaling or pickling to put it pythonic) refers to
    the process of encoding a given object (or data structure) into its binary
    format. Accordingly, deseriaization is the process of restoring an object
    out of its binary data stream.

    SerDes is an important activity related to data exchange, mostly to ensure
    thread safety and data consistency as well as network/remote transmissions.
    A detailed discussion is out of the scope of this documentation. Refer to
    the online documentation page 'pickle — Python object serialization' which
    is a good place to start:
        https://docs.python.org/3/library/pickle.html

    Representing a necessary activity which might require some (considerable)
    programming effort for special use cases, subsystem of messaging releases
    both sender and receiver from the issue of SerDes for the most common and
    usual use cases by use of the abovementioned standard library 'pickle'
    behind the scenes.

    As far as the sending or receving interface functions/methods are concerned,
    it is important to remeber that SerDes has been already applied (to the fix
    portion of the message object) by the framework when messaging, except for
    the use case of internal (or self-) posting.

    However, handling of the payload (if any) is designed flexible enough to
    enable application tasks to cover any possible SerDes scenario when
    messaging. This is achieved by allowing the sender to choose one of the
    options below
        - default:
          SerDes is applied by the framework on both ends,

        - bypass:
          payload is excluded from the process of SerDes (e.g. for performance
          or security or encryption reasons),

        - custom:
          almost same as default, except the subsystem uses custom methods
          (specified by the sender) for SerDes.


    Note:
    ------
        - In general, queued messages are presented to a receiver task by the
          subsystem in an auto-managed way. The exact time by when this happens
          for a given message is basically a commitment given to individual
          tasks by the framework when they are created (or configured).
          The related policy of such a commitemnt, however, is not entirely
          available yet. This is especially true for internal messages, hence
          this version of the framework does not support them, but planned to be
          available by the next version soon.
        - Custom marshaling is not released yet (mainly due to ongoing tests).
        - Dynamic (de-)registration of user-defined dispatch filters is not
          released yet (mainly due to ongoing test runs).


    See:
    -----
        - XTask
        - XTaskProfile
        - XMessage
        - XMessageHeader
        - XPayload
        - XPayloadIF
        - EPreDefinedMessagingID
    """


    __slots__ = []

    def __init__(self):
        pass


    # ------------------------------------------------------------------------------
    # API - Messaging
    # ------------------------------------------------------------------------------
    @staticmethod
    def SendMessage( rxTask_       : Union[XTask, IntEnum, int]
                   , msgLabelID_   : Union[IntEnum, int]        =EPreDefinedMessagingID.DontCare
                   , msgClusterID_ : Union[IntEnum, int]        =EPreDefinedMessagingID.DontCare
                   , msgPayload_   : Union[XPayloadIF, dict]    =None) -> int:
        """
        Request to submit an external message with currently running task taken
        as sender.

        Main responsibility of this interface function is to construct a
        message object based on the passed in parameters, and to put that object
        to the external queue of the receiver task.

        In cases an immediate delivery is not possible, for example when
        receiver's queue is temporarily full, an internal, shared service
        responsible for delivery of pending messages is in charge to take over
        the remaining part of the delivery process.

        Later, framework's execution of the run phase of the receiver task is
        responsible to call the respective callback method (for processing of
        external messages) passing an instance of class XMessage as the message
        object sent by the sender.

        Parameters:
        -------------
            - rxTask_ :
              an instance of class XTask, or unique task ID of such a task,
              or a pre-defined alias ID, or a user-defined enum or an integer
              resolving to a unique task ID.
            - msgLabelID_ :
              optional pre-/user-defined message label.
            - msgClusterID_ :
              optional pre-/user-defined message cluster.
            - msgPayload_ :
              payload (if any) to be associated to the message to be sent.

        Returns:
        ----------
            Positive integer number uniquely identifying sent message if the
            operation succeeded, 0 otherwise.

        Note:
        ------
            - The multipurpose type annotation of the first three parameters to
              be passed to enables the senders to choose any of the addressing
              policies, i.e. direct or alias or anonymous addressing, at their
              convenient.
            - For general description of the messaging subsystem refer to class
              description of XMessageManager above.

        See:
        -----
            - XMessage
            - XMessageHeader
            - XPayload
            - XPayloadIF
            - XTask.xtaskUniqueID
            - XTask.ProcessExternalMessage()
            - XTask.TriggerExternalQueueProcessing()
            - EPreDefinedMessagingID
        """
        return _XMsgMgrImpl._SendXMsg(rxTask_, msgLabelID_, msgClusterID_, payload_=msgPayload_)


    @staticmethod
    def BroadcastMessage( msgLabelID_   : Union[IntEnum, int]
                        , msgClusterID_ : Union[IntEnum, int]     =EPreDefinedMessagingID.DontCare
                        , msgPayload_   : Union[XPayloadIF, dict] =None) -> int:
        """
        Request to broadcast an external message with currently running task
        taken as sender.

        This interface is provided for convenience only. It works exactly the
        same way as 'SendMessage()' explained above except for:
            - parameter 'rxTask_' to be passed to is set to the pre-defined ID
              below 'EPreDefinedMessagingID.Broadcast',
            - parameter 'msgLabelID_' is mandatory.

        The major benefits of sending a message as broadcast is: firstly to have
        to submit one single request when more than one receiver are supposed
        to be delivered, secondly when anonymous addressing is either the
        preferred or the only available option to specify the receivers.

        Parameters:
        -------------
            - msgLabelID_ :
              mandatory pre-/user-defined message label.
            - msgClusterID_ :
              optional pre-/user-defined message cluster.
            - msgPayload_ :
              payload (if any) to be associated to the message to be sent.

        Returns:
        ----------
            Positive integer number uniquely identifying sent message if the
            operation succeeded, 0 otherwise.

        Note:
        ------
            - For general description of the messaging subsystem refer to class
              description of XMessageManager above.

        See:
        -----
            - XMessageManager.SendMessage()
        """
        return _XMsgMgrImpl._BroadcastXMsg(msgLabelID_, msgClusterID_,payload_=msgPayload_)
##END class XMessageManager
