import sqlite3
import statistics
from config import DB_PATH
from store import clear_cache
from pipeline import handle
from queries import GROUPS
import time

# Clean slate so the numbers are honest
clear_cache()
conn = sqlite3.connect(DB_PATH)
conn.execute("DELETE FROM requests")
conn.commit()
conn.close()

results = []

print("\n--- COLD RUN (fills the cache) ---")
for q, _ in GROUPS:
    r = handle(q)
    results.append(r)
    print(f"{r['model']:<22} {r['latency_ms']:>7.0f} ms  {q[:55]}")
    time.sleep(4)

print("\n--- PARAPHRASE RUN (should hit the cache) ---")
for q, paraphrases in GROUPS:
    for p in paraphrases:
        r = handle(p)
        results.append(r)
        tag = f"HIT  sim={r['similarity']}" if r["cache_hit"] else "miss"
        print(f"{tag:<18} {r['latency_ms']:>7.0f} ms  {p[:50]}")
        if r["cache_hit"]:
            print(f"{'':<18} matched: {r['matched_query'][:60]}")
        time.sleep(4)

hits = [r for r in results if r["cache_hit"]]
miss = [r for r in results if not r["cache_hit"]]
print("\n=== SUMMARY ===")
print(f"Requests: {len(results)} | cache hit rate: {len(hits)/len(results):.0%}")
if hits:
    print(f"Avg latency on hit:  {statistics.mean(r['latency_ms'] for r in hits):.0f} ms")
print(f"Avg latency on miss: {statistics.mean(r['latency_ms'] for r in miss):.0f} ms")
print(f"Total cost: ${sum(r['cost_usd'] for r in results):.5f}")