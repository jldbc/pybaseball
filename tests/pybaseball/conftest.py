import os
import urllib.parse
from typing import Callable, Dict, Generator, List, Union

import pandas as pd
import pytest
import requests
from _pytest.monkeypatch import MonkeyPatch
from typing_extensions import Protocol

_ParseDates = Union[bool, List[int], List[str], List[List], Dict]

# The Protocol class below is to be sure that we are passing the correct kind of Callable around in our tests.
# These are validated by MyPy at test time. Not at runtime (Python does not do runtime type checking).
# Protocols are a way to define that when we pass a function around
# (like we do in these tests to pass the functions in to load data),
# that the function sent over will take the correct typed parameters,
# and return the correct types.
# So in this instance we're defining that the type GetDataFrameCallable is a function that will
# take the params defined in __call__ and the return type defined in __call__.
# Further reading: https://docs.python.org/3/library/typing.html#typing.Protocol
class GetDataFrameCallable(Protocol):
    def __call__(self, filename: str, parse_dates: _ParseDates = False) -> pd.DataFrame: ...


@pytest.fixture()
def data_dir() -> str:
    """
        Returns the path to the tests data directory
    """
    this_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(this_dir, 'data')

@pytest.fixture()
def get_data_file_contents(data_dir: str) -> Callable:
    """
        Returns a function that will allow getting the contents of a file in the tests data directory easily
    """
    def get_contents(filename: str) -> str:
        """
            Get the str contents of a file in the tests data directory


            ARGUMENTS:
            filename    : str : the name of the file within the tests data directory to get the contents of
        """
        with open(os.path.join(data_dir, filename)) as _file:
            return _file.read()

    return get_contents

@pytest.fixture()
def get_data_file_dataframe(data_dir: str) -> GetDataFrameCallable:
    """
        Returns a function that will allow getting a dataframe from a csv file in the tests data directory easily
    """
    def get_dataframe(filename: str, parse_dates: _ParseDates = False) -> pd.DataFrame:
        """
            Get the DatFrame representation of the contents of a csv file in the tests data directory


            ARGUMENTS:
            filename    : str : the name of the file within the tests data directory to load into a DataFrame
        """
        return pd.read_csv(os.path.join(data_dir, filename), index_col=0, parse_dates=parse_dates).reset_index(drop=True)

    return get_dataframe

@pytest.fixture()
def response_get_monkeypatch(monkeypatch: MonkeyPatch) -> Callable:
    """
        Returns a function that will monkeypatch the requests.get function call to return expected data
    """
    def setup(result: Union[str, bytes], expected_url: str = None) -> None:
        """
           Get the DatFrame representation of the contents of a csv file in the tests data directory


            ARGUMENTS:
            result          : str            : the payload to return in the contents of the request.get call
            expected_url    : str (optional) : an expected_url to test the get call against
                                               to ensure the correct endpoint is hit
        """
        def _monkeypatch(url: str, params: Dict = None, timeout: int = None) -> object:
            final_url = url

            if params:
                query_params = urllib.parse.urlencode(params, safe=',')
                final_url = f"{final_url}?{query_params}"

            if expected_url is not None:
                # These prints are desired as these are long and get cut off in the test outpute.
                # These will only render on failed tests, so only when you would want to see them anyway.
                print("expected", expected_url)
                print("received", final_url)
                assert final_url.endswith(expected_url)

            class DummyResponse:
                def __init__(self, content: Union[str, bytes]):
                    self.content = content
                    self.status_code = 200

            return DummyResponse(result)

        monkeypatch.setattr(requests, 'get', _monkeypatch)

    return setup
