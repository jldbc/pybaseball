import pandas as pd
import requests
import io
import os

# dropped key_uuid. looks like a has we wouldn't need for anything.
# TODO: allow for typos. String similarity?

url = "https://raw.githubusercontent.com/chadwickbureau/register/master/data/people.csv"
register_file = 'chadwick-register.csv'

def chadwick_register(save: bool = False) -> pd.DataFrame:
    ''' Get the Chadwick register Database '''

    if os.path.exists(register_file):
        table = pd.read_csv(register_file)
        return table

    print('Gathering player lookup table. This may take a moment.')
    s = requests.get(url).content
    mlb_only_cols = ['key_retro', 'key_bbref', 'key_fangraphs', 'mlb_played_first', 'mlb_played_last']
    cols_to_keep = ['name_last', 'name_first', 'key_mlbam'] + mlb_only_cols
    table = pd.read_csv(io.StringIO(s.decode('utf-8')), usecols=cols_to_keep)

    table.dropna(how='all', subset=mlb_only_cols, inplace=True) # Keep only the major league rows
    table.reset_index(inplace=True, drop=True)

    table[['key_mlbam', 'key_fangraphs']] = table[['key_mlbam', 'key_fangraphs']].fillna(-1)
    # originally returned as floats which is wrong
    table[['key_mlbam', 'key_fangraphs']] = table[['key_mlbam', 'key_fangraphs']].astype(int)

    # Reorder the columns to the right order
    table = table[cols_to_keep]

    if save:
        table.to_csv(register_file, index=False)
    
    return table


def get_lookup_table(save=False):
    table = chadwick_register(save)
    #make these lowercase to avoid capitalization mistakes when searching
    table['name_last'] = table['name_last'].str.lower()
    table['name_first'] = table['name_first'].str.lower()
    return table


def playerid_lookup(last=None, first=None, player_list=None):
    # force input strings to lowercase
    if last:
        last = last.lower()
    if first:
        first = first.lower()
    table = get_lookup_table()

    # if player_list has a value, then the user is passing in a list of players
    # the list of players may be comma delimited for last, first, or just last
    if player_list:
        player_counter = 1
        for player in player_list:
            last = player.split(",")[0].strip()
            first = None
            if (len(player.split(",")) > 1):
                first = player.split(",")[1].strip()
            if (player_counter == 1):
                results = playerid_lookup(last, first)
            else:
                results = results.append(playerid_lookup(last, first), ignore_index=True)
            player_counter += 1
        return results

    if first is None:
        results = table.loc[table['name_last'] == last]
    else:
        results = table.loc[(table['name_last'] == last) & (table['name_first'] == first)]
    #results[['key_mlbam', 'key_fangraphs', 'mlb_played_first', 'mlb_played_last']] = results[['key_mlbam', 'key_fangraphs', 'mlb_played_first', 'mlb_played_last']].astype(int) # originally returned as floats which is wrong
    results = results.reset_index().drop('index', 1)
    return results


# data = playerid_lookup('bonilla')
# data = playerid_lookup('bonilla', 'bobby')


def playerid_reverse_lookup(player_ids, key_type=None):
    """Retrieve a table of player information given a list of player ids

    :param player_ids: list of player ids
    :type player_ids: list
    :param key_type: name of the key type being looked up (one of "mlbam", "retro", "bbref", or "fangraphs")
    :type key_type: str

    :rtype: :class:`pandas.core.frame.DataFrame`
    """
    key_types = (
        'mlbam',
        'retro',
        'bbref',
        'fangraphs',
    )

    if not key_type:
        key_type = key_types[0]  # default is "mlbam" if key_type not provided
    elif key_type not in key_types:
        raise ValueError('[Key Type: {}] Invalid; Key Type must be one of "{}"'.format(
            key_type, '", "'.join(key_types)))

    table = get_lookup_table()
    key = 'key_{}'.format(key_type)

    results = table[table[key].isin(player_ids)]
    results = results.reset_index().drop('index', 1)
    return results
