"""
Classes related to the accounts.
"""
# core python packages
import collections
import datetime
import os
import re
# third party packages
import dateutil.relativedelta
import yaml
# custom packages
import pybanker.shared


class AccountConfigException(Exception):
    pass


def add_month(date):
    return date + dateutil.relativedelta.relativedelta(months=1)


class MonthlyIterator(object):

    def __init__(self, start_date):
        self.start_date = start_date

    def __iter__(self):
        self.current_date = self.start_date
        self.today_date = datetime.date.today()
        return self

    def __next__(self):
        self.current_date = \
            self.current_date + dateutil.relativedelta.relativedelta(months=1)
        if self.current_date > self.today_date:
            raise StopIteration
        return self.current_date


class Accounts(collections.OrderedDict):

    def __init__(self):
        super().__init__()
        self.config = pybanker.shared.GlobalConfig()
        self.logger = self.config.build_logger(self)
        self._load_accounts()

    @property
    def data_directory(self):
        return self.config.accounts_directory

    def _load_accounts(self):
        self.logger.debug(f'Loading accounts: {self.data_directory}')
        try:
            contents = os.listdir(self.data_directory)
        except FileNotFoundError:
            msg = f'Account directory not found: {self.data_directory}'
            raise AccountConfigException(msg)
        self.logger.debug(f'Elements in accounts dir: {len(contents)}')
        self.accounts = dict()
        for cur in contents:
            full = os.path.join(self.data_directory, cur)
            new_account = _AccountItem(full)
            self.accounts[new_account.short_name] = new_account
            self.logger.debug('Added account: {}'.format(new_account.name))

    def verify_data(self):
        self.logger.debug('Verifying account data.')
        for cur in self.values():
            cur.verify_data()

    def show_summary(self):
        print('Accounts')
        print('========')
        for cur in self.values():
            print(cur.get_summary_output(), end='')


