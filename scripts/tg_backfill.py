"""Backfill the essay archive: download every indexed document whose message id has no
file in tg-private/docs yet, then convert it to .txt.

Works by message id, so it is immune to the filename-collision problem that left 145
ambiguous entries unresolved and needs no Google Drive access for Yar's own 98.

    py scripts/tg_backfill.py --plan            # what is missing, by sender
    py scripts/tg_backfill.py --run --limit 40  # download a batch
    py scripts/tg_backfill.py --run --all

Read-only against Telegram. Writes only into tg-private/docs (gitignored).
"""
import argparse
import collections
import io
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent))

INDEX = Path("tg-private/tac-docs-index.json")
OUT = Path("tg-private/docs")
CHAT = "-1001351431623"
TEXT_EXT = {".pdf", ".docx"}


def safe(s):
    s = re.sub(r'[<>:"/\\|?*]', "_", str(s)).strip()
    # pdftotext is an ANSI Windows binary and cannot open a path holding characters
    # outside the system codepage (one sender's display name carries an emoji).
    return "".join(c if c.encode("cp1252", "ignore") else "_" for c in s)


def convert(src, dst_txt):
    ext = os.path.splitext(src)[1].lower()
    if ext == ".pdf":
        r = subprocess.run(
            ["pdftotext", "-layout", str(src), str(dst_txt)], capture_output=True, text=True
        )
        if r.returncode != 0:
            return False, (r.stderr or "").strip()[:120]
        return True, ""
    if ext == ".docx":
        import docx

        d = docx.Document(str(src))
        parts = [p.text for p in d.paragraphs]
        for t in d.tables:
            for row in t.rows:
                parts.append("\t".join(c.text for c in row.cells))
        Path(dst_txt).write_text("\n".join(parts), encoding="utf-8")
        return True, ""
    return False, "no converter"


def have_ids():
    """Message ids already on disk, read from the YYYY-MM-DD_<id>_... filenames."""
    ids = set()
    if OUT.exists():
        for f in OUT.iterdir():
            m = re.match(r"\d{4}-\d{2}-\d{2}_(\d+)_", f.name)
            if m:
                ids.add(int(m.group(1)))
    return ids


def missing():
    idx = json.loads(INDEX.read_text(encoding="utf-8"))
    got = have_ids()
    out = [
        e
        for e in idx
        if e["id"] not in got and os.path.splitext(e.get("file", ""))[1].lower() in TEXT_EXT
    ]
    out.sort(key=lambda e: e["date"])
    return out


ap = argparse.ArgumentParser()
ap.add_argument("--plan", action="store_true")
ap.add_argument("--run", action="store_true")
ap.add_argument("--limit", type=int, default=40)
ap.add_argument("--all", action="store_true")
ap.add_argument("--batch", type=int, default=25, help="ids per get_messages call")
args = ap.parse_args()

todo = missing()
by_sender = collections.Counter(e["sender"] for e in todo)
print(f"{len(todo)} indexed pdf/docx attachments have no file on disk")
for who, n in by_sender.most_common():
    print(f"  {n:4d}  {who}")

if args.plan or not args.run:
    sys.exit(0)

if not args.all:
    todo = todo[: args.limit]

from tg import get_client, resolve  # noqa: E402

client = get_client()
OUT.mkdir(parents=True, exist_ok=True)
t0 = time.time()
ok = fail = nodoc = 0
try:
    entity = resolve(client, CHAT)
    meta = {e["id"]: e for e in todo}
    ids = list(meta)
    for i in range(0, len(ids), args.batch):
        chunk = ids[i : i + args.batch]
        for msg in client.get_messages(entity, ids=chunk):
            if msg is None or not getattr(msg, "document", None):
                nodoc += 1
                continue
            e = meta[msg.id]
            who = safe(e["sender"]).replace(" ", "_")
            dst = OUT / f"{e['date'][:10]}_{msg.id}_{who}_{safe(e['file'])}"
            dst_txt = dst.with_suffix(".txt")
            if dst_txt.exists():
                continue
            client.download_media(msg, file=str(dst))
            good, err = convert(dst, dst_txt)
            if good:
                n = len(dst_txt.read_text(encoding="utf-8", errors="replace").split())
                ok += 1
                flag = "  <-- ZERO WORDS, image-only pdf" if n < 50 else ""
                print(f"  OK {n:6d}w  {dst.name[:74]}{flag}")
            else:
                fail += 1
                print(f"  FAIL {err}  {dst.name[:70]}")
        print(f"  ... {min(i + args.batch, len(ids))}/{len(ids)}  ({time.time() - t0:.0f}s)")
finally:
    client.disconnect()

el = time.time() - t0
print(f"\ndownloaded {ok}, failed {fail}, no-document {nodoc} in {el:.0f}s")
