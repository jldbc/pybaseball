from enum import Enum
from typing import Optional, Type, TypeVar

_T = TypeVar('_T')

class EnumBase(Enum):
    @classmethod
    def parse(enum_class: Type[_T], value: str, fail_silently: bool = False) -> _T:
        try:
            return enum_class[value] # type: ignore
        except KeyError:
            raise ValueError(f"Invalid stat column of {value} was used. Stat columns must be a valid member of the enum: {enum_class.__name__}")

    @classmethod
    def safe_parse(enum_class: Type[_T], value: str) -> Optional[_T]:
        try:
            return enum_class[value] # type: ignore
        except KeyError:
            return None
