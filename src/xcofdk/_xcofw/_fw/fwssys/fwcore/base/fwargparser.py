# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwargparser.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------

import sys

from argparse import HelpFormatter  as _PyHelpFormatter
from argparse import ArgumentError  as _PyArgumentError
from argparse import ArgumentParser as _PyArgumentParser
from gettext  import gettext        as _

from _fw.fwssys.fwcore.base.listutil     import _ListUtil
from _fw.fwssys.fwcore.swpfm.sysinfo     import _SystemInfo
from _fw.fwssys.fwcore.types.commontypes import override

class _ParsedNamespace:
    def __init__(self):
        pass

class _FwArgParser(_PyArgumentParser):
    __slots__ = [ '__c' , '__m' , '__bX' ]

    def __init__( self
                , prog_                =None
                , usage_               =None
                , description_         =None
                , epilog_              =None
                , parents_             =[]
                , formatterClass_      =_PyHelpFormatter
                , prefixChars_         ='-'
                , fromfilePrefixChars_ =None
                , argumentDefault_     =None
                , conflictHandler_     ='error'
                , bAddHelp_            =False
                , bAllowAbbrev_        =False
                , bExitOnError_        =False):
        self.__c  = 0
        self.__m  = None
        self.__bX = bExitOnError_

        if not _SystemInfo._IsPythonVersionCompatible(3, 9):
            super().__init__( prog=prog_
                            , usage=usage_
                            , description=description_
                            , epilog=epilog_
                            , parents=parents_
                            , formatter_class=formatterClass_
                            , prefix_chars=prefixChars_
                            , fromfile_prefix_chars=fromfilePrefixChars_
                            , argument_default=argumentDefault_
                            , conflict_handler=conflictHandler_
                            , add_help=bAddHelp_
                            , allow_abbrev=bAllowAbbrev_)
        else:
            super().__init__( prog=prog_
                            , usage=usage_
                            , description=description_
                            , epilog=epilog_
                            , parents=parents_
                            , formatter_class=formatterClass_
                            , prefix_chars=prefixChars_
                            , fromfile_prefix_chars=fromfilePrefixChars_
                            , argument_default=argumentDefault_
                            , conflict_handler=conflictHandler_
                            , add_help=bAddHelp_
                            , allow_abbrev=bAllowAbbrev_
                            , exit_on_error=bExitOnError_)

    @property
    def isErrorFree(self):
        return self.__c < 1

    @property
    def errorMessage(self):
        return self.__m

    def GetUsage(self):
        return self.format_usage()

    def GetHelp(self):
        return self.format_help()

    def AddArgument(self, *args_: str, **kwargs_: dict):
        super().add_argument(*args_, **kwargs_)

    def Parse(self, args_ =None, namespace_ =None):
        res = namespace_
        if res is None:
            res = _ParsedNamespace()
        try:
            res = super().parse_args(args=args_, namespace=res)
        except _PyArgumentError as _xcp:
            self.__c += 1
            self.__m = str(_xcp)
        return res

    def ClearError(self):
        self.__c = 0
        self.__m = None

    @override
    def error(self, message):
        self.__c += 1

        _args = { 'prog': self.prog, 'message': message }
        self.__m = _('%(prog)s: error: %(message)s\n') % _args

        if not self.__bX:
            raise Exception(self.__m)

        self.print_usage(sys.stderr)
        self.exit(2, self.__m)

    @override
    def exit(self, status=0, message=None):
        self.__Exit(status_=status, message_=message)

    def __Exit(self, status_=0, message_=None):
        if message_:
            self._print_message(message_, sys.stderr)
        if self.__bX:
            sys.exit(status_)
