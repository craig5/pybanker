#!/usr/bin/env python3
"""Setup script for pybanker (python3)."""
# core python packaes
import os
import setuptools
# third party packages
# custom packages


setup_args = {
    'name': 'pybanker',
    'version': '0.0.2',
    'description': 'Simple command line tool for managing your finances.',
    'author': 'Craig Sebenik',
    'author_email': 'craig5@users.noreply.github.com',
    'url': 'http://www.friedserver.com/',
    'keywords': ['python', 'python3', 'finance', 'money', 'quicken'],
}
#
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_LIB_DIR = 'lib'
_DATA_DIR = 'data'
_TESTS_DIR = 'tests'
_DATA_LIST = ['{0}/*'.format(_DATA_DIR)]


setup_args['package_dir'] = {'': _LIB_DIR}
setup_args['packages'] = setuptools.find_packages(_LIB_DIR)
setup_args['package_data'] = {'': _DATA_LIST}
setup_args['include_package_data'] = True
setup_args['test_suite'] = 'nose2.collector.collector'


class Info(setuptools.Command):
    """
    Show basic info about the package.
    """
    description = 'Show package info'
    user_options = []

    def initialize_options(self):
        """Init options..."""
        pass

    def finalize_options(self):
        """Finalize the things..."""
        pass

    def run(self):
        """Really show the info."""
        print('Package Name: {name}'.format(**setup_args))
        print('Version: {version}'.format(**setup_args))


setup_args['cmdclass'] = {'info': Info}
setup_args['entry_points'] = {
    'console_scripts': [
        'pybanker=pybanker.cli:PyBankerCli.main'
    ]
}

setuptools.setup(**setup_args)
