# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : __init__.py
#
# Copyright(c) 2024 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


"""
The package 'xcofdk' is an implementation of XCOFDK for the programming
language Python.

XCOFDK is 'the architecture' of an eXtensible, Customizable, Object-oriented
Framework Development Kit. It provides applications with a runtime environment
capable of: 
    - stable and reliable execution at any time,
    - running active services responsible for life-cycle management,
    - managed, unified error handling,
    - parallel or concurrent processing out-of-the-box,
    - instant access for transparent task or process communication,
    - providing API for auxiliary, bundled services commonly expected for
      application developement.


Public API:
------------
The public API of XCOFDK is given through its subpackages applications can use
for interfacing. For an introductary walkthrough of the API below source code
components are recommended (in their given order):
    - subpacakge xcofdk.fwapi
      for start and stop of the framework,

    - class xcofdk.fwapi.xtask.XTask
      for basic concepts of the framework and its support for multithreading,

    - class xcofdk.fwapi.xtask.XTaskError
      for both life-cycle management and subsystem of error handling,

    - class xcofdk.fwapi.xprocess.XProcess
      for the subsystem of multiprocessing,

    - class xcofdk.fwapi.xmsg.XMessageManager
      for the subsystem of messaging,

    - module xcofdk.fwcom.xlogif
      for the subsystem of logging.


Examples:
-----------
For both testing and demosntration purposes example programs are provided, too.
Detailed information can be found in class description blow:
    - xcofdk.tests.userapp.st.welcome.stguiappwelcome.STGuiAppWelcome


Note:
------
    - Unless otherwise stated, the term 'XCOFDK' and a given implementation of
      its architecture, e.g. the package 'xcofdk', are often used
      interchangeably.
    - Also, the terms 'XCOFDK', 'frameowrk' and 'runtime environment' are used
      interchangeably, too, throughout this documentation.
    - Applications shall interface with the framework only using the public API
      provided as subpackages of 'xcofdk'.
    - Be aware that all subpackages named with a leading underscore, e.g.:
          xcofdk._xcofw
          xcofdk._xcofwa

      are protected, interal implementation of the framework representing its
      subsystem 'core'. They must not be used or imported by applications.

      The subsystem 'core' is prone to (frequent) changes due to the evolving
      nature of framework's development. Also, its immediate use or access
      from within an application would most probably cause violation against
      framework's internal state, breaking the whole runtime environment (the 
      application relies on) as a worst-case scenario.
"""
