from typing import Any

import pytest
from pybaseball.cache import func_utils


class TestCacheFuncUtils:
    def test_get_func_name_function(self) -> None:
        def test_func() -> None:
            pass

        assert func_utils.get_func_name(test_func) == "test_func"

    def test_get_func_name_class_method(self) -> None:
        class test_class:
            def test_func(self) -> None:
                pass

        assert func_utils.get_func_name(test_class().test_func) == "test_class.test_func"
