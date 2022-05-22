from typing import Callable


def get_func_name(func: Callable) -> str:
    '''
    Get a function name. This is a function because __name__ can fail on a class method.
    '''

    if '__self__' in dir(func):
        # This is a class method
        return f"{func.__getattribute__('__self__').__class__.__name__}.{func.__name__}"
    # it's a method of an instantiated object
    elif "__qualname__" in dir(func) and r'<locals>' not in func.__qualname__:
        return func.__qualname__

    return func.__name__
