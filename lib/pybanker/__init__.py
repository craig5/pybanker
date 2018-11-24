"""
Main class that wraps pybanker functionality
"""
# core python libraries
import logging
# third party libraries
# custom libraries
import pybanker.shared
import pybanker.accounts
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
        self._schedule = None
        self._accounts = None

    def _init_logger(self, logger_level=None):
        """Initialize logger. (self.logger)"""
        logger_name = self.global_config.build_logger_name(self)
        self.logger = logging.getLogger(logger_name)
        self.logger.debug('Logger initialized: {0}'.format(logger_name))

    @property
    def accounts(self):
        if self._accounts is None:
            self._accounts = pybanker.accounts.Accounts()
        return self._accounts

    @property
    def schedule(self):
        if self._schedule is None:
            self._schedule = pybanker.schedule.Schedule()
        return self._schedule

    def list_accounts(self):
        self.accounts.show_summary()

    def show_schedule(self):
        self.schedule.show_summary()

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
        (self.get_command_routine(command))()


if __name__ == '__main__':
    pass
