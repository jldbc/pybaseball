import datetime
from time import sleep
from typing import Any, Optional

import requests

from ..datahelpers import singleton


class BRefSession(singleton.Singleton):
    """
    This is needed because Baseball Reference has rules against bots.

    Current policy says no more than 20 requests per minute, but in testing
    anything more than 10 requests per minute gets you blocked for one hour.

    So this global session will prevent a user from getting themselves blocked.
    """

    def __init__(self, max_requests_per_minute: int = 10) -> None:
        self.max_requests_per_minute = max_requests_per_minute
        self.last_request: Optional[datetime.datetime]  = None
        self.session = requests.Session()
    
    def get(self, url: str, **kwargs: Any) -> requests.Response:
        if self.last_request:
            delta = datetime.datetime.now() - self.last_request
            sleep_length = (60 / self.max_requests_per_minute) - delta.total_seconds()
            if sleep_length > 0:
                sleep(sleep_length)

        self.last_request = datetime.datetime.now()

        return self.session.get(url, **kwargs)
                