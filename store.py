import time
import uuid
import chromadb
from config import CHROMA_PATH, CACHE_THRESHOLD, CACHE_TTL_SECONDS, TOP_K
from embeddings import embed

_client = chromadb.PersistentClient(path=CHROMA_PATH)
docs = _client.get_or_create_collection("docs", metadata={"hnsw:space": "cosine"})
cache = _client.get_or_create_collection("cache", metadata={"hnsw:space": "cosine"})

def add_chunks(chunks: list[str], source: str, tenant: str = "public"):
    docs.add(
        ids=[str(uuid.uuid4()) for _ in chunks],
        documents=chunks,
        embeddings=embed(chunks),
        metadatas=[{"source": source, "tenant": tenant}] * len(chunks),
    )

def retrieve(q_emb, tenant: str, k: int = TOP_K):
    """Tenant isolation: only this tenant's chunks plus 'public' ones."""
    if docs.count() == 0:
        return []
    res = docs.query(
        query_embeddings=[q_emb],
        n_results=k,
        where={"tenant": {"$in": [tenant, "public"]}},
    )
    out = []
    for text, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
        out.append({"text": text, "source": meta["source"], "sim": 1 - dist})
        return out

def cache_lookup(q_emb, tenant: str):
    if cache.count() == 0:
        return None
    res = cache.query(query_embeddings=[q_emb], n_results=1, where={"tenant": tenant})
    if not res["ids"][0]:
        return None
    sim = 1 - res["distances"][0][0]
    meta = res["metadatas"][0][0]
    fresh = time.time() - meta["created"] < CACHE_TTL_SECONDS
    if sim >= CACHE_THRESHOLD and fresh:
        return {
            "answer": meta["answer"],
            "similarity": sim,
            "baseline_cost": meta["baseline_cost"],
            "matched_query": res["documents"][0][0],
        }
    return None

def cache_store(query: str, q_emb, tenant: str, answer: str, baseline_cost: float):
    cache.add(
        ids=[str(uuid.uuid4())],
        documents=[query],
        embeddings=[q_emb],
        metadatas=[{
            "tenant": tenant,
            "answer": answer,
            "baseline_cost": baseline_cost,
            "created": time.time(),
        }],
    )

def clear_cache(tenant: str | None = None):
    """Call after re-ingesting docs so stale answers don't survive."""
    if tenant:
        cache.delete(where={"tenant": tenant})
    else:
        ids = cache.get()["ids"]
        if ids:
            cache.delete(ids=ids)

