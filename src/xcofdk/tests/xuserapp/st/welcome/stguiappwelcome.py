#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : stguiappwelcome.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# PYTHONPATH extension
# ------------------------------------------------------------------------------
import os, sys
from   typing import Union

_xcoRP = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../../../..'))
if _xcoRP.endswith('/src') and os.path.exists(os.path.join(_xcoRP, 'xcofdk')) and _xcoRP not in sys.path: sys.path.extend([_xcoRP])
try:
    import xcofdk
except ImportError:
    exit(f"[{os.path.basename(__file__)}] Failed to import Python package 'xcofdk', missing installation.")
sys.path.extend(((_xua := os.path.normpath(os.path.join(os.path.dirname(__file__), '../../..'))) not in sys.path) * [_xua])


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from xcofdk.fwcom import override

from xuserapp.util.tkimport import tk

from xuserapp.st.welcome.common.commondefs import EGuiConfig
from xuserapp.st.welcome.common.commondefs import EDetailViewID

from xuserapp.st.welcome.interfaces.modelif          import UserAppModelIF
from xuserapp.st.welcome.interfaces.viewif           import UserAppViewIF
from xuserapp.st.welcome.interfaces.controllerif     import UserAppControllerIF

from xuserapp.st.welcome.views.welcomeViewGuiActionFrame import WelcomeViewGuiActionFrame
from xuserapp.st.welcome.views.welcomeViewInfoFrame      import WelcomeInfoFrame

from xuserapp.st.welcome.views.detailViewMainTask    import DetailViewMainTaskFrame
from xuserapp.st.welcome.views.detailViewServiceTask import DetailViewServiceTaskFrame

from xuserapp.st.welcome.views.gil.detailViewGIL            import DetailViewGILFrame
from xuserapp.st.welcome.views.gil.detailViewFiboResult     import DetailViewFiboResultFrame
from xuserapp.st.welcome.views.gil.detailViewMainTaskGIL    import DetailViewMainTaskGILFrame
from xuserapp.st.welcome.views.gil.detailViewServiceTaskGIL import DetailViewServiceTaskGILFrame

from xuserapp.st.welcome.views.mp.detailViewFiboResultMP    import DetailViewFiboResultMPFrame


