#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : welcomeViewInfoFrame.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from xuserapp.util.tkimport import tk
from xuserapp.util.tkimport import ttk

from xuserapp.st.welcome.interfaces.modelif import UserAppUtil
from xuserapp.st.welcome.interfaces.modelif import UserAppModelIF


# ------------------------------------------------------------------------------
# Interface / impl
# ------------------------------------------------------------------------------
class WelcomeInfoFrame:
    __slots__ = [ '__tkbAutoClose'   , '__tkbAutoStart'
                , '__chbtnAutoStart' , '__chbtnAutoClose'
                , '__lblVerPy'       , '__lblNumCpuCors'
                , '__lblPlf'         , '__imgXcofdk'
                , '__lblXcoImage'
                ]

    def __init__(self, rootWin_ : tk.Tk, imgXcofdk_ : tk.Image, bAutoStart_=True, bAutoClose_ =True, modelif_ : UserAppModelIF =None):
        self.__lblPlf         = None
        self.__lblVerPy       = None
        self.__imgXcofdk      = None
        self.__tkbAutoClose   = None
        self.__tkbAutoStart   = None
        self.__lblNumCpuCors  = None
        self.__chbtnAutoClose = None
        self.__chbtnAutoStart = None

        _frm = ttk.LabelFrame(rootWin_, text='Info')
        _frm['borderwidth'] = 2
        _frm['relief'] = 'groove'
        _frm.grid(padx=5, pady=5, sticky=(tk.W+tk.E))

        self.__imgXcofdk = imgXcofdk_

        _row      = 0
        _bNoModel = modelif_ is None

        # create image/version labels
        if _bNoModel:
            _col = 0
            self.__lblXcoImage = ttk.Label(_frm, image=self.__imgXcofdk)
            self.__lblXcoImage.grid(row=_row, column=_col, padx=5, pady=0, sticky=tk.W)
        else:
            _col = 0
            self.__lblXcoImage = ttk.Label(_frm, image=self.__imgXcofdk)
            self.__lblXcoImage.grid(row=_row, column=_col, padx=5, pady=0, sticky=tk.W)

            _col += 1
            self.__lblVerPy = ttk.Label(_frm, text=f'v{modelif_.xcofdkVersion}')
            self.__lblVerPy.grid(row=_row, column=_col, padx=5, pady=0, sticky=tk.W)

            _col += 1
            _ver = modelif_.pythonVersion
            _bFT = _ver.endswith('-FT')
            self.__lblVerPy = ttk.Label(_frm, text=f'Python:  v{_ver}')
            self.__lblVerPy.grid(row=_row, column=_col, padx=5, pady=0, sticky=tk.W)
            if _bFT:
                self.__lblVerPy.configure(foreground='red' if UserAppUtil.IsExperimentalFTPythonVersion() else 'blue')

            _col += 1
            _txt = modelif_.hostPlatform
            if len(_txt) < 1:
                _txt = '**UNKNOWN**'
            elif _txt == 'Darwin':
                _txt = 'MacOS'
            self.__lblPlf = ttk.Label(_frm, text=f'Platform/OS:  {modelif_.hostPlatform}')
            self.__lblPlf.grid(row=_row, column=_col, padx=5, pady=0, sticky=tk.W)

            _col += 1
            self.__lblNumCpuCors = ttk.Label(_frm, text=f'CPU cores:  {modelif_.numCpuCores}')
            self.__lblNumCpuCors.grid(row=_row, column=_col, padx=5, pady=0, sticky=tk.W)

            _row += 1

        # create check button auto-start
        _col        = 1 if _bNoModel else 0
        _columnspan = 1 if _bNoModel else 2
        self.__tkbAutoStart   = tk.BooleanVar(value=bAutoStart_)
        self.__chbtnAutoStart = ttk.Checkbutton(_frm, text='auto-start', variable=self.__tkbAutoStart)
        self.__chbtnAutoStart.grid(row=_row, column=_col, columnspan=_columnspan, padx=5, pady=5, sticky=tk.W)
        self.__chbtnAutoStart.configure(state='disable')

        # create check button auto-close
        _col = 2
        self.__tkbAutoClose   = tk.BooleanVar(value=bAutoClose_)
        self.__chbtnAutoClose = ttk.Checkbutton(_frm, text='auto-close', variable=self.__tkbAutoClose)
        self.__chbtnAutoClose.grid(row=_row, column=_col, padx=5, pady=5, sticky=tk.W)

    @property
    def isAutoStartEnabled(self):
        return (self.__tkbAutoStart is not None) and self.__tkbAutoStart.get()

    @property
    def isAutoCloseEnabled(self):
        return (self.__tkbAutoClose is not None) and self.__tkbAutoClose.get()
#END class WelcomeInfoFrame
