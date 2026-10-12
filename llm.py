from openai import OpenAI
from config import API_KEY, BASE_URL, PRICES, LARGE_MODEL

# max_retries: the SDK honors Groq's retry-after header, so rate limits just slow us down
_client = OpenAI(api_key=API_KEY, base_url=BASE_URL, max_retries=8, timeout=60)

SYSTEM = (
    "Answer using ONLY the numbered context. Cite sources like [1]. "
    "If the answer is not in the context, say exactly: "
    "\"I don't know based on the provided documents.\" Be concise."
)


def extra(model: str) -> dict:
    # gpt-oss models "think" with hidden tokens; low effort = fewer tokens, lower latency
    return {"reasoning_effort": "low"} if "gpt-oss" in model else {}


def _cost(model: str, pt: int, ct: int) -> float:
    pin, pout = PRICES[model]
    return (pt * pin + ct * pout) / 1_000_000


def generate(model: str, query: str, chunks: list[dict]):
    ctx = "\n\n".join(f"[{i+1}] ({c['source']}) {c['text']}" for i, c in enumerate(chunks))
    r = _client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"Context:\n{ctx}\n\nQuestion: {query}"},
        ],
        extra_body=extra(model),
    )
    u = r.usage
    return {
        "answer": (r.choices[0].message.content or "").strip(),
        "prompt_tokens": u.prompt_tokens,
        "completion_tokens": u.completion_tokens,
        "cost": _cost(model, u.prompt_tokens, u.completion_tokens),
        # what this exact call would have cost on the large model (savings baseline)
        "baseline_cost": _cost(LARGE_MODEL, u.prompt_tokens, u.completion_tokens),
    }