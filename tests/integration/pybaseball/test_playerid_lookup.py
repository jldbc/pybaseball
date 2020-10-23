import pandas as pd

from pybaseball.playerid_lookup import playerid_lookup


def test_playerid_lookup_misspelling() -> None:
    """Test simple 'hank aaron' misspelling"""
    aaron_df = playerid_lookup("aron", "hak", search=True)
    assert aaron_df["name_first"][0] == "hank"
    assert aaron_df["name_last"][0] == "aaron"

def test_playerid_lookup_multiple_player() -> None:
    """Test multiple players per name - two pedro martinez"""
    assert len(playerid_lookup("martinez", "pedro", search=True)) == 2

def test_playerid_lookup_last_name() -> None:
    """Test last name-only search"""
    gariciappara_df = playerid_lookup("gariciappara", search=True)
    assert gariciappara_df["name_first"][0] == "nomar"
    assert gariciappara_df["name_last"][0] == "garciaparra"

def test_playerid_lookup_phonetic_yastrzemski() -> None:
    """Test phonetically tougher names with reasonable guesses (use-case)"""
    # Mike Yastrezremski
    yastrzemski_df = playerid_lookup("yastremsky", "mike", search=True)
    assert yastrzemski_df["name_last"][0] == "yastrzemski"

def test_playerid_lookup_phonetic_bogaerts() -> None:
    """Test phonetically tougher names with reasonable guesses (use-case)"""
    # Xander Bogaerts
    bogaerts_df = playerid_lookup("bogarts", "zander", search=True)
    assert bogaerts_df["name_last"][0] == "bogaerts"
    assert bogaerts_df["name_first"][0] == "xander"