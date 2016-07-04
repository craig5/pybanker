"""
Global config for pybanker.
"""
# core python libraries
import logging
import os
import pkg_resources
# third party libraries
# custom libraries


class GlobalConfig(object):
    package_name = 'pybanker'
    version = pkg_resources.get_distribution(package_name).version
    #
    home_dir = os.path.expanduser('~')
    default_logger_level = logging.INFO
    default_config_file = os.path.join(
        home_dir,
        '.{0}'.format(package_name),
        'config.ini')
# End of file.
