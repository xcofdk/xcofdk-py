<!-- ---------------------------------------------------------------------------
File        : README.md
Copyright   : Copyright(c) 2023-2024 Farzad Safa (farzad.safa@xcofdk.de)
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
multithreaded applications. <br>
Representing a quite simple example, it creates application's main task with synchronous execution type, which is
executed by the framework from within program's entry point <tt>Main()</tt>, that is synchronously to program's
<tt>MainThread</tt>:

```python
# file : quickStart.py

from threading import current_thread as _PyCurThread  # for demonstration purposes only

from xcofdk             import fwapi
from xcofdk.fwcom       import ETernaryCallbackResultID
from xcofdk.fwcom       import override
from xcofdk.fwcom       import xlogif
from xcofdk.fwapi.xtask import MainXTask
from xcofdk.fwapi.xtask import XTaskProfile

class AppMainTask(MainXTask):
    def __init__(self):
        _tp = XTaskProfile.CreateSynchronousTaskProfile(aliasName_='appMainTask')
        MainXTask.__init__(self, taskProfile_=_tp)

    @override
    def RunXTask(self) -> ETernaryCallbackResultID:
        _msg  = 'sync.' if self.xtaskProfile.isSynchronousTask else 'async.'
        _msg  = f'Welcome to XCOFDK by {_msg} {self.xtaskAliasName}:'
        _msg += f'\n\tcurrent host thread : {_PyCurThread().name}'
        xlogif.LogInfo(_msg)
        return ETernaryCallbackResultID.STOP

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
[14:11:19.856 KPI] Done initial (resource) loading, consumed CPU time was: 0.090
[14:11:19.857 KPI] Framework is up and running, consumed CPU time was: 0.064
[14:11:19.868 XINF][XTd_501001] Welcome to XCOFDK by sync. appMainTask:
    current host thread : MainThread
[14:11:19.871 INF][XTd_501001] Got request to stop framework.
[14:11:19.872 KPI][XTd_501001] Starting coordinated shutdown...
[14:11:19.873 INF][XTd_501001] Got request to join framework.
[14:11:19.873 INF][XTd_501001] Waiting for framework to complete shutdown sequence...
[14:11:19.974 KPI] Finished coordinated shutdown.
[14:11:19.991 KPI] Framework active tracking duration: 0.188

--------------------------------------------------------------------------------
Fatals(0), Errors(0), Warnings(0), Infos(4)
Total processing time: 0.293
--------------------------------------------------------------------------------
...
```

<br>

More related information available on:
- [1. Introduction](https://github.com/xcofdk/xcofdk-py/wiki/1.-Introduction) for an overview of the framework,
- [2. Quick Start](https://github.com/xcofdk/xcofdk-py/wiki/2.-Quick-Start) explaining the above console program
  in more detail,
- [4. At a Glance - Process Instances](https://github.com/xcofdk/xcofdk-py/wiki/4.-At-a-Glance#process-instances)
  presenting the console program [quickStartMP.py](https://github.com/xcofdk/xcofdk-py/wiki/4.-At-a-Glance#process-instances)
  for multiprocessing,
- [5. Basic Examples - exampleB11](https://github.com/xcofdk/xcofdk-py/wiki/5.-Basic-Examples#exampleb11---common-sample-for-multithreaded-gui-programs)
  presenting a simple [tkinter](https://docs.python.org/3/library/tkinter.html) GUI application following the same usage pattern
  illustrated above.

<br>

# Licensing

[XCOFDK](https://github.com/xcofdk/xcofdk-py) is available under [MIT License](https://github.com/xcofdk/xcofdk-py/blob/master/LICENSE.txt).

<br>

# Links

<style>
td, th {
   border: none!important;
}
</style>

| Main page         | :      | [XCOFDK on GitHub](https://github.com/xcofdk/xcofdk-py)                      |
| ----------------  | -----  | ---------------------------------------------------------------------------- |
| **Wiki page**     | **:**  | [**XCOFDK Wiki**](https://github.com/xcofdk/xcofdk-py/wiki)                  |
| **License file**  | **:**  | [**MIT License**](https://github.com/xcofdk/xcofdk-py/blob/master/LICENSE.txt) |
