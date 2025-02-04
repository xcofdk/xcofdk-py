# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# File   : test_main.py
#
# Copyright(c) 2023-2024 Farzad Safa (farzad.safa@xcofdk.de)
# This software is distributed under the MIT License (http://opensource.org/licenses/MIT).
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Import libs / modules
# ------------------------------------------------------------------------------
from unittest import TestCase
from unittest import TestSuite

from xcofdk.tests.userapp.basic.mt.exampleB10.main import Main


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
def load_tests(loader, tests, pattern):
    res = TestSuite() if tests is None else tests

    tcInst = TCRunMain()
    res.addTest(tcInst)
    print(f'[load_tests] Added TC instance {type(tcInst).__name__}.')

    return res
#END load_tests()


def LoadTests():
    return load_tests(None, None, None)
#END LoadTests()


class TCRunMain(TestCase):
    def __init__(self):
        super().__init__(methodName='RunMain')

    def RunMain(self):
        print()

        retVal = Main()
        self.assertEqual(retVal, 0, f'[TCStartXcoFDK] TC {self._testMethodName} failed.')
        print(f'[TCStartXcoFDK] TC {self._testMethodName} passed.')
#END class TCRunMain


# ------------------------------------------------------------------------------
# Execution
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    from unittest import TextTestRunner as _TextTestRunner

    runner = _TextTestRunner()
    runner.run(LoadTests())
