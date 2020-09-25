import os
import pathlib
import shutil
from unittest.mock import MagicMock

import pytest
from _pytest.monkeypatch import MonkeyPatch

from pybaseball import cache


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
        cache,
        'cache_config',
        cache.CacheConfig(cache_directory=os.path.join(cache.CacheConfig().cache_directory, '.pytest'))
    )
    cache.flush_cache()
