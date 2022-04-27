"""
Classes related to the accounts.
"""
# core python packages
import collections
import datetime
import os
import re
# third party packages
import yaml
# custom packages
import pybanker.shared
import pybanker.frequency_utils


class AccountConfigException(Exception):
    pass


class Accounts(collections.OrderedDict):

    def __init__(self):
        super().__init__()
        self.config = pybanker.shared.GlobalConfig()
        self.logger = self.config.build_logger(self)
        self._accounts = None

    @property
    def data_directory(self):
        return self.config.accounts_directory

    def _get_accounts(self):
        self.logger.debug(f'Loading accounts: {self.data_directory}')
        try:
            contents = os.listdir(self.data_directory)
        except FileNotFoundError:
            msg = f'Account directory not found: {self.data_directory}'
            raise AccountConfigException(msg)
        self.logger.debug(f'Elements in accounts dir: {len(contents)}')
        accounts = dict()
        for cur in contents:
            full = os.path.join(self.data_directory, cur)
            new_account = _AccountItem(full)
            accounts[new_account.short_name] = new_account
            self.logger.debug('Added account: {}'.format(new_account.name))
        return accounts

    @property
    def accounts(self):
        if self._accounts is None:
            self._accounts = self._get_accounts()
        return self._accounts

    def verify_data(self):
        self.logger.debug('Verifying account data.')
        for cur_name, cur_obj in self.accounts.items():
            cur_obj.verify_data()

    def show_summary(self):
        print('Accounts')
        print('========')
        for cur_name, cur_obj in self.accounts.items():
            print(cur_obj.get_summary_output())


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

    @property
    def statements_base_dir(self):
        if self.type == 'payroll':
            return 'pay-stubs'
        return 'statements'

    def _calc_statements_directory(self):
        subdir = os.path.join(self.data_directory, self.statements_base_dir)
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
        output = output.rstrip('\n')
        return output

    def _verify_core_data(self):
        fails = list()
        for req in self.get_required_fields():
            if req not in self:
                fails.append(f'Missing required key ({self.name}): {req}')
        if 'statement_period' in self.get_required_fields():
            period = self.get('statement_period', None)
            if not pybanker.frequency_utils.is_supported_type(period):
                fails.append(f'Unsupported statement period: {period}')
        if len(fails) > 0:
            raise AccountConfigException(fails)

    def _parse_date_file_name(self, name):
        try:
            return self._parse_date_string(name.rstrip('.pdf'))
        except Exception:
            raise

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
        for cur in self._get_null_statements():
            self.statements[cur] = None
        for cur in self._get_known_missing_statements():
            self.statements[cur] = None

    def _convert_raw_to_datetimes(self, key_name):
        raw_list = self.statements_index.get(key_name, list())
        converted_list = list()
        self.logger.debug(f'Found {key_name} statements: {self.name}:{len(raw_list)}')
        for cur in raw_list:
            self.logger.debug(f'Adding {key_name}: {self.name}:{cur}')
            # Data cleanup, first...
            if isinstance(cur, int):
                cur = str(cur)
            # Convert to datetime, if needed.
            if isinstance(cur, str):
                dt_date = self._parse_date_file_name(cur)
            elif isinstance(cur, datetime.date):
                dt_date = cur
            else:
                # TODO better exception
                raise Exception(f'Could not convert to dt: {cur}')
            cur_key = dt_date.isoformat()
            converted_list.append(cur_key)
        return converted_list

    def _get_null_statements(self):
        return self._convert_raw_to_datetimes('null_statements')

    def _get_known_missing_statements(self):
        return self._convert_raw_to_datetimes('known_missing_statements')

    def _verify_statements(self):
        if self.is_cash():
            return
        if self.has_shared_statements():
            return
        statement_dates = list()
        for cur in sorted(self.statements.keys()):
            statement_dates.append(datetime.date.fromisoformat(cur))
        freq_helper = pybanker.frequency_utils.FrequencyHelper(
            self['statement_period'], statement_dates, self['start_date'])
        self.missing_statement_dates = freq_helper.find_missing_statement_dates()
        if len(self.missing_statement_dates) > 0:
            for cur in self.missing_statement_dates:
                self.logger.error(f'Missing statement: {self.name}: {cur}')
            raise AccountConfigException(
                f'Missing statements: {self.name}: {self.missing_statement_dates}')

    def verify_data(self):
        raise NotImplementedError('Verify data is not done in accounts item.')


if __name__ == '__main__':
    pass
