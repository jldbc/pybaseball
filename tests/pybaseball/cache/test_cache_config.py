import os
from typing import cast
from unittest.mock import MagicMock, patch

import pytest
from pybaseball import cache
from pybaseball.cache import file_utils
from pybaseball.cache.cache_record import cfg


def test_not_enabled_default() -> None:
    config = cache.CacheConfig()
    assert not config.enabled


def test_enabled_set() -> None:
    config = cache.CacheConfig(enabled=True)
    assert config.enabled

def test_enable() -> None:
    config = cache.CacheConfig()
    assert not config.enabled

    config.enable()
    assert config.enabled

    config.enable(False)
    assert not config.enabled


def test_cache_directory_default(mkdir: MagicMock) -> None:
    config = cache.CacheConfig()
    assert config.cache_directory == cache.CacheConfig.DEFAULT_CACHE_DIR
    assert mkdir.called_once_with(cache.CacheConfig.DEFAULT_CACHE_DIR)


def test_cache_directory_set(mkdir: MagicMock) -> None:
    my_dir: str = '~/my_dir'
    cache.config.cache_directory = my_dir

    assert cache.config.cache_directory == my_dir
    assert mkdir.called_once_with(my_dir)


def test_expiration_default() -> None:
    config = cache.CacheConfig()
    assert config.default_expiration == cache.CacheConfig.DEFAULT_EXPIRATION


def test_expiration_set() -> None:
    my_expiration: int = 365

    config = cache.CacheConfig(default_expiration=my_expiration)
    assert config.default_expiration == my_expiration


def test_cache_type_default() -> None:
    config = cache.CacheConfig()
    assert config.cache_type == cache.CacheConfig.DEFAULT_CACHE_TYPE


def test_cache_type_invalid() -> None:
    with pytest.raises(ValueError):
        cache.CacheConfig(enabled=False, cache_type='exe')


def test_cache_type_set() -> None:
    config = cache.CacheConfig(cache_type='parquet')
    assert config.cache_type == 'parquet'


def test_cache_config_singleton() -> None:
    new_config = cache.CacheConfig(enabled=False, default_expiration=365, cache_type='csv')
    assert new_config == cache.config
    assert new_config == cfg

    assert not cfg.enabled
    assert cfg.default_expiration == 365
    assert cfg.cache_type == 'csv'

    cache.config.cache_directory = '~/temp'
    assert cfg.cache_directory == '~/temp'


@patch('pybaseball.cache.file_utils.safe_jsonify', MagicMock())
def test_cache_config_save() -> None:
    new_config = cache.CacheConfig(enabled=False, default_expiration=364, cache_type='csv')

    # pylint: disable=protected-access
    new_config._save() # type: ignore

    cast(MagicMock, file_utils.safe_jsonify).assert_called_once()  # pylint: disable=no-member

@patch('os.path.isfile', MagicMock(return_value=True))
@patch('pybaseball.cache.file_utils.load_json', MagicMock(
    return_value={'enabled': False, 'default_expiration': 363, 'cache_type': 'csv'}
))
def test_autoload_cache() -> None:
    autoload_filename = os.path.join(cache.CacheConfig.DEFAULT_CACHE_DIR, cache.CacheConfig.CFG_FILENAME)

    # pylint: disable=protected-access
    cache.cache_config._autoload_cache() # type: ignore

    cast(MagicMock, os.path.isfile).assert_called_once_with(autoload_filename)  # pylint: disable=no-member
    cast(MagicMock, cache.file_utils.load_json).assert_called_once_with(autoload_filename)  # pylint: disable=no-member

    assert not cache.config.enabled
    assert cache.config.default_expiration == 363
    assert cache.config.cache_type == 'csv'
