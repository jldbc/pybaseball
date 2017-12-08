import pandas as pd
import requests
import io

# dropped key_uuid. looks like a has we wouldn't need for anything. 
# TODO: allow for typos. String similarity? 
# TODO: allow user to submit list of multiple names


def get_lookup_table():
    print('Gathering player lookup table. This may take a moment.')
    url = "https://raw.githubusercontent.com/chadwickbureau/register/master/data/people.csv"
    s=requests.get(url).content
    table = pd.read_csv(io.StringIO(s.decode('utf-8')), dtype={'key_sr_nfl': object, 'key_sr_nba': object, 'key_sr_nhl': object})
    #subset columns
    cols_to_keep = ['name_last','name_first','key_mlbam', 'key_retro', 'key_bbref', 'key_fangraphs', 'mlb_played_first','mlb_played_last']
    table = table[cols_to_keep]
    #make these lowercase to avoid capitalization mistakes when searching
    table['name_last'] = table['name_last'].str.lower()
    table['name_first'] = table['name_first'].str.lower()
    # Pandas cannot handle NaNs in integer columns. We need IDs to be ints for successful queries in statcast, etc. 
    # Workaround: replace ID NaNs with -1, then convert columns to integers. User will have to understand that -1 is not a valid ID. 
    table[['key_mlbam', 'key_fangraphs']] = table[['key_mlbam', 'key_fangraphs']].fillna(-1)
    table[['key_mlbam', 'key_fangraphs']] = table[['key_mlbam', 'key_fangraphs']].astype(int) # originally returned as floats which is wrong
    return table


def playerid_lookup(last, first=None):
    # force input strings to lowercase
    last = last.lower()
    if first:
        first = first.lower()
    table = get_lookup_table()
    if first is None:
        results = table.loc[table['name_last']==last]
    else:
        results = table.loc[(table['name_last']==last) & (table['name_first']==first)]
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
    key_types = ('mlbam', 'retro', 'bbref', 'fangraphs', )

    if not key_type:
        key_type = key_types[0]     # default is "mlbam" if key_type not provided
    elif key_type not in key_types:
        raise ValueError(
            '[Key Type: {}] Invalid; Key Type must be one of "{}"'.format(key_type, '", "'.join(key_types))
        )

    table = get_lookup_table()
    key = 'key_{}'.format(key_type)

    results = table[table[key].isin(player_ids)]
    results = results.reset_index().drop('index', 1)
    return results
