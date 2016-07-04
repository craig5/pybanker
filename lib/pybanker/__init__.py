"""
Main class that wraps pybanker functionality
"""
# core python libraries
import logging
import os
# third party libraries
import yaml
# custom libraries
import pybanker.shared


GLOBAL_CONFIG = pybanker.shared.GlobalConfig()


# TODO some stuff
class Banker(object):

    def __init__(self, logger_level=None):
        self._init_logger(logger_level)
        self.command = None

    def _init_logger(self, logger_level=None):
        """Initialize logger. (self.logger)"""
        logger_name = self.__class__.__name__
        if logger_level is None:
            logger_level = GLOBAL_CONFIG.default_logger_level
        format_string = '[%(levelname)s] %(name)s(%(lineno)d) - %(message)s'
        formatter = logging.Formatter(format_string)
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        handler.setLevel(logger_level)
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logger_level)
        self.logger.addHandler(handler)
        self.logger.debug('Logger initialized: {0}'.format(logger_name))

    def load_accounts(self):
        self.logger.debug('Loading accounts: {0}'.format(self.accounts_file))
        with open(self.accounts_file, 'r') as fp:
            accounts = yaml.load(fp)
        print(accounts)

    def load_schedule(self):
        self.logger.debug('Loading schedule: {0})'.format(self.schedule_file))
        with open(self.schedule_file, 'r') as fp:
            schedule = yaml.load(fp)
        print(schedule)

    def main(self):
        self.logger.debug('Inside main.')
        self.load_accounts()
        self.load_schedule()

    @property
    def command(self):
        return self._command

    @command.setter
    def command(self, value):
        self._command = value

    @property
    def accounts_file(self):
        return os.path.join(self.data_dir, 'accounts.yaml')

    @property
    def schedule_file(self):
        return os.path.join(self.data_dir, 'schedule.yaml')

    @property
    def data_dir(self):
        return self._data_dir

    @data_dir.setter
    def data_dir(self, value):
        if not value.startswith('/'):
            home_dir = os.path.expanduser('~')
            value = os.path.join(home_dir, value)
        self._data_dir = value


class Accounts(object):

    def __init__(self):
        pass


class Budget(object):

    def __init__(self):
        pass

# End of file.
