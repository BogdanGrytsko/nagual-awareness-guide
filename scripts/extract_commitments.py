"""Stage 1 of the commitments-vs-outcomes study: the cheap keyword prefilter.

Scans essays (tg-private/docs/*.txt) and chat (tg-private/tac-full.jsonl) in a date
window for first-person commitment language, and emits candidate sentences with
context for hand classification.

    py scripts/extract_commitments.py --since 2021-01-01 --until 2022-12-31 \
        --out tg-private/tmp/candidates-2021-22.jsonl

This does NOT score anything. Per the frozen rules in analysis/commitments-vs-outcomes.md,
extraction happens and the list is frozen to git before any outcome is looked at.
Recall of the patterns below gets checked by hand-reading one full month.
"""
import argparse
import collections
import io
import json
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DOCS = Path("tg-private/docs")
CHAT = Path("tg-private/tac-full.jsonl")

# First-person commitment language. Deliberately generous: this is a recall-first
# prefilter and precision is handled by the classification pass.
PATTERNS = [
    (r"\bI will\b(?! be (?:able|honest|damned))", "i-will"),
    (r"\bI'?ll\b", "ill"),
    (r"\bI am going to\b|\bI'?m going to\b", "going-to"),
    (r"\bfrom now on\b", "from-now-on"),
    (r"\bstarting (?:today|tomorrow|now|next week|this week)\b", "starting"),
    (r"\bI (?:commit|promise|vow|pledge)\b", "commit"),
    (r"\bmy (?:commitment|promise|vow) (?:is|to)\b", "my-commitment"),
    (r"\bI (?:have )?decided to\b", "decided"),
    (r"\bI (?:intend|plan|aim) to\b", "intend"),
    (r"\bI (?:must|need to|have to|should)\b", "must"),
    (r"\bno more\b", "no-more"),
    (r"\bI (?:stop|will stop|am stopping|quit|will quit)\b", "stop"),
    (r"\bevery (?:day|morning|evening|night|week|month)\b", "cadence"),
    (r"\bI change now\b", "i-change-now"),
    (r"\bmy (?:task|assignment|homework) (?:is|was)\b", "assigned"),
    (r"\bby (?:the end of|next) (?:week|month|year|\w+day)\b", "deadline"),
    (r"\bby (?:January|February|March|April|May|June|July|August|September|October|November|December)\b", "deadline-month"),
    (r"\bwithin (?:a|one|two|three|\d+) (?:week|weeks|month|months|day|days)\b", "deadline-within"),
    (r"\b(?:I|i) (?:won'?t|will not) (?:ever )?\b", "will-not"),
]
COMPILED = [(re.compile(p, re.I), tag) for p, tag in PATTERNS]

# Sentence split that tolerates essay formatting: hard stops, newlines, bullets.
SENT = re.compile(r"(?<=[.!?])\s+|\n+")

FNAME = re.compile(r"^(\d{4}-\d{2}-\d{2})_(\d+)_([^_]+(?:_[^_]+)*?)_(.+)\.txt$")
INDEX = Path("tg-private/tac-docs-index.json")

# Display names are embedded in filenames with spaces turned into underscores, so a
# filename cannot be split back into sender and title unambiguously ("SatiMa Ra" came
# out as "SatiMa"). The document index carries the authoritative sender per message id.
ID_SENDER = {e["id"]: e["sender"] for e in json.loads(INDEX.read_text(encoding="utf-8"))}


def sentences(text):
    for raw in SENT.split(text):
        s = " ".join(raw.split())
        if 12 <= len(s) <= 600:
            yield s


def scan(text):
    """Yield (sentence_index, sentence, [tags]) for sentences that match."""
    sents = list(sentences(text))
    for i, s in enumerate(sents):
        tags = [tag for rx, tag in COMPILED if rx.search(s)]
        if tags:
            yield i, s, tags, sents


ap = argparse.ArgumentParser()
ap.add_argument("--since", required=True)
ap.add_argument("--until", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--essays-only", action="store_true")
ap.add_argument("--chat-only", action="store_true")
args = ap.parse_args()

out = Path(args.out)
out.parent.mkdir(parents=True, exist_ok=True)
fh = out.open("w", encoding="utf-8")
n_cand = 0
per_source = collections.Counter()
per_person = collections.Counter()
tag_counts = collections.Counter()
scanned = collections.Counter()

if not args.chat_only:
    for f in sorted(DOCS.glob("*.txt")):
        m = FNAME.match(f.name)
        if not m:
            continue
        date, msgid, sender, title = m.groups()
        if not (args.since <= date <= args.until):
            continue
        sender = ID_SENDER.get(int(msgid), sender.replace("_", " "))
        text = f.read_text(encoding="utf-8", errors="replace")
        words = len(text.split())
        scanned["essays"] += 1
        scanned["essay_words"] += words
        if words == 0:
            scanned["essays_empty"] += 1
            continue
        for i, s, tags, sents in scan(text):
            rec = {
                "source": "essay",
                "date": date,
                "msgid": int(msgid),
                "sender": sender,
                "title": title,
                "sent_i": i,
                "text": s,
                "before": sents[i - 1] if i else "",
                "after": sents[i + 1] if i + 1 < len(sents) else "",
                "tags": tags,
            }
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            n_cand += 1
            per_source["essay"] += 1
            per_person[rec["sender"]] += 1
            tag_counts.update(tags)

if not args.essays_only:
    for line in CHAT.open(encoding="utf-8"):
        d = json.loads(line)
        date = d["date"][:10]
        if not (args.since <= date <= args.until):
            continue
        text = d.get("text") or ""
        scanned["chat_msgs"] += 1
        scanned["chat_words"] += len(text.split())
        for i, s, tags, sents in scan(text):
            rec = {
                "source": "chat",
                "date": date,
                "msgid": int(d["id"]),
                "sender": d.get("sender") or "?",
                "title": "",
                "sent_i": i,
                "text": s,
                "before": sents[i - 1] if i else "",
                "after": sents[i + 1] if i + 1 < len(sents) else "",
                "tags": tags,
            }
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            n_cand += 1
            per_source["chat"] += 1
            per_person[rec["sender"]] += 1
            tag_counts.update(tags)

fh.close()
print(f"window {args.since} .. {args.until}")
print(
    f"scanned {scanned['essays']} essays ({scanned['essay_words']:,} words, "
    f"{scanned['essays_empty']} empty) and {scanned['chat_msgs']:,} chat messages "
    f"({scanned['chat_words']:,} words)"
)
print(f"candidates: {n_cand:,}  (essay {per_source['essay']:,}, chat {per_source['chat']:,})")
print("\nby sender:")
for who, n in per_person.most_common():
    print(f"  {n:6,}  {who}")
print("\nby pattern:")
for tag, n in tag_counts.most_common():
    print(f"  {n:6,}  {tag}")
print(f"\nwritten to {out}")
