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


_PACKAGE_NAME = 'pybanker'


class ConfigError(Exception):
    pass


def home_dir():
    return os.path.expanduser('~')


class GlobalConfig(object):
    base_logger_name = _PACKAGE_NAME
    default_logger_level = logging.WARN
    version = pkg_resources.get_distribution(_PACKAGE_NAME).version
    #
    package_name = _PACKAGE_NAME
    logger_level = logging.INFO
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
        self._config_file = None
        self.conf = self._get_config_object()

    def _init_vars(self):
        self._data_dir = None

    def _build_config_file(self):
        config_file = os.path.join(
            home_dir(),
            '.{0}'.format(self.package_name),
            'config.ini'
        )
        self.logger.debug(f'Built config file: {config_file}')
        return config_file

    @property
    def config_file(self):
        if self._config_file is None:
            self._config_file = self._build_config_file()
        return self._config_file

    def _get_config_object(self):
        conf = configparser.ConfigParser()
        if not os.path.exists(self.config_file):
            raise ConfigError(f'Config file does not exist: {self.config_file}')
        self.logger.debug('Reading config file: {}'.format(self.config_file))
        conf.read(self.config_file)
        return conf

    @property
    def data_dir(self):
        # TODO add check to make sure 'data_dir' exists in conf
        data_dir = self.conf.get('default', 'data_dir')
        if not data_dir.startswith('/'):
            data_dir = os.path.join(home_dir(), data_dir)
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
