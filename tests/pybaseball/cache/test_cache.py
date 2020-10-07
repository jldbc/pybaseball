from datetime import datetime, timedelta
from typing import Callable
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from _pytest.monkeypatch import MonkeyPatch
from pybaseball import cache


@pytest.fixture(name="mock_data_1")
def _mock_data_1() -> pd.DataFrame:
    return pd.DataFrame([1, 2], columns=['a'])


@pytest.fixture(name='empty_load_mock')
def _empty_load_mock(monkeypatch: MonkeyPatch) -> MagicMock:
    load_mock = MagicMock(return_value=None)
    monkeypatch.setattr(cache.dataframe_utils, 'load_df', load_mock)
    return load_mock

@pytest.fixture(name='load_mock')
def _load_mock(monkeypatch: MonkeyPatch, mock_data_1: pd.DataFrame) -> MagicMock:
    load_mock = MagicMock(return_value=mock_data_1)
    monkeypatch.setattr(cache.dataframe_utils, 'load_df', load_mock)
    return load_mock


@pytest.fixture(name='save_mock')
def _save_mock(monkeypatch: MonkeyPatch) -> MagicMock:
    save_mock = MagicMock()
    monkeypatch.setattr(cache.dataframe_utils, 'save_df', save_mock)
    return save_mock


def test_cache_enable() -> None:
    enable_mock = MagicMock()
    with patch('pybaseball.cache.config.enable', enable_mock):
        cache.enable()
        enable_mock.assert_called_once_with(True)


def test_cache_disable() -> None:
    enable_mock = MagicMock()
    with patch('pybaseball.cache.config.enable', enable_mock):
        cache.disable()
        enable_mock.assert_called_once_with(False)


@patch('pybaseball.cache.config.enabled', False)
def test_call_cache_disabled(load_mock: MagicMock, save_mock: MagicMock) -> None:
    df_func = MagicMock(return_value=pd.DataFrame([1, 2], columns=['a']))
    df_func.__name__ = "df_func"

    df_cache = cache.df_cache()
    assert not df_cache.cache_config.enabled

    wrapper = df_cache.__call__(df_func)
    wrapper(*(1, 2), **{'val1': 'a'})

    df_func.assert_called_once_with(1, 2, val1='a')
    load_mock.assert_not_called()
    save_mock.assert_not_called()


@patch('os.path.exists', MagicMock(return_value=True))
@patch('os.path.getmtime', MagicMock(return_value=datetime.now().timestamp()))
@patch('pybaseball.cache.config.enabled', True)
@patch('glob.glob', MagicMock(return_value=['1.cache_record.json']))
@patch('pybaseball.cache.file_utils.load_json', MagicMock(
    return_value={
        'expires': '3000-01-01',
        'func': 'df_func',
        'args': [1, 2],
        'kwargs': {'val1': 'a'},
        'dataframe': 'cachefile.csv'
    }
))
def test_call_cache_enabled_loads_cache(mock_data_1: pd.DataFrame, load_mock: MagicMock, save_mock: MagicMock) -> None:
    df_func = MagicMock()
    df_func.__name__ = "df_func"

    df_cache = cache.df_cache()
    assert df_cache.cache_config.enabled

    wrapper = df_cache.__call__(df_func)
    result = wrapper(*(1, 2), **{'val1': 'a'})

    load_mock.assert_called_once()
    df_func.assert_not_called()
    save_mock.assert_not_called()

    assert isinstance(result, pd.DataFrame)

    pd.testing.assert_frame_equal(result, mock_data_1)


@patch('os.path.exists', MagicMock(return_value=True))
@patch('os.path.getmtime', MagicMock(return_value=datetime.now()-timedelta(days=7)).timestamp())
@patch('pybaseball.cache.config.enabled', True)
@patch('glob.glob', MagicMock(return_value=['1.cache_record.json']))
@patch('pybaseball.cache.file_utils.load_json', MagicMock(
    return_value={'expires': '2020-01-01', 'filename': 'old_file.csv'}
))
def test_call_cache_ignores_expired(mock_data_1: pd.DataFrame, load_mock: MagicMock, save_mock: MagicMock) -> None:
    df_func = MagicMock(return_value=mock_data_1)
    df_func.__name__ = "df_func"

    df_cache = cache.df_cache()
    assert df_cache.cache_config.enabled

    wrapper = df_cache.__call__(df_func)
    wrapper(*(1, 2), **{'val1': 'a'})

    df_func.assert_called_once_with(1, 2, val1='a')
    load_mock.assert_not_called()

    save_mock.assert_called_once()
    pd.testing.assert_frame_equal(mock_data_1, save_mock.call_args[0][0])


