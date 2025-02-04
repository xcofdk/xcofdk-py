# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : arunnable.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from xcofdk._xcofwa.fwadmindefs import _FwSubsystemCoding

if _FwSubsystemCoding.IsSubsystemMessagingConfigured():
    from xcofdk._xcofw.fw.fwssys.fwmsg.msg.messagedefs  import _EMessagePeer
    from xcofdk._xcofw.fw.fwssys.fwmsg.msg.messagedefs  import _EMessageLabel
    from xcofdk._xcofw.fw.fwssys.fwmsg.msg.messagedefs  import _EMessageType
    from xcofdk._xcofw.fw.fwssys.fwmsg.msg.messagedefs  import _EMessageCluster
    from xcofdk._xcofw.fw.fwssys.fwmsg.msg.messagedefs  import _EMessageChannel
    from xcofdk._xcofw.fw.fwssys.fwmsg.msg.messagedefs  import _SubsysMsgUtil
    from xcofdk._xcofw.fw.fwssys.fwmsg.msg.messagedefs  import _MessageCluster

    from xcofdk._xcofw.fw.fwssys.fwmsg.msg.fwmessagehdr import _FwMessageHeader
    from xcofdk._xcofw.fw.fwssys.fwmsg.msg.fwmessage    import _FwMessage
    from xcofdk._xcofw.fw.fwssys.fwmsg.msg.messagehdrif import _MessageHeaderIF
    from xcofdk._xcofw.fw.fwssys.fwmsg.msg.messageif    import _MessageIF
    from xcofdk._xcofw.fw.fwssys.fwmsg.msg.fwpayload    import _FwPayload
else:
    _FwMessageHeader, _FwMessage                = object, object
    _EMessagePeer, _EMessageType, _EMessageCluster = object, object, object
    MessageLabel, _EMessageChannel               = object, object
    _MessageCluster, _SubsysMsgUtil               = object, object
    _MessageHeaderIF, _MessageIF, _FwPayload    = object, object, object
