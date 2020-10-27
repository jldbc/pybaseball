import pandas as pd

from pybaseball.playerid_lookup import player_search_client


def test_playerid_lookup_misspelling() -> None:
    """Test simple 'hank aaron' misspelling"""
    client = player_search_client()
    aaron_df = client.search("aron", "hak", fuzzy=True)
    assert aaron_df["name_first"][0] == "hank"
    assert aaron_df["name_last"][0] == "aaron"

def test_playerid_lookup_multiple_player() -> None:
    """Test multiple players per name - two pedro martinez"""
    client = player_search_client()
    assert len(client.search("martinez", "pedro", fuzzy=True)) == 2

def test_playerid_lookup_last_name() -> None:
    """Test last name-only search"""
    client = player_search_client()
    gariciappara_df = client.search("gariciappara", fuzzy=True)
    assert gariciappara_df["name_first"][0] == "nomar"
    assert gariciappara_df["name_last"][0] == "garciaparra"

def test_playerid_lookup_phonetic_yastrzemski() -> None:
    """Test phonetically tougher names with reasonable guesses (use-case)"""
    # Mike Yastrezremski
    client = player_search_client()
    yastrzemski_df = client.search("yastremsky", "mike", fuzzy=True)
    assert yastrzemski_df["name_last"][0] == "yastrzemski"

def test_playerid_lookup_phonetic_bogaerts() -> None:
    """Test phonetically tougher names with reasonable guesses (use-case)"""
    # Xander Bogaerts
    client = player_search_client()
    bogaerts_df = client.search("bogarts", "zander", fuzzy=True)
    assert bogaerts_df["name_last"][0] == "bogaerts"
    assert bogaerts_df["name_first"][0] == "xander"
