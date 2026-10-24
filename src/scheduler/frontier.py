from common.kafka_client import publish
from common.url_utils import host_of, normalize_url


class Frontier:
    def __init__(self, repo, conn, producer, topic: str, max_depth: int):
        self._repo = repo
        self._conn = conn
        self._producer = producer
        self._topic = topic
        self._max_depth = max_depth

    def enqueue(self, raw_url: str, depth: int, base: str | None = None) -> bool:
        url = normalize_url(raw_url, base)
        if url is None or depth > self._max_depth:
            return False
        host = host_of(url)
        if not self._repo.claim_new(self._conn, url, host, depth):
            return False
        # shortcut: crash between insert and publish strands the URL, upgrade when pending rows are requeued
        publish(self._producer, self._topic, {"url": url, "depth": depth}, host)
        self._repo.mark(self._conn, url, "queued")
        return True
