#!/usr/bin/env python3
"""Setup script for pybanker (python3)."""
import os
import setuptools
import sys


setup_args = {
    'name': 'pybanker',
    'version': '0.0.1',
    'description': 'Simple command line tool for managing your finances.',
    'author': 'Craig Sebenik',
    'author_email': 'craig5@pobox.com',
    'url': 'http://www.friedserver.com/',
    'keywords': ['python', 'python3', 'finance', 'money', 'quicken'],
}
#
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_LIB_DIR = 'lib'
_SCRIPTS_DIR = 'scripts'
_DATA_DIR = 'data'
_TESTS_DIR = 'tests'
_TESTS_LIB_DIR = os.path.join('tests', '.lib')
_DATA_LIST = ['{0}/*'.format(_DATA_DIR)]
_SCRIPTS_LIST = [os.path.join(_SCRIPTS_DIR, f)
                 for f in os.listdir(_SCRIPTS_DIR)
                 if not f.startswith('.')]
_REQUIREMENTS_FILE = 'requirements.txt'
_REQUIREMENTS = []
_TESTS_REQUIREMENTS_FILE = os.path.join(_TESTS_DIR, _REQUIREMENTS_FILE)
_TESTS_REQUIREMENTS = []
try:
    with open(_REQUIREMENTS_FILE, 'r') as fp:
        _REQUIREMENTS = fp.read().splitlines()
except os.FileNotFoundError:
    print('Requirements file missing: {0}'.format(_REQUIREMENTS_FILE))
try:
    with open(_TESTS_REQUIREMENTS_FILE, 'r') as fp:
        _TESTS_REQUIREMENTS = fp.read().splitlines()
except os.FileNotFoundError:
    print('Tests requirements file missing: {0}'.format(
        _TESTS_REQUIREMENTS_FILE))
sys.path.append(_TESTS_LIB_DIR)


setup_args['package_dir'] = {'': _LIB_DIR}
setup_args['packages'] = setuptools.find_packages(_LIB_DIR)
setup_args['package_data'] = {'': _DATA_LIST}
setup_args['include_package_data'] = True
setup_args['scripts'] = _SCRIPTS_LIST
setup_args['install_requires'] = _REQUIREMENTS
setup_args['setup_requires'] = _TESTS_REQUIREMENTS
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
        print('Scripts: {scripts}'.format(**setup_args))
        print('Requirements: {install_requires}'.format(**setup_args))
        print('Tests Lib Dir: {0}'.format(_TESTS_LIB_DIR))
        print('Test requirments: {setup_requires}'.format(**setup_args))


setup_args['cmdclass'] = {'info': Info}


setuptools.setup(**setup_args)

# End of file.
