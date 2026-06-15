from typing import Callable

from bs4 import BeautifulSoup

from pybaseball.team_results import get_table


def test_get_table_unknown_attendance_becomes_nan(get_data_file_contents: Callable[[str], str]) -> None:
    # Regression test for #459: 'Unknown' attendance values must be converted to
    # NaN so the column can be made numeric. The previous chained-assignment
    # `inplace=True` form silently failed under pandas copy-on-write (and emitted
    # a FutureWarning), leaving the value as the string 'Unknown'.
    soup = BeautifulSoup(get_data_file_contents('team_results.html'), 'lxml')

    result = get_table(soup, 'NYY')

    assert 'Attendance' in result.columns
    assert result['Attendance'].isna().any()
    assert 'Unknown' not in result['Attendance'].tolist()
