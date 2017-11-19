#!/usr/bin/env python3 -B
"""
Test the basic formatting of the python code.
"""
# python core packages
import os
# third party packages
# custom packages
import utils_for_tests


class TestFlake8(utils_for_tests.BaseTestCase):

    def setUp(self):
        self.logger.debug('Running setup.')
        self.flake8_wrapper = utils_for_tests.Flake8Wrapper()

    def tearDown(self):
        self.logger.debug('Running teardown.')

    def test_flake8_lib_dir(self):
        dir_name = self.test_dir
        self.logger.debug('Checking dir: {0}'.format(dir_name))
        total_errors = 0
        for cur_file in os.listdir(dir_name):
            full = os.path.join(dir_name, cur_file)
            self.logger.debug('Checking file: {0}'.format(full))
            total_errors += self.flake8_wrapper.check_file(cur_file, dir_name)
        self.logger.debug('Total errors: {0}'.format(total_errors))
        self.assertEqual(total_errors, 0)


if __name__ == '__main__':
    pass
