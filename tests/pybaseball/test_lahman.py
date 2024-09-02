import tempfile
from typing import Callable

import pytest

from pybaseball.lahman import *
from pybaseball.lahman import _get_base_string, _get_download_url, _get_session


@pytest.fixture(name="sample_html")
def _sample_html(get_data_file_contents: Callable[[str], str]) -> str:
    return get_data_file_contents('lahman.html')

@pytest.fixture(name="sample_bytes")
def _sample_bytes(get_data_file_bytes: Callable[[str], bytes]) -> bytes:
    return get_data_file_bytes('lahman_1871-2023_csv.7z')

@pytest.fixture(name="target")
def _target() -> str:
    return _get_session()

@pytest.fixture(autouse=True)
def run_around_tests():
    # setup
    tempdir = tempfile.TemporaryDirectory()
    cache.config.cache_directory = tempdir.name
    yield
    # teardown

def test_get_lahman_info(target_get_monkeypatch: Callable, sample_html: str):
    target_get_monkeypatch(sample_html)

    url = _get_download_url()
    base_string = _get_base_string()

    assert(url == "https://www.dropbox.com/scl/fi/hy0sxw6gaai7ghemrshi8/lahman_1871-2023_csv.7z?rlkey=edw1u63zzxg48gvpcmr3qpnhz&dl=1")
    assert(base_string == "lahman_1871-2023_csv")

def test_download_lahman(target_get_monkeypatch: Callable, sample_html: str,
                         response_get_monkeypatch: Callable, sample_bytes: bytes):
    target_get_monkeypatch(sample_html)
    response_get_monkeypatch(sample_bytes)

    # test download
    b1 = download_lahman()
    b2 = download_lahman()
    b3 = download_lahman(force=True)

    assert b1
    assert not b2
    assert b3

def test_lahman_tables(target_get_monkeypatch: Callable, sample_html: str,
                       response_get_monkeypatch: Callable, sample_bytes: bytes):
    target_get_monkeypatch(sample_html)
    response_get_monkeypatch(sample_bytes)

    download_lahman()

    # test tables
    assert not all_star_full().empty
    assert not appearances().empty
    assert not awards_managers().empty
    assert not awards_players().empty
    assert not awards_share_managers().empty
    assert not awards_share_players().empty
    assert not batting().empty
    assert not batting_post().empty
    assert not college_playing().empty
    assert not fielding().empty
    assert not fielding_of().empty
    assert not fielding_of_split().empty
    assert not fielding_post().empty
    assert not hall_of_fame().empty
    assert not home_games().empty
    assert not managers().empty
    assert not managers_half().empty
    assert not master().empty
    assert not parks().empty
    assert not people().empty
    assert not pitching().empty
    assert not pitching_post().empty
    assert not salaries().empty
    assert not schools().empty
    assert not series_post().empty
    assert not teams_core().empty
    assert not teams_franchises().empty
    assert not teams_half().empty

def test_lahman_schools(target_get_monkeypatch: Callable, sample_html: str,
                        response_get_monkeypatch: Callable, sample_bytes: bytes):
    target_get_monkeypatch(sample_html)
    response_get_monkeypatch(sample_bytes)

    download_lahman()

    table = schools()
    row = table.loc[table['schoolID'] == "ksstmaC"].iloc[0]
    name = row['name_full']
    assert name == "St. Mary's College"
