import os
import pathlib
import pickle
import shutil
from datetime import datetime, timedelta
from unittest.mock import MagicMock, mock_open, patch

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from pybaseball.datahelpers import caching


@pytest.fixture(autouse=True, name="mkdir")
def _mkdir(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr(caching, '_mkdir', mock)
    return mock


@pytest.fixture(autouse=True, name="remove")
def _remove(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr(caching, '_remove', mock)
    return mock


@pytest.fixture(autouse=True, name="rmtree")
def _rmtree(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr(caching, '_rmtree', mock)
    return mock


@pytest.fixture()
def mock_data_1():
    return pd.DataFrame([1, 2], columns=['a'])


@pytest.fixture()
def mock_data_2():
    return pd.DataFrame([[1, 2], [3, 4]], columns=['a', 'b'])


class TestCacheConfig:
    def test_not_enabled_default(self):
        config = caching.CacheConfig()
        assert config.enabled == False

    def test_enabled_set(self):
        config = caching.CacheConfig(enabled=True)
        assert config.enabled == True

    def test_enable(self):
        config = caching.CacheConfig()
        assert config.enabled == False

        config.enable()
        assert config.enabled == True

        config.enable(False)
        assert config.enabled == False

    def test_cache_directory_default(self, mkdir):
        config = caching.CacheConfig()
        assert config.cache_directory == caching.CacheConfig.DEFAULT_CACHE_DIR
        assert mkdir.called_once_with(caching.CacheConfig.DEFAULT_CACHE_DIR)

    def test_cache_directory_set(self, mkdir):
        my_dir: str = '~/my_dir'

        config = caching.CacheConfig(cache_directory=my_dir)
        assert config.cache_directory == my_dir
        assert mkdir.called_once_with(my_dir)

    def test_expiration_default(self):
        config = caching.CacheConfig()
        assert config.expiration == caching.CacheConfig.DEFAULT_EXPIRATION

    def test_expiration_set(self):
        my_expiration: timedelta = timedelta(days=365)

        config = caching.CacheConfig(expiration=my_expiration)
        assert config.expiration == my_expiration

    def test_cache_type_default(self):
        config = caching.CacheConfig()
        assert config.cache_type == caching.CacheType.CSV

    def test_cache_type_set(self):
        config = caching.CacheConfig(cache_type=caching.CacheType.PARQUET)
        assert config.cache_type == caching.CacheType.PARQUET


class TestCacheWrapper:
    def test_get_value_hash_str(self):
        test_str = "TESTING"

        assert caching.dataframe_cache._get_value_hash(test_str) == f"'{test_str}'"

    def test_get_value_hash_str_no_designators(self):
        test_str = "TESTING"

        assert caching.dataframe_cache._get_value_hash(test_str, include_designators=False) == test_str

    def test_get_value_hash_str_with_bad_chars(self):
        test_str = "TESTING/"

        assert caching.dataframe_cache._get_value_hash(test_str) == str(test_str.__hash__())

    def test_get_value_hash_hashable(self):
        test_float = 3.14159

        assert caching.dataframe_cache._get_value_hash(test_float) == str(test_float.__hash__())

    def test_get_value_hash_none(self):
        test_value = None

        assert caching.dataframe_cache._get_value_hash(test_value) == 'None'

    def test_get_value_hash_list(self):
        test_value = ['a', 'b']

        assert caching.dataframe_cache._get_value_hash(test_value) == "['a', 'b']"

    def test_get_value_hash_list_no_designators(self):
        test_value = ['a', 'b']

        assert caching.dataframe_cache._get_value_hash(test_value, include_designators=False) == "'a', 'b'"

    def test_get_value_hash_tuple(self):
        test_value = ('a', 'b')

        assert caching.dataframe_cache._get_value_hash(test_value) == "('a', 'b')"

    def test_get_value_hash_tuple_no_designators(self):
        test_value = ('a', 'b')

        assert caching.dataframe_cache._get_value_hash(test_value, include_designators=False) == "'a', 'b'"

    def test_get_value_hash_dict(self):
        test_value = {'a': 'foo', 'b': 'bar'}

        assert caching.dataframe_cache._get_value_hash(test_value) == "{a='foo', b='bar'}"

    def test_get_value_hash_dict_no_designators(self):
        test_value = {'a': 'foo', 'b': 'bar'}

        assert caching.dataframe_cache._get_value_hash(test_value, include_designators=False) == "a='foo', b='bar'"

    def test_get_f_name_function(self):
        def test_func():
            pass

        assert caching.dataframe_cache._get_f_name(test_func) == "test_func"

    def test_get_f_name_class_method(self):
        class test_class:
            def test_func(self):
                pass

        assert caching.dataframe_cache._get_f_name(test_class().test_func) == "test_class.test_func"

    def test_get_f_hash_no_params(self):
        def test_func(*args, **kwargs):
            pass

        assert caching.dataframe_cache._get_f_hash(test_func, (), {}) == "test_func()"

    def test_get_f_hash_with_args(self):
        def test_func(*args, **kwargs):
            pass

        expected_hash = f"test_func('a', {(1).__hash__()})"

        assert caching.dataframe_cache._get_f_hash(test_func, ('a', 1), {}) == expected_hash

    def test_get_f_hash_with_kwargs(self):
        def test_func(*args, **kwargs):
            pass

        expected_hash = f"test_func(val1={(1.5).__hash__()}, val2='b')"

        assert caching.dataframe_cache._get_f_hash(test_func, (), {'val1': 1.5, 'val2': 'b'}) == expected_hash

    def test_get_f_hash_with_args_and_kwargs(self):
        def test_func(*args, **kwargs):
            pass

        expected_hash = f"test_func('a', {(1).__hash__()}, val1={(1.5).__hash__()}, val2='b')"

        assert caching.dataframe_cache._get_f_hash(test_func, ('a', 1), {'val1': 1.5, 'val2': 'b'}) == expected_hash

    def test_cache_config_override_default(self, mkdir):
        df_cache = caching.dataframe_cache()
        assert df_cache.cache_config == caching.cache_config
        assert mkdir.called_once_with(caching.cache_config.cache_directory)

    def test_cache_config_override_set(self, mkdir):
        override = caching.CacheConfig(enabled=True, cache_directory='~/my_dir',
                                       expiration=timedelta(days=7), cache_type=caching.CacheType.PICKLE)
        df_cache = caching.dataframe_cache(cache_config_override=override)
        assert df_cache.cache_config == override
        assert mkdir.called_once_with('~/my_dir')

    def test_cache_config_reset_cache_default(self):
        df_cache = caching.dataframe_cache()
        assert df_cache.reset_cache == False

    def test_cache_config_reset_cache_set(self):
        df_cache = caching.dataframe_cache(reset_cache=True)
        assert df_cache.reset_cache == True

    def test_extension(self):
        assert caching.dataframe_cache().extension == caching.cache_config.cache_type.value

        for cache_type in caching.CacheType:
            override = caching.CacheConfig(cache_type=cache_type)
            df_cache = caching.dataframe_cache(cache_config_override=override)

            assert df_cache.extension == cache_type.value

    def test_call_cache_disabled(self):
        df_func = MagicMock(return_value=pd.DataFrame([1, 2], columns=['a']))

        df_cache = caching.dataframe_cache()
        df_cache.load = MagicMock()
        df_cache.save = MagicMock()

        assert df_cache.cache_config.enabled == False

        wrapper = df_cache.__call__(df_func)

        wrapper(*(1, 2), **{'val1': 'a'})

        df_func.assert_called_once_with(1, 2, val1='a')
        df_cache.load.assert_not_called()
        df_cache.save.assert_not_called()

    def test_call_cache_enabled_loads_cache(self, monkeypatch, mock_data_1):
        monkeypatch.setattr(os.path, 'exists', MagicMock(return_value=True))
        monkeypatch.setattr(os.path, 'getmtime', MagicMock(return_value=datetime.now().timestamp()))

        df_func = MagicMock()
        df_func.__name__ = "df_func"

        df_cache = caching.dataframe_cache(cache_config_override=caching.CacheConfig(enabled=True))
        df_cache.load = MagicMock(return_value=mock_data_1)
        df_cache.save = MagicMock()

        assert df_cache.cache_config.enabled == True

        wrapper = df_cache.__call__(df_func)

        result = wrapper(*(1, 2), **{'val1': 'a'})

        expected_filename = os.path.join(
            df_cache.cache_config.cache_directory,
            caching.dataframe_cache._get_f_hash(df_func, (1, 2), {'val1': 'a'}) + "." + df_cache.extension
        )

        df_cache.load.assert_called_once_with(expected_filename)
        df_func.assert_not_called()
        df_cache.save.assert_not_called()

        pd.testing.assert_frame_equal(result, mock_data_1)

    def test_call_cache_ignores_expired(self, monkeypatch, mock_data_1):
        a_week_ago = (datetime.now()-timedelta(days=7)).timestamp()

        monkeypatch.setattr(os.path, 'exists', MagicMock(return_value=True))
        monkeypatch.setattr(os.path, 'getmtime', MagicMock(return_value=a_week_ago))

        df_func = MagicMock(return_value=mock_data_1)
        df_func.__name__ = "df_func"

        df_cache = caching.dataframe_cache(cache_config_override=caching.CacheConfig(enabled=True))
        df_cache.load = MagicMock()
        df_cache.save = MagicMock()

        assert df_cache.cache_config.enabled == True

        wrapper = df_cache.__call__(df_func)

        wrapper(*(1, 2), **{'val1': 'a'})

        expected_filename = os.path.join(
            df_cache.cache_config.cache_directory,
            caching.dataframe_cache._get_f_hash(df_func, (1, 2), {'val1': 'a'}) + "." + df_cache.extension
        )

        df_func.assert_called_once_with(1, 2, val1='a')
        df_cache.load.assert_not_called()
        df_cache.save.assert_called_once_with(mock_data_1, expected_filename)

    def test_call_cache_gets_uncached_data(self, monkeypatch, mock_data_1):
        monkeypatch.setattr(os.path, 'exists', MagicMock(return_value=False))

        df_func = MagicMock(return_value=mock_data_1)
        df_func.__name__ = "df_func"

        df_cache = caching.dataframe_cache(cache_config_override=caching.CacheConfig(enabled=True))
        df_cache.load = MagicMock()
        df_cache.save = MagicMock()

        assert df_cache.cache_config.enabled == True

        wrapper = df_cache.__call__(df_func)

        wrapper(*(1, 2), **{'val1': 'a'})

        expected_filename = os.path.join(
            df_cache.cache_config.cache_directory,
            caching.dataframe_cache._get_f_hash(df_func, (1, 2), {'val1': 'a'}) + "." + df_cache.extension
        )

        df_func.assert_called_once_with(1, 2, val1='a')
        df_cache.load.assert_not_called()
        df_cache.save.assert_called_once_with(mock_data_1, expected_filename)

    def test_call_cache_resets_cache(self, monkeypatch, remove):
        test_filename = 'df_func().csv'
        mock_walk = [(caching.cache_config.cache_directory, [], [test_filename])]
        monkeypatch.setattr(os, 'walk', MagicMock(return_value=(x for x in mock_walk)))
        df_func = MagicMock()
        df_func.__name__ = 'df_func'

        df_cache = caching.dataframe_cache(cache_config_override=caching.CacheConfig(enabled=True), reset_cache=True)

        assert df_cache.cache_config.enabled == True
        assert df_cache.reset_cache == True

        df_cache.__call__(df_func)

        assert df_cache.reset_cache == False
        remove.assert_called_once_with(os.path.join(df_cache.cache_config.cache_directory, test_filename))

    def test_load_csv(self, monkeypatch):
        monkeypatch.setattr(pd, 'read_csv', MagicMock())

        df_cache = caching.dataframe_cache(
            cache_config_override=caching.CacheConfig(enabled=True, cache_type=caching.CacheType.CSV)
        )

        test_filename = 'test.csv'

        df_cache.load(test_filename)

        pd.read_csv.assert_called_once_with(test_filename)

    def test_load_csv_gz(self, monkeypatch):
        monkeypatch.setattr(pd, 'read_csv', MagicMock())

        df_cache = caching.dataframe_cache(
            cache_config_override=caching.CacheConfig(enabled=True, cache_type=caching.CacheType.CSV_GZ)
        )

        test_filename = 'test.csv.gz'

        df_cache.load(test_filename)

        pd.read_csv.assert_called_once_with(test_filename)

    def test_load_parquet(self, monkeypatch):
        pq_read_table = MagicMock()
        monkeypatch.setattr(pq, 'read_table', pq_read_table)

        df_cache = caching.dataframe_cache(
            cache_config_override=caching.CacheConfig(enabled=True, cache_type=caching.CacheType.PARQUET)
        )

        test_filename = 'test.parquet'

        df_cache.load(test_filename)

        pq_read_table.assert_called_once_with(test_filename)

    def test_load_pickle(self, monkeypatch, mock_data_1):
        pickle_load = MagicMock(return_value=mock_data_1)
        monkeypatch.setattr(pickle, 'load', pickle_load)

        df_cache = caching.dataframe_cache(
            cache_config_override=caching.CacheConfig(enabled=True, cache_type=caching.CacheType.PICKLE)
        )
        test_filename = 'test.pickle'

        open_mock = mock_open(read_data=b'')
        with patch('pybaseball.datahelpers.caching.open', open_mock):
            df_cache.load(test_filename)

        open_mock.assert_called_once_with(test_filename, 'rb')
        pickle_load.assert_called()

    def test_save_csv(self, monkeypatch, mock_data_1):
        to_csv = MagicMock()
        monkeypatch.setattr(mock_data_1, 'to_csv', to_csv)

        df_cache = caching.dataframe_cache(
            cache_config_override=caching.CacheConfig(enabled=True, cache_type=caching.CacheType.CSV)
        )

        test_filename = 'test.csv'

        df_cache.save(mock_data_1, test_filename)

        to_csv.assert_called_once_with(test_filename)

    def test_save_csv_gz(self, monkeypatch, mock_data_1):
        to_csv = MagicMock()
        monkeypatch.setattr(mock_data_1, 'to_csv', to_csv)

        df_cache = caching.dataframe_cache(
            cache_config_override=caching.CacheConfig(enabled=True, cache_type=caching.CacheType.CSV_GZ)
        )

        test_filename = 'test.csv.gz'

        df_cache.save(mock_data_1, test_filename)

        to_csv.assert_called_once_with(test_filename)

    def test_save_parquet(self, monkeypatch, mock_data_1):
        pq_write_table = MagicMock()
        monkeypatch.setattr(pq, 'write_table', pq_write_table)

        df_cache = caching.dataframe_cache(
            cache_config_override=caching.CacheConfig(enabled=True, cache_type=caching.CacheType.PARQUET)
        )

        test_filename = 'test.parquet'

        df_cache.save(mock_data_1, test_filename)

        pq_write_table.assert_called_once_with(pa.Table.from_pandas(mock_data_1), test_filename)

    def test_save_pickle(self, monkeypatch, mock_data_1):
        pickle_dump = MagicMock(return_value=mock_data_1)
        monkeypatch.setattr(pickle, 'dump', pickle_dump)

        df_cache = caching.dataframe_cache(
            cache_config_override=caching.CacheConfig(enabled=True, cache_type=caching.CacheType.PICKLE)
        )
        test_filename = 'test.pickle'

        open_mock = mock_open(read_data=b'')
        with patch('pybaseball.datahelpers.caching.open', open_mock):
            df_cache.save(mock_data_1, test_filename)

        open_mock.assert_called_once_with(test_filename, 'wb')
        pickle_dump.assert_called()


def test_bust_cache(rmtree, mkdir):
    caching.bust_cache()

    assert rmtree.called_once_with(caching.cache_config.cache_directory)
    assert mkdir.called_once_with(caching.cache_config.cache_directory)
