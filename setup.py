#!/usr/bin/env python3
"""
Setup script for pybanker (python3).
"""
# core python packaes
import setuptools
# third party packages
# custom packages


_LIB_DIR = 'lib'


def main():
    setup_args = dict()
    setup_args['package_dir'] = {'': _LIB_DIR}
    setup_args['packages'] = setuptools.find_packages(_LIB_DIR)
    setuptools.setup(**setup_args)


if __name__ == '__main__':
    main()
