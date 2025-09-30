# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : __init__.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# PYTHONPATH extension
# ------------------------------------------------------------------------------
import os
import sys
sys.path.extend(((_xcoFWP := os.path.normpath(os.path.join(os.path.dirname(__file__), '_xcofw'))) not in sys.path) * [_xcoFWP])
sys.path.extend(((_xcoFWPA := os.path.normpath(os.path.join(os.path.dirname(__file__), '_xcofwa'))) not in sys.path) * [_xcoFWPA])


"""
The package 'xcofdk' is an implementation of XCOFDK for the programming
language Python.

XCOFDK is the architecture of an eXtensible, Customizable, Object-oriented
Framework Development Kit. It provides applications with a runtime environment
capable of: 
    - stable and reliable execution at any time,
    - running active services responsible for life-cycle management,
    - managed, unified error handling,
    - parallel or concurrent processing out-of-the-box,
    - instant access for transparent task or process communication,
    - providing API for auxiliary, bundled services commonly expected for
      the developement of applications capable of multitasking.


Public API:
------------
The public API of XCOFDK is given through its subpackages, also called
subsystems, which applications can use for interfacing. For an introductory
walkthrough of both the architecture and the subsystems of XCOFDK below wiki
page is highly recommended.
    https://github.com/xcofdk/xcofdk-py/wiki/3.-Architecture

Currently available subpackages (or subsystems) are as follows:
    - xcofdk.fwcom
      providing common and frequently used definitions,

    - xcofdk.fwapi
      the actual public API composed of the subpackages below:
          - xcofdk.fwapi.apiif
            collection of public interface classes,
            
          - xcofdk.fwapi.fwctrl
            providing API functions to control the framework, e.g. start or stop
            of the framework or error reporting via logging,
            
          - xcofdk.fwapi.rtecfg
            providing API functions for pre-start configuration of the framework,
            
          - xcofdk.fwapi.xmt
            providing both multithreading and life-cycle management,
            
          - xcofdk.fwapi.xmsg
            providing the subsystem of messaging,
            
          - xcofdk.fwapi.xmp
            providing the subsystem of multiprocessing.


Examples:
-----------
For both testing and demosntration purposes example programs are provided, too.
Detailed information can be found in class description blow:
    - xcofdk.tests.xuserapp.st.welcome.stguiappwelcome.STGuiAppWelcome


Documentation:
----------------
The source code documentation, also referred to as 'this documentation', of the
public API of XCOFDK frequently refers to the terms and basic concepts explained
in the above-mentioned wiki page. For better readability this documentation has
chosen to not repeat those explanations, their knowledge will be assumed
throughout this documentation.

Also, note that this documentation intensively uses 'doctest' lines with a
leading '>>>' for both:
    a) (highlighting of) embedded code snippet inside docstrings.
       Modern IDE editors, e.g. PyCharm (Community Edition), are able to
       display them as expected,
    b) cross referencing to existing documentation provided at some other place,
       e.g. to the respective API documentation of the parent class.
       Again, modern IDE editors are able to generate and display the 
       corresponding hyperlink, too.

By no means, however, such 'doctest' lines are designed for any kind of
interactive example or (regression) testing, as otherwise commonly intended
when using Python developer tool 'doctest'. Especially, as none of the modules
of this package, i.e. 'xcofdk', is designed to be executed by the interpreter
as the main module '__main__'.

This is also true for the respective main module of the provided examples where
the purpose of embedded code snippet (if any) is basically to illustrate sample
code or usage hints only, but never any kind of doctest-ing.


Note:
------
    - Unless otherwise stated, the term 'XCOFDK' and a given implementation of
      its architecture, e.g. this package 'xcofdk' for Python, are often used
      interchangeably,

    - also, the terms 'XCOFDK', 'frameowrk' and 'runtime environment' are used
      interchangeably, too, throughout this documentation,

    - applications shall interface with the framework only using the public API
      of XCOFDK mentioned above,

    - be aware that all subpackages named with a leading underscore, e.g.:
          xcofdk._xcofw
          xcofdk._xcofwa

      are protected, interal implementation of the framework representing its
      private 'library'. Subpackages or modules of the library must not be used
      or imported by applications.

      The private library of this package is prone to (frequent) changes due to
      the evolving nature of framework's development. Also, its immediate use
      from within an application would most probably cause violation against
      framework's internal state, breaking the whole runtime environment (the
      application relies on) as a worst-case scenario.
"""
