"""
Classes to handle the scheduled items.
"""
import logging

import yaml

import pybanker.shared


class Schedule(dict):

    def __init__(self):
        self.config = pybanker.shared.GlobalConfig()
        self._init_logger()
        self.load_items()

    def _init_logger(self):
        logger_name = '.'.join([
            self.config.package_name,
            self.__class__.__name__
        ])
        self.logger = logging.getLogger(logger_name)

    def load_items(self):
        file_name = self.config.schedule_file
        self.logger.debug('Loading schedule: {0}'.format(file_name))
        with open(file_name, 'r') as fp:
            raw = yaml.safe_load(fp)
        for cur_name, cur_data in raw['items'].items():
            self[cur_name] = ScheduleItem(cur_name, cur_data)

    def show_summary(self):
        self.logger.debug('Showing schedule summary.')
        data = dict()
        data['Schedule'] = list()
        for cur in self.values():
            data['Schedule'].append(cur.get_summary())
        print(yaml.dump(
            data,
            indent=2,
            default_flow_style=False
        ))


class ScheduleItem(object):

    def __init__(self, name, data):
        self._init_logger()
        self.name = name
        self._load_data(data)

    def _init_logger(self):
        logger_name = self.__class__.__name__
        self.logger = logging.getLogger(logger_name)

    def _load_data(self, data):
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


if __name__ == '__main__':
    pass
