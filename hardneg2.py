import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder
from queries import GROUPS, HARD_NEGATIVES

emb = SentenceTransformer("all-MiniLM-L6-v2")
ce = CrossEncoder("cross-encoder/quora-distilroberta-base")

originals = [g[0] for g in GROUPS]
O = emb.encode(originals, normalize_embeddings=True)

# Good pairs: each paraphrase vs its true original
pos_pairs = [(p, g[0]) for g in GROUPS for p in g[1]]
# Bad pairs: each hard negative vs the cached question the embedding thinks is closest
H = emb.encode(HARD_NEGATIVES, normalize_embeddings=True)
nearest = (H @ O.T).argmax(axis=1)
neg_pairs = [(q, originals[j]) for q, j in zip(HARD_NEGATIVES, nearest)]

pos = ce.predict(pos_pairs)
neg = ce.predict(neg_pairs)

print("PARAPHRASES (should be HIGH):")
for (a, b), s in zip(pos_pairs, pos):
    print(f"  {s:.2f}  {a}")
print("\nHARD NEGATIVES (should be LOW):")
for (a, b), s in zip(neg_pairs, neg):
    print(f"  {s:.2f}  {a}")

print("\nthreshold | paraphrases accepted | wrong answers served")
for t in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
    print(f"  {t:.1f}     | {(pos >= t).mean():>6.0%}               | {int((neg >= t).sum())} of {len(neg)}")