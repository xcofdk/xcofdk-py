<!-- ---------------------------------------------------------------------------
File        : README.md
Copyright   : Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
License     : This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
------------------------------------------------------------------------------->


# Project Description

**XCOFDK** is the architecture of an e**X**tensible, **C**ustomizable and **O**bject-oriented **F**ramework 
**D**evelopment **K**it.

This project presents an implementation of XCOFDK for Python through the package **<tt>xcofdk</tt>**. <br>
It provides Python applications with a runtime environment capable of: 
- stable and reliable execution at any time,
- running active services responsible for life-cycle management,
- managed, unified error handling,
- parallel or concurrent processing out-of-the-box,
- instant access for transparent task or process communication,
- providing API for auxiliary, bundled services commonly expected for application developement. 

<br>

# Installation

[XCOFDK](https://github.com/xcofdk/xcofdk-py) is available for **Python versions 3.8+** on both POSIX and Windows platfroms.

> **NOTE:** <br>
> By installing you agree to the terms and conditions of use of the software (see section [Licensing](#licensing) below).

Install using [PyPI package xcofdk](https://pypi.org/project/xcofdk/):

```bash
$> # install for Python 3.12
$> python3.12 -m pip install xcofdk
```

<br>

# Quick Start

The example below demonstrates typical use of the framework of [XCOFDK](https://github.com/xcofdk/xcofdk-py) by 
multithreaded applications. Representing a quite simple example:
- it creates application's main task with synchronous execution type, which is executed by the framework from 
  within program's entry point <tt>Main()</tt>, that is synchronously to program's <tt>MainThread</tt>,
- the main task, on the other hand, creates a few asynchronous tasks each performing some geometric calculation 
  for the passed arguments when started.

<br>

```python
# file : quickStart.py

from math      import pi             as _PI           # for demonstration purposes only
from math      import pow            as _POW          # ditto
from threading import current_thread as _PyCurThread  # ditto

from xcofdk             import fwapi
from xcofdk.fwcom       import ETernaryCallbackResultID
from xcofdk.fwcom       import override
from xcofdk.fwcom       import xlogif
from xcofdk.fwapi.xtask import MainXTask
from xcofdk.fwapi.xtask import XTaskProfile

class AppMainTask(MainXTask):
    def __init__(self):
        _tp = XTaskProfile.CreateSynchronousTaskProfile(aliasName_='appMainTask')
        super().__init__(taskProfile_=_tp)

    @override
    def RunXTask(self) -> ETernaryCallbackResultID:
        _msg  = 'sync.' if self.xtaskProfile.isSynchronousTask else 'async.'
        _msg  = f'Welcome to XCOFDK by {_msg} {self.xtaskAliasName}:'
        _msg += f'\n\tcurrent host thread : {_PyCurThread().name}'
        xlogif.LogInfo(_msg)

        xlogif.LogInfo('Starting a few async. tasks for geometric calculation...')
        _msg = GeomTask.CreateStartGeomPool()
        xlogif.LogInfo(f'Done, result:{_msg}')

        xlogif.LogInfo(f'Going to stop the run-phase of {self.xtaskAliasName}...')
        return ETernaryCallbackResultID.STOP

class GeomTask(XTask):
    def __init__(self, index_ : int):
        self.geomCalc = 0
        _tp = XTaskProfile.CreateAsynchronousTaskProfile(aliasName_=f'geomTask_{index_}')
        super().__init__(taskProfile_=_tp)

    @override
    def RunXTask(self, radius_ : float, bCalcArea_ =False) -> ETernaryCallbackResultID:
        self.geomCalc = _PI*_POW(radius_, 2) if bCalcArea_ else 2*_PI*radius_
        return ETernaryCallbackResultID.STOP

    @staticmethod
    def CreateStartGeomPool(size_ : int =5) -> str:
        _pool = [ GeomTask(ii) for ii in range(size_) ]
        for ii in range(size_):
            _tsk = _pool[ii]
            _tsk.Start(1.7+ii, bCalcArea_=ii%2)

        res, _FMT = '', '\n\t[{}] circle radius : {:<.2f}  ,  {:>12s} : {:<.4f}'
        for ii in range(size_):
            _tsk = _pool[ii]
            _tsk.Join()
            res += _FMT.format(_tsk.xtaskAliasName, 1.7+ii, 'enclosedArea' if ii%2 else 'perimeter', _tsk.geomCalc)
        return res

def Main():
    if not fwapi.StartXcoFW(): return 71   # step 1: start the framework
                                           #
    _myTsk = AppMainTask()                 # step 2: create application's main task
    _myTsk.Start()                         # step 3: start main task
    _myTsk.Join()                          # step 4: wait for main task's termination
    fwapi.StopXcoFW()                      # step 5: stop the framework
    _bLcErrorFree = fwapi.JoinXcoFW()      # step 6: wait for framework's coordinated shutdown
                                           #
    res = 72 if not _bLcErrorFree else 0   # step 7: check for LC failure (if any)
    return res

if __name__ == "__main__":
    exit(Main())
```

The output of the program should look like below:

```bash
$> python3.12 -m quickStart
...
[13:45:52.377 KPI] Done initial (resource) loading, consumed CPU time was: 0.079
[13:45:52.378 KPI] Framework is up and running, consumed CPU time was: 0.062
[13:45:52.381 XINF][XTd_501001] Welcome to XCOFDK by sync. appMainTask:
	current host thread : MainThread
[13:45:52.381 XINF][XTd_501001] Starting a few async. tasks for geometric calculation...
[13:45:52.395 XINF][XTd_501001] Done, result:
	[geomTask_0] circle radius : 1.70  ,     perimeter : 10.6814
	[geomTask_1] circle radius : 2.70  ,  enclosedArea : 22.9022
	[geomTask_2] circle radius : 3.70  ,     perimeter : 23.2478
	[geomTask_3] circle radius : 4.70  ,  enclosedArea : 69.3978
	[geomTask_4] circle radius : 5.70  ,     perimeter : 35.8142
[13:45:52.396 XINF][XTd_501001] Going to stop the run-phase of appMainTask...
[13:45:52.396 INF][XTd_501001] Got request to stop framework.
[13:45:52.397 KPI][XTd_501001] Starting coordinated shutdown...
[13:45:52.397 INF][XTd_501001] Got request to join framework.
[13:45:52.397 INF][XTd_501001] Waiting for framework to complete shutdown sequence...
[13:45:52.401 XWNG] Waiting for 1 task(s) to enter shutdown phase...
[13:45:52.508 KPI] Finished coordinated shutdown.
[13:45:52.531 KPI] Framework active tracking duration: 0.206

--------------------------------------------------------------------------------
Fatals(0), Errors(0), Warnings(0), Infos(7)
Total processing time: 0.299
--------------------------------------------------------------------------------
```

<br>

More related information available on:
- [1. Introduction](https://github.com/xcofdk/xcofdk-py/wiki/1.-Introduction) for an overview of the framework,
- [2. Quick Start](https://github.com/xcofdk/xcofdk-py/wiki/2.-Quick-Start) explaining the above console program
  in more detail,
- [4. At a Glance - Quick Start MP](https://github.com/xcofdk/xcofdk-py/wiki/4.-At-a-Glance#quick-start-mp)
  presenting the console program [quickStartMP.py](https://github.com/xcofdk/xcofdk-py/wiki/4.-At-a-Glance#quick-start-mp)
  for multiprocessing,
- [5. Basic Examples - exampleB11](https://github.com/xcofdk/xcofdk-py/wiki/5.-Basic-Examples#exampleb11---common-sample-for-multithreaded-gui-programs)
  presenting a simple [tkinter](https://docs.python.org/3/library/tkinter.html) GUI application following the same usage pattern
  illustrated above.

<br>

# Licensing

[XCOFDK](https://github.com/xcofdk/xcofdk-py) is available under [MIT License](https://github.com/xcofdk/xcofdk-py/blob/master/LICENSE.txt).

<br>

# Links

| Main page            | :      | [XCOFDK on GitHub](https://github.com/xcofdk/xcofdk-py)                                                        |
| -------------------  | -----  | -------------------------------------------------------------------------------                                |
| **Wiki**             | **:**  | [**XCOFDK Wiki**](https://github.com/xcofdk/xcofdk-py/wiki)                                                    |
| **Examples**         | **:**  | [**userapp.tar.gz**](https://github.com/xcofdk/xcofdk-py/blob/master/src/xcofdk/tests/userapp/userapp.tar.gz) \| [**userapp.zip**](https://github.com/xcofdk/xcofdk-py/blob/master/src/xcofdk/tests/userapp/userapp.zip) |
| **Changelog**        | **:**  | [**Release notes**](https://github.com/xcofdk/xcofdk-py/blob/master/doc/release_notes.md)                      |
| **Error reporting**  | **:**  | **error-xpy@xcofdk.de**                                                                                        |
| **License file**     | **:**  | [**MIT License**](https://github.com/xcofdk/xcofdk-py/blob/master/LICENSE.txt)                                 |
