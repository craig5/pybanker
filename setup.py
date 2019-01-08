#!/usr/bin/env python3
"""
Setup script for pybanker (python3).
"""
# core python packaes
import setuptools
# third party packages
# custom packages
import git_tools


_LIB_DIR = 'lib'

class InfoCommand(setuptools.Command):
    """Show basic info about the package."""
    description = 'show basic package info'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        print('Version: {}'.format(git_tools.version_from_tag()))


def main():
    setup_args = dict()
    setup_args['version'] = git_tools.version_from_tag()
    setup_args['package_dir'] = {'': _LIB_DIR}
    setup_args['packages'] = setuptools.find_packages(_LIB_DIR)
    setup_args['cmdclass'] = {'info': InfoCommand}
    setuptools.setup(**setup_args)


if __name__ == '__main__':
    main()
