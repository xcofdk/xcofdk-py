# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : cloptions.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# PYTHONPATH extension
# ------------------------------------------------------------------------------
import os, sys
_xcoRP = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../../..'))
if _xcoRP.endswith('/src') and os.path.exists(os.path.join(_xcoRP, 'xcofdk')) and _xcoRP not in sys.path: sys.path.extend([_xcoRP])
try:
    import xcofdk
except ImportError:
    exit(f"[{os.path.basename(__file__)}] Failed to import Python package 'xcofdk', missing installation.")


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from enum   import auto
from enum   import IntEnum
from typing import List
from typing import Union


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
class ECLOptionID(IntEnum):
    # help options
    #
    eH                  = 0
    eHelp               = auto()
    # framework options
    #
    eLogLevel           = auto()
    eFwLogLevel         = auto()
    eDisableLogCS       = auto()
    eDisableLogTS       = auto()
    eDisableLogHL       = auto()
    #
    # common userapp options
    eEnableAutoClose    = auto()
    eDisableAutoStart   = auto()
    eBypassFTGuard      = auto()
    #
    # misc. userapp options
    eSyncStarterTask    = auto()
    eNoMainStarterTask  = auto()
    eAsyncMainTask      = auto()
    eServiceTasksCount  = auto()
    eForceDeficientFreq = auto()
    eFiboInput          = auto()
    eSmallCartProd      = auto()

    @property
    def isHelpOption(self):
        return self.value <= ECLOptionID.eHelp.value

    @property
    def isFwOption(self):
        return ECLOptionID.eHelp.value < self.value <= ECLOptionID.eDisableLogHL.value

    @property
    def isAppOption(self):
        return self.value > ECLOptionID.eDisableLogHL.value
#END class ECLOptionID


class _CLOptionSpec:
    __slots__ = [ '__n' , '__h' , '__d' , '__c' , '__v' , '__bS' , '__bK' ]

    def __init__(self, name_: str, default_, help_: str =None, choices_ : list =None, bKeyValue_ =False):
        self.__c  = choices_
        self.__d  = default_
        self.__h  = help_ if help_ is not None else f'[{name_}]'
        self.__n  = name_
        self.__v  = None
        self.__bK = bKeyValue_ or (choices_ is not None)
        self.__bS = False

    # def __str__(self):
    #     return '[{}] {} , {} , {} , {}'.format(type(self).__name__, self.optionName, self.optionHelp, self.optionDefault)

    @property
    def isSupplied(self):
        return self.__bS

    @isSupplied.setter
    def isSupplied(self, bS_ : bool):
        self.__bS = bS_

    @property
    def isKeyValue(self):
        return self.__bK

    @property
    def optionName(self):
        return self.__n

    @property
    def optionValue(self):
        return self.__v if self.__v is not None else self.__d

    @optionValue.setter
    def optionValue(self, vv_):
        self.__v = vv_

    @property
    def optionDefault(self):
        return self.__d

    @property
    def optionHelp(self):
        return self.__h

    @property
    def optionChoices(self) -> Union[list, None]:
        return self.__c
#END class _CLOptionSpec


class CLOptions:
    __slots__ = [ '__tbl' ]


    # --------------------------------------------------------------------------
    # c-tor / built-in
    # --------------------------------------------------------------------------
    def __init__(self, appOptionIDs_ : Union[List[ECLOptionID], ECLOptionID, None] =None, bAddCommonAppOptions_ =True, bAddHelp_ =True):
        self.__tbl = None

        if appOptionIDs_ is None:
            appOptionIDs_ = []
        elif isinstance(appOptionIDs_, ECLOptionID):
            appOptionIDs_ = [appOptionIDs_]
        self.__tbl = CLOptions.__InitTable(appOptionIDs_, bAddCommonAppOptions_, bAddHelp_)
        if self.__tbl is None:
            return
        self.__ScanCmdLine()
    # --------------------------------------------------------------------------
    # c-tor / built-in
    # --------------------------------------------------------------------------


    # --------------------------------------------------------------------------
    # API
    # --------------------------------------------------------------------------
    @property
    def isValid(self):
        return self.__tbl is not None

    @property
    def isHelpSupported(self):
        if not self.isValid:
            return False
        return (ECLOptionID.eH in self.__tbl) or (ECLOptionID.eHelp in self.__tbl)

    @property
    def isHelpSupplied(self):
        if not (self.isValid and self.isHelpSupported):
            return False
        return self.__tbl[ECLOptionID.eH].isSupplied or self.__tbl[ECLOptionID.eHelp].isSupplied

    @property
    def isAutoStartEnabled(self):
        _id = ECLOptionID.eDisableAutoStart
        return self.isValid and (_id in self.__tbl) and not self.__tbl[_id].optionValue

    @property
    def isAutoCloseEnabled(self):
        _id = ECLOptionID.eEnableAutoClose
        return self.isValid and (_id in self.__tbl) and self.__tbl[_id].optionValue

    @property
    def isSyncStarterTaskEnabled(self):
        _id = ECLOptionID.eSyncStarterTask
        return self.isValid and (_id in self.__tbl) and self.__tbl[_id].optionValue

    @property
    def isMainStarterTaskEnabled(self):
        _id = ECLOptionID.eNoMainStarterTask
        return self.isValid and (_id in self.__tbl) and not self.__tbl[_id].optionValue

    @property
    def isAsynMainTaskEnabled(self):
        _id = ECLOptionID.eAsyncMainTask
        return self.isValid and (_id in self.__tbl) and self.__tbl[_id].optionValue

    @property
    def isForceDeficientFrequencyEnabled(self):
        _id = ECLOptionID.eForceDeficientFreq
        return self.isValid and (_id in self.__tbl) and self.__tbl[_id].optionValue

    @property
    def isSmallCartProdEnabled(self):
        _id = ECLOptionID.eSmallCartProd
        return self.isValid and (_id in self.__tbl) and self.__tbl[_id].optionValue

    @property
    def isFreeThreadingGuardBypassed(self):
        _id = ECLOptionID.eBypassFTGuard
        return self.isValid and (_id in self.__tbl) and self.__tbl[_id].optionValue

    @property
    def serviceTasksCount(self):
        _id = ECLOptionID.eServiceTasksCount
        return 0 if not (self.isValid and (_id in self.__tbl)) else self.__tbl[_id].optionValue

    @property
    def fibonacciInput(self):
        _id = ECLOptionID.eFiboInput
        return 0 if not (self.isValid and (_id in self.__tbl)) else self.__tbl[_id].optionValue

    def GetSuppliedFwOptions(self) -> Union[str, None]:
        if not self.isValid:
            return None

        res = ''
        for _kk, _vv in self.__tbl.items():
            if not _kk.isFwOption:
                continue
            if not _vv.isSupplied:
                continue

            res += f'{_vv.optionName} '
            if _vv.isKeyValue:
                res += f'{_vv.optionValue} '
        return res.strip()

    def PrintUsage(self):
        if self.isValid:
            print()
            print(self.__GetUsage())

    def CleanUp(self):
        if self.isValid:
            self.__tbl.clear()
            self.__tbl = None
    # --------------------------------------------------------------------------
    # API
    # --------------------------------------------------------------------------


    # --------------------------------------------------------------------------
    # Impl
    # --------------------------------------------------------------------------
    @staticmethod
    def __InitTable(appOptionIDs_ : List[ECLOptionID], bAddCommonAppOptions_ : bool, bAddHelp_ : bool) -> Union[dict, None]:
        if not isinstance(appOptionIDs_, list):
            print(f"[UserApp::CLOptions] Got unexpected object type '{type(appOptionIDs_).__name__}' passed in as (list) of option IDs.")
            return None

        # auto-add common userapp options
        _cmn = [ECLOptionID.eEnableAutoClose, ECLOptionID.eDisableAutoStart, ECLOptionID.eBypassFTGuard]
        if bAddCommonAppOptions_:
            for _id in _cmn:
                if _id not in appOptionIDs_:
                    appOptionIDs_.append(_id)

        _fwIDs, _appIDs = [], []
        for _id in appOptionIDs_:
            if not isinstance(_id, ECLOptionID):
                print(f"[UserApp::CLOptions] Got unexpected object type '{type(_id).__name__}' passed in as option ID.")
                return None

            if _id.isFwOption:
                _fwIDs.append(_id)
            else:
                _appIDs.append(_id)
        #END for _id...

        if len(_fwIDs) < 1:
            for _n, _m in ECLOptionID.__members__.items():
                if _m.isFwOption:
                    _fwIDs.append(_m)

        _tbl = dict()

        # help option
        if not bAddHelp_:
            bAddHelp_ = (ECLOptionID.eH in appOptionIDs_) or (ECLOptionID.eHelp in appOptionIDs_)
        if bAddHelp_:
            _tbl[ECLOptionID.eH]    = _CLOptionSpec('-h', False, None, None)
            _tbl[ECLOptionID.eHelp] = _CLOptionSpec('--help', False, None, None)

        # fw options
        for _id in _fwIDs:
            if not _id.isFwOption:
                pass
            elif _id == ECLOptionID.eLogLevel:
                _tbl[_id] = _CLOptionSpec('--log-level', 'info', help_='[--log-level LLEVEL]', choices_='trace debug info warning error'.split())
            elif _id == ECLOptionID.eFwLogLevel:
                _tbl[_id] = _CLOptionSpec('--fw-log-level', 'error', help_='[--fw-log-level FWLLEVEL]', choices_='info kpi warning error'.split())
            elif _id == ECLOptionID.eDisableLogCS:
                _tbl[_id] = _CLOptionSpec('--disable-log-callstack', False)
            elif _id == ECLOptionID.eDisableLogTS:
                _tbl[_id] = _CLOptionSpec('--disable-log-timestamp', False)
            else:  #if _id == ECLOptionID.eDisableLogHL:
                _tbl[_id] = _CLOptionSpec('--disable-log-highlighting' , False)

        # user app options
        for _id in _appIDs:
            if not _id.isAppOption:
                pass
            elif _id == ECLOptionID.eEnableAutoClose:
                _tbl[_id] = _CLOptionSpec('--enable-auto-close', False)
            elif _id == ECLOptionID.eDisableAutoStart:
                _tbl[_id] = _CLOptionSpec('--disable-auto-start', False)
            elif _id == ECLOptionID.eBypassFTGuard:
                _tbl[_id] = _CLOptionSpec('--bypass-free-threading-guard', False)
            elif _id == ECLOptionID.eSyncStarterTask:
                _tbl[_id] = _CLOptionSpec('--sync-starter-task', False)
            elif _id == ECLOptionID.eNoMainStarterTask:
                _tbl[_id] = _CLOptionSpec('--no-main-starter-task', False)
            elif _id == ECLOptionID.eAsyncMainTask:
                _tbl[_id] = _CLOptionSpec('--async-main-task', False)
            elif _id == ECLOptionID.eForceDeficientFreq:
                _tbl[_id] = _CLOptionSpec('--force-deficient-frequency', False)
            elif _id == ECLOptionID.eSmallCartProd:
                _tbl[_id] = _CLOptionSpec('--small-cartesian-product', False)
            elif _id == ECLOptionID.eServiceTasksCount:
                _tbl[_id] = _CLOptionSpec('--service-tasks-count', 12, help_='[--service-tasks-count COUNT]', choices_=['[1..12]'], bKeyValue_=True)
            elif _id == ECLOptionID.eFiboInput:
                _tbl[_id] = _CLOptionSpec('--fibonacci-input', 21, help_='[--fibonacci-input FIBOIN]', choices_=['[19..24]'], bKeyValue_=True)
        return _tbl

    def __GetUsage(self) -> str:
        #_usage = f'Usage:\n\t$> python3 -m {_usage} [--help] [--use-sync-task] [--no-main-task] [--disable-log-timestamp] [--disable-log-highlighting] [--disable-log-callstack]'
        #
        _BN    = os.path.basename(os.path.splitext(sys.argv[0])[0])
        _DIR   = os.path.dirname(sys.argv[0])
        _HDR1  = f'Usage: '
        _HDR2  = f"{len(_HDR1)*' '}$> python3 -m {_BN} "
        _HDR1 += f'$> cd {_DIR}{os.path.sep}'
        _LHDR2 = len(_HDR2)

        res, _ccFW, _ccApp = '', '', ''

        # help options
        for _kk, _vv in self.__tbl.items():
            if not _kk.isHelpOption:
                continue
            res += f'{_vv.optionHelp} '
        if len(res):
            res += f"\n{_LHDR2*' '}"

        _tmp = ''
        # userapp options
        for _kk, _vv in self.__tbl.items():
            if not _kk.isAppOption:
                continue
            _tmp += f'{_vv.optionHelp} '
            if _vv.optionChoices is not None:
                _ph = _vv.optionHelp.lstrip('[').rstrip(']').split()[1]
                _ccApp += "\n{}{:<8} : {}".format(_LHDR2*' ', _ph, ' | '.join(_vv.optionChoices))

        if len(_tmp):
            _tmp += f"\n{_LHDR2*' '}"

        # fw options
        for _kk, _vv in self.__tbl.items():
            if not _kk.isFwOption:
                continue
            _tmp += f'{_vv.optionHelp} '
            if _vv.optionChoices is not None:
                _ph = _vv.optionHelp.lstrip('[').rstrip(']').split()[1]
                _ccFW += "\n{}{:<8} : {}".format(_LHDR2*' ', _ph, ' | '.join(_vv.optionChoices))

        if len(_tmp):
            res += _tmp.rstrip()
            if len(_ccApp):
                res += f'{_ccApp}'
            if len(_ccFW):
                res += _ccFW

        return f'{_HDR1}\n{_HDR2}{res}'

    def __GetSuppliedAppOptions(self) -> Union[str, None]:
        if not self.isValid:
            return None

        res = ''
        for _kk, _vv in self.__tbl.items():
            if not _kk.isAppOption:
                continue
            if not _vv.isSupplied:
                continue

            res += f'{_vv.optionName} '
            if _vv.isKeyValue:
                res += f'{_vv.optionValue} '
        return res.strip()

    def __ScanCmdLine(self) -> bool:
        _args = []

        _NARGS = len(sys.argv)
        if _NARGS < 1:
            return True

        _ii = 0
        while True:
            _ii += 1
            if _ii >= _NARGS:
                break

            _aa = sys.argv[_ii]
            if _aa.startswith('#'):
                break
            _args.append(_aa)

        self.__ScanHelp(_args)
        if self.isHelpSupplied:
            self.PrintUsage()
            return True

        res = self.__ScanOptions(_args, bFwOptions_=True)
        res = res and self.__ScanOptions(_args, bFwOptions_=False)
        if not res:
            self.CleanUp()
        elif len(_args):
            print('[UserApp::CLOptions] Ignored unrecognized and/or repeated CmdLine option(s) below:\n\t{}\n'.format(' '.join(_args)))
        return res

    def __ScanHelp(self, args_ : List[str]):
        if not self.isHelpSupported:
            return
        _hspec    = self.__tbl[ECLOptionID.eH]
        _helpSpec = self.__tbl[ECLOptionID.eHelp]

        for _aa in args_:
            if (_aa != _hspec.optionName) and (_aa != _helpSpec.optionName):
                continue
            if _aa == _hspec.optionName:
                _hspec.isSupplied  = True
                _hspec.optionValue = True
            else:
                _helpSpec.isSupplied  = True
                _helpSpec.optionValue = True

    def __ScanOptions(self, args_ : List[str], bFwOptions_ =True) -> bool:
        _NARGS, _rm = len(args_), []

        for _kk, _vv in self.__tbl.items():
            if _kk.isHelpOption:
                continue
            if bFwOptions_ and not _kk.isFwOption:
                continue
            if (not bFwOptions_) and not _kk.isAppOption:
                continue
            if not _vv.optionName in args_:
                continue

            _optn = _vv.optionName
            _rm.append(_optn)
            _vv.isSupplied = True
            if not _vv.isKeyValue:
                _vv.optionValue = True
                continue
            _idx = args_.index(_optn)
            if _idx >= (_NARGS-1):
                print(f"[UserApp::CLOptions] Missing value specification for CmdLine option '{_optn}'.")
                return False

            _val = args_[_idx+1]
            _rm.append(_val)

            _bFiboInput  = _kk == ECLOptionID.eFiboInput
            _bSrvTsksCnt = _kk == ECLOptionID.eServiceTasksCount
            if _bSrvTsksCnt or _bFiboInput:
                _FIBO_INPUT_MIN     = 19
                _FIBO_INPUT_MAX     = 24
                _FIBO_INPUT_DEFAULT = 21
                _MIN_NUM_SRV_TASKS  = 1
                _MAX_NUM_SRV_TASKS  = 12
                _FALLBACK_VAL       = _FIBO_INPUT_DEFAULT if _bFiboInput else _MAX_NUM_SRV_TASKS

                _min = _FIBO_INPUT_MIN if _bFiboInput else _MIN_NUM_SRV_TASKS
                _max = _FIBO_INPUT_MAX if _bFiboInput else _MAX_NUM_SRV_TASKS
                try:
                    _cnt = int(_val)
                    if not (_min <= _cnt <= _max):
                        _cnt = _FALLBACK_VAL
                        if _bFiboInput:
                            print(f"[UserApp::CLOptions] Submitted Fibonacci input number '{_val}' is out of the range, fall back to default value of {_cnt}, valid range: [{_min}..{_max}]")
                        else:
                            print(f"[UserApp::CLOptions] Submitted service tasks number '{_val}' is out of the range, fall back to default value of {_cnt}, valid range: [{_min}..{_max}]")
                except (ValueError, Exception) as _xcp:
                    _cnt = _FALLBACK_VAL
                    if _bFiboInput:
                        print(f"[UserApp::CLOptions] Got exception below while evaluating submitted Fibnnacci input number '{_val}', fall back to default value of {_cnt}\n\t{_xcp}\n")
                    else:
                        print(f"[UserApp::CLOptions] Got exception below while evaluating submitted service tasks number '{_val}', fall back to default value of {_cnt}\n\t{_xcp}\n")
                _vv.optionValue = _cnt
            else:
                _vv.optionValue = _val

                if _vv.optionChoices is not None:
                    if _val not in _vv.optionChoices:
                        _ccFW = ' | '.join(_vv.optionChoices)
                        print(f"[UserApp::CLOptions] Found invalid value specification for CmdLine option '{_optn}', valid values are:\n\t{_ccFW}")
                        return False
        #END for _kk...

        for _aa in _rm:
            args_.remove(_aa)
        return True
    # --------------------------------------------------------------------------
    #END Impl
    # --------------------------------------------------------------------------
#END class CLOptions


def GetCmdLineOptions(appOptionIDs_ : Union[List[ECLOptionID], ECLOptionID, None] =None, bAddCommonAppOptions_ =True, bAddHelp_ =True) -> Union[CLOptions, None]:
    res = CLOptions(appOptionIDs_=appOptionIDs_, bAddCommonAppOptions_=bAddCommonAppOptions_, bAddHelp_=bAddHelp_)
    if not res.isValid:
        res = None
    return res
