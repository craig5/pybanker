"""Helpers to manage statements."""
import dataclasses
import datetime
import enum
import functools
import pathlib
import re
import typing

import yaml

import pybanker.frequency_utils
import pybanker.shared


class ConfigError(Exception):
    pass


class MissingStatements(Exception):

    def __init__(self, message, account_name, missing):
        super().__init__(message)
        self.account_name = account_name
        self.missing = missing


def _parse_date_string(date_string, name_formats):
    for cur_format in name_formats:
        filename_matcher = re.compile(cur_format)
        date_matches = filename_matcher.match(date_string)
        if date_matches is None:
            continue
        try:
            dt_date = datetime.date(
                int(date_matches.group(1)),
                int(date_matches.group(2)),
                int(date_matches.group(3))
            )
        except Exception:
            raise
        return dt_date
    raise ConfigError(f'Cannot parse date string: {date_string}')


@dataclasses.dataclass
class _StatementItem:
    date_dt: datetime.date
    path: typing.Optional[pathlib.Path] = None

    def __post_init__(self):
        self.global_config = pybanker.shared.GlobalConfig()
        self.logger = self.global_config.build_logger(self)

    @classmethod
    def from_file(cls, path, name_formats):
        stem = path.stem
        date_dt = _parse_date_string(stem, name_formats)
        return cls(date_dt=date_dt, path=path)

    @classmethod
    def from_config(cls, date):
        if isinstance(date, datetime.date):
            return cls(date_dt=date)
        try:
            dt = datetime.datetime.strptime(str(date), '%Y%m%d')
            return cls(date_dt=dt.date())
        except Exception:
            pass
        # TODO unit test to verify this behavior
        breakpoint()


class _StatementPeriod(enum.Enum):
    bi_weekly = 'bi-weekly'
    monthly = 'monthly'
    quarterly = 'quarterly'


@dataclasses.dataclass
class _IndexData:
    index_path: pathlib.Path
    name_formats: list[str]
    start_date: datetime.date
    period: str
    period_ref: _StatementPeriod = dataclasses.field(init=False)
    # optional
    end_date: typing.Optional[datetime.date] = None
    null_statements: typing.Optional[list[datetime.date]] = None
    known_missing_statements: typing.Optional[list[datetime.date]] = None
    filename_date_map: typing.Optional[dict[str: datetime.date]] = None

    def __post_init__(self) -> None:
        self.config = pybanker.shared.GlobalConfig()
        self.logger = self.config.build_logger(self)
        self.period_ref = _StatementPeriod(self.period)
        self.null_statements = self._transform_statements_list('null_statements')
        self.known_missing_statements = self._transform_statements_list('known_missing_statements')
        if self.filename_date_map is None:
            self.filename_date_map = {}

    def _transform_statements_list(self, cur_key) -> list:
        """Transform a list of dates in statement items."""
        raw_list = getattr(self, cur_key, [])
        items = []
        if raw_list is not None:
            for cur in raw_list:
                new_item = _StatementItem.from_config(cur)
                items.append(new_item)
        return items

    @staticmethod
    def read_index_file(index_path: pathlib.Path) -> dict:
        with index_path.open() as fp:
            data = yaml.safe_load(fp)
        return data

    @classmethod
    def from_file(cls, index_path: pathlib.Path):
        if not index_path.exists():
            raise ConfigError(f'Index file does not exist: {index_path}')
        # This is overkill... :(
        config = pybanker.shared.GlobalConfig()
        logger = config.build_logger(cls)
        logger.debug('Reading statements index: %s', index_path)
        data = cls.read_index_file(index_path)
        try:
            this = cls(index_path=index_path, **data)
        except Exception as exc:
            # TODO make this a real exception once the "legacy support" is removed.
            # logger.exception(exc)
            logger.debug('Could not create from file: %s', exc)
            this = None
        return this


