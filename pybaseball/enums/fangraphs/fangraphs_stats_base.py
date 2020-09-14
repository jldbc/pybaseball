from enum import Enum
from typing import List

_COMMON_COLUMNS =  ['0', '1', '2']

class FanGraphsStatsBase(Enum):
    @classmethod
    def ALL(enum_class) -> List:
        common_columns = ['c'] + _COMMON_COLUMNS
        column_list = list(set(
            [column for column in enum_class if column.value not in common_columns]
        ))
        column_list.sort(key=lambda x: int(x.value) if x.value.isdigit() else -2)
        prepend = []
        # pylint: disable = no-member
        enum_members: List[str] = enum_class._member_names_ # type: ignore
        # pylint: disable = no-member
        if 'COMMON' in enum_members:
            prepend = [enum_class.COMMON] # type: ignore
        return prepend + column_list

    @classmethod
    def replace_common(enum_class, enum_values: List) -> List:
        stripped = [x for x in enum_values if x.value not in _COMMON_COLUMNS]

        # pylint: disable = no-member
        return [enum_class.COMMON] + stripped # type: ignore
        

    @classmethod
    def str_list(enum_class, enum_values: List, replace_common: bool = True) -> str:
        stripped = enum_class.replace_common(enum_values) if replace_common else enum_values

        return ','.join([x.value for x in stripped])

def type_list_to_str(values: List, replace_common: bool = True) -> str:
    if not values:
        return ''

    obj_type = type(values[0])

    return obj_type.str_list(values, replace_common)
