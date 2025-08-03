#!/usr/bin/env python -B
"""
Some generic utilities for the tests.


The name of this package is a little odd...
The test collector (nose) will grab anything that starts with "test_".
So, I avoided that prefix and this was the best I could come up with...

TODO: verify this filename since moving away from nose.
Eg I think pytest uses a standard name for shared routines.
"""
import logging
import os
import unittest

import flake8.api.legacy


class BaseTestCase(unittest.TestCase):
    logger_level = logging.WARN
    others_level = logging.WARN

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_logger()
        self.package_name = 'pybanker'
        self.test_dir = os.path.dirname(__file__)
        self.base_dir = os.path.dirname(self.test_dir)
        self.lib_dir = os.path.join(self.base_dir, 'lib')

    def setup_logger(self):
        logger_name = self.__class__.__name__
        format_string = '[%(levelname)s]'
        format_string += ' - %(message)s'
        logging.basicConfig(format=format_string, level=self.logger_level)
        self.logger = logging.getLogger(logger_name)
        #
        for cur_name in ['nose2', 'flake8']:
            self.logger.debug('Reset logger level: {}'.format(cur_name))
            cur_logger = logging.getLogger(cur_name)
            cur_logger.setLevel(self.others_level)


class Flake8Wrapper(object):
    """
    The new flake8 library (3.5.0) has a kinda crappy API.
    This class wraps that shitty API into something a little easier to use.
    """

    def __init__(self):
        logger_name = self.__class__.__name__
        self.logger = logging.getLogger(logger_name)

    def check_file(self, file_name, dir_name):
        full = os.path.join(dir_name, file_name)
        if not os.path.isfile(full):
            self.logger.debug('Skipping non-file: {0}'.format(full))
            return 0
        # Stupid vim turd files... :(
        if file_name.startswith('.'):
            self.logger.debug('Skipping dotfile: {0}'.format(file_name))
            return 0
        if not file_name.endswith('.py'):
            self.logger.debug('Skipping non-py file: {0}'.format(file_name))
            return 0
        full_name = os.path.join(dir_name, file_name)
        self.logger.info('Checking python file: {0}'.format(full_name))
        style_guide = flake8.api.legacy.get_style_guide()
        report = style_guide.check_files([full_name])
        num_errors = report.total_errors
        if num_errors > 0:
            self.logger.error('Num errors: {0}'.format(num_errors))
        return num_errors

    def check_dir(self, dir_name):
        total_errors = 0
        for cur_file in os.listdir(dir_name):
            full = os.path.join(dir_name, cur_file)
            self.logger.debug('Checking file: {0}'.format(full))
            total_errors += self.check_file(cur_file, dir_name)
        self.logger.debug('Total errors: {0}'.format(total_errors))
        return total_errors


if __name__ == '__main__':
    pass
