#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : detailViewFiboResult.py
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
class DetailViewFiboResultFrame(UserAppViewIF):

    # Grid layout --------------------------------------------------------------
    # (not necessarily up-to-date)
    #
    #             +-----------------+------------------- +---------------------+
    # row No. 1:  | lblTitleSender  | lblTitleFiboInput  | lblTitleFiboResult  |
    #             +---------------------+----------------+---------------------+
    #         2:  | lblSender1      | lblInput1          | lblResult1          |
    #             +-----------------+--------------------+---------------------+
    #         3:  | lblSender2      | lblInput2          | lblResult2          |
    #             +-----------------+--------------------+---------------------+
    #         4:  | lblSender3      | lblInput3          | lblResult3          |
    #             +-----------------+--------------------+---------------------+
    #
    # --------------------------------------------------------------------------


    __slots__ = [ '__mdlif' , '__lstHeader'
                , '__lstLblSenderValue' , '__lstLblFiboInputValue' , '__lstLblFiboResultValue'
                ]

    def __init__(self, rootWin_: tk.Tk, modelif_: UserAppModelIF =None, numReplies_ =3):
        super().__init__()

        self.__mdlif = modelif_

        self.__lstHeader             = []
        self.__lstLblSenderValue     = []
        self.__lstLblFiboInputValue  = []
        self.__lstLblFiboResultValue = []

        frm = ttk.LabelFrame(rootWin_, text='Fibonacci Reply')
        frm['borderwidth'] = 2
        frm['relief'] = 'groove'
        frm.grid(padx=5, pady=5, sticky=(tk.W + tk.E))

    # row 1
        row = 0

        col = 0
        lbl = ttk.Label(frm, text='Sent by Service Task: ')
        lbl.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)
        self.__lstHeader.append(lbl)

        col += 1
        lbl = ttk.Label(frm, text='N: ')
        lbl.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)
        self.__lstHeader.append(lbl)

        col += 1
        lbl = ttk.Label(frm, text='Fibonacci(N): ')
        lbl.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)
        self.__lstHeader.append(lbl)

    # rows 2, 3, 4
        for ii in range(numReplies_):
            row += 1

            col = 0
            lbl = ttk.Label(frm, text='-')
            lbl.configure(foreground='blue')
            lbl.grid(row=row, column=col, padx=5, pady=0, sticky=tk.E)
            self.__lstLblSenderValue.append(lbl)

            col += 1
            lbl = ttk.Label(frm, text='-')
            lbl.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)
            self.__lstLblFiboInputValue.append(lbl)

            col += 1
            lbl = ttk.Label(frm, text='-')
            self.__lstLblFiboResultValue.append(lbl)
            lbl.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)
        #END for ii...

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
        lstFiboResult = self.__mdlif.fibonacciReplyList

        NUM_ROWS    = len(self.__lstLblSenderValue)
        NUM_RESULTS = 0 if lstFiboResult is None else len(lstFiboResult)

        lblTimeMS = self.__lstHeader[2]
        txtTimeMS = 'Fibonacci(N) in   '

        for ii in range(NUM_ROWS):
            if ii >= NUM_RESULTS:
                fiboResult = None
            else:
                fiboResult = lstFiboResult[ii]

            if ii == 0:
                txtTimeMS += '0.00 [ms]' if fiboResult is None else fiboResult.calculationTimeMS
                txtTimeMS += ':'
                lblTimeMS['text'] = txtTimeMS

            if fiboResult is None:
                self.__lstLblSenderValue[ii]['text']     = '-'
                self.__lstLblFiboInputValue[ii]['text']  = '-'
                self.__lstLblFiboResultValue[ii]['text'] = '-'
            else:
                self.__lstLblSenderValue[ii]['text']     = fiboResult.sender
                self.__lstLblFiboInputValue[ii]['text']  = fiboResult.fibonacciInput
                self.__lstLblFiboResultValue[ii]['text'] = fiboResult.fibonacciResult
        #END for ii...

        self.__mdlif.Unlock()

        return True
    # --------------------------------------------------------------------------
    #END override of interface inherited from UserAppViewIF
    # --------------------------------------------------------------------------
#END class DetailViewFiboResultFrame
