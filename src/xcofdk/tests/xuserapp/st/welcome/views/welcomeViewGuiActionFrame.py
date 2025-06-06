#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : welcomeViewGuiActionFrame.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from enum     import auto
from enum     import IntEnum
from enum     import unique
from datetime import datetime
from datetime import timedelta

from xcofdk.fwcom import override

from xuserapp.util.tkimport    import tk
from xuserapp.util.tkimport    import ttk
from xuserapp.util.userAppUtil import UserAppUtil

from xuserapp.st.welcome.common.commondefs          import EGuiConfig
from xuserapp.st.welcome.interfaces.viewif          import UserAppViewIF
from xuserapp.st.welcome.views.welcomeViewInfoFrame import WelcomeInfoFrame


# ------------------------------------------------------------------------------
# Interface / impl
# ------------------------------------------------------------------------------
class WelcomeViewGuiActionFrame(UserAppViewIF):
    # ------------------------------------------------------------------------------
    # inner-class(es) of WelcomeViewGuiActionFrame
    # ------------------------------------------------------------------------------
    @unique
    class _EProgBarState(IntEnum):
        ePBInactive    = 0
        ePBIdle        = auto()
        ePBProceeding  = auto()
        ePBInterrupted = auto()
        ePBDone        = auto()

        @property
        def isPBIdle(self):
            return self == WelcomeViewGuiActionFrame._EProgBarState.ePBIdle

        @property
        def isPBDone(self):
            return self == WelcomeViewGuiActionFrame._EProgBarState.ePBDone

        @property
        def isPBProceeding(self):
            return self == WelcomeViewGuiActionFrame._EProgBarState.ePBProceeding

        @property
        def isPBInterrupted(self):
            return self == WelcomeViewGuiActionFrame._EProgBarState.ePBInterrupted

        @property
        def isPBInactive(self):
            return self == WelcomeViewGuiActionFrame._EProgBarState.ePBInactive
    #END class _EProgBarState
    # ------------------------------------------------------------------------------
    #END inner-class(es) of WelcomeViewGuiActionFrame
    # ------------------------------------------------------------------------------


    __slots__ = [ '__state'      , '__stepCnt'
                , '__rootWin'    , '__btnStart'
                , '__lblElptTxt' , '__lblElptVal'
                , '__pb'         , '__infoFrm'
                , '__tsRefTime'  , '__tsDelta'
                ]

    def __init__(self, rootWin_ : tk.Tk, infoFrame_: WelcomeInfoFrame):
        super().__init__()

        self.__state     = WelcomeViewGuiActionFrame._EProgBarState.ePBIdle
        self.__infoFrm   = infoFrame_
        self.__stepCnt   = 0
        self.__tsDelta   = timedelta()
        self.__tsRefTime = None

        self.__pb         = None
        self.__btnStart   = None
        self.__lblElptTxt = None

        # set root window
        self.__rootWin = rootWin_

        _itFONT = ('TkDefaultFont', 11, 'italic')

        # create frame
        frm = ttk.LabelFrame(self.__rootWin, text='GUI Action')
        frm['borderwidth'] = 2
        frm['relief'] = 'groove'
        frm.grid(padx=5, pady=5, sticky=(tk.W+tk.E))

        frm.columnconfigure(2, weight=1)

    # row 1
        _row = 0

        _col = 0

        bIncludeTitleLabel = False
        if bIncludeTitleLabel:
            # create label for elapsed time text
            self.__lblElptTxt = ttk.Label(frm, text='Elapsed time:');
            self.__lblElptTxt.grid(row=_row, column=_col, padx=5, pady=0, sticky=tk.W)
            _col += 1

        # create label for elapsed time value
        self.__lblElptVal = ttk.Label(frm, text='0')
        self.__lblElptVal.grid(row=_row, column=_col, padx=5, pady=0, sticky=tk.W)
        #self.__lblElptVal.configure(width=9, borderwidth=2, relief='groove')

    # row 2
        _row += 1

        # create progress bar
        _col = 0
        self.__pb = ttk.Progressbar(frm, orient='horizontal', length=220, mode='determinate')
        self.__pb.grid(columnspan=2, row=_row, column=_col, padx=5, pady=0)

        # create stat/stop button
        _col = 2
        self.__btnStart = tk.Button(frm, text='Start', font=_itFONT, command=self._Start)
        self.__btnStart.grid(row=_row, column=_col, padx=5, pady=5, sticky=tk.E)


    # --------------------------------------------------------------------------
    # API
    # --------------------------------------------------------------------------
    @property
    def isGAFDone(self):
        return (self.__state is not None) and self.__state.isPBDone

    @property
    def isGAFProceeding(self):
        return (self.__state is not None) and self.__state.isPBProceeding

    @property
    def isGAFInterrupted(self):
        return (self.__state is not None) and self.__state.isPBInterrupted

    def Restart(self):
        if not self.isGAFDone:
            pass
        else:
            self._Start()

    # --------------------------------------------------------------------------
    # override of interface inherited from UserAppViewIF
    # --------------------------------------------------------------------------
    @UserAppViewIF.isActive.getter
    def isActive(self) -> bool:
        self.__UpdateState()
        return (self.__state is not None) and not self.__state.isPBInactive

    @override
    def StartView(self) -> bool:
        if self.__rootWin is None:
            return False

        if not self.__infoFrm.isAutoStartEnabled:
            return True

        return self._Start()

    @override
    def UpdateView(self, updateCounter_ : int =None) -> bool:
        return self.isActive


    # --------------------------------------------------------------------------
    # Impl
    # --------------------------------------------------------------------------
    def _Start(self) -> bool:
        if self.__rootWin is None:
            return False

        self.__state = WelcomeViewGuiActionFrame._EProgBarState.ePBProceeding
        self.__tsRefTime = datetime.now()
        self.__btnStart.configure(text=' Pause ', command=self._Pause)
        self.__pb['value'] = self.__stepCnt

        self.__rootWin.after(EGuiConfig.eProgressBarInitialUpdateWaitTimeMS.value, self._Step)
        return True

    def _Pause(self):
        self.__state = WelcomeViewGuiActionFrame._EProgBarState.ePBInterrupted
        self.__btnStart['text'] = 'Resume'

    def _Step(self):
        self.__UpdateElapsedTime(datetime.now())

        self.__pb['value'] = self.__stepCnt
        if self.isGAFInterrupted:
            self._Resume()
            return

        self.__UpdateElapsedTime(datetime.now())

        # step size reached?
        if self.__stepCnt == EGuiConfig.eProgressBarStepSize.value:
            self._Resume(bReset_=True)
        else:
            self.__stepCnt += 2
            self.__rootWin.after(EGuiConfig.eProgressBarUpdateFrequencyMS.value, self._Step)

        self.UpdateView()

    def _Resume(self, bReset_ =False):
        txt = 'Restart' if bReset_ else 'Resume'
        self.__btnStart.configure(text=txt, command=self._Start)

        if bReset_:
            self.__state   = WelcomeViewGuiActionFrame._EProgBarState.ePBDone
            self.__stepCnt = 0
            self.__tsDelta = timedelta()

    def __UpdateState(self):
        if self.__lblElptVal is None:
            pass
        elif not (self.isGAFProceeding or self.isGAFInterrupted):
            if self.__infoFrm is not None:
                if self.__infoFrm.isAutoCloseEnabled:
                    self.__state = WelcomeViewGuiActionFrame._EProgBarState.ePBInactive
        else:
            pass

    def __UpdateElapsedTime(self, tsRefTime_ : datetime =None):
        if tsRefTime_ is None:
            pass
        else:
            self.__tsDelta  += tsRefTime_ - self.__tsRefTime
            self.__tsRefTime = tsRefTime_

        if self.__stepCnt == 0:
            pass
        else:
            self.__lblElptVal['text'] = UserAppUtil.DeltaTime2Str(self.__tsDelta)
#END class WelcomeViewGuiActionFrame
