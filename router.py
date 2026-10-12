import re
from config import SMALL_MODEL, LARGE_MODEL, ROUTE_THRESHOLD

HARD_HINTS = re.compile(
    r"\b(compare|why|explain|analy[sz]e|trade-?offs?|difference|design|"
    r"step[- ]by[- ]step|evaluate|pros and cons|summari[sz]e|how does|impact)\b",
    re.I,
)

UNSURE_HINTS = ("i don't know", "not enough information", "cannot find", "not mentioned")

def complexity_score(query: str, top_sim: float) -> float:
    score = 0.0
    score += min(len(query.split()) / 40, 1) * 0.35
    if HARD_HINTS.search(query):
        score += 0.30
    if query.count("?") > 1 or " and " in query.lower():
        score += 0.15
    if top_sim < 0.45:
        score += 0.20
    return round(min(score, 1.0), 2)


def pick_model(score: float) -> str:
    return LARGE_MODEL if score >= ROUTE_THRESHOLD else SMALL_MODEL

def is_unsure(answer: str) -> bool:
    a = answer.lower()
    return any(h in a for h in UNSURE_HINTS)