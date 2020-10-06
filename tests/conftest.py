import copy
import logging
import os
from typing import Any, Callable, Optional
from unittest.mock import MagicMock

import pandas as pd
import pytest

from pybaseball import cache


@pytest.fixture(name='logging_side_effect')
def _logging_side_effect() -> Callable:
    def _logger(name: str, after: Optional[Callable] = None) -> Callable:
        def _side_effect(*args: Any, **kwargs: Any) -> Optional[Any]:
            logging.debug(f'Mock {name} => {args} {kwargs}')
            if after is not None:
                return after(*args, **kwargs)

            return None

        return _side_effect

    return _logger


@pytest.fixture(name='cache_config')
def _cache_config() -> cache.CacheConfig:
    test_cache_directory = os.path.join(cache.CacheConfig.DEFAULT_CACHE_DIR, '.pytest')
    config = cache.CacheConfig(enabled=False)
    config.cache_directory = test_cache_directory
    return config


@pytest.fixture(autouse=True)
def _override_cache_config(cache_config: cache.CacheConfig) -> None:
    def _test_auto_load() -> cache.CacheConfig:
        logging.debug('_test_auto_load')
        return cache_config

    # Copy this for when we want to test the autoload_cache function
    if not hasattr(cache.cache_config, '_autoload_cache'):
        # pylint: disable=protected-access
        cache.cache_config._autoload_cache = copy.copy(cache.cache_config.autoload_cache)  # type: ignore
    cache.cache_config.autoload_cache = _test_auto_load

    # Copy this for when we want to test the save function
    if not hasattr(cache.cache_config.CacheConfig, '_save'):
        # pylint: disable=protected-access
        cache.cache_config.CacheConfig._save = copy.copy(cache.cache_config.CacheConfig.save)  # type: ignore

    cache.cache_config.CacheConfig.save = MagicMock()  # type: ignore
    cache.config = cache_config
    cache.cache_record.cfg = cache_config


@pytest.fixture(name="assert_frame_not_equal")
def _assert_frame_not_equal() -> Callable:
    def _assert(*args: Any, **kwargs: Any) -> bool:
        try:
            pd.testing.assert_frame_equal(*args, **kwargs)
        except AssertionError:
            # frames are not equal
            return True
        else:
            # frames are equal
            raise AssertionError

    return _assert


@pytest.fixture(name="thrower")
def _thrower() -> Callable:
    def _raise(*args: Any, **kwargs: Any) -> None:
        raise Exception

    return _raise
