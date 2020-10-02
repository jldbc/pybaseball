import copy
import logging
import os
from typing import Any, Callable, Optional
from unittest.mock import MagicMock

import pandas as pd
import pytest
from _pytest.monkeypatch import MonkeyPatch


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
