import sqlite3
import pandas as pd
import streamlit as st
from config import DB_PATH
from metrics import init_db

st.set_page_config(page_title="TOLLGATE", page_icon="⚡", layout="wide")
st.title("⚡ TOLLGATE: cost & latency dashboard")

init_db()  

if st.button("Refresh"):
    st.rerun()

conn = sqlite3.connect(DB_PATH)
df = pd.read_sql("SELECT * FROM requests", conn)
conn.close()

if df.empty:
    st.info("No requests yet. Send a question to the API first, then click Refresh.")
    st.stop()

df["time"] = pd.to_datetime(df["ts"], unit="s")
df["path"] = df.apply(lambda r: "cache" if r.cache_hit else r.model, axis=1)

spent, baseline = df.cost_usd.sum(), df.baseline_cost_usd.sum()
savings = (1 - spent / baseline) * 100 if baseline > 0 else 0

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Requests", len(df))
c2.metric("Cache hit rate", f"{df.cache_hit.mean()*100:.0f}%")
c3.metric("Spent", f"${spent:.4f}")
c4.metric("Savings vs always-large", f"{savings:.0f}%")
c5.metric("Escalations", int(df.escalated.sum()))

l, r = st.columns(2)
with l:
    st.subheader("Requests by path")
    st.bar_chart(df.path.value_counts())
    st.subheader("Cumulative cost: TOLLGATE vs always-large")
    cum = df.sort_values("time")[["time", "cost_usd", "baseline_cost_usd"]].set_index("time").cumsum()
    cum.columns = ["TOLLGATE", "Always large model"]
    st.line_chart(cum)
with r:
    st.subheader("Latency (ms) by path")
    st.bar_chart(df.groupby("path").latency_ms.mean())
    p50 = df.latency_ms.median()
    p95 = df.latency_ms.quantile(0.95)
    st.write(f"**p50:** {p50:.0f} ms &nbsp; **p95:** {p95:.0f} ms")
    st.subheader("Complexity vs latency")
    st.scatter_chart(df[df.cache_hit == 0], x="complexity", y="latency_ms")

st.subheader("Recent requests")
st.dataframe(
    df.sort_values("time", ascending=False)[
        ["time", "tenant", "query", "path", "complexity", "escalated", "cost_usd", "latency_ms"]
    ].head(50),
    use_container_width=True,
)