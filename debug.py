import traceback

def step(name, fn):
    try:
        out = fn()
        print(f"OK   {name}: {out}")
        return out
    except Exception:
        print(f"FAIL {name}")
        traceback.print_exc()
        raise SystemExit(1)

from config import API_KEY, SMALL_MODEL, LARGE_MODEL
step("API key loaded", lambda: "yes" if API_KEY else "NO KEY FOUND")

from embeddings import embed
emb = step("embedding", lambda: len(embed(["hello"])[0]))

from store import docs, cache, retrieve
step("docs in database", lambda: docs.count())
step("retrieve", lambda: len(retrieve(embed(["leave"])[0], "public")))

from llm import generate
step("small model call", lambda: generate(SMALL_MODEL, "Say hi", [{"text": "hi", "source": "t", "sim": 1}])["answer"])
step("large model call", lambda: generate(LARGE_MODEL, "Say hi", [{"text": "hi", "source": "t", "sim": 1}])["answer"])

from pipeline import handle
step("full pipeline", lambda: handle("How many days of annual leave do I get?")["answer"])