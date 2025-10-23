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
- supporting free-threaded (FT) Python (starting with the stable Python version <tt>3.14.0</tt>), 
- providing API for auxiliary, bundled services commonly expected for application developement. 

<br>


# Installation

[XCOFDK](https://github.com/xcofdk/xcofdk-py) is available for **Python versions 3.8+** on both POSIX and Windows platfroms.

> **NOTE:** <br>
> - By installing you agree to the terms and conditions of use of the software (see section [Licensing](#licensing) below). 

<br> 

Install using [PyPI package xcofdk](https://pypi.org/project/xcofdk/):

```bash
$> python3 -m pip install xcofdk
```

<br>


# Quick Start

In general, the [runtime environment RTE](https://github.com/xcofdk/xcofdk-py/wiki/3.-Architecture#312-runtime-environment-rte) 
of the framework of [XCOFDK for Python](https://github.com/xcofdk/xcofdk-py) is responsible for the complete execution 
(of part) of the task model of a program which uses the 
[multithreading subsystem](https://github.com/xcofdk/xcofdk-py/wiki/4.-API-Overview#42-xmt---subsystem-multithreading) 
of XCOFDK to construct that (part of the) task model. As such and except for the traditional <tt>'Hello world!'</tt>, 
any possible quick-start and sample porgram is by definition more than a 2-liner, especially when demonstrating some 
major aspects in practice.

Hence, the console program [<tt>quickStart.py</tt>](https://github.com/xcofdk/xcofdk-py/blob/master/src/xcofdk/tests/xuserapp/basic/xmt/rc/quickStart.py) 
demonstrates (partly advanced) use of the framework illustrating many of framework's features available for 
applications developed for multitasking. The task model of <tt>quickStart.py</tt> is composed of task instances designed for 
*rapid construction (RC)* by passing a (regular) callback function to the contructor of the respective class: 
- a [message-driven server task](https://github.com/xcofdk/xcofdk-py/wiki/2.-Quick-Start#24-algoservercbtgt), an 
  instance of class [<tt>MessageDrivenTask</tt>](https://github.com/xcofdk/xcofdk-py/blob/master/src/xcofdk/fwapi/xmt/rctask.py),
- a few [asynchronous client tasks](https://github.com/xcofdk/xcofdk-py/wiki/2.-Quick-Start#25-algoclientcbtgt), 
  instances of class [<tt>AsyncTask</tt>](https://github.com/xcofdk/xcofdk-py/blob/master/src/xcofdk/fwapi/xmt/rctask.py), 
- an [(a)synchronous starter (or main) task](https://github.com/xcofdk/xcofdk-py/wiki/2.-Quick-Start#26-startertaskcbtgt), 
  an instance of class [<tt>AsyncTask</tt>](https://github.com/xcofdk/xcofdk-py/blob/master/src/xcofdk/fwapi/xmt/rctask.py) 
  or [<tt>SyncTask</tt>](https://github.com/xcofdk/xcofdk-py/blob/master/src/xcofdk/fwapi/xmt/rctask.py). 

Note that the above-mentioned [RC task classes](https://github.com/xcofdk/xcofdk-py/wiki/4.-API-Overview#421-task-classes) 
are each an implementation of the interface class 
[IRCTask](https://github.com/xcofdk/xcofdk-py/blob/master/src/xcofdk/fwapi/apiif/ifrctask.py) or 
[IRCCommTask](https://github.com/xcofdk/xcofdk-py/blob/master/src/xcofdk/fwapi/apiif/ifrctask.py), respectively. 


## Program Purpose

The application is designed to provide the execution of a given algorithm, here 
[<tt>CartProdAlgo()</tt>](https://github.com/xcofdk/xcofdk-py/blob/master/src/xcofdk/tests/xuserapp/util/userAppUtil.py), 
several times using both multithreading and multiprocessing. Each time an execution is requested, the algorithm 
constructs a random **Cartesian Product (CP)** and properly returns the result to the requestor, which is either an 
application (client) task or a child process. 

The output of the program is as shown below: 
- with the command line option for small CPs supplied:
  ```bash
  $> python3 -m quickStart --small-cartesian-product
  ...
  [14:12:13.121 XINF][MainThread] Welcome to XCOFDK in TerminalMode of RTE.
  [14:12:13.124 XINF][Tsk_501002] Running async. MainTask, current host thread: Tsk_501002
  [14:12:13.129 XINF][Tsk_501002] Starting 5x child processes...
  [14:12:13.137 XINF][CTsk_501001] Task AlgoSrv received first delivered message.
  [14:12:13.178 XINF][Tsk_501002] Starting 5x async. algo-client tasks...
  [14:12:14.841 XINF][CTsk_501001] Put request to stop the framework.
  [14:12:15.087 XINF] Got total of 29x small CartProdAlgo executions:
      [14:12:13.144][TID:501001:AlgoSrv]  digitSet='439811'   size=7776     tail:   11113 ,  11119 ,  11118 ,  11111 ,  11111
      [14:12:13.144][TID:501002]          digitSet='220997'   size=7776     tail:   77772 ,  77770 ,  77779 ,  77779 ,  77777
      [14:12:13.187][TID:501003]          digitSet='268683'   size=7776     tail:   33336 ,  33338 ,  33336 ,  33338 ,  33333
      [14:12:13.190][TID:501004:AlgoC_4]  digitSet='735711'   size=7776     tail:   11113 ,  11115 ,  11117 ,  11111 ,  11111
      [14:12:13.203][TID:501006:AlgoC_6]  digitSet='865122'   size=7776     tail:   22226 ,  22225 ,  22221 ,  22222 ,  22222
      [14:12:13.204][TID:501003:AlgoC_3]  digitSet='539839'   size=7776     tail:   99993 ,  99999 ,  99998 ,  99993 ,  99999
      [14:12:13.209][TID:501005]          digitSet='470867'   size=7776     tail:   77777 ,  77770 ,  77778 ,  77776 ,  77777
      [14:12:13.231][TID:501007]          digitSet='962670'   size=7776     tail:   00006 ,  00002 ,  00006 ,  00007 ,  00000
      [14:12:13.232][TID:501003]          digitSet='818163'   size=7776     tail:   33331 ,  33338 ,  33331 ,  33336 ,  33333
      [14:12:13.247][TID:501003:AlgoC_3]  digitSet='242801'   size=7776     tail:   11114 ,  11112 ,  11118 ,  11110 ,  11111
      [14:12:13.254][TID:501004]          digitSet='657175'   size=7776     tail:   55555 ,  55557 ,  55551 ,  55557 ,  55555
      [14:12:13.258][TID:501005:AlgoC_5]  digitSet='944577'   size=7776     tail:   77774 ,  77774 ,  77775 ,  77777 ,  77777
      [14:12:13.273][TID:501004:AlgoC_4]  digitSet='524020'   size=7776     tail:   00002 ,  00004 ,  00000 ,  00002 ,  00000
      [14:12:13.296][TID:501006]          digitSet='022271'   size=7776     tail:   11112 ,  11112 ,  11112 ,  11117 ,  11111
      [14:12:13.312][TID:501007:AlgoC_7]  digitSet='868329'   size=7776     tail:   99996 ,  99998 ,  99993 ,  99992 ,  99999
      [14:12:13.318][TID:501004]          digitSet='559993'   size=7776     tail:   33335 ,  33339 ,  33339 ,  33339 ,  33333
      [14:12:13.340][TID:501005]          digitSet='557954'   size=7776     tail:   44445 ,  44447 ,  44449 ,  44445 ,  44444
      [14:12:13.367][TID:501006:AlgoC_6]  digitSet='183362'   size=7776     tail:   22228 ,  22223 ,  22223 ,  22226 ,  22222
      [14:12:13.381][TID:501005:AlgoC_5]  digitSet='038110'   size=7776     tail:   00003 ,  00008 ,  00001 ,  00001 ,  00000
      [14:12:13.422][TID:501007]          digitSet='609383'   size=7776     tail:   33330 ,  33339 ,  33333 ,  33338 ,  33333
      [14:12:13.465][TID:501006]          digitSet='149734'   size=7776     tail:   44444 ,  44449 ,  44447 ,  44443 ,  44444
      [14:12:13.515][TID:501007:AlgoC_7]  digitSet='174329'   size=7776     tail:   99997 ,  99994 ,  99993 ,  99992 ,  99999
      [14:12:13.731][TID:501002]          digitSet='013871'   size=7776     tail:   11111 ,  11113 ,  11118 ,  11117 ,  11111
      [14:12:13.732][TID:501001:AlgoSrv]  digitSet='756316'   size=7776     tail:   66665 ,  66666 ,  66663 ,  66661 ,  66666
      [14:12:14.703][PID:18098]           digitSet='16217270' size=2097152  tail:  0000001 , 0000007 , 0000002 , 0000007 , 0000000
      [14:12:14.758][PID:18099]           digitSet='68090537' size=2097152  tail:  7777779 , 7777770 , 7777775 , 7777773 , 7777777
      [14:12:14.762][PID:18097]           digitSet='99538187' size=2097152  tail:  7777773 , 7777778 , 7777771 , 7777778 , 7777777
      [14:12:14.771][PID:18100]           digitSet='06201049' size=2097152  tail:  9999990 , 9999991 , 9999990 , 9999994 , 9999999
      [14:12:14.772][PID:18101]           digitSet='58426844' size=2097152  tail:  4444442 , 4444446 , 4444448 , 4444444 , 4444444
  [14:12:15.087 XINF] Done, elapsed time for small CartProdAlgo: 0:00:02.041763
  ```
- lines with **<tt>[TID:nnnn]</tt>** inside are each the CP result of a request made by or on behalf of an application (client) task,
- lines with **<tt>[PID:nnnn]</tt>** inside are each the CP result of a request made out of a child process.


## Main Function

The module function [<tt>Main()</tt>](https://github.com/xcofdk/xcofdk-py/blob/master/src/xcofdk/tests/xuserapp/basic/xmt/rc/quickStart.py) 
represents program's entry point which is basically organized in accordance to the 
[common pattern of use](https://github.com/xcofdk/xcofdk-py/wiki/4.-API-Overview#4411-common-pattern-of-use) of the 
framework. When called, it performs below activities:
- **step 1:** [configuration of framework's RTE](https://github.com/xcofdk/xcofdk-py/wiki/4.-API-Overview#432-rte-configuration-api) 
  depending on the supplied command line options (if any):
  - enable RTE policy for [TerminalMode](https://github.com/xcofdk/xcofdk-py/blob/master/src/xcofdk/fwcom/fwdefs.py), 
  - bypass RTE policy for [experimental free-threading guard](https://github.com/xcofdk/xcofdk-py/blob/master/src/xcofdk/fwcom/fwdefs.py),
- **step 2:** [start of the framework](https://github.com/xcofdk/xcofdk-py/wiki/4.-API-Overview#4412-control-functions), 
- **step 3:** create and start application's [message-driven server task](https://github.com/xcofdk/xcofdk-py/wiki/2.-Quick-Start#24-algoservercbtgt) 
  which will be responsible for: 
  - triggering new CP calculations on behalf of application (client) tasks the server receives request messages from, 
  - managing the <tt>TerminalMode</tt> (if enabled):
    - wait for running child processes (if any) to complete, 
    - leave the <tt>TerminalMode</tt> by putting a [stop request to the framework](https://github.com/xcofdk/xcofdk-py/wiki/4.-API-Overview#4412-control-functions), 
- **step 4:** create and start application's [starter task](https://github.com/xcofdk/xcofdk-py/wiki/2.-Quick-Start#26-startertaskcbtgt), 
  responsible for: 
  - start of both child processes and client tasks,
  - wait for client tasks to complete,
  - request the server task to quit, 
- **step 5:** if the RTE policy <tt>TerminalMode</tt> is disabled: 
  - wait for running child processes (if any) to complete, 
- **step 6:** wait for [framework's coordinated shutdown](https://github.com/xcofdk/xcofdk-py/wiki/4.-API-Overview#4412-control-functions): 
  - if the RTE policy <tt>TerminalMode</tt> is enabled, then the framework will wait before entering its shutdown sequence <br> 
    as long as the <tt>TerminalMode</tt> is not left (see step 3 above), 
  - otherwise it will wait as long as there are application tasks still running (see RTE policy 
    [AutoStop](https://github.com/xcofdk/xcofdk-py/blob/master/src/xcofdk/fwcom/fwdefs.py)),
- **step 7:** collect and put out the CP results.

<br>

```python
def Main(cmdLineOpts_ : CLOptions):
    _startTime = datetime.now()

    # step 1: configure framework's RTE for terminal mode and/or
    #         experimental free-threaded Python (if enabled via CmdLine)
    if cmdLineOpts_.isSmallCartProdEnabled:
        DisableBigCartProd()
        rtecfg.RtePolicyEnableTerminalMode()
    if cmdLineOpts_.isFreeThreadingGuardBypassed:
        rtecfg.RtePolicyBypassExperimentalFreeThreadingGuard()

    # step 2: start framework
    if not fwapi.StartXcoFW(fwStartOptions_=cmdLineOpts_.GetSuppliedFwOptions()):
        return 71

    # step 3: create and start appplication's algo-server task
    _algoSrv = MessageDrivenTask(AlgoServerCBTgt, aliasName_='AlgoSrv', bRefToCurTaskRequired_=True, pollingFrequency_=20)
    _algoSrv.Start()

    # step 4: create and start appplication's starter task
    #         (which will create and start both child processes and client tasks, too)
    _count, _procPool = 5, []
    _starterTsk = CreateStartStarterTask(cmdLineOpts_, _algoSrv.taskUID, _count, _procPool)

    # step 5: if not in terminal mode, wait for running child processes to complete
    if not rtecfg.RtePolicyGetConfig().isTerminalModeEnabled:
        fwapi.JoinProcesses()

    # step 6: wait for framework's coordinated shutdown
    _bLcErrorFree = fwapi.JoinXcoFW()

    # step 7: collect and print out results of CP requests executed
    if _bLcErrorFree:
        _procPoolRes = [_pp.processSuppliedData for _pp in _procPool if _pp.processSuppliedData is not None]
        _cp  = _procPoolRes + _starterTsk.GetTaskOwnedData() + _algoSrv.GetTaskOwnedData()
        _cp.sort(key=lambda _ee: _ee.cartProdTimestamp)
        _cpLEN = len(_cp)
        _cp = '\n\t'.join( [str(_ee) for _ee in _cp] )

        _msg1 = 'small' if cmdLineOpts_.isSmallCartProdEnabled else 'big'
        _msg2 = f'Got total of {_cpLEN}x {_msg1} CartProdAlgo executions:\n\t{_cp}'
        xlogif.LogInfo(_msg2)
        xlogif.LogInfo(f'Done, elapsed time for {_msg1} CartProdAlgo: ' + str(datetime.now()-_startTime))

    # done: check for LC failure (if any)
    res = 72 if not _bLcErrorFree else 0
    return res
```

<br>

More introductory information relared to [XCOFDK for Python](https://github.com/xcofdk/xcofdk-py) available on the 
wiki pages below: 
- [1. Introduction](https://github.com/xcofdk/xcofdk-py/wiki/1.-Introduction) for an overview of the framework, 
- [2. Quick Start](https://github.com/xcofdk/xcofdk-py/wiki/2.-Quick-Start) explaining the above console program 
  in more detail: 
  - [2.2 Import of the API](https://github.com/xcofdk/xcofdk-py/wiki/2.-Quick-Start#22-import-of-the-api)
  - [2.4 AlgoServerCBTgt()](https://github.com/xcofdk/xcofdk-py/wiki/2.-Quick-Start#24-algoservercbtgt)
  - [2.5 AlgoClientCBTgt()](https://github.com/xcofdk/xcofdk-py/wiki/2.-Quick-Start#25-algoclientcbtgt)
  - [2.6 StarterTaskCBTgt()](https://github.com/xcofdk/xcofdk-py/wiki/2.-Quick-Start#26-startertaskcbtgt)
  - [2.7.1 CreateStartStarterTask()](https://github.com/xcofdk/xcofdk-py/wiki/2.-Quick-Start#271-createstartstartertask)
  - [2.7.2 CreateStartAlgoProcesses()](https://github.com/xcofdk/xcofdk-py/wiki/2.-Quick-Start#272-createstartalgoprocesses)
  - [2.7.3 CreateStartAlgoClients()](https://github.com/xcofdk/xcofdk-py/wiki/2.-Quick-Start#273-createstartalgoclients)
- [3. Architecture](https://github.com/xcofdk/xcofdk-py/wiki/3.-Architecture) for the design and subsystems of the 
  framework,
- [4. API Overview](https://github.com/xcofdk/xcofdk-py/wiki/4.-API-Overview) for an overview of the API of the framework, 
- [6. Basic Examples](https://github.com/xcofdk/xcofdk-py/wiki/6.-Basic-Examples) for introductory examples of 
  (real-world) programs using the framework. <br> 
  Note that most of the examples are applications developed using GUI framework [tkinter](https://docs.python.org/3/library/tkinter.html). 

<br>

# Licensing

[XCOFDK](https://github.com/xcofdk/xcofdk-py) is available under [MIT License](https://github.com/xcofdk/xcofdk-py/blob/master/LICENSE.txt).

<br>

# Links

| Main page            | :      | [XCOFDK on GitHub](https://github.com/xcofdk/xcofdk-py)                                                                                                                                                                                               |
| -------------------  | -----  |----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------                           |
| **Wiki**             | **:**  | [**XCOFDK Wiki**](https://github.com/xcofdk/xcofdk-py/wiki)                                                                                                                                                                                           |
| **API**              | **:**  | [**API Overview**](https://github.com/xcofdk/xcofdk-py/wiki/4.-API-Overview)                                                                                                                                                                          |
| **Examples**         | **:**  | [**xcofdk-py-examples.tar.gz**](https://github.com/xcofdk/xcofdk-py/blob/master/src/xcofdk/tests/xcofdk-py-examples.tar.gz) \| [**xcofdk-py-examples.zip**](https://github.com/xcofdk/xcofdk-py/blob/master/src/xcofdk/tests/xcofdk-py-examples.zip)  |
| **Changelog**        | **:**  | [**Release highlights & release notes**](https://github.com/xcofdk/xcofdk-py/blob/master/doc/release_notes.md#release-highlights-v32)                                                                                                                 |
| **Roadmap**          | **:**  | [**Roadmap of XCOFDK**](https://github.com/xcofdk/xcofdk-py/wiki/1.-Introduction#12-roadmap-of-xcofdk)                                                                                                                                                |
| **License file**     | **:**  | [**MIT License**](https://github.com/xcofdk/xcofdk-py/blob/master/LICENSE.txt)                                                                                                                                                                        |
| **Error reporting**  | **:**  | **error-xpy@xcofdk.de**                                                                                                                                                                                                                               |
