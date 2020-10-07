import copy

import pytest
from pybaseball.cache import cache_record


def test_bad_cache_record() -> None:
    with pytest.raises(ValueError):
        cache_record.CacheRecord()

def test_supports_self_true() -> None:
    func_data = {'func': '_test_func', 'args': (1, 2, 3), 'kwargs': {'named_param': True}}

    record = cache_record.CacheRecord(data=func_data)

    assert record.supports(func_data)

@pytest.mark.parametrize(
    "missing_attribute", ['func', 'args', 'kwargs']
)
def test_supports_missing_attribute_false(missing_attribute: str) -> None:
    func_data = {'func': '_test_func', 'args': (1, 2, 3), 'kwargs': {'named_param': True}}

    record = cache_record.CacheRecord(data=func_data)

    bad_func_data = copy.deepcopy(func_data)
    del bad_func_data[missing_attribute]

    assert not record.supports(bad_func_data)


def test_supports_extra_attribute_ignored() -> None:
    func_data = {'func': '_test_func', 'args': (1, 2, 3), 'kwargs': {'named_param': True}}

    record = cache_record.CacheRecord(data=func_data)

    bad_func_data = copy.deepcopy(func_data)
    bad_func_data['extra'] = {'extra_data': True}

    assert record.supports(bad_func_data)
