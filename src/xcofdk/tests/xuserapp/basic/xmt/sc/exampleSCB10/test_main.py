# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : test_main.py
#
# Copyright(c) 2023-2025 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# PYTHONPATH extension
# ------------------------------------------------------------------------------
import os, sys
_xcoRP = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../../../../../..'))
if _xcoRP.endswith('/src') and os.path.exists(os.path.join(_xcoRP, 'xcofdk')) and _xcoRP not in sys.path: sys.path.extend([_xcoRP])
try:
    import xcofdk
except ImportError:
    exit(f"[{os.path.basename(__file__)}] Failed to import Python package 'xcofdk', missing installation.")
sys.path.extend(((_xua := os.path.normpath(os.path.join(os.path.dirname(__file__), '../../../../..'))) not in sys.path) * [_xua])


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from unittest import TestCase
from unittest import TestSuite

from xuserapp.basic.xmt.sc.exampleSCB10.main import Main


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
def load_tests(loader, tests, pattern):
    res = TestSuite() if tests is None else tests

    tcInst = TCExampleB10()
    res.addTest(tcInst)
    print(f'[load_tests] Added TC instance {type(tcInst).__name__}.')

    return res
#END load_tests()


def LoadTests():
    return load_tests(None, None, None)
#END LoadTests()


class TCExampleB10(TestCase):
    def __init__(self):
        super().__init__(methodName='RunExampleB10Main')

    def RunExampleB10Main(self):
        print()

        retVal = Main()
        self.assertEqual(retVal, 0, f'[TCExampleB10] TC {self._testMethodName} failed.')
        print(f'[TCExampleB10] TC {self._testMethodName} passed.')
#END class TCRunMain


# ------------------------------------------------------------------------------
# Execution
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    from unittest import TextTestRunner as _TextTestRunner

    runner = _TextTestRunner()
    runner.run(LoadTests())
