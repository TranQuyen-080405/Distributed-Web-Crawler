import time
from urllib.parse import urlsplit
from urllib.robotparser import RobotFileParser

import requests


class Politeness:
    def __init__(self, user_agent: str, delay: float, timeout: float):
        self._user_agent = user_agent
        self._delay = delay
        self._timeout = timeout
        self._robots: dict[str, RobotFileParser] = {}
        self._next_ok: dict[str, float] = {}

    def allow(self, url: str) -> bool:
        parts = urlsplit(url)
        host = parts.netloc
        parser = self._robots.get(host)
        if parser is None:
            parser = RobotFileParser()
            robots_url = f"{parts.scheme}://{host}/robots.txt"
            try:
                response = requests.get(
                    robots_url,
                    timeout=self._timeout,
                    headers={"User-Agent": self._user_agent},
                )
                lines = response.text.splitlines() if response.ok else []
            except requests.RequestException:
                lines = []
            parser.parse(lines)
            self._robots[host] = parser
        return parser.can_fetch(self._user_agent, url)

    def wait(self, url: str) -> None:
        # shortcut: delay is per process, upgrade when several replicas share one host
        host = urlsplit(url).netloc
        pause = self._next_ok.get(host, 0) - time.monotonic()
        if pause > 0:
            time.sleep(pause)
        self._next_ok[host] = time.monotonic() + self._delay
