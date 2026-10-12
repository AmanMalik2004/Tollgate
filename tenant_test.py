from store import add_chunks, clear_cache
from pipeline import handle

clear_cache()
add_chunks(["Acme internal salary bands: engineers earn 80000 to 120000 dollars per year."],
           source="acme_private.txt", tenant="acme")

def show(label, query, tenant):
    r = handle(query, tenant)
    print(f"[{tenant:>6}] {label:<28} cache_hit={r['cache_hit']!s:<5} -> {r['answer'][:90]}")

show("original question", "What are the salary bands for engineers?", "acme")
show("original question", "What are the salary bands for engineers?", "public")
show("paraphrase", "What is the pay range for engineers?", "acme")
show("paraphrase", "What is the pay range for engineers?", "public")