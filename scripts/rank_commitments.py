"""Stage 2 of the commitments study: rank prefilter candidates by how likely they are to
be a *commitment* under the frozen definition — a first-person, dated statement whose
action is specific enough that its absence would be visible.

    py scripts/rank_commitments.py --in tg-private/tmp/candidates-2021-22.jsonl \
        --out tg-private/tmp/ranked-2021-22.jsonl

Nothing here scores an outcome. This only decides reading order, and it writes the band
boundaries so the recall check (hand-reading one full month) can be done against them.
"""
import argparse
import collections
import io
import json
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# Volitional first-person frames — the core signal.
VOLITION = re.compile(
    r"\bI (?:will|shall|commit to|promise to|vow to|pledge to|am going to|intend to|plan to|"
    r"have decided to|decided to|am starting|am stopping|quit|choose to)\b|\bI'?ll\b|"
    r"\bfrom now on\b|\bI change now\b|\bmy (?:commitment|promise|vow) (?:is|to)\b",
    re.I,
)
# Obligation frames: real commitments hide here ("I must quit smoking") but so does most
# ordinary reflective prose, so they only count alongside a concrete object.
OBLIGATION = re.compile(r"\bI (?:must|need to|have to|should|want to)\b", re.I)

CADENCE = re.compile(
    r"\bevery (?:day|morning|evening|night|week|month|other day)\b|\bdaily\b|\bweekly\b|"
    r"\btwice a (?:day|week|month)\b|\b\d+ times a (?:day|week|month)\b",
    re.I,
)
DEADLINE = re.compile(
    r"\bby (?:the end of|next) (?:week|month|year|\w+day)\b|"
    r"\bby (?:January|February|March|April|May|June|July|August|September|October|November|December)\b|"
    r"\bwithin (?:a|one|two|three|four|\d+) (?:week|weeks|month|months|day|days)\b|"
    r"\bbefore (?:the end of|next)\b|\buntil I\b",
    re.I,
)
QUANTITY = re.compile(r"[£$€]\s?\d|\b\d+\s?(?:%|percent|kg|km|minutes|hours|pages|euros?|pounds?|dollars?)\b|\b\d{2,}\b")

# Actions that leave a trace someone else could check.
CONCRETE = re.compile(
    r"\b(?:quit|smok\w+|cigarette\w*|alcohol|drink\w*|drug\w*|porn\w*|masturbat\w*|"
    r"gym|train\w*|jiu.?jitsu|jujitsu|bjj|run\w*|walk\w*|exercise\w*|yoga|cold shower|"
    r"meditat\w*|wake up|get up|sleep|fast\w*|diet|eat\w*|sugar|meat|vegan|vegetarian|"
    r"essay\w*|chapter\w*|book\w*|read\w*|writ\w*|masterclass\w*|video\w*|watch\w*|"
    r"job|work|quit my job|business|client\w*|customer\w*|sell\w*|sold|launch\w*|"
    r"money|pay\w*|paid|save\w*|invest\w*|debt|fee\w*|penalt\w*|gift\w*|donat\w*|"
    r"call\w*|phone\w*|email\w*|messag\w*|apolog\w*|forgive|tell (?:him|her|them|my)|"
    r"ask\w*|speak|talk to|visit\w*|move\w*|travel\w*|flight|rent\w*|apartment|house|"
    r"gratitude|affirmation\w*|task\w*|recapitulat\w*|dream\w*|journal\w*|not.?doing)\b",
    re.I,
)
# Signals that this is the book talking, not the apprentice.
QUOTED = re.compile(
    r"^[\"“'`]|[\"”]\s*$|\b(?:Tolle|Castaneda|Hay|Don Juan|don Juan|Genaro|Nagual writes|"
    r"the (?:book|author|chapter) (?:says|writes|states)|he (?:says|writes)|she (?:says|writes)|"
    r"quote|citation)\b"
)
HYPOTHETICAL = re.compile(
    r"\b(?:if|maybe|perhaps|might|would|could|possibly|probably|hopefully|I wonder|"
    r"suppose|imagine|what if)\b",
    re.I,
)
SECOND_THIRD = re.compile(r"^(?:you|he|she|they|we|it|one)\b", re.I)


def score(text):
    s = 0
    why = []
    if VOLITION.search(text):
        s += 3
        why.append("volition")
    elif OBLIGATION.search(text):
        s += 1
        why.append("obligation")
    if CADENCE.search(text):
        s += 2
        why.append("cadence")
    if DEADLINE.search(text):
        s += 2
        why.append("deadline")
    if QUANTITY.search(text):
        s += 1
        why.append("quantity")
    if CONCRETE.search(text):
        s += 2
        why.append("concrete")
    if QUOTED.search(text):
        s -= 3
        why.append("-quoted")
    if HYPOTHETICAL.search(text):
        s -= 2
        why.append("-hypothetical")
    if SECOND_THIRD.match(text):
        s -= 2
        why.append("-not-first-person")
    if text.rstrip().endswith("?"):
        s -= 2
        why.append("-question")
    return s, why


def band(s):
    if s >= 6:
        return "high"
    if s >= 4:
        return "mid"
    if s >= 2:
        return "low"
    return "reject"


ap = argparse.ArgumentParser()
ap.add_argument("--in", dest="inp", required=True)
ap.add_argument("--out", required=True)
args = ap.parse_args()

rows = [json.loads(l) for l in Path(args.inp).open(encoding="utf-8")]
for r in rows:
    r["score"], r["why"] = score(r["text"])
    r["band"] = band(r["score"])
rows.sort(key=lambda r: (-r["score"], r["date"]))

with Path(args.out).open("w", encoding="utf-8") as fh:
    for r in rows:
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")

bands = collections.Counter(r["band"] for r in rows)
print(f"{len(rows):,} candidates ranked -> {args.out}")
for b in ("high", "mid", "low", "reject"):
    n = bands[b]
    src = collections.Counter(r["source"] for r in rows if r["band"] == b)
    print(f"  {b:7} {n:5,}   essay {src['essay']:5,}  chat {src['chat']:5,}")
print(f"\nto hand-classify (high+mid): {bands['high'] + bands['mid']:,}")
