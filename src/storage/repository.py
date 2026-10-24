from pathlib import Path

import psycopg

SCHEMA = Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")


class Repository:
    def __init__(self, dsn: str):
        self._dsn = dsn

    def connect(self):
        return psycopg.connect(self._dsn)

    def init_schema(self, conn) -> None:
        for statement in SCHEMA.split(";"):
            sql = statement.strip()
            if sql:
                conn.execute(sql)
        conn.commit()

    def claim_new(self, conn, url: str, host: str, depth: int) -> bool:
        row = conn.execute(
            """
            INSERT INTO urls (url, host, depth)
            VALUES (%s, %s, %s)
            ON CONFLICT (url) DO NOTHING
            RETURNING url
            """,
            (url, host, depth),
        ).fetchone()
        conn.commit()
        return row is not None

    def mark(self, conn, url: str, status: str) -> None:
        conn.execute("UPDATE urls SET status = %s WHERE url = %s", (status, url))
        conn.commit()

    def save_page(
        self, conn, url: str, status_code: int, title: str, content: str
    ) -> None:
        conn.execute(
            """
            INSERT INTO pages (url, status_code, title, content)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (url) DO UPDATE
            SET status_code = EXCLUDED.status_code,
                title = EXCLUDED.title,
                content = EXCLUDED.content,
                fetched_at = now()
            """,
            (url, status_code, title, content),
        )
        conn.execute("UPDATE urls SET status = 'done' WHERE url = %s", (url,))
        conn.commit()
