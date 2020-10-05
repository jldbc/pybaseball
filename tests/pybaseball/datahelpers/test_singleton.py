from pybaseball.datahelpers import singleton

def test_singleton() -> None:
    class MySingleton(singleton.Singleton):
        def __init__(self, my_arg: int, my_kwarg: str = 'default'):
            self.my_arg = my_arg
            self.my_kwarg = my_kwarg

    mine = MySingleton(1)
    other = MySingleton(2)

    assert mine == other
    assert mine.my_arg == 2


def test_singleton_with_kwarg() -> None:
    class MySingleton(singleton.Singleton):
        def __init__(self, my_arg: int, my_kwarg: str = 'default'):
            self.my_arg = my_arg
            self.my_kwarg = my_kwarg

    mine = MySingleton(1)
    other = MySingleton(2, my_kwarg='NOT DEFAULT')

    assert mine == other
    assert mine.my_kwarg == 'NOT DEFAULT'


def test_singleton_member_set() -> None:
    class MySingleton(singleton.Singleton):
        def __init__(self, my_arg: int, my_kwarg: str = 'default'):
            self.my_arg = my_arg
            self.my_kwarg = my_kwarg

    mine = MySingleton(1)
    other = MySingleton(2)

    assert mine == other
    mine.my_kwarg = 'NOT DEFAULT'
    assert other.my_kwarg == 'NOT DEFAULT'
