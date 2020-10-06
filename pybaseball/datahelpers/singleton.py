from typing import Any, Optional, Type

class Singleton:
    # Use this and __new__ to make this a singleton. Only one ever exists.
    __INSTANCE__: Optional['Singleton'] = None
    def __new__(cls: Type['Singleton'], *args: Any, **kwargs: Any) -> 'Singleton':
        if cls.__INSTANCE__ == None:
            cls.__INSTANCE__ = super(Singleton, cls).__new__(cls)

        assert cls.__INSTANCE__ is not None
        return cls.__INSTANCE__ 
