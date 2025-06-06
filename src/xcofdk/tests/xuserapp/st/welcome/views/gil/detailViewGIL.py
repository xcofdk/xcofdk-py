#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : detailViewGIL.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from xcofdk.fwcom import override

from xuserapp.util.tkimport  import tk
from xuserapp.util.tkimport  import ttk
#from xuserapp.util.tkimport import ttf

from xuserapp.st.welcome.interfaces.modelif import UserAppModelIF
from xuserapp.st.welcome.interfaces.viewif  import UserAppViewIF


# ------------------------------------------------------------------------------
# Interface / impl
# ------------------------------------------------------------------------------
class DetailViewGILFrame(UserAppViewIF):
    # Grid layout ------------------------------------------------------------------
    # (not necessarily up-to-date)
    #
    #             +---------------------+----------------------+--------------+
    # row No. 1:  | lblNote             |                      |              |
    #             +---------------------+----------------------+--------------+
    #         2:  | lblSrvTskTSText     | lblSrvTskTSValue     |              |
    #             +---------------------+----------------------+--------------+
    #         3:  | lblFiboInputText    | lblFiboInputValue    |              |
    #             +---------------------+----------------------+--------------+
    #         4:  | lblFiboCpuTimeText  | lblFiboCpuTimeValue  |              |
    #             +---------------------+----------------------+--------------+
    #         5:  |                     |                      | btnPauseGIL  |
    #             +---------------------+----------------------+--------------+
    #
    # ------------------------------------------------------------------------------


    __slots__ = [ '__mdlif' , '__lblNote' , '__btnPauseGIL'
                , '__lblSrvTskTSText'    , '__lblSrvTskTSValue'
                , '__lblFiboInputText'   , '__lblFiboInputValue'
                , '__lblFiboCpuTimeText' , '__lblFiboCpuTimeValue'
                ]

    def __init__(self, rootWin_: tk.Tk, modelif_: UserAppModelIF = None, bGil2_ =False):
        super().__init__()

        self.__mdlif = modelif_

        self.__lblNote             = None
        self.__btnPauseGIL         = None
        self.__lblSrvTskTSText     = None
        self.__lblSrvTskTSValue    = None
        self.__lblFiboInputText    = None
        self.__lblFiboInputValue   = None
        self.__lblFiboCpuTimeText  = None
        self.__lblFiboCpuTimeValue = None

        _itFONT = ('TkDefaultFont', 11, 'italic')

        frm = ttk.LabelFrame(rootWin_, text='GIL2' if bGil2_ else 'GIL')
        frm['borderwidth'] = 2
        frm['relief'] = 'groove'
        frm.grid(padx=5, pady=5, sticky=(tk.W + tk.E))

        srvTaskGilSpec = None if modelif_ is None else modelif_.serviceTaskGilSpec

        if srvTaskGilSpec is None:
            _color          = 'black'
            _fiboInput      = '??'
            _fiboCpuTime    = '??'
            _runPhaseFreqMS = '??'
        else:
            _fiboInput   = f'{srvTaskGilSpec.fibonacciInput}'
            _fiboCpuTime = f'{srvTaskGilSpec.fibonacciCpuTimeMS}'

            if srvTaskGilSpec.isDeficientFrequencyForced:
                _color = 'red'
                _runPhaseFreqMS = f'{srvTaskGilSpec.deficientRunPhaseFrequencyMS}'
            else:
                _color = 'green'
                _runPhaseFreqMS = f'{srvTaskGilSpec.runPhaseFrequencyMS}'

    # row 1
        row = 0

        col = 0
        self.__lblNote = ttk.Label(frm, text='NOTE:\nItems highlighted in magenta refer to reference test environment.\n')
        self.__lblNote.grid(row=row, column=col, columnspan=3, padx=5, pady=0, sticky=tk.W)

    # row 2
        row += 1

        col = 0
        self.__lblSrvTskTSText = ttk.Label(frm, text='Service Tasks\' run-phase frequency [ms]:  ')
        self.__lblSrvTskTSText.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

        col = 1
        self.__lblSrvTskTSValue = ttk.Label(frm, text=_runPhaseFreqMS)
        self.__lblSrvTskTSValue.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)
        self.__lblSrvTskTSValue.configure(foreground=_color)

    # row 3
        row += 1

        col = 0
        txt  = 'Service Tasks\' '
        txt += 'Fibonacci calc. based on N:  ' if bGil2_ else 'Fibonacci input N:  '
        self.__lblFiboInputText = ttk.Label(frm, text=txt)
        self.__lblFiboInputText.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

        col = 1
        self.__lblFiboInputValue = ttk.Label(frm, text=_fiboInput)
        self.__lblFiboInputValue.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)
        self.__lblFiboInputValue.configure(foreground='blue')

    # row 4
        row += 1

        col = 0
        txt = f'Fibonacci ({_fiboInput}) ca. CPU time [ms]:  '
        self.__lblFiboCpuTimeText = ttk.Label(frm, text=txt)
        self.__lblFiboCpuTimeText.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

        col = 1
        self.__lblFiboCpuTimeValue = ttk.Label(frm, text=_fiboCpuTime)
        self.__lblFiboCpuTimeValue.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)
        self.__lblFiboCpuTimeValue.configure(foreground='magenta')

    # row 5
        row += 1

        col = 2
        self.__btnPauseGIL = tk.Button(frm, text='Pause Fibonacci', width=14, font=_itFONT, command=self.__PauseGIL)
        self.__btnPauseGIL.grid(row=row, column=col, padx=5, pady=5, sticky=tk.E)

    # --------------------------------------------------------------------------
    # override of interface inherited from UserAppViewIF
    # --------------------------------------------------------------------------
    @UserAppViewIF.isActive.getter
    def isActive(self) -> bool:
        return self.__mdlif is not None

    @override
    def StartView(self) -> bool:
        # nothing to do
        return True

    @override
    def UpdateView(self, updateCounter_ : int =None) -> bool:
        if not self.isActive:
            return False
        return True
    # --------------------------------------------------------------------------
    #END override of interface inherited from UserAppViewIF
    # --------------------------------------------------------------------------


    # --------------------------------------------------------------------------
    # Impl
    # --------------------------------------------------------------------------
    def __PauseGIL(self):
        if not self.isActive:
            return

        self.__mdlif.Lock()
        self.__mdlif.serviceTaskGilSpec.isGilPaused = True
        self.__mdlif.Unlock()

        self.__btnPauseGIL.configure(text='Resume Fibonacci', command=self.__ResumeGIL)

    def __ResumeGIL(self):
        if not self.isActive:
            return

        self.__mdlif.Lock()
        self.__mdlif.serviceTaskGilSpec.isGilPaused = False
        self.__mdlif.Unlock()

        self.__btnPauseGIL.configure(text='Pause Fibonacci', command=self.__PauseGIL)
    # --------------------------------------------------------------------------
    #END Impl
    # --------------------------------------------------------------------------
#END class DetailViewGILFrame