# ------------------------------------------------------------------------------
# Interface / impl
# ------------------------------------------------------------------------------
class STGuiAppWelcome(UserAppViewIF):
    """
    This class provides a (simple) GUI program commonly used by basic examples
    of XCOFDK to demonstrate how (GUI) applications can use the framework.


    MVC design:
    --------------
    The general design of the example GUI applications using this class follows
    the well-known Model-View-Controller architecture composed of three
    interface classes:
        - UserAppViewIF:
          view interface of main/child window(s)

        - UserAppModelIF:
          model interface to create/access data used by controller/window(s)

        - UserAppControllerIF:
          controller interface to be accessed for notifications

    Accordingly, class STGuiAppWelcome serves as the main GUI window of an
    example program. If run as main script, it represents a singlethreaded GUI
    application with no data model or child views used.


    GUI structure:
    ---------------
    All example programms present their respective user graphical interface by
    building blocks below:
        - Info frame:
          version info plus two checkboxes related to both 'auto-start' and
          'auto-close' (see section 'Program arguments' below).

        - GUI Action frame:
          sample graphical activity (implemented as a GUI progress bar) which
          is executed by the main task in a cyclical manner in case of
          mutlithreaded example programs.

          From viewpoint of the user, this frame represents the utmost
          requirement for 'responsiveness'. That is, regardless of how many
          additional tasks are running otherwise, the program action related to
          this frame is expected to be performed in an acceptable amount of time
          during whole program execution.

          Presented as GUI progress bar, this frame demonstrates a typical
          graphical action of any arbitrary GUI application. This way it can be
          considered a replacement for more complex real-world programs, e.g.
          image processing editors, front-end of (critical) monitoring systems,
          data search program on local machine, etc.

        - Child frames:
          additinal child window(s) of the given example.


    Program arguments:
    ----------------------
    In general, the command line options '-h' or '--help' will provide a
    self-explaining usage hint and exit the program.

    Also, there are two optional command line arguments commonly available to
    all basic GUI examples:
        1) --disable-auto-start:
           disables auto-start of the 'GUI Action' frame upon program start.
           It defaults to False.

        2) --enable-auto-close:
           enables auto-close of the program as soon as next cycle (if any) of
           the 'GUI Action' frame is accomplished.
           It defaults to False.


    Basic examples:
    -----------------
    The basic examples of XCOFDK are available through subpackages below:
        - xcofdk.tests.xuserapp.basic.xmt.rc  (for multithreading by RC tasks)
        - xcofdk.tests.xuserapp.basic.xmt.sc  (for multithreading by SC tasks)
        - xcofdk.tests.xuserapp.basic.xmp     (for multiprocessing)

    RC tasks are application tasks created as instances of class RCTask (or one
    of its derived classes) for rapid construction of tasks by passing callback
    functions.

    SC tasks, however, are application tasks created by subclassing the abstract
    classes XTask and/or XMainTask. The SC approach is recommended only if
    a support of application tasks with specific 'added-value' task abstraction
    and/or features is intended. Otherwise, SC shall be considered an undesired
    overhead in terms of required programming effort.

    Unless otherwise stated, presented (basic) examples are always given using
    RC tasks. Their SC counterparts (if any) can be found in above-mentioned
    subpackage. They are presented for demonstration purposes only.

    Currently available RC examples are as follows:
        QS)  xmt.rc.quickStart.py
             This console program is designed to demonstrate a small, but
             almost full-featured application for both multithreading and
             multiprocessing using XCOFDK.

        B11) xmt/rc/exampleB11/mtguiapp.py
             This Tk program uses application's main task to (a)synchronously
             start the GUI.

        B21) xmt/rc/exampleB21/mtguiapp.py
             This Tk application uses a synchronous main task and multiple
             asynchronous service tasks.
             It demostrates common pattern of multiple application tasks.

             The application is made quite parameterized to serve as a generic
             application used by other examples wherever applicable.
             It also is used to highlight basic features of the subsystem 'xmsg'
             for messaging.

        B22) xmt/rc/exampleB22/mtguiapp.py
             This Tk application uses a synchronous main task and multiple
             asynchronous service tasks.
             It demostrates use of broadcast as part of anonymous message
             addressing.

        B23) xmt/rc/exampleB23/mtguiapp.py
             This Tk application uses a synchronous main task and multiple
             asynchronous service tasks.
             It demostrates use of blocking external queues for message driven
             tasks.

        B24) xmt/rc/exampleB24/mtguiapp.py
             This Tk application uses a synchronous main task and multiple
             asynchronous service tasks.
             It demostrates messaging with (de-)serialization of the payload
             of individual messages disabled.

        B25) xmt/rc/exampleB25/mtguiapp.py
             This Tk application uses a synchronous main task and multiple
             asynchronous service tasks.
             It demostrates use of custom payload classes.

        B31) xmt/rc/exampleB31/mtguiapp.py
             This Tk application uses a synchronous main task and multiple
             asynchronous service tasks.
             It demostrates the impact of GIL on application's responsiveness.

        B32) xmt/rc/exampleB32/mtguiapp.py
             This Tk application uses a synchronous main task and multiple
             asynchronous service tasks.
             It demostrates achievable improvement via optimization of CPU-bound
             tasks even despite GIL.

        MPB11) xmp/exampleMPB11/mpguiapp.py
             This Tk application uses a synchronous main task and multiple
             service processes running in parallel.
             It demostrates multiprocessing using child processes provided by
             the framework.


    Note:
    ------
        - Class STGuiAppWelcome uses Tcl/Tk GUI toolkit provided via Python
          package 'tkinter'. Refer to link below for install guide (if needed):
              https://tkdocs.com/tutorial/install.html'

    See:
    -----
        >>> STGuiAppWelcome.Main()
        >>> UserAppViewIF
        >>> UserAppModelIF
        >>> UserAppControllerIF
    """


    __slots__ = [ '__rootWin' , '__hfrm'   , '__ifrm'   , '__gafrm'
                , '__dfrmMT'  , '__dfrmST' , '__ctrlif' , '__mdlif'
                , '__gfrm'    , '__ffrm'   , '__mpfrm'  , '__logo'
                , '__cpbRestartCtr'
                ]

    # --------------------------------------------------------------------------
    # constructor / initializer
    # --------------------------------------------------------------------------
    def __init__( self
                , title_           : str
                , bAutoStart_      =True
                , bAutoClose_      =False
                , bProgBarDemo_    =True
                , controllerif_    : UserAppControllerIF =None
                , modelif_         : UserAppModelIF      =None
                , detailViewID_    : EDetailViewID       =EDetailViewID.eNone
                , numServices_     =0
                , bBroadcast_      =False
                , bBlockingSrvTsk_ =False
                , bRCExample_      : Union[bool, None] =True):
        super().__init__()

        if not bAutoStart_:
            bAutoClose_ = False

        if isinstance(bRCExample_, bool):
            title_ += ' - RC' if bRCExample_ else ' - SC'

        self.__logo   = None
        self.__ifrm   = None
        self.__ffrm   = None
        self.__gfrm   = None
        self.__hfrm   = None
        self.__gafrm  = None
        self.__mpfrm  = None
        self.__dfrmMT = None
        self.__dfrmST = None

        self.__mdlif  = modelif_
        self.__ctrlif = controllerif_

        self.__cpbRestartCtr = 0

        # create root window
        self.__rootWin = tk.Tk()
        self.__rootWin.title(title_)
        self.__rootWin.resizable(width=False, height=False)

        self.__logo = tk.PhotoImage(file=os.path.join(os.path.split(__file__)[0], 'images/png/xcofdk_logo.png'))

        # create info frame
        self.__ifrm = WelcomeInfoFrame(self.__rootWin, self.__logo, bAutoStart_=bAutoStart_, bAutoClose_=bAutoClose_, modelif_=self.__mdlif)

        # create common progress bar
        if bProgBarDemo_:
            self.__gafrm = WelcomeViewGuiActionFrame(self.__rootWin, self.__ifrm)

        if isinstance(detailViewID_, EDetailViewID):
            # mp view
            if detailViewID_ & EDetailViewID.eFibonacciResultMP:
                self.__mpfrm = DetailViewFiboResultMPFrame(self.__rootWin, modelif_=self.__mdlif, numServices_=numServices_)

            # gil view
            elif (detailViewID_ & EDetailViewID.eGil) or (detailViewID_ & EDetailViewID.eFibonacciResult):
                bFiboResultView = (detailViewID_ & EDetailViewID.eFibonacciResult) != 0

                self.__gfrm = DetailViewGILFrame(self.__rootWin, modelif_=self.__mdlif, bGil2_=bFiboResultView)
                if bFiboResultView:
                    self.__ffrm = DetailViewFiboResultFrame(self.__rootWin, modelif_=self.__mdlif)

            # main task view
            if detailViewID_ & EDetailViewID.eMainTaskGil:
                self.__dfrmMT = DetailViewMainTaskGILFrame(self.__rootWin, modelif_=self.__mdlif, numServices_=numServices_)
            elif detailViewID_ & EDetailViewID.eMainTaskMsgInfo:
                self.__dfrmMT = DetailViewMainTaskFrame(self.__rootWin, modelif_=self.__mdlif, bIncludeMsgInfo_=True, numServices_=numServices_, bBroadcast_=bBroadcast_, bBlockingSrvTsk_=bBlockingSrvTsk_)
            elif detailViewID_ & EDetailViewID.eMainTask:
                self.__dfrmMT = DetailViewMainTaskFrame(self.__rootWin, modelif_=self.__mdlif, bIncludeMsgInfo_=False)

            # service task view
            if detailViewID_ & EDetailViewID.eServiceTaskGil:
                self.__dfrmST = DetailViewServiceTaskGILFrame(self.__rootWin, modelif_=self.__mdlif)
            elif detailViewID_ & EDetailViewID.eServiceTaskMsgInfo:
                self.__dfrmST = DetailViewServiceTaskFrame(self.__rootWin, modelif_=self.__mdlif, bIncludeMsgInfo_=True, bBroadcast_=bBroadcast_)
            elif detailViewID_ & EDetailViewID.eServiceTask:
                self.__dfrmST = DetailViewServiceTaskFrame(self.__rootWin, modelif_=self.__mdlif, bIncludeMsgInfo_=False)
        else:
            pass
    # --------------------------------------------------------------------------
    #END constructor / initializer
    # --------------------------------------------------------------------------


    # --------------------------------------------------------------------------
    # own API
    # --------------------------------------------------------------------------
    @staticmethod
    def Main():
        bAutoStart, bAutoClose = True, False
        if len(sys.argv) > 1:
            for aa in sys.argv[1:]:
                if aa.startswith('#'):
                    break

                if (aa == '-h') or (aa == '--help'):
                    _usage = os.path.splitext(os.path.basename(sys.argv[0]))[0]
                    _usage = f'Usage:\n\t$> python3 -m {_usage} [--help|-h] [--disable-auto-start] [--enable-auto-close]'
                    print(_usage)
                    return

                if aa == '--disable-auto-start':
                    bAutoStart = False
                elif aa == '--enable-auto-close':
                    bAutoClose = True

        if not bAutoStart:
            bAutoClose =False

        mygui = STGuiAppWelcome(title_='STGuiAppWelcome', bAutoStart_=bAutoStart, bAutoClose_=bAutoClose, bRCExample_=None)
        mygui.StartView()
    # --------------------------------------------------------------------------
    #END own API
    # --------------------------------------------------------------------------


    # --------------------------------------------------------------------------
    # override of interface inherited from UserAppViewIF
    # --------------------------------------------------------------------------
    @UserAppViewIF.isActive.getter
    def isActive(self) -> bool:
        return self.__rootWin is not None

    @override
    def StartView(self) -> bool:
        if self.__rootWin is None:
            return False

        if self.__gfrm:
            self.__gfrm.StartView()

        if self.__gafrm is not None:
            if not self.__gafrm.StartView():
                return False

            # trigger first view update
            self.__rootWin.after(EGuiConfig.eControllerNotificationFrequencyMS.value, self.UpdateView, 1)

        res, _msg, _xcp = True, None, None
        try:
            self.__rootWin.mainloop()
        except (AttributeError, Exception) as _x:
            _xcp = _x
            _msg = f'GUI event loop raised {type(_x).__name__}'
        finally:
            if _xcp is not None:
                res     = False
                _ctrlif = self.__ctrlif

                self.__rootWin.destroy()
                self.__rootWin = None
                self.__ctrlif = None

                if _ctrlif is not None:
                    _ctrlif.OnViewEncounteredException(_msg, _xcp)
        return res

    @override
    def UpdateView(self, updateCounter_ : int =None) -> bool:
        if self.__gafrm is None:
            return False

        if self.__ctrlif is not None:
            bProceeding = self.__gafrm.isGAFProceeding

            if self.__ctrlif.isControllerRunning:
                # trigger controller's callback
                if not self.__NotifyController(updateCounter_, bProgressBarProceeding_=bProceeding):
                    self.__Destroy()
                    return False

            if self.__gafrm.isGAFDone:
                self.__cpbRestartCtr += 1

                if (self.__cpbRestartCtr % EGuiConfig.eProgressBarAutoRestartFrequency.value) == 0:
                    self.__gafrm.Restart()
            else:
                self.__cpbRestartCtr = 0

        # update progress bar view
        if not self.__gafrm.UpdateView():
            self.__Destroy()
            return False

        # update main task view
        if self.__dfrmMT is not None:
            if not self.__dfrmMT.UpdateView():
                self.__Destroy()
                return False

        # update service task view
        if self.__dfrmST is not None:
            if not self.__dfrmST.UpdateView():
                self.__Destroy()
                return False

        # update fibo result view
        if self.__ffrm is not None:
            if not self.__ffrm.UpdateView():
                self.__Destroy()
                return False

        # update mp fibo result view
        if self.__mpfrm is not None:
            if not self.__mpfrm.UpdateView():
                self.__Destroy()
                return False

        # trigger next view update
        self.__rootWin.after(EGuiConfig.eControllerNotificationFrequencyMS.value, self.UpdateView, updateCounter_+1)
        return True
    # --------------------------------------------------------------------------
    #END override of interface inherited from UserAppViewIF
    # --------------------------------------------------------------------------


    # --------------------------------------------------------------------------
    # Impl
    # --------------------------------------------------------------------------
    def __SetGeometry(self, posx_ : int, posy_ : int, width_ : int, height_ : int):
        if self.__rootWin is None:
            return
        geom = f'{width_}x{height_}+{posx_}+{posy_}'
        self.__rootWin.geometry(geom)

    def __NotifyController(self, notifCounter_ : int, bProgressBarProceeding_ : bool =False, bOnDestroy_ =False) -> bool:
        if not self.__ctrlif.isControllerRunning:
            return False

        res, _msg, _xcp, _ctrlif = False, None, None, None

        try:
            res = self.__ctrlif.OnViewNotification(notifCounter_, bProgressBarProceeding_=bProgressBarProceeding_, bOnDestroy_=bOnDestroy_)
        except (AttributeError, Exception) as _x:
            _xcp = _x
            _msg = f'Controller notification caused {type(_x).__name__}'

            self.__rootWin.destroy()
            _ctrlif        = self.__ctrlif
            self.__ctrlif  = None
            self.__rootWin = None

            if _ctrlif is not None:
                _ctrlif.OnViewEncounteredException(_msg, _xcp)
        #finally:
        #    pass
        return res

    def __Destroy(self):
        if self.__ctrlif is not None:
            self.__NotifyController(0, bOnDestroy_=True)
            self.__ctrlif = None

        if self.__rootWin is not None:
            self.__rootWin.destroy()
            self.__rootWin = None
    # --------------------------------------------------------------------------
    #END Impl
    # --------------------------------------------------------------------------
#END class STGuiAppWelcome


# ------------------------------------------------------------------------------
# Execution
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    STGuiAppWelcome.Main()
