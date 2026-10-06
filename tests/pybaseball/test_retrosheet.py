from unittest.mock import MagicMock

import pytest

import pybaseball.retrosheet as retrosheet


def test_events_uses_token_auth(monkeypatch: pytest.MonkeyPatch) -> None:
    # Regression test for #455: when GH_TOKEN is set, the GitHub client must be
    # built with the modern keyword auth API (Auth.Token) rather than the
    # deprecated positional-token form.
    monkeypatch.setenv('GH_TOKEN', 'dummy_token')
    fake_github = MagicMock()
    fake_github.return_value.get_repo.side_effect = RuntimeError("stop")
    monkeypatch.setattr(retrosheet, 'Github', fake_github)

    with pytest.raises(RuntimeError):
        retrosheet.events(2019)

    args, kwargs = fake_github.call_args
    assert args == ()
    assert 'auth' in kwargs


def test_events_anonymous_without_token(monkeypatch: pytest.MonkeyPatch) -> None:
    # Regression test for #455: with no GH_TOKEN, the client must be created
    # anonymously (Github()) instead of passing an empty token string.
    monkeypatch.delenv('GH_TOKEN', raising=False)
    fake_github = MagicMock()
    fake_github.return_value.get_repo.side_effect = RuntimeError("stop")
    monkeypatch.setattr(retrosheet, 'Github', fake_github)

    with pytest.raises(RuntimeError):
        retrosheet.events(2019)

    args, kwargs = fake_github.call_args
    assert args == ()
    assert 'auth' not in kwargs
