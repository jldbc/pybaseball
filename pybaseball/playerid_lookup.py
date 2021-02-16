from difflib import get_close_matches
import io
import os

from typing import List, Tuple

import pandas as pd
import requests

from . import cache

url = "https://raw.githubusercontent.com/chadwickbureau/register/master/data/people.csv"

_client = None


def get_register_file():
    return os.path.join(cache.config.cache_directory, 'chadwick-register.csv')


@cache.df_cache()
def chadwick_register(save: bool = False) -> pd.DataFrame:
    ''' Get the Chadwick register Database '''

    if os.path.exists(get_register_file()):
        table = pd.read_csv(get_register_file())
        return table

    print('Gathering player lookup table. This may take a moment.')
    s = requests.get(url).content
    mlb_only_cols = ['key_retro', 'key_bbref', 'key_fangraphs', 'mlb_played_first', 'mlb_played_last']
    cols_to_keep = ['name_last', 'name_first', 'key_mlbam'] + mlb_only_cols
    table = pd.read_csv(io.StringIO(s.decode('utf-8')), usecols=cols_to_keep)

    table.dropna(how='all', subset=mlb_only_cols, inplace=True)  # Keep only the major league rows
    table.reset_index(inplace=True, drop=True)

    table[['key_mlbam', 'key_fangraphs']] = table[['key_mlbam', 'key_fangraphs']].fillna(-1)
    # originally returned as floats which is wrong
    table[['key_mlbam', 'key_fangraphs']] = table[['key_mlbam', 'key_fangraphs']].astype(int)

    # Reorder the columns to the right order
    table = table[cols_to_keep]

    if save:
        table.to_csv(get_register_file(), index=False)

    return table


def get_lookup_table(save=False):
    table = chadwick_register(save)
    # make these lowercase to avoid capitalization mistakes when searching
    table['name_last'] = table['name_last'].str.lower()
    table['name_first'] = table['name_first'].str.lower()
    return table


def get_closest_names(last: str, first: str, player_table: pd.DataFrame) -> pd.DataFrame:
    """Calculates similarity of first and last name provided with all players in player_table

    Args:
        last (str): Provided last name
        first (str): Provided first name
        player_table (pd.DataFrame): Chadwick player table including names

    Returns:
        pd.DataFrame: 5 nearest matches from difflib.get_close_matches
    """
    filled_df = player_table.fillna("").assign(chadwick_name=lambda row: row.name_first + " " + row.name_last)
    fuzzy_matches = pd.DataFrame(
        get_close_matches(f"{first} {last}", filled_df.chadwick_name, n=5, cutoff=0)
    ).rename({0: "chadwick_name"}, axis=1)
    return fuzzy_matches.merge(filled_df, on="chadwick_name").drop("chadwick_name", axis=1)


class _PlayerSearchClient:
    def __init__(self) -> None:
        self.table = get_lookup_table()

    def search(self, last: str, first: str = None, fuzzy: bool = False) -> pd.DataFrame:
        """Lookup playerIDs (MLB AM, bbref, retrosheet, FG) for a given player

        Args:
            last (str, required): Player's last name.
            first (str, optional): Player's first name. Defaults to None.
            fuzzy (bool, optional): In case of typos, returns players with names close to input. Defaults to False.

        Returns:
            pd.DataFrame: DataFrame of playerIDs, name, years played
        """

        # force input strings to lowercase
        last = last.lower()
        first = first.lower() if first else None

        if first is None:
            results = self.table.loc[self.table['name_last'] == last]
        else:
            results = self.table.loc[(self.table['name_last'] == last) & (self.table['name_first'] == first)]

        results = results.reset_index(drop=True)

        # If no matches, return 5 closest names
        if len(results) == 0 and fuzzy:
            print("No identically matched names found! Returning the 5 most similar names.")
            results=get_closest_names(last=last, first=first, player_table=self.table)
            
        return results


    def search_list(self, player_list: List[Tuple[str, str]]) -> pd.DataFrame:
        '''
        Lookup playerIDs (MLB AM, bbref, retrosheet, FG) for a list of players.

        Args:
            player_list: List of (last, first) tupels.

        Returns:
            pd.DataFrame: DataFrame of playerIDs, name, years played
        ''' 
        results = pd.DataFrame()

        for last, first in player_list:
            results = results.append(self.search(last, first), ignore_index=True)
        
        return results


    def reverse_lookup(self, player_ids: List[str], key_type: str = 'mlbam') -> pd.DataFrame:
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

        if key_type not in key_types:
            raise ValueError(f'[Key Type: {key_type}] Invalid; Key Type must be one of {key_types}')

        key = f'key_{key_type}'

        results = self.table[self.table[key].isin(player_ids)]
        results = results.reset_index(drop=True)

        return results


def _get_client() -> _PlayerSearchClient:
    global _client
    if _client is None:
        _client = _PlayerSearchClient()
    return _client

def playerid_lookup(last: str, first: str = None, fuzzy: bool = False) -> pd.DataFrame:
    """Lookup playerIDs (MLB AM, bbref, retrosheet, FG) for a given player

    Args:
        last (str, required): Player's last name.
        first (str, optional): Player's first name. Defaults to None.
        fuzzy (bool, optional): In case of typos, returns players with names close to input. Defaults to False.

    Returns:
        pd.DataFrame: DataFrame of playerIDs, name, years played
    """
    client = _get_client()
    return client.search(last, first, fuzzy)

def player_search_list(player_list: List[Tuple[str, str]]) -> pd.DataFrame:
    '''
    Lookup playerIDs (MLB AM, bbref, retrosheet, FG) for a list of players.

    Args:
        player_list: List of (last, first) tupels.

    Returns:
        pd.DataFrame: DataFrame of playerIDs, name, years played
    ''' 
    client = _get_client()
    return client.search_list(player_list)

def playerid_reverse_lookup(player_ids: List[str], key_type: str = 'mlbam') -> pd.DataFrame:
    """Retrieve a table of player information given a list of player ids

    :param player_ids: list of player ids
    :type player_ids: list
    :param key_type: name of the key type being looked up (one of "mlbam", "retro", "bbref", or "fangraphs")
    :type key_type: str

    :rtype: :class:`pandas.core.frame.DataFrame`
    """
    client = _get_client()
    return client.reverse_lookup(player_ids, key_type)
