"""Stage 3: pull the evidence needed to score one frozen commitment.

For a commitment id (or a person), print everything that person wrote AFTER the
commitment date which matches its keywords — chat and essays together, in date order.
Scoring is done by reading these, per rule 6: search for the action, not for the
person's later self-assessment.

    py scripts/trace_outcome.py --cid C065 --terms smok,cigarette,tobacco --months 18
    py scripts/trace_outcome.py --person fenn --terms smok --since 2022-05-01

Nothing is written. This only reads the local archive.
"""
import argparse
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


def load_frozen():
    return [json.loads(l) for l in FROZEN.open(encoding="utf-8")]


ap = argparse.ArgumentParser()
ap.add_argument("--cid")
ap.add_argument("--person", help="alias, or the raw sender name")
ap.add_argument("--terms", required=True, help="comma-separated substrings, case-insensitive")
ap.add_argument("--since", help="YYYY-MM-DD; defaults to the commitment date")
ap.add_argument("--until")
ap.add_argument("--width", type=int, default=260)
ap.add_argument("--max", type=int, default=60)
ap.add_argument("--essays", action="store_true", help="also scan essay text (slower)")
args = ap.parse_args()

frozen = load_frozen()
sender = None
since = args.since
if args.cid:
    c = next(x for x in frozen if x["cid"] == args.cid)
    sender = c["sender_raw"]
    since = since or c["date"]
    print(f"# {c['cid']}  {c['date']}  {c['person']}  [{c['kind']}/{c['tier']}]")
    print(f"# commitment: {c['quote']}")
    print(f"# deadline:   {c['deadline']}")
    print(f"# settles it: {c['check']}")
    print()
elif args.person:
    hit = next((x for x in frozen if x["person"] == args.person), None)
    sender = hit["sender_raw"] if hit else args.person

terms = [t.strip().lower() for t in args.terms.split(",") if t.strip()]
rx = re.compile("|".join(re.escape(t) for t in terms), re.I)

rows = []
for line in CHAT.open(encoding="utf-8"):
    d = json.loads(line)
    if sender and d["sender"] != sender:
        continue
    date = d["date"][:10]
    if since and date < since:
        continue
    if args.until and date > args.until:
        continue
    t = d.get("text") or ""
    if rx.search(t):
        rows.append((date, "chat", int(d["id"]), t))

if args.essays:
    id_sender = {e["id"]: e["sender"] for e in json.loads(INDEX.read_text(encoding="utf-8"))}
    for f in glob.glob(str(DOCS / "*.txt")):
        m = re.match(r"(\d{4}-\d{2}-\d{2})_(\d+)_", os.path.basename(f))
        if not m:
            continue
        date, mid = m.group(1), int(m.group(2))
        if since and date < since:
            continue
        if args.until and date > args.until:
            continue
        if sender and id_sender.get(mid) != sender:
            continue
        text = Path(f).read_text(encoding="utf-8", errors="replace")
        for para in re.split(r"\n{2,}|(?<=[.!?])\s+", text):
            p = " ".join(para.split())
            if p and rx.search(p):
                rows.append((date, "essay", mid, p))

rows.sort(key=lambda r: (r[0], r[2]))
print(f"# {len(rows)} matches for {terms} by {sender or 'anyone'} since {since or 'start'}")
print()
for date, kind, mid, t in rows[: args.max]:
    t = " ".join(t.split())[: args.width]
    print(f"{date} {kind[0]}{mid:>6}  {t}")
if len(rows) > args.max:
    print(f"\n# ... {len(rows) - args.max} more suppressed (raise --max)")
