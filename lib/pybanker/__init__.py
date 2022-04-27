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
import pybanker.receipts
import pybanker.transactions


class UndefinedCommandException(Exception):
    pass


class Banker(object):

    def __init__(self, logger_level=None):
        self.config = pybanker.shared.GlobalConfig()
        self.logger = self.config.build_logger(self)
        self._init_vars()
        self.load_data()

    def _init_vars(self):
        self.command = None
        self._schedule = None
        self._accounts = None
        self._receipts = None
        self._transactions = None

    def _init_logger(self, logger_level=None):
        """Initialize logger. (self.logger)"""
        logger_name = self.config.build_logger_name(self)
        self.logger = logging.getLogger(logger_name)
        self.logger.debug('Logger initialized: {0}'.format(logger_name))

    def load_data(self):
        self.accounts = pybanker.accounts.Accounts()
        self.schedule = pybanker.schedule.Schedule()
        self.receipts = pybanker.receipts.Receipts()
        self.transactions = pybanker.transactions.Transactions()
        self.transactions.link_receipts(self.receipts)

    def list_accounts(self):
        self.accounts.show_summary()

    def show_schedule(self):
        self.schedule.show_summary()

    def show_summary(self):
        """
        Show a summary of: accounts, schedule and "errors".
        """
        self.list_accounts()
        print('='*50)
        self.show_schedule()

    def _get_command_routine(self, command):
        """
        """
        command_lookup = dict()
        for cur in self.config.commands:
            command_lookup[cur['option']] = cur['routine']
        routine_name = command_lookup.get(command, None)
        self.logger.debug('Routine name: {}'.format(routine_name))
        if routine_name is None:
            msg = 'Bad command: {}'.format(command)
            self.logger.fatal(msg)
            raise UndefinedCommandException(msg)
        routine = getattr(self, routine_name)
        return routine

    def verify_data(self):
        """
        """
        # TODO verify that required data files exist and are in the correct format
        # TODO verify that every receipt has a corresponding transaction
        # self.receipts.receipts
        # TODO move all verify steps to when the data is loaded
        self.transactions.verify_data()
        self.receipts.verify_data()

    def __call__(self, command):
        self.logger.debug('Main running command: {}'.format(command))
        self.verify_data()
        (self._get_command_routine(command))()


if __name__ == '__main__':
    pass
