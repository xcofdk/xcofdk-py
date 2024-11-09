# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : fwargparser.py
#
# Copyright(c) 2023 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


import sys

from argparse import HelpFormatter  as _PyHelpFormatter
from argparse import ArgumentError  as _PyArgumentError
from argparse import ArgumentParser as _PyArgumentParser
from gettext  import gettext        as _

from xcofdk.fwcom import override

from xcofdk._xcofw.fw.fwssys.fwcore.base.listutil import _ListUtil
from xcofdk._xcofw.fw.fwssys.fwcore.swpfm.sysinfo import _SystemInfo


class _ParsedNamespace:

    def __init__(self):
        pass


class _FwArgParser(_PyArgumentParser):

    __slots__ = [ '__cntErr' , '__errMsg' , '__bExitOnErr' ]

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

        self.__cntErr     = 0
        self.__errMsg     = None
        self.__bExitOnErr = bExitOnError_

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


    @staticmethod
    def PrintNamespace(ns_):
        _maxLen = _ListUtil.GetMaxLen(ns_.__dict__)
        _maxLen = max(4, _maxLen)

        _fmtstr  = str(_maxLen)
        _fmtstr  = '{:>' + _fmtstr + 's} : {}'
        _keys = list(ns_.__dict__.keys())
        _keys.sort()

        print('Parsed namespace:')
        for _kk in _keys:
            print(_fmtstr.format(_kk, str(ns_.__dict__[_kk])))

    @property
    def isErrorFree(self):
        return self.__cntErr < 1

    @property
    def errorMessage(self):
        return self.__errMsg

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
        except _PyArgumentError as xcp:
            self.__cntErr += 1
            self.__errMsg = str(xcp)
        return res

    def ClearError(self):
        self.__cntErr = 0
        self.__errMsg = None


    @override
    def error(self, message):
        self.__cntErr += 1

        _args = { 'prog': self.prog, 'message': message }
        self.__errMsg = _('%(prog)s: error: %(message)s\n') % _args

        if not self.__bExitOnErr:
            raise Exception(self.__errMsg)

        self.print_usage(sys.stderr)
        self.exit(2, self.__errMsg)

    @override
    def exit(self, status=0, message=None):
        self.__Exit(status_=status, message_=message)


    def __Exit(self, status_=0, message_=None):
        if message_:
            self._print_message(message_, sys.stderr)
        if self.__bExitOnErr:
            sys.exit(status_)
