import os
from typing import Generator, Callable, Union

import pandas as pd
import pytest
import requests

from _pytest.monkeypatch import MonkeyPatch

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
def get_data_file_dataframe(data_dir: str) -> Callable:
    """
        Returns a function that will allow getting a dataframe from a csv file in the tests data directory easily
    """
    def get_dataframe(filename: str, parse_dates=False) -> pd.DataFrame:
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
    def setup(result: Union[str, bytes], expected_url: str = None):
        """
           Get the DatFrame representation of the contents of a csv file in the tests data directory

                
            ARGUMENTS:
            result          : str            : the payload to return in the contents of the request.get call
            expected_url    : str (optional) : an expected_url to test the get call against
                                               to ensure the correct endpoint is hit
        """
        def _monkeypatch(url: str, timeout: int = None) -> object:
            if expected_url is not None:
                assert url.endswith(expected_url)

            class DummyResponse:
                def __init__(self, content: Union[str, bytes]):
                    self.content = content

            return DummyResponse(result)

        monkeypatch.setattr(requests, 'get', _monkeypatch)

    return setup
