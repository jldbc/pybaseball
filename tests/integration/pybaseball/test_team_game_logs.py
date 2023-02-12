from time import sleep
from typing import Generator

import pytest

import pybaseball


@pytest.fixture(autouse=True)
def before_after_each() -> Generator[None, None, None]:
    # before each test
    yield
    # after each test
    sleep(6) # BBRef will throttle us if we make more than 10 calls per minute

def test_nyy_game_logs_regression1() -> None:
    """Regression test for NYY 2021 example"""
    df = pybaseball.team_game_logs(2021, "NYY", "pitching") 

    # NYY home against TOR 9/9/2021
    assert df.loc[139]["Home"]

    # subway series 9/11/2021, NYY playing Mets @ Citi (NYY is Away)
    assert not df.loc[141]["Home"]
