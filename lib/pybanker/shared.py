"""
Global config for pybanker.
"""
# core python libraries
import configparser
import logging
import os
import pkg_resources
# third party libraries
# custom libraries


class GlobalConfig(object):
    package_name = 'pybanker'
    base_logger_name = package_name
    default_logger_level = logging.WARN
    version = pkg_resources.get_distribution(package_name).version
    #
    home_dir = os.path.expanduser('~')
    logger_level = logging.INFO
    default_config_file = os.path.join(
        home_dir,
        '.{0}'.format(package_name),
        'config.ini'
    )
    # The first one ([0]) is the default.
    commands = [
        {'option': 'show-summary', 'routine': 'show_summary'},
        {'option': 'show-schedule', 'routine': 'show_schedule'},
        {'option': 'list-accounts', 'routine': 'list_accounts'}
    ]

    def __init__(self):
        self.logger = self.build_logger(self)
        self._init_vars()
        # TODO add kwarg for "config_file" to override default
        self.config_file = self.default_config_file
        self._load_config_file()

    def _init_vars(self):
        self._data_dir = None

    def _load_config_file(self):
        self.conf = configparser.ConfigParser()
        self.logger.debug('Reading config file: {}'.format(self.config_file))
        self.conf.read(self.config_file)

    @property
    def data_dir(self):
        # TODO add check to make sure 'data_dir' exists in conf
        data_dir = self.conf.get('default', 'data_dir')
        if not data_dir.startswith('/'):
            data_dir = os.path.join(self.home_dir, data_dir)
            self.logger.debug('Data dir: {}'.format(data_dir))
        return data_dir

    @property
    def schedule_file(self):
        return os.path.join(self.data_dir, 'schedule.yaml')

    @property
    def accounts_directory(self):
        return os.path.join(self.data_dir, 'accounts')

    def build_logger(self, class_object):
        logger_name = self.build_logger_name(class_object)
        logger = logging.getLogger(logger_name)
        logger.debug('Logger created: {}'.format(logger.name))
        return logger

    def build_logger_name(self, class_object):
        return '.'.join([self.base_logger_name, class_object.__class__.__name__])


if __name__ == '__main__':
    pass
