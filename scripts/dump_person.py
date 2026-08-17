"""Dump one person's complete record — essays and chat interleaved in date order — for a
per-person dossier.

    py scripts/dump_person.py David --part 1 --parts 4
    py scripts/dump_person.py David --replies      # also messages that name/@ them

Dossiers built from this stay in tg-private/ and are never committed: they carry health,
finances, relationships and exit circumstances for named real people.
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

CHAT = Path("tg-private/tac-full.jsonl")
DOCS = Path("tg-private/docs")
INDEX = Path("tg-private/tac-docs-index.json")

ap = argparse.ArgumentParser()
ap.add_argument("person", help="raw sender name as it appears in the archive")
ap.add_argument("--part", type=int, default=1)
ap.add_argument("--parts", type=int, default=1)
ap.add_argument("--since")
ap.add_argument("--until")
ap.add_argument("--replies", action="store_true", help="instead dump OTHERS' messages naming them")
ap.add_argument("--names", help="comma-separated names/handles to match for --replies")
args = ap.parse_args()

id_sender = {e["id"]: e["sender"] for e in json.loads(INDEX.read_text(encoding="utf-8"))}

items = []
if args.replies:
    pats = [p.strip() for p in (args.names or args.person).split(",") if p.strip()]
    rx = re.compile("|".join(re.escape(p) for p in pats), re.I)
    for line in CHAT.open(encoding="utf-8"):
        d = json.loads(line)
        if d["sender"] == args.person:
            continue
        t = d.get("text") or ""
        if rx.search(t):
            items.append((d["date"][:10], int(d["id"]), "REPLY", d["sender"], t))
else:
    for line in CHAT.open(encoding="utf-8"):
        d = json.loads(line)
        if d["sender"] != args.person:
            continue
        items.append((d["date"][:10], int(d["id"]), "chat", args.person, d.get("text") or ""))
    for f in glob.glob(str(DOCS / "*.txt")):
        m = re.match(r"(\d{4}-\d{2}-\d{2})_(\d+)_(.+)\.txt$", os.path.basename(f))
        if not m:
            continue
        date, mid, title = m.group(1), int(m.group(2)), m.group(3)
        if id_sender.get(mid) != args.person:
            continue
        items.append((date, mid, "ESSAY", title, Path(f).read_text(encoding="utf-8", errors="replace")))

items = [i for i in items if not (args.since and i[0] < args.since) and not (args.until and i[0] > args.until)]
items.sort(key=lambda i: (i[0], i[1]))

n = len(items)
per = (n + args.parts - 1) // args.parts
chunk = items[(args.part - 1) * per : args.part * per]
words = sum(len(str(i[4]).split()) for i in chunk)
print(f"### {args.person} — part {args.part}/{args.parts} — {len(chunk)} of {n} items, {words:,} words")
if chunk:
    print(f"### {chunk[0][0]} .. {chunk[-1][0]}\n")
for date, mid, kind, who, text in chunk:
    body = " ".join(str(text).split())
    if kind == "ESSAY":
        print(f"\n{'='*90}\n[ESSAY] {date} e{mid} :: {who}\n{'='*90}\n{body}")
    elif kind == "REPLY":
        print(f"[{date} c{mid}] <{who}> {body}")
    else:
        print(f"[{date} c{mid}] {body}")
