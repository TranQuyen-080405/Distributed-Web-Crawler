import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    kafka_bootstrap: str
    crawl_topic: str
    discovered_topic: str
    database_url: str
    user_agent: str
    crawl_delay_seconds: float
    max_depth: int
    request_timeout: float


def load_config() -> Config:
    return Config(
        kafka_bootstrap=os.environ.get("KAFKA_BOOTSTRAP", "localhost:9092"),
        crawl_topic=os.environ.get("CRAWL_TOPIC", "crawl-urls"),
        discovered_topic=os.environ.get("DISCOVERED_TOPIC", "discovered-links"),
        database_url=os.environ.get(
            "DATABASE_URL",
            "postgresql://crawler:crawler@localhost:5432/crawler",
        ),
        user_agent=os.environ.get("USER_AGENT", "DistributedWebCrawler/0.1"),
        crawl_delay_seconds=float(os.environ.get("CRAWL_DELAY_SECONDS", "1")),
        max_depth=int(os.environ.get("MAX_DEPTH", "2")),
        request_timeout=float(os.environ.get("REQUEST_TIMEOUT", "10")),
    )
