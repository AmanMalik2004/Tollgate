from sentence_transformers import SentenceTransformer
from queries import GROUPS, HARD_NEGATIVES
from verifier import verify

emb = SentenceTransformer("all-MiniLM-L6-v2")
originals = [g[0] for g in GROUPS]
O = emb.encode(originals, normalize_embeddings=True)

pos = [(p, g[0]) for g in GROUPS for p in g[1]]
H = emb.encode(HARD_NEGATIVES, normalize_embeddings=True)
neg = [(q, originals[j]) for q, j in zip(HARD_NEGATIVES, (H @ O.T).argmax(axis=1))]

total_cost = 0.0

print("PARAPHRASES (want YES):")
accepted = 0
for a, b in pos:
    ok, c = verify(a, b)
    total_cost += c
    accepted += ok
    print(f"  {'YES' if ok else 'no ':<3}  {a}")

print("\nHARD NEGATIVES (want no):")
wrong = 0
for a, b in neg:
    ok, c = verify(a, b)
    total_cost += c
    wrong += ok
    print(f"  {'YES  <-- WRONG' if ok else 'no':<15}  {a}")

print(f"\nParaphrases accepted: {accepted}/{len(pos)} ({accepted/len(pos):.0%})")
print(f"Wrong answers served: {wrong}/{len(neg)}")
print(f"Verifier cost for {len(pos)+len(neg)} checks: ${total_cost:.5f}")