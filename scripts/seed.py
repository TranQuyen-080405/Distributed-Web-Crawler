import sys

from common.config import load_config
from common.kafka_client import flush, make_producer
from scheduler.frontier import Frontier
from storage.repository import Repository


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("usage: python scripts/seed.py <url> [url...]")
    cfg = load_config()
    repo = Repository(cfg.database_url)
    conn = repo.connect()
    repo.init_schema(conn)
    producer = make_producer(cfg.kafka_bootstrap)
    frontier = Frontier(repo, conn, producer, cfg.crawl_topic, cfg.max_depth)
    try:
        for url in sys.argv[1:]:
            frontier.enqueue(url, 0)
        flush(producer)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
