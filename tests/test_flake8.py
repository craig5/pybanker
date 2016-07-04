#!/usr/bin/env python -B
'''
Base tests for python: compile and PEP8.

Specifically, a valid import and flake8.
'''
# python core libraries
import logging
import os
# third party libraries
import flake8.main
import unittest


logger = logging.getLogger(__name__)
__unittest = True


_TEST_DIR = os.path.dirname(__file__)
_BASE_DIR = os.path.dirname(_TEST_DIR)


class TestFlake8(unittest.TestCase):

    @classmethod
    def setup(cls):
        logger.debug('Running setup.')

    @classmethod
    def teardown(cls):
        logger.debug('Running teardown.')

    def test_test_flake8(self):
        dir_name = _TEST_DIR
        logger.debug('Checking dir: {0}'.format(dir_name))
        total_errors = 0
        for cur_file in os.listdir(dir_name):
            full = os.path.join(dir_name, cur_file)
            logger.debug('Checking file: {0}'.format(full))
            total_errors += self._check_file(cur_file, dir_name)
        logger.debug('Total errors: {0}'.format(total_errors))
        assert total_errors == 0

    def _check_file(self, file_name, dir_name):
        full = os.path.join(dir_name, file_name)
        if not os.path.isfile(full):
            logger.debug('Skipping non-file: {0}'.format(full))
            return 0
        # Stupid vim turd files... :(
        if file_name.startswith('.'):
            logger.debug('Skipping dotfile: {0}'.format(file_name))
            return 0
        if not file_name.endswith('.py'):
            logger.debug('Skipping non-py file: {0}'.format(file_name))
            return 0
        full_name = os.path.join(dir_name, file_name)
        logger.info('Checking python file: {0}'.format(full_name))
        num_errors = flake8.main.check_file(full_name)
        if num_errors > 0:
            logger.error('Num errors: {0}'.format(num_errors))
        return num_errors

# End of file.
