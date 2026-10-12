import time
from sentence_transformers import SentenceTransformer
from config import CACHE_THRESHOLD
from verifier import verify

ORIGINALS = [
    "How many days per week can employees work remotely?",
    "Whose approval is needed to work remotely?",
    "How many times per year can the home-office stipend be claimed?",
    "Where must business travel be booked?",
    "Above what dollar amount does an expense need prior approval?",
    "Who has to approve expenses above 200 dollars?",
    "Which messaging platform must remote employees be reachable on?",
    "Up to how many leave days can be carried into next year?",
    "How much can be spent on meals per day while travelling?",
    "Within how many days are expense claims reimbursed?",
]
PARAPHRASES = [
    "What's the maximum number of weekdays I'm allowed to do my job from home?",
    "Who needs to sign off before I can work remotely?",
    "How often can I get the work-from-home stipend?",
    "Which system should I use to reserve work trips?",
    "Beyond what dollar figure do I need permission before spending?",
    "Which manager signs off on spending over 200 dollars?",
    "Which chat app do remote staff need to stay reachable on?",
    "How many leave days can I bring over into the following year?",
    "How much can I spend on food per day on a business trip?",
    "How many days until I'm paid back for submitted expenses?",
]
HARD_NEGATIVES = [
    "How many days per week can employees work from the office?",
    "Whose approval is needed to book business travel?",
    "How often can I claim the travel meal allowance?",
    "What is the daily hotel allowance when travelling?",
    "Within how many days must I submit receipts after a trip?",
]

assert ORIGINALS and len(ORIGINALS) == len(PARAPHRASES), "need one paraphrase per original"
assert HARD_NEGATIVES, "hard negatives list is empty"

emb = SentenceTransformer("all-MiniLM-L6-v2")
O = emb.encode(ORIGINALS, normalize_embeddings=True)
P = emb.encode(PARAPHRASES, normalize_embeddings=True)
H = emb.encode(HARD_NEGATIVES, normalize_embeddings=True)

candidates = accepted = 0
print("PARAPHRASES")
for i, (p, row) in enumerate(zip(PARAPHRASES, P @ O.T)):
    j = int(row.argmax())
    is_candidate = (j == i) and row[j] >= CACHE_THRESHOLD
    ok = False
    if is_candidate:
        ok, _ = verify(p, ORIGINALS[j])
        time.sleep(1.5)
    candidates += is_candidate
    accepted += ok
    if ok:
        status = "HIT"
    elif is_candidate:
        status = "rejected by verifier"
    elif j != i:
        status = f"matched wrong sibling #{j}"
    else:
        status = "below embedding threshold"
    print(f"  {status:<28} sim={row[j]:.2f}  {p}")

wrong = 0
print("\nHARD NEGATIVES")
for q, row in zip(HARD_NEGATIVES, H @ O.T):
    j = int(row.argmax())
    served = False
    if row[j] >= CACHE_THRESHOLD:
        served, _ = verify(q, ORIGINALS[j])
        time.sleep(1.5)
    wrong += served
    print(f"  {'WRONG ANSWER SERVED' if served else 'blocked':<28} sim={row[j]:.2f}  {q}")

n = len(PARAPHRASES)
print(f"\nCandidate recall (embedding stage): {candidates}/{n}")
print(f"Paraphrases served from cache:      {accepted}/{n}")
print(f"Wrong answers served:               {wrong}/{len(HARD_NEGATIVES)}")