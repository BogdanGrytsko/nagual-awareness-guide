"""Run many outcome traces in one pass and print them compactly.

Each spec line is:  CID | terms,comma,separated | since | until | max
Blank since/until fall back to the commitment date / no limit.

    py scripts/trace_batch.py specs.txt

Word-boundary matching, because substring matching made "earn" hit "learn" and
returned 938 rows for one commitment.
"""
import glob
import io
import json
import os
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

FROZEN = Path("tg-private/commitments-2021-22-frozen.jsonl")
CHAT = Path("tg-private/tac-full.jsonl")
DOCS = Path("tg-private/docs")
INDEX = Path("tg-private/tac-docs-index.json")

frozen = {}
for l in FROZEN.open(encoding="utf-8"):
    o = json.loads(l)
    frozen[o["cid"]] = o

chat = [json.loads(l) for l in CHAT.open(encoding="utf-8")]
chat.sort(key=lambda d: d["date"])
id_sender = {e["id"]: e["sender"] for e in json.loads(INDEX.read_text(encoding="utf-8"))}

essays = []
for f in glob.glob(str(DOCS / "*.txt")):
    m = re.match(r"(\d{4}-\d{2}-\d{2})_(\d+)_", os.path.basename(f))
    if m:
        essays.append((m.group(1), int(m.group(2)), f))
essays.sort()


def build_rx(terms):
    parts = []
    for t in terms:
        t = t.strip()
        if not t:
            continue
        if re.match(r"^\w", t) and re.search(r"\w$", t):
            parts.append(r"\b" + re.escape(t) + r"\w*")
        else:
            parts.append(re.escape(t))
    return re.compile("|".join(parts), re.I)


for raw in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines():
    raw = raw.strip()
    if not raw or raw.startswith("#"):
        continue
    parts = [p.strip() for p in raw.split("|")]
    cid, terms = parts[0], parts[1].split(",")
    since = parts[2] if len(parts) > 2 and parts[2] else None
    until = parts[3] if len(parts) > 3 and parts[3] else None
    cap = int(parts[4]) if len(parts) > 4 and parts[4] else 8
    c = frozen[cid]
    sender = c["sender_raw"]
    since = since or c["date"]
    rx = build_rx(terms)

    rows = []
    for d in chat:
        if d["sender"] != sender:
            continue
        date = d["date"][:10]
        if date < since or (until and date > until):
            continue
        t = d.get("text") or ""
        if rx.search(t):
            rows.append((date, "c", int(d["id"]), t))
    for date, mid, f in essays:
        if date < since or (until and date > until) or id_sender.get(mid) != sender:
            continue
        for para in re.split(r"\n{2,}|(?<=[.!?])\s+", Path(f).read_text(encoding="utf-8", errors="replace")):
            p = " ".join(para.split())
            if p and rx.search(p):
                rows.append((date, "e", mid, p))
    rows.sort(key=lambda r: (r[0], r[2]))

    print("=" * 100)
    print(f"{cid}  {c['date']}  {c['person']}  deadline={c['deadline']}")
    print(f"  COMMITMENT: {c['quote'][:160]}")
    print(f"  SETTLES IT: {c['check']}")
    print(f"  {len(rows)} hits since {since}" + (f" until {until}" if until else ""))
    for date, kind, mid, t in rows[:cap]:
        print(f"    {date} {kind}{mid:>6}  {' '.join(t.split())[:180]}")
    if len(rows) > cap:
        print(f"    ... +{len(rows) - cap} more")
    print()
