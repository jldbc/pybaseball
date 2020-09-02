import os
import pytest
import pandas as pd
import requests

@pytest.fixture()
def data_dir() -> str:
    this_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(this_dir, 'data')

@pytest.fixture()
def get_data_file_contents(data_dir: str):
    def get_contents(filename: str) -> str:
        with open(os.path.join(data_dir, filename)) as _file:
            return _file.read()
    
    return get_contents

@pytest.fixture()
def get_data_file_dataframe(data_dir: str):
    def get_dataframe(filename: str) -> pd.DataFrame:
        return pd.read_csv(os.path.join(data_dir, filename), index_col=0).reset_index(drop=True)

    return get_dataframe

@pytest.fixture()
def response_get_monkeypatch(monkeypatch):
    def setup(result: str, expected_url: str):
        def _monkeypatch(url: str):
            assert url.endswith(expected_url)

            class DummyResponse:
                def __init__(self, html):
                    self.content = html

            return DummyResponse(result)

        monkeypatch.setattr(requests, 'get', _monkeypatch)

    return setup
