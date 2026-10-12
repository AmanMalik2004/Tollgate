from config import SMALL_MODEL, PRICES
from llm import _client, extra

PROMPT = """You decide whether a cached answer can be reused for a new question.

Reply YES only if both questions ask for the SAME specific fact, so the same answer is correct for both.
Ignore differences in wording, tone, pronouns ("I" vs "employees"), or word order.
Reply NO if they differ in any detail that changes the answer: a different category, group, quantity, time period or item.

Examples:
A: How many vacation days do new hires get? | B: What is the number of holiday days for new hires? -> YES
A: What is the price of the basic plan? | B: How much does the basic plan cost? -> YES
A: What is the price of the basic plan? | B: What is the price of the premium plan? -> NO
A: How long is the warranty for laptops? | B: How long is the warranty for phones? -> NO
A: How do I cancel my subscription? | B: How do I get a refund for my subscription? -> NO

Reply with only YES or NO.
A: {a} | B: {b} ->"""


def verify(new_q: str, cached_q: str):
    """Returns (is_same_question, cost_usd). Fails safe: anything but YES means no."""
    r = _client.chat.completions.create(
        model=SMALL_MODEL,
        temperature=0,
        max_completion_tokens=200,
        messages=[{"role": "user", "content": PROMPT.format(a=new_q, b=cached_q)}],
        extra_body=extra(SMALL_MODEL),
    )
    u = r.usage
    pin, pout = PRICES[SMALL_MODEL]
    cost = (u.prompt_tokens * pin + u.completion_tokens * pout) / 1_000_000
    answer = (r.choices[0].message.content or "").strip().upper()
    return answer.startswith("YES"), cost