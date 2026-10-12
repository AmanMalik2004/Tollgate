import sys
from pathlib import Path
from store import add_chunks, clear_cache

def chunk(text: str, size: int = 180, overlap: int = 30):
    words = text.split()
    out, i = [], 0
    while i < len(words):
        out.append(" ".join(words[i:i + size]))
        i += size - overlap
    return out


if __name__ == "__main__":
    tenant = sys.argv[1] if len(sys.argv) > 1 else "public"
    for p in Path("data").glob("*"):
        if p.suffix.lower() in {".txt", ".md"}:
            chunks = chunk(p.read_text(encoding="utf-8", errors="ignore"))
            add_chunks(chunks, source=p.name, tenant=tenant)
            print(f"{p.name}: {len(chunks)} chunks -> tenant '{tenant}'")
    clear_cache(tenant)