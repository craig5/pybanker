"""
Main class that wraps pybanker functionality
"""
# core python libraries
import configparser
import logging
import os
# third party libraries
import yaml
# custom libraries
import pybanker.shared
import pybanker.account
import pybanker.schedule


class UndefinedCommandException(Exception):
    pass


class Banker(object):
    global_config = pybanker.shared.GlobalConfig()

    def __init__(self, logger_level=None):
        self._init_logger(logger_level)
        self._init_vars()

    def _init_vars(self):
        self.command = None
        self.accounts = None
        self.schedule = None
        self.config = None
        self._data_dir = None

    def _init_logger(self, logger_level=None):
        """Initialize logger. (self.logger)"""
        logger_name = self.__class__.__name__
        self.logger = logging.getLogger(logger_name)
        self.logger.debug('Logger initialized: {0}'.format(logger_name))

    def load_accounts(self):
        self.logger.debug('Loading accounts: {0}'.format(self.accounts_file))
        self.accounts = dict()
        with open(self.accounts_file, 'r') as fp:
            accounts = yaml.load(fp)
        for account_num, raw_account in accounts.items():
            new_account = pybanker.account.Account(account_num, raw_account)
            if new_account.short_name in self.accounts:
                self.logger.error('Duplicate account: {}'.format(
                    new_account.short_name))
                continue
            self.accounts[new_account.short_name] = new_account

    def list_accounts(self):
        self.logger.debug('Listing all accounts.')
        print('Accounts:')
        for account_id, account in self.accounts.items():
            print('  - {}'.format(account.get_summary()))

    def show_schedule(self):
        self.logger.debug('Showing schedule.')

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

    def load_config(self):
        """
        """
        conf_file = self.global_config.default_config_file
        self.logger.debug('Loading config: {0}'.format(conf_file))
        self.config = configparser.ConfigParser()
        with open(conf_file, 'r') as fp:
            self.config.readfp(fp)
        def_sec = 'default'
        self.data_dir = self.config.get(def_sec, 'data_dir')
        self.logger.debug('Data dir: {0}'.format(self.data_dir))

    def get_command_routine(self, command):
        """
        """
        command_lookup = dict()
        for cur in self.global_config.commands:
            command_lookup[cur['option']] = cur['routine']
        routine_name = command_lookup.get(command, None)
        self.logger.debug('Routine name: {}'.format(routine_name))
        if routine_name is None:
            msg = 'Bad command: {}'.format(command)
            self.logger.fatal(msg)
            raise UndefinedCommandException(msg)
        routine = getattr(self, routine_name)
        return routine

    def __call__(self, command):
        self.logger.debug('Main running command: {}'.format(command))
        self.load_config()
        self.load_accounts()
        self.schedule = pybanker.schedule.Schedule()
        self.schedule.load_data()
        (self.get_command_routine(command))()


if __name__ == '__main__':
    pass
