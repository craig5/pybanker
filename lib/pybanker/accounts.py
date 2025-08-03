"""
Classes related to the accounts.
"""
import dataclasses
import datetime
import functools
import pathlib
import typing

import yaml

import pybanker.frequency_utils
import pybanker.shared
import pybanker.statements


class AccountConfigException(Exception):
    pass


@dataclasses.dataclass
class AccountManager:

    def __post_init__(self):
        self.global_config = pybanker.shared.GlobalConfig()
        self.logger = self.global_config.build_logger(self)

    @property
    def data_directory(self):
        return pathlib.Path(self.global_config.accounts_directory)

    @functools.cached_property
    def accounts(self):
        self.logger.debug(f'Loading accounts: {self.data_directory}')
        if not self.data_directory.exists():
            msg = f'Account directory not found: {self.data_directory}'
            raise AccountConfigException(msg)
        accounts = dict()
        for cur in sorted(self.data_directory.iterdir()):
            if not cur.is_dir():
                self.logger.debug('Skipping non-dir: %s', cur)
                continue
            if cur.stem.startswith('.'):
                self.logger.debug('Skipping dotdir: %s', cur)
                continue
            try:
                new_account = _SingleAccount(cur)
            except Exception as exc:
                self.logger.exception(exc)
                self.logger.error('Could not create account: %s', cur)
                breakpoint()
                raise
            accounts[new_account.slug] = new_account
            self.logger.debug('Added account: {}'.format(new_account.slug))
        self.logger.debug('Number accounts found: %d', len(accounts))
        return accounts

    def verify_data(self):
        self.logger.debug('Verifying account data.')
        for cur_name, cur_obj in self.accounts.items():
            cur_obj.verify_data()

    def show_summary(self):
        print('Accounts')
        print('========')
        for cur_name, cur_obj in self.accounts.items():
            print(cur_obj.get_summary_output())


@dataclasses.dataclass
class _AccountIndexData:
    index_path: pathlib.Path
    slug: str
    name: str
    active: bool
    visible: bool
    account_type: str  # Maybe make this an enum?
    start_date: datetime.date
    statement_period: str  # TODO make this an enum
    # optional
    short_name: typing.Optional[str] = None
    no_statements: typing.Optional[bool] = False
    url: typing.Optional[str] = None
    bills_url: typing.Optional[str] = None
    statement_url: typing.Optional[str] = None
    shared_statement_account: typing.Optional[str] = None
    account_endings: typing.Optional[list[str]] = None
    # TODO need to remove the legacy "singular"
    statements_directory: typing.Optional[str] = None
    statements_directories: typing.Optional[list[str]] = None
    # legacy/unused???
    statement_date: typing.Optional[str] = None

    def __post_init__(self):
        self.global_config = pybanker.shared.GlobalConfig()
        self.logger = self.global_config.build_logger(self)

    @classmethod
    def from_file(cls, slug: str, index_path: pathlib.Path):
        global_config = pybanker.shared.GlobalConfig()
        logger = global_config.build_logger(cls)
        logger.debug('Reading index file: %s', index_path)
        try:
            with open(index_path, 'r') as fp:
                data = yaml.safe_load(fp)
        except FileNotFoundError:
            msg = f'Account missing index file: {index_path}'
            raise AccountConfigException(msg)
        except yaml.scanner.ScannerError as e:
            logger.exception(e)
            msg = f'Canot parse YAML file: {index_path}'
            raise AccountConfigException(msg)
        if 'type' in data:
            logger.warning('Legacy index element: type')
            data['account_type'] = data['type']
            del data['type']
        if data.get('shared_statement_account', None) is not None:
            data['statement_period'] = None
            data['statements_directories'] = []
            data['start_date'] = None
        try:
            this = cls(slug=slug, index_path=index_path, **data)
        except Exception as exc:
            logger.exception(exc)
            breakpoint()
        return this


@dataclasses.dataclass
class _SingleAccount:
    data_directory: pathlib.Path
    slug: str = dataclasses.field(init=False)

    def __post_init__(self):
        """Initialize the computed values."""
        self.global_config = pybanker.shared.GlobalConfig()
        self.logger = self.global_config.build_logger(self)
        self.logger.debug('Loadding account from dir: %s', self.data_directory)
        self.path = pathlib.Path(self.data_directory)
        self.slug = self.path.stem
        self.index_file = self.data_directory / 'index.yaml'
        self.index_data = _AccountIndexData.from_file(slug=self.slug, index_path=self.index_file)
        self.statements_manager = pybanker.statements.StatementsManager(
            account_key=self.slug,
            base_path=self.path,
            paths=self.statements_paths,
            account_index_data=self.index_data,
        )
        self._verify_core_data()
        self.statements_manager.verify()

    def has_shared_statements(self):
        # TODO verify that the shared account actually exists.
        if self.index_data.shared_statement_account is not None:
            return True
        return False

    def has_statements(self):
        if self.has_shared_statements() is True:
            return False
        return not self.index_data.no_statements

    @functools.cached_property
    def statements_paths(self):
        paths = None
        if not self.has_statements():
            self.logger.info('No statements by config: %s', self.slug)
            return []
        # First, look for the legacy "single" entry.
        single_key = 'statements_directory'
        single = getattr(self.index_data, single_key, None)
        # Then, then new list/array format.
        multi_key = 'statements_directories'
        multi = getattr(self.index_data, multi_key, None)
        if single is None and multi is not None:
            dirs = multi
        elif single is not None and multi is None:
            dirs = [single]
        elif single is None and multi is None:
            raise AccountConfigException(f'No statement dirs defined: {self.slug}')
        else:
            # One cannot define BOTH.
            raise AccountConfigException(
                f'Both {single_key} and {multi_key} are defined for {self.slug}.')
        self.logger.debug('Statement dir: %s', dirs)
        paths = [self.path / cur for cur in dirs]
        self.logger.debug('Statement paths: %s', paths)
        return paths

    @functools.cached_property
    def required_fields(self):
        reqs = list()
        if self.has_statements():
            reqs.append('start_date')
        return reqs

    def _verify_core_data(self):
        """Run any account verifcation steps needed.

        Note: this used to be more important before using "dataclasses".
            Now, the `dataclass` structure enforces any required fields.
        """
        return

    def build_summary_data(self):
        """Build a dictionary with the "summary data" for this account."""
        data = {
            'Name': self.index_data.name,
            'Type': self.index_data.account_type,
        }
        return {self.slug: data}

    def get_verbose_output(self):
        """Return a string that can be printed that shows this account's data."""
        output = yaml.dump(
            self.build_summary_data(),
            indent=2,
            default_flow_style=False
        )
        output = output.rstrip('\n')
        return output

    def get_summary_output(self):
        """Return a string that can be printed that shows this account's summary data."""
        # TODO use prettytable
        format_string = '{name:50s} [{slug:22s}]: {account_type}'
        output = format_string.format(
            name=self.index_data.name,
            slug=self.slug,
            account_type=self.index_data.account_type
        )
        return output


if __name__ == '__main__':
    pass
