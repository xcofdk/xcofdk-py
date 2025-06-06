#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : detailViewMainTaskGIL.py
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
class DetailViewMainTaskGILFrame(UserAppViewIF):

    # Grid layout ------------------------------------------------------------------
    # (not necessarily up-to-date)
    #
    #             +-------------------------+--------------------------+--------------+
    # row No. 1:  | lblMainTaskText         | lblMainTaskValue         |              |
    #             +-------------------------+--------------------------+--------------+
    #         2:  |                         | chbtnMainTaskAsync       |              |
    #             +-------------------------+--------------------------+--------------+
    #         3:  | lblStartedAtText        | lblStartedAtValue        |              |
    #             +-------------------------+--------------------------+--------------+
    #         4:  | lblDurationText         | lblDurationValue         |              |
    #             +-------------------------+--------------------------+--------------+
    #         5:  | lblNumSrvTasksText      | lblNumSrvTasksValue      |              |
    #             +-------------------------+--------------------------+--------------+
    #         6:  | lblMsgRcvText           | lblMsgRcvValue           |              |
    #             +-------------------------+--------------------------+--------------+
    #         7:  | lblSntMsgErrText        | lblSntMsgErrValue        |              |
    #             +-------------------------+--------------------------+--------------+
    #         8:  | lblOutOfOrderText       | lblOutOfOrderValue       |              |
    #             +-------------------------+--------------------------+--------------+
    #         9:  | lblSntMsgTotalErrText   | lblSntMsgTotalErrValue   |              |
    #             +------------------------ +--------------------------+--------------+
    #        10:  | lblOutOfOrderTotalText  | lblOutOfOrderTotalValue  |              |
    #             +------------------------ +--------------------------+--------------+
    #
    # ------------------------------------------------------------------------------

    __slots__ = [ '__mdlif' , '__numServiceTasks'
                #
                , '__lblMainTaskText'         , '__lblMainTaskValue'
                , '__lblDurationText'         , '__lblDurationValue'
                , '__lblStartedAtText'        , '__lblStartedAtValue'
                , '__lblNumSrvTasksText'      , '__lblNumSrvTasksValue'
                , '__lblMsgRcvText'           , '__lblMsgRcvValue'
                , '__tkbMainTaskAsync'        , '__chbtnMainTaskAsync'
                , '__lblSntMsgErrText'        , '__lblSntMsgErrValue'
                , '__lblOutOfOrderText'       , '__lblOutOfOrderValue'
                , '__lblSntMsgTotalErrText'   , '__lblSntMsgTotalErrValue'
                , '__lblOutOfOrderTotalText'  , '__lblOutOfOrderTotalValue'
                ]

    def __init__(self, rootWin_ : tk.Tk, modelif_ : UserAppModelIF, numServices_ =1):
        super().__init__()

        if numServices_ < 1:
            numServices_ = 1

        self.__mdlif           = modelif_
        self.__numServiceTasks = numServices_

        self.__lblMainTaskText         = None
        self.__lblMainTaskValue        = None
        self.__lblDurationText         = None
        self.__lblDurationValue        = None
        self.__lblStartedAtText        = None
        self.__lblStartedAtValue       = None
        self.__lblSntMsgErrText        = None
        self.__lblSntMsgErrValue       = None
        self.__lblOutOfOrderText       = None
        self.__lblOutOfOrderValue      = None
        self.__lblNumSrvTasksText      = None
        self.__lblNumSrvTasksValue     = None
        self.__lblSntMsgTotalErrText   = None
        self.__lblSntMsgTotalErrValue  = None
        self.__lblOutOfOrderTotalText  = None
        self.__lblOutOfOrderTotalValue = None

        _frm = ttk.LabelFrame(rootWin_, text='Main Task GIL')
        _frm['borderwidth'] = 2
        _frm['relief'] = 'groove'
        _frm.grid(padx=5, pady=5, sticky=(tk.W+tk.E))

        mtInfo = self.__mdlif.mainTaskInfo

    # row 1
        row = 0

        col = 0
        self.__lblMainTaskText = ttk.Label(_frm, text='Alias name/uid:  ')
        self.__lblMainTaskText.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

        col = 1
        self.__lblMainTaskValue = ttk.Label(_frm, text=f'{mtInfo.taskName}::{mtInfo.taskUID}')
        self.__lblMainTaskValue.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

    # row 2
        row += 1

        col = 1
        txt = 'Async. task' if mtInfo.isAsyncTask else 'Sync. task'
        self.__tkbMainTaskAsync   = tk.BooleanVar(value=True)
        self.__chbtnMainTaskAsync = ttk.Checkbutton(_frm, text=txt, variable=self.__tkbMainTaskAsync)
        self.__chbtnMainTaskAsync.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)
        self.__chbtnMainTaskAsync.configure(state='disable')

    # row 3
        row += 1

        col = 0
        self.__lblStartedAtText = ttk.Label(_frm, text='Started at:  ')
        self.__lblStartedAtText.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

        col = 1
        self.__lblStartedAtValue = ttk.Label(_frm, text=f'{mtInfo.taskStartTime}')
        self.__lblStartedAtValue.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

    # row 4
        row += 1

        col = 0
        self.__lblDurationText = ttk.Label(_frm, text='Duration:  ')
        self.__lblDurationText.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

        col = 1
        self.__lblDurationValue = ttk.Label(_frm, text=f'{mtInfo.taskDurationTime}')
        self.__lblDurationValue.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

    # row 5
        row += 1

        col = 0
        self.__lblNumSrvTasksText = ttk.Label(_frm, text='Number of service tasks:  ')
        self.__lblNumSrvTasksText.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

        col = 1
        self.__lblNumSrvTasksValue = ttk.Label(_frm, text=f'{numServices_}')
        self.__lblNumSrvTasksValue.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

    # row 6
        row += 1

        col = 0
        txt = 'Messages received:  '
        self.__lblMsgRcvText = ttk.Label(_frm, text=txt)
        self.__lblMsgRcvText.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

        col = 1
        self.__lblMsgRcvValue = ttk.Label(_frm, text=f'{mtInfo.messageCountReceived}')
        self.__lblMsgRcvValue.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

    # row 7
        row += 1

        col = 0
        self.__lblSntMsgErrText = ttk.Label(_frm, text='Send failures:  ')
        self.__lblSntMsgErrText.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

        col = 1
        self.__lblSntMsgErrValue = ttk.Label(_frm, text=f'{mtInfo.failuresCountSent}')
        self.__lblSntMsgErrValue.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

    # row 8
        row += 1

        col = 0
        self.__lblOutOfOrderText = ttk.Label(_frm, text='Received out-of-order:  ')
        self.__lblOutOfOrderText.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

        col = 1
        self.__lblOutOfOrderValue = ttk.Label(_frm, text=f'{mtInfo.outOfOrderReceivedCount}')
        self.__lblOutOfOrderValue.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

        frm2 = ttk.LabelFrame(_frm, text='All service tasks', width=_frm.winfo_width())
        frm2['borderwidth'] = 2
        frm2['relief'] = 'groove'
        frm2.grid(padx=5, pady=5, columnspan=3, sticky=(tk.W + tk.E))

    # row 9
        row += 1

        col = 0
        self.__lblSntMsgTotalErrText = ttk.Label(frm2, text='Total send failures:  ')
        self.__lblSntMsgTotalErrText.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

        col = 1
        self.__lblSntMsgTotalErrValue = ttk.Label(frm2, text=f'{mtInfo.serviceTasksTotalFailuresCountSent}')
        self.__lblSntMsgTotalErrValue.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

    # row 10
        row += 1

        col = 0
        self.__lblOutOfOrderTotalText = ttk.Label(frm2, text='Total received out-of-order:  ')
        self.__lblOutOfOrderTotalText.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

        col = 1
        self.__lblOutOfOrderTotalValue = ttk.Label(frm2, text=f'{mtInfo.serviceTasksOutOfOrderReceivedTotalCount}')
        self.__lblOutOfOrderTotalValue.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)


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
        mtInfo = self.__mdlif.mainTaskInfo

        self.__lblDurationValue['text'] = f'{mtInfo.taskDurationTime}'

        self.__lblMsgRcvValue['text']          = f'{mtInfo.messageCountReceived}'
        self.__lblSntMsgErrValue['text']       = f'{mtInfo.failuresCountSent}'
        self.__lblOutOfOrderValue['text']      = f'{mtInfo.outOfOrderReceivedCount}'
        self.__lblSntMsgTotalErrValue['text']  = f'{mtInfo.serviceTasksTotalFailuresCountSent}'
        self.__lblOutOfOrderTotalValue['text'] = f'{mtInfo.serviceTasksOutOfOrderReceivedTotalCount}'

        self.__mdlif.Unlock()
        return True
    # --------------------------------------------------------------------------
    #END override of interface inherited from UserAppViewIF
    # --------------------------------------------------------------------------
#END class DetailViewMainTaskGILFrame
