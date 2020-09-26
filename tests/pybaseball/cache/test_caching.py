import os
import pathlib
import pickle
import shutil
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple
from unittest.mock import MagicMock, mock_open, patch

import pandas as pd
import pytest
from _pytest.monkeypatch import MonkeyPatch

from pybaseball import cache

@pytest.fixture(name='save_mock')
def _save_mock(monkeypatch: MonkeyPatch) -> MagicMock:
    mock = MagicMock()
    monkeypatch.setattr(cache.dataframe_cache, 'save', mock)
    return mock


@pytest.fixture(name="mock_data_1")
def _mock_data_1() -> pd.DataFrame:
    return pd.DataFrame([1, 2], columns=['a'])


@pytest.fixture(name="mock_data_2")
def _mock_data_2() -> pd.DataFrame:
    return pd.DataFrame([[1, 2], [3, 4]], columns=['a', 'b'])


class TestCacheWrapper:
    def test_cache_enable(self, monkeypatch: MonkeyPatch) -> None:
        monkeypatch.setattr(cache, 'cache_config', cache.CacheConfig(enabled=False))
        assert cache.cache_config.enabled == False
        cache.enable()
        assert cache.cache_config.enabled

    def test_cache_disable(self, monkeypatch: MonkeyPatch) -> None:
        monkeypatch.setattr(cache, 'cache_config', cache.CacheConfig(enabled=True))
        assert cache.cache_config.enabled
        cache.disable()
        assert cache.cache_config.enabled == False

    def test_cache_config_override_default(self, mkdir: MagicMock) -> None:
        df_cache = cache.dataframe_cache()
        assert df_cache.cache_config == cache.cache_config
        assert mkdir.called_once_with(cache.cache_config.cache_directory)

    def test_cache_config_override_set(self, mkdir: MagicMock) -> None:
        override = cache.CacheConfig(enabled=True, cache_directory='~/my_dir', expiration=timedelta(days=7),
                                       cache_type=cache.CacheType.PICKLE)
        df_cache = cache.dataframe_cache(cache_config_override=override)
        assert df_cache.cache_config == override
        assert mkdir.called_once_with('~/my_dir')

    def test_cache_config_reset_cache_default(self) -> None:
        df_cache = cache.dataframe_cache()
        assert df_cache.reset_cache == False

    def test_cache_config_reset_cache_set(self) -> None:
        df_cache = cache.dataframe_cache(reset_cache=True)
        assert df_cache.reset_cache == True

    def test_extension(self) -> None:
        assert cache.dataframe_cache().extension == cache.cache_config.cache_type.value

        for cache_type in cache.CacheType:
            override = cache.CacheConfig(cache_type=cache_type)
            df_cache = cache.dataframe_cache(cache_config_override=override)

            assert df_cache.extension == cache_type.value

    def test_call_cache_disabled(self, monkeypatch: MonkeyPatch, save_mock: MagicMock) -> None:
        df_func = MagicMock(return_value=pd.DataFrame([1, 2], columns=['a']))

        load_mock = MagicMock()

        df_cache = cache.dataframe_cache()
        monkeypatch.setattr(df_cache, 'load', load_mock)

        assert df_cache.cache_config.enabled == False

        wrapper = df_cache.__call__(df_func)

        wrapper(*(1, 2), **{'val1': 'a'})

        df_func.assert_called_once_with(1, 2, val1='a')
        load_mock.assert_not_called()
        save_mock.assert_not_called()

    def test_call_cache_enabled_loads_cache(self, monkeypatch: MonkeyPatch, mock_data_1: pd.DataFrame,
                                            save_mock: MagicMock) -> None:
        monkeypatch.setattr(os.path, 'exists', MagicMock(return_value=True))
        monkeypatch.setattr(os.path, 'getmtime', MagicMock(return_value=datetime.now().timestamp()))

        df_func = MagicMock()
        df_func.__name__ = "df_func"

        load_mock = MagicMock(return_value=mock_data_1)

        df_cache = cache.dataframe_cache(cache_config_override=cache.CacheConfig(enabled=True))
        monkeypatch.setattr(df_cache, 'load', load_mock)

        assert df_cache.cache_config.enabled == True

        wrapper = df_cache.__call__(df_func)

        result = wrapper(*(1, 2), **{'val1': 'a'})

        expected_filename = os.path.join(
            df_cache.cache_config.cache_directory,
            cache.get_func_hash(df_func, (1, 2), {'val1': 'a'}) + "." + df_cache.extension
        )

        load_mock.assert_called_once_with(expected_filename)
        df_func.assert_not_called()
        save_mock.assert_not_called()

        assert isinstance(result, pd.DataFrame)

        pd.testing.assert_frame_equal(result, mock_data_1)

    def test_call_cache_ignores_expired(self, monkeypatch: MonkeyPatch, mock_data_1: pd.DataFrame,
                                        save_mock: MagicMock) -> None:
        a_week_ago = (datetime.now()-timedelta(days=7)).timestamp()

        monkeypatch.setattr(os.path, 'exists', MagicMock(return_value=True))
        monkeypatch.setattr(os.path, 'getmtime', MagicMock(return_value=a_week_ago))

        df_func = MagicMock(return_value=mock_data_1)
        df_func.__name__ = "df_func"

        load_mock = MagicMock()

        df_cache = cache.dataframe_cache(cache_config_override=cache.CacheConfig(enabled=True))
        monkeypatch.setattr(df_cache, 'load', load_mock)

        assert df_cache.cache_config.enabled == True

        wrapper = df_cache.__call__(df_func)

        wrapper(*(1, 2), **{'val1': 'a'})

        expected_filename = os.path.join(
            df_cache.cache_config.cache_directory,
            cache.get_func_hash(df_func, (1, 2), {'val1': 'a'}) + "." + df_cache.extension
        )

        df_func.assert_called_once_with(1, 2, val1='a')
        load_mock.assert_not_called()

        save_mock.assert_called_once()
        pd.testing.assert_frame_equal(mock_data_1, save_mock.call_args[0][0])
        assert expected_filename == save_mock.call_args[0][1]

    def test_call_cache_gets_uncached_data(self, monkeypatch: MonkeyPatch, mock_data_1: pd.DataFrame,
                                           save_mock: MagicMock) -> None:
        monkeypatch.setattr(os.path, 'exists', MagicMock(return_value=False))

        df_func = MagicMock(return_value=mock_data_1)
        df_func.__name__ = "df_func" # type: ignore

        load_mock = MagicMock()

        df_cache = cache.dataframe_cache(cache_config_override=cache.CacheConfig(enabled=True))
        monkeypatch.setattr(df_cache, 'load', load_mock)

        assert df_cache.cache_config.enabled == True

        wrapper = df_cache.__call__(df_func)

        wrapper(*(1, 2), **{'val1': 'a'})

        expected_filename = os.path.join(
            df_cache.cache_config.cache_directory,
            cache.get_func_hash(df_func, (1, 2), {'val1': 'a'}) + "." + df_cache.extension
        )

        df_func.assert_called_once_with(1, 2, val1='a')
        load_mock.assert_not_called()

        save_mock.assert_called_once()
        pd.testing.assert_frame_equal(mock_data_1, save_mock.call_args[0][0])
        assert expected_filename == save_mock.call_args[0][1]

    def test_call_cache_resets_cache(self, monkeypatch: MonkeyPatch, remove: MagicMock) -> None:
        test_filename = 'df_func().csv'

        monkeypatch.setattr(os, 'listdir', MagicMock(return_value=[test_filename]))

        df_func = MagicMock()
        df_func.__name__ = 'df_func' # type: ignore

        df_cache = cache.dataframe_cache(cache_config_override=cache.CacheConfig(enabled=True), reset_cache=True)

        assert df_cache.cache_config.enabled == True
        assert df_cache.reset_cache == True

        df_cache.__call__(df_func)

        assert df_cache.reset_cache == False
        remove.assert_called_once_with(os.path.join(df_cache.cache_config.cache_directory, test_filename))

    def test_call_cache_fails_silently_and_calls_wrapped_function(self, monkeypatch: MonkeyPatch,
                                                                  mock_data_1: pd.DataFrame,
                                                                  save_mock: MagicMock) -> None:
        def _thrower(*args: Any, **kwargs: Any) -> bool:
            raise Exception


        df_func = MagicMock(return_value=mock_data_1)
        df_func.__name__ = "df_func"

        load_mock = MagicMock()

        df_cache = cache.dataframe_cache(cache_config_override=cache.CacheConfig(enabled=True))
        monkeypatch.setattr(df_cache, 'load', load_mock)
        monkeypatch.setattr(cache, 'get_func_hash', _thrower)

        assert df_cache.cache_config.enabled == True

        wrapper = df_cache.__call__(df_func)

        result = wrapper(*(1, 2), **{'val1': 'a'})

        assert isinstance(result, pd.DataFrame)

        pd.testing.assert_frame_equal(result, mock_data_1)
        load_mock.assert_not_called()
        save_mock.assert_not_called()

    @pytest.mark.parametrize(
        "cache_type, method", [
            (cache.CacheType.CSV, 'read_csv'),
            (cache.CacheType.PARQUET, 'read_parquet'),
            (cache.CacheType.PICKLE, 'read_pickle'),
        ]
    )
    def test_load(self, monkeypatch: MonkeyPatch, cache_type: cache.CacheType, method: str) -> None:
        read_mock = MagicMock()
        monkeypatch.setattr(pd, method, read_mock)

        df_cache = cache.dataframe_cache(
            cache_config_override=cache.CacheConfig(enabled=True, cache_type=cache_type)
        )

        test_filename = f'test.{df_cache.extension}'

        df_cache.load(test_filename)

        assert read_mock.called_once_with(test_filename)

    def test_load_invalid_cache_type(self, monkeypatch: MonkeyPatch) -> None:
        read_csv_mock = MagicMock()
        monkeypatch.setattr(pd, 'read_csv', read_csv_mock)

        df_cache = cache.dataframe_cache(
            cache_config_override=cache.CacheConfig(enabled=True, cache_type="exe") # type: ignore
        )

        test_filename = 'test.csv'

        with pytest.raises(ValueError):
            df_cache.load(test_filename)

        read_csv_mock.assert_not_called()

    @pytest.mark.parametrize(
        "cache_type, method", [
            (cache.CacheType.CSV, 'to_csv'),
            (cache.CacheType.PARQUET, 'to_parquet'),
            (cache.CacheType.PICKLE, 'to_pickle'),
        ]
    )
    def test_save(self, monkeypatch: MonkeyPatch, mock_data_1: pd.DataFrame, cache_type: cache.CacheType,
                  method: str) -> None:
        to_method = MagicMock()
        monkeypatch.setattr(mock_data_1, method, to_method)

        df_cache = cache.dataframe_cache(
            cache_config_override=cache.CacheConfig(enabled=True, cache_type=cache_type)
        )

        test_filename = f'test.{df_cache.extension}'

        df_cache.save(mock_data_1, test_filename)

        assert to_method.called_once_with(test_filename)

    def test_save_invalid_cache_type(self, monkeypatch: MonkeyPatch, mock_data_1: pd.DataFrame) -> None:
        pickle_dump = MagicMock()
        monkeypatch.setattr(pickle, 'dump', pickle_dump)

        df_cache = cache.dataframe_cache(
            cache_config_override=cache.CacheConfig(enabled=True, cache_type="exe") # type: ignore
        )
        test_filename = 'test.pickle'

        open_mock = mock_open(read_data=b'')
        with patch('pybaseball.cache.open', open_mock):
            with pytest.raises(ValueError):
                df_cache.save(mock_data_1, test_filename)

        open_mock.assert_not_called()
        pickle_dump.assert_not_called()


def test_flush(rmtree: MagicMock, mkdir: MagicMock) -> None:
    cache.flush()

    assert rmtree.called_once_with(cache.cache_config.cache_directory)
    assert mkdir.called_once_with(cache.cache_config.cache_directory)
