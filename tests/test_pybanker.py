#!/usr/bin/env python -B
'''
Base tests for python: compile and PEP8.

Specifically, a valid import and flake8.
'''
# python core libraries
import logging
import os
# third party libraries
import unittest
# custom libraries


logger = logging.getLogger(__name__)
__unittest = True


_TEST_DIR = os.path.dirname(__file__)
_BASE_DIR = os.path.dirname(_TEST_DIR)


class TestComments(unittest.TestCase):

    @classmethod
    def setup(cls):
        logger.debug('Running setup.')

    @classmethod
    def teardown(cls):
        logger.debug('Running teardown.')

    def test_pybanker_load(self):
        import pybanker
        pybanker.Banker()

# End of file.
