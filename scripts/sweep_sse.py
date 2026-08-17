"""Sweep the archive for successful-self-employment evidence: money amounts, venture events,
job changes, and the teacher's own claims about SSE.

Built 2026-08-17 for analysis/sse-outcomes.md. Applies the lesson from
analysis/commitments-recall-check.md: state up front what the method CANNOT see, which here
is income that was simply never posted. Absence of a reported figure is not absence of income.

    py scripts/sweep_sse.py --kind money --person holt --essays
    py scripts/sweep_sse.py --kind venture --counts
    py scripts/sweep_sse.py --kind teacher_claim
"""
import argparse
import collections
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

PATTERNS = {
    # a concrete monetary quantity
    "money": r"([£$€]\s?\d[\d,.]*\s?(k\b)?|\b\d[\d,.]*\s?(euros?|pounds?|dollars?|quid|CHF|USD|EUR|GBP|kr\b)|\b\d+\s?k\b(?=\s|$|\.|,))",
    # starting, running, or abandoning an income venture
    "venture": r"\b(my (own )?(business|company|shop|studio|practice|brand)|self.?employ\w*|SSE\b|freelanc\w*|client\w*|customer\w*|commission\w*|invoice\w*|sold (a|my|the|\d)|first (sale|client|customer|paying)|launch\w*|market stall|etsy|website|price list|rates?\b|quote[ds]?\b|paid me|got paid|income|revenue|profit|turnover)\b",
    # leaving or taking employment - the L0 boundary
    "employment": r"\b(quit (my )?job|left (my )?job|resign\w*|handed in (my )?notice|new job|got a job|started work\w*|full.?time|part.?time|\d+%\s?(position|work)|employer|boss|shift work|contract\w*|salary|wage[sd]?|payroll|redundan\w*|fired|laid off)\b",
    # the teacher making a claim or setting a target about SSE
    "teacher_claim": r"\b(successfully self.?employ\w*|SSE\b|path with heart|slave job|resource gather\w*|gather resources|abundance)\b",
}

ALIAS = {
    "Asaya": "holt", "Steen": "fenn", "Derwen Lyava": "vela", "Kisha Bo": "orin",
    "SatiMa Ra": "sena", "David": "arlo", "Jewels": "kesh", "Avianna": "isla",
    "Brooke Sophia": "thea", "Jarrad Gould": "bram", "Will Turner Sanders": "gale",
    "Ian Minick": "hale", "Dean": "dov", "Brett": "rex", "Sila": "wren", "Ilona": "sable",
    "Yar": "yar", "674233980": "mira", "1731636219": "wynn", "1907051013": "pia",
    "1589462348": "juno", "1548288276": "bode", "Hugo": "dell", "Leo": "rook",
    "Nagual Anaam": "Nagual Anaam",
}
REV = {v: k for k, v in ALIAS.items()}


def alias(s):
    return ALIAS.get(s, s)


ap = argparse.ArgumentParser()
ap.add_argument("--kind", required=True, choices=list(PATTERNS))
ap.add_argument("--person", help="alias (holt, fenn, ...) or raw sender name")
ap.add_argument("--since")
ap.add_argument("--until")
ap.add_argument("--max", type=int, default=50)
ap.add_argument("--width", type=int, default=185)
ap.add_argument("--counts", action="store_true")
ap.add_argument("--essays", action="store_true")
args = ap.parse_args()

rx = re.compile(PATTERNS[args.kind], re.I)
want = REV.get(args.person, args.person) if args.person else None

rows = []
for line in CHAT.open(encoding="utf-8"):
    d = json.loads(line)
    date = d["date"][:10]
    if (args.since and date < args.since) or (args.until and date > args.until):
        continue
    if want and d["sender"] != want:
        continue
    t = d.get("text") or ""
    if rx.search(t):
        rows.append((date, "c", int(d["id"]), alias(d["sender"]), t))

if args.essays:
    id_sender = {e["id"]: e["sender"] for e in json.loads(INDEX.read_text(encoding="utf-8"))}
    for f in glob.glob(str(DOCS / "*.txt")):
        m = re.match(r"(\d{4}-\d{2}-\d{2})_(\d+)_", os.path.basename(f))
        if not m:
            continue
        date, mid = m.group(1), int(m.group(2))
        if (args.since and date < args.since) or (args.until and date > args.until):
            continue
        raw = id_sender.get(mid, "?")
        if want and raw != want:
            continue
        for para in re.split(r"\n{2,}|(?<=[.!?])\s+", Path(f).read_text(encoding="utf-8", errors="replace")):
            p = " ".join(para.split())
            if p and rx.search(p):
                rows.append((date, "e", mid, alias(raw), p))

rows.sort(key=lambda r: (r[0], r[2]))
per = collections.Counter(r[3] for r in rows)
print(f"# {len(rows)} hits for kind={args.kind}" + (f" person={args.person}" if args.person else ""))
print("# by sender: " + ", ".join(f"{w}={n}" for w, n in per.most_common(30)))
if args.counts:
    sys.exit(0)
print()
for date, src, mid, who, t in rows[: args.max]:
    print(f"{date} {src}{mid:>6} {who[:12]:12} {' '.join(t.split())[: args.width]}")
if len(rows) > args.max:
    print(f"\n# ... +{len(rows) - args.max} more")
