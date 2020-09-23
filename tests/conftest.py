from typing import Any, Callable

import pandas as pd
import pytest

from pybaseball.datahelpers import caching

@pytest.fixture(autouse=True)
def _disable_cache() -> None:
    # Always disable caching in tests
    caching.cache_config.enable(False)

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