@patch('pybaseball.cache.config.enabled', True)
@patch('glob.glob', MagicMock(return_value=[]))
@patch('os.path.exists', MagicMock(return_value=False))
def test_call_cache_gets_uncached_data(mock_data_1: pd.DataFrame, load_mock: MagicMock, save_mock: MagicMock) -> None:
    df_func = MagicMock(return_value=mock_data_1)
    df_func.__name__ = "df_func"  # type: ignore

    df_cache = cache.df_cache()
    assert df_cache.cache_config.enabled

    wrapper = df_cache.__call__(df_func)
    wrapper(*(1, 2), **{'val1': 'a'})

    df_func.assert_called_once_with(1, 2, val1='a')
    load_mock.assert_not_called()

    save_mock.assert_called_once()
    pd.testing.assert_frame_equal(mock_data_1, save_mock.call_args[0][0])


@patch('pybaseball.cache.config.enabled', True)
def test_call_cache_get_func_data_fails_silently(mock_data_1: pd.DataFrame, thrower: Callable, load_mock: MagicMock,
                                                 save_mock: MagicMock) -> None:
    assert cache.config.enabled

    df_func = MagicMock(return_value=mock_data_1)
    df_func.__name__ = "df_func"

    df_cache = cache.cache.df_cache()
    assert df_cache.cache_config.enabled

    with patch('pybaseball.cache.func_utils.get_func_name', thrower):
        wrapper = df_cache.__call__(df_func)
        result = wrapper(*(1, 2), **{'val1': 'a'})

    assert isinstance(result, pd.DataFrame)

    pd.testing.assert_frame_equal(result, mock_data_1)
    load_mock.assert_not_called()
    save_mock.assert_not_called()


@patch('pybaseball.cache.config.enabled', True)
def test_call_cache_load_fails_silently(mock_data_1: pd.DataFrame, thrower: Callable, load_mock: MagicMock,
                                        save_mock: MagicMock) -> None:
    assert cache.config.enabled
    df_func = MagicMock(return_value=mock_data_1)
    df_func.__name__ = "df_func"

    df_cache = cache.cache.df_cache()
    assert df_cache.cache_config.enabled

    with patch('glob.glob', thrower):
        wrapper = df_cache.__call__(df_func)
        result = wrapper(*(1, 2), **{'val1': 'a'})

    assert isinstance(result, pd.DataFrame)

    pd.testing.assert_frame_equal(result, mock_data_1)
    load_mock.assert_not_called()
    save_mock.assert_called_once()


@patch('pybaseball.cache.config.enabled', True)
def test_call_cache_save_fails_silently(mock_data_1: pd.DataFrame, thrower: Callable, empty_load_mock: MagicMock,
                                        save_mock: MagicMock) -> None:
    assert cache.config.enabled

    df_func = MagicMock(return_value=mock_data_1)
    df_func.__name__ = "df_func"

    df_cache = cache.cache.df_cache()
    assert df_cache.cache_config.enabled

    with patch.object(cache.cache_record.CacheRecord, 'save', thrower):
        wrapper = df_cache.__call__(df_func)
        result = wrapper(*(1, 2), **{'val1': 'a'})

    assert isinstance(result, pd.DataFrame)

    pd.testing.assert_frame_equal(result, mock_data_1)
    empty_load_mock.assert_called_once()
    save_mock.assert_not_called()


def test_purge(remove: MagicMock) -> None:
    glob_result = ['1.cache_record.json', '2.cache_record.json']
    glob_mock = MagicMock(return_value=glob_result)

    mock_cache_record = {'expires': '3000-01-01', 'filename': 'df_cache.parquet'}
    mock_load_json = MagicMock(return_value=mock_cache_record)

    with patch('glob.glob', glob_mock):
        with patch('pybaseball.cache.file_utils.load_json', mock_load_json):
            cache.purge()

    assert glob_mock.called_once()
    assert mock_load_json.call_count == len(glob_result)
    assert remove.call_count == len(glob_result)


def test_flush(remove: MagicMock) -> None:
    glob_result = ['1.cache_record.json', '2.cache_record.json']
    glob_mock = MagicMock(return_value=glob_result)

    mock_cache_records = [
        {'expires': '2000-01-01', 'filename': 'df_cache.parquet'},
        {'expires': '3000-01-01', 'filename': 'df_cache2.parquet'},
    ]
    mock_load_json = MagicMock(side_effect=mock_cache_records)

    with patch('glob.glob', glob_mock):
        with patch('pybaseball.cache.file_utils.load_json', mock_load_json):
            cache.flush()

    assert glob_mock.called_once()
    assert mock_load_json.call_count == len(glob_result)
    remove.assert_called_once()
