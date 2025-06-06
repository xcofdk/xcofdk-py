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

The console program [quickStart.py](https://github.com/xcofdk/xcofdk-py/blob/master/src/xcofdk/tests/xuserapp/basic/xmt/rc/quickStart.py) 
demonstrates (partly advanced) use of the framework of [XCOFDK for Python](https://github.com/xcofdk/xcofdk-py) 
illustrating many of its features available for applications developed for multitasking. Its task model is composed of:
- a message-driven server task, an instance of class <tt>MessageDrivenTask</tt>,
- an (a)synchronous starter (or main) task, an instance of class <tt>AsyncTask</tt> or <tt>SyncTask</tt>,
- a few asynchronous client tasks, instances of class <tt>AsyncTask</tt>.

The usage of the program is as shown below:
```bash
$> python3.12 -m quickStart --help
Usage: $> cd .../src/xcofdk/tests/xuserapp/basic/xmt/rc/
       $> python3 -m quickStart [-h] [--help] 
                                [--sync-starter-task] [--no-main-starter-task] [--small-cartesian-product] [--bypass-free-threading-guard] 
                                [--log-level LLEVEL] [--fw-log-level FWLLEVEL] [--disable-log-callstack] [--disable-log-timestamp] [--disable-log-highlighting]
                                LLEVEL   : trace | debug | info | warning | error
                                FWLLEVEL : info | kpi | warning | error
$> 
```

The bullet points below give a (schematic) description of program's purpose and structure (refer to 
[quickStart.py](https://github.com/xcofdk/xcofdk-py/blob/master/src/xcofdk/tests/xuserapp/basic/xmt/rc/quickStart.py)) 
for full version of the source code).

- **Purpose of program:** <br>
  The application is supposed to provide the execution of a given algorithm, here <tt>CartProdAlgo</tt>, several times 
  using both multithreading and multiprocessing. <br> 
  Each time an execution is requested, the algorithm constructs a random *Cartesian Product* (CP) and properly returns 
  the result to the requestor, which is either an application task or a child process. <br>
  For example, the output of the program should look like below if executed with the command line option 
  <tt>--small-cartesian-product</tt> supplied:

    ```bash
    $> python3.12 -m quickStart --small-cartesian-product
    ...
    [10:34:26.056 XINF] Welcome to XCOFDK in TerminalMode of RTE.
    [10:34:26.058 XINF][Tsk_501002] Running async. MainTask, current host thread: Tsk_501002
    [10:34:26.078 XINF][CTsk_501001] Task AlgoSrv received first delivered message.
    [10:34:26.135 XINF][Tsk_501002] Starting 5x child processes...
    [10:34:26.244 XINF][Tsk_501002] Starting 5x async. algo-client tasks...
    [10:34:26.795 XINF][CTsk_501001] Put request to stop the framework.
    [10:34:27.071 XINF] Got total of 29x CartProdAlgo executions:
        [10:34:26.080][TID:501001:AlgoSrv]  digitSet='230464'   size=7776     tail:   44443 ,  44440 ,  44444 ,  44446 ,  44444
        [10:34:26.080][TID:501002]          digitSet='642920'   size=7776     tail:   00004 ,  00002 ,  00009 ,  00002 ,  00000
        [10:34:26.194][PID:6416]            digitSet='9344143'  size=117649   tail:  333334 , 333334 , 333331 , 333334 , 333333
        [10:34:26.203][PID:6417]            digitSet='4445617'  size=117649   tail:  777774 , 777775 , 777776 , 777771 , 777777
        [10:34:26.239][PID:6418]            digitSet='6584554'  size=117649   tail:  444448 , 444444 , 444445 , 444445 , 444444
        [10:34:26.256][TID:501003]          digitSet='448984'   size=7776     tail:   44444 ,  44448 ,  44449 ,  44448 ,  44444
        [10:34:26.259][TID:501004:AlgoC_4]  digitSet='558330'   size=7776     tail:   00005 ,  00008 ,  00003 ,  00003 ,  00000
        [10:34:26.269][TID:501006:AlgoC_6]  digitSet='776740'   size=7776     tail:   00007 ,  00006 ,  00007 ,  00004 ,  00000
        [10:34:26.275][TID:501003:AlgoC_3]  digitSet='853336'   size=7776     tail:   66665 ,  66663 ,  66663 ,  66663 ,  66666
        [10:34:26.280][TID:501005]          digitSet='898731'   size=7776     tail:   11119 ,  11118 ,  11117 ,  11113 ,  11111
        [10:34:26.288][PID:6419]            digitSet='7164156'  size=117649   tail:  666666 , 666664 , 666661 , 666665 , 666666
        [10:34:26.295][PID:6420]            digitSet='1189117'  size=117649   tail:  777778 , 777779 , 777771 , 777771 , 777777
        [10:34:26.296][TID:501007]          digitSet='563531'   size=7776     tail:   11116 ,  11113 ,  11115 ,  11113 ,  11111
        [10:34:26.318][TID:501003]          digitSet='597979'   size=7776     tail:   99999 ,  99997 ,  99999 ,  99997 ,  99999
        [10:34:26.319][TID:501004]          digitSet='665646'   size=7776     tail:   66666 ,  66665 ,  66666 ,  66664 ,  66666
        [10:34:26.320][TID:501003:AlgoC_3]  digitSet='711602'   size=7776     tail:   22221 ,  22221 ,  22226 ,  22220 ,  22222
        [10:34:26.327][TID:501005:AlgoC_5]  digitSet='169842'   size=7776     tail:   22226 ,  22229 ,  22228 ,  22224 ,  22222
        [10:34:26.343][TID:501004:AlgoC_4]  digitSet='585428'   size=7776     tail:   88888 ,  88885 ,  88884 ,  88882 ,  88888
        [10:34:26.362][TID:501006]          digitSet='543092'   size=7776     tail:   22224 ,  22223 ,  22220 ,  22229 ,  22222
        [10:34:26.379][TID:501007:AlgoC_7]  digitSet='758838'   size=7776     tail:   88885 ,  88888 ,  88888 ,  88883 ,  88888
        [10:34:26.405][TID:501004]          digitSet='157746'   size=7776     tail:   66665 ,  66667 ,  66667 ,  66664 ,  66666
        [10:34:26.406][TID:501005]          digitSet='887103'   size=7776     tail:   33338 ,  33337 ,  33331 ,  33330 ,  33333
        [10:34:26.433][TID:501006:AlgoC_6]  digitSet='473863'   size=7776     tail:   33337 ,  33333 ,  33338 ,  33336 ,  33333
        [10:34:26.451][TID:501005:AlgoC_5]  digitSet='606221'   size=7776     tail:   11110 ,  11116 ,  11112 ,  11112 ,  11111
        [10:34:26.494][TID:501007]          digitSet='888171'   size=7776     tail:   11118 ,  11118 ,  11111 ,  11117 ,  11111
        [10:34:26.517][TID:501006]          digitSet='178848'   size=7776     tail:   88887 ,  88888 ,  88888 ,  88884 ,  88888
        [10:34:26.586][TID:501007:AlgoC_7]  digitSet='965081'   size=7776     tail:   11116 ,  11115 ,  11110 ,  11118 ,  11111
        [10:34:26.793][TID:501002]          digitSet='822035'   size=7776     tail:   55552 ,  55552 ,  55550 ,  55553 ,  55555
        [10:34:26.794][TID:501001:AlgoSrv]  digitSet='588403'   size=7776     tail:   33338 ,  33338 ,  33334 ,  33330 ,  33333
    [10:34:27.071 XINF] Done.
    ```

- **Import of needed API:** <br>
  e.g. the above-mentioned CP-algo <tt>CartProdAlgo</tt>, or task classes <tt>AsyncTask</tt>, <tt>MessageDrivenTask</tt> 
  etc.:
  
    ```python
    # file : quickStart.py
    # ...

    from xcofdk       import fwapi
    from xcofdk.fwapi import rtecfg
    from xcofdk.fwcom import EExecutionCmdID, EXmsgPredefinedID
    from xcofdk.fwapi import SyncTask, AsyncTask, MessageDrivenTask, IRCTask
    from xcofdk.fwapi import GetCurTask, IMessage, XProcess, xlogif

    from xuserapp.util.cloptions   import ECLOptionID, CLOptions, GetCmdLineOptions
    from xuserapp.util.userAppUtil import CartProdAlgo, DisableBigCartProd

    class EMsgLabel(IntEnum):
        DontCare    = EXmsgPredefinedID.MinUserDefinedID.value
        AlgoRequest = auto()
        Quit        = auto()
    ```

- **Main function:** <br>

    ```python
    def Main(cmdLineOpts_ : CLOptions):
        # step 1: configure framework's RTE for terminal mode and/or
        #         free-threaded Python (if enabled via CmdLine)
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
        #         (which will create and start both child process and client tasks, too)
        _count, _procPool = 5, []
        _starterTsk = CreateStartStarterTask(cmdLineOpts_, _algoSrv.taskUID, _count, _procPool)

        # step 5: wait for running child processes to complete
        fwapi.JoinProcesses()
        _procPoolRes = [ _pp.processSuppliedData for _pp in _procPool if _pp.processSuppliedData is not None ]

        # step 6: wait for framework's coordinated shutdown
        _bLcErrorFree = fwapi.JoinXcoFW()

        # step 7: collect and print out results of CP requests executed
        if _bLcErrorFree:
            _cp  = _procPoolRes + _starterTsk.GetTaskOwnedData() + _algoSrv.GetTaskOwnedData()
            _cp.sort(key=lambda _ee: _ee.cartProdTimestamp)
            _cpLEN = len(_cp)
            _cp = '\n\t'.join( [str(_ee) for _ee in _cp] )

            xlogif.LogInfo(f'Got total of {_cpLEN}x CartProdAlgo executions:\n\t{_cp}')
            xlogif.LogInfo('Done.')

        # done: check for LC failure (if any)
        res = 72 if not _bLcErrorFree else 0
        return res
    ```

- **Callback of message-driven algo-server task:** <br>
  responsible to process CP-requests or other messages sent by algo clients or starter task. <br>
  The server is also responsible to stop the frameworks, if it was started in <tt>TerminalMode</tt>: 

    ```python
    def AlgoServerCBTgt(myTsk_ : IRCTask, msg_ : IMessage) -> EExecutionCmdID:
        # ...
        _lbl = msg_.msgHeader.msgLabel

        # dont-care message?
        if _lbl == EMsgLabel.DontCare:
            # ignore, wait for next message
            return EExecutionCmdID.CONTINUE

        # request to quit?
        if _lbl != EMsgLabel.AlgoRequest:
            # put last own CP-request
            CartProdAlgo(tid_=f'{myTsk_.taskUID}:{myTsk_.aliasName}')

            # framework has been started in TerminalMode?
            if rtecfg.RtePolicyGetConfig().isTerminalModeEnabled:
                # instruct the framework to stop
                fwapi.StopXcoFW()
                xlogif.LogInfo(f'Put request to stop the framework.')

            # stop the algo-server
            return EExecutionCmdID.STOP

        # put a new CP-request on behalf of the sender
        CartProdAlgo(tid_=msg_.msgHeader.msgSender)

        # wait for next message
        return EExecutionCmdID.CONTINUE
    ```

- **Callback of async. algo-client tasks:** <br>
  responsible to provide next CP-request:

    ```python
    def AlgoClientCBTgt(myTsk_ : IRCTask, srvUID_ : int) -> EExecutionCmdID:
        # already done 4x CP-requests?
        if myTsk_.currentRunPhaseIterationNo >= 4:
            # stop running
            return EExecutionCmdID.STOP

        # delegate next CP-request to algo-server, or do it yourself
        _bDelegate = (myTsk_.taskCompoundUID.instNo + myTsk_.currentRunPhaseIterationNo) % 2
        if _bDelegate:
            myTsk_.SendMessage(srvUID_, EMsgLabel.AlgoRequest)
        else:
            CartProdAlgo(tid_=f'{myTsk_.taskUID}:{myTsk_.aliasName}')

        # continue running
        return EExecutionCmdID.CONTINUE
    ```

- **Callback of (a)sync. starter task:** <br>
  responsible to start both child processes (i.e. instances of class <tt>XProcess</tt>) and client tasks waiting for 
  the termination of clients. <br> 
  It also collects the CP-results of the clients before requesting the algo-server to quit.

    ```python
    def StarterTaskCBTgt(srvUID_ : int, count_ : int, procPool_ : List[XProcess]) -> EExecutionCmdID:
        _curTsk = GetCurTask()
        #...

        # send first CP-request to algo-server
        _curTsk.SendMessage(srvUID_, EMsgLabel.AlgoRequest)

        # create and start child processes
        procPool_ += CreateStartAlgoProcesses(count_)

        # create and start client tasks
        _clientPool = CreateStartAlgoClients(count_, srvUID_)

        # wait for termination of client tasks
        fwapi.JoinTasks([_cc.taskUID for _cc in _clientPool])

        # collect the CP-results of client tasks and store them as own (user) data
        _ud = []
        for _cc in _clientPool:
            if _cc.GetTaskOwnedData() is not None:
                _ud += _cc.GetTaskOwnedData()
        _curTsk.SetTaskOwnedData(_ud)

        # send one last CP-request to algo-server
        _curTsk.SendMessage(srvUID_, EMsgLabel.AlgoRequest)

        # put request to algo-server to quit
        _curTsk.SendMessage(srvUID_, EMsgLabel.Quit)

        # done, stop the starter task
        return EExecutionCmdID.STOP
    ```

- **Helper functions:** <br>

    ```python
    def CreateStartAlgoProcesses(count_ : int) -> List[XProcess]:
        #...
    def CreateStartAlgoClients(count_ : int, srvUID_ : int) -> list:
        #...
    def CreateStartStarterTask(cmdLineOpts_ : CLOptions, srvUID_ : int, count_ : int, procPool_ : List[XProcess]):
        #...
    ```
<br>

More introductory information relared to [XCOFDK for Python](https://github.com/xcofdk/xcofdk-py) available on the 
wiki pages below: 
- [1. Introduction](https://github.com/xcofdk/xcofdk-py/wiki/1.-Introduction) for an overview of the framework and 
  roadmap of XCOFDK,
- [2. Quick Start](https://github.com/xcofdk/xcofdk-py/wiki/2.-Quick-Start) explaining the above console program
  in more detail,
- [3. Architecture](https://github.com/xcofdk/xcofdk-py/wiki/3.-Architecture) for the design and subsystems of the 
  framework,
- [4. At a Glance](https://github.com/xcofdk/xcofdk-py/wiki/4.-At-a-Glance) for basic features of the framework,
- [7. Basic Examples](https://github.com/xcofdk/xcofdk-py/wiki/7.-Basic-Examples) for introductory examples of 
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
| **Roadmap**          | **:**  | [**Roadmap of XCOFDK**](https://github.com/xcofdk/xcofdk-py/wiki/1.-Introduction#roadmap-of-xcofdk)                                                                                                                                                   |
| **API**              | **:**  | [**API documentation**](https://github.com/xcofdk/xcofdk-py/wiki/6.-API-Documentation)                                                                                                                                                                |
| **Examples**         | **:**  | [**xcofdk-py-examples.tar.gz**](https://github.com/xcofdk/xcofdk-py/blob/master/src/xcofdk/tests/xcofdk-py-examples.tar.gz) \| [**xcofdk-py-examples.zip**](https://github.com/xcofdk/xcofdk-py/blob/master/src/xcofdk/tests/xcofdk-py-examples.zip)  |
| **Changelog**        | **:**  | [**Release highlights & release notes**](https://github.com/xcofdk/xcofdk-py/blob/master/doc/release_notes.md#release-highlights-v30)                                                                                                                 |
| **License file**     | **:**  | [**MIT License**](https://github.com/xcofdk/xcofdk-py/blob/master/LICENSE.txt)                                                                                                                                                                        |
| **Error reporting**  | **:**  | **error-xpy@xcofdk.de**                                                                                                                                                                                                                               |
