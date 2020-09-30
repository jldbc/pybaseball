from datetime import timedelta
from unittest.mock import MagicMock

from pybaseball import cache


def test_not_enabled_default() -> None:
    config = cache.CacheConfig()
    assert config.enabled == False


def test_enabled_set() -> None:
    config = cache.CacheConfig(enabled=True)
    assert config.enabled == True


def test_enable() -> None:
    config = cache.CacheConfig()
    assert config.enabled == False

    config.enable()
    assert config.enabled == True

    config.enable(False)
    assert config.enabled == False


def test_cache_directory_default(mkdir: MagicMock) -> None:
    config = cache.CacheConfig()
    assert config.cache_directory == cache.CacheConfig.DEFAULT_CACHE_DIR
    assert mkdir.called_once_with(cache.CacheConfig.DEFAULT_CACHE_DIR)


def test_cache_directory_set(mkdir: MagicMock) -> None:
    my_dir: str = '~/my_dir'
    config = cache.CacheConfig(cache_directory=my_dir)

    assert config.cache_directory == my_dir
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


def test_cache_type_set() -> None:
    config = cache.CacheConfig(cache_type='parquet')
    assert config.cache_type == 'parquet'