@dataclasses.dataclass
class _StatementsDirectory:
    path: pathlib.Path
    account_index_data: object

    def __post_init__(self):
        self.config = pybanker.shared.GlobalConfig()
        self.logger = self.config.build_logger(self)
        self.index_path = self.path / 'index.yaml'
        try:
            self.index_data = _IndexData.from_file(self.index_path)
        except ConfigError:
            # TODO temporary... until all index files are created, use the legacy method
            self.logger.error('Ignoring missing index file for now: %s', self.index_path)
            self.index_data = None
        if self.index_data is None:
            self.index_data = self._legacy_index_data()
        self.freq_helper = pybanker.frequency_utils.FrequencyHelper(
            self.index_data.period,
            [cur.date_dt for cur in self.statements],
            self.index_data.start_date,
            self.index_data.end_date,
        )
        self.missing_statement_dates = self.freq_helper.find_missing_statement_dates()

    def _legacy_index_data(self):
        self.logger.warning('Using LEGACY index data: %s', self)
        try:
            index_data = _IndexData.read_index_file(self.index_path)
        except FileNotFoundError:
            self.logger.error('Ignoring missing index file for now: %s', self.index_path)
            index_data = {
                'name_formats': [r'^(\d{4})-(\d{2})-(\d{2})'],
            }
        defaults = {
            'name_formats': [r'^(\d{4})-(\d{2})-(\d{2})'],
            'start_date': self.account_index_data.start_date,
            'period': self.account_index_data.statement_period,
        }
        for cur_key, cur_default in defaults.items():
            if cur_key not in index_data:
                self.logger.debug('Adding default (%s): %s', self.path, cur_key)
                index_data[cur_key] = cur_default
        try:
            this = _IndexData(index_path=self.index_path, **index_data)
        except Exception as exc:
            self.logger.exception(exc)
            breakpoint()
        return this

    @functools.cached_property
    def actual_file_paths(self):
        actual = []
        skip_list = ['index']
        for cur in sorted(self.path.iterdir()):
            cur_stem = cur.stem
            if cur_stem in skip_list:
                self.logger.debug('Skipping from skip_list: %s', cur)
                continue
            if cur_stem.startswith('.'):
                self.logger.debug('Skipping dot file: %s', cur)
                continue
            actual.append(cur)
        return actual

    @functools.cached_property
    def statements(self):
        self.logger.debug('Loading statements: %s', self)
        statements = []
        found_dts = []
        actual_file_paths = self.actual_file_paths
        for cur_file, cur_dt in self.index_data.filename_date_map.items():
            cur_path = self.path / cur_file
            new_item = _StatementItem(
                path=cur_path,
                date_dt=cur_dt,
            )
            # Remove the current file from the "actual" list.
            try:
                actual_file_paths.remove(cur_path)
            except ValueError:
                self.logger.error(f'File in filename_date_map does not exist: {cur_path}')
                breakpoint()
            found_dts.append(new_item.date_dt)
            statements.append(new_item)
        for cur in self.index_data.null_statements:
            if cur.date_dt in found_dts:
                raise ConfigError(f'Duplicate dates: {cur.date_dt}')
            found_dts.append(cur.date_dt)
            statements.append(cur)
        for cur in self.index_data.known_missing_statements:
            if cur.date_dt in found_dts:
                breakpoint()
                raise ConfigError(f'Duplicate dates: {cur.date_dt}')
            found_dts.append(cur.date_dt)
            statements.append(cur)
        for cur in actual_file_paths:
            new_item = _StatementItem.from_file(cur, self.index_data.name_formats)
            if new_item.date_dt in found_dts:
                raise ConfigError(f'Duplicate dates: {new_item.date_dt}')
            found_dts.append(new_item.date_dt)
            statements.append(new_item)
        # Sort the statements by date.
        sorted_statements = sorted(statements, key=lambda cur: cur.date_dt)
        return sorted_statements

    def verify(self):
        self.logger.debug('Verify statements dir: %s', self)
        if len(self.missing_statement_dates) > 0:
            cur_dir = self.path.stem
            slug = self.account_index_data.slug
            for cur in self.missing_statement_dates:
                self.logger.error('Missing statement: %s/%s - %s', slug, cur_dir, cur)


@dataclasses.dataclass
class StatementsManager:
    account_key: str
    base_path: pathlib.Path
    paths: list[pathlib.Path]
    account_index_data: object

    def __post_init__(self):
        self.config = pybanker.shared.GlobalConfig()
        self.logger = self.config.build_logger(self)
        #
        self._init_dirs()

    def _init_dirs(self):
        self.logger.debug('Init dirs: %s', self)
        self.statements_directories = list()
        for cur in self.paths:
            full_path = self.base_path / cur
            new_st_dir = _StatementsDirectory(
                path=full_path,
                account_index_data=self.account_index_data
            )
            self.statements_directories.append(new_st_dir)
        self.logger.debug('Statements dirs: %s', self.statements_directories)

    @functools.cached_property
    def statements(self):
        breakpoint()

    def verify(self):
        self.logger.debug('Verifying statements: %s', self.account_key)
        for cur in self.statements_directories:
            cur.verify()
