import pandas as pd

from pybaseball.playerid_lookup import playerid_lookup


def test_playerid_lookup_misspelling() -> None:
    """Test simple 'hank aaron' misspelling"""
    aaron_df = playerid_lookup("aron", "hak", fuzzy=True)
    assert aaron_df["name_first"][0] == "hank"
    assert aaron_df["name_last"][0] == "aaron"

def test_playerid_lookup_multiple_player() -> None:
    """Test multiple players per name - two pedro martinez"""
    assert len(playerid_lookup("martinez", "pedro", fuzzy=True)) == 2

def test_playerid_lookup_last_name() -> None:
    """Test last name-only search"""
    gariciappara_df = playerid_lookup("gariciappara", fuzzy=True)
    assert gariciappara_df["name_first"][0] == "nomar"
    assert gariciappara_df["name_last"][0] == "garciaparra"

def test_playerid_lookup_phonetic_yastrzemski() -> None:
    """Test phonetically tougher names with reasonable guesses (use-case)"""
    # Mike Yastrezremski
    yastrzemski_df = playerid_lookup("yastremsky", "mike", fuzzy=True)
    assert yastrzemski_df["name_last"][0] == "yastrzemski"

def test_playerid_lookup_phonetic_bogaerts() -> None:
    """Test phonetically tougher names with reasonable guesses (use-case)"""
    # Xander Bogaerts
    bogaerts_df = playerid_lookup("bogarts", "zander", fuzzy=True)
    assert bogaerts_df["name_last"][0] == "bogaerts"
    assert bogaerts_df["name_first"][0] == "xander"
    
def test_playerid_lookup_three_word_name() -> None:
    """Test names with three words in them"""
    # Hyun Jin Ryu
    ryu_df = playerid_lookup("jin ryu", "hyun", fuzzy=True)
    assert ryu_df["name_last"][0] == "ryu"
    assert ryu_df["name_first"][0] == "hyun jin"

def test_playerid_lookup_abbreviated_name() -> None:
    """Test names with abbreviations in them"""
    # JD Martinez
    martinez_df = playerid_lookup("martinez", "jd", fuzzy=True)
    assert martinez_df["name_last"][0] == "martinez"
    assert martinez_df["name_first"][0] == "j. d."
    
def test_playerid_lookup_name_with_jr() -> None:
    """Test names with abbreviations in them"""
    # Ronald Acuna Jr
    acuna_df = playerid_lookup("acuna jr.", "ronald", fuzzy=True)
    assert acuna_df["name_last"][0] == "acuna"
    assert acuna_df["name_first"][0] == "ronald"
    
def test_playerid_lookup_hyphenated_name() -> None:
    """Test names with abbreviations in them"""
    # Isiah Kiner-Falefa
    falefa_df = playerid_lookup("Kiner Falefa", "isiah", fuzzy=True)
    assert falefa_df["name_last"][0] == "kiner-falefa"
    assert falefa_df["name_first"][0] == "isiah"

def test_playerid_lookup_garbage() -> None:
    """Test non-player string"""
    no_match = playerid_lookup("abcxyz", "xyzabc", fuzzy=True)
    assert len(no_match) == 5
