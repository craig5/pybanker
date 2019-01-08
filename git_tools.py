"""Routines to work with git data."""
# core python packaes
import os
import re
import setuptools
import subprocess
# third party packages
# custom packages


def version_from_tag():
    """
    Parse 'git describe --tags' and return a version.

    :return: (string) Version.
    """
    cmd = [
        'git',
        'describe',
        '--tags',
        '--match',
        'v*',
        '--long',
        '--dirty'
    ]
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = proc.communicate()
    stdout = stdout.decode('utf-8').rstrip('\n')
    version = stdout
    version = version.replace('-dirty', '+dirty')
    version = re.sub('-g\w{7}', '', version)
    version = re.sub('-(\d+)', r'.post\1', version)
    # remove the leading 'v'
    return version[1:]


if __name__ == '__main__':
    pass
