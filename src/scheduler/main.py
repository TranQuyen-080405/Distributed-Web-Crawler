import json

from common.config import load_config
from common.kafka_client import flush, make_consumer, make_producer
from scheduler.frontier import Frontier
from storage.repository import Repository


def main() -> None:
    cfg = load_config()
    repo = Repository(cfg.database_url)
    conn = repo.connect()
    repo.init_schema(conn)
    producer = make_producer(cfg.kafka_bootstrap)
    frontier = Frontier(repo, conn, producer, cfg.crawl_topic, cfg.max_depth)
    consumer = make_consumer(cfg.kafka_bootstrap, "scheduler", cfg.discovered_topic)
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None or msg.error():
                continue
            _handle(frontier, producer, msg.value())
            consumer.commit(message=msg)
    finally:
        consumer.close()
        conn.close()


def _handle(frontier: Frontier, producer, raw: bytes) -> None:
    try:
        job = json.loads(raw)
        frontier.enqueue(job["url"], int(job["depth"]))
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        return
    flush(producer)


if __name__ == "__main__":
    main()
