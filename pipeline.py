import time
from embeddings import embed
from store import retrieve, cache_lookup, cache_store
from router import complexity_score, pick_model, is_unsure
from llm import generate
from config import SMALL_MODEL, LARGE_MODEL
from metrics import log_request
from verifier import verify


def handle(query: str, tenant: str = "public") -> dict:
    t0 = time.perf_counter()
    q_emb = embed([query])[0]

    # 1) Semantic cache: embeddings find a candidate, the verifier confirms it
    hit = cache_lookup(q_emb, tenant)
    verify_cost = 0.0
    if hit:
        same, verify_cost = verify(query, hit["matched_query"])
        if not same:
            hit = None   # looked similar, but it's a different question

    if hit:
        latency = (time.perf_counter() - t0) * 1000
        log_request(tenant=tenant, query=query, cache_hit=1, model="cache", complexity=0,
                    escalated=0, prompt_tokens=0, completion_tokens=0, cost_usd=verify_cost,
                    baseline_cost_usd=hit["baseline_cost"], latency_ms=latency,
                    similarity=hit["similarity"])
        return {"answer": hit["answer"], "cache_hit": True, "model": "cache",
                "similarity": round(hit["similarity"], 3), "matched_query": hit["matched_query"],
                "cost_usd": round(verify_cost, 6), "latency_ms": round(latency, 1)}

    # 2) Retrieve (tenant-filtered) + route
    chunks = retrieve(q_emb, tenant)
    top_sim = chunks[0]["sim"] if chunks else 0.0
    score = complexity_score(query, top_sim)
    model = pick_model(score)

    # 3) Generate, with escalation if the small model isn't sure
    out = generate(model, query, chunks)
    cost = verify_cost + out["cost"]          # a rejected verification still cost money
    baseline = out["baseline_cost"]
    pt, ct = out["prompt_tokens"], out["completion_tokens"]
    escalated = 0
    if model == SMALL_MODEL and chunks and is_unsure(out["answer"]) and SMALL_MODEL != LARGE_MODEL:
        out2 = generate(LARGE_MODEL, query, chunks)
        cost += out2["cost"]
        baseline = out2["baseline_cost"]
        pt += out2["prompt_tokens"]
        ct += out2["completion_tokens"]
        out, model, escalated = out2, LARGE_MODEL, 1

    # 4) Cache good answers only
    if not is_unsure(out["answer"]):
        cache_store(query, q_emb, tenant, out["answer"], baseline)

    latency = (time.perf_counter() - t0) * 1000
    log_request(tenant=tenant, query=query, cache_hit=0, model=model, complexity=score,
                escalated=escalated, prompt_tokens=pt, completion_tokens=ct, cost_usd=cost,
                baseline_cost_usd=baseline, latency_ms=latency, similarity=0.0)
    return {"answer": out["answer"], "cache_hit": False, "model": model, "complexity": score,
            "escalated": bool(escalated), "sources": [c["source"] for c in chunks],
            "cost_usd": round(cost, 6), "latency_ms": round(latency, 1)}