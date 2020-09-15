from enum import Enum
from typing import Any, List, Optional, Type, TypeVar

_T = TypeVar('_T')

class EnumBase(Enum):
    @classmethod
    def values(enum_class: Type[_T]) -> Any:
        return [x.value for x in enum_class] # type: ignore
    
    @classmethod
    def parse(enum_class: Type[_T], value: str) -> _T:
        parsed = enum_class.safe_parse(value) # type: ignore

        if parsed is None:
            raise ValueError(f"Invalid value of '{value}'. Values must be a valid member of the enum: {enum_class.__name__}")

        return parsed

    @classmethod
    def safe_parse(enum_class: Type[_T], value: str) -> Optional[_T]:
        try:
            return enum_class[value] # type: ignore
        except KeyError:
            pass

        parsed = enum_class.safe_parse_by_value(value) # type: ignore

        if parsed is not None:
            return parsed

        return None
    
    @classmethod
    def safe_parse_by_value(enum_class: Type[_T], value: Any) -> Optional[_T]:
        values = enum_class.values() # type: ignore

        matched = [x for x in values if str(x).upper() == str(value).upper()]

        if matched:
            return enum_class(matched[0]) # type: ignore

        return None
