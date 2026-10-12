import numpy as np
from sentence_transformers import SentenceTransformer
from queries import GROUPS, UNRELATED

MODELS = ["all-MiniLM-L6-v2", "BAAI/bge-small-en-v1.5", "all-mpnet-base-v2"]
THRESHOLDS = [round(float(t), 2) for t in np.arange(0.50, 0.96, 0.05)]

originals = [g[0] for g in GROUPS]
paras, truth = [], []
for i, (_, ps) in enumerate(GROUPS):
    for p in ps:
        paras.append(p)
        truth.append(i)
truth = np.array(truth)

for name in MODELS:
    print(f"\n=== {name} ===")
    m = SentenceTransformer(name)
    O = m.encode(originals, normalize_embeddings=True)
    P = m.encode(paras, normalize_embeddings=True)
    U = m.encode(UNRELATED, normalize_embeddings=True)

    sims = P @ O.T                      
    best_sim = sims.max(axis=1)
    best_idx = sims.argmax(axis=1)
    right = best_idx == truth
    unrelated_best = (U @ O.T).max(axis=1)

    print(f"median paraphrase sim: {np.median(best_sim):.2f} | "
          f"highest unrelated sim: {unrelated_best.max():.2f}")
    print(f"{'thr':>5} | {'hit rate':>8} | {'wrong-topic hits':>16} | {'unrelated false hits':>20}")

    best = None
    for t in THRESHOLDS:
        hit = best_sim >= t
        hit_rate = hit.mean()
        wrong = int((hit & ~right).sum())
        false_hits = int((unrelated_best >= t).sum())
        flag = ""
        if wrong == 0 and false_hits == 0 and (best is None or hit_rate > best[1]):
            best = (t, hit_rate)
        print(f"{t:>5} | {hit_rate:>7.0%} | {wrong:>16} | {false_hits:>20}")
    if best:
        print(f"--> safest threshold with max hit rate: {best[0]} ({best[1]:.0%} hit rate)")
    else:
        print("--> no threshold gave zero wrong hits for this model")