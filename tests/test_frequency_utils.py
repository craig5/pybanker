#!/usr/bin/env python3 -B
"""Test for pybanker.frequency_utils class and routines."""
# python core packages
import datetime
# third party packages
import pytest
# custom packages
import pybanker.frequency_utils


def _get_today_dt():
    return datetime.date(2021, 12, 15)


@pytest.fixture
def mocked_today(mocker):
    mocked_today = mocker.patch.object(pybanker.frequency_utils, '_get_today_dt')
    mocked_today.return_value = _get_today_dt()
    return mocked_today


def test_frequency_helper_init_good(mocked_today):
    start_dt = datetime.date(2021, 11, 1)
    freq_helper = pybanker.frequency_utils.FrequencyHelper(
        'monthly', [], start_dt)
    assert freq_helper.end_dt.isoformat() == _get_today_dt().isoformat()
    assert freq_helper.buffer_days == 5
    assert freq_helper.days_delta == 30


def test_frequency_helper_init_bad_frequency():
    start_dt = datetime.date(2021, 11, 1)
    bad_freq = 'foo'
    with pytest.raises(pybanker.frequency_utils.UnknownFrequency) as exc:
        pybanker.frequency_utils.FrequencyHelper(bad_freq, [], start_dt)
    assert exc.value.args[0] == f'Unknown frequency: {bad_freq}'


def test_frequency_helper_pop_latest_doc(mocked_today):
    statement_dts = [
        datetime.date(2021, 2, 19),
        datetime.date(2021, 3, 22),
    ]
    start_dt = datetime.date(2021, 3, 15)
    freq_helper = pybanker.frequency_utils.FrequencyHelper(
        'monthly', statement_dts, start_dt)
    latest_dt = freq_helper._pop_latest_doc()
    assert latest_dt.isoformat() == '2021-02-19'
    latest_dt = freq_helper._pop_latest_doc()
    assert latest_dt.isoformat() == '2021-03-22'
    latest_dt = freq_helper._pop_latest_doc()
    assert latest_dt is None


def test_frequency_helper_increment_frequency(mocked_today):
    start_dt = datetime.date(2021, 3, 15)
    freq_helper = pybanker.frequency_utils.FrequencyHelper(
        'monthly', list(), start_dt)
    next_dt = freq_helper._increment_frequency(start_dt)
    assert next_dt.isoformat() == '2021-04-14'


def test_frequency_helper_find_missing_statements_good(mocked_today, caplog):
    caplog.set_level('DEBUG')
    statement_dts = [
        datetime.date(2021, 7, 1),
        datetime.date(2021, 7, 13),
        datetime.date(2021, 8, 13),
        # datetime.date(2021, 9, 13),
        datetime.date(2021, 10, 13),
        datetime.date(2021, 11, 13),
    ]
    start_dt = datetime.date(2021, 6, 15)
    freq_helper = pybanker.frequency_utils.FrequencyHelper(
        'monthly', statement_dts, start_dt)
    missing = freq_helper.find_missing_statement_dates()
    assert len(missing) == 2
    assert missing[0].isoformat() == '2021-09-12'
    assert missing[1].isoformat() == '2021-12-13'


if __name__ == '__main__':
    pass
