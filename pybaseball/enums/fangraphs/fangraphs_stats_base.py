from typing import List

from ..enum_base import EnumBase

_COMMON_COLUMNS =  ['0', '1', '2']

class FangraphsStatsBase(EnumBase):
    @classmethod
    def ALL(cls) -> List:  # pylint: disable=invalid-name
        common_columns = ['c'] + _COMMON_COLUMNS
        column_list = list(set(
            [column for column in cls if column.value not in common_columns]
        ))
        # Order the columns numerically, except for 'c' which always goes first
        column_list.sort(key=lambda x: int(x.value) if x.value.isdigit() else -2)
        prepend = []
        # pylint: disable = no-member
        if cls.safe_parse('COMMON') is not None and cls.COMMON not in column_list: # type: ignore
            prepend = [cls.COMMON] # type: ignore
        return prepend + column_list

    @classmethod
    def replace_common(cls, enum_values: List) -> List:
        stripped = [x for x in enum_values if x.value not in _COMMON_COLUMNS]

        # pylint: disable = no-member
        return [cls.COMMON] + stripped # type: ignore


    @classmethod
    def str_list(cls, enum_values: List, replace_common: bool = True) -> str:
        stripped = cls.replace_common(enum_values) if replace_common else enum_values

        return ','.join([x.value for x in stripped])

def stat_list_to_str(values: List, replace_common: bool = True) -> str:
    if not values:
        return ''

    assert isinstance(values[0], FangraphsStatsBase)

    obj_type = type(values[0])

    return obj_type.str_list(values, replace_common)
