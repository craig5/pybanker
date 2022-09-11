"""
Classes related to the accounts.
"""
# core python packages
import datetime
# third party packages
# custom packages
import pybanker.shared


_FREQUENCY_DATA = {
    'bi-weekly': {'days': 14, 'buffer': 2},
    'monthly': {'days': 30, 'buffer': 5},
    'quarterly': {'days': 90, 'buffer': 5},
}


class UnknownFrequency(Exception):
    pass


def _get_today_dt():
    return datetime.date.today()


def get_frequency_types():
    return _FREQUENCY_DATA.keys()


def is_supported_type(period_type):
    if period_type in get_frequency_types():
        return True
    return False


class FrequencyHelper:

    def __init__(self, frequency, statement_dates, start_dt, end_dt=None):
        self.config = pybanker.shared.GlobalConfig()
        self.logger = self.config.build_logger(self)
        self.frequency = frequency
        try:
            self.frequency_data = _FREQUENCY_DATA[self.frequency]
        except KeyError:
            raise UnknownFrequency(f'Unknown frequency: {self.frequency}')
        self.statement_dates = statement_dates
        self.start_dt = start_dt
        self.end_dt = end_dt
        if self.end_dt is None:
            self.end_dt = _get_today_dt()

    @property
    def buffer_days(self):
        return self.frequency_data['buffer']

    @property
    def days_delta(self):
        return self.frequency_data['days']

    def _pop_latest_doc(self):
        if len(self.statement_dates) <= 0:
            return None
        next_doc = self.statement_dates.pop(0)
        self.logger.debug(f'Popped doc with date: {next_doc}')
        return next_doc

    def _increment_frequency(self, cur_dt):
        return cur_dt + datetime.timedelta(days=self.days_delta)

    def _decrement_frequency(self, cur_dt):
        return cur_dt - datetime.timedelta(days=self.days_delta)

    def _is_inside_window(self, cur_dt, start_dt):
        end_dt = self._increment_frequency(start_dt)
        if cur_dt < (end_dt + datetime.timedelta(days=self.buffer_days)):
            return True
        return False

    def find_missing_statement_dates(self):
        self.logger.debug('Searching for missing statements.')
        missing = list()
        window_start_dt = self.start_dt
        latest_doc_dt = self._pop_latest_doc()
        end_dt = self._decrement_frequency(self.end_dt)
        self.logger.debug(f'Start date: {window_start_dt}')
        self.logger.debug(f'End date: {end_dt} (orig: {self.end_dt})')
        while window_start_dt < end_dt:
            self.logger.debug(f'Checking: doc={latest_doc_dt}  window_start={window_start_dt}')
            # If there are no more statements, mark all of the rest as missing
            if latest_doc_dt is not None:
                if self._is_inside_window(latest_doc_dt, start_dt=window_start_dt):
                    self.logger.debug(f'Found statement: {latest_doc_dt}')
                    window_start_dt = latest_doc_dt
                    latest_doc_dt = self._pop_latest_doc()
                    continue
            else:
                self.logger.error('No more statments.')
            # If "latest_doc_dt" is outside the window, then increment the window first,
            # this should make ""window_start_dt" the DESIRED date, i.e. the "window end".
            window_start_dt = self._increment_frequency(window_start_dt)
            self.logger.error(f'Missing statement: {window_start_dt}')
            missing.append(window_start_dt)
        return missing


if __name__ == '__main__':
    pass
