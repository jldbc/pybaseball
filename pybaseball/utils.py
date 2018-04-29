import pandas as pd
import requests
import datetime
import io


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
        # add at most 60 days
        delta = min(remaining, datetime.timedelta(days=60))
        next_dt = current_dt + delta
        start_str = current_dt.strftime('%Y-%m-%d')
        end_str = next_dt.strftime('%Y-%m-%d')
        data = requests.get(url.format(start_str, end_str, player_id))
        df = pd.read_csv(io.StringIO(data.text))
        results.append(df)
        current_dt = next_dt + datetime.timedelta(days=1)
    return pd.concat(results)
