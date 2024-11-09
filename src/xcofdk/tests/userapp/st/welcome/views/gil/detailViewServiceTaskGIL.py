#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : detailViewServiceTaskGIL.py
#
# Copyright(c) 2024 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from xcofdk.fwcom import override

from xcofdk.tests.userapp.util.tkimport  import tk
from xcofdk.tests.userapp.util.tkimport  import ttk
#from xcofdk.tests.userapp.util.tkimport import ttf

from xcofdk.tests.userapp.st.welcome.interfaces.modelif import UserAppModelIF
from xcofdk.tests.userapp.st.welcome.interfaces.viewif  import UserAppViewIF


# ------------------------------------------------------------------------------
# Interface / impl
# ------------------------------------------------------------------------------
class DetailViewServiceTaskGILFrame(UserAppViewIF):

    # Grid layout ------------------------------------------------------------------
    # (not necessarily up-to-date)
    #
    #             +--------------------+---------------------+-----------+
    # row No. 1:  | lblSrvTaskText     | lblSrvTaskValue     |           |
    #             +--------------------+---------------------+-----------+
    #         2:  |                    | chbtnSrvTaskAsync   |           |
    #             +--------------------+---------------------+-----------+
    #         3:  | lblStartedAtText   | lblStartedAtValue   |           |
    #             +--------------------+---------------------+-----------+
    #         4:  | lblDurationText    | lblDurationValue    |           |
    #             +--------------------+---------------------+-----------+
    #         5:  | lblMsgSentText     | lblMsgSentValue     |           |
    #             +--------------------+---------------------+-----------+
    #         6:  | lblMsgRcvText      | lblMsgRcvValue      |           |
    #             +--------------------+---------------------+-----------+
    #         7:  | lblSntMsgErrText   | lblSntMsgErrValue   |           |
    #             +--------------------+---------------------+-----------+
    #         8:  | lblOutOfOrderText  | lblOutOfOrderValue  |           |
    #             +--------------------+---------------------+-----------+
    #
    # ------------------------------------------------------------------------------


    __slots__ = [ '__mdlif'              , '__frm'
                , '__lblSrvTaskText'     , '__lblSrvTaskValue'
                , '__lblDurationText'    , '__lblDurationValue'
                , '__lblStartedAtText'   , '__lblStartedAtValue'
                , '__tkbSrvTaskAsync'    , '__chbtnSrvTaskAsync'
                , '__lblSntMsgErrText'   , '__lblSntMsgErrValue'
                , '__lblOutOfOrderText'  , '__lblOutOfOrderValue'
                ]

    def __init__(self, rootWin_ : tk.Tk, modelif_ : UserAppModelIF):
        super().__init__()

        self.__mdlif = modelif_

        self.__frm                = None
        self.__lblSrvTaskText     = None
        self.__lblSrvTaskValue    = None
        self.__lblDurationText    = None
        self.__lblDurationValue   = None
        self.__lblStartedAtText   = None
        self.__lblStartedAtValue  = None
        self.__lblSntMsgErrText   = None
        self.__lblSntMsgErrValue  = None
        self.__tkbSrvTaskAsync    = None
        self.__chbtnSrvTaskAsync  = None
        self.__lblOutOfOrderText  = None
        self.__lblOutOfOrderValue = None

        stInfo = self.__mdlif.serviceTaskInfo

        txt = 'Service task GIL {:>2}'.format(stInfo.serviceTaskNo)
        frm = ttk.LabelFrame(rootWin_, text=txt)
        frm['borderwidth'] = 2
        frm['relief'] = 'groove'
        frm.grid(padx=5, pady=5, sticky=(tk.W+tk.E))
        self.__frm = frm

    # row 1
        row = 0

        col = 0
        self.__lblSrvTaskText = ttk.Label(frm, text='Alias name/uid:  ')
        self.__lblSrvTaskText.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

        col = 1
        self.__lblSrvTaskValue = ttk.Label(frm, text=f'{stInfo.taskName}::{stInfo.taskUID}')
        self.__lblSrvTaskValue.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

    # row 2
        row += 1

        col = 1
        txt = 'Async. task' if stInfo.isAsyncTask else 'Sync. task'
        self.__tkbSrvTaskAsync   = tk.BooleanVar(value=True)
        self.__chbtnSrvTaskAsync = ttk.Checkbutton(frm, text=txt, variable=self.__tkbSrvTaskAsync)
        self.__chbtnSrvTaskAsync.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)
        self.__chbtnSrvTaskAsync.configure(state='disable')

    # row 3
        row += 1

        col = 0
        self.__lblStartedAtText = ttk.Label(frm, text='Started at:  ')
        self.__lblStartedAtText.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

        col = 1
        self.__lblStartedAtValue = ttk.Label(frm, text=f'{stInfo.taskStartTime}')
        self.__lblStartedAtValue.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

    # row 4
        row += 1

        col = 0
        self.__lblDurationText = ttk.Label(frm, text='Duration:  ')
        self.__lblDurationText.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

        col = 1
        self.__lblDurationValue = ttk.Label(frm, text=f'{stInfo.taskDurationTime}')
        self.__lblDurationValue.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

    # row 5
        row += 1

        col = 0
        self.__lblSntMsgErrText = ttk.Label(frm, text='Send failures:  ')
        self.__lblSntMsgErrText.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

        col = 1
        self.__lblSntMsgErrValue = ttk.Label(frm, text=f'{stInfo.failuresCountSent}')
        self.__lblSntMsgErrValue.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

    # row 6
        row += 1

        col = 0
        self.__lblOutOfOrderText = ttk.Label(frm, text='Received out-of-order:  ')
        self.__lblOutOfOrderText.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

        col = 1
        self.__lblOutOfOrderValue = ttk.Label(frm, text=f'{stInfo.outOfOrderReceivedCount}')
        self.__lblOutOfOrderValue.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)


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
        stInfo = self.__mdlif.serviceTaskInfo

        txt = 'Service task GIL {:>2}'.format(stInfo.serviceTaskNo)

        self.__frm['text'] = txt

        self.__lblSrvTaskValue['text']  = f'{stInfo.taskName}::{stInfo.taskUID}'
        self.__lblDurationValue['text'] = f'{stInfo.taskDurationTime}'
        self.__tkbSrvTaskAsync.set(stInfo.isAsyncTask)

        self.__lblSntMsgErrValue['text']  = f'{stInfo.failuresCountSent}'
        self.__lblOutOfOrderValue['text'] = f'{stInfo.outOfOrderReceivedCount}'

        self.__mdlif.Unlock()
        return True
    # --------------------------------------------------------------------------
    #END override of interface inherited from UserAppViewIF
    # --------------------------------------------------------------------------
#END class DetailViewServiceTaskGILFrame
