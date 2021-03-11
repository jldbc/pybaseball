import pandas as pd
import pytest
from pybaseball.datahelpers import transform
from unittest.mock import patch


@pytest.fixture(name='fielding')
def _fielding() -> pd.DataFrame:
    return pd.DataFrame([
        ['1', 2015, 'P',  157],
        ['1', 2015, 'CF', 5],
        ['1', 2016, 'CF', 162],
        ['2', 2015, 'C',  1],
    ],
    columns=['playerID', 'yearID', 'POS', 'G'])

@pytest.fixture(name='people')
def _people() -> pd.DataFrame:
    return pd.DataFrame([
        ['1', 1990],
        ['2', 1985],
    ],
    columns=['playerID', 'birthYear'])


@pytest.fixture(name='stats')
def _stats() -> pd.DataFrame:
    return pd.DataFrame([
        ['1', 2015],
        ['1', 2016],
        ['2', 2015],
    ],
    columns=['playerID', 'yearID'])

def test_get_age(stats: pd.DataFrame, people: pd.DataFrame) -> None:
    expected = pd.DataFrame([
            ['1', 2015, 25],
            ['1', 2016, 26],
            ['2', 2015, 30],
        ],
        columns=['playerID', 'yearID', 'age']
    )
    
    result = transform.get_age(stats, people)

    pd.testing.assert_frame_equal(expected, result, check_dtype=False)

def test_get_age_default_people(stats: pd.DataFrame, people: pd.DataFrame) -> None:
    expected = pd.DataFrame([
            ['1', 2015, 25],
            ['1', 2016, 26],
            ['2', 2015, 30],
        ],
        columns=['playerID', 'yearID', 'age']
    )
    
    with patch('pybaseball.datahelpers.transform.people', return_value=people) as people_mock:
        result = transform.get_age(stats)

        pd.testing.assert_frame_equal(expected, result, check_dtype=False)

        people_mock.assert_called_once()

def test_get_primary_position(fielding: pd.DataFrame) -> None:
    expected = pd.DataFrame([
            ['1', 2015, 'P'],
            ['1', 2016, 'CF'],
            ['2', 2015, 'C'],
        ],
        columns=['playerID', 'yearID', 'primaryPos'],
        index=pd.RangeIndex(1, 4),
    )
    
    result = transform.get_primary_position(fielding)

    print(expected)
    print(result)

    pd.testing.assert_frame_equal(expected, result)
