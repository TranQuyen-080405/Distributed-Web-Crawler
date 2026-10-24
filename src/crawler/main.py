import json

import requests

from common.config import load_config
from common.kafka_client import flush, make_consumer, make_producer, publish
from common.url_utils import host_of
from crawler.fetcher import fetch
from crawler.parser import parse
from crawler.politeness import Politeness
from storage.repository import Repository


def main() -> None:
    cfg = load_config()
    repo = Repository(cfg.database_url)
    conn = repo.connect()
    repo.init_schema(conn)
    politeness = Politeness(cfg.user_agent, cfg.crawl_delay_seconds, cfg.request_timeout)
    consumer = make_consumer(cfg.kafka_bootstrap, "crawler", cfg.crawl_topic)
    producer = make_producer(cfg.kafka_bootstrap)
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None or msg.error():
                continue
            _handle(cfg, repo, conn, politeness, producer, msg.value())
            consumer.commit(message=msg)
    finally:
        consumer.close()
        conn.close()


def _handle(cfg, repo, conn, politeness: Politeness, producer, raw: bytes) -> None:
    try:
        job = json.loads(raw)
        url = job["url"]
        depth = int(job["depth"])
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        return
    if not politeness.allow(url):
        repo.mark(conn, url, "blocked")
        return
    politeness.wait(url)
    try:
        status, html = fetch(url, cfg.user_agent, cfg.request_timeout)
    except requests.RequestException:
        # shortcut: a failed fetch is not retried, upgrade when failures need a budget
        repo.mark(conn, url, "failed")
        return
    title, content, links = parse(html, url)
    repo.save_page(conn, url, status, title, content)
    for link in links:
        publish(
            producer,
            cfg.discovered_topic,
            {"url": link, "depth": depth + 1},
            host_of(link),
        )
    flush(producer)


if __name__ == "__main__":
    main()
