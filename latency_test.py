import time
from verifier import verify

for i in range(6):
    t = time.perf_counter()
    ok, cost = verify("What's the yearly vacation allowance?",
                      "How many days of paid annual leave do employees get?")
    print(f"{(time.perf_counter() - t) * 1000:6.0f} ms  -> {ok}  cost ${cost:.6f}")
    time.sleep(3)    # well under any rate limit