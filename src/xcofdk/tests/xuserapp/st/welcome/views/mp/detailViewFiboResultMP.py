#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : detailViewFiboResultMP.py
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
class DetailViewFiboResultMPFrame(UserAppViewIF):

    # Grid layout ------------------------------------------------------------------
    # (not necessarily up-to-date)
    #
    #             +-----------------+--------------------+---------------------+------------------+----------------------+
    # row No. 1:  | lblSMText       | lblSMValue         |                     |                  | lblDurationValue     |
    #             +-----------------+--------------------+---------------------+------------------+----------------------+
    #         2:  | lblErrNumText   | lblErrNumValue     |                     |                  | btnPause             |
    #             +-----------------+------------------- +---------------------+------------------+----------------------+
    #         3:  | lblNote         |                    |                     |                  |                      |
    #             +-----------------+------------------- +---------------------+------------------+----------------------+
    #         4:  | lblTitleSender  | lblTitleFiboInput  | lblTitleFiboResult  | lblTitleCpuTime  | lblTitleElapsedTime  |
    #             +---------------------+----------------+---------------------+------------------+----------------------+
    #         5:  | lblSender1      | lblInput1          | lblResult1          | lblCpuTime1      | lblElapsedTime1      |
    #             +-----------------+--------------------+---------------------+------------------+----------------------+
    #         6:  | lblSender2      | lblInput2          | lblResult2          | lblCpuTime2      | lblElapsedTime2      |
    #             +-----------------+--------------------+---------------------+------------------+----------------------+
    #         7:  | lblSender3      | lblInput3          | lblResult3          | lblCpuTime3      | lblElapsedTime3      |
    #             +-----------------+--------------------+---------------------+------------------+----------------------+
    #         8:  | lblComp         |                    |                     | lblCpuTimeTotal  | lblElapsedTimeTotal  |
    #             +---------------------+----------------+---------------------+------------------+----------------------+
    #
    # ------------------------------------------------------------------------------


    __slots__ = [ '__mdlif' , '__frmMP'  , '__lstHeader' , '__btnPause' , '__lblNote'
                , '__lstLblSenderValue'  , '__lstLblFiboInputValue'     , '__lstLblFiboResultValue'
                , '__lstLblCpuTimeValue' , '__lstLblElapsedTimeValue'
                , '__lblCpuTimeTotal'    , '__lblElapsedTimeTotal'
                , '__lblDurationValue'   , '__lstDummyLabels'
                , '__lblSMText'          , '__lblSMValue'
                , '__lblErrNumText'      , '__lblErrNumValue'
                ]

    def __init__(self, rootWin_: tk.Tk, modelif_: UserAppModelIF =None, numServices_ =3):
        super().__init__()

        self.__mdlif = modelif_

        if numServices_ != len(self.__mdlif.serviceProcessResultList):
            self.__mdlif = None
            return

        self.__frmMP               = None
        self.__btnPause            = None

        self.__lstHeader              = []
        self.__lstDummyLabels         = []
        self.__lstLblSenderValue      = []
        self.__lstLblCpuTimeValue     = []
        self.__lstLblFiboInputValue   = []
        self.__lstLblFiboResultValue  = []
        self.__lstLblElapsedTimeValue = []

        self.__lblNote             = None
        self.__lblSMText           = None
        self.__lblSMValue          = None
        self.__lblErrNumText       = None
        self.__lblErrNumValue      = None
        self.__lblCpuTimeTotal     = None
        self.__lblDurationValue    = None
        self.__lblElapsedTimeTotal = None

        _itFONT             = ('TkDefaultFont', 11, 'italic')
        _mpSTART_METHOD     = self.__mdlif.serviceProcess.mpStartMethod
        _mpSTART_METHOD_LEN = len(_mpSTART_METHOD)

        if _mpSTART_METHOD_LEN < 6:
            _DUMMY_LEN = 22
        elif _mpSTART_METHOD_LEN > 13:
            _DUMMY_LEN = 7
        else:
            _DUMMY_LEN = 13


    # row 1
        _row = 0

        _frm1 = ttk.LabelFrame(rootWin_, text='MP:  Info & Control')
        _frm1['borderwidth'] = 2
        _frm1['relief'] = 'groove'
        _frm1.grid(padx=5, pady=5, sticky=(tk.W+tk.E))

        _col = 0
        self.__lblSMText = ttk.Label(_frm1, text='MP Start Method:  ')
        self.__lblSMText.grid(row=_row, column=_col, padx=5, pady=0, sticky=tk.W)

        _col += 1
        self.__lblSMValue = ttk.Label(_frm1, text=_mpSTART_METHOD)
        self.__lblSMValue.grid(row=_row, column=_col, padx=5, pady=0, sticky=tk.W)
        self.__lblSMValue.configure(foreground='blue')

        for ii in range(2,4):
            _col += 1
            _lbl = ttk.Label(_frm1, text=' '*_DUMMY_LEN)
            _lbl.grid(row=_row, column=_col, padx=5, pady=0, sticky=tk.E)
            self.__lstDummyLabels.append(_lbl)

        _col += 1
        self.__lblDurationValue = ttk.Label(_frm1, text='')
        self.__lblDurationValue.grid(row=_row, column=_col, padx=5, pady=0, sticky=tk.E)

    # row 2
        _row += 1

        _col = 0
        self.__lblErrNumText = ttk.Label(_frm1, text='Number of Errors:  ')
        self.__lblErrNumText.grid(row=_row, column=_col, padx=5, pady=0, sticky=tk.W)

        _col += 1
        self.__lblErrNumValue = ttk.Label(_frm1, text='0')
        self.__lblErrNumValue.grid(row=_row, column=_col, padx=5, pady=0, sticky=tk.W)

        _col = 4
        self.__btnPause = tk.Button(_frm1, text='Pause (next) MP Run', width=16, font=_itFONT, command=self.__Pause)
        self.__btnPause.grid(row=_row, column=_col, padx=5, pady=5, sticky=tk.W)

    # row 3
        _frm2 = ttk.LabelFrame(rootWin_, text='MP:')
        _frm2['borderwidth'] = 2
        _frm2['relief'] = 'groove'
        _frm2.grid(padx=5, pady=5, sticky=(tk.W + tk.E))
        self.__frmMP = _frm2

        _row = 0

        col = 0
        self.__lblNote = ttk.Label(_frm2, text='NOTE:\nItems highlighted in magenta refer to reference test environment.\n')
        self.__lblNote.grid(row=_row, column=col, columnspan=5, padx=5, pady=0, sticky=tk.W)

    # row 4
        _row += 1

        _col = 0
        lbl = ttk.Label(_frm2, text='PID::Service Process:  ')
        lbl.grid(row=_row, column=_col, padx=5, pady=0, sticky=tk.W)
        self.__lstHeader.append(lbl)

        _col += 1
        lbl = ttk.Label(_frm2, text='N: ')
        lbl.grid(row=_row, column=_col, padx=5, pady=0, sticky=tk.W)
        self.__lstHeader.append(lbl)

        _col += 1
        lbl = ttk.Label(_frm2, text='Fibonacci(N): ')
        lbl.grid(row=_row, column=_col, padx=5, pady=0, sticky=tk.W)
        self.__lstHeader.append(lbl)

        _col += 1
        lbl = ttk.Label(_frm2, text='ST CPU Time [s]: ')
        lbl.grid(row=_row, column=_col, padx=5, pady=0, sticky=tk.W)
        self.__lstHeader.append(lbl)

        _col += 1
        lbl = ttk.Label(_frm2, text='MP CPU Time [s]: ')
        lbl.grid(row=_row, column=_col, padx=5, pady=0, sticky=tk.W)
        self.__lstHeader.append(lbl)

    # rows 5, 6, 7
        for ii in range(numServices_):
            _row += 1

            _col = 0
            lbl = ttk.Label(_frm2, text='-')
            lbl.configure(foreground='blue')
            lbl.grid(row=_row, column=_col, padx=5, pady=0, sticky=tk.E)
            self.__lstLblSenderValue.append(lbl)

            _col += 1
            lbl = ttk.Label(_frm2, text='-')
            lbl.grid(row=_row, column=_col, padx=5, pady=0, sticky=tk.E)
            self.__lstLblFiboInputValue.append(lbl)

            _col += 1
            lbl = ttk.Label(_frm2, text='-')
            self.__lstLblFiboResultValue.append(lbl)
            lbl.grid(row=_row, column=_col, padx=5, pady=0, sticky=tk.E)

            _col += 1
            lbl = ttk.Label(_frm2, text='-')
            lbl.configure(foreground='magenta')
            self.__lstLblCpuTimeValue.append(lbl)
            lbl.grid(row=_row, column=_col, padx=5, pady=0, sticky=tk.E)

            _col += 1
            lbl = ttk.Label(_frm2, text='-')
            self.__lstLblElapsedTimeValue.append(lbl)
            lbl.grid(row=_row, column=_col, padx=5, pady=0, sticky=tk.E)
        #END for ii...

    # row 8
        if numServices_ > 1:
            _row += 1

            _col = 3
            lbl = ttk.Label(_frm2, text='-')
            lbl.configure(foreground='green')
            lbl.grid(row=_row, column=_col, padx=5, pady=0, sticky=tk.E)
            self.__lblCpuTimeTotal = lbl

            _col += 1
            lbl = ttk.Label(_frm2, text='-')
            lbl.configure(foreground='green')
            lbl.grid(row=_row, column=_col, padx=5, pady=0, sticky=tk.E)
            self.__lblElapsedTimeTotal = lbl

        self.UpdateView()


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

        self.__mdlif.Lock()

        _srvProcess    = self.__mdlif.serviceProcess
        _lstProcResult = self.__mdlif.serviceProcessResultList
        NUM_ROWS = len(_lstProcResult)

        self.__frmMP['text']            = 'MP:  Run No.  {:>02d}'.format(_srvProcess.mpRunCount)
        self.__lblErrNumValue['text']   = f'{_srvProcess.mpNumErrors}'
        self.__lblDurationValue['text'] = _srvProcess.durationTime

        if self.__lblCpuTimeTotal is not None:
            if self.__lblCpuTimeTotal['text'].startswith('-'):
                _fiboCpuTotal = sum( [pr.fibonacciCpuTimeSEC for pr in _lstProcResult] )
                self.__lblCpuTimeTotal['text'] = f'ST vs. MP:  {_fiboCpuTotal}'

        if self.__lblElapsedTimeTotal is not None:
            self.__lblElapsedTimeTotal['text'] = _srvProcess.processElapsedTimeTotalSEC

        for ii in range(NUM_ROWS):
            _procResult = _lstProcResult[ii]

            self.__lstLblSenderValue[ii]['text']      = _procResult.processName
            self.__lstLblCpuTimeValue[ii]['text']     = _procResult.fibonacciCpuTimeSEC
            self.__lstLblFiboInputValue[ii]['text']   = _procResult.fibonacciInput
            self.__lstLblElapsedTimeValue[ii]['text'] = _procResult.processElapsedTimeSEC

            if _procResult.fibonacciResult is not None:
                self.__lstLblFiboResultValue[ii]['text'] = _procResult.fibonacciResult
        #END for ii...

        self.__mdlif.Unlock()

        return True
    # --------------------------------------------------------------------------
    #END override of interface inherited from UserAppViewIF
    # --------------------------------------------------------------------------


    # --------------------------------------------------------------------------
    # Impl
    # --------------------------------------------------------------------------
    def __Pause(self):
        if not self.isActive:
            return

        self.__mdlif.Lock()
        self.__mdlif.serviceProcess.isPaused = True
        self.__mdlif.Unlock()

        self.__btnPause.configure(text='Resume (next) MP Run', command=self.__Resume)

    def __Resume(self):
        if not self.isActive:
            return

        self.__mdlif.Lock()
        self.__mdlif.serviceProcess.isPaused = False
        self.__mdlif.Unlock()

        self.__btnPause.configure(text='Pause (next) MP Run', command=self.__Pause)
    # --------------------------------------------------------------------------
    #END Impl
    # --------------------------------------------------------------------------
#END class DetailViewFiboResultMPFrame
