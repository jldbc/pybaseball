import os
import pathlib
import pickle
import shutil
from datetime import datetime, timedelta
from typing import Any, List, Tuple
from unittest.mock import MagicMock, mock_open, patch

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pytest
from _pytest.monkeypatch import MonkeyPatch

from pybaseball.datahelpers import caching

# Autouse to prevent file system side effects
@pytest.fixture(autouse=True, name="mkdir")
def _mkdir(monkeypatch: MonkeyPatch) -> MagicMock:
    mock = MagicMock()
    monkeypatch.setattr('pathlib.Path.mkdir', mock)
    return mock


# Autouse to prevent file system side effects
@pytest.fixture(autouse=True, name="remove")
def _remove(monkeypatch: MonkeyPatch) -> MagicMock:
    mock = MagicMock()
    monkeypatch.setattr(os, 'remove', mock)
    return mock


# Autouse to prevent file system side effects
@pytest.fixture(autouse=True, name="rmtree")
def _rmtree(monkeypatch: MonkeyPatch) -> MagicMock:
    mock = MagicMock()
    monkeypatch.setattr(shutil, 'rmtree', mock)
    return mock

# Autouse to prevent file system side effects
@pytest.fixture(autouse=True)
def _override_cache_directory(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(
        caching,
        'cache_config',
        caching.CacheConfig(cache_directory=os.path.join(caching.CacheConfig().cache_directory, '.pytest'))
    )
    assert not os.path.exists(caching.cache_config.cache_directory)

@pytest.fixture(name='save_mock')
def _save_mock(monkeypatch: MonkeyPatch) -> MagicMock:
    mock = MagicMock()
    monkeypatch.setattr(caching.dataframe_cache, 'save', mock)
    return mock


@pytest.fixture(name="mock_data_1")
def _mock_data_1() -> pd.DataFrame:
    return pd.DataFrame([1, 2], columns=['a'])


@pytest.fixture(name="mock_data_2")
def _mock_data_2() -> pd.DataFrame:
    return pd.DataFrame([[1, 2], [3, 4]], columns=['a', 'b'])


class TestCacheConfig:
    def test_not_enabled_default(self) -> None:
        config = caching.CacheConfig()
        assert config.enabled == False

    def test_enabled_set(self) -> None:
        config = caching.CacheConfig(enabled=True)
        assert config.enabled == True

    def test_enable(self) -> None:
        config = caching.CacheConfig()
        assert config.enabled == False

        config.enable()
        assert config.enabled == True

        config.enable(False)
        assert config.enabled == False

    def test_cache_directory_default(self, mkdir: MagicMock) -> None:
        config = caching.CacheConfig()
        assert config.cache_directory == caching.CacheConfig.DEFAULT_CACHE_DIR
        assert mkdir.called_once_with(caching.CacheConfig.DEFAULT_CACHE_DIR)

    def test_cache_directory_set(self, mkdir: MagicMock) -> None:
        my_dir: str = '~/my_dir'

        config = caching.CacheConfig(cache_directory=my_dir)
        assert config.cache_directory == my_dir
        assert mkdir.called_once_with(my_dir)

    def test_expiration_default(self) -> None:
        config = caching.CacheConfig()
        assert config.expiration == caching.CacheConfig.DEFAULT_EXPIRATION

    def test_expiration_set(self) -> None:
        my_expiration: timedelta = timedelta(days=365)

        config = caching.CacheConfig(expiration=my_expiration)
        assert config.expiration == my_expiration

    def test_cache_type_default(self) -> None:
        config = caching.CacheConfig()
        assert config.cache_type == caching.CacheType.CSV

    def test_cache_type_set(self) -> None:
        config = caching.CacheConfig(cache_type=caching.CacheType.PARQUET)
        assert config.cache_type == caching.CacheType.PARQUET


class TestCacheWrapper:
    def test_get_value_hash_str(self) -> None:
        test_str = "TESTING"

        assert caching.dataframe_cache._get_value_hash(test_str) == f"'{test_str}'"

    def test_get_value_hash_str_no_designators(self) -> None:
        test_str = "TESTING"

        assert caching.dataframe_cache._get_value_hash(test_str, include_designators=False) == test_str

    def test_get_value_hash_str_with_bad_chars(self) -> None:
        test_str = "TESTING/"

        assert caching.dataframe_cache._get_value_hash(test_str) == str(test_str.__hash__())

    def test_get_value_hash_hashable(self) -> None:
        test_float = 3.14159

        assert caching.dataframe_cache._get_value_hash(test_float) == str(test_float.__hash__())

    def test_get_value_hash_none(self) -> None:
        test_value = None

        assert caching.dataframe_cache._get_value_hash(test_value) == 'None'

    def test_get_value_hash_list(self) -> None:
        test_value = ['a', 'b']

        assert caching.dataframe_cache._get_value_hash(test_value) == "['a', 'b']"

    def test_get_value_hash_list_no_designators(self) -> None:
        test_value = ['a', 'b']

        assert caching.dataframe_cache._get_value_hash(test_value, include_designators=False) == "'a', 'b'"

    def test_get_value_hash_tuple(self) -> None:
        test_value = ('a', 'b')

        assert caching.dataframe_cache._get_value_hash(test_value) == "('a', 'b')"

    def test_get_value_hash_tuple_no_designators(self) -> None:
        test_value = ('a', 'b')

        assert caching.dataframe_cache._get_value_hash(test_value, include_designators=False) == "'a', 'b'"

    def test_get_value_hash_dict(self) -> None:
        test_value = {'a': 'foo', 'b': 'bar'}

        assert caching.dataframe_cache._get_value_hash(test_value) == "{a='foo', b='bar'}"

    def test_get_value_hash_dict_no_designators(self) -> None:
        test_value = {'a': 'foo', 'b': 'bar'}

        assert caching.dataframe_cache._get_value_hash(test_value, include_designators=False) == "a='foo', b='bar'"

    def test_get_value_hash_non_hashable(self) -> None:
        class NonHashable:
            def __hash__(self) -> int:
                raise NotImplementedError

        with pytest.raises(ValueError):
            print(caching.dataframe_cache._get_value_hash(NonHashable()))

    def test_get_f_name_function(self) -> None:
        def test_func() -> None:
            pass

        assert caching.dataframe_cache._get_f_name(test_func) == "test_func"

    def test_get_f_name_class_method(self) -> None:
        class test_class:
            def test_func(self) -> None:
                pass

        assert caching.dataframe_cache._get_f_name(test_class().test_func) == "test_class.test_func"

    def test_get_f_hash_no_params(self) -> None:
        def test_func(*args: Any, **kwargs: Any) -> None:
            pass

        assert caching.dataframe_cache._get_f_hash(test_func, (), {}) == "test_func()"

    def test_get_f_hash_with_args(self) -> None:
        def test_func(*args: Any, **kwargs: Any) -> None:
            pass

        expected_hash = f"test_func('a', {(1).__hash__()})"

        assert caching.dataframe_cache._get_f_hash(test_func, ('a', 1), {}) == expected_hash

    def test_get_f_hash_with_kwargs(self) -> None:
        def test_func(*args: Any, **kwargs: Any) -> None:
            pass

        expected_hash = f"test_func(val1={(1.5).__hash__()}, val2='b')"

        assert caching.dataframe_cache._get_f_hash(test_func, (), {'val1': 1.5, 'val2': 'b'}) == expected_hash

    def test_get_f_hash_with_args_and_kwargs(self) -> None:
        def test_func(*args: Any, **kwargs: Any) -> None:
            pass

        expected_hash = f"test_func('a', {(1).__hash__()}, val1={(1.5).__hash__()}, val2='b')"

        assert caching.dataframe_cache._get_f_hash(test_func, ('a', 1), {'val1': 1.5, 'val2': 'b'}) == expected_hash

    def test_get_f_hash_long_path_windows(self) -> None:
        def test_func(*args: Any, **kwargs: Any) -> None:
            pass

        expected_hash = "test_func(93ece9cbe326c434412e28b87d466bd08bc0f2e7db0770cff852e7b9f46240d8)"

        long_kwargs = {f"val{str(x)}": x for x in range(caching.dataframe_cache.MAX_ARGS_KEY_LENGTH)}

        assert caching.dataframe_cache._get_f_hash(test_func, ('a', 1), long_kwargs) == expected_hash

    def test_cache_config_override_default(self, mkdir: MagicMock) -> None:
        df_cache = caching.dataframe_cache()
        assert df_cache.cache_config == caching.cache_config
        assert mkdir.called_once_with(caching.cache_config.cache_directory)

    def test_cache_config_override_set(self, mkdir: MagicMock) -> None:
        override = caching.CacheConfig(enabled=True, cache_directory='~/my_dir', expiration=timedelta(days=7),
                                       cache_type=caching.CacheType.PICKLE)
        df_cache = caching.dataframe_cache(cache_config_override=override)
        assert df_cache.cache_config == override
        assert mkdir.called_once_with('~/my_dir')

    def test_cache_config_reset_cache_default(self) -> None:
        df_cache = caching.dataframe_cache()
        assert df_cache.reset_cache == False

    def test_cache_config_reset_cache_set(self) -> None:
        df_cache = caching.dataframe_cache(reset_cache=True)
        assert df_cache.reset_cache == True

    def test_extension(self) -> None:
        assert caching.dataframe_cache().extension == caching.cache_config.cache_type.value

        for cache_type in caching.CacheType:
            override = caching.CacheConfig(cache_type=cache_type)
            df_cache = caching.dataframe_cache(cache_config_override=override)

            assert df_cache.extension == cache_type.value

    def test_call_cache_disabled(self, monkeypatch: MonkeyPatch, save_mock: MagicMock) -> None:
        df_func = MagicMock(return_value=pd.DataFrame([1, 2], columns=['a']))

        load_mock = MagicMock()

        df_cache = caching.dataframe_cache()
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

        df_cache = caching.dataframe_cache(cache_config_override=caching.CacheConfig(enabled=True))
        monkeypatch.setattr(df_cache, 'load', load_mock)

        assert df_cache.cache_config.enabled == True

        wrapper = df_cache.__call__(df_func)

        result = wrapper(*(1, 2), **{'val1': 'a'})

        expected_filename = os.path.join(
            df_cache.cache_config.cache_directory,
            caching.dataframe_cache._get_f_hash(df_func, (1, 2), {'val1': 'a'}) + "." + df_cache.extension
        )

        load_mock.assert_called_once_with(expected_filename)
        df_func.assert_not_called()
        save_mock.assert_not_called()

        pd.testing.assert_frame_equal(result, mock_data_1)

    def test_call_cache_ignores_expired(self, monkeypatch: MonkeyPatch, mock_data_1: pd.DataFrame,
                                        save_mock: MagicMock) -> None:
        a_week_ago = (datetime.now()-timedelta(days=7)).timestamp()

        monkeypatch.setattr(os.path, 'exists', MagicMock(return_value=True))
        monkeypatch.setattr(os.path, 'getmtime', MagicMock(return_value=a_week_ago))

        df_func = MagicMock(return_value=mock_data_1)
        df_func.__name__ = "df_func"
        
        load_mock = MagicMock()

        df_cache = caching.dataframe_cache(cache_config_override=caching.CacheConfig(enabled=True))
        monkeypatch.setattr(df_cache, 'load', load_mock)

        assert df_cache.cache_config.enabled == True

        wrapper = df_cache.__call__(df_func)

        wrapper(*(1, 2), **{'val1': 'a'})

        expected_filename = os.path.join(
            df_cache.cache_config.cache_directory,
            caching.dataframe_cache._get_f_hash(df_func, (1, 2), {'val1': 'a'}) + "." + df_cache.extension
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

        df_cache = caching.dataframe_cache(cache_config_override=caching.CacheConfig(enabled=True))
        monkeypatch.setattr(df_cache, 'load', load_mock)

        assert df_cache.cache_config.enabled == True

        wrapper = df_cache.__call__(df_func)

        wrapper(*(1, 2), **{'val1': 'a'})

        expected_filename = os.path.join(
            df_cache.cache_config.cache_directory,
            caching.dataframe_cache._get_f_hash(df_func, (1, 2), {'val1': 'a'}) + "." + df_cache.extension
        )

        df_func.assert_called_once_with(1, 2, val1='a')
        load_mock.assert_not_called()

        save_mock.assert_called_once()
        pd.testing.assert_frame_equal(mock_data_1, save_mock.call_args[0][0])
        assert expected_filename == save_mock.call_args[0][1]

    def test_call_cache_resets_cache(self, monkeypatch: MonkeyPatch, remove: MagicMock) -> None:
        test_filename = 'df_func().csv'
        
        mock_walk: List[Tuple[str, List[str], List[str]]] = [
            (caching.cache_config.cache_directory, [], [test_filename])
        ]
        monkeypatch.setattr(os, 'walk', MagicMock(return_value=(x for x in mock_walk)))
        
        df_func = MagicMock()
        df_func.__name__ = 'df_func' # type: ignore

        df_cache = caching.dataframe_cache(cache_config_override=caching.CacheConfig(enabled=True), reset_cache=True)

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

        df_cache = caching.dataframe_cache(cache_config_override=caching.CacheConfig(enabled=True))
        monkeypatch.setattr(df_cache, 'load', load_mock)
        monkeypatch.setattr(caching.dataframe_cache, '_get_f_hash', _thrower)
    
        assert df_cache.cache_config.enabled == True

        wrapper = df_cache.__call__(df_func)
    
        result = wrapper(*(1, 2), **{'val1': 'a'})

        pd.testing.assert_frame_equal(result, mock_data_1)
        load_mock.assert_not_called()
        save_mock.assert_not_called()

    @pytest.mark.parametrize(
        "cache_type, method", [
            (caching.CacheType.CSV, 'read_csv'),
            (caching.CacheType.CSV_GZ, 'read_csv'),
            (caching.CacheType.EXCEL, 'read_excel'),
            (caching.CacheType.FEATHER, 'read_feather'),
            (caching.CacheType.JSON, 'read_json'),
            (caching.CacheType.PARQUET, 'read_parquet'),
            (caching.CacheType.PICKLE, 'read_pickle'),
        ]
    )
    def test_load(self, monkeypatch: MonkeyPatch, cache_type: caching.CacheType, method: str) -> None:
        read_mock = MagicMock()
        monkeypatch.setattr(pd, method, read_mock)

        df_cache = caching.dataframe_cache(
            cache_config_override=caching.CacheConfig(enabled=True, cache_type=cache_type)
        )

        test_filename = f'test.{df_cache.extension}'

        df_cache.load(test_filename)

        read_mock.assert_called_once_with(test_filename)

    def test_load_invalid_cache_type(self, monkeypatch: MonkeyPatch) -> None:
        read_csv_mock = MagicMock()
        monkeypatch.setattr(pd, 'read_csv', read_csv_mock)

        df_cache = caching.dataframe_cache(
            cache_config_override=caching.CacheConfig(enabled=True, cache_type="exe") # type: ignore
        )

        test_filename = 'test.csv'

        with pytest.raises(ValueError):
            df_cache.load(test_filename)
        
        read_csv_mock.assert_not_called()
    
    @pytest.mark.parametrize(
        "cache_type, method", [
            (caching.CacheType.CSV, 'to_csv'),
            (caching.CacheType.CSV_GZ, 'to_csv'),
            (caching.CacheType.EXCEL, 'to_excel'),
            (caching.CacheType.FEATHER, 'to_feather'),
            (caching.CacheType.JSON, 'to_json'),
            (caching.CacheType.PARQUET, 'to_parquet'),
            (caching.CacheType.PICKLE, 'to_pickle'),
        ]
    )
    def test_save(self, monkeypatch: MonkeyPatch, mock_data_1: pd.DataFrame, cache_type: caching.CacheType,
                  method: str) -> None:
        to_method = MagicMock()
        monkeypatch.setattr(mock_data_1, method, to_method)

        df_cache = caching.dataframe_cache(
            cache_config_override=caching.CacheConfig(enabled=True, cache_type=cache_type)
        )

        test_filename = f'test.{df_cache.extension}'

        df_cache.save(mock_data_1, test_filename)

        to_method.assert_called_once_with(test_filename)

    def test_save_invalid_cache_type(self, monkeypatch: MonkeyPatch, mock_data_1: pd.DataFrame) -> None:
        pickle_dump = MagicMock()
        monkeypatch.setattr(pickle, 'dump', pickle_dump)

        df_cache = caching.dataframe_cache(
            cache_config_override=caching.CacheConfig(enabled=True, cache_type="exe") # type: ignore
        )
        test_filename = 'test.pickle'

        open_mock = mock_open(read_data=b'')
        with patch('pybaseball.datahelpers.caching.open', open_mock):
            with pytest.raises(ValueError):
                df_cache.save(mock_data_1, test_filename)

        open_mock.assert_not_called()
        pickle_dump.assert_not_called()


def test_bust_cache(rmtree: MagicMock, mkdir: MagicMock) -> None:
    caching.bust_cache()

    assert rmtree.called_once_with(caching.cache_config.cache_directory)
    assert mkdir.called_once_with(caching.cache_config.cache_directory)
