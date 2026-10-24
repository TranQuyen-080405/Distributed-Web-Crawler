# Distributed Web Crawler

Three processes talk through Kafka. PostgreSQL stops the same URL from being crawled twice and stores each page.

```text
seed.py
  → Frontier (dedup in the urls table)
  → topic crawl-urls
  → Crawler (robots.txt, delay, download HTML, extract links)
  → pages table
  → topic discovered-links
  → Scheduler / Frontier
```

The scheduler runs as a single replica. It receives new links, normalizes each URL, drops URLs it has already seen, and sends jobs to the crawlers. Crawlers run as many replicas in the `crawler` consumer group, so each job is handled once. The Kafka message key is the hostname, so URLs for the same host stay on one partition.

`urls.status` moves from `pending` to `queued` to `done`. It can also become `blocked` or `failed`.

## Run locally

Kafka and PostgreSQL must already be running.

```powershell
copy .env.example .env
uv sync
$env:PYTHONPATH = "src"
uv run python -m scheduler.main
uv run python -m crawler.main
uv run python scripts/seed.py https://example.com
```

Start the scheduler and the crawler in separate terminals, then run `seed.py`.

## Kubernetes

```powershell
docker build -t distributed-web-crawler:latest .
kubectl apply -f k8s/kafka.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/scheduler.yaml
kubectl apply -f k8s/crawler.yaml
```

`k8s/kafka.yaml` starts one KRaft broker. If Lab 1 already provides Kafka, point `KAFKA_BOOTSTRAP` at that Service and skip this file.

The Postgres password in the manifest is a local default only.
