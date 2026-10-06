import pandas as pd

from pybaseball.team_game_logs import _to_numeric_or_keep, postprocess


def test_postprocess_converts_numeric_columns_and_keeps_text() -> None:
    # Regression test: postprocess used DataFrame.apply(pd.to_numeric, errors="ignore"),
    # and pandas 3 rejects errors="ignore", so team_game_logs raised ValueError.
    columns = pd.MultiIndex.from_tuples([
        ('Unnamed: 0_level_0', 'Rk'),
        ('Unnamed: 1_level_0', 'Gtm'),
        ('Unnamed: 2_level_0', 'Date'),
        ('Unnamed: 3_level_0', 'Unnamed: 3_level_1'),
        ('Unnamed: 4_level_0', 'Opp'),
        ('Batting', 'R'),
    ])
    data = pd.DataFrame([
        ['1', '1', 'Mar 28', '@', 'NYY', '3'],
        ['2', '2', 'Mar 29', None, 'NYY', '5'],
        ['Rk', 'Gtm', 'Date', None, 'Opp', 'R'],
        ['3', '3', 'Mar 30', None, 'NYY', '0'],
        ['', '', '', None, '', '8'],
    ], columns=columns)

    result = postprocess(data)

    assert len(result) == 3
    assert result[('Unnamed: 1_level_0', 'Game')].tolist() == [1, 2, 3]
    assert result[('Unnamed: 3_level_0', 'Home')].tolist() == [False, True, True]
    assert pd.api.types.is_numeric_dtype(result[('Batting', 'R')])
    assert result[('Batting', 'R')].tolist() == [3, 5, 0]
    assert result[('Unnamed: 4_level_0', 'Opp')].tolist() == ['NYY', 'NYY', 'NYY']


def test_numeric_conversion_handles_duplicate_column_labels() -> None:
    # Selecting a duplicated label returns a DataFrame, so a per-column
    # pd.to_numeric loop would silently leave every column as text.
    columns = pd.MultiIndex.from_tuples([('Batting', 'R'), ('Batting', 'R'), ('Opp', 'Opp')])
    data = pd.DataFrame([['3', '4', 'NYY'], ['5', '6', 'BOS']], columns=columns)

    result = data.apply(_to_numeric_or_keep)

    assert result[('Batting', 'R')].values.tolist() == [[3, 4], [5, 6]]
    assert all(pd.api.types.is_numeric_dtype(dtype) for dtype in result[('Batting', 'R')].dtypes)
    assert result.iloc[:, 2].tolist() == ['NYY', 'BOS']
