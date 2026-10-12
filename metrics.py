import sqlite3
import time
from config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts REAL, tenant TEXT, query TEXT,
    cache_hit INTEGER, model TEXT, complexity REAL,
    escalated INTEGER,
    prompt_tokens INTEGER, completion_tokens INTEGER,
    cost_usd REAL, baseline_cost_usd REAL,
    latency_ms REAL, similarity REAL
)
"""


def init_db():
    c = sqlite3.connect(DB_PATH)
    c.execute(SCHEMA)
    c.commit()
    c.close()


init_db()  


def log_request(**r):
    c = sqlite3.connect(DB_PATH)
    c.execute(
        """INSERT INTO requests
        (ts, tenant, query, cache_hit, model, complexity, escalated,
         prompt_tokens, completion_tokens, cost_usd, baseline_cost_usd, latency_ms, similarity)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (time.time(), r["tenant"], r["query"], r["cache_hit"], r["model"], r["complexity"],
         r["escalated"], r["prompt_tokens"], r["completion_tokens"], r["cost_usd"],
         r["baseline_cost_usd"], r["latency_ms"], r["similarity"]),
    )
    c.commit()
    c.close()