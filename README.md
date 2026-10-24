# Distributed Web Crawler

Ba process nói chuyện qua Kafka. PostgreSQL là nơi chống trùng URL và lưu trang.

```text
seed.py
  → Frontier (dedup trong bảng urls)
  → topic crawl-urls
  → Crawler (robots.txt, delay, tải HTML, tách link)
  → bảng pages
  → topic discovered-links
  → Scheduler / Frontier
```

Scheduler chỉ có một replica: nó nhận link mới, chuẩn hóa URL, bỏ URL đã thấy, rồi đẩy job sang crawler. Crawler chạy nhiều replica, cùng consumer group `crawler`, mỗi job một lần. Key của message Kafka là hostname, nên URL cùng host nằm một partition.

`urls.status` đi từ `pending` → `queued` → `done`, hoặc `blocked` / `failed`.

## Chạy local

```powershell
copy .env.example .env
uv sync
$env:PYTHONPATH = "src"
uv run python -m scheduler.main
uv run python -m crawler.main
uv run python scripts/seed.py https://example.com
```

## Kubernetes

```powershell
docker build -t distributed-web-crawler:latest .
kubectl apply -f k8s/kafka.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/scheduler.yaml
kubectl apply -f k8s/crawler.yaml
```

`k8s/kafka.yaml` là một broker KRaft. Nếu Lab 1 đã có Kafka, trỏ `KAFKA_BOOTSTRAP` vào Service đó và không apply file này.

Mật khẩu Postgres trong manifest là mặc định cho máy local.
