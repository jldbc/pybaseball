from pybaseball.cache import func_utils


def test_get_func_name_function() -> None:
    def test_func() -> None:
        pass

    assert func_utils.get_func_name(test_func) == "test_func"

def test_get_func_name_class_method() -> None:
    # pylint: disable=too-few-public-methods
    class TestClass:
        # pylint: disable=no-self-use
        def test_func(self) -> None:
            pass

    assert func_utils.get_func_name(TestClass().test_func) == "TestClass.test_func"