class _AccountItem(collections.UserDict):

    def __init__(self, data_directory):
        """
        :param data: Dictionary containing the basic account data.
        """
        self.config = pybanker.shared.GlobalConfig()
        self.logger = self.config.build_logger(self)
        self.data_directory = data_directory
        index_data = self._read_index_file()
        super().__init__(**index_data)
        self._statements_directory = None
        self._statements_index = None
        self._verify_core_data()
        if self.is_cash():
            self.logger.debug('Cash account: not loading/verifying statments.')
        elif self.has_shared_statements():
            self.logger.debug(f'Shared statements for: {self.name}')
        else:
            self._load_statements()
            self._verify_statements()

    def __str__(self):
        return self['name']

    @property
    def home_dir(self):
        return self.config.home_dir

    @property
    def short_name(self):
        return os.path.basename(self.data_directory)

    @property
    def index_file(self):
        return os.path.join(self.data_directory, 'index.yaml')

    def _read_index_file(self):
        self.logger.debug(f'Reading index file ({self.short_name}): {self.index_file}')
        try:
            with open(self.index_file, 'r') as fp:
                data = yaml.safe_load(fp)
        except FileNotFoundError:
            msg = f'Account missing index file: {self.data_directory}'
            raise AccountConfigException(msg)
        except yaml.scanner.ScannerError as e:
            self.logger.exception(e)
            msg = f'Canot parse YAML file: {self.index_file}'
            raise AccountConfigException(msg)
        return data

    def _calc_statements_directory(self):
        """
        First priority is to use the dir defined in the index file.
        If there is a "statements" dir in the data dir, use that.
        """
        # TODO show an error if BOTH a subdir and config entry exist?
        try:
            cfg_dir = self['statements_directory']
            cfg_full = os.path.join(self.home_dir, cfg_dir)
            if os.path.exists(cfg_full):
                return cfg_full
            self.logger.warning(f'Config statements dir does not exist: {cfg_full}')
        except KeyError:
            self.logger.debug('No statments dir in config.')
        subdir = os.path.join(self.data_directory, 'statements')
        if os.path.exists(subdir):
            self.logger.debug(f'Using subdir for statements: {subdir}')
            return subdir
        raise AccountConfigException(f'No statements directory: {self.name}')

    @property
    def statements_directory(self):
        if self._statements_directory is None:
            self._statements_directory = self._calc_statements_directory()
        return self._statements_directory

    def _load_statements_index_file(self):
        index_file = os.path.join(self.statements_directory, 'index.yaml')
        if os.path.exists(index_file):
            with open(index_file, 'r') as fp:
                data = yaml.safe_load(fp)
                return data
        return dict()

    @property
    def statements_index(self):
        if self._statements_index is None:
            self._statements_index = self._load_statements_index_file()
        return self._statements_index

    @property
    def name_formats(self):
        return self.statements_index.get('name_formats', list())

    @property
    def account_id(self):
        """
        The 'short name' for this account.
        """
        return self['short_name']

    @property
    def type(self):
        return self['type']

    @property
    def name(self):
        return self['name']

    def is_cash(self):
        if self.type == 'cash':
            return True
        return False

    def has_shared_statements(self):
        if 'shared_statement_account' in self:
            return True
        return False

    def build_summary_data(self):
        """
        Build a dictionary with the "summary data" for this account.
        """
        data = {
            'Name': self['name'],
            'Type': self['type']
        }
        return {self.short_name: data}

    def get_required_fields(self):
        reqs = list()
        if not self.is_cash() and not self.has_shared_statements():
            reqs.append('start_date')
            reqs.append('statement_period')
        return reqs

    def get_summary_output(self):
        """
        Return a string that can be printed that shows this account's summary data.
        """
        output = yaml.dump(
            self.build_summary_data(),
            indent=2,
            default_flow_style=False
        )
        return output

    def _verify_core_data(self):
        fails = list()
        for req in self.get_required_fields():
            if req not in self:
                fails.append(f'Missing required key ({self.name}): {req}')
        if 'statement_period' in self.get_required_fields():
            period = self.get('statement_period', None)
            if period != 'monthly':
                # TODO add suppport for more than monthly
                fails.append(f'Unsupported statement period: {period}')
        if len(fails) > 0:
            raise AccountConfigException(fails)

    def _parse_date_file_name(self, name):
        return self._parse_date_string(name.rstrip('.pdf'))

    def _parse_date_string(self, date_string):
        for name_format in self.name_formats:
            filename_matcher = re.compile(name_format)
            date_matches = filename_matcher.match(date_string)
            if date_matches is None:
                continue
            dt_date = datetime.date(
                int(date_matches.group(1)),
                int(date_matches.group(2)),
                int(date_matches.group(3))
            )
            return dt_date
        raise AccountConfigException(f'Cannot parse date string: {date_string}')

    def _load_statements(self):
        self.statements = dict()
        for cur in os.listdir(self.statements_directory):
            if cur.startswith('.'):
                continue
            if cur == 'index.yaml':
                continue
            item = {'full_path': os.path.join(self.statements_directory, cur)}
            item['date'] = self._parse_date_file_name(cur)
            cur_key = item['date'].isoformat()
            if cur_key in self.statements:
                raise Exception(f'Duplicate statements: {self.name}')
            self.statements[cur_key] = item
        self._load_null_statements()

    def _load_null_statements(self):
        nulls = self.statements_index.get('null_statements', list())
        self.logger.debug(f'Found null statements: {self.name}:{len(nulls)}')
        self.logger.debug(f'Nulls: {nulls}')
        for cur in nulls:
            if type(cur) == int:
                cur = str(cur)
            self.logger.debug(f'Adding null: {self.name}:{cur}')
            dt_date = self._parse_date_file_name(cur)
            cur_key = dt_date.isoformat()
            self.statements[cur_key] = None

    def _verify_statements(self):
        if self.is_cash():
            return
        if self.has_shared_statements():
            return
        supported_types = ['monthly']
        period = self['statement_period']
        if period not in supported_types:
            raise AccountConfigException(f'Unsupported statement period: {period}')
        statement_dates = list()
        for cur in sorted(self.statements.keys()):
            statement_dates.append(datetime.date.fromisoformat(cur))
        today = datetime.date.today()
        cur_date = self['start_date']
        self.missing_statements = list()
        while cur_date <= today:
            self.logger.debug(f'Checking statement date: {self.name}:{cur_date}')
            try:
                delta = statement_dates[0] - cur_date
            except IndexError:
                # If there are no more statements,
                # then take the delta between the "desired date"
                # (aka "cur_date") and today.
                delta = cur_date - today
            self.logger.debug(f'Data delta: {delta}')
            if delta.days < -5 or delta.days > 30:
                self.missing_statements.append(cur_date)
                self.logger.error(f'Missing statement: {self.name}: {cur_date}')
            else:
                if len(statement_dates) > 0:
                    cur_date = statement_dates.pop(0)
                    self.logger.debug(f'Found statement: {cur_date}')
                else:
                    self.logger.info('No statements remaining: {cur_date}')
            cur_date = add_month(cur_date)
        if len(self.missing_statements) > 0:
            raise AccountConfigException(
                f'Missing statements: {self.name}: {self.missing_statements}')


if __name__ == '__main__':
    pass
