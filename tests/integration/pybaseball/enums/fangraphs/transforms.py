def transform_leaderboard_item(leaderboard_item: str) -> str:
    """
        Helper function to take a Fangraphs column name, and translate it to its related enum value.

        E.g.:
            '1B'         => 'SINGLES'
            'ERA'        => 'ERA'
            'OPS+'       => 'OPS_PLUS'
            'Made 1-10%' => 'MADE_ONE_TO_TEN_PCT'

        This will be used in integration tests to compare our current enum values to what Fangraphs supports,
        so that we can see if any columns have been added or removed before a user submits that as a bug report.
    """
    start_replacements = {
        '-': 'NEGATIVE ',
        '+': 'POSITIVE ',
        '1B': 'SINGLES ',
        '2B': 'DOUBLES ',
        '3B': 'TRIPLES ',
    }
    end_replacements = {
        '-': ' MINUS',
    }
    mid_replacements = {
        '+': ' PLUS ',
        '(': ' ',
        ')': ' ',
        '/': ' ',
        ' 0-': ' ZERO TO ',
        ' 0%': ' ZERO PCT ',
        ' 1-': ' ONE TO ',
        ' 10-': ' TEN TO ',
        ' 40-': ' FORTY TO ',
        ' 60-': ' SIXTY TO ',
        '90-': ' NINETY TO ',
        '100': ' ONE HUNDRED ',
        '10': ' TEN ',
        '40': ' FORTY ',
        '60': ' SIXTY ',
        '90': ' NINETY ',
        '-': ' ',
        '%': ' PCT ',
    }

    leaderboard_item = leaderboard_item.upper()

    for _from, _to in start_replacements.items():
        if leaderboard_item.startswith(_from):
            leaderboard_item = _to + leaderboard_item[len(_from):]

    for _from, _to in end_replacements.items():
        if leaderboard_item.endswith(_from):
            leaderboard_item = leaderboard_item[:-1*len(_from)] + _to

    for _from, _to in mid_replacements.items():
        leaderboard_item = leaderboard_item.replace(_from, _to)

    while '  ' in leaderboard_item:
        leaderboard_item = leaderboard_item.replace('  ', ' ')

    return leaderboard_item.strip().replace(' ', '_')
