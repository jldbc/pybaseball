import pandas as pd

def playerid_mapping() -> pd.DataFrame:
    """Returns a pandas DataFrame with player ID references for many available data sources
    Includes 
    - Player Name (first, last, MLB, FanGraphs, Yahoo, CBS, NFBC, FanDuel, ESPN, DraftKings, Rotowire, Razzball)
    - Player ID (Fangraphs, MLB, CBS, Retrosheet, BBRef, NFBC, Baseball Prospectus, Yahoo, Rotowire, Fanduel)
    - Team, League, Position

    Returns:
        pd.DataFrame: DataFrame from smartfantasybaseball, useful for merges across data sources
    """
    return pd.read_csv("https://www.smartfantasybaseball.com/PLAYERIDMAPCSV")
