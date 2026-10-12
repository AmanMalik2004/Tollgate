from sentence_transformers import SentenceTransformer
from queries import GROUPS, HARD_NEGATIVES

m = SentenceTransformer("all-MiniLM-L6-v2")
O = m.encode([g[0] for g in GROUPS], normalize_embeddings=True)
H = m.encode(HARD_NEGATIVES, normalize_embeddings=True)
sims = H @ O.T

for q, row in zip(HARD_NEGATIVES, sims):
    j = row.argmax()
    print(f"{row[j]:.2f}  {q}\n      closest cached: {GROUPS[j][0]}\n")

print("Wrong answers served at each threshold:")
for t in [0.60, 0.65, 0.70, 0.75, 0.80, 0.85]:
    n = int((sims.max(axis=1) >= t).sum())
    print(f"  threshold {t}: {n} of {len(HARD_NEGATIVES)}")