"""
Classes to handle the scheduled items.
"""
# core python libraries
import logging
# third party libraries
import yaml
# custom libraries
import pybanker.shared


class Schedule(object):

    def __init__(self):
        self.__init_vars__()
        self.__init_logger__()

    def __init_vars__(self):
        self.items = dict()

    def __init_logger__(self):
        self.global_config = pybanker.shared.GlobalConfig()
        logger_name = '.'.join([
            self.global_config.package_name,
            self.__class__.__name__
        ])
        self.logger = logging.getLogger(logger_name)

    @property
    def schedule_file(self):
        return self.global_config.schedule_file

    def load_data(self):
        self.logger.debug('Loading schedule: {0})'.format(self.schedule_file))
        with open(self.schedule_file, 'r') as fp:
            raw = yaml.load(fp)
        for cur_name, cur_data in raw['items'].items():
            self.items[cur_name] = ScheduleItem(cur_name, cur_data)


class ScheduleItem(object):

    def __init__(self, name, data):
        self.__init_logger__()
        self.name = name
        self.__load_data__(data)

    def __init_logger__(self):
        logger_name = self.__class__.__name__
        self.logger = logging.getLogger(logger_name)

    def __load_data__(self, data):
        self.payee = data['payee']
        self.start_date = data['start-date']
        self.frequency = data['frequency']
        self.day = data['day']
        self.amount = data['amount']
        self.category = data['category']
        self.active = data['active']

    def __str__(self):
        return self.name

    def get_summary(self):
        """Show a short summary of the account."""
        output = self.name
        return output
# End of file.
