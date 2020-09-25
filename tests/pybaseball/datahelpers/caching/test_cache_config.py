from datetime import timedelta
from unittest.mock import MagicMock

from pybaseball.datahelpers import caching


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
