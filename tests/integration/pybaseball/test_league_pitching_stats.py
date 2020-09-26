from datetime import date, datetime, timedelta

import pytest

from pybaseball import league_pitching_stats


def test_sanitize_input_none_none() -> None:
    result1, result2 = league_pitching_stats.sanitize_input(None, None)
    
    assert datetime.strptime(result1, '%Y-%m-%d').date() == date.today() - timedelta(days=1)
    assert datetime.strptime(result2, '%Y-%m-%d').date() == date.today()


def test_sanitize_input_end_dt_none() -> None:
    result1, result2 = league_pitching_stats.sanitize_input('2019-05-01', None)
    
    assert result1 == '2019-05-01'
    assert result2 == result1


def test_sanitize_input_start_dt_gt_end_dt() -> None:
    result1, result2 = league_pitching_stats.sanitize_input('2019-07-01', '2019-06-01')

    assert result1 == '2019-06-01'
    assert result2 == '2019-07-01'


def test_sanitize_input_start_dt_none() -> None:
    result1, result2 = league_pitching_stats.sanitize_input(None, '2019-06-01')
    
    assert result2 == '2019-06-01'
    assert result1 == result2


def test_get_soup_none_none() -> None:
    result = league_pitching_stats.get_soup(None, None)
    assert result is None


def test_pitching_stats_range_start_dt_lt_2008() -> None:
    with pytest.raises(ValueError):
        league_pitching_stats.pitching_stats_range('2007-01-01', '2019-01-01')


def test_pitching_stats_bref() -> None:
    result = league_pitching_stats.pitching_stats_bref(2019)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 40
    assert(len(result)) == 831


def test_pitching_stats_bref_none() -> None:
    result = league_pitching_stats.pitching_stats_bref(None)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 40
    assert(len(result)) == 729


def test_pitching_stats_bref_future() -> None:
    with pytest.raises(IndexError):
        league_pitching_stats.pitching_stats_bref(datetime.today().year + 1)


def test_pitching_stats_bref_bad_year() -> None:
    with pytest.raises(ValueError):
        league_pitching_stats.pitching_stats_bref('NOT A YEAR')


def test_bwar_pitch() -> None:
    result = league_pitching_stats.bwar_pitch()

    assert result is not None
    assert not result.empty

    bwar_pitch_2019 = result.query('year_ID == 2019')

    assert len(bwar_pitch_2019.columns) == 19
    assert(len(bwar_pitch_2019)) == 938


def test_bwar_pitch_return_all() -> None:
    result = league_pitching_stats.bwar_pitch(return_all=True)

    assert result is not None
    assert not result.empty

    bwar_pitch_2019 = result.query('year_ID == 2019')

    assert len(bwar_pitch_2019.columns) == 43
    assert(len(bwar_pitch_2019)) == 938
