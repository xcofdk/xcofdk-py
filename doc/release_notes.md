<font size="7">XCOFDK-py - Release Notes</font> <br>
<table>
  <tr>
    <th></th>
    <th></th>
    <th></th>
  </tr>
  <tr>
     <td>Version</td>
     <td>:</td>
     <td>1.9</td>
  </tr>
  <tr>
     <td>Date</td>
     <td>:</td>
     <td>24.10.2025</td>
  </tr>
  <tr>
     <td>&copy<c>Copyright</c></td>
     <td>:</td>
     <td>2023-2025 Farzad Safa (<a href>farzad.safa@xcofdk.de</a>)</td>
  </tr>
  <tr>
     <td> </td>
     <td></td>
     <td>All rights reserved.</td>
  </tr>
  <tr>
     <td> </td>
     <td> </td>
     <td> </td>
  </tr>
</table>

<br>


# Table of Contents
<!-- TOC depthFrom:1 depthTo:6 withLinks:1 updateOnSave:1 orderedList:0 -->
- [Table of Contents](#table-of-contents)
  - [Release Highlights](#release-highlights)
    - [Release Highlights v3.2](#release-highlights-v32)
    - [Release Highlights v3.1](#release-highlights-v31)
    - [Release Highlights v3.0](#release-highlights-v30)
    - [Release Highlights v2.1](#release-highlights-v21)
  - [Release Notes](#release-notes)
    - [Release Notes v3.2 - 24.10.2025](#release-notes-v32---24102025)
    - [Release Notes v3.1 - 30.09.2025](#release-notes-v31---30092025)
    - [Release Notes v3.0 - 12.06.2025](#release-notes-v30---12062025)
    - [Release Notes v2.1 - 04.02.2025](#release-notes-v21---04022025)
    - [Release Notes v2.0.1 - 19.11.2024](#release-notes-v201---19112024)
    - [Release Notes v2.0 - 11.11.2024](#release-notes-v20---11112024)
<!-- /TOC -->

<br>

## Release Highlights

### Release Highlights v3.2

- The framework now officially supports free-threaded (FT) Python:
  - The framework considers the stable version <tt>3.14.0</tt> the first Python version officially supporting 
    *free-threaded (FT)*.
  - Also, the framework now considers Python versions <tt>3.13</tt> and pre-releases of the stable version 
    <tt>3.14.0</tt> supporting *experimental free-threaded*. <br> 
    If built with the build configuration for disabling <tt>GIL</tt>, for these interpreter versions use of the RTE 
    configuration policy via the API function below still remains mandatory: <br>
    <tt>rtecfg.RtePolicyBypassExperimentalFreeThreadingGuard()</tt>
  - See also new API functions below: 
    - <tt>fwutil.IsFTPythonVersion()</tt>
    - <tt>fwutil.IsExperimentalFTPythonVersion()</tt>

[TOC](#table-of-contents)
______

<br>


### Release Highlights v3.1

- Introduction of public api function <tt>fwutil.GetLcFailure()</tt>.
- Introduction of RTE configuration policy for disabling console output:
  - <tt>rtecfg.RtePolicyDisableLogRDConsoleSink()</tt>
- Introduction of RTE configuration policy for redirection of logging output to file sink:
  - <tt>rtecfg.RtePolicyEnableLogRDFileSink()</tt>
- Introduction of RTE configuration policy for redirection of logging output to TCP sink:
  - <tt>rtecfg.RtePolicyEnableLogRDTcpSink()</tt>
- Task/process alias name is now allowed to be a printable. non-empty string literal without spaces.
- [DEPRECATED] Task state property <tt>ITask.isAborting</tt> is deprecated now:
  - with <tt>False</tt> is always returned,
  - <tt>ITask.isFailed</tt> shall be used instead.

[TOC](#table-of-contents)
______

<br>


### Release Highlights v3.0

- Complete refactoring of the public API of package <tt>xcofdk</tt>:
  - re-organized the API on a *by-subsystem* basis,
  - interface classes have been introduced: 
    - to avoid possible, undesiered issue of cyclic import, 
    - to avoid possible layout conflicts when task classes part of a multiple inheritance,
    - to ease access to task (or other) object instances created elsewhere
    - to improve type annotations.
- Introduction of pre-start configuration of the framework by RTE policy items and related API functions:
  - <tt>rtecfg.RtePolicyGetConfig()</tt>
  - <tt>rtecfg.RtePolicyConfigure()</tt>
  - <tt>rtecfg.RtePolicyEnableAutoStop()</tt>
  - <tt>rtecfg.RtePolicyEnableTerminalMode()</tt>
  - <tt>rtecfg.RtePolicyEnableForcedAutoStop()</tt>
  - <tt>rtecfg.RtePolicyDisableSubSystemMessaging()</tt>
  - <tt>rtecfg.RtePolicyDisableSubSystemMultiProcessing()</tt>
  - <tt>rtecfg.RtePolicyBypassExperimentalFreeThreadingGuard()</tt>
  - <tt>rtecfg.RtePolicyDisableExceptionTrackingOfChildProcesses()</tt>
- Introduction of class <tt>RCTask</tt> (and its derived classes) for rapid construction of task instances by simply <br>
  passing callable objects (as opposed to mandatory subclassing of the abstract classes <tt>XTask</tt> and <tt>XMainTask</tt>):
  - <tt>class SyncTask</tt>
  - <tt>class AsyncTask</tt>
  - <tt>class SyncCommTask</tt>
  - <tt>class AsyncCommTask</tt>
  - <tt>class MessageDrivenTask</tt>
  - <tt>class XFSyncTask</tt>
  - <tt>class XFAsyncTask</tt>
  - <tt>class XFSyncCommTask</tt>
  - <tt>class XFAsyncCommTask</tt>
  - <tt>class XFMessageDrivenTask</tt>
- Introduction of new API functions/properties of task instances of both classes <tt>RCTask</tt> and <tt>XTask</tt>:
  - <tt>isMainTask)</tt>
  - <tt>isCanceling</tt>
  - <tt>isPendingRun</tt>
  - <tt>Cancel()</tt>
  - <tt>SelfCheck()</tt>
  - <tt>SelfCheckSleep()</tt>
  - <tt>SendMessage()</tt>
  - <tt>BroadcastMessage()</tt>
  - <tt>GetTaskOwnedData()</tt>
  - <tt>SetTaskOwnedData()</tt>
- Provide new API functions to enable access to currently running task instance:
  - <tt>GetCurTask() -> IRCTask | IRCCommTask</tt>
  - <tt>GetCurXTask() -> IXTask</tt>
- Refactoring of class <tt>XProcess</tt>:
  - to enable rapid construction of child processes with no obligation to have to deal with framework-specific data types,
  - to provide the new feature of *exception tracking* of child processes when executed,
  - to provide a new API function to terminate a child process.
- New API functions to wait for termination (of a subset) of running tasks or child processes:
  - <tt>fwapi.JoinTasks()</tt>
  - <tt>fwapi.JoinProcesses()</tt>
- New API function to terminate (a subset) of running child processes:
  - <tt>fwapi.TerminateProcesses()</tt>
- Default start options of the framework properly arranged in a way commonly expected for an application deployed in release mode.
- Two new framework start options are available now:
  - <tt>--fw-log-level</tt>
  - <tt>--disable-log-callstack</tt> <br>
    (<tt>--enable-log-callstack</tt> has been removed).

[TOC](#table-of-contents)
______

<br>


### Release Highlights v2.1

- Tasks can send messages even if in teardown phase.
- Support of positional and/or keyword arguments passed to tasks when started.
- All user or fatal errors submitted by the framework are given a pre-defined, unique error code.
- Synchronous tasks can be configured to have a cyclic run phase, too.
- Two new framework start options are available now:
  - <tt>--enable-log-callstack</tt>
  - <tt>--suppress-start-preamble</tt>

[TOC](#table-of-contents)
______

<br>


## Release Notes

### Release Notes v3.2 - 24.10.2025

- XPY-369 – Update doc: source code, readme and release notes
- XPY-368 – Enable official support of free-threaded Python

[TOC](#table-of-contents)
______

<br>


### Release Notes v3.1 - 30.09.2025

- XPY-366 – Update readme and release notes
- XPY-359 – Introduce public api function <tt>GetLcFailure()</tt>
- XPY-358 – Deprecated: Task state property <tt>isAborting</tt> is deprecated now
- XPY-357 – Allow task/process alias name to be a printable. non-empty string literal without spaces
- XPY-350 – Introduce RTE policy for redirection of logging output to TCP sink
- XPY-349 – Introduce RTE policy for redirection of logging output to file sink
- XPY-347 – Introduce RTE policy for disabling console output
- XPY-345 – Bugfix: Sporadically exception raised while determining current running task
- XPY-341 – Bugfix: <tt>isFailed</tt> returns wrong value upon failure (especially for async. tasks)
- XPY-328 – Bugfix: Creating a child process before start of the framework ends up with an exception
- XPY-316 – Bugfix: Sporadically wrong exit code of child process

[TOC](#table-of-contents)
______

<br>


### Release Notes v3.0 - 12.06.2025

- XPY-327 – Update readme and release notes
- XPY-314 – Rename public API module <tt>curxtask</tt> and its API
- XPY-311 – Introduce public API property <tt>IXTask.isMainTask</tt>
- XPY-310 – Introduce public API property <tt>ITask.isPendingRun</tt>
- XPY-308 – Re-organize subpackage <tt>fwapi.rtecfg</tt>
- XPY-298 – Provide framework start option <tt>--disable-log-callstack</tt>
- XPY-299 – Remove framework start option <tt>--enable-log-callstack</tt>
- XPY-297 – Introduce public API subpackage <tt>fwapi.fwctrl</tt>
- XPY-293 – Bugfix: Send failure when a task is going to be stopped
- XPY-290 – Bugfix: Failure regarding list of joinable child processes
- XPY-285 – Provide API functions <tt>SendMessage()</tt> and <tt>BroadcastMessage()</tt> for task instances
- XPY-280 – Refactoring: Implementation of class <tt>XTask</tt>
- XPY-272 – Provide public API function <tt>TerminateProcesses()</tt>
- XPY-269 – Rework default settings of start options
- XPY-266 – Provide basic examples for RC tasks
- XPY-264 – Introduce RTE policy for disabling exception tracking of child processes
- XPY-263 – Refactoring: Implementation of class <tt>XTaskException</tt>
- XPY-258 – Provide public API <tt>XProcess.processException</tt>
- XPY-256 – Provide public API <tt>XProcess.Terminate()</tt>
- XPY-255 – Close host process resources if terminated
- XPY-253 – Refactoring: Implementation of class <tt>XTaskProfile</tt>
- XPY-251 – Provide property <tt>XProcess.aliasName</tt>
- XPY-249 – Introduce public API <tt>XTask.taskCompoundUID</tt>
- XPY-248 – Refactoring: Construction of instances of class <tt>XProcess</tt>
- XPY-246 – Missing return value of <tt>XProcess.Join()</tt>
- XPY-244 – Provide timeout implementation of <tt>XProcess.Join()</tt>
- XPY-242 – Provide public API function <tt>SelfCheck()</tt> of tasks
- XPY-235 – Introduce public API function <tt>JoinProcesses()</tt>
- XPY-234 – Refactoring: Top-level design and layout of subpackage <tt>xcofdk.fwapi</tt>
- XPY-230 – Refactoring: Implementation of <tt>ToString()</tt>
- XPY-229 – Introduce RTE policy items for disabling specific subsystems
- XPY-225 – Refactoring: Implementation of dependency injection
- XPY-223 – Refactoring: Implementation of class <tt>XProcess</tt>
- XPY-218 – Re-organize existing basic examples for SC tasks
- XPY-217 – Allow message posting even for tasks with no external queue support
- XPY-216 – Introduce public API function <tt>JoinTasks()</tt>
- XPY-215 – Provide public API <tt>GetCurXTask()</tt>
- XPY-212 – Refactoring: Implementation of default logging config
- XPY-210 – Refactoring: Implementation of subsystem <tt>fwerrh</tt>
- XPY-208 – Arrange public availability of framework start option <tt>--fw-log-level</tt>
- XPY-202 – Provide public API <tt>GetCurTask()</tt>
- XPY-195 – Introduce new API function <tt>Cancel()</tt> of tasks
- XPY-189 – Design and implementation of class <tt>RCTask</tt>
- XPY-185 – Introduce read/write API for task-owned, user-specific data of tasks
- XPY-178 – Introduce new public API class <tt>RteConfig</tt>
- XPY-103 – Introuduce RTE policy items for both auto-stop and terminal mode
- Total of 64 additional planned PM issues mostly related to stability, ease of use, re-organization and clean code.

[TOC](#table-of-contents)
______

<br>


### Release Notes v2.1 - 04.02.2025

- XPY-172 – Bugfix: Resolve typo by wrong getter to access message header.
- XPY-171 – Bugfix: Resolve typo related to cmdline option <tt>'--fibonacci-input'</tt> of example applications.
- XPY-162 – Bugfix: Increment of messaging error counter of multithreaded userapp examples.
- XPY-154 – Support of positional and/or keyword arguments passed to tasks when started.
- XPY-150 – Refactoring: detailed design and implementation of (limited) RTE modes.
- XPY-148 – Enable message sending in teardown-phase of tasks.
- XPY-134 – Rework output format of LC failures.
- XPY-125 – Provide framework start option <tt>'--suppress-start-preamble'</tt>.
- XPY-124 – Provide framework start option <tt>'--enable-log-callstack'</tt>.
- XPY-120 – Bugfix: Error logging not working after start of synchronous tasks.
- XPY-119 – Bugfix: Framework gets stuck if application missed to stop it before joining.
- XPY-115 – Make synchronous tasks may have cyclic run-phase, too.
- XPY-110 – Provide pre-defined error codes for errors reported by the framework.
- Total of 26 additional known and/or planned PM issues mostly related to stability.

[TOC](#table-of-contents)
______

<br>


### Release Notes v2.0.1 - 19.11.2024

- Add command line option of userapp basic examples to print out a usage hint.
- Bugfix regarding scan of command line arguments of userapp basic examples.

[TOC](#table-of-contents)
______

<br>


### Release Notes v2.0 - 11.11.2024

- Created release v2.0.

[TOC](#table-of-contents)
______
