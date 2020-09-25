from typing import Any

import pytest
from pybaseball.cache import func_utils


class TestCacheFuncUtils:
    def test_get_value_hash_str(self) -> None:
        test_str = "TESTING"

        assert func_utils.get_value_hash(test_str) == f"'{test_str}'"

    def test_get_value_hash_str_no_designators(self) -> None:
        test_str = "TESTING"

        assert func_utils.get_value_hash(test_str, include_designators=False) == test_str

    def test_get_value_hash_str_with_bad_chars(self) -> None:
        test_str = "TESTING/"

        assert func_utils.get_value_hash(test_str) == str(test_str.__hash__())

    def test_get_value_hash_hashable(self) -> None:
        test_float = 3.14159

        assert func_utils.get_value_hash(test_float) == str(test_float.__hash__())

    def test_get_value_hash_none(self) -> None:
        test_value = None

        assert func_utils.get_value_hash(test_value) == 'None'

    def test_get_value_hash_list(self) -> None:
        test_value = ['a', 'b']

        assert func_utils.get_value_hash(test_value) == "['a', 'b']"

    def test_get_value_hash_list_no_designators(self) -> None:
        test_value = ['a', 'b']

        assert func_utils.get_value_hash(test_value, include_designators=False) == "'a', 'b'"

    def test_get_value_hash_tuple(self) -> None:
        test_value = ('a', 'b')

        assert func_utils.get_value_hash(test_value) == "('a', 'b')"

    def test_get_value_hash_tuple_no_designators(self) -> None:
        test_value = ('a', 'b')

        assert func_utils.get_value_hash(test_value, include_designators=False) == "'a', 'b'"

    def test_get_value_hash_dict(self) -> None:
        test_value = {'a': 'foo', 'b': 'bar'}

        assert func_utils.get_value_hash(test_value) == "{a='foo', b='bar'}"

    def test_get_value_hash_dict_no_designators(self) -> None:
        test_value = {'a': 'foo', 'b': 'bar'}

        assert func_utils.get_value_hash(test_value, include_designators=False) == "a='foo', b='bar'"

    def test_get_value_hash_non_hashable(self) -> None:
        class NonHashable:
            def __hash__(self) -> int:
                raise NotImplementedError

        with pytest.raises(ValueError):
            print(func_utils.get_value_hash(NonHashable()))

    def test_get_func_name_function(self) -> None:
        def test_func() -> None:
            pass

        assert func_utils.get_func_name(test_func) == "test_func"

    def test_get_func_name_class_method(self) -> None:
        class test_class:
            def test_func(self) -> None:
                pass

        assert func_utils.get_func_name(test_class().test_func) == "test_class.test_func"

    def test_get_func_hash_no_params(self) -> None:
        def test_func(*args: Any, **kwargs: Any) -> None:
            pass

        assert func_utils.get_func_hash(test_func, (), {}) == "test_func()"

    def test_get_func_hash_with_args(self) -> None:
        def test_func(*args: Any, **kwargs: Any) -> None:
            pass

        expected_hash = f"test_func('a', {(1).__hash__()})"

        assert func_utils.get_func_hash(test_func, ('a', 1), {}) == expected_hash

    def test_get_func_hash_with_kwargs(self) -> None:
        def test_func(*args: Any, **kwargs: Any) -> None:
            pass

        expected_hash = f"test_func(val1={(1.5).__hash__()}, val2='b')"

        assert func_utils.get_func_hash(test_func, (), {'val1': 1.5, 'val2': 'b'}) == expected_hash

    def test_get_func_hash_with_args_and_kwargs(self) -> None:
        def test_func(*args: Any, **kwargs: Any) -> None:
            pass

        expected_hash = f"test_func('a', {(1).__hash__()}, val1={(1.5).__hash__()}, val2='b')"

        assert func_utils.get_func_hash(test_func, ('a', 1), {'val1': 1.5, 'val2': 'b'}) == expected_hash

    def test_get_func_hash_long_path_windows(self) -> None:
        def test_func(*args: Any, **kwargs: Any) -> None:
            pass

        expected_hash = "test_func(93ece9cbe326c434412e28b87d466bd08bc0f2e7db0770cff852e7b9f46240d8)"

        long_kwargs = {f"val{str(x)}": x for x in range(func_utils.MAX_ARGS_KEY_LENGTH)}

        assert func_utils.get_func_hash(test_func, ('a', 1), long_kwargs) == expected_hash
