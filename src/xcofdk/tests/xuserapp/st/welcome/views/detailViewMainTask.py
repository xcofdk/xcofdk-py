#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : detailViewMainTask.py
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

from xuserapp.st.welcome.interfaces.modelif import EModelItemID
from xuserapp.st.welcome.interfaces.modelif import UserAppModelIF
from xuserapp.st.welcome.interfaces.viewif  import UserAppViewIF


# ------------------------------------------------------------------------------
# Interface / impl
# ------------------------------------------------------------------------------
class DetailViewMainTaskFrame(UserAppViewIF):

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
    #         6:  |                         |                          | btnPauseMsg  |
    #             +-------------------------+--------------------------+--------------+
    #         7:  | lblMsgSentText          | lblMsgSentValue          |              |
    #             +-------------------------+--------------------------+--------------+
    #         8:  | lblMsgRcvText           | lblMsgRcvValue           |              |
    #             +-------------------------+--------------------------+--------------+
    #         9:  | lblSntMsgErrText        | lblSntMsgErrValue        |              |
    #             +-------------------------+--------------------------+--------------+
    #        10:  | lblOutOfOrderText       | lblOutOfOrderValue       |              |
    #             +-------------------------+--------------------------+--------------+
    #        11:  | lblRcvMsgExpectedText   | lblRcvMsgExpectedValue   |              |
    #             +-------------------------+--------------------------+--------------+
    #        12:  | lblRcvMsgTotalText      | lblRcvMsgTotalValue      |              |
    #             +-------------------------+--------------------------+--------------+
    #        13:  | lblSntMsgTotalText      | lblSntMsgTotalValue      |              |
    #             +-------------------------+--------------------------+--------------+
    #        14:  | lblSntMsgTotalErrText   | lblSntMsgTotalErrValue   |              |
    #             +------------------------ +--------------------------+--------------+
    #        15:  | lblOutOfOrderTotalText  | lblOutOfOrderTotalValue  |              |
    #             +------------------------ +--------------------------+--------------+
    #
    # ------------------------------------------------------------------------------


    __slots__ = [ '__mdlif' , '__bMsgInfo' , '__numServiceTasks' , '__bBroadcast'
                #
                , '__lblMainTaskText'         , '__lblMainTaskValue'
                , '__lblMsgRcvText'           , '__lblMsgRcvValue'
                , '__lblMsgSentText'          , '__lblMsgSentValue'
                , '__lblDurationText'         , '__lblDurationValue'
                , '__lblStartedAtText'        , '__lblStartedAtValue'
                , '__lblNumSrvTasksText'      , '__lblNumSrvTasksValue'
                , '__tkbMainTaskAsync'        , '__chbtnMainTaskAsync'
                , '__lblSntMsgErrText'        , '__lblSntMsgErrValue'
                , '__lblSntMsgTotalErrText'   , '__lblSntMsgTotalErrValue'
                , '__lblRcvMsgTotalText'      , '__lblRcvMsgTotalValue'
                , '__lblRcvMsgExpectedText'   , '__lblRcvMsgExpectedValue'
                , '__lblSntMsgTotalText'      , '__lblSntMsgTotalValue'
                , '__lblOutOfOrderText'       , '__lblOutOfOrderValue'
                , '__lblOutOfOrderTotalText'  , '__lblOutOfOrderTotalValue'
                , '__btnPausePosting'
                ]

    def __init__(self, rootWin_ : tk.Tk, modelif_ : UserAppModelIF, bIncludeMsgInfo_ =False, numServices_ =0, bBroadcast_ =False, bBlockingSrvTsk_ =False):
        super().__init__()

        self.__mdlif           = modelif_
        self.__bMsgInfo        = bIncludeMsgInfo_
        self.__bBroadcast      = bBroadcast_
        self.__numServiceTasks = numServices_

        self.__lblMsgRcvText           = None
        self.__lblMsgRcvValue          = None
        self.__lblMsgSentText          = None
        self.__lblMsgSentValue         = None
        self.__btnPausePosting         = None
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
        self.__lblRcvMsgTotalText      = None
        self.__lblRcvMsgTotalValue     = None
        self.__lblSntMsgTotalText      = None
        self.__lblSntMsgTotalValue     = None
        self.__lblSntMsgTotalErrText   = None
        self.__lblSntMsgTotalErrValue  = None
        self.__lblRcvMsgExpectedText   = None
        self.__lblRcvMsgExpectedValue  = None
        self.__lblOutOfOrderTotalText  = None
        self.__lblOutOfOrderTotalValue = None

        _itFONT = ('TkDefaultFont', 11, 'italic')

        txt = 'Main Task'
        if bBroadcast_:
            txt += ' BC'
        elif bBlockingSrvTsk_:
            txt += ' BXQ'
        frm = ttk.LabelFrame(rootWin_, text=txt)
        frm['borderwidth'] = 2
        frm['relief'] = 'groove'
        frm.grid(padx=5, pady=5, sticky=(tk.W+tk.E))

        mtInfo = self.__mdlif.mainTaskInfo

    # row 1
        row = 0

        col = 0
        self.__lblMainTaskText = ttk.Label(frm, text='Alias name/uid:  ')
        self.__lblMainTaskText.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

        col = 1
        self.__lblMainTaskValue = ttk.Label(frm, text=f'{mtInfo.taskName}::{mtInfo.taskUID}')
        self.__lblMainTaskValue.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

    # row 2
        row += 1

        col = 1
        txt = 'Async. task' if mtInfo.isAsyncTask else 'Sync. task'
        self.__tkbMainTaskAsync   = tk.BooleanVar(value=True)
        self.__chbtnMainTaskAsync = ttk.Checkbutton(frm, text=txt, variable=self.__tkbMainTaskAsync)
        self.__chbtnMainTaskAsync.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)
        self.__chbtnMainTaskAsync.configure(state='disable')

    # row 3
        row += 1

        col = 0
        self.__lblStartedAtText = ttk.Label(frm, text='Started at:  ')
        self.__lblStartedAtText.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

        col = 1
        self.__lblStartedAtValue = ttk.Label(frm, text=f'{mtInfo.taskStartTime}')
        self.__lblStartedAtValue.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

    # row 4
        row += 1

        col = 0
        self.__lblDurationText = ttk.Label(frm, text='Duration:  ')
        self.__lblDurationText.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

        col = 1
        self.__lblDurationValue = ttk.Label(frm, text=f'{mtInfo.taskDurationTime}')
        self.__lblDurationValue.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

        if not bIncludeMsgInfo_:
            return
        if numServices_ < 1:
            return

    # row 5
        row += 1

        col = 0
        self.__lblNumSrvTasksText = ttk.Label(frm, text='Number of service tasks:  ')
        self.__lblNumSrvTasksText.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

        col = 1
        self.__lblNumSrvTasksValue = ttk.Label(frm, text=f'{numServices_}')
        self.__lblNumSrvTasksValue.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)


    # row 6
        row += 1

        col = 1
        self.__btnPausePosting = tk.Button(frm, text='Pause posting', width=14, font=_itFONT, command=self.__PauseMessaging)
        self.__btnPausePosting.grid(row=row, column=col, padx=5, pady=5, sticky=tk.E)

    # row 7
        row += 1

        col = 0
        txt = 'Broadcasts sent:  ' if bBroadcast_ else 'Messages sent:  '
        self.__lblMsgSentText = ttk.Label(frm, text=txt)
        self.__lblMsgSentText.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

        col = 1
        self.__lblMsgSentValue = ttk.Label(frm, text=f'{mtInfo.messageCountSent}')
        self.__lblMsgSentValue.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

    # row 8
        row += 1

        col = 0
        self.__lblMsgRcvText = ttk.Label(frm, text='Messages received:  ')
        self.__lblMsgRcvText.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

        col = 1
        self.__lblMsgRcvValue = ttk.Label(frm, text=f'{mtInfo.messageCountReceived}')
        self.__lblMsgRcvValue.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

    # row 9
        row += 1

        col = 0
        self.__lblSntMsgErrText = ttk.Label(frm, text='Send failures:  ')
        self.__lblSntMsgErrText.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

        col = 1
        self.__lblSntMsgErrValue = ttk.Label(frm, text=f'{mtInfo.failuresCountSent}')
        self.__lblSntMsgErrValue.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

    # row 10
        row += 1

        col = 0
        self.__lblOutOfOrderText = ttk.Label(frm, text='Received out-of-order:  ')
        self.__lblOutOfOrderText.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

        col = 1
        self.__lblOutOfOrderValue = ttk.Label(frm, text=f'{mtInfo.outOfOrderReceivedCount}')
        self.__lblOutOfOrderValue.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

    # row 11
        frm2 = ttk.LabelFrame(frm, text='All service tasks', width=frm.winfo_width())
        frm2['borderwidth'] = 2
        frm2['relief'] = 'groove'
        frm2.grid(padx=5, pady=5, columnspan=3, sticky=(tk.W + tk.E))

        row = -1

        if bBroadcast_:
            row += 1

            col = 0
            self.__lblRcvMsgExpectedText = ttk.Label(frm2, text='Total expected broadcasts:  ')
            self.__lblRcvMsgExpectedText.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

            col = 1
            self.__lblRcvMsgExpectedValue = ttk.Label(frm2, text=f'{numServices_*mtInfo.messageCountSent}')
            self.__lblRcvMsgExpectedValue.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

    # row 12
        row += 1
        col = 0
        txt = 'Total received broadcasts:  ' if bBroadcast_ else 'Total received messages:  '
        self.__lblRcvMsgTotalText = ttk.Label(frm2, text=txt)
        self.__lblRcvMsgTotalText.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

        col = 1
        self.__lblRcvMsgTotalValue = ttk.Label(frm2, text=f'{mtInfo.serviceTasksTotalCountReceived}')
        self.__lblRcvMsgTotalValue.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

    # row 13
        row += 1

        col = 0
        self.__lblSntMsgTotalText = ttk.Label(frm2, text='Total sent messages:  ')
        self.__lblSntMsgTotalText.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

        col = 1
        self.__lblSntMsgTotalValue = ttk.Label(frm2, text=f'{mtInfo.serviceTasksTotalCountSent}')
        self.__lblSntMsgTotalValue.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

    # row 14
        row += 1

        col = 0
        self.__lblSntMsgTotalErrText = ttk.Label(frm2, text='Total send failures:  ')
        self.__lblSntMsgTotalErrText.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

        col = 1
        self.__lblSntMsgTotalErrValue = ttk.Label(frm2, text=f'{mtInfo.serviceTasksTotalFailuresCountSent}')
        self.__lblSntMsgTotalErrValue.grid(row=row, column=col, padx=5, pady=0, sticky=tk.W)

    # row 15
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
        self.__lblMainTaskValue['text'] = f'{mtInfo.taskName}::{mtInfo.taskUID}'

        # skip message info parts?
        if not self.__bMsgInfo:
            pass
        else:
            self.__lblMsgRcvValue['text']          = f'{mtInfo.messageCountReceived}'
            self.__lblMsgSentValue['text']         = f'{mtInfo.messageCountSent}'
            self.__lblSntMsgErrValue['text']       = f'{mtInfo.failuresCountSent}'
            self.__lblOutOfOrderValue['text']      = f'{mtInfo.outOfOrderReceivedCount}'
            self.__lblSntMsgTotalValue['text']     = f'{mtInfo.serviceTasksTotalCountSent}'
            self.__lblRcvMsgTotalValue['text']     = f'{mtInfo.serviceTasksTotalCountReceived}'
            self.__lblSntMsgTotalErrValue['text']  = f'{mtInfo.serviceTasksTotalFailuresCountSent}'
            self.__lblOutOfOrderTotalValue['text'] = f'{mtInfo.serviceTasksOutOfOrderReceivedTotalCount}'

            bNotEqual = mtInfo.messageCountReceived != mtInfo.serviceTasksTotalCountSent
            color     = 'red' if bNotEqual else 'green'
            self.__lblMsgRcvValue.configure(foreground=color)
            self.__lblSntMsgTotalValue.configure(foreground=color)

            if self.__bBroadcast:
                totalExpected = self.__numServiceTasks*mtInfo.messageCountSent
                self.__lblRcvMsgExpectedValue['text'] = f'{totalExpected}'

                bNotEqual = mtInfo.serviceTasksTotalCountReceived != totalExpected
                color     = 'red' if bNotEqual else 'blue'
                self.__lblRcvMsgTotalValue.configure(foreground=color)
                self.__lblRcvMsgExpectedValue.configure(foreground=color)
            else:
                bNotEqual = mtInfo.messageCountSent != mtInfo.serviceTasksTotalCountReceived
                color     = 'red' if bNotEqual else 'blue'
                self.__lblMsgSentValue.configure(foreground=color)
                self.__lblRcvMsgTotalValue.configure(foreground=color)

        self.__mdlif.Unlock()
        return True
    # --------------------------------------------------------------------------
    #END override of interface inherited from UserAppViewIF
    # --------------------------------------------------------------------------


    # --------------------------------------------------------------------------
    # own API
    # --------------------------------------------------------------------------
    # --------------------------------------------------------------------------
    #END own API
    # --------------------------------------------------------------------------


    # --------------------------------------------------------------------------
    # Impl
    # --------------------------------------------------------------------------
    def __PauseMessaging(self):
        if not self.isActive:
            return
        self.__mdlif.SetItem(EModelItemID.ePostingPaused, True)
        self.__btnPausePosting.configure(text='Resume posting', command=self.__ResumeMessaging)

    def __ResumeMessaging(self):
        if not self.isActive:
            return
        self.__mdlif.SetItem(EModelItemID.ePostingPaused, False)
        self.__btnPausePosting.configure(text='Pause posting', command=self.__PauseMessaging)
    # --------------------------------------------------------------------------
    #END Impl
    # --------------------------------------------------------------------------
#END class DetailViewMainTaskFrame
