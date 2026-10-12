import sqlite3
from config import DB_PATH

c = sqlite3.connect(DB_PATH)
spent, base, n = c.execute("""
    SELECT SUM(cost_usd), SUM(baseline_cost_usd), COUNT(*) FROM requests
    WHERE query NOT LIKE '%salary bands%' AND query NOT LIKE '%pay range%'
""").fetchone()
print(f"requests: {n}")
print(f"spent: ${spent:.5f} | always-large baseline: ${base:.5f}")
print(f"savings: {(1 - spent / base) * 100:.0f}%")