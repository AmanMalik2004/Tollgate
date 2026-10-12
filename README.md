# TOLLGATE ⚡

A cost-aware gateway for RAG: **verified semantic caching**, **complexity-based model routing**,
**tenant isolation**, and a per-request **cost & latency dashboard**.

## The problem
RAG gets expensive at scale. Many questions are repeats in different words, and most don't need
the biggest model. TOLLGATE sits in front of the LLM and decides, per request, whether to answer
from cache, a small model, or a large model, and records what each decision cost.

## How it works
```
query → embed → tenant-scoped cache lookup → candidate found?
                                   │ yes → LLM verifier: "same question?" → YES → serve cached answer
                                   │ no / rejected
                 retrieve (tenant-filtered) → complexity router → small model ─(unsure)→ large model
                                   → cache answer → log cost/latency → dashboard
```

## Results (development benchmark: 30 requests = 10 questions + 20 paraphrases; two runs)
| Metric | Result |
|---|---|
| Paraphrases served from cache | 15–16 of 20 (75–80%) |
| Spend vs always using the large model | $0.00093 vs $0.00289 (**68% lower**) |
| Verifier cost per cache hit | ≈ $0.000007 |
| Average latency, cache hit vs miss | 462 ms vs 915 ms (single run; misses include large-model calls) |
| Held-out test: paraphrases served | 8/10 |
| Held-out test: wrong answers served | **0/5** adversarial near-misses |
| Tenant isolation (`tenant_test.py`) | No cross-tenant retrieval or cache leakage |

The 68% depends on the workload: this benchmark is 2/3 paraphrases by design. Routing alone saves
about 50% on routed requests, because the two model tiers differ ~2× in price.

## What I tried, and what failed
1. **Threshold-only cache at similarity 0.88:** 1 of 20 paraphrases hit.
2. **Loosened to 0.65:** hit rate rose to 47%, but adversarial near-misses ("primary" vs "secondary"
   caregiver, "paid" vs "unpaid" leave) scored 0.71–0.97, overlapping the genuine paraphrases (0.57–0.95); "secondary caregiver" (0.97)
   outscored all of them. No threshold separates them: **8/8 wrong answers would be served.**
3. **Cross-encoder verifier (Quora duplicate-question model):** at thresholds ≤0.5 it accepted ≤20% of
   paraphrases and still served 1/8 near-misses; at ≥0.6 it was safe but accepted only 15%. Rejected.
4. **LLM verifier (small model, YES/NO):** 18/20 paraphrases accepted, 0/8 wrong on the dev set, then
   8/10 and 0/5 on a held-out set.

## Design decisions
- **Embeddings propose, an LLM verifies.** Wrong cached answers cost more than missed hits, so the cache fails safe.
- **Tenant-scoped cache and retrieval.** Cached answers never cross tenants (see `tenant_test.py`).
- **Escalation:** if the small model says it doesn't know, the request is retried on the large model.
- **Honest accounting:** verifier calls and failed escalations are included in cost.

## Limitations
- Small, self-written evaluation sets (20 + 10 paraphrases, 8 + 5 near-misses): thresholds should be re-tuned on real traffic.
- Recall is capped by the embedding stage: heavily reworded questions never become candidates.
- The router is a heuristic (length, keywords, retrieval confidence), not a trained classifier.
- Savings baseline: the same tokens priced at the large model; prices are in `config.py` and should be verified.
- Free-tier rate limits (8,000 tokens/minute) affected latency measurements.
- The router is optimized for cost; I have not evaluated whether small-model answers are as good as large-model answers.
- Answer quality was not measured, only cache correctness (was the *question* a true match).
- Results varied by one paraphrase between runs (LLM verifier is not perfectly deterministic).
- The corpus is one small synthetic policy file (3 paragraphs); retrieval quality at realistic scale is untested.
- The verifier prompt was revised once after dev-set results (first version accepted only 35% of paraphrases),
  so dev numbers are tuned; the held-out set was written afterward, with AI assistance, and is not fully blind.

## Run it
```bash
pip install -r requirements.txt
cp .env.example .env        # add your key
python ingest.py public
uvicorn main:app --reload   # API docs at http://localhost:8000/docs
streamlit run dashboard.py
python bench.py
```