import pathlib
from datetime import timedelta
import os
from typing import Optional, cast
# from typing_extensions import Literal
import json
import pandas as pd

from .file_utils import _mkdir, safe_jsonify, load_json
# CacheType = Literal['csv', 'parquet']

class CacheConfig:
    DEFAULT_CACHE_DIR = os.path.join(pathlib.Path.home(), '.pybaseball', 'cache')
    DEFAULT_EXPIRATION = 7 # number of days to cache by default
    DEFAULT_CACHE_TYPE = 'parquet'
    CFG_FILENAME = 'cache_config.json'

    # pylint: disable=too-many-arguments
    def __init__(self, enabled: bool = False, cache_directory: str = None, default_expiration: int = None,
                 cache_type: Optional[str] = None):
        self.enabled = enabled
        self.cache_directory = cache_directory or CacheConfig.DEFAULT_CACHE_DIR
        self.default_expiration = default_expiration or CacheConfig.DEFAULT_EXPIRATION
        if cache_type is not None:
            self.cache_type = cache_type.lower()
            if self.cache_type not in ('csv', 'parquet'):
                raise ValueError(f"Invalid CacheType: {cache_type}")
        else:
            self.cache_type = self.DEFAULT_CACHE_TYPE

        _mkdir(self.cache_directory)

    def enable(self, enabled: bool = True) -> None:
        self.enabled = enabled
        if self.enabled:
            _mkdir(self.cache_directory)
            self.save()
        elif os.path.exists(self.cache_directory):
            self.save()

    def save(self) -> None:
        data = {
            'enabled': self.enabled,
            'default_expiration': self.default_expiration,
            'cache_type': self.cache_type
        }
        safe_jsonify(self.cache_directory, self.CFG_FILENAME, data)


def autoload_cache() -> CacheConfig:
    ''' Load from the policy file if it exists, otherwise create an object '''
    cfg_handle = os.path.join(CacheConfig.DEFAULT_CACHE_DIR, CacheConfig.CFG_FILENAME)
    if os.path.isfile(cfg_handle):
        data = load_json(cfg_handle)
        return CacheConfig(**data)
    return CacheConfig()
