"""Sweep the whole archive for enforcement events — penalties, fines, ultimatums, deadlines
imposed, and assigned tasks — in the phrasings the commitment prefilter provably cannot see.

Built 2026-08-17 after the recall check showed `dov`'s "I was given an ultimatum" never
entered the candidate pool. The leavers base-rate test needs EVERY penalty and ultimatum,
so it cannot be built on the commitment extractor's patterns.

    py scripts/sweep_enforcement.py --kind penalty
    py scripts/sweep_enforcement.py --kind ultimatum --context
    py scripts/sweep_enforcement.py --kind assignment --counts

Reads only. Scans chat and essays together.
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
    # money consequences attached to non-performance
    # NOTE: an earlier version of this pattern included a bare `fine[ds]?`, which matched
    # "that's fine" and produced 80 hits of which most were noise. Keep it tight.
    "penalty": r"(\bpenalt\w+|\bfined\b|£\s?\d+|\bGBP\s?\d+|\bforfeit\w*|\bowes? me\b|\bowing me\b|\byou owe\b|\bpayback all that you owe\b|\bincur\w*\s+(consequences|penalt\w+)|\bchopping block\b)",
    # threats to the continuation of the apprenticeship
    "ultimatum": r"\b(ultimatum|last chance|final warning|or (else|you'?re out|leave)|kicked out|thrown out|removed from|no longer (be )?(an? )?apprentice|end (your|the) apprenticeship|before you (can|could) continue|cannot continue|stop (your )?(training|apprenticeship)|out of (the|this) (group|apprenticeship)|expel\w*|dismiss\w*)\b",
    # tasks handed down - the phrasing the commitment prefilter misses entirely
    "assignment": r"\b(I was (given|gifted|tasked|assigned|told to|asked to)|I have been (given|tasked|asked)|my task (is|was)|the task (I was )?(given|received)|was tasked (with|to)|Nagual( Anaam)? (gave|asked|told|tasked) me|don Anaam (gave|asked|told|tasked) me|he (gave|tasked) me (a|the|with)|assigned me)\b",
    # explicit deadlines imposed by someone else
    "imposed_deadline": r"\b(by when|give me a date|pre.?decide[ds]? (a )?date|set a date|deadline|within \d+ days|send within|before you|you have (until|\d+))\b",
}

ALIAS = {
    "Asaya": "holt", "Steen": "fenn", "Derwen Lyava": "vela", "Kisha Bo": "orin",
    "SatiMa Ra": "sena", "David": "arlo", "Jewels": "kesh", "Avianna": "isla",
    "Brooke Sophia": "thea", "Jarrad Gould": "bram", "Will Turner Sanders": "gale",
    "Ian Minick": "hale", "Dean": "dov", "Brett": "rex", "Sila": "wren", "Ilona": "sable",
    "Yar": "yar", "674233980": "mira", "1731636219": "wynn", "1907051013": "pia",
    "1589462348": "juno", "1548288276": "bode", "Olupandu N \U0001f451": "tove",
    "Hugo": "dell", "Nagual Anaam": "Nagual Anaam",
}


def alias(s):
    return ALIAS.get(s, s)


ap = argparse.ArgumentParser()
ap.add_argument("--kind", required=True, choices=list(PATTERNS) + ["all"])
ap.add_argument("--since")
ap.add_argument("--until")
ap.add_argument("--max", type=int, default=60)
ap.add_argument("--width", type=int, default=190)
ap.add_argument("--counts", action="store_true", help="only per-person counts")
ap.add_argument("--from-teacher", action="store_true", help="only messages sent by the teacher")
ap.add_argument("--essays", action="store_true")
args = ap.parse_args()

kinds = list(PATTERNS) if args.kind == "all" else [args.kind]
rxs = {k: re.compile(PATTERNS[k], re.I) for k in kinds}

rows = []
for line in CHAT.open(encoding="utf-8"):
    d = json.loads(line)
    date = d["date"][:10]
    if args.since and date < args.since:
        continue
    if args.until and date > args.until:
        continue
    if args.from_teacher and d["sender"] != "Nagual Anaam":
        continue
    t = d.get("text") or ""
    for k, rx in rxs.items():
        if rx.search(t):
            rows.append((date, k, "c", int(d["id"]), alias(d["sender"]), t))
            break

if args.essays:
    id_sender = {e["id"]: e["sender"] for e in json.loads(INDEX.read_text(encoding="utf-8"))}
    for f in glob.glob(str(DOCS / "*.txt")):
        m = re.match(r"(\d{4}-\d{2}-\d{2})_(\d+)_", os.path.basename(f))
        if not m:
            continue
        date, mid = m.group(1), int(m.group(2))
        if (args.since and date < args.since) or (args.until and date > args.until):
            continue
        who = alias(id_sender.get(mid, "?"))
        if args.from_teacher and who != "Nagual Anaam":
            continue
        for para in re.split(r"\n{2,}|(?<=[.!?])\s+", Path(f).read_text(encoding="utf-8", errors="replace")):
            p = " ".join(para.split())
            if not p:
                continue
            for k, rx in rxs.items():
                if rx.search(p):
                    rows.append((date, k, "e", mid, who, p))
                    break

rows.sort(key=lambda r: (r[0], r[3]))
print(f"# {len(rows)} hits for {kinds}" + (f" from the teacher only" if args.from_teacher else ""))
per = collections.Counter(r[4] for r in rows)
perkind = collections.Counter(r[1] for r in rows)
print(f"# by kind: {dict(perkind)}")
print("# by sender: " + ", ".join(f"{w}={n}" for w, n in per.most_common()))
if args.counts:
    sys.exit(0)
print()
for date, k, src, mid, who, t in rows[: args.max]:
    print(f"{date} {k[:4]:4} {src}{mid:>6} {who[:13]:13} {' '.join(t.split())[: args.width]}")
if len(rows) > args.max:
    print(f"\n# ... +{len(rows) - args.max} more")
