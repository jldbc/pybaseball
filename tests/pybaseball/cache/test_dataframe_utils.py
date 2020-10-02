from unittest.mock import MagicMock

import pandas as pd
import pytest
from _pytest.monkeypatch import MonkeyPatch
from pybaseball import cache


@pytest.fixture(name="mock_data_1")
def _mock_data_1() -> pd.DataFrame:
    return pd.DataFrame([1, 2], columns=['a'])

@pytest.mark.parametrize(
    "cache_type, method", [
        ('csv', 'read_csv'),
        ('parquet', 'read_parquet'),
    ]
)
def test_load(monkeypatch: MonkeyPatch, cache_type: str, method: str) -> None:
    read_mock = MagicMock()
    monkeypatch.setattr(pd, method, read_mock)
    monkeypatch.setattr(cache.config, 'cache_type', cache_type)

    test_filename = f'test.{cache_type}'

    cache.dataframe_utils.load_df(test_filename)

    assert read_mock.called_once_with(test_filename)

def test_load_invalid_cache_type() -> None:
    test_filename = 'test.exe'

    with pytest.raises(ValueError):
        cache.dataframe_utils.load_df(test_filename)

@pytest.mark.parametrize(
    "cache_type, method", [
        ('csv', 'to_csv'),
        ('parquet', 'to_parquet'),
    ]
)
def test_save(monkeypatch: MonkeyPatch, mock_data_1: pd.DataFrame, cache_type: str, method: str) -> None:
    to_method = MagicMock()
    monkeypatch.setattr(mock_data_1, method, to_method)

    test_filename = f'test.{cache_type}'

    cache.dataframe_utils.save_df(mock_data_1, test_filename)

    assert to_method.called_once_with(test_filename)


def test_save_invalid_cache_type(mock_data_1: pd.DataFrame) -> None:
    test_filename = 'test.exe'

    with pytest.raises(ValueError):
        cache.dataframe_utils.save_df(mock_data_1, test_filename)
