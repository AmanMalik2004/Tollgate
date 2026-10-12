from store import add_chunks, clear_cache
from pipeline import handle

clear_cache()
add_chunks(["Acme internal salary bands: engineers earn 80000 to 120000 dollars per year."],
           source="acme_private.txt", tenant="acme")

def show(label, query, tenant):
    r = handle(query, tenant)
    print(f"[{tenant:>6}] {label:<28} cache_hit={r['cache_hit']!s:<5} -> {r['answer'][:90]}")

def has_salary(r):
    return "80,000" in r["answer"] or "80000" in r["answer"]

r1 = handle("What are the salary bands for engineers?", "acme")
r2 = handle("What are the salary bands for engineers?", "public")
r3 = handle("What is the pay range for engineers?", "acme")
r4 = handle("What is the pay range for engineers?", "public")

assert has_salary(r1) and not r1["cache_hit"]
assert not has_salary(r2)
assert has_salary(r3) and r3["cache_hit"]
assert not has_salary(r4) and not r4["cache_hit"]
print("PASS: tenant isolation holds")