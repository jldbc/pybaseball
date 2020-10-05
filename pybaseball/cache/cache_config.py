import os
import pathlib
from typing import Optional

from . import file_utils
from ..datahelpers import singleton


class CacheConfig(singleton.Singleton):
    DEFAULT_CACHE_DIR = os.path.join(pathlib.Path.home(), '.pybaseball', 'cache')
    DEFAULT_EXPIRATION = 7  # number of days to cache by default
    DEFAULT_CACHE_TYPE = 'parquet'
    CFG_FILENAME = 'cache_config.json'
    PYBASEBALL_CACHE_ENV = 'PYBASEBALL_CACHE'

    def __init__(self, enabled: bool = False, default_expiration: int = None, cache_type: Optional[str] = None):
        self.enabled = enabled
        self.cache_directory = os.environ.get(CacheConfig.PYBASEBALL_CACHE_ENV) or CacheConfig.DEFAULT_CACHE_DIR
        self.default_expiration = default_expiration or CacheConfig.DEFAULT_EXPIRATION
        if cache_type is not None:
            self.cache_type = cache_type.lower()
            if self.cache_type not in ('csv', 'parquet'):
                raise ValueError(f"Invalid cache_type: {cache_type}")
        else:
            self.cache_type = CacheConfig.DEFAULT_CACHE_TYPE

        file_utils.mkdir(self.cache_directory)

    def enable(self, enabled: bool = True) -> None:
        self.enabled = enabled
        if self.enabled:
            file_utils.mkdir(self.cache_directory)
            self.save()
        elif os.path.exists(self.cache_directory):
            self.save()

    def save(self) -> None:
        data = {
            'enabled': self.enabled,
            'default_expiration': self.default_expiration,
            'cache_type': self.cache_type.lower(), # in case of "Parquet" or "CSV", ensures a uniform filename.
        }
        file_utils.safe_jsonify(self.cache_directory, CacheConfig.CFG_FILENAME, data)


def autoload_cache() -> CacheConfig:
    ''' Load from the policy file if it exists, otherwise create an object '''
    cfg_handle = os.path.join(CacheConfig.DEFAULT_CACHE_DIR, CacheConfig.CFG_FILENAME)
    if os.path.isfile(cfg_handle):
        data = file_utils.load_json(cfg_handle)
        assert isinstance(data, dict)
        return CacheConfig(**data)
    return CacheConfig()
