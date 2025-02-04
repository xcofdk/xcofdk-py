#!
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : __init__.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

from xcofdk._xcofwa.fwadmindefs import _FwAdapterConfig

if _FwAdapterConfig._IsRedirectPyLoggingEnabled():
    import logging as _PyLogger

    _loglevel = _PyLogger.DEBUG if _FwAdapterConfig._IsRedirectPyLoggingDebugLogLevelEnabled() else _PyLogger.INFO

    _PyLogger.basicConfig(encoding='utf-8', level=_loglevel, format='[%(levelname)s] %(message)s')
    from xcofdk._xcofw.fwadapter                import logifadaptee as rlogif
    from xcofdk._xcofw.fwadapter.aobjectadaptee import _AbstractObject
    from xcofdk._xcofw.fw.fwssys.fwcore.apiimpl import xlogifbase
else:
    if _FwAdapterConfig._IsLogIFDefaultConfigReleaseModeDisabled():
        from xcofdk._xcofw.fw.fwssys.fwcore.config.fwstartuppolicy import _FwStartupPolicy
        _FwStartupPolicy._SetUp(bRelMode_=False)
    from xcofdk._xcofw.fw.fwssys.fwcore.types.aobject import _AbstractObject
    from xcofdk._xcofw.fw.fwssys.fwcore.apiimpl       import xlogifbase

    if _FwAdapterConfig._IsLogIFUTSwitchModeEnabled():
        from xcofdk._xcofw.fw.fwssys.fwcore.logging import logif as rlogif
    else:
        from xcofdk._xcofw.fw.fwssys.fwcore.logging import vlogif as rlogif

