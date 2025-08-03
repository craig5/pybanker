#!/usr/bin/env python3 -B
"""Test the basic formatting of the python code."""
import utils_for_tests


class TestFlake8(utils_for_tests.BaseTestCase):

    def setUp(self):
        self.logger.debug('Running setup.')
        self.flake8_wrapper = utils_for_tests.Flake8Wrapper()

    def tearDown(self):
        self.logger.debug('Running teardown.')


if __name__ == '__main__':
    pass
