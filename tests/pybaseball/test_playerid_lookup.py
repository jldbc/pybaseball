import os
import sys
import time
import tempfile
from pathlib import Path

import pytest

from pybaseball.playerid_lookup import chadwick_register

pil = sys.modules["pybaseball.playerid_lookup"]


def test_chadwick_register_refreshes_when_stale(monkeypatch):
    monkeypatch.setattr(pil.cache.config, "enabled", False)
    with tempfile.TemporaryDirectory() as td:
        fake_register = Path(td) / "chadwick-register.csv"
        fake_register.write_text("name_last,name_first,key_mlbam\nstale,player,1\n")

        monkeypatch.setattr(pil, "get_register_file", lambda: str(fake_register))

        old = time.time() - 100 * 86400
        os.utime(fake_register, (old, old))

        calls = {"n": 0}

        def fake_get(*args, **kwargs):
            calls["n"] += 1
            raise RuntimeError("network hit")

        monkeypatch.setattr(pil.requests, "get", fake_get)

        with pytest.raises(RuntimeError, match="network hit"):
            chadwick_register()

        assert calls["n"] == 1