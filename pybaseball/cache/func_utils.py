import copy
import hashlib
import re
from typing import Callable, Dict, Hashable, Iterable, Optional, Tuple, Union

MAX_ARGS_KEY_LENGTH = 128

def get_func_name(func: Callable) -> str:
    '''
    Get a function name. This is a function because __name__ can fail on a class method.
    '''
    if '__self__' in dir(func):
        # This is a class method
        return f"{func.__getattribute__('__self__').__class__.__name__}.{func.__name__}"
    return f"{func.__name__}"
