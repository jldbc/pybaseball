from typing import Callable

import pytest

from pybaseball import active_roster

@pytest.fixture(name="sample_html")
def _sample_html(get_data_file_contents: Callable[[str], str]) -> str:
    return get_data_file_contents('active_roster.html')

def test_active_roster(response_get_monkeypatch: Callable, sample_html: str):
    response_get_monkeypatch(sample_html)

    with pytest.raises(ValueError) as ex_info:
        active_roster('FAKE')
    assert str(ex_info.value == 'Team must be the three-letter abbreviation of an active MLB team.')

    active_roster_result = active_roster('WSN')

    # make sure IL is populated
    assert active_roster_result[active_roster_result["Name"] == "Cade Cavalli"]["IL"].values[0] == "15-day"

    # make sure a player who hasn't played in the majors has Alt URL set correctly
    assert active_roster_result[active_roster_result["Name"] == "Andry Lara"]["Alt URL"].values[0]