import pandas as pd
import requests
import datetime
import io
import zipfile


# dictionary containing team abbreviations and their first year in existance
first_season_map = {'ALT': 1884, 'ANA': 1997, 'ARI': 1998, 'ATH': 1871,
                    'ATL': 1966, 'BAL': 1872, 'BLA': 1901, 'BLN': 1892,
                    'BLU': 1884, 'BOS': 1871, 'BRA': 1872, 'BRG': 1890,
                    'BRO': 1884, 'BSN': 1876, 'BTT': 1914, 'BUF': 1879,
                    'BWW': 1890, 'CAL': 1965, 'CEN': 1875, 'CHC': 1876,
                    'CHI': 1871, 'CHW': 1901, 'CIN': 1876, 'CKK': 1891,
                    'CLE': 1871, 'CLV': 1879, 'COL': 1883, 'COR': 1884,
                    'CPI': 1884, 'DET': 1901, 'DTN': 1881, 'ECK': 1872,
                    'FLA': 1993, 'HAR': 1874, 'HOU': 1962, 'IND': 1878,
                    'KCA': 1955, 'KCC': 1884, 'KCN': 1886, 'KCP': 1914,
                    'KCR': 1969, 'KEK': 1871, 'LAA': 1961, 'LAD': 1958,
                    'LOU': 1876, 'MAN': 1872, 'MAR': 1873, 'MIA': 2012,
                    'MIL': 1884, 'MIN': 1961, 'MLA': 1901, 'MLG': 1878,
                    'MLN': 1953, 'MON': 1969, 'NAT': 1872, 'NEW': 1915,
                    'NHV': 1875, 'NYG': 1883, 'NYI': 1890, 'NYM': 1962,
                    'NYP': 1883, 'NYU': 1871, 'NYY': 1903, 'OAK': 1968,
                    'OLY': 1871, 'PBB': 1890, 'PBS': 1914, 'PHA': 1882,
                    'PHI': 1873, 'PHK': 1884, 'PHQ': 1890, 'PIT': 1882,
                    'PRO': 1878, 'RES': 1873, 'RIC': 1884, 'ROC': 1890,
                    'ROK': 1871, 'SDP': 1969, 'SEA': 1977, 'SEP': 1969,
                    'SFG': 1958, 'SLB': 1902, 'SLM': 1884, 'SLR': 1875,
                    'STL': 1875, 'STP': 1884, 'SYR': 1879, 'TBD': 1998,
                    'TBR': 2008, 'TEX': 1972, 'TOL': 1884, 'TOR': 1977,
                    'TRO': 1871, 'WAS': 1873, 'WES': 1875, 'WHS': 1884,
                    'WIL': 1884, 'WOR': 1880, 'WSA': 1961, 'WSH': 1901,
                    'WSN': 2005}


def validate_datestring(date_text):
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD")


def sanitize_input(start_dt, end_dt, player_id):
    # error if no player ID provided
    if player_id is None:
        raise ValueError("Player ID is required. If you need to find a player's id, try pybaseball.playerid_lookup(last_name, first_name) and use their key_mlbam. If you want statcast data for all players, try the statcast() function.")
    # this id should be a string to place inside a url
    player_id = str(player_id)
    # if no dates are supplied, assume they want yesterday's data
    # send a warning in case they wanted to specify
    if start_dt is None and end_dt is None:
        today = datetime.datetime.today()
        start_dt = (today - datetime.timedelta(1)).strftime("%Y-%m-%d")
        end_dt = today.strftime("%Y-%m-%d")
        print("Warning: no date range supplied. Returning yesterday's Statcast data. For a different date range, try get_statcast(start_dt, end_dt).")
    # if only one date is supplied, assume they only want that day's stats
    # query in this case is from date 1 to date 1
    if start_dt is None:
        start_dt = end_dt
    if end_dt is None:
        end_dt = start_dt
    # now that both dates are not None, make sure they are valid date strings
    validate_datestring(start_dt)
    validate_datestring(end_dt)
    return start_dt, end_dt, player_id


def split_request(start_dt, end_dt, player_id, url):
    """
    Splits Statcast queries to avoid request timeouts
    """
    current_dt = datetime.datetime.strptime(start_dt, '%Y-%m-%d')
    end_dt = datetime.datetime.strptime(end_dt, '%Y-%m-%d')
    results = []  # list to hold data as it is returned
    player_id = str(player_id)
    print('Gathering Player Data')
    # break query into multiple requests
    while current_dt < end_dt:
        remaining = end_dt - current_dt
        # increment date ranges by at most 60 days
        delta = min(remaining, datetime.timedelta(days=2190))
        next_dt = current_dt + delta
        start_str = current_dt.strftime('%Y-%m-%d')
        end_str = next_dt.strftime('%Y-%m-%d')
        # retrieve data
        data = requests.get(url.format(start_str, end_str, player_id))
        df = pd.read_csv(io.StringIO(data.text))
        # add data to list and increment current dates
        results.append(df)
        current_dt = next_dt + datetime.timedelta(days=1)
    return pd.concat(results)


def get_zip_file(url):
    """
    Get zip file from provided URL
    """
    with requests.get(url, stream=True) as f:
        z = zipfile.ZipFile(io.BytesIO(f.content))
    return z
