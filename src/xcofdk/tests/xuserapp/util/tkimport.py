#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : tkimport.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
import sys

try:
    import tkinter as tk

    _bThreaded = tk.Tcl().eval('set tcl_platform(threaded)') == '1'
except ImportError:
    _impErr  = '[TkImport] This Python script requires pre-installation of GUI package Tcl/Tk.'
    _impErr += '\nRefer to link below for install guide and try it again after installation:'
    _impErr += '\n    - https://tkdocs.com/tutorial/install.html'
    _impErr += '\nYou may also try \'python3 -m tkinter\' from the command line to check your installation of Tcl/Tk.'
    print(_impErr)
    sys.exit(1)
except Exception as _xcp:
    _impErr  = '[TkImport] Encountered exception below while trying to import Tcl/Tk:'
    _impErr += f'\n\t[{type(_xcp).__name__}] {_xcp}'
    _impErr += '\nNote that the execution of a Tcl/Tk program out of a virtual environment might fail, depending on the running Python version.'
    print(_impErr)
    sys.exit(2)

import tkinter.ttk         as ttk
from   tkinter import font as ttf
